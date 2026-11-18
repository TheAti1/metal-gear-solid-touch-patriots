# Port plan, input 1: every platform API the game touches

Status as of 2026-10-09. Sources:
- C imports: `analysis/symbols/stubs_v230.tsv`, with call sites counted in the exported C
  (`recovered/compile/functions.jsonl`);
- ObjC framework receivers and selectors: `analysis/dynamic/msgsend_sites.tsv` (runtime capture)
  and `analysis/objc/external_methods.tsv` (SDK signatures).

## The approach this inventory serves

The goal is a port that behaves exactly like the original, so the port compiles the **verified
decompiled C** (every function proven bit-identical or V0-audited) and replaces only what lies
outside the game: the iOS frameworks below. The game logic is not rewritten. The earlier
hand-written workspace (`android/native/core`, about 1,800 lines, paused) predates the
decompilation and is not exact; its platform pieces (`android/native/plat`: JNI bridge,
renderer, Platform) are reusable as a starting point.

### Decision needed: the memory model

The verified C is ILP32 ARM code. Pointers are 32-bit, structs are laid out with 4-byte
pointers, and it addresses the original image's data (selector refs, globals, constants) at fixed
addresses 0x69000-0x89000.

| option | how | exact? | runs on |
|---|---|---|---|
| **A. armeabi-v7a** (32-bit) | build the C as-is for 32-bit ARM; map the original `__DATA`/constant image at its original addresses (above `mmap_min_addr`, MAP_FIXED); VFP FPSCR = FZ+DN like the device | yes, closest to the binary | devices that still run 32-bit apps; several 2023+ phones are 64-bit only (Pixel 7 and later) |
| **B. arm64 with a 32-bit memory arena** | the recompiler emits every pointer as a 32-bit offset into one 4 GB arena (as wasm2c does); the image is loaded into the arena at the original addresses; FPCR FZ+DN | yes: same values and same layout, pointers translated | every Android device (and other systems later) |
| C. hand port | rewrite the game logic | no | n/a |

Recommendation: **A first** (fastest way to a verifiable, running port, using the same
differential tools against the emulator), then **B** as a mechanical transform of the same C
for 64-bit-only devices and other systems. The differential harness can check B's output against
A and against the original.

## Inventory by subsystem

Counts are call sites in the decompiled C (C imports) or sites observed at runtime
(ObjC messages).

### ObjC runtime: the dispatch core
`objc_msgSend` 5,951 · `objc_msgSend_stret` 221 · `objc_msgSendSuper2` 147 ·
`objc_enumerationMutation` 19 · `objc_setProperty` 1.

**Port:** a small ObjC runtime in C that keeps the original class and method tables from the
image (`analysis/objc/classes.tsv`, `methods.tsv`). Selectors stay the original selref
addresses, so the verified C runs unchanged. Dispatch: class -> method list -> IMP, which is the
recompiled function. Messages to framework classes go to the shims below.

### Foundation (about 400 runtime sites)
| class | main selectors (sites) |
|---|---|
| NSArray/NSMutableArray (NSCFArray) | objectAtIndex: 48, fast enumeration 17, addObject: 14, removeAllObjects 5, count, reverseObjectEnumerator, sortUsingFunction:context: |
| NSString (NSCFString) | stringWithFormat: 48, UTF8String 24, length 22, componentsSeparatedByString: 18, stringWithCString:encoding: 12, intValue 9, lineRangeForRange:, substringWithRange:, floatValue, dataUsingEncoding:, stringWithContentsOfFile:encoding:error: |
| NSBundle | mainBundle 33, pathForResource:ofType: 24, ...inDirectory: 6, localizedStringForKey:value:table: 2 |
| NSDictionary/NSMutableDictionary | objectForKey: 7, setObject:forKey: 4, dictionary 4, dictionaryWithObjectsAndKeys:, initWithObjectsAndKeys: |
| NSNumber | numberWithInt: 10, intValue 6, numberWithBool: |
| NSData | dataWithContentsOfFile: 2, bytes, length, getBytes: |
| NSFileManager | changeCurrentDirectoryPath: 2 |
| NSUserDefaults | standardUserDefaults, registerDefaults: |
| NSNotificationCenter | addObserver:selector:name:object: |
| NSLock / NSThread / NSTimer | lock/unlock, detachNewThreadSelector:toTarget:withObject:, scheduledTimerWithTimeInterval:... |
| NSAutoreleasePool | alloc/init (`_main`) |
| C: `NSLog` 49, `NSSearchPathForDirectoriesInDomains` 2 | |

