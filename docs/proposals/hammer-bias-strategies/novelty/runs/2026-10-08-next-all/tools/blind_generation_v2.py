"""Prospective case-packet construction; no scored artifact is read on import.

The CLI reads only a selected scheduled case when explicitly run later. Terminal
receipts (or an exact disposition manifest) are required. Administrative bindings
are returned separately and written exclusively beneath receipts/ by the CLI.
"""
from pathlib import Path
from itertools import combinations
import argparse
import copy
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
TABLES = {
    "raw_rows": ("card_id",),
    "archive_pairs": ("card_id", "archive_id"),
    "candidate_pairs": ("card_a", "card_b"),
    "post_rows": ("card_id",),
    "retention_rows": ("source_card_id",),
    "lineage_rows": ("unit_id", "source_id"),
    "addition_rows": ("card_id",),
    "attack_rows": ("unit_id", "attack_id"),
    "contradiction_rows": ("unit_id", "pair_id"),
    "unit_rows": ("unit_id",),
}
EXECUTIONS = {"valid", "invalid", "missing", "skipped"}
MARKER = "Missing source cards are not silently invented."


def read(path):
    return json.loads(Path(path).read_text())


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def opaque(domain, value):
    return domain + "-" + digest("generation-blind-v2|" + domain + "|" + value)[:20]


def card_id(job, local):
    return opaque("U", job) + ":" + opaque("C", job + "|" + str(local))


def administrative_text(text):
    """Hide study/cell labels while preserving the supplied causal instruction."""
    text = re.sub(r"\b[IP]\d{2}(?:-[IP]\d{2})?\b", "[study withheld]", text)
    text = text.replace("All arms", "All comparable units").replace("Both arms", "Both comparable units")
    text = text.replace("per arm", "per source pool").replace("All arms/reviewers", "All units/reviewers")
    text = text.replace("A/Q raw", "treatment raw").replace("Shared Z", "Shared source")
    text = text.replace("Z1,Z2,A1,A2,Q1,Q2", "frozen source order")
    return text


def scrub(value):
    if isinstance(value, str):
        return administrative_text(value)
    if isinstance(value, list):
        return [scrub(x) for x in value]
    if isinstance(value, dict):
        return {administrative_text(k): scrub(v) for k, v in value.items()}
    return value


def semantic_contract(prompt, prompt_ref):
    if MARKER in prompt:
        text = prompt.split(MARKER, 1)[1].strip()
        # These sentences describe a factorial schedule, not an operator action.
        text = text.replace(
            "In carrier-off cells retain the source ordinary function carrier; in carrier-on cells follow the assigned carrier instruction.",
            "Keep the source ordinary function carrier." if prompt_ref.endswith("conversion-original.txt") else
            "Apply the additional carrier instruction below.")
        text = text.replace(
            "Conversion-off leaves response ordinary, conversion-on adds its assigned instruction.",
            "Keep the response ordinary; no disturbance conversion is required." if prompt_ref.endswith("ordinary-relocated.txt") else
            "Apply the preceding disturbance conversion instruction.")
        text = re.sub(r"across all I03 arms", "across all comparable units", text)
    else:
        # The entire summary contract carries protected-field meaning. Drop only
        # workflow/role labels, retaining the source adapter and bounded proposal rule.
        text = prompt.replace("role:D,", "").replace("Generation-source adapter:", "Source adapter:")
    text = text.replace("Attack IDs A1/A2", "At most two supplied opaque attack IDs")
    text = text.replace("opening R1", "opening with its supplied opaque ID")
    text = text.replace("{id:D1...", "{id:opaque_current_id")
    text = text.replace("actual D IDs", "actual opaque summary IDs").replace("current local R IDs", "current opaque source IDs")
    text = text.replace("{id:P1/P2", "{id:opaque_proposal_id")
    return administrative_text(text)


