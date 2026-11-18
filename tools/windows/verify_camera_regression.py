"""Check the original game's live sight movement after large relative input."""
from pathlib import Path
import json
import math
import re

base=Path(r"D:\Patriots_MGS_Touch_PC\QA")
log=(base/"camera-regression.log").read_text(encoding="utf-8",errors="replace")
pattern=r"PC probe (\w+): scene=(\d+) mission=(\d+) active=(\d+) sight=\(([-\d.]+),([-\d.]+)\) previous=\(([-\d.]+),([-\d.]+)\)"
rows={m[0]:{"scene":int(m[1]),"mission":int(m[2]),"active":int(m[3]),"sight":[float(m[4]),float(m[5])],"previous":[float(m[6]),float(m[7])]} for m in re.findall(pattern,log)}
assert "Game closed; result=0" in log and "TRAP" not in log
for label in ("baseline","negative_edge","reverse_negative","positive_edge","reverse_positive","after_cover","after_resume","svd_edge","svd_reverse","after_weapon"):
    r=rows[label]
    assert r["scene"]==8 and r["active"]==1,(label,r)
    assert all(math.isfinite(v) and 0<=v<=480 for v in r["sight"]+r["previous"]),(label,r)
for first,second,direction in (("negative_edge","reverse_negative",1),("positive_edge","reverse_positive",-1),("svd_edge","svd_reverse",-1)):
    a,b=rows[first]["sight"],rows[second]["sight"]
    assert direction*(b[0]-a[0])>1 and direction*(a[1]-b[1])>1,(first,second,a,b)
assert rows["paused"]["active"]==0
assert "Game window icons installed: large and small" in log
assert "Patriots website: https://www.patriotsceviri.com.tr/" in log
report={"passed":True,"mission":rows["baseline"]["mission"],"large_input_both_directions":True,"reversed_after_extreme_input":True,"after_cover_pause_and_weapon_switch":True,"native_icons":True,"patriots_url_route":True,"probes":rows}
(base/"camera_regression_result.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k!="probes"}))
