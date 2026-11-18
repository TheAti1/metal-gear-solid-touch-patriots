/* Correct instance/static (`this`) on C++ member functions from an evidence
 * table (LOG 2026-10-07 STEP 2). Ghidra's demangler cannot know static-ness
 * (the Itanium mangling does not encode it); wrong guesses shift every
 * argument by one register, in the function AND in every decompiled caller.
 *
 *   analysis/symbols/cpp_this.tsv   addr, function, instance|static, evidence
 *
 * instance -> __thiscall (Ghidra adds `ClassName *this` as auto-parameter)
 * static   -> the compiler spec's default convention (no auto `this`)
 * Explicit parameters are kept; storage is recomputed (dynamic).
 *
 * Usage: analyzeHeadless analysis/ghidra MGST -process MGSTUS -noanalysis
 *          -scriptPath tools/ghidra -postScript FixCppThis.java   (idempotent)
 */
import java.io.*;
import java.util.*;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

public class FixCppThis extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String dflt = currentProgram.getCompilerSpec().getDefaultCallingConvention().getName();
        int changed = 0, same = 0;
        try (BufferedReader r = new BufferedReader(new FileReader("analysis/symbols/cpp_this.tsv"))) {
            String l;
            while ((l = r.readLine()) != null) {
                if (l.startsWith("#") || l.startsWith("addr\t") || l.isBlank()) continue;
                String[] p = l.split("\t");
                Function f = getFunctionAt(toAddr(Long.decode(p[0])));
                if (f == null) { printerr("no function at " + p[0]); continue; }
                boolean inst = p[2].equals("instance");
                boolean isThis = "__thiscall".equals(f.getCallingConventionName());
                if (inst == isThis) { same++; continue; }
                f.setCustomVariableStorage(false);
                f.setCallingConvention(inst ? "__thiscall" : dflt);
                f.setSignatureSource(SourceType.USER_DEFINED);
                println(String.format("%s %s -> %s", p[0], p[1], f.getSignature().getPrototypeString()));
                changed++;
            }
        }
        println("FixCppThis: " + changed + " changed, " + same + " already correct");
    }
}
