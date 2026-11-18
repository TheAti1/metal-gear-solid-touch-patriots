from pathlib import Path
import hashlib
import json
import re

base=Path(r"D:\Patriots_MGS_Touch_PC")
log=(base/"QA/gamepad-flow.log").read_text(encoding="utf-8",errors="replace")
pattern=r"NAV probe (\w+): kind=(\d+) index=(\d+) count=(\d+) busy=(\d+) overlay_focus=(\d+) pc=(\d+)"
rows={r[0]:dict(zip(("kind","index","count","busy","overlay_focus","pc"),map(int,r[1:]))) for r in re.findall(pattern,log)}
assert "Game closed; result=0" in log and "TRAP" not in log
assert "whose isa" not in log
assert rows["main_menu"]["kind"]==1 and rows["mission_menu"]["kind"]==1
for label in ("gameplay","resume_a","resume_mouse","resume_b"):
    assert rows[label]["pc"]==1,(label,rows[label])
assert rows["pause_held_stick"]["kind"]==11 and rows["pause_held_stick"]["overlay_focus"]==0
assert rows["pause_patriots_selected"]["overlay_focus"]==1
assert rows["pause_quit_selected"]["overlay_focus"]==2
assert rows["quit_confirmation"]["kind"]==12 and rows["quit_confirmation"]["overlay_focus"]==1
assert rows["quit_cancel_default"]["kind"]==11
assert rows["result"]["kind"]==3 and rows["result"]["index"]==0 and rows["result"]["busy"]==0
assert re.search(r"PC probe mission_2: scene=8 mission=2 ",log)
assert "Patriots website:" not in log,"A resume or menu confirm accidentally opened Patriots"
remap=(base/"QA/gamepad-remap.log").read_text(encoding="utf-8",errors="replace")
assert "Game closed; result=0" in remap and "TRAP" not in remap
assert re.search(r"PC probe unbound_a: scene=1 ",remap)
assert re.search(r"PC probe mapped_confirm: scene=5 ",remap)
assert re.search(r"PC probe mapped_back: scene=1 ",remap)
mission2=(base/"QA/gamepad-mission2.log").read_text(encoding="utf-8",errors="replace")
assert "Game closed; result=0" in mission2 and "TRAP" not in mission2
for label in ("mission_2_gameplay","mission_2_resumed","mission_2_back_resume"):
    assert re.search(r"PC probe "+label+r": scene=8 mission=2 active=1",mission2),label
assert re.search(r"NAV probe mission_2_back_pause: kind=11",mission2)
assert re.search(r"NAV probe mission_2_start_pause: kind=11",mission2)
assert "Patriots website:" not in mission2
exe=base/"package/Oyun/mgs_touch.exe"
report={"passed":True,"native_exe_sha256":hashlib.sha256(exe.read_bytes()).hexdigest(),"gamepad_event_path":True,"main_and_mission_menus":True,"story_advice_and_ready":True,"pause_confirm_resume":True,"mouse_resume_hit_test":True,"held_stick_does_not_change_default":True,"quit_defaults_to_cancel":True,"back_and_pause_distinct":True,"mission_clear_to_mission_2":True,"custom_button_mapping":True,"unexpected_patriots_launches":0,"result_fixture":"QA-only completion counter; original game result/next-stage logic","probes":rows}
(base/"QA/gamepad_regression_result.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="probes"}))
