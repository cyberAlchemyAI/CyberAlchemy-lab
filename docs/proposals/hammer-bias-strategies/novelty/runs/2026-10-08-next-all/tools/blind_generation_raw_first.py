"""Prospective raw-first packet assembly from caller-supplied unscored or scored bodies.

Imports do not read scheduled artifacts. The original v2 builder supplies source
IDs, causal instructions and matrix identities; this adapter changes review timing.
Native terminal witnessing, admission and first-save publication belong to runtime.
"""
from pathlib import Path
import copy
import hashlib
import json

import blind_generation_v2 as base
import generation_review_validation_v2 as validation

ROOT = Path(__file__).resolve().parents[1]
VERSION = "generation-blind-raw-first-v1"
CARRIED_TABLES = {"raw_rows", "archive_pairs", "candidate_pairs", "attack_rows", "contradiction_rows"}
FAMILY_FIELDS = {("archive_pairs", "relation"), ("candidate_pairs", "relation"),
                 ("raw_rows", "novelty"), ("raw_rows", "family_confirmed")}
STATUSES = {"agreed", "adjudicated", "family_unresolved", "scalar_unresolved", "unobservable"}


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def load_inputs(root=ROOT):
    root = Path(root)
    schedule, _, contract, criteria, archives = base.load_inputs(root)
    reviews = base.read(root / "generation-review-schedule.raw-first.json")
    return schedule, reviews, contract, criteria, archives


def _phase_jobs(study, case, reviews, phase):
    prefix = "RF-" + ("R" if phase == "raw" else "P") + "-" + study + "-" + case + "-"
    expected = {prefix + "1", prefix + "2"}
    jobs = [j for j in reviews["jobs"] if j.get("study_id") == study and
            j.get("case_id") == case and str(j.get("job_id", "")).startswith(prefix)]
    if len(jobs) != 2 or {j["job_id"] for j in jobs} != expected:
        raise ValueError("exact two scheduled phase-specific RF review jobs required")
    return jobs


def _source_ids(packet):
    return {u["unit_id"] for u in packet["units"] if u["content_kind"] == "source"}


def is_carried(table, obligation, source_ids):
    return table in CARRIED_TABLES or (table in {"lineage_rows", "unit_rows"} and
                                      obligation["identity"].get("unit_id") in source_ids)


def native_fixed_values(packet, table, obligation):
    """The only frozen-v2 fixed fields, derived again from assessed objects."""
    identity = obligation["identity"]
    units = {u["unit_id"]: u for u in packet["units"]}
    if table == "unit_rows":
        unit = units[identity["unit_id"]]
        return {"execution": unit["execution"], **({"no_opening_reason_supported": None}
            if unit["execution"] == "valid" and unit["artifact"].get("openings") else {})}
    if table == "lineage_rows" and not obligation["null_semantics"]:
        lineage = units[identity["unit_id"]]["artifact"].get("lineage", [])
        lineage = lineage if isinstance(lineage, list) else []
        by_source = {row.get("source_id"): row for row in lineage if isinstance(row, dict)
                     and isinstance(row.get("source_id"), str)}
        return {"disposition": by_source.get(identity["source_id"], {}).get("disposition")}
    if table == "post_rows":
        cards = [row for u in packet["units"] if u["content_kind"] == "summary"
                 for row in (u["artifact"].get("openings", [])
                             if isinstance(u["artifact"].get("openings"), list) else [])
                 if isinstance(row, dict) and row.get("id") == identity["card_id"]]
        if len(cards) != 1:
            raise ValueError("exact assessed post card required")
        sources = cards[0].get("source_ids", [])
        return {"source_ids": sources if isinstance(sources, list) else []}
    return {}


