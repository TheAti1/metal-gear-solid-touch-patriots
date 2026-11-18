/* Apply the ObjC-runtime-derived types (analysis/objc/types.spec, written by
 * tools/objc_types.py) to the MGSTUS Ghidra program:
 *
 *   1. STRUCT / CLASS  -> structure data types (pEneDat = EneDat, one struct
 *      per class holding inherited + own ivars at their real offsets).
 *   2. IVARVAR         -> the ObjC 2.0 "ivar offset variables" (e.g.
 *      EnemyBase::aiControl) become 4-byte CONSTANT ints. Ivar accesses are
 *      compiled as `*(self + *ivarOffsetVar)`; the decompiler only folds the
 *      offset and shows `self->field` when it may treat that load as a
 *      constant.
 *   3. METHOD          -> signatures: self as `<Class> *`, _cmd as sel, real
 *      parameter/return types. By-value structs are flattened into their
 *      scalar fields (that is how the armv6 soft-float ABI passes them);
 *      methods returning a by-value struct larger than 4 bytes are skipped.
 *
 * Usage:
 *     analyzeHeadless analysis/ghidra MGST -process MGSTUS -noanalysis \
 *         -scriptPath tools/ghidra -postScript ApplyObjcTypes.java \
 *         [types.spec path]
 * Idempotent.
 */
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import ghidra.app.cmd.function.ApplyFunctionSignatureCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.util.CodeUnitInsertionException;

public class ApplyObjcTypes extends GhidraScript {

    DataTypeManager dtm;
    final Map<String, Structure> structs = new LinkedHashMap<>();
    final Map<String, Structure> classStructs = new LinkedHashMap<>();
    final Map<String, Integer> structSize = new LinkedHashMap<>();
    final Set<String> keepExisting = new HashSet<>();
    boolean skipFields = false;

    int countFields(List<String[]> rows, String name) {
        int n = 0;
        boolean in = false;
        for (String[] p : rows) {
            if (p[0].equals("STRUCT")) in = p[1].equals(name);
            else if (!p[0].equals("FIELD")) in = false;
            else if (in) n++;
        }
        return n;
    }
    static final CategoryPath TYPES = new CategoryPath("/mgst");
    static final CategoryPath OBJC = new CategoryPath("/mgst/objc");

