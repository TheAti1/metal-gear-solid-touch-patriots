/* Apply runtime facts from the oracle (tools/mgst_calls.py -> analysis/dynamic)
 * to the MGSTUS Ghidra program, closing gaps static analysis cannot:
 *
 *   msgsend_sites.tsv    PRE comment "dyn: -[Class sel]" at every executed
 *                        objc_msgSend* call; the decompiler prints it above
 *                        the call, including the ~200 calls where it lost
 *                        the selector/receiver (`_objc_msgSend()`).
 *   bl_nonreturn.tsv     `bl` used as a long branch (never returned to
 *                        site+4 at runtime): flow override BRANCH; if the
 *                        target is not a real function start (not in
 *                        function_map.csv) its bogus FUN_ is removed and the
 *                        containing function's body is re-fixed so the code
 *                        is decompiled inline (e.g. FUN_0001339c = shared
 *                        epilogue of -[CrashLandingAppDelegate GameScene]).
 *   indirect_targets.tsv COMPUTED_CALL / COMPUTED_JUMP references to every
 *                        observed target of a register/pc branch.
 *
 * Usage:
 *   analyzeHeadless analysis/ghidra MGST -process MGSTUS -noanalysis \
 *       -scriptPath tools/ghidra -postScript ApplyDynamicCalls.java [dir]
 * Idempotent (comments replaced, references de-duplicated by Ghidra).
 */
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.FlowOverride;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.SourceType;

public class ApplyDynamicCalls extends GhidraScript {

    List<String[]> rows(File f) throws Exception {
        List<String[]> out = new ArrayList<>();
        if (!f.exists()) { printerr("missing " + f); return out; }
        try (BufferedReader r = new BufferedReader(new FileReader(f))) {
            String line = r.readLine();   // header
            while ((line = r.readLine()) != null) {
                if (!line.isEmpty()) out.add(line.split("\t", -1));
            }
        }
        return out;
    }

    Address va(String hex) {
        return toAddr(Long.parseLong(hex.replace("0x", ""), 16));
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        File dir = new File(args.length > 0 ? args[0] : "analysis/dynamic");

        Set<Long> realStarts = new HashSet<>();
        try (BufferedReader r = new BufferedReader(new FileReader("analysis/symbols/function_map.csv"))) {
            String line = r.readLine();
            while ((line = r.readLine()) != null) {
                String a = line.split(",", 2)[0];
                try { realStarts.add(Long.parseLong(a.replace("0x", ""), 16)); } catch (NumberFormatException e) { }
            }
        }

        // ---- 1. msgSend comments
        int nc = 0;
        for (String[] p : rows(new File(dir, "msgsend_sites.tsv"))) {
            Address a = va(p[0]);
            StringBuilder sb = new StringBuilder("dyn: ");
            for (String o : p[3].split(" \\| ")) {
                if (sb.length() > 5) sb.append(" | ");
                sb.append(o.replaceAll(" x\\d+$", ""));
            }
            setPreComment(a, sb.toString());
            nc++;
        }
        println("msgSend site comments: " + nc);

        // ---- 2. BL used as branch
        int nf = 0, nr = 0;
        Set<Function> refix = new HashSet<>();
        for (String[] p : rows(new File(dir, "bl_nonreturn.tsv"))) {
            Address tgt = va(p[0]);
            for (String s : p[3].split(" ")) {
                Instruction ins = getInstructionAt(va(s));
                if (ins == null) { printerr("no insn at " + s); continue; }
                ins.setFlowOverride(FlowOverride.BRANCH);
                nf++;
            }
            if (!realStarts.contains(tgt.getOffset())) {
                Function bogus = getFunctionAt(tgt);
                if (bogus != null) {
                    removeFunction(bogus);
                    nr++;
                }
            }
            Function parent = getFunctionContaining(va(p[3].split(" ")[0]));
            if (parent != null) refix.add(parent);
        }
        for (Function f : refix) {
            CreateFunctionCmd.fixupFunctionBody(currentProgram, f, monitor);
        }
        println("BL->BRANCH overrides: " + nf + ", bogus functions removed: " + nr
                + ", bodies re-fixed: " + refix.size());

        // ---- 3. indirect targets
        int nref = 0;
        for (String[] p : rows(new File(dir, "indirect_targets.tsv"))) {
            Address src = va(p[0]);
            boolean call = p[2].equals("blx_reg");
            for (String t : p[4].split(" \\| ")) {
                Address dst = va(t.split(" ")[0]);
                createMemoryReference(currentProgram.getListing().getCodeUnitAt(src) instanceof Instruction
                        ? (Instruction) currentProgram.getListing().getCodeUnitAt(src) : null,
                        src, dst, call ? RefType.COMPUTED_CALL : RefType.COMPUTED_JUMP);
                nref++;
            }
        }
        println("indirect references added: " + nref);
    }

    void createMemoryReference(Instruction ins, Address src, Address dst, RefType t) {
        if (ins == null) { printerr("no insn at " + src); return; }
        currentProgram.getReferenceManager().addMemoryReference(src, dst, t, SourceType.ANALYSIS, 0);
    }
}
