"""Independent whole-source orchestration observer for the selected Python form.

Dynamic program/type/import/recovery expectations derive from checked inputs.
Settlement mechanics are bound to a reviewed AST digest and independently tested
by the R01 native metadata matrix. A digest pin is custody, not a semantic proof.
No target module or TypeScript renderer is imported by this observer.
"""
import ast
import hashlib
import importlib.util
import json
import pathlib
import sys

spec = importlib.util.spec_from_file_location('material_observer', pathlib.Path(__file__).with_name('python-workflow-materialization-observer.py'))
material = importlib.util.module_from_spec(spec)
spec.loader.exec_module(material)
base = material.base


def require(ok, why):
    if not ok:
        raise ValueError('PYTHON_WORKFLOW_OBSERVER:' + why)


def canonical(v):
    if isinstance(v, dict):
        return '{' + ','.join(canonical(k) + ':' + canonical(v[k]) for k in sorted(v, key=lambda s: s.encode('utf-16-be', 'surrogatepass'))) + '}'
    if isinstance(v, list):
        return '[' + ','.join(map(canonical, v)) + ']'
    if isinstance(v, str):
        s = json.dumps(v.encode('utf-16-le', 'surrogatepass').decode('utf-16-le', 'surrogatepass'), ensure_ascii=False)
        return ''.join('\\u%04x' % ord(c) if 0xd800 <= ord(c) <= 0xdfff else c for c in s)
    return json.dumps(v, separators=(',', ':'))


def digest(v):
    return hashlib.sha256(canonical(v).encode()).hexdigest()


def prefixes(w, policy):
    result = []
    for count in range(len(w['steps'])):
        completed = {s['step_id']: i for i, s in enumerate(w['steps'][:count])}
        pending = {c['compensation_id']: c for c in w['compensations'] if c['for_step'] in completed}
        active, emitted, ordered = set(pending), set(), []
        while pending:
            ready = [c for c in pending.values() if set(c['depends_on']) & active <= emitted]
            require(bool(ready), 'cyclic selected compensation graph')
            c = max(ready, key=lambda c: completed[c['for_step']])
            row = {k: c[k] for k in ('compensation_id', 'for_step', 'operation_ref', 'action_sha256')}
            row.update(depends_on=sorted(set(c['depends_on']) & active), inactive_dependencies=sorted(set(c['depends_on']) - active))
            row.update({k: c[k] for k in ('arguments', 'events', 'failure_continuation')})
            ordered.append(row)
            emitted.add(c['compensation_id'])
            del pending[c['compensation_id']]
        result.append(dict(steps=[{k: s[k] for k in ('step_id', 'operation_ref', 'action_sha256')} for s in w['steps'][:count]], plan=ordered, plan_digest=digest(dict(schema_version='domainspec.workflow-recovery-plan/v3-candidate', policy_sha256=policy, plan=ordered)) if ordered else None))
    return result


