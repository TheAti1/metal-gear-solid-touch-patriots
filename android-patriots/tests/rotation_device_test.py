"""Exercise a running title/paused screen through actual Android OS rotations.

Run on a dedicated test emulator/device after opening the native game. Requires
adb and Pillow; no original game data or save is read/written by this script.
Example: python android-patriots/tests/rotation_device_test.py --serial emulator-5554 --out rotation-qa
"""
import argparse,io,json,os,re,subprocess,time
from pathlib import Path
from PIL import Image,ImageChops,ImageStat

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--serial',required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--scene',choices=['portrait','landscape'],default='portrait')
    p.add_argument('--adb',default=os.environ.get('ADB','adb'));a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    def adb(*args):return subprocess.check_output([a.adb,'-s',a.serial,*map(str,args)],timeout=30)
    pid=adb('shell','pidof','com.patriots.mgstouch:game').strip();assert pid,'Native game is not running'
    top=adb('shell','dumpsys','activity','activities').decode(errors='replace')
    assert re.search(r'topResumedActivity=.*RetouchedActivity',top),'Show the native game, not the launcher'
    original=adb('shell','wm','user-rotation').decode().split();report=[]
    def capture(name):
        raw=adb('exec-out','screencap','-p');(a.out/(name+'.png')).write_bytes(raw)
        im=Image.open(io.BytesIO(raw)).convert('RGB');w,h=im.size
        sw,sh=(320,480) if a.scene=='portrait' else (480,320)
        k=min(w/sw,h/sh);bw,bh=round(sw*k),round(sh*k);x,y=(w-bw)//2,(h-bh)//2
        return im.crop((x,y,x+bw,y+bh)).resize((sw,sh))
    try:
        adb('shell','wm','user-rotation','lock',0);time.sleep(2);base=capture('baseline')
        if a.scene=='portrait':base=base.crop((0,275,320,475))
        for index,rotation in enumerate([1,2,3,0,1,0,3,2,1,0]):
            adb('shell','wm','user-rotation','lock',rotation);time.sleep(2)
            image=capture(f'{index:02d}-rotation-{rotation}')
            if a.scene=='portrait':image=image.crop((0,275,320,475))
            error=sum(ImageStat.Stat(ImageChops.difference(base,image)).mean)/3
            assert error<18,(rotation,error,'Picture changed/cropped; use a stationary title or paused screen')
            assert pid==adb('shell','pidof','com.patriots.mgstouch:game').strip(),'Game restarted'
            report.append(dict(rotation=rotation,mean_pixel_error=round(error,3),same_process=True))
    finally:
        if original and original[0]=='lock':adb('shell','wm','user-rotation','lock',original[-1])
        else:adb('shell','wm','user-rotation','free')
    (a.out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('PASS: 10 OS rotations, expected picture bounds and uninterrupted native process')

if __name__=='__main__':main()
