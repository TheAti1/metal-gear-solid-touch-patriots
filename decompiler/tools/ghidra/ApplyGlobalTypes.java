/* One consistent type (and a name) for every unnamed global the game code
 * touches (DAT_xxxxxxxx - mostly file-static variables in __bss/__common that
 * have no symbol, e.g. Player.mm's HP at 0x84b44).
 *
 * For each function the decompiler's inferred type of every HighGlobal is
 * tallied per address; the most common concrete type (float beats int for
 * the same size, pointer beats int) is defined as data there. Name:
 * <SourceFile>_<addr> after the source file whose functions use it most
 * (statics are file-local), or the known name where the meaning was
 * established (LOG steps 2/5, oracle-verified).
 *
 * Usage: analyzeHeadless ... -postScript ApplyGlobalTypes.java   (idempotent)
 */
import java.util.*;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.HighSymbol;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.util.CodeUnitInsertionException;

public class ApplyGlobalTypes extends GhidraScript {

    /** Ghidra's default data labels (typed or not); PTR_/cf_/s_ names are kept. */
    static final java.util.regex.Pattern AUTO = java.util.regex.Pattern.compile(
            "(DAT|INT|UINT|FLOAT|DOUBLE|CHAR|UCHAR|SHORT|USHORT|BYTE|WORD|DWORD|LONG|ULONG|BOOL|SBYTE|longlong|ulonglong)_[0-9a-f]{8}");
    static final Map<Long, String> KNOWN = new HashMap<>();
    static {
        KNOWN.put(0x84b44L, "Player_s_hp");            // +[Player getHP] / setDamage::: (oracle: god mode)
        KNOWN.put(0x84b48L, "Player_s_maxHp");         // +[Player getMaxHP]
        KNOWN.put(0x84b58L, "Player_s_weaponMode");    // switch in private_getDamageVal
        KNOWN.put(0x84c98L, "Player_s_noDamage");      // +[Player isNoDamage]
        KNOWN.put(0x84d60L, "Stage_s_subNum");         // +[Stage setSubNum:] (oracle: sub-stage log)
        KNOWN.put(0x84d6cL, "Stage_s_enemyMax");       // +[Stage getEnemyMax]
    }