**Port:** implement exactly this subset in C on top of the runtime (immutable/mutable arrays,
dictionaries, strings with a printf-compatible `stringWithFormat:`). Bundle paths go to the APK
assets; the Documents directory goes to the app's files directory. `NSLog` goes to logcat.

### UIKit (C: `UIApplicationMain`, `UIGraphicsPush/PopContext`)
UIWindow (initWithFrame:, bounds, addSubview:, makeKeyAndVisible), UIScreen (mainScreen, bounds,
applicationFrame), UIDevice (currentDevice, model, userInterfaceIdiom), UITouch (locationInView:),
UIAccelerometer/UIAcceleration (x/y/z, setUpdateInterval:), UIImage (imageWithContentsOfFile:,
CGImage), UIFont (fontWithName:size:), UIColor, UIAlertView (initWithTitle:..., show),
UIApplication (openURL:, setNetworkActivityIndicatorVisible:), UIWebView (DWWebView: loadRequest:,
loadHTMLString:baseURL:).

**Port:** NativeActivity (or GameActivity) owns the window and the 480x320 logical screen;
Android touch events become UITouch objects with the same coordinates (landscape transform as on
the device). The accelerometer comes from the Android sensor at the same update interval.
UIWebView goes to Android WebView (or is dropped: it holds online news and links). UIAlertView
goes to an AlertDialog.

### Graphics: OpenGL ES 1.1 (33 functions) and EAGL
glBlendFunc 99, glTexEnvf 25, glTexParameteri 18, glDisable 14, glEnable 10, glColor4f 5,
glBindTexture, glDrawArrays, glVertexPointer/glTexCoordPointer, glMatrixMode, glOrthof,
glClipPlanef, glScissor, glTexImage2D, framebuffer/renderbuffer OES. EAGLContext (initWithAPI:,
presentRenderbuffer:, renderbufferStorage:fromDrawable:), CAEAGLLayer.

**Port:** Android supports OpenGL ES 1.1 natively through EGL. The calls pass through
one-to-one; EAGL maps to EGL context and surface. The GL call stream is already compared by the
differential harness (vertex data included), so the port can be checked call by call.

### CoreGraphics (20 functions): runtime texture and text rendering
CGBitmapContextCreate 8, color spaces, CGContextDrawImage, CTM transforms, fills,
CGImageGetWidth/Height/AlphaInfo. Text: NSString `drawInRect:withFont:lineBreakMode:alignment:`,
`sizeWithFont:` (Texture2D Text, Helvetica-Bold).

**Port:** image decoding into a premultiplied RGBA bitmap, written in C. **Text cannot be
reproduced exactly with an Android font rasterizer.** Exact approach: capture every runtime-rendered
text texture (string, font and size, then the `glTexImage2D` bytes) from the emulator, which
already runs the original, and ship them as assets; the text drawing path looks them up.

### Audio: OpenAL (22), AudioToolbox (23), AudioSession
OpenAL: alGenSources/Buffers, alSource*, alListener*, alDistanceModel, alc* context (sound effects,
3D positioned). AudioToolbox: AudioQueue* (BGM streaming), AudioFile* (CAF reading),
AudioServicesPlaySystemSound, AudioSession*.

**Port:** OpenAL Soft (builds with the NDK; same API) for effects. AudioQueue goes to an
Oboe/AAudio stream fed by the game's own buffer callbacks. AudioFile reads the converted files.
AudioSession goes to Android audio focus.

