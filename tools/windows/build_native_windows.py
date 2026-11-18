"""Build a portable SDL3 Windows executable from locally recovered wasm2c C."""
from pathlib import Path
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import time

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"D:\Patriots_MGS_Touch_PC")
ROOT = Path(__file__).resolve().parents[2]
REPO = BASE / "mgs-retouched"
SRC = Path(__file__).resolve().parent
TC = ROOT / "dependencies/llvm-mingw/bin"
SDL = ROOT / "dependencies/SDL3"
NINJA = ROOT / "dependencies/ninja.exe"
GEN = REPO / "build/retouched/gen"
WABT = BASE / "tools/wabt-1.0.37/wasm2c"
PACKAGE = BASE / "package"
WINDOWS = REPO / "windows"
ENV = os.environ.copy()
ENV["PATH"] = str(TC) + os.pathsep + ENV["PATH"]

def unpack(name, digest):
    archive = BASE / "downloads" / name
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest, name + " hash mismatch"
    with tarfile.open(archive) as tar:
        tar.extractall(BASE / "tools", filter="data")

def run(args, name):
    log = REPO / "build/windows-logs" / (name + ".log")
    print(time.strftime("%H:%M:%S"), name, flush=True)
    with log.open("w", encoding="utf-8") as output:
        p = subprocess.run([str(x) for x in args], cwd=REPO, env=ENV, stdout=output, stderr=subprocess.STDOUT)
    if p.returncode:
        print(log.read_text(encoding="utf-8", errors="replace")[-9000:], flush=True)
        raise RuntimeError(name + " failed: " + str(log))

