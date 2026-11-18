/* Static structure fixes that the oracle's runtime data pointed at, applied
 * to ALL code (executed or not):
 *
 *   1. dyld stubs (__symbol_stub4, analysis/symbols/stubs_v230.tsv) are
 *      checked to be thunks to their EXTERNAL import (ExportMgstDecompilation
 *      lists thunks in _imports.txt instead of decompiling them - they were
 *      187 of the 188 "Could not recover jumptable" warnings).
 *   2. Split fragments: a function in __text whose entry is NOT a real start
 *      in analysis/symbols/function_map.csv (STABS/symbol-table starts) and
 *      whose every reference is a `bl` from inside the SAME real function is
 *      `bl` used as a long branch (Thumb-1 has no long B). Those BLs get a
 *      BRANCH flow override, the fragment is removed and the containing
 *      function's body re-fixed, so the code decompiles inline.
 *      Confirmed dynamically for 10 targets (analysis/dynamic/bl_nonreturn.tsv:
 *      no execution ever returned to site+4); this generalises the rule to
 *      code the oracle never ran. Anything referenced from another function
 *      or by data is kept and reported (a real function missing from the map).
 *   2b. Literal pools that Ghidra disassembled into "functions" (their only
 *      references are `ldr rX,[pc,#..]` READs from the owning function) are
 *      removed and re-typed as 32-bit data - they decompiled as garbage.
 *   2c. objc_msgSend / Super2 / _stret get their real varargs prototypes
 *      (the import left them `undefined f(void)`, so r0/r1 were dropped).
 *   3. Phantom functions outside every initialized memory block (e.g. `_exit`
 *      at 0xd60c4, beyond __bss) are removed.
 *
 * Usage:
 *   analyzeHeadless analysis/ghidra MGST -process MGSTUS -noanalysis \
 *       -scriptPath tools/ghidra -postScript FixSplitsAndStubs.java
 * Idempotent.
 */
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

import ghidra.app.cmd.function.ApplyFunctionSignatureCmd;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.program.model.data.*;
import ghidra.program.model.symbol.SourceType;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.FlowOverride;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;

public class FixSplitsAndStubs extends GhidraScript {

    static final long TEXT_LO = 0x1000, HELPERS_LO = 0x5a5b4, STUB_LO = 0x5a614, STUB_HI = 0x5ae9c;

    /** Only READ (literal-pool load) references, from inside its owner, and no flow in. */
    boolean isLiteralPool(Function f, Long owner, Long ownerEnd) {
        Reference[] refs = getReferencesTo(f.getEntryPoint());
        if (refs.length == 0 || owner == null) return false;
        for (Reference r : refs) {
            long from = r.getFromAddress().getOffset();
            boolean inside = from >= owner && (ownerEnd == null || from < ownerEnd);
            if (!r.getReferenceType().isRead() || r.getReferenceType().isFlow() || !inside) return false;
        }
        return true;
    }

