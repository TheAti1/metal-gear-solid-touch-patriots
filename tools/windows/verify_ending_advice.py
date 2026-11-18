from pathlib import Path
import hashlib,json,re
b=Path(r'D:\Patriots_MGS_Touch_PC')
log=(b/'QA/ending-advice.log').read_text(encoding='utf-8',errors='replace')
assert 'Game closed; result=0' in log and 'TRAP' not in log
assert re.search(r'VIEW probe ending_advice: scene=13 case=1 landscape=1 rotation=90',log)
assert re.search(r'NAV probe ending_next: kind=2 index=0 count=1 busy=0',log)
assert 'Menu confirm: kind=2 item=0 at=20.0,460.0' in log
assert re.search(r'VIEW probe after_advice: scene=1 case=1 landscape=0 rotation=0',log)
assert 'NAV probe menu_restored: kind=1' in log
report={'passed':True,'native_exe_sha256':hashlib.sha256((b/'package/Oyun/mgs_touch.exe').read_bytes()).hexdigest(),
    'scene_13_landscape':True,'gamepad_next_uses_original_button':True,'original_advice_exit':True,
    'portrait_menu_restored':True,'fixture':'Initialize original GameScene advice at scene 13; no boss win or player save fabricated'}
(b/'QA/ending_advice_result.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
