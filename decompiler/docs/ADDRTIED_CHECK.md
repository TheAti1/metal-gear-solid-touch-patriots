# Address-tied stack variables: static check (gate review item)

**Question.** `RayMissile update` failed because the decompiler mishandled a stack buffer whose
address is passed to calls (an `objc_msgSend_stret` result). Does any other function have the
same defect? (LOG 2026-10-09)

**Tool.** `tools/ghidra/CheckAddrTiedMerge.java` (read-only, about 90 s for all 1,395 functions):

1. **No write effect.** A call is passed `&stackvar`, but the decompiler gives it no write effect
   (INDIRECT) on that variable, and the variable is read after the call. The decompiler then
   assumes the call left it unchanged, while the C passes `&var`, so the recompiled call writes it.
   This is the actual `RayMissile` defect.
2. **Merged versions.** A value defined at `d` is read at `u`, while another write `w` to the same
   storage lies in between, with `d` dominating `w` and `w` dominating `u`. In C there is only
   one variable, so the read would see `w`'s value. A call's own write effect at the read's
   instruction is excluded, because the call reads its inputs before writing.

Positive control: `RayMissile update` (before its fix) is flagged by check 1 at call 0x56aa8,
with reads at 0x56c2a, 0x56c32 and 0x56c70.

**Result (all 1,395 functions): 11 flagged reads in 4 functions**
(`addrtied_flags.tsv`), each reviewed against the disassembly:

| function | flag | binary | verdict |
|---|---|---|---|
| `RayMissile update` 0x5698c | check 1 at 0x56aa8 | the second stret result is never read; the first was saved to sp+0x2c/0x30 | real; **fixed** (`analysis/symbols/stret_dead.tsv`, recompile transform 1i); passes 54/54 frames |
| `HavenSoldierB getMovePoint` 0x52080 | check 2, `local_24` | `[sp,#0xc]` = -1 at 0x520ac, read at 0x5213a, written at 0x5214e: the latest value is always read | false positive (extra SSA versions from the 64-bit shift sequence); passes 150 states |
| `Canard getEnemyScale` 0x2e794 | check 2, `local_30` | running maximum in a loop; the C `if (local_30 < f) local_30 = f;` reads the latest value | false positive (loop back edge); passes 18 states |
| `Texture2D initWithImage:` 0x3ad4 | check 2, `local_6c` | old buffer `[sp,#0x24]` read in the loop and freed, then replaced by the new `[sp,#0x28]`; the C does the same in the same order | false positive (conservative effect on the `malloc` call); passes 7 states |

A first, looser version (address order, 64-byte window) also flagged
`EnemyBase checkCollisionWithBullet_Dmg:weaponType:damage:` 0x2dc3c. That was a false positive:
the buffer is written by `memcpy` and only passed by pointer, and the "read" was the incoming
stack parameter `damage`.

**Conclusion.** The defect class is closed: the only real instance is fixed, and every other flag
was reviewed and is a false positive. The 44 functions with two or more stret calls into one local
are covered by check 1, which inspects every call that receives a stack address.
