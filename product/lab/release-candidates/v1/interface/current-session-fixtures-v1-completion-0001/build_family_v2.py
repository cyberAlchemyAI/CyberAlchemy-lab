"""Stage a distinct, independently signed current fixture family from public recipes.

Every instance is an exclusive new output. This generator never edits a parent,
renews an old Assignment, transfers an old approval, or freezes a shared API.
Root must select and merge the actual construction-bound instance separately.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
INTERFACE = HERE.parent
ROOT = HERE.parents[5]
TEMPLATES = {
    "source": "source8-lesson-fixture-source-v4-action-0148",
    "reader": "source8-lesson-fixture-reader-v4-action-0148",
    "mapped": "source8-lesson-fixture-mapped-v1-action-0148",
    "context": "source8-lesson-fixture-context-v1-action-0148",
}
SOURCE_PARENT = INTERFACE / "current-participation-v8"
OLD_SOURCE_PIN = "cc484b86ba0e8a2d1e07f1e8d640db055250f5aa5075450c8e8b7acc7cdebf36"
OLD_PACKAGE_PIN = "c0a01500743d01c5b487b83b219b184fbc14259bc49dde2f36cad684a70e4f4f"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def binding(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path.read_bytes())}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True) + "\n")


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("closed recipe selector absent/ambiguous: " + old[:100])
    return text.replace(old, new, 1)


def stage(instance):
    if re.fullmatch(r"[a-z][a-z0-9-]{0,48}", instance) is None:
        raise ValueError("bounded new instance name required")
    destination = HERE / "instances" / instance
    if destination.exists():
        raise ValueError("immutable construction instance already exists")
    # These are independently selected original pins, not values supplied by a store.
    if sha((SOURCE_PARENT / "source-manifest.json").read_bytes()) != OLD_SOURCE_PIN:
        raise ValueError("original Source8 selection changed")
    if sha((SOURCE_PARENT / "packages/0001/manifest.json").read_bytes()) != OLD_PACKAGE_PIN:
        raise ValueError("original Source8 package changed")
    started = datetime.now(timezone.utc)
    expires = started + timedelta(hours=24)
    prefix = "completion-current-session-0001-" + instance
    index = []
    for role, template in TEMPLATES.items():
        folder = destination / role
        folder.mkdir(parents=True)
        for path in sorted((INTERFACE / template).glob("*.py")):
            # Old producer launch/freezer/qualification drivers encode their own
            # epochs. New bounded construction drivers are provided separately.
            if path.name in {"freeze.py", "produce.py", "qualify.py", "run_checks.py", "preflight.py"}:
                continue
            original = path.read_text()
            text = original
            text = text.replace("HERE.parents[5]", "HERE.parents[8]")
            text = text.replace("R03-source8-lesson-fixture-0208", prefix)
            text = text.replace("R03-source8-runtime-lesson-fixture-0208", prefix)
            text = text.replace("R03-source8-fixture-0208", prefix)
            text = text.replace("decision:R03-source8-fixture:", "decision:" + prefix + ":")
            text = text.replace("ontology:R03-controlled-Source8-lesson-fixture-projection:0208", "ontology:" + prefix + ":projection")
            text = text.replace("FixtureReader", "CurrentFixtureReader")
            text = text.replace("_cal_source8_controlled_fixture_mapping_reader_0208", "_cal_completion_" + instance.replace("-", "_") + "_mapping_reader")
            text = text.replace("_cal_source8_lesson_fixture", "_cal_completion_" + instance.replace("-", "_"))
            # Select external originals via the exact interface; select local
            # new family roles through the actual instance directory.
            for external in ["custody-correction-v4", "current-participation-v8", "fact-read-scope-v1", "api-integration-v12"]:
                text = text.replace("HERE.parent/'" + external, "(ROOT/'product/lab/release-candidates/v1/interface')/'" + external)
            text = text.replace("ADAPTER_ROOT.parent/'" + TEMPLATES["source"] + "'", "ADAPTER_ROOT.parent/'source'")
            for selected_role, old_name in TEMPLATES.items():
                text = text.replace("HERE.parent/'" + old_name, "HERE.parent/'" + selected_role)
            source_entry = (destination / "reader/reader.py").relative_to(ROOT).as_posix() + "#CurrentFixtureReader.open_signed"
            text = text.replace("product/lab/release-candidates/v1/interface/source8-lesson-fixture-reader-v4-action-0148/reader.py#CurrentFixtureReader.open_signed", source_entry)
            context_entry = (destination / "context/build.py").relative_to(ROOT).as_posix() + "#generate"
            text = text.replace("str((HERE.parent/'source8-lesson-fixture-context-v1-action-0148/build.py').relative_to(ROOT))+'#generate'", repr(context_entry))
            text = text.replace("Exact source8-lesson-fixture-context-v1-action-0148 and fact-read-scope-v1 runtime", "Exact " + (destination / "context").relative_to(ROOT).as_posix() + " and fact-read-scope-v1 runtime")
            if role == "source" and path.name == "base.py":
                begin = text.index("def episode():\n")
                end = text.index("def cut(view):\n", begin)
                text = text[:begin] + '''def episode():
    value=load(HERE/'episode-contract.json')
    require(value['authority_effect']=='none' and value['actual_owner_outcome'] is None and value['fixture_only'] is True,'fixture grants no human or original authority')
    start=datetime.fromisoformat(value['not_before']);end=datetime.fromisoformat(value['expires_at'])
    require(start.tzinfo is not None and end.tzinfo is not None and end-start==timedelta(hours=24),'independently fixed24h source period required')
    require(value['original_Source8_period_binding']==binding((ROOT/'product/lab/release-candidates/v1/interface')/'current-participation-v8/packages/0001/period.json'),'original period provenance differs')
    require(value['original_Assignment_renewed'] is False and value['original_signer_restored'] is False and value['Session_memory_rehydrated'] is False,'old authority or memory cannot be restored')
    require(value['principal_ref']==records_identity('PRINCIPAL') and value['assignment_version_ref']==records_identity('ASSIGNMENT')+'@'+records_identity('VERSION'),'independent current identities differ')
    return value
def records_identity(name):
    from . import records
    return getattr(records,name)
''' + text[end:]
            if role == "source" and path.name == "build.py":
                text = text.replace("Distinct controlled fixture period capped at original Source8 end; no original renewal or human outcome.", "Distinct independently signed24h construction fixture; original source period remains expired and unchanged.")
                text = text.replace("source8-lesson-fixture-context-v1-action-0148/build.py", (destination / "context/build.py").relative_to(INTERFACE).as_posix())
            ast.parse(text)
            target = folder / path.name
            write(target, text)
            index.append({"role": role, "original": binding(path), "new": binding(target), "changed": text != original})
        if role == "context":
            # Original protocol resource IDs/schema semantics are retained. The
            # new generator's actual code/reader binding is authored separately.
            template_root = INTERFACE / template
            resources = [template_root / "lifetime-policy.json"] + sorted((template_root / "protocols").glob("*.json"))
            for resource in resources:
                target = folder / resource.relative_to(template_root)
                write(target, resource.read_text())
                index.append({"role": role, "original": binding(resource), "new": binding(target), "changed": False})
    records = destination / "source/records.py"
    constants = {}
    for node in ast.parse(records.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                constants[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    # Prefix-based identities are independently declared from this generator,
    # never obtained from a runtime class or selected store envelope.
    version = constants["VERSION"]
    declaration = {
        "schema_version": "lab-current-source-fixture-episode/v1-candidate",
        "period_ref": "protocol:" + prefix + "-period/v1",
        "not_before": started.isoformat(), "expires_at": expires.isoformat(),
        "principal_ref": "principal:" + prefix,
        "assignment_version_ref": "agent-assignment:" + prefix + "@" + version,
        "original_Source8_period_binding": binding(SOURCE_PARENT / "packages/0001/period.json"),
        "old_episode_period_binding": binding(INTERFACE / "custody-participation-v1/packages/0001/period.json"),
        "original_Assignment_renewed": False, "original_signer_restored": False,
        "Session_memory_rehydrated": False, "fixture_only": True,
        "authority_effect": "none", "actual_owner_outcome": None,
        "reader_grant_max_seconds": 1800, "session_max_seconds": 900,
    }
    write(destination / "source/episode-contract.json", declaration)
    selection = {
        "schema_version": "lab-current-session-construction-selection/v1-candidate",
        "status": "staged-unqualified", "instance": instance,
        "public_source_name": "completion-current-participation:" + instance,
        "source_directory": (destination / "source").relative_to(ROOT).as_posix(),
        "reader_directory": (destination / "reader").relative_to(ROOT).as_posix(),
        "reader_class": "CurrentFixtureReader", "reader_entrypoint_ref": source_entry,
        "context_directory": (destination / "context").relative_to(ROOT).as_posix(),
        "context_entrypoint_ref": context_entry, "prefix": prefix,
        "episode_binding": binding(destination / "source/episode-contract.json"),
        "original_source_binding": binding(SOURCE_PARENT / "source-manifest.json"),
        "original_package_binding": binding(SOURCE_PARENT / "packages/0001/manifest.json"),
        "template_rows": index, "generator_binding": binding(Path(__file__).resolve()),
        "authority_effect": "none", "actual_owner_outcome": None,
        "original_approvals_transferred": False, "shared_API_qualified": False,
    }
    write(destination / "construction-selection.json", selection)
    return selection


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instance", required=True)
    args = parser.parse_args()
    value = stage(args.instance)
    print(json.dumps({"result": "STAGED-UNQUALIFIED", "selection": value["source_directory"], "template_files": len(value["template_rows"])}))


if __name__ == "__main__":
    main()
