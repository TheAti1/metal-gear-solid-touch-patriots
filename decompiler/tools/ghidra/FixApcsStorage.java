/* Parameter/return storage per Apple's armv6 calling convention (APCS-gnu
 * style, the ABI tools/mgst_recompile.py compiles with), for every function
 * Ghidra's ARM allocator gets wrong (LOG 2026-10-07 STEP 2):
 *   - a composite (struct) return > 4 bytes comes back through a hidden
 *     pointer in r0 (objc_msgSend_stret callers already pass it); made an
 *     explicit first parameter `__stret`, return void. Ghidra returned CGPoint
 *     in r0:r1 and shifted self/_cmd/arguments one register;
 *   - arguments are 4-byte aligned words in r0-r3 then the stack; an 8-byte
 *     scalar or a struct may SPLIT between r3 and the stack. Ghidra put
 *     CGRect/CGPoint/double arguments wholly on the stack and back-filled
 *     later ones into r2/r3 (proved wrong from the machine code of
 *     SoundMisc::calculateByteForTime: its double is in r2:r3).
 * A by-value struct parameter is FLATTENED into its scalar fields (each a
 * whole word for the all-float CG structs: same ABI, word for word), so every
 * word has plain register or plain stack storage: the decompiler does not
 * translate the stack piece of a joined register+stack parameter from the
 * callee's frame to the caller's (it showed up as the caller's own
 * `_uStack00000000` in -[Texture2D(Image) initWithImage:]).
 * Applied as custom storage to every function (internal and import) with a
 * composite parameter, an 8-byte scalar parameter or a composite return
 * > 4 bytes. Multi-register storage is most-significant first. Idempotent.
 *
 * Usage: analyzeHeadless analysis/ghidra MGST -process MGSTUS -noanalysis
 *          -scriptPath tools/ghidra -postScript FixApcsStorage.java
 */
import java.util.*;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.*;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.*;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.symbol.SourceType;

public class FixApcsStorage extends GhidraScript {
    Register[] R;

    static DataType base(DataType t) {
        while (t instanceof TypeDef) t = ((TypeDef) t).getBaseDataType();
        return t;
    }

    static boolean composite(DataType t) {
        t = base(t);
        return t instanceof Structure || t instanceof Union || t instanceof Array;
    }

    /** words [first, first+n) of the argument area: r0-r3 then stack. */
    VariableStorage words(int first, int size) throws Exception {
        int n = (size + 3) / 4;
        List<Varnode> v = new ArrayList<>();      // least significant first, reversed below
        int regWords = Math.max(0, Math.min(n, 4 - first));
        for (int k = 0; k < regWords; k++) v.add(new Varnode(R[first + k].getAddress(), 4));
        if (regWords < n) {
            int stackOff = Math.max(0, first - 4) * 4;
            int stackSize = size - regWords * 4;
            Address sa = currentProgram.getAddressFactory().getStackSpace().getAddress(stackOff);
            v.add(new Varnode(sa, stackSize));
        }
        if (v.size() == 1 && regWords == 1 && size < 4) {
            return new VariableStorage(currentProgram, new Varnode(R[first].getAddress(), 4));
        }
        Collections.reverse(v);
        return new VariableStorage(currentProgram, v.toArray(new Varnode[0]));
    }

    @Override
    protected void run() throws Exception {
        R = new Register[4];
        for (int i = 0; i < 4; i++) R[i] = currentProgram.getRegister("r" + i);
        int changed = 0, seen = 0;
        List<Function> all = new ArrayList<>();
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) all.add(f);
        for (Function f : currentProgram.getFunctionManager().getExternalFunctions()) all.add(f);
        for (Function f : all) {
            if (f.isThunk()) continue;                 // the thunked (external) one carries it
            DataType rt = f.getReturnType();
            // Ghidra may already model the struct return as forced-indirect
            // (return type shown as a pointer, auto __return_storage_ptr__)
            if (f.getReturn().getVariableStorage().isForcedIndirect() && base(rt) instanceof Pointer)
                rt = ((Pointer) base(rt)).getDataType();
            boolean stret = composite(rt) && rt.getLength() > 4;
            boolean need = stret;
            for (Parameter p : f.getParameters()) {
                DataType t = p.getDataType();
                if (composite(t) || (base(t).getLength() == 8 && !(base(t) instanceof Pointer))) need = true;
            }
            if (!need) continue;
            seen++;
            List<ParameterImpl> ps = new ArrayList<>();
            int w = 0;
            if (stret) {
                ps.add(new ParameterImpl("__stret", new PointerDataType(rt), words(0, 4), currentProgram));
                w = 1;
            }
            List<Object[]> flat = new ArrayList<>();       // {name, type}
            boolean ok = true;
            for (Parameter p : f.getParameters()) {
                // Ghidra's auto hidden-return pointer is replaced by __stret;
                // an auto `this` stays, as an explicit first parameter
                if (p.isAutoParameter() && !p.getName().equals("this")) continue;
                ok &= flatten(p.getName(), p.getDataType(), flat);
            }
            if (!ok) { printerr("not flattened (sub-word struct fields): " + f.getName(true)); continue; }
            for (Object[] x : flat) {
                DataType t = (DataType) x[1];
                int size = Math.max(4, t.getLength());
                ps.add(new ParameterImpl((String) x[0], t, words(w, t.getLength() < 4 ? t.getLength() : size), currentProgram));
                w += (size + 3) / 4;
            }
            ReturnParameterImpl ret = stret
                    ? new ReturnParameterImpl(VoidDataType.dataType, VariableStorage.VOID_STORAGE, currentProgram)
                    : new ReturnParameterImpl(rt, f.getReturn().getVariableStorage(), currentProgram);
            String before = f.getSignature().getPrototypeString() + " " + storageOf(f);
            f.setCustomVariableStorage(true);
            f.updateFunction(f.getCallingConventionName(), ret, ps, FunctionUpdateType.CUSTOM_STORAGE, true,
                    SourceType.USER_DEFINED);
            String after = f.getSignature().getPrototypeString() + " " + storageOf(f);
            if (!after.equals(before)) {
                changed++;
                println(f.getEntryPoint() + " " + f.getName(true) + "\n    was " + before + "\n    now " + after);
            }
        }
        println("FixApcsStorage: " + seen + " functions checked, " + changed + " changed");
    }

    /** Struct -> its scalar leaves `name_field`; false if a leaf is not a
     *  whole number of words (APCS packs such fields; not flattenable). */
    static boolean flatten(String name, DataType t, List<Object[]> out) {
        DataType b = base(t);
        if (b instanceof Structure) {
            for (DataTypeComponent c : ((Structure) b).getDefinedComponents()) {
                String fn = c.getFieldName() != null ? c.getFieldName() : "f" + c.getOrdinal();
                if (!flatten(name + "_" + fn, c.getDataType(), out)) return false;
            }
            return true;
        }
        if (composite(b)) return false;
        if (b.getLength() % 4 != 0 && !out.isEmpty() && name.contains("_")) return false;
        out.add(new Object[]{name, t});
        return true;
    }

    static String storageOf(Function f) {
        StringBuilder b = new StringBuilder("[");
        for (Parameter p : f.getParameters()) b.append(p.getName()).append('@').append(p.getVariableStorage()).append(' ');
        return b.append("]").toString();
    }
}
