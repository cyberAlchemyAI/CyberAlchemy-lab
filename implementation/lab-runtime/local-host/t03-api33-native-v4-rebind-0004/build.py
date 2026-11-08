"""Bind the preclaim API successor to the signed native-v4 one-Lesson cut."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "product/lab/release-candidates/v1/interface"
OLD = BASE / "api-integration-v33-t35-session-preflight-0002"
NEW = BASE / "api-integration-v33-t03-one-lesson-native-v4-0004"
FAMILY = ROOT / "implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-d95e3b741ca86f02"
CONTEXT = FAMILY / "context-native-v4-0001"
HOST = BASE / "lesson-host-composition-v46-completion-0001"
OLD_SHA = "094d456fb4cddca37a83b03f1562b26afc3527d98d4bede752a69a0f63b7884f"
OLD_ID = "947e6c2a5b3d10f8"
NEW_ID = "d95e3b741ca86f02"
OLD_PINS = {
    "source/packages/0001/manifest.json": "da64e865676b7001fc8d5b8dfcfcdbaff8f3a041849649f49afc3df92ab4d901",
    "mapped/packages/0001/manifest.json": "a0b3299db97cc50cdc1b0200ea4a063296ce6323671bf0052a2121d0fe67a270",
    "mapped/packages/0001/mapping.json": "6c64958278d3841d6ffe66b4981997ce4b71dfb9dc481fed45d11936db8f2f8c",
    "context/source-manifest.json": "9a7baaf2453bed90a67b7145dd02c21f6e72150759885358e18f643f34899ddd",
}
CHANGED = {"source_bridge.py", "current_context_sessions.py", "current_legacy_context_sessions.py",
           "machine_auth_scope.py", "native_dispositions.py", "authentication.schema.json"}


def sha(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError("selected path missing or linked: " + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def build() -> dict:
    if sha(OLD / "source-manifest.json") != OLD_SHA or NEW.exists():
        raise ValueError("predecessor changed or successor already exists")
    source = json.loads((OLD / "source-manifest.json").read_bytes())
    profile = json.loads((OLD / "contract-profile.json").read_bytes())
    prefix = OLD.relative_to(ROOT).as_posix() + "/"
    own = [r for r in source["files"] if r["path"].startswith(prefix)]
    if len(own) != 201:
        raise ValueError("predecessor own closure differs")
    NEW.mkdir()
    for selected in own:
        original = ROOT / selected["path"]
        if sha(original) != selected["sha256"]:
            raise ValueError("predecessor member changed")
        copied = NEW / selected["path"][len(prefix):]
        copied.parent.mkdir(parents=True, exist_ok=True)
        copied.write_bytes(original.read_bytes())
    for name in CHANGED - {"authentication.schema.json"}:
        path = NEW / name
        raw = path.read_text()
        if OLD_ID not in raw:
            raise ValueError("expected family ID absent in " + name)
        raw = raw.replace(OLD_ID, NEW_ID)
        for relative, old_sha in OLD_PINS.items():
            selected = CONTEXT / "source-manifest.json" if relative.startswith("context/") else FAMILY / relative
            raw = raw.replace(old_sha, sha(selected))
        raw = raw.replace("legacy-local-" + NEW_ID + "/context'", "legacy-local-" + NEW_ID + "/context-native-v4-0001'")
        if name == "native_dispositions.py":
            if raw.count("604") != 3:
                raise ValueError("native subject closure count changed")
            raw = raw.replace("604", "654")
        path.write_text(raw)
    schema = NEW / "authentication.schema.json"
    raw = schema.read_text()
    if raw.count(OLD_ID) != 6:
        raise ValueError("authentication family enum count differs")
    schema.write_text(raw.replace(OLD_ID, NEW_ID))
    (NEW / "current_lesson_selection.py").write_text(
        '"""Select the source-closed local one-Lesson host."""\nfrom .t03_lesson_host import LessonHost\n')
    host = (HOST / "host.py").read_text()
    old = """            if Path(self.C.__file__).name in ('fixture_context_sessions.py','current_context_sessions.py'):
                declaration_path=self.C.D.reader.HERE/'packages/0001/fixture-applicability.json'
                declaration=E.parse(declaration_path.read_bytes())
                require(declaration['required_generator_ref']==str((self.C.D.HERE/'build.py').relative_to(ROOT))+'#generate'
                        and declaration['required_scope_ref']==self.source.sources.scope_ref
                        and declaration['fixture_only'] is True and declaration['observed_runtime_selection'] is False,
                        'controlled fixture declaration names another actual generator or scope')
                subject=self.view.subjects.get(declaration['lesson'])
                require(subject is not None and subject['kind']=='operational-lesson'
                        and subject['effective_state'] in self.C.D.reader.adapter.CURRENT,'declared actual current fixture Lesson unavailable')
                family=subject['record']['payload']['applicability']
