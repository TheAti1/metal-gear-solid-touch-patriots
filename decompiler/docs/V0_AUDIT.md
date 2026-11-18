# V0 manual audit: functions not decided by differential testing

PLAN 4b gate: every function is either proven bit-identical by differential tests (natural or
synthetic states), or on this list with a written asm-to-C audit. The budget is ≤ 2 % of
1,395 functions. Current list: 6 (0.43 %).

Each entry gives what the binary does (disassembly of MGSTUS v2.3.0), what the exported C does,
the verdict, and what the Android port must do.

Status as of 2026-10-08.

---

## Shared pattern: SjLj exception frames (4 functions)

`_main` 0x2628, `-[CrashLandingAppDelegate renderScene]` 0xa2c0, `Sound::ready` 0x200d4 and
`SoundService::init` 0x21b44 contain C++ code that can throw (operator new, ObjC message
sends inside @try, C++ constructors). Apple's armv6 toolchain implements that with **setjmp/longjmp
("SjLj") exception handling**:

- On entry the function builds a `_Unwind_FunctionContext` in its own frame. The fields are:
  `prev`, `call_site` (`local_50`), `data[4]`, `personality` (`local_3c` = `PTR_00069094`),
  `lsda` (`local_38` = `GCC_except_table…`), and `jbuf[]`. `jbuf` holds the frame pointer
  (`local_34 = &stack0x00000038` = entry SP + 0x38, which is the value of r7 after the
  prologue), the landing-pad address (`local_30 = &LAB_…`) and SP (`local_2c`).
- It links the context into the thread's chain with `_Unwind_SjLj_Register`.
- Before each call that may throw, it stores a call-site index into `call_site` (`local_50 = N`).
- On exit it unlinks with `_Unwind_SjLj_Unregister`.

The context is consumed **only when an exception propagates** through the frame: the unwinder
longjmps to `jbuf` (restores r7/SP, jumps to the landing pad) and dispatches on `call_site`.

