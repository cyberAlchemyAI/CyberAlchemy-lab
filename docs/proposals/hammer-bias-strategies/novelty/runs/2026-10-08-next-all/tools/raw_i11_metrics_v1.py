"""Unscored arithmetic over locked I11 judgments; no semantic regrading.

Per-unit bounds have at most two cards. First appearance uses every direct
prior-card relation, without transitive family closure. Missing factorial
corners remain null. Independent completion audit is still required.
"""
from fractions import Fraction
import composition_i11_runtime_v3 as i
import generation_raw_first_runtime as f
import raw_first_case_metrics as m

FACTORS = ("inversion", "attack", "conversion")
CELLS = tuple(f"{n:03b}" for n in range(8))


def interval_contrast(cells, changed):
    """Average finite difference across backgrounds of unchanged factors."""
    changed = tuple(changed)
    if not changed or len(set(changed)) != len(changed) or any(x not in range(3) for x in changed):
        raise ValueError("one to three distinct factorial coordinates")
    missing = [key for key in CELLS if cells.get(key) is None]
    if missing:
        return {"bounds": None, "unavailable_corners": missing}
    lower = upper = Fraction(0)
    coefficients = {}
    for key in CELLS:
        bounds = cells[key]
        if (not isinstance(bounds, (list, tuple)) or len(bounds) != 2
                or any(type(x) not in (int, float) for x in bounds)
                or bounds[0] > bounds[1]):
            raise ValueError("ordered numeric interval; booleans are not counts")
        sign = (-1) ** sum(key[n] == "0" for n in changed)
        weight = Fraction(sign, 2 ** (3 - len(changed)))
        coefficients[key] = float(weight)
        lower += weight * Fraction(bounds[0] if weight > 0 else bounds[1])
        upper += weight * Fraction(bounds[1] if weight > 0 else bounds[0])
    return {"bounds": [float(lower), float(upper)],
            "unavailable_corners": [], "coefficients": coefficients,
            "meaning": "descriptive finite difference; no significance or causal efficacy claim"}


def factorial_contrasts(cells):
    return {
        "main": {name: interval_contrast(cells, [n]) for n, name in enumerate(FACTORS)},
        "pair": {FACTORS[a] + "_x_" + FACTORS[b]: interval_contrast(cells, [a, b])
                 for a, b in [(0, 1), (0, 2), (1, 2)]},
        "three_way": interval_contrast(cells, [0, 1, 2]),
        "generic_in_factorial": False,
    }


def appearance(card_id, prior_ids, pairs):
    relations = [{"prior_card_id": p, "relation": m.pair_relation(card_id, p, pairs)}
                 for p in prior_ids]
    inherited = any(x["relation"] in ("equivalent", "parameter") for x in relations)
    unresolved = any(x["relation"] != "distinct" for x in relations)
    return {"status": "inherited_family" if inherited else "unresolved" if unresolved
            else "first_introduced", "direct_prior_relations": relations}


