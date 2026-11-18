/* Give a return type to C/C++ functions declared `void` whose callers use r0
 * after the call (LOG 2026-10-08 STEP 3). C++ mangling does not encode the
 * return type, so Ghidra guessed void for e.g. SoundManager::play2DSound
 * (returns the Sound * it creates): the caller's `_pSounds[n] = <result>`
 * decompiled as `_pSounds[n] = iVar1` (the argument still in its variable),
 * and the recompiled C stored the wrong value.
 *
 * Evidence, from the machine code: r0 is caller-saved, so an instruction
 * after the call that READS r0 before anything writes it uses the callee's
 * return value. Checked with Ghidra's per-instruction input/result register
 * sets up to the next branch/call. Objective-C methods are skipped (their
 * returns come from the runtime type encodings; audited by A2), and so are
 * call-fixup helpers (switch tables follow their call; vfp save keeps r0).
 *   -> return type undefined4, listed in analysis/symbols/void_returns.tsv
 * Idempotent (a function no longer void is not re-examined).
 */
import java.io.*;
import java.util.*;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.*;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class FixVoidReturns extends GhidraScript {
    @Override
    protected void run() throws Exception {
        Set<Long> objc = new HashSet<>();
        try (BufferedReader r = new BufferedReader(new FileReader("analysis/objc/methods.tsv"))) {
            String l;
            while ((l = r.readLine()) != null) {
                String[] p = l.split("\t");
                if (p.length > 4 && p[4].startsWith("0x")) objc.add(Long.decode(p[4]) & ~1L);
            }
        }
        Register r0 = currentProgram.getRegister("r0");
        List<String> rows = new ArrayList<>();
        int checked = 0, fixed = 0;
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            if (f.isThunk() || objc.contains(f.getEntryPoint().getOffset())) continue;
            // runtime helpers modelled as call-fixups (switch helpers: the bytes
            // after the call are the inline table; ___save_vfp_*: preserve r0)
            if (f.getCallFixup() != null || f.getName().matches("___(save|restore)_vfp_.*")) continue;
            if (!(f.getReturnType() instanceof VoidDataType)) continue;
            checked++;
            List<String> ev = new ArrayList<>();
            for (Reference ref : getReferencesTo(f.getEntryPoint())) {
                if (!ref.getReferenceType().isCall()) continue;
                Instruction call = getInstructionAt(ref.getFromAddress());
                if (call == null) continue;
                Instruction in = call.getNext();
                for (int k = 0; in != null && k < 8; k++, in = in.getNext()) {
                    boolean reads = false, writes = false;
                    for (Object o : in.getInputObjects()) if (r0.equals(o)) reads = true;
                    for (Object o : in.getResultObjects()) if (r0.equals(o)) writes = true;
                    if (reads) { ev.add(ref.getFromAddress() + ":" + in); break; }
                    if (writes || in.getFlowType().isCall() || in.getFlowType().isJump() || in.getFlowType().isTerminal()) break;
                }
            }
            if (ev.isEmpty()) continue;
            f.setReturnType(Undefined4DataType.dataType, SourceType.USER_DEFINED);
            rows.add(f.getEntryPoint() + "\t" + f.getName(true) + "\t" + ev.size() + "\t" + String.join(" | ", ev.subList(0, Math.min(3, ev.size()))));
            fixed++;
        }
        // optional arg: report path (tools/build_ghidra_project.sh writes it to
        // its log dir; the tracked analysis/symbols/void_returns.tsv is the
        // record of the original project)
        String outPath = getScriptArgs().length > 0 ? getScriptArgs()[0] : "analysis/symbols/void_returns.tsv";
        try (PrintWriter w = new PrintWriter(new FileWriter(outPath, fixed == 0))) {
            if (fixed > 0) w.println("# C/C++ functions declared void whose callers read r0 after the call (FixVoidReturns.java)\naddr\tfunction\tcall_sites_reading_r0\tevidence");
            for (String x : rows) w.println(x);
        }
        for (String x : rows) println(x);
        println("FixVoidReturns: " + checked + " void C/C++ functions checked, " + fixed + " given a return value");
    }
}