def common_source_contract(prompt):
    """Keep shared semantic obligations once, excluding native dispatch bindings."""
    text = prompt.split(MARKER, 1)[0]
    text = text[text.index("These resources/observations"):]
    text = text.replace("Save first substantive JSON only at assigned output, no retries/overwrite.", "")
    text = text.replace("Final only reports artifact/hash; parent observes terminal separately.", "")
    text = text.replace("The parent assigns an exact job_id and role. Echo its role verbatim.", "")
    text = text.replace("The parent supplies the prior artifact/job map.", "")
    text = text.replace("Output {case_id,role,", "Source content {")
    text = text.replace("IDs stable R1,R2 for new card IDs", "Stable supplied opaque IDs for new cards")
    text = text.replace("Current local opening IDs are R1/R2", "Current openings have supplied opaque IDs")
    text = text.replace("<prior_job_id>:<prior_local_id>", "<opaque_prior_unit_id>:<opaque_prior_card_id>")
    text = text.replace("<prior_job_id>:<local_id>:prediction", "<opaque_prior_unit_id>:<opaque_prior_card_id>:prediction")
    text = text.replace("I08 contradiction commitments are", "If contradiction enumeration is instructed, commitments are")
    return administrative_text(text.strip())


def load_inputs(root=ROOT):
    root = Path(root)
    schedule = read(root / "generation-schedule.v2.json")
    reviews = read(root / "generation-review-schedule.v2.json")
    contract = read(root / "generation-review-contract.v2.json")
    criteria = read(root / "criteria-generation.v2.json")
    archives = read(root / "archives/case-archives.json")
    return schedule, reviews, contract, criteria, archives


