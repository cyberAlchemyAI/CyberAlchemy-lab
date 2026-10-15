"""Blinded evaluation mechanics. No semantic judgments are made here.

Packet/review binding: every review supplies ``packet_sha256`` from its packet.
Main rows are keyed by ``unit_id:raw_id``. Pair rows use opaque pair/arm IDs.
Runtime completion must be witnessed by a terminal join/skip or runtime.status().
Native event records accept job_id, event/type, status/terminal_status and a
validation boolean or {valid: bool}; a completed file alone is never evidence.

Optional adjudication accepts scalar resolutions only, and only for declared
disagreements; agreed values are immutable. Family disputes remain uncertain.
Format: {resolutions: [{candidate_key, field, value, reason}], unresolved: [...]}.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ADMIN_KEYS = {"condition", "method", "method_name", "job_id", "role",
              "role_prompt", "prompt", "template", "prefix", "stage",
              "repetition", "source_path", "source_file", "filename"}
ID_KEYS = ("raw_id", "opening_id", "candidate_id", "source_id", "post_id", "id")
ROW_KEYS = ("openings", "candidates", "raw", "proposals", "mechanisms",
            "questions", "items", "alternatives", "entries")
FIT = {"preserves", "uncertain", "conditional", "violates"}
SUPPORT = {"stipulated", "inference", "speculative", "unsupported"}
RETENTION = {"retained", "lost", "uncertain", "unobservable"}
MAIN_SCALARS = ("intelligible", "kind", "novelty", "usefulness", "fit",
                "observability", "support", "retention", "contract")
P08_SCALARS = ("decision_relevant", "competing_predictions", "probe_feasible",
               "fit", "support", "distinct_question", "unresolved_contradictions")
P09_SCALARS = ("causal_relation", "discriminator", "uncertainty")
TERMINAL = {"completed", "complete", "succeeded", "success", "failed", "invalid",
            "missing", "skipped", "cancelled", "canceled", "error"}
SUCCESS = {"completed", "complete", "succeeded", "success", "valid"}


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def opaque(*parts: Any) -> str:
    return "x-" + digest(list(parts))[:24]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any, once: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "x" if once else "w"
    with path.open(mode, encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def semantic(value: Any) -> Any:
    """Remove named administrative keys, never rewrite arbitrary prose."""
    if isinstance(value, dict):
        return {k: semantic(v) for k, v in value.items() if k not in ADMIN_KEYS}
    if isinstance(value, list):
        return [semantic(v) for v in value]
    return value


def row_id(row: dict) -> str:
    for key in ID_KEYS:
        if isinstance(row.get(key), str) and row[key]:
            return row[key]
    raise ValueError("opening has no nonempty string ID")


def openings(value: Any) -> list[dict]:
    """Extract named opening arrays, retaining the complete original row."""
    rows: list[dict] = []
    if isinstance(value, list):
        if all(isinstance(row, dict) for row in value):
            rows = value
        else:
            raise ValueError("opening array must contain objects")
    elif isinstance(value, dict):
        for key in ROW_KEYS:
            if key in value:
                if not isinstance(value[key], list):
                    raise ValueError(f"{key} must be an array")
                rows.extend(openings(value[key]))
        if not rows and any(key in value for key in ID_KEYS):
            rows = [value]
        elif not rows and isinstance(value.get("outputs"), list):
            for output in value["outputs"]:
                rows.extend(openings(output))
        elif not rows and not any(key in value for key in ROW_KEYS):
            raise ValueError("no recognized opening array")
    else:
        raise ValueError("source must be an object or opening array")
    ids = [row_id(row) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate source opening IDs")
    return rows


def archive_ids(value: Any) -> list[str]:
    found: set[str] = set()
    def visit(item: Any) -> None:
        if isinstance(item, dict):
            for key in ("archive_id", "id"):
                if isinstance(item.get(key), str) and item[key]:
                    found.add(item[key])
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)
    visit(value)
    return sorted(found)


def source(root: Path, relative: str, private: dict) -> dict:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("source outside run")
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    _source_record(private, sha, str(path.relative_to(root.resolve())))
    return {"source_sha256": sha, "evidence": semantic(json.loads(raw))}


def _source_record(private: dict, sha: str, path: str) -> None:
    record = private.setdefault(sha, {"path": path, "paths": [], "sha256": sha})
    if path not in record["paths"]:
        record["paths"].append(path)


def _validation(record: dict) -> bool | None:
    validation = record.get("validation", record.get("output_validation"))
    if isinstance(validation, bool):
        return validation
    if isinstance(validation, dict):
        for key in ("valid", "ok"):
            if isinstance(validation.get(key), bool):
                return validation[key]
        if validation.get("status") in {"valid", "invalid"}:
            return validation["status"] == "valid"
    for key in ("output_valid", "validation_ok", "valid"):
        if isinstance(record.get(key), bool):
            return record[key]
    return None


def dispositions(root: Path) -> dict[str, dict]:
    """Use only terminal witnesses; file existence cannot complete a job."""
    result: dict[str, dict] = {}
    events = root / "receipts" / "events.jsonl"
    if not events.exists():
        events = root / "events.jsonl"
    if events.exists():
        for line in events.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            name = event.get("event", event.get("type", event.get("action")))
            job = event.get("job_id")
            status = event.get("terminal_status", event.get("status"))
            if not isinstance(job, str) or name not in {"join", "skip"}:
                continue
            if name == "join" and (event.get("terminal_observed") is False or event.get("native") is False):
                continue
            if name == "skip":
                status = "skipped"
            elif status is None and event.get("native") is True and event.get("terminal_observed") is True:
                status = "valid" if _validation(event) is True else "failed"
            if status not in TERMINAL and status != "valid":
                continue
            validation = _validation(event)
            # An observed success without exact output validation is incomplete.
            execution = ("valid" if status in SUCCESS and validation is True else
                         "invalid" if status in SUCCESS or status == "invalid" else
                         "skipped" if status == "skipped" else "missing" if status == "missing" else "invalid")
            result[job] = {"terminal_status": status, "execution": execution,
                           "terminal_observed": True, "validation": validation,
                           "witness": "event_stream", "witness_sha256": event.get("sha256")}
    # Runtime is optional; do not depend on reading or modifying its source here.
    runtime_path = root / "tools" / "runtime.py"
    if runtime_path.exists():
        try:
            spec = importlib.util.spec_from_file_location("evaluation_runtime", runtime_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            status_value = module.status()
            if isinstance(status_value, dict):
                states = status_value.get("jobs", status_value)
                if isinstance(states, list):
                    states = {r["job_id"]: r for r in states if isinstance(r, dict) and "job_id" in r}
                if isinstance(states, dict):
                    for job, state in states.items():
                        if job in result or not isinstance(state, dict):
                            continue
                        terminal = state.get("terminal_status", state.get("status"))
                        if terminal not in TERMINAL and terminal != "valid":
                            continue
                        validation = _validation(state)
                        if terminal == "valid" and isinstance(state.get("errors"), list):
                            validation = not state["errors"]
                        execution = ("valid" if terminal in SUCCESS and validation is True else
                                     "invalid" if terminal in SUCCESS or terminal == "invalid" else
                                     "skipped" if terminal == "skipped" else "missing" if terminal == "missing" else "invalid")
                        result[job] = {"terminal_status": terminal, "execution": execution,
                                       "terminal_observed": True, "validation": validation,
                                       "witness": "runtime_status", "witness_sha256": state.get("sha256")}
        except (ImportError, AttributeError, TypeError, ValueError, OSError):
            pass
    return result


def job_output(root: Path, job_id: str, states: dict, private: dict) -> dict:
    state = states.get(job_id, {"execution": "missing", "terminal_status": "unobserved",
                                "terminal_observed": False, "validation": None,
                                "witness": None})
    packet = {"disposition": {k: v for k, v in state.items() if k != "witness"},
              "source_sha256": None, "evidence": None, "openings": [],
              "observed_output_words": 0}
    path = root / "outputs" / f"{job_id}.json"
    if path.exists():
        saved = path.read_bytes()
        packet["observed_output_words"] = len(saved.decode("utf-8", errors="replace").split())
        sha = hashlib.sha256(saved).hexdigest()
        packet["source_sha256"] = sha
        _source_record(private, sha, str(path.relative_to(root)))
        if state.get("witness_sha256") and sha != state["witness_sha256"]:
            packet["disposition"]["execution"] = "invalid"
            packet["disposition"]["output_error"] = "terminal output hash mismatch"
    if path.exists():
        try:
            binding = source(root, str(path.relative_to(root)), private)
            packet.update(binding)
            rows = openings(binding["evidence"])
            packet["openings"] = [{"raw_id": row_id(r)} for r in rows]
        except (OSError, ValueError, TypeError, KeyError) as error:
            packet["disposition"] = {**packet["disposition"], "execution": "invalid",
                                      "output_error": str(type(error).__name__)}
    elif packet["disposition"]["execution"] == "valid":
        packet["disposition"]["execution"] = "invalid"
        packet["disposition"]["output_error"] = "native terminal output missing"
    return packet


def _source_paths(sources: Any) -> list[str]:
    if isinstance(sources, str):
        return [sources]
    if isinstance(sources, list):
        return [path for item in sources for path in _source_paths(item)]
    if isinstance(sources, dict):
        return [path for item in sources.values() for path in _source_paths(item)]
    return []


def _case_paths(schedule: dict, case_id: str, root: Path) -> tuple[str, str]:
    bindings = schedule.get("cases", {})
    case = bindings.get(case_id, {}) if isinstance(bindings, dict) else {}
    if isinstance(case, dict) and "case" in case and "archive" in case:
        return case["case"], case["archive"]
    for job in schedule["jobs"]:
        if job.get("case_id") == case_id and isinstance(job.get("sources"), dict):
            sources = job["sources"]
            if isinstance(sources.get("case"), str) and isinstance(sources.get("archive"), str):
                return sources["case"], sources["archive"]
    scheduled = [p for j in schedule["jobs"] if j.get("case_id") == case_id
                 for p in _source_paths(j.get("sources", []))]
    # Explicit common paths, used only if no schedule binding was provided.
    case_paths = [f"cases/{case_id}.json", f"inputs/{case_id}.json"]
    archive_paths = [f"archives/{case_id}.json", f"inputs/{case_id}-archive.json"]
    case_path = next((p for p in scheduled if p == f"cases/{case_id}.json"), None)
    case_path = case_path or next((p for p in case_paths if (root / p).exists()), None)
    archive_paths.append(f"archives/{case_id}-archive.json")
    archive_path = next((p for p in scheduled if "archive" in p and Path(p).suffix == ".json"), None)
    archive_path = archive_path or next((p for p in archive_paths if (root / p).exists()), None)
    if not case_path or not archive_path:
        raise ValueError("schedule must bind case and archive source paths")
    return case_path, archive_path


def _seal(packet: dict) -> dict:
    packet["packet_sha256"] = digest(packet)
    return packet


def _prepare_main(root: Path, schedule: dict, case_id: str, states: dict,
                  private: dict) -> tuple[dict, dict]:
    case_path, archive_path = _case_paths(schedule, case_id, root)
    case = source(root, case_path, private["sources"])
    archive = source(root, archive_path, private["sources"])
    jobs = {j["job_id"]: j for j in schedule["jobs"]}
    input_paths = list(dict.fromkeys(p for j in schedule["jobs"]
                                   if j.get("case_id") == case_id and j.get("stage") in {"main", "critique"}
                                   for p in _source_paths(j.get("sources", []))
                                   if not p.startswith("outputs/") and p not in {case_path, archive_path}))
    shared_sources = [source(root, p, private["sources"]) for p in input_paths]
    input_hashes = {p: b["source_sha256"] for p, b in zip(input_paths, shared_sources)}
    units = []
    for unit in schedule["units"]:
        if unit["case_id"] != case_id:
            continue
        unit_id = opaque(case_id, unit["unit_id"])
        raw = [job_output(root, job, states, private["sources"]) for job in unit["raw_jobs"]]
        post = job_output(root, unit["post_job"], states, private["sources"])
        # IDs must remain exact; repeated shared Z IDs in different units are legal.
        ids = [r["raw_id"] for output in raw for r in output["openings"]]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate opening IDs within unit")
        packet_unit = {"unit_id": unit_id, "semantic_requirement": unit["semantic_requirement"],
                       "raw": raw, "post": post,
                       "raw_semantic_requirements": {r["raw_id"]: (
                           "Source-grounded incumbent mechanism/question with rival prediction, defeat and bounded probe; preserve outcome and constraints"
                           if r["raw_id"].startswith("Z") else unit["semantic_requirement"])
                           for o in raw for r in o["openings"]},
                       "input_source_sha256s": sorted(set(input_hashes[p]
                           for job_id in [*unit["raw_jobs"], unit["post_job"]]
                           for p in _source_paths(jobs[job_id].get("sources", [])) if p in input_hashes))}
        units.append(packet_unit)
        private["units"][unit_id] = copy.deepcopy(unit)
    base = {"kind": "main", "case_id": case_id, "case": case, "archive": archive,
            "known_archive_ids": archive_ids(archive["evidence"]), "units": units,
            "shared_sources": shared_sources,
            "limits": "Method labels are hidden; semantic content may remain recognizable.",
            "expected_coverage": {"unit_ids": [u["unit_id"] for u in units],
                                  "raw_ids": {u["unit_id"]: _main_raw_ids(u) for u in units},
                                  "post_ids": {u["unit_id"]: _post_ids(u["post"]) for u in units}}}
    left = _seal(copy.deepcopy(base))
    right = copy.deepcopy(base)
    right["units"].reverse()
    for unit in right["units"]:
        unit["raw"].reverse()
    return left, _seal(right)


def _prepare_pairs(root: Path, schedule: dict, kind: str, states: dict,
                   private: dict) -> tuple[dict, dict]:
    jobs = {j["job_id"]: j for j in schedule["jobs"]}
    pairs = []
    for pair in schedule[f"{kind}_pairs"]:
        pair_id = opaque(kind, pair["pair_id"])
        private["pairs"][pair_id] = copy.deepcopy(pair)
        source_paths = ([pair["case"], *pair["raw_sources"]] if kind == "p09" else
                        _source_paths(jobs[next(iter(pair["arms"].values()))].get("sources", [])))
        # Explicitly exclude evaluator-only artifacts even if inadvertently bound.
        forbidden = pair.get("evaluator_only")
        source_paths = list(dict.fromkeys(p for p in source_paths if p != forbidden))
        bindings = [source(root, p, private["sources"]) for p in source_paths]
        if kind == "p08":
            _, archive_path = _case_paths(schedule, pair["case_id"], root)
            if archive_path not in source_paths:
                bindings.append(source(root, archive_path, private["sources"]))
        raw_ids = []
        if kind == "p09":
            raw_bindings = [source(root, p, private["sources"]) for p in pair["raw_sources"]]
            raw_ids = [row_id(r) for b in raw_bindings for r in openings(b["evidence"])]
            if len(raw_ids) != len(set(raw_ids)):
                raise ValueError("duplicate raw source IDs in pair")
        arms = []
        for label, job_id in pair["arms"].items():
            arm_id = opaque(kind, pair["pair_id"], job_id)
            arms.append({"arm_id": arm_id, "output": job_output(root, job_id, states, private["sources"])})
            private["arms"][arm_id] = {"pair_id": pair["pair_id"], "arm": label, "job_id": job_id}
        pairs.append({"pair_id": pair_id, "sources": bindings, "raw_ids": raw_ids, "arms": arms})
    base = {"kind": kind, "pairs": pairs,
            "limits": "Method labels are hidden; semantic content may remain recognizable.",
            "expected_coverage": {p["pair_id"]: {"arm_ids": [a["arm_id"] for a in p["arms"]],
                                                  "raw_ids": p["raw_ids"]} for p in pairs}}
    left = _seal(copy.deepcopy(base))
    right = copy.deepcopy(base)
    right["pairs"].reverse()
    for pair in right["pairs"]:
        pair["arms"].reverse()
    return left, _seal(right)


def prepare(kind: str, case_id: str | None = None, root: Path = ROOT) -> list[Path]:
    if kind not in {"main", "p08", "p09"} or (kind == "main" and not case_id):
        raise ValueError("prepare requires main CASE, p08, or p09")
    stem = f"main-{case_id}" if kind == "main" else kind
    paths = [root / "blinded" / f"{stem}-J{i}.json" for i in (1, 2)]
    mapping_path = root / "blinded" / f"{stem}-mapping.json"
    if any(path.exists() for path in [*paths, mapping_path]):
        raise FileExistsError("packets/mapping are once-only; existing files cannot be replaced")
    schedule = read_json(root / "schedule.json")
    private = {"sources": {}, "units": {}, "pairs": {}, "arms": {}}
    states = dispositions(root)
    if kind == "main":
        packets = _prepare_main(root, schedule, case_id, states, private)
    else:
        packets = _prepare_pairs(root, schedule, kind, states, private)
    for path, packet in zip(paths, packets):
        write_json(path, packet, once=True)
    write_json(mapping_path, private, once=True)
    return paths


def _main_raw_ids(unit: dict) -> list[str]:
    return [r["raw_id"] for output in unit["raw"] for r in output["openings"]]


def _main_raw_sources(unit: dict) -> dict[str, dict]:
    result = {}
    for output in unit["raw"]:
        if output["evidence"] is None:
            continue
        try:
            rows = openings(output["evidence"])
        except (TypeError, ValueError):
            continue
        for row in rows:
            result[row_id(row)] = {"source_sha256": output["source_sha256"],
                                   "claim": row.get("claim"), "source_evidence": row,
                                   "execution_valid": output["disposition"]["execution"] == "valid"}
    return result


def _post_ids(output: dict) -> list[str]:
    return [r["raw_id"] for r in output["openings"]]


def _post_valid(unit: dict) -> bool:
    return unit["post"]["disposition"]["execution"] == "valid"


def _rows(value: Any, context: str, errors: list[str]) -> list[dict]:
    if not isinstance(value, list):
        errors.append(f"{context}: expected array")
        return []
    good = []
    for index, row in enumerate(value):
        if not isinstance(row, dict):
            errors.append(f"{context}[{index}]: expected object")
        else:
            good.append(row)
    return good


def _exact(rows: list[dict], key: str, expected: list[str], context: str,
           errors: list[str]) -> dict[str, dict]:
    indexed = {}
    for row in rows:
        identifier = row.get(key)
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{context}: {key} must be nonempty string")
        elif identifier in indexed:
            errors.append(f"{context}: duplicate {identifier}")
        else:
            indexed[identifier] = row
    for identifier in sorted(set(expected) - set(indexed)):
        errors.append(f"{context}: missing {identifier}")
    for identifier in sorted(set(indexed) - set(expected)):
        errors.append(f"{context}: unknown {identifier}")
    return indexed


def _field(row: dict, key: str, allowed: set | type, context: str,
           errors: list[str]) -> None:
    value = row.get(key)
    if isinstance(allowed, set):
        valid = isinstance(value, (str, int, bool)) and value in allowed
    elif allowed is int:
        valid = type(value) is int
    else:
        valid = isinstance(value, allowed)
    if not valid:
        errors.append(f"{context}: invalid {key}")


def _strings(row: dict, keys: tuple[str, ...], context: str, errors: list[str]) -> None:
    for key in keys:
        _field(row, key, str, context, errors)


def _packet_check(kind: str, packet: dict, review: dict, errors: list[str]) -> None:
    if packet.get("kind") != kind:
        errors.append("packet kind mismatch")
    sealed = {k: v for k, v in packet.items() if k != "packet_sha256"}
    if packet.get("packet_sha256") != digest(sealed):
        errors.append("packet hash invalid")
    if review.get("packet_sha256") != packet.get("packet_sha256"):
        errors.append("review packet hash mismatch or missing")
    _strings(review, ("reviewer_id", "limits"), "review", errors)


def _check_main(packet: dict, review: dict, errors: list[str]) -> None:
    if review.get("case_id") != packet["case_id"]:
        errors.append("case_id mismatch")
    units = {u["unit_id"]: u for u in packet["units"]}
    rows = _exact(_rows(review.get("units"), "units", errors), "unit_id",
                  list(units), "units", errors)
    families = _rows(review.get("families"), "families", errors)
    family_ids = [f.get("family_id") for f in families]
    if any(not isinstance(f, str) or not f for f in family_ids):
        errors.append("families: invalid family_id")
    if len([f for f in family_ids if isinstance(f, str)]) != len(set(f for f in family_ids if isinstance(f, str))):
        errors.append("families: duplicate family_id")
    known = set(f for f in family_ids if isinstance(f, str))
    declared: dict[str, str] = {}
    for family in families:
        fid = family.get("family_id")
        _strings(family, ("signature", "reason"), "family", errors)
        for field, allowed in (("archive_matches", set(packet["known_archive_ids"])),
                               ("uncertain_with", known - {fid} if isinstance(fid, str) else known)):
            values = family.get(field)
            if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
                errors.append(f"family {fid}: invalid {field}")
            elif len(values) != len(set(values)) or not set(values) <= allowed:
                errors.append(f"family {fid}: unknown or duplicate {field}")
        members = family.get("members")
        if not isinstance(members, list) or not members or any(not isinstance(m, str) for m in members):
            errors.append(f"family {fid}: members must be nonempty string array")
            continue
        for member in members:
            if member in declared:
                errors.append(f"families: duplicate member {member}")
            declared[member] = fid
    expected_members: dict[str, str] = {}
    for uid, unit in units.items():
        row = rows.get(uid)
        if row is None:
            continue
        _strings(row, ("lineage_comment",), uid, errors)
        raws = _exact(_rows(row.get("raw"), f"{uid}.raw", errors), "raw_id",
                     _main_raw_ids(unit), f"{uid}.raw", errors)
        for raw_id, raw in raws.items():
            context = f"{uid}:{raw_id}"
            _field(raw, "intelligible", bool, context, errors)
            for field, allowed in (("kind", {"mechanism", "hypothesis", "question"}),
                                   ("novelty", {"new", "equivalent", "parameter", "uncertain"}),
                                   ("fit", FIT), ("support", SUPPORT), ("retention", RETENTION),
                                   ("contract", {"met", "partial", "not_met", "inapplicable"})):
                _field(raw, field, allowed, context, errors)
            for field in ("usefulness", "observability"):
                _field(raw, field, int, context, errors)
                if type(raw.get(field)) is int and raw[field] not in (0, 1, 2):
                    errors.append(f"{context}: {field} outside 0..2")
            _strings(raw, ("reason", "retention_reason"), context, errors)
            family_id = raw.get("family_id")
            if raw.get("intelligible") is True:
                if not isinstance(family_id, str) or family_id not in known:
                    errors.append(f"{context}: undeclared family")
                else:
                    expected_members[context] = family_id
            elif family_id is not None:
                errors.append(f"{context}: unintelligible candidate requires null family")
            if not _post_valid(unit) and raw.get("retention") != "unobservable":
                errors.append(f"{context}: failed/missing D requires unobservable retention")
        post_rows = _rows(row.get("post_only"), f"{uid}.post_only", errors)
        seen = set()
        post_ids = set(_post_ids(unit["post"]))
        for post in post_rows:
            pid = post.get("post_id")
            if not isinstance(pid, str) or pid not in post_ids or pid in seen:
                errors.append(f"{uid}.post_only: unknown/duplicate post_id")
            else:
                seen.add(pid)
            _field(post, "support", SUPPORT, uid, errors)
            _field(post, "fit", FIT, uid, errors)
            _strings(post, ("reason",), uid, errors)
    if declared != expected_members:
        errors.append("family partition does not match exactly all intelligible unit_id:raw_id rows")


def _check_pairs(kind: str, packet: dict, review: dict, errors: list[str]) -> None:
    pairs = {p["pair_id"]: p for p in packet["pairs"]}
    rows = _exact(_rows(review.get("pairs"), "pairs", errors), "pair_id", list(pairs), "pairs", errors)
    for pid, pair in pairs.items():
        row = rows.get(pid)
        if row is None:
            continue
        _strings(row, ("contrast",), pid, errors)
        packet_arms = {a["arm_id"]: a for a in pair["arms"]}
        arms = _exact(_rows(row.get("arms"), f"{pid}.arms", errors), "arm_id",
                      list(packet_arms), f"{pid}.arms", errors)
        for aid, arm in arms.items():
            _field(arm, "fit", FIT, aid, errors)
            _strings(arm, ("reason",), aid, errors)
            if kind == "p08":
                for field in ("decision_relevant", "competing_predictions", "distinct_question"):
                    _field(arm, field, bool, aid, errors)
                _field(arm, "probe_feasible", FIT, aid, errors)
                _field(arm, "support", SUPPORT, aid, errors)
                _field(arm, "unresolved_contradictions", int, aid, errors)
                if type(arm.get("unresolved_contradictions")) is int and arm["unresolved_contradictions"] < 0:
                    errors.append(f"{aid}: unresolved_contradictions must be nonnegative")
            else:
                raws = _exact(_rows(arm.get("raw"), f"{aid}.raw", errors), "source_id",
                              pair["raw_ids"], f"{aid}.raw", errors)
                for rid, raw in raws.items():
                    for field in P09_SCALARS:
                        _field(raw, field, RETENTION, f"{aid}:{rid}", errors)
                        if packet_arms.get(aid, {}).get("output", {}).get("disposition", {}).get("execution") != "valid" and raw.get(field) != "unobservable":
                            errors.append(f"{aid}:{rid}: missing/failed arm requires unobservable {field}")
                    _strings(raw, ("reason",), f"{aid}:{rid}", errors)
                post_ids = set(_post_ids(packet_arms.get(aid, {}).get("output", {"openings": []})))
                seen = set()
                for post in _rows(arm.get("unsupported_additions"), f"{aid}.unsupported_additions", errors):
                    post_id = post.get("post_id")
                    if not isinstance(post_id, str) or post_id not in post_ids or post_id in seen:
                        errors.append(f"{aid}: unknown/duplicate unsupported addition post_id")
                    else:
                        seen.add(post_id)
                    _strings(post, ("reason",), aid, errors)


def check(kind: str, packet: Any, review: Any) -> list[str]:
    """Return all discovered structural errors; never repair reviewer content."""
    errors: list[str] = []
    if not isinstance(packet, dict) or not isinstance(review, dict):
        return ["packet and review must be objects"]
    if kind not in {"main", "p08", "p09"}:
        return ["unknown review kind"]
    try:
        _packet_check(kind, packet, review, errors)
        (_check_main(packet, review, errors) if kind == "main" else
         _check_pairs(kind, packet, review, errors))
    except (KeyError, TypeError, ValueError) as error:
        errors.append(f"malformed packet/review structure: {type(error).__name__}")
    return errors


def _review_main_rows(review: dict) -> dict[str, dict]:
    return {f'{u["unit_id"]}:{r["raw_id"]}': r for u in review["units"] for r in u["raw"]}


def _family_relation(review: dict) -> tuple[set[tuple], set[tuple], dict[str, str]]:
    same, uncertain, assignments = set(), set(), {}
    by_id = {f["family_id"]: f for f in review["families"]}
    for family in review["families"]:
        members = sorted(family["members"])
        for member in members:
            assignments[member] = family["family_id"]
        for i, left in enumerate(members):
            for right in members[i + 1:]:
                same.add((left, right))
        for other in family["uncertain_with"]:
            for left in members:
                for right in by_id[other]["members"]:
                    uncertain.add(tuple(sorted((left, right))))
    return same, uncertain, assignments


def _components(edges: set[tuple], vertices: set[str]) -> list[list[str]]:
    neighbors = {v: set() for v in vertices}
    for left, right in edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    result = []
    remaining = set(vertices)
    while remaining:
        first = min(remaining)
        pending, component = [first], set()
        while pending:
            current = pending.pop()
            if current in component:
                continue
            component.add(current)
            pending.extend(neighbors[current] - component)
        remaining -= component
        result.append(sorted(component))
    return result


def _scalar_disputes(left: dict, right: dict, fields: tuple[str, ...], target: str) -> list[dict]:
    return [{"target": target, "field": field, "review1": left[field], "review2": right[field]}
            for field in fields if left[field] != right[field]]


def compare(kind: str, packet1: dict, review1: dict, packet2: dict, review2: dict) -> dict:
    errors = {"review1": check(kind, packet1, review1), "review2": check(kind, packet2, review2)}
    if any(errors.values()):
        return {"kind": kind, "status": "incomplete", "errors": errors, "disputes": []}
    if review1["reviewer_id"] == review2["reviewer_id"]:
        return {"kind": kind, "status": "incomplete", "errors": {"reviewers": ["distinct reviewer IDs required"]}, "disputes": []}
    if _normalized_packet(packet1) != _normalized_packet(packet2):
        return {"kind": kind, "status": "incomplete", "errors": {"packets": ["reviewers were not given identical source evidence/coverage"]}, "disputes": []}
    disputes = []
    families = {"co_membership": [], "uncertain_links": [], "clusters": []}
    if kind == "main":
        left, right = _review_main_rows(review1), _review_main_rows(review2)
        for key in sorted(left):
            disputes.extend(_scalar_disputes(left[key], right[key], MAIN_SCALARS, key))
        same1, uncertain1, assigned1 = _family_relation(review1)
        same2, uncertain2, assigned2 = _family_relation(review2)
        co_difference = same1 ^ same2
        uncertainty_difference = uncertain1 ^ uncertain2
        families["co_membership"] = [list(edge) for edge in sorted(co_difference)]
        families["uncertain_links"] = [list(edge) for edge in sorted(uncertainty_difference)]
        changed_intelligibility = set(assigned1) ^ set(assigned2)
        # Entire connected family clusters are declared; a split cannot confirm
        # another link inside the same disputed equivalence cluster by accident.
        edges = same1 | same2 | uncertain1 | uncertain2
        touched = {m for edge in co_difference | uncertainty_difference for m in edge} | changed_intelligibility
        vertices = set(assigned1) | set(assigned2)
        families["clusters"] = [c for c in _components(edges, vertices) if set(c) & touched]
        left_units = {u["unit_id"]: u for u in review1["units"]}
        right_units = {u["unit_id"]: u for u in review2["units"]}
        for uid in sorted(left_units):
            p1 = {r["post_id"]: r for r in left_units[uid]["post_only"]}
            p2 = {r["post_id"]: r for r in right_units[uid]["post_only"]}
            for pid in sorted(set(p1) | set(p2)):
                target = f"{uid}:post:{pid}"
                if pid not in p1 or pid not in p2:
                    disputes.append({"target": target, "field": "presence", "review1": pid in p1, "review2": pid in p2})
                else:
                    disputes.extend(_scalar_disputes(p1[pid], p2[pid], ("support", "fit"), target))
        # Archive correspondence is a judgment independent of a family label.
        for key in sorted(set(assigned1) & set(assigned2)):
            f1 = next(f for f in review1["families"] if f["family_id"] == assigned1[key])
            f2 = next(f for f in review2["families"] if f["family_id"] == assigned2[key])
            if set(f1["archive_matches"]) != set(f2["archive_matches"]):
                disputes.append({"target": key, "field": "archive_matches", "review1": sorted(f1["archive_matches"]), "review2": sorted(f2["archive_matches"])})
    else:
        pairs1 = {p["pair_id"]: p for p in review1["pairs"]}
        pairs2 = {p["pair_id"]: p for p in review2["pairs"]}
        for pid in sorted(pairs1):
            arms1 = {a["arm_id"]: a for a in pairs1[pid]["arms"]}
            arms2 = {a["arm_id"]: a for a in pairs2[pid]["arms"]}
            for aid in sorted(arms1):
                if kind == "p08":
                    disputes.extend(_scalar_disputes(arms1[aid], arms2[aid], P08_SCALARS, f"{pid}:{aid}"))
                else:
                    disputes.extend(_scalar_disputes(arms1[aid], arms2[aid], ("fit",), f"{pid}:{aid}"))
                    raws1 = {r["source_id"]: r for r in arms1[aid]["raw"]}
                    raws2 = {r["source_id"]: r for r in arms2[aid]["raw"]}
                    for rid in sorted(raws1):
                        disputes.extend(_scalar_disputes(raws1[rid], raws2[rid], P09_SCALARS, f"{pid}:{aid}:{rid}"))
                    posts1 = {r["post_id"] for r in arms1[aid]["unsupported_additions"]}
                    posts2 = {r["post_id"] for r in arms2[aid]["unsupported_additions"]}
                    for post_id in sorted(posts1 ^ posts2):
                        disputes.append({"target": f"{pid}:{aid}:post:{post_id}", "field": "presence",
                                         "review1": post_id in posts1, "review2": post_id in posts2})
    return {"kind": kind, "status": "compared", "disputes": disputes,
            "families": families, "errors": errors,
            "semantic_adjudication": "none; disagreements declared without repair"}


def _normalized_packet(packet: dict) -> dict:
    value = copy.deepcopy(packet)
    value.pop("packet_sha256", None)
    if value["kind"] == "main":
        value["units"].sort(key=lambda u: u["unit_id"])
        for unit in value["units"]:
            unit["raw"].sort(key=lambda o: (o["source_sha256"] or "", digest(o)))
    else:
        value["pairs"].sort(key=lambda p: p["pair_id"])
        for pair in value["pairs"]:
            pair["arms"].sort(key=lambda a: a["arm_id"])
    return value


def _adjudicate(kind: str, comparison: dict, adjudication: Any) -> tuple[dict, list[str]]:
    if adjudication is None:
        return {}, []
    if not isinstance(adjudication, dict) or not isinstance(adjudication.get("resolutions"), list):
        return {}, ["adjudication resolutions must be an array"]
    if not isinstance(adjudication.get("unresolved", []), list):
        return {}, ["adjudication unresolved must be an array"]
    declared = {(d["target"], d["field"]): d for d in comparison["disputes"]}
    overrides, errors = {}, []
    enum_fields = {"kind": {"mechanism", "hypothesis", "question"},
                   "novelty": {"new", "equivalent", "parameter", "uncertain"},
                   "fit": FIT, "probe_feasible": FIT, "support": SUPPORT,
                   "retention": RETENTION, "causal_relation": RETENTION,
                   "discriminator": RETENTION, "uncertainty": RETENTION,
                   "contract": {"met", "partial", "not_met", "inapplicable"}}
    bool_fields = {"intelligible", "decision_relevant", "competing_predictions",
                   "distinct_question", "presence"}
    int_fields = {"usefulness", "observability", "unresolved_contradictions"}
    allowed_fields = ((set(MAIN_SCALARS) | {"presence"}) if kind == "main" else
                      set(P08_SCALARS) if kind == "p08" else set(P09_SCALARS) | {"fit", "presence"})
    for row in adjudication["resolutions"]:
        if not isinstance(row, dict):
            errors.append("adjudication resolution must be an object")
            continue
        key = row.get("candidate_key"), row.get("field")
        if not all(isinstance(v, str) for v in key):
            errors.append("adjudication requires string candidate_key and field")
            continue
        if key not in declared:
            errors.append(f"adjudication cannot edit agreed/undeclared field {key[0]}:{key[1]}")
            continue
        if key in overrides:
            errors.append(f"duplicate adjudication resolution {key[0]}:{key[1]}")
            continue
        field, value = key[1], row.get("value")
        valid = field in allowed_fields
        if field in enum_fields:
            valid = valid and isinstance(value, str) and value in enum_fields[field]
        elif field in bool_fields:
            valid = valid and type(value) is bool
        elif field in int_fields:
            valid = valid and type(value) is int and value >= 0
            if field != "unresolved_contradictions":
                valid = valid and value <= 2
        else:
            valid = False
        if not valid:
            errors.append(f"invalid scalar adjudication value for {key[0]}:{field}")
            continue
        if not isinstance(row.get("reason"), str) or not row["reason"].strip():
            errors.append(f"adjudication reason required for {key[0]}:{field}")
            continue
        overrides[key] = row
    return ({} if errors else overrides), errors


def _agreed(left: dict, right: dict, fields: tuple[str, ...], target: str = "",
            overrides: dict | None = None) -> tuple[dict, list[str]]:
    overrides = overrides or {}
    values, unresolved = {}, []
    for field in fields:
        if left[field] == right[field]:
            values[field] = left[field]
        elif (target, field) in overrides:
            values[field] = overrides[(target, field)]["value"]
        else:
            values[field] = None
            unresolved.append(field)
    return values, unresolved


def normalize_main(packet1: dict, review1: dict, packet2: dict, review2: dict,
                   mapping: dict, adjudication: dict | None = None) -> dict:
    result = {"case_id": packet1.get("case_id"), "status": "incomplete",
              "judgments_locked": False, "equivalence_review_locked": False,
              "families": [], "units": [], "unresolved": [],
              "sources": {"packet_hashes": [packet1.get("packet_sha256"), packet2.get("packet_sha256")],
                          "review_hashes": [digest(review1), digest(review2)],
                          "source_bindings": copy.deepcopy(mapping.get("sources", {}))}}
    comparison = compare("main", packet1, review1, packet2, review2)
    if comparison["status"] != "compared":
        result["unresolved"] = [{"coverage_errors": comparison["errors"]}]
        return result
    overrides, adjudication_errors = _adjudicate("main", comparison, adjudication)
    if adjudication_errors:
        result["unresolved"] = [{"adjudication_errors": adjudication_errors}]
        return result
    if adjudication is not None:
        result["sources"]["adjudication_sha256"] = digest(adjudication)
        result["sources"]["scalar_resolutions"] = list(overrides.values())
    rows1, rows2 = _review_main_rows(review1), _review_main_rows(review2)
    same1, uncertain1, assignment1 = _family_relation(review1)
    same2, uncertain2, assignment2 = _family_relation(review2)
    clusters = comparison["families"]["clusters"]
    affected = {m for cluster in clusters for m in cluster}
    # Confirm only common, unaffected membership. Disputed candidates stay
    # separate with explicit uncertain links; no semantic transitive merge.
    vertices = set(assignment1) | set(assignment2)
    agreed_edges = {edge for edge in same1 & same2 if not set(edge) & affected}
    groups = _components(agreed_edges, vertices)
    member_family = {}
    family_rows = {}
    for members in groups:
        fid = "f-" + digest(members)[:24]
        for member in members:
            member_family[member] = fid
        archive_sets = []
        signatures, reasons = [], []
        for review, assignments in ((review1, assignment1), (review2, assignment2)):
            for family in review["families"]:
                if set(family["members"]) & set(members):
                    archive_sets.append(set(family["archive_matches"]))
                    signatures.append(family["signature"])
                    reasons.append(family["reason"])
        archive_agrees = bool(archive_sets) and all(s == archive_sets[0] for s in archive_sets)
        family = {"family_id": fid, "members": members,
                  "equivalence_status": "uncertain" if set(members) & affected or not archive_agrees else "confirmed",
                  "uncertain_equivalence_with": [],
                  "archive_matches": sorted(archive_sets[0]) if archive_agrees else None,
                  "reviewed_signatures": signatures, "reviewed_reasons": reasons}
        result["families"].append(family)
        family_rows[fid] = family
    uncertain_edges = uncertain1 | uncertain2
    for cluster in clusters:
        uncertain_edges |= {(left, right) for i, left in enumerate(cluster) for right in cluster[i + 1:]}
    for left, right in uncertain_edges:
        if left in member_family and right in member_family:
            fid1, fid2 = member_family[left], member_family[right]
            if fid1 != fid2:
                family_rows[fid1]["uncertain_equivalence_with"].append(fid2)
                family_rows[fid2]["uncertain_equivalence_with"].append(fid1)
    for family in result["families"]:
        family["uncertain_equivalence_with"] = sorted(set(family["uncertain_equivalence_with"]))
    unit_rows1 = {u["unit_id"]: u for u in review1["units"]}
    unit_rows2 = {u["unit_id"]: u for u in review2["units"]}
    for unit in packet1["units"]:
        uid = unit["unit_id"]
        if uid not in mapping.get("units", {}):
            result["unresolved"] = [{"mapping_error": f"missing unit mapping {uid}"}]
            result["families"], result["units"] = [], []
            return result
        original = mapping["units"][uid]
        raw_sources = _main_raw_sources(unit)
        raw_rows = []
        for raw_id in _main_raw_ids(unit):
            key = f"{uid}:{raw_id}"
            fields, unresolved = _agreed(rows1[key], rows2[key], MAIN_SCALARS, key, overrides)
            family_id = member_family.get(key)
            raw_rows.append({"raw_id": raw_id, "family_id": family_id, **fields,
                             **raw_sources.get(raw_id, {"claim": None, "source_sha256": None,
                                                        "source_evidence": None, "execution_valid": False}),
                             "judgment_resolved": not unresolved,
                             "unresolved_fields": unresolved,
                             "raw_judgment_resolved": not any(field != "retention" for field in unresolved),
                             "raw_unresolved_fields": [field for field in unresolved if field != "retention"],
                             "review_reasons": [rows1[key]["reason"], rows2[key]["reason"]],
                             "retention_reasons": [rows1[key]["retention_reason"], rows2[key]["retention_reason"]]})
        post1 = {p["post_id"]: p for p in unit_rows1[uid]["post_only"]}
        post2 = {p["post_id"]: p for p in unit_rows2[uid]["post_only"]}
        post_rows = []
        for pid in sorted(set(post1) | set(post2)):
            if pid in post1 and pid in post2:
                fields, unresolved = _agreed(post1[pid], post2[pid], ("support", "fit"), f"{uid}:post:{pid}", overrides)
                presence = True
            else:
                fields = {"support": None, "fit": None}
                unresolved, presence = ["presence", "support", "fit"], None
                presence_override = overrides.get((f"{uid}:post:{pid}", "presence"))
                if presence_override:
                    presence = presence_override["value"]
                    unresolved = ["support", "fit"] if presence else []
            post_rows.append({"post_id": pid, "presence": presence, **fields,
                              "judgment_resolved": not unresolved, "unresolved_fields": unresolved,
                              "review_rows": [post1.get(pid), post2.get(pid)]})
        outputs = [*unit["raw"], unit["post"]]
        execution_valid = all(o["disposition"]["execution"] == "valid" for o in outputs)
        terminal_observed = all(o["disposition"]["terminal_observed"] for o in outputs)
        raw_assessment_complete = all(o["evidence"] is not None for o in unit["raw"])
        post_assessment_complete = _post_valid(unit) and unit["post"]["evidence"] is not None
        result["units"].append({"unit_id": original["unit_id"], "opaque_unit_id": uid,
                                "condition": original["condition"], "repetition": original["repetition"],
                                "execution_valid": execution_valid,
                                "raw_execution_valid": all(o["disposition"]["execution"] == "valid" for o in unit["raw"]),
                                "raw_assessment_complete": raw_assessment_complete,
                                "post_assessment_complete": post_assessment_complete,
                                "assessment_complete": raw_assessment_complete and post_assessment_complete,
                                "terminal_status": "valid" if execution_valid else "failed" if terminal_observed else "incomplete",
                                "execution_dispositions": [o["disposition"] for o in outputs],
                                "raw": raw_rows, "post_only": post_rows,
                                "lineage_comments": [unit_rows1[uid]["lineage_comment"], unit_rows2[uid]["lineage_comment"]],
                                "observed_output_words": sum(o.get("observed_output_words", 0) for o in outputs),
                                "output_words": sum(o.get("observed_output_words", 0) for o in outputs) if execution_valid else None})
    result["status"] = "resolved_conservatively"
    result["judgments_locked"] = True
    result["equivalence_review_locked"] = True
    result["unresolved"] = [d for d in comparison["disputes"] if (d["target"], d["field"]) not in overrides] + [
        {"family_cluster": c, "cause": "declared membership/uncertainty disagreement"} for c in clusters]
    return result


def normalize_pairs(kind: str, packet1: dict, review1: dict, packet2: dict,
                    review2: dict, mapping: dict, adjudication: dict | None = None) -> dict:
    result = {"kind": kind, "status": "incomplete", "judgments_locked": False,
              "pairs": [], "unresolved": [], "sources": {"packet_hashes": [packet1.get("packet_sha256"), packet2.get("packet_sha256")],
                                                               "review_hashes": [digest(review1), digest(review2)]}}
    comparison = compare(kind, packet1, review1, packet2, review2)
    if comparison["status"] != "compared":
        result["unresolved"] = [{"coverage_errors": comparison["errors"]}]
        return result
    overrides, adjudication_errors = _adjudicate(kind, comparison, adjudication)
    if adjudication_errors:
        result["unresolved"] = [{"adjudication_errors": adjudication_errors}]
        return result
    if adjudication is not None:
        result["sources"]["adjudication_sha256"] = digest(adjudication)
        result["sources"]["scalar_resolutions"] = list(overrides.values())
    pairs1 = {p["pair_id"]: p for p in review1["pairs"]}
    pairs2 = {p["pair_id"]: p for p in review2["pairs"]}
    for pair in packet1["pairs"]:
        pid = pair["pair_id"]
        if pid not in mapping.get("pairs", {}):
            result["unresolved"] = [{"mapping_error": f"missing pair mapping {pid}"}]
            result["pairs"] = []
            return result
        original = mapping["pairs"][pid]
        arms1 = {a["arm_id"]: a for a in pairs1[pid]["arms"]}
        arms2 = {a["arm_id"]: a for a in pairs2[pid]["arms"]}
        arm_rows = []
        for arm in pair["arms"]:
            aid = arm["arm_id"]
            if aid not in mapping.get("arms", {}):
                result["unresolved"] = [{"mapping_error": f"missing arm mapping {aid}"}]
                result["pairs"] = []
                return result
            fields, unresolved = _agreed(arms1[aid], arms2[aid], P08_SCALARS if kind == "p08" else ("fit",), f"{pid}:{aid}", overrides)
            output = {"arm_id": aid, "method": mapping["arms"][aid]["arm"], **fields,
                      "judgment_resolved": not unresolved, "unresolved_fields": unresolved,
                      "execution_valid": arm["output"]["disposition"]["execution"] == "valid",
                      "terminal_status": arm["output"]["disposition"]["terminal_status"],
                      "assessment_complete": True, "review_reasons": [arms1[aid]["reason"], arms2[aid]["reason"]]}
            if kind == "p09":
                raws1 = {r["source_id"]: r for r in arms1[aid]["raw"]}
                raws2 = {r["source_id"]: r for r in arms2[aid]["raw"]}
                output["raw"] = []
                for rid in pair["raw_ids"]:
                    agreed, disputed = _agreed(raws1[rid], raws2[rid], P09_SCALARS, f"{pid}:{aid}:{rid}", overrides)
                    output["raw"].append({"source_id": rid, **agreed, "judgment_resolved": not disputed,
                                          "unresolved_fields": disputed,
                                          "review_reasons": [raws1[rid]["reason"], raws2[rid]["reason"]]})
                additions1 = {r["post_id"]: r for r in arms1[aid]["unsupported_additions"]}
                additions2 = {r["post_id"]: r for r in arms2[aid]["unsupported_additions"]}
                output["unsupported_additions"] = []
                for post_id in sorted(set(additions1) | set(additions2)):
                    agreed_presence = post_id in additions1 and post_id in additions2
                    resolution = overrides.get((f"{pid}:{aid}:post:{post_id}", "presence"))
                    output["unsupported_additions"].append({
                        "post_id": post_id, "presence": True if agreed_presence else resolution["value"] if resolution else None,
                        "judgment_resolved": agreed_presence or resolution is not None,
                        "review_rows": [additions1.get(post_id), additions2.get(post_id)]})
                output["judgment_resolved"] = (output["judgment_resolved"] and
                                               all(r["judgment_resolved"] for r in output["raw"]) and
                                               all(r["judgment_resolved"] for r in output["unsupported_additions"]))
            arm_rows.append(output)
        result["pairs"].append({"pair_id": original["pair_id"], "opaque_pair_id": pid,
                                "case_id": original["case_id"], "arms": arm_rows,
                                "stratum": original.get("stratum") if kind == "p09" else None,
                                "contrast_reviews": [pairs1[pid]["contrast"], pairs2[pid]["contrast"]]})
    result["status"], result["judgments_locked"] = "resolved_conservatively", True
    result["unresolved"] = [d for d in comparison["disputes"] if (d["target"], d["field"]) not in overrides]
    return result


def resolve(kind: str, case_id: str | None = None, root: Path = ROOT) -> dict:
    stem = f"main-{case_id}" if kind == "main" else kind
    paths = {"packet1": root / "blinded" / f"{stem}-J1.json",
             "packet2": root / "blinded" / f"{stem}-J2.json",
             "review1": root / "reviews" / f"{stem}-J1.json",
             "review2": root / "reviews" / f"{stem}-J2.json",
             "mapping": root / "blinded" / f"{stem}-mapping.json"}
    contents, failures = {}, {}
    for key, path in paths.items():
        try:
            contents[key] = read_json(path)
        except (OSError, ValueError) as error:
            failures[key] = type(error).__name__
    report_path = root / "reports" / f"{stem}-resolved.json"
    if failures:
        result = {"status": "incomplete", "judgments_locked": False, "unresolved": [{"input_errors": failures}],
                  "sources": {}, "families": [], "units": [], "equivalence_review_locked": False,
                  "case_id": case_id} if kind == "main" else {
                      "kind": kind, "status": "incomplete", "judgments_locked": False,
                      "pairs": [], "unresolved": [{"input_errors": failures}], "sources": {}}
    else:
        adjudication_path = root / "reviews" / f"{stem}-adjudication.json"
        try:
            adjudication = read_json(adjudication_path) if adjudication_path.exists() else None
        except (OSError, ValueError):
            adjudication = {"invalid_input": True}
        if kind == "main":
            result = normalize_main(contents["packet1"], contents["review1"], contents["packet2"], contents["review2"], contents["mapping"], adjudication)
        else:
            result = normalize_pairs(kind, contents["packet1"], contents["review1"], contents["packet2"], contents["review2"], contents["mapping"], adjudication)
    write_json(report_path, result)
    # Evaluation logs are separate from native completion events.
    with (root / "reports" / "evaluation-events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"operation": "resolve", "kind": kind, "case_id": case_id,
                                 "report_sha256": digest(result), "sources": result["sources"],
                                 "status": result["status"]}, ensure_ascii=False) + "\n")
    return result


def cli() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    sub = parser.add_subparsers(dest="operation", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("kind", choices=("main", "p08", "p09"))
    prep.add_argument("case", nargs="?")
    checker = sub.add_parser("check")
    checker.add_argument("kind", choices=("main", "p08", "p09"))
    checker.add_argument("packet", type=Path)
    checker.add_argument("review", type=Path)
    resolver = sub.add_parser("resolve")
    resolver.add_argument("kind", choices=("main", "p08", "p09"))
    resolver.add_argument("case", nargs="?")
    args = parser.parse_args()
    try:
        if args.operation == "prepare":
            print(json.dumps({"packets": [str(p) for p in prepare(args.kind, args.case, args.root)]}))
            return 0
        if args.operation == "check":
            packet, review = read_json(args.packet), read_json(args.review)
            errors = check(args.kind, packet, review)
            args.root.joinpath("reports").mkdir(parents=True, exist_ok=True)
            with (args.root / "reports" / "evaluation-events.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"operation": "check", "kind": args.kind,
                                         "packet_sha256": packet.get("packet_sha256") if isinstance(packet, dict) else None,
                                         "review_sha256": digest(review), "errors": errors}) + "\n")
            print(json.dumps({"valid": not errors, "errors": errors}))
            return int(bool(errors))
        if args.kind == "main" and not args.case:
            raise ValueError("resolve main requires CASE")
        result = resolve(args.kind, args.case, args.root)
        print(json.dumps({"status": result["status"], "unresolved": result["unresolved"]}))
        return int(result["status"] == "incomplete")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"status": "incomplete", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(cli())