def metadata(w):
    c = base.Context(None, '', '')
    def shape(name, fields, optional=()):
        return c.shape(name, [(k, v, v, k in optional) for k, v in fields.items()])[1]
    none, evidence, unperformed = '_Literal["none"]', '_Literal["caller-supplied"]', '_Literal["not-performed"]'
    shape('_Settlement', dict(commit_status='_Literal["committed", "not-committed", "indeterminate"]', origin='_Literal["returned", "invalid-return", "threw", "not-started"]', status='_Literal["committed", "failed", "rejected", "indeterminate"] | None', stage='str | None', code='str | None', continuation='str | None', cleanup_failed='bool | None', result_validation=unperformed))
    shape('_Observation', dict(schema_version='_Literal["domainspec.workflow-step-observation/v1-candidate"]', contract_sha256='str', workflow_sha256='str', step_id='str', operation_ref='str', action_sha256='str', settlement='_Settlement', evidence=evidence, authority_effect=none, observation_sha256='str'))
    shape('_FailureJournal', dict(schema_version='_Literal["domainspec.workflow-failure-journal/v1-candidate"]', workflow_execution_id='str', failure_occurrence_id='str', completed_step_ids='tuple[str, ...]', failed_step_id='str', failed_commit_status='_Literal["not-committed", "indeterminate"]'))
    shape('_RecoveryRow', dict(compensation_id='str', for_step='str', operation_ref='str', action_sha256='str', depends_on='tuple[str, ...]', inactive_dependencies='tuple[str, ...]', arguments='tuple[object, ...]', events='tuple[object, ...]', failure_continuation='str', invocation_identity='str'))
    shape('_RecoveryIntent', dict(schema_version='_Literal["domainspec.workflow-recovery-intent/v3-candidate"]', workflow_selector='str', workflow_sha256='str', policy_sha256='str', workflow_execution_id='str', failure_occurrence_id='str', failed_step_id='str', completed_step_journal_digest='str', plan_digest='str', intent_id='str', semantic_status='_Literal["required"]', plan='tuple[_RecoveryRow, ...]'))
    shape('_RecoveryEvaluation', dict(schema_version='_Literal["domainspec.workflow-recovery-evaluation/v1-candidate"]', workflow_sha256='str', policy_sha256='str', journal='_FailureJournal', journal_sha256='str', commit_evidence=evidence, intent_registration=unperformed, compensation_execution='_Literal[False]', authority_effect=none, status='_Literal["evaluated", "reconciliation-required"]', workflow_evaluation_result='_Literal["not-required", "recovery-required"] | None', recovery_intent='_RecoveryIntent | None', unknown_step_id='str'), ['unknown_step_id'])
    shape('WorkflowEvaluation', dict(schema_version='_Literal["domainspec.workflow-outcome-evaluation/v1-candidate"]', workflow_sha256='str', policy_sha256='str', workflow_execution_id='str', failure_occurrence_id='str | None', completed_step_ids='tuple[str, ...]', observations='tuple[_Observation, ...]', evidence=evidence, result_validation=unperformed, execution=unperformed, authority_effect=none, status='_Literal["forward-stopped", "orchestration-error", "forward-complete", "awaiting-next-step"]', failure='_Settlement | None', local_error='_Literal["committed-result-invalid", "result-materialization-failed"] | None', recovery_status='_Literal["evaluated", "reconciliation-required", "not-evaluable", "not-evaluated"]', recovery='_RecoveryEvaluation | None'))
    bindings = []
    for i, row in enumerate(w['compensations']):
        bindings.append(shape('_Binding' + str(i), dict(intent_id='str', plan_digest='str', invocation_identity='str', compensation_id='_Literal[' + repr(row['compensation_id']) + ']', operation_ref='_Literal[' + repr(row['operation_ref']) + ']', action_sha256='_Literal[' + repr(row['action_sha256']) + ']', arguments='_material._Arguments' + str(len(w['steps']) + i))))
    shape('RecoveryBindings', dict(schema_version='_Literal["domainspec.workflow-recovery-bindings/v1-candidate"]', intent_id='str', plan_digest='str', bindings='tuple[' + (' | '.join(bindings) or '_Never') + ', ...]', compensation_execution='_Literal[False]', authority_effect=none))
    return '\n'.join(c.shapes)


SETTLEMENT_NAMES = ['_fail', '_own', '_text', '_identity', '_freeze', '_canonical', '_digest', '_unknown', '_not_started', '_operation_data', '_settlement', '_imported', '_observe', '_recover', '_evaluate']
# Identity-only outcome type checks: qualified by the active-metaclass red/green
# regression as well as the existing independent R01 metadata matrix.
SETTLEMENT_AST_SHA256 = 'e6d629443abb1ec345d7604243afa9c751891618edf5078801e1c11b2f01609a'


