import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[4]
PREVIOUS = ROOT.parent / "0014-policy-carrier"
L1 = ROOT.parent / "0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability"
PACKAGE = ROOT / "artifact-types/authority-model/v1"


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def binding(path):
    return {"path": str(path.relative_to(LAB)), "sha256": sha(path)}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value
