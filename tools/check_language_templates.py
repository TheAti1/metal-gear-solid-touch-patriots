"""Validate Touch template coverage, stable IDs and protected format tokens."""
from pathlib import Path
import json
from prepare_language_templates import generate, tokens

ROOT = Path(__file__).resolve().parents[1]


def main():
    launcher, game, _ = generate()
    for component, expected in [('launcher', launcher), ('game', game)]:
        actual = json.loads((ROOT / f'localization/{component}/{component}.en.json').read_text(encoding='utf-8-sig'))
        assert actual == expected, f'{component} template drift'
        rows = {r['id']: r for r in actual['entries']}
        assert len(rows) == len(actual['entries']), 'Duplicate IDs'
        for row in rows.values():
            assert row['required_tokens'] == tokens(row['source'])
        for file in (ROOT / f'localization/{component}').glob('*.json'):
            doc = json.loads(file.read_text(encoding='utf-8-sig'))
            assert doc['format'] == actual['format'] and doc['source_sha256'] == actual['source_sha256']
            for row in doc['entries']:
                assert {k: v for k, v in row.items() if k != 'text'} == {k: v for k, v in rows[row['id']].items() if k != 'text'}
                if row['text']:
                    assert tokens(row['text']) == row['required_tokens']
        print(f'{component}: {len(rows)} entries, coverage/IDs/tokens PASS')
    assert json.loads((ROOT / 'launcher/launcher.en.json').read_text(encoding='utf-8-sig')) == launcher
    assert (ROOT / 'runtime/windows/main.c').read_bytes() == (ROOT / 'tools/windows/windows_main.c').read_bytes(), 'Native build helper is stale'


if __name__ == '__main__':
    main()
