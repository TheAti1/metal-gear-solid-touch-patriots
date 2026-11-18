"""Resumable native-Windows equivalent of the upstream static Ghidra pipeline."""
from pathlib import Path
import json
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(r"D:\Patriots_MGS_Touch_PC")
REPO = BASE / "mgs-decomp"
GHIDRA = BASE / "tools/ghidra_11.3.2_PUBLIC"
HEADLESS = GHIDRA / "support/analyzeHeadless.bat"
WORKSPACE = Path(__file__).resolve().parents[2]
TC = WORKSPACE / "dependencies/llvm-mingw/bin"
LOG = REPO / "build/ghidra-build-logs"
LOG.mkdir(parents=True, exist_ok=True)
ENV = os.environ.copy()
ENV.update(PYTHONUTF8="1", JAVA_HOME=r"C:\Program Files\Java\jdk-21.0.10")
ENV["PATH"] = str(TC) + os.pathsep + ENV["JAVA_HOME"] + r"\bin" + os.pathsep + ENV["PATH"]

def run(args, name, check_errors=False):
    path = LOG / (name + ".log")
    stamp = LOG / (name + ".done")
    if stamp.exists():
        print("Already done:", name, flush=True)
        return
    print(time.strftime("%H:%M:%S"), name, flush=True)
    with path.open("w", encoding="utf-8") as output:
        result = subprocess.run([str(x) for x in args], cwd=REPO, env=ENV,
                                stdout=output, stderr=subprocess.STDOUT)
    text = path.read_text(encoding="utf-8", errors="replace")
    bad = ("REPORT SCRIPT ERROR" in text or "Error running script" in text or
           "Failed to compile" in text or "SCRIPT FAILED" in text)
    if result.returncode or (check_errors and bad):
        print(text[-7000:], flush=True)
        raise RuntimeError(name + " failed; see " + str(path))
    stamp.write_text(time.strftime("%Y-%m-%d %H:%M:%S"), encoding="utf-8")
    print(text[-900:], flush=True)

def headless_args():
    return [HEADLESS, "analysis/ghidra", "MGST", "-max-cpu", "4", "-scriptPath", "tools/ghidra"]

def main():
    while not (BASE / "patched-ghidra.sha256").exists():
        time.sleep(15)
    external = REPO / "tools/ghidra/ApplyExternalPrototypes.java"
    text = external.read_text(encoding="utf-8")
    text = text.replace("/opt/ghidra/Ghidra/Features/Base/data/typeinfo/mac_10.9/mac_osx.gdt",
                        (GHIDRA / "Ghidra/Features/Base/data/typeinfo/mac_10.9/mac_osx.gdt").as_posix())
    external.write_text(text, encoding="utf-8")
    (REPO / "analysis/ghidra").mkdir(parents=True, exist_ok=True)
    run(headless_args() + ["-import", "work/extracted/Payload/MGSTUS.app/MGSTUS",
        "-preScript", "ApplyMgstSymbols.java", "analysis/symbols/ghidra_symbols.tsv"], "00_import", True)
    script = (REPO / "tools/build_ghidra_project.sh").read_text(encoding="utf-8")
    for line in script.splitlines():
        m = re.match(r"step\s+(\S+)\s+(\S+\.java)(.*)", line)
        if not m:
            continue
        name, java, args = m.groups()
        args = args.strip().replace('"$LOGDIR/void_returns.tsv"', "build/ghidra-build-logs/void_returns.tsv")
        run(headless_args() + ["-process", "MGSTUS", "-noanalysis", "-postScript", java] + args.split(), name, True)
    run(headless_args() + ["-process", "MGSTUS", "-noanalysis", "-readOnly",
        "-postScript", "ExportMgstDecompilation.java", "recovered/decompiled", "120",
        "-postScript", "ExportCompilable.java", "recovered/compile",
        "-postScript", "DumpV1Facts.java", "analysis/verification/v1"], "23_export", True)
    # Ghidra's getC() emits CRLF on Windows; the token printer deliberately emits LF.
    # Normalize only that platform newline difference, then rerun the actual self-check.
    printer = REPO / "tools/ghidra/ExportCompilable.java"
    text = printer.read_text(encoding="utf-8")
    text = text.replace('plain.replaceAll(', 'plain.replace("\\r\\n", "\\n").replaceAll(')
    text = text.replace('getC().replaceAll(', 'getC().replace("\\r\\n", "\\n").replaceAll(')
    printer.write_text(text, encoding="utf-8")
    run(headless_args() + ["-process", "MGSTUS", "-noanalysis", "-readOnly",
        "-postScript", "ExportCompilable.java", "recovered/compile"], "23b_export_normalized", True)
    check = (LOG / "23b_export_normalized.log").read_text(encoding="utf-8")
    assert "printer self-check mismatches: 0" in check, "Token-printer self-check failed"
    data = REPO / "recovered/compile/functions.jsonl"
    funcs = [json.loads(line) for line in data.read_text(encoding="utf-8").splitlines()]
    assert sum(bool(f.get("c")) for f in funcs) == 1395, "Missing game functions"
    assert sum(f.get("c") is None for f in funcs) == 182, "Import-stub count changed"
    # Replace Linux binutils command names with the equivalent local LLVM tools.
    path = REPO / "tools/mgst_recompile.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace('"arm-none-eabi-objdump"', repr((TC / "llvm-objdump.exe").as_posix()))
    text = text.replace('"arm-none-eabi-ar"', repr((TC / "llvm-ar.exe").as_posix()))
    text = text.replace('(?P<file>[^:]+)', '(?P<file>.+?)')
    path.write_text(text, encoding="utf-8")
    run([sys.executable, "tools/mgst_recompile.py", "--jobs", "6"], "24_recompile")
    report = (REPO / "recovered/compile/compile_report.md").read_text(encoding="utf-8")
    print(report[:1600], flush=True)
    run([sys.executable, "tools/mgst_audit.py"], "25_static_audit")
    (BASE / "decompiled-windows.ready").write_text("1395 functions exported; inspect compile and audit logs\n")

if __name__ == "__main__":
    main()