    @Override
    protected void run() throws Exception {
        Map<Long, Map<String, Integer>> votes = new HashMap<>();
        Map<Long, Map<String, Integer>> files = new HashMap<>();
        Map<String, DataType> byName = new HashMap<>();
        DecompInterface d = new DecompInterface();
        d.toggleSyntaxTree(true);
        d.openProgram(currentProgram);
        int nf = 0;
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            if (f.isThunk() || f.isExternal()) continue;
            DecompileResults r = d.decompileFunction(f, 120, monitor);
            if (!r.decompileCompleted()) continue;
            HighFunction hf = r.getHighFunction();
            String src = f.getComment() != null && f.getComment().startsWith("Original source: ")
                    ? f.getComment().substring(17).split("\\R")[0].replaceAll(".*/", "").replaceAll("\\.\\w+$", "")
                    : "global";
            // globals show up as RAM varnodes in the high p-code, each with the
            // HighVariable (and type) the decompiler inferred in this function
            Set<Long> seenHere = new HashSet<>();
            Iterator<ghidra.program.model.pcode.PcodeOpAST> it = hf.getPcodeOps();
            while (it.hasNext()) {
                ghidra.program.model.pcode.PcodeOpAST op = it.next();
                int oc = op.getOpcode();
                ghidra.program.model.pcode.Varnode val;
                List<DataType> ts = new ArrayList<>();
                if (oc == ghidra.program.model.pcode.PcodeOp.LOAD) {
                    val = op.getOutput();
                    if (val == null) continue;
                    Iterator<ghidra.program.model.pcode.PcodeOp> ds = val.getDescendants();
                    while (ds.hasNext()) { DataType t = usageType(ds.next(), val); if (t != null) ts.add(t); }
                } else if (oc == ghidra.program.model.pcode.PcodeOp.STORE) {
                    val = op.getInput(2);
                    if (val.getDef() != null) { DataType t = usageType(val.getDef(), val); if (t != null) ts.add(t); }
                } else {
                    continue;
                }
                Long addr = constAddr(op.getInput(1), 0);
                if (addr == null) continue;
                boolean fallback = ts.isEmpty();
                if (fallback) {
                    // only copied / set to constants: plain integer of the accessed size
                    // (weak vote: any usage evidence from another function wins)
                    DataType fb = val.getSize() == 1 ? CharDataType.dataType : val.getSize() == 2 ? ShortDataType.dataType
                            : val.getSize() == 4 ? IntegerDataType.dataType : null;
                    if (fb == null) continue;
                    ts.add(fb);
                }
                Address a = toAddr(addr);
                MemoryBlock b = getMemoryBlock(a);
                // literal-pool constants live in __text: allow them, but never an instruction
                if (b == null || (b.isExecute() && getInstructionContaining(a) != null)) continue;
                Symbol s = getSymbolAt(a);
                if (s != null && !AUTO.matcher(s.getName()).matches()) continue;
                for (DataType t : ts) {
                    if (t.getLength() != val.getSize()) continue;
                    if (!seenHere.add(addr * 64 + t.getLength() * 8 + rank(t))) continue;
                    votes.computeIfAbsent(addr, k -> new HashMap<>()).merge(t.getPathName(), fallback ? 1 : 1000, Integer::sum);
                    byName.put(t.getPathName(), t);
                    files.computeIfAbsent(addr, k -> new HashMap<>()).merge(src, 1, Integer::sum);
                }
            }
            if (++nf % 300 == 0) println("  functions: " + nf);
        }
        d.dispose();

        int typed = 0, named = 0, conflicts = 0, failed = 0;
        for (Map.Entry<Long, Map<String, Integer>> e : votes.entrySet()) {
            String best = pick(e.getValue(), byName);
            if (e.getValue().size() > 1) conflicts++;
            DataType t = byName.get(best);
            Address a = toAddr(e.getKey());
            try {
                Data cur = getDataAt(a);
                if (cur == null || !cur.isDefined() || cur.getDataType().getName().startsWith("undefined")) {
                    DataUtilities.createData(currentProgram, a, t, t.getLength(), false,
                            DataUtilities.ClearDataMode.CLEAR_ALL_UNDEFINED_CONFLICT_DATA);
                    typed++;
                }
            } catch (CodeUnitInsertionException | IllegalArgumentException ex) {
                failed++;
            }
            String file = files.get(e.getKey()).entrySet().stream()
                    .max(Map.Entry.comparingByValue()).get().getKey();
            String name = KNOWN.getOrDefault(e.getKey(), file + "_" + Long.toHexString(e.getKey()));
            Symbol s = getSymbolAt(a);
            // only unnamed data: never replace Ghidra's informative auto names
            // (PTR__g_accelerometer_..., cf_..., s_...)
            if (s == null || AUTO.matcher(s.getName()).matches()) {
                createLabel(a, name, true, SourceType.ANALYSIS);
                named++;
            }
        }
        // ---- record-array pointers with clear element evidence
        int ptrs = 0;
        DataTypeManager dtm = currentProgram.getDataTypeManager();
        DataType ene = dtm.getDataType(new CategoryPath("/mgst"), "EneDat");
        Object[][] P = {
            {0x75ad8L, ene != null ? new PointerDataType(ene) : null, "enemy_data"},             // stride 0x2fc = EneDat
            {0x75778L, new PointerDataType(CharDataType.dataType), null},                          // GSaveCtrl::SaveData (1024-byte buffer)
            {0x755acL, new PointerDataType(IntegerDataType.dataType), null},                       // g_appear (int per pattern)
            {0x80f74L, new PointerDataType(IntegerDataType.dataType), null},                       // g_saveHp
            // the __nl_symbol_ptr slots the code actually loads them through
            {0x69074L, ene != null ? new PointerDataType(new PointerDataType(ene)) : null, null},
            {0x69030L, new PointerDataType(new PointerDataType(CharDataType.dataType)), null},
            {0x69040L, new PointerDataType(new PointerDataType(IntegerDataType.dataType)), null},
            {0x69048L, new PointerDataType(new PointerDataType(IntegerDataType.dataType)), null}};
        for (Object[] q : P) {
            if (q[1] == null) continue;
            Address a = toAddr((Long) q[0]);
            try {
                Data dd = DataUtilities.createData(currentProgram, a, (DataType) q[1], 4, false,
                        DataUtilities.ClearDataMode.CLEAR_ALL_CONFLICT_DATA);
                if (a.getOffset() < 0x6a000) MutabilitySettingsDefinition.DEF.setChoice(dd, MutabilitySettingsDefinition.CONSTANT);
                ptrs++;
            } catch (Exception ex) { printerr("pointer type at " + a + ": " + ex.getMessage()); }
        }

