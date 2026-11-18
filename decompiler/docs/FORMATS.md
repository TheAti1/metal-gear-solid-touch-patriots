# MGS Touch — Resource Format Specifications

All offsets little-endian. Every claim is tagged with its evidence:

- **CONFIRMED** — transcribed from the decompiled loader and validated against
  every shipped file
- **INFER** — consistent across all files but not proven from code
- **UNKNOWN** — not established

---

## `.al` — animation list — **CONFIRMED**

102 files, pairing 1:1 by basename with `.rl`. Loader:
`DWUtilities readAnimeData::` @ `0x22f5c`.

```
struct AL {
    int16  frameCount
    int16  unk                      // equals frameCount in most files (INFER)
    Frame  frames[frameCount]
}

struct Frame {
    int16  partCount
    int16  unk
    Part   parts[partCount]         // stride 0x0c
}

struct Part {                       // 6 x int16
    int16  rectIndex                // -> index into the paired .rl groups
    int16  unk1
    int16  offsetX                  // signed, usually negative (centring)
    int16  offsetY                  // signed
    int16  unk4
    int16  unk5
}
```

## `.rl` — rect / atlas table — **CONFIRMED**

102 files. Loader: `DWUtilities readRectData::` @ `0x23190`.

```
struct RL {
    int16  groupCount
    int16  unk
    Group  groups[groupCount]
}

struct Group {
    int16  itemCount
    Item   items[itemCount]         // stride 0x0e
}

struct Item {                       // 7 x int16
    int16  textureId
    int16  x, y                     // atlas position
    int16  w, h                     // atlas size
    int16  unk5, unk6
}
```

### Why the obvious reading is wrong

Both formats look like flat fixed-stride records at a glance, and a
16-byte-record interpretation parses roughly 55% of files cleanly. It is
wrong. The structures are **nested and variable-length**, which is exactly why
43 `.rl` files "don't divide evenly" under the flat theory.

Validation is by **exact consumption**: a correct structural reading consumes
every byte of all 204 files with none left over. `tools/parse_alrl.py`
enforces this and reports 204/204.

### Playback

```
frame -> part -> rectIndex -> .rl group -> item -> atlas sub-image
```
drawn at the part's signed `offsetX`/`offsetY`.

---

## `.data` — configuration tables — **CONFIRMED**

164 files, **plain ASCII CSV**. No binary decoding, no compression, no
encryption. Families by filename:

| Pattern | Contents |
|---|---|
| `shstage<NN>_<p>.data` | per-stage/phase configuration |
| `shstage<NN>_<p>_ap.data` | spawn ("appear") tables |
| `Imagestage<NN>.data` | per-stage background image tables |
| `menu_<n>.data` | menu layout |
| `drebin_<n>.data` | Drebin shop data |

### Spawn table layout — **INFER**

```
<count>,<unk>                       header row
kind,x1,y1,z1,x2,y2,z2,time,n       one row per spawn entry
```

Row *count* is confirmed. Column meanings are inferred from consistent
behaviour: the two coordinate triples look like a movement path, `time`
increases monotonically within a file, `n` is small. Verify against
`EnemyManager updateAppearData:` before relying on it.

---

## `.caf` — audio — **CONFIRMED**

228 files. **Not uniform** — this catches people out:

| Codec | Files | Bytes | Note |
|---|---:|---:|---|
| `pcm_s16le` | 193 | 15 MiB | SFX, raw |
| `adpcm_ima_qt` | 35 | 94 MiB | music, **already compressed 4:1** |

86% of the audio *bytes* are already lossy. Transcoding the music to Ogg
Vorbis is therefore a second lossy generation and needs extra bitrate to
avoid compounding artefacts; `tools/convert_assets.py` selects quality by
source codec rather than by file size for exactly this reason.

Sample rates vary (18/22.05/24/28/32/36/44.1 kHz), mono and stereo both
present.

---

## `.png` — images — **CONFIRMED**

832 PNG (plus 29 BMP). `ipd_`-prefixed variants are iPad-resolution assets.

### Most of them are NOT standard PNG — read this before anything else

**469 of 832 are Apple "iPhone-optimized" CgBI PNGs.** Xcode runs shipped
PNGs through a modified pngcrush that produces a format only CoreGraphics
understands. Four differences:

1. A proprietary `CgBI` chunk is inserted **before** IHDR.
2. IDAT holds a **raw deflate** stream — no zlib header, no adler32.
3. Channel order is **BGRA**, not RGBA.
4. Colour is **premultiplied** by alpha.

This is the single nastiest trap in the bundle, because it does not fail
loudly. A standard decoder parses IHDR happily and reports the correct
dimensions, so logs look healthy — then the pixels come out wrong. Observed
symptom on Android: a **completely black screen** alongside a
`texture loaded 768x1024` success line. Python's Pillow is stricter and
reports `broken data stream`, which is a useful quick check.

Detect by looking for `CgBI` in the first chunk:

```bash
xxd -s 8 -l 8 file.png     # "....CgBI" => optimized
```

Convert with `tools/decgbi.py` (handles detection, raw-deflate inflate,
un-filtering, BGRA→RGBA swap, and un-premultiplication):

```bash
python3 tools/decgbi.py --check path/to/assets     # count them
python3 tools/decgbi.py --in-place path/to/assets  # convert
```

Detection is per-file — 363 of the PNGs are already standard, so converting
unconditionally would corrupt those.

### Also

Decode with `inScaled = false` on Android. Density scaling silently resizes
the artwork and invalidates every atlas rect the `.rl` tables describe.

---

## Localization — **CONFIRMED**

`<lang>.lproj/Localizable.strings` is an **Apple binary plist**, not a text
`.strings` file. Parse with `plistlib`. Keys are numeric strings; values are
UI text.

Structural indices established:

- stage titles: index `385 + 8n`, n = 0..19
- objective strings: a contiguous block interleaved with font names

Languages: English, Japanese, French, German, Italian, Spanish.

---

## Mach-O notes — **CONFIRMED**

Thin ARMv6 `MH_EXECUTE`, 26 load commands, 15 linked dylibs, no embedded
frameworks.

Two things that will cost you time if missed:

**`cryptid=0`.** Not FairPlay encrypted. Check this first on any IPA — if it
is non-zero the `__TEXT` segment is encrypted and this approach does not
apply.

**Segment file sizes are not vm sizes.** `__DATA` has `vmsize 0x20000` but
`filesize 0xd000`, because `__common` and `__bss` are zero-fill with no file
backing. Any address ≥ `0x75784` has no file offset. Mapping naively from
vmsize points every global and static into `__LINKEDIT` and yields silent
garbage. `tools/macho.py` parses real load commands and returns `None` for
unmapped addresses.

**ARM vs Thumb.** 1388 Thumb functions, 7 ARM. The flag is
`N_ARM_THUMB_DEF (0x0008)` in each symbol's `n_desc` — **not** the address low
bit, which is clean in this symbol table (unlike the Objective-C method-list
IMP fields, where it is set). Seed Ghidra's `TMode` for every function *before*
analysis; see `tools/ghidra/ApplyMgstSymbols.java` for why it must be a
separate pass from disassembly.
