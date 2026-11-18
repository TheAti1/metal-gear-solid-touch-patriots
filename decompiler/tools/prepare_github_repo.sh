#!/usr/bin/env bash
# Stage the public GitHub repository from GIT_UPLOAD/ (LOG 2026-10-10).
#
#   tools/prepare_github_repo.sh [DEST]     (default build/github-repo)
#
# 1. regenerates GIT_UPLOAD/ (tools/make_github_folder.py)
# 2. copies it to DEST and creates a FRESH git repository there with one
#    commit - no history from this working repo, so nothing that was ever
#    tracked here (and later removed) can reach GitHub
# 3. safety checks: no game data / decompiled code / binaries / third-party
#    texts / personal paths; size limits
# It never pushes. To publish (your step):
#   cd DEST && git remote add origin git@github.com:<you>/<repo>.git && git push -u origin main
set -euo pipefail
cd "$(dirname "$0")/.."
DEST=${1:-build/github-repo}
python3 tools/make_github_folder.py
[[ -e $DEST ]] && { echo "$DEST exists - remove it first (or pass another path)"; exit 2; }
mkdir -p "$DEST"
cp -a GIT_UPLOAD/. "$DEST/"

fail=0
check() { if [[ -n "$2" ]]; then echo "BLOCKED ($1):"; echo "$2" | head -20; fail=1; fi; }
# screenshots and figures of the write-up (claude_notes/) are the only images allowed
check "game data / binaries" "$(cd "$DEST" && find . -path ./claude_notes -prune -o -type f \( -iname '*.ipa' -o -iname '*.caf' -o -iname '*.png' -o -iname '*.bmp' \
    -o -iname '*.al' -o -iname '*.rl' -o -iname '*.data' -o -iname '*.flac' -o -iname '*.ogg' -o -name 'MGSTUS' \
    -o -iname '*.bin' -o -iname '*.o' -o -iname '*.elf' -o -iname '*.bundle' \) -print )"
check "decompiled code" "$(cd "$DEST" && find . -path '*recovered*' -o -path '*PORT_HANDOFF*' -o -name 'functions.jsonl' | head)"
check "third-party texts" "$(cd "$DEST" && find . -type f \( -iname '*walkthrough*.txt' -o -iname '*guide*.txt' -o -iname '*.mht' -o -name 'guide_enemy_missions.json' \))"
# any text file: a real home directory (/home/<user>, /Users/<user>) - the original
# developer's build root from STABS included (raw dumps are excluded for that reason)
check "personal paths" "$(grep -rlE '/home/[a-z][a-z0-9_-]*|/Users/[a-z][A-Za-z0-9_]*/' "$DEST" --exclude-dir=.git \
    --exclude='*.png' --exclude='*.svg' 2>/dev/null || true)"
check "large files (> 5 MB)" "$(find "$DEST" -type f -size +5M)"
if [[ $fail == 1 ]]; then echo "NOT staged: fix the items above"; rm -rf "$DEST"; exit 1; fi

cd "$DEST"
git init -q -b main
git add -A
git -c user.name="${GIT_AUTHOR_NAME:-mgstouch}" -c user.email="${GIT_AUTHOR_EMAIL:-mgstouch@users.noreply.github.com}" \
    commit -q -m "MGS Touch v2.3.0: verified decompilation toolkit (tools, metadata, results, walkthrough)"
echo "staged: $DEST  ($(git ls-files | wc -l) files, $(du -sh . --exclude=.git | cut -f1))"
echo "publish: cd $DEST && git remote add origin <url> && git push -u origin main"
