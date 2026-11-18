"""Windows build of the recovered 32-bit game through LLVM/WABT AOT."""
from pathlib import Path
import concurrent.futures
import os
import shutil
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"D:\Patriots_MGS_Touch_PC")
DECOMP = BASE / "mgs-decomp"
REPO = BASE / "mgs-retouched"
HANDOFF = DECOMP / "PORT_HANDOFF"
B = REPO / "build"
G = B / "gen"
RO = B / "robj-retouched"
OUTG = B / "retouched/gen"
ENV = os.environ.copy()
ENV.update(PYTHONUTF8="1", MGST_HANDOFF=str(HANDOFF))
LOG = B / "windows-logs"
LOG.mkdir(parents=True, exist_ok=True)

GAME = "--target=wasm32 -O1 -std=gnu17 -ffreestanding -fno-builtin -nostdlib -fsigned-char -fno-short-enums -mnontrapping-fptoint -mbulk-memory -ffp-contract=off -fno-strict-aliasing -w -Wno-error=int-conversion -Wno-error=incompatible-pointer-types -Wno-error=implicit-function-declaration -Wno-error=incompatible-function-pointer-types -Wno-error=return-type -Wno-error=int-to-pointer-cast".split()
RT = "--target=wasm32 -O2 -std=gnu23 -ffreestanding -fno-builtin -nostdlib -mnontrapping-fptoint -mbulk-memory -ffp-contract=off -fno-strict-aliasing -w -DMGST_RETOUCHED".split()

def run(args, name, cwd=REPO):
    args = [str(x) for x in args]
    print(time.strftime("%H:%M:%S"), name, flush=True)
    path = LOG / (name + ".log")
    with path.open("w", encoding="utf-8") as output:
        p = subprocess.run(args, cwd=cwd, env=ENV, stdout=output, stderr=subprocess.STDOUT)
    if p.returncode:
        print(path.read_text(encoding="utf-8", errors="replace")[-7000:], flush=True)
        raise RuntimeError(name + " failed; " + str(path))

