"""Read-only validator for the exact MGS Touch IPA expected by etruj/mgs-retouched.
Usage: py -3 validate_mgs_touch_ipa.py "D:\Game.ipa" [--out report.json]
The validator reads two ZIP members; it does not extract or execute the game.
"""
from pathlib import Path
import argparse,hashlib,json,plistlib,struct,sys,tempfile,zipfile
EXPECTED_SHA256='07ac5db07fb8909a95b23c791d20800237bf14a51de1cec32cd0be8e37773a9c'
def macho(data):
    if len(data)<28:raise ValueError('Truncated Mach-O header')
    magic,cpu,subtype,kind,ncmds,sizecmds,flags=struct.unpack_from('<7I',data)
    if magic!=0xfeedface:raise ValueError('Expected a thin 32-bit Mach-O executable')
    end=28+sizecmds
    if end>len(data) or ncmds>10000:raise ValueError('Invalid Mach-O load-command table')
    off=28;cryptids=[]
    for _ in range(ncmds):
        if off+8>end:raise ValueError('Truncated load command')
        cmd,size=struct.unpack_from('<2I',data,off)
        if size<8 or off+size>end:raise ValueError('Invalid load-command size')
        if cmd==0x21:
            if size<20:raise ValueError('Truncated encryption command')
            cryptids.append(struct.unpack_from('<I',data,off+16)[0])
        off+=size
    return {'cpu_type':cpu,'cpu_subtype':subtype,'file_type':kind,'cryptids':cryptids}
def inspect(path,expected=EXPECTED_SHA256):
    with zipfile.ZipFile(path) as z:
        names=z.namelist();plists=[n for n in names if n.startswith('Payload/') and n.endswith('.app/Info.plist') and len(n.split('/'))==3]
        if len(plists)!=1:raise ValueError('Expected exactly one main Payload/*.app/Info.plist')
        name=plists[0]
        if z.getinfo(name).file_size>2*1024*1024:raise ValueError('Info.plist is unexpectedly large')
        info=plistlib.loads(z.read(name));exe=info.get('CFBundleExecutable','')
        if not isinstance(exe,str) or not exe or '/' in exe or '\\' in exe:raise ValueError('Invalid CFBundleExecutable')
        member=name.rsplit('/',1)[0]+'/'+exe
        if z.getinfo(member).file_size>64*1024*1024:raise ValueError('Executable is unexpectedly large')
        binary=z.read(member)
    report={'ipa':str(Path(path).resolve()),'bundle_id':info.get('CFBundleIdentifier'),'version':str(info.get('CFBundleVersion','')),'executable':exe,'executable_sha256':hashlib.sha256(binary).hexdigest(),'expected_sha256':expected,'minimum_ios':info.get('MinimumOSVersion'),'device_families':info.get('UIDeviceFamily')}
    report.update(macho(binary));reasons=[]
    if report['bundle_id']!='com.konami.mgst':reasons.append('Different app identifier')
    if report['version']!='2.3.0':reasons.append('Only version 2.3.0 is supported by the inspected builder')
    if exe!='MGSTUS':reasons.append('Different executable name')
    if report['cpu_type']!=12 or report['file_type']!=2:reasons.append('Expected an ARM executable')
    if any(report['cryptids']):reasons.append('Executable is encrypted (cryptid is not zero)')
    if report['executable_sha256']!=expected:reasons.append('Executable hash differs from the tested build')
    report['supported_by_inspected_builder']=not reasons;report['reasons']=reasons
    return report
def selftest():
    good=struct.pack('<7I',0xfeedface,12,6,2,1,20,0)+struct.pack('<5I',0x21,20,0,0,0)
    def fixture(path,version='2.3.0',data=good):
        with zipfile.ZipFile(path,'w') as z:
            z.writestr('Payload/MGSTUS.app/Info.plist',plistlib.dumps({'CFBundleIdentifier':'com.konami.mgst','CFBundleVersion':version,'CFBundleExecutable':'MGSTUS'}));z.writestr('Payload/MGSTUS.app/MGSTUS',data)
    with tempfile.TemporaryDirectory(prefix='mgst-ipa-check-') as temp:
        p=Path(temp)/'fixture.ipa';digest=hashlib.sha256(good).hexdigest();fixture(p)
        assert inspect(p,digest)['supported_by_inspected_builder']
        assert not inspect(p)['supported_by_inspected_builder']
        fixture(p,version='2.3.1');assert not inspect(p,digest)['supported_by_inspected_builder']
        encrypted=good[:-4]+struct.pack('<I',1);fixture(p,data=encrypted);assert not inspect(p,hashlib.sha256(encrypted).hexdigest())['supported_by_inspected_builder']
        for bad in [b'abc',struct.pack('<7I',0xfeedface,12,6,2,1,8,0)+struct.pack('<2I',0x21,4)]:
            try:macho(bad)
            except ValueError:pass
            else:raise AssertionError('Malformed Mach-O accepted')
    print('PASS: matching fixture, wrong hash, wrong version, encrypted executable and malformed Mach-O checks')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('ipa',type=Path,nargs='?');p.add_argument('--out',type=Path);p.add_argument('--self-test',action='store_true');a=p.parse_args()
    if a.self_test:selftest();return 0
    if not a.ipa:p.error('provide an IPA path')
    try:r=inspect(a.ipa)
    except (ValueError,OSError,KeyError,zipfile.BadZipFile,plistlib.InvalidFileException) as e:r={'supported_by_inspected_builder':False,'error':str(e)}
    s=json.dumps(r,ensure_ascii=False,indent=2);print(s)
    if a.out:a.out.write_text(s+'\n',encoding='utf-8')
    return 0 if r.get('supported_by_inspected_builder') else 1
if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
