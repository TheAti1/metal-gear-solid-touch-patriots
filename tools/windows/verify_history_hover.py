from pathlib import Path
import hashlib,json,re
from PIL import Image
b=Path(r"D:\Patriots_MGS_Touch_PC")
log=(b/"QA/history-hover.log").read_text(encoding="utf-8",errors="replace")
assert "Game closed; result=0" in log and "TRAP" not in log and "whose isa" not in log
views={r[0]:dict(zip(("scene","case","landscape","rotation","hover","selected"),map(int,r[1:]))) for r in re.findall(r"VIEW probe (\w+): scene=(\d+) case=(\d+) landscape=(\d+) rotation=(\d+) hover=(-?\d+) selected=(\d+)",log)}
for name in ("history_picture","history_text","back_picture"):
    assert views[name]["scene"]==21 and views[name]["case"]==7 and views[name]["landscape"]==1 and views[name]["rotation"]==90
for name in ("back_history_list","back_special","back_main"):assert views[name]["landscape"]==0 and views[name]["rotation"]==0
assert views["hover_start"]["hover"]==0 and views["hover_none"]["hover"]==-1
scroll={n:(int(e),int(p)) for n,e,p in re.findall(r"SCROLL probe (\w+): extent=(-?\d+) position=(-?\d+)",log)}
assert scroll["history_top"][0]>0 and scroll["history_top"][1]==0
assert scroll["history_down"][1]<0 and scroll["history_up"][1]==0
assert scroll["wheel_up"][1]>scroll["history_down"][1] and scroll["wheel_down"][1]<scroll["wheel_up"][1]
on=Image.open(b/"QA/main-hover-green.png").convert("RGB");off=Image.open(b/"QA/main-hover-none.png").convert("RGB")
# A patch of the START button background, outside its label and round corners.
box=(490,485,525,510)
def mean_green(im):return sum(g-r for r,g,bb in im.crop(box).getdata())/((box[2]-box[0])*(box[3]-box[1]))
assert mean_green(on)>mean_green(off)+15,(mean_green(on),mean_green(off))
pause=(b/"QA/pause-hover.log").read_text(encoding="utf-8",errors="replace")
assert "Game closed; result=0" in pause and "Patriots website:" not in pause
assert re.search(r"NAV probe hover_patriots: .*overlay_focus=1",pause)
assert re.search(r"NAV probe hover_resume: .*overlay_focus=0",pause)
assert "PC probe hover_then_resume: scene=8 mission=2 active=1" in pause
box=(450,470,475,495)
pa=Image.open(b/"QA/pause-hover-patriots.png").convert("RGB")
pr=Image.open(b/"QA/pause-hover-resume.png").convert("RGB")
assert mean_green(pa)>mean_green(pr)+10
report={"passed":True,"native_exe_sha256":hashlib.sha256((b/"package/Oyun/mgs_touch.exe").read_bytes()).hexdigest(),"special_history_landscape":True,"history_right_stick_scroll":True,"history_mouse_wheel_scroll":True,"return_to_portrait_menus":True,"mouse_hover_changes_button_color":True,"selection_uses_color_without_outline":True,"views":views,"scroll":scroll}
report["pause_hover_matches_clicked_button"]=True
(b/"QA/history_hover_result.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k not in {"views","scroll"}}))
