/* Teach Ghidra's decompiler what MGST's compiler-runtime float/int helpers
 * DO, so `___addsf3vfp(a,b)` decompiles as `a + b` (float typed) instead of an
 * opaque call on `undefined4`.
 *
 * MGSTUS is armv6 with -mfloat-abi=soft, so every float operation is a call
 * into libSystem's compiler-rt (`___addsf3vfp` etc.): floats travel in r0/r1
 * (r0:r1 and r2:r3 for doubles, low word in the lower register), the result
 * comes back in r0 (r0:r1). Comparisons return 0/1 in r0 (compiler-rt's VFP
 * variants; NOT the libgcc -1/0/1 convention). A program-scoped callfixup
 * (same mechanism as InstallSwitchCallFixup.java) replaces the call with
 * equivalent p-code; nothing outside this program's own database is touched.
 *
 * Usage:
 *     analyzeHeadless <proj_dir> <proj_name> -process MGSTUS -noanalysis \
 *         -scriptPath tools/ghidra -postScript InstallSoftFloatCallFixup.java
 * Idempotent.
 */
import java.util.LinkedHashMap;
import java.util.Map;

import ghidra.app.script.GhidraScript;
import ghidra.program.database.SpecExtension;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Symbol;

public class InstallSoftFloatCallFixup extends GhidraScript {

    static final String D_A = "local a:8; a[0,32] = r0; a[32,32] = r1;\n";
    static final String D_AB = D_A + "local b:8; b[0,32] = r2; b[32,32] = r3;\n";
    static final String RET_D = "r0 = res:4; r1 = res(4);\n";

    static Map<String, String> table() {
        Map<String, String> t = new LinkedHashMap<>();
        // float arithmetic
        t.put("___addsf3vfp", "r0 = r0 f+ r1;");
        t.put("___subsf3vfp", "r0 = r0 f- r1;");
        t.put("___mulsf3vfp", "r0 = r0 f* r1;");
        t.put("___divsf3vfp", "r0 = r0 f/ r1;");
        // float compares: 1 if true
        t.put("___ltsf2vfp", "r0 = zext(r0 f< r1);");
        t.put("___gtsf2vfp", "r0 = zext(r0 f> r1);");
        t.put("___gesf2vfp", "r0 = zext(r0 f>= r1);");
        t.put("___lesf2vfp", "r0 = zext(r0 f<= r1);");
        t.put("___eqsf2vfp", "r0 = zext(r0 f== r1);");
        t.put("___nesf2vfp", "r0 = zext(r0 f!= r1);");
        t.put("___unordsf2vfp", "r0 = zext(nan(r0) || nan(r1));");
        // int <-> float
        t.put("___floatsisfvfp", "r0 = int2float(r0);");
        t.put("___floatunssisfvfp", "local t:8 = zext(r0); r0 = int2float(t);");
        t.put("___fixsfsivfp", "r0 = trunc(r0);");
        t.put("___fixunssfsivfp", "local t:8 = trunc(r0); r0 = t:4;");
        // double arithmetic
        t.put("___adddf3vfp", D_AB + "local res:8 = a f+ b;\n" + RET_D);
        t.put("___subdf3vfp", D_AB + "local res:8 = a f- b;\n" + RET_D);
        t.put("___muldf3vfp", D_AB + "local res:8 = a f* b;\n" + RET_D);
        t.put("___divdf3vfp", D_AB + "local res:8 = a f/ b;\n" + RET_D);
        // double compares
        t.put("___ltdf2vfp", D_AB + "r0 = zext(a f< b);");
        t.put("___gtdf2vfp", D_AB + "r0 = zext(a f> b);");
        t.put("___gedf2vfp", D_AB + "r0 = zext(a f>= b);");
        t.put("___ledf2vfp", D_AB + "r0 = zext(a f<= b);");
        t.put("___eqdf2vfp", D_AB + "r0 = zext(a f== b);");
        t.put("___nedf2vfp", D_AB + "r0 = zext(a f!= b);");
        t.put("___unorddf2vfp", D_AB + "r0 = zext(nan(a) || nan(b));");
        // conversions with doubles
        t.put("___extendsfdf2vfp", "local res:8 = float2float(r0);\n" + RET_D);
        t.put("___truncdfsf2vfp", D_A + "r0 = float2float(a);");
        t.put("___floatsidfvfp", "local res:8 = int2float(r0);\n" + RET_D);
        t.put("___floatunssidfvfp", "local t:8 = zext(r0); local res:8 = int2float(t);\n" + RET_D);
        t.put("___fixdfsivfp", D_A + "r0 = trunc(a);");
        t.put("___fixunsdfsivfp", D_A + "local t:8 = trunc(a); r0 = t:4;");
        // integer division helpers
        t.put("___divsi3", "r0 = r0 s/ r1;");
        t.put("___modsi3", "r0 = r0 s% r1;");
        t.put("___udivsi3", "r0 = r0 / r1;");
        t.put("___umodsi3", "r0 = r0 % r1;");
        // VFP callee-saved register spill (vpush/vpop {d8-d15}; ARM-mode
        // libgcc helpers): they touch only SP and d8-d15. As ordinary calls
        // Ghidra assumed r0-r3 clobbered and lost the caller's live arguments
        // (Sound::ready's param_1 became `extraout_r1`, LOG 2026-10-08).
        t.put("___save_vfp_d8_d15_regs", "sp = sp - 64;");
        t.put("___restore_vfp_d8_d15_regs", "sp = sp + 64;");
        return t;
    }

    @Override
    public void run() throws Exception {
        SpecExtension ext = new SpecExtension(currentProgram);
        int attached = 0, missing = 0;
        for (Map.Entry<String, String> e : table().entrySet()) {
            String name = e.getKey();
            String fx = "mgst" + name;
            boolean found = false;
            for (Symbol sym : currentProgram.getSymbolTable().getSymbols(name)) {
                Function fn = currentProgram.getFunctionManager().getFunctionAt(sym.getAddress());
                if (fn == null) {
                    println("WARNING: no function object for " + name + " @ " + sym.getAddress());
                    continue;
                }
                String xml = "<callfixup name=\"" + fx + "\">\n"
                    + "  <target name=\"" + name + "\"/>\n"
                    + "  <pcode><body><![CDATA[\n" + e.getValue() + "\n]]></body></pcode>\n"
                    + "</callfixup>\n";
                ext.addReplaceCompilerSpecExtension(xml, monitor);
                fn.setCallFixup(fx);
                println("  " + name + " @ " + fn.getEntryPoint()
                        + (fn.isThunk() ? " (thunk)" : "") + " -> " + fx);
                attached++;
                found = true;
            }
            if (!found) {
                missing++;
                println("  (absent in this binary: " + name + ")");
            }
        }
        println("Attached " + attached + " soft-float/int helper fixups, " + missing + " names absent.");
    }
}
