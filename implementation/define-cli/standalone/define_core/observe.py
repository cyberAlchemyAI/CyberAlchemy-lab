"""Later observations accept explicit current evidence and never mutate a Pack."""
from datetime import datetime, timezone
from .exact import binding, decode, sha


def observe(buffers, requested_use, consumer, current_source=None):
    pack_raw = buffers["pack.json"];pack = decode(pack_raw);capture = decode(buffers["capture.json"])
    source = capture["source_profile_binding"]
    freshness = "not-evaluable" if current_source is None else "ready" if sha(current_source) == source["sha256"] else "blocked"
    same = requested_use == pack["scope"]["intended_use"]
    inspect_only = requested_use == "inspect-preparation"
    return {"schema_version": "define.use-observation/v2", "pack_binding": binding(pack_raw, "pack.json"),
            "requested_use": requested_use, "consumer": consumer, "observed_at": datetime.now(timezone.utc).isoformat(),
            "frozen_integrity": "verified", "same_intended_use": same, "source_profile_freshness": freshness,
            "current_source_profile_binding": None if current_source is None else binding(current_source, source["path"]),
            "outcome": "blocked" if not same or not inspect_only or freshness == "blocked" else "ready" if freshness == "ready" else "not-evaluable",
            "operational_authorization": "not-established", "actual_owner_outcome": None,
            "limitations": ["Exact reconstruction remains available without current source evidence.",
                            "A caller-supplied source comparison is not authenticated freshness or permission.",
                            "Changed use or inputs require a new frozen revision."], "authority_effect": "none"}
