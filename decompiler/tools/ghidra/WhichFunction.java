/* Print the function containing each given address. Usage: -postScript WhichFunction.java <addr_hex> ... */
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class WhichFunction extends GhidraScript {
    @Override
    public void run() throws Exception {
        for (String a : getScriptArgs()) {
            Address ad = currentProgram.getAddressFactory().getAddress(a);
            Function f = currentProgram.getFunctionManager().getFunctionContaining(ad);
            println(a + " -> " + (f == null ? "none" : f.getName() + " @ " + f.getEntryPoint()
                + " body " + f.getBody().getMinAddress() + ".." + f.getBody().getMaxAddress()));
        }
    }
}
