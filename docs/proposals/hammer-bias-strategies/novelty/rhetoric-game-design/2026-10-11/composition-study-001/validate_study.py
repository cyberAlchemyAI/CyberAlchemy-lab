"""Validate paper-study artifacts; does not execute gameplay or assess originality."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p / '.git').exists())
checks = []


def check(name, condition, details=None):
    checks.append({'name': name, 'passed': bool(condition), 'details': details})


def read(name):
    return json.loads((ROOT / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pointer(document, value):
    for part in value.lstrip('/').split('/') if value else []:
        part = part.replace('~1', '/').replace('~0', '~')
        document = document[int(part)] if isinstance(document, list) else document[part]
    return document


if __name__ == '__main__':
    parsed = {}
    errors = []
    for path in ROOT.glob('*.json'):
        try:
            parsed[path.name] = json.loads(path.read_text())
        except Exception as exc:
            errors.append({'file': path.name, 'error': str(exc)})
    check('study_json_parses', not errors, {'count': len(parsed), 'errors': errors})

    evidence_errors = []
    evidence_seen = set()

    def inspect_evidence(node):
        if isinstance(node, dict):
            artifact = node.get('artifact')
            ref = node.get('json_pointer')
            lines = node.get('lines')
            if isinstance(artifact, str) and (ref is not None or lines is not None):
                target = ROOT / artifact
                identity = (artifact, str(ref if ref is not None else lines))
                if identity not in evidence_seen:
                    evidence_seen.add(identity)
                    try:
                        if ref is not None:
                            pointer(json.loads(target.read_text()), ref)
                        elif isinstance(lines, list) and len(lines) == 2:
                            assert 1 <= lines[0] <= lines[1] <= len(target.read_text().splitlines())
                    except Exception as exc:
                        evidence_errors.append({'artifact': artifact, 'reference': ref or lines, 'error': str(exc)})
            for value in node.values():
                inspect_evidence(value)
        elif isinstance(node, list):
            for value in node:
                inspect_evidence(value)

    for document in parsed.values():
        inspect_evidence(document)
    check('exact_json_and_line_evidence_references_resolve', not evidence_errors, {'unique_references': len(evidence_seen), 'failures': evidence_errors})

    frozen = read('AUDIT-INPUT-HASHES.json')['hashes']
    failures = [n for n, h in frozen.items() if sha(ROOT / n) != h]
    check('fourteen_frozen_inputs_preserved', len(frozen) == 14 and not failures, failures)
    baseline = read('BASELINE-HASHES.json')
    failures = [n for n, h in baseline.items() if sha(ROOT.parent / n) != h]
    check('twenty_nine_historical_files_preserved', len(baseline) == 29 and not failures, failures)
    report = REPO / 'docs/proposals/hammer-bias-strategies/RESEARCH-REPORT.md'
    body = report.read_bytes().split(b'\n## 1. Problem and research questions\n', 1)[1]
    body = b'\n## 1. Problem and research questions\n' + body
    digest = hashlib.sha256(body[:199147]).hexdigest()
    check('main_report_sections_one_to_eighteen_preserved', digest == 'edbc6afa01ad9c83ee6db9c292706b35744299da07811f53bf2d2b3bd793ef72', digest)

    state = read('STATE.json')
    trace = read('DISTILL-TRACE.json')
    check('twelve_actual_role_turns', state['actual_completed_agent_turns'] == 12 and state['actual_completed_distill_agent_turns'] == 9 and state['actual_robot_talks_agent_turns'] == 3, '9 Distill including G0; 3 Robot Talks; parent synthesis excluded')
    check('three_conversations_per_composition', set(trace['per_composition_conversations_completed'].values()) == {3} and len(trace['per_composition_conversations_completed']) == 6)
    auth = read('AUTHORIZATION-ROBOT-TALKS-DISPOSITIONS.json')
    check('six_direct_human_dispositions_bound', auth['accepted_ids'] == ['S01', 'S02', 'S03', 'S04', 'S05', 'S06'])
    findings = [read('ROBOT-TALKS-' + role + '.json')['findings'] for role in ['RULES', 'AUTHORSHIP', 'INTERPRETATION']]
    check('fifteen_actual_robot_talks_findings', [len(x) for x in findings] == [5, 5, 5])
    pool = read('GENERATION-POOL.json')['variants']
    check('eighteen_initial_drafts_retained', len(pool) == 18)
    check('nine_completed_distill_turn_receipts', len(state['actual_agent_turns_dispatched']) == 9 and all('completed' in x['task_status_at_last_observation'] for x in state['actual_agent_turns_dispatched']))

    rows = trace['normalized_technique_receipts']
    required = {'technique_id', 'hook', 'activation', 'trigger_summary', 'inspected_state', 'emitted_output', 'decision', 'readiness_effect', 'source_file'}
    check('eighty_eight_normalized_technique_receipts', len(rows) == 88 and all(required <= set(x) for x in rows))
    packs = {}
    for row in rows:
        packs.setdefault(row['source_file'], []).append(row['technique_id'])
    check('eight_eleven_technique_role_packs', len(packs) == 8 and all(len(v) == len(set(v)) == 11 for v in packs.values()), {k: len(v) for k, v in packs.items()})

    contracts = read('CANDIDATES-R3.json')['candidates']
    check('six_final_contracts_with_six_authored_rules', len(contracts) == 6 and all(len(x['manual_auto']['policy_rules']) == 6 for x in contracts))
    for critique, reconciliation in [('BALANCER-R1-PRE.json', 'RECONCILIATION-R1-PRE.json'), ('BALANCER-R1-POST.json', 'RECONCILIATION-R1-POST.json'), ('BALANCER-R2.json', 'RECONCILIATION-R2.json'), ('BALANCER-R3.json', 'RECONCILIATION-R3.json')]:
        objection_ids = {x.get('id', x.get('objection_id')) for x in read(critique)['objections']}
        dispositions = {x['objection_id'] for x in read(reconciliation)['dispositions']}
        check('every_objection_reconciled_' + critique, objection_ids == dispositions, {'objections': len(objection_ids), 'dispositions': len(dispositions)})
    final = read('RECONCILIATION-R3.json')['prior_round_dispositions']
    check('five_final_repairs_have_scoped_dispositions', {x['objection_id'] for x in final} == {'R2B01', 'R2B02', 'R2B03', 'R2B04', 'R2B05'} and all(x['closed'] for x in final))
    independent = read('BALANCER-R3.json')
    check('final_independent_flags_preserved', independent['overall_verdict'] == 'flag' and all(x['independent_verdict'] == 'flag' for x in independent['reviewed_candidates']))
    check('original_finite_cap_fires', state['cycle_guard']['fires'] and state['cycle_guard']['remaining_rounds'] == 0)

    initial = read('SOURCES.json')
    followup = read('SOURCES-R1-FOLLOWUP.json')
    ability = read('SOURCES-ABILITY-FOLLOWUP.json')
    games = initial['games'] + followup['games']
    source_count = sum(len(x['sources']) for x in games) + len(ability['sources'])
    check('twenty_five_game_entries_twenty_eight_source_records', len(games) == 25 and source_count == 28, {'game_entries': len(games), 'source_records': source_count})
    check('no_gameplay_or_simulations_claimed', state['actual_gameplay_tests'] == state['actual_simulations'] == 0)

    bad_links = []
    total_links = 0
    session = REPO / 'claude/current_conversations/2026-10-11-0649-mechanic-compositions-001.md'
    for path in list(ROOT.glob('*.md')) + [report, session]:
        for target in re.findall(r'\]\(([^\n)]+)\)', path.read_text()):
            if target.startswith(('https://', 'http://', '#', 'codex:', 'app:', 'mailto:')):
                continue
            target = target.strip('<>').split('#')[0]
            target = re.sub(r':\d+$', '', target)
            if not target:
                continue
            total_links += 1
            if not (path.parent / target).exists():
                bad_links.append({'file': str(path.relative_to(REPO)), 'target': target})
    check('local_markdown_targets_exist', not bad_links, {'count': total_links, 'failures': bad_links})

    result = {'schema_version': 'mechanic-composition-artifact-validation.v3', 'recorded_at_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'Final paper research; syntax, evidence trace, counts, preservation and links only', 'passed': all(x['passed'] for x in checks), 'checks': checks, 'claim_ceiling': 'No gameplay, feasibility, method superiority, player learning or worldwide novelty established.'}
    (ROOT / 'ARTIFACT-CHECKS.v3.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failures': [x for x in checks if not x['passed']]}, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
