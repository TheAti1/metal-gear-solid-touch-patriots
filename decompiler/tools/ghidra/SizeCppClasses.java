/* Grow C++ class structs to their allocation size (LOG 2026-10-07 STEP 2).
 * ApplyCppTypes lays a class out from its `this` accesses only, so bytes no
 * method touches are missing (SoundResourceManager: 0x18 laid out, 0x24
 * allocated). `new T` allocates exactly sizeof(T), so the allocation size
 * from analysis/symbols/cpp_sizes.tsv is the true size. Never shrinks.
 * Run after ApplyCppTypes. Idempotent.
 */
import java.io.*;
import java.util.*;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.*;

public class SizeCppClasses extends GhidraScript {
    @Override
    protected void run() throws Exception {
        DataTypeManager dtm = currentProgram.getDataTypeManager();
        int grown = 0;
        try (BufferedReader r = new BufferedReader(new FileReader("analysis/symbols/cpp_sizes.tsv"))) {
            String l;
            while ((l = r.readLine()) != null) {
                if (l.startsWith("#") || l.startsWith("class\t") || l.isBlank()) continue;
                String[] p = l.split("\t");
                int size = Integer.decode(p[1]);
                List<DataType> found = new ArrayList<>();
                dtm.findDataTypes(p[0], found);
                for (DataType t : found) {
                    if (!(t instanceof Structure)) continue;
                    Structure st = (Structure) t;
                    if (st.getLength() < size) {
                        int was = st.getLength();
                        st.growStructure(size - was);
                        println(String.format("%s %s: 0x%x -> 0x%x", st.getCategoryPath(), p[0], was, st.getLength()));
                        grown++;
                    }
                    // name the trailing undefined bytes as the decompiler prints
                    // them (field_0xNN): the C header otherwise writes fieldK_0xNN
                    int end = 0;
                    for (DataTypeComponent c : st.getDefinedComponents())
                        end = Math.max(end, c.getOffset() + c.getLength());
                    for (int off = end; off < st.getLength(); off++) {
                        DataTypeComponent c = st.getComponentAt(off);
                        if (c != null && c.getDataType() == DataType.DEFAULT) {
                            st.replaceAtOffset(off, Undefined1DataType.dataType, 1,
                                    String.format("field_0x%x", off), "allocation-size bytes (cpp_sizes.tsv)");
                        }
                    }
                }
            }
        }
        println("SizeCppClasses: " + grown + " struct(s) grown");
    }
}
