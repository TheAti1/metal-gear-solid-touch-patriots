/* Export decompiled C for MGSTUS, grouped by original source file.
 *
 * Runs as a -postScript after auto-analysis. Because the STABS gave us the
 * original translation-unit layout, we can write one .c per original .mm/.m
 * instead of a flat dump of 1388 functions. That mirrors the structure we are
 * going to reimplement against, so a ported file can be diffed directly
 * against the decompilation of the file it came from.
 *
 * Usage:
 *     -postScript ExportMgstDecompilation.java /abs/out/dir [timeoutSeconds]
 */
import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

public class ExportMgstDecompilation extends GhidraScript {

    private static final String SRC_TAG = "Original source: ";

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            println("ERROR: expected output directory");
            return;
        }
        File outDir = new File(args[0]);
        outDir.mkdirs();
        int timeout = args.length > 1 ? Integer.parseInt(args[1]) : 60;

        DecompInterface decomp = new DecompInterface();
        decomp.setOptions(new DecompileOptions());
        if (!decomp.openProgram(currentProgram)) {
            println("ERROR: could not open program for decompilation");
            return;
        }

        // Bucket functions by the source file recorded in the plate comment.
        Map<String, List<Function>> byFile = new TreeMap<>();
        FunctionIterator it = currentProgram.getFunctionManager()
                                            .getFunctions(true);
        int total = 0;
        List<Function> thunks = new ArrayList<>();
        while (it.hasNext()) {
            Function f = it.next();
            // dyld __symbol_stub4 entries made thunks by FixSplitsAndStubs.java:
            // linker glue, not source. Listed in _imports.txt, not decompiled
            // (decompiling them produced 187 bogus "Could not recover
            // jumptable" warnings - one per `ldr pc` stub).
            if (f.isThunk()) {
                thunks.add(f);
                continue;
            }
            String c = f.getComment();
            String src = "_unattributed";
            if (c != null && c.startsWith(SRC_TAG)) {
                // First line only. Ghidra's demangler analyzer appends the
                // demangled signature as an extra line on this same comment,
                // and folding that into the key produced filenames with
                // embedded newlines and one bucket per C++ function.
                String first = c.substring(SRC_TAG.length()).split("\\R", 2)[0];
                src = first.trim();
            }
            byFile.computeIfAbsent(src, k -> new ArrayList<>()).add(f);
            total++;
        }
        try (java.io.PrintWriter pw = new java.io.PrintWriter(new File(outDir, "_imports.txt"))) {
            pw.println("# dyld symbol stubs (thunks to imported functions), not decompiled");
            for (Function t : thunks) {
                Function tgt = t.getThunkedFunction(true);
                pw.println(t.getEntryPoint() + "\t" + t.getName() + "\t-> "
                        + (tgt != null ? tgt.getName(true) : "?"));
            }
        }
        println("Thunks listed in _imports.txt: " + thunks.size());
        println("Decompiling " + total + " functions across "
                + byFile.size() + " source files...");

        Map<String, Integer> stats = new HashMap<>();
        int ok = 0, fail = 0;

        for (Map.Entry<String, List<Function>> e : byFile.entrySet()) {
            // Classes/Enemies/Gekko.mm -> Classes_Enemies_Gekko.mm.c
            String flat = e.getKey().replaceAll("[/\\\\]", "_") + ".c";
            File out = new File(outDir, flat);

            try (PrintWriter w = new PrintWriter(out, StandardCharsets.UTF_8)) {
                w.println("/* Decompiled from MGSTUS (Metal Gear Solid Touch v2.3.0)");
                w.println(" * Original source file: " + e.getKey());
                w.println(" * Functions: " + e.getValue().size());
                w.println(" *");
                w.println(" * Ghidra decompiler output. Treat as evidence, not as");
                w.println(" * source: names come from the shipped symbol table but");
                w.println(" * types, locals and control flow are reconstructed.");
                w.println(" */");
                w.println();

                for (Function f : e.getValue()) {
                    if (monitor.isCancelled()) {
                        break;
                    }
                    DecompileResults r = decomp.decompileFunction(f, timeout, monitor);
                    if (r != null && r.decompileCompleted()
                            && r.getDecompiledFunction() != null) {
                        w.println("/* " + f.getEntryPoint() + "  "
                                  + f.getName() + " */");
                        w.println(r.getDecompiledFunction().getC());
                        w.println();
                        ok++;
                    } else {
                        String msg = (r == null) ? "null result" : r.getErrorMessage();
                        w.println("/* FAILED: " + f.getName() + " @ "
                                  + f.getEntryPoint() + " - " + msg + " */");
                        w.println();
                        fail++;
                    }
                }
            }
            stats.put(e.getKey(), e.getValue().size());
        }

        decomp.dispose();
        println("=== decompilation export ===");
        println("  output dir : " + outDir.getAbsolutePath());
        println("  succeeded  : " + ok);
        println("  failed     : " + fail);
    }
}
