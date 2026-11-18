/* Per-call-site prototypes for every objc_msgSend / Super2 / _stret call,
 * so the decompiler types returns and arguments with the REAL method
 * signature instead of the generic `void *objc_msgSend(void *, char *, ...)`.
 *
 * Why it matters for a 1:1 port: 625 calls go to the 27 float-returning
 * selectors (Camera getDrawScale, Texture2D getImgW/H, ...). Untyped, their
 * result is a pointer/int that later becomes a float: compiled as C that is
 * a numeric conversion, not the bit-reinterpretation the original performs.
 * Same for double (UIAcceleration x/y), BOOL/short returns and float/double
 * parameters (soft-float: they travel in core registers).
 *
 * Inputs:
 *   analysis/objc/types.spec          STRUCT/CLASS/METHOD (tools/objc_types.py,
 *                                     incl. Texture2D categories)
 *   analysis/objc/external_methods.tsv Foundation/UIKit/EAGL selectors (iOS 3.1)
 *   analysis/dynamic/msgsend_sites.tsv runtime (site, [Class sel]) for receivers
 *                                     and register-held selectors
 * Selector per site: decompiler p-code (constant -> string, or LOAD of a
 * selref); runtime capture otherwise. Receiver class: constant class ref,
 * runtime capture, else the selector's signature if it is the same in every
 * class. Lookup walks the superclass chain.
 *
 * Usage:
 *   analyzeHeadless analysis/ghidra MGST -process MGSTUS -noanalysis \
 *       -scriptPath tools/ghidra -postScript ApplyCallsiteSignatures.java
 * Idempotent (overrides are replaced).
 */
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.*;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.*;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.Namespace;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.pcode.*;

public class ApplyCallsiteSignatures extends GhidraScript {

    static final long MSGSEND = 0x5add0, SUPER2 = 0x5addc, STRET = 0x5ade8;

    DataTypeManager dtm;
    final Map<String, String> superOf = new HashMap<>();
    final Map<Long, String> classAt = new HashMap<>();          // class_t VA -> name
    final Map<Long, String> metaAt = new HashMap<>();           // metaclass VA -> name
    final Map<String, String[]> methods = new HashMap<>();      // "Cls|kind|sel" -> [ret, args...]
    final Map<String, Set<String>> sigsBySel = new HashMap<>(); // sel -> distinct signatures
    final Map<String, String[]> bySelUnique = new HashMap<>();
    final Map<String, String[]> external = new HashMap<>();
    final Set<String> externalVarargs = new HashSet<>();
    final Map<Long, List<String[]>> dyn = new HashMap<>();      // site -> [kind(+/-), class, sel]
    final Map<String, Integer> stats = new TreeMap<>();

    void stat(String k) { stats.merge(k, 1, Integer::sum); }

    List<String[]> tsv(String path) throws Exception {
        List<String[]> out = new ArrayList<>();
        try (BufferedReader r = new BufferedReader(new FileReader(path))) {
            String l;
            while ((l = r.readLine()) != null) {
                if (l.isEmpty() || l.startsWith("#")) continue;
                out.add(l.split("\t", -1));
            }
        }
        return out;
    }

