/* C++ class layouts for the SoundLibrary/AudioSupport code.
 *
 *   1. Every C++ class with __thiscall methods (Sound, SoundLabel,
 *      SoundManager, SoundService, SoundResourceManager, ALSound, AQSound, ...)
 *      gets its struct filled from the `this` accesses of ALL its methods
 *      (Ghidra's FillOutStructureHelper = "Auto Fill in Structure", run per
 *      method and accumulated; two passes so new field types propagate).
 *   2. SoundAPI_vtbl from __ZTV7ALSound (0x6943c): one function-pointer member
 *      per slot, named after the ALSound method in it; checked slot by slot
 *      against __ZTV7AQSound (0x69498). SoundAPI / ALSound / AQSound get it as
 *      `vptr` at offset 0. Runtime confirmation: analysis/dynamic/
 *      indirect_targets.tsv (every observed virtual target is ALSound::x or
 *      AQSound::x of the same slot).
 *   3. Sound's backend pointer (the field the virtual calls load; +0x10) is
 *      typed SoundAPI *, so they decompile as this->backend->vptr->play(...).
 *
 * Usage: analyzeHeadless ... -postScript ApplyCppTypes.java   (idempotent)
 */
import java.util.*;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.decompiler.util.FillOutStructureHelper;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.HighParam;
import ghidra.program.model.pcode.HighSymbol;
import ghidra.program.model.pcode.HighVariable;
import ghidra.program.model.symbol.Namespace;

public class ApplyCppTypes extends GhidraScript {

    static final long VT_AL = 0x6943c, VT_AL_END = 0x69484, VT_AQ = 0x69498;
    static final CategoryPath CPP = new CategoryPath("/mgst/cpp");
    DataTypeManager dtm;

    @Override
    protected void run() throws Exception {
        dtm = currentProgram.getDataTypeManager();

        // ---- collect classes: parent namespace of __thiscall functions
        Map<String, List<Function>> byClass = new TreeMap<>();
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            if (f.isThunk() || f.isExternal()) continue;
            if (!"__thiscall".equals(f.getCallingConventionName())) continue;
            Namespace ns = f.getParentNamespace();
            if (ns == null || ns.isGlobal()) continue;
            byClass.computeIfAbsent(ns.getName(), k -> new ArrayList<>()).add(f);
        }
        println("C++ classes with __thiscall methods: " + byClass.keySet());
        methodsOf.putAll(byClass);

        // ---- the struct each class namespace owns (what `this` points to):
        // turn Ghidra's 1-byte "not yet defined" placeholders into defined
        // 4-byte structs so FillOutStructureHelper extends them in place
        for (String cls : byClass.keySet()) {
            Namespace ns = byClass.get(cls).get(0).getParentNamespace();
            // fill exactly the struct the methods' `this` points to (with two
            // same-named structs, findOrCreateClassStruct may return the other
            // one and the fill never reaches the decompiled code)
            Structure st = null;
            for (Function mf : byClass.get(cls)) {
                if (mf.getParameterCount() == 0) continue;
                DataType pt = mf.getParameter(0).getDataType();
                if (pt instanceof Pointer && ((Pointer) pt).getDataType() instanceof Structure) {
                    st = (Structure) ((Pointer) pt).getDataType();
                    break;
                }
            }
            if (st == null) st = ghidra.program.model.listing.VariableUtilities.findOrCreateClassStruct(
                    (ghidra.program.model.listing.GhidraClass) (ns instanceof ghidra.program.model.listing.GhidraClass ? ns
                            : currentProgram.getSymbolTable().convertNamespaceToClass(ns)), dtm);
            if (st.isNotYetDefined() || st.getLength() <= 1) {
                StructureDataType fresh = new StructureDataType(st.getCategoryPath(), st.getName(), 4);
                st.replaceWith(fresh);
            }
            classStruct.put(cls, st);
        }

        Set<String> opt = new HashSet<>(Arrays.asList(getScriptArgs()));
        // ---- vtable
        Structure vtbl = opt.contains("novtable") ? null : buildVtable();

