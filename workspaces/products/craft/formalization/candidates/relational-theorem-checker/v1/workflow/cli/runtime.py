"""Four-command local adapter over accepted independent checkers."""
from copy import deepcopy
from pathlib import Path
import argparse
import json
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'evidence'))
import aggregate as a
b = a.b; v = b.v; s = b.s; g = b.g; o = a.o; sem = a.sem
d = b.i.c.d; r = g.c.r
F0 = 'f0-three-kind/v1'
STRUCTURE = 'captured-registry-structure/v1'
COMMANDS = ['check-instance', 'check-extension', 'check-proof', 'replay-evidence']


def policy():
    return {'schema': 'relational.cli-policy/v1-candidate', 'commands': COMMANDS,
            'instance_profiles': [F0, STRUCTURE],
            'proposal_context': 'Explicit --proposal is required for proof and evidence replay; hashes do not reconstruct context.',
            'json': 'One UTF-8 JSON outcome on stdout; provider progress on stderr; strict bounded local inputs.',
            'ci': 'Fresh command execution plus independently complete current semantic readiness; single checks cannot authorize extension review.',
            'authority_effect': 'none'}


def read_input(path):
    path = Path(path).resolve()
    s.require(path.is_relative_to(s.ROOT) and path.is_file(), 'input must be an existing workspace file')
    binding = s.binding(path)
    _, raw = v.safe_binding(binding, limit=4 * 1024 * 1024)
    try:
        value = d.decode(raw)
    except RecursionError as error:
        raise ValueError('JSON parser depth limit exceeded') from error
    s.require(isinstance(value, dict), 'input must be a JSON object')
    return value, binding


def current_adapter():
    """Check current accepted exports and this adapter without binding mutable plan status."""
    paths = {HERE / name for name in ['runtime.py', 'cli', 'ci.py', 'ci-example', 'cli-policy.json']}
    for task_id in ['R01', 'R03']:
        task = s.task(task_id)
        s.require(task['status'] == 'accepted', 'CLI prerequisite not accepted: ' + task_id)
        receipt_binding = task['validation']['acceptance_ref']
        v.safe_binding(receipt_binding, limit=64 * 1024 * 1024)
        receipt_path = s.ROOT / receipt_binding['path']; paths.add(receipt_path)
        receipt = s.read(receipt_path)
        for item in receipt['artifacts'] + receipt['dependency_bindings']:
            v.safe_binding({'path': item['path'], 'sha256': item['sha256']}, limit=64 * 1024 * 1024)
            paths.add(s.ROOT / item['path'])
    s.require(s.read(HERE / 'cli-policy.json') == policy(), 'CLI policy changed')
    return [s.binding(p) for p in sorted(paths)]


def reference_diagnostics(report, graph, obligation, location='graph'):
    edges = {e['id']: e for e in graph['assertions']}
    actions = {
        'wrong-target-version': 'Set the exact-version qualifier to the literal target version, then recheck.',
        'undeclared-ordered-pair': 'Use an exact declared source/target type pair or submit a separately supported theory change.',
        'wrong-definition-version': 'Bind the exact captured relation-kind definition version.',
        'absent-evidence': 'Supply the referenced assessment with matching endpoints, scope and role.',
        'wrong-output-identity': 'Make the receipt, output qualifier and target content identities agree.',
        'wrong-evidence-scope': 'Use an assessment for the exact declared conformance scope.',
        'unaccepted-evidence': 'Supply independently justified accepted assessment evidence and rerun.',
        'invalid-qualifiers': 'Supply exactly the declared qualifier fields with nonempty string values.'}
    result = []
    for failure in report.get('errors', []):
        subject = failure['subject']; edge = edges.get(subject) if isinstance(subject, str) else None
        relation = edge['kind'] if edge else 'node/evidence inventory'
        detail = failure['detail']
        result.append(a.diagnostic(failure['code'], f'{relation} / {subject}: {detail}', obligation,
            f'{location}.assertions[{subject}]' if edge else location,
            actions.get(failure['code'], 'Correct the named identity, endpoint or assessment and rerun the check.')))
    return result