**Exported C.**
- The registration, the call-site stores and the unregistration are reproduced literally.
- `stack0x00000038` (an address relative to the caller's frame) has no C equivalent. The
  recompile approximates it with `__ENTRY_STACK(0x38)`, derived from
  `__builtin_frame_address(0)`, and lists it under "Entry-stack approximations".
- `LAB_…` is the landing pad's address **in the original binary**.

**Verdict.**
- **Equivalent on every non-exceptional path.** Differential tests cover these paths:
  - `renderScene`: natural frames in every snapshot;
  - `Sound::ready`: offline, frame and synthetic states, after the `___save_vfp_d8_d15_regs`
    fix, LOG 2026-10-08;
  - `SoundService::init`: synthetic calls;
  - `_main`: never re-entered after start-up.

  On those paths the context is only written, never read back (the chain head lives in
  thread-local storage and is restored on unregister).
- **Not equivalent on the exceptional path.** A recompiled frame registers the ORIGINAL landing
  pad and an approximated r7, so an exception thrown through it would land in original code
  with a foreign frame layout. Nothing in the game throws through these frames in normal
  operation: no `@throw` in MGSTUS; `operator new` fails only on out-of-memory.

**Port.** Replace the SjLj frame with the source-level construct it was compiled from:
C++ `try { … } catch (…) { … }` (or ObjC `@try`). The landing-pad bodies are the
code at the `LAB_…` addresses, decompiled as part of each function's body after the
`setjmp`-style dispatch. Write them as `catch` blocks.

### `_main` 0x2628
- Also V0 because Ghidra loses its first argument. `___save_vfp_d8_d15_regs` was a plain call,
  so r0-r3 counted as clobbered: `argv` became `extraout_r1`. **Fixed 2026-10-08:** the helper
  pair is now a p-code call-fixup (`sp -= 64` / `sp += 64`, ARM `vpush/vpop {d8-d15}`), so
  `argv` flows through. The function is `UIApplicationMain(argc, argv, nil,
  @"CrashLandingAppDelegate")` inside an autorelease pool. Port: Android `main` /
  `NativeActivity` entry; no direct translation needed.

### `-[CrashLandingAppDelegate renderScene]` 0xa2c0
- The per-frame method: `GameScene`, touch clear, pre-render, `glClear`, `DrawGame`,
  post-render, accelerometer re-init, `GSoundCtrl::update`. The body passes differential tests on
  every snapshot frame; only the SjLj frame is approximated.

### `Sound::ready` 0x200d4 and `SoundService::init` 0x21b44
- **Fixed 2026-10-10 (a real bug, hidden behind the V0 label):** both returned nothing in the
  recompiled C. The recompiler's stack-frame overlay took `return uStack_b4;` /
  `return iStack_ac;` for a declaration and turned it into a `#define`, deleting the return. The
  original returns the value (`ldr r0,[sp,#0x10]` at 0x202fe before the epilogue).
- **Fixed 2026-10-11 (found by the mgsport port):**
  - `struct Sound` was laid out as 0x39 bytes, so the port loop in `SoundService::init` stepped
    0x3f per element. The binary allocates `operator_new(n * 0x3c)`, so the size is now 0x3c
    (`cpp_sizes.tsv`).
  - Four sound-volume functions return float bits but were declared `undefined4`, so callers
    converted 1.0f into 1.065e9: `SoundManager::masterVolume`, `SoundManager::categoryVolume`,
    `SoundResourceManager::attributeVolume`, `SoundService::categoryVolume`. They are now typed
    float (`float_returns.tsv`, `ApplyFloatReturns.java`).
- **Correction:** the remaining 3-byte difference in `Sound::ready`, attributed on 2026-10-10 to
  the SjLj approximation, was the volume defect. With these fixes `Sound::ready` and
  `SoundService::init` **pass** (31/31 and 12/12). The SjLj frames remain V0 for the
  exceptional path only.
- Same pattern. Both also lost their argument through the VFP spill helper (`param_1` →
  `extraout_r1`); fixed by the same call-fixup.

---

## `entry` 0x25bc (crt0 `start`)

```
25bc ldr  r0, [sp]            ; argc
25c0 add  r1, sp, #4          ; argv
25c4 add  r4, r0, #1
25c8 add  r2, r1, r4, lsl #2  ; envp = argv + argc + 1
25cc bic  sp, sp, #7          ; 8-byte align the stack
25d0 mov  r3, r2
25d4 ldr  r4, [r3], #4        ; apple = past envp's NULL
25d8 cmp  r4, #0
25dc bne  25d4
25e0..25ec blx  *_main        ; r0..r3 = argc, argv, envp, apple
25f0..25fc bx   *_exit        ; r0 = main's result
```

**Exported C** reproduces the envp scan, but **drops the register arguments**: `_main()` is
called with none and `exit()` without the status. Ghidra's prototype for the indirect target is
`code *` with no parameters. The stack reads use `stack0x…` (the kernel-built entry stack).

**Verdict: not equivalent as C.** The faithful form is:

```c
void start(void) {                         /* sp -> argc, argv[], NULL, envp[], NULL, apple[] */
    int argc = *(int *)SP;
    char **argv = (char **)SP + 1;
    char **envp = argv + argc + 1;
    char **apple = envp;
    while (*apple++ != 0) ;
    exit(main(argc, argv, envp, apple));
}
```

**Port.** None needed: the C runtime / Android loader provides the entry point.

---

## `dyld_stub_binding_helper` 0x2608

```
2608 push {ip}                ; lazy-pointer offset
260c ldr  ip, [pc, #12]
2610 ldr  ip, [pc, ip]        ; dyld's image cache entry (0x69000 + …)
2614 push {ip}
2618 ldr  ip, [pc, #4]
261c ldr  pc, [pc, ip]        ; tail-jump into dyld's binder
```

**What it is.** It is dyld glue, not application code. The first call through a lazy symbol stub
lands here; dyld resolves the import, patches the lazy pointer, and jumps to the target.
Differential tests cannot decide it: dyld's code lies outside the test world.

**Exported C.** An indirect call through `global_69000`. That is correct as a description, but
not meaningful.

**Port.** None: Android's dynamic linker binds imports.

---

## Summary

| function | addr | equivalent (normal paths) | issue | port action |
|---|---|---|---|---|
| `entry` | 0x25bc | as asm | C drops `main`'s args and `exit` status | none (runtime entry) |
| `_main` | 0x2628 | yes (argv fixed 2026-10-08) | SjLj frame approximated | Android entry |
| `renderScene` | 0xa2c0 | yes (tested every frame) | SjLj frame approximated | `try/catch` |
| `Sound::ready` | 0x200d4 | yes (tested) | SjLj frame approximated | `try/catch` |
| `SoundService::init` | 0x21b44 | yes (synthetic) | SjLj frame approximated | `try/catch` |
| `dyld_stub_binding_helper` | 0x2608 | n/a (dyld glue) | not app code | none |
