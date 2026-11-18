# Gameplay Reference & Port Verification Matrix

Reference for checking the Android port reproduces the original's behaviour,
and the test matrix to record results in.

Regenerate the data behind this file with:

```bash
python3 tools/extract_ground_truth.py     # -> analysis/verification/ground_truth.json
```

---

## Evidence policy

Every row below is tagged with where it came from and how much to trust it.

| Tag | Meaning |
|---|---|
| **DATA** | Read directly out of the shipped bundle. Authoritative. |
| **CODE** | Read out of the decompiled binary. Authoritative. |
| **INFER** | Consistent hypothesis from DATA/CODE, not yet confirmed. |
| **UNKNOWN** | Not established. Do not build on it. |

### On the external sources

Two were suggested: a Neoseeker walkthrough and a YouTube playthrough.
Neither was usable — the walkthrough host returns **HTTP 403** to automated
fetches, and video content can't be read.

That matters less than it sounds. Both are *secondary* sources, and this
project has the primary one: the game's own shipped tables and executable.
Where a walkthrough would say "stage 14 is Crying Wolf," the bundle says it
with `shstage14_*.data` and the string table. The reference below is built
from the bundle throughout.

They remain useful for one thing the data can't give cheaply — **observed
runtime feel** (enemy aggression, timing, difficulty curve). If you want that
captured, play the video and fill in the "Original (observed)" column; the
matrix is laid out for exactly that.

---

## Structure — **DATA**

20 stages, 5 areas × 4 stages. Titles from `English.lproj/Localizable.strings`
(binary plist, numeric keys; stage titles at index `385 + 8n`).

| # | Area | Location | Phases | Spawn entries |
|---:|---|---|---:|---:|
| 1 | MIDDLE EAST | RED ZONE | 1 | 7 |
| 2 | MIDDLE EAST | RED ZONE | 1 | 24 |
| 3 | MIDDLE EAST | DOWNTOWN | 1 | 24 |
| 4 | MIDDLE EAST | ADVENT PALACE | 1 | 22 |
| 5 | SOUTH AMERICA | CAVE VALLEY VILLAGE | 1 | 22 |
| 6 | SOUTH AMERICA | POWER STATION | 1 | 28 |
| 7 | SOUTH AMERICA | VISTA MANSION | 1 | 32 |
| **8** | SOUTH AMERICA | RESEARCH LAB | **4** | **111** |
| 9 | EASTERN EUROPE | MIDTOWN S SECTOR | 1 | 12 |
| 10 | EASTERN EUROPE | MIDTOWN NE SECTOR | 1 | 22 |
| 11 | EASTERN EUROPE | RIVERSIDE WEST | 1 | 28 |
| **12** | EASTERN EUROPE | ECHO'S BEACON | **3** | **35** |
| 13 | SHADOW MOSES | HELIPORT | 1 | 66 |
| **14** | SHADOW MOSES | SNOWFIELD | **4** | **140** |
| 15 | SHADOW MOSES | UNDERGROUND SUPPLY TUNNEL | 1 | 10 |
| **16** | SHADOW MOSES | PORT AREA | **6** | **54** |
| 17 | OUTER HAVEN | SHIP BOW | 1 | 24 |
| **18** | OUTER HAVEN | COMMAND CENTER | **4** | **136** |
| 19 | OUTER HAVEN | MISSILE HANGAR | 1 | 26 |
| 20 | OUTER HAVEN | SAIL | 1 | 9 |

## Enemy type ids — **CONFIRMED** (data × guide)

Solved by constraint propagation: intersect each stage's recovered type-id
list (line 1 of its `_ap` file) with the enemies the GameFAQs enemy guide
places in that mission, then propagate from the single-enemy stages.

| Type | Enemy | Stages |
|---:|---|---|
| 0, 1, 3 | PMC Soldier *(variants — cf. `PMC switchToPMC_A/B`)* | 1,2,3,5,6,7,9,10 |
| 2, 17 | Haven Trooper | 4,8,11,14,17,18 |
| 4 | Canard Attack Chopper | 3,10 |
| 5 | Gekko | 7,11,13,17 |
| 6 | Dwarf Gekko | 13,19 |
| 7 | Gekko — self-destruct variant *(cf. `SelfDestructionGekko`)* | 15 |
| 8, 15 | Laughing Octopus | 8 |
| 9 | Raging Raven | 12 |
| 10 | Crying Wolf | 14 |
| 11 | *(no guide coverage)* — Metal Gear RAY | 16 |
| 12 | Screaming Mantis | 18 |
| 13 | *(no guide coverage)* — Liquid Ocelot | 20 |

Every id resolved to a single name except 11 and 13, which appear only in
stages 16 and 20 and are absent from the guide's enemy list — consistent with
them being the RAY and Liquid encounters.

