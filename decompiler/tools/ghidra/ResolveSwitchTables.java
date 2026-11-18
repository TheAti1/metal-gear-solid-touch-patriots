/* For every ___switch8/___switchu8/___switch16 call site, decode the inline
 * jump table and force-disassemble each recovered target through Ghidra's
 * own validated disassembler - not a hand-rolled decoder - so a garbage
 * decode shows up as a disassembly failure or nonsense instructions instead
 * of silently "succeeding" the way manual byte math can.
 *
 * TABLE FORMAT (empirically confirmed against two independent call sites
 * with known surrounding semantics before writing this - see
 * analysis/notes/switch8_tables.md for the validation):
 *     byte[0]        = count N (number of case entries)
 *     byte[1..N]     = signed offsets, one per case
 *     target(i)      = fallthrough_addr + (signed)byte[1+i] * 2
 * fallthrough_addr is the call instruction's own address + its length
 * (already correct per-callsite from ExtractSwitchTables.java's XREF walk -
 * this script re-derives it the same way rather than trusting stale bytes).
 *
 * Usage:
 *     analyzeHeadless <proj_dir> <proj_name> -process MGSTUS -noanalysis \
 *         -scriptPath tools/ghidra -postScript ResolveSwitchTables.java <out.tsv>
 */
import java.io.PrintWriter;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;
import ghidra.program.model.lang.Register;
import ghidra.program.model.address.AddressFactory;

public class ResolveSwitchTables extends GhidraScript {

    static final String[] TARGETS = {"___switch8", "___switchu8", "___switch16"};

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) { println("ERROR: expected output TSV path"); return; }

        Memory mem = currentProgram.getMemory();
        SymbolTable symTab = currentProgram.getSymbolTable();
        AddressFactory af = currentProgram.getAddressFactory();
        Register tmode = currentProgram.getProgramContext().getRegister("TMode");

        try (PrintWriter out = new PrintWriter(args[0])) {
            out.println("target\tcaller\tcall_addr\tfallthrough\tcount\tcase_idx\tentry_byte\tgoto_addr\tdisasm_ok\tinsn_text");

            for (String target : TARGETS) {
                for (Symbol sym : symTab.getSymbols(target)) {
                    Address defAddr = sym.getAddress();
                    ReferenceIterator refs = currentProgram.getReferenceManager()
                            .getReferencesTo(defAddr);
                    while (refs.hasNext()) {
                        Reference ref = refs.next();
                        if (!ref.getReferenceType().isCall()) continue;
                        Address callAddr = ref.getFromAddress();
                        Instruction insn = currentProgram.getListing().getInstructionAt(callAddr);
                        if (insn == null) continue;
                        Address fallthrough = callAddr.add(insn.getLength());
                        Function fn = currentProgram.getFunctionManager()
                                .getFunctionContaining(callAddr);
                        String callerName = fn != null ? fn.getName() : "?";

                        byte countB = mem.getByte(fallthrough);
                        int count = countB & 0xff;
                        // Sanity bound: a genuine dense-switch table here is never
                        // in the hundreds; treat implausible counts as a parse
                        // failure rather than reading wild memory.
                        if (count == 0 || count > 64) {
                            out.println(target + "\t" + callerName + "\t" + callAddr + "\t"
                                    + fallthrough + "\t" + count + "\t-\t-\t-\tCOUNT_IMPLAUSIBLE\t-");
                            continue;
                        }

                        for (int i = 0; i < count; i++) {
                            byte entry = mem.getByte(fallthrough.add(1 + i));
                            Address goTo = fallthrough.add(((long) entry) * 2);

                            // Seed TMode=1 (Thumb) at the target before asking
                            // Ghidra to disassemble it, exactly as
                            // ApplyMgstSymbols.java does for the main corpus -
                            // without this a correct target can still decode as
                            // wrong-mode garbage.
                            String insnText;
                            boolean ok;
                            try {
                                // Clear whatever Ghidra's original (flawed) auto-
                                // analysis left here first - most of these targets
                                // were never reachable by its own control-flow
                                // analysis, so anything already defined at them is
                                // exactly the "could not recover jumptable"
                                // fallout, not something to preserve. Clearing lets
                                // the context-register write and disassemble()
                                // below apply cleanly instead of conflicting with
                                // stale code units.
                                clearListing(goTo, goTo.add(15));
                                if (tmode != null) {
                                    currentProgram.getProgramContext()
                                            .setValue(tmode, goTo, goTo,
                                                    java.math.BigInteger.ONE);
                                }
                                boolean disOk = disassemble(goTo);
                                Instruction result = disOk ?
                                        currentProgram.getListing().getInstructionAt(goTo) : null;
                                if (result != null) {
                                    ok = true;
                                    insnText = result.toString();
                                } else {
                                    ok = false;
                                    insnText = "(disassemble failed)";
                                }
                            } catch (Exception e) {
                                ok = false;
                                insnText = "EXCEPTION: " + e.getMessage();
                            }

                            out.println(target + "\t" + callerName + "\t" + callAddr + "\t"
                                    + fallthrough + "\t" + count + "\t" + i + "\t"
                                    + (entry & 0xff) + "\t" + goTo + "\t" + ok + "\t" + insnText);
                        }
                    }
                }
            }
        }
        println("wrote " + args[0]);
    }
}