    @Override
    protected void run() throws Exception {
        dtm = currentProgram.getDataTypeManager();
        String[] args = getScriptArgs();
        File spec = new File(args.length > 0 ? args[0] : "analysis/objc/types.spec");
        List<String[]> rows = new ArrayList<>();
        try (BufferedReader r = new BufferedReader(new FileReader(spec))) {
            String line;
            while ((line = r.readLine()) != null) {
                if (!line.isEmpty()) rows.add(line.split("\t", -1));
            }
        }

        // ---- phase 1: empty structures (so pointers and by-value nesting resolve)
        Set<String> names = new HashSet<>();
        for (String[] p : rows) if (p[0].equals("STRUCT")) names.add(p[1]);
        for (String[] p : rows) {
            if (p[0].equals("STRUCT")) {
                if (p[3].equals("1")) printerr("union " + p[1] + " treated as struct");
                // never clobber a richer existing layout (e.g. the C++ class
                // structs ApplyCppTypes.java filled for Sound/SoundService/...;
                // the ObjC encodings only know them as opaque ^{Sound=})
                DataType ex = dtm.getDataType(TYPES, p[1]);
                if (ex instanceof Structure && ((Structure) ex).getNumDefinedComponents()
                        > countFields(rows, p[1]) && ex.getLength() >= Integer.parseInt(p[2])) {
                    keepExisting.add(p[1]);
                    structs.put(p[1], (Structure) ex);
                    structSize.put(p[1], ex.getLength());
                    println("kept richer existing layout: " + ex.getPathName());
                    continue;
                }
                Structure c = new StructureDataType(TYPES, p[1], Integer.parseInt(p[2]));
                structs.put(p[1], (Structure) dtm.resolve(c, DataTypeConflictHandler.REPLACE_HANDLER));
                structSize.put(p[1], Integer.parseInt(p[2]));
            } else if (p[0].equals("CLASS")) {
                String n = names.contains(p[1]) ? p[1] + "_obj" : p[1];
                Structure s = new StructureDataType(OBJC, n, Integer.parseInt(p[2]));
                classStructs.put(p[1], (Structure) dtm.resolve(s, DataTypeConflictHandler.REPLACE_HANDLER));
            }
        }

        // ---- phase 2: fields
        Structure cur = null;
        int nFields = 0;
        for (String[] p : rows) {
            switch (p[0]) {
                case "STRUCT":
                    if (keepExisting.contains(p[1])) { cur = null; skipFields = true; break; }
                    skipFields = false;
                    cur = structs.get(p[1]);
                    cur.replaceWith(new StructureDataType(TYPES, p[1], structSize.get(p[1])));
                    break;
                case "CLASS": {
                    skipFields = false;
                    cur = classStructs.get(p[1]);
                    Structure fresh = new StructureDataType(OBJC, cur.getName(), Integer.parseInt(p[2]));
                    fresh.replaceAtOffset(0, new PointerDataType(VoidDataType.dataType), 4, "isa", null);
                    cur.replaceWith(fresh);
                    break;
                }
                case "FIELD": {
                    if (skipFields) break;
                    DataType dt = type(p[3]);
                    int off = Integer.parseInt(p[1]);
                    cur.replaceAtOffset(off, dt, Math.max(dt.getLength(), 1), p[2], null);
                    nFields++;
                    break;
                }
                default:
                    cur = null;
                    skipFields = false;
            }
        }
        println("structs: " + structs.size() + ", class structs: " + classStructs.size()
                + ", fields: " + nFields);

        // ---- ivar offset variables -> constant ints
        int nVars = 0;
        for (String[] p : rows) {
            if (!p[0].equals("IVARVAR")) continue;
            Address a = toAddr(Long.parseLong(p[1].substring(2), 16));
            try {
                Data d = DataUtilities.createData(currentProgram, a, IntegerDataType.dataType, 4,
                        false, DataUtilities.ClearDataMode.CLEAR_ALL_CONFLICT_DATA);
                MutabilitySettingsDefinition.DEF.setChoice(d, MutabilitySettingsDefinition.CONSTANT);
                nVars++;
            } catch (CodeUnitInsertionException e) {
                printerr("ivar var " + p[1] + " " + p[2] + "." + p[3] + ": " + e.getMessage());
            }
        }
        println("ivar offset variables made constant: " + nVars);

        int nPtrs = 0;
        for (String[] p : rows) {
            if (!p[0].equals("IVARPTR")) continue;
            Address a = toAddr(Long.parseLong(p[1].substring(2), 16));
            try {
                Data d = DataUtilities.createData(currentProgram, a,
                        new PointerDataType(IntegerDataType.dataType), 4,
                        false, DataUtilities.ClearDataMode.CLEAR_ALL_CONFLICT_DATA);
                MutabilitySettingsDefinition.DEF.setChoice(d, MutabilitySettingsDefinition.CONSTANT);
                nPtrs++;
            } catch (CodeUnitInsertionException e) {
                printerr("ivar ptr " + p[1] + ": " + e.getMessage());
            }
        }
        println("ivar-offset-variable pointers made constant: " + nPtrs);

        // ---- method signatures
        int ok = 0, noFn = 0, skipped = 0, failed = 0;
        for (String[] p : rows) {
            if (!p[0].equals("METHOD")) continue;
            // METHOD class kind selector imp ret self sel args...
            String cls = p[1], kind = p[2], sel = p[3];
            Address a = toAddr(Long.decode(p[4]) & ~1L);
            Function fn = getFunctionAt(a);
            if (fn == null) { noFn++; continue; }
            String ret = p[5];
            if (byValueBig(ret)) { skipped++; continue; }
            List<ParameterDefinition> params = new ArrayList<>();
            DataType selfT = kind.equals("-") && classStructs.containsKey(cls)
                    ? new PointerDataType(classStructs.get(cls)) : new PointerDataType(VoidDataType.dataType);
            params.add(new ParameterDefinitionImpl("self", selfT, null));
            params.add(new ParameterDefinitionImpl("_cmd", new PointerDataType(VoidDataType.dataType), null));
            String[] kw = sel.split(":", -1);
            Set<String> used = new HashSet<>(List.of("self", "_cmd"));
            int argNo = 0;
            for (int i = 8; i < p.length; i++) {
                String base = argNo < kw.length && !kw[argNo].isEmpty() && sel.contains(":")
                        ? kw[argNo].replaceAll("[^A-Za-z0-9_]", "") : "";
                if (base.isEmpty() || Character.isDigit(base.charAt(0))) base = "arg" + argNo;
                argNo++;
                flatten(p[i], base, params, used);
            }
            try {
                FunctionDefinitionDataType def = new FunctionDefinitionDataType(fn.getName());
                def.setReturnType(retType(ret));
                def.setArguments(params.toArray(new ParameterDefinition[0]));
                ApplyFunctionSignatureCmd cmd = new ApplyFunctionSignatureCmd(a, def, SourceType.USER_DEFINED);
                if (cmd.applyTo(currentProgram, monitor)) ok++; else failed++;
            } catch (Exception e) {
                printerr("sig " + cls + " " + sel + ": " + e);
                failed++;
            }
        }
        println("method signatures applied: " + ok + ", no function at imp: " + noFn
                + ", skipped (sret): " + skipped + ", failed: " + failed);
    }