def summarize_units(jobs, mapping, lock, states):
    """Pure unit/stage interpretation of existing values and direct pairs."""
    raw_rows = {x["identity"]["card_id"]: x for x in lock["rows"] if x["table"] == "raw_rows"}
    cards = {x["opaque_id"]: x for x in mapping if x.get("field") == "openings"}
    if set(raw_rows) != set(cards):
        raise ValueError("exact complete raw-card map")
    pairs = m.relation_index(lock["rows"])
    units = {}
    for job in jobs:
        key = job["job_id"]
        current = [c for c, x in cards.items() if x["job_id"] == key]
        prior = [c for c, x in cards.items() if x["job_id"] in job["depends_on"]]
        if len(current) > 2:
            raise ValueError("per-stage two-card ceiling")
        valid = states[key] == "valid" and lock["independent_review_complete"]
        rows = [{"card_id": c, "local_id": cards[c]["local_id"],
                 "qualification": m.qualification(raw_rows[c]),
                 "locked_values": raw_rows[c]["values"],
                 "field_status": raw_rows[c]["field_status"],
                 "first_appearance": appearance(c, prior, pairs) if valid else None}
                for c in current]
        eligible = [x["card_id"] for x in rows if x["qualification"]["status"] == "eligible"]
        unknown = [x["card_id"] for x in rows if x["qualification"]["status"] == "unresolved"]
        introduced = [x["card_id"] for x in rows if x["qualification"]["status"] == "eligible"
                      and valid and x["first_appearance"]["status"] == "first_introduced"]
        units[key] = {"job_id": key, "arm": job["arm"], "stage": job["stage"],
                      "operation": job["operation"], "execution": states[key],
                      "evaluable": valid, "candidate_count": len(current), "cards": rows,
                      "qualified_card_count": len(eligible) if valid else None,
                      "unresolved_card_count": len(unknown) if valid else None,
                      "qualified_family_bounds": m.family_bounds(eligible, pairs) if valid else None,
                      "potential_family_bounds": [m.family_bounds(eligible, pairs)[0],
                                                  len(eligible) + len(unknown)] if valid else None,
                      "qualified_first_introduced_family_bounds": m.family_bounds(introduced, pairs) if valid else None,
                      "no_opening": states[key] == "valid" and not current}
    final = {x["arm"]: x for x in units.values() if x["stage"] == 3}
    if set(final) != set(CELLS) | {"G"}:
        raise ValueError("all nine final-stage cells including matched generic")
    return {"units": units, "final_cells": final,
            "factorial_qualified_family_contrasts": factorial_contrasts(
                {k: final[k]["qualified_family_bounds"] for k in CELLS}),
            "interpretation": "Final-stage current qualification differs from first creation. "
                              "Prior matches remain inherited; unknown direct relations remain unresolved."}


def case_metrics(case):
    f.ready()
    i.bindings_valid(i.read(i.R / i.ADMISSION)["upstream_phase_bindings"])
    independent = i.read(i.R / i.INDEPENDENT)
    for field in ("review", "input", "prompt"):
        if i.sha(i.R / independent["native_" + field + "_ref"]) != independent["native_" + field + "_sha256"]:
            raise ValueError("parent upstream/independent source binding drift")
    i.ready()
    log = i.events()
    packet, _ = i.bound_case(case, "packet", log)
    lock, _ = i.bound_case(case, "lock", log)
    admin = i.read(i.R / i.packet_ref(case, "map"))
    jobs = [j for j in i.all_jobs().values() if j["case_id"] == case and j.get("role") == "raw"]
    states = i.status(log)
    if len(jobs) != 27 or any(states[j["job_id"]] not in i.TERMINAL for j in jobs):
        raise ValueError("all 27 planned raw units terminal or explicitly skipped")
    result = summarize_units(jobs, admin["mapping"], lock, states)
    ids = {j["job_id"] for j in i.all_jobs().values() if j["case_id"] == case}
    terminals = [e for e in log if e.get("job_id") in ids and e["event_kind"] == "native_terminal_join"]
    result.update(study_id="I11", case_id=case, raw_review_complete=lock["independent_review_complete"],
                  disposition_coverage=lock["disposition_coverage"], expected_rows=packet["expected_total_rows"],
                  saved_words_proxy=sum(e["validation"].get("saved_words") or 0 for e in terminals),
                  no_compression_planned=True, compression_preservation=None,
                  raw_scalar_unresolved=len(lock["disputes"]),
                  raw_family_unresolved=len(lock["family_disagreements"]),
                  source_bindings=lock["source_bindings"] + i.bindings([
                      i.packet_ref(case, "lock"), "tools/raw_i11_metrics_v1.py",
                      "tools/raw_first_case_metrics.py", i.FREEZE, i.INDEPENDENT, i.ADMISSION]))
    return result
