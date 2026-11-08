"""Bind a local Lesson host to the exact signed current one-Lesson family."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "product/lab/release-candidates/v1/interface"
OLD = BASE / "api-integration-v33-t03-one-lesson-0002"
NEW = BASE / "api-integration-v33-t03-one-lesson-0003"
HOST = BASE / "lesson-host-composition-v46-completion-0001"
OLD_SHA = "7c2405d840737eafa9b734f988b2129c1caa5f71d4bf564ed4db8015cef40b8d"


def sha(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError("selected path missing or linked")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)}


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def build():
    if sha(OLD / "source-manifest.json") != OLD_SHA or NEW.exists():
        raise ValueError("predecessor changed or successor already exists")
    source = json.loads((OLD / "source-manifest.json").read_bytes())
    profile = json.loads((OLD / "contract-profile.json").read_bytes())
    prefix = OLD.relative_to(ROOT).as_posix() + "/"
    own = [r for r in source["files"] if r["path"].startswith(prefix)]
    if len(own) != 201:
        raise ValueError("predecessor closure differs")
    NEW.mkdir()
    for selected in own:
        original = ROOT / selected["path"]
        if sha(original) != selected["sha256"]:
            raise ValueError("predecessor member changed")
        copied = NEW / selected["path"][len(prefix):]
        copied.parent.mkdir(parents=True, exist_ok=True)
        copied.write_bytes(original.read_bytes())
    current = NEW / "current_lesson_selection.py"
    current.write_text('"""Select the source-closed local one-Lesson host."""\nfrom .t03_lesson_host import LessonHost\n')
    host_path = NEW / "t03_lesson_host.py"
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
                # The signed T03 family is a complete one-Lesson native mapping,
                # not the older fixture-applicability declaration package.
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
    host = host.replace(old, new)
    host_path.write_text(host)
    (NEW / "plan.schema.json").write_bytes((HOST / "plan.schema.json").read_bytes())
    # The helper is now part of this API source closure, so the host can prove
    # its own code origin through the exact selected manifest.
    added = [row(NEW / name) for name in ("t03_lesson_host.py", "plan.schema.json")]
    profile["files"] = [row(NEW / r["path"][len(prefix):]) if r["path"].startswith(prefix) else r
                        for r in profile["files"]] + added
    profile["files"] = sorted(profile["files"], key=lambda r: r["path"])
    profile["integration_members_binding"] = row(NEW / "integration-members.json")
    profile["claim_ceiling"] = "T03 one-Lesson local host source closure; selection requires actual reviewed plan and live Machine Session."
    write(NEW / "contract-profile.json", profile)
    source["files"] = sorted([row(NEW / r["path"][len(prefix):]) if r["path"].startswith(prefix) else r
                              for r in source["files"]] + added, key=lambda r: r["path"])
    source["profile_binding"] = row(NEW / "contract-profile.json")
    source["predecessor_source_manifest_binding"] = row(OLD / "source-manifest.json")
    source["claim_ceiling"] = profile["claim_ceiling"]
    write(NEW / "source-manifest.json", source)
    receipt = {"schema_version": "lab-T03-one-Lesson-API-rebind/v3-candidate",
               "successor_package": NEW.relative_to(ROOT).as_posix(),
               "successor_manifest_sha256": sha(NEW / "source-manifest.json"),
               "predecessor_binding": row(OLD / "source-manifest.json"),
               "local_lesson_host_binding": row(host_path),
               "authority_effect": "none", "lesson_selected": False}
    write(NEW / "rebind-receipt.json", receipt)
    return receipt


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