    @Override
    protected void run() throws Exception {
        TreeSet<Long> real = new TreeSet<>();
        try (BufferedReader r = new BufferedReader(new FileReader("analysis/symbols/function_map.csv"))) {
            String line = r.readLine();
            while ((line = r.readLine()) != null) {
                try { real.add(Long.parseLong(line.split(",", 2)[0].replace("0x", ""), 16)); }
                catch (NumberFormatException e) { }
            }
        }

        // ---- 1. stubs must be thunks to their imports (the Mach-O loader
        // already does this for v2.3.0; verified, not re-done)
        int nThunk = 0, nNot = 0;
        for (long va = STUB_LO; va < STUB_HI; va += 12) {
            Function f = getFunctionAt(toAddr(va));
            if (f != null && f.isThunk()) nThunk++;
            else { nNot++; printerr("stub at 0x" + Long.toHexString(va) + " is not a thunk"); }
        }
        println("stubs that are thunks: " + nThunk + ", not: " + nNot);

        // ---- 2. split fragments
        List<Function> cands = new ArrayList<>();
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            long e = f.getEntryPoint().getOffset();
            if (e >= TEXT_LO && e < HELPERS_LO && !real.contains(e) && !f.isThunk()) cands.add(f);
        }
        int merged = 0, kept = 0, overrides = 0, pools = 0;
        Set<Function> refix = new HashSet<>();
        for (Function f : cands) {
            long e = f.getEntryPoint().getOffset();
            Long owner = real.floor(e);
            Long ownerEnd = real.higher(e);
            boolean ok = owner != null;
            List<Instruction> sites = new ArrayList<>();
            String why = "";
            for (Reference ref : getReferencesTo(f.getEntryPoint())) {
                long from = ref.getFromAddress().getOffset();
                Instruction ins = getInstructionAt(ref.getFromAddress());
                boolean inside = owner != null && from >= owner && (ownerEnd == null || from < ownerEnd);
                boolean flow = ref.getReferenceType().isCall() || ref.getReferenceType().isJump();
                if (ins == null || !flow || !inside) {
                    ok = false;
                    why = (ins == null ? "data ref" : !flow ? "non-flow ref " + ref.getReferenceType()
                            : "flow from outside owner 0x" + Long.toHexString(owner == null ? 0 : owner))
                            + " at " + ref.getFromAddress();
                    break;
                }
                if (ref.getReferenceType().isCall()) {
                    sites.add(ins);       // bl, or a `b` Ghidra took for a tail call
                }
            }
            if (isLiteralPool(f, owner, ownerEnd)) {
                // only the contiguous range at the pool itself: a garbage body can
                // run on into real code of the owner, which must stay code
                AddressSet body = new AddressSet(f.getBody().getRangeContaining(f.getEntryPoint()));
                removeFunction(f);
                clearListing(body);
                Address a0 = body.getMinAddress();
                long end = body.getMaxAddress().getOffset();
                for (long va = a0.getOffset() & ~3L; va + 3 <= end; va += 4) {
                    try { createDWord(toAddr(va)); } catch (Exception ex) { }
                }
                println("literal pool re-typed as data: " + body);
                pools++;
                continue;
            }
            if (!ok || sites.isEmpty()) {
                println("kept: " + f.getName() + " @ " + f.getEntryPoint()
                        + " refs=" + getReferencesTo(f.getEntryPoint()).length + " - "
                        + (ok ? "no bl sites" : why));
                kept++;
                continue;
            }
            for (Instruction ins : sites) {
                ins.setFlowOverride(FlowOverride.BRANCH);
                overrides++;
            }
            removeFunction(f);
            merged++;
            Function parent = getFunctionAt(toAddr(owner));
            if (parent != null) refix.add(parent);
        }
        for (Function p : refix) CreateFunctionCmd.fixupFunctionBody(currentProgram, p, monitor);
        println("literal pools mis-disassembled as functions, re-typed as data: " + pools);
        println("split fragments merged: " + merged + " (" + overrides + " BL->BRANCH), kept: " + kept
                + ", parents re-fixed: " + refix.size());

