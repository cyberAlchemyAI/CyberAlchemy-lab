#!/usr/bin/env python3
"""Read-only intake/reuse inventory, emits only inside this candidate directory."""
import collections
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[4]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def audit():
    registry_path = LAB / "authority/definitions/registry.json"
    registry = json.loads(registry_path.read_text())
    baseline = json.loads((LAB / "docs/plans/definition-formal-assurance/source-baseline.json").read_text())
    entries = {e["definition_id"] + "@" + e["version"]: e for e in registry["entries"]}
    assert len(entries) == len(registry["entries"]), "duplicate version identity"
    # rg enumerates the repository's implementation, validation, candidates,
    # and historical trees. Do not treat an index or one canonical doc as full coverage.
    names = subprocess.check_output(["rg", "--files", "--hidden", "-g", "!.git/**", "-g", "!.arcanum/**"], cwd=LAB, text=True).splitlines()
    corpus = []
    native_suffixes = {".lean", ".smt2", ".tla", ".alloy", ".als", ".dfy", ".v", ".agda"}
    for name in sorted(names):
        path = LAB / name
        if path.is_relative_to(HERE):
            continue
        if path.suffix in native_suffixes or (path.suffix in {".json", ".ts", ".py", ".mjs", ".md"} and re.search(r"formal|theorem|proof|assurance|binding", name, re.I)):
            corpus.append({"path": name, "sha256": sha(path), "native_source": path.suffix in native_suffixes,
                           "text": path.read_text(errors="replace")})
    queue, mismatches = [], []
    for identity, version_ref in sorted(registry["current_lookup"].items()):
        entry = entries[version_ref]
        source_path = LAB / entry["path"]
        source = json.loads(source_path.read_text())
        observed = sha(source_path)
        bound = observed == entry["sha256"] and source["definition_id"] == identity and source["version"] == entry["version"]
        if not bound:
            mismatches.append(identity)
        pattern = re.compile(r"(?<![\w.-])" + re.escape(identity) + r"(?![\w.-])")
        related = [{"path": f["path"], "sha256": f["sha256"], "native_source": f["native_source"]}
                   for f in corpus if pattern.search(f["text"])]
        sf = source["voices"]["scientific_formal"]
        queue.append({"definition_id": identity, "version_ref": version_ref, "term": entry["term"],
                      "source_path": entry["path"], "source_sha256": entry["sha256"], "observed_sha256": observed,
                      "source_binding_status": "verified" if bound else "stale",
                      "effective_status": entry["lifecycle_state"], "source_label_ceiling": source.get("claim_ceiling"),
                      "formal_voice_expression": bool(sf.get("formal_expression")),
                      "expression_sha256": hashlib.sha256(sf.get("formal_expression", "").encode()).hexdigest(),
                      "related_artifacts": related, "related_artifact_meaning": "textual identity mention, not proof coverage",
                      "existing_formalization_assessment": "source-prose-expression; no verified current semantic provider binding located",
                      "source_fidelity": "not-reviewed", "non_collapse": "not-run", "consistency": "not-run",
                      "pilot_translation": "candidate-partial" if identity in {"cal.definition.authority", "cal.definition.provenance", "cal.definition.governance-axis-independence-invariant"} else "missing",
                      "next_action": "review and extend partial interpretation" if identity in {"cal.definition.authority", "cal.definition.provenance", "cal.definition.governance-axis-independence-invariant"} else "author explicit signature, dependencies, meaning and obligations"})
    baseline_current = (baseline["registry_sha256"] == sha(registry_path) and
                        {x["version_ref"] for x in baseline["definitions"]} == set(registry["current_lookup"].values()))
    result = {"schema_version": "definition-assurance-coverage/v1-candidate", "authority_effect": "none",
              "registry_sha256": sha(registry_path), "intake_current": baseline_current,
              "version_count": len(entries), "current_identity_count": len(queue), "source_binding_mismatches": mismatches,
              "formal_voice_expression_count": sum(q["formal_voice_expression"] for q in queue),
              "verified_current_mechanized_semantic_proof_count": 0, "owner_reviewed_translation_count": 0,
              "partial_pilot_translation_count": 3, "missing_translation_count": len(queue) - 3,
              "search": {"enumerator": "rg --files --hidden, excluding Git and generated Arcanum indexes",
                         "selection": "native formal languages plus formal/theorem/proof/assurance/binding paths",
                         "assessed_artifact_count": len(corpus), "native_artifact_count": sum(f["native_source"] for f in corpus),
                         "limit": "Textual identity search and manual reuse audit. No theorem replay; undiscovered indirect mappings remain possible.",
                         "artifacts": [{k: v for k, v in f.items() if k != "text"} for f in corpus]},
              "queue": queue, "full_combined_theory": "not-run: missing translations and dependency classifications"}
    dump("coverage.json", result)
    tools = {name: shutil.which(name) for name in ("python3", "lean", "lake", "z3", "cvc5", "java", "souffle")}
    dump("tooling.json", {"authority_effect": "none", "path_tools": tools, "python_version": sys.version,
                          "python_executable_sha256": sha(sys.executable),
                          "extra_locations_checked": ["/home/vlad_/.elan", "/home/vlad_/.local/share", "/opt", "/home/vlad_/projects/domainspec-core/.formal-tools"],
                          "decision": "Python finite model enumerator; no installation needed",
                          "limitation": "This is a custom trusted finite checker, not an SMT provider or mechanized proof kernel."})
    print(json.dumps({k: result[k] for k in ("intake_current", "version_count", "current_identity_count", "source_binding_mismatches", "formal_voice_expression_count", "partial_pilot_translation_count", "missing_translation_count")}))
    return 0 if baseline_current and not mismatches else 1


if __name__ == "__main__":
    raise SystemExit(audit())
