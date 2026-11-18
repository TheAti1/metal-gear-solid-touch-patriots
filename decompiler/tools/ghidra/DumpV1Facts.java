/* V1 static audit facts (PLAN 4b V1, LOG 2026-10-07 STEP 1). Read-only.
 *
 * Decompiles every function with the SAME options as ExportCompilable /
 * ExportMgstDecompilation (defaults) and dumps what the decompiler actually
 * used, for tools/mgst_audit.py to check against independent sources:
 *
 *   <out>/v1_jumptables.tsv  function, switch address, case label, destination
 *                            (HighFunction.getJumpTables(): the recovered or
 *                            overridden switch the C output was built from)
 *   <out>/v1_msgsend.tsv     every CALL to the objc_msgSend* stubs: call site,
 *                            stub, output size and data type (the per-site
 *                            prototype's return as the decompiler applied it;
 *                            "-" = result unused) and the static selector(s)
 *                            (selref / literal / MULTIEQUAL merge, "|"-joined)
 *   <out>/v1_failed.tsv      functions that failed to decompile
 *
 * Usage: analyzeHeadless analysis/ghidra MGST -process MGSTUS -noanalysis
 *          -readOnly -scriptPath tools/ghidra -postScript DumpV1Facts.java <outdir>
 */
import java.io.*;
import java.util.*;

import ghidra.app.decompiler.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.pcode.*;

public class DumpV1Facts extends GhidraScript {
    static final long[] STUBS = { 0x5add0, 0x5addc, 0x5ade8 };
    static final String[] STUB_NAMES = { "msgSend", "msgSendSuper2", "msgSend_stret" };

    @Override
    protected void run() throws Exception {
        String out = getScriptArgs().length > 0 ? getScriptArgs()[0] : "analysis/verification";
        new File(out).mkdirs();
        PrintWriter jt = new PrintWriter(new File(out, "v1_jumptables.tsv"));
        PrintWriter ms = new PrintWriter(new File(out, "v1_msgsend.tsv"));
        PrintWriter fl = new PrintWriter(new File(out, "v1_failed.tsv"));
        jt.println("function\tentry\tswitch\tlabel\tdest");
        ms.println("function\tentry\tsite\tstub\tout_size\tout_type\tselectors");
        fl.println("function\tentry\terror");
        DecompInterface d = new DecompInterface();
        d.setOptions(new DecompileOptions());
        d.openProgram(currentProgram);
        int n = 0, failed = 0;
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            if (f.isThunk() || f.isExternal()) continue;
            monitor.checkCancelled();
            DecompileResults r = d.decompileFunction(f, 120, monitor);
            n++;
            HighFunction hf = r.getHighFunction();
            if (hf == null) {
                failed++;
                fl.println(f.getName() + "\t" + f.getEntryPoint() + "\t" + r.getErrorMessage().replace('\n', ' '));
                continue;
            }
            for (JumpTable t : hf.getJumpTables()) {
                Address[] dst = t.getCases();
                Integer[] lab = t.getLabelValues();
                for (int i = 0; i < dst.length; i++) {
                    jt.println(f.getName() + "\t" + f.getEntryPoint() + "\t" + t.getSwitchAddress() + "\t"
                               + (lab != null && i < lab.length ? lab[i] : "?") + "\t" + dst[i]);
                }
            }
            Iterator<PcodeOpAST> it = hf.getPcodeOps();
            while (it.hasNext()) {
                PcodeOpAST op = it.next();
                if (op.getOpcode() != PcodeOp.CALL) continue;
                long tgt = op.getInput(0).getAddress().getOffset();
                int k = -1;
                for (int i = 0; i < STUBS.length; i++) if (STUBS[i] == tgt) k = i;
                if (k < 0) continue;
                Varnode o = op.getOutput();
                String ty = "-", sz = "0";
                if (o != null) {
                    sz = Integer.toString(o.getSize());
                    HighVariable hv = o.getHigh();
                    ty = hv != null && hv.getDataType() != null ? hv.getDataType().getDisplayName() : "?";
                }
                Set<String> sels = new TreeSet<>();
                int selIdx = k == 2 ? 3 : 2;
                if (op.getNumInputs() > selIdx) selectorsOf(op.getInput(selIdx), sels, 0);
                ms.println(f.getName() + "\t" + f.getEntryPoint() + "\t" + op.getSeqnum().getTarget() + "\t"
                           + STUB_NAMES[k] + "\t" + sz + "\t" + ty + "\t"
                           + (sels.isEmpty() ? "?" : String.join("|", sels)));
            }
        }
        jt.close(); ms.close(); fl.close();
        println("DumpV1Facts: " + n + " functions decompiled, " + failed + " failed -> " + out);
    }

    /* Selector resolution: same rules as ApplyCallsiteSignatures.java. */
    void selectorsOf(Varnode v, Set<String> out, int depth) throws Exception {
        if (v == null || depth > 6) return;
        PcodeOp def = v.getDef();
        if (def != null && def.getOpcode() == PcodeOp.MULTIEQUAL) {
            for (int i = 0; i < def.getNumInputs(); i++) selectorsOf(def.getInput(i), out, depth + 1);
            return;
        }
        String s1 = selectorOf(v);
        if (s1 != null) out.add(s1);
    }

    String selectorOf(Varnode v) throws Exception {
        for (int hop = 0; hop < 4 && v != null; hop++) {
            if (v.isConstant() || v.isAddress()) return stringOrSelref(v.getOffset());
            PcodeOp def = v.getDef();
            if (def == null) return null;
            if (def.getOpcode() == PcodeOp.LOAD && def.getInput(1).isConstant()) {
                return stringOrSelref(getInt(toAddr(def.getInput(1).getOffset())) & 0xffffffffL);
            }
            if (def.getOpcode() == PcodeOp.COPY || def.getOpcode() == PcodeOp.CAST) { v = def.getInput(0); continue; }
            if (def.getOpcode() == PcodeOp.PTRSUB && def.getInput(0).isConstant() && def.getInput(1).isConstant()) {
                return stringOrSelref(def.getInput(0).getOffset() + def.getInput(1).getOffset());
            }
            return null;
        }
        return null;
    }

    String stringOrSelref(long va) throws Exception {
        MemoryBlock b = getMemoryBlock(toAddr(va));
        if (b == null) return null;
        String bn = b.getName();
        if (bn.contains("selrefs") || bn.contains("nl_symbol") || bn.contains("objc_const") || bn.contains("__data")) {
            long p = getInt(toAddr(va)) & 0xffffffffL;
            MemoryBlock b2 = getMemoryBlock(toAddr(p));
            if (b2 != null && (b2.getName().contains("cstring") || b2.getName().contains("methname"))) return cstr(p);
            return null;
        }
        if (bn.contains("cstring") || bn.contains("methname")) return cstr(va);
        return null;
    }

    String cstr(long va) throws Exception {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 128; i++) {
            byte c = getByte(toAddr(va + i));
            if (c == 0) break;
            sb.append((char) c);
        }
        return sb.length() > 0 ? sb.toString() : null;
    }
}
