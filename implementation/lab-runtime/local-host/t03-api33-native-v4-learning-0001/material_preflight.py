"""Check the exact public-review JSON material without Source replay."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
API = ROOT / "product/lab/release-candidates/v1/interface/api-integration-v33-t03-one-lesson-native-v4-0004"
REF = "implementation/lab-runtime/local-host/working/api33-native-dispositions-independent-review-0003/REVIEW.md"
RAW_SHA = "d76090f5e8e501282c9234b00cad68b8d53a36b81be8549cc119c990615b3c29"


def main():
    name = "_cal_t03_v4_review_material_preflight"
    spec = importlib.util.spec_from_file_location(name, API / "__init__.py", submodule_search_locations=[str(API)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    P = __import__(name + ".protocol", fromlist=["compact"])
    F = __import__(name + ".fixtures", fromlist=["provision"])
    W = __import__(name + ".workspace", fromlist=["validate_scope"])
    raw = (ROOT / REF).read_bytes()
    if hashlib.sha256(raw).hexdigest() != RAW_SHA:
        raise ValueError("selected public review changed")
    encoded = P.compact(raw.decode("utf-8"))
    if P.frame_parse(encoded).encode("utf-8") != raw:
        raise ValueError("review JSON representation is not exact")
    with tempfile.TemporaryDirectory(prefix="cal-t03-review-material-", dir="/tmp") as temporary:
        folder = Path(temporary)
        folder.chmod(0o700)
        _, path, _ = F.provision(folder, materials={REF: encoded})
        _, manifest = W.validate_scope(P.frame_parse(path.read_bytes()))
        if manifest["materials"] != [{"ref": REF, "path": "inputs/input_0.json",
                                      "sha256": hashlib.sha256(encoded).hexdigest()}]:
            raise ValueError("workspace review material differs")
    return {"status": "pass", "raw_review_sha256": RAW_SHA,
            "encoded_review_sha256": hashlib.sha256(encoded).hexdigest(),
            "raw_roundtrip": True, "workspace_materials": 1,
            "owned_temporary_fixture_removed": not folder.exists()}


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, indent=2))