        // ---- 3. phantoms
        List<Function> ph = new ArrayList<>();
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            MemoryBlock b = getMemoryBlock(f.getEntryPoint());
            if (!f.isExternal() && (b == null || !b.isInitialized())) ph.add(f);
        }
        int phantoms = 0;
        for (Function f : ph) {
            println("phantom removed: " + f.getName() + " @ " + f.getEntryPoint());
            removeFunction(f);
            phantoms++;
        }
        println("phantom functions removed: " + phantoms);

        // ---- 4. real objc_msgSend* prototypes (before the switch check,
        // which decompiles)
        fixMsgSendPrototypes();

        // ---- 5. switch-helper sites the decompiler still cannot recover
        fixSwitchOverrides();
    }

    /** The Mach-O import gave the msgSend stubs `undefined f(void)`, not
     *  varargs: the decompiler then printed `_objc_msgSend()` with r0/r1
     *  dropped wherever its own inference failed (~25 sites, e.g. the
     *  [NSBundle mainBundle] loads in +[Player init]). */
    void fixMsgSendPrototypes() throws Exception {
        DataType id = new PointerDataType(VoidDataType.dataType);
        DataType sel = new PointerDataType(CharDataType.dataType);
        Object[][] spec = {
            {0x5add0L, "_objc_msgSend", id, new String[]{"self", "op"}, new DataType[]{id, sel}},
            {0x5adc4L, null, null, null, null},
            {0x5addcL, "_objc_msgSendSuper2", id, new String[]{"super", "op"}, new DataType[]{id, sel}},
            {0x5ade8L, "_objc_msgSend_stret", VoidDataType.dataType,
                    new String[]{"stret", "self", "op"}, new DataType[]{id, id, sel}}};
        int n = 0;
        for (Object[] sp : spec) {
            if (sp[1] == null) continue;
            FunctionDefinitionDataType d = new FunctionDefinitionDataType((String) sp[1]);
            d.setReturnType((DataType) sp[2]);
            String[] names = (String[]) sp[3];
            DataType[] types = (DataType[]) sp[4];
            ParameterDefinition[] p = new ParameterDefinition[names.length];
            for (int i = 0; i < p.length; i++) p[i] = new ParameterDefinitionImpl(names[i], types[i], null);
            d.setArguments(p);
            d.setVarArgs(true);
            Function st = getFunctionAt(toAddr((Long) sp[0]));
            if (st == null) { printerr("no stub at " + sp[0]); continue; }
            for (Function f : new Function[]{st, st.isThunk() ? st.getThunkedFunction(true) : null}) {
                if (f == null) continue;
                if (new ApplyFunctionSignatureCmd(f.getEntryPoint(), d, SourceType.USER_DEFINED)
                        .applyTo(currentProgram, monitor)) n++;
            }
        }
        println("objc_msgSend* prototypes applied: " + n);
    }

    static final long SW_U8 = 0x5a5b4, SW_8 = 0x5a5cc, SW_16 = 0x5a5e4;

    /** Static case targets of the inline table after `bl/blx helper` at SITE
     *  (formats: LOG STEPS 3+4; checked against runtime case targets in
     *  analysis/dynamic/switch_targets.tsv - e.g. all 5 distinct targets of
     *  0x2c184 were observed). */
    List<Address> switchTargets(long site, long helper) throws Exception {
        long ret = site + 4;
        List<Address> out = new ArrayList<>();
        java.util.LinkedHashSet<Long> seen = new java.util.LinkedHashSet<>();
        if (helper == SW_16) {
            int cnt = getShort(toAddr(ret)) & 0xffff;
            for (int i = 0; i <= cnt; i++) seen.add(ret + 2L * getShort(toAddr(ret + 2 + 2L * i)));
        } else {
            int cnt = getByte(toAddr(ret)) & 0xff;
            for (int i = 0; i <= cnt; i++) {
                int e = getByte(toAddr(ret + 1 + i));
                if (helper == SW_U8) e &= 0xff;
                seen.add(ret + 2L * e);
            }
        }
        for (long t : seen) out.add(toAddr(t));
        return out;
    }

    void fixSwitchOverrides() throws Exception {
        java.util.Map<Function, List<Instruction>> byFn = new java.util.LinkedHashMap<>();
        for (Instruction ins : currentProgram.getListing().getInstructions(true)) {
            for (Address t : ins.getFlows()) {
                long o = t.getOffset();
                if (o == SW_U8 || o == SW_8 || o == SW_16) {
                    Function f = getFunctionContaining(ins.getAddress());
                    if (f != null) byFn.computeIfAbsent(f, k -> new ArrayList<>()).add(ins);
                }
            }
        }
        ghidra.app.decompiler.DecompInterface d = new ghidra.app.decompiler.DecompInterface();
        d.openProgram(currentProgram);
        int fixed = 0, checked = 0;
        for (java.util.Map.Entry<Function, List<Instruction>> e : byFn.entrySet()) {
            ghidra.app.decompiler.DecompileResults r = d.decompileFunction(e.getKey(), 120, monitor);
            if (!r.decompileCompleted()) continue;
            String c = r.getDecompiledFunction().getC();
            checked++;
            for (Instruction ins : e.getValue()) {
                String tag = String.format("Could not recover jumptable at 0x%08x", ins.getAddress().getOffset());
                if (!c.contains(tag)) continue;
                long helper = ins.getFlows()[0].getOffset();
                List<Address> tg = switchTargets(ins.getAddress().getOffset(), helper);
                ghidra.program.model.pcode.JumpTable jt = new ghidra.program.model.pcode.JumpTable(
                        ins.getAddress(), new ArrayList<>(tg), true);
                jt.writeOverride(e.getKey());
                println("jumptable override at " + ins.getAddress() + " (" + e.getKey().getName() + "): " + tg);
                fixed++;
            }
        }
        d.dispose();
        println("switch-helper functions checked: " + checked + ", jumptable overrides written: " + fixed);
    }
}
