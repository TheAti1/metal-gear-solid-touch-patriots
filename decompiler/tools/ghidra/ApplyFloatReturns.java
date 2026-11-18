/* Functions whose return value is a float's bits (armv6 softfp: r0), from
 * analysis/symbols/float_returns.tsv (addr, function, reason). Declared
 * undefined4, their callers' C converted the integer with (float) instead of
 * reinterpreting the bits (LOG 2026-10-11, found by the mgsport port: music
 * volume 1.0 became 1.065e9). Sets the return type to float. Idempotent.
 */
import java.nio.file.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

public class ApplyFloatReturns extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String path = getScriptArgs().length > 0 ? getScriptArgs()[0] : "analysis/symbols/float_returns.tsv";
        int n = 0;
        for (String l : Files.readAllLines(Paths.get(path))) {
            if (!l.startsWith("0x")) continue;
            String[] p = l.split("\t");
            Function f = getFunctionAt(toAddr(Long.decode(p[0])));
            if (f == null) { println("no function at " + p[0]); continue; }
            f.setReturnType(FloatDataType.dataType, SourceType.USER_DEFINED);
            println("float return: " + f.getName(true));
            n++;
        }
        println("ApplyFloatReturns: " + n);
    }
}
