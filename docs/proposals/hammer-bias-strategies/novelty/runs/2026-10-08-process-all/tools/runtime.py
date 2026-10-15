#!/usr/bin/env python3
"""Structural experiment runtime; receipts are parent-recorded, without OS isolation."""

import argparse
import contextlib
import datetime
import hashlib
import json
import re
from pathlib import Path

R = Path(__file__).resolve().parents[1]
FIT = {"preserves", "uncertain", "conditional", "violates"}
KINDS = {"mechanism", "hypothesis", "question"}
DISPOSITIONS = {"retained", "merged", "rejected", "parked"}
CONSTRUCTION = {"constructed", "tested", "no_viable_branch"}


class RuntimeFault(Exception):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def words(data):
    return len(data.decode("utf-8", errors="replace").split())


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate JSON property: " + key)
        result[key] = value
    return result


def decode(data):
    return json.loads(data.decode("utf-8"), object_pairs_hook=pairs)


def file_record(path):
    data = path.read_bytes()
    return {"path": str(path), "sha256": sha(data), "word_proxy": words(data),
            "bytes": len(data)}


def path_for(value):
    path = Path(value)
    return path.resolve() if path.is_absolute() else (R / path).resolve()


def paths(job_id):
    return (R / "prompts" / "jobs" / (job_id + ".txt"),
            R / "prompts" / "jobs" / (job_id + ".manifest.json"),
            R / "outputs" / (job_id + ".json"))


def schedule():
    data = (R / "schedule.json").read_bytes()
    digest = sha(data)
    freeze = R / "freeze-manifest.json"
    if freeze.exists():
        frozen = decode(freeze.read_bytes())
        expected = frozen.get("schedule_sha256", frozen.get("schedule_hash"))
        if expected is None:
            expected = frozen.get("hashes", {}).get("schedule.json")
        if expected is None:
            entry = frozen.get("schedule")
            expected = entry.get("sha256") if isinstance(entry, dict) else entry
        if expected != digest:
            raise RuntimeFault("frozen schedule hash is missing or does not match")
    document = decode(data)
    rows = document.get("jobs") if isinstance(document, dict) else None
    if not isinstance(rows, list):
        raise RuntimeFault("schedule must contain a jobs list")
    jobs = {}
    for job in rows:
        if not isinstance(job, dict):
            raise RuntimeFault("schedule job must be an object")
        for field in ("job_id", "stage", "case_id", "role", "condition", "prefix", "kind", "template"):
            if not isinstance(job.get(field), str) or not job[field]:
                raise RuntimeFault("schedule job needs nonempty string " + field)
        identifier = job["job_id"]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", identifier) or identifier in jobs:
            raise RuntimeFault("unsafe or duplicate job ID: " + identifier)
        if job["kind"] not in {"raw", "critique", "distill"} or job["role"] not in {"Z", "A", "Q", "T", "D"}:
            raise RuntimeFault("unknown job kind or role: " + identifier)
        if (job["kind"] == "distill") != (job["role"] == "D"):
            raise RuntimeFault("distill must have role D: " + identifier)
        if Path(job["template"]).is_absolute():
            raise RuntimeFault("template must be relative: " + identifier)
        for field in ("sources", "depends_on"):
            if not isinstance(job.get(field), list) or any(not isinstance(x, str) or not x for x in job[field]):
                raise RuntimeFault(field + " must be a string list: " + identifier)
            if len(job[field]) != len(set(job[field])):
                raise RuntimeFault("duplicate " + field + ": " + identifier)
        jobs[identifier] = job
    for identifier, job in jobs.items():
        if identifier in job["depends_on"] or any(dep not in jobs for dep in job["depends_on"]):
            raise RuntimeFault("unknown or self dependency: " + identifier)
    visiting, visited = set(), set()

    def visit(identifier):
        if identifier in visiting:
            raise RuntimeFault("dependency cycle")
        if identifier in visited:
            return
        visiting.add(identifier)
        for dep in jobs[identifier]["depends_on"]:
            visit(dep)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in jobs:
        visit(identifier)
    return jobs, digest


