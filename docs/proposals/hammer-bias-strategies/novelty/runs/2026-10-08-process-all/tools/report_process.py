#!/usr/bin/env python3
"""Frozen deterministic stage summaries over locked model assessments."""
import collections
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
PRIMARY = {'P01': ['ordinary'], 'P03': ['resist'],
           'P04': ['ordinary', 'parent_a', 'parent_b'], 'P05': ['ordinary'],
           'P06': ['carrier'], 'P07': ['ordinary'], 'P02': ['critique']}


def families(data):
    value = data['families']
    return value if isinstance(value, dict) else {f['family_id']: f for f in value}


def raw_ready(unit):
    return unit.get('raw_execution_valid') is True and unit.get('raw_assessment_complete') is True


def qualified(row, family):
    return (row.get('intelligible') is True and row.get('novelty') == 'new'
            and row.get('usefulness') in [1, 2] and row.get('fit') == 'preserves'
            and row.get('observability') == 2 and row.get('support') != 'unsupported'
            and row.get('support') is not None and row.get('contract') == 'met'
            and row.get('raw_judgment_resolved', row.get('judgment_resolved')) is True
            and family.get('equivalence_status') == 'confirmed')


def family_pool(units):
    return {r['family_id'] for u in units for r in u['raw']
            if r.get('intelligible') is True and r.get('family_id') is not None}


def distinct(family_id, pool, metadata):
    connected = {family_id} | set(metadata[family_id].get('uncertain_equivalence_with', []))
    return not connected & pool


def main_case(data):
    metadata = families(data)
    results = {operator: [] for operator in PRIMARY}
    for unit in data['units']:
        operator = unit['condition']
        if operator not in PRIMARY:
            continue
        block = [u for u in data['units'] if u['repetition'] == unit['repetition']]
        primary = [u for u in block if u['condition'] in PRIMARY[operator]]
        controls = [u for u in block if u['condition'] in ['ordinary', 'creative']]
        primary_ok = len(primary) == len(PRIMARY[operator]) and all(raw_ready(u) for u in primary)
        controls_ok = len(controls) == 2 and all(raw_ready(u) for u in controls)
        prefix = 'Q' if operator == 'P02' else 'A'
        rows = [r for r in unit['raw'] if r['raw_id'].startswith(prefix)]
        eligible = {r['family_id'] for r in rows if r.get('family_id') in metadata
                    and qualified(r, metadata[r['family_id']])} if raw_ready(unit) else None
        primary_pool, control_pool = family_pool(primary), family_pool(controls)
        exclusive = ({f for f in eligible if distinct(f, primary_pool | control_pool, metadata)}
                     if eligible is not None and primary_ok and controls_ok else None)
        retained = ({r['family_id'] for r in rows if r.get('family_id') in (exclusive or set())
                     and r.get('retention') == 'retained'}
                    if exclusive is not None and unit.get('execution_valid') is True
                    and unit.get('post_assessment_complete') is True else None)
        results[operator].append({
            'case_id': data['case_id'], 'unit_id': unit['unit_id'], 'repetition': unit['repetition'],
            'raw_evaluable': raw_ready(unit), 'primary_exposure_complete': primary_ok,
            'generic_control_exposure_complete': controls_ok,
            'qualified_raw_families': sorted(eligible) if eligible is not None else None,
            'exclusive_raw_families': sorted(exclusive) if exclusive is not None else None,
            'exclusive_retained_families': sorted(retained) if retained is not None else None,
            'shared_Z_families': sorted((eligible or set()) & {
                r['family_id'] for r in unit['raw'] if r['raw_id'].startswith('Z')}),
            'contract_dispositions': dict(collections.Counter(r.get('contract') for r in rows)),
            'fit_dispositions': dict(collections.Counter(r.get('fit') for r in rows)),
            'unsupported_count': sum(r.get('support') == 'unsupported' for r in rows),
            'post_only_dispositions': unit['post_only'],
            'observed_output_words': unit.get('observed_output_words'),
            'output_words_valid_workflow': unit.get('output_words')})
    return results


def p08(data):
    rows = []
    for pair in data['pairs']:
        arms = []
        for arm in pair['arms']:
            qualified_probe = (arm.get('execution_valid') is True
                               and arm.get('judgment_resolved') is True
                               and arm.get('decision_relevant') is True
                               and arm.get('competing_predictions') is True
                               and arm.get('probe_feasible') == 'preserves'
                               and arm.get('fit') == 'preserves'
                               and arm.get('support') not in [None, 'unsupported']
                               and arm.get('distinct_question') is True)
            arms.append(dict(arm, qualified_discriminating_probe=qualified_probe))
        rows.append({'pair_id': pair['pair_id'], 'case_id': pair['case_id'], 'arms': arms,
                     'contrast_reviews': pair['contrast_reviews']})
    return {'strategy': 'P08', 'pairs': rows,
            'assessment_complete_by_arm': {method: sum(a.get('assessment_complete') is True
                for p in rows for a in p['arms'] if a['method'] == method)
                for method in ['consensus', 'P08']},
            'qualified_probes_by_arm': {method: sum(a['qualified_discriminating_probe']
                for p in rows for a in p['arms'] if a['method'] == method)
                for method in ['consensus', 'P08']},
            'scope': 'Fixed concern-report convergence step; no whole Robot Talks effect.'}


