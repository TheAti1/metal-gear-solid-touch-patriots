/* Type stack structs that are passed by address but which Ghidra split into
 * unrelated scalar locals (LOG 2026-10-07 STEP 3). In recompiled C the
 * pieces become independent variables: what the callee writes through the
 * pointer is not what the function later reads (and stores to the pieces
 * are dead), so the C diverges from the binary.
 *   objc_msgSendSuper2(&sup, ...)        struct objc_super      {receiver, class}
 *   [x countByEnumeratingWithState:&st objects:buf count:n]  (for-in loops)
 *                                        NSFastEnumerationState {state, itemsPtr,
 *                                                                mutationsPtr, extra[5]}
 * For each call site the argument's stack slot gets the struct type
 * (overlapping locals are cleared). Supersedes FixObjcSuperLocals.java.
 * Idempotent.
 */
import java.util.*;

import ghidra.app.decompiler.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.pcode.*;
import ghidra.program.model.symbol.SourceType;

public class FixStackStructLocals extends GhidraScript {
    static final long MSGSEND = 0x5add0, SUPER2 = 0x5addc;

    DataType ptr() { return new PointerDataType(VoidDataType.dataType); }

    @Override
    protected void run() throws Exception {
        DataTypeManager dtm = currentProgram.getDataTypeManager();
        StructureDataType sup = new StructureDataType(new CategoryPath("/mgst"), "objc_super", 0);
        sup.add(ptr(), 4, "receiver", null);
        sup.add(ptr(), 4, "super_class", "current class (objc_msgSendSuper2 starts at its superclass)");
        DataType tSup = dtm.addDataType(sup, DataTypeConflictHandler.REPLACE_HANDLER);
        StructureDataType fe = new StructureDataType(new CategoryPath("/mgst"), "NSFastEnumerationState", 0);
        fe.add(UnsignedIntegerDataType.dataType, 4, "state", null);
        fe.add(new PointerDataType(ptr()), 4, "itemsPtr", null);
        fe.add(new PointerDataType(UnsignedIntegerDataType.dataType), 4, "mutationsPtr", null);
        fe.add(new ArrayDataType(UnsignedIntegerDataType.dataType, 5, 4), 20, "extra", null);
        DataType tFe = dtm.addDataType(fe, DataTypeConflictHandler.REPLACE_HANDLER);

        DecompInterface d = new DecompInterface();
        d.setOptions(new DecompileOptions());
        d.openProgram(currentProgram);
        Map<String, Integer> stats = new TreeMap<>();
        Set<Function> todo = new LinkedHashSet<>();
        for (long tgt : new long[]{MSGSEND, SUPER2})
            for (ghidra.program.model.symbol.Reference r : getReferencesTo(toAddr(tgt))) {
                Function f = getFunctionContaining(r.getFromAddress());
                if (f != null && !f.isThunk()) todo.add(f);
            }
        for (Function f : todo) {
            DecompileResults res = d.decompileFunction(f, 60, monitor);
            HighFunction hf = res.getHighFunction();
            if (hf == null) { stats.merge("decompile failed", 1, Integer::sum); continue; }
            Map<Integer, DataType> want = new TreeMap<>();
            Iterator<PcodeOpAST> it = hf.getPcodeOps();
            while (it.hasNext()) {
                PcodeOpAST op = it.next();
                if (op.getOpcode() != PcodeOp.CALL) continue;
                long tgt = op.getInput(0).getAddress().getOffset();
                int argIdx = -1;
                DataType ty = null;
                if (tgt == SUPER2) { argIdx = 1; ty = tSup; }
                else if (tgt == MSGSEND && op.getNumInputs() > 3
                        && "countByEnumeratingWithState:objects:count:".equals(selectorOf(op.getInput(2)))) {
                    argIdx = 3; ty = tFe;
                }
                if (argIdx < 0) continue;
                stats.merge("sites " + ty.getName(), 1, Integer::sum);
                Integer off = stackOffset(op.getInput(argIdx));
                if (off == null) { stats.merge("not a stack address " + ty.getName(), 1, Integer::sum); continue; }
                want.put(off, ty);
            }
            StackFrame fr = f.getStackFrame();
            for (Map.Entry<Integer, DataType> e : want.entrySet()) {
                int off = e.getKey();
                DataType ty = e.getValue();
                Variable v = fr.getVariableContaining(off);
                if (v != null && v.getStackOffset() == off && v.getDataType().isEquivalent(ty)) {
                    stats.merge("already " + ty.getName(), 1, Integer::sum);
                    continue;
                }
                for (int k = 0; k < ty.getLength(); k++) {
                    Variable c = fr.getVariableContaining(off + k);
                    if (c != null) fr.clearVariable(c.getStackOffset());
                }
                fr.createVariable((ty == tSup ? "sup_" : "fe_") + Integer.toHexString(Math.abs(off)), off, ty,
                        SourceType.USER_DEFINED);
                stats.merge("typed " + ty.getName(), 1, Integer::sum);
            }
        }
        println("FixStackStructLocals: " + stats);
    }

    Integer stackOffset(Varnode a) {
        PcodeOp def = a.getDef();
        while (def != null && (def.getOpcode() == PcodeOp.COPY || def.getOpcode() == PcodeOp.CAST)) def = def.getInput(0).getDef();
        if (def != null && def.getOpcode() == PcodeOp.PTRSUB && def.getInput(1).isConstant())
            return (int) def.getInput(1).getOffset();
        return null;
    }

    String selectorOf(Varnode v) throws Exception {
        for (int hop = 0; hop < 4 && v != null; hop++) {
            if (v.isConstant() || v.isAddress()) return stringOrSelref(v.getOffset());
            PcodeOp def = v.getDef();
            if (def == null) return null;
            if (def.getOpcode() == PcodeOp.LOAD && def.getInput(1).isConstant())
                return stringOrSelref(getInt(toAddr(def.getInput(1).getOffset())) & 0xffffffffL);
            if (def.getOpcode() == PcodeOp.COPY || def.getOpcode() == PcodeOp.CAST) { v = def.getInput(0); continue; }
            if (def.getOpcode() == PcodeOp.PTRSUB && def.getInput(0).isConstant() && def.getInput(1).isConstant())
                return stringOrSelref(def.getInput(0).getOffset() + def.getInput(1).getOffset());
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
        return sb.toString();
    }
}
