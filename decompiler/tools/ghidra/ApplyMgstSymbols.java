/* Apply the recovered MGSTUS symbol table to a freshly imported program.
 *
 * Runs as a -preScript, before auto-analysis, because the single most
 * important thing it does is set the TMode context register. MGSTUS is 1388
 * Thumb functions to 7 ARM; if analysis starts without knowing that, Ghidra
 * decodes Thumb halfwords as ARM words and produces plausible-looking
 * garbage that is worse than no output. Seeding TMode plus a disassembly
 * seed at every known entry point makes the subsequent auto-analysis correct
 * by construction rather than something we clean up afterwards.
 *
 * Input TSV (from tools/export_ghidra_symbols.py):
 *     address <TAB> thumb(0|1) <TAB> source_file <TAB> name
 *
 * Usage:
 *     analyzeHeadless <proj> <name> -import MGSTUS \
 *         -scriptPath tools/ghidra \
 *         -preScript ApplyMgstSymbols.java /abs/path/ghidra_symbols.tsv
 */
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;

import ghidra.app.script.GhidraScript;
import ghidra.framework.options.OptionType;
import ghidra.framework.options.Options;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Program;
import ghidra.program.model.symbol.SourceType;

public class ApplyMgstSymbols extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            println("ERROR: expected path to ghidra_symbols.tsv");
            return;
        }
        List<String> lines = Files.readAllLines(Paths.get(args[0]),
                                                StandardCharsets.UTF_8);

        // Ghidra's "Non-Returning Functions - Discovered" analyzer reliably
        // misfires on _objc_msgSend in this binary: it sees the tail-call
        // pattern the compiler emits for ObjC dispatch, concludes msgSend
        // never returns, and truncates the caller at its first message send.
        // On an Objective-C game that silently guts most of the codebase, so
        // the analyzer is turned off here rather than repaired afterwards —
        // once bad flow is baked in, re-flowing is far messier than
        // preventing it.
        // Match the analyzer's own toggle exactly. A substring match also hits
        // its sub-options — including an INT threshold — and setBoolean on
        // those throws IllegalStateException, which aborts this whole script
        // before a single symbol gets applied.
        Options analysis = currentProgram.getOptions(Program.ANALYSIS_PROPERTIES);
        final String NORET = "Non-Returning Functions - Discovered";
        for (String opt : analysis.getOptionNames()) {
            if (opt.equals(NORET)
                    && analysis.getType(opt) == OptionType.BOOLEAN_TYPE) {
                analysis.setBoolean(opt, false);
                println("Disabled analyzer option: " + opt);
            }
        }

        Register tmode = currentProgram.getLanguage().getRegister("TMode");
        if (tmode == null) {
            println("WARNING: no TMode register - is this an ARM program?");
        }

        int applied = 0, thumbSet = 0, named = 0, failed = 0, tmodeFail = 0;

        // PASS 1 - context only, no disassembly.
        //
        // Setting TMode and disassembling in the same loop is self-defeating:
        // disassemble() follows flow and decodes downstream functions, and
        // once an instruction exists at an address its context register can no
        // longer be changed ("Context register change conflicts"). Everything
        // reached by flow before its own turn came up was therefore locked to
        // whatever mode it was reached in. Harmless for the 1388 Thumb
        // functions, but it silently locked the 7 ARM runtime helpers
        // (___switch8, VFP save/restore) to Thumb and decoded them as garbage.
        // Seeding all context first makes the modes authoritative.
        if (tmode != null) {
            for (String line : lines) {
                if (line.isEmpty() || line.startsWith("#")) {
                    continue;
                }
                String[] f = line.split("\t", -1);
                if (f.length < 4) {
                    continue;
                }
                try {
                    Address a = toAddr(Long.decode(f[0]));
                    boolean th = "1".equals(f[1]);
                    currentProgram.getProgramContext().setValue(
                        tmode, a, a, th ? BigInteger.ONE : BigInteger.ZERO);
                    if (th) {
                        thumbSet++;
                    }
                } catch (Exception e) {
                    tmodeFail++;
                }
            }
        }

        // PASS 2 - disassemble, create and name.
        for (String line : lines) {
            if (line.isEmpty() || line.startsWith("#")) {
                continue;
            }
            String[] f = line.split("\t", -1);
            if (f.length < 4) {
                continue;
            }
            long addrVal;
            try {
                addrVal = Long.decode(f[0]);
            } catch (NumberFormatException e) {
                continue;
            }
            boolean isThumb = "1".equals(f[1]);
            String srcFile = f[2];
            String name = f[3];

            Address addr = toAddr(addrVal);
            if (addr == null) {
                failed++;
                continue;
            }

            // Seed disassembly at the entry point; TMode is already correct
            // for every known address from pass 1.
            disassemble(addr);

            // Create the function if analysis has not already.
            Function fn = getFunctionAt(addr);
            if (fn == null) {
                fn = createFunction(addr, name);
            }

            if (fn != null) {
                // Objective-C selectors contain characters Ghidra rejects in
                // symbol names ("-[Gekko appearPoint]"), so normalise to the
                // same underscore convention Ghidra's own ObjC analyzer uses
                // instead of letting 1200+ renames throw and lose the name.
                String safe = name.replaceAll("[^A-Za-z0-9_$:.]", "_");
                if (!safe.equals(fn.getName())) {
                    try {
                        fn.setName(safe, SourceType.IMPORTED);
                        named++;
                    } catch (Exception e) {
                        failed++;
                    }
                } else {
                    named++;   // already correctly named by an analyzer
                }
                // Record provenance: which original .mm/.m this came from.
                // Kept on ONE line: the demangler analyzer appends its own
                // signature line to this comment later, and anything reading
                // it back must take only the first line.
                if (!srcFile.isEmpty()) {
                    fn.setComment("Original source: " + srcFile);
                }
                applied++;
            } else {
                failed++;
            }

            if (monitor.isCancelled()) {
                break;
            }
        }

        println("=== MGST symbol import ===");
        println("  functions touched : " + applied);
        println("  named             : " + named);
        println("  TMode=Thumb set   : " + thumbSet);
        println("  TMode failures    : " + tmodeFail);
        println("  name failures     : " + failed);
    }
}
