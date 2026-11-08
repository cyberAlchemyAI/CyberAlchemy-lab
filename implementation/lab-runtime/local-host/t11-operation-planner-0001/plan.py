#!/usr/bin/env python3
"""Effect-free local admission planning for 230 pinned T11 candidate bodies."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import types

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parents[4]
MATRIX = {"path": "docs/plans/0011-lab-runtime-completion/runs/0001-execution/T11/scope-routing-matrix-0002.json",
          "sha256": "f74f5c6a85e7eacb420785165fcb8257f2120337b31e482bf6bfb65125575628"}
ROUTER = {"path": "implementation/lab-runtime/local-host/t11-scoped-consumer-0001/router.py",
          "sha256": "171da60bce9b203c27c836029cb4b5e57b6d10f4cf99162e0a04d54578115052"}


class PlanRefusal(ValueError):
    pass


def need(value, reason):
    if not value:
        raise PlanRefusal(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def selected_router():
    raw = (ROOT / ROUTER["path"]).read_bytes()
    need(sha(raw) == ROUTER["sha256"], "selected router code changed")
    module = types.ModuleType("_t11_selected_router")
    module.__file__ = str(ROOT / ROUTER["path"])
    exec(compile(raw, module.__file__, "exec", dont_inherit=True), module.__dict__)
    return module


def fixture_grant(private_key, route, now):
    """Technical test grant, never an original Lab authorization."""
    grant = {"schema": "lab-local-scoped-body-grant/v1", "actor": "fixture:t11-planner",
             "member_ref": route["member_ref"], "scope_ref": route["body_scope_ref"],
             "body_sha256": route["body_binding"]["sha256"], "operation": route["operation"],
             "not_before": (now - timedelta(minutes=1)).isoformat(),
             "expires_at": (now + timedelta(minutes=1)).isoformat()}
    return {"grant": grant, "signature": private_key.sign(canonical(grant)).hex()}


class CandidatePlanner:
    def __init__(self, root, router, matrix_binding, public_key, *, clock):
        self.router = router
        self.consumer = router.ScopedConsumer(root, matrix_binding, public_key, clock=clock)
        matrix = self.consumer.matrix
        need(matrix["actual_successful_operational_routes"] == 0 and
             matrix["authority_effect"] == "none" and matrix["task_complete"] is False and
             matrix["source_body_currentness"] == "not-reverified; exact historical selected bindings only",
             "historical matrix status changed")
        need(Counter(route["body_scope_ref"] for route in matrix["routes"]) ==
             {"lab.legacy-source-assertion.cav2-product-thesis": 220,
              "scope:lab-runtime-local:w06-learning-0002-560605b8": 6,
              "scope:lab-integrated-model": 1,
              "project:cyberalchemy-v2-to-lab-migration@foundation.1": 1,
              "protocol:lab-final-review:C10": 1,
              "scope:lab-runtime-local:o02-source-withdrawal-fixture": 1},
             "six exact T11 scopes differ")
        self.heads = {}
        self.identities = set()
        self.plans = []

    def head(self, scope):
        return self.heads.get(scope, sha(canonical({"empty_candidate_plan_scope": scope})))

    def prepare(self, request, signed_grant):
        need(type(request) is dict and set(request) ==
             {"member_ref", "scope_ref", "version_ref", "expected_head", "operation", "category", "body_sha256"},
             "closed operation request required")
        member, scope = request["member_ref"], request["scope_ref"]
        route = self.consumer.routes.get(member)
        need(route is not None and route["body_scope_ref"] == scope, "member outside exact scope")
        need(route["operation"] == request["operation"] == "admit" and
             route["category"] == request["category"] == "artifact-instance" and
             route["version_ref"] == request["version_ref"] and
             route["body_binding"]["sha256"] == request["body_sha256"],
             "requested effect or target differs")
        need(request["expected_head"] == self.head(scope), "stale candidate plan head")

        def operation(raw, selected_route):
            need(selected_route == route and sha(raw) == request["body_sha256"],
                 "consumed bytes or selected route differ")
            body = json.loads(raw)
            ident = body["node_id"]
            need(request["version_ref"].startswith(ident + "@") and
                 len(request["version_ref"]) > len(ident) + 1 and
                 body["scope_ref"] == scope and body["authority_effect"] == "none" and
                 body.get("lifecycle_state", body.get("record_state")) == "candidate",
                 "candidate identity, scope or state differs")
            need((scope, ident) not in self.identities, "duplicate candidate identity")
            return {"member_ref": member, "scope_ref": scope, "identity": ident,
                    "version_ref": request["version_ref"], "category": "artifact-instance",
                    "proposed_operation": "admit", "carrier_ref": route["carrier_ref"],
                    "body_binding": route["body_binding"],
                    "historical_decision_ref": route["decision_ref"],
                    "predecessor_ref": None, "planning_state": "candidate-prepared",
                    "authority_effect": "none"}

        plan = self.consumer.consume(member, scope, signed_grant, operation)
        previous = self.head(scope)
        successor = sha(canonical({"previous": previous, "plan": plan}))
        self.heads[scope] = successor
        self.identities.add((scope, plan["identity"]))
        self.plans.append({"plan": plan, "previous_head": previous, "resulting_head": successor})
        return self.plans[-1]


def request_for(planner, route):
    return {"member_ref": route["member_ref"], "scope_ref": route["body_scope_ref"],
            "version_ref": route["version_ref"], "expected_head": planner.head(route["body_scope_ref"]),
            "operation": route["operation"], "category": route["category"],
            "body_sha256": route["body_binding"]["sha256"]}


def build():
    router = selected_router()
    signer = Ed25519PrivateKey.generate()
    now = datetime(2026, 10, 23, 0, 0, tzinfo=timezone.utc)
    planner = CandidatePlanner(ROOT, router, MATRIX, signer.public_key(), clock=lambda: now)
    for route in planner.consumer.matrix["routes"]:
        planner.prepare(request_for(planner, route), fixture_grant(signer, route, now))
    need(len(planner.plans) == 230 and len(planner.identities) == 230,
         "candidate operation coverage incomplete")
    return {"schema_version": "lab-T11-candidate-operation-plans/v1",
            "matrix_binding": MATRIX, "router_binding": ROUTER,
            "runner_sha256": sha(Path(__file__).read_bytes()),
            "technical_operation_plans": len(planner.plans),
            "by_scope": dict(sorted(Counter(p["plan"]["scope_ref"] for p in planner.plans).items())),
            "plans": planner.plans, "final_heads": dict(sorted(planner.heads.items())),
            "original_successful_operational_routes": 0,
            "native_prepare_calls": 0, "authority_effect": "none", "T11_complete": False,
            "claim_ceiling": "230 effect-free exact-body candidate admission plans under fixture grants; no native prepare/apply, current domain grant, producer proof, relation closure or original authority."}


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