## Mission clear conditions — **CONFIRMED** (data × guide)

`shstage<NN>_<s>.data` row 0:

```
field[2] = mode      0 = kill count, 1 = survive timer
field[3] = target    kills required, or seconds to survive
```

Checked against the walkthrough's stated goal for every mission that names a
count: **13/13 match exactly.** Boss stages carry `field[3] = 1`. Stage 15
carries `field[2] = 1, field[3] = 90` — the "survive for 90 seconds"
objective, which is the only timed win condition in the game.

### Spawn tables cycle

Mission 1's goal is **12** PMC kills but its `_ap` table holds only **7**
spawn entries. Not a contradiction: `EnemyManager updateAppearData:` resets
`currentAppearIndex` to 0 when it passes `appearDataCount[ptn]`, so the spawn
list **loops**. Kill target and spawn-list length are independent.

## Boss stages — **CONFIRMED** (was INFER, now verified)

The four multi-phase stages flagged earlier as inference are confirmed by the
enemy guide's mission list: **8 = Laughing Octopus, 12 = Raging Raven,
14 = Crying Wolf, 18 = Screaming Mantis.** Stage 16 (RAY) and 20 (Liquid)
remain inference — the guide does not cover them — but their dedicated type
ids (11, 13) and objective strings are consistent.

### Original inference, retained for provenance

Stages 8, 12, 14, 16, 18 carry 3–6 phases where every other stage has one.
Two independent signals agree that these are the multi-phase boss encounters:

1. **DATA** — phase count and spawn volume are 3–20× the surrounding stages.
2. **DATA** — the `EnemyBase` subclasses recovered from the binary include
   exactly the expected boss set (`Octopus`, `Raven`, `Wolf`, `Mantis`, `Ray`,
   `Liquid`), and the string table carries a matching "DEFEAT ..." objective
   for each.

The specific boss↔stage assignment below is **INFER, not confirmed**:

| Stage | Location | Likely boss | Why |
|---:|---|---|---|
| 8 | RESEARCH LAB (S. America) | Laughing Octopus | 4 phases; area matches |
| 12 | ECHO'S BEACON (E. Europe) | Raging Raven | 3 phases; area matches |
| 14 | SNOWFIELD (Shadow Moses) | Crying Wolf | 4 phases; area matches |
| 16 | PORT AREA (Shadow Moses) | Metal Gear RAY | 6 phases — most in game |
| 18 | COMMAND CENTER (Outer Haven) | Screaming Mantis | 4 phases; area matches |
| 20 | SAIL (Outer Haven) | Liquid Ocelot | final stage; only 9 spawns, consistent with a scripted duel |

> **Do not treat this table as fact when implementing.** The objective strings
> are pre-rendered to textures rather than indexed at runtime, so the
> stage→objective mapping could not be traced from the draw code. Confirm from
> the per-stage enemy tables before relying on it.

## Objectives — **DATA** (set), **UNKNOWN** (mapping)

19 objective strings recovered. Distinct types:

- Defeat PMC soldiers
- Defeat Haven Troopers
- Defeat "Dwarf Gekko" unmanned scouts (×2 occurrences)
- Defeat "Gekko" bipedal unmanned war machines
- Fight off the Canard attack chopper
- Defeat Laughing Octopus / Raging Raven / Crying Wolf / Screaming Mantis
- Defeat Metal Gear RAY
- Defeat Liquid Ocelot
- **Survive for 90 seconds** ← the one timed objective; a distinct win
  condition the port must implement separately

19 strings vs 20 stages, so the block is **not** 1:1 in string-ID order.
Resolve from code before wiring objectives up.

## Spawn table format — **CONFIRMED** (structure) / **INFER** (columns)

`shstage<NN>_<phase>_ap.data`, plain ASCII CSV, and **sectioned — not flat**:

```
countPerSection,numSections        header
<marker>                           1-field section marker
kind,x1,y1,z1,x2,y2,z2,time,n      9-field spawn rows
x,y,?,time                         4-field parallel table (some stages)
```

**The number of 9-field rows equals `countPerSection * numSections`.**
Verified across **all 36 `_ap` files**. Reading the file flat overcounts
badly — stage 1 yields 18 rows for 7 real spawns, because section markers and
the parallel table get counted as spawns. The 4-field rows pair to spawns by
their last column, which matches the spawn's `time`.

### The real format — **CONFIRMED from the parser**

The loader lives in `MGSTAppDelegate` @ ~`0x1a2xx` (builds
`shstage%02d_%d_ap`, splits on newline then comma). Decoded:

```
line 0:  entriesPerType , numEnemyTypes
line 1:  <enemy type id> [, <id> ...]        one id per enemy type
line 2+: numEnemyTypes blocks of entriesPerType rows, 9 fields each
```

