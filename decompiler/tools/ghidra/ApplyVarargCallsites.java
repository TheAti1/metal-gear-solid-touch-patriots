/* Explicit prototypes for variadic call sites whose format string is a
 * constant (LOG 2026-10-08): NSLog / printf / sprintf / snprintf / fprintf
 * and the ObjC format selectors (stringWithFormat:, initWithFormat:,
 * appendFormat:, stringByAppendingFormat:, localizedStringWithFormat:).
 *
 * Ghidra cannot know how many arguments follow `...`, so it printed none:
 * `[NSString stringWithFormat:@"%s"]` lost its string, `printf("No.%d")` its
 * number, and the recompiled call formatted whatever was left in r3. The
 * format string says exactly which words follow. Every site gets a
 * non-variadic override with those parameters:
 *   %d %i %u %x %X %o %c %p %s %@ %C %S  -> one 32-bit word
 *   %f %e %g %a (double), %ll* %q*         -> two 32-bit words (lo, hi)
 *   `*` width / precision                  -> one word each
 * 64-bit values are passed as two words because Apple's armv6 APCS packs
 * them at 4-byte alignment (r1:r2, r3:stack), which a single 8-byte
 * parameter would not express. The return type and the fixed parameters
 * before the format are kept from any existing override.
 * Run after ApplyCallsiteSignatures.java (it replaces that script's
 * override at these sites). Idempotent.
 */
import java.util.*;
import java.util.regex.*;

import ghidra.app.decompiler.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.pcode.*;
import ghidra.program.model.symbol.*;

public class ApplyVarargCallsites extends GhidraScript {
    static final long MSGSEND = 0x5add0;
    static final Map<String, Integer> C_FMT = new HashMap<>();
    static {
        C_FMT.put("_NSLog", 0); C_FMT.put("_printf", 0); C_FMT.put("_sprintf", 1);
        C_FMT.put("_snprintf", 2); C_FMT.put("_fprintf", 1);
    }
    static final Set<String> OBJC_FMT = new HashSet<>(Arrays.asList("stringWithFormat:", "initWithFormat:",
            "appendFormat:", "stringByAppendingFormat:", "localizedStringWithFormat:"));
    static final Pattern SPEC = Pattern.compile(
            "%(?:%|[-+ #0']*(\\*|\\d+)?(?:\\.(\\*|\\d+))?(hh|h|ll|l|q|L|z|t|j)?([diouxXcCsSpP@eEfFgGaA]))");
    Map<String, Integer> stats = new TreeMap<>();

    void stat(String k) { stats.merge(k, 1, Integer::sum); }

