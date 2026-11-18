/* Retype individual decompiler variables from analysis/symbols/var_types.tsv
 * (func_addr <TAB> variable <TAB> type <TAB> reason). For variables whose type
 * Ghidra inferred wrongly and where the wrong type changes semantics, e.g. an
 * int loop counter merged with a float (LOG 2026-10-08: drawEnemyWaitMeter
 * compared the counter with float ==, which under the device's flush-to-zero
 * treats small integers' bit patterns (denormals) as 0). The binary shows the
 * real operation (cmp r5, r8); the reason column cites it.
 * The variable is committed as a user-defined local of the given type
 * (HighFunctionDBUtil.updateDBVariable). Idempotent: a row whose variable no
 * longer exists under that name is reported as "not found (already applied?)".
 */
import java.io.*;
import java.util.*;

import ghidra.app.decompiler.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.pcode.*;
import ghidra.program.model.symbol.SourceType;

public class ApplyVarTypes extends GhidraScript {
    @Override
    protected void run() throws Exception {
        File tsv = new File(getScriptArgs().length > 0 ? getScriptArgs()[0] : "analysis/symbols/var_types.tsv");
        Map<String, DataType> types = new HashMap<>();
        types.put("int", IntegerDataType.dataType);
        types.put("uint", UnsignedIntegerDataType.dataType);
        types.put("float", FloatDataType.dataType);
        types.put("short", ShortDataType.dataType);
        types.put("char", CharDataType.dataType);
        DecompInterface d = new DecompInterface();
        d.setOptions(new DecompileOptions());
        d.openProgram(currentProgram);
        Map<String, Integer> stats = new TreeMap<>();
        for (String line : java.nio.file.Files.readAllLines(tsv.toPath())) {
            if (line.isBlank() || line.startsWith("#") || line.startsWith("func")) continue;
            String[] p = line.split("\t");
            Function f = getFunctionAt(toAddr(Long.decode(p[0])));
            DataType ty = types.get(p[2]);
            if (f == null || ty == null) { stats.merge("bad row", 1, Integer::sum); println("bad row: " + line); continue; }
            DecompileResults res = d.decompileFunction(f, 60, monitor);
            HighFunction hf = res.getHighFunction();
            if (hf == null) { stats.merge("decompile failed", 1, Integer::sum); continue; }
            HighSymbol hit = null;
            Iterator<HighSymbol> it = hf.getLocalSymbolMap().getSymbols();
            while (it.hasNext()) {
                HighSymbol s = it.next();
                if (s.getName().equals(p[1])) hit = s;
            }
            if (hit == null) { stats.merge("not found (already applied?)", 1, Integer::sum); println("not found: " + line); continue; }
            HighFunctionDBUtil.updateDBVariable(hit, null, ty, SourceType.USER_DEFINED);
            stats.merge("retyped", 1, Integer::sum);
            println("retyped " + p[0] + " " + p[1] + " -> " + p[2]);
        }
        println("ApplyVarTypes: " + stats);
    }
}
