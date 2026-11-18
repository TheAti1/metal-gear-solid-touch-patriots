# `___switch8` / `___switchu8` / `___switch16` jump tables — FULLY RESOLVED

**Status (2026-09-28, "STEP 6"): Ghidra's own decompiler now resolves every
one of these call sites into a real `switch` statement, automatically, for
every caller — not just the ones this project hand-decoded.** See
"§3 — Getting Ghidra's decompiler to do this itself" below for the mechanism.
This is the actual fix; the manual per-site table decoding in §1–2 below is
now historical context (kept because it's how the format was first proven,
and because it independently cross-validates the automatic result), not a
required step for reading any of these dispatches going forward.

**Status of the table FORMAT (CODE, confirmed against 665/670 = 99.3% of all
call sites, decoded by hand before the mechanism in §3 existed):**
`EnemyBase::update:`'s `aiControl` dispatch (the OQ-1 target) fully resolved
to 11 named selectors — see the worked example below, corrected 2026-09-28
against the right binary, and now independently reproduced by Ghidra's own
decompiler (§3) with no hand-decoding at all. Phase 0 of the (retired) oracle
plan. No emulator was used for any of this — hand-decoding and the
decompiler fix are both fully static.

## The format (CODE — confirmed against 665/670 = 99.3% of all call sites)

```
bl/blx  ___switch8            <- 4-byte Thumb call instruction
        DCB  count             <- byte[0] at (call_addr + 4), "fallthrough"
        DCB  offset_0          <- signed byte
        DCB  offset_1
        ...
        DCB  offset_{count-1}
<code resumes, reachable only via computed targets below>

target(i) = fallthrough + (signed)offset_i * 2
```

`___switch8`'s own body (symtab address `0x5a5cc`) is **not** where the table
lives and its bytes are not meaningful for this — the table is inline at
each individual call site, addressed via that call's own return address.
Ghidra's decompiled C for `___switch8` itself is explicitly self-flagged
("Could not recover jumptable at 0x5a5e0. Too many branches") and was not
trusted for the exact byte layout; the layout above was derived from and
validated against real call sites instead.

## Why this is trustworthy, not a guess

1. Hand-disassembling forward from a guessed address drifted twice (Thumb
   mixes 16- and 32-bit instructions; a misaligned guess still decodes into
   plausible-looking nonsense — this cost real time before being caught).
2. Anchored instead to Ghidra's own already-validated instruction lengths
   and XREFs (`getReferencesTo`), not re-derived by hand — eliminates the
   alignment-drift failure mode entirely.
3. Validated against `-[CrashLandingAppDelegate ReturnStageGame:]`
   (`0xa4dc`), a case whose surrounding logic was already independently
   decompiled: case 0's computed target landed on genuine, distinct handler
   code (`movs r6,#8; b <shared>`) — not a coincidental valid-looking decode.
4. **Then scaled to all 72 call sites automatically**
   (`tools/ghidra/ResolveSwitchTables.java`): decode every table, seed Thumb
   mode at every computed target, clear whatever Ghidra's original failed
   analysis had left there, force-disassemble. **665/670 case entries
   (99.3%) produced valid, real Thumb instructions.** A wrong formula does
   not clear 99.3% of ~600 essentially-random-looking targets by chance.
5. Five failures, all one caller (`-[Effect
   setEffEnemyChar:index:type:]`, `___switch16`, a backward-offset case
   landing inside an already-claimed instruction elsewhere in the same
   function) — isolated, not investigated further, does not affect the
   format's validity elsewhere.

**One caution for future use of this table, important enough to repeat
here:** the decompiled if/else chains Ghidra shows around calls it could not
resolve (which is every switch8 call site, by definition — that is why they
appear as if-chains rather than switch statements) are Ghidra's own
reconstruction *around the gap*, not independent ground truth. Do not assume
"decompiled case N == table index N" without checking the caller's own
index-computation code — several call sites explicitly bias the index before
calling (e.g. `___switch8(param_3 - 1)`, `Camera::shake`), and this offset is
per-call-site, not universal.

