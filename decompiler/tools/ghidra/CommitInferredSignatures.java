/* Commit decompiler-inferred types for the parts of function signatures that
 * are still undefinedN - and ONLY those. ObjC methods (ApplyObjcTypes),
 * imports (ApplyExternalPrototypes) and demangled C++ parameters keep their
 * types; e.g. `undefined4 SoundService::setMasterVolume(SoundService *this,
 * float)` gets its return type from what the decompiler sees returned.
 * Untyped signatures otherwise spread undefined4 into every caller.
 *
 * Two passes (callers benefit from callees committed in pass 1).
 * Usage: analyzeHeadless ... -postScript CommitInferredSignatures.java
 */
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.Undefined;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.pcode.FunctionPrototype;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.HighSymbol;
import ghidra.program.model.symbol.SourceType;

public class CommitInferredSignatures extends GhidraScript {

    static boolean undef(DataType t) {
        return t == null || Undefined.isUndefined(t) || t.getName().startsWith("undefined");
    }

    @Override
    protected void run() throws Exception {
        DecompInterface d = new DecompInterface();
        d.openProgram(currentProgram);
        for (int pass = 1; pass <= 2; pass++) {
            int rets = 0, params = 0, seen = 0;
            for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
                if (f.isThunk() || f.isExternal()) continue;
                boolean retU = undef(f.getReturnType()) && !f.getReturnType().getName().equals("void");
                boolean parU = false;
                for (Parameter p : f.getParameters()) if (undef(p.getDataType())) parU = true;
                if (!retU && !parU) continue;
                seen++;
                DecompileResults r = d.decompileFunction(f, 120, monitor);
                if (!r.decompileCompleted()) continue;
                HighFunction hf = r.getHighFunction();
                FunctionPrototype fp = hf.getFunctionPrototype();
                if (retU && fp.getReturnType() != null && !undef(fp.getReturnType())) {
                    try {
                        f.setReturnType(fp.getReturnType(), SourceType.ANALYSIS);
                        rets++;
                    } catch (Exception e) { }
                }
                if (parU) {
                    Parameter[] ps = f.getParameters();
                    for (int i = 0; i < ps.length && i < hf.getLocalSymbolMap().getNumParams(); i++) {
                        if (!undef(ps[i].getDataType())) continue;
                        HighSymbol hs = hf.getLocalSymbolMap().getParamSymbol(i);
                        if (hs == null || undef(hs.getDataType())) continue;
                        try {
                            ps[i].setDataType(hs.getDataType(), SourceType.ANALYSIS);
                            params++;
                        } catch (Exception e) { }
                    }
                }
            }
            println("pass " + pass + ": functions with untyped signature parts " + seen
                    + ", return types committed " + rets + ", parameter types committed " + params);
        }
        d.dispose();
    }
}
