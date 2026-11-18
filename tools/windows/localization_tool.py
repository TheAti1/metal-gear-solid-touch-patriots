"""Lossless English JSON extraction and Turkish binary-plist overlay creation."""
from pathlib import Path
import argparse
import hashlib
import json
import plistlib
import re
import struct
import sys

APP = Path(r"D:\Patriots_MGS_Touch_PC\mgs-decomp\work\extracted\Payload\MGSTUS.app")
OUT = Path(__file__).resolve().parents[2] / "outputs/Metal_Gear_Solid_Touch_Localization"
FONTS = {"Helvetica", "Helvetica-Bold", "HiraKakuProN-W3", "HiraKakuProN-W6", "Arial", "Arial-BoldMT"}

def load_source(app):
    return plistlib.loads((app / "English.lproj/Localizable.strings").read_bytes())

def cfstrings(app):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "decompiler/tools"))
    from macho import MachO
    image = MachO(str(app / "MGSTUS"))
    sec = image.section("__DATA", "__cfstring")
    if not sec:
        return []
    raw = (app / "MGSTUS").read_bytes()
    rows = []
    for offset in range(sec[4], sec[4] + sec[3], 16):
        isa, flags, ptr, length = struct.unpack_from("<IIII", raw, offset)
        try:
            fileoff = image.off(ptr)
        except (ValueError, KeyError, AttributeError):
            continue
        if fileoff is None or not (0 < length < 16384):
            continue
        wide = bool(flags & 0x10)
        value = raw[fileoff:fileoff + length * (2 if wide else 1)].decode("utf-16-le" if wide else "utf-8", errors="replace")
        if re.search(r"[A-Za-z]{2}", value):
            visible = bool(re.search(r"[A-Za-z]+[ .!?][A-Za-z .!?]", value)) and not re.search(r"[/\\]|\.(png|data|caf|rl|al|csv)$", value)
            rows.append({"id": "cf_" + format(sec[2] + offset - sec[4], "08x"),
                         "source": value, "text": value, "translatable": visible,
                         "kind": "constant", "address": format(sec[2] + offset - sec[4], "08x")})
    return rows

def export(app, out):
    source = load_source(app)
    rows = []
    font_counts = {}
    for key in sorted(source, key=lambda x: int(x) if x.isdecimal() else 100000):
        value = source[key]
        isfont = value in FONTS or bool(re.fullmatch(r"(?:Helvetica|HiraKakuProN|Arial|Courier|Times)[A-Za-z0-9_-]*", value))
        if isfont:
            font_counts[value] = font_counts.get(value, 0) + 1
        rows.append({"id": key, "source": value, "text": value,
                     "translatable": not isfont and bool(value.strip()),
                     "kind": "font" if isfont else "localized"})
    constants = cfstrings(app)
    images = []
    for path in sorted((app / "English.lproj").glob("*.png")):
        images.append({"path": str(path.relative_to(app)).replace("\\", "/"),
                       "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                       "status": "image_requires_visual_localization"})
    data = {"format": "patriots.mgs-touch.localization.v1", "game": "Metal Gear Solid Touch",
            "version": "2.3.0", "source_language": "en", "target_language": "tr",
            "instructions": "Edit only text values. Keep IDs, source, font entries and placeholders unchanged. Original English has not been translated.",
            "source_sha256": hashlib.sha256((app / "English.lproj/Localizable.strings").read_bytes()).hexdigest(),
            "entries": rows, "constants": constants, "image_text_assets": images,
            "fonts": font_counts}
    out.mkdir(parents=True, exist_ok=True)
    target = out / "metal_gear_solid_touch_english.json"
    if (out / "catalogue_frozen.json").exists() and target.exists():
        raise FileExistsError("This catalogue was delivered for translation; export to a new folder instead of replacing it.")
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "localization_inventory.json").write_text(json.dumps({
        "localized_records": len(rows), "editable_localized_records": sum(r["translatable"] for r in rows),
        "constant_records": len(constants), "constant_text_candidates": sum(r["translatable"] for r in constants),
        "image_text_assets": len(images), "fonts": font_counts}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(target)
    print("Localized records:", len(rows), "editable:", sum(r["translatable"] for r in rows), "constant records:", len(constants))
    return data

def import_json(path, app, dest):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    assert data["format"] == "patriots.mgs-touch.localization.v1", "Wrong JSON format"
    source = load_source(app)
    digest = hashlib.sha256((app / "English.lproj/Localizable.strings").read_bytes()).hexdigest()
    assert data["source_sha256"] == digest, "Source version mismatch"
    seen = set()
    for row in data["entries"]:
        key = row["id"]
        assert key in source and key not in seen, "Unknown or duplicate ID: " + key
        assert row["source"] == source[key], "Original source changed: " + key
        seen.add(key)
        if row["kind"] == "font":
            assert row["text"] == source[key], "Font name changed: " + key
        else:
            assert isinstance(row["text"], str) and "\0" not in row["text"], "Invalid text: " + key
            source[key] = row["text"]
    assert seen == set(source), "Missing records"
    target = dest / "Turkish.lproj/Localizable.strings"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(plistlib.dumps(source, fmt=plistlib.FMT_BINARY, sort_keys=False))
    assert plistlib.loads(target.read_bytes()) == source
    # Runtime constants are separate from bplist strings; the desktop text bridge loads this table.
    changed = [{"source": r["source"], "text": r["text"]} for r in data.get("constants", [])
               if r.get("translatable") and r["text"] != r["source"]]
    (dest / "runtime_text_overrides.json").write_text(json.dumps(changed, ensure_ascii=False, indent=2), encoding="utf-8")
    encoded = bytearray(b"PTXT0001") + struct.pack(">I", len(changed))
    for row in changed:
        for field in ("source", "text"):
            raw = row[field].encode("utf-8")
            encoded.extend(struct.pack(">I", len(raw)))
            encoded.extend(raw)
    (dest / "runtime_text.bin").write_bytes(encoded)
    print("Verified overlay:", target, "changed entries:", sum(r["source"] != r["text"] for r in data["entries"]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["export", "import"])
    parser.add_argument("json", nargs="?", type=Path)
    parser.add_argument("--app", type=Path, default=APP)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    if args.command == "export":
        export(args.app, args.out)
    else:
        assert args.json, "Supply the translated JSON"
        import_json(args.json, args.app, args.out)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
