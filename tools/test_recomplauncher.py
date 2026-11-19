"""Validate the SDK schema, settings contract and safe update packaging."""
from pathlib import Path
import argparse
import json
import tempfile
import zipfile
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--schema', type=Path)
    args = parser.parse_args()
    # Exact 2026-11-19 SDK snapshot, compared with both the guide's embedded
    # schema and the published URL. No website/bot-policy dependency in CI.
    schema = json.loads((args.schema or ROOT / 'tools/recomplauncher.schema.json').read_text(encoding='utf-8'))
    profile = json.loads((ROOT / 'recomplauncher.json').read_text(encoding='utf-8'))
    Draft7Validator.check_schema(schema)
    Draft7Validator(schema).validate(profile)
    assert profile['repo'] == 'TheAti1/metal-gear-solid-touch-patriots'
    assert profile['start'] == {'program': ['Metal Gear Solid Touch.exe'], 'args': ['--recomplauncher']}
    assert not any(key in profile for key in ('game', 'prepare', 'inputs')), 'Prepared-package profile must not invent an input/setup/dump claim'
    assert profile['config'][0]['file'] == [{'path': '{install}/settings.json'}]
    assert not any(c.get('always') or c.get('new') or c.get('ensure') for c in profile['config']), 'Retain user preferences and game defaults'
    ids = [s['id'] for s in profile['settings']]
    assert len(ids) == len(set(ids)) == 19
    paths = set()
    for row in profile['settings']:
        for choice in row.get('choices', []):
            for key, raw in choice['set'].items():
                json.loads(raw)  # JSON strings must be quoted; booleans/numbers stay typed.
                paths.add(key)
        for raw in row.get('defaults', {}).values():
            json.loads(raw)
        if 'slider' in row:
            slider = row['slider']
            assert slider['min'] <= slider['max'] and slider['step'] > 0
        if 'bindings' in row:
            assert row['bindings']['max'] == 1 and len(row['bindings']['actions']) == 12
            assert all(a['key'].startswith('Keys/') and not a.get('pad') for a in row['bindings']['actions'])
    assert 'DirectPlay' not in paths, 'External launch must not change ordinary launcher behavior'
    assert profile['saves'] == ['{install}/Saves/SAVE*.data', '{install}/settings.json', '{install}/Oyun/desktop.ini', '{install}/Saves/retouched.cfg']
    assert profile['looks']['graphics'] == 'opengl'
    # The public update packager must include only integration files, never game
    # assets, mutable config files or a developer save, even if they are present.
    from package_recomplauncher_update import package
    with tempfile.TemporaryDirectory(prefix='touch-profile-') as temp:
        source, output = Path(temp) / 'package', Path(temp) / 'out'
        (source / 'Oyun/Assets').mkdir(parents=True)
        (source / 'Saves').mkdir()
        (source / 'Metal Gear Solid Touch.exe').write_bytes(b'launcher fixture')
        (source / 'settings.json').write_text('{}')
        (source / 'Saves/SAVE.data').write_bytes(b'private save')
        (source / 'Oyun/Assets/never-ship.bin').write_bytes(b'game data fixture')
        artifact = package(source, output, 'test')
        with zipfile.ZipFile(artifact) as archive:
            names = set(archive.namelist())
            assert 'recomplauncher.json' in names and 'Metal Gear Solid Touch.exe' in names
            assert not any(name.startswith(('Saves/', 'Oyun/')) or name == 'settings.json' for name in names)
    print('PASS: official SDK schema, 19 settings, typed JSON, 12 bindings and asset/save-free update packaging')


if __name__ == '__main__':
    main()
