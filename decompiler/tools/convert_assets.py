#!/usr/bin/env python3
"""Build the Android asset tree from the extracted MGSTUS bundle.

Two rules drive this:

1. Preserve the original basenames. The engine looks resources up by name
   (TextureManager getTexture:/loadTexture:name:ofType:, and the sound IDs in
   GSoundCtrl), so keeping "wp301" -> wp301.png intact means the ported
   lookup code stays identical to the original. Only extensions change.

2. Only audio is re-encoded, because Android cannot play .caf natively. The
   228 files are NOT uniform: 193 SFX are raw pcm_s16le (15 MiB total) but
   the 35 music tracks are already IMA4 ADPCM (94 MiB, i.e. 86% of the audio
   bytes). That split drives the quality setting below — re-encoding an
   already-lossy source compounds artefacts, so music gets more bitrate than
   its size alone would suggest.

3. PNGs are de-CgBI'd. Most of the bundle's PNGs are Apple "iPhone-optimized"
   (byte-swapped BGRA, premultiplied alpha, raw deflate). Standard decoders
   read the header fine and report correct dimensions, then produce garbage
   pixels — which on Android showed up as a black screen with a
   successful-looking texture-load log. See tools/decgbi.py.

   The .data/.al/.rl tables are still copied byte-for-byte so the recovered
   data stays authoritative.

Usage:
    python3 tools/convert_assets.py [--jobs N] [--dry-run]
"""
import argparse
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import decgbi  # noqa: E402  (needs the path insert above)

APP = Path("work/extracted/Payload/MGSTUS.app")
OUT = Path("android/app/src/main/assets")

# Quality is chosen by SOURCE CODEC, not by file size. The music tracks are
# already IMA4 ADPCM, so Vorbis is a second lossy generation over them and
# needs headroom to avoid audible compounding; the raw-PCM SFX are a first
# generation and short, so they tolerate a lower setting.
Q_LOSSY_SRC = "6"   # adpcm_ima_qt sources (music) - limit generation loss
Q_PCM_SRC = "3"     # pcm_s16le sources (SFX) - first generation, short

# .png is handled separately (CgBI conversion), not copied verbatim.
COPY_EXTS = {".bmp", ".data", ".al", ".rl", ".strings", ".csv",
             ".plist", ".nib"}


def convert_png(src: Path, dst: Path, dry: bool) -> tuple[str, int, int]:
    """Copy a PNG, de-CgBI'ing it if Apple mangled it on the way in."""
    before = src.stat().st_size
    if dry:
        return (src.name, before, 0)
    dst.parent.mkdir(parents=True, exist_ok=True)
    data = src.read_bytes()
    if decgbi.is_cgbi(data):
        try:
            data = decgbi.convert(data)
        except Exception as e:
            print(f"  CgBI convert failed for {src.name}: {e}", file=sys.stderr)
            return (src.name, before, -1)
    dst.write_bytes(data)
    return (src.name, before, dst.stat().st_size)


def probe_codec(src: Path) -> str:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name",
         "-of", "csv=p=0", str(src)],
        capture_output=True, text=True)
    return r.stdout.strip().split("\n")[0] if r.stdout.strip() else ""


def convert_caf(src: Path, dst: Path, dry: bool) -> tuple[str, int, int]:
    before = src.stat().st_size
    if dry:
        return (src.name, before, 0)
    dst.parent.mkdir(parents=True, exist_ok=True)
    q = Q_LOSSY_SRC if "adpcm" in probe_codec(src) else Q_PCM_SRC
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
         "-c:a", "libvorbis", "-q:a", q, str(dst)],
        capture_output=True, text=True)
    if r.returncode != 0:
        return (src.name, before, -1)
    after = dst.stat().st_size
    if after == 0:
        return (src.name, before, -1)
    return (src.name, before, after)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not APP.is_dir():
        sys.exit(f"missing {APP} — extract the IPA first")

    files = [p for p in APP.rglob("*") if p.is_file()]
    cafs = [p for p in files if p.suffix.lower() == ".caf"]
    pngs = [p for p in files if p.suffix.lower() == ".png"]
    copies = [p for p in files if p.suffix.lower() in COPY_EXTS]
    skipped = [p for p in files
               if p.suffix.lower() not in COPY_EXTS | {".caf", ".png"}]

    n_cgbi = sum(1 for p in pngs if decgbi.is_cgbi(p.read_bytes()))
    print(f"source: {len(files)} files, "
          f"{sum(p.stat().st_size for p in files)/2**20:.1f} MiB")
    print(f"  transcode .caf -> .ogg : {len(cafs)}")
    print(f"  png (of which CgBI)    : {len(pngs)} ({n_cgbi})")
    print(f"  copy verbatim          : {len(copies)}")
    print(f"  skipped                : {len(skipped)}")

    copied_bytes = 0
    for p in copies:
        rel = p.relative_to(APP)
        dst = OUT / rel
        copied_bytes += p.stat().st_size
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)

    png_before = png_after = 0
    png_failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = [ex.submit(convert_png, p, OUT / p.relative_to(APP), args.dry_run)
                for p in pngs]
        for i, f in enumerate(futs, 1):
            name, before, after = f.result()
            png_before += before
            if after < 0:
                png_failures.append(name)
            else:
                png_after += after
            if i % 200 == 0:
                print(f"    png {i}/{len(futs)}")

    audio_before = audio_after = 0
    failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = [ex.submit(convert_caf, p,
                          OUT / p.relative_to(APP).with_suffix(".ogg"),
                          args.dry_run)
                for p in cafs]
        for i, f in enumerate(futs, 1):
            name, before, after = f.result()
            audio_before += before
            if after < 0:
                failures.append(name)
            else:
                audio_after += after
            if i % 40 == 0:
                print(f"    ...{i}/{len(futs)}")

    print("\n--- result ---")
    print(f"copied verbatim : {copied_bytes/2**20:8.1f} MiB")
    if args.dry_run:
        print("png             : (dry run)")
    else:
        print(f"png before      : {png_before/2**20:8.1f} MiB")
        print(f"png after       : {png_after/2**20:8.1f} MiB  "
              f"({n_cgbi} de-CgBI'd)")
        if png_failures:
            print(f"  PNG FAILURES ({len(png_failures)}): {png_failures[:8]}")
    if args.dry_run:
        print("audio           : (dry run, not transcoded)")
    else:
        saved = audio_before - audio_after
        print(f"audio before    : {audio_before/2**20:8.1f} MiB")
        print(f"audio after     : {audio_after/2**20:8.1f} MiB"
              f"   ({saved/2**20:.1f} MiB saved)")
        print(f"TOTAL           : "
              f"{(copied_bytes+audio_after+png_after)/2**20:8.1f} MiB")
    if failures or png_failures:
        print(f"\nFAILED audio ({len(failures)}): {failures[:10]}")
        print(f"FAILED png ({len(png_failures)}): {png_failures[:10]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
