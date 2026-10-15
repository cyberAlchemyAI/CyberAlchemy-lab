"""Exact packet-bound review coverage/types, never semantic verification."""
from pathlib import Path
import argparse
import hashlib
import json

IDENTITIES = {
    "raw_rows": ["card_id"], "archive_pairs": ["card_id", "archive_id"],
    "candidate_pairs": ["card_a", "card_b"], "post_rows": ["card_id"],
    "retention_rows": ["source_card_id"], "lineage_rows": ["unit_id", "source_id"],
    "addition_rows": ["card_id"], "attack_rows": ["unit_id", "attack_id"],
    "contradiction_rows": ["unit_id", "pair_id"], "unit_rows": ["unit_id"],
}
EXACT_COLUMNS = {
    "raw_rows": ["card_id", "intelligible", "usefulness", "observability", "fit", "support", "novelty", "contract", "family_confirmed", "evidence"],
    "archive_pairs": ["card_id", "archive_id", "relation", "evidence"],
    "candidate_pairs": ["card_a", "card_b", "relation", "evidence"],
    "post_rows": ["card_id", "source_ids", "fit_preserved", "new_assertion", "evidence"],
    "retention_rows": ["source_card_id", "relation", "discriminator", "uncertainty", "lineage_consistent", "fit_preserved", "complete_protected_fields", "evidence"],
    "lineage_rows": ["unit_id", "source_id", "disposition", "targets_valid", "meaning_consistent", "evidence"],
    "addition_rows": ["card_id", "fit", "support", "evidence"],
    "attack_rows": ["unit_id", "attack_id", "construction_link_met", "evidence"],
    "contradiction_rows": ["unit_id", "pair_id", "incompatible_decision_commitments", "evidence"],
    "unit_rows": ["unit_id", "execution", "no_opening_reason_supported", "contract", "evidence"],
}
BOOLS = {"intelligible", "family_confirmed", "fit_preserved", "new_assertion",
         "lineage_consistent", "complete_protected_fields", "targets_valid",
         "meaning_consistent", "construction_link_met", "incompatible_decision_commitments",
         "no_opening_reason_supported"}
ENUMS = {
    "fit": ["preserves", "uncertain", "conditional", "violates"],
    "support": ["stipulated", "inference", "speculative", "unsupported"],
    "novelty": ["new", "equivalent", "parameter", "uncertain"],
    "contract": ["met", "partial", "not_met", "inapplicable"],
    "execution": ["valid", "invalid", "missing", "skipped"],
    "disposition": ["retained", "changed", "merged", "parked", "rejected"],
    "discriminator": ["retained", "lost", "uncertain", "unobservable"],
    "uncertainty": ["retained", "lost", "uncertain", "unobservable"],
}


def read_json(path):
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("duplicate JSON object key: " + key)
            obj[key] = value
        return obj
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)


