"""Immutable single-writer local store, signed approvals and verified replay."""
from __future__ import annotations

import copy
import fcntl
import os
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .common import RuntimeFault, atomic, digest, encoded, fsync_dir, load, require, sealed, verify_seal
from .operations import CATEGORIES, OPERATIONS, consequences, prepare
from .operations import protocol_check
from .protocols import APPROVAL_SCHEMA, CONFIG_SCHEMA, HEAD_SCHEMA, TRANSACTION_SCHEMA
from .sources import capture, freshness


def keygen(private_path, public_path):
    private_path, public_path = Path(private_path), Path(public_path)
    require(private_path.resolve() != public_path.resolve(), "private and public key outputs must differ")
    require(not private_path.exists() and not public_path.exists(), "key output already exists")
    private = Ed25519PrivateKey.generate()
    fd = os.open(private_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(private.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    public_path.write_text(private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex() + "\n")
    return {"public_key": public_path.read_text().strip(), "private_key_path": str(private_path)}


def approval_core(proposal, cores, config, approved_at):
    return {"schema_version": "lab-runtime-approval/v1", "store_id": config["store_id"],
            "owner_ref": config["owner_ref"], "scope_ref": proposal["scope_ref"], "policy_ref": proposal["policy_ref"],
            "challenge_route": proposal["challenge_route"], "source_snapshot_digest": proposal["source_snapshot_digest"],
            "expected_head": proposal["expected_head"], "proposal_digest": digest(proposal),
            "decision_core_digests": [digest(c) for c in cores], "approved_at": approved_at, "outcome": "authorize-exact-local-effects"}


def verify_approval(approval, proposal, cores, config):
    protocol_check(approval, APPROVAL_SCHEMA)
    expected = approval_core(proposal, cores, config, approval["approved_at"])
    require(set(approval) == set(expected) | {"signature"}, "approval envelope must be closed")
    core = {k: v for k, v in approval.items() if k != "signature"}
    require(core == expected, "approval does not bind exact proposal, authority, scope and HEAD")
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(config["public_key"])).verify(bytes.fromhex(approval["signature"]), encoded(core))
    except (InvalidSignature, ValueError, TypeError) as exc:
        raise RuntimeFault("invalid owner approval signature") from exc


class Store:
    def __init__(self, path, repo):
        self.path = Path(path).resolve()
        self.repo = Path(repo).resolve()
        if self.path.is_relative_to(self.repo):
            require(self.path.is_relative_to(self.repo / ".local"), "local runtime state inside repository must live under .local/")

    @contextmanager
    def lock(self):
        require(self.path.is_dir(), "store not initialized")
        f = self.path / ".writer.lock"
        require(not f.is_symlink(), "writer lock symlink forbidden")
        with f.open("a+") as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise RuntimeFault("another writer owns the store") from exc
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def initialize(self, profile, store_id, owner_ref, public_key, allowed_categories=None, allowed_effects=None, *, selected_scope_ref=None):
        require(profile == load(Path(__file__).resolve().parents[1] / "profile.json"), "store initialization requires this executable's exact source profile")
        require(not self.path.exists(), "store already exists; initialize a new branch explicitly")
        require(store_id and all(c.isalnum() or c == "-" for c in store_id), "invalid store identity")
        require(owner_ref.startswith("role:") or owner_ref.startswith("principal:"), "explicit provisioned owner identity required")
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key))
        except (ValueError, TypeError) as exc:
            raise RuntimeFault("invalid public key") from exc
        categories = allowed_categories or CATEGORIES
        effects = allowed_effects or OPERATIONS
        require(set(categories) <= set(CATEGORIES) and set(effects) <= set(OPERATIONS), "unknown provisioned effects/categories")
        baseline = capture(self.repo, profile)
        from .endpoint_mapping import ENGINE_ID, binding
        scope_ref = selected_scope_ref or 'scope:lab-runtime-local:' + store_id
        require(selected_scope_ref is None or selected_scope_ref == profile['project_ref'],
            'selected candidate scope must bind the exact source Project')
        config = {"schema_version": "lab-runtime-store-config/v2-candidate", "store_id": store_id,
                  "source_snapshot_digest": baseline["snapshot_digest"], "owner_ref": owner_ref,
                  "public_key": public_key, "scope_ref": scope_ref,
                  "policy_ref": profile["policy_ref"], "challenge_route": profile["challenge_route"],
                  "allowed_categories": categories, "allowed_effects": effects,
                  "authority_boundary": "operator-provisioned-local-store", "repository_admission_effect": "none",
                  'endpoint_engine_id': ENGINE_ID, 'endpoint_mapping_binding': binding(),
                  'endpoint_mapping_authority': 'isolated-candidate-local-interpretation'}
        self.path.mkdir(parents=True, mode=0o700)
        (self.path / "transactions").mkdir()
        # Genesis has the same commit point as subsequent transactions.
        atomic(self.path / "config.json", encoded(sealed(config)))
        atomic(self.path / "baseline.json", encoded(baseline))
        genesis = sealed({"schema_version": "lab-runtime-transaction/v1", "sequence": 0, "previous_digest": None,
                          "config_digest": digest(config), "baseline_digest": baseline["snapshot_digest"],
                          "projection_digest": digest(self.initial_projection(baseline)), "kind": "genesis"})
        atomic(self.path / "transactions/0000000000.json", encoded(genesis))
        atomic(self.path / "HEAD.json", encoded(sealed({"sequence": 0, "transaction_digest": genesis["digest"],
                                                       "config_digest": digest(config), "baseline_digest": baseline["snapshot_digest"]})))
        return self.status()

    @staticmethod
    def initial_projection(baseline):
        return copy.deepcopy({k: baseline[k] for k in ("subjects", "contracts", "relation_contracts", "documents", "state", "histories")})

    def roots(self):
        config = load(self.path / "config.json")
        verify_seal(config)
        config = {k: v for k, v in config.items() if k != "digest"}
        protocol_check(config, CONFIG_SCHEMA)
        baseline = load(self.path / "baseline.json")
        require(baseline["snapshot_digest"] == digest({k: v for k, v in baseline.items() if k != "snapshot_digest"}), "baseline envelope changed")
        head = load(self.path / "HEAD.json")
        verify_seal(head)
        protocol_check(head, HEAD_SCHEMA)
        require(set(head) == {"sequence", "transaction_digest", "config_digest", "baseline_digest", "digest"}, "HEAD envelope must be closed")
        require(type(head["sequence"]) is int and 0 <= head["sequence"] <= 100000, "invalid HEAD sequence")
        require(head["config_digest"] == digest(config) and head["baseline_digest"] == baseline["snapshot_digest"], "store configuration/baseline binding mismatch")
        require(config["source_snapshot_digest"] == baseline["snapshot_digest"], "store source binding mismatch")
        return config, baseline, head

    def replay(self, *, require_current=False):
        config, baseline, head = self.roots()
        fresh = freshness(self.repo, baseline)
        active_profile = load(Path(__file__).resolve().parents[1] / "profile.json")
        from .endpoint_mapping import ENGINE_ID, binding
        if config.get('endpoint_engine_id') != ENGINE_ID or config.get('endpoint_mapping_binding') != binding():
            fresh['status'] = 'stale'
            fresh['changed'] = sorted(set(fresh['changed']) | {'endpoint-mapping-profile-required'})
        if baseline["profile"] != active_profile:
            fresh["status"] = "stale"
            fresh["changed"] = sorted(set(fresh["changed"]) | {"runtime-source-profile-successor-required"})
        if require_current:
            require(fresh["status"] == "current", "stale repository sources: " + ", ".join(fresh["changed"][:4]))
        projection = self.initial_projection(baseline)
        previous = None
        records = []
        ids = set()
        for sequence in range(head["sequence"] + 1):
            tx = load(self.path / "transactions" / f"{sequence:010d}.json")
            verify_seal(tx)
            protocol_check(tx, TRANSACTION_SCHEMA)
            fields = {"schema_version", "sequence", "previous_digest", "config_digest", "baseline_digest", "projection_digest", "kind", "digest"}
            if sequence:
                fields |= {"proposal", "decision_cores", "approval", "consequences"}
            require(set(tx) == fields and tx["schema_version"] == "lab-runtime-transaction/v1", "transaction envelope must be closed")
            require(tx["sequence"] == sequence and tx["previous_digest"] == previous, "transaction chain mismatch")
            require(tx["config_digest"] == digest(config) and tx["baseline_digest"] == baseline["snapshot_digest"], "transaction belongs to a different store")
            if sequence == 0:
                require(tx["kind"] == "genesis", "invalid genesis")
            else:
                require(tx["kind"] == "admission", "unknown committed transaction kind")
                proposal = tx["proposal"]
                require(proposal["proposal_id"] not in ids, "duplicate committed proposal ID")
                ids.add(proposal["proposal_id"])
                projection, cores = prepare(projection, proposal, previous, config)
                verify_approval(tx["approval"], proposal, cores, config)
                expected = consequences(projection, proposal, cores, tx["approval"], sequence, config["store_id"])
                require(expected == tx["consequences"], "deterministic consequence/receipt mismatch")
                require(cores == tx["decision_cores"], "Decision core mismatch")
            require(tx["projection_digest"] == digest(projection), "replayed projection digest mismatch")
            previous = tx["digest"]
            records.append(tx)
        require(previous == head["transaction_digest"], "HEAD points to a different transaction")
        return {"config": config, "baseline": baseline, "head": head, "projection": projection, "transactions": records, "freshness": fresh}

    def leftovers(self, head):
        values = []
        if (self.path / "PENDING.json").exists():
            values.append("PENDING.json")
        for f in sorted((self.path / "transactions").iterdir()):
            if f.name.startswith(".") or (f.suffix == ".json" and f.stem.isdigit() and int(f.stem) > head["sequence"]):
                values.append("transactions/" + f.name)
        for f in self.path.glob(".HEAD.json.*"):
            values.append(f.name)
        return values

    def status(self):
        data = self.replay()
        p, h = data["projection"], data["head"]
        return {"schema_version": "lab-runtime-status/v1", "store_id": data["config"]["store_id"],
                "implementation_state": "candidate", "head": h["transaction_digest"], "sequence": h["sequence"],
                "current_project_state": p["state"], "freshness": data["freshness"],
                "history_cursors": {k: len(v["payload"]["events"]) for k, v in p["histories"].items()},
                "subject_count": len(p["subjects"]), "recovery_required": self.leftovers(h),
                "repository_admission_as_of": data["baseline"]["admission_as_of"], "repository_runtime_activation": "not-observed",
                "authority_effect": "none", "replay_source": False}

    def review(self, proposal):
        data = self.replay(require_current=True)
        post, cores = prepare(data["projection"], proposal, data["head"]["transaction_digest"], data["config"])
        from .endpoint_mapping import binding, explain
        endpoint_explanations = []
        for target in proposal['targets']:
            if target['category'] == 'typed-relation' and target['operation'] != 'withdraw':
                for endpoint in target['record']['payload']['source'], target['record']['payload']['target']:
                    from .sources import resolve
                    row = explain(resolve(post['subjects'], endpoint['version_ref']), post)
                    if row not in endpoint_explanations:
                        endpoint_explanations.append(row)
        return {"proposal_digest": digest(proposal), "decision_cores": cores, "target_count": len(proposal["targets"]),
                'endpoint_mapping_binding': binding(), 'endpoint_explanations': endpoint_explanations,
                "proposed_subject_count": len(post["subjects"]), "authority_effect": "none", "approval_required": True,
                "planned_consequences": {"project_states": 1, "semantic_events": 1, "governance_events": 1,
                                         "decisions": len(cores), "decision_scopes": len(cores), "decision_bundles": 1,
                                         "checkpoints": 1, "authority_boundaries": 1, "admission_transactions": 1,
                                         "registry_projections": 1, "deterministic_typed_relations": 6,
                                         "declared_relation_axes": ["relation.member-of", "relation.successor-of", "relation.materializes-consequence"],
                                         "runtime_activations": 0, "external_effects": 0, "repository_admission_effect": "none"},
                "scope_ref": data["config"]["scope_ref"], "source_snapshot_digest": data["baseline"]["snapshot_digest"]}

    def authorize(self, proposal, private_key):
        data = self.replay(require_current=True)
        _, cores = prepare(data["projection"], proposal, data["head"]["transaction_digest"], data["config"])
        f = Path(private_key)
        require(not f.resolve().is_relative_to(self.path) and not f.resolve().is_relative_to(self.repo), "private owner key must remain outside store and repository")
        require(f.stat().st_mode & 0o077 == 0, "private key must have owner-only permissions")
        try:
            private = serialization.load_pem_private_key(f.read_bytes(), password=None)
        except (ValueError, TypeError) as exc:
            raise RuntimeFault("invalid owner private key") from exc
        require(isinstance(private, Ed25519PrivateKey), "Ed25519 operator key required")
        pub = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()
        require(pub == data["config"]["public_key"], "private key does not match provisioned owner")
        approved_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        core = approval_core(proposal, cores, data["config"], approved_at)
        return {**core, "signature": private.sign(encoded(core)).hex()}

    def apply(self, proposal, approval, *, crash_at=None):
        with self.lock():
            data = self.replay(require_current=True)
            for tx in data["transactions"][1:]:
                if tx["proposal"]["proposal_id"] == proposal["proposal_id"]:
                    require(tx["proposal"] == proposal and tx["approval"] == approval, "proposal ID reused with different bytes")
                    return {"idempotent": True, "transaction_digest": tx["digest"], "receipt": tx["consequences"]["receipt"]}
            require(not self.leftovers(data["head"]), "uncommitted work exists; recover before writing")
            projection, cores = prepare(data["projection"], proposal, data["head"]["transaction_digest"], data["config"])
            verify_approval(approval, proposal, cores, data["config"])
            sequence = data["head"]["sequence"] + 1
            output = consequences(projection, proposal, cores, approval, sequence, data["config"]["store_id"])
            tx = sealed({"schema_version": "lab-runtime-transaction/v1", "kind": "admission", "sequence": sequence,
                         "previous_digest": data["head"]["transaction_digest"], "config_digest": digest(data["config"]),
                         "baseline_digest": data["baseline"]["snapshot_digest"], "proposal": proposal, "decision_cores": cores,
                         "approval": approval, "consequences": output, "projection_digest": digest(projection)})
            def crash(stage):
                if crash_at == stage:
                    os._exit(86)
            pending = {"sequence": sequence, "expected_head": data["head"]["transaction_digest"], "transaction_digest": tx["digest"]}
            atomic(self.path / "PENDING.json", encoded(sealed(pending)))
            crash("after-pending")
            target = self.path / "transactions" / f"{sequence:010d}.json"
            require(not target.exists(), "uncommitted transaction occupies next sequence")
            atomic(target, encoded(tx))
            crash("before-head")
            head = sealed({"sequence": sequence, "transaction_digest": tx["digest"], "config_digest": digest(data["config"]), "baseline_digest": data["baseline"]["snapshot_digest"]})
            # Verify sources again immediately before publishing the fully staged transaction.
            require(freshness(self.repo, data["baseline"])["status"] == "current", "source changed before commit")
            atomic(self.path / "HEAD.json", encoded(head))
            crash("after-head")
            (self.path / "PENDING.json").unlink()
            fsync_dir(self.path)
            return {"idempotent": False, "transaction_digest": tx["digest"], "receipt": output["receipt"]}

    def recover(self, expected_head):
        with self.lock():
            data = self.replay()
            require(data["head"]["transaction_digest"] == expected_head, "recovery HEAD mismatch")
            files = self.leftovers(data["head"])
            pending = self.path / "PENDING.json"
            if pending.exists():
                value = load(pending)
                verify_seal(value)
                if value["sequence"] <= data["head"]["sequence"]:
                    require(value["sequence"] == data["head"]["sequence"] and value["transaction_digest"] == expected_head, "unrecognized committed pending record")
                else:
                    require(value["sequence"] == data["head"]["sequence"] + 1 and value["expected_head"] == expected_head, "pending record does not bind current HEAD")
            for name in files:
                path = self.path / name
                require(not path.is_symlink() and path.is_file(), "unexpected recovery material")
                if name.startswith("transactions/") and path.suffix == ".json" and path.stem.isdigit():
                    require(int(path.stem) == data["head"]["sequence"] + 1, "unknown future transaction preserved for inspection")
            for name in files:
                (self.path / name).unlink()
            fsync_dir(self.path / "transactions")
            fsync_dir(self.path)
            return {"head": expected_head, "removed_uncommitted_files": files, "committed_history_preserved": True}
