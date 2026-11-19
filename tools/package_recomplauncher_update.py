"""Package only Touch's RecompLauncher adapter; requires a full prepared PC install.

This archive is an update, not a standalone build or an automatic-install asset.
No original assets, native executable, personal save or user preferences enter it.
"""
from pathlib import Path
import argparse
import hashlib
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def package(source, output, version, include_source=False):
    if not (source / 'Metal Gear Solid Touch.exe').is_file():
        raise FileNotFoundError('Build the Patriots launcher first')
    output.mkdir(parents=True, exist_ok=True)
    # SDK source bundles are auxiliary assets, not automatic-install candidates.
    name = 'MGS_Touch_RecompLauncher_SDK_source_Windows_x64.zip' if include_source else f'MGS_Touch_RecompLauncher_{version}_Windows_x64_Update.zip'
    target = output / name
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.write(source / 'Metal Gear Solid Touch.exe', 'Metal Gear Solid Touch.exe')
        archive.write(ROOT / 'recomplauncher.json', 'recomplauncher.json')
        for name in ('RECOMPLAUNCHER.md', 'RECOMPLAUNCHER-REPORT.md'):
            archive.write(ROOT / 'docs' / name, 'Validation/' + name)
        archive.write(ROOT / 'LICENSE', 'Validation/RecompLauncher-adapter-LICENSE.txt')
        if include_source:
            commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
            source_zip = subprocess.check_output(['git', '-C', str(ROOT), 'archive', '--format=zip', '--prefix=touch-launcher-source/', 'HEAD', 'launcher', 'localization', 'assets', 'licenses', 'LICENSE', 'NOTICE.md'])
            archive.writestr('Source/Touch-launcher-source.zip', source_zip)
            archive.writestr('Source/commit.txt', commit + '\n')
        archive.writestr('RECOMPLAUNCHER-UPDATE.txt', 'MGS Touch RecompLauncher support update\n\nExtract over a complete prepared Patriots Touch PC package (v1.1.0).\nThis update contains no game data and is not a standalone automatic install.\nIn RecompLauncher enable Developer tools, choose Add a build and select that complete folder.\nThe original Patriots launcher continues to work without arguments.\nSee Validation/RECOMPLAUNCHER.md and RECOMPLAUNCHER-REPORT.md.\n')
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(digest + '  ' + target.name + '\n', encoding='ascii')
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=ROOT / 'dist')
    parser.add_argument('--version', default='support-1')
    parser.add_argument('--with-source', action='store_true', help='Auxiliary SDK source bundle, excluded from automatic game-asset selection')
    args = parser.parse_args()
    print(package(args.package, args.out, args.version, args.with_source))


if __name__ == '__main__':
    main()