def validate_review(packet, review):
    errors = []

    def need(ok, message):
        if not ok:
            errors.append(message)

    if not isinstance(packet, dict) or not isinstance(review, dict):
        return {"valid": False, "errors": ["packet/review must be objects"], "semantic_validity": "not asserted"}
    parent_contract = packet.get("contract", {})
    columns = parent_contract.get("columns", {}) if isinstance(parent_contract, dict) else {}
    expected = packet.get("expected_matrix", {})
    if not isinstance(columns, dict) or not isinstance(expected, dict):
        return {"valid": False, "errors": ["packet columns/matrix must be objects"], "semantic_validity": "not asserted"}
    need(columns == EXACT_COLUMNS, "packet columns differ from frozen v2 contract")
    need(set(columns) == set(IDENTITIES), "packet column tables differ from declared v2 tables")
    need(set(expected) == set(IDENTITIES), "packet expected table coverage")
    counts_expected = {k: len(v) for k, v in expected.items() if isinstance(v, list)}
    need(packet.get("matrix_counts") == counts_expected, "packet matrix counts equality")
    need(packet.get("expected_total_rows") == sum(counts_expected.values()), "packet total rows equality")
    need(review.get("columns") == columns, "exact columns equality required")
    need(isinstance(review.get("reviewer_id"), str) and bool(review.get("reviewer_id", "").strip()), "reviewer_id nonempty string")
    need(isinstance(review.get("limits"), str) and bool(review.get("limits", "").strip()), "limits nonempty string")
    need(set(review) == {"reviewer_id", "columns", "limits", *IDENTITIES}, "exact review top-level fields")
    counts = {}
    for table, keys in IDENTITIES.items():
        cols = columns.get(table)
        obligations = expected.get(table)
        if not isinstance(cols, list) or not all(isinstance(c, str) for c in cols) or len(cols) != len(set(cols)) or not all(k in cols for k in keys):
            need(False, table + ": malformed packet columns")
            continue
        if not isinstance(obligations, list):
            need(False, table + ": expected rows must be a list")
            continue
        bindings = {}
        for obligation in obligations:
            if not isinstance(obligation, dict) or not isinstance(obligation.get("identity"), dict):
                need(False, table + ": malformed expected row")
                continue
            identity = obligation["identity"]
            if set(identity) != set(keys) or not all(isinstance(identity[k], str) and identity[k] for k in keys):
                need(False, table + ": exact expected identity columns/types")
                continue
            identity_key = tuple(identity[k] for k in keys)
            need(identity_key not in bindings, table + ": duplicate expected identity")
            bindings[identity_key] = obligation
            need(type(obligation.get("null_semantics")) is bool, table + ": expected null_semantics bool")
            need(isinstance(obligation.get("fixed_values"), dict), table + ": fixed_values object")
            if isinstance(obligation.get("fixed_values"), dict):
                need(set(obligation["fixed_values"]) <= set(cols) - set(keys) - {"evidence"}, table + ": fixed columns must belong to declared nonidentity fields")
        values = review.get(table)
        if not isinstance(values, list):
            need(False, table + ": review rows must be list")
            continue
        counts[table] = len(values)
        seen = set()
        for index, row in enumerate(values):
            label = table + "[" + str(index) + "]"
            if not isinstance(row, list) or len(row) != len(cols):
                need(False, label + ": exact row width/array required")
                continue
            data = dict(zip(cols, row))
            if not all(isinstance(data[k], str) and data[k] for k in keys):
                need(False, label + ": identity string required")
                continue
            identity = tuple(data[k] for k in keys)
            need(identity not in seen, label + ": duplicate identity")
            seen.add(identity)
            obligation = bindings.get(identity)
            if obligation is None:
                need(False, label + ": unexpected row identity")
                continue
            fixed = obligation.get("fixed_values", {})
            fixed = fixed if isinstance(fixed, dict) else {}
            for key, value in data.items():
                if key in keys:
                    continue
                if key == "evidence":
                    need(isinstance(value, str) and bool(value.strip()), label + ": nonempty evidence string required")
                    continue
                if key in fixed:
                    need(type(value) is type(fixed[key]) and value == fixed[key], label + ": fixed binding " + key)
                    if key == "source_ids":
                        need(isinstance(value, list) and all(isinstance(x, str) and x for x in value) and len(value) == len(set(value)), label + ": source_ids unique string list")
                    elif key == "execution":
                        need(isinstance(value, str) and value in ENUMS[key], label + ": fixed execution enum")
                    elif key == "disposition":
                        need(isinstance(value, str) and value in ENUMS[key], label + ": fixed disposition enum")
                    elif key == "no_opening_reason_supported":
                        need(value is None, label + ": nonempty unit no-opening field inapplicable")
                    continue
                if obligation.get("null_semantics"):
                    need(value is None, label + ": unavailable semantic field must be null: " + key)
                    continue
                if key in BOOLS:
                    need(type(value) is bool, label + ": boolean required: " + key)
                elif key in ("usefulness", "observability"):
                    need(type(value) is int and value in [0, 1, 2], label + ": grade integer 0/1/2 required: " + key)
                elif key == "relation":
                    enums = ["retained", "lost", "uncertain", "unobservable"] if table == "retention_rows" else ["equivalent", "parameter", "distinct", "uncertain"]
                    need(isinstance(value, str) and value in enums, label + ": relation enum")
                elif key in ENUMS:
                    need(isinstance(value, str) and value in ENUMS[key], label + ": enum " + key)
                elif key == "source_ids":
                    need(isinstance(value, list) and all(isinstance(x, str) and x for x in value) and len(value) == len(set(value)), label + ": source_ids unique string list")
                else:
                    need(False, label + ": unrecognized declared column " + key)
        need(seen == set(bindings), table + ": exact expected row coverage; missing=" + str(len(set(bindings) - seen)) + ", extra=" + str(len(seen - set(bindings))))
    return {"valid": not errors, "errors": errors, "row_counts": counts,
            "expected_rows": sum(len(x) for x in expected.values() if isinstance(x, list)),
            "semantic_validity": "not asserted; field/reference support and causal judgments require independent native review"}


def validate_paths(packet_path, review_path):
    try:
        packet = read_json(packet_path)
        review = read_json(review_path)
    except (OSError, ValueError, UnicodeError) as exc:
        return {"valid": False, "errors": ["unreadable/invalid/duplicate-key JSON: " + str(exc)], "semantic_validity": "not asserted"}
    result = validate_review(packet, review)
    result["review_sha256"] = hashlib.sha256(Path(review_path).read_bytes()).hexdigest()
    result["saved_words"] = len(Path(review_path).read_text().split())
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("review", type=Path)
    args = parser.parse_args()
    result = validate_paths(args.packet, args.review)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["valid"] else 1)
