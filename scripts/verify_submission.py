"""Static release gates for the PriorWordBind source bundle."""

from pathlib import Path
import ast
import hashlib
import re


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "contracts" / "PriorWordBind.py"
HASH_FILE = ROOT / "SOURCE_SHA256.txt"


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


text = SOURCE.read_text(encoding="utf-8")
lines = text.splitlines()

require(lines[0] == "# v0.2.16", "version header must be first")
require(
    lines[1]
    == '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }',
    "Depends header must be second",
)
require(lines[2] == "", "third line must be blank")
require(lines[3] == "from genlayer import *", "v0.2 import must be fourth")
ast.parse(text, filename=str(SOURCE))

for forbidden in (
    "import genlayer as gl",
    "gl.contract.Contract",
    "gl.vm.run_nondet(",
    "gl.message.raw",
    "datetime.now",
    "time.time",
    "gl.nondet.web.render",
    "emit_transfer",
    "payable",
    "gl.evm",
):
    require(forbidden not in text, "forbidden construct: " + forbidden)

for required in (
    "class PriorWordBind(gl.Contract):",
    "positions: TreeMap[str, PositionRecord]",
    "followups: TreeMap[str, FollowupRecord]",
    "MAX_MODEL_CALLS_PER_POSITION = 5",
    '"Position has already been walked back"',
    '"Position is still standing"',
    '"Model call limit reached"',
    'return " ".join(value.split())',
    "gl.vm.run_nondet_unsafe(",
    'response_format="json"',
):
    require(required in text, "missing invariant: " + required)

require(
    text.count("gl.vm.run_nondet_unsafe(") == 1,
    "contract must have one nondeterministic call site",
)
require(
    "self.positions = TreeMap" not in text,
    "storage map initialized in __init__",
)
require(
    "self.followups = TreeMap" not in text,
    "storage map initialized in __init__",
)

write_methods = re.findall(
    r"@gl\.public\.write\s+def\s+(\w+)",
    text,
)
view_methods = re.findall(
    r"@gl\.public\.view\s+def\s+(\w+)",
    text,
)
require(
    write_methods
    == [
        "open_position",
        "register_reliance",
        "submit_followup",
        "withdraw_reliance",
    ],
    "unexpected write surface: " + repr(write_methods),
)
require(
    view_methods
    == [
        "get_position",
        "get_followup",
        "get_followups",
        "get_reliance",
        "get_reliances",
        "get_rubric",
        "get_limits",
    ],
    "unexpected view surface: " + repr(view_methods),
)

for method in view_methods:
    require(
        not method.startswith(("preview_", "classify_", "dry_run_")),
        "forbidden preview view: " + method,
    )

submit_start = text.index("    def submit_followup(")
submit_end = text.index("    @gl.public.write\n    def withdraw_reliance")
submit = text[submit_start:submit_end]
require(
    submit.index('position.state != "STANDING"')
    < submit.index("self._classify("),
    "walkback guard must precede model",
)
require(
    submit.index("MAX_MODEL_CALLS_PER_POSITION")
    < submit.index("self._clean_followup_text"),
    "model cap must precede text/model work",
)
require(
    submit.index('"Follow-up already exists"')
    < submit.index("self._classify("),
    "duplicate guard must precede model",
)

digest = hashlib.sha256(
    SOURCE.read_bytes().replace(b"\r\n", b"\n").rstrip(b"\n") + b"\n"
).hexdigest()
if HASH_FILE.exists():
    declared = HASH_FILE.read_text(encoding="utf-8").strip().split()[0]
    require(digest == declared, "SOURCE_SHA256.txt does not match contract")

print("PASS: static release gates")
print(
    "writes="
    + str(len(write_methods))
    + " views="
    + str(len(view_methods))
    + " sha256="
    + digest
)
