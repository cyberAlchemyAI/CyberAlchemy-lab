#!/usr/bin/env python3
"""P10 deterministic presentation comparisons over immutable locked assessments.

compare_set expects unit-level execution_valid, assessment_complete,
judgments_locked and equivalence_review_locked flags. assessment_complete
attests exact dual-review coverage; unresolved individual scalars may remain.
The CLI inherits document locks without overriding a false unit-level lock.
Only explicit stratum='historical' permits unavailable historical support.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path


RAW_ORDER = {raw_id: i for i, raw_id in enumerate(('Z1', 'Z2', 'A1', 'A2', 'Q1', 'Q2'))}
FIT_ORDER = {fit: i for i, fit in enumerate(('preserves', 'uncertain', 'conditional', 'violates'))}
SCORE_FIELDS = ('novelty', 'usefulness', 'fit', 'observability', 'retention',
                'support', 'contract', 'judgment_resolved', 'intelligible')
HISTORICAL_FILES = {
    'bundle-D1-resolved.json': 8,
    'bundle-D2-resolved.json': 8,
    'confirmation-H1-resolved.json': 12,
    'confirmation-H2-resolved.json': 12,
    'confirmation-H3-resolved.json': 12,
    'confirmation-H4-resolved.json': 12,
    'discovery-D1-resolved.json': 28,
    'discovery-D2-resolved.json': 28,
}
FRESH_FILES = ('reports/main-S1-resolved.json', 'reports/main-S2-resolved.json')


def _scores(record):
    return {key: copy.deepcopy(record[key]) for key in SCORE_FIELDS if key in record}


def _number(value):
    return value if type(value) in (int, float) and value in (0, 1, 2) else -1


def _rank(record):
    raw_id = record['raw_id']
    return (FIT_ORDER.get(record.get('fit'), len(FIT_ORDER)),
            -_number(record.get('usefulness')), -_number(record.get('observability')),
            RAW_ORDER.get(raw_id, len(RAW_ORDER)), raw_id)


def _linked(first_family, other_family, families):
    return (other_family in families[first_family].get('uncertain_equivalence_with', [])
            or first_family in families[other_family].get('uncertain_equivalence_with', []))


def _candidate_words(record):
    for field in ('text', 'claim'):
        if isinstance(record.get(field), str):
            return len(record[field].split())
    return None


def _view(records, words):
    burdens = [words[record['raw_id']] for record in records]
    return {
        'raw_ids': [record['raw_id'] for record in records],
        'family_ids': [record['family_id'] for record in records],
        'fixed_scores': [_scores(record) for record in records],
        'candidate_text_words': burdens,
        'total_text_words': None if any(value is None for value in burdens) else sum(burdens),
    }


def _qualification(record, families, historical):
    reasons = []
    requirements = {
        'intelligible': record.get('intelligible') is True,
        'novelty_new': record.get('novelty') == 'new',
        'usefulness_at_least_one': _number(record.get('usefulness')) >= 1,
        'fit_preserves': record.get('fit') == 'preserves',
        'observability_two': record.get('observability') == 2,
        'retained': record.get('retention') == 'retained',
        'resolved': record.get('judgment_resolved') is True
                    and not record.get('unresolved_judgments'),
        'confirmed_family': families[record['family_id']].get('equivalence_status') == 'confirmed',
    }
    for requirement, passes in requirements.items():
        if not passes:
            reasons.append(requirement)
    support_available = isinstance(record.get('support'), str) and bool(record['support'])
    if 'support' in record and not support_available:
        reasons.append('support_unresolved')
    elif record.get('support') == 'unsupported':
        reasons.append('support_unsupported')
    elif not support_available and not historical:
        reasons.append('support_unavailable')
    if 'contract' in record and record['contract'] is None:
        reasons.append('contract_unresolved')
    return {
        'qualifies': not reasons,
        'exclusions': reasons,
        'support_available': support_available,
        'support_basis': 'historical_locked_rubric' if historical else 'criteria_p10',
    }


def compare_set(unit, families):
    """Return a gate or two views without mutating candidates or assessments.

    Ordinary uses retained records, including unresolved records, and distinct
    family IDs. Alternative qualification additionally needs confirmed family
    equivalence; uncertain links to the first family exclude that second slot.
    Gate exposures/views are null, never falsely empty.
    """
    raw = unit.get('raw')
    causes = []
    for flag in ('execution_valid', 'assessment_complete', 'judgments_locked',
                 'equivalence_review_locked'):
        if unit.get(flag) is not True:
            causes.append(flag + '_not_complete')
    if unit.get('review_coverage_complete', True) is not True:
        causes.append('dual_review_coverage_incomplete')
    if unit.get('retention_observed', True) is not True:
        causes.append('neutral_D_missing')
    if 'D' in unit.get('missing_output_roles', []) or 'D' in unit.get('skipped_roles', []):
        causes.append('neutral_D_missing')
    if not isinstance(raw, list) or any(not isinstance(record, dict) for record in raw):
        causes.append('candidate_set_missing_or_invalid')
        raw = []
    raw_ids = [record.get('raw_id') for record in raw]
    if any(not isinstance(raw_id, str) or not raw_id for raw_id in raw_ids):
        causes.append('raw_id_missing')
    elif len(set(raw_ids)) != len(raw_ids):
        causes.append('duplicate_raw_id')
    if not isinstance(families, dict):
        causes.append('families_missing')
        families = {}
    for record in raw:
        family_id = record.get('family_id')
        if not isinstance(family_id, str) or not isinstance(families.get(family_id), dict):
            causes.append('family_missing:' + str(family_id))
        if record.get('retention') == 'retained':
            for field in ('fit', 'usefulness', 'observability'):
                value = record.get(field)
                known = value in FIT_ORDER if field == 'fit' and isinstance(value, str) else (
                    _number(value) >= 0 if field != 'fit' else False)
                if not known:
                    causes.append('unresolved-ranking-score:' + str(record.get('raw_id')) + ':' + field)
    historical = unit.get('stratum') == 'historical'
    if not historical:
        for record in raw:
            if 'support' not in record:
                causes.append('support_missing:' + str(record.get('raw_id')))
    result = {
        'unit_id': unit.get('unit_id'),
        'status': 'not_evaluable' if causes else 'evaluable',
        'gate_causes': sorted(set(causes)),
        'candidates': copy.deepcopy(raw),
        'ordinary': None, 'alternative': None, 'eligibility': None,
        'entering': None, 'displaced': None, 'family_exposures': None,
        'utility_displacement': None, 'violations': None, 'text_burden': None,
    }
    if causes:
        return result
    ranked = sorted((record for record in raw if record.get('retention') == 'retained'), key=_rank)
    ordinary = []
    for record in ranked:
        if record['family_id'] not in {item['family_id'] for item in ordinary}:
            ordinary.append(record)
        if len(ordinary) == 2:
            break
    eligibility = {record['raw_id']: _qualification(record, families, historical) for record in raw}
    first = ordinary[0] if ordinary else None
    for record in raw:
        item = eligibility[record['raw_id']]
        if first and record['family_id'] == first['family_id']:
            item['slot_exclusions'] = ['same_family_as_first']
        elif first and _linked(first['family_id'], record['family_id'], families):
            item['slot_exclusions'] = ['uncertain_equivalence_with_first']
        else:
            item['slot_exclusions'] = []
        item['eligible_for_second'] = item['qualifies'] and first is not None and not item['slot_exclusions']
    selected = next((record for record in ranked if eligibility[record['raw_id']]['eligible_for_second']), None)
    alternative = ordinary[:1]
    if selected is not None:
        alternative.append(selected)
    elif len(ordinary) == 2:
        alternative.append(ordinary[1])
    ordinary_second = ordinary[1] if len(ordinary) == 2 else None
    alternative_second = alternative[1] if len(alternative) == 2 else None
    changed = (ordinary_second or {}).get('raw_id') != (alternative_second or {}).get('raw_id')
    def displacement(record):
        return None if record is None else {
            'raw_id': record['raw_id'], 'family_id': record['family_id'], 'fixed_scores': _scores(record),
        }
    words = {record['raw_id']: _candidate_words(record) for record in raw}
    exposures = []
    for family_id in sorted({record['family_id'] for record in raw}):
        exposures.append({
            'family_id': family_id,
            'candidate_raw_ids': [record['raw_id'] for record in raw if record['family_id'] == family_id],
            'ordinary': sum(record['family_id'] == family_id for record in ordinary),
            'alternative': sum(record['family_id'] == family_id for record in alternative),
        })
    delta = {}
    for field in ('usefulness', 'observability'):
        values = [(ordinary_second or {}).get(field), (alternative_second or {}).get(field)]
        delta[field + '_delta'] = values[1] - values[0] if all(_number(value) >= 0 for value in values) else None
    result.update({
        'ordinary': _view(ordinary, words), 'alternative': _view(alternative, words),
        'eligibility': eligibility, 'alternative_found': selected is not None,
        'entering': displacement(alternative_second) if changed else None,
        'displaced': displacement(ordinary_second) if changed else None,
        'family_exposures': exposures, 'utility_displacement': delta,
        'violations': {name: [record['raw_id'] for record in view if record.get('fit') == 'violates']
                       for name, view in (('ordinary', ordinary), ('alternative', alternative))},
        'conditional_fit': {name: [record['raw_id'] for record in view if record.get('fit') == 'conditional']
                            for name, view in (('ordinary', ordinary), ('alternative', alternative))},
        'text_burden': {'candidate_words': words,
                        'ordinary_words': _view(ordinary, words)['total_text_words'],
                        'alternative_words': _view(alternative, words)['total_text_words']},
    })
    return result


def parse_document(data):
    """Validate assessed container structure only; never rank or judge records."""
    if not isinstance(data, dict) or not isinstance(data.get('units'), list):
        raise ValueError('assessed document requires units list')
    if isinstance(data.get('families'), list):
        family_map = {}
        for family in data['families']:
            family_id = family.get('family_id') if isinstance(family, dict) else None
            if not isinstance(family_id, str) or not family_id or family_id in family_map:
                raise ValueError('family list requires unique nonempty family_id strings')
            family_map[family_id] = copy.deepcopy(family)
        data = dict(data, families=family_map)
    if not isinstance(data.get('families'), dict):
        raise ValueError('assessed document requires families object or list')
    seen = set()
    for unit in data['units']:
        if not isinstance(unit, dict) or not isinstance(unit.get('unit_id'), str) or not isinstance(unit.get('raw'), list):
            raise ValueError('unit requires string unit_id and raw list')
        if unit['unit_id'] in seen:
            raise ValueError('duplicate unit_id within document')
        seen.add(unit['unit_id'])
        raw_ids = set()
        for record in unit['raw']:
            required = {'raw_id', 'family_id', 'novelty', 'usefulness', 'fit', 'observability',
                        'retention', 'judgment_resolved', 'intelligible'}
            if not isinstance(record, dict) or not required.issubset(record):
                raise ValueError('raw record missing assessment fields')
            if not isinstance(record['raw_id'], str) or record['raw_id'] in raw_ids:
                raise ValueError('raw_id must be a unique string within unit')
            raw_ids.add(record['raw_id'])
            if record['family_id'] is None and (record['intelligible'] is False or
                    record['intelligible'] is None and record['judgment_resolved'] is False):
                continue  # Kept intact; compare_set gates this unit with family_missing.
            if not isinstance(record['family_id'], str) or record['family_id'] not in data['families']:
                raise ValueError('raw record references missing family')
    for family_id, family in data['families'].items():
        if not isinstance(family, dict) or not isinstance(family.get('uncertain_equivalence_with', []), list):
            raise ValueError('family must be an object with a link list')
        if any(not isinstance(link, str) or link not in data['families']
               for link in family.get('uncertain_equivalence_with', [])):
            raise ValueError('uncertain equivalence link references missing family')
    return data


def load_documents(run_dir, mode='historical'):
    """Read exact assessment files and hashes; this function performs no comparisons."""
    run_dir = Path(run_dir)
    historical_dir = run_dir / 'inputs/historical-ranking'
    if {path.name for path in historical_dir.glob('*.json')} != set(HISTORICAL_FILES):
        raise ValueError('expected exactly the eight historical ranking files')
    paths = [('inputs/historical-ranking/' + name, 'historical') for name in HISTORICAL_FILES]
    if mode == 'all':
        paths.extend((name, 'fresh') for name in FRESH_FILES)
    elif mode != 'historical':
        raise ValueError('mode must be historical or all')
    loaded = []
    counts = {'historical': 0, 'fresh': 0}
    for name, stratum in paths:
        source_path = run_dir / name
        source_bytes = source_path.read_bytes()
        if stratum == 'fresh' and json.loads(source_bytes).get('status') == 'incomplete':
            gated = source_path.with_name(source_path.name.replace('-resolved.json', '-gated.json'))
            if gated.exists():
                name = str(gated.relative_to(run_dir))
                source_bytes = gated.read_bytes()
        data = parse_document(json.loads(source_bytes))
        if stratum == 'historical' and len(data['units']) != HISTORICAL_FILES[Path(name).name]:
            raise ValueError('historical unit count mismatch: ' + name)
        counts[stratum] += len(data['units'])
        loaded.append({'path': name, 'sha256': hashlib.sha256(source_bytes).hexdigest(),
                       'stratum': stratum, 'data': data})
    if counts['historical'] != 120 or (mode == 'all' and counts['fresh'] != 56):
        raise ValueError('expected 120 historical and, for all, 56 fresh dispositions')
    return loaded


def run(run_dir, mode):
    loaded = load_documents(run_dir, mode)
    comparisons = []
    sources = []
    for source in loaded:
        data = source['data']
        sources.append({key: source[key] for key in ('path', 'sha256', 'stratum')}
                       | {'assessment_sources': copy.deepcopy(data.get('sources', []))})
        for original in data['units']:
            unit = dict(original, stratum=source['stratum'])
            for flag in ('judgments_locked', 'equivalence_review_locked'):
                unit[flag] = data.get(flag) is True and original.get(flag, True) is True
            if data.get('review_coverage_complete', True) is not True:
                unit['review_coverage_complete'] = False
            result = compare_set(unit, data['families'])
            result.update({'source': source['path'], 'stratum': source['stratum'],
                           'case_id': data.get('case_id'), 'phase': data.get('phase')})
            comparisons.append(result)
    report = {'strategy': 'P10', 'mode': mode, 'dispositions': len(comparisons),
              'sources': sources, 'comparisons': comparisons,
              'claim_ceiling': 'Deterministic presentation exposure over fixed model assessments; no human decision benefit inference.'}
    output = Path(run_dir) / 'reports' / ('p10-all.json' if mode == 'all' else 'p10-historical.json')
    # Exclusive creation makes a scored invocation unable to silently replace a report.
    with output.open('x', encoding='utf-8') as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write('\n')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('historical', 'all'))
    parser.add_argument('--run-dir', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        output = run(args.run_dir, args.mode)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + '\n')
    print(output)


if __name__ == '__main__':
    main()
