"""Build verified Windows release ZIPs around a source-built Patriots launcher.

The native runtime and licensed game inputs are carried forward from an exact
published package. They are NOT claimed to have been rebuilt in this workflow.
No game inputs, generated game C, user saves or signing keys enter Git history.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import shutil
import ssl
import subprocess
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.2.1'
BASE_NAME = 'MGS_Touch_Patriots_PC_v1.2.0.zip'
BASE_SHA256 = '1093a5cea12de2c0a9e64f7b4d8620b051ce614edd4f8c5066f5b13d041f4bd5'
BASE_URL = 'https://github.com/TheAti1/metal-gear-solid-touch-patriots/releases/download/v1.2.0/' + BASE_NAME
BASE_PREFIX = 'Metal Gear Solid Touch Patriots PC/'
NATIVE = {
    'Oyun/mgs_touch.exe': '807ce36865ccc7915fbaeca7169df20c433844f1beac82f97c81d86f9b421bba',
    'Oyun/SDL3.dll': '2b4b128d8d510cc2d442693cf848c050d700d43dc667afe9e5fd82b0570d667e',
}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def clean_member(name):
    path = PurePosixPath(name)
    if not name or '\\' in name or ':' in name or path.is_absolute() or '..' in path.parts:
        raise ValueError('Unsafe ZIP path: ' + name)
    return path


def personal(name):
    path = clean_member(name)
    return (path.parts[0].lower() in ('saves', 'qa') or
            path.name.lower() in ('settings.json', 'desktop.ini', 'retouched.cfg', 'save.data',
                                  'patriots_state.json', 'recompsettingsprobe.exe') or
            path.suffix.lower() in ('.log', '.tmp', '.previous'))


def extract_base(archive, target):
    seen = set()
    with zipfile.ZipFile(archive) as source:
        for info in source.infolist():
            clean_member(info.filename)
            if not info.filename.startswith(BASE_PREFIX):
                raise ValueError('Unexpected base root: ' + info.filename)
            name = info.filename[len(BASE_PREFIX):]
            if not name or info.is_dir():
                continue
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError('Symlinks are not release inputs')
            clean_member(name)
            if name.lower() in seen:
                raise ValueError('Duplicate ZIP path: ' + name)
            seen.add(name.lower())
            if personal(name):
                raise ValueError('Personal data in base: ' + name)
            dest = target / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            with source.open(info) as src, dest.open('wb') as dst:
                shutil.copyfileobj(src, dst)


def write_zip(path, folder, update=False):
    # Stable ordering, permissions and timestamps; no random padding or packer.
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as out:
        for source in sorted(p for p in folder.rglob('*') if p.is_file()):
            name = source.relative_to(folder).as_posix()
            if personal(name):
                raise ValueError('Personal data in release: ' + name)
            if update and name.startswith('Oyun/Assets/') and name != 'Oyun/Assets/fonts/DroidSansFallbackFull.ttf':
                continue
            if update and name.startswith('Oyun/languages/tr/'):
                continue
            info = zipfile.ZipInfo(name, (2026, 11, 21, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            with source.open('rb') as src, out.open(info, 'w') as dst:
                shutil.copyfileobj(src, dst)
    with zipfile.ZipFile(path) as check:
        if check.testzip() is not None:
            raise ValueError('ZIP CRC check failed')
        assert 'recomplauncher.json' in check.namelist()
        assert 'Metal Gear Solid Touch.exe' in check.namelist()


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def package(base, launcher, out, stage):
    if sha(base) != BASE_SHA256:
        raise ValueError('Published 1.2.0 base SHA256 mismatch')
    if stage.exists() or out.exists():
        raise ValueError('Use new, empty stage and output paths')
    stage.mkdir(parents=True)
    out.mkdir(parents=True)
    extract_base(base, stage)
    for name, digest in NATIVE.items():
        if sha(stage / name) != digest:
            raise ValueError('Unexpected native binary: ' + name)
    if not (launcher / 'Metal Gear Solid Touch.exe').is_file():
        raise FileNotFoundError('Build the launcher first')
    shutil.copy2(launcher / 'Metal Gear Solid Touch.exe', stage / 'Metal Gear Solid Touch.exe')
    shutil.copytree(launcher / 'Arayuz', stage / 'Arayuz', dirs_exist_ok=True)
    shutil.copy2(ROOT / 'recomplauncher.json', stage / 'recomplauncher.json')
    commit = git('rev-parse', 'HEAD').decode().strip()
    receipt = {
        'version': VERSION, 'source_commit': commit,
        'repository': 'https://github.com/TheAti1/metal-gear-solid-touch-patriots',
        'workflow': '.github/workflows/release-pc.yml',
        'workflow_run': ('https://github.com/' + os.environ['GITHUB_REPOSITORY'] + '/actions/runs/' + os.environ['GITHUB_RUN_ID']) if os.environ.get('GITHUB_RUN_ID') else None,
        'launcher': {'rebuilt_from_source': True, 'compiler': '.NET SDK 9.0.320 Roslyn',
                     'target': '.NET Framework 4.8 / Windows x64', 'deterministic': True,
                     'sha256': sha(stage / 'Metal Gear Solid Touch.exe'),
                     'authenticode': 'unsigned (no code-signing certificate configured)'},
        'carried_forward': {'base_url': BASE_URL, 'base_sha256': BASE_SHA256,
                            'native_binaries': NATIVE, 'native_rebuilt_in_this_workflow': False},
        'limits': ['GitHub build provenance is not an Authenticode signature or an antivirus verdict.',
                   'The prior VBA32 report has not been independently cleared by this build.'],
    }
    scan = ROOT / 'build/defender.json'
    if scan.is_file():
        receipt['launcher_defender_scan'] = json.loads(scan.read_text(encoding='utf-8-sig'))
    text = json.dumps(receipt, indent=2) + '\n'
    (stage / 'BUILD-PROVENANCE.json').write_text(text, encoding='utf-8')
    (out / 'BUILD-PROVENANCE.json').write_text(text, encoding='utf-8')
    for name in ('RELEASE-1.2.1.md', 'WINDOWS-RELEASE-SECURITY.md'):
        shutil.copy2(ROOT / 'docs' / name, stage / 'Validation' / name)
    for name in ('BENI_OKU.txt', 'README-English.txt'):
        p = stage / name
        p.write_text(p.read_text(encoding='utf-8-sig') + '\nPC 1.2.1: source-built deterministic launcher and GitHub Actions provenance.\nSee BUILD-PROVENANCE.json and Validation/WINDOWS-RELEASE-SECURITY.md.\n', encoding='utf-8')
    # Replace the old embedded source archives with this exact source commit.
    for name, paths in (
        ('KaynakKod_Launcher.zip', ['launcher','localization','assets','licenses','LICENSE','NOTICE.md']),
        ('KaynakKod_PC_Araclari.zip', ['tools','runtime','docs','.github','recomplauncher.json','LICENSE','NOTICE.md']),
    ):
        (stage / name).write_bytes(git('archive', '--format=zip', 'HEAD', *paths))
    validation = json.loads((stage / 'Dogrulama.json').read_text(encoding='utf-8'))
    validation['pc_1_2_1'] = receipt
    (stage / 'Dogrulama.json').write_text(json.dumps(validation, indent=2), encoding='utf-8')
    manifest = {p.relative_to(stage).as_posix(): sha(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name != 'dosyalar.sha256.json'}
    (stage / 'dosyalar.sha256.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    artifacts = []
    for suffix, update in (('', False), ('_Guncelleme', True)):
        target = out / ('MGS_Touch_Patriots_PC_v' + VERSION + suffix + '.zip')
        write_zip(target, stage, update)
        artifacts.append(target)
    source = out / ('MGS_Touch_Patriots_Source_v' + VERSION + '.zip')
    source.write_bytes(git('archive', '--format=zip', 'HEAD'))
    artifacts.extend([source, out / 'BUILD-PROVENANCE.json'])
    sums = ''.join(sha(p) + '  ' + p.name + '\n' for p in artifacts)
    (out / 'SHA256SUMS.txt').write_text(sums, encoding='ascii')
    for artifact in artifacts:
        artifact.with_name(artifact.name + '.sha256').write_text(sha(artifact) + '  ' + artifact.name + '\n', encoding='ascii')
    print(json.dumps(receipt, indent=2))
    print(sums)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-zip', type=Path, default=ROOT / 'build' / BASE_NAME)
    parser.add_argument('--launcher', type=Path, default=ROOT / 'package')
    parser.add_argument('--out', type=Path, default=ROOT / 'dist')
    parser.add_argument('--stage', type=Path, default=ROOT / 'build/pc-release')
    args = parser.parse_args()
    if not args.base_zip.is_file():
        args.base_zip.parent.mkdir(parents=True, exist_ok=True)
        try:
            import certifi
            context = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            context = ssl.create_default_context()
        with urllib.request.urlopen(BASE_URL, timeout=180, context=context) as src, args.base_zip.open('wb') as dst:
            shutil.copyfileobj(src, dst)
    package(args.base_zip, args.launcher, args.out, args.stage)


if __name__ == '__main__':
    main()
