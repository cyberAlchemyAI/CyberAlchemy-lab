/** Native R01 metadata classification; values are validated only by R02. */
export const PYTHON_WORKFLOW_SETTLEMENT = String.raw`
def _fail(why):
    raise TypeError("WORKFLOW_RUNTIME:" + why)

def _own(value, names):
    if type(value) is not dict or any(type(k) is not str for k in value) or set(value) != set(names):
        _fail("closed inert fields")
    return dict(value)

def _text(v):
    return type(v) is str and 0 < len(v.encode("utf-16-le", "surrogatepass")) // 2 <= 2048

def _identity(v):
    if type(v) is not str or len(v) > 256 or not _fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", v):
        _fail("identity")
    return v

def _freeze(v):
    if type(v) in (dict, _MappingProxyType):
        return _MappingProxyType({k: _freeze(value) for k, value in v.items()})
    if type(v) in (list, tuple):
        return tuple(_freeze(value) for value in v)
    return v

def _canonical(v):
    if type(v) in (tuple, list):
        return "[" + ",".join(_canonical(x) for x in v) + "]"
    if type(v) in (dict, _MappingProxyType):
        return "{" + ",".join(_canonical(k) + ":" + _canonical(v[k]) for k in sorted(v, key=lambda k: k.encode("utf-16-be", "surrogatepass"))) + "}"
    if type(v) is str:
        normalized = v.encode("utf-16-le", "surrogatepass").decode("utf-16-le", "surrogatepass")
        encoded = _json_dumps(normalized, ensure_ascii=False, separators=(",", ":"))
        return "".join("\\u%04x" % ord(c) if 0xd800 <= ord(c) <= 0xdfff else c for c in encoded)
    if v is None or type(v) in (bool, int):
        return _json_dumps(v, separators=(",", ":"))
    return _fail("metadata value")

def _digest(v):
    return _sha256(_canonical(v).encode("utf-8")).hexdigest()

def _unknown(origin):
    return _freeze(dict(commit_status="indeterminate", origin=origin, status=None, stage=None, code=None, continuation=None, cleanup_failed=None, result_validation="not-performed"))

def _not_started():
    return _freeze(dict(commit_status="not-committed", origin="not-started", status=None, stage="argument-materialization", code="ARGUMENT_MATERIALIZATION_FAILED", continuation=None, cleanup_failed=None, result_validation="not-performed"))

def _operation_data(value, outcome_types):
    if type(value) is dict:
        if any(type(k) is not str for k in value) or type(value.get("status")) is not str:
            return _fail("Operation outcome status")
        return _own(value, ("status", "value") if value["status"] == "committed" else ("status", "stage", "code", "continuation", "cleanupFailed"))
    if all(type(value) is not expected for expected in outcome_types):
        return _fail("Operation outcome type")
    status = object.__getattribute__(value, "status")
    if type(status) is not str:
        return _fail("Operation outcome status")
    names = ("status", "value") if status == "committed" else ("status", "stage", "code", "continuation", "cleanupFailed")
    if tuple(type(value).__slots__) != names:
        return _fail("Operation outcome fields")
    return {name: object.__getattribute__(value, name) for name in names}

def _settlement(value, expected_continuation, outcome_types):
    if not _text(expected_continuation):
        _fail("continuation")
    try:
        d = _operation_data(value, outcome_types)
        status = d["status"]
        if type(status) is not str:
            return _unknown("invalid-return")
        if status == "committed":
            return _freeze(dict(commit_status="committed", origin="returned", status="committed", stage=None, code=None, continuation=None, cleanup_failed=None, result_validation="not-performed"))
        stage, code, cleanup, continuation = d["stage"], d["code"], d["cleanupFailed"], d["continuation"]
        if not _text(stage) or not _text(code) or type(continuation) is not str or continuation != expected_continuation or type(cleanup) is not bool:
            return _unknown("invalid-return")
        valid = False
        if stage == "commit":
            valid = not cleanup and (status == "rejected" and code == "COMMIT_REJECTED" or status == "indeterminate" and code in ("COMMIT_INDETERMINATE", "INVALID_COMMIT_RECEIPT", "COMMIT_UNCERTAIN"))
        elif stage == "input":
            valid = status == "failed" and code == "OPERATION_INPUT" and not cleanup
        elif stage == "begin":
            valid = status == "failed" and code == "BEGIN_FAILED" and not cleanup
        elif stage in ("read", "guard", "write-validation", "event", "result"):
            valid = status == "failed" and code == "OPERATION_FAILED" or stage == "read" and status == "failed" and code in ("READ_NOT_FOUND", "READ_IDENTITY_MISMATCH") or stage == "guard" and status == "rejected" and _fullmatch(r"RULE_REJECTED:[a-z][a-z0-9-]*:[a-z][a-z0-9-]*", code) is not None
        if not valid:
            return _unknown("invalid-return")
        return _freeze(dict(commit_status="indeterminate" if status == "indeterminate" else "not-committed", origin="returned", status=status, stage=stage, code=code, continuation=continuation, cleanup_failed=cleanup, result_validation="not-performed"))
    except Exception:
        return _unknown("invalid-return")

def _imported(fn, expected_type, selector, action, descriptor):
    if type(fn) is not expected_type:
        _fail("Operation callable")
    d = fn.descriptor
    if type(d) is not _MappingProxyType or d["selector"] != selector or d["action_sha256"] != action or d["descriptor_sha256"] != descriptor:
        _fail("Operation identity")

def _observe(index, settlement):
    body = dict(schema_version="domainspec.workflow-step-observation/v1-candidate", contract_sha256=_OUTCOME_CONTRACT, workflow_sha256=_WF["hash"], **_WF["steps"][index], settlement=settlement, evidence="caller-supplied", authority_effect="none")
    return _freeze(dict(body, observation_sha256=_digest(body)))

def _recover(completed, failed, ids):
    template = _PREFIXES[len(completed)]
    journal = dict(schema_version="domainspec.workflow-failure-journal/v1-candidate", workflow_execution_id=ids["workflow_execution_id"], failure_occurrence_id=ids["failure_occurrence_id"], completed_step_ids=completed, failed_step_id=failed["step_id"], failed_commit_status=failed["settlement"]["commit_status"])
    common = dict(schema_version="domainspec.workflow-recovery-evaluation/v1-candidate", workflow_sha256=_WF["hash"], policy_sha256=_POLICY, journal=journal, journal_sha256=_digest(journal), commit_evidence="caller-supplied", intent_registration="not-performed", compensation_execution=False, authority_effect="none")
    if failed["settlement"]["commit_status"] == "indeterminate":
        return _freeze(dict(common, status="reconciliation-required", workflow_evaluation_result=None, recovery_intent=None, unknown_step_id=failed["step_id"]))
    if not template["plan"]:
        return _freeze(dict(common, status="evaluated", workflow_evaluation_result="not-required", recovery_intent=None))
    prefix = dict(schema_version="domainspec.workflow-completed-prefix/v1-candidate", workflow_sha256=_WF["hash"], workflow_execution_id=ids["workflow_execution_id"], steps=template["steps"])
    plan_digest = template["plan_digest"]
    body = dict(schema_version="domainspec.workflow-recovery-intent/v3-candidate", workflow_selector=_WF["selector"], workflow_sha256=_WF["hash"], policy_sha256=_POLICY, workflow_execution_id=ids["workflow_execution_id"], failure_occurrence_id=ids["failure_occurrence_id"], failed_step_id=failed["step_id"], completed_step_journal_digest=_digest(prefix), plan_digest=plan_digest)
    intent_id = _digest(body)
    plan = tuple(dict(row, invocation_identity=_digest(dict(schema_version="domainspec.compensation-invocation/v2-candidate", intent_id=intent_id, plan_digest=plan_digest, compensation_id=row["compensation_id"], operation_ref=row["operation_ref"], action_sha256=row["action_sha256"]))) for row in template["plan"])
    return _freeze(dict(common, status="evaluated", workflow_evaluation_result="recovery-required", recovery_intent=dict(body, intent_id=intent_id, semantic_status="required", plan=plan)))

def _evaluate(observations, ids, local_error):
    last = observations[-1] if observations else None
    failed = last if last and last["settlement"]["commit_status"] != "committed" else None
    completed = tuple(row["step_id"] for row in observations if row["settlement"]["commit_status"] == "committed")
    common = dict(schema_version="domainspec.workflow-outcome-evaluation/v1-candidate", workflow_sha256=_WF["hash"], policy_sha256=_POLICY, workflow_execution_id=ids["workflow_execution_id"], failure_occurrence_id=ids["failure_occurrence_id"] if failed or local_error else None, completed_step_ids=completed, observations=observations, evidence="caller-supplied", result_validation="not-performed", execution="not-performed", authority_effect="none")
    if failed:
        recovery = _recover(completed, failed, ids)
        return _freeze(dict(common, status="forward-stopped", failure=failed["settlement"], local_error=None, recovery_status=recovery["status"], recovery=recovery))
    if local_error:
        return _freeze(dict(common, status="orchestration-error", failure=None, local_error=local_error, recovery_status="not-evaluable", recovery=None))
    return _freeze(dict(common, status="forward-complete" if len(completed) == len(_WF["steps"]) else "awaiting-next-step", failure=None, local_error=None, recovery_status="not-evaluated", recovery=None))
`;