def expected(w, policy, path, imports):
    package, name = path.rsplit('.', 1)
    source = f'''from __future__ import annotations
from asyncio import CancelledError as _CancelledError
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from typing import Literal as _Literal, Never as _Never, NotRequired as _NotRequired, Protocol as _Protocol, TypedDict as _TypedDict, overload as _overload, cast as _cast, get_args as _get_args
from hashlib import sha256 as _sha256
from json import dumps as _json_dumps
from re import fullmatch as _fullmatch
from {package} import {name} as _material
from {path} import WorkflowInput, WorkflowValue
'''
    for i, r in enumerate(imports):
        source += f'from {r["module"]} import {r["symbol"]} as _forward{i}, _BoundOperation as _Operation{i}, OperationOutcome as _Outcome{i}, OperationDependencies as _Dependencies{i}\n'
    source += metadata(w)
    deps = ', '.join(repr(r['selector']) + ': _Dependencies' + str(i) for i, r in enumerate(imports))
    wf = dict(hash=w['workflow_sha256'], selector=w['bindings']['selector'], steps=[{k: s[k] for k in ('step_id', 'operation_ref', 'action_sha256')} for s in w['steps']])
    source += f'''
WorkflowIdentity = _TypedDict("WorkflowIdentity", {{"workflow_execution_id": str, "failure_occurrence_id": str}})
WorkflowDependencies = _TypedDict("WorkflowDependencies", {{{deps}}})
@_dataclass(frozen=True, slots=True)
class WorkflowSuccess:
    status: _Literal["succeeded"]
    value: WorkflowValue
    evaluation: WorkflowEvaluation
    recovery_bindings: None = None
@_dataclass(frozen=True, slots=True)
class WorkflowStopped:
    status: _Literal["forward-stopped", "orchestration-error"]
    evaluation: WorkflowEvaluation
    bindings_status: _Literal["ready", "not-required", "not-evaluable", "failed"]
    recovery_bindings: RecoveryBindings | None
WorkflowOutcome = WorkflowSuccess | WorkflowStopped
_WF = {material.freeze(wf)}
_POLICY = {policy!r}
_OUTCOME_CONTRACT = "0a7cb5a92bbec1bc5003dd5a6ba70ebc184a8316ad617f2a362b5d9de82ba607"
_PREFIXES = {material.freeze(prefixes(w, policy))}
__reviewed_settlement_placeholder__ = None
def _prepare_bindings(input, results, intent):
    bindings = []
    for row in intent["plan"]:
'''
    for c in w['compensations']:
        source += f'''        if row["compensation_id"] == {c['compensation_id']!r}:
            if row["operation_ref"] != {c['operation_ref']!r} or row["action_sha256"] != {c['action_sha256']!r}:
                _fail("compensation identity")
            bindings.append(dict(intent_id=intent["intent_id"], plan_digest=intent["plan_digest"], invocation_identity=row["invocation_identity"], compensation_id={c['compensation_id']!r}, operation_ref={c['operation_ref']!r}, action_sha256={c['action_sha256']!r}, arguments=_material.compensations[{c['compensation_id']!r}].arguments(input, results)))
            continue
'''
    source += '''        _fail("unknown compensation")
    return _freeze(dict(schema_version="domainspec.workflow-recovery-bindings/v1-candidate", intent_id=intent["intent_id"], plan_digest=intent["plan_digest"], bindings=bindings, compensation_execution=False, authority_effect="none"))
def _stopped(input, results, observations, ids, local_error=None):
    evaluation = _evaluate(observations, ids, local_error)
    recovery = evaluation["recovery"]
    intent = recovery["recovery_intent"] if recovery else None
    if intent is None:
        return WorkflowStopped("orchestration-error" if local_error else "forward-stopped", evaluation, "not-required" if recovery and recovery["workflow_evaluation_result"] == "not-required" else "not-evaluable", None)
    try:
        return WorkflowStopped("forward-stopped", evaluation, "ready", _prepare_bindings(input, results, intent))
    except (Exception, _CancelledError):
        return WorkflowStopped("forward-stopped", evaluation, "failed", None)
async def execute(parameters: WorkflowInput, execution_identity: WorkflowIdentity, dependencies: WorkflowDependencies) -> WorkflowOutcome:
    e = _own(execution_identity, ("workflow_execution_id", "failure_occurrence_id"))
    ids = _MappingProxyType({"workflow_execution_id": _identity(e["workflow_execution_id"]), "failure_occurrence_id": _identity(e["failure_occurrence_id"])})
    input = _material.capture(parameters)
'''
    source += '    d = _own(dependencies, ' + repr(tuple(r['selector'] for r in imports)) + ')\n'
    for i, r in enumerate(imports):
        source += f'''    call{i} = _forward{i}
    _imported(call{i}, _Operation{i}, {r['selector']!r}, {r['action_sha256']!r}, {r['descriptor_sha256']!r})
    dep{i} = d[{r['selector']!r}]
    outcomes{i} = _get_args(_Outcome{i})
'''
    source += '    results = []\n    observations = []\n'
    for n, s in enumerate(w['steps']):
        i = next(i for i, r in enumerate(imports) if r['selector'] == s['operation_ref'])
        source += f'''    try:
        args{n} = _material.steps[{s['step_id']!r}].operation_input(input, results)
    except (Exception, _CancelledError):
        observations.append(_observe({n}, _not_started()))
        return _stopped(input, results, observations, ids)
    try:
        raw{n} = await call{i}(args{n}, dep{i})
    except (Exception, _CancelledError):
        observations.append(_observe({n}, _unknown("threw")))
        return _stopped(input, results, observations, ids)
    settlement{n} = _settlement(raw{n}, {s['failure_continuation']!r}, outcomes{i})
    observations.append(_observe({n}, settlement{n}))
    if settlement{n}["commit_status"] != "committed":
        return _stopped(input, results, observations, ids)
    try:
        results.append(_material.capture_result(input, {s['step_id']!r}, _operation_data(raw{n}, outcomes{i})["value"]))
    except (Exception, _CancelledError):
        return _stopped(input, results, observations, ids, "committed-result-invalid")
'''
    source += '''    try:
        value = _material.result(input, results)
    except (Exception, _CancelledError):
        return _stopped(input, results, observations, ids, "result-materialization-failed")
    return WorkflowSuccess("succeeded", value, _evaluate(observations, ids, None))
'''
    return ast.parse(source)