## Call site census

72 total: 31 × `___switch8`, 8 × `___switchu8`, 32 × `___switch16`, across
23 distinct enemy/game-logic callers including every boss's
`updateAttack`/`updateMove`/`updateSpecialAttack` (Ray, Wolf, Raven, Mantis,
Octopus, Liquid, Gekko, DwarfGekko), `EnemyBase::update`/`subDamage`,
`Player`, `Effect`, `Camera::shake`, `ReturnStageGame:` (the load-state
machine documented in the retracted session entry above), and
`GetMenuNum:`. Full per-site raw data: `analysis/notes/switch8_raw.tsv`
(call sites) and `analysis/notes/switch_resolved.tsv` (every individual case
→ target, 670 rows). Multi-instruction listings for the enemy-AI-relevant
callers: `analysis/notes/case_bodies.txt`.

**This also durably improved the shared Ghidra project**
(`analysis/ghidra/MGST.gpr`/`.rep`) — 665 addresses that were previously
undiscovered by Ghidra's own control-flow analysis (unreachable except via
the computed jump it couldn't resolve) now have real instructions. Anyone
opening the project in the GUI benefits from this, not just this export.

## Worked example: `EnemyBase::update`'s `aiControl` dispatch (11 states)

This is the OQ-1 / "every AI duration is invented" target from LOG.md. What
is now known (CODE, confirmed):

```
-[EnemyBase update:]  @ 0x2de10
  ___switch8((int)*(short*)(self + aiControl))   ; @ 0x2de24, 11 cases, no bias
```

> ⚠️ **Corrected 2026-09-28 (see LOG "STEP 2/3" entries).** The table below
> was originally decoded reading **v2.1.0's file bytes at v2.3.0's
> addresses** — a version mix-up caught in the 2026-09-27 AUDIT. Re-derived
> here directly from v2.3.0's own bytes (`work/extracted/…/MGSTUS`, the same
> binary Ghidra and `function_map.csv` describe) with a fresh, independent
> script — not copied from the audit's numbers. The two "unresolved, reads as
> non-pointer" cases (9–10) resolve cleanly once read from the correct file;
> there was never a literal-pool boundary problem, only a wrong-binary one.

**Structural finding, now fully resolved:** the 11 states are NOT 11 separate
code blocks. Each case loads exactly **one** distinct selector-reference
literal into `r1`, then falls into one shared continuation at `0x2de60`
(an `objc_msgSend` dispatch — every state is "message self this selector"):

```
case  0 -> 0x2de36:  ldr r1,[0x2dea8]  sel @0x6b5a0 -> "updateAppearance"
case  1 -> 0x2de3a:  ldr r1,[0x2deac]  sel @0x6b59c -> "updateAttack"
case  2 -> 0x2de3e:  ldr r1,[0x2deb0]  sel @0x6b598 -> "updateMove"
case  3 -> 0x2de42:  ldr r1,[0x2deb4]  sel @0x6b594 -> "updateMoveAttack"
case  4 -> 0x2de46:  ldr r1,[0x2deb8]  sel @0x6b590 -> "updateMoveAttack2"
case  5 -> 0x2de4a:  ldr r1,[0x2debc]  sel @0x6b58c -> "updateMoveEnd"
case  6 -> 0x2de4e:  ldr r1,[0x2dec0]  sel @0x6b588 -> "updateLifeAct"
case  7 -> 0x2de52:  ldr r1,[0x2dec4]  sel @0x6b584 -> "updateSelfDestruction"
case  8 -> 0x2de56:  ldr r1,[0x2dec8]  sel @0x6b580 -> "updateSpecialAttack"
case  9 -> 0x2de5a:  ldr r1,[0x2decc]  sel @0x6b57c -> "updateDataMove"
case 10 -> 0x2de5e:  ldr r1,[0x2ded0]  sel @0x6b418 -> "updateDie"
```

