/* Static check for the RayMissile pattern (LOG 2026-10-09): Ghidra merges
 * all SSA versions of an address-tied stack variable (a buffer whose address
 * is passed to a call, e.g. an objc_msgSend_stret result) into ONE C
 * variable. If a value defined by one write is still read after a LATER write
 * to the same storage, the C text reads the variable and so gets the later
 * value - not what the binary does.
 *
 * For every address-tied stack local of the given functions: for each
 * instance (SSA version) v defined at op d, and each read u of v, flag it if
 * another instance of the same variable is defined at an op w with
 * d < w < u in the same basic-block chain order (address order inside the
 * function, no loop back-edge between them). Address order is a heuristic:
 * every flag is reviewed by hand against the disassembly.
 *
 * Check 2 (the actual RayMissile case): a CALL is passed the address of a
 * stack variable (PTRSUB of the stack base) but the decompiler put no
 * INDIRECT (write effect) on that variable at the call, and the variable is
 * read after the call. The decompiler then assumes the call left it
 * unchanged; the C text passes &var, so the recompiled call writes it.
 *
 * Args: output tsv, then function addresses (hex). Read-only.
 *   func  name  variable  def  overwrite  use  (kind in use_op column)
 */
import java.io.*;
import java.util.*;

import ghidra.app.decompiler.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.pcode.*;

public class CheckAddrTiedMerge extends GhidraScript {
    /** Dominator sets of a function's basic blocks (iterative). */
    static Map<PcodeBlockBasic, Set<PcodeBlockBasic>> dominators(HighFunction hf) {
        List<PcodeBlockBasic> bs = hf.getBasicBlocks();
        Map<PcodeBlockBasic, Set<PcodeBlockBasic>> dom = new HashMap<>();
        Set<PcodeBlockBasic> all = new HashSet<>(bs);
        for (PcodeBlockBasic b : bs) dom.put(b, b.getInSize() == 0 ? new HashSet<>(List.of(b)) : new HashSet<>(all));
        boolean ch = true;
        while (ch) {
            ch = false;
            for (PcodeBlockBasic b : bs) {
                if (b.getInSize() == 0) continue;
                Set<PcodeBlockBasic> n = null;
                for (int i = 0; i < b.getInSize(); i++) {
                    Set<PcodeBlockBasic> pd = dom.get((PcodeBlockBasic) b.getIn(i));
                    if (pd == null) continue;
                    if (n == null) n = new HashSet<>(pd); else n.retainAll(pd);
                }
                if (n == null) n = new HashSet<>();
                n.add(b);
                if (!n.equals(dom.get(b))) { dom.put(b, n); ch = true; }
            }
        }
        return dom;
    }