def build_packet(study_id, case_id, artifacts, dispositions, root=ROOT, inputs=None):
    """Pure assembly from caller-provided bodies/statuses; scheduled files untouched.

    artifacts values are JSON objects, or {unparsed_text: ...} for malformed JSON.
    dispositions values are {execution, cause}. Every scheduled unit must occur.
    Invalid-but-readable content is retained; its assessment fields are null.
    """
    root = Path(root)
    schedule, reviews, contract, criteria, archives = inputs or load_inputs(root)
    selected = [j for j in schedule["jobs"] if j["study_id"] == study_id and j["case_id"] == case_id]
    if not selected:
        raise ValueError("unknown scheduled case")
    jobs = {j["job_id"]: j for j in selected}
    if set(dispositions) != set(jobs):
        raise ValueError("exact scheduled disposition coverage required")
    if not set(artifacts) <= set(jobs):
        raise ValueError("artifact outside selected case")
    for k, d in dispositions.items():
        if not isinstance(d, dict) or d.get("execution") not in EXECUTIONS:
            raise ValueError("explicit execution enum required: " + k)
        if not isinstance(d.get("cause"), str) or not d["cause"].strip():
            raise ValueError("explicit disposition cause required: " + k)
        if d["execution"] == "valid" and not isinstance(artifacts.get(k), dict):
            raise ValueError("valid unit requires parsed artifact: " + k)

    # Build all identifiers before translating any dependency or free-text reference.
    output_jobs = {j["output_ref"]: j["job_id"] for j in schedule["jobs"]}
    ids, local_ids, original_cards = {}, {}, {}
    allocated_ids = set()
    mappings = []
    for k in jobs:
        body = artifacts.get(k, {})
        local_ids[k] = {}
        for field in ("openings", "proposals", "attacks"):
            values = body.get(field, []) if isinstance(body, dict) else []
            if not isinstance(values, list):
                continue
            for index, item in enumerate(values):
                if not isinstance(item, dict):
                    continue
                local = item.get("attack_id" if field == "attacks" else "id")
                if not isinstance(local, str):
                    local = "unidentified-" + field + "-" + str(index)
                # Invalid duplicates remain separately visible; no discarded unit/card.
                unique = local if local not in local_ids[k] else local + "#duplicate-" + str(index)
                ident = card_id(k, unique)
                collision = 0
                while ident in allocated_ids:
                    collision += 1
                    ident = card_id(k, unique + "#" + field + "-" + str(index) + "-" + str(collision))
                allocated_ids.add(ident)
                ids[(k, field, index)] = ident
                local_ids[k].setdefault(local, ident)
                if field == "openings":
                    original_cards.setdefault(k, []).append((ident, item))
                mappings.append({"opaque_id": ident, "job_id": k, "field": field, "index": index,
                                 "local_id": local, "duplicate": unique != local})

    unresolved = set()

    def ref(job, value):
        if not isinstance(value, str):
            return value
        match = re.fullmatch(r"(G\d+):([^:]+)(:prediction)?", value)
        if match:
            producer, local, suffix = match.groups()
            ident = local_ids.get(producer, {}).get(local, card_id(producer, local))
            if producer not in jobs or local not in local_ids.get(producer, {}):
                unresolved.add(ident + (suffix or ""))
            return ident + (suffix or "")
        if value in local_ids.get(job, {}):
            return local_ids[job][value]
        return translate(job, value)

    def translate(job, value):
        if isinstance(value, list):
            return [translate(job, x) for x in value]
        if isinstance(value, dict):
            return {translate(job, k): translate(job, v) for k, v in value.items()
                    if k not in {"role", "job_id", "study_id", "arm", "method", "prompt_ref", "output_ref"}}
        if not isinstance(value, str):
            return value
        if value in local_ids.get(job, {}):
            return local_ids[job][value]
        for output, producer in output_jobs.items():
            value = value.replace(output, opaque("U", producer))
        for source_prompt in {j["prompt_ref"] for j in schedule["jobs"]}:
            value = value.replace(source_prompt, "[administrative instruction reference withheld]")
        value = re.sub(r'"(?:role|job_id|study_id|arm|method|prompt_ref|output_ref)"\s*:\s*"[^"\n]*"',
                       '"binding": "[administrative binding withheld]"', value)
        value = re.sub(r"\bG\d+:[A-Za-z0-9_-]+(?::prediction)?",
                       lambda m: ref(job, m.group(0)), value)
        value = re.sub(r"\bG\d+\b", lambda m: opaque("U", m.group(0)), value)
        return administrative_text(value)

    units, semantic_contracts = [], {}
    for k in sorted(jobs, key=lambda x: opaque("U", x)):
        j = jobs[k]
        prompt = (root / j["prompt_ref"]).read_text()
        instruction = semantic_contract(prompt, j["prompt_ref"])
        contract_id = opaque("O", instruction)
        semantic_contracts[contract_id] = instruction
        common_id = None
        if j["role"] != "compression":
            common = common_source_contract(prompt)
            common_id = opaque("O", common)
            semantic_contracts[common_id] = common
        source_jobs = list(dict.fromkeys(output_jobs[p] for p in j["input_refs"] if p in output_jobs))
        body = copy.deepcopy(artifacts.get(k, {}))
        if not isinstance(body, dict):
            body = {"malformed_value": body}
        body = {key: value for key, value in body.items() if key not in {"role", "job_id", "case_id", "study_id", "arm", "method"}}
        for field in ("openings", "proposals", "attacks"):
            if isinstance(body.get(field), list):
                for index, item in enumerate(body[field]):
                    if isinstance(item, dict):
                        id_key = "attack_id" if field == "attacks" else "id"
                        item[id_key] = ids[(k, field, index)]
                        if "source_ids" in item and isinstance(item["source_ids"], list):
                            # Summary source IDs are local to its one immediate raw pool.
                            producer = source_jobs[-1] if source_jobs else k
                            item["source_ids"] = [ref(producer, x) for x in item["source_ids"]]
        if isinstance(body.get("lineage"), list):
            for item in body["lineage"]:
                if isinstance(item, dict) and "source_id" in item:
                    producer = source_jobs[-1] if j["role"] == "compression" and source_jobs else k
                    item["source_id"] = ref(producer, item["source_id"])
        body = translate(k, body)
        unit_id = opaque("U", k)
        units.append({"unit_id": unit_id, "content_kind": "summary" if j["role"] == "compression" else "source",
                      "execution": dispositions[k]["execution"], "disposition_reason": translate(k, dispositions[k]["cause"]),
                      "source_unit_ids": [opaque("U", z) for z in source_jobs],
                      "semantic_contract_ref": contract_id, "common_contract_ref": common_id, "artifact": body})
        mappings.append({"unit_id": unit_id, "job_id": k, "role": j["role"],
                         "arm_or_method": Path(j["prompt_ref"]).stem,
                         "prompt_ref": j["prompt_ref"], "output_ref": j["output_ref"], "study_id": study_id,
                         "case_id": case_id, "source_job_ids": source_jobs})

    unit_by_id = {u["unit_id"]: u for u in units}
    raw = [(ident, k, item) for k in jobs if jobs[k]["role"] != "compression"
           for ident, item in original_cards.get(k, [])]
    raw.sort(key=lambda x: x[0])
    raw_valid = {ident: dispositions[k]["execution"] == "valid" for ident, k, _ in raw}
    fam = next(a["families"] for a in archives["archives"] if a["case_id"] == case_id)
    archive_list = []
    for item in fam:
        archived = copy.deepcopy(item)
        archived["id"] = opaque("B", case_id + "|" + item["id"])
        archive_list.append(archived)
        mappings.append({"archive_id": archived["id"], "original_archive_id": item["id"]})
    archive_list.sort(key=lambda x: x["id"])
    expected = {name: [] for name in TABLES}

    def row(table, identity, available=True, fixed=None):
        encoded = json.dumps(identity, sort_keys=True, separators=(",", ":"))
        expected[table].append({"row_id": opaque("E", table + "|" + encoded), "identity": identity,
                                "null_semantics": not available, "fixed_values": fixed or {}})

    for ident, k, _ in raw:
        row("raw_rows", {"card_id": ident}, raw_valid[ident])
        for a in archive_list:
            row("archive_pairs", {"card_id": ident, "archive_id": a["id"]}, raw_valid[ident])
    for a, b in combinations([r[0] for r in raw], 2):
        row("candidate_pairs", {"card_a": a, "card_b": b}, raw_valid[a] and raw_valid[b])

    for k in jobs:
        j, uid = jobs[k], opaque("U", k)
        unit = unit_by_id[uid]
        valid = unit["execution"] == "valid"
        body = unit["artifact"]
        sources = unit["source_unit_ids"]
        prior_cards = [o["id"] for s in sources for o in (unit_by_id[s]["artifact"].get("openings", [])
                       if isinstance(unit_by_id[s]["artifact"].get("openings"), list) else [])
                       if isinstance(o, dict) and isinstance(o.get("id"), str)]
        # Exact prior-source coverage is derived from inputs, never an emitted lineage list.
        emitted = body.get("lineage", [])
        emitted = emitted if isinstance(emitted, list) else []
        lin_by_source = {z.get("source_id"): z for z in emitted if isinstance(z, dict) and isinstance(z.get("source_id"), str)}
        all_lineage = list(dict.fromkeys(prior_cards + [z["source_id"] for z in emitted
                                if isinstance(z, dict) and isinstance(z.get("source_id"), str)]))
        for source in all_lineage:
            available = valid and raw_valid.get(source, False)
            row("lineage_rows", {"unit_id": uid, "source_id": source}, available,
                {"disposition": lin_by_source.get(source, {}).get("disposition")} if available else {})
        if j["role"] == "compression":
            for source in prior_cards:
                row("retention_rows", {"source_card_id": source}, valid and raw_valid.get(source, False))
            for post in body.get("openings", []) if isinstance(body.get("openings"), list) else []:
                if isinstance(post, dict) and isinstance(post.get("id"), str):
                    source_ids = post.get("source_ids", [])
                    source_ids = source_ids if isinstance(source_ids, list) else []
                    row("post_rows", {"card_id": post["id"]}, valid and all(raw_valid.get(s, False) for s in source_ids),
                        {"source_ids": source_ids})
            for post in body.get("proposals", []) if isinstance(body.get("proposals"), list) else []:
                if isinstance(post, dict) and isinstance(post.get("id"), str):
                    row("addition_rows", {"card_id": post["id"]}, valid)
        for attack in body.get("attacks", []) if isinstance(body.get("attacks"), list) else []:
            if isinstance(attack, dict) and isinstance(attack.get("attack_id"), str):
                row("attack_rows", {"unit_id": uid, "attack_id": attack["attack_id"]}, valid)
        if j["role"] == "convergence":
            commitments = sorted(source + ":prediction" for source in prior_cards)
            declarations = body.get("contradictions", [])
            declarations = declarations if isinstance(declarations, list) else []
            declared = {tuple(sorted(z["pair"])): z for z in declarations if isinstance(z, dict)
                        and isinstance(z.get("pair"), list) and len(z["pair"]) == 2
                        and all(isinstance(v, str) for v in z["pair"])}
            pairs = list(dict.fromkeys(list(combinations(commitments, 2)) + sorted(declared)))
            unit["prediction_commitment_pairs"] = []
            for pair in pairs:
                pair_id = uid + ":" + opaque("K", "|".join(pair))
                unit["prediction_commitment_pairs"].append({"pair_id": pair_id, "pair": list(pair),
                    "declared": pair in declared, "declaration": declared.get(pair)})
                row("contradiction_rows", {"unit_id": uid, "pair_id": pair_id},
                    valid and all(raw_valid.get(x.removesuffix(":prediction"), False) for x in pair))
        row("unit_rows", {"unit_id": uid}, valid, {"execution": unit["execution"],
            **({"no_opening_reason_supported": None} if valid and body.get("openings") else {})})

    for table in expected:
        expected[table].sort(key=lambda x: json.dumps(x["identity"], sort_keys=True))
        keys = [tuple(x["identity"].values()) for x in expected[table]]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate expected identity: " + table)
    packet_id = opaque("J", study_id + "|" + case_id)
    packet = {"version": "generation-blind-v2", "packet_id": packet_id,
        "epistemic_status": "supplied synthetic task plus model artifacts; no measured efficacy",
        "case": read(root / ("cases/" + case_id + ".json")), "archive": archive_list,
        "review_job_ids": sorted(opaque("V", x["job_id"]) for x in reviews["jobs"]
            if x["study_id"] == study_id and x["case_id"] == case_id),
        "contract": scrub(contract), "criteria": scrub(criteria),
        "semantic_contracts": semantic_contracts, "units": units, "expected_matrix": expected,
        "matrix_counts": {k: len(v) for k, v in expected.items()},
        "expected_total_rows": sum(map(len, expected.values())),
        "unresolved_references": sorted(unresolved),
        "matrix_policy": "All source cards, including shared/intermediate cards; source x archive; all unordered source pairs; every summary/proposal; each immediate raw retention source; exact prior and summary lineage; all declared attacks; every unordered prior central-prediction commitment pair per convergence, with declared membership retained. Nonvalid source-dependent semantic fields must be null, never zero novelty.",
        "review_shape": {"identity_columns": {k: list(v) for k, v in TABLES.items()},
            "unit_contracts": "Apply both common_contract_ref (when present) and semantic_contract_ref; shared common source instructions appear once.",
            "reviewer_id": "Nonempty string; use the assigned opaque review job ID.",
            "limits": "Nonempty string describing review limits and epistemic ceiling.",
            "null_rule": "For a null_semantics row, all nonidentity/nonfixed fields except evidence are null. Evidence always remains a nonempty string. On valid nonempty units no_opening_reason_supported is null (inapplicable).",
            "scope": "Structural validation only: no semantic correctness, evidence adequacy or independence claim."}}
    binding_paths = {"generation-schedule.v2.json", "generation-review-schedule.v2.json",
        "generation-review-contract.v2.json", "criteria-generation.v2.json", "archives/case-archives.json",
        "cases/" + case_id + ".json", *(j["prompt_ref"] for j in selected)}
    mapping = {"version": "generation-method-mapping-v2", "packet_id": packet_id,
               "study_id": study_id, "case_id": case_id, "mapping": mappings,
               "input_bindings": [{"path": p, "sha256": hashlib.sha256((root / p).read_bytes()).hexdigest()}
                   for p in sorted(binding_paths)],
               "artifact_payload_bindings": [{"job_id": k, "sha256": digest(json.dumps(v, sort_keys=True))}
                   for k, v in sorted(artifacts.items())],
               "review_job_bindings": [{"opaque_job_id": opaque("V", x["job_id"]), "job_id": x["job_id"]}
                   for x in reviews["jobs"] if x["study_id"] == study_id and x["case_id"] == case_id]}
    return packet, mapping


