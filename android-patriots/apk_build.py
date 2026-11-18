from pathlib import Path
import hashlib,json,os,secrets,shutil,subprocess,sys,zipfile
from PIL import Image

ROOT=Path(__file__).resolve().parents[1];BASE=Path(os.environ.get('PATRIOTS_ANDROID_WORK','D:/Patriots_Android'));SDK=Path(os.environ.get('ANDROID_HOME',BASE/'sdk'));BT=SDK/'build-tools/35.0.0';JAR=SDK/'platforms/android-35/android.jar';JAVA=Path(os.environ['JAVA_HOME'])/'bin';WORK=BASE/'logs';WORK.mkdir(parents=True,exist_ok=True);OUT=ROOT/'outputs/Android';SOURCE=ROOT/'android-patriots'

def run(args,name,env=None):
    with (WORK/(name+'.log')).open('w',encoding='utf-8') as out:p=subprocess.run([str(a) for a in args],stdout=out,stderr=subprocess.STDOUT,env=env)
    if p.returncode:print((WORK/(name+'.log')).read_text(encoding='utf-8',errors='replace')[-7000:]);raise RuntimeError(name)

def signing():
    private=BASE/'signing';private.mkdir(exist_ok=True);password=private/'release-password.txt';key=private/'patriots-android.jks'
    if not password.exists():password.write_text(secrets.token_hex(24),encoding='ascii')
    env=os.environ.copy();env['PATRIOTS_SIGN_PASS']=password.read_text().strip();env['JAVA_HOME']=str(JAVA.parent)
    if not key.exists():run([JAVA/'keytool.exe','-genkeypair','-keystore',key,'-storepass:env','PATRIOTS_SIGN_PASS','-keypass:env','PATRIOTS_SIGN_PASS','-alias','patriots','-keyalg','RSA','-keysize','3072','-validity','10000','-dname','CN=Patriots Android,O=Patriots Ceviri'],'signing-create',env)
    return key,env