def observe(data):
    p, w = data['plan'], data['workflow']
    require(len(p['modules']) == 1, 'Workflow module count')
    m, ops = p['modules'][0], p['operation_plan']
    root = p['materialization']['module_root']
    feature, node = w['bindings']['selector'].split(':')
    path = root + '/features/' + feature.replace('-', '_') + '/src/application/workflows/' + node.replace('-', '_') + '.py'
    provider = path.rsplit('/', 1)[0] + '/_providers/' + path.rsplit('/', 1)[1]
    require(m['relative_path'] == path and m['provider_path'] == provider, 'Workflow paths')
    require(m['material_path'] == p['materialization']['relative_path'], 'materialization path')
    require(m['import_name'] == path[:-3].replace('/', '.') and m['callable'] == 'workflow_' + node.replace('-', '_'), 'public name')
    required = {s['operation_ref']: s['action_sha256'] for s in w['steps'] + w['compensations']}
    require(len(ops['modules']) == len(required) and {m['selector']: m['descriptor']['action_sha256'] for m in ops['modules']} == required, 'exact Operation closure')
    imports = []
    for i, selector in enumerate(sorted({s['operation_ref'] for s in w['steps']})):
        op = next(m for m in ops['modules'] if m['selector'] == selector)
        imports.append(dict(selector=selector, module=base.relative(provider, op['relative_path'][:-3]), symbol=op['callable'], local='_forward' + str(i), action_sha256=required[selector], descriptor_sha256=op['descriptor']['descriptor_sha256']))
    descriptor = m['descriptor']
    require(descriptor['operation_imports'] == imports, 'forward-only imported identities')
    target = pathlib.Path(data['root'])
    actual = ast.parse((target / provider).read_bytes())
    fixed = [n for n in actual.body if isinstance(n, ast.FunctionDef) and n.name in SETTLEMENT_NAMES]
    require([n.name for n in fixed] == SETTLEMENT_NAMES, 'settlement function closure')
    fixed_ast = ast.Module(body=fixed, type_ignores=[])
    require(hashlib.sha256(base.dump(fixed_ast).encode()).hexdigest() == SETTLEMENT_AST_SHA256, 'reviewed settlement AST changed')
    want = expected(w, p['selection']['policy']['policy_sha256'], base.relative(provider, m['material_path'][:-3]), imports)
    index = next(i for i, n in enumerate(want.body) if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == '__reviewed_settlement_placeholder__')
    want.body[index:index + 1] = fixed
    require(base.dump(actual) == base.dump(want), 'orchestration complete AST')
    body = dict(schema_version='domainspec.generated-python-workflow-descriptor/v1-candidate', protocol_id='python.bound-workflow/v1', form_id='python.workflow-step-orchestrator', primary_callable_count=1, selector=w['bindings']['selector'], workflow_sha256=w['workflow_sha256'], policy_sha256=p['selection']['policy']['policy_sha256'], contract_sha256='6b6da704b6478b66525e0b2b91240ab136fac0698ca04a57527c1f9b0c635aa2', material_sha256=p['materialization']['provider_sha256'], provider_sha256=hashlib.sha256((target / provider).read_bytes()).hexdigest(), operation_plan_sha256=ops['plan_sha256'], operation_imports=imports, compensation_execution=False, publication=False, authority_effect='none')
    require(descriptor == dict(body, descriptor_sha256=digest(body)), 'descriptor meaning/custody')
    wrapper = f'''from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from {base.relative(path, provider[:-3])} import execute as _execute, WorkflowInput, WorkflowValue, WorkflowIdentity, WorkflowDependencies, WorkflowOutcome, WorkflowEvaluation, RecoveryBindings
_DESCRIPTOR = {material.freeze(descriptor)}
@_dataclass(frozen=True, slots=True)
class _BoundWorkflow:
    @property
    def descriptor(self):
        return _DESCRIPTOR
    async def __call__(self, parameters: WorkflowInput, execution_identity: WorkflowIdentity, dependencies: WorkflowDependencies) -> WorkflowOutcome:
        return await _execute(parameters, execution_identity, dependencies)
{m['callable']} = _BoundWorkflow()
__all__ = [{m['callable']!r}, "WorkflowInput", "WorkflowValue", "WorkflowIdentity", "WorkflowDependencies", "WorkflowOutcome", "WorkflowEvaluation", "RecoveryBindings"]
'''
    require(base.dump(ast.parse((target / path).read_bytes())) == base.dump(ast.parse(wrapper)), 'public wrapper complete AST')
    material.observe(dict(data, plan=p['materialization']))
    operation_context = dict(data, module_root=root, actions={a['bindings']['selector']: a for a in ops['selection']['actions']}, rule_modules=ops['rule_plan']['modules'], event_modules=(ops.get('event_plan') or {}).get('modules', []))
    for op in ops['modules']:
        base.observe(operation_context, op)
    dependencies = {a['relative_path']: a['content'] for a in ops['artifacts'] + p['materialization']['artifacts']}
    paths = set(dependencies) | {provider, path}
    for file in list(paths):
        parts = file.split('/')
        paths.update('/'.join(parts[:i]) + '/__init__.py' for i in range(1, len(parts)))
    require(len(p['artifacts']) == len(paths) and {a['relative_path'] for a in p['artifacts']} == paths, 'complete artifact closure')
    for a in p['artifacts']:
        file = a['relative_path']
        content = (target / file).read_bytes()
        if file.endswith('/__init__.py'):
            require(not content, 'package initializer')
        if file in dependencies:
            require(content == dependencies[file].encode(), 'dependency-plan custody:' + file)
        require(content == a['content'].encode() and hashlib.sha256(content).hexdigest() == a['sha256'] and len(content) == a['size_bytes'], 'artifact custody:' + file)
    return dict(whole_source=True, prefixes=len(w['steps']), implicit_compensation_execution=False)


if __name__ == '__main__':
    print(json.dumps(observe(json.load(sys.stdin))))