Stored as `g_ApEnemyData[typeId][entry][field]` — stride `0x900` bytes per
type (so **64 entries max per type**), `0x24` per entry (9 x int32).

**Correction to an earlier entry in this file:** the second header field is
the number of **enemy types**, not a count of "sections"/patterns, and the
short row after the header is the **list of type ids** — not a section
marker. Worked examples:

| Stage | header | line 1 | 9-field rows |
|---|---|---|---|
| 01 | `7,1` | `0` | 1 type x 7 = 7 |
| 08 | `13,3` | 3 ids | 3 x 13 = 39 |
| 14 | `17,2` | `2,10` | 2 x 17 = 34 |
| 20 | `9,1` | 1 id | 1 x 9 = 9 |

Re-parsed with these semantics, **36/36 files match exactly**.

Separately, `EnemyManager updateAppearData:` @ `0x2adac` reduces the table at
runtime to `(time, enemyIndex)` short pairs in `appearData[ptn * 0x20 + i]`,
bounded by `appearDataCount[ptn]` — a *pattern* cap of 32, which is a
different axis from the 64-per-type storage limit above.

### Field meanings — **partly CODE-confirmed**

| Field | Byte off | Destination | Status |
|---:|---|---|---|
| 0 | `+0x00` | `pEneDat+0xb4` (`PMC switchToPMC_*`) | CODE |
| 1 | `+0x04` | `pEneDat+0x98`, int→float — **X** | CODE |
| 2 | `+0x08` | `pEneDat+0x9c`, int→float — **Y** | CODE |
| 3 | `+0x0c` | **no reader found** | see below |
| 4–6 | `+0x10`–`+0x18` | partial reads seen | UNKNOWN |
| 7 | `+0x1c` | **time** (drives `appearData` sort) | CODE |
| 8 | `+0x20` | read by `NPC` | CODE |

### What `z` (field 3) is — **UNRESOLVED, likely unused**

No code anywhere in the 1645 decompiled functions reads field 3 (`+0x0c`),
while fields 0, 1, 2, 7 and 8 all have identifiable consumers. Four
hypotheses tested and rejected:

1. **Screen depth.** Stage 1 alone gave `corr(y,z) = -0.589`, which looked
   convincing. Over all 832 rows it is **+0.008** — the stage-1 figure was
   noise from n=7.
2. **Sprite scale.** Range 0–910 with 38% exactly zero; no scale reading fits.
3. **Enemy asset id** (`sh_enemy<NNN>_*.png`). Only 13 of 107 distinct values
   match a real asset — 12%.
4. **Per-enemy-type constant.** `0/17` types have a single `z` value.

Leading hypothesis: **vestigial / authoring-tool data that the shipped engine
never reads.** Supporting it: no consumer found, 38% of values are exactly 0,
and no functional interpretation fits. Against it: the non-zero values are
clearly structured (`A*100 + B` with `B` from a small repeating set like
12/22/32/42/52), which is not what dead data usually looks like — so a
consumer may exist along a path the decompiler mangled.

**Do not guess at this when implementing.** Field 3 can be carried through
and ignored; nothing observed depends on it.

### Other column statistics

Over **all 832 spawn rows in the game**:

| Fact | Value |
|---|---|
| `z1 == z2` | 819/832 (98.4%) — `z` is a per-spawn constant, not a path component |
| `y1 == y2` | 650/832 (78.1%) — most spawns move horizontally only |
| `kind` values | 0 (616), 1 (163), 3 (29), 2 (24) |
| `z` range | 0–910; 320 rows are exactly 0 |

Hypotheses tested and **rejected** — recorded so they are not retried:

1. **`z` is screen depth.** Stage 1 alone showed `corr(y,z) = -0.589`, which
   looked promising. Across all 832 rows it is **+0.008**. The stage-1 figure
   was noise from n=7.
2. **`z` is a sprite scale.** Values run 0–910 with 38% exactly zero; no
   plausible scale reading fits.
3. **`z` is an enemy asset ID** (`sh_enemy<NNN>_*.png`). Only 13 of 107
   distinct `z` values correspond to a real asset ID — 12%.

`z`, `kind` and the trailing `n` stay **UNKNOWN**. The runtime struct keeps
only `(time, enemyIndex)`, so the remaining columns are consumed during load
— resolve from `sh_load_enemy:` / `sh_load_enemy_setting`, not by fitting
curves to the data.

### What the plot does show

Plotting stage 1's 7 spawns over the real background and over the shootmap
(`screenshots/03`, `05`):

- markers land along the street and building line, not scattered at random
- all 7 sit in the upper ~40% of frame, leaving the near-camera foreground
  empty — consistent with the enemy plane of an on-rails shooter
- one spawn starts at exactly `x=512`, the shootmap width, moving left:
  consistent with entering from off-screen right, and evidence that spawn X
  shares the shootmap's 512-wide coordinate space
