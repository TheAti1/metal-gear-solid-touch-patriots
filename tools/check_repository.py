"""Check source publication boundaries and the frozen bilingual catalogue."""
from pathlib import Path
import json,re,subprocess,sys
root=Path(__file__).resolve().parents[1]
try:
    names=subprocess.check_output(['git','ls-files'],cwd=root,text=True).splitlines()
except subprocess.CalledProcessError:names=[]
paths=[root/n for n in names] if names else [p for p in root.rglob('*') if p.is_file() and '.git' not in p.parts]
for p in paths:
    if not p.is_file():continue
    rel=p.relative_to(root).as_posix()
    assert p.suffix.lower() not in {'.ipa','.sis','.sisx','.rom','.fpsx','.exe','.dll','.wasm','.obj','.pdb'},rel
    assert p.name not in {'SAVE.data','settings.json','retouched.cfg','patriots_state.json'},rel
    if p.suffix.lower() in {'.py','.ps1','.cs','.md','.json','.yml','.yaml','.txt','.c','.h','.inc'}:
        s=p.read_text(encoding='utf-8-sig',errors='replace')
        assert not re.search(r'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',s),rel
en=json.loads((root/'localization/metal_gear_solid_touch_english.json').read_text(encoding='utf-8-sig'))
tr=json.loads((root/'localization/TR_metal_gear_solid_touch_english.json').read_text(encoding='utf-8-sig'))
for group in ('entries','constants'):
    assert len(en[group])==len(tr[group])
    for a,b in zip(en[group],tr[group]):
        assert {k:v for k,v in a.items() if k!='text'}=={k:v for k,v in b.items() if k!='text'},a.get('id')
        if a['kind']=='font':assert a['text']==b['text']
for p in (root/'tools/windows').glob('*.py'):compile(p.read_text(encoding='utf-8'),str(p),'exec')
print('PASS: publication boundaries, frozen translation metadata, font names and Python syntax')