    boolean byValueBig(String t) {
        if (!t.startsWith("struct(")) return false;
        return structSize.getOrDefault(t.substring(7, t.length() - 1), 0) > 4;
    }

    DataType retType(String t) {
        if (t.startsWith("struct(")) return IntegerDataType.dataType;   // <= 4 bytes
        return type(t);
    }

    void flatten(String t, String name, List<ParameterDefinition> out, Set<String> used) {
        if (t.startsWith("struct(")) {
            Structure s = structs.get(t.substring(7, t.length() - 1));
            int k = 0;
            for (DataTypeComponent c : s.getDefinedComponents()) {
                flatten(typeString(c.getDataType()), name + "_" + (c.getFieldName() != null ? c.getFieldName() : "f" + k), out, used);
                k++;
            }
            return;
        }
        String n = name;
        int x = 2;
        while (!used.add(n)) n = name + x++;
        out.add(new ParameterDefinitionImpl(n, type(t), null));
    }

    String typeString(DataType dt) {
        if (dt instanceof Structure) return "struct(" + dt.getName() + ")";
        if (dt instanceof Pointer) return "ptr(void)";
        if (dt instanceof FloatDataType) return "f4";
        if (dt instanceof DoubleDataType) return "f8";
        if (dt instanceof ArrayDataType) return "ptr(void)";
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
            case "id":
            case "sel": return new PointerDataType(VoidDataType.dataType);
        }
        if (t.startsWith("ptr(")) return new PointerDataType(type(t.substring(4, t.length() - 1)));
        if (t.startsWith("struct(")) {
            Structure s = structs.get(t.substring(7, t.length() - 1));
            if (s == null) throw new IllegalStateException("unknown struct in " + t);
            return s;
        }
        if (t.startsWith("arr(")) {
            int comma = t.indexOf(',');
            int n = Integer.parseInt(t.substring(4, comma));
            DataType el = type(t.substring(comma + 1, t.length() - 1));
            return new ArrayDataType(el, n, Math.max(el.getLength(), 1));
        }
        throw new IllegalStateException("unknown type " + t);
    }
}
