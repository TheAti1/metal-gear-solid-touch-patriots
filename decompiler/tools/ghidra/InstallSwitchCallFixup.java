/* Fix Ghidra's handling of MGST's ___switch8/___switchu8/___switch16 jump
 * tables, PROPERLY - not by hand-decoding each call site (Phase 0 already
 * did that, 665/670 resolved - see analysis/notes/switch8_tables.md) but by
 * teaching Ghidra's OWN decompiler the table format, so its OWN value-set
 * analysis walks the table and emits a real `switch` statement, for EVERY
 * call site (not just the 665 already resolved), including a correct
 * per-call-site index-bias range check - all for free, from one shared fix.
 *
 * MECHANISM: a program-scoped compiler-spec "callfixup" extension
 * (ghidra.program.database.SpecExtension - the same public class backing
 * Ghidra's GUI "Specification Extensions" option editor). This does NOT
 * touch the shared Ghidra install - it is stored in THIS PROGRAM's own
 * database (Program Options, category "Specification Extensions"), so it is
 * project-local and travels with analysis/ghidra/MGST.rep.
 *
 * FORMATS (corrected 2026-09-29, LOG "STEPS 3+4"): Apple's three helpers are
 * real ARM-mode code and do NOT share one table shape. `ret` is the return
 * address (Thumb bit cleared); r0 is the index:
 *     ___switchu8  @0x5a5b4  u8 count N, unsigned byte entries at ret+1
 *     ___switch8   @0x5a5cc  u8 count N, signed byte entries at ret+1
 *     ___switch16  @0x5a5e4  u16 count N, signed halfword entries at ret+2
 * entry[N] is the DEFAULT, taken when r0 >= N (unsigned), and every target is
 * ret + entry*2 with the Thumb bit set. Each fixup is written in the only
 * shape that Ghidra's jumptable recovery accepts: an in-bounds guard, an
 * in-range table load, else a load of the default entry, ONE BRANCHIND.
 * (Phi-clamping the index, or two BRANCHIND exits, both fail with "Too many
 * branches".) The earlier version decoded ___switch16 as 1-byte entries and
 * ignored the default; the "all three share the 1-byte format" statement in
 * LOG STEP 6 is retracted.
 *
 * KNOWN RESIDUAL: EnemyManager updateEachCharacter: (0x2c184, switch16, 7
 * entries + default) still fails "Too many branches" although its count and
 * default fold correctly; cause unknown.
 */
import ghidra.app.script.GhidraScript;
import ghidra.program.database.SpecExtension;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;

public class InstallSwitchCallFixup extends GhidraScript {

    // The three Apple helpers (ARM-mode code at 0x5a5b4/0x5a5cc/0x5a5e4, read
    // from the binary 2026-09-29): all read a count at the return address,
    // then N+1 entries (entry N is the DEFAULT case, reached when r0 >= count),
    // target = returnAddress + entry*2, Thumb bit set.
    //   ___switchu8 : u8 count,  unsigned byte entries at ret+1
    //   ___switch8  : u8 count,  signed   byte entries at ret+1
    //   ___switch16 : u16 count, signed   half entries at ret+2
    static String fixup(String name, String target, String load, String cnt,
                        String base, String scale) {
        return
        "<callfixup name=\"" + name + "\">\n" +
        "  <target name=\"" + target + "\"/>\n" +
        "  <pcode>\n" +
        "    <body><![CDATA[\n" +
        "      tmpptr = lr & 0xfffffffe;\n" +
        "      tblsize = " + cnt + ";\n" +
        "      r12 = zext(tblsize);\n" +
        "      inbounds = r0 < r12;\n" +
        "      if (!inbounds) goto <next1>;\n" +
        "      r12 = " + load.replace("IDX", "r0") + ";\n" +
        "      <next1>\n" +
        "      if (inbounds) goto <next2>;\n" +
        "      r12 = " + load.replace("IDX", "zext(" + cnt + ")") + ";\n" +
        "      <next2>\n" +
        "      r12 = r12 * 2;\n" +
        "      lr = lr + r12;\n" +
        "      ISAModeSwitch = (lr & 1) != 0;\n" +
        "      TB = ISAModeSwitch;\n" +
        "      pc = lr & 0xfffffffe;\n" +
        "      goto [pc];\n" +
        "    ]]></body>\n" +
        "  </pcode>\n" +
        "</callfixup>\n";
    }

    static final String[][] FIXUPS = {
        {"apple_switchu8", "___switchu8"},
        {"apple_switch8", "___switch8"},
        {"apple_switch16", "___switch16"},
    };

    static String xmlFor(String name) {
        switch (name) {
        case "apple_switchu8":
            return fixup(name, "___switchu8", "zext(*:1 (tmpptr + 1 + IDX))",
                         "*:1 tmpptr", "", "");
        case "apple_switch8":
            return fixup(name, "___switch8", "sext(*:1 (tmpptr + 1 + IDX))",
                         "*:1 tmpptr", "", "");
        default:
            return fixup(name, "___switch16", "sext(*:2 (tmpptr + 2 + IDX * 2))",
                         "*:2 tmpptr", "", "");
        }
    }

    @Override
    public void run() throws Exception {
        SpecExtension ext = new SpecExtension(currentProgram);
        SymbolTable symTab = currentProgram.getSymbolTable();
        int attached = 0, missing = 0;
        for (String[] fx : FIXUPS) {
            ext.addReplaceCompilerSpecExtension(xmlFor(fx[0]), monitor);
            println("Compiler-spec extension registered/replaced: " + fx[0]);
            boolean found = false;
            for (Symbol sym : symTab.getSymbols(fx[1])) {
                Function fn = currentProgram.getFunctionManager().getFunctionAt(sym.getAddress());
                if (fn == null) {
                    println("WARNING: no function object at " + fx[1] + " @ " + sym.getAddress());
                    continue;
                }
                fn.setCallFixup(fx[0]);
                println("  " + fx[1] + " @ " + fn.getEntryPoint() + " -> callfixup " + fx[0]);
                attached++;
                found = true;
            }
            if (!found) {
                println("WARNING: symbol " + fx[1] + " not found in this program");
                missing++;
            }
        }
        println("Attached to " + attached + " helper function(s), " + missing + " name(s) not found.");
    }
}
