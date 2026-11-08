"""Validate this proposed review package without changing accepted evidence."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'docs/plans/relational-theorem-checker/PLAN-SOURCE.json').is_file())


def read(path):
    return json.loads(path.read_text())


def check(binding):
    relative = Path(binding['path'])
    assert not relative.is_absolute() and '..' not in relative.parts
    path = (ROOT / relative).resolve()
    assert path.is_relative_to(ROOT) and path.is_file(), str(path)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == binding['sha256'], str(path)


def validate():
    plan = read(HERE / 'plan.json')
    assert plan['status'] == 'proposed-not-executed' and plan['first_step'] == 'H00'
    assert plan['authority_effect'] == 'none' and not plan['application_authorized']
    check(plan['original_plan'])
    ids = {t['id'] for t in plan['tasks']}
    assert len(ids) == len(plan['tasks']) == 21
    pending = {t['id']: set(t['depends_on']) for t in plan['tasks']}
    assert all(t['status'] == 'proposed' for t in plan['tasks'])
    assert all(deps <= ids for deps in pending.values())
    assert [key for key, deps in pending.items() if not deps] == ['H00']
    ordered = []
    while pending:
        ready = sorted(key for key, deps in pending.items() if not deps)
        assert ready, 'dependency cycle'
        ordered.extend(ready)
        for key in ready:
            del pending[key]
        for deps in pending.values():
            deps.difference_update(ready)
    for edge in plan['optional_edges']:
        assert edge['from'] in ids and edge['to'] in ids
        assert ordered.index(edge['from']) < ordered.index(edge['to'])
    current = read(ROOT / plan['original_plan']['path'])
    assert [(t['id'], t['status']) for t in current['tasks'] if t['id'] in {'R06', 'G4'}] == [
        ('R06', 'not-started'), ('G4', 'not-started')]
    context = read(HERE / 'context-pack.json')
    assert context['strict_coverage'] == 'pass' and len(context['selected_sources']) == 14
    covered = set()
    for row in context['selected_sources']:
        check(row['binding'])
        covered.update(row['obligation_refs'])
    assert covered == {o['id'] for o in context['obligations']}
    link_count = 0
    for name in ['REVIEW.md', 'PLAN.md', 'context-pack.md']:
        text = (HERE / name).read_text()
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
            if target.startswith(('https://', 'http://', '#')):
                continue
            path = Path(target)
            assert path.is_absolute() and path.is_file(), target
            link_count += 1
    assert all(t['id'] in (HERE / 'PLAN.md').read_text() for t in plan['tasks'])
    for e in range(7):
        assert '## E0' + str(e) in (HERE / 'REVIEW.md').read_text()
    completion = read(HERE.parents[1] / 'completion.json')
    # The earlier audit invocation's report is preserved byte-for-byte at its
    # bound path; its fresh result is stored separately in this review.
    def check_prior_audit(value):
        if isinstance(value, dict):
            if isinstance(value.get('path'), str) and value['path'].endswith('/complete-plan-audit.json'):
                check(value)
            for nested in value.values():
                check_prior_audit(nested)
        elif isinstance(value, list):
            for nested in value:
                check_prior_audit(nested)
    check_prior_audit(completion)
    return {'result': 'pass', 'proposed_tasks': len(ids), 'mandatory_edges': sum(len(t['depends_on']) for t in plan['tasks']),
            'optional_edges': len(plan['optional_edges']), 'context_sources': 14,
            'checked_local_links': link_count, 'original_gates': 'pending-unchanged',
            'prior_completion_audit_binding': 'current', 'authority_effect': 'none'}


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