def p09(data):
    strata = {}
    for stratum in ['selected_historical_diagnostic', 'untouched_authored']:
        selected = [p for p in data['pairs'] if p['stratum'] == stratum]
        arms = {}
        for method in ['ordinary', 'P09']:
            selected_arms = [a for p in selected for a in p['arms'] if a['method'] == method]
            axes = {axis: dict(collections.Counter(r.get(axis) or 'unresolved'
                    for a in selected_arms for r in a['raw']))
                    for axis in ['causal_relation', 'discriminator', 'uncertainty']}
            arms[method] = {'attempts': len(selected_arms),
                            'execution_valid': sum(a.get('execution_valid') is True for a in selected_arms),
                            'axes': axes,
                            'unsupported_additions': (sum(x.get('presence') is True
                                for a in selected_arms for x in a['unsupported_additions'])
                                if all(a.get('assessment_complete') is True for a in selected_arms) else None),
                            'addition_presence_unresolved': sum(x.get('presence') is None
                                for a in selected_arms for x in a['unsupported_additions'])}
        strata[stratum] = {'pairs': len(selected), 'arms': arms}
    return {'strategy': 'P09', 'strata': strata, 'pairs': data['pairs'],
            'scope': 'Preservation of existing relations and uncertainty; not original invention.'}


def p10(data):
    results = {}
    for stratum in ['historical', 'fresh']:
        selected = [x for x in data['comparisons'] if x['stratum'] == stratum]
        complete = [x for x in selected if x['status'] == 'evaluable']
        changed = [x for x in complete if x.get('entering') is not None]
        results[stratum] = {'attempts': len(selected), 'evaluable': len(complete),
            'not_evaluable': len(selected) - len(complete), 'changed_second_slots': len(changed),
            'eligible_alternative_present': sum(x.get('alternative_found') is True for x in complete),
            'gate_causes': dict(collections.Counter(c for x in selected for c in x['gate_causes'])),
            'utility_displacement': [x['utility_displacement'] for x in changed],
            'entering_contracts': dict(collections.Counter(
                x['entering']['fixed_scores'].get('contract') or 'historical_unavailable'
                for x in changed)),
            'displaced_contracts': dict(collections.Counter(
                x['displaced']['fixed_scores'].get('contract') or 'historical_unavailable'
                for x in changed if x['displaced'])),
            'text_burden': [x['text_burden'] for x in changed]}
    return {'strategy': 'P10', 'strata': results,
            'scope': 'Presentation over locked assessments; exposure is partly rule-defined, human decision effects untested.'}


def build(root=R):
    root = Path(root)
    inputs = ['reports/main-S1-resolved.json', 'reports/main-S2-resolved.json',
              'reports/p08-resolved.json', 'reports/p09-resolved.json', 'reports/p10-all.json']
    data, active_sources = {}, {}
    for name in inputs:
        path = root / name
        value = json.loads(path.read_text())
        if value.get('status') == 'incomplete':
            gated = path.with_name(path.name.replace('-resolved.json', '-gated.json'))
            if gated.exists():
                value = json.loads(gated.read_text())
                path = gated
        data[name] = value
        active_sources[name] = path
    sources = [{'path': str(path.relative_to(root)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
               for path in active_sources.values()]
    generation = {key: [] for key in PRIMARY}
    for case in ['S1', 'S2']:
        assessed = data[f'reports/main-{case}-resolved.json']
        if len(assessed['units']) != 28:
            raise ValueError('Incomplete main assessment; preserve incomplete gate before generating report')
        for operator, rows in main_case(assessed).items():
            generation[operator].extend(rows)
    if any(len(rows) != 4 for rows in generation.values()):
        raise ValueError('All seven generation/construction interventions require four attempts')
    if len(data['reports/p08-resolved.json']['pairs']) != 4 or len(data['reports/p09-resolved.json']['pairs']) != 7:
        raise ValueError('Incomplete downstream assessment coverage')
    result = {'scope': 'P01-P10', 'sources': sources, 'generation': generation,
              'P08': p08(data['reports/p08-resolved.json']),
              'P09': p09(data['reports/p09-resolved.json']),
              'P10': p10(data['reports/p10-all.json']),
              'claim_ceiling': 'Case-local model distinctions, preservation and deterministic exposure, not global originality or field effects.'}
    with (root / 'reports/process-findings.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    return result


if __name__ == '__main__':
    result = build()
    print(json.dumps({'scope': result['scope'], 'generation_blocks': 28,
                      'P08_pairs': 4, 'P09_pairs': 7, 'P10': result['P10']['strata']}, indent=2))
