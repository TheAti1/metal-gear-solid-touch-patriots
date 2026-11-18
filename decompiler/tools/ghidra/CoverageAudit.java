/* Decompilation coverage audit (LOG 2026-10-09): does the function set cover
 * ALL code in the binary?
 *
 *  1. __text bytes: union of every function body vs the section range; each
 *     uncovered run is classified from the listing (instructions outside any
 *     function = MISSING CODE; defined data / undefined bytes / zero padding).
 *  2. Instructions anywhere in executable memory that belong to no function.
 *  3. Every function entry in __text, with its body size, for cross-checks
 *     against analysis/symbols/function_entries.txt and the STABS list.
 *  4. DECOMPILED coverage (the one that matters): every function is
 *     decompiled with the project's settings and the address of every p-code
 *     op it produced is collected. Ghidra's stored bodies do not include
 *     switch-table targets reached through the ___switch* call-fixups, but
 *     the decompiler follows them. Every __text instruction no decompiled
 *     function consumed is listed (decompiled_uncovered.tsv) with its kind:
 *     Thumb alignment NOP (mov r8,r8), a block the decompiler removed as
 *     unreachable, or OTHER (needs review).
 *
 * Args: output directory. Writes coverage_gaps.tsv, coverage_functions.tsv and
 * prints a summary. Read-only.
 */
import java.io.*;
import java.util.*;

import ghidra.app.decompiler.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.pcode.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;