def enrich_extension(outcome, proposal):
    for row in outcome['results']:
        if row['obligation_id'].endswith(':selected-data-compatibility') and row['verdict'] == 'violated':
            report = r.resolve(proposal['after']['graph'], proposal['after']['registry'])
            details = reference_diagnostics(report, proposal['after']['graph'], row['obligation_id'], 'after.graph')
            row['diagnostics'].extend(details); outcome['diagnostics'].extend(details)
    for diag in outcome['diagnostics']:
        if diag['code'] == 'evidence-stale':
            diag['next_action'] = 'Recapture the proposal and complete evidence bundle from current source bytes; replay every hard obligation.'
        elif diag['code'] == 'unsupported-profile':
            diag['next_action'] = 'Select a documented supported change profile or formalize and review its missing preservation and conservativity obligations.'
    return outcome


def single_outcome(command, profile, request_binding, report, definition_paths, output,
                   diagnostics=None, baseline=None, proposal=None):
    execution = report.get('execution', 'completed')
    currentness = report.get('currentness', 'current')
    verdict = report['verdict']; method = report.get('evidence_method', 'none')
    oid = s.digest(s.ROOT / request_binding['path']) + (':instance-validity' if command == 'check-instance' else ':submitted-proof')
    # Proof rejection means invalid evidence for the required proposition, not its mathematical negation.
    statement = report.get('required_statement', 'Relational.Inv selected graph' if profile == F0 else 'Registry.Inv captured selected graph')
    if command == 'check-proof': oid = report.get('obligation_id', oid)
    evidence = output / 'verified-single-check.json'
    s.write(evidence, {'schema': 'relational.cli-single-evidence/v1-candidate', 'request': request_binding,
                      'command': command, 'profile': profile, 'detail': report, 'authority_effect': 'none'})
    row = {'obligation_id': oid, 'hard': True,
           'required_statement': {'id': statement, 'definition_bindings': [s.binding(p) for p in definition_paths]},
           'execution': execution, 'currentness': currentness, 'evidence_method': method,
           'verdict': verdict, 'evidence_refs': [s.binding(evidence)], 'diagnostics': diagnostics or []}
    doc = {'schema_version': 'relational.cli-outcome/v1-candidate', 'command': command, 'profile_id': profile,
           'baseline_identity': baseline, 'proposal_identity': proposal, 'execution': execution, 'currentness': currentness,
           'evidence': {'methods': [method], 'policy_identity': g.c.identity(policy()), 'trust_boundary': v.policy()['trust']},
           'results': [row], 'required_hard_obligation_ids': [oid], 'missing_hard_obligation_ids': [],
           'unresolved_hard_obligation_ids': [] if verdict == 'satisfied' else [oid], 'readiness': 'not-applicable',
           'compatibility_dimensions': {label: 'not-applicable' for label in o.DIMENSIONS},
           'diagnostics': diagnostics or [], 'authority_effect': 'none'}
    o.validate(doc, [oid]); return doc


