"""Normalize Apple CgBI PNGs for inspection; preserve and inventory the source art."""
from pathlib import Path
import hashlib
import io
import json
import struct
import zlib
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
BASE = Path(r"D:\Patriots_MGS_Touch_PC")
APP = BASE / "mgs-decomp/work/extracted/Payload/MGSTUS.app"
OUT = HERE.parents[1] / "outputs/Metal_Gear_Solid_Touch_Localization"

def chunk(kind, data):
    return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data))

def decode(path):
    data=path.read_bytes()
    if b"CgBI" not in data[:64]:
        return Image.open(io.BytesIO(data)).convert("RGBA")
    pos=8; chunks=[]; compressed=bytearray()
    while pos+12<=len(data):
        n=struct.unpack_from(">I",data,pos)[0];kind=data[pos+4:pos+8];value=data[pos+8:pos+8+n];pos+=12+n
        if kind==b"IDAT":compressed.extend(value)
        elif kind not in (b"CgBI",b"IEND"):chunks.append((kind,value))
    raw=zlib.decompress(compressed,-15)
    normal=b"\x89PNG\r\n\x1a\n"+b"".join(chunk(k,v) for k,v in chunks)+chunk(b"IDAT",zlib.compress(raw))+chunk(b"IEND",b"")
    image=Image.open(io.BytesIO(normal)).convert("RGBA")
    pixels=np.array(image).astype(np.uint32)
    pixels[:,:,[0,2]]=pixels[:,:,[2,0]]
    alpha=pixels[:,:,3:4]
    pixels[:,:,:3]=np.minimum(255,np.where(alpha>0,(pixels[:,:,:3]*255+alpha//2)//np.maximum(alpha,1),0))
    return Image.fromarray(pixels.astype(np.uint8),"RGBA")

def main():
    visuals=OUT / "Visual_Assets"
    visuals.mkdir(parents=True,exist_ok=True)
    candidates=list((APP / "English.lproj").glob("*.png"))
    candidates += [APP/name for name in ("Icon.png","IconPad.png","ipd_mainmenu_bg1.png","ipd_mainmenu_bg2.png","ipd_mainmenu_bg3.png","ipd_mainmenu_logo.png","ipd_mainmenu_logotxt.png")]
    images=[];inventory=[]
    for path in candidates:
        image=decode(path);name=path.relative_to(APP).as_posix().replace("/","__")
        image.save(visuals/name)
        inventory.append({"source":path.relative_to(APP).as_posix(),"png":name,"size":list(image.size),"source_sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
        thumb=image.copy();thumb.thumbnail((280,250))
        tile=Image.new("RGB",(320,290),(34,38,40));tile.paste(thumb,((320-thumb.width)//2,30),thumb)
        ImageDraw.Draw(tile).text((8,8),name,fill="white",font=ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf",12))
        images.append(tile)
    sheet=Image.new("RGB",(1280,290*((len(images)+3)//4)),(18,20,22))
    for i,tile in enumerate(images):sheet.paste(tile,((i%4)*320,(i//4)*290))
    sheet.save(visuals/"contact_sheet.jpg",quality=92)
    (visuals/"inventory.json").write_text(json.dumps(inventory,indent=2),encoding="utf-8")
    glyphs="ÇçĞğİıÖöŞşÜü"
    faces=[BASE/"tools/liberation-fonts-ttf-2.1.5"/name for name in ("LiberationSans-Regular.ttf","LiberationSans-Bold.ttf")]
    faces += [BASE/"mgs-retouched/android-retouched/fonts/BebasNeue-Regular.ttf"]
    rows=[];sheet=Image.new("RGB",(1100,600),(18,22,24));draw=ImageDraw.Draw(sheet)
    for i,path in enumerate(faces):
        cmap=TTFont(path).getBestCmap();missing=[c for c in glyphs if ord(c) not in cmap]
        assert not missing,(path,missing)
        rows.append({"font":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"turkish_characters":glyphs,"missing":missing})
        draw.text((24,20+i*180),path.name,fill=(161,201,105),font=ImageFont.truetype(str(faces[0]),24))
        draw.text((24,64+i*180),"Çç Ğğ İı Öö Şş Üü — Yükleniyor...",fill="white",font=ImageFont.truetype(str(path),36))
        draw.text((24,113+i*180),"İSTANBUL / ığdır / ŞİFRE ÇÖZÜLDÜ / ÖZEL GÖREV",fill="white",font=ImageFont.truetype(str(path),24))
    sheet.save(OUT/"turkish_font_coverage.png")
    (OUT/"font_coverage.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Normalized images:",len(images),"Turkish font coverage passed for",len(rows),"fonts")

if __name__=="__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
