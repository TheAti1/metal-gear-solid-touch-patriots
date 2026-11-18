# -*- coding: utf-8 -*-
"""REX plugin for the lossless Patriots MGS Touch localization JSON."""
from __future__ import annotations
import json
from typing import Any

PLUGIN_NAME = "Metal Gear Solid Touch (Patriots PC)"
SUPPORTED_EXTENSIONS = [".json"]
GAME_CONTEXT_PROMPT = """Metal Gear Solid Touch, Metal Gear Solid 4 olaylarını temel alır.
Old Snake, Otacon, Drebin ve Liquid Ocelot yer alır. Metinler görev açıklamaları,
CODEC konuşmaları, menüler, seri özeti ve oynanış kılavuzundan oluşur.
JSON dosyası özgün iOS 2.3.0 dil tablosunu ve çalıştırılabilir dosyadaki sabit metin adaylarını içerir."""
TRANSLATION_PROMPT = """`|` oyun içindeki alt satıra geçme kodudur; fiziksel Enter değildir.
Metni fiziksel satırlara bölme. `<c1>` gerçek bir dikey çizgi karakteridir.
Varsa %s, %d, %02d gibi printf yer tutucularını ve etiketleri koru.
Yalnızca verilen metinleri işle; JSON anahtarları, kimlikler ve font adları çevrilecek metne dahil edilmez."""
TERM_PROMPT = ""
FORMAT = "patriots.mgs-touch.localization.v1"

def get_file_encoding(filepath: str) -> str:
    return "utf-8-sig"

def _coerce_text(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        value = value[0] if value else ""
    if isinstance(value, dict):
        for key in ("text", "translation", "translated_text", "value"):
            if key in value:
                return _coerce_text(value[key])
        return ""
    return str(value) if value is not None else ""

def _load(content):
    data = json.loads(str(content or "").lstrip("\ufeff"))
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        raise ValueError("Bu eklenti Patriots MGS Touch localization.v1 JSON dosyasını bekliyor.")
    return data

def _rows(data):
    for group in ("entries", "constants"):
        for row in data.get(group, []):
            if (isinstance(row, dict) and row.get("translatable") is True
                    and row.get("kind") != "font" and isinstance(row.get("text"), str)
                    and row["text"].strip()):
                yield group + "." + str(row["id"]), row

def _protect(text):
    return text.replace("|", "<c1>").replace("\r\n", "|").replace("\r", "|").replace("\n", "|")

def _restore(text):
    import re
    return re.sub(r"<c1>", "|", text.replace("\r\n", "\n").replace("\r", "\n").replace("|", "\n"), flags=re.I)

def extract_translatable_texts(content: str, filepath: str, extraction_context: dict | None = None) -> dict:
    data = _load(content)
    return {key: (_protect(row["text"]), {"source": row["source"], "id": row["id"], "kind": row["kind"]})
            for key, row in _rows(data)}

def rebuild_content_with_translations(original_content: str, translations: dict,
                                      filepath: str, rebuild_context: dict | None = None) -> str:
    # Installed REX still calls (content, originals, translated); newer versions pass a path.
    if isinstance(filepath, dict):
        translations = filepath
    data = _load(original_content)
    changed = False
    for key, row in _rows(data):
        if key not in translations:
            continue
        text = _restore(_coerce_text(translations[key]))
        if not text.strip() or isinstance(translations[key], bool):
            continue
        if text == row["source"] and row["text"] != row["source"]:
            continue
        if text != row["text"]:
            row["text"] = text
            changed = True
    if not changed:
        return original_content
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"