- spawns fall in mixed shootmap zones, so the zones are **not** a simple
  spawnable/blocked mask

## Resource formats — **CODE** (confirmed)

Transcribed from the decompiled loaders, then validated by parsing all 204
files with **exact byte consumption** (`tools/parse_alrl.py`):

```
.al  DWUtilities readAnimeData:: @0x22f5c    .rl  readRectData:: @0x23190
  int16 frameCount, unk                        int16 groupCount, unk
  frameCount x:                                groupCount x:
    int16 partCount, unk                         int16 itemCount
    partCount x: int16[6] (stride 0x0c)          itemCount x: int16[7] (stride 0x0e)

  part = [rectIndex, ?, offsetX, offsetY, ?, ?]  item = [textureId, x, y, w, h, ?, ?]
```

Playback is frame → part → rect → atlas sub-image at the part's signed offset.

---

## Port verification matrix

Fill **Original (observed)** from the video/walkthrough or a real device;
fill **Port** from the Android build. Status: `PASS` / `PARTIAL` / `FAIL` /
`UNKNOWN`. No subjective ratings.

### Subsystems

| Feature | Original (observed) | Port | Status |
|---|---|---|---|
| App launches | — | boots, GL ES 2 context | PARTIAL |
| Renders a recovered texture | — | yes (harness) | PASS |
| Touch input routed | — | yes, mapped to 480×320 | PARTIAL |
| `.al`/`.rl` parsed on device | — | yes, 204/204 desktop | PARTIAL |
| Stage `.data` loaded | — | not implemented | FAIL |
| Player movement | — | not implemented | FAIL |
| Aiming | — | not implemented | FAIL |
| Shooting | — | not implemented | FAIL |
| Enemy spawn | — | not implemented | FAIL |
| Enemy AI | — | not implemented | FAIL |
| Hit detection | — | not implemented | FAIL |
| Mission complete | — | not implemented | FAIL |
| Stage transition | — | not implemented | FAIL |
| Scoring (`GResult`) | — | not implemented | FAIL |
| Save/load (`GSaveCtrl`) | — | not implemented | FAIL |
| Audio | — | not implemented | FAIL |
| Menus / Drebin shop | — | not implemented | FAIL |

### Per-stage (M2 gate)

| # | Location | Bg correct | Spawns match | Objective | Clears | Status |
|---:|---|---|---|---|---|---|
| 1 | RED ZONE | | | | | UNKNOWN |
| 2 | RED ZONE | | | | | UNKNOWN |
| 3 | DOWNTOWN | | | | | UNKNOWN |
| 4 | ADVENT PALACE | | | | | UNKNOWN |
| 5 | CAVE VALLEY VILLAGE | | | | | UNKNOWN |
| 6 | POWER STATION | | | | | UNKNOWN |
| 7 | VISTA MANSION | | | | | UNKNOWN |
| 8 | RESEARCH LAB *(boss, 4ph)* | | | | | UNKNOWN |
| 9 | MIDTOWN S SECTOR | | | | | UNKNOWN |
| 10 | MIDTOWN NE SECTOR | | | | | UNKNOWN |
| 11 | RIVERSIDE WEST | | | | | UNKNOWN |
| 12 | ECHO'S BEACON *(boss, 3ph)* | | | | | UNKNOWN |
| 13 | HELIPORT | | | | | UNKNOWN |
| 14 | SNOWFIELD *(boss, 4ph)* | | | | | UNKNOWN |
| 15 | UNDERGROUND SUPPLY TUNNEL | | | | | UNKNOWN |
| 16 | PORT AREA *(boss, 6ph)* | | | | | UNKNOWN |
| 17 | SHIP BOW | | | | | UNKNOWN |
| 18 | COMMAND CENTER *(boss, 4ph)* | | | | | UNKNOWN |
| 19 | MISSILE HANGAR | | | | | UNKNOWN |
| 20 | SAIL *(final)* | | | | | UNKNOWN |

### Highest-value early checks

Cheap to run, and each would catch a whole class of error:

1. **Stage 1 spawn count is 7** — lowest in the game. If the port's stage 1
   spawns anything else, the `_ap` parser or its indexing is wrong.
2. **Stage 14 has 140 spawn entries across 4 phases** — the busiest. Good
   stress test for the spawn scheduler.
3. **Stage 16 has 6 phases** — more than any other. Exercises phase
   transition hardest.
4. **Stage 20 has only 9 spawns** — if the final boss looks like a normal
   stage, phase/scripting handling is wrong.
5. **The "survive 90 seconds" objective** — the only timed win condition.
   Easy to miss entirely when implementing objectives as kill-counts.

---

*Ground truth: `analysis/verification/ground_truth.json`.
Regenerate: `python3 tools/extract_ground_truth.py`.*