def check_instance(request, binding, profile, output):
    if profile not in [F0, STRUCTURE]:
        diag = a.diagnostic('unsupported-profile', 'Instance meaning is outside supported profiles: ' + profile,
                            location='--profile', next_action='Select f0-three-kind/v1 or captured-registry-structure/v1.')
        return single_outcome('check-instance', profile, binding,
            {'verdict': 'unsupported', 'execution': 'not-run', 'currentness': 'unresolved'}, [HERE / 'runtime.py'], output, [diag])
    legacy = s.read(s.BASE / 'replay/dependency-manifest.json'); v.replay.verify(legacy)
    diagnostics = []
    with tempfile.TemporaryDirectory(prefix='cli-instance-') as temp:
        build = Path(temp)
        if profile == F0:
            normal = d.normalize(request); graph = r.from_decoder(json.dumps(request, ensure_ascii=False).encode())
            references = r.resolve(graph, s.read(s.BASE / 'registry/normalized-registry.json'))
            modules = s.compile_lean(build, d.core_modules()); detail = d.check(normal, build)
            for name in ['InputQuery', 'InputEvaluation']:
                (output / (name + '.lean')).write_bytes((build / (name + '.lean')).read_bytes())
            accepted = detail['accepted_result'] and references['status'] == 'supported'
            verdict = 'satisfied' if accepted else 'unsupported' if references['status'] == 'unsupported' else 'violated'
            definitions = [s.FORMAL / 'core/RelationalSemantics.lean', s.FORMAL / 'proofs/l0/CheckerSoundness.lean']
            detail.update(references=references, fresh_modules=modules,
                          generated_sources=[s.binding(output / (n + '.lean')) for n in ['InputQuery', 'InputEvaluation']])
        else:
            s.require(set(request) == {'schema_version', 'graph'} and
                      request['schema_version'] == 'relational-checker.registry-instance-input/v1-candidate', 'invalid registry instance envelope')
            graph = request['graph']; baseline = g.c.baseline()
            # Exact host shape validation. Normative findings are reported as outside this explicit structural profile.
            references = r.resolve(graph, baseline['registry'])
            accepted = sem.structural_graph_valid(baseline['registry'], graph)
            proposal = s.read(s.BASE / 'workflow/evidence/unchanged-proposal.json')
            proposal['after']['graph'] = deepcopy(graph)
            modules = sem.compile_registry(build, sem.p.captured_modules())
            modules += s.compile_lean(build, [('Preservation', s.BASE / 'evolution/preservation/Preservation.lean'),
                ('ConservativeExpansion', s.BASE / 'evolution/models/ConservativeExpansion.lean')])
            source = sem.registry_source(proposal)
            log = sem.compile_registry_generated(build, 'BundleRegistry', source)
            (output / 'RegistryInstance.lean').write_text(source)
            detail = {'accepted_result': accepted, 'fresh_modules': modules, 'evaluation': log,
                      'source': s.binding(output / 'RegistryInstance.lean'), 'normative_meanings': 'outside structural profile',
                      'reference_findings_not_used_as_structural_truth': references}
            verdict = 'satisfied' if accepted else 'violated'
            definitions = [s.BASE / 'registry/RegistryChecker.lean']
        oid = s.digest(s.ROOT / binding['path']) + ':instance-validity'
        if verdict != 'satisfied':
            diagnostics = reference_diagnostics(references, graph, oid)
            if not diagnostics: diagnostics = [a.diagnostic('instance-invalid', 'The selected graph violates the named invariant.', oid,
                'graph', 'Inspect assertion diagnostics, exact endpoint pairs and duplicate identities, then rerun.')]
    v.replay.verify(legacy)
    detail.update(verdict=verdict, evidence_method='verified-checker', execution='completed', currentness='current')
    return single_outcome('check-instance', profile, binding, detail, definitions, output, diagnostics,
                          baseline=legacy['dependency_identity'])


def check_proof(proposal, submission, binding, output):
    b.source_boundary(proposal); b.execution_profile(proposal)
    obligation, descriptor = v.selected(proposal, submission.get('obligation_id'))
    report = v.check(proposal, submission)
    report.update(obligation_id=obligation['id'], required_statement=descriptor[1])
    diagnostics = []
    if not report.get('accepted'):
        stale = 'stale' in report.get('diagnostic', '') or 'changed' in report.get('diagnostic', '')
        if stale: report['currentness'] = 'stale'
        code = 'evidence-stale' if stale else 'proof-rejected' if report['execution'] == 'completed' else 'proof-not-verified'
        diagnostics = [a.diagnostic(code, report.get('diagnostic', 'Proof did not pass the required statement audit.'),
            obligation['id'], 'submission.proof', 'Bind current dependencies and prove the exact required statement; rejection does not disprove the theorem.')]
    return single_outcome('check-proof', 'r02-isolated-exact-proof/v1', binding, report,
        [s.BASE / 'workflow/proof-verifier/verifier.py', s.BASE / 'workflow/proof-verifier/Verifier.lean'], output,
        diagnostics, proposal['baseline_identity'], g.c.identity(proposal))


