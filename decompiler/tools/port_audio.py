#!/usr/bin/env python3
"""Lossless audio for the port (LOG 2026-10-09): every CAF of the app bundle
-> FLAC, bit-exact.

The earlier port workspace used Ogg Vorbis (lossy), so its sound could never
match the original sample for sample. FLAC is lossless and Android decodes it
natively. For each file the decoded PCM of the CAF and of the FLAC are
compared (md5 of s16le samples); any mismatch is an error.

  linear PCM CAFs (192): the FLAC holds exactly the original samples.
  IMA4 CAFs (36, BGM):    the FLAC holds ffmpeg's IMA4 decode. The game plays
                          these through AudioQueue, i.e. Apple's decoder; that
                          the two decoders agree is NOT proven here (to verify
                          against the oracle; the port may instead ship the
                          IMA4 data and decode it with a verified decoder).

  tools/port_audio.py [--src DIR] [--out DIR] [--jobs N]
Output (not committed - derived from copyrighted assets): build/port_assets/audio/
"""
import argparse
import concurrent.futures as cf
import hashlib
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pcm_md5(path):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-"], capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode()[:200])
    return hashlib.md5(p.stdout).hexdigest(), len(p.stdout)


def codec(path):
    return subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                           "stream=codec_name,sample_rate,channels", "-of", "csv=p=0", path],
                          capture_output=True, text=True).stdout.strip()


def one(src, out):
    dst = os.path.join(out, os.path.basename(src)[:-4] + ".flac")
    c = codec(src)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:a", "flac", "-compression_level", "8",
                    "-sample_fmt", "s16", dst], check=True)
    a, n = pcm_md5(src)
    b, m = pcm_md5(dst)
    return os.path.basename(src), c, n, a == b and n == m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(ROOT, "work/extracted/Payload/MGSTUS.app"))
    ap.add_argument("--out", default=os.path.join(ROOT, "build/port_assets/audio"))
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    srcs = sorted(os.path.join(a.src, f) for f in os.listdir(a.src) if f.endswith(".caf"))
    bad = 0
    rows = []
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for name, c, n, ok in ex.map(lambda s: one(s, a.out), srcs):
            rows.append((name, c, n, ok))
            bad += not ok
    with open(os.path.join(a.out, "manifest.tsv"), "w") as w:
        w.write("file\tcodec,rate,channels\tpcm_bytes\tbit_exact\n")
        for r in rows:
            w.write("%s\t%s\t%d\t%s\n" % r)
    ima = sum(1 for r in rows if r[1].startswith("adpcm"))
    print("audio: %d files -> FLAC, %d bit-exact mismatches; %d IMA4 (decoder vs Apple's unverified)"
          % (len(rows), bad, ima))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
