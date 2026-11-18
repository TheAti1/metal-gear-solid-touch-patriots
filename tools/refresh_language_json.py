"""Carry completed Touch translations into the current matching JSON template."""
from pathlib import Path
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--template', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    old = json.loads(args.input.read_text(encoding='utf-8-sig'))
    kind = {'mgs-touch-launcher-language-v1': 'launcher', 'mgs-touch-game-language-v1': 'game'}.get(old.get('format'))
    if not kind:
        parser.error('Use a modern Touch launcher/game language JSON')
    template = args.template or Path(__file__).resolve().parents[1] / f'localization/{kind}/{kind}.en.json'
    new = json.loads(template.read_text(encoding='utf-8-sig'))
    if old['format'] != new['format'] or old['source_sha256'] != new['source_sha256']:
        parser.error('Template type or source version mismatch')
    existing = {r['id']: r for r in old['entries']}
    canonical = {r['id']: r for r in new['entries']}
    if len(existing) != len(old['entries']):
        parser.error('Duplicate translated IDs')
    for key, row in existing.items():
        if key not in canonical or {k: v for k, v in row.items() if k != 'text'} != {k: v for k, v in canonical[key].items() if k != 'text'}:
            parser.error(f'Protected source/metadata changed for {key}')
    for field in ('language', 'native_name', 'culture', 'author'):
        new[field] = old.get(field, new[field])
    for row in new['entries']:
        if row['id'] in existing:
            row['text'] = existing[row['id']]['text']
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(new, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Preserved {sum(bool(r["text"]) for r in new["entries"])} translated entries; {len(canonical.keys() - existing.keys())} new entries.')


if __name__ == '__main__':
    main()
