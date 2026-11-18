"""Build the Turkish HUD label from a font, preserving every other atlas pixel."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from extract_visual_assets import decode, APP

ROOT=Path(r"D:\Patriots_MGS_Touch_PC")
OUT=ROOT/"package/Oyun/languages/tr/Turkish.lproj"
OUT.mkdir(parents=True,exist_ok=True)
font=ROOT/"tools/liberation-fonts-ttf-2.1.5/LiberationSans-Bold.ttf"
rows=[]
for filename,k in (("general_0.png",1),("ipd_general_0.png",2)):
    image=decode(APP/"English.lproj"/filename)
    original=np.asarray(image).copy()
    box=(46*k,116*k,100*k,124*k)
    layer=Image.new("RGBA",(54*k,8*k),(0,0,0,0))
    face=ImageFont.truetype(str(font),11*k)
    bbox=face.getbbox("CAN")
    ImageDraw.Draw(layer).text((0,-bbox[1]),"CAN",font=face,fill=(0,0,0,255))
    image.paste(layer,box[:2])
    changed=np.any(original!=np.asarray(image),axis=2)
    mask=np.zeros(changed.shape,dtype=bool);mask[box[1]:box[3],box[0]:box[2]]=True
    assert not np.any(changed & ~mask),"Atlas pixels outside the LIFE text changed"
    image.save(OUT/filename)
    rows.append({"asset":filename,"rect":box,"source":"LIFE","turkish":"CAN","outside_rect_unchanged":True})
(ROOT/"package/Localization/hud_localization.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
print("Turkish CAN HUD atlas generated; all other pixels preserved")