        // ---- name every remaining auto-labelled global that code references,
        // after the source file of the referencing functions (file statics)
        int named2 = 0;
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            if (b.isExecute() || !(b.getName().contains("bss") || b.getName().contains("common") || b.getName().equals("__data"))) continue;
            // DAT_ labels are dynamic (no stored symbol): walk reference destinations
            ghidra.program.model.address.AddressIterator it2 = currentProgram.getReferenceManager()
                    .getReferenceDestinationIterator(new ghidra.program.model.address.AddressSet(b.getStart(), b.getEnd()), true);
            while (it2.hasNext()) {
                Address a = it2.next();
                Symbol sym = currentProgram.getSymbolTable().getPrimarySymbol(a);
                if (sym != null && !sym.isDynamic() && !AUTO.matcher(sym.getName()).matches()) continue;
                if (sym != null && !AUTO.matcher(sym.getName()).matches()) continue;
                Map<String, Integer> byFile = new HashMap<>();
                for (ghidra.program.model.symbol.Reference r : getReferencesTo(a)) {
                    Function f = getFunctionContaining(r.getFromAddress());
                    if (f != null) byFile.merge(srcOf(f), 1, Integer::sum);
                }
                if (byFile.isEmpty()) continue;
                String file = byFile.entrySet().stream().max(Map.Entry.comparingByValue()).get().getKey();
                String nm = KNOWN.getOrDefault(a.getOffset(), file + "_" + Long.toHexString(a.getOffset()));
                try { createLabel(a, nm, true, SourceType.ANALYSIS); named2++; } catch (Exception ex) { }
            }
        }
        println("record pointers typed: " + ptrs + ", further globals named from references: " + named2);

        println("globals seen: " + votes.size() + ", typed: " + typed + ", named: " + named
                + ", with conflicting per-function types: " + conflicts + ", failed: " + failed);
    }

    Long constAddr(ghidra.program.model.pcode.Varnode v, int depth) {
        if (v == null || depth > 4) return null;
        if (v.isConstant()) return v.getOffset();
        if (v.isAddress() && v.getSize() == 4) {
            // PIC: the global's address is a literal-pool word in __text
            // (read-only) plus a constant - read the word
            MemoryBlock b = getMemoryBlock(v.getAddress());
            if (b != null && b.isInitialized() && !b.isWrite()) {
                try { return getInt(v.getAddress()) & 0xffffffffL; } catch (Exception e) { return null; }
            }
        }
        ghidra.program.model.pcode.PcodeOp d = v.getDef();
        if (d == null) return null;
        int oc = d.getOpcode();
        if (oc == ghidra.program.model.pcode.PcodeOp.PTRSUB || oc == ghidra.program.model.pcode.PcodeOp.INT_ADD) {
            Long x = constAddr(d.getInput(0), depth + 1), y = constAddr(d.getInput(1), depth + 1);
            return x != null && y != null ? x + y : null;
        }
        if (oc == ghidra.program.model.pcode.PcodeOp.COPY || oc == ghidra.program.model.pcode.PcodeOp.CAST) {
            return constAddr(d.getInput(0), depth + 1);
        }
        return null;
    }

    String srcOf(Function f) {
        String c = f.getComment();
        if (c == null || !c.startsWith("Original source: ")) return "global";
        String first = c.substring(17).split("\n")[0].trim();
        int slash = first.lastIndexOf('/');
        if (slash >= 0) first = first.substring(slash + 1);
        int dot = first.lastIndexOf('.');
        return dot > 0 ? first.substring(0, dot) : first;
    }

    /** Type implied by how the op uses the global (the high types of
     *  unnamed globals stay undefinedN, so usage is the evidence). */
    DataType usageType(ghidra.program.model.pcode.PcodeOp op, ghidra.program.model.pcode.Varnode v) {
        int oc = op.getOpcode();
        int sz = v.getSize();
        boolean fl = oc >= ghidra.program.model.pcode.PcodeOp.FLOAT_EQUAL && oc <= ghidra.program.model.pcode.PcodeOp.FLOAT_ROUND
                && !(oc == ghidra.program.model.pcode.PcodeOp.FLOAT_INT2FLOAT && op.getOutput() != v);
        if (oc == ghidra.program.model.pcode.PcodeOp.FLOAT_TRUNC && op.getOutput() == v) fl = false;
        if (fl) return sz == 8 ? DoubleDataType.dataType : sz == 4 ? FloatDataType.dataType : null;
        boolean uns = oc == ghidra.program.model.pcode.PcodeOp.INT_LESS || oc == ghidra.program.model.pcode.PcodeOp.INT_LESSEQUAL
                || oc == ghidra.program.model.pcode.PcodeOp.INT_ZEXT;
        boolean sig = oc == ghidra.program.model.pcode.PcodeOp.INT_SLESS || oc == ghidra.program.model.pcode.PcodeOp.INT_SLESSEQUAL
                || oc == ghidra.program.model.pcode.PcodeOp.INT_SEXT || oc == ghidra.program.model.pcode.PcodeOp.INT_SDIV
                || oc == ghidra.program.model.pcode.PcodeOp.INT_SREM || oc == ghidra.program.model.pcode.PcodeOp.INT_SRIGHT;
        boolean arith = oc == ghidra.program.model.pcode.PcodeOp.INT_ADD || oc == ghidra.program.model.pcode.PcodeOp.INT_SUB
                || oc == ghidra.program.model.pcode.PcodeOp.INT_MULT || oc == ghidra.program.model.pcode.PcodeOp.INT_EQUAL
                || oc == ghidra.program.model.pcode.PcodeOp.INT_NOTEQUAL;
        if (!uns && !sig && !arith) return null;
        switch (sz) {
            case 1: return uns ? UnsignedCharDataType.dataType : CharDataType.dataType;
            case 2: return uns ? UnsignedShortDataType.dataType : ShortDataType.dataType;
            case 4: return uns ? UnsignedIntegerDataType.dataType : IntegerDataType.dataType;
            case 8: return uns ? UnsignedLongLongDataType.dataType : LongLongDataType.dataType;
        }
        return null;
    }

    /** Majority type; on a tie of equal-size types prefer float/double, then pointer. */
    String pick(Map<String, Integer> v, Map<String, DataType> byName) {
        return v.entrySet().stream().max((x, y) -> {
            int c = Integer.compare(x.getValue(), y.getValue());
            if (c != 0) return c;
            return Integer.compare(rank(byName.get(x.getKey())), rank(byName.get(y.getKey())));
        }).get().getKey();
    }

    int rank(DataType t) {
        if (t instanceof FloatDataType || t instanceof DoubleDataType) return 4;
        if (t instanceof AbstractIntegerDataType && !((AbstractIntegerDataType) t).isSigned()) return 3;
        if (t instanceof Pointer) return 2;
        return 1;
    }
}
