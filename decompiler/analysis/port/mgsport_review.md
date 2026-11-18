# Review of the Android port (`mgsport`, APK `com.mgsport.touch` 0.1-d1)

**Date:** 2026-10-11 · **Reviewed:** the port project's source (read-only, with the user's
permission) and its APK (`assets/mgst-touch.apk`, built 2026-10-11 07:06), run on the Android
emulator. **Question:** is the port exact, and does it prove the decompilation is proper?

## Verdict

| question | answer |
|---|---|
| **Does the port prove the decompilation is proper?** | **Yes.** The port compiles the verified C of all 1,395 functions, minus the 6 V0 glue functions the platform replaces (entry, `_main`, dyld, switch helpers), with mechanical transforms only. It runs the original game flow: `UIApplicationMain`, the delegate, the 20 Hz NSTimer, the title menu, ACT 1, the controls tutorial, and Mission 01 gameplay (the port's scripted runs). The port found **2 defects** in the decompilation; both are now fixed at the source, together with a third link in the same chain found while re-testing (below). |
| **Is the port an exact copy?** | **Not yet.** It is a faithful port (game logic unchanged, assets original), but four measured differences remain, listed below. The port's own plan calls exactness "Delivery 2", not started. |

## What the port does right (checked)

| item | evidence |
|---|---|
| Game code = the verified C | `tools/xform.py`: strips comments, maps globals to their original addresses, routes message sends through argument-word thunks (armv6 APCS), patches two documented defects. No logic rewritten. |
| Memory model | wasm32 is ILP32, and the original data image is loaded at its original addresses (0x1000-0x89000); `layout_check.sh`: 0 struct layout differences in 208 structs |
| **`random()`** | Darwin BSD generator reimplemented. **Measured: 18,000 / 18,000 values identical** to the real iOS `libSystem` (called inside a captured snapshot through the game's own import stub; 9 seeds x 2,000; `tools/mgst_libcheck.py random`) |
| Integer division | wasm2c output patched to the device's helpers (x/0 = 0, INT_MIN/-1 = INT_MIN) |
| No fused multiply-add | `-ffp-contract=off` |
| Assets | the original bundle, unmodified, read from the APK; IMA4 music decoder matches FFmpeg on all 1,867,520 samples of the title theme (port's test) |
| Startup and menus | on the emulator with host GPU: the original title menu, ACT 1, and the 7-page controls tutorial render as in the original |

## Decompilation defects the port found, now fixed here

1. **`struct Sound` was 0x39 bytes** (laid out from `this` accesses). The binary allocates
   `operator_new(n * 0x3c)`, but the C stepped `&p[1] + 3` = 0x3f, so no music played. Fixed
   with `Sound 0x3c` in `cpp_sizes.tsv`; the C now reads `this_01 = this_01 + 1`.
2. **Float bits returned as `undefined4` and converted by callers** (volume 1.0 became 1.065e9).
   Fixed for `SoundManager::masterVolume`, `SoundManager::categoryVolume` and
   `SoundResourceManager::attributeVolume`, and, found when re-testing, for
   `SoundService::categoryVolume` too (`float_returns.tsv`, `ApplyFloatReturns.java`).
   Scans: no other occurrence of either class in 1,395 functions.
3. **Why the tests had missed them, now fixed:**
   - the callee boundary stubbed the volume functions to return 0, and `(float)0` equals the bits
     of 0;
   - the ledger let a pass row outrank a return-value difference. Such rows now count as fail
     unless the function is void. Re-ranking the ledger found no further failures.
   - My 2026-10-10 explanation of `Sound::ready`'s remaining 3-byte difference (the SjLj
     approximation) was wrong: it was this defect. `Sound::ready` and `SoundService::init` now
     pass.

**Note for the port:** a handoff regenerated from this fixed decompilation no longer contains
those two patterns. The port's `DEFECTS` / `FLOAT_BITS_RETURNERS` patches will then stop its
build ("no longer matches"), as designed. Remove them; no other change is needed.

## Differences that keep the port from being exact (measured)

| # | difference | measurement | effect | fix in the port |
|---|---|---|---|---|
| 1 | **No flush-to-zero / default-NaN.** The iPod's VFP runs FZ+DN; wasm and arm64 default to IEEE denormals | Frame driver over 8 missions/menus with the recompiled side in IEEE mode (`MGST_RECOMP_FPSCR=ieee`): **8 functions differ on real game states**: `Player private_Breath` (sniper sway value 0 vs a denormal at 0x84b69; also seen in its callers `Player proc`, `sh_gameMain`, `GameScene`) and the sound-volume chain (`SoundService::updateVolume`, `Sound::reset`, `GSoundCtrl::Se3DSet`, `SoundService::updateStatus`) | sniper-scope sway and sound fades take slightly different values; later comparisons against 0 can branch differently | set FPCR.FZ + FPCR.DN on the game thread (arm64), MXCSR FTZ+DAZ (x86_64). ARMv8 FZ/DN behave like the armv6 VFP bits |
| 2 | **`sinf` / `cosf` / `atan2f` from Android's libm** | iOS libm (real, from the snapshot) vs bionic (x86_64, on the emulator), over the game's inputs: **sinf 2,985 / 18,401, cosf 2,977 / 18,401, atan2f 744 / 4,374 results differ, all by 1 ULP** | rotations, missile/effect trajectories, enemy paths can drift by an ULP and accumulate | ship the original algorithms: decompile iOS libm's `sinf`/`cosf`/`atan2f` from the snapshot like the game functions, and verify them the same way; check arm64 bionic separately (it may use different code) |
| 3 | **Text rendered with Liberation Sans** instead of Helvetica-Bold | by construction (the port's plan, D2.3) | menu and number glyph pixels differ | capture the original's runtime text textures from the emulator and ship them |
| 4 | **Not yet verified:** OpenAL distance attenuation and mixing, GPU rasterisation | port's plan D2.4 / D2.1 | sound levels, sub-pixel rendering | per-frame GL stream + framebuffer comparison against the emulator |

## Deliberate deviations (acceptable)

- **Online features off:** `openURL`, UIWebView (news, Drebin movie page), MPMoviePlayer. The
  servers no longer exist; v2.3.0's own `getMovieURL:` already returns nil.
- **The one dialog is auto-cancelled:** the game's only UIAlertView is
  *"This will close the application and launch the web browser … Proceed? OK / Cancel"*, shown
  before the online links (menu items 0x10/0x13). Cancel is the only meaningful answer offline.

## Platform caveat found while testing

On the emulator's software renderer (SwiftShader) the game framebuffer is incomplete
(status 0), so the screen stays black with `GL_INVALID_OPERATION` every frame. On the host GPU
it is complete (0x8cd5) with 0 GL errors. Phones whose GLES 1.1 lacks a working
`OES_framebuffer_object` would hit the same; the port's planned GLES2 fallback covers them.

## Reproduce

```
python3 tools/mgst_libcheck.py random                   # iOS random() vs the port's
python3 tools/mgst_libcheck.py libm OUT.tsv             # iOS sinf/cosf/atan2f results; run the
                                                        # same inputs through the device libm
MGST_RECOMP_FPSCR=ieee python3 tools/mgst_snap.py frames <snap dirs> --out X.jsonl   # FZ impact
```
