"""Second implementation of witness evaluation; does not import the checker.

This improves error detection. It is not a mechanized checker soundness proof.
"""

FIELDS = ("scope", "owner", "surface", "object", "operation", "basis", "effect", "challenge_route")
AXES = {"kind", "status", "evidence", "commitment", "provenance", "owner", "residue"}


def facts(model):
    p, a = set(), set()
    roots = {tuple(root.get(k) for k in FIELDS) for root in model["root_grants"]}
    for record in model["records"]:
        path = record["provenance_path"]
        trail_ok = len(path) > 0
        for step in path:
            keys = ("residue_ref", "owner_route") if step.get("missing") is True else ("source", "relation", "operation", "owner", "posture")
            if any(not isinstance(step.get(k), str) or not step[k].strip() for k in keys):
                trail_ok = False
        if trail_ok:
            p.add(record["id"])
        claim = record["authority_claim"]
        if claim is not None:
            values = tuple(claim.get(k) for k in FIELDS)
            if (all(isinstance(v, str) and v.strip() for v in values) and values in roots
                    and claim["object"] == record["id"] and claim["scope"] == "scope:pilot-local-use"):
                a.add(record["id"])
    return p, a


def frame(move):
    if move["before"].keys() != AXES or move["after"].keys() != AXES:
        return False
    delta = {k for k in AXES if move["before"][k] != move["after"][k]}
    allowed = set(move["intended_axes"]) | set(move["recorded_changes"])
    return bool(move["intended_axes"]) and allowed <= AXES and not (delta - allowed) and not (set(move["recorded_changes"]) - delta)


def verify(model, spec, query):
    # A submitted witness cannot replace trusted inputs or omit a subject.
    expected_roots = [g for g in spec["root_grants"] if any(r["authority_claim"] is not None and r["id"] == g["object"] for r in model["records"])]
    if model["root_grants"] != expected_roots or model["move"] not in spec["moves"]:
        return False
    if [r["id"] for r in model["records"]] != spec["bounds"]["subjects"]:
        return False
    if not frame(model["move"]):
        return False
    p, a = facts(model)
    for record in model["records"]:
        if record["provenance_path"] and record["id"] not in p:
            return False
        if record["authority_claim"] is not None and record["id"] not in a:
            return False
    if spec["coupling"] == "routed-authority-requires-recorded-provenance" and a - p:
        return False
    restrictions = set(spec["restrictions"])
    if ("provenance-implies-authority" in restrictions and p - a) or ("no-authority" in restrictions and a) or ("no-provenance" in restrictions and p) or ("some-authority" in restrictions and not a):
        return False
    return {"combined-satisfiability": True, "required-inhabitation": bool(p and a),
            "provenance-without-authority": bool(p and a and p - a), "permitted-overlap": bool(p & a)}[query]
