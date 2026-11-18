/* One definition per struct name for the compilable header.
 *   - C++ classes (functions in the namespace with __thiscall): the struct
 *     their `this` points to wins (the layout ApplyCppTypes.java filled).
 *   - everything else: the /mgst definition (from the binary's own ObjC type
 *     encodings, tools/objc_types.py) wins - it is authoritative for THIS
 *     binary's layout (e.g. tagBITMAPFILEHEADER is 16 bytes here, not a
 *     packed 14/22-byte variant from a generic archive).
 *   - no /mgst and no class owner: left alone (reported).
 * Usage: analyzeHeadless ... -postScript FixDuplicateTypes.java  (idempotent)
 */
import java.util.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.Function;

public class FixDuplicateTypes extends GhidraScript {
    @Override
    protected void run() throws Exception {
        DataTypeManager dtm = currentProgram.getDataTypeManager();
        Map<String, DataType> classThis = new HashMap<>();
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            if (!"__thiscall".equals(f.getCallingConventionName()) || f.getParameterCount() == 0) continue;
            DataType t = f.getParameter(0).getDataType();
            if (t instanceof Pointer && ((Pointer) t).getDataType() instanceof Structure) {
                DataType s = ((Pointer) t).getDataType();
                classThis.merge(s.getName(), s, (x, y) -> x.getLength() >= y.getLength() ? x : y);
            }
        }
        Map<String, List<DataType>> byName = new HashMap<>();
        for (Iterator<DataType> it = dtm.getAllDataTypes(); it.hasNext(); ) {
            DataType t = it.next();
            if (t instanceof Structure) byName.computeIfAbsent(t.getName(), k -> new ArrayList<>()).add(t);
        }
        int fixed = 0, left = 0;
        for (Map.Entry<String, List<DataType>> e : byName.entrySet()) {
            if (e.getValue().size() < 2) continue;
            // most defined fields wins; ties -> the struct `this` uses -> /mgst
            DataType thisT = classThis.get(e.getKey());
            DataType keep = null;
            int best = -1;
            for (DataType t : e.getValue()) {
                int score = ((Structure) t).getNumDefinedComponents() * 4
                        + (thisT != null && t.getPathName().equals(thisT.getPathName()) ? 2 : 0)
                        + (t.getCategoryPath().getPath().equals("/mgst") ? 1 : 0);
                if (score > best) { best = score; keep = t; }
            }
            if (keep == null) { println("left alone: " + e.getKey() + " " + e.getValue()); left++; continue; }
            for (DataType t : new ArrayList<>(e.getValue())) {
                if (t.equals(keep) || t.getPathName().equals(keep.getPathName())) continue;
                println("replace " + t.getPathName() + " (" + t.getLength() + ") -> " + keep.getPathName() + " (" + keep.getLength() + ")");
                dtm.replaceDataType(t, keep, true);
                fixed++;
            }
        }
        println("duplicate struct names resolved: " + fixed + ", left alone: " + left);
    }
}
