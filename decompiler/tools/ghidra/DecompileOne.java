/* Decompile the named function(s) to stdout. Usage: -postScript DecompileOne.java <addr_hex|name> ... */
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;

public class DecompileOne extends GhidraScript {
    @Override
    public void run() throws Exception {
        DecompInterface d = new DecompInterface();
        ghidra.app.decompiler.DecompileOptions o = new ghidra.app.decompiler.DecompileOptions();
        println("defaults: respectReadOnly=" + o.isRespectReadOnly() + " maxJumpTable=" + o.getMaxJumpTableEntries());
        if (System.getenv("MGST_RO") != null) o.setRespectReadOnly(true);
        if (System.getenv("MGST_JT") != null) o.setMaxJumpTableEntries(Integer.parseInt(System.getenv("MGST_JT")));
        d.setOptions(o);
        d.openProgram(currentProgram);
        for (String a : getScriptArgs()) {
            Function f = null;
            try {
                f = currentProgram.getFunctionManager().getFunctionContaining(
                    currentProgram.getAddressFactory().getAddress(a));
            } catch (Exception e) { }
            if (f == null) continue;
            DecompileResults r = d.decompileFunction(f, 120, monitor);
            println("=== " + f.getName() + " @ " + f.getEntryPoint());
            println(r.decompileCompleted() ? r.getDecompiledFunction().getC() : ("FAILED " + r.getErrorMessage()));
        }
    }
}
