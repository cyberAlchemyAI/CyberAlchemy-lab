"""Exact successor review binding with zero new credit for carried raw grades."""
from pathlib import Path
import argparse
import copy
import hashlib
import json

import blind_generation_raw_first as packets
import generation_review_validation_v2 as base


def validate_carried(packet, raw_packet, raw_lock):
    errors = []
    try:
        if packet.get("phase") != "post" or raw_packet is None or raw_lock is None:
            raise ValueError("post validation requires original raw packet and raw lock")
        rows = packets.locked_rows(raw_packet, raw_lock)
        meta = packet.get("raw_first", {})
        bindings = {"raw_packet_id": raw_packet["packet_id"],
                    "raw_packet_context_sha256": packets.raw_context_hash(raw_packet),
                    "raw_packet_sha256": packets.canonical_hash(raw_packet),
                    "raw_lock_sha256": packets.canonical_hash(raw_lock),
                    "raw_lock_source_bindings_sha256": packets.canonical_hash(raw_lock["source_bindings"]),
                    "independent_raw_review_complete": raw_lock["independent_review_complete"],
                    "raw_lock_meaning_status": raw_lock["meaning_status"],
                    "carried_independent_grade_credit": 0, "carried_rows": rows}
        for key, value in bindings.items():
            if type(meta.get(key)) is not type(value) or packets.canonical_hash(meta.get(key)) != packets.canonical_hash(value):
                errors.append("exact raw carry binding: " + key)
        if packets.raw_context_hash(packet) != packets.raw_context_hash(raw_packet):
            errors.append("post raw assessed object/case/archive/rubric/contract/matrix drift")
        locked = {(row["table"], row["row_id"]): row for row in rows}
        originals = {(table, row["row_id"]): row for table, obligations in raw_packet["expected_matrix"].items() for row in obligations}
        seen = set()
        sources = packets._source_ids(packet)
        for table, obligations in packet["expected_matrix"].items():
            for ob in obligations:
                if not packets.is_carried(table, ob, sources):
                    if "assessment_origin" in ob or "independent_grade_credit" in ob:
                        errors.append("fresh row cannot declare carried assessment origin")
                    continue
                key = (table, ob["row_id"])
                if key in seen or key not in locked:
                    errors.append("unexpected/duplicate carried row")
                    continue
                seen.add(key)
                row, original = locked[key], originals[key]
                fixed = {k: v for k, v in row["values"].items() if k not in ob["identity"] and k != "evidence"}
                if (ob["identity"] != row["identity"] or ob["null_semantics"] != original["null_semantics"] or
                    packets.canonical_hash(ob["fixed_values"]) != packets.canonical_hash(fixed) or ob.get("assessment_origin") != "locked_raw" or
                    type(ob.get("independent_grade_credit")) is not int or ob["independent_grade_credit"] != 0):
                    errors.append("exact carried obligation/fixed value binding")
        if seen != set(locked):
            errors.append("missing/extra carried row")
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        errors.append("invalid raw carry binding: " + str(exc))
    return {"valid": not errors, "errors": errors, "carried_independent_grade_credit": 0}


