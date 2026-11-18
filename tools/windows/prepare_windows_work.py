"""Prepare an isolated, resumable MGS Touch build; leave the supplied IPA intact."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
BUILD = Path(r"D:\Patriots_MGS_Touch_PC")
IPA = Path.home() / "Downloads/MetalGearSolidTouch/Metal Gear Solid Touch.ipa"

for name in ("mgs-decomp", "mgs-retouched"):
    dest = BUILD / name
    if not dest.exists():
        shutil.copytree(ROOT.parents[1] / ("runtime" if name=="mgs-retouched" else "decompiler"), dest)
        print("Copied", name, flush=True)

dest = BUILD / "mgs-decomp/work/extracted"
app = dest / "Payload/MGSTUS.app"
if not (app / "MGSTUS").is_file():
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(IPA) as archive:
        for entry in archive.infolist():
            target = (dest / entry.filename).resolve()
            if not target.is_relative_to(dest.resolve()):
                raise ValueError("Unsafe archive path: " + entry.filename)
        archive.extractall(dest)
    print("Extracted supplied IPA", flush=True)

digest = hashlib.sha256((app / "MGSTUS").read_bytes()).hexdigest()
assert digest == "07ac5db07fb8909a95b23c791d20800237bf14a51de1cec32cd0be8e37773a9c", digest
(BUILD / "build-input.json").write_text(json.dumps({
    "ipa": str(IPA), "app": str(app), "executable_sha256": digest,
    "decomp_commit": "9441736930437cd1c6866463dc5b23f2f6412453",
    "retouched_commit": "d4edb7bc1b2ea3a2ec4114a413cb86f7a5cca7ed",
    "status": "inputs_validated"
}, indent=2), encoding="utf-8")
print("Build inputs verified:", app, flush=True)
