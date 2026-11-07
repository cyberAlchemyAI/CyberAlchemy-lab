"""A later-use observation never rewrites the frozen Pack."""
from datetime import datetime, timezone
from pathlib import Path
from .exact import binding, decode, encode, read, sha, write_package
from .package import inspect_local


def observe(directory, requested_use, consumer, repo, destination):
    _, _, _, buffers = inspect_local(directory)
    pack_raw = buffers["pack.json"];pack = decode(pack_raw);capture = decode(buffers["capture.json"])
    source = capture["source_profile_binding"]
    current = read(Path(repo) / source["path"])
    unchanged = sha(current) == source["sha256"]
    same_use = requested_use == pack["scope"]["intended_use"]
    ready = unchanged and same_use and requested_use == "inspect-preparation"
    result = {"observation_id": "observation:" + sha(encode({"pack": sha(pack_raw), "use": requested_use, "consumer": consumer})),
              "schema_version": "cal.define.use-observation/v1", "pack_binding": binding(pack_raw, "pack.json"),
              "captured_intended_use_binding": binding(encode(pack["scope"]["intended_use"]), "scope-intended-use.json"),
              "requested_use": requested_use, "current_source_profile_binding": binding(current, source["path"]),
              "current_cut": {"kind": "repository-registry", "sha256": sha(current)}, "observed_at": datetime.now(timezone.utc).isoformat(),
              "consumer_binding": {"consumer": consumer, "posture": "explicit-local-request"}, "permission_observation_binding": None,
              "obligation_results": [
                  {"obligation": "unchanged-source-profile", "result": "ready" if unchanged else "blocked", "evidence": [sha(current)], "affected_scope": requested_use},
                  {"obligation": "same-frozen-intended-use", "result": "ready" if same_use else "blocked", "evidence": [sha(pack_raw)], "affected_scope": requested_use},
                  {"obligation": "current-host-permission", "result": "not-evaluable", "evidence": [], "affected_scope": "operational-use"}],
              "evidence_bindings": [], "outcome": "ready" if ready else "blocked",
              "limitations": ["Local frozen inspection only; no live permission observation.", "Changed intended use or inputs require a new frozen revision; this observation cannot amend the Pack."], "authority_effect": "none"}
    write_package(destination, {"observation.json": encode(result)})
    return result