"""
    new = """            if Path(self.C.__file__).name == 'current_context_sessions.py':
                current=[s for s in self.view.subjects.values()
                         if s['kind']=='operational-lesson' and
                            s['effective_state'] in self.C.D.reader.adapter.CURRENT]
                require(len(current)==1 and current[0]['carrier_ref']=='cal.artifact-type.operational-lesson/v1'
                        and current[0]['record']['scope_ref']==self.source.sources.scope_ref,
                        'exact signed one-Lesson source inventory differs')
                family=current[0]['record']['payload']['applicability']
            elif Path(self.C.__file__).name == 'fixture_context_sessions.py':
                declaration_path=self.C.D.reader.HERE/'packages/0001/fixture-applicability.json'
                declaration=E.parse(declaration_path.read_bytes())
                require(declaration['required_generator_ref']==str((self.C.D.HERE/'build.py').relative_to(ROOT))+'#generate'
                        and declaration['required_scope_ref']==self.source.sources.scope_ref
                        and declaration['fixture_only'] is True and declaration['observed_runtime_selection'] is False,
                        'controlled fixture declaration names another actual generator or scope')
                subject=self.view.subjects.get(declaration['lesson'])
                require(subject is not None and subject['kind']=='operational-lesson'
                        and subject['effective_state'] in self.C.D.reader.adapter.CURRENT,'declared actual current fixture Lesson unavailable')
                family=subject['record']['payload']['applicability']
"""
    if host.count(old) != 1:
        raise ValueError("selected host branch changed")
    (NEW / "t03_lesson_host.py").write_text(host.replace(old, new))
    (NEW / "plan.schema.json").write_bytes((HOST / "plan.schema.json").read_bytes())
    added = [row(NEW / name) for name in ("t03_lesson_host.py", "plan.schema.json")]
    family_fields = {
        "family_source_manifest_binding": FAMILY / "source/source-manifest.json",
        "family_source_package_binding": FAMILY / "source/packages/0001/manifest.json",
        "family_reader_manifest_binding": FAMILY / "reader/source-manifest.json",
        "family_mapped_package_binding": FAMILY / "mapped/packages/0001/manifest.json",
        "family_mapping_binding": FAMILY / "mapped/packages/0001/mapping.json",
        "family_context_manifest_binding": CONTEXT / "source-manifest.json",
        "family_context_package_binding": CONTEXT / "packages/0001/manifest.json",
    }
    for field, path in family_fields.items():
        source[field] = row(path)
    profile["files"] = sorted([row(NEW / r["path"][len(prefix):]) if r["path"].startswith(prefix) else r
                               for r in profile["files"]] + added, key=lambda r: r["path"])
    profile["integration_members_binding"] = row(NEW / "integration-members.json")
    profile["claim_ceiling"] = "T03 native-v4 one-Lesson local host; live selection and assessment require observed API effects."
    write(NEW / "contract-profile.json", profile)
    source["files"] = sorted([row(NEW / r["path"][len(prefix):]) if r["path"].startswith(prefix) else r
                              for r in source["files"]] + added, key=lambda r: r["path"])
    source["profile_binding"] = row(NEW / "contract-profile.json")
    source["predecessor_source_manifest_binding"] = row(OLD / "source-manifest.json")
    source["claim_ceiling"] = profile["claim_ceiling"]
    write(NEW / "source-manifest.json", source)
    receipt = {"schema_version": "lab-T03-one-Lesson-native-v4-API-rebind/v1-candidate",
               "successor_package": NEW.relative_to(ROOT).as_posix(),
               "successor_manifest_sha256": sha(NEW / "source-manifest.json"),
               "predecessor_binding": row(OLD / "source-manifest.json"),
               "family_binding": row(FAMILY / "source/source-manifest.json"),
               "context_successor_binding": row(CONTEXT / "source-manifest.json"),
               "changed_runtime_files": [row(NEW / name) for name in sorted(CHANGED)],
               "authority_effect": "none", "lesson_selected": False}
    write(NEW / "rebind-receipt.json", receipt)
    return receipt


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
