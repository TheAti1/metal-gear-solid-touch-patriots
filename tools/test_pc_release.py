"""Adversarial packaging checks: traversal, saves and stable release ZIPs."""
import hashlib
from pathlib import Path
import tempfile
import zipfile
from package_pc_release import clean_member, personal, extract_base, write_zip, BASE_PREFIX

for bad in ('../escape', '/absolute', 'C:/drive', 'folder\\escape', 'a/../../escape'):
    try:
        clean_member(bad)
    except ValueError:
        pass
    else:
        raise AssertionError('Accepted path: ' + bad)
for name in ('Saves/SAVE.data', 'settings.json', 'Oyun/desktop.ini', 'QA/report.json', 'Saves/Backups/private.data'):
    assert personal(name), name
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    malicious = root / 'input.zip'
    with zipfile.ZipFile(malicious, 'w') as z:
        z.writestr(BASE_PREFIX + '../escape', b'bad')
    try:
        extract_base(malicious, root / 'extract')
    except ValueError:
        pass
    else:
        raise AssertionError('Traversal base accepted')
    stage = root / 'stage'
    (stage / 'Oyun/Assets').mkdir(parents=True)
    (stage / 'recomplauncher.json').write_text('{}')
    (stage / 'Metal Gear Solid Touch.exe').write_bytes(b'launcher fixture')
    (stage / 'Oyun/Assets/unchanged.dat').write_bytes(b'game fixture')
    write_zip(root / 'a.zip', stage)
    write_zip(root / 'b.zip', stage)
    assert hashlib.sha256((root / 'a.zip').read_bytes()).digest() == hashlib.sha256((root / 'b.zip').read_bytes()).digest()
    write_zip(root / 'update.zip', stage, True)
    with zipfile.ZipFile(root / 'update.zip') as z:
        assert 'Oyun/Assets/unchanged.dat' not in z.namelist()
    (stage / 'settings.json').write_text('{"private":true}')
    try:
        write_zip(root / 'bad.zip', stage)
    except ValueError:
        pass
    else:
        raise AssertionError('Packaged private settings')
print('PASS: unsafe ZIP paths and personal files rejected; deterministic full/update packaging')
