from pathlib import Path
import os,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT=Path(__file__).resolve().parents[1];BASE=Path(os.environ.get('PATRIOTS_ANDROID_WORK','D:/Patriots_Android'));SDK=Path(os.environ.get('ANDROID_HOME',BASE/'sdk'));NDK=SDK/'ndk/29.0.14206865';DEPS=BASE/'deps';NINJA=Path(__import__('shutil').which('ninja') or 'ninja')
ENV=os.environ.copy();ENV['PATH']='C:/msys64/usr/bin;'+str(NDK/'toolchains/llvm/prebuilt/windows-x86_64/bin')+';'+ENV['PATH'];ENV['MSYS_NO_PATHCONV']='1';ENV['PATH']=str(BASE/'shims')+';'+ENV['PATH']

def run(args,label):
    log=BASE/'logs'/f'{label}.log';log.parent.mkdir(parents=True,exist_ok=True);print(label,flush=True)
    with log.open('w',encoding='utf-8') as out:r=subprocess.run([str(a) for a in args],stdout=out,stderr=subprocess.STDOUT,env=ENV)
    if r.returncode:print(log.read_text(encoding='utf-8',errors='replace')[-7000:],flush=True);raise RuntimeError(label)

def cmake(src,build,abi,extra=()):
    run(['cmake','-S',src,'-B',build,'-G','Ninja',f'-DCMAKE_MAKE_PROGRAM={NINJA}',f'-DCMAKE_TOOLCHAIN_FILE={NDK}/build/cmake/android.toolchain.cmake',f'-DANDROID_ABI={abi}','-DANDROID_PLATFORM=android-28','-DANDROID_STL=c++_static','-DCMAKE_BUILD_TYPE=Release',*extra],build.name+'-configure')

def mobile(abi):
    # Windows users do not need symlink privileges for Unicorn's archive alias.
    if os.name=='nt':
        import shutil
        bundle=DEPS/'unicorn-2.1.4/cmake/bundle_static.cmake'
        if bundle.exists():
            value=bundle.read_text(encoding='utf-8');bundle.write_text(value.replace('create_symlink','copy_if_different'),encoding='utf-8')
        shims=BASE/'shims';shims.mkdir(parents=True,exist_ok=True)
        if not (shims/'strings.exe').exists():shutil.copy2(NDK/'toolchains/llvm/prebuilt/windows-x86_64/bin/llvm-strings.exe',shims/'strings.exe')
    uc=BASE/f'build-unicorn-{abi}'
    shims=BASE/'shims';shims.mkdir(exist_ok=True);(shims/'pkg-config').write_text('#!/bin/sh\nexit 1\n',encoding='ascii',newline='\n');ENV['PATH']=str(shims)+';'+ENV['PATH']
    if not (uc/'libunicorn.a').exists():
        cmake(DEPS/'unicorn-2.1.4',uc,abi,['-DUNICORN_ARCH=arm','-DUNICORN_BUILD_TESTS=OFF','-DUNICORN_INSTALL=OFF','-DBUILD_SHARED_LIBS=OFF','-DCMAKE_C_FLAGS=-fPIC'])
        run(['cmake','--build',uc,'--parallel','3'],uc.name+'-build')
    build=BASE/f'build-mobile-{abi}';src=BASE/'mobile-cmake';src.mkdir(exist_ok=True)
    repo=ROOT/'runtime'
    (src/'CMakeLists.txt').write_text(f'''cmake_minimum_required(VERSION 3.22)
project(PatriotsMobileAndroid C CXX)
set(SDL_SHARED ON CACHE BOOL "" FORCE)
set(SDL_STATIC OFF CACHE BOOL "" FORCE)
set(SDL_TEST_LIBRARY OFF CACHE BOOL "" FORCE)
set(SDL_TESTS OFF CACHE BOOL "" FORCE)
string(APPEND CMAKE_SHARED_LINKER_FLAGS " -Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384")
add_subdirectory("{(DEPS/'SDL3-3.4.18').as_posix()}" SDL3)
set(UNICORN_ROOT "{(DEPS/'unicorn-2.1.4').as_posix()}" CACHE PATH "" FORCE)
set(UNICORN_LIB "{(uc/'libunicorn.a').as_posix()}" CACHE FILEPATH "" FORCE)
add_subdirectory("{(repo/'mgs_native').as_posix()}" mgs)
''',encoding='utf-8')
    cmake(src,build,abi);run(['cmake','--build',build,'--target','mgs_mobile','--parallel','3'],build.name+'-build')

