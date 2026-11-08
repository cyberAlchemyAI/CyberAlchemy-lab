"""Independent pure v2 regression controls, no generated role execution."""
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

C = Path(__file__).resolve().parent.parent / "docker-chain-preparation-0002"
raw = (C / "prepare.py").read_bytes()
if hashlib.sha256(raw).hexdigest() != "d8f744bd5afe4cfe3f3b3979f49f4d07078f09dbadae89a7e9bc6d20013d0ba1":
    raise RuntimeError("selected source drift")
spec = importlib.util.spec_from_file_location("reviewed_prepare", C / "prepare.py")
m = importlib.util.module_from_spec(spec)
exec(compile(raw, str(C / "prepare.py"), "exec"), m.__dict__)
s = m.load_closed((C / "selection.json").read_bytes())
observations = []

def refusal(name, action):
    try:
        action()
    except ValueError:
        observations.append({"case": name, "result": "REFUSED"})
    else:
        raise RuntimeError("expected refusal: " + name)

for name in ("constructor", "phase_rebind", "hardener", "path_contract"):
    altered = copy.deepcopy(s)
    replacement = "compose" if name == "path_contract" else "path_contract"
    altered["inputs"][name] = copy.deepcopy(s["inputs"][replacement])
    refusal("coherent_wrong_dependency_binding_" + name, lambda: m.prepare(altered))

got = m.prepare(copy.deepcopy(s))
frozen = m.load_closed((C / "proposed-selection.json").read_bytes())
if got != frozen:
    raise RuntimeError("positive projection drift")
observations.append({"case": "exact_27_positive", "result": "PASS"})

for key, module_name in m.T35_MODULES.items():
    mod = sys.modules[module_name]
    old_path = mod.__file__
    try:
        mod.__file__ = str(C / "selection.json")
        refusal("redirected_module_path_" + key, m.checked_imported_closure)
    finally:
        mod.__file__ = old_path
m.checked_imported_closure()

for key in ("container_ready", "source_effect_ready", "fd_limit_verified",
            "scratch_capacity_verified"):
    altered = copy.deepcopy(s)
    altered["feasibility"][key] = True
    refusal("false_" + key, lambda: m.prepare(altered))

staged = m.role_stage.stage_rows(
    m.role_stage.DisposableLayout(
        family=m.PurePosixPath(s["layout"]["family"]),
        snapshot=m.PurePosixPath(s["layout"]["snapshot"]),
        instance=s["layout"]["instance"]),
    lambda name: m.checked_bytes(next(r for r in s["preimages"] if r["path"] == name)))
for row, stage in zip(got["roles"], staged, strict=True):
    recovered = m.apply_inverse(stage["bytes"], row["inverse_diff"]["patch"])
    if recovered != m.checked_bytes(row["preimage"]):
        raise RuntimeError("inverse mismatch")
observations.append({"case": "27_inverse_reconstructions", "result": "PASS"})
print(json.dumps({"schema": "independent-pure-probes/v1", "effect": "NONE",
                  "observations": observations}, indent=2))