def prepare(game):
    build=BASE/('apk-'+game);assets=build/'assets';assets.mkdir(parents=True,exist_ok=True)
    repo=ROOT
    shutil.copy2(repo/'assets/patriots.jpg',assets/'patriots.jpg')
    res=build/'res/mipmap-xxxhdpi';res.mkdir(parents=True,exist_ok=True)
    Image.open(repo/'assets/patriots.jpg').convert('RGBA').resize((192,192),Image.Resampling.LANCZOS).save(res/'ic_launcher.png')
    if game=='mobile':
        source=Path(os.environ.get('PATRIOTS_PC_PACKAGE',ROOT/'package'))/'Oyun'
        with zipfile.ZipFile(assets/'gamepack.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for folder in ('game','languages/en','languages/tr'):
                for p in (source/folder).rglob('*'):
                    if p.is_file() and 'savedata' not in p.name.lower() and not p.name.endswith(('.log','.tmp','.previous')):z.write(p,p.relative_to(source).as_posix())
    else:
        source=Path(os.environ.get('PATRIOTS_PC_PACKAGE',ROOT/'package'))/'Oyun'
        for folder,dest in [('Assets/MGSTUS.app','MGSTUS.app'),('Assets/fonts','fonts'),('languages/tr','languages/tr')]:
            for p in (source/folder).rglob('*'):
                if p.is_file() and not p.name.endswith(('.previous','.tmp')):
                    target=assets/dest/p.relative_to(source/folder);target.parent.mkdir(parents=True,exist_ok=True)
                    if not target.exists() or target.stat().st_size != p.stat().st_size or target.stat().st_mtime_ns != p.stat().st_mtime_ns:
                        try:os.link(p,target)
                        except OSError:shutil.copy2(p,target)
    return build

def java(build,game):
    classes=build/'classes';classes.mkdir(exist_ok=True);dex=build/'dex';dex.mkdir(exist_ok=True)
    files=[p for p in (SOURCE/'java/com/patriots/shared').glob('*.java') if p.name!='UpdatePolicyTest.java']+[p for p in (SOURCE/'java').rglob('*.java') if 'com/patriots/shared' not in p.as_posix()]
    if game=='mobile':files+=list((BASE/'deps/SDL3-3.4.18/android-project/app/src/main/java').rglob('*.java'))
    run([JAVA/'javac.exe','--release','8','-encoding','UTF-8','-nowarn','-classpath',JAR,'-d',classes,*files],game+'-javac')
    jar=build/'classes.jar';run([JAVA/'jar.exe','cf',jar,'-C',classes,'.'],game+'-jar')
    env=os.environ.copy();env['JAVA_HOME']=str(JAVA.parent)
    run([BT/'d8.bat','--min-api','28','--lib',JAR,'--output',dex,jar],game+'-dex',env)

def build(game,abi='arm64-v8a',code=1000000):
    folder=prepare(game);java(folder,game)
    package='com.patriots.'+('mgstouch' if game=='touch' else 'mgsmobile');name='Metal Gear Solid '+('Touch' if game=='touch' else 'Mobile')+' Â· Patriots'
    activity='com.mgsport.retouched.RetouchedActivity' if game=='touch' else 'org.mgsmobile.port.MGSActivity';orientation='portrait' if game=='touch' else 'sensorLandscape'
    native='''<meta-data android:name="android.app.lib_name" android:value="mgst"/>''' if game=='touch' else ''
    version=f'{code//1000000}.{code//1000%1000}.{code%1000}'
    manifest=f'''<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="{package}" android:versionCode="{code}" android:versionName="{version}">
<uses-sdk android:minSdkVersion="28" android:targetSdkVersion="34"/>
<uses-permission android:name="android.permission.INTERNET"/><uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES"/><uses-permission android:name="android.permission.VIBRATE"/>
<uses-feature android:glEsVersion="0x00020000" android:required="true"/><uses-feature android:name="android.hardware.gamepad" android:required="false"/><uses-feature android:name="android.hardware.sensor.gyroscope" android:required="false"/>
<application android:label="{name}" android:icon="@mipmap/ic_launcher" android:allowBackup="false" android:isGame="true" android:appCategory="game" android:extractNativeLibs="false" android:usesCleartextTraffic="false" android:theme="@android:style/Theme.Material.NoActionBar">
<activity android:name="com.patriots.shared.HomeActivity" android:exported="true" android:screenOrientation="portrait"><intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter></activity>
<activity android:name="{activity}" android:exported="false" android:process=":game" android:launchMode="singleTop" android:screenOrientation="{orientation}" android:theme="@android:style/Theme.NoTitleBar.Fullscreen" android:configChanges="orientation|screenSize|keyboardHidden|keyboard|navigation|screenLayout|smallestScreenSize|density|uiMode">{native}</activity>
<provider android:name="com.patriots.shared.ApkProvider" android:authorities="{package}.updates" android:exported="false" android:grantUriPermissions="true"/>
</application></manifest>'''
    (folder/'AndroidManifest.xml').write_text(manifest,encoding='utf-8')
    run([BT/'aapt2.exe','compile','--dir',folder/'res','-o',folder/'res.zip'],game+'-resources')
    run([BT/'aapt2.exe','link','--manifest',folder/'AndroidManifest.xml','-I',JAR,'-A',folder/'assets','-R',folder/'res.zip','--min-sdk-version','28','--target-sdk-version','34','--auto-add-overlay','--no-compress','-o',folder/'unsigned.apk'],game+'-package')
    abis=abi.split(',')
    libs=[]
    for architecture in abis:
        values=[(BASE/f'build-touch-{architecture}/libmgst.so','libmgst.so')] if game=='touch' else [(BASE/f'build-mobile-{architecture}/mgs/libmain.so','libmain.so'),(BASE/f'build-mobile-{architecture}/SDL3/libSDL3.so','libSDL3.so')]
        libs.extend((f,n,architecture) for f,n in values)
    strip=SDK/'ndk/29.0.14206865/toolchains/llvm/prebuilt/windows-x86_64/bin/llvm-strip.exe'
    with zipfile.ZipFile(folder/'unsigned.apk','a',zipfile.ZIP_STORED) as z:
        z.write(folder/'dex/classes.dex','classes.dex')
        for file,name,architecture in libs:
            target=folder/(architecture+'-'+name);shutil.copy2(file,target);run([strip,'--strip-unneeded',target],game+'-strip-'+name);z.write(target,f'lib/{architecture}/{name}')
    run([BT/'zipalign.exe','-f','-P','16','4',folder/'unsigned.apk',folder/'aligned.apk'],game+'-align')
    key,env=signing();OUT.mkdir(parents=True,exist_ok=True);target=OUT/('MGS_'+('Touch' if game=='touch' else 'Mobile')+'_Patriots_Android'+('' if len(abis)>1 else '_'+abi)+'.apk')
    if code<1000000:target=folder/f'qa-{code}.apk'
    run([BT/'apksigner.bat','sign','--ks',key,'--ks-key-alias','patriots','--ks-pass','env:PATRIOTS_SIGN_PASS','--key-pass','env:PATRIOTS_SIGN_PASS','--out',target,folder/'aligned.apk'],game+'-sign',env)
    run([BT/'apksigner.bat','verify','--verbose','--print-certs',target],game+'-verify',env)
    run([BT/'zipalign.exe','-c','-P','16','4',target],game+'-alignment-verify')
    h=hashlib.sha256(target.read_bytes()).hexdigest();target.with_suffix('.apk.sha256').write_text(h+'  '+target.name+'\n',encoding='ascii')
    print(json.dumps({'apk':str(target),'package':package,'version_code':code,'sha256':h,'bytes':target.stat().st_size},indent=2),flush=True)

if __name__=='__main__':
    build(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else 'arm64-v8a',int(sys.argv[3]) if len(sys.argv)>3 else 1000000)
