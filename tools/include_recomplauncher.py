"""Stage the verified profile beside the Windows executable before archiving."""
from pathlib import Path
import argparse
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]


def include(package):
    if not (package / 'Metal Gear Solid Touch.exe').is_file():
        raise FileNotFoundError('Expected the root Patriots Touch launcher')
    profile = json.loads((ROOT / 'recomplauncher.json').read_text(encoding='utf-8'))
    assert profile['repo'] == 'TheAti1/metal-gear-solid-touch-patriots'
    target = package / 'recomplauncher.json'
    shutil.copy2(ROOT / 'recomplauncher.json', target)
    assert target.read_bytes() == (ROOT / 'recomplauncher.json').read_bytes()
    return target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    args = parser.parse_args()
    print(include(args.package))