def runtime_case(study_id, case_id, root=ROOT, manifest=None):
    """Explicit later invocation; no actual scheduled artifacts used for fixtures."""
    root = Path(root)
    inputs = load_inputs(root)
    selected = [j for j in inputs[0]["jobs"] if j["study_id"] == study_id and j["case_id"] == case_id]
    selected_ids = {j["job_id"] for j in selected}
    if manifest is not None:
        dispositions = read(manifest)
    else:
        dispositions = {}
        for line in (root / "receipts/events.jsonl").read_text().splitlines():
            event = json.loads(line)
            if event.get("job_id") not in selected_ids:
                continue
            if event.get("event_kind") == "native_terminal_join":
                dispositions[event["job_id"]] = {"execution": "valid" if event["validation"]["valid"] else "invalid",
                    "cause": "terminal structural receipt: " + "; ".join(event["validation"].get("errors", [])) if not event["validation"]["valid"] else "terminal structural-valid receipt; semantic validity unasserted",
                    "output_sha256": event["validation"].get("output_sha256")}
            elif event.get("event_kind") == "dependency_disposition":
                dispositions[event["job_id"]] = {"execution": "skipped", "cause": event["cause"]}
        dispositions = {j["job_id"]: dispositions[j["job_id"]] for j in selected if j["job_id"] in dispositions}
    if set(dispositions) != {j["job_id"] for j in selected}:
        raise ValueError("case has nonterminal units; provide every explicit disposition")
    artifacts = {}
    for j in selected:
        path = root / j["output_ref"]
        receipt_hash = dispositions[j["job_id"]].get("output_sha256")
        if manifest is None and dispositions[j["job_id"]]["execution"] == "valid" and not receipt_hash:
            raise ValueError("valid terminal receipt lacks output hash")
        if receipt_hash and (not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != receipt_hash):
            raise ValueError("terminal output bytes changed: " + j["job_id"])
        if path.exists():
            try:
                artifacts[j["job_id"]] = read(path)
            except (ValueError, UnicodeError):
                artifacts[j["job_id"]] = {"unparsed_text": path.read_text(errors="replace")}
    return build_packet(study_id, case_id, artifacts, dispositions, root, inputs)


def save_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as file:
        file.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", required=True)
    parser.add_argument("--case", required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--dispositions", type=Path)
    args = parser.parse_args()
    packet, mapping = runtime_case(args.study, args.case, args.root, args.dispositions)
    packet_path = args.root / "fixtures/generation-blind" / (args.study + "-" + args.case + ".json")
    mapping_path = args.root / "receipts/generation-blind-maps-v2" / (packet["packet_id"] + ".json")
    if packet_path.exists() or mapping_path.exists():
        raise FileExistsError("first-save packet/map already exists")
    # Publish mapping separately; packet contains no filenames/job/method bindings.
    save_new(mapping_path, mapping)
    save_new(packet_path, packet)
    print(json.dumps({"packet": str(packet_path), "mapping_receipt": str(mapping_path),
                      "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
                      "expected_rows": packet["expected_total_rows"], "semantic_validity": "not asserted"}))


if __name__ == "__main__":
    main()