def events():
    path = R / "receipts" / "events.jsonl"
    if not path.exists():
        return []
    result = []
    for line_no, line in enumerate(path.read_bytes().splitlines(), 1):
        if not line:
            raise RuntimeFault("empty receipt line " + str(line_no))
        value = decode(line)
        if not isinstance(value, dict):
            raise RuntimeFault("receipt must be an object")
        result.append(value)
    return result


def append(event):
    event = dict(event, timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat())
    path = R / "receipts" / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("ab") as stream:
        stream.write((json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
        stream.flush()
    return event


@contextlib.contextmanager
def locked():
    # Serialize CLI transactions. This is bookkeeping, not model isolation.
    import fcntl
    directory = R / "receipts"
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".runtime.lock").open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield
        fcntl.flock(stream, fcntl.LOCK_UN)


def selected(rows, identifier, kind):
    return [row for row in rows if row.get("job_id") == identifier and row.get("event") == kind]


def one(rows, identifier, kind, required=False):
    matches = selected(rows, identifier, kind)
    if len(matches) > 1 or (required and not matches):
        raise RuntimeFault("expected " + ("exactly one " if required else "at most one ") + kind + " for " + identifier)
    return matches[0] if matches else None


def disposition(rows, identifier):
    joined = one(rows, identifier, "join")
    skipped = one(rows, identifier, "skip")
    if joined and skipped:
        raise RuntimeFault("multiple terminal dispositions: " + identifier)
    if skipped:
        return "skipped"
    if joined:
        return "valid" if joined.get("validation", {}).get("valid") is True else "failed"
    return None


def check_record(record, label, errors, expected_path):
    try:
        if record["path"] != str(expected_path):
            errors.append(label + " path changed")
            return
        current = file_record(Path(record["path"]))
        if current["sha256"] != record["sha256"]:
            errors.append(label + " hash changed")
    except (OSError, KeyError, TypeError, ValueError) as error:
        errors.append(label + " unavailable: " + str(error))


def manifest_for(job, rows, digest):
    prepared = one(rows, job["job_id"], "prepare", required=True)
    prompt, manifest_path, output = paths(job["job_id"])
    errors = []
    try:
        data = manifest_path.read_bytes()
        if sha(data) != prepared.get("manifest_sha256"):
            errors.append("manifest hash changed")
        manifest = decode(data)
        if not isinstance(manifest, dict) or not isinstance(manifest.get("sources"), list) or any(not isinstance(source, dict) for source in manifest["sources"]):
            return None, errors + ["manifest has invalid structure"]
        if not isinstance(manifest.get("prompt"), dict) or not isinstance(manifest.get("template"), dict):
            return None, errors + ["manifest prompt/template has invalid structure"]
        if manifest.get("job") != job or manifest.get("schedule_sha256") != digest:
            errors.append("prepared job or schedule changed")
        if manifest.get("prompt", {}).get("path") != str(prompt) or manifest.get("output_path") != str(output):
            errors.append("manifest prompt/output path mismatch")
        if manifest.get("template", {}).get("path") != str(path_for(job["template"])):
            errors.append("manifest template does not match named template")
        if [source.get("path") for source in manifest.get("sources", [])] != [str(path_for(value)) for value in job["sources"]]:
            errors.append("manifest sources do not match named sources")
        check_record(manifest.get("prompt", {}), "prompt", errors, prompt)
        check_record(manifest.get("template", {}), "template", errors, path_for(job["template"]))
        for index, source in enumerate(manifest.get("sources", [])):
            if index < len(job["sources"]):
                check_record(source, "source " + str(index), errors, path_for(job["sources"][index]))
        # The receipt contains independent snapshots, so a changed manifest cannot
        # redefine the allowed input hashes without producing an audit error.
        if manifest.get("prompt") != prepared.get("prompt") or manifest.get("template") != prepared.get("template") or manifest.get("sources") != prepared.get("sources"):
            errors.append("manifest does not match prepare receipt")
        return manifest, errors
    except (OSError, ValueError, KeyError, TypeError) as error:
        return None, errors + ["manifest unavailable: " + str(error)]


def dependency_receipts(job, rows):
    receipts = []
    for dep in job["depends_on"]:
        joined = one(rows, dep, "join", required=True)
        if joined.get("terminal_observed") is not True or joined.get("validation", {}).get("valid") is not True or not joined.get("sha256"):
            raise RuntimeFault("dependency has no valid native terminal join: " + dep)
        if joined.get("native") is not True:
            raise RuntimeFault("dependency join is not native: " + dep)
        dep_output = paths(dep)[2]
        if not dep_output.exists() or sha(dep_output.read_bytes()) != joined["sha256"]:
            raise RuntimeFault("dependency output hash changed or missing: " + dep)
        if one(rows, dep, "skip"):
            raise RuntimeFault("dependency was skipped: " + dep)
        receipts.append({"job_id": dep, "agent": joined["agent"], "sha256": joined["sha256"]})
    return receipts


def prepare(identifier):
    jobs, digest = schedule()
    job = jobs[identifier]
    rows = events()
    prompt, manifest_path, output = paths(identifier)
    if any(path.exists() for path in (prompt, manifest_path, output)) or any(selected(rows, identifier, kind) for kind in ("prepare", "spawn", "join", "skip")):
        raise RuntimeFault("job prompt/output or receipt already exists: " + identifier)
    dependencies = dependency_receipts(job, rows)
    template_path = path_for(job["template"])
    template_data = template_path.read_bytes()
    template = file_record(template_path)
    sources = []
    for source_path in job["sources"]:
        path = path_for(source_path)
        record = file_record(path)
        if path.suffix.lower() == ".json":
            decode(path.read_bytes())
        sources.append(record)
    access = {"job_id": identifier, "case_id": job["case_id"], "role": job["role"],
              "prefix": job["prefix"], "kind": job["kind"], "allowed_sources": sources,
              "template": template, "exact_output_path": str(output)}
    text = template_data.decode("utf-8") + "\n\nRuntime file contract:\nRead the exact allowed source files below directly. Save the requested JSON to the exact output path.\n" + json.dumps(access, indent=2, ensure_ascii=False) + "\n"
    prompt_data = text.encode("utf-8")
    prompt_record = {"path": str(prompt), "sha256": sha(prompt_data), "word_proxy": words(prompt_data), "bytes": len(prompt_data)}
    manifest = {"version": 1, "job": job, "schedule_sha256": digest, "sources": sources,
                "template": template, "prompt": prompt_record, "output_path": str(output),
                "dependencies": dependencies, "actual_tokens": None, "os_isolation": False}
    manifest_data = (json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    prompt.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    with prompt.open("xb") as stream:
        stream.write(prompt_data)
    with manifest_path.open("xb") as stream:
        stream.write(manifest_data)
    return append({"event": "prepare", "job_id": identifier, "stage": job["stage"],
                   "native": False, "manifest_sha256": sha(manifest_data),
                   "prompt": prompt_record, "template": template, "sources": sources,
                   "dependencies": dependencies, "actual_tokens": None})


def source_ids(source_documents, errors, case_id):
    refs, raw = set(), set()
    for index, source in enumerate(source_documents):
        if not isinstance(source, dict):
            continue
        supplied_case = source.get("case_id")
        if supplied_case == case_id:
            refs.add(case_id)
        for field in ("observations", "hard_constraints", "supplied_observations", "hard_constraints_with_source"):
            for item in source.get(field, []) if isinstance(source.get(field, []), list) else []:
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    identifier = item["id"]
                    refs.add(identifier)
                    if supplied_case == case_id and re.fullmatch(r"[OC][0-9]+", identifier):
                        refs.add(case_id + ":" + identifier)
        if source.get("role") == "D":
            continue
        openings = source.get("openings", [])
        if not isinstance(openings, list):
            continue
        for opening in openings:
            if isinstance(opening, dict) and isinstance(opening.get("id"), str):
                if "source_ids" in opening:
                    continue
                identifier = opening["id"]
                if identifier in raw:
                    errors.append("duplicate source opening ID: " + identifier)
                raw.add(identifier)
    return refs | raw, raw


def string_field(row, field, where, errors):
    if not isinstance(row.get(field), str):
        errors.append(where + "." + field + " must be a string")


def string_list(row, field, where, errors):
    value = row.get(field)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        errors.append(where + "." + field + " must be a string list")
        return []
    return value


def validate_document(job, document, source_documents):
    errors = []
    refs, raw = source_ids(source_documents, errors, job["case_id"])
    if not isinstance(document, dict):
        return {"valid": False, "errors": ["output must be an object"]}
    if document.get("case_id") != job["case_id"]:
        errors.append("case_id does not match job")
    if document.get("role") != job["role"]:
        errors.append("role does not match job")
    openings = document.get("openings")
    if not isinstance(openings, list):
        errors.append("openings must be a list")
        openings = []
    limit = 6 if job["kind"] == "distill" else 2
    if len(openings) > limit:
        errors.append("too many openings")
    actual_ids, post_sources = set(), {}
    allowed_ids = {job["prefix"] + str(index) for index in range(1, limit + 1)}
    for index, opening in enumerate(openings):
        where = "openings[" + str(index) + "]"
        if not isinstance(opening, dict):
            errors.append(where + " must be an object")
            continue
        identifier = opening.get("id")
        if not isinstance(identifier, str) or identifier not in allowed_ids:
            errors.append(where + ".id has wrong prefix or slot")
        elif identifier in actual_ids:
            errors.append("duplicate output ID: " + identifier)
        else:
            actual_ids.add(identifier)
        if not isinstance(opening.get("fit"), str) or opening["fit"] not in FIT:
            errors.append(where + ".fit is invalid")
        if job["kind"] == "distill":
            for field in ("claim", "discriminator", "probe", "uncertainty"):
                string_field(opening, field, where, errors)
            ids = string_list(opening, "source_ids", where, errors)
            if not ids or len(ids) != len(set(ids)) or any(value not in raw for value in ids):
                errors.append(where + ".source_ids must be nonempty unique known raw IDs")
            if isinstance(identifier, str):
                post_sources[identifier] = set(ids)
        else:
            if not isinstance(opening.get("kind"), str) or opening["kind"] not in KINDS:
                errors.append(where + ".kind is invalid")
            for field in ("claim", "delta", "prediction", "rival_prediction", "defeat", "probe"):
                string_field(opening, field, where, errors)
            ids = string_list(opening, "refs", where, errors)
            string_list(opening, "assumptions", where, errors)
            if any(value not in refs for value in ids):
                errors.append(where + ".refs contains unknown reference")
            if job["condition"] == "P04" and job["role"] == "A":
                comparison = opening.get("component_comparison")
                if not isinstance(comparison, dict):
                    errors.append(where + ".component_comparison must be an object")
                else:
                    for field in ("baseline", "parent_a", "parent_b", "hybrid", "interaction_test"):
                        if not isinstance(comparison.get(field), str) or not comparison[field].strip():
                            errors.append(where + ".component_comparison." + field + " must be a nonempty string")
    if job["kind"] != "distill":
        if job["role"] == "T":
            string_field(document, "decision", "output", errors)
            unresolved = document.get("unresolved")
            if not isinstance(unresolved, list):
                errors.append("unresolved must be a list")
                unresolved = []
            for index, item in enumerate(unresolved):
                where = "unresolved[" + str(index) + "]"
                if not isinstance(item, dict):
                    errors.append(where + " must be an object")
                    continue
                string_field(item, "issue", where, errors)
                ids = string_list(item, "refs", where, errors)
                if any(value not in refs for value in ids):
                    errors.append(where + ".refs contains unknown reference")
        critiques = document.get("critiques", [])
        if job["kind"] == "critique" and "critiques" not in document:
            errors.append("critique output requires critiques list")
        if not isinstance(critiques, list):
            errors.append("critiques must be a list")
            critiques = []
        if len(critiques) > 2:
            errors.append("too many critiques")
        for index, critique in enumerate(critiques):
            where = "critiques[" + str(index) + "]"
            if not isinstance(critique, dict):
                errors.append(where + " must be an object")
                continue
            if not isinstance(critique.get("source_id"), str) or critique["source_id"] not in raw:
                errors.append(where + ".source_id is unknown")
            string_field(critique, "issue", where, errors)
            if not isinstance(critique.get("fit"), str) or critique["fit"] not in FIT:
                errors.append(where + ".fit is invalid")
            ids = string_list(critique, "opening_ids", where, errors)
            if len(ids) != len(set(ids)) or any(value not in actual_ids for value in ids):
                errors.append(where + ".opening_ids must refer to unique actual output openings")
            if job["condition"] == "P02" or "construction_disposition" in critique:
                state = critique.get("construction_disposition")
                if not isinstance(state, str) or state not in CONSTRUCTION:
                    errors.append(where + ".construction_disposition is invalid or missing")
                elif job["condition"] == "P02":
                    if state in {"constructed", "tested"} and not ids:
                        errors.append(where + " constructed/tested requires opening_ids")
                    if state == "no_viable_branch":
                        if ids:
                            errors.append(where + " no_viable_branch requires empty opening_ids")
                        if not isinstance(critique.get("issue"), str) or not critique["issue"].strip():
                            errors.append(where + " no_viable_branch requires issue/reason text")
    else:
        string_field(document, "decision", "output", errors)
        lineage = document.get("lineage")
        if not isinstance(lineage, list):
            errors.append("lineage must be a list")
            lineage = []
        seen, links = set(), {}
        for index, entry in enumerate(lineage):
            where = "lineage[" + str(index) + "]"
            if not isinstance(entry, dict):
                errors.append(where + " must be an object")
                continue
            identifier = entry.get("source_id")
            if not isinstance(identifier, str) or identifier not in raw:
                errors.append(where + ".source_id is unknown")
            elif identifier in seen:
                errors.append("duplicate lineage source: " + identifier)
            else:
                seen.add(identifier)
            state = entry.get("disposition")
            if not isinstance(state, str) or state not in DISPOSITIONS:
                errors.append(where + ".disposition is invalid")
                state = None
            targets = string_list(entry, "target_ids", where, errors)
            string_field(entry, "reason", where, errors)
            if len(targets) != len(set(targets)) or any(target not in actual_ids for target in targets):
                errors.append(where + ".target_ids contains duplicate or unknown post ID")
            if state in {"retained", "merged"}:
                if not targets or any(identifier not in post_sources.get(target, set()) for target in targets):
                    errors.append(where + " retained/merged source is not represented in its targets")
            elif state in {"rejected", "parked"} and targets:
                errors.append(where + " rejected/parked source must have no targets")
            if isinstance(identifier, str):
                links[identifier] = (state, set(targets))
        if seen != raw:
            errors.append("lineage must cover every raw source ID exactly once")
        for target, ids in post_sources.items():
            for identifier in ids:
                state, targets = links.get(identifier, (None, set()))
                if state not in {"retained", "merged"} or target not in targets:
                    errors.append("post source is orphaned or misattributed: " + identifier + " -> " + target)
    return {"valid": not errors, "errors": errors}


def validation_for(job, rows, digest):
    manifest, errors = manifest_for(job, rows, digest)
    source_documents = []
    # Never let a corrupt manifest expand the read surface beyond named sources.
    for source in job["sources"]:
        try:
            path = path_for(source)
            if path.suffix.lower() == ".json":
                source_documents.append(decode(path.read_bytes()))
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append("source JSON unavailable: " + str(error))
    output = paths(job["job_id"])[2]
    try:
        data = output.read_bytes()
        digest_out, known_words = sha(data), words(data)
        try:
            result = validate_document(job, decode(data), source_documents)
            errors.extend(result["errors"])
        except (ValueError, TypeError, KeyError) as error:
            errors.append("invalid output JSON: " + str(error))
    except OSError as error:
        digest_out, known_words = None, None
        errors.append("output unavailable: " + str(error))
    return {"valid": not errors, "errors": errors}, digest_out, known_words


def validate(identifier):
    jobs, digest = schedule()
    result, output_sha, known_words = validation_for(jobs[identifier], events(), digest)
    return append({"event": "validate", "job_id": identifier, "stage": jobs[identifier]["stage"],
                   "native": False, "validation": result, "sha256": output_sha,
                   "known_words": known_words, "actual_tokens": None})


def spawn(identifier, agent):
    jobs, digest = schedule()
    job, rows = jobs[identifier], events()
    if not isinstance(agent, str) or not agent.strip():
        raise RuntimeFault("agent must be a nonempty string")
    if any(selected(rows, identifier, kind) for kind in ("spawn", "join", "skip")) or paths(identifier)[2].exists():
        raise RuntimeFault("prior spawn/join/skip or output prevents spawn: " + identifier)
    _, errors = manifest_for(job, rows, digest)
    if errors:
        raise RuntimeFault("prepared prompt is not hash-current: " + "; ".join(errors))
    dependency_receipts(job, rows)
    return append({"event": "spawn", "job_id": identifier, "stage": job["stage"],
                   "agent": agent, "native": True, "parent_recorded": True,
                   "os_isolation": False, "actual_tokens": None})


def join(identifier, agent, terminal_observed=False):
    jobs, digest = schedule()
    job, rows = jobs[identifier], events()
    if not terminal_observed:
        raise RuntimeFault("join requires --terminal-observed")
    if selected(rows, identifier, "join") or selected(rows, identifier, "skip"):
        raise RuntimeFault("prior terminal disposition prevents join: " + identifier)
    prior = one(rows, identifier, "spawn", required=True)
    if prior.get("agent") != agent:
        raise RuntimeFault("join agent differs from prior spawn")
    validation, output_sha, known_words = validation_for(job, rows, digest)
    return append({"event": "join", "job_id": identifier, "stage": job["stage"],
                   "agent": agent, "native": True, "terminal_observed": True,
                   "observation": "parent-recorded terminal observation", "parent_recorded": True,
                   "os_isolation": False, "output_path": str(paths(identifier)[2]),
                   "validation": validation, "sha256": output_sha,
                   "known_words": known_words, "actual_tokens": None})


def skip(identifier):
    jobs, _ = schedule()
    job, rows = jobs[identifier], events()
    if any(selected(rows, identifier, kind) for kind in ("spawn", "join", "skip")) or paths(identifier)[2].exists():
        raise RuntimeFault("spawn/output or prior disposition prevents skip: " + identifier)
    causes = [{"job_id": dep, "state": disposition(rows, dep)} for dep in job["depends_on"]
              if disposition(rows, dep) in {"failed", "skipped"}]
    if not causes:
        raise RuntimeFault("skip requires a terminal failed/skipped dependency")
    return append({"event": "skip", "job_id": identifier, "stage": job["stage"],
                   "native": False, "causes": causes,
                   "reason": "Dependency failure propagated from " + ", ".join(cause["job_id"] for cause in causes),
                   "actual_tokens": None})


def status():
    jobs, digest = schedule()
    rows = events()
    states, ready = {}, []
    for identifier, job in jobs.items():
        errors = []
        terminal = disposition(rows, identifier)
        prepared = one(rows, identifier, "prepare")
        spawned = one(rows, identifier, "spawn")
        if prepared:
            _, errors = manifest_for(job, rows, digest)
        if terminal:
            state = terminal
            if terminal in {"valid", "failed"}:
                receipt = one(rows, identifier, "join", required=True)
                output = paths(identifier)[2]
                current = sha(output.read_bytes()) if output.exists() else None
                if current != receipt.get("sha256"):
                    errors.append("joined output changed or missing")
                if errors:
                    state = "failed"
            elif paths(identifier)[2].exists():
                errors.append("skipped job has an output")
        elif spawned:
            state = "running"
        else:
            state = "unprepared"
            if paths(identifier)[2].exists():
                errors.append("output exists without spawn/join")
            if prepared and not errors:
                try:
                    dependency_receipts(job, rows)
                    state = "ready"
                    ready.append(identifier)
                except RuntimeFault as error:
                    errors.append(str(error))
        states[identifier] = {"status": state, "errors": errors}
    return {"jobs": states, "next_ready_ids": ready,
            "terminal": all(value["status"] in {"valid", "failed", "skipped"} for value in states.values())}


def audit():
    jobs, digest = schedule()
    rows, errors = events(), []
    history = []
    for index, receipt in enumerate(rows):
        identifier, kind = receipt.get("job_id"), receipt.get("event")
        if identifier not in jobs or kind not in {"prepare", "spawn", "join", "skip", "validate"}:
            errors.append("unknown receipt job/event at " + str(index))
            history.append(receipt)
            continue
        job = jobs[identifier]
        if receipt.get("stage") != job["stage"]:
            errors.append("receipt stage mismatch: " + identifier)
        try:
            if kind in {"prepare", "spawn", "join", "skip"} and selected(history, identifier, kind):
                raise RuntimeFault("duplicate " + kind + ": " + identifier)
            if kind in {"prepare", "spawn"}:
                dependency_receipts(job, history)
                if any(selected(history, identifier, value) for value in ("join", "skip")):
                    raise RuntimeFault("activity after terminal disposition: " + identifier)
                if kind == "spawn":
                    one(history, identifier, "prepare", required=True)
            if kind == "join":
                prior = one(history, identifier, "spawn", required=True)
                if selected(history, identifier, "skip") or receipt.get("agent") != prior.get("agent") or receipt.get("terminal_observed") is not True or receipt.get("native") is not True:
                    raise RuntimeFault("invalid native join: " + identifier)
                if receipt.get("parent_recorded") is not True or receipt.get("os_isolation") is not False or receipt.get("actual_tokens") is not None or receipt.get("observation") != "parent-recorded terminal observation":
                    raise RuntimeFault("join observation/usage metadata mismatch: " + identifier)
                validation = receipt.get("validation")
                if not isinstance(validation, dict) or not isinstance(validation.get("valid"), bool) or not isinstance(validation.get("errors"), list):
                    raise RuntimeFault("join lacks full validation result: " + identifier)
                if validation["valid"] == bool(validation["errors"]):
                    raise RuntimeFault("inconsistent join validation result: " + identifier)
            if kind == "skip":
                if any(selected(history, identifier, value) for value in ("spawn", "join")):
                    raise RuntimeFault("skip after execution: " + identifier)
                causes = [{"job_id": dep, "state": disposition(history, dep)} for dep in job["depends_on"] if disposition(history, dep) in {"failed", "skipped"}]
                if not causes or receipt.get("causes") != causes or not isinstance(receipt.get("reason"), str) or not receipt["reason"]:
                    raise RuntimeFault("skip has no exact causal failed dependency: " + identifier)
        except (RuntimeFault, OSError, ValueError, KeyError, TypeError) as error:
            errors.append(str(error))
        history.append(receipt)
    terminals, counts = [], {"scheduled_jobs": len(jobs), "preparation_events": 0,
                            "native_spawns": 0, "native_joins": 0, "scored_native_spawns": 0,
                            "preflight_native_spawns": 0, "valid": 0, "failed": 0, "skipped": 0}
    counts["preparation_events"] = sum(row.get("event") == "prepare" for row in rows)
    counts["native_spawns"] = sum(row.get("event") == "spawn" for row in rows)
    counts["native_joins"] = sum(row.get("event") == "join" for row in rows)
    counts["scored_native_spawns"] = sum(row.get("event") == "spawn" and row.get("stage") != "preflight" for row in rows)
    counts["preflight_native_spawns"] = sum(row.get("event") == "spawn" and row.get("stage") == "preflight" for row in rows)
    for identifier, job in jobs.items():
        try:
            prepared = one(rows, identifier, "prepare")
            spawned = one(rows, identifier, "spawn")
            terminal = disposition(rows, identifier)
            if terminal:
                terminals.append(identifier)
                counts[terminal] += 1
            if prepared:
                manifest, issues = manifest_for(job, rows, digest)
                errors.extend(identifier + ": " + issue for issue in issues)
                if manifest is not None:
                    expected = dependency_receipts(job, rows)
                    if manifest.get("dependencies") != expected or prepared.get("dependencies") != expected:
                        errors.append("prepared dependency snapshot mismatch: " + identifier)
            elif paths(identifier)[0].exists() or paths(identifier)[1].exists():
                errors.append("prompt/manifest has no prepare receipt: " + identifier)
            output = paths(identifier)[2]
            if terminal in {"valid", "failed"}:
                receipt = one(rows, identifier, "join", required=True)
                current = sha(output.read_bytes()) if output.exists() else None
                if current != receipt.get("sha256"):
                    errors.append("joined output changed, removed, or added: " + identifier)
                current_words = words(output.read_bytes()) if output.exists() else None
                if current_words != receipt.get("known_words") or receipt.get("output_path") != str(output):
                    errors.append("joined output metadata mismatch: " + identifier)
            elif terminal == "skipped" and output.exists():
                errors.append("skipped output must remain absent: " + identifier)
            elif output.exists() and not spawned:
                errors.append("output has no native spawn: " + identifier)
            failed_deps = [dep for dep in job["depends_on"] if disposition(rows, dep) in {"failed", "skipped"}]
            if failed_deps and terminal and terminal != "skipped":
                errors.append("failed-dependent job was not skipped: " + identifier)
        except (RuntimeFault, OSError, ValueError, KeyError, TypeError) as error:
            errors.append(identifier + ": " + str(error))
    terminal = len(terminals) == len(jobs)
    return {"ok": not errors, "terminal": terminal, "errors": errors, "counts": counts,
            "open_job_ids": [identifier for identifier in jobs if identifier not in terminals],
            "limitation": "Structural success is not semantic evidence. Native observations are parent-recorded; no OS isolation; actual tokens are unobserved."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("prepare", "validate", "skip"):
        commands.add_parser(command).add_argument("job")
    for command in ("spawn", "join"):
        sub = commands.add_parser(command)
        sub.add_argument("job")
        sub.add_argument("agent")
        if command == "join":
            sub.add_argument("--terminal-observed", action="store_true")
    for command in ("status", "audit"):
        commands.add_parser(command)
    arguments = parser.parse_args(argv)
    try:
        with locked():
            if arguments.command in {"prepare", "validate", "skip"}:
                result = globals()[arguments.command](arguments.job)
            elif arguments.command == "spawn":
                result = spawn(arguments.job, arguments.agent)
            elif arguments.command == "join":
                result = join(arguments.job, arguments.agent, arguments.terminal_observed)
            else:
                result = globals()[arguments.command]()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if result.get("validation", {}).get("valid") is False or result.get("ok") is False:
            return 1
        return 0
    except (RuntimeFault, OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