def raw_context(packet):
    """All assessed raw objects and obligations, without phase/reviewer labels.

    Reconstructing native fixed fields lets post context be compared to pre-D
    context without treating carried grades as newly assessed objects.
    """
    units = [copy.deepcopy(u) for u in packet["units"] if u["content_kind"] == "source"]
    sources = {u["unit_id"] for u in units}
    refs = {u[k] for u in units for k in ("semantic_contract_ref", "common_contract_ref") if u.get(k)}
    expected = {table: [{"row_id": row["row_id"], "identity": copy.deepcopy(row["identity"]),
                        "null_semantics": row["null_semantics"],
                        "fixed_values": native_fixed_values(packet, table, row)}
                       for row in rows if is_carried(table, row, sources)]
                for table, rows in packet["expected_matrix"].items()}
    return {"case": packet["case"], "archive": packet["archive"],
            "contract": packet["contract"], "criteria": packet["criteria"],
            "semantic_contracts": {ref: packet["semantic_contracts"][ref] for ref in sorted(refs)},
            "units": units, "expected_matrix": expected}


def raw_context_hash(packet):
    return canonical_hash(raw_context(packet))


def _typed(table, field, value):
    if field in validation.BOOLS:
        return type(value) is bool
    if field in {"usefulness", "observability"}:
        return type(value) is int and value in {0, 1, 2}
    if field == "relation":
        return isinstance(value, str) and value in (["retained", "lost", "uncertain", "unobservable"]
            if table == "retention_rows" else ["equivalent", "parameter", "distinct", "uncertain"])
    if field in validation.ENUMS:
        return isinstance(value, str) and value in validation.ENUMS[field]
    if field == "source_ids":
        return isinstance(value, list) and all(isinstance(x, str) and x for x in value) and len(value) == len(set(value))
    return False


