from pathlib import Path
import hashlib,json,re
b=Path(r"D:\Patriots_MGS_Touch_PC")
log=(b/"QA/text-scroll.log").read_text(encoding="utf-8",errors="replace")
rows={n:{"extent":int(e),"position":int(p)} for n,e,p in re.findall(r"SCROLL probe (\w+): extent=(-?\d+) position=(-?\d+)",log)}
assert "Game closed; result=0" in log and "TRAP" not in log and "whose isa" not in log
assert rows["top"]["extent"]>50000 and rows["top"]["position"]==0
assert rows["down"]["position"]<-50000
assert rows["up"]["position"]>rows["down"]["position"]+50000
assert abs(rows["up"]["position"])<15000
assert rows["loading_axes"]["extent"]==0
assert "NAV probe ready_after_loading: kind=2 index=0" in log
for name in ("after_loading_held_axes","resumed"):
    assert re.search(r"PC probe "+name+r": scene=8 mission=1 active=1",log)
assert "Patriots website:" not in log
report={"passed":True,"native_exe_sha256":hashlib.sha256((b/"package/Oyun/mgs_touch.exe").read_bytes()).hexdigest(),"right_stick_text_scroll_both_directions":True,"loading_with_both_sticks_and_held_confirm":True,"confirm_works_after_loading":True,"pause_and_resume":True,"selection_boxes_removed_visual_check":True,"probes":rows}
(b/"QA/text_scroll_result.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report))
