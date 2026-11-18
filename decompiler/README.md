# MGS Touch: a verified, function-by-function decompilation

This is a complete, verified decompilation of **METAL GEAR SOLID TOUCH v2.3.0** (iOS, 2009,
`MGSTUS`, 32-bit ARM) back into C: every one of its 1,395 functions. Each function is either
**proven to behave bit for bit like the original machine code**, or covered by a written
assembly-to-C audit.

This repository holds the **method and the tools**: everything needed to reproduce the
decompilation from your own copy of the game, check it, and build on it. It holds **no game
code and no game data**.

| | |
|---|---|
| functions in the binary | **1,395** (all 1,388 from the compiler's own STABS debug list, plus 7 compiler/linker glue) |
| decompiled, each compiling as standalone C | **1,395 (100 %)** |
| **proven bit-identical by differential testing** | **1,389 (99.6 %)** |
| covered by a written audit instead (cannot be tested: crt0 `entry`, `_main`, dyld glue, the 3 switch helpers) | 6 |
| **gate: every function proven or audited** | **PASSED (100 %)** |
| machine instructions taken into the decompilation | **100 %** of real code (99.10 % of `__text`; the rest is data: literal pools, switch tables, padding) |

Details: [`docs/GATE_SIGNOFF.md`](docs/GATE_SIGNOFF.md) ·
[`docs/COVERAGE_AUDIT.md`](docs/COVERAGE_AUDIT.md) · [`docs/STATUS.md`](docs/STATUS.md)

## Quick start

```bash
./reproduce.sh /path/to/your.ipa              # decompile: about 15 minutes, plus one-time installs
./reproduce.sh /path/to/your.ipa --verify     # also prove it against the emulated original: hours, unattended
```

You need your own copy of the **v2.3.0** IPA ([how to recognise it](#step-1-your-copy-of-the-game))
and a Linux machine (tested on Fedora 43). The script checks the IPA and installs what is
missing after asking: build tools via `dnf`, Python modules via `pip`, Ghidra 11.3.2 + JDK 21
into `/opt`. It then decompiles all 1,395 functions into `recovered/`, one C file per original
source file plus one compilable file per function, and runs the static audits. It ends with
the [status table](#5-reading-the-results). Every stage skips work that is already done, so
after an interruption run the same command again.

`--verify` also builds the emulator and captures the reference set of game states (about 7
hours). It then runs the differential tests and prints the gate. It downloads the emulator's
firmware, about 540 MB from the `qemu-ios` fork's releases
([step 6](#step-6-the-oracle-the-original-game-emulated)). It needs root once, to install the
app into the emulator's disk image.

The walkthrough in section 4 explains what each stage does, and how to run it by hand.

---

## Contents

- [Quick start](#quick-start)
1. [What is (and is not) in this repository](#1-what-is-and-is-not-in-this-repository)
2. [How it works, in one picture](#2-how-it-works-in-one-picture)
3. [Requirements](#3-requirements)
4. [Walkthrough](#4-walkthrough)
   - [Step 1: your copy of the game](#step-1-your-copy-of-the-game)
   - [Step 2: facts straight from the binary](#step-2-facts-straight-from-the-binary)
   - [Step 3: Ghidra with a patched decompiler](#step-3-ghidra-with-a-patched-decompiler)
   - [Step 4: build the Ghidra project](#step-4-build-the-ghidra-project)
   - [Step 5: export, recompile, static audits](#step-5-export-recompile-static-audits)
   - [Step 6: the oracle (the original game, emulated)](#step-6-the-oracle-the-original-game-emulated)
   - [Step 7: capture game states](#step-7-capture-game-states)
   - [Step 8: differential testing](#step-8-differential-testing)
   - [Step 9: the ledger and the gate](#step-9-the-ledger-and-the-gate)
   - [Step 10: checking the checker](#step-10-checking-the-checker)
5. [Reading the results](#5-reading-the-results)
6. [What we learned (pitfalls for anyone doing this)](#6-what-we-learned-pitfalls-for-anyone-doing-this)
7. [Repository layout](#7-repository-layout)
8. [Next: porting](#8-next-porting)
9. [Licence and legal](#9-licence-and-legal)

---

## 1. What is (and is not) in this repository

**Included (original work):**
- every tool of the pipeline: Mach-O/STABS parsers, 30+ Ghidra scripts, two decompiler patches,
  the exporter, the recompiler, the differential test harness, the emulator drivers, the ledger;
- **metadata** read from the binary: symbol tables, function map, Objective-C class, method and
  ivar tables, call-site facts. These are facts about the program, not its code;
- every **verification result**: per-function status, audits, sign-off;
- documentation: file formats, the platform API inventory, gameplay reference.

**Not included, and never redistributed:**
- the game (IPA, executable, art, audio, data tables): Konami's copyrighted work;
- the **decompiled C**, which is a machine translation of the copyrighted binary and therefore a
  derivative work. **You generate it yourself** from your own copy (step 5). It lands in
  `recovered/`, which is git-ignored;
- Apple firmware for the emulator (downloaded by the setup script from its upstream project);
- emulator snapshots (memory images of the running game).

This follows the model of established decompilation projects: **ship the tools; bring your own
copy.**

## 2. How it works, in one picture

```
 your IPA ──► Mach-O / STABS / ObjC metadata ──► Ghidra project ──────────────────┐
              (step 2: names, 1,388 functions,   (steps 3-4: patched decompiler,   │
               source files, Thumb/ARM mode)       22 typing / fixup scripts)      │
                                                                                   ▼
                                       decompiled C, one file per function  (step 5: export)
                                                                                   │
                                     recompile each function ALONE with clang,     │
                                     link it against the ORIGINAL binary  ◄────────┘
                                                                                   │
 original game in an emulator  ──► snapshots of real game states  ───────────────►│
 (step 6: QEMU iPod touch 2G,      (step 7: 20 missions, bosses, menus, taps)      │
  iOS 3.1.3)                                                                       ▼
                         differential test (step 8): from the SAME state, run the original
                         machine code and the recompiled function in an emulator (Unicorn);
                         compare returns, every byte written, every framework/GL call
                                                                                   │
                                                 ledger + gate (step 9) ◄──────────┘
```

The idea that makes "100 % exact" checkable: the recompiled function is linked **against the
original binary**. Every other function, every global and every constant stays the original's,
so a test isolates exactly one function's decompilation. It runs from real states captured in
the running game, under the device's exact floating-point mode, and its observable effects must
match **bit for bit**.

## 3. Requirements

Tested on Fedora 43 (x86-64). Any recent Linux should work.

| for | needs |
|---|---|
| everything | Python ≥ 3.11 with `unicorn` (2.1), `capstone` (5.0), `numpy`; `unzip` |
| steps 3-5 | Ghidra **11.3.2** + **JDK 21** (exactly 21: 11.3.2 rejects newer JDKs); `make`, `g++`, `bison`, `flex` (to rebuild the decompiler with our patches); `clang` (≥ 17) and `arm-none-eabi-gcc` (for `libgcc`) |
| steps 6-7 | the QEMU iOS fork's build dependencies (`oracle/scripts/setup_oracle.sh` installs them), `gdb` with ARM support, root once (offline app injection into the NAND image); about 540 MB of downloads |
| optional | `ffmpeg` (lossless audio conversion for a port) |

Disk: about 2 GB for the project, plus about 25 GB if you capture the full snapshot set.
CPU: a 4-core laptop is enough. The heaviest batch steps are capped at about 30 minutes.

## 4. Walkthrough

Run everything from the repository root. Paths are relative to it.

### Step 1: your copy of the game

You need your own copy of the IPA of **v2.3.0**. This repository decompiles that one version.
All addresses, symbols and test results in `analysis/` belong to its executable. You can
recognise it from its `Info.plist`:

| key | v2.3.0 |
|---|---|
| `CFBundleIdentifier` | `com.konami.mgst` |
| `CFBundleVersion` | `2.3.0` |
| `CFBundleExecutable` | `MGSTUS` |
| `DTSDKName` | `iphoneos3.2` |
| `UIDeviceFamily` | `[1, 2]` (universal: iPhone and iPad) |
| `MinimumOSVersion` | `2.0` |

Versions of the game, and whether this repository supports them:

| version | supported | why |
|---|---|---|
| 1.0.0, 2.0.0, 2.1.0 | no | iPhone-only builds (SDK 2.0) with different code, so every address differs. They are not FairPlay-encrypted either, so the same approach should apply, but the function map, the types and the tests would have to be redone for each. |
| **2.3.0** | **yes** | the reference build: last universal build that runs on iOS 2.0+, unencrypted, with debug symbols |
| 2.3.1 | no | needs iOS 3.0+ (`MinimumOSVersion 3.0`); different executable |

The decisive check is the executable hash. The IPA hash can differ between copies (an App Store IPA carries
per-purchase metadata) while the executable is the same:

| file | SHA-256 |
|---|---|
| IPA | `7c9904ea40eb190b3be7af2a3cdfaccb67f8440b1605e2edadefb92c425a1f8a` |
| `MGSTUS` executable | `07ac5db07fb8909a95b23c791d20800237bf14a51de1cec32cd0be8e37773a9c` |

```bash
./reproduce.sh /path/to/"Metal Gear Solid Touch.ipa"    # verifies, extracts to work/extracted/
```

Two properties make this target tractable, and the first one is worth checking on any iOS
binary:
- **Not FairPlay-encrypted:** `LC_ENCRYPTION_INFO cryptid=0`, so the code is directly
  readable.
- **Shipped unstripped:** 6,973 STABS debug records give the original build tree, all 68
  source file names, and 1,388 named functions with addresses.

### Step 2: facts straight from the binary

`reproduce.sh` runs these (all pure Python, no Ghidra):

| tool | output |
|---|---|
| `tools/macho.py` | load commands, segments, sections (`analysis/notes/macho_loadcommands.txt`) |
| `tools/dump_symbols.py`, `tools/dump_stabs.py` | symbol table, STABS records (`analysis/symbols/`) |
| `tools/build_function_map.py` | function -> address -> source file (`analysis/symbols/function_map.csv`) |
| `tools/export_ghidra_symbols.py` | every entry with its **ARM/Thumb mode** (`analysis/symbols/ghidra_symbols.tsv`) |
| `tools/objc_meta.py`, `tools/objc_types.py` | Objective-C classes, methods, ivars, type encodings (`analysis/objc/`) |

The tracked `analysis/` folder contains the processed results for v2.3.0 (function map, Ghidra symbols, ObjC tables) so you can compare. The raw symbol-table and STABS dumps are not published; `reproduce.sh` regenerates them from your own copy.

### Step 3: Ghidra with a patched decompiler

```bash
tools/install_ghidra.sh        # Ghidra 11.3.2 + JDK 21 (system-wide, once)
tools/ghidra_overlay.sh        # project-local copy with OUR decompiler build
```

`ghidra_overlay.sh` copies the installation to `build/ghidra-overlay/` (never modifying the
original) and rebuilds the native decompiler with two patches
(`tools/ghidra/patches/`). Both were found by differential testing, because stock Ghidra emits
C whose floating-point results differ from the binary:
- **`subflow-exact.patch`:** Ghidra narrows double arithmetic to float. That is exact only when
  at most one rounding operation is involved and the constants are exact; the patch enforces
  this.
- **`printc-float-nonassociative.patch`:** float `+` and `*` are not associative, so the
  printer must not drop parentheses.

### Step 4: build the Ghidra project

```bash
tools/build_ghidra_project.sh analysis/ghidra     # about 12 minutes
```

This imports `MGSTUS` and seeds every function entry with its ARM/Thumb mode *before*
auto-analysis. It then applies 22 scripts in dependency order:

| stage | scripts | what they fix |
|---|---|---|
| code structure | `InstallSwitchCallFixup`, `InstallSoftFloatCallFixup`, `FixSplitsAndStubs`, `ApplyDynamicCalls`, `ApplySwitchComments` | the compiler's `___switch8/u8/16` helpers become real `switch` statements; VFP soft-float helpers become float operators; functions Ghidra split at Thumb `bl` long branches are re-joined; runtime-observed indirect targets are added |
| types | `ApplyObjcTypes`, `ApplyCppTypes`, `SizeCppClasses`, `FixCppThis`, `TypeStaticProcs`, `FixDuplicateTypes`, `ApplyGlobalTypes`, `ApplyGlobalNames`, `ApplyExternalPrototypes` | every ObjC class from the runtime's own encodings; C++ classes from `this` usage and allocation sizes; globals; iOS SDK prototypes |
| signatures | `FixApcsStorage`, `FixStackStructLocals`, `CommitInferredSignatures`, `FixVoidReturns`, `SetUnusedReturnsVoid` | Apple's armv6 calling convention (64-bit values at 4-byte alignment); `objc_super` / fast-enumeration stack structs; return types proven from call sites |
| call sites | `ApplyCallsiteSignatures`, `ApplyVarargCallsites`, `ApplyVarTypes` | the **real method prototype at each of 6,313 `objc_msgSend` sites** (float returns, 64-bit arguments as two words); `NSLog` / `printf` / `stringWithFormat:` arguments from their constant format strings; individual variable types where Ghidra merged an int with a float |

Every input these scripts read is a tracked file under `analysis/`.

**Reproducibility, measured** ([`docs/REBUILD.md`](docs/REBUILD.md)): a from-scratch build was
compared with the original long-lived project. 1,390 of 1,395 functions compile to
**identical machine code**, the other 5 compile differently but pass all their differential
tests, and the static audits pass.

### Step 5: export, recompile, static audits

```bash
tools/mgst_verify.sh            # export -> recompile -> audits -> link -> ledger
```

| stage | tool | result |
|---|---|---|
| export | `ExportMgstDecompilation.java` (readable corpus, by original source file), `ExportCompilable.java` | `recovered/decompiled/*.c`, and `recovered/compile/functions.jsonl` (one compilable C body per function, printed from the decompiler's token tree so float/int reinterpretations and exact call targets are kept) |
| recompile | `tools/mgst_recompile.py` | every function compiled **alone** with `clang --target=armv6 -mthumb -mfloat-abi=softfp -O1`; the transforms it applies are listed in its header and in `recovered/compile/compile_report.md` |
| static audits (V1) | `tools/mgst_audit.py` | every switch table, every `objc_msgSend` site and every jump checked against the binary |
| coverage | `CoverageAudit.java` | every `__text` instruction taken into a decompiled function, or classified as data ([`docs/COVERAGE_AUDIT.md`](docs/COVERAGE_AUDIT.md)) |

Without the emulator you can go this far: a complete, compiling decompilation that passes all
static checks. **Tested:** a fresh copy of this folder plus the IPA reproduces this in about 14
minutes (`./reproduce.sh` does steps 1-5; re-tested 2026-10-12: 11 minutes plus audio): 1,395 / 1,395 functions decompiled and compiling,
V1 audits PASS. The regenerated symbol and ObjC metadata in `analysis/` is byte-identical to the
shipped files. The V1 fact tables differ only in the functions that
[`docs/REBUILD.md`](docs/REBUILD.md) lists as rebuilding to different machine code; those
functions still pass their tests.

Note: after step 5 your local `analysis/verification/status.md` shows **0 proven**. That is
expected: proofs come from differential tests (steps 6-8), whose captured game states cannot be
shipped. The reference results of the full run are in [`docs/STATUS.md`](docs/STATUS.md) and
`analysis/verification/function_status.tsv`.

### Step 6: the oracle (the original game, emulated)

Differential testing needs **real states of the running game**. The oracle is QEMU emulating an
iPod touch 2nd generation on iOS 3.1.3 (the community `qemu-ios` fork), with MGS Touch installed:

```bash
MGST_IPA=/path/to/your.ipa oracle/scripts/setup_oracle.sh   # deps, fork, our patches, firmware, build, plugins
sudo APP_SRC=work/extracted/Payload/MGSTUS.app NAND_DST=$PWD/oracle/firmware/nand-mgst-v230 \
    tools/inject_app_offline.sh      # install MGSTUS.app into the NAND image (offline; see the script for why)
oracle/scripts/boot_oracle.sh        # optional, to look around: boot; tools/mgst_launch.py starts the game
```

What `setup_oracle.sh` downloads (from the `qemu-ios` fork's GitHub releases): the iPod
touch 2G boot ROM, NOR and the iOS 3.1.3 NAND image `nand-appsync3`, which is patched to
install unsigned apps. `boot_oracle.sh` boots it with code-signature enforcement off, so the
game runs as you extracted it. It also downloads `iPod-touch-2G-macOS.zip` (262 MB, same release) for the **guest GL
engine** inside it (`MBXGLEngine`, an armv6 guest binary that forwards the game's OpenGL ES to
the host). `MGST_MACOS_ZIP=/path` uses a copy you already have. Every download is checked
against the SHA-256 of the copy this project was verified with. The NAND archive no longer
matches the release's own `SHA256SUMS` (upstream re-uploaded it); the script accepts GitHub's
current digest for it, which is the copy used here.

Our QEMU patches add two TCG plugins: **`drcov_mgst`** (coverage and dynamic call edges) and
**`snap_mgst`** (state capture). `tools/mgst_gdb.py` adds gdb commands that drive the game
(stage selection, menu scenes, boss phases) by writing the game's own state fields, so no
scripted gameplay is needed.

### Step 7: capture game states

```bash
tools/mgst_capture_all.sh                                           # the whole reference set (~7 h, resumable)
# or individually:
SNAP=dump tools/mgst_snapcampaign.sh 300 1-1 2-2 3-3 ... 20-20     # one snapshot set per mission
SUBSTAGE=3 ... tools/mgst_campaign.sh 16 16                         # boss phases
tools/mgst_menutour.sh 20 15 18 21 17 14 ...                        # menu screens
MGST_TOUR_TAPS="80,60;400,60;240,160" TAG_SUFFIX=_taps tools/mgst_menutour.sh 20 15 5   # in-screen taps
```

Each snapshot is a full process image (memory pages, registers, FPU mode) taken between frames,
stored under `oracle/reports/snap/`. The reference set is 40 directories (20 missions, boss
stages and phases, menu tours, tap tours).

### Step 8: differential testing

```bash
python3 tools/mgst_snap.py diff   oracle/reports/snap/<per-call dirs>    # functions as the game called them
python3 tools/mgst_snap.py frames oracle/reports/snap/*_dump             # whole frames from snapshots
python3 tools/mgst_snap.py calls  oracle/reports/snap/*_dump             # synthetic calls for the rest
python3 tools/mgst_snap.py refresh                                       # re-test only what changed
python3 tools/mgst_retest.py 0xADDR ...                                  # quick check of one function
```

What a test does (`tools/mgst_difftest.py`):
1. Load the state into Unicorn twice: once running the **original** function, once running the
   **recompiled** one (linked against the original binary).
2. Both run under the device's measured FPU mode (flush-to-zero plus default-NaN). Float
   helpers are real VFP instructions (`vfpshim.a`), and integer division has the measured
   semantics (`x/0 = 0`).
3. Compare **everything observable**: return registers, every byte written outside the run's
   own stack frame, and the exact sequence of calls to the outside world (OpenGL with the vertex
   data it consumes, OpenAL, libc, framework messages) with their arguments.
4. Read uninitialised stack under two poison patterns, so a difference caused only by garbage
   the original also reads is recognised.

Functions the game never called in a captured state are called **synthetically**: on a live
object of their class found in the snapshot, with fixed, live (the object's own fields) or
caller-derived arguments (`analysis/symbols/call_args.tsv`). Runs that get stuck outside the
game's code retry with boundaries, one tier at a time:
1. **Framework:** messages to UIKit/Foundation objects are recorded instead of executed.
2. **Callee:** only the specific proven function that gets stuck is stubbed, and every other
   call runs for real.
3. **Placeholder pages:** memory the capture lacks gets a deterministic pattern, identical in
   both runs.

Every result row records the tier.

### Step 9: the ledger and the gate

```bash
python3 tools/mgst_status.py     # -> analysis/verification/{status.md, function_status.tsv, gate_open.tsv}
```

The ledger keeps the strongest evidence per function. Results are tied to a **fingerprint** of
the exact recompiled binary, so a change makes its old results stale. **The gate:** every
function is proven, or listed in the V0 audit (`docs/V0_AUDIT.md`) with a written reason.

### Step 10: checking the checker

```bash
python3 tools/mgst_mutation.py --n 10 --dirs 8     # does the harness catch wrong code?
```

Proven functions are deliberately broken: an integer constant +1, a comparison flipped, a float
constant changed in its last bit. The harness must report **fail**. Result: 15 of 19 tested
mutants killed. The 4 survivors are 2 *equivalent* mutants (the change cannot alter behaviour)
and 2 in a branch no captured state reaches. The test also exposed a blind spot in the
harness, which is now fixed. Details: [`docs/MUTATION_TEST.md`](docs/MUTATION_TEST.md).

**What "proven" covers:** identical behaviour on every path the captured states exercise. Code
on paths no captured state reaches is decompiled and compiles, but is not executed by a test.
That is measured too:

```bash
python3 tools/mgst_testcov.py      # -> analysis/verification/test_coverage.{md,tsv}
```

The harness records which of the tested function's own instructions the original code executed
in every passing test. Result: **45.0 %** of the instructions of proven functions; 684 functions
at 100 %. The gaps are mostly the scene state machines and loaders, which run at scene
transitions ([`docs/TEST_COVERAGE.md`](docs/TEST_COVERAGE.md)).

Further static checks:
- `CheckAddrTiedMerge.java`: a decompiler defect class (stack buffers written through pointers),
  checked across all functions; [`docs/ADDRTIED_CHECK.md`](docs/ADDRTIED_CHECK.md).
- `CoverageAudit.java`: coverage, as in step 5.

## 5. Reading the results

| file | what |
|---|---|
| [`docs/GATE_SIGNOFF.md`](docs/GATE_SIGNOFF.md) | the sign-off: what "proven" means, evidence strength per function, V0 list, every defect class found and fixed |
| [`docs/STATUS.md`](docs/STATUS.md), `analysis/verification/function_status.tsv` | the ledger: one row per function (address, name, states, verdict, reason) |
| [`docs/COVERAGE_AUDIT.md`](docs/COVERAGE_AUDIT.md) | every byte of code accounted for |
| [`docs/V0_AUDIT.md`](docs/V0_AUDIT.md) | the 9 functions verified by reading the assembly instead of testing |
| [`docs/V1_AUDIT.md`](docs/V1_AUDIT.md) | static audits (switch tables, message sites) |
| [`docs/MUTATION_TEST.md`](docs/MUTATION_TEST.md) | how sensitive the harness is |
| [`docs/TEST_COVERAGE.md`](docs/TEST_COVERAGE.md) | which share of each function the tests executed |
| [`docs/REBUILD.md`](docs/REBUILD.md) | from-scratch rebuild compared with the original project |
| [`docs/ADDRTIED_CHECK.md`](docs/ADDRTIED_CHECK.md) | one decompiler defect class, closed |
| [`docs/FORMATS.md`](docs/FORMATS.md) | `.al` / `.rl` / `.data` / `.caf` / CgBI PNG formats |
| [`docs/PLATFORM_API.md`](docs/PLATFORM_API.md) | every iOS API the game uses, mapped to Android, with exactness risks |
| [`docs/GAMEPLAY_REFERENCE.md`](docs/GAMEPLAY_REFERENCE.md) | mission and enemy reference used to plan captures |

## 6. What we learned (pitfalls for anyone doing this)

Each of these was a real, silent difference between "decompiled" and "identical", found by the
tests:

- **Thumb vs ARM:** the mode is in each symbol's `n_desc` (`N_ARM_THUMB_DEF`), **not** the
  address's low bit. Seed it before analysis, or Ghidra decodes Thumb as ARM.
- **Soft-float:** armv6 code calls VFP helper functions (`___addsf3vfp` ...). Model them as float
  operators (call-fixups), and run them under the device's FPSCR (flush-to-zero), or results
  drift.
- **Float narrowing and associativity:** the stock decompiler prints double maths as float, and
  reassociates `+`/`*`. Both change results (our two patches).
- **Bit reinterpretation vs conversion:** Ghidra prints `(float)x` for both. Our exporter
  marks reinterpretations as `__BITCAST`.
- **Apple's armv6 calling convention:** 64-bit arguments are 4-byte aligned (r1:r2, r3:stack).
  Ghidra's default reads them from the wrong place: the `NSTimer` interval came out as
  `(self, selector)`.
- **Variadic calls:** `NSLog(@"%d", x)` decompiles without its `x` unless the format string is
  read.
- **Stack buffers written by calls** (stret results): Ghidra can miss the write and merge
  versions, so the C reads a stale value. This is closed by a static check.
- **Names that collide in C:** distinct Ghidra symbols (`cf_,` and `cf_:`) sanitise to one C
  identifier. Use the address-unique name.
- **Inline switch tables and literal pools** sit inside `__text` and get disassembled as code.
  Classify them, don't "decompile" them.
- **Ghidra's stored function bodies** omit switch-case code reached through call-fixups, so
  measure coverage on the decompiler's own flow (`firstpass`), not on `Function.getBody()`.
- **Your verifier needs verifying:** stubbing every callee to return 0 hid branches that
  depended on callee results. A mutation test exposed this, and the harness now stubs only what
  gets stuck.

## 7. Repository layout

```
README.md            this walkthrough
reproduce.sh         step 1-2: verify + extract your IPA, static facts
docs/                results and reference documents (copies of the analysis/ originals)
tools/               the pipeline (Python / shell)
  ghidra/            Ghidra scripts (Java) + decompiler patches
analysis/            metadata from the binary + verification results (tracked)
  symbols/  objc/  dynamic/  coverage/  notes/  verification/  port/
oracle/              emulator recipe: setup/boot scripts + our QEMU patches
```
Generated locally (git-ignored): `work/` (extracted app), `analysis/ghidra/` (Ghidra project),
`build/` (decompiler overlay, logs), `recovered/` (**the decompiled C**),
`oracle/firmware`, `oracle/qemu-ios`, `oracle/reports/snap` (snapshots).

This folder is generated from the working repository by `tools/make_github_folder.py`, which
also enforces the exclusions in section 1.

## 8. Next: porting

The decompilation is the foundation for exact ports. The plan in
[`docs/PLATFORM_API.md`](docs/PLATFORM_API.md) is to compile the **verified C unchanged** and
replace only the iOS frameworks (a small ObjC runtime, a Foundation subset, OpenGL ES 1.1 via
EGL, OpenAL Soft, Oboe). It starts with a 32-bit ARM build that maps the original data image at
its original addresses, then moves to a 64-bit build that keeps every pointer as a 32-bit offset
into one memory arena. It lists what makes "exact" hard beyond the code: Darwin's `random()`, iOS
libm `sinf`/`cosf`, text rendered at runtime, premultiplied CgBI textures and the IMA4 music
decoder.

## 9. Licence and legal

The original work in this repository (tools, scripts, patches, documentation, metadata tables)
is released under the MIT licence (`LICENSE`).

That does **not** cover METAL GEAR SOLID TOUCH. *METAL GEAR SOLID* and *METAL GEAR SOLID TOUCH*
are trademarks of Konami; the game, its code and its assets are Konami's copyrighted work. This
project is not affiliated with or endorsed by Konami. Use your own legally obtained copy. Do
not redistribute the game, its assets, or the decompiled code you generate from it.
