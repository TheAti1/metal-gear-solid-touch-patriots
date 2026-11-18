"""Validate JSON/font protection, Unicode round trips and the installed REX contract."""
from pathlib import Path
import importlib.util
import json
import plistlib
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / "outputs/Metal_Gear_Solid_Touch_Localization"
REX = Path(os.environ.get('REX_HOME',str(Path.home()/'Desktop/Patriots/REX')))
sys.path.insert(0, str(REX / "Tool Dosyaları"))
from file_processor import FileProcessor
import localization_tool

plugin_file = REX / "Eklentiler/Metal_Gear_Solid_Touch.py"
plugin_file.write_bytes((HERE / plugin_file.name).read_bytes())
fp = FileProcessor(str(REX), str(REX / "Eklentiler"))
plugin = fp.load_plugin_module(str(plugin_file))
path = OUT / "metal_gear_solid_touch_english.json"
original = path.read_text(encoding="utf-8")
extracted = plugin.extract_translatable_texts(original, str(path))
assert len(extracted) == 497, len(extracted)
assert all("\n" not in text and "\r" not in text for text, meta in extracted.values())
assert plugin.rebuild_content_with_translations(original, {k:v[0] for k,v in extracted.items()}, str(path)) == original
sample = "ÇçĞğİıÖöŞşÜü Iı İi\nİkinci satır"
translated = plugin.rebuild_content_with_translations(original, {"entries.1":sample.replace("\n", "|")}, str(path))
data = json.loads(translated)
assert next(r for r in data["entries"] if r["id"] == "1")["text"] == sample
assert all(a == b for a,b in zip(json.loads(original)["entries"],data["entries"]) if a["id"] != "1")
temp = OUT / "unicode_validation.json"
temp.write_text(translated,encoding="utf-8")
localization_tool.import_json(temp,localization_tool.APP,OUT / "validation_overlay")
plist = plistlib.loads((OUT / "validation_overlay/Turkish.lproj/Localizable.strings").read_bytes())
assert plist["1"] == sample
temp.unlink()
test_path = path.with_name("T_" + path.name)
try:
    ok, message = fp.test_plugin_health(str(path), lambda level,text: print("["+level+"]",text),custom_plugin=plugin)
    assert ok, message
    checked = json.loads(test_path.read_text(encoding="utf-8-sig"))
    assert sum(row["text"].startswith("[T]") for row in checked["entries"]) == 445
    assert all(a == b for a,b in zip(json.loads(original)["entries"],checked["entries"]) if a["kind"] == "font")
finally:
    if test_path.exists():
        test_path.unlink()
(OUT / "validation_result.json").write_text(json.dumps({"passed":True,"rex_health":True,"extracted_blocks":len(extracted),"unicode_roundtrip":True,"font_entries_protected":445},indent=2),encoding="utf-8")
print("Localization and live REX integration passed")