def patch_host():
    original = ROOT / "upstream/mgs-retouched"
    # Derive platform adaptations from the pinned original each time (idempotent).
    core = (original / "engine/host/core.c").read_text(encoding="utf-8")
    core = core.replace('#include <errno.h>', '#include <errno.h>\n#ifdef _WIN32\n#include <direct.h>\n#define mkdir(path,mode) _mkdir(path)\n#endif')
    core = core.replace("if (!g_cfg.overlay_dir[0] || strchr(rel, '/')) return 0;",
        "if (!g_cfg.overlay_dir[0] || rel[0] == '/' || strchr(rel, '\\\\') || strchr(rel, ':') || strstr(rel, \"..\")) return 0;")
    (REPO / "engine/host/core.c").write_text(core, encoding="utf-8")
    vfs=(original / "engine/host/vfs.c").read_text(encoding="utf-8")
    vfs=vfs.replace('struct stat st; if (stat(path, &st) != 0 || !S_ISREG(st.st_mode)) return -1;\n    return (long)st.st_size;',
        'FILE *f=fopen(path,"rb");if(!f)return -1;\n    if(fseek(f,0,SEEK_END)){fclose(f);return -1;}long n=ftell(f);fclose(f);return n;')
    (REPO / "engine/host/vfs.c").write_text(vfs,encoding="utf-8")
    rtx = (original / "android-retouched/host/rtx_host.c").read_text(encoding="utf-8")
    rtx = rtx.replace('#include <sys/stat.h>', '#include <sys/stat.h>\n#ifdef _WIN32\n#include <direct.h>\n#define mkdir(path,mode) _mkdir(path)\n#endif')
    rtx = rtx.replace('if (!paused) g_ext.render_scale = S.sharp ? (k < 1 ? 1 : k > 4 ? 4 : k) : 1;',
        '#ifndef PATRIOTS_DESKTOP\n    if (!paused) g_ext.render_scale = S.sharp ? (k < 1 ? 1 : k > 4 ? 4 : k) : 1;\n#endif')
    rtx = rtx.replace('pad_seen = now_t; }', 'if (pad_ax || pad_ay) pad_seen = now_t; }')
    rtx = rtx.replace('if ((st & ST_MISSION) && screen == SCR_NONE) {', 'if (g_cfg.rotate) {')
    rtx = rtx.replace('if (st & ST_INCLINATION) { float t = dx;', 'if (g_cfg.rotate == 90) { float t = dx;')
    rtx = rtx.replace('#include <sys/stat.h>', '#include <sys/stat.h>\nextern int desktop_open_settings(void);')
    rtx = rtx.replace('if (ev == 1 && screen == SCR_NONE) { screen = SCR_OPTIONS;',
        'if (ev == 1 && screen == SCR_NONE) { if (desktop_open_settings()) return; screen = SCR_OPTIONS;')
    rtx = rtx.replace('else { screen = SCR_OPTIONS; opt_from_pause = 1; tab = 0; }',
        'else { if (!desktop_open_settings()) { screen = SCR_OPTIONS; opt_from_pause = 1; tab = 0; } }')
    rtx = rtx.replace('if (st & ST_MAIN_MENU) { screen = SCR_OPTIONS;',
        'if (st & ST_MAIN_MENU) { return 0; screen = SCR_OPTIONS;')
    rtx=rtx.replace('static int quit_confirm;', 'static int pause_focus,quit_focus=1,overlay_mouse,pause_hover=-1,quit_hover=-1;\nstatic int quit_confirm;')
    rtx=rtx.replace('static void do_pause(void) { if (!paused) {', 'static void do_pause(void) { if (!paused) { pause_focus=0;quit_focus=1;overlay_mouse=0;')
    rtx=rtx.replace('"RESUME", 1);','"RESUME", (overlay_mouse?pause_hover:pause_focus)==0);').replace('"RETOUCHED", 0);','"RETOUCHED", (overlay_mouse?pause_hover:pause_focus)==1);').replace('"QUIT", 0);','"QUIT", (overlay_mouse?pause_hover:pause_focus)==2);')
    rtx=rtx.replace('"YES", 0);','"YES", (overlay_mouse?quit_hover:quit_focus)==0);').replace('"NO", 1);','"NO", (overlay_mouse?quit_hover:quit_focus)==1);')
    rtx=rtx.replace('else if (which == 3) quit_confirm = 1;', 'else if (which == 3) {quit_confirm = 1;quit_focus=1;}')
    rtx=rtx.replace('    if (lit) ui_frame(x, y, w, h, 1.5f, ACCENT);','    if (lit) ui_fill(x,y,w,h,(Col){.35f,.68f,.20f,.32f});')
    rtx=rtx.replace('12.5f, 1, 1, WHITE, w - 8);','12.5f, 1, 1, lit?ACCENT:WHITE, w - 8);')
    rtx=rtx.replace('if (now_t - pad_seen < 4.0 && pad_seen > 0)', 'if (0)')
    # Hit testing must use the overlay's coordinate space, never whichever space
    # the last help/cursor drawing call left in the immediate-mode renderer.
    rtx=rtx.replace('    if (reentry) return 0;', '    ui_set_space(screen==SCR_PAUSE || (screen!=SCR_NONE && opt_from_pause) || (screen==SCR_NONE && (st&ST_MISSION)), !(st&ST_INCLINATION));\n    if (reentry) return 0;')
    rtx=rtx.replace('#include "rtx_host.h"', '#include "rtx_host.h"\nvoid ui_set_space(int land,int flip);')
    rtx+='\n'+(SRC/'desktop_menu_host.inc').read_text(encoding='utf-8')
    (REPO / "android-retouched/host/rtx_host.c").write_text(rtx, encoding="utf-8")
    text = (original / "engine/host/text_ft.c").read_text(encoding="utf-8")
    text = text.replace('static FT_Library ft;', 'extern const char *pc_runtime_text(const char *s);\nstatic FT_Library ft;')
    text = text.replace('    Line lines[256]; int n = layout(s,', '    s = pc_runtime_text(s);\n    Line lines[256]; int n = layout(s,')
    (REPO / "engine/host/text_ft.c").write_text(text, encoding="utf-8")
    gfx = (original / "engine/host/gfx.c").read_text(encoding="utf-8")
    gfx+='''\nvoid gfx_view_to_window(float vx,float vy,float *wx,float *wy){
    int x,y,w,h;screen_box(&x,&y,&w,&h);float lx=vx,ly=vy;
    if(g_cfg.rotate==90){lx=vy;ly=320-vx;}else if(g_cfg.rotate==270){lx=480-vy;ly=vx;}
    *wx=x+lx*w/scr_w();*wy=y+ly*h/scr_h();
}\n'''
    gfx = gfx.replace('void *gfx_getproc(const char *name);', 'int pc_write_png(const char *path,int w,int h,const uint8_t *rgba);\nvoid *gfx_getproc(const char *name);')
    gfx = gfx.replace('FILE *f = fopen(capture_path, "wb");', 'FILE *f=NULL;size_t plen=strlen(capture_path);\n        if(plen>=4&&!strcmp(capture_path+plen-4,".png")){if(pc_write_png(capture_path,win_w,win_h,px))hlog("PNG capture failed: %s",capture_path);}\n        else f=fopen(capture_path,"wb");')
    a = gfx.index("    genFB = glGenFramebuffers;")
    b = gfx.index("\n#endif", a)
    assignments = {"genFB":("PFgen","glGenFramebuffers"), "genRB":("PFgen","glGenRenderbuffers"),
        "delFB":("PFgen","glDeleteFramebuffers"),"delRB":("PFgen","glDeleteRenderbuffers"),
        "bindFB":("PFbind","glBindFramebuffer"),"bindRB":("PFbind","glBindRenderbuffer"),
        "rbStorage":("PFstore","glRenderbufferStorage"),"fbRB":("PFattrb","glFramebufferRenderbuffer"),
        "fbTex":("PFattt","glFramebufferTexture2D"),"checkFB":("PFcheck","glCheckFramebufferStatus"),
        "getRB":("PFgetrb","glGetRenderbufferParameteriv")}
    gfx = gfx[:a] + "\n".join('    '+key+' = ('+typ+')gfx_getproc("'+name+'");' for key,(typ,name) in assignments.items()) + gfx[b:]
    (REPO / "engine/host/gfx.c").write_text(gfx, encoding="utf-8")
    ui = (original / "android-retouched/host/rtx_ui.c").read_text(encoding="utf-8")
    ui = ui.replace('#include <GL/gl.h>', '#include <GL/gl.h>\n#include <GL/glext.h>')
    ui = ui.replace("glMatrixMode(GL_MODELVIEW); glLoadIdentity();", """glMatrixMode(GL_MODELVIEW); glLoadIdentity();
    /* Present overlays in the same automatically rotated space as the game. */
    if (g_cfg.rotate) {
        glMatrixMode(GL_PROJECTION); glLoadIdentity(); glOrtho_(0,480,320,0,-1,1);
        glMatrixMode(GL_MODELVIEW);
        if (g_cfg.rotate == 90) { glTranslatef(0,320,0); glRotatef(-90,0,0,1); }
        else { glTranslatef(480,0,0); glRotatef(90,0,0,1); }
    }""", 1)
    (REPO / "android-retouched/host/rtx_ui.c").write_text(ui, encoding="utf-8")
    with (REPO / "android-retouched/host/rtx_ui.c").open("a",encoding="utf-8") as output:
        output.write('''\n/* Desktop control hints use window pixels, independently of game rotation. */
void pc_ui_begin_window(int w,int h) {
    ppu=1;
    glViewport(0,0,w,h);
    glMatrixMode(GL_TEXTURE);glLoadIdentity();
    glMatrixMode(GL_PROJECTION);glLoadIdentity();glOrtho_(0,w,h,0,-1,1);
    glMatrixMode(GL_MODELVIEW);glLoadIdentity();
    glEnable(GL_BLEND);glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
    glDisableClientState(GL_COLOR_ARRAY);glEnableClientState(GL_VERTEX_ARRAY);
}
void ui_set_space(int l,int f){land=l;flip=f;}
''')