    /** op a dominates op b (same block: a earlier). */
    static boolean dom(Map<PcodeBlockBasic, Set<PcodeBlockBasic>> d, PcodeOp a, PcodeOp b) {
        if (a == null) return true;                     // function input dominates everything
        PcodeBlockBasic ba = a.getParent(), bb = b.getParent();
        if (ba == bb) return a.getSeqnum().getOrder() < b.getSeqnum().getOrder();
        return d.getOrDefault(bb, Set.of()).contains(ba);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0]));
        out.println("func\tname\tvariable\tdef\toverwrite\tuse\tuse_op");
        DecompInterface d = new DecompInterface();
        d.setOptions(new DecompileOptions());
        d.openProgram(currentProgram);
        int nf = 0, nflag = 0;
        for (int i = 1; i < args.length; i++) {
            Function f = getFunctionAt(toAddr(Long.decode(args[i])));
            if (f == null) continue;
            nf++;
            DecompileResults r = d.decompileFunction(f, 120, monitor);
            HighFunction hf = r.getHighFunction();
            if (hf == null) continue;
            // ---- check 2: call passed &stackvar without a write effect on it
            Map<Long, List<PcodeOp>> indirectAt = new HashMap<>();
            Iterator<PcodeOpAST> all = hf.getPcodeOps();
            List<PcodeOp> calls = new ArrayList<>();
            List<PcodeOp> ops = new ArrayList<>();
            while (all.hasNext()) {
                PcodeOp op = all.next();
                ops.add(op);
                if (op.getOpcode() == PcodeOp.INDIRECT && op.getOutput() != null)
                    indirectAt.computeIfAbsent(op.getSeqnum().getTarget().getOffset(), k -> new ArrayList<>()).add(op);
                if (op.getOpcode() == PcodeOp.CALL || op.getOpcode() == PcodeOp.CALLIND) calls.add(op);
            }
            for (PcodeOp c : calls) {
                for (int k = 1; k < c.getNumInputs(); k++) {
                    PcodeOp pd = c.getInput(k).getDef();
                    while (pd != null && (pd.getOpcode() == PcodeOp.CAST || pd.getOpcode() == PcodeOp.COPY))
                        pd = pd.getInput(0).getDef();
                    if (pd == null || pd.getOpcode() != PcodeOp.PTRSUB) continue;
                    Varnode base = pd.getInput(0);
                    if (!(base.isRegister() || base.getSpace() == currentProgram.getAddressFactory().getStackSpace().getSpaceID())
                            || !pd.getInput(1).isConstant()) continue;
                    if (!base.isRegister() && !base.getAddress().getAddressSpace().isStackSpace()) continue;
                    long off = pd.getInput(1).getOffset();
                    if (off > 0x7fffffffL) off -= 0x100000000L;
                    if (off >= 0) continue;                              // caller's frame only
                    final long so = off;
                    boolean written = false;
                    for (PcodeOp ind : indirectAt.getOrDefault(c.getSeqnum().getTarget().getOffset(), List.of())) {
                        Varnode o = ind.getOutput();
                        if (o.getAddress().isStackAddress()) {
                            long vo = o.getOffset();
                            if (vo > 0x7fffffffL && vo < 0x100000000L) vo -= 0x100000000L;
                            if (o.getAddress().getOffset() <= so + 64 && so <= o.getAddress().getOffset() + o.getSize()
                                    || (vo <= so + 64 && so <= vo + o.getSize())) { written = true; break; }
                        }
                    }
                    if (written) continue;
                    // a later read of that stack storage?
                    Address ca = c.getSeqnum().getTarget();
                    for (PcodeOp u : ops) {
                        if (u.getSeqnum().getTarget().compareTo(ca) <= 0) continue;
                        int uc = u.getOpcode();
                        if (uc == PcodeOp.INDIRECT || uc == PcodeOp.MULTIEQUAL) continue;
                        for (Varnode in : u.getInputs()) {
                            if (in == null || !in.getAddress().isStackAddress()) continue;
                            long vo = in.getAddress().getOffset();
                            if (vo > 0x7fffffffL) vo -= 0x100000000L;
                            if (vo >= so && vo < so + 16) {
                                PcodeOp idf = in.getDef();
                                Address dd = idf == null ? f.getEntryPoint() : idf.getSeqnum().getTarget();
                                if (dd.compareTo(ca) < 0) {               // value from before the call
                                    out.println(f.getEntryPoint() + "\t" + f.getName(true) + "\tstack" + so + "\t"
                                            + dd + "\t" + ca + "\t" + u.getSeqnum().getTarget() + "\tNO-WRITE-EFFECT " + u.getMnemonic());
                                    nflag++;
                                }
                            }
                        }
                    }
                }
            }
            Map<PcodeBlockBasic, Set<PcodeBlockBasic>> domSets = dominators(hf);
            Set<HighVariable> seenHv = new HashSet<>();
            Iterator<HighSymbol> it = hf.getLocalSymbolMap().getSymbols();
            while (it.hasNext()) {
                HighSymbol hs = it.next();
                HighVariable hv = hs.getHighVariable();
                if (hv == null || !seenHv.add(hv)) continue;
                Varnode rep = hv.getRepresentative();
                if (rep == null || !rep.isAddrTied() || !hs.getStorage().isStackStorage()) continue;
                Varnode[] inst = hv.getInstances();
                // definitions of this storage (by address order)
                List<PcodeOp> defs = new ArrayList<>();
                for (Varnode v : inst) {
                    PcodeOp dop = v.getDef();
                    if (dop != null && dop.getOpcode() != PcodeOp.MULTIEQUAL) defs.add(dop);
                }
                for (Varnode v : inst) {
                    PcodeOp dop = v.getDef();
                    Address da = dop == null ? f.getEntryPoint() : dop.getSeqnum().getTarget();
                    Iterator<PcodeOp> us = v.getDescendants();
                    while (us.hasNext()) {
                        PcodeOp u = us.next();
                        int oc = u.getOpcode();
                        if (oc == PcodeOp.INDIRECT || oc == PcodeOp.MULTIEQUAL) continue;
                        Address ua = u.getSeqnum().getTarget();
                        // definite: the old value's def dominates a later write
                        // of the same storage, which dominates this read
                        for (PcodeOp w : defs) {
                            if (w == dop) continue;
                            // a call's own write effect (INDIRECT at the call) is
                            // ordered before it but happens after its inputs are read
                            if (w.getSeqnum().getTarget().equals(u.getSeqnum().getTarget())) continue;
                            if (dom(domSets, dop, w) && dom(domSets, w, u)) {
                                out.println(f.getEntryPoint() + "\t" + f.getName(true) + "\t" + hs.getName() + "\t"
                                        + da + "\t" + w.getSeqnum().getTarget() + "\t" + ua + "\t" + u.getMnemonic());
                                nflag++;
                                break;
                            }
                        }
                    }
                }
            }
        }
        out.close();
        println("CheckAddrTiedMerge: " + nf + " functions, " + nflag + " flagged reads");
    }
}