def validate_review(packet, review, raw_packet=None, raw_lock=None):
    errors = []
    try:
        if not isinstance(packet, dict) or not isinstance(review, dict):
            raise ValueError("packet/review objects required")
        phase = packet.get("phase")
        if packet.get("version") != packets.VERSION or phase not in {"raw", "post"}:
            raise ValueError("explicit successor raw/post phase required")
        meta = packet.get("raw_first", {})
        if (meta.get("phase") != phase or meta.get("raw_packet_context_sha256") != packets.raw_context_hash(packet) or
            type(meta.get("carried_independent_grade_credit")) is not int or meta["carried_independent_grade_credit"] != 0):
            errors.append("exact phase/context/zero carried credit required")
        if review.get("reviewer_id") not in packet.get("review_job_ids", []):
            errors.append("assigned phase-specific opaque reviewer ID required")
        fresh_packet, fresh_review = copy.deepcopy(packet), copy.deepcopy(review)
        carried_keys = set()
        if phase == "raw":
            if any(u["content_kind"] != "source" for u in packet["units"]) or any(packet["expected_matrix"][table] for table in ("post_rows", "retention_rows", "addition_rows")):
                errors.append("raw packet must exclude all summary objects and assessments")
            if meta.get("carried_rows") != []:
                errors.append("raw phase cannot carry previous grades")
        else:
            result = validate_carried(packet, raw_packet, raw_lock)
            errors.extend(result["errors"])
            if not result["valid"]:
                return {"valid": False, "errors": errors, "semantic_validity": "not asserted",
                        "carried_independent_grade_credit": 0}
            carried = meta["carried_rows"]
            carried_keys = {(row["table"], row["row_id"]) for row in carried}
            # Equality of the complete row, including evidence, is checked before
            # removing carried rows from fresh v2 validation. This handles locked
            # true/false no-opening reasons and unresolved nulls without opening
            # the frozen validator's permissive arbitrary-fixed-value path.
            for table, columns in packet["contract"]["columns"].items():
                obligations = packet["expected_matrix"][table]
                locked = {tuple(row["identity"][k] for k in base.IDENTITIES[table]): row
                          for row in carried if row["table"] == table}
                found, remaining = set(), []
                for values in review.get(table, []):
                    if not isinstance(values, list) or len(values) != len(columns):
                        errors.append(table + ": exact row width/array required")
                        continue
                    data = dict(zip(columns, values))
                    identity = tuple(data[k] for k in base.IDENTITIES[table])
                    if identity in locked:
                        if identity in found or packets.canonical_hash(data) != packets.canonical_hash(locked[identity]["values"]) or any(
                            type(data[k]) is not type(locked[identity]["values"][k]) for k in columns):
                            errors.append(table + ": exact carried value/evidence equality required")
                        found.add(identity)
                    else:
                        remaining.append(values)
                if found != set(locked):
                    errors.append(table + ": exact carried review coverage required")
                fresh_review[table] = remaining
                fresh_packet["expected_matrix"][table] = [ob for ob in obligations
                    if (table, ob["row_id"]) not in carried_keys]
        for table, obligations in fresh_packet["expected_matrix"].items():
            for ob in obligations:
                if ob["fixed_values"] != packets.native_fixed_values(fresh_packet, table, ob):
                    errors.append(table + ": arbitrary fresh fixed fields forbidden")
        fresh_packet["matrix_counts"] = {table: len(rows) for table, rows in fresh_packet["expected_matrix"].items()}
        fresh_packet["expected_total_rows"] = sum(fresh_packet["matrix_counts"].values())
        # Validate original counts/columns as well: truncating obligations for the
        # fresh pass must not conceal a malformed full packet or review shape.
        if packet.get("matrix_counts") != {t: len(r) for t, r in packet["expected_matrix"].items()} or packet.get("expected_total_rows") != sum(len(r) for r in packet["expected_matrix"].values()):
            errors.append("full packet exact matrix counts required")
        result = base.validate_review(fresh_packet, fresh_review)
        errors.extend(result["errors"])
        return {"valid": not errors, "errors": errors, "phase": phase,
                "row_counts": {t: len(review.get(t, [])) for t in base.IDENTITIES},
                "expected_rows": packet["expected_total_rows"], "carried_rows": len(carried_keys),
                "fresh_rows": fresh_packet["expected_total_rows"], "carried_independent_grade_credit": 0,
                "semantic_validity": "not asserted; carried values are bound copies, fresh evidence adequacy and independence require native review"}
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        return {"valid": False, "errors": errors + ["invalid packet/review: " + str(exc)],
                "semantic_validity": "not asserted", "carried_independent_grade_credit": 0}


def validate_paths(packet_path, review_path, raw_packet_path=None, raw_lock_path=None):
    try:
        packet, review = base.read_json(packet_path), base.read_json(review_path)
        raw_packet = base.read_json(raw_packet_path) if raw_packet_path is not None else None
        raw_lock = base.read_json(raw_lock_path) if raw_lock_path is not None else None
    except (OSError, ValueError, UnicodeError) as exc:
        return {"valid": False, "errors": ["unreadable/invalid/duplicate-key JSON: " + str(exc)], "semantic_validity": "not asserted"}
    result = validate_review(packet, review, raw_packet, raw_lock)
    result["review_sha256"] = hashlib.sha256(Path(review_path).read_bytes()).hexdigest()
    result["saved_words"] = len(Path(review_path).read_text().split())
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("review", type=Path)
    parser.add_argument("--raw-packet", type=Path)
    parser.add_argument("--raw-lock", type=Path)
    args = parser.parse_args()
    result = validate_paths(args.packet, args.review, args.raw_packet, args.raw_lock)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["valid"] else 1)
