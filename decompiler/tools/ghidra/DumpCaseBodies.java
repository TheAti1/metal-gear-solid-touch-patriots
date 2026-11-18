/* For each resolved switch-table case target belonging to a chosen set of
 * callers, walk forward N instructions (Ghidra's own validated listing, not
 * a separate Capstone pass) and print them. Used to read actual case-handler
 * semantics (timer constants, animation-index stores) now that the targets
 * are real, disassembled code - ResolveSwitchTables.java already proved the
 * addresses are right; this just reads more of what is there.
 *
 * Usage:
 *     analyzeHeadless <proj> <name> -process MGSTUS -noanalysis \
 *         -scriptPath tools/ghidra -postScript DumpCaseBodies.java \
 *         <callers_csv> <max_insns_per_case> <out.txt>
 * callers_csv: comma-separated exact caller names as they appear in
 *              switch_resolved.tsv's "caller" column (e.g.
 *              "__EnemyBase_update:_,__Octopus_updateAppearanceProcess_")
 */
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;

public class DumpCaseBodies extends GhidraScript {

    static final String[] TARGETS = {"___switch8", "___switchu8", "___switch16"};

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 3) {
            println("ERROR: expected callers_csv max_insns out.txt");
            return;
        }
        Set<String> wantCallers = new HashSet<>(Arrays.asList(args[0].split(",")));
        int maxInsns = Integer.parseInt(args[1]);
        SymbolTable symTab = currentProgram.getSymbolTable();

        try (PrintWriter out = new PrintWriter(args[2])) {
            for (String target : TARGETS) {
                for (Symbol sym : symTab.getSymbols(target)) {
                    Address defAddr = sym.getAddress();
                    ReferenceIterator refs = currentProgram.getReferenceManager()
                            .getReferencesTo(defAddr);
                    while (refs.hasNext()) {
                        Reference ref = refs.next();
                        if (!ref.getReferenceType().isCall()) continue;
                        Address callAddr = ref.getFromAddress();
                        Instruction callInsn = currentProgram.getListing().getInstructionAt(callAddr);
                        if (callInsn == null) continue;
                        var fn = currentProgram.getFunctionManager().getFunctionContaining(callAddr);
                        String callerName = fn != null ? fn.getName() : "?";
                        if (!wantCallers.contains(callerName)) continue;

                        Address fallthrough = callAddr.add(callInsn.getLength());
                        int count = currentProgram.getMemory().getByte(fallthrough) & 0xff;
                        out.println("\n===== " + target + " in " + callerName
                                + " @ " + callAddr + " (fallthrough " + fallthrough
                                + ", " + count + " cases) =====");
                        if (count == 0 || count > 64) {
                            out.println("  (implausible count, skipped)");
                            continue;
                        }
                        for (int i = 0; i < count; i++) {
                            byte entry = currentProgram.getMemory().getByte(fallthrough.add(1 + i));
                            Address goTo = fallthrough.add(((long) entry) * 2);
                            out.println("  --- case " + i + " (entry=" + (entry & 0xff)
                                    + ") -> " + goTo + " ---");
                            Instruction insn = currentProgram.getListing().getInstructionAt(goTo);
                            if (insn == null) {
                                out.println("      (no instruction here)");
                                continue;
                            }
                            for (int k = 0; k < maxInsns && insn != null; k++) {
                                out.println("      " + insn.getAddress() + "  " + insn);
                                insn = insn.getNext();
                            }
                        }
                    }
                }
            }
        }
        println("wrote " + args[2]);
    }
}
