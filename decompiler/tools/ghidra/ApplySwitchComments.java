/* Readable switch tables. The 65 Apple switch-helper sites (___switchu8 /
 * ___switch8 / ___switch16) decompile via jumptable overrides
 * (FixSplitsAndStubs.java) whose case labels are the TABLE VALUE (entry * 2),
 * not the source-level index - the decompiler normalises to the loaded entry.
 * Targets are exact; this adds the index view: a PRE comment at each site
 * with the decoded inline table, grouped by target.
 *
 *   switch index (0..N-1, >= N -> default) -> case label (entry*2) -> target
 *
 * Usage: analyzeHeadless ... -postScript ApplySwitchComments.java  (idempotent)
 */
import java.util.*;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;

public class ApplySwitchComments extends GhidraScript {
    static final long SW_U8 = 0x5a5b4, SW_8 = 0x5a5cc, SW_16 = 0x5a5e4;

    @Override
    protected void run() throws Exception {
        int n = 0;
        for (Instruction ins : currentProgram.getListing().getInstructions(true)) {
            Address[] fl = ins.getFlows();
            if (fl.length == 0) continue;
            long h = fl[0].getOffset();
            if (h != SW_U8 && h != SW_8 && h != SW_16) continue;
            long ret = ins.getAddress().getOffset() + 4;
            int cnt;
            List<Integer> ent = new ArrayList<>();
            if (h == SW_16) {
                cnt = getShort(toAddr(ret)) & 0xffff;
                for (int i = 0; i <= cnt; i++) ent.add((int) getShort(toAddr(ret + 2 + 2L * i)));
            } else {
                cnt = getByte(toAddr(ret)) & 0xff;
                for (int i = 0; i <= cnt; i++) {
                    int e = getByte(toAddr(ret + 1 + i));
                    ent.add(h == SW_U8 ? e & 0xff : e);
                }
            }
            Map<Long, List<String>> byTarget = new TreeMap<>();
            for (int i = 0; i <= cnt; i++) {
                long tgt = ret + 2L * ent.get(i);
                byTarget.computeIfAbsent(tgt, k -> new ArrayList<>()).add(i == cnt ? "default" : Integer.toString(i));
            }
            StringBuilder sb = new StringBuilder(String.format(
                    "switch table (%s, index 0..%d, >=%d -> default); case label = entry*2:",
                    h == SW_16 ? "___switch16" : h == SW_8 ? "___switch8" : "___switchu8", cnt - 1, cnt));
            for (Map.Entry<Long, List<String>> e : byTarget.entrySet()) {
                int idx0 = e.getValue().get(0).equals("default") ? cnt : Integer.parseInt(e.getValue().get(0));
                sb.append(String.format("\n  idx %s -> case 0x%x -> %08x", String.join(",", e.getValue()),
                        ent.get(idx0) * 2 & (h == SW_16 ? 0xffffffffL : 0xffffffffL), e.getKey()));
            }
            setPreComment(ins.getAddress(), sb.toString());
            n++;
        }
        println("switch table comments: " + n);
    }
}