def locked_rows(raw_packet, raw_lock):
    """Verify a complete source-bound lock, retaining unresolved and gated nulls.

    This validates structure and binding, never judges evidence or claims that a
    caller's lock was produced by independent native terminals.
    """
    if raw_packet.get("version") != VERSION or raw_packet.get("phase") != "raw":
        raise ValueError("raw-phase successor packet required")
    if (raw_packet.get("contract", {}).get("columns") != validation.EXACT_COLUMNS or
        set(raw_packet.get("expected_matrix", {})) != set(base.TABLES) or
        any(u["content_kind"] != "source" for u in raw_packet["units"]) or
        any(raw_packet["expected_matrix"][t] for t in ("post_rows", "retention_rows", "addition_rows"))):
        raise ValueError("exact raw-only frozen table/column contract required")
    if raw_packet.get("raw_first", {}).get("raw_packet_context_sha256") != raw_context_hash(raw_packet):
        raise ValueError("raw assessed-object context hash drift")
    if not isinstance(raw_lock, dict) or raw_lock.get("case_packet_id") != raw_packet["packet_id"]:
        raise ValueError("lock must name exact raw packet")
    complete = raw_lock.get("independent_review_complete")
    if type(complete) is not bool:
        raise ValueError("explicit independent review completeness required")
    meaning = "locked_source_bound_model_judgments" if complete else "gated_incomplete_review"
    if raw_lock.get("meaning_status") != meaning:
        raise ValueError("lock meaning/completeness mismatch")
    bindings = raw_lock.get("source_bindings")
    if not isinstance(bindings, list) or not bindings or any(not isinstance(x, dict) or
        not isinstance(x.get("path"), str) or not x["path"] or not isinstance(x.get("sha256"), str) or
        len(x["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in x["sha256"]) for x in bindings):
        raise ValueError("lock source hash bindings required")
    packet_hash = canonical_hash(raw_packet)
    if "raw_packet_sha256" in raw_lock:
        if raw_lock["raw_packet_sha256"] != packet_hash:
            raise ValueError("raw packet lock hash drift")
    else:
        conventional = {hashlib.sha256((json.dumps(raw_packet, indent=2, ensure_ascii=ascii_mode) + "\n").encode()).hexdigest()
                        for ascii_mode in (True, False)}
        if not any(x["sha256"] in conventional for x in bindings):
            raise ValueError("lock lacks exact raw packet source binding")
    if "raw_packet_context_sha256" in raw_lock and raw_lock["raw_packet_context_sha256"] != raw_context_hash(raw_packet):
        raise ValueError("raw context lock hash drift")
    rows = raw_lock.get("rows")
    if not isinstance(rows, list):
        raise ValueError("locked rows list required")
    by_key = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"table", "row_id", "identity", "values", "field_status"}:
            raise ValueError("exact locked row shape required")
        key = (row["table"], row["row_id"])
        if key in by_key:
            raise ValueError("duplicate locked row")
        by_key[key] = row
    expected_keys, result = set(), []
    for table, obligations in raw_packet["expected_matrix"].items():
        for ob in obligations:
            key = (table, ob["row_id"])
            expected_keys.add(key)
            if key not in by_key:
                raise ValueError("missing locked raw row: " + table)
            row = by_key[key]
            columns = raw_packet["contract"]["columns"][table]
            values, statuses = row["values"], row["field_status"]
            fixed = native_fixed_values(raw_packet, table, ob)
            if ob["fixed_values"] != fixed or row["identity"] != ob["identity"]:
                raise ValueError("locked identity/native fixed field drift")
            if not isinstance(values, dict) or set(values) != set(columns):
                raise ValueError("exact locked value columns required")
            semantic = set(columns) - set(ob["identity"]) - set(fixed) - {"evidence"}
            if not isinstance(statuses, dict) or set(statuses) != semantic or any(s not in STATUSES for s in statuses.values()):
                raise ValueError("exact locked semantic field statuses required")
            if not isinstance(values["evidence"], str) or not values["evidence"].strip():
                raise ValueError("locked evidence required")
            for field, value in values.items():
                if field in ob["identity"] or field in fixed:
                    wanted = ob["identity"].get(field, fixed.get(field))
                    if type(value) is not type(wanted) or value != wanted:
                        raise ValueError("locked identity/fixed value mismatch")
                    if field in fixed and value is not None and not _typed(table, field, value):
                        raise ValueError("locked fixed value type")
                    continue
                if field == "evidence":
                    continue
                status = statuses[field]
                unresolved = status in {"family_unresolved", "scalar_unresolved", "unobservable"}
                if status == "family_unresolved" and (table, field) not in FAMILY_FIELDS:
                    raise ValueError("family status outside family field")
                if status == "scalar_unresolved" and (table, field) in FAMILY_FIELDS:
                    raise ValueError("family dispute cannot become scalar")
                if not complete and (status != "unobservable" or value is not None):
                    raise ValueError("incomplete raw review requires unobservable null judgments")
                if unresolved or ob["null_semantics"]:
                    if value is not None:
                        raise ValueError("unresolved/unavailable locked value must remain null")
                elif not _typed(table, field, value):
                    raise ValueError("typed resolved locked value required")
            result.append(copy.deepcopy(row))
    if set(by_key) != expected_keys:
        raise ValueError("extra locked raw row")
    return result


def _decorate(packet, admin, study, case, phase, inputs):
    jobs = _phase_jobs(study, case, inputs[1], phase)
    packet["version"] = VERSION
    packet["phase"] = phase
    packet["packet_id"] = base.opaque("J", "raw-first|" + phase + "|" + study + "|" + case)
    packet["review_job_ids"] = sorted(base.opaque("V", j["job_id"]) for j in jobs)
    admin.update(version="generation-method-mapping-raw-first-v1", phase=phase,
                 packet_id=packet["packet_id"], review_job_bindings=[
                     {"opaque_job_id": base.opaque("V", j["job_id"]), "job_id": j["job_id"]} for j in jobs],
                 input_payload_bindings=[{"input": label, "sha256": canonical_hash(value)}
                     for label, value in zip(("schedule", "reviews", "contract", "criteria", "archives"), inputs)])
    packet["raw_first"] = {"phase": phase, "raw_packet_context_sha256": raw_context_hash(packet),
                           "carried_rows": [], "carried_independent_grade_credit": 0}
    if phase == "raw":
        packet["review_shape"]["scope"] = "Fresh raw source, archive, pair, attack, contradiction and source-lineage/unit assessments before any summary. Structural validation does not prove semantic correctness or native independence."
    else:
        packet["review_shape"]["scope"] = "Fresh post, retention, additions and summary lineage/unit assessments only. Copy every carried value and evidence exactly; carried fields earn zero new independent grade credit."
    return packet, admin


def build_raw(study, case, artifacts, dispositions, root=ROOT, inputs=None):
    """Build a raw-only packet; no compression artifact/disposition is accepted."""
    inputs = inputs or load_inputs(root)
    schedule = copy.deepcopy(inputs[0])
    schedule["jobs"] = [j for j in schedule["jobs"] if j["role"] != "compression"]
    selected_ids = {j["job_id"] for j in schedule["jobs"] if j["study_id"] == study and j["case_id"] == case}
    if set(dispositions) != selected_ids or not set(artifacts) <= selected_ids:
        raise ValueError("raw phase requires exact non-compression dispositions and only source artifacts")
    packet, admin = base.build_packet(study, case, artifacts, dispositions, root, (schedule, *inputs[1:]))
    return _decorate(packet, admin, study, case, "raw", inputs)


def build_post(study, case, artifacts, dispositions, raw_packet, raw_lock, root=ROOT, inputs=None):
    """Build post context with every actual locked raw field/evidence carried exactly."""
    inputs = inputs or load_inputs(root)
    source_ids = {j["job_id"] for j in inputs[0]["jobs"] if j["study_id"] == study and
                  j["case_id"] == case and j["role"] != "compression"}
    rebuilt, _ = build_raw(study, case, {k: v for k, v in artifacts.items() if k in source_ids},
                          {k: v for k, v in dispositions.items() if k in source_ids}, root, inputs)
    if canonical_hash(rebuilt) != canonical_hash(raw_packet):
        raise ValueError("actual raw packet/object/instruction/context drift")
    carried = locked_rows(raw_packet, raw_lock)
    packet, admin = base.build_packet(study, case, artifacts, dispositions, root, inputs)
    if raw_context_hash(packet) != raw_context_hash(raw_packet):
        raise ValueError("post raw assessed objects, contracts, case/archive/rubric or matrix drift")
    packet, admin = _decorate(packet, admin, study, case, "post", inputs)
    by_key = {(row["table"], row["row_id"]): row for row in carried}
    seen = set()
    sources = _source_ids(packet)
    for table, obligations in packet["expected_matrix"].items():
        for ob in obligations:
            if not is_carried(table, ob, sources):
                continue
            key = (table, ob["row_id"])
            if key not in by_key or ob["identity"] != by_key[key]["identity"]:
                raise ValueError("post carried row coverage/identity drift")
            row = by_key[key]
            ob["fixed_values"] = {field: copy.deepcopy(value) for field, value in row["values"].items()
                                  if field not in ob["identity"] and field != "evidence"}
            ob.update(assessment_origin="locked_raw", independent_grade_credit=0)
            seen.add(key)
    if seen != set(by_key):
        raise ValueError("missing/extra post carried row")
    packet["raw_first"].update(raw_packet_id=raw_packet["packet_id"],
        raw_packet_sha256=canonical_hash(raw_packet), raw_lock_sha256=canonical_hash(raw_lock),
        raw_lock_source_bindings_sha256=canonical_hash(raw_lock["source_bindings"]),
        independent_raw_review_complete=raw_lock["independent_review_complete"],
        raw_lock_meaning_status=raw_lock["meaning_status"], carried_rows=carried)
    admin.update(raw_packet_sha256=canonical_hash(raw_packet), raw_lock_sha256=canonical_hash(raw_lock),
                 raw_packet_context_sha256=raw_context_hash(raw_packet),
                 raw_lock_source_bindings=copy.deepcopy(raw_lock["source_bindings"]))
    return packet, admin
