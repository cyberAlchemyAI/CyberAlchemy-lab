#!/usr/bin/env python3
"""Byte-backed replay and exact coverage check of all 29 T10 local mappings."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
MATRIX = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10/all29-semantic-route-matrix-inactive-0002/MATRIX.json",
          "sha256": "67b3dc214a36a027469b0bfac863f27c79e7d62fd55aa8249d52dc3da8d1f22c"}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_selected(binding):
    rel = binding["path"]
    need(type(rel) is str and rel and not rel.startswith("/") and "\\" not in rel and
         ".." not in Path(rel).parts and str(Path(rel)) == rel,
         "unsafe selected path")
    path = ROOT / rel
    for ancestor in (path, *path.parents):
        if ancestor == ROOT.parent:
            break
        need(not stat.S_ISLNK(ancestor.lstat().st_mode), "linked selected path")
    before = path.stat()
    need(stat.S_ISREG(before.st_mode) and before.st_size < 32 * 1024 * 1024,
         "unbounded selected file")
    raw = path.read_bytes()
    after = path.stat()
    need(before == after and len(raw) == before.st_size and sha(raw) == binding["sha256"],
         "selected file bytes changed")
    return raw


def members_of(result):
    entries = result.get("entries")
    if entries is None:
        entries = [result]
    need(type(entries) is list and entries and
         result["selected_governed_model_representations"] == len(entries) and
         result.get("original_members_admitted", 0) == 0 and
         result["T10_complete"] is False and result["authority_effect"] == "none",
         "local result count or authority ceiling differs")
    seen = []
    for entry in entries:
        index = entry["member_index"]
        docs = entry["documents"]
        need(type(index) is int and entry["original_member_admitted"] is False and
             set(docs) == {"model", "implementation", "typed_relation"} and
             docs["model"]["kind"] == "governed-model" and
             docs["implementation"]["kind"] == "implementation" and
             docs["typed_relation"]["kind"] == "typed-relation" and
             all(body["authority_effect"] == "none" and body["lifecycle_state"] == "candidate"
                 for body in docs.values()),
             "local representation or original admission differs")
        seen.append(index)
    need(len(seen) == len(set(seen)), "duplicate members inside one selection")
    return seen


def validate_catalog(catalog):
    need(catalog["schema_version"] == "lab-T10-all29-local-catalog/v1" and
         catalog["matrix_binding"] == MATRIX and
         type(catalog["packages"]) is list and len(catalog["packages"]) == 14,
         "closed 14-package catalog required")
    seen = []
    selected = set()
    for item in catalog["packages"]:
        need(set(item) == {"runner", "result", "members"} and
             item["runner"]["path"] not in selected and
             item["result"]["path"] not in selected and
             item["runner"]["path"].endswith(("/select_model.py", "/select_models.py")) and
             item["result"]["path"].endswith("/RESULT.json") and
             Path(item["runner"]["path"]).parent == Path(item["result"]["path"]).parent and
             type(item["members"]) is list and item["members"] and
             all(type(index) is int and 0 <= index <= 28 for index in item["members"]),
             "catalog package or runner/result pairing differs")
        selected.update((item["runner"]["path"], item["result"]["path"]))
        seen += item["members"]
    need(len(seen) == len(set(seen)) == 29 and sorted(seen) == list(range(29)),
         "exact 29-member local coverage required")


def execute_captured(binding, raw):
    path = str(ROOT / binding["path"])
    child = ("import sys;p=sys.argv[1];b=sys.stdin.buffer.read();"
             "n={'__name__':'__main__','__file__':p};"
             "exec(compile(b,p,'exec',dont_inherit=True),n)")
    process = subprocess.run([sys.executable, "-I", "-B", "-c", child, path],
                             input=raw, cwd=ROOT, capture_output=True, timeout=180, check=False)
    need(process.returncode == 0,
         "captured selector refused: " + process.stderr.decode(errors="replace")[-500:])
    return process.stdout


def build():
    catalog_raw = (HERE / "CATALOG.json").read_bytes()
    catalog = json.loads(catalog_raw)
    validate_catalog(catalog)
    matrix = json.loads(read_selected(MATRIX))
    need([row["index"] for row in matrix["rows"]] == list(range(29)) and
         matrix["T10_complete"] is False and
         matrix["semantically_grounded_selected_representations"] == 0,
         "original matrix or claim ceiling differs")
    covered = []
    packages = []
    model_ids = set()
    for item in catalog["packages"]:
        runner_raw = read_selected(item["runner"])
        result_raw = read_selected(item["result"])
        observed_raw = execute_captured(item["runner"], runner_raw)
        need(observed_raw == result_raw, "fresh selector output differs from retained receipt")
        observed = json.loads(observed_raw)
        members = members_of(observed)
        need(members == item["members"] and
             [matrix["rows"][index]["member_ref"] for index in members] ==
             [entry["member_ref"] for entry in observed.get("entries", [observed])],
             "selected member identity differs")
        for entry in observed.get("entries", [observed]):
            model_id = entry["documents"]["model"]["node_id"]
            need(model_id not in model_ids, "duplicate local model identity")
            model_ids.add(model_id)
        need(read_selected(item["runner"]) == runner_raw and
             read_selected(item["result"]) == result_raw,
             "selected source changed during replay")
        covered += members
        packages.append({"members": members, "runner": item["runner"],
                         "result": item["result"], "fresh_exact_match": True})
    need(sorted(covered) == list(range(29)) and len(model_ids) == 29,
         "29 distinct local models required")
    return {"schema_version": "lab-T10-all29-local-aggregate/v1",
            "catalog_sha256": sha(catalog_raw), "matrix_binding": MATRIX,
            "packages": packages, "covered_member_indices": sorted(covered),
            "local_schema_valid_mappings": 29, "fresh_exact_matches": 14,
            "original_members_admitted": 0, "original_T10_complete": False,
            "local_mapping_complete": True, "authority_effect": "none",
            "runner_sha256": sha(Path(__file__).read_bytes()),
            "claim_ceiling": "All 29 original member indices have distinct, fresh-replayed schema-valid local classifications. Original GovernedModels remain refused; no owner meaning, admission, private use or runtime effects follow."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
