#!/usr/bin/env python3
"""Build the publishable GitHub folder (GIT_UPLOAD/) from the working repo
(LOG 2026-10-09).

Copies a CURATED set of tracked files - original tooling, analysis metadata,
verification results, documentation - keeping the repo layout (tools/,
analysis/, oracle/), so every script runs unchanged from the folder's root.
Never copied: game assets, the extracted app, decompiler output (recovered/),
the Ghidra database, firmware, emulator state, third-party texts (GameFAQs
guides), disassembly/decompiled snippets, logs with local paths.

Hand-maintained in GIT_UPLOAD/ and left alone: README.md, LICENSE,
.gitignore, reproduce.sh. Everything else under the managed directories is
regenerated (files no longer selected are removed).

  tools/make_github_folder.py [--out GIT_UPLOAD] [--check]
--check: list what would be published and exit.
"""
import argparse
import fnmatch
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# game screenshots (Konami's imagery) stay local; only the generated figures are published
NOTES_SKIP = {"screenshots"}
MANAGED = ("tools", "analysis", "oracle", "docs", "claude_notes")
KEEP = {"README.md", "LICENSE", ".gitignore", "reproduce.sh"}

INCLUDE = [
    "tools/*.py", "tools/*.sh",
    "tools/ghidra/*.java", "tools/ghidra/patches/*",
    "oracle/scripts/*", "oracle/patches/*",
    "analysis/symbols/*", "analysis/objc/*", "analysis/dynamic/*",
    "analysis/coverage/*", "analysis/notes/*", "analysis/port/*",
    "analysis/verification/*", "analysis/verification/v1/*",
]
EXCLUDE = [
    "tools/grant_autonomy.sh",                       # local agent permissions, not part of the toolkit
    "tools/read_mht.py",                             # reads saved third-party guide pages; not part of the pipeline
    "analysis/verification/*Walkthrough*", "analysis/verification/*Guide*",   # GameFAQs texts (third-party)
    "analysis/verification/guide_enemy_missions.json",                       # derived from those
    "analysis/notes/case_bodies.txt", "analysis/notes/rsg_disasm.txt",       # code / disassembly snippets
    "analysis/ghidra/*",                             # Ghidra database + logs (local paths)
    "analysis/claude_notes/*",                       # published at claude_notes/ instead
    # raw extracts of the binary: regenerated locally by reproduce.sh from the
    # user's own IPA; they carry the original developer's build path and verbatim
    # symbol-table dumps (public-release review, LOG 2026-10-11)
    "analysis/symbols/stabs_raw.txt", "analysis/symbols/symtab_full.txt", "analysis/symbols/code_symbols.txt",
    "analysis/symbols/object_files.txt", "analysis/symbols/source_files.txt", "analysis/symbols/source_tree_map.md",
    "analysis/symbols/cpp_symbols_demangled.txt",
    "analysis/symbols/function_map_v1.csv", "analysis/symbols/function_map_v210.csv",   # other game versions
    # raw code bytes / disassembly text of the binary (not needed by the pipeline)
    "analysis/notes/switch8_raw.tsv", "analysis/notes/switch_resolved.tsv", "analysis/verification/coverage_unconsumed.tsv",
    # notes on a third-party walkthrough video; game text extracted from the data tables
    "analysis/coverage/walkthrough_index.md", "analysis/verification/ground_truth.json",
    "analysis/notes/ipa_compat_2026-09-23.txt",      # lists other IPA versions' file names
]
# documentation surfaced under docs/ (copied in addition to their analysis/ path)
DOCS = {
    "docs/GATE_SIGNOFF.md": "analysis/verification/gate_signoff.md",
    "docs/STATUS.md": "analysis/verification/status.md",
    "docs/V0_AUDIT.md": "analysis/verification/v0_audit.md",
    "docs/V1_AUDIT.md": "analysis/verification/v1_audit.md",
    "docs/ADDRTIED_CHECK.md": "analysis/verification/addrtied_check.md",
    "docs/COVERAGE_AUDIT.md": "analysis/verification/coverage_audit.md",
    "docs/MUTATION_TEST.md": "analysis/verification/mutation_test.md",
    "docs/REBUILD.md": "analysis/verification/rebuild_check.md",
    "docs/TEST_COVERAGE.md": "analysis/verification/test_coverage.md",
    "docs/PLATFORM_API.md": "analysis/port/platform_api.md",
    "docs/PORT_REVIEW.md": "analysis/port/mgsport_review.md",
    "docs/GAMEPLAY_REFERENCE.md": "analysis/verification/GAMEPLAY_REFERENCE.md",
    "docs/MACHO_LOADCOMMANDS.txt": "analysis/notes/macho_loadcommands.txt",
}
CARRY = ["docs/FORMATS.md"]          # already in GIT_UPLOAD/docs, hand-maintained


def tracked():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
    return [f for f in out if f]


def selected():
    files = []
    for f in tracked():
        if not any(fnmatch.fnmatch(f, p) for p in INCLUDE):
            continue
        if any(fnmatch.fnmatch(f, p) for p in EXCLUDE):
            continue
        files.append(f)
    return sorted(files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "GIT_UPLOAD"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    files = selected()
    docs = {k: v for k, v in DOCS.items() if os.path.exists(os.path.join(ROOT, v))}
    if a.check:
        for f in files:
            print(f)
        for k, v in docs.items():
            print("%s <- %s" % (k, v))
        print("%d files + %d docs" % (len(files), len(docs)))
        return
    out = a.out
    os.makedirs(out, exist_ok=True)
    keep_docs = {os.path.join(out, c): open(os.path.join(out, c), "rb").read()
                 for c in CARRY if os.path.exists(os.path.join(out, c))}
    want = set(files) | set(docs)
    nroot = os.path.join(ROOT, "analysis/claude_notes")
    for dp, dn, fn in os.walk(nroot):
        dn[:] = [d for d in dn if d not in NOTES_SKIP]
        for f in fn:
            want.add(os.path.join("claude_notes", os.path.relpath(os.path.join(dp, f), nroot)))
    # remove managed files no longer selected (only inside MANAGED dirs)
    removed = 0
    for d in MANAGED:
        base = os.path.join(out, d)
        for dp, dn, fn in os.walk(base):
            for f in fn:
                rel = os.path.relpath(os.path.join(dp, f), out)
                if rel not in want and rel not in CARRY:
                    os.remove(os.path.join(dp, f))
                    removed += 1
    for f in files:
        dst = os.path.join(out, f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, f), dst)
    for k, v in docs.items():
        dst = os.path.join(out, k)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, v), dst)
    # claude_notes/: the write-up and its generated figures (tools/make_claude_notes.py)
    notes = os.path.join(ROOT, "analysis/claude_notes")
    if os.path.isdir(notes):
        for dp, dn, fn in os.walk(notes):
            dn[:] = [d for d in dn if d not in NOTES_SKIP]
            for f in fn:
                rel = os.path.relpath(os.path.join(dp, f), notes)
                dst = os.path.join(out, "claude_notes", rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(os.path.join(dp, f), dst)
    for p, data in keep_docs.items():
        open(p, "wb").write(data)
    # empty directories left behind
    for d in MANAGED:
        for dp, dn, fn in sorted(os.walk(os.path.join(out, d)), key=lambda x: -len(x[0])):
            if not os.listdir(dp):
                os.rmdir(dp)
    print("GitHub folder %s: %d files, %d docs, %d stale removed" % (out, len(files), len(docs), removed))


if __name__ == "__main__":
    sys.exit(main())
