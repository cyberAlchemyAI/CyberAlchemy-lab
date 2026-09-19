"""Shared paths and deterministic encoding for the reconstruction batch."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT.parents[4]
SOURCE = LAB.parent / "cyberAlchemy-v2"
PREVIOUS = ROOT.parent / "0003-review-led-reconstruction"
L0 = ROOT.parent / "0004-artifact-reconstruction-pipeline"
L1 = L0 / "layers/l1-semantic-repeatability"
KINDS = ("axiom", "premise", "hypothesis")


def load(path):
    return json.loads(path.read_text())


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode(value))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(path):
    return {"path": str(path.relative_to(LAB)), "sha256": sha(path)}


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def need(condition, message):
    if not condition:
        raise ValueError(message)
