/* Does any caller use a function's return value? (LOG 2026-10-09)
 *
 * C++ mangled names carry no return type, so Ghidra infers one; 20 functions
 * then test "return-unverified" (r0 differs, but r0 may be garbage). The
 * binary answers it: after each call site, follow the caller's instructions
 * (straight-line, then both edges of branches, bounded) until r0 is
 * overwritten (dead: value unused) or read (used). A function none of whose
 * call sites reads r0 (nor r1, for 64-bit returns) returns nothing.
 *
 * Args: output tsv, then function addresses (hex). Writes
 *   addr  name  sites  used_r0  used_r1  verdict(void|value|unknown)
 * Read-only.
 */
import java.io.*;
import java.util.*;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnalyzeReturnUse extends GhidraScript {
    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(args[0]));
        out.println("addr\tname\tsites\tused_r0\tused_r1\tverdict\tevidence");
        Register r0 = currentProgram.getRegister("r0"), r1 = currentProgram.getRegister("r1");
        for (int i = 1; i < args.length; i++) {
            Function f = getFunctionAt(toAddr(Long.decode(args[i])));
            if (f == null) continue;
            int sites = 0, u0 = 0, u1 = 0, unk = 0;
            passUp = 0; reads.clear();
            for (Reference ref : getReferencesTo(f.getEntryPoint())) {
                if (!ref.getReferenceType().isCall()) continue;
                Instruction call = getInstructionAt(ref.getFromAddress());
                if (call == null) continue;
                sites++;
                Function caller = getFunctionContaining(call.getAddress());
                int rs = caller == null ? 8 : (caller.getReturnType() instanceof ghidra.program.model.data.VoidDataType ? 0
                        : caller.getReturnType().getLength());
                retR0 = rs > 0; retR1 = rs > 4;
                int a = use(call.getNext(), r0, 0, new HashSet<>());
                int b = use(call.getNext(), r1, 0, new HashSet<>());
                if (a > 0) u0++;
                if (b > 0) u1++;
                if (a < 0 || b < 0) unk++;
            }
            String v = sites == 0 ? "unknown" : (u0 + u1 > 0 ? "value" : (unk > 0 ? "unknown" : "void"));
            out.println(f.getEntryPoint() + "\t" + f.getName(true) + "\t" + sites + "\t" + u0 + "\t" + u1 + "\t" + v
                    + "\tpass-up=" + passUp + " reads=" + reads);
        }
        out.close();
    }

    boolean retR0, retR1;
    int passUp; List<String> reads = new ArrayList<>();          // does the CALLER return r0 / r1 (its own declared type)?

    /** 1 = register read before written, 0 = overwritten / not read, -1 = undecided. */
    int use(Instruction ins, Register reg, int depth, Set<Address> seen) {
        for (int n = 0; ins != null && n < 64; n++) {
            if (!seen.add(ins.getAddress())) return 0;
            for (Object o : ins.getInputObjects())
                if (o instanceof Register && ((Register) o).contains(reg)) { reads.add(ins.getAddress().toString()); return 1; }
            boolean written = false;
            for (Object o : ins.getResultObjects())
                if (o instanceof Register && ((Register) o).contains(reg)) written = true;
            FlowType ft = ins.getFlowType();
            if (ft.isCall()) return 0;                     // the next call clobbers r0-r3 (args already checked)
            if (written) return 0;
            if (ft.isTerminal()) {                          // passed up only if the caller returns it
                boolean up = reg.getName().equals("r0") ? retR0 : retR1;
                if (up) passUp++;
                return up ? 1 : 0;
            }
            if (ft.isJump()) {
                if (depth > 3) return -1;
                int best = 0;
                for (Address t : ins.getFlows()) {
                    int r = use(getInstructionAt(t), reg, depth + 1, seen);
                    if (r == 1) return 1;
                    if (r < 0) best = -1;
                }
                if (ft.isConditional()) {
                    int r = use(ins.getNext(), reg, depth + 1, seen);
                    if (r == 1) return 1;
                    if (r < 0) best = -1;
                }
                return best;
            }
            ins = ins.getNext();
        }
        return -1;
    }
}
