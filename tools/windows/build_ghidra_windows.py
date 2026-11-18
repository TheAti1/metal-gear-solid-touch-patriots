"""Build the pinned, patched decompiler locally for Windows without changing installed Ghidra."""
from pathlib import Path
import concurrent.futures
import hashlib
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"D:\Patriots_MGS_Touch_PC")
GHIDRA = BASE / "tools/ghidra_11.3.2_PUBLIC"
REPO = BASE / "mgs-decomp"
WORKSPACE = Path(__file__).resolve().parents[2]
TC = WORKSPACE / "dependencies/llvm-mingw/bin"
NINJA = WORKSPACE / "dependencies/ninja.exe"
PATCH = Path(r"C:\Program Files\Git\usr\bin\patch.exe")
REL = Path("Ghidra/Features/Decompiler/src/decompile/cpp")

def run(args, cwd, log):
    print("Running", Path(str(args[0])).name, "log:", log, flush=True)
    with Path(log).open("w", encoding="utf-8") as output:
        p = subprocess.run([str(x) for x in args], cwd=cwd, stdout=output, stderr=subprocess.STDOUT)
    if p.returncode:
        print(Path(log).read_text(encoding="utf-8", errors="replace")[-6000:], flush=True)
        raise RuntimeError(str(args[0]) + " failed: " + str(p.returncode))

def main():
    while not (GHIDRA / "support/analyzeHeadless.bat").exists():
        time.sleep(15)
    # Extraction can still be completing: the upstream source is near the end of the ZIP.
    while not (GHIDRA / REL / "Makefile").exists():
        time.sleep(5)
    patchroot = REPO / "build/ghidra-decompile-src"
    src = patchroot / REL
    if not (patchroot / ".patched").exists():
        import shutil
        shutil.copytree(GHIDRA / REL, src, dirs_exist_ok=True)
        for patch in sorted((REPO / "tools/ghidra/patches").glob("*.patch")):
            with patch.open("rb") as inp:
                subprocess.run([str(PATCH), "-p1", "--forward", "--batch", "-i", str(patch)],
                               cwd=patchroot, check=True)
        (patchroot / ".patched").write_text("Ghidra 11.3.2: upstream MGS Touch numerical fixes\n")
    make = (src / "Makefile").read_text().replace("\\\n", " ")
    names = []
    for group in ("CORE", "DECCORE", "GHIDRA"):
        value = re.search(r"^" + group + r"\s*=([^\n]+)", make, re.M).group(1)
        names += [x for x in value.split() if re.fullmatch(r"[A-Za-z0-9_]+", x)]
    names += [p.stem for p in src.glob("coreext_*.cc")]
    names += [p.stem for p in src.glob("ghidraext_*.cc")]
    names = sorted(set(names))
    assert all((src / (n + ".cc")).is_file() for n in names), names
    cmake = """cmake_minimum_required(VERSION 3.20)
project(PatriotsPatchedDecompiler LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 11)
add_executable(decompile
""" + "\n".join('  "' + (src / (n + ".cc")).as_posix() + '"' for n in names) + """
)
target_compile_definitions(decompile PRIVATE _WINDOWS NOMINMAX)
target_compile_options(decompile PRIVATE -O2 -w)
target_link_options(decompile PRIVATE -static)
"""
    (patchroot / "CMakeLists.txt").write_text(cmake, encoding="utf-8")
    build = patchroot / "win64"
    env = os.environ.copy()
    os.environ["PATH"] = str(TC) + os.pathsep + env["PATH"]
    run(["cmake", "-S", patchroot, "-B", build, "-G", "Ninja",
         "-DCMAKE_MAKE_PROGRAM=" + NINJA.as_posix(),
         "-DCMAKE_CXX_COMPILER=" + (TC / "clang++.exe").as_posix(),
         "-DCMAKE_BUILD_TYPE=Release"], REPO, patchroot / "configure-windows.log")
    run(["cmake", "--build", build, "--parallel", "6"], REPO, patchroot / "build-windows.log")
    dest = GHIDRA / "Ghidra/Features/Decompiler/os/win_x86_64/decompile.exe"
    import shutil
    original = dest.with_suffix(".original.exe")
    if not original.exists():
        shutil.copy2(dest, original)
    shutil.copy2(build / "decompile.exe", dest)
    (BASE / "patched-ghidra.sha256").write_text(hashlib.sha256(dest.read_bytes()).hexdigest() + "  " + str(dest) + "\n")
    print("Patched Windows Ghidra ready:", dest, flush=True)

if __name__ == "__main__":
    main()
