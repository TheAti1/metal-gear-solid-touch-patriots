"""Check Android-only additions without changing the reviewed contributor files."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
ui=json.loads((root/'localization/launcher/pt-BR.launcher.json').read_text(encoding='utf-8'))
extra=json.loads((root/'localization/android/pt-BR.android.json').read_text(encoding='utf-8'))['strings']
strings=dict(extra);strings.update({e['source']:e['text'] for e in ui['entries'] if e.get('text')})
assert all(isinstance(k,str) and isinstance(v,str) and v for k,v in strings.items())
sources=[]
for p in (root/'android-patriots/java/com/patriots/shared').glob('*.java'):
    for m in re.finditer(r'\bt\("(?:[^"\\]|\\.)*",\s*("(?:[^"\\]|\\.)*")\)',p.read_text(encoding='utf-8')):
        sources.append(json.loads(m[1]))
sources+=['OVERVIEW','GAME']
missing=sorted(set(sources)-strings.keys())
assert not missing,'Untranslated Android launcher text: '+repr(missing)
print(f'PASS: {len(set(sources))} Android launcher/updater PT-BR labels, contributor wording takes priority')
