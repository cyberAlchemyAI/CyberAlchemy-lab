#!/usr/bin/env python3
"""Disposable local Source -> Reader -> Mapper -> Context development journey.

This is a distinct fixture profile. It does not execute the historical Source8,
Reader, Mapper or Context role packages or grant protected authority.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization


REPO = Path(__file__).resolve().parents[4]
WORK_RUN = REPO / "implementation/lab-runtime/local-product/run.py"
SCOPE = "scope:cyberalchemy-local-chain-fixture"
NODE_IDS = (
    "principal", "principal-reference", "goal", "work", "intent", "profile",
    "assignment", "coordination", "context", "capability", "implementation",
    "source", "project", "project-state", "product-capability",
)
EDGE_IDS = (
    ("principal", "work"), ("work", "goal"), ("assignment", "principal"),
    ("assignment", "work"), ("coordination", "assignment"),
    ("context", "coordination"), ("capability", "principal"),
    ("implementation", "product-capability"), ("project-state", "project"),
    ("source", "project-state"),
)


class Refused(ValueError):
    pass


def need(ok: bool, code: str) -> None:
    if not ok:
        raise Refused(code)


def wire(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def plain_json(raw: bytes) -> object:
    def pairs(rows):
        value = {}
        for key, item in rows:
            need(key not in value, "DUPLICATE_JSON_KEY")
            value[key] = item
        return value
    try:
        return json.loads(raw, object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(Refused("NONFINITE_JSON")))
    except (UnicodeError, ValueError, TypeError, RecursionError) as error:
        raise Refused("INVALID_JSON") from error


def load_work_product() -> dict:
    spec = importlib.util.spec_from_file_location("cal_local_work_product_chain", WORK_RUN)
    need(spec is not None and spec.loader is not None, "WORK_PRODUCT_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    outcome = module.run()
    need(outcome["result"] == "PASS" and outcome["fresh_process_replay"] == "PASS"
         and outcome["repository_admission_effect"] == "none"
         and outcome["external_effects"] == 0 and outcome["disposable_root_removed"],
         "WORK_PRODUCT_REFUSED")
    return outcome


def source_body(work: dict, now: datetime) -> dict:
    need(now.tzinfo is not None and now.utcoffset() == timedelta(0), "UTC_REQUIRED")
    records = [{"id": name, "value": work["local_project_state"] if name == "project-state"
                else work["work_version"] if name == "work" else "fixture:" + name}
               for name in NODE_IDS]
    relations = [{"id": f"relation:{index:02d}", "from": left, "to": right}
                 for index, (left, right) in enumerate(EDGE_IDS)]
    return {"schema": "lab-local-chain-source/v1-fixture", "scope": SCOPE,
            "not_before": now.isoformat(), "expires": (now + timedelta(minutes=20)).isoformat(),
            "work_receipt_sha256": sha(wire(work)),
            "records": records, "relations": relations,
            "authority_effect": "none", "actual_owner_outcome": None}


def sign_source(body: dict, key: Ed25519PrivateKey) -> bytes:
    raw = wire(body)
    public = key.public_key().public_bytes(serialization.Encoding.Raw,
                                           serialization.PublicFormat.Raw)
    return wire({"schema": "lab-local-chain-signed-source/v1-fixture",
                 "body": body, "body_sha256": sha(raw), "public_key": public.hex(),
                 "signature": key.sign(raw).hex()})


def read_source(raw: bytes, expected_scope: str, now: datetime,
                expected_public_key: str, expected_work_sha256: str) -> dict:
    envelope = plain_json(raw)
    need(type(envelope) is dict and set(envelope) ==
         {"schema", "body", "body_sha256", "public_key", "signature"}
         and envelope["schema"] == "lab-local-chain-signed-source/v1-fixture",
         "SOURCE_ENVELOPE")
    body = envelope["body"]
    need(type(body) is dict and set(body) ==
         {"schema", "scope", "not_before", "expires", "work_receipt_sha256",
          "records", "relations", "authority_effect", "actual_owner_outcome"}
         and body["schema"] == "lab-local-chain-source/v1-fixture"
         and body["authority_effect"] == "none"
         and body["actual_owner_outcome"] is None, "SOURCE_BODY")
    need(wire(envelope) == raw and sha(wire(body)) == envelope["body_sha256"],
         "SOURCE_BYTES")
    need(envelope["public_key"] == expected_public_key and
         body["work_receipt_sha256"] == expected_work_sha256,
         "SOURCE_SELECTED_INPUT_BINDING")
    try:
        public = bytes.fromhex(envelope["public_key"])
        signature = bytes.fromhex(envelope["signature"])
        need(len(public) == 32 and len(signature) == 64, "SOURCE_SIGNATURE_SHAPE")
        Ed25519PublicKey.from_public_bytes(public).verify(signature, wire(body))
    except (ValueError, InvalidSignature) as error:
        raise Refused("SOURCE_SIGNATURE") from error
    need(body["scope"] == expected_scope, "SOURCE_SCOPE")
    try:
        start = datetime.fromisoformat(body["not_before"])
        end = datetime.fromisoformat(body["expires"])
    except (TypeError, ValueError) as error:
        raise Refused("SOURCE_PERIOD") from error
    need(start.tzinfo is not None and end.tzinfo is not None and
         start.utcoffset() == end.utcoffset() == timedelta(0) and
         start <= now < end and end - start == timedelta(minutes=20), "SOURCE_PERIOD")
    need([row["id"] for row in body["records"]] == list(NODE_IDS)
         and [(r["from"], r["to"]) for r in body["relations"]] == list(EDGE_IDS)
         and len({r["id"] for r in body["relations"]}) == 10,
         "SOURCE_SHAPE")
    return body


def map_source(body: dict) -> dict:
    nodes = [{"kind": "ontology-node", "id": "node:" + row["id"],
              "source_sha256": sha(wire(row)), "label": row["value"]}
             for row in body["records"]]
    edges = [{"kind": "ontology-edge", "id": "edge:" + row["id"],
              "source": "node:" + row["from"], "target": "node:" + row["to"],
              "source_sha256": sha(wire(row))} for row in body["relations"]]
    node_ids = {node["id"] for node in nodes}
    need(len(nodes) == 15 and len(node_ids) == 15 and len(edges) == 10 and
         len({edge["id"] for edge in edges}) == 10 and
         all(edge["source"] in node_ids and edge["target"] in node_ids for edge in edges),
         "MAPPING_CLOSURE")
    return {"schema": "lab-local-chain-mapping/v1-fixture", "scope": body["scope"],
            "source_body_sha256": sha(wire(body)), "nodes": nodes, "edges": edges,
            "authority_effect": "none"}


def context_view(mapping: dict, body: dict, scope: str) -> dict:
    need(scope == body["scope"] == mapping["scope"], "CONTEXT_SCOPE")
    need(mapping["source_body_sha256"] == sha(wire(body)), "CONTEXT_SOURCE_BINDING")
    need(mapping == map_source(body), "CONTEXT_MAPPING_BINDING")
    identities = [row["id"] for row in mapping["nodes"] + mapping["edges"]]
    need(len(identities) == len(set(identities)) == 25, "CONTEXT_CLOSURE")
    return {"schema": "lab-local-chain-context-view/v1-fixture", "scope": scope,
            "mapping_sha256": sha(wire(mapping)), "source_body_sha256": sha(wire(body)),
            "included_refs": identities, "node_count": 15, "edge_count": 10,
            "authority_effect": "none", "actual_owner_outcome": None}


def run() -> dict:
    work = load_work_product()
    now = datetime.now(timezone.utc)
    body = source_body(work, now)
    key = Ed25519PrivateKey.generate()
    public = key.public_key().public_bytes(serialization.Encoding.Raw,
                                           serialization.PublicFormat.Raw).hex()
    signed = sign_source(body, key)
    with TemporaryDirectory(prefix="cal-local-chain-") as directory:
        root = Path(directory)
        (root / "source.json").write_bytes(signed)
        selected = read_source((root / "source.json").read_bytes(), SCOPE, now,
                               public, sha(wire(work)))
        mapping = map_source(selected)
        (root / "mapping.json").write_bytes(wire(mapping))
        need(plain_json((root / "mapping.json").read_bytes()) == mapping, "MAPPING_READBACK")
        view = context_view(mapping, selected, SCOPE)
        (root / "context.json").write_bytes(wire(view))
        need(plain_json((root / "context.json").read_bytes()) == view, "CONTEXT_READBACK")
    need(not root.exists(), "TEMPORARY_STATE_REMAINS")
    return {"status": "PASS_LOCAL_CHAIN_FIXTURE", "source": sha(signed),
            "reader": "ED25519_SIGNATURE_SCOPE_PERIOD_PASS", "mapper": sha(wire(mapping)),
            "context": sha(wire(view)), "nodes": 15, "edges": 10,
            "work_runtime": work["runtime"], "work_replay": work["fresh_process_replay"],
            "temporary_state_removed": True, "external_effects": 0,
            "authority_effect": "none", "original_roles_executed": False,
            "claim_ceiling": "Disposable local four-phase fixture over the admitted Work runtime; no original Source8/Reader/Mapper/Context role qualification."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    options = parser.parse_args()
    try:
        result = run()
    except (Refused, OSError, ValueError) as error:
        print(f"Local chain fixture failed: {error}", file=__import__("sys").stderr)
        return 1
    if options.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("CyberAlchemy Lab — local Source → Reader → Mapper → Context fixture: PASS")
        print(f"Work runtime: {result['work_runtime']}; fresh-process replay: {result['work_replay']}")
        print(f"Source: signed local fixture {result['source']}")
        print(f"Reader: {result['reader']}")
        print(f"Mapper: {result['nodes']} nodes, {result['edges']} edges; {result['mapper']}")
        print(f"Context: 25 bound references; {result['context']}")
        print("Temporary state removed; external effects: 0")
        print("Profile: disposable fixture; original Source8/Reader/Mapper/Context roles not executed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