def main():
    while not (BASE / "wasm-windows.ready").exists():
        time.sleep(15)
    unpack("freetype-2.13.3.tar.xz", "0550350666d427c74daeb85d5ac7bb353acba5f76956395995311a9c6f063289")
    unpack("zlib-1.3.1.tar.gz", "9a93b2b7dfdac77ceba5a558a580e74667dd6fede4585b91eefb60f03b72df23")
    unpack("liberation-fonts-2.1.5.tar.gz", "7191c669bf38899f73a2094ed00f7b800553364f90e2637010a69c0e268f25d0")
    assert hashlib.sha256((BASE / "downloads/DroidSansFallbackFull.ttf").read_bytes()).hexdigest() == "acb6440a713d880a13a21b468ba7cd43f5a2b2934972e51be791c880730777b8"
    WINDOWS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC / "windows_main.c", WINDOWS / "main.c")
    shutil.copy2(SRC / "windows_utf8.h", WINDOWS / "windows_utf8.h")
    shutil.copy2(SRC / "windows_png.c", WINDOWS / "windows_png.c")
    shutil.copy2(SRC / "windows_navigation.inc", WINDOWS / "windows_navigation.inc")
    shutil.copy2(PACKAGE / "Arayuz/game.ico", WINDOWS / "game.ico")
    (WINDOWS / "mgs_touch.rc").write_text('1 ICON "game.ico"\n',encoding="utf-8")
    run([TC / "x86_64-w64-mingw32-windres.exe", "-i", WINDOWS / "mgs_touch.rc", "-I", WINDOWS, "-O", "coff", "-o", WINDOWS / "game_icon.o"],"native_icon")
    patch_host()
    ft = BASE / "tools/freetype-2.13.3"
    zlib = BASE / "tools/zlib-1.3.1"
    cmake = """cmake_minimum_required(VERSION 3.20)
project(PatriotsMGSTouch LANGUAGES C)
set(CMAKE_C_STANDARD 23)
set(CMAKE_C_FLAGS_RELEASE "-O2 -DNDEBUG")
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(ZLIB_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
add_subdirectory("@ZLIB@" zlib)
add_library(game_module STATIC "@GEN@/mgst_w2c.c")
target_include_directories(game_module PRIVATE "@GEN@" "@WABT@")
target_compile_definitions(game_module PRIVATE WASM_RT_MEMCHECK_GUARD_PAGES=0 WASM_RT_MEMCHECK_BOUNDS_CHECK=1 WASM_RT_USE_STACK_DEPTH_COUNT=1)
target_compile_options(game_module PRIVATE -w -fno-strict-aliasing -ffp-contract=off)
set_source_files_properties("@GEN@/mgst_w2c.c" PROPERTIES COMPILE_OPTIONS "-O1")
add_library(freetype_min STATIC
@FTFILES@
)
target_compile_definitions(freetype_min PRIVATE FT2_BUILD_LIBRARY FT_CONFIG_MODULES_H="ftmodule.h")
target_include_directories(freetype_min PRIVATE "@REPO@/engine/host" "@FT@/include")
target_compile_options(freetype_min PRIVATE -w)
add_executable(mgs_touch
  main.c
  windows_png.c
  game_icon.o
  "@WABT@/wasm-rt-impl.c"
  "@WABT@/wasm-rt-exceptions-impl.c"
  "@WABT@/wasm-rt-mem-impl.c"
  "@REPO@/engine/host/core.c" "@REPO@/engine/host/gfx.c"
  "@REPO@/engine/host/vfs.c" "@REPO@/engine/host/touch.c"
  "@REPO@/engine/host/image.c" "@REPO@/engine/host/mixer.c"
  "@REPO@/engine/host/text_ft.c"
  "@REPO@/android-retouched/host/rtx_host.c"
  "@REPO@/android-retouched/host/rtx_ui.c"
)
target_include_directories(mgs_touch PRIVATE "@GEN@" "@WABT@" "@SDL@/include" "@FT@/include" "@REPO@/engine/host" "@REPO@/android-retouched/host" "@ZLIB@")
target_compile_definitions(mgs_touch PRIVATE PATRIOTS_DESKTOP MGST_RETOUCHED WASM_RT_MEMCHECK_GUARD_PAGES=0 WASM_RT_MEMCHECK_BOUNDS_CHECK=1 WASM_RT_USE_STACK_DEPTH_COUNT=1)
target_compile_options(mgs_touch PRIVATE -fno-strict-aliasing -ffp-contract=off -Wall -Wno-unused-function -Wno-unused-variable)
target_compile_options(mgs_touch PRIVATE -include "@REPO@/windows/windows_utf8.h")
target_link_options(mgs_touch PRIVATE -static -Wl,--stack,16777216)
target_link_libraries(mgs_touch PRIVATE game_module freetype_min zlibstatic "@SDL@/lib/x64/SDL3.lib" opengl32 shell32 winpthread)
"""
    ftfiles = "base/ftsystem.c base/ftinit.c base/ftdebug.c base/ftbase.c base/ftbitmap.c base/ftglyph.c base/ftmm.c truetype/truetype.c sfnt/sfnt.c smooth/smooth.c autofit/autofit.c psnames/psnames.c gzip/ftgzip.c".split()
    values = {"ZLIB":zlib.as_posix(),"GEN":GEN.as_posix(),"WABT":WABT.as_posix(),"REPO":REPO.as_posix(),"SDL":SDL.as_posix(),"FT":ft.as_posix(),
              "FTFILES":"\n".join('  "'+(ft / "src" / f).as_posix()+'"' for f in ftfiles)}
    for key,val in values.items():
        cmake = cmake.replace("@"+key+"@",val)
    (WINDOWS / "CMakeLists.txt").write_text(cmake, encoding="utf-8")
    build = REPO / "build/windows-native"
    run(["cmake","-S",WINDOWS,"-B",build,"-G","Ninja","-DCMAKE_MAKE_PROGRAM="+NINJA.as_posix(),"-DCMAKE_C_COMPILER="+(TC / "clang.exe").as_posix(),"-DCMAKE_BUILD_TYPE=Release"],"native_configure")
    run(["cmake","--build",build,"--target","mgs_touch","--parallel","3"],"native_compile")
    game = PACKAGE / "Oyun"
    fonts = game / "Assets/fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(build / "mgs_touch.exe",game)
    shutil.copy2(SDL / "lib/x64/SDL3.dll",game)
    app = BASE / "mgs-decomp/work/extracted/Payload/MGSTUS.app"
    shutil.copytree(app, game / "Assets/MGSTUS.app", dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("MGSTUS", "_CodeSignature", "CodeResources", "embedded.mobileprovision"))
    for name in ("LiberationSans-Regular.ttf","LiberationSans-Bold.ttf"):
        shutil.copy2(BASE / "tools/liberation-fonts-ttf-2.1.5" / name,fonts)
    shutil.copy2(BASE / "downloads/DroidSansFallbackFull.ttf",fonts)
    shutil.copy2(REPO / "android-retouched/fonts/BebasNeue-Regular.ttf",fonts)
    (PACKAGE / "Saves").mkdir(exist_ok=True)
    (game / "desktop.ini").write_text("language=en\nfullscreen=0\nvsync=1\nmax_fps=120\nfill=1\nrender_scale=3\ndeadzone=0.18\n",encoding="utf-8")
    (BASE / "native-windows.ready").write_text(str(game / "mgs_touch.exe") + "\n")
    print("Windows game ready for first actual boot:",game / "mgs_touch.exe",flush=True)

if __name__ == "__main__":
    main()