public class CoverageAudit extends GhidraScript {
    @Override
    protected void run() throws Exception {
        File out = new File(getScriptArgs()[0]);
        out.mkdirs();
        MemoryBlock text = null;
        for (MemoryBlock b : currentProgram.getMemory().getBlocks())
            if (b.getName().equals("__text")) text = b;
        if (text == null) { println("no __text block"); return; }
        AddressSet textSet = new AddressSet(text.getStart(), text.getEnd());
        AddressSet covered = new AddressSet();
        Listing L = currentProgram.getListing();
        int nf = 0;
        try (PrintWriter w = new PrintWriter(new FileWriter(new File(out, "coverage_functions.tsv")))) {
            w.println("entry\tname\tbody_bytes\tranges\tthunk");
            for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
                AddressSetView body = f.getBody();
                if (!textSet.contains(f.getEntryPoint())) continue;
                nf++;
                covered.add(body);
                w.println(f.getEntryPoint() + "\t" + f.getName(true) + "\t" + body.getNumAddresses() + "\t"
                        + body.getNumAddressRanges() + "\t" + f.isThunk());
            }
        }
        AddressSet gaps = textSet.subtract(covered);
        long textBytes = textSet.getNumAddresses(), cov = covered.intersect(textSet).getNumAddresses();
        Map<String, Long> kinds = new TreeMap<>();
        int missingRuns = 0;
        try (PrintWriter w = new PrintWriter(new FileWriter(new File(out, "coverage_gaps.tsv")))) {
            w.println("start\tend\tbytes\tkind\tdetail");
            for (AddressRange r : gaps) {
                // classify the run
                int insns = 0, dataBytes = 0, zero = 0, undef = 0;
                String detail = "";
                Address a = r.getMinAddress();
                while (a != null && a.compareTo(r.getMaxAddress()) <= 0) {
                    CodeUnit cu = L.getCodeUnitAt(a);
                    int len = 1;
                    if (cu instanceof Instruction) {
                        insns++;
                        len = cu.getLength();
                        if (detail.isEmpty()) detail = cu.toString();
                    } else if (cu instanceof Data && ((Data) cu).isDefined()) {
                        dataBytes += cu.getLength();
                        len = cu.getLength();
                        if (detail.isEmpty()) detail = ((Data) cu).getDataType().getName();
                    } else {
                        byte v = getByte(a);
                        if (v == 0) zero++; else undef++;
                    }
                    a = a.add(Math.max(1, len));
                }
                String kind = insns > 0 ? "CODE-OUTSIDE-FUNCTION" : dataBytes > 0 ? "data"
                        : undef == 0 ? "zero-padding" : "undefined-nonzero";
                if (insns > 0) missingRuns++;
                kinds.merge(kind, r.getLength(), Long::sum);
                w.println(r.getMinAddress() + "\t" + r.getMaxAddress() + "\t" + r.getLength() + "\t" + kind + "\t"
                        + detail.replace("\t", " ") + (undef > 0 ? " nonzero=" + undef : ""));
            }
        }
        // instructions outside functions anywhere executable
        int orphan = 0;
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            if (!b.isExecute()) continue;
            InstructionIterator it = L.getInstructions(new AddressSet(b.getStart(), b.getEnd()), true);
            while (it.hasNext()) {
                Instruction i = it.next();
                if (getFunctionContaining(i.getAddress()) == null) orphan++;
            }
        }
        // ---- 4. decompiled coverage
        // "firstpass": p-code straight after flow following and heritage, before
        // any simplification removes or merges ops/blocks - the address of each
        // op is an instruction the decompiler took into the function
        DecompInterface d = new DecompInterface();
        d.setOptions(new DecompileOptions());
        d.setSimplificationStyle("firstpass");
        d.openProgram(currentProgram);
        // the normal pass, only for its "removed unreachable block" warnings
        DecompInterface dn = new DecompInterface();
        dn.setOptions(new DecompileOptions());
        dn.openProgram(currentProgram);
        Set<Address> used = new HashSet<>();
        PrintWriter fnInsns = new PrintWriter(new FileWriter(new File(out, "function_insns.tsv")));
        fnInsns.println("function\tinstruction");
        Map<Address, String> removed = new HashMap<>();
        int fails = 0;
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            if (!textSet.contains(f.getEntryPoint()) || monitor.isCancelled()) continue;
            DecompileResults r = d.decompileFunction(f, 120, monitor);
            HighFunction hf = r.getHighFunction();
            DecompileResults rn = dn.decompileFunction(f, 120, monitor);
            if (hf == null) {
                // firstpass can fail where the normal pass works (DrawGame:
                // "Decoding error"): fall back to the normal pass's ops and
                // its basic blocks' instruction ranges
                fails++;
                println("firstpass failed, normal-pass fallback: " + f.getName(true) + " " + r.getErrorMessage());
                hf = rn.getHighFunction();
                if (hf == null) { println("decompile FAILED: " + f.getName(true)); continue; }
                for (PcodeBlockBasic b : hf.getBasicBlocks()) {
                    Address bs = b.getStart(), be = b.getStop();
                    if (bs == null || be == null || !bs.isMemoryAddress()) continue;
                    InstructionIterator bi = L.getInstructions(new AddressSet(bs, be), true);
                    while (bi.hasNext()) used.add(bi.next().getAddress());
                }
            }
            Iterator<PcodeOpAST> ops = hf.getPcodeOps();
            Set<Address> mine = new TreeSet<>();
            while (ops.hasNext()) { Address oa = ops.next().getSeqnum().getTarget(); used.add(oa); mine.add(oa); }
            // per-function instruction list (test-coverage denominator,
            // tools/mgst_testcov.py): instructions of THIS function's flow
            if (hf == rn.getHighFunction()) {
                for (PcodeBlockBasic b : hf.getBasicBlocks()) {
                    Address bs = b.getStart(), be = b.getStop();
                    if (bs == null || be == null || !bs.isMemoryAddress()) continue;
                    InstructionIterator bi = L.getInstructions(new AddressSet(bs, be), true);
                    while (bi.hasNext()) mine.add(bi.next().getAddress());
                }
            }
            for (Address ia : mine)
                if (textSet.contains(ia) && L.getInstructionAt(ia) != null) fnInsns.println(f.getEntryPoint() + "\t" + ia);
            // blocks the decompiler dropped: from the normal pass's warnings
            String c = rn.getDecompiledFunction() != null ? rn.getDecompiledFunction().getC() : "";
            java.util.regex.Matcher m = java.util.regex.Pattern
                    .compile("Removing unreachable block \\(ram,0x([0-9a-f]+)\\)").matcher(c);
            while (m.find()) removed.put(toAddr(Long.parseLong(m.group(1), 16)), f.getName(true));
        }
        // literal pool extents: from each data-referenced word in __text, the
        // pool continues over consecutive unconsumed words
        fnInsns.close();
        AddressSet poolRun = new AddressSet();
        ghidra.program.model.symbol.ReferenceManager rm = currentProgram.getReferenceManager();
        for (Address src : rm.getReferenceDestinationIterator(textSet, true)) {
            boolean isData = false;
            for (ghidra.program.model.symbol.Reference ref : getReferencesTo(src))
                if (ref.getReferenceType().isRead() || ref.getReferenceType().isData()) isData = true;
            if (!isData || used.contains(src)) continue;
            Address a2 = src;
            while (textSet.contains(a2) && !used.contains(a2) && poolRun.getNumAddresses() < 10_000_000) {
                poolRun.add(a2, a2.add(3));
                a2 = a2.add(4);
            }
        }
        // inline switch tables: a bl to ___switchu8/8/16 reads its table from
        // the return address; the table occupies the words after the call
        AddressSet switchRun = new AddressSet();
        for (long helper : new long[]{0x5a5b4L, 0x5a5ccL, 0x5a5e4L}) {
            for (ghidra.program.model.symbol.Reference ref : getReferencesTo(toAddr(helper))) {
                if (!ref.getReferenceType().isCall()) continue;
                Instruction call = getInstructionAt(ref.getFromAddress());
                if (call == null) continue;
                Address a2 = call.getAddress().add(call.getLength());
                while (textSet.contains(a2) && !used.contains(a2) && switchRun.getNumAddresses() < 10_000_000) {
                    switchRun.add(a2, a2.add(1));
                    a2 = a2.add(2);
                }
            }
        }
        int insnTotal = 0, insnUsed = 0;
        Map<String, Integer> ukinds = new TreeMap<>();
        try (PrintWriter w = new PrintWriter(new FileWriter(new File(out, "decompiled_uncovered.tsv")))) {
            w.println("addr	instruction	kind	containing_or_previous_function");
            InstructionIterator it = L.getInstructions(textSet, true);
            while (it.hasNext()) {
                Instruction i = it.next();
                insnTotal++;
                if (used.contains(i.getAddress())) { insnUsed++; continue; }
                String txt = i.toString();
                String kind;
                if (switchRun.contains(i.getAddress())) kind = "inline-switch-table";
                else if (txt.equals("mov r8,r8") || txt.equals("nop")) kind = "alignment-nop";
                else {
                    // inside a removed-unreachable block? (block start <= addr, same function)
                    kind = "OTHER";
                    for (Map.Entry<Address, String> e : removed.entrySet()) {
                        Address bs = e.getKey();
                        if (bs.compareTo(i.getAddress()) <= 0 && i.getAddress().subtract(bs) < 64) { kind = "removed-unreachable"; break; }
                    }
                }
                if (kind.equals("OTHER")) {
                    // a literal pool disassembled as Thumb code: some instruction
                    // READS this address (or the word containing it) as data
                    Address wa = toAddr(i.getAddress().getOffset() & ~3L);
                    for (Address q : new Address[]{i.getAddress(), wa, wa.add(4 - 4)}) {
                        for (ghidra.program.model.symbol.Reference ref : getReferencesTo(q))
                            if (ref.getReferenceType().isRead() || ref.getReferenceType().isData()) kind = "literal-pool-as-code";
                    }
                    if (kind.equals("OTHER") && poolRun.contains(i.getAddress())) kind = "literal-pool-as-code";
                }
                ukinds.merge(kind, 1, Integer::sum);
                Function cf = getFunctionContaining(i.getAddress());
                if (cf == null) cf = getFunctionBefore(i.getAddress());
                w.println(i.getAddress() + "\t" + txt.replace("\t", " ") + "\t" + kind + "\t" + (cf == null ? "-" : cf.getName(true)));
            }
        }
        println(String.format("CoverageAudit DECOMPILED: %d/%d __text instructions consumed by the decompiler (%.3f %%); "
                + "not consumed: %s; decompile failures %d", insnUsed, insnTotal, 100.0 * insnUsed / insnTotal, ukinds, fails));
        println(String.format("CoverageAudit: functions in __text %d; __text %d bytes, in function bodies %d (%.3f %%); "
                + "gaps %s; code runs outside functions in __text: %d; instructions outside any function (all exec blocks): %d",
                nf, textBytes, cov, 100.0 * cov / textBytes, kinds, missingRuns, orphan));
    }
}