### Video: MediaPlayer
MPMoviePlayerController (initWithContentURL:, setScalingMode:, play; finished notification).
**Port:** Android MediaPlayer/ExoPlayer, with the same completion callback into the game.

### C library and runtime (28 + 40)
random 240, malloc 48, free 44, sinf 26, printf 18, cosf 17, memcpy 15, sqrtf 10, memset 8,
strlen, fopen/fread/fwrite/fseek/ftell/fclose, qsort, strings, srandom, atan2/atan2f,
mach_absolute_time, CFAbsoluteTimeGetCurrent. Compiler runtime: VFP soft-float helpers,
integer division, C++ new/delete, SjLj exception registration.

**Exactness risks:**
- **`random()`** (240 sites, enemy AI and effects): the port must use Darwin libc's `random()`,
  the BSD additive-feedback generator seeded by `srandom`, bit-exact. Bionic's is a different
  generator. Implement from the BSD source and verify its output against the emulator.
- **`sinf`/`cosf`/`sqrtf`/`atan2(f)`**: iOS 3.x libm results must match to the last bit, or
  positions drift. `sqrtf` is exact (IEEE). For `sinf`/`cosf`/`atan2`, differentially test
  Android's results against the original's over the values the game uses (the harness can
  capture them); ship Apple-equivalent implementations if they differ.
- **Float mode:** the device runs VFP with flush-to-zero and default NaN (measured). Set the
  same in FPSCR (32-bit) or FPCR (arm64) on every game thread.
- **Integer division:** ARMv6 had no divide instruction; the measured semantics (x/0 = 0,
  INT_MIN/-1 = INT_MIN) are already in `vfpshim.a`; the port links the same helpers.
- **SjLj exception frames** (4 functions, V0): rewritten as `try/catch` (see
  `analysis/verification/v0_audit.md`).
- **Time:** `mach_absolute_time` and `CFAbsoluteTimeGetCurrent` go to `clock_gettime`. Game
  logic is frame-driven, so time affects pacing only.

## Assets

App bundle: `work/extracted/Payload/MGSTUS.app` (273 MB). Converted output goes to
`build/port_assets/` (not committed: derived from copyrighted data).

| type | count | conversion | exact? |
|---|---:|---|---|
| CAF linear PCM | 192 | FLAC, `tools/port_audio.py` | **yes**: bit-exact round trip verified for every file |
| CAF IMA4 ADPCM (BGM) | 35 | FLAC of ffmpeg's IMA4 decode | **to verify**: Apple's AudioQueue decoder vs ffmpeg (or ship IMA4 and decode in the port with a verified decoder) |
| PNG, Apple CgBI | 427 | `tools/decgbi.py` exists (to standard PNG) | **care**: CgBI is premultiplied BGRA. Un-premultiplying is lossy, so the port should keep the premultiplied pixels, which is what CoreGraphics hands the game, and verify against the `glTexImage2D` bytes recorded on the emulator |
| PNG, standard | 333 | as-is (decode to premultiplied RGBA like CoreGraphics) | verify the same way |
| .data / .al / .rl / .csv / .bmp / .plist / .strings / nib | 164 / 102 / 102 / 4 / 29 / 2 / 1 / 1 | copied verbatim | yes |

The earlier workspace (`android/app/src/main/assets`) holds Ogg Vorbis audio, which is lossy and
therefore not exact; replace it with the FLAC set.

## Order of work (proposed)
1. Decide on the memory model (A, then B).
2. ObjC runtime and Foundation subset, which the verified C needs in order to run at all.
3. GLES 1.1 and EGL, input, then the frame loop: `renderScene` driven by Choreographer.
4. Audio (OpenAL Soft, Oboe for AudioQueue), video, file I/O and saves.
5. Exactness work: Darwin `random()`, libm check, text-texture capture, IMA4 decoder check.
6. Frame-by-frame comparison against the emulator and the reference video (PLAN).