    @Override
    protected void run() throws Exception {
        dtm = currentProgram.getDataTypeManager();
        for (String[] p : tsv("analysis/objc/types.spec")) {
            if (p[0].equals("CLASS") && p.length > 3) superOf.put(p[1], p[3]);
            if (p[0].equals("METHOD")) {
                // METHOD class kind selector imp ret self sel args...
                String[] sig = new String[p.length - 7];
                sig[0] = p[5];
                System.arraycopy(p, 8, sig, 1, p.length - 8);
                methods.put(p[1] + "|" + p[2] + "|" + p[3], sig);
                sigsBySel.computeIfAbsent(p[3], k -> new HashSet<>()).add(String.join(",", sig));
                bySelUnique.put(p[3], sig);
            }
        }
        for (String[] p : tsv("analysis/objc/classes.tsv")) {
            if (p[0].equals("class")) continue;
            long va = Long.decode(p[2]);
            classAt.put(va, p[0]);
            if (!superOf.containsKey(p[0]) || superOf.get(p[0]).equals("?")) superOf.put(p[0], p[1]);
            try { metaAt.put(getInt(toAddr(va)) & 0xffffffffL, p[0]); } catch (Exception e) { }
        }
        for (String[] p : tsv("analysis/objc/external_methods.tsv")) {
            List<String> sig = new ArrayList<>();
            sig.add(p[1]);
            if (!p[2].isEmpty()) sig.addAll(Arrays.asList(p[2].split(",")));
            external.put(p[0], sig.toArray(new String[0]));
            if (p[3].equals("1")) externalVarargs.add(p[0]);
        }
        for (String[] p : tsv("analysis/dynamic/msgsend_sites.tsv")) {
            if (p[0].equals("site")) continue;
            long site = Long.decode(p[0]);
            for (String o : p[3].split(" \\| ")) {
                o = o.replaceAll(" x\\d+$", "");
                java.util.regex.Matcher m = java.util.regex.Pattern.compile("^([+-])\\[(\\S+) (.+)\\]$").matcher(o);
                if (m.matches()) dyn.computeIfAbsent(site, k -> new ArrayList<>())
                        .add(new String[]{m.group(1), m.group(2), m.group(3)});
            }
        }
        println("methods: " + methods.size() + ", external: " + external.size() + ", runtime sites: " + dyn.size());

        DecompInterface d = new DecompInterface();
        DecompileOptions o = new DecompileOptions();
        d.setOptions(o);
        d.toggleSyntaxTree(true);
        d.openProgram(currentProgram);
        int nf = 0;
        List<Function> fns = new ArrayList<>();
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            if (!f.isThunk() && !f.isExternal()) fns.add(f);
        }
        for (Function f : fns) {
            monitor.checkCancelled();
            DecompileResults r = d.decompileFunction(f, 120, monitor);
            if (!r.decompileCompleted() || r.getHighFunction() == null) { stat("decompile failed"); continue; }
            Iterator<PcodeOpAST> it = r.getHighFunction().getPcodeOps();
            while (it.hasNext()) {
                PcodeOpAST op = it.next();
                if (op.getOpcode() != PcodeOp.CALL) continue;
                long tgt = op.getInput(0).getAddress().getOffset();
                if (tgt != MSGSEND && tgt != SUPER2 && tgt != STRET) continue;
                stat("sites");
                handle(f, op, tgt);
            }
            if (++nf % 200 == 0) println("  functions: " + nf + "/" + fns.size());
        }
        d.dispose();
        for (Map.Entry<String, Integer> e : stats.entrySet()) println(e.getKey() + ": " + e.getValue());
    }

    void handle(Function f, PcodeOpAST op, long tgt) throws Exception {
        Address site = op.getSeqnum().getTarget();
        boolean stret = tgt == STRET;
        int selIdx = stret ? 3 : 2, rcvIdx = stret ? 2 : 1;
        if (op.getNumInputs() <= selIdx) { stat("skip: selector input missing"); return; }

        Set<String> cand = new TreeSet<>();
        selectorsOf(op.getInput(selIdx), cand, 0);
        String sel = null;
        if (cand.size() == 1) sel = cand.iterator().next();
        List<String[]> obs = dyn.get(site.getOffset());
        if (cand.size() > 1) {
            Set<String> sigs = new HashSet<>();
            String[] rs = classConst(op.getInput(rcvIdx));
            if (rs == null) rs = selfReceiver(f, op.getInput(rcvIdx));
            for (String c : cand) {
                String[] sg = rs != null ? lookup(rs[1], rs[0], c) : null;
                if (sg == null && sigsBySel.containsKey(c)) sg = normalizedUnique(c);
                if (sg == null && external.containsKey(c)) sg = external.get(c);
                sigs.add(sg == null ? "?" : norm(sg));
            }
            if (sigs.size() == 1 && !sigs.contains("?")) {
                sel = cand.iterator().next();
                stat("selector: static merge of " + cand.size() + " selrefs, identical signatures");
            } else {
                stat("skip: static merged selectors with different signatures");
                stat("  merged @" + f.getName() + " " + cand);
                return;
            }
        }
        if (sel == null && obs != null) {
            Set<String> s = new HashSet<>();
            for (String[] x : obs) s.add(x[2]);
            if (s.size() == 1) { sel = s.iterator().next(); stat("selector from runtime"); }
            else {
                // compiler-merged call site: several selectors, one call. Fine
                // to type if every candidate has the same signature.
                Set<String> sigs = new HashSet<>();
                String pick = null;
                for (String[] x : obs) {
                    String[] sg = lookup(x[1], x[0], x[2]);
                    if (sg == null && external.containsKey(x[2])) sg = external.get(x[2]);
                    sigs.add(sg == null ? "?" : norm(sg));
                    pick = x[2];
                }
                if (sigs.size() == 1 && !sigs.contains("?")) {
                    sel = pick;
                    stat("selector from runtime (merged site, identical signatures)");
                } else {
                    stat("skip: register selector, polymorphic at runtime");
                    stat("  polymorphic @" + f.getName() + " " + s);
                    return;
                }
            }
        }
        if (sel == null) { stat("skip: selector unknown"); stat("  unknown selector @" + f.getName() + " " + site); return; }

        // receiver: [kind, class]
        String[] rcv = null;
        if (tgt == SUPER2) {
            rcv = superReceiver(f);
        } else {
            rcv = classConst(op.getInput(rcvIdx));
            if (rcv == null) rcv = selfReceiver(f, op.getInput(rcvIdx));
        }
        if (rcv == null && obs != null) {
            Set<String> s = new HashSet<>();
            for (String[] x : obs) if (x[2].equals(sel)) s.add(x[0] + x[1]);
            if (s.size() == 1) {
                String k = s.iterator().next();
                rcv = new String[]{k.substring(0, 1), k.substring(1)};
            }
        }
        String[] sig = null;
        boolean varargs = false;
        String how;
        if (rcv != null && (sig = lookup(rcv[1], rcv[0], sel)) != null) {
            how = "typed: class method table";
        } else if (rcv != null && external.containsKey(sel)) {
            // the receiver is known but its MGST class chain does not define the
            // selector (a UIKit/Foundation class, or inherited from one): the SDK
            // signature, never an unrelated MGST class's (-[UIAcceleration z]
            // was typed as -[ObjectBase z] const float * - LOG 2026-10-07 STEP 1)
            sig = external.get(sel);
            varargs = externalVarargs.contains(sel);
            how = "typed: external SDK table (known foreign receiver)";
        } else if (sigsBySel.containsKey(sel) && sigsBySel.get(sel).size() == 1) {
            sig = bySelUnique.get(sel);
            how = "typed: unique MGST signature";
        } else if (sigsBySel.containsKey(sel) && normalizedUnique(sel) != null) {
            sig = normalizedUnique(sel);
            how = "typed: MGST signature unique up to pointer type";
        } else if (external.containsKey(sel)) {
            sig = external.get(sel);
            varargs = externalVarargs.contains(sel);
            how = "typed: external SDK table";
        } else {
            stat("skip: ambiguous selector " + (sigsBySel.containsKey(sel) ? "(MGST, receiver unknown)" : "(unknown external)"));
            stat("  skipped selector: " + sel + (rcv != null ? " on " + rcv[0] + rcv[1] : "") + " @" + f.getName());
            return;
        }

        FunctionDefinitionDataType def = new FunctionDefinitionDataType("msg_" + site.toString());
        List<ParameterDefinition> ps = new ArrayList<>();
        DataType id = new PointerDataType(VoidDataType.dataType);
        DataType selT = new PointerDataType(CharDataType.dataType);
        String ret = sig[0];
        boolean bigStruct = ret.startsWith("struct(") && type(ret).getLength() > 4;
        if (stret) {
            DataType rt = ret.startsWith("struct(") ? type(ret) : VoidDataType.dataType;
            if (rt instanceof Pointer) rt = VoidDataType.dataType;
            ps.add(new ParameterDefinitionImpl("stret", new PointerDataType(rt), null));
            def.setReturnType(VoidDataType.dataType);
        } else if (bigStruct) {
            stat("skip: struct return through plain msgSend");
            return;
        } else if (ret.startsWith("struct(")) {
            def.setReturnType(IntegerDataType.dataType);
        } else {
            def.setReturnType(type(ret));
        }
        ps.add(new ParameterDefinitionImpl(tgt == SUPER2 ? "super" : "self", id, null));
        ps.add(new ParameterDefinitionImpl("op", selT, null));
        Set<String> used = new HashSet<>(Arrays.asList("stret", "self", "super", "op"));
        for (int i = 1; i < sig.length; i++) flatten(sig[i], "a" + i, ps, used);
        def.setArguments(ps.toArray(new ParameterDefinition[0]));
        def.setVarArgs(varargs);
        // writeOverride does not remove an earlier override at the same site:
        // a re-run left TWO and the decompiler used the stale one (LOG
        // 2026-10-07 STEP 2). Delete every existing one first.
        Namespace os = HighFunction.findOverrideSpace(f);
        if (os != null) {
            List<Symbol> old = new ArrayList<>();
            for (Symbol sym : currentProgram.getSymbolTable().getSymbols(os))
                if (sym.getAddress().equals(site)) old.add(sym);
            for (Symbol sym : old) { sym.delete(); stat("  stale override removed"); }
        }
        HighFunctionDBUtil.writeOverride(f, site, def);
        stat(how);
        if (ret.equals("f4") || ret.equals("f8")) stat("  of which float/double returns");
    }

    /** Signature with every pointer-ish type folded to ptr(void). */
    String norm(String[] sig) {
        StringBuilder b = new StringBuilder();
        for (String t : sig) b.append(t.startsWith("ptr(") || t.equals("id") || t.equals("sel") ? "ptr(void)" : t).append(',');
        return b.toString();
    }

    String[] normalizedUnique(String sel) {
        Set<String> n = new HashSet<>();
        String[] any = null;
        for (String k : methods.keySet()) {
            if (!k.endsWith("|" + sel)) continue;
            String[] sg = methods.get(k);
            n.add(norm(sg));
            any = sg;
        }
        if (n.size() != 1 || any == null) return null;
        return norm(any).split(",");
    }

    String[] lookup(String cls, String kind, String sel) {
        String c = cls;
        for (int depth = 0; c != null && depth < 16; depth++) {
            String[] s = methods.get(c + "|" + kind + "|" + sel);
            if (s != null) return s;
            c = superOf.get(c);
            if (c == null || c.equals("?")) break;
        }
        return null;
    }

    /** objc_msgSendSuper2 inside -[C m] / +[C m]: lookup starts at C's super. */
    String[] superReceiver(Function f) {
        String n = f.getName();
        java.util.regex.Matcher m = java.util.regex.Pattern.compile("^__(\\w+?)_").matcher(n);
        String cmt = f.getComment() == null ? "" : f.getComment();
        java.util.regex.Matcher m2 = java.util.regex.Pattern.compile("([+-])\\[(\\w+)[ (]").matcher(cmt + " " + f.getName(true));
        for (String cls : classAt.values()) {
            if (n.startsWith("__" + cls + "_")) {
                String sup = superOf.get(cls);
                if (sup == null || sup.equals("?")) return null;
                boolean isClassMethod = f.getParameterCount() > 0 && f.getParameter(0).getDataType() instanceof Pointer
                        && ((Pointer) f.getParameter(0).getDataType()).getDataType() instanceof VoidDataType;
                return new String[]{isClassMethod ? "+" : "-", sup};
            }
        }
        return null;
    }

    void selectorsOf(Varnode v, Set<String> out, int depth) throws Exception {
        if (v == null || depth > 6) return;
        PcodeOp def = v.getDef();
        if (def != null && def.getOpcode() == PcodeOp.MULTIEQUAL) {
            for (int i = 0; i < def.getNumInputs(); i++) selectorsOf(def.getInput(i), out, depth + 1);
            return;
        }
        String s1 = selectorOf(v);
        if (s1 != null) out.add(s1);
    }

    /** Receiver is the method's own `self` (first parameter): its class. */
    String[] selfReceiver(Function f, Varnode v) {
        if (v == null) return null;
        HighVariable hv = v.getHigh();
        if (!(hv instanceof HighParam) || ((HighParam) hv).getSlot() != 0) return null;
        String best = null;
        for (String cls : classAt.values()) {
            if (f.getName().startsWith("__" + cls + "_") && (best == null || cls.length() > best.length())) best = cls;
        }
        if (best == null) return null;
        String kind = f.getComment() != null && f.getComment().contains("+[") ? "+" : "-";
        return new String[]{kind, best};
    }

    String selectorOf(Varnode v) throws Exception {
        for (int hop = 0; hop < 4 && v != null; hop++) {
            if (v.isConstant() || v.isAddress()) {
                return stringOrSelref(v.getOffset());
            }
            PcodeOp def = v.getDef();
            if (def == null) return null;
            if (def.getOpcode() == PcodeOp.LOAD && def.getInput(1).isConstant()) {
                long p = getInt(toAddr(def.getInput(1).getOffset())) & 0xffffffffL;
                return stringOrSelref(p);
            }
            if (def.getOpcode() == PcodeOp.COPY || def.getOpcode() == PcodeOp.CAST) { v = def.getInput(0); continue; }
            if (def.getOpcode() == PcodeOp.PTRSUB && def.getInput(0).isConstant() && def.getInput(1).isConstant()) {
                return stringOrSelref(def.getInput(0).getOffset() + def.getInput(1).getOffset());
            }
            return null;
        }
        return null;
    }

    String stringOrSelref(long va) throws Exception {
        MemoryBlock b = getMemoryBlock(toAddr(va));
        if (b == null) return null;
        String bn = b.getName();
        if (bn.contains("selrefs") || bn.contains("nl_symbol") || bn.contains("objc_const") || bn.contains("__data")) {
            long p = getInt(toAddr(va)) & 0xffffffffL;
            MemoryBlock b2 = getMemoryBlock(toAddr(p));
            if (b2 != null && (b2.getName().contains("cstring") || b2.getName().contains("methname"))) return cstr(p);
            return null;
        }
        if (bn.contains("cstring") || bn.contains("methname")) return cstr(va);
        return null;
    }

    String cstr(long va) throws Exception {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 128; i++) {
            byte c = getByte(toAddr(va + i));
            if (c == 0) break;
            sb.append((char) c);
        }
        return sb.length() > 0 ? sb.toString() : null;
    }

    String[] classConst(Varnode v) throws Exception {
        for (int hop = 0; hop < 4 && v != null; hop++) {
            if (v.isConstant() || v.isAddress()) {
                long a = v.getOffset();
                if (classAt.containsKey(a)) return new String[]{"+", classAt.get(a)};
                return null;
            }
            PcodeOp def = v.getDef();
            if (def == null) return null;
            if (def.getOpcode() == PcodeOp.LOAD && def.getInput(1).isConstant()) {
                long p = getInt(toAddr(def.getInput(1).getOffset())) & 0xffffffffL;
                if (classAt.containsKey(p)) return new String[]{"+", classAt.get(p)};
                return null;
            }
            if (def.getOpcode() == PcodeOp.COPY || def.getOpcode() == PcodeOp.CAST) { v = def.getInput(0); continue; }
            if (def.getOpcode() == PcodeOp.PTRSUB && def.getInput(0).isConstant() && def.getInput(1).isConstant()) {
                long a = def.getInput(0).getOffset() + def.getInput(1).getOffset();
                if (classAt.containsKey(a)) return new String[]{"+", classAt.get(a)};
            }
            return null;
        }
        return null;
    }

    void flatten(String t, String name, List<ParameterDefinition> out, Set<String> used) {
        if (t.startsWith("struct(")) {
            DataType s = type(t);
            if (s instanceof Structure) {
                int k = 0;
                for (DataTypeComponent c : ((Structure) s).getDefinedComponents()) {
                    flatten(typeString(c.getDataType()), name + "_" + (c.getFieldName() != null ? c.getFieldName() : "f" + k), out, used);
                    k++;
                }
                return;
            }
        }
        String n = name;
        int x = 2;
        while (!used.add(n)) n = name + x++;
        if (t.equals("f8") || t.equals("i8") || t.equals("u8")) {
            // Apple's armv6 APCS packs a 64-bit argument at 4-byte alignment
            // (r1:r2, r3:stack); Ghidra's convention aligns it to 8 and reads
            // it from the wrong storage (NSTimer interval came out as
            // CONCAT(sel, self), LOG 2026-10-09). Two 32-bit words say exactly
            // what the caller passes, as ApplyVarargCallsites does.
            out.add(new ParameterDefinitionImpl(n + "_lo", UnsignedIntegerDataType.dataType, null));
            out.add(new ParameterDefinitionImpl(n + "_hi", UnsignedIntegerDataType.dataType, null));
            return;
        }
        out.add(new ParameterDefinitionImpl(n, type(t), null));
    }

    final Set<String> structTrace = new HashSet<>();

    String typeString(DataType dt) {
        if (dt instanceof Structure) return "struct(" + dt.getName() + ")";
        if (dt instanceof Pointer || dt instanceof Array) return "ptr(void)";
        if (dt instanceof FloatDataType) return "f4";
        if (dt instanceof DoubleDataType) return "f8";
        return "i" + dt.getLength();
    }

    DataType type(String t) {
        switch (t) {
            case "void": return VoidDataType.dataType;
            case "i1": return CharDataType.dataType;
            case "u1": return UnsignedCharDataType.dataType;
            case "bool": return BooleanDataType.dataType;
            case "i2": return ShortDataType.dataType;
            case "u2": return UnsignedShortDataType.dataType;
            case "i4": return IntegerDataType.dataType;
            case "u4": return UnsignedIntegerDataType.dataType;
            case "i8": return LongLongDataType.dataType;
            case "u8": return UnsignedLongLongDataType.dataType;
            case "f4": return FloatDataType.dataType;
            case "f8": return DoubleDataType.dataType;
            case "id": return new PointerDataType(VoidDataType.dataType);
            case "sel": return new PointerDataType(CharDataType.dataType);
        }
        if (t.startsWith("ptr(")) return new PointerDataType(type(t.substring(4, t.length() - 1)));
        if (t.startsWith("arr(")) return new PointerDataType(VoidDataType.dataType);
        if (t.startsWith("struct(")) {
            String n = t.substring(7, t.length() - 1);
            DataType s = dtm.getDataType(new CategoryPath("/mgst"), n);
            if (s == null) s = dtm.getDataType(new CategoryPath("/mgst/objc"), n);
            if (s == null) {
                // any category (FixDuplicateTypes may have kept another copy):
                // the defined Structure with the most components
                List<DataType> found = new ArrayList<>();
                dtm.findDataTypes(n, found);
                for (DataType d : found) {
                    if (d instanceof TypeDef) d = ((TypeDef) d).getBaseDataType();
                    if (d instanceof Structure && !d.isNotYetDefined()
                            && (s == null || ((Structure) d).getNumDefinedComponents() > ((Structure) s).getNumDefinedComponents()))
                        s = d;
                }
            }
            if (s != null) return s;
            // never stand a pointer in for a by-value struct: that silently drops
            // arguments (LOG 2026-10-07 STEP 2: a re-run lost every CGRect/CGSize
            // argument after the struct moved category)
            throw new IllegalStateException("struct type not found: " + n);
        }
        return IntegerDataType.dataType;
    }
}
