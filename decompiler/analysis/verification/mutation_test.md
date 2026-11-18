# Mutation test: does the differential harness catch wrong code?

**Date:** 2026-10-09 · **Tool:** `tools/mgst_mutation.py`

A proof is only as good as the checker. Proven functions were deliberately broken, one small
change at a time, in their recompiled C:
- `int`: an integer literal +1;
- `cmp`: a comparison flipped (`<` <-> `<=`, `==` <-> `!=`);
- `float`: a float literal changed in its last mantissa bit.

Each mutant was compiled, linked and tested exactly like the real function: synthetic calls and
the frame driver on 8 mission snapshots spread over the game. A mutant must FAIL (killed).
Afterwards the original files are restored and their fingerprints checked.

## Result (10 functions picked automatically, 22 mutants)

| | mutants |
|---|---:|
| killed (harness reported fail) | **15** |
| survived | 4 |
| untested (no captured state reaches the function's object) | 3 |

Every survivor was analysed:

| function | mutant | why it survived | verdict |
|---|---|---|---|
| `Player drawPlayer` 0x38d50 | `weaponMode - 4U < 4` -> `< 5` | switch table: 4 entries, then the default byte at index 4; `< 5` reads index 4 = the default byte. Identical behaviour | **equivalent mutant** (no test can kill it) |
| `Player drawPlayer` 0x38d50 | `<` -> `<=` (same comparison) | same reason | **equivalent mutant** |
| `GResult Result_Save_Survival_continue` 0x50f34 | `== 8` -> `== 9`; `200.0f` -> next float | inside `if (stage == 16 or 20) and [Player getMaxHP] == 8`; no captured state has max HP 8 on those stages, so the branch never runs | **branch not exercised** by the captured states |

**A harness weakness found by this test and fixed (harness 8).** In the first run the
Survival-branch mutants were tested with the stub-every-callee boundary, where `+[Stage getNum]`
returned 0, so no Survival branch could ever run. The callee boundary now stubs only the
specific callee that gets stuck; every other call runs for real (`mgst_difftest.py`,
`HARNESS = 8`). All functions previously proven through the old boundary were re-tested: 0
failures. Only 2 functions still rest solely on the old stub-everything proofs: `getFileSize`
0x29a5c and `Canard updateAttackProcess` 0x2eb5c.

## What this means for "proven"

A proof is **identical behaviour on every path the captured states exercise**. Code on paths no
captured state reaches (here a Survival max-HP special case) is decompiled and compiles, but is
not checked by a test. Equivalent mutants are expected and harmless. The next level of rigour is
measuring, per function, the share of its instructions that the tests executed (see the gate
sign-off, remaining work).

Data: `mutation_test.tsv` (the last run's rows).
