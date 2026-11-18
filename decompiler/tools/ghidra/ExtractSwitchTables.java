/* Dump every call site to the ___switch8 / ___switchu8 / ___switch16 family,
 * using GHIDRA'S OWN validated disassembly to get the call instruction's
 * true length (2 or 4 bytes) rather than re-deriving it by hand. The table
 * data these compiler-rt helpers dispatch through lives inline, immediately
 * after the call instruction (addressed via the caller's own return
 * address, not the helper's body) - so what matters here is exactly where
 * each individual call site's fall-through address is, which Ghidra already
 * knows correctly (it already decompiled the surrounding code without
 * complaint; only the jump table itself is what it flagged unresolved).
 *
 * For each XREF to one of the switch helpers, prints:
 *     caller_function  call_site_addr  call_len  fallthrough_addr  <32 raw bytes at fallthrough>
 *
 * Table FORMAT DECODING deliberately happens OUTSIDE Ghidra, in Python,
 * against these raw bytes - safer to validate against ARM's documented
 * __switch8 convention in a fast, iterable script than to re-run headless
 * analysis for every hypothesis.
 *
 * Usage:
 *     analyzeHeadless <proj_dir> <proj_name> -process MGSTUS -noanalysis \
 *         -scriptPath tools/ghidra -postScript ExtractSwitchTables.java <out.tsv>
 */
import java.io.PrintWriter;
import java.util.List;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;

public class ExtractSwitchTables extends GhidraScript {

    static final String[] TARGETS = {"___switch8", "___switchu8", "___switch16", "___switch32"};

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            println("ERROR: expected output TSV path");
            return;
        }
        Memory mem = currentProgram.getMemory();
        SymbolTable symTab = currentProgram.getSymbolTable();

        try (PrintWriter out = new PrintWriter(args[0])) {
            out.println("target\tcaller\tcall_addr\tcall_len\tfallthrough\tbytes_hex");
            for (String target : TARGETS) {
                for (Symbol sym : symTab.getSymbols(target)) {
                    Address defAddr = sym.getAddress();
                    println("=== " + target + " defined at " + defAddr
                            + " (this address's own bytes are NOT used) ===");
                    ReferenceIterator refs = currentProgram.getReferenceManager()
                            .getReferencesTo(defAddr);
                    int n = 0;
                    while (refs.hasNext()) {
                        Reference ref = refs.next();
                        if (!ref.getReferenceType().isCall()) continue;
                        Address callAddr = ref.getFromAddress();
                        Instruction insn = currentProgram.getListing().getInstructionAt(callAddr);
                        if (insn == null) {
                            println("  " + callAddr + ": no instruction (skipping)");
                            continue;
                        }
                        int len = insn.getLength();
                        Address fallthrough = callAddr.add(len);
                        Function fn = currentProgram.getFunctionManager()
                                .getFunctionContaining(callAddr);
                        String callerName = fn != null ? fn.getName() : "?";

                        byte[] buf = new byte[32];
                        int got = mem.getBytes(fallthrough, buf);
                        StringBuilder hex = new StringBuilder();
                        for (int i = 0; i < got; i++) {
                            hex.append(String.format("%02x", buf[i] & 0xff));
                        }
                        out.println(target + "\t" + callerName + "\t" + callAddr + "\t"
                                + len + "\t" + fallthrough + "\t" + hex);
                        n++;
                    }
                    println("  " + n + " call site(s) found");
                }
            }
        }
        println("wrote " + args[0]);
    }
}
