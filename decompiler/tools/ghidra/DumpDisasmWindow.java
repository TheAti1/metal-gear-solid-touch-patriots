/* Dump Ghidra's own linear disassembly (not decompilation) for a window of
 * addresses, plus any data/instruction classification Ghidra has for each.
 * Used to ground-truth switch-table byte layout hypotheses against Ghidra's
 * validated instruction boundaries, rather than a hand-rolled Capstone sweep
 * that has no independent confirmation of staying aligned.
 *
 * Usage:
 *     analyzeHeadless <proj_dir> <proj_name> -process MGSTUS -noanalysis \
 *         -scriptPath tools/ghidra -postScript DumpDisasmWindow.java \
 *         <start_hex> <end_hex> <out.txt>
 */
import java.io.PrintWriter;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;

public class DumpDisasmWindow extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 3) {
            println("ERROR: expected start_hex end_hex out.txt");
            return;
        }
        Address start = currentProgram.getAddressFactory().getAddress(args[0]);
        Address end = currentProgram.getAddressFactory().getAddress(args[1]);
        Listing listing = currentProgram.getListing();
        Memory mem = currentProgram.getMemory();

        try (PrintWriter out = new PrintWriter(args[2])) {
            Address a = start;
            while (a.compareTo(end) <= 0) {
                CodeUnit cu = listing.getCodeUnitAt(a);
                if (cu == null) {
                    out.println(a + "  <no code unit - possibly mid-instruction>");
                    a = a.add(1);
                    continue;
                }
                int len = cu.getLength();
                byte[] buf = new byte[len];
                mem.getBytes(a, buf);
                StringBuilder hex = new StringBuilder();
                for (byte b : buf) hex.append(String.format("%02x", b & 0xff));
                out.println(a + "  len=" + len + "  bytes=" + hex + "  "
                        + cu.getMnemonicString() + "  " + cu);
                a = a.add(len);
            }
        }
        println("wrote " + args[2]);
    }
}