def main():
    while not (BASE / "decompiled-windows.ready").exists():
        time.sleep(15)
    clangs = list((BASE / "tools").glob("wasi-sdk*/bin/clang.exe"))
    while not clangs:
        time.sleep(15)
        clangs = list((BASE / "tools").glob("wasi-sdk*/bin/clang.exe"))
    clang = clangs[0]
    linker = clang.parent / "wasm-ld.exe"
    wasm2cs = list((BASE / "tools").glob("wabt*/build-patriots/wasm2c.exe"))
    while not wasm2cs:
        time.sleep(10)
        wasm2cs = list((BASE / "tools").glob("wabt*/build-patriots/wasm2c.exe"))
    if not (HANDOFF / "index.tsv").exists():
        # The handoff records the local static results; it does not assert an unrun differential test.
        status = DECOMP / "analysis/verification/function_status.tsv"
        if not status.exists():
            status.write_text("addr\tfunction\tstage\tcoverage\tverdict\tevidence\n", encoding="utf-8")
        run([sys.executable, "tools/make_port_handoff.py"], "handoff", DECOMP)
    assert len(list((HANDOFF / "src").rglob("*.c"))) == 1395, "Incomplete recovered source handoff"
    if not (HANDOFF / "README.md").exists():
        (HANDOFF / "README.md").write_text("Local MGS Touch 2.3.0 handoff. 1395 functions compiled; static audits passed. Full dynamic differential verification was not rerun. Generated original game material remains local.\n",encoding="utf-8")
    for p in (G / "include", B / "wobj", RO, OUTG):
        p.mkdir(parents=True, exist_ok=True)
    run([sys.executable, "engine/tools/mk_image.py", G], "image")
    run([sys.executable, "engine/tools/mk_header.py", HANDOFF / "include/mgst_types.fixed.h", G / "include/mgst_types.fixed.h"], "header")
    shutil.copy2(HANDOFF / "include/ghidra_ops.h", G / "include")
    # A 64-bit host is safe only if the wasm32 game preserves all original field offsets.
    import re
    header = (HANDOFF / "include/mgst_types.fixed.h").read_text(encoding="utf-8")
    names = sorted(set(re.findall(r'^struct (\w+) \{', header, re.M)))
    layout_c = G / "layout_check.c"
    layout_c.write_text('#include "mgst_types.fixed.h"\n' + ''.join(f'int s{i}=sizeof(struct {name});\n' for i,name in enumerate(names)), encoding="utf-8")
    native_clang = Path(__file__).resolve().parents[2] / "dependencies/llvm-mingw/bin/clang.exe"
    run([native_clang, "--target=armv6-none-eabi", "-mabi=apcs-gnu", "-mfloat-abi=softfp", "-fsigned-char", "-fno-short-enums", "-w", "-I", HANDOFF / "include", "-Xclang", "-fdump-record-layouts-simple", "-fsyntax-only", layout_c], "layout_arm")
    run([clang, "--target=wasm32", "-fsigned-char", "-fno-short-enums", "-w", "-I", G / "include", "-Xclang", "-fdump-record-layouts-simple", "-fsyntax-only", layout_c], "layout_wasm")
    def layout_lines(name):
        return [line.strip() for line in (LOG / (name + ".log")).read_text(encoding="utf-8").splitlines() if "Alignment" not in line]
    assert layout_lines("layout_arm") == layout_lines("layout_wasm"), "Original ARM and wasm32 structure layouts differ"
    if not (G / ".windows-xform.done").exists():
        run([sys.executable, "engine/tools/xform.py", G], "transform")
        (G / ".windows-xform.done").write_text("upstream transform complete\n")
    run([sys.executable, "engine/tools/mk_imports.py", G / "imports.txt"], "imports")
    run([sys.executable, "engine/tools/mk_autostubs.py", G / "imports.txt", G / "autostubs.c"], "autostubs")
    inc = ["-I", G / "include", "-I", G, "-I", "engine/rt"]
    def build_game(f):
        obj = B / "wobj" / (f.stem + ".o")
        if obj.exists() and obj.stat().st_mtime > f.stat().st_mtime:
            return
        p = subprocess.run([str(x) for x in [clang] + GAME + inc + ["-c", f, "-o", obj]], cwd=REPO, env=ENV, capture_output=True, text=True)
        if p.returncode:
            (LOG / ("game_" + f.stem + ".log")).write_text(p.stderr, encoding="utf-8")
            raise RuntimeError(f.name + ": " + p.stderr[-3000:])
    files = sorted((G / "game").glob("*.c"))
    print("Compiling", len(files), "game C files", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for i, _ in enumerate(pool.map(build_game, files), 1):
            if i % 100 == 0:
                print("Game objects", i, "/", len(files), flush=True)
    sources = list((REPO / "engine/rt").glob("*.c")) + list((REPO / "android-retouched/rt").glob("*.c"))
    sources += [G / "image_meta.c", G / "invoke_orig.c", G / "autostubs.c"]
    sources += list((REPO / "android-retouched/rt/game").glob("*.c"))
    for f in sources:
        flags = GAME + ["-DMGST_RETOUCHED"] if f.name in ("invoke_orig.c", "autostubs.c") or f.parent.name == "game" else RT
        run([clang] + flags + inc + ["--embed-dir=" + str(G), "-c", f, "-o", RO / (f.stem + ".o")], "rt_" + f.stem)
    module = B / "retouched/mgst.wasm"
    objects = sorted((B / "wobj").glob("*.o")) + sorted(RO.glob("*.o"))
    response = B / "wasm-objects.rsp"
    response.write_text("\n".join('"' + obj.as_posix() + '"' for obj in objects) + "\n", encoding="utf-8")
    run([linker, "--no-entry", "--global-base=1048576", "-z", "stack-size=2097152", "--initial-memory=134217728",
        "--max-memory=2147483648", "--export=__stack_pointer", "--export=__heap_base", "--export-table",
        "--growable-table", "--fatal-warnings", "-o", module, "@" + str(response)], "link_wasm")
    run([wasm2cs[0], "--module-name=mgst", "-o", OUTG / "mgst_w2c.c", module], "wasm2c")
    run([sys.executable, "engine/tools/patch_w2c.py", OUTG / "mgst_w2c.c"], "patch_arithmetic")
    (BASE / "wasm-windows.ready").write_text(str(module) + "\n")
    print("Recovered game compiled to native C:", OUTG / "mgst_w2c.c", flush=True)

if __name__ == "__main__":
    main()