def touch(abi):
    src=BASE/'touch-cmake';src.mkdir(exist_ok=True);work=ROOT/'android-patriots/native';gen=Path(os.environ.get('PATRIOTS_TOUCH_GEN','D:/Patriots_MGS_Touch_PC/mgs-retouched/build/retouched/gen'));wabt=Path(os.environ.get('PATRIOTS_WABT','D:/Patriots_MGS_Touch_PC/tools/wabt-1.0.37/wasm2c'));ft=Path(os.environ.get('PATRIOTS_FREETYPE','D:/Patriots_MGS_Touch_PC/tools/freetype-2.13.3'));glue=NDK/'sources/android/native_app_glue'
    ftfiles='base/ftsystem.c base/ftinit.c base/ftdebug.c base/ftbase.c base/ftbitmap.c base/ftglyph.c base/ftmm.c truetype/truetype.c sfnt/sfnt.c smooth/smooth.c autofit/autofit.c psnames/psnames.c gzip/ftgzip.c'.split()
    files=[ROOT/'runtime/windows/windows_png.c']+[work/'engine/host'/n for n in ['core.c','gfx.c','vfs.c','touch.c','image.c','mixer.c','text_ft.c']]+[work/'android-retouched/host'/n for n in ['rtx_host.c','rtx_ui.c']]+[work/'android-vanilla/host/main.c',ROOT/'android-patriots/native/android_locale.c',glue/'android_native_app_glue.c']+[wabt/n for n in ['wasm-rt-impl.c','wasm-rt-exceptions-impl.c','wasm-rt-mem-impl.c']]
    q=lambda paths:'\n'.join('"'+p.as_posix()+'"' for p in paths)
    cm=f'''cmake_minimum_required(VERSION 3.22)
project(PatriotsTouchAndroid C)
set(CMAKE_C_STANDARD 23)
add_compile_definitions(MGST_RETOUCHED HOST_GLES WASM_RT_MEMCHECK_GUARD_PAGES=0 WASM_RT_MEMCHECK_BOUNDS_CHECK=1 WASM_RT_USE_STACK_DEPTH_COUNT=1)
add_compile_options(-fno-strict-aliasing -ffp-contract=off)
include_directories("{gen.as_posix()}" "{wabt.as_posix()}" "{(work/'engine/host').as_posix()}" "{(work/'android-retouched/host').as_posix()}" "{(ft/'include').as_posix()}" "{glue.as_posix()}")
add_library(game_module STATIC "{(gen/'mgst_w2c.c').as_posix()}")
target_compile_options(game_module PRIVATE -w -O1)
set_target_properties(game_module PROPERTIES POSITION_INDEPENDENT_CODE ON)
add_library(freetype_min STATIC
{q([ft/'src'/f for f in ftfiles])})
target_compile_definitions(freetype_min PRIVATE FT2_BUILD_LIBRARY FT_CONFIG_MODULES_H="ftmodule.h")
set_target_properties(freetype_min PROPERTIES POSITION_INDEPENDENT_CODE ON)
add_library(mgst SHARED
{q(files)})
target_link_libraries(mgst PRIVATE game_module freetype_min android log EGL GLESv1_CM aaudio z m)
target_link_options(mgst PRIVATE -uANativeActivity_onCreate -Wl,--no-undefined -Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384)
'''
    (src/'CMakeLists.txt').write_text(cm,encoding='utf-8');build=BASE/f'build-touch-{abi}';cmake(src,build,abi);run(['cmake','--build',build,'--target','mgst','--parallel','3'],build.name+'-build')

if __name__=='__main__':
    game=sys.argv[1];abi=sys.argv[2] if len(sys.argv)>2 else 'arm64-v8a'
    (mobile if game=='mobile' else touch)(abi)
    print(game,abi,'native build complete',flush=True)
