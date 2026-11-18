/* Labels for globals that the decompiler resolves but the listing has no
 * references to (PC-relative / literal-pool addressing): names from
 * analysis/dynamic/global_names.tsv (<SourceFile>_<addr>, generated from the
 * exported corpus). Only replaces Ghidra's default DAT_/typed auto labels.
 * Usage: analyzeHeadless ... -postScript ApplyGlobalNames.java  (idempotent)
 */
import java.io.BufferedReader;
import java.io.FileReader;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;

public class ApplyGlobalNames extends GhidraScript {
    static final java.util.regex.Pattern AUTO = java.util.regex.Pattern.compile(
            "(DAT|INT|UINT|FLOAT|DOUBLE|CHAR|UCHAR|SHORT|USHORT|BYTE|WORD|DWORD|LONG|ULONG|BOOL|SBYTE|longlong|ulonglong)_[0-9a-f]{8}");

    @Override
    protected void run() throws Exception {
        int n = 0, kept = 0;
        try (BufferedReader r = new BufferedReader(new FileReader("analysis/dynamic/global_names.tsv"))) {
            String l;
            while ((l = r.readLine()) != null) {
                if (l.startsWith("#") || l.isEmpty()) continue;
                String[] p = l.split("\t");
                Address a = toAddr(Long.decode(p[0]));
                Symbol s = currentProgram.getSymbolTable().getPrimarySymbol(a);
                if (s != null && !s.isDynamic() && !AUTO.matcher(s.getName()).matches()) { kept++; continue; }
                createLabel(a, p[1], true, SourceType.ANALYSIS);
                n++;
            }
        }
        println("globals named from corpus usage: " + n + " (already named: " + kept + ")");
    }
}
