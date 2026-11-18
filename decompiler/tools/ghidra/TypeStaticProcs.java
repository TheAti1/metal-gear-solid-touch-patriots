/* Type function-static `proc` pointers of extension wrappers (LOG 2026-10-07
 * STEP 2). _alBufferDataStaticProc / alcMacOSMixerOutputRateProc follow
 * Apple's OpenAL sample: `static proc; if (!proc) proc = alGetProcAddress(..);
 * if (proc) proc(<the wrapper's own arguments>)`. The static is untyped
 * (undefined *), so the indirect call is not a callable in C. Its type is a
 * pointer to the enclosing wrapper's own signature. Idempotent.
 */
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.*;

public class TypeStaticProcs extends GhidraScript {
    @Override
    protected void run() throws Exception {
        int n = 0;
        for (Symbol s : currentProgram.getSymbolTable().getSymbols("proc")) {
            Namespace ns = s.getParentNamespace();
            if (!(ns instanceof Function)) {
                Function f = getFunctionAt(s.getAddress());
                if (f != null) continue;
                // namespace named after the function signature (C++ local static)
                Function owner = null;
                for (Function f2 : currentProgram.getFunctionManager().getFunctions(true))
                    if (ns.getName().startsWith(f2.getName() + "(")) { owner = f2; break; }
                if (owner == null) { printerr("no owner for " + s.getName(true)); continue; }
                ns = owner;
            }
            Function owner = (Function) ns;
            FunctionDefinitionDataType fd = new FunctionDefinitionDataType(owner.getSignature());
            fd.setName(owner.getName() + "_proc_t");
            DataType ft = currentProgram.getDataTypeManager().addDataType(fd, DataTypeConflictHandler.REPLACE_HANDLER);
            Pointer pt = new PointerDataType(ft);
            clearListing(s.getAddress(), s.getAddress().add(3));
            Data d = createData(s.getAddress(), pt);
            println(s.getName(true) + " @ " + s.getAddress() + " -> " + d.getDataType().getDisplayName());
            n++;
        }
        println("TypeStaticProcs: " + n + " typed");
    }
}
