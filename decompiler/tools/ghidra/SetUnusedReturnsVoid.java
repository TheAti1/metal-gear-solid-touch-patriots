/* Declare void the functions whose return value no caller uses
 * (analysis/symbols/unused_returns.tsv, produced from AnalyzeReturnUse.java:
 * no call site reads r0/r1 after the call; at most the caller passes r0 up
 * from a tail position under its own inferred type). C++ mangled names carry
 * no return type, so Ghidra had inferred one; the recompiled function's r0 was
 * then compared although it is never observable (LOG 2026-10-09).
 * Inverse of FixVoidReturns.java (void functions whose r0 IS read). Idempotent.
 */
import java.nio.file.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

public class SetUnusedReturnsVoid extends GhidraScript {
    @Override
    protected void run() throws Exception {
        int n = 0;
        for (String l : Files.readAllLines(Paths.get(getScriptArgs().length > 0 ? getScriptArgs()[0]
                : "analysis/symbols/unused_returns.tsv"))) {
            if (!l.startsWith("0")) continue;
            Function f = getFunctionAt(toAddr(Long.parseLong(l.split("\t")[0], 16)));
            if (f == null || f.getReturnType() instanceof VoidDataType) continue;
            f.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
            n++;
        }
        println("SetUnusedReturnsVoid: " + n + " function(s) set void");
    }
}
