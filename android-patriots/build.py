from pathlib import Path
import os,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_build,apk_build
version=sys.argv[1] if len(sys.argv)>1 else '1.0.1'
parts=[int(x) for x in version.split('.')]
assert len(parts)==3 and 0<=parts[0]<100 and 0<=parts[1]<100 and 0<=parts[2]<1000
code=parts[0]*1000000+parts[1]*1000+parts[2]
abis=os.environ.get('PATRIOTS_ANDROID_ABIS','arm64-v8a,armeabi-v7a').split(',')
for abi in abis:native_build.touch(abi)
apk_build.build('touch',','.join(abis),code)