class Parser(argparse.ArgumentParser):
    def error(self, message): raise ValueError(message)


def parser():
    p = Parser(description='Candidate relation checker; all results have authority_effect none.')
    commands = p.add_subparsers(dest='command', required=True)
    for name in COMMANDS:
        sub = commands.add_parser(name); sub.add_argument('input', type=Path)
        if name == 'check-instance': sub.add_argument('--profile', default=F0)
        if name in ['check-proof', 'replay-evidence']: sub.add_argument('--proposal', type=Path, required=True)
        if name == 'check-extension': sub.add_argument('--bundle', type=Path)
    return p


def invalid_outcome(command, error):
    # R03's invalid-input constructor is an extension outcome. Adapt command and
    # readiness together before validating the single-check contract.
    outcome = a.invalid_outcome('check-extension', error)
    outcome['command'] = command
    outcome['diagnostics'][0]['location'] = 'input/arguments'
    if command in ['check-instance', 'check-proof']:
        outcome['readiness'] = 'not-applicable'
        outcome['compatibility_dimensions'] = {label: 'not-applicable' for label in o.DIMENSIONS}
    o.validate(outcome, [])
    return outcome


def run(argv):
    command = argv[0] if argv and argv[0] in COMMANDS else 'check-extension'
    output = Path(tempfile.mkdtemp(prefix='check-', dir=ensure_runs()))
    inputs = []; before = None
    try:
        args = parser().parse_args(argv); command = args.command
        request, binding = read_input(args.input); inputs.append(binding)
        before = current_adapter()
        if command == 'check-instance': outcome = check_instance(request, binding, args.profile, output)
        elif command == 'check-extension':
            bundle = None
            if args.bundle:
                bundle, bound = read_input(args.bundle); inputs.append(bound)
            outcome = enrich_extension(a.verify(request, bundle), request)
        else:
            proposal, bound = read_input(args.proposal); inputs.append(bound)
            outcome = check_proof(proposal, request, binding, output) if command == 'check-proof' else enrich_extension(
                a.verify(proposal, request, command='replay-evidence'), proposal)
        for item in inputs: v.safe_binding(item, limit=4 * 1024 * 1024)
        s.require(current_adapter() == before, 'CLI dependencies changed during checking')
    except (ValueError, KeyError, TypeError, UnicodeError, g.c.jsonschema.ValidationError) as error:
        outcome = invalid_outcome(command, str(error))
        if 'stale' in str(error) or 'changed during' in str(error):
            outcome['diagnostics'][0]['code'] = 'evidence-stale'; outcome['currentness'] = 'stale'
            outcome['diagnostics'][0]['next_action'] = 'Recapture current source, request and verifier bindings and rerun.'
    except subprocess.TimeoutExpired:
        outcome = invalid_outcome(command, 'Checker exceeded its bounded execution budget; no verdict was established.')
        outcome['execution'] = 'timeout'; outcome['diagnostics'][0]['code'] = 'checker-timeout'
    except OSError:
        outcome = invalid_outcome(command, 'A required local file, toolchain or provider is unavailable.')
        outcome['execution'] = 'unavailable'; outcome['diagnostics'][0]['code'] = 'checker-unavailable'
    if command in ['check-instance', 'check-proof']: outcome['readiness'] = 'not-applicable'
    o.validate(outcome, outcome['required_hard_obligation_ids'])
    s.write(output / 'request-bindings.json', {'requests': inputs, 'adapter': before, 'authority_effect': 'none'})
    s.write(output / 'outcome.json', outcome)
    return outcome


def ensure_runs():
    path = HERE / 'runs'; path.mkdir(exist_ok=True); return path


def main():
    outcome = run(sys.argv[1:]); print(json.dumps(outcome, indent=2, ensure_ascii=False))
    return o.exit_code(outcome)


if __name__ == '__main__': raise SystemExit(main())