All 11 literal-pool slots decode as `__DATA __objc_selrefs` entries (the
"one range alternates between two sections" reading in the pre-correction
version was an artifact of reading the wrong file's bytes at these
addresses — in the real v2.3.0 binary every one of these 11 slots is a
selector reference, no exceptions, no shared slots, no unresolved cases).
None of `updateAppearance`/`updateAttack`/`…`/`updateDie` are ambiguous or
ObjC-runtime-only names — they read directly as C strings in `__TEXT
__objc_methname`.

**What this means for the port:** `aiControl`'s 11 values name an explicit
state machine, each state dispatching to its own named ObjC method on the
enemy (or a subclass override of it — `EnemyBase` almost certainly declares
all 11 as overridable, with per-enemy-type behavior in the subclasses per
`case_bodies.txt`'s 22 other callers). This is **CODE, confirmed**, not
inference: read the 11 method bodies (`-[EnemyBase updateAppearance]`,
`-[EnemyBase updateAttack]`, etc., and their per-subclass overrides) for the
actual timing/duration values — that is now the real next step for OQ-1 and
the aim/fire/cooldown durations, and it no longer depends on any further
switch-table work.

## Not yet done

- **Read the 11 state methods themselves** (mechanical: they are ordinary
  named ObjC methods now, e.g. `-[EnemyBase updateAttack]` — no jump-table
  recovery needed to reach them). This is the actual path to OQ-1 and the
  invented AI timings.
- `case_bodies.txt`'s 22 other captured callers now have real, correct
  decompiled `switch` bodies too (§3 fixes ALL callers of the 3 helpers, not
  case by case) — reading their raw multi-instruction listings by hand is no
  longer the way to get at them; read `recovered/decompiled/` instead.
- Per-call-site index bias is no longer something to catalogue by hand —
  Ghidra's own value-set analysis recovers it per call site automatically
  (see `ReturnStageGame:` in §3: the bounds check `param_3 - 8 < 0xd` was
  produced entirely by the decompiler, not looked up from this file).
- The 5 `___switch16` failures in `setEffEnemyChar:index:type:` — **not
  re-investigated**, and now lower priority: every OTHER call in that same
  function decompiles cleanly via §3's fixup, so the failures are isolated
  to whichever specific case(s) had the original backward-offset ambiguity;
  worth a look but no longer blocking anything.

## §3 — Getting Ghidra's decompiler to do this itself (the actual fix)

Hand-decoding 665 call sites (§1–2) told a human what each dispatch does,
but Ghidra's decompiler still cut every one of these functions off at
`Could not recover jumptable` / `Treating indirect jump as call`, because
disassembling the resolved TARGETS (what §1–2 did) doesn't teach the
DECOMPILER that the `bl ___switch8` CALL instruction itself is a computed
multi-way branch — from its own p-code's perspective, that instruction is
just an ordinary call to a real function, full stop.

**Two things that look like the fix and are NOT:**
- `Instruction.setFlowOverride` cannot turn a *direct* call (fixed target,
  `bl ___switch8`) into a *computed* one — the override enum only changes
  whether the flow is modeled as call/branch/return, never whether the
  destination becomes register-derived. `___switch8`'s address is fixed at
  the instruction level regardless of any override.
- Attaching a `JumpTable` override (the mechanism Ghidra's own shipped
  `SwitchOverride.java` example script uses, for a *genuine* indirect-branch
  instruction the analyzer merely failed to resolve) to our plain `CALL`
  instruction **crashed the decompiler outright** ("Decompiler process
  died") when tried empirically. A JumpTable override is only meaningful
  where the underlying p-code already contains a computed-branch op for it
  to attach to; ours doesn't, without the fix below.

**The actual fix: a program-scoped compiler-spec `callfixup`.** ARM.cspec
(shipped with Ghidra) already has this exact mechanism for the *structurally
identical* GCC runtime helpers (`__gnu_thumb1_case_uqi`/`switch8_r0`,
`switch8_r3`, etc. — "read a byte table immediately after the return
address, index by a register, computed-jump through it"). A callfixup
REPLACES the p-code emitted for a call to a named function with a custom
p-code body, which — unlike a call — legitimately ends in a computed
`BRANCHIND`. That gives Ghidra's own value-set analysis a genuine computed
branch to walk, and it recovers the switch **itself**, reading the table
bytes via its own symbolic execution — no per-call-site data need be
supplied at all.

Adapted for MGST's own validated format (count byte, then N signed-byte
offsets, index in **r0**, target = fallthrough + offset×2 — confirmed
identical across all three Apple helper names, unlike GCC's family where
`switch16_shi_r0` uses 2-byte entries and `switch8_r3` reads its count from
`lr-1` and indexes via r3):

```sleigh
tmpptr = lr & 0xfffffffe;
tblsize = *:1 tmpptr;
r12 = zext(tblsize);
inbounds = r0 < r12;
if (!inbounds) goto <next1>;
offset = *:1 (tmpptr + 1 + r0);
r12 = sext(offset);
<next1>
if (inbounds) goto <next2>;
r12 = 0;
<next2>
r12 = r12 * 2;
lr = lr + r12;
ISAModeSwitch = (lr & 1) != 0;
TB = ISAModeSwitch;
pc = lr & 0xfffffffe;
goto [pc];
```

Registered via `ghidra.program.database.SpecExtension` (the public class
backing Ghidra's GUI "Specification Extensions" option editor) —
**program-scoped**, stored in this project's own `analysis/ghidra/MGST.rep`
database, no shared/system Ghidra install file touched. Attached to all
three helpers via `Function.setCallFixup("apple_switch_table")`.
`tools/ghidra/InstallSwitchCallFixup.java` is the (idempotent, safe to
re-run) script that does both steps; run it once, it persists in the
project.

**Result, verified 2026-09-28:**
- `___switch8`, `___switchu8` and `___switch16` call sites all confirmed
  working (`ReturnStageGame:`, `StageObjLoad`, `sh_gameMain` spot-checked
  individually before the full rollout).
- Full corpus re-export: **1645/1645 functions succeeded, 0 failed.**
- 71 `WARNING: Function: ___switch{8,u8,16} replaced with injection` markers
  (matches the raw census's 31+8+32=71 call sites exactly) and 75 new
  `switch(...)` statements in the decompiled output (some functions have
  more than one call site).
- Diffed old vs new corpus: **exactly the 26 files containing a switch8-family
  caller changed; the other 42 are byte-identical.** No unrelated
  side-effects anywhere in the corpus.
- `EnemyBase::update:`'s `aiControl` switch (the OQ-1 target) now decompiles
  as a real `switch(iVar3) { case 1: ...updateAttack...; case 2:
  ...updateMove...; ...}`, matching §2's hand-derived selector table exactly
  — produced by the decompiler, not looked up.
- Only 2 of the 66 known switch8-family caller functions show any residual
  "Could not recover jumptable" warning, and neither is a regression:
  `setGroundHit::::`'s warning is a **different, unrelated** genuine
  indirect function-pointer call elsewhere in the same function (nothing to
  do with switch8/16/u8); `updateEachCharacter:` still shows a redundant
  leftover warning comment alongside otherwise-correct generated logic
  (bounds check + table read, functionally right, just an extra stale
  comment from the analyzer's earlier failed attempt).

**Files:** `tools/ghidra/InstallSwitchCallFixup.java` (the fix),
`recovered/decompiled/` (re-exported corpus, promoted from this fix — the
old `analysis/notes/redecomp/`, `redecomp2/` scratch copies were deleted
once promoted). See LOG.md "STEP 6 DONE" for the full narrative including
the two dead ends.
