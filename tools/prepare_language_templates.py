"""Generate separate, stable Touch launcher/game templates from the shipped source.

Never overwrites a filled translation. The older frozen Turkish catalogue remains
untouched; binary game assets are not needed and are not added to the repository.
"""
from pathlib import Path
import copy
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
STRING = r'("(?:[^"\\]|\\.)*")'


def tokens(value):
    return sorted(re.findall(r'\{[^{}]+\}|%(?:\d+\$)?[-+#0 .\d]*(?:@|[sdifuoxX])|%%', value))


def key(source, prefix):
    return prefix + hashlib.sha256(source.encode()).hexdigest()[:20]


def generate():
    ui = {}
    for path in sorted((ROOT / 'launcher').glob('*.cs')):
        if path.name in ('TouchLanguageChecks.cs', 'DiscordProtocolTest.cs'):
            continue
        source = path.read_text(encoding='utf-8-sig')
        for tr, en in re.findall(r'\bL\(' + STRING + r'\s*,\s*' + STRING, source):
            ui.setdefault(json.loads(en), json.loads(tr))
        if path.name == 'TouchLocale.cs':
            for tr, en in re.findall(r'\{' + STRING + r'\s*,\s*' + STRING + r'\}', source):
                ui.setdefault(json.loads(en), json.loads(tr))
        for message in re.findall(r'throw new \w+Exception\(' + STRING, source):
            ui.setdefault(json.loads(message), json.loads(message))
        for tag in re.findall(r'Heading\("([^"]+)"', source):
            ui.setdefault(tag, tag)
    for fixed in ('05 / LOCALIZATION', 'TACTICAL TOUCH ACTION', '01 / PATRIOTS PC EDITION'):
        ui.setdefault(fixed, fixed)
    metadata = dict(template_version=1, source_sha256='', language='en', native_name='English', culture='en-US', author='', instructions=[
        'Translate every text field using source as the English reference. All entries in these two files are translatable.',
        'Preserve id, source, record_id, category and required_tokens. Keep placeholders, format specifiers and intentional line breaks.',
        'Copy unchanged names into text. Empty text falls back to English. Language metadata is preset in the pt-BR files; you may add your credit to author.'
    ])

    def entry(id_, source, category, record=''):
        return dict(id=id_, source=source, text='', category=category, record_id=record, required_tokens=tokens(source))

    launcher = dict(metadata, format='mgs-touch-launcher-language-v1', entries=[entry(key(en, 'ui_'), en, 'launcher') for en in sorted(ui)])
    original = json.loads((ROOT / 'localization/metal_gear_solid_touch_english.json').read_text(encoding='utf-8-sig'))
    rows = []
    for group, category in [('entries', 'game_localization'), ('constants', 'constant')]:
        rows.extend(entry(r['id'], r['source'], category, r['id']) for r in original[group] if r.get('translatable'))
    native = (ROOT / 'runtime/windows/main.c').read_text(encoding='utf-8')
    runtime = {}
    for tr, en in re.findall(r'pc_text\(' + STRING + r'\s*,\s*' + STRING, native):
        runtime.setdefault(json.loads(en), json.loads(tr))
    block = native[native.index('const char *pc_runtime_text'):native.index('static const char *pc_text')]
    for en, tr in re.findall(r'\{' + STRING + r'\s*,\s*' + STRING + r'\}', block):
        runtime.setdefault(json.loads(en), json.loads(tr))
    discord = (ROOT / 'launcher/DiscordPresence.cs').read_text(encoding='utf-8')
    for tr, en in re.findall(r'GameL\(' + STRING + r'\s*,\s*' + STRING, discord):
        runtime.setdefault(json.loads(en), json.loads(tr))
    for fixed in ('GAMEPAD', 'Button'):
        runtime.setdefault(fixed, fixed)
    rows.extend(entry(key(en, 'runtime_'), en, 'runtime') for en in sorted(runtime))
    rows.append(entry('hud_life', 'LIFE', 'hud'))
    game = dict(metadata, format='mgs-touch-game-language-v1', source_sha256=original['source_sha256'], entries=rows)
    return launcher, game, ui


def write(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        previous = json.loads(path.read_text(encoding='utf-8-sig'))
        if any(row.get('text') for row in previous.get('entries', [])):
            raise RuntimeError(f'Refusing to overwrite translated text: {path}')
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    launcher, game, ui = generate()
    for component, doc in [('launcher', launcher), ('game', game)]:
        write(ROOT / f'localization/{component}/{component}.en.json', doc)
        draft = copy.deepcopy(doc)
        draft.update(language='pt-BR', native_name='Português (Brasil)', culture='pt-BR')
        write(ROOT / f'localization/{component}/pt-BR.{component}.json', draft)
    write(ROOT / 'launcher/launcher.en.json', launcher)
    (ROOT / 'launcher/launcher.tr.reference.json').write_text(json.dumps(ui, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Launcher: {len(launcher["entries"])}; game: {len(game["entries"])}')
