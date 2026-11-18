from pathlib import Path
import hashlib,json,re
b=Path(r'D:\Patriots_MGS_Touch_PC')
log=(b/'QA/final-boss-dodge.log').read_text(encoding='utf-8',errors='replace')
assert 'Game closed; result=0' in log and 'TRAP' not in log
pattern=r'DODGE probe (\w+): mission=(\d+) active=(\d+) state=(\d+) pose=(\d+) frame=(\d+) protected=(\d+)'
rows={m[0]:dict(zip(('mission','active','state','pose','frame','protected'),map(int,m[1:]))) for m in re.findall(pattern,log)}
# Landscape phone gestures run opposite to screen-relative stick directions.
for label,state,pose in [('left',8,5),('right',7,4),('resumed_right',7,4)]:
    p=rows[label]
    assert p['mission']==20 and p['active']==1 and p['state']==state and p['pose']==pose and p['protected']==1,(label,p)
for label in ('held_after_loading','held_left','held_right','held_after_pause','vertical'):
    p=rows[label]
    assert p['mission']==20 and p['state']==5 and p['protected']==0,(label,p)
assert log.count('Final boss dodge: left')==1
assert log.count('Final boss dodge: right')==2
assert 'NAV probe paused: kind=11' in log
report={'passed':True,'native_exe_sha256':hashlib.sha256((b/'package/Oyun/mgs_touch.exe').read_bytes()).hexdigest(),
    'original_left_and_right_dodge_animations':True,'original_dodge_protection':True,
    'landscape_direction_inversion_corrected':True,
    'held_stick_does_not_repeat':True,'held_stick_after_loading_and_pause_ignored':True,
    'vertical_motion_ignored':True,'mission_20_only_guard_reviewed':True,
    'input_path':'same right-stick handler as physical SDL gamepad; isolated copy of player save',
    'whole_boss_fight_played':False,'probes':rows}
(b/'QA/final_boss_dodge_result.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
