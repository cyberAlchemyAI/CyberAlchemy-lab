"""Independent byte/terminal/metadata scope audit of selected source successors."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
AUTH = HERE.parent / 'session-authority-v2'
PARENT = HERE.parent / 'session-authority-v1/receipts/R03-0010.json'
PINS = {HERE: '44b04e0e61f5b05feb9b1f334f0afb23a4d9e27885eb1b9e2fac8d40919a990c',
    AUTH: '38ae505ed27215deef43f2dadb404aa430560b61e7ce6e897394f1a5c2a904b6'}


def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(path): return json.loads(path.read_bytes())


def main():
    checks = []
    def check(value, label):
        if not value: raise ValueError(label)
        checks.append({'test': label, 'result': 'PASS'})
    check(sha(PARENT.read_bytes()) == '1460903a840ae502e664db5b3dc2e0cf3c2bb7beb39193ac3db814b801c221ca', 'predecessor partial proof pin')
    for b in load(PARENT)['files']:
        p = ROOT / b['path'];check(p.is_file() and not p.is_symlink() and sha(p.read_bytes()) == b['sha256'], 'retained exact predecessor ' + b['path'])
    for package, pin in PINS.items():
        check(sha((package / 'source-manifest.json').read_bytes()) == pin, 'selected successor manifest ' + package.name)
        for b in load(package / 'source-manifest.json')['files']:
            p = ROOT / b['path'];check(p.is_file() and not p.is_symlink() and sha(p.read_bytes()) == b['sha256'], 'exact successor source ' + b['path'])
    check(importlib.metadata.version('jsonschema') == '4.23.0', 'selected R02 validator environment')
    for package, expected in [(AUTH, 90), (HERE, 33)]:
        result = load(package / 'receipts/tests-result.json');terminal = load(package / 'receipts/tests-tool-terminal.json')
        log = (package / 'receipts/tests.stderr').read_text()
        check(result['result'] == 'PASS' and result['tests_run'] == result['expected_tests'] == expected
            and result['failures'] == result['errors'] == 0 and terminal['exit_code'] == 0, 'complete actual test terminal ' + package.name)
        check(len(re.findall(r'^test_\S+ .* \.\.\. ok$', log, re.M)) == expected
            and re.search(r'Ran ' + str(expected) + r' tests.*\n\nOK\n', log), 'complete selected transcript ' + package.name)
    check(load(AUTH / 'receipts/tests-result.json')['unchanged_predecessor_tests'] == 74, 'all original preflight regressions retained')
    process = load(HERE / 'receipts/processes/0001/result.json')
    terminal = load(HERE / 'receipts/processes/0001/tool-terminal.json')
    check(process['result'] == 'PASS' and process['actual_terminal_processes'] == 3 and terminal['exit_code'] == 0, 'actual complete process proof')
    children = process['children'];check(len(children) == 3 and all(c['exit_code'] == 0 for c in children), 'all three child terminal exits')
    reports = []
    for child in children:
        for name in ['stdout_binding', 'stderr_binding']:
            b = child[name];check(sha((ROOT / b['path']).read_bytes()) == b['sha256'], 'original child observation ' + child['name'] + ' ' + name)
        report = load(ROOT / child['stdout_binding']['path']);reports.append(report)
        check(report['accounted_subjects'] == len(report['dispositions']), 'complete source accounting ' + child['name'])
        check(report['included_current_instances'] == sum(report['carrier_counts'].values()), 'complete included-carrier accounting ' + child['name'])
        check(not report['fresh_Session_participation_established'] and not report['native_domain_mapping_supplied']
            and not report['context_or_ontology_views_generated'] and report['authority_effect'] == 'none'
            and report['actual_owner_outcome'] is None, 'operational gaps remain explicit ' + child['name'])
        check('session_memory' not in json.dumps(report) and 'working_record_refs' not in json.dumps(report), 'no protected memory exported ' + child['name'])
    check(reports[0] == reports[1], 'independent same-cut cold metadata parity')
    check(reports[0]['source_cut'] != reports[2]['source_cut'], 'distinct signed branch cuts preserved')
    current = reports[0]
    check(set(current['missing_current_carriers']) == {'cal.artifact-type.goal/v1', 'cal.artifact-type.coordination-context/v2'}, 'actual missing current Goal/Coordination Context')
    check(current['carrier_counts']['cal.artifact-type.project-state/v2'] == 1, 'current corrected-branch Project State is not replaced by C12')
    check(len(current['instance_bound_assignments']) == 1 and current['instance_bound_assignments'][0]['eligible_ref'] == 'agent-instance:first-governed-agent-episode:2026-10-06', 'old Assignment is not fresh participation')
    products = [row for row in current['dispositions'] if row.get('artifact', {}).get('carrier_ref') == 'cal.artifact-type.product-identity/v2']
    check(len(products) == 1 and products[0]['artifact']['version_ref'] == 'product:cyberalchemy-lab@foundation.1'
        and products[0]['original_body_version'] == '2.0.0-foundation.1'
        and products[0]['version_binding_rule'] == 'verified-source-revision', 'Product source revision and body version both retained')
    for version in ['operator-context-v1', 'operator-context-v2', 'operator-context-v3']:
        failures = list((HERE.parent / version / 'receipts/attempts').glob('*/terminal.json'))
        check(failures and all(load(p)['exit_code'] == 1 and load(p)['selected'] is False for p in failures), 'failed predecessor observations retained ' + version)
    output = HERE / 'receipts/audit-result.json'
    if output.exists(): raise ValueError('audit output already exists')
    value = {'schema_version': 'lab-same-cut-independent-audit/v1-candidate', 'result': 'PASS', 'checks': checks,
        'checks_count': len(checks), 'public_API_operations_added': 0, 'active_Agents_created': 0,
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'claim_ceiling': 'Exact candidate source/participation successor observations only; no new public API, fresh Agent, native mapping, admission or complete plan.'}
    output.write_text(json.dumps(value, indent=2) + '\n');print(json.dumps({'result': 'PASS', 'checks': len(checks)}), flush=True)


if __name__ == '__main__': main()
