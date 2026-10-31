#!/usr/bin/env bash
# Usage: score.sh <workdir> <task_files_dir> <base_sha> <bench_mirror> <out_dir> <godot_bin>
# Scores an agent's workdir: restores pristine regression tests + GUT, adds the
# hidden tests, imports the project, runs both GUT suites, writes score.json.
set -euo pipefail

if [ "$#" -ne 6 ]; then
    echo "usage: $0 <workdir> <task_files_dir> <base_sha> <bench_mirror> <out_dir> <godot_bin>" >&2
    exit 2
fi
workdir=$1 task_files=$2 base_sha=$3 mirror=$4 out_dir=$5 godot=$6

if [ ! -x "$godot" ]; then
    echo "score.sh: godot binary not found or not executable: $godot" >&2
    exit 3
fi

mkdir -p "$out_dir"
out_dir=$(cd "$out_dir" && pwd)
project=$out_dir/project

# Clear results from any earlier attempt so stale files can't be read as current.
rm -rf "$project"
rm -f "$out_dir"/regression.xml "$out_dir"/hidden.xml "$out_dir"/score.json "$out_dir"/*.log

# 1. Fresh copy of the agent's work (no .git).
mkdir -p "$project"
rsync -a --delete --exclude '.git' "$workdir"/ "$project"/

# 2. Review Focus 1: the agent must not be able to edit the regression tests, GUT or
#    its config (.gutconfig.json can narrow runs or run pre/post scripts).
rm -rf "$project/tests/regression" "$project/addons/gut" "$project/.gutconfig.json"
restore=(tests/regression addons/gut)
if git -C "$mirror" cat-file -e "$base_sha:.gutconfig.json" 2>/dev/null; then
    restore+=(.gutconfig.json)
fi
git -C "$mirror" archive "$base_sha" "${restore[@]}" | tar -x -C "$project"

# 3. Hidden tests (the tests/ dir is optional: some tasks use score_extra.sh only).
rm -rf "$project/tests/hidden"
mkdir -p "$project/tests/hidden"
if [ -d "$task_files/tests" ]; then
    find "$task_files/tests" -maxdepth 1 -name '*.gd' -exec cp {} "$project/tests/hidden/" \;
fi

# Run a command under timeout; sets $rc (exit code) and $timed_out (true/false).
run_timed() {
    local secs=$1; shift
    rc=0
    timeout -k 10 "$secs" "$@" || rc=$?
    if [ "$rc" -eq 124 ] || [ "$rc" -eq 137 ]; then timed_out=true; else timed_out=false; fi
}

# 4. Import.
run_timed 300 "$godot" --headless --path "$project" --import >"$out_dir/import.log" 2>&1
import_exit=$rc import_timed_out=$timed_out

# 5. GUT suites, run separately so one hanging suite doesn't hide the other.
run_gut() {
    local name=$1
    run_timed 600 "$godot" --headless --path "$project" -s addons/gut/gut_cmdln.gd \
        "-gdir=res://tests/$name" -gexit "-gjunit_xml_file=$out_dir/$name.xml" \
        >"$out_dir/$name.log" 2>&1
}
run_gut regression
regression_exit=$rc regression_timed_out=$timed_out
run_gut hidden
hidden_exit=$rc hidden_timed_out=$timed_out

# 6. Optional task-specific scoring; it may overwrite hidden.xml.
# If it fails or times out, drop hidden.xml so hidden scores as None (fail), never
# a stale plain-GUT result.
extra_exit=null extra_timed_out=false
if [ -f "$task_files/score_extra.sh" ]; then
    run_timed 600 bash "$task_files/score_extra.sh" "$project" "$godot" "$out_dir" \
        >"$out_dir/extra.log" 2>&1
    extra_exit=$rc extra_timed_out=$timed_out
    if [ "$rc" -ne 0 ]; then rm -f "$out_dir/hidden.xml"; fi
fi

# 7. score.json
OUT_DIR=$out_dir \
IMPORT_EXIT=$import_exit IMPORT_TO=$import_timed_out \
REG_EXIT=$regression_exit REG_TO=$regression_timed_out \
HID_EXIT=$hidden_exit HID_TO=$hidden_timed_out \
EXTRA_EXIT=$extra_exit EXTRA_TO=$extra_timed_out \
python3 - <<'PY'
import json, os
from pathlib import Path

out = Path(os.environ["OUT_DIR"])
def xml(name):
    p = out / name
    return str(p) if p.is_file() else None
score = {
    "import_exit": int(os.environ["IMPORT_EXIT"]),
    "import_timed_out": os.environ["IMPORT_TO"] == "true",
    "import_log": str(out / "import.log"),
    "regression_exit": int(os.environ["REG_EXIT"]),
    "regression_timed_out": os.environ["REG_TO"] == "true",
    "regression_xml": xml("regression.xml"),
    "hidden_exit": int(os.environ["HID_EXIT"]),
    "hidden_timed_out": os.environ["HID_TO"] == "true",
    "hidden_xml": xml("hidden.xml"),
    "extra_exit": None if os.environ["EXTRA_EXIT"] == "null" else int(os.environ["EXTRA_EXIT"]),
    "extra_timed_out": os.environ["EXTRA_TO"] == "true",
}
(out / "score.json").write_text(json.dumps(score, indent=2) + "\n")
PY