    @Override
    protected void run() throws Exception {
        DecompInterface d = new DecompInterface();
        d.setOptions(new DecompileOptions());
        d.openProgram(currentProgram);
        Set<Function> todo = new LinkedHashSet<>();
        Map<Address, String> cTargets = new HashMap<>();
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            if (C_FMT.containsKey(f.getName())) cTargets.put(f.getEntryPoint(), f.getName());
        }
        List<Address> targets = new ArrayList<>(cTargets.keySet());
        targets.add(toAddr(MSGSEND));
        for (Address t : targets)
            for (Reference r : getReferencesTo(t)) {
                Function f = getFunctionContaining(r.getFromAddress());
                if (f != null && !f.isThunk()) todo.add(f);
            }
        for (Function f : todo) {
            if (monitor.isCancelled()) break;
            DecompileResults res = d.decompileFunction(f, 60, monitor);
            HighFunction hf = res.getHighFunction();
            if (hf == null) { stat("decompile failed"); continue; }
            Iterator<PcodeOpAST> it = hf.getPcodeOps();
            List<Object[]> sites = new ArrayList<>();
            while (it.hasNext()) {
                PcodeOpAST op = it.next();
                if (op.getOpcode() != PcodeOp.CALL) continue;
                Address tgt = op.getInput(0).getAddress();
                int fmtIdx;          // index of the format among the call's arguments
                String kind;
                if (cTargets.containsKey(tgt)) { fmtIdx = C_FMT.get(cTargets.get(tgt)); kind = cTargets.get(tgt); }
                else if (tgt.getOffset() == MSGSEND && op.getNumInputs() > 3) {
                    String sel = constString(op.getInput(2), false);
                    if (sel == null || !OBJC_FMT.contains(sel)) continue;
                    fmtIdx = 2; kind = sel;
                } else continue;
                if (op.getNumInputs() <= 1 + fmtIdx) { stat("format argument not visible"); continue; }
                String fmt = constString(op.getInput(1 + fmtIdx), true);
                if (fmt == null) { stat("format not constant: " + kind); continue; }
                sites.add(new Object[]{op.getSeqnum().getTarget(), fmtIdx, kind, fmt});
            }
            for (Object[] s : sites) apply(f, (Address) s[0], (Integer) s[1], (String) s[2], (String) s[3]);
        }
        println("ApplyVarargCallsites: " + stats);
    }

    void apply(Function f, Address site, int fmtIdx, String kind, String fmt) throws Exception {
        DataType u32 = UnsignedIntegerDataType.dataType;
        DataType ptr = new PointerDataType(VoidDataType.dataType);
        FunctionDefinition old = null;
        Namespace os = HighFunction.findOverrideSpace(f);
        List<Symbol> stale = new ArrayList<>();
        if (os != null)
            for (Symbol sym : currentProgram.getSymbolTable().getSymbols(os))
                if (sym.getAddress().equals(site)) {
                    stale.add(sym);
                    DataTypeSymbol dts = HighFunctionDBUtil.readOverride(sym);
                    if (dts != null && dts.getDataType() instanceof FunctionDefinition) old = (FunctionDefinition) dts.getDataType();
                }
        FunctionDefinitionDataType def = new FunctionDefinitionDataType("fmt_" + site.toString());
        List<ParameterDefinition> ps = new ArrayList<>();
        ParameterDefinition[] oldArgs = old != null ? old.getArguments() : new ParameterDefinition[0];
        int stretShift = (old != null && oldArgs.length > 0 && oldArgs[0].getName().equals("stret")) ? 1 : 0;
        for (int i = 0; i <= fmtIdx + stretShift; i++) {
            if (i < oldArgs.length) ps.add(new ParameterDefinitionImpl(oldArgs[i].getName(), oldArgs[i].getDataType(), null));
            else ps.add(new ParameterDefinitionImpl(i == fmtIdx + stretShift ? "fmt" : "p" + i, ptr, null));
        }
        int n = 0, words = 0;
        Matcher m = SPEC.matcher(fmt);
        while (m.find()) {
            if (m.group(0).equals("%%")) continue;
            for (int g = 1; g <= 2; g++)
                if ("*".equals(m.group(g))) { ps.add(new ParameterDefinitionImpl("w" + (n++), IntegerDataType.dataType, null)); words++; }
            String conv = m.group(4), mod = m.group(3);
            boolean wide = "eEfFgGaA".contains(conv) || "ll".equals(mod) || "q".equals(mod);
            DataType t = "s@pP".contains(conv) ? ptr : u32;
            if (wide) {
                ps.add(new ParameterDefinitionImpl("a" + n + "_lo", u32, null));
                ps.add(new ParameterDefinitionImpl("a" + n + "_hi", u32, null));
                words += 2;
            } else {
                ps.add(new ParameterDefinitionImpl("a" + n, t, null));
                words++;
            }
            n++;
        }
        def.setArguments(ps.toArray(new ParameterDefinition[0]));
        def.setReturnType(old != null ? old.getReturnType()
                : kind.equals("_NSLog") ? VoidDataType.dataType
                : kind.startsWith("_") ? IntegerDataType.dataType : ptr);
        def.setVarArgs(false);
        for (Symbol sym : stale) sym.delete();
        HighFunctionDBUtil.writeOverride(f, site, def);
        stat("site typed: " + kind + (words == 0 ? " (no arguments)" : ""));
    }

    /** Constant string behind a varnode: a C string, or a CFString (cstr at +8) when cf. */
    String constString(Varnode v, boolean cf) {
        try {
            for (int hop = 0; hop < 6 && v != null; hop++) {
                if (v.isConstant() || v.isAddress()) return readStr(v.getOffset(), cf);
                PcodeOp def = v.getDef();
                if (def == null) return null;
                int oc = def.getOpcode();
                if (oc == PcodeOp.COPY || oc == PcodeOp.CAST) { v = def.getInput(0); continue; }
                if (oc == PcodeOp.PTRSUB && def.getInput(1).isConstant()) return readStr(def.getInput(1).getOffset(), cf);
                if (oc == PcodeOp.LOAD && def.getInput(1).isConstant()) {      // selref / pointer slot
                    long slot = def.getInput(1).getOffset();
                    long p = getInt(toAddr(slot)) & 0xffffffffL;
                    return readStr(p, cf);
                }
                return null;
            }
        } catch (Exception e) { }
        return null;
    }

    String readStr(long a, boolean cf) throws Exception {
        if (a < 0x1000 || a >= 0x90000) return null;
        long p = a;
        if (cf) {
            // CFString constant: isa, flags, cstr, length (in __cfstring); else a plain C string
            MemoryBlockCheck:
            {
                ghidra.program.model.mem.MemoryBlock b = currentProgram.getMemory().getBlock(toAddr(a));
                if (b != null && b.getName().contains("cfstring")) p = getInt(toAddr(a + 8)) & 0xffffffffL;
            }
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 1024; i++) {
            byte c = getByte(toAddr(p + i));
            if (c == 0) break;
            sb.append((char) (c & 0xff));
        }
        return sb.toString();
    }
}
