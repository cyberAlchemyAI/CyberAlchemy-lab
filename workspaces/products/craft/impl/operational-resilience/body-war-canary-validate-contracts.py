#!/usr/bin/env python3
"""Pure no-effect validation for the Body War canary contract family."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
EXPECTED_TABLETOP_IDS = [f"T{i:02d}" for i in range(1, 33)]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_config(value: dict) -> list[str]:
    errors: list[str] = []
    exact = {
        "platform": "linux/amd64",
        "runtime_admission": "denied",
        "authority_effect": "none",
        "source_mode": "runtime-receipt-derived-offline-snapshot",
    }
    for key, expected in exact.items():
        if value.get(key) != expected:
            errors.append(f"{key} must equal {expected}")
    ports = value.get("ports", {})
    if ports != {"bind":"127.0.0.1","gateway_data":18080,"gateway_control":18081,"stable":18101,"candidate":18102,"prometheus":19090}:
        errors.append("ports must be the exact loopback-only set")
    topology = value.get("topology", {})
    if topology != {"services":4,"networks":1,"named_volumes":0,"public_ingress":False,"real_strava":False,"persistent_storage":False}:
        errors.append("topology must be four services, one network, and zero persistent/public scope")
    limits = value.get("limits", {})
    expected_limits = {"cpu":0.5,"memory_mib":256,"pids":128,"app_tmpfs_mib":16,"prometheus_tmpfs_mib":128,"prometheus_retention_minutes":30,"prometheus_retention_mib":64,"max_inflight":10,"hard_inflight":20,"request_timeout_ms":1000,"max_scheduled":900,"max_evidence_bytes":33554432}
    if limits != expected_limits:
        errors.append("numeric safety limits drifted")
    thresholds = value.get("thresholds", {})
    if thresholds != {"candidate_min_total":20,"stable_min_total":180,"candidate_bad_rate_min":0.2,"stable_bad_rate_max":0.01,"rollback_deadline_ms":20000,"teardown_deadline_ms":30000}:
        errors.append("decision thresholds drifted")
    return errors


def main() -> int:
    schema_paths = sorted((ROOT / "contracts").glob("body-war-canary-*.schema.json"))
    assert len(schema_paths) == 5, f"expected five schemas, got {len(schema_paths)}"
    for path in schema_paths:
        schema = load_json(path)
        assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
        assert schema.get("type") == "object"
        assert schema.get("additionalProperties") is False
        assert schema.get("required")

    config = load_json(ROOT / "fixtures/valid/body-war-canary-local-config.json")
    assert validate_config(config) == []
    for mutation in (
        ("public-bind", lambda x: x["ports"].__setitem__("bind", "0.0.0.0")),
        ("named-volume", lambda x: x["topology"].__setitem__("named_volumes", 1)),
        ("disabled-threshold", lambda x: x["thresholds"].__setitem__("candidate_bad_rate_min", 0)),
        ("runtime-admission", lambda x: x.__setitem__("runtime_admission", "admitted")),
    ):
        hostile = copy.deepcopy(config)
        mutation[1](hostile)
        assert validate_config(hostile), f"hostile mutation accepted: {mutation[0]}"

    provenance = load_json(ROOT / "contracts/body-war-canary-dependency-provenance.json")
    assert provenance["package_installation_performed"] is False
    assert provenance["network_access_performed"] is False
    for row in provenance["poker_team_manifests"]:
        source = REPO / row["path"]
        assert source.is_file(), source
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row["sha256"], source

    tabletop = load_json(ROOT / "fixtures/hostile/body-war-canary-tabletop-cases.json")
    ids = [case["id"] for case in tabletop["cases"]]
    assert ids == EXPECTED_TABLETOP_IDS
    assert len({case["discriminator"] for case in tabletop["cases"]}) == 32
    assert tabletop["authority_effect"] == "none"
    print("CONTRACT_SCHEMAS=5")
    print("GOLDEN_CONFIG=pass")
    print("HOSTILE_CONFIGS=4/4 rejected")
    print("PROVENANCE=pass")
    print("TABLETOP_CASES=32/32")
    print("AUTHORITY_EFFECT=none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
