"""Exercise the selected governance-v5 role projection with fresh local inputs."""

import copy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "product/lab/release-candidates/v1/interface/api-governance-integration-v5-current-t12-0001"
SOURCE_SHA256 = "8a215ad66e94179385bcb4dcac79eab5267ee6ac50e12e7b1dac21645301d337"
PROFILE_SHA256 = "7798fda1f9e7e4038425bc8aa6f227f2e22612affa4acb2c28c9a12d31531af3"
sys.path.insert(0, str(PACKAGE.parent))
governance = importlib.import_module(PACKAGE.name + ".governance")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def fixture(kind):
    return json.loads((ROOT / f"authority/artifact-types/{kind}/v1/fixtures/valid/record.json").read_bytes())


def utc(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


class LocalHost:
    def __init__(self, scope):
        self.policy = {"scope_refs": [scope]}
        self.rows = {}

    def add(self, ref, value):
        raw = encoded(value)
        self.rows[ref] = raw
        return {"ref": ref, "sha256": sha(raw)}

    def material(self, binding):
        raw = self.rows[binding["ref"]]
        if sha(raw) != binding["sha256"]:
            raise ValueError("changed selected role input")
        return raw

    def document(self, binding):
        return json.loads(self.material(binding))


def selection(*, role_state="active", assignment_state="active", assignment_scope=None,
              assignment_end=None, assignment_start=None, principal_status="active",
              assignment_assignee=None, assignment_role=None, recognition_scope=None):
    scope = "scope:local-lab-role-qualification"
    principal = fixture("principal")
    principal["node_id"] = "principal:local-operator"
    principal["scope_ref"] = scope
    principal["payload"]["status"] = principal_status
    principal["payload"]["stable_subject_ref"] = "person-reference:synthetic-local-lab-operator"
    role = fixture("role")
    role["node_id"] = "role:local-lab-operator"
    role["scope_ref"] = scope
    role["lifecycle_state"] = role_state
    assignment = fixture("role-assignment")
    assignment["node_id"] = "role-assignment:local-lab-operator"
    assignment["role_ref"] = assignment_role or role["node_id"]
    assignment["assignee_ref"] = assignment_assignee or principal["payload"]["stable_subject_ref"]
    assignment["scope_ref"] = scope if assignment_scope is None else assignment_scope
    assignment["assignment_state"] = assignment_state
    instant = datetime.now(timezone.utc)
    assignment["period"] = {"start": assignment_start or utc(instant - timedelta(hours=1)),
                            "end": assignment_end}
    host = LocalHost(scope)
    principal_binding = host.add("principal:local-operator", principal)
    role_binding = host.add("role:local-lab-operator", role)
    assignment_binding = host.add("assignment:local-lab-operator", assignment)
    key = "11" * 32
    recognition_binding = host.add("recognition:local-lab-operator", {
        "schema_version": "lab-owned-governance-owner-recognition/v1-candidate",
        "principal_binding": principal_binding, "role_binding": role_binding,
        "assignment_binding": assignment_binding, "public_key_hex": key,
        "scope_ref": recognition_scope or scope, "authority_effect": "none", "claim_ceiling": governance.CEILING})
    owner = {"principal_ref": principal["node_id"], "role_ref": role["node_id"],
             "principal_binding": principal_binding, "role_binding": role_binding,
             "assignment_binding": assignment_binding,
             "recognition_binding": recognition_binding, "public_key_hex": key,
             "not_before": utc(instant - timedelta(hours=1)),
             "expires_at": utc(instant + timedelta(hours=1))}
    selected = {"recognized_owners": [owner],
                "required_members": [{"owner_principal_ref": principal["node_id"],
                                      "owner_role_ref": role["node_id"]}]}
    return host, selected


class SelectedRoleProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        manifest = PACKAGE / "source-manifest.json"
        profile = PACKAGE / "contract-profile.json"
        if sha(manifest.read_bytes()) != SOURCE_SHA256 or sha(profile.read_bytes()) != PROFILE_SHA256:
            raise AssertionError("selected governance-v5 source/profile changed")
        rows = {row["path"]: row["sha256"] for row in json.loads(manifest.read_bytes())["files"]}
        if rows[(PACKAGE / "governance.py").relative_to(ROOT).as_posix()] != sha((PACKAGE / "governance.py").read_bytes()):
            raise AssertionError("selected role adapter bytes changed")
        if Path(governance.__file__).resolve() != (PACKAGE / "governance.py").resolve():
            raise AssertionError("loaded role adapter origin differs")
        governance.guard(SOURCE_SHA256)
        for kind in ("principal", "role", "role-assignment"):
            path = f"authority/artifact-types/{kind}/v1/schema.json"
            if rows[path] != sha((ROOT / path).read_bytes()):
                raise AssertionError("selected role schema bytes changed: " + kind)

    def test_current_exact_role_and_assignment_resolve(self):
        host, selected = selection()
        owners = governance.recognition(host, selected)
        self.assertEqual(set(owners), {("principal:local-operator", "role:local-lab-operator")})

    def test_future_assignment_refuses(self):
        future = utc(datetime.now(timezone.utc) + timedelta(minutes=1))
        host, selected = selection(assignment_start=future)
        with self.assertRaisesRegex(Exception, "expired"):
            governance.recognition(host, selected)

    def test_active_assignment_with_finite_end_refuses_at_schema(self):
        expired = utc(datetime.now(timezone.utc) - timedelta(minutes=1))
        host, selected = selection(assignment_end=expired)
        with self.assertRaisesRegex(Exception, "original carrier schema"):
            governance.recognition(host, selected)

    def test_ended_and_elapsed_assignment_refuses(self):
        expired = utc(datetime.now(timezone.utc) - timedelta(minutes=1))
        host, selected = selection(assignment_state="ended", assignment_end=expired)
        with self.assertRaisesRegex(Exception, "assignment differs"):
            governance.recognition(host, selected)

    def test_revoked_assignment_refuses(self):
        host, selected = selection(assignment_state="revoked")
        with self.assertRaisesRegex(Exception, "assignment differs"):
            governance.recognition(host, selected)

    def test_wrong_scope_refuses(self):
        host, selected = selection(assignment_scope="scope:other")
        with self.assertRaisesRegex(Exception, "assignment differs"):
            governance.recognition(host, selected)

    def test_wrong_assignee_refuses(self):
        host, selected = selection(assignment_assignee="person-reference:other")
        with self.assertRaisesRegex(Exception, "assignment differs"):
            governance.recognition(host, selected)

    def test_wrong_role_ref_refuses(self):
        host, selected = selection(assignment_role="role:other")
        with self.assertRaisesRegex(Exception, "assignment differs"):
            governance.recognition(host, selected)

    def test_wrong_recognition_original_refuses(self):
        host, selected = selection(recognition_scope="scope:other")
        with self.assertRaisesRegex(Exception, "recognition original differs"):
            governance.recognition(host, selected)

    def test_duplicate_owner_pair_refuses(self):
        host, selected = selection()
        selected["recognized_owners"].append(copy.deepcopy(selected["recognized_owners"][0]))
        with self.assertRaisesRegex(Exception, "Duplicate"):
            governance.recognition(host, selected)

    def test_missing_required_owner_refuses(self):
        host, selected = selection()
        selected["required_members"] = []
        with self.assertRaisesRegex(Exception, "exact required roster"):
            governance.recognition(host, selected)

    def test_inactive_role_refuses(self):
        host, selected = selection(role_state="retired")
        with self.assertRaisesRegex(Exception, "Role is inactive"):
            governance.recognition(host, selected)

    def test_inactive_principal_refuses(self):
        host, selected = selection(principal_status="inactive")
        with self.assertRaisesRegex(Exception, "Principal or Role is inactive"):
            governance.recognition(host, selected)

    def test_changed_selected_bytes_refuse(self):
        host, selected = selection()
        ref = selected["recognized_owners"][0]["assignment_binding"]["ref"]
        host.rows[ref] += b" "
        with self.assertRaisesRegex(ValueError, "changed selected role input"):
            governance.recognition(host, selected)


if __name__ == "__main__":
    unittest.main()
