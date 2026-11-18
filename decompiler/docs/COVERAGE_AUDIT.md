# Decompilation coverage audit: is every byte of code decompiled?

**Date:** 2026-10-09 · **Tool:** `tools/ghidra/CoverageAudit.java` (read-only, about 5 min) ·
**Result: yes.** Every instruction in `__text` is either taken into a decompiled function by the
decompiler, or is data that Ghidra's disassembler had decoded as instructions.

## 1. The function set is complete

| check | result |
|---|---|
| functions with an entry in `__text` | 1,395 |
| exported with C (`recovered/compile/functions.jsonl`) | 1,395, the same set (`analysis/symbols/function_entries.txt`) |
| STABS `N_FUN` records (the compiler's own list of functions) | 1,388, **all** exported |
| exported but not in STABS | 7: crt0 `entry` 0x25bc, `dyld_stub_binding_helper` 0x2608, `___switchu8/8/16`, the VFP save/restore helpers 0x5a604/0x5a60c (compiler and linker glue) |
| `__symbol_stub4` (182 import stubs) | dyld trampolines into system libraries; not application code |

## 2. Every instruction is decompiled

Ghidra's stored function bodies cover only 75.8 % of `__text`, because they omit switch-case
code reached through the `___switch*` call-fixups. That is not the measure that matters. The
audit decompiles every function in **`firstpass`** mode (p-code straight after flow following,
before any simplification merges or removes blocks) and collects the instruction behind every
p-code op.

| `__text` instructions (as disassembled by Ghidra) | 131,539 |
|---|---:|
| **taken into a decompiled function** | **130,359 (99.10 %)** |
| not taken: **literal pools** decoded as Thumb code (an `ldr [pc]` reads that word as data) | 594 |
| not taken: **inline switch tables**; each of the 70 runs starts right after a `bl ___switch8/u8/16`, which reads its table from the return address | 579 |
| not taken: alignment NOPs (`mov r8,r8`) | 7 |
| **unexplained** | **0** |

`DrawGame` (0x1e568) fails only in `firstpass` mode (a Ghidra "Decoding error"); its normal-pass
basic blocks are used instead. Its normal decompilation and export are complete, and it passes
its differential tests.

Data: the audit writes every instruction not taken, with its classification, to `<outdir>/decompiled_uncovered.tsv` (generated locally; not published, as it lists disassembly of the binary).

## 3. Data in `__text`

50,376 bytes of `__text` are data: literal pools (32-bit constants that Thumb code loads with
`ldr rX,[pc,#]`) and the inline switch tables. The decompiled C carries their values: pool
constants become literals or address references in the C, and switch tables are resolved into C
`switch` cases (V1 audit A3 checks all 76 tables). They need no code of their own.

## Reproduce

```
analyzeHeadless analysis/ghidra MGST -process MGSTUS -noanalysis -readOnly \
    -scriptPath tools/ghidra -postScript CoverageAudit.java <outdir>
```