        // ---- fill class structs from `this` accesses
        DecompInterface d = new DecompInterface();
        DecompileOptions o = new DecompileOptions();
        d.setOptions(o);
        d.toggleSyntaxTree(true);
        d.openProgram(currentProgram);
        for (int pass = 1; pass <= (opt.contains("nofill") ? 0 : 2); pass++) {
            for (Map.Entry<String, List<Function>> e : byClass.entrySet()) {
                int grown = 0;
                for (Function f : e.getValue()) {
                    Structure s = fillFrom(f, d);
                    if (s != null) grown++;
                }
                if (pass == 2) {
                    DataType cls = classType(e.getKey());
                    println(String.format("class %-22s methods %3d  size %4s  fields %3s", e.getKey(),
                            e.getValue().size(), cls == null ? "?" : "0x" + Integer.toHexString(cls.getLength()),
                            cls instanceof Structure ? ((Structure) cls).getNumDefinedComponents() : "?"));
                }
            }
            sanitize();
            if (pass == 1 && vtbl != null) applyVptrs(vtbl);
        }
        d.dispose();
        if (vtbl != null) { applyVptrs(vtbl); typeBackend(); }
    }

    final Map<String, List<Function>> methodsOf = new HashMap<>();
    final Map<String, Structure> classStruct = new HashMap<>();

    /** The struct the class's methods actually use as `this`. */
    /** FillOutStructureHelper writes class structs BY VALUE into 4-byte
     *  slots while the class is still a placeholder (e.g. ALSound +0x24
     *  SoundLabel); once the class grows the layout overlaps and 28 methods
     *  failed to decompile. Such fields are pointers. */
    void sanitize() {
        int fixed = 0;
        int tx = currentProgram.startTransaction("sanitize C++ fields");
        try {
            for (Structure st : classStruct.values()) {
                for (DataTypeComponent c : st.getDefinedComponents()) {
                    DataType t = c.getDataType();
                    if (t instanceof Structure && (methodsOf.containsKey(t.getName()) || t.getLength() > c.getLength()
                            || ((Structure) t).isNotYetDefined())) {
                        st.replaceAtOffset(c.getOffset(), new PointerDataType(t), 4, c.getFieldName(), c.getComment());
                        fixed++;
                    }
                }
            }
        } finally {
            currentProgram.endTransaction(tx, true);
        }
        println("by-value class fields turned into pointers: " + fixed);
    }

    DataType classType(String name) {
        if (classStruct.containsKey(name)) return classStruct.get(name);
        List<Function> fs = methodsOf.get(name);
        if (fs != null) {
            for (Function f : fs) {
                if (f.getParameterCount() == 0) continue;
                DataType t = f.getParameter(0).getDataType();
                if (t instanceof Pointer && ((Pointer) t).getDataType() instanceof Structure) {
                    return ((Pointer) t).getDataType();
                }
            }
        }
        for (Iterator<DataType> it = dtm.getAllDataTypes(); it.hasNext(); ) {
            DataType t = it.next();
            if (t instanceof Structure && t.getName().equals(name) && !t.getCategoryPath().getPath().startsWith("/mgst/objc")) {
                return t;
            }
        }
        return null;
    }

    Structure fillFrom(Function f, DecompInterface d) throws Exception {
        DecompileResults r = d.decompileFunction(f, 120, monitor);
        if (!r.decompileCompleted()) return null;
        HighFunction hf = r.getHighFunction();
        HighVariable thisVar = null;
        for (int i = 0; i < hf.getLocalSymbolMap().getNumParams(); i++) {
            HighSymbol s = hf.getLocalSymbolMap().getParamSymbol(i);
            if (s != null && s.getName().equals("this")) { thisVar = s.getHighVariable(); break; }
        }
        if (thisVar == null) return null;
        DataType dt = thisVar.getDataType();
        if (!(dt instanceof Pointer)) return null;
        DataType pointed = ((Pointer) dt).getDataType();
        if (!(pointed instanceof Structure)) return null;
        FillOutStructureHelper h = new FillOutStructureHelper(currentProgram, monitor);
        // Ghidra's class placeholders are 1-byte "not yet defined" structs the
        // helper will not extend: build a fresh one for those, extend otherwise.
        boolean fresh = false;
        Structure filled = h.processStructure(thisVar, f, fresh, true, d);
        if (filled == null) return null;
        Structure existing = (Structure) pointed;
        int tx = currentProgram.startTransaction("fill " + existing.getName());
        try {
            // field-by-field: the fresh struct may point at itself, which a
            // wholesale replaceWith() rejects ("can't contain itself")
            if (filled.getLength() > existing.getLength()) {
                if (existing.isNotYetDefined() || existing.getLength() <= 1) {
                    existing.deleteAll();
                    existing.growStructure(filled.getLength());
                } else {
                    existing.growStructure(filled.getLength() - existing.getLength());
                }
            }
            for (DataTypeComponent c : filled.getDefinedComponents()) {
                DataType t = c.getDataType();
                if (t instanceof Pointer && ((Pointer) t).getDataType() != null
                        && ((Pointer) t).getDataType().getName().equals(filled.getName())) {
                    t = new PointerDataType(existing);
                }
                if (t.getName().equals(filled.getName())) continue;
                // a C++ class struct is never a by-value field here (the fill
                // guesses by-value for 4-byte slots while the class is still a
                // placeholder; once the class grows, the layout overlaps and
                // the decompiler fails) - it is a pointer
                if (t instanceof Structure && methodsOf.containsKey(t.getName())) {
                    t = new PointerDataType(t);
                }
                DataTypeComponent cur = existing.getComponentAt(c.getOffset());
                boolean free = cur == null || cur.getDataType() == DataType.DEFAULT
                        || cur.getDataType().getName().startsWith("undefined");
                if (!free || c.getOffset() + c.getLength() > existing.getLength()) continue;
                try {
                    existing.replaceAtOffset(c.getOffset(), t, c.getLength(), c.getFieldName(), null);
                } catch (IllegalArgumentException ex) {
                    // overlapping/self-referencing component: leave undefined
                }
            }
        } finally {
            currentProgram.endTransaction(tx, true);
        }
        return existing;
    }

    Structure buildVtable() throws Exception {
        int n = (int) ((VT_AL_END - VT_AL) / 4) - 2;
        StructureDataType vt = new StructureDataType(CPP, "SoundAPI_vtbl", 0);
        int mismatches = 0;
        for (int i = 0; i < n; i++) {
            long pAL = getInt(toAddr(VT_AL + 8 + 4L * i)) & 0xfffffffeL;
            long pAQ = getInt(toAddr(VT_AQ + 8 + 4L * i)) & 0xfffffffeL;
            Function fAL = getFunctionAt(toAddr(pAL));
            Function fAQ = getFunctionAt(toAddr(pAQ));
            String nAL = fAL == null ? "slot" + i : fAL.getName();
            String nAQ = fAQ == null ? "?" : fAQ.getName();
            if (!nAL.equals(nAQ)) mismatches++;
            DataType fp = new PointerDataType(VoidDataType.dataType);
            if (fAL != null) {
                FunctionDefinitionDataType fd = new FunctionDefinitionDataType(fAL, false);
                fd.setName("SoundAPI_" + nAL + "_t");
                // slot type takes the abstract base, not ALSound *
                ParameterDefinition[] args = fd.getArguments();
                if (args.length > 0) {
                    DataType base = dtm.resolve(new StructureDataType(CPP, "SoundAPI", 4),
                            DataTypeConflictHandler.KEEP_HANDLER);
                    args[0] = new ParameterDefinitionImpl("this", new PointerDataType(base), null);
                    fd.setArguments(args);
                }
                fd.setCategoryPath(CPP);
                fp = new PointerDataType(dtm.resolve(fd, DataTypeConflictHandler.REPLACE_HANDLER));
            }
            String fname = nAL;
            int k = 2;
            while (vt.getComponents().length > 0 && hasField(vt, fname)) fname = nAL + "_" + k++;
            vt.add(fp, 4, fname, String.format("slot %d (+0x%x): ALSound::%s / AQSound::%s", i, 4 * i, nAL, nAQ));
        }
        Structure r = (Structure) dtm.resolve(vt, DataTypeConflictHandler.REPLACE_HANDLER);
        println("SoundAPI_vtbl: " + n + " slots, ALSound/AQSound name mismatches: " + mismatches);
        return r;
    }

    boolean hasField(Structure s, String n) {
        for (DataTypeComponent c : s.getComponents()) if (n.equals(c.getFieldName())) return true;
        return false;
    }

    void applyVptrs(Structure vtbl) {
        for (String cls : new String[]{"SoundAPI", "ALSound", "AQSound"}) {
            DataType t = classType(cls);
            Structure s;
            if (t instanceof Structure) {
                s = (Structure) t;
            } else {
                s = (Structure) dtm.resolve(new StructureDataType(CPP, cls, 4), DataTypeConflictHandler.KEEP_HANDLER);
            }
            if (s.getLength() < 4) s.growStructure(4 - s.getLength());
            s.replaceAtOffset(0, new PointerDataType(vtbl), 4, "vptr", "virtual table (SoundAPI)");
        }
    }

    void typeBackend() {
        DataType snd = classType("Sound");
        DataType api = classType("SoundAPI");
        if (!(snd instanceof Structure) || api == null) { printerr("Sound/SoundAPI missing"); return; }
        Structure s = (Structure) snd;
        if (s.getLength() < 0x14) { printerr("Sound too small: " + s.getLength()); return; }
        s.replaceAtOffset(0x10, new PointerDataType(api), 4, "backend",
                "SoundAPI * (ALSound = OpenAL, AQSound = AudioQueue); runtime-confirmed");
        println("Sound.backend typed SoundAPI * at +0x10");
    }
}
