"""Prospective I13 native compression/retention runtime; no admission on import.

All builders and validators below are memory-only.  Existing v2 columns and
helpers are never patched.  Parent receipts are external authority: their
presence, an output file, or a status string is never a native terminal witness.
Fictional capacity fixtures are UNSCORED and cannot enter the experiment.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import copy
import hashlib
import itertools
import json
import os
import re

import generation_review_validation_v2 as frozen
import blind_generation_raw_first as original
import presentation_v4 as p10

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'composition-i13-native-v1'
CASES = ('H-P', 'A-P', 'H-C1', 'H-C2', 'A-C1', 'A-C2')
POOLS = ('ordinary', 'backcast')
COMPRESSORS = ('ordinary_D', 'source_D')
VIEWS = ('ordinary', 'alternative')
SHARDS = (('H-P', 'A-P'), ('H-C1', 'H-C2'), ('A-C1', 'A-C2'))
BINDINGS = dict(zip(CASES, [('G0235','G0237','G0239'), ('G0241','G0243','G0245'),
                          ('G0247','G0249','G0251'), ('G0253','G0255','G0257'),
                          ('G0259','G0261','G0263'), ('G0265','G0267','G0269')]))
CODE = 'tools/composition_i13_runtime_v1.py'
TEST = 'tools/test_composition_i13_runtime_v1.py'
CHECK = 'reports/I13-native-runtime-preparation-code-check.v1.json'
PACK = 'receipts/I13-native-author-inputs.v1.json'
EXTENSION = 'receipts/I13-native-author-source-extension.v1.json'
CONTRACT = 'contracts/I13-native-preparation-contract.v1.json'
SCHEDULE = 'composition-i13-schedule.draft-v1.json'
REVIEW_SCHEDULE = 'composition-i13-reviews.draft-v1.json'
PROMPT_DIR = 'prompts/composition-i13-draft-v1'
FIXTURE_INPUTS = 'fixtures/composition-i13-maximal-inputs.v1.json'
FIXTURE_PACKET = 'fixtures/composition-i13-maximal-shard.v1.json'
FIXTURE_COMPLETE = 'fixtures/composition-i13-maximal-complete-report.v1.json'
CAPACITY_BODY = 'reviews/composition-i13-capacity/maximal.v1.json'
CAPACITY_RECEIPT = 'reports/I13-native-maximal-capacity-validation.v1.json'
INDEPENDENT_RECEIPT = 'reports/I13-native-independent-prelaunch.v1.json'
INDEPENDENT_BODY = 'reports/I13-native-independent-prelaunch-body.v1.json'
INDEPENDENT_INPUTS = 'receipts/I13-native-independent-prelaunch-inputs.v1.json'
FREEZE = 'freeze-I13-native.v1.json'
ADMISSION = 'receipts/gates/I13-composition-native-admission.v1.json'
PHASE_DECISION = 'receipts/gates/I13-confirmation-decision.v1.json'
FRESH_COLUMNS = copy.deepcopy(frozen.EXACT_COLUMNS)
FRESH_COLUMNS['retention_rows'] = ['compressor_id', *FRESH_COLUMNS['retention_rows']]
FRESH_IDENTITIES = copy.deepcopy(frozen.IDENTITIES)
FRESH_IDENTITIES['retention_rows'] = ['compressor_id', 'source_card_id']
PAIR_COLUMNS = ['post_card_id', 'source_card_id', 'relation', 'evidence']
CARRY_TABLES = ('raw_rows', 'archive_pairs', 'candidate_pairs', 'unit_rows')
STATUSES = ('agreed', 'adjudicated', 'family_unresolved', 'scalar_unresolved', 'unobservable')
RESOLVED = {'agreed', 'adjudicated'}
PAIR_RELATIONS = ('equivalent', 'parameter', 'distinct', 'uncertain')
RETENTION = ('retained', 'lost', 'uncertain', 'unobservable')
OWNED_PATHS = (CODE, TEST, SCHEDULE, REVIEW_SCHEDULE, FIXTURE_INPUTS, FIXTURE_PACKET,
               FIXTURE_COMPLETE, CHECK, *(f'{PROMPT_DIR}/{x}.txt' for x in
               ('ordinary_D', 'source_D', 'review', 'maximal-capacity', 'independent-prelaunch')))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def identical(a, b):
    return canonical(a) == canonical(b)


def parse_json(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate JSON object key: ' + key)
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON ' + x)))


def normalized(path):
    require(type(path) is str and path and '\\' not in path, 'normalized relative path required')
    parts = PurePosixPath(path)
    require(not parts.is_absolute() and str(parts) == path and
            all(x not in ('', '.', '..') for x in path.split('/')), 'non-normalized or escaping path')
    return path


def object_schema(properties, required=None):
    return {'type': 'object', 'properties': properties,
            'required': list(properties) if required is None else required,
            'additionalProperties': False}


def array_schema(items, maximum=None, minimum=0, unique=False):
    result = {'type': 'array', 'items': items, 'minItems': minimum}
    if maximum is not None:
        result['maxItems'] = maximum
    if unique:
        result['uniqueItems'] = True
    return result


TEXT = {'type': 'string', 'minLength': 1}
BOOL = {'type': 'boolean'}
NULL = {'type': 'null'}


def enum(values):
    return {'type': 'string', 'enum': list(values)}


def nullable(schema):
    return {'anyOf': [schema, NULL]}


def field_schema(table, name):
    if name in frozen.BOOLS:
        return BOOL
    if name in ('usefulness', 'observability'):
        return {'type': 'integer', 'enum': [0, 1, 2]}
    if name == 'relation':
        return enum(RETENTION if table == 'retention_rows' else PAIR_RELATIONS)
    if name in frozen.ENUMS:
        return enum(frozen.ENUMS[name])
    if name == 'source_ids':
        return array_schema(TEXT, unique=True)
    return TEXT


def row_schema(table, columns, identities, allow_null=True):
    fields = []
    for key in columns:
        shape = field_schema(table, key)
        if allow_null and key not in identities and key != 'evidence':
            shape = nullable(shape)
        fields.append(shape)
    return {'type': 'array', 'prefixItems': fields, 'items': False,
            'minItems': len(fields), 'maxItems': len(fields)}


D_SCHEMA = object_schema({
    'case_id': TEXT, 'role': {'const': 'D'},
    'openings': array_schema(object_schema({
        'id': enum([f'D{i}' for i in range(1, 7)]),
        'source_ids': array_schema(enum(['R1', 'R2']), 2, 1, True),
        'claim': TEXT, 'discriminator': TEXT,
        'fit': enum(frozen.ENUMS['fit']), 'probe': TEXT, 'uncertainty': TEXT}), 6),
    'lineage': array_schema(object_schema({
        'source_id': enum(['R1', 'R2']),
        'disposition': enum(['retained', 'merged', 'rejected', 'parked']),
        'target_ids': array_schema(enum([f'D{i}' for i in range(1, 7)]), 6, unique=True),
        'reason': TEXT}), 2),
    'decision': TEXT,
    'proposals': array_schema(object_schema({
        'id': enum(['P1', 'P2']), 'claim': TEXT, 'fit': enum(frozen.ENUMS['fit']),
        'probe': TEXT, 'uncertainty': TEXT, 'source_gap': TEXT}), 2)
}, ['case_id', 'role', 'openings', 'lineage', 'decision'])


def carry_schema():
    choices = []
    for table in CARRY_TABLES:
        ids = frozen.IDENTITIES[table]
        values = {k: (field_schema(table, k) if k in ids or k == 'evidence' else
                      nullable(field_schema(table, k))) for k in frozen.EXACT_COLUMNS[table]}
        status_keys = [k for k in values if k not in ids and k != 'evidence']
        # Fixed fields (execution and nonempty no-opening) are absent from the
        # original field_status map; preserve exact maps instead of inventing one.
        choices.append(object_schema({
            'table': {'const': table}, 'row_id': TEXT,
            'identity': object_schema({k: TEXT for k in ids}),
            'values': object_schema(values),
            'field_status': object_schema({k: enum(STATUSES) for k in status_keys}, [])}))
    return {'oneOf': choices}


def review_schema():
    limits = {'post_rows': 24, 'retention_rows': 8, 'lineage_rows': 8,
              'addition_rows': 8, 'unit_rows': 4}
    fresh = {'reviewer_id': TEXT, 'columns': {'const': FRESH_COLUMNS}, 'limits': TEXT}
    fresh.update({table: array_schema(row_schema(table, columns, FRESH_IDENTITIES[table]),
                                     limits.get(table, 0))
                  for table, columns in FRESH_COLUMNS.items()})
    case = object_schema({'case_packet_id': TEXT,
                          'carried_raw_rows': array_schema(carry_schema(), 48),
                          'new_review': object_schema(fresh),
                          'source_pairs': array_schema(row_schema('source_pairs', PAIR_COLUMNS,
                                                       PAIR_COLUMNS[:2]), 48)})
    return object_schema({'packet_id': TEXT, 'reviewer_id': TEXT,
                          'cases': array_schema(case, 3, 1)})


REVIEW_SCHEMA = review_schema()
INDEPENDENT_BODY_SCHEMA = object_schema({
    'study_id':{'const':'I13'},'classification':enum(['pass','repair_required']),
    'checks':object_schema({k:BOOL for k in ('literal_prompt_policy_verified','exact_source_reuse_verified',
        'runtime_mechanics_verified','native_capacity_structure_verified','immutable_sources_verified')}),
    'findings':array_schema(object_schema({'finding_id':TEXT,'severity':enum(['blocking','nonblocking']),
                                          'evidence':TEXT,'required_change':TEXT})),
    'source_bindings':array_schema(object_schema({'path':TEXT,'sha256':TEXT}),minimum=1),
    'experimental_admission_claim':{'const':False},'claim_limit':TEXT})


def schema_errors(schema, value, label='$'):
    """Small strict JSON-schema evaluator for these literal finite schemas."""
    errors = []
    if schema is False:
        return [label + ': additional item prohibited']
    if 'const' in schema and not identical(value, schema['const']):
        errors.append(label + ': exact constant')
    if 'enum' in schema and not any(identical(value, x) for x in schema['enum']):
        errors.append(label + ': enum')
    for combinator in ('oneOf', 'anyOf'):
        if combinator in schema:
            count = sum(not schema_errors(s, value, label) for s in schema[combinator])
            if (count != 1 if combinator == 'oneOf' else count == 0):
                errors.append(label + ': ' + combinator)
            return errors
    kind = schema.get('type')
    types = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'integer': int,
             'null': type(None)}
    if kind and type(value) is not types[kind]:
        return errors + [label + ': ' + kind + ' required']
    if kind == 'object':
        keys = schema.get('properties', {})
        if not set(schema.get('required', [])) <= set(value):
            errors.append(label + ': required keys')
        if schema.get('additionalProperties') is False and not set(value) <= set(keys):
            errors.append(label + ': unknown keys')
        for key in value.keys() & keys.keys():
            errors.extend(schema_errors(keys[key], value[key], label + '.' + key))
    elif kind == 'array':
        if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', len(value)):
            errors.append(label + ': array length')
        if schema.get('uniqueItems') and len({canonical(x) for x in value}) != len(value):
            errors.append(label + ': duplicate array value')
        prefixes = schema.get('prefixItems', [])
        for i, item in enumerate(value):
            sub = prefixes[i] if i < len(prefixes) else schema.get('items', {})
            errors.extend(schema_errors(sub, item, label + '[' + str(i) + ']'))
    elif kind == 'string' and (len(value) < schema.get('minLength', 0) or
                               schema.get('minLength', 0) and not value.strip()):
        errors.append(label + ': nonempty string')
    return errors


def validate_D(case, source, body):
    errors = schema_errors(D_SCHEMA, body)
    if errors:
        return {'valid': False, 'errors': errors}
    if body['case_id'] != case:
        errors.append('unchanged assigned case_id')
    raw_ids = [c['id'] for c in source['openings']]
    require(len(raw_ids) <= 2 and len(set(raw_ids)) == len(raw_ids) and
            set(raw_ids) <= {'R1','R2'}, 'exact current raw local IDs')
    cards = {c['id']: c for c in body['openings']}
    lineage = {l['source_id']: l for l in body['lineage']}
    if len(cards) != len(body['openings']):
        errors.append('duplicate D ID')
    if len({c['id'] for c in body.get('proposals', [])}) != len(body.get('proposals', [])):
        errors.append('duplicate optional P ID')
    if len(lineage) != len(body['lineage']) or set(lineage) != set(raw_ids):
        errors.append('exact once current-source lineage')
    for card in cards.values():
        for local in card['source_ids']:
            item = lineage.get(local)
            if item is None or item['disposition'] not in ('retained', 'merged') or card['id'] not in item['target_ids']:
                errors.append('D/lineage reciprocal source membership')
    for item in lineage.values():
        targets = item['target_ids']
        if item['disposition'] in ('parked', 'rejected') and targets:
            errors.append('parked/rejected requires empty targets')
        if item['disposition'] in ('retained', 'merged') and not targets:
            errors.append('retained/merged requires actual carrier')
        for target in targets:
            if target not in cards or item['source_id'] not in cards[target]['source_ids']:
                errors.append('lineage/D reciprocal target membership')
    return {'valid': not errors, 'errors': errors, 'raw_creation_credit': 0,
            'optional_preservation_credit': 0}


def obligation(table, identity, fixed=None, null=False):
    return {'row_id': 'E-' + digest([table, identity])[:24], 'identity': identity,
            'fixed_values': fixed or {}, 'null_semantics': null}


def qualified(job, local):
    return job + ':' + local


def fresh_case(context, D_units):
    """Derive the full fresh matrix from actual assigned D objects, not metadata."""
    require(len(D_units) == 4, 'all four planned D units retained')
    expected_jobs = {f'I13-{context["case_id"]}-{pool}-{comp}' for pool in POOLS for comp in COMPRESSORS}
    require({u['unit_id'] for u in D_units} == expected_jobs, 'exact D factorial cells')
    matrix = {t: [] for t in FRESH_COLUMNS}
    pairs = []
    normalized_units = []
    for item in D_units:
        unit = copy.deepcopy(item)
        job, pool = unit['unit_id'], unit['pool']
        require(unit['execution'] in frozen.ENUMS['execution'], 'explicit valid/invalid/missing/skipped D disposition')
        require(unit['compressor'] in COMPRESSORS and pool in POOLS and
                job == f'I13-{context["case_id"]}-{pool}-{unit["compressor"]}', 'D cell identity')
        source = context['producers'][pool]
        unit['semantic_contract_ref'] = unit['compressor']
        valid = unit['execution'] == 'valid'
        body = unit.get('artifact')
        if valid:
            require(validate_D(context['case_id'], source['artifact'], body)['valid'], 'valid D structural contract')
        local_to_original = source['local_to_original']
        cards = body.get('openings', []) if isinstance(body, dict) else []
        proposals = body.get('proposals', []) if isinstance(body, dict) else []
        representable = (type(cards) is list and type(proposals) is list and len(cards)<=6 and len(proposals)<=2 and
            all(type(c) is dict and type(c.get('id')) is str and c['id'] in {f'D{i}' for i in range(1,7)} for c in cards) and
            len({c['id'] for c in cards})==len(cards) and
            all(type(c) is dict and c.get('id') in ('P1','P2') for c in proposals) and
            len({c['id'] for c in proposals})==len(proposals))
        if not valid and not representable:
            unit['unassessable_original_artifact'] = copy.deepcopy(body)
            body, cards, proposals = None, [], []
        unit['artifact'] = copy.deepcopy(body)
        for c in cards:
            require(type(c) is dict and type(c.get('id')) is str, 'representable D card identity')
            declared = c.get('source_ids', [])
            declared = declared if type(declared) is list else []
            sources = list(dict.fromkeys(local_to_original[x] for x in declared if type(x) is str and x in local_to_original))
            card_id = qualified(job, c['id'])
            matrix['post_rows'].append(obligation('post_rows', {'card_id': card_id}, {'source_ids': sources}, not valid))
            for source_id in local_to_original.values():
                pairs.append(obligation('source_pairs', {'post_card_id': card_id, 'source_card_id': source_id}, null=not valid))
        declared_lineage = {x['source_id']: x for x in body.get('lineage', [])} if valid else {}
        for local, source_id in local_to_original.items():
            matrix['retention_rows'].append(obligation('retention_rows', {'compressor_id': job, 'source_card_id': source_id}, null=not valid))
            fixed = {'disposition': declared_lineage[local]['disposition']} if valid else {}
            matrix['lineage_rows'].append(obligation('lineage_rows', {'unit_id': job, 'source_id': source_id}, fixed, not valid))
        for c in proposals:
            require(type(c) is dict and type(c.get('id')) is str, 'representable proposal identity')
            matrix['addition_rows'].append(obligation('addition_rows', {'card_id': qualified(job, c['id'])}, null=not valid))
        fixed = {'execution': unit['execution']}
        if valid and cards:
            fixed['no_opening_reason_supported'] = None
        matrix['unit_rows'].append(obligation('unit_rows', {'unit_id': job}, fixed, not valid))
        normalized_units.append(unit)
    result = {'case_packet_id': 'I13-C-' + digest([context['case_id'], context['context_sha256'], normalized_units])[:24],
              'case_id': context['case_id'], 'source_context': copy.deepcopy(context),
              'carried_raw_rows': copy.deepcopy(context['carried_raw_rows']),
              'D_units': normalized_units, 'expected_matrix': matrix, 'source_pair_matrix': pairs,
              'fresh_semantic_contracts':{comp:build_prompts(FROZEN_COMPRESSION_SOURCE)[f'{PROMPT_DIR}/{comp}.txt'].split(
                  'BEGIN_LITERAL_JSON_SCHEMA')[0] for comp in COMPRESSORS},
              'matrix_counts': {t: len(rs) for t, rs in matrix.items()},
              'copied_raw_count': len(context['carried_raw_rows']), 'new_source_pair_count': len(pairs)}
    result['expected_native_rows'] = result['copied_raw_count'] + sum(result['matrix_counts'].values()) + len(pairs)
    require(result['expected_native_rows'] <= 148, 'per-case native row cap')
    return result


def build_packet(contexts, all_D_units, reviewers, fixture=False):
    require(1 <= len(contexts) <= 3 and len({c['case_id'] for c in contexts}) == len(contexts), 'unique whole shard cases')
    require(len(reviewers) == 2 and len(set(reviewers)) == 2 and all(type(x) is str and x for x in reviewers), 'distinct assigned reviewers')
    if not fixture:
        require(tuple(c['case_id'] for c in contexts) in SHARDS, 'exact scheduled two-case shard')
        require(all(c['creation_valid'] and not c['diagnostic_only'] and not c['fictional'] for c in contexts),
                'original pilot has no live native review packet; retain administrative gated denominators')
    cases = [fresh_case(c, all_D_units[c['case_id']]) for c in contexts]
    return {'version': VERSION, 'packet_id': 'I13-S-' + digest(cases)[:24],
            'study_id': 'I13', 'reviewer_ids': list(reviewers), 'cases': cases,
            'columns': copy.deepcopy(FRESH_COLUMNS), 'source_pairs_columns': PAIR_COLUMNS[:],
            'expected_native_rows': sum(c['expected_native_rows'] for c in cases),
            'live_admissible': not fixture, 'epistemic_status': 'UNSCORED_CAPACITY_FIXTURE' if fixture else 'source_bound_model_judgments_only',
            'raw_creation_credit': 0, 'native_view_judgment_credit': 0}


def validate_fresh(case, review, reviewer_id):
    errors = []
    if review.get('reviewer_id') != reviewer_id or review.get('columns') != FRESH_COLUMNS:
        errors.append('fresh reviewer/columns exact binding')
    for table, obligations in case['expected_matrix'].items():
        columns, ids = FRESH_COLUMNS[table], FRESH_IDENTITIES[table]
        lookup = {tuple(o['identity'][k] for k in ids): o for o in obligations}
        if len(lookup) != len(obligations):
            errors.append(table + ': duplicate packet identity')
        seen = set()
        for row in review.get(table, []):
            if type(row) is not list or len(row) != len(columns):
                errors.append(table + ': exact row width')
                continue
            values = dict(zip(columns, row))
            key = tuple(values[k] for k in ids)
            if key in seen:
                errors.append(table + ': duplicate row identity')
            seen.add(key)
            binding = lookup.get(key)
            if binding is None:
                errors.append(table + ': unknown row identity')
                continue
            for field, value in values.items():
                if field in ids or field == 'evidence':
                    continue
                if field in binding['fixed_values']:
                    if not identical(value, binding['fixed_values'][field]):
                        errors.append(table + ': exact fixed ' + field)
                elif binding['null_semantics']:
                    if value is not None:
                        errors.append(table + ': unavailable semantics must be null')
                elif value is None:
                    errors.append(table + ': resolved fresh field cannot be null ' + field)
        if seen != set(lookup):
            errors.append(table + ': complete row coverage')
    return errors


def validate_review(packet, review):
    errors = schema_errors(REVIEW_SCHEMA, review)
    if errors:
        return {'valid': False, 'errors': errors, 'semantic_validity': 'not asserted'}
    try:
        require(packet['version'] == VERSION and packet['columns'] == FRESH_COLUMNS and
                packet['source_pairs_columns'] == PAIR_COLUMNS, 'exact I13 packet contract')
        require(type(packet['reviewer_ids']) is list and len(packet['reviewer_ids'])==2 and
                len(set(packet['reviewer_ids']))==2 and all(type(x) is str and x for x in packet['reviewer_ids']),
                'exact two assigned reviewer IDs')
        require(review['packet_id'] == packet['packet_id'] and review['reviewer_id'] in packet['reviewer_ids'], 'assigned packet/reviewer')
        originals = {c['case_packet_id']: c for c in packet['cases']}
        require(len(originals) == len(packet['cases']), 'unique packet cases')
        seen, total = set(), 0
        for body in review['cases']:
            key = body['case_packet_id']
            require(key in originals and key not in seen, 'unknown/duplicate case review')
            seen.add(key)
            case = originals[key]
            require(identical(case, fresh_case(case['source_context'],case['D_units'])),
                    'packet obligations derived from exact assessed D objects; no metadata echo')
            cbody = {k:v for k,v in case['source_context'].items() if k!='context_sha256'}
            require(digest(cbody)==case['source_context']['context_sha256'], 'source context hash drift')
            require(identical(body['carried_raw_rows'], case['carried_raw_rows']), 'complete original raw values/evidence/status/order protected')
            require(identical(case['carried_raw_rows'], case['source_context']['carried_raw_rows']), 'packet raw carry drift')
            errors.extend(validate_fresh(case, body['new_review'], review['reviewer_id']))
            obligations = {(o['identity']['post_card_id'], o['identity']['source_card_id']): o for o in case['source_pair_matrix']}
            pair_seen = set()
            for post, source, relation, evidence in body['source_pairs']:
                pair = (post, source)
                require(pair in obligations and pair not in pair_seen, 'source-pair unknown/duplicate')
                pair_seen.add(pair)
                require((relation is None) is obligations[pair]['null_semantics'], 'source-pair exact null rule')
            require(pair_seen == set(obligations), 'complete D x assigned-current-raw pairs including undeclared sources')
            count = len(body['carried_raw_rows']) + sum(len(body['new_review'][t]) for t in FRESH_COLUMNS) + len(body['source_pairs'])
            require(case['matrix_counts'] == {t: len(rs) for t, rs in case['expected_matrix'].items()} and
                    count == case['expected_native_rows'], 'case row count/matrix equality')
            total += count
        require(seen == set(originals) and total == packet['expected_native_rows'], 'whole scheduled shard exact rows')
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        errors.append(str(exc))
    return {'valid': not errors, 'errors': errors, 'expected_rows': packet.get('expected_native_rows'),
            'carried_independent_grade_credit': 0, 'native_view_judgment_credit': 0,
            'semantic_validity': 'not asserted; independent native evidence judgments required'}


def validate_source_reuse(original_source_context, reused_context):
    errors = []
    if not identical(original_source_context, reused_context):
        errors.append('exact complete source context/bytes/identities/grades/statuses drift')
    return {'valid': not errors, 'errors': errors, 'raw_creation_credit': 0}


def validate_bindings(bindings, corpus, exact_paths=None):
    require(type(bindings) is list and bindings, 'nonempty exact source bindings')
    seen = set()
    for binding in bindings:
        require(type(binding) is dict and set(binding) == {'path','sha256'}, 'binding exact keys')
        path = normalized(binding['path'])
        require(path not in seen, 'duplicate source binding')
        seen.add(path)
        require(type(binding['sha256']) is str and re.fullmatch('[0-9a-f]{64}', binding['sha256']), 'SHA256 required')
        require(path in corpus and type(corpus[path]) is bytes and digest(corpus[path]) == binding['sha256'], 'exact source bytes ' + path)
    if exact_paths is not None:
        require(seen == set(exact_paths), 'missing/extra prospective source closure')
    return True


def source_context(case, corpus):
    """Verify original I06 full context from the assigned immutable byte corpus.

    Historical native events predate explicit native_call_id. They are preserved
    verbatim and checked against their original schema; fresh I13 calls require
    the stronger schema below and can never adopt those old events.
    """
    require(case in CASES, 'original case only')
    validate_bindings([{'path':p,'sha256':h} for p,h in ASSIGNED_SOURCE_HASHES.items()],corpus)
    sources = {p: parse_json(corpus[p]) for p in corpus if p.endswith('.json')}
    diagnostic = case.endswith('-P')
    packet_ref = f'fixtures/generation-blind/I06-{case}.json' if diagnostic else f'fixtures/generation-raw-first/I06-{case}-raw.json'
    packet = sources[packet_ref]
    map_ref = ('receipts/generation-blind-maps-v2/' + packet['packet_id'] + '.json') if diagnostic else f'receipts/generation-raw-first-maps/I06-{case}-raw.json'
    lock_ref = f'reports/generation-locked/I06-{case}.json' if diagnostic else f'reports/generation-raw-first-locked/I06-{case}-raw.json'
    admin, lock = sources[map_ref], sources[lock_ref]
    require(admin['case_id'] == case and admin['packet_id'] == packet['packet_id'] == lock['case_packet_id'], 'original assessed-object identity')
    require(identical(packet['case'], sources[f'cases/{case}.json']) and
            identical(packet['contract']['columns'], frozen.EXACT_COLUMNS), 'unchanged case/frozen columns')
    validate_bindings(admin['input_bindings'],corpus)
    artifact_payload_hashes = {b['job_id']:b['sha256'] for b in admin['artifact_payload_bindings']}
    rows = copy.deepcopy(lock['rows']) if diagnostic else original.locked_rows(packet, lock)
    raw_units = {u['unit_id'] for u in packet['units'] if u['content_kind'] == 'source'}
    carried = [r for r in rows if r['table'] in CARRY_TABLES and
               (r['table'] != 'unit_rows' or r['identity']['unit_id'] in raw_units)]
    require(len(carried) <= 48 and all(set(r) == {'table','row_id','identity','values','field_status'} for r in carried), 'literal full raw rows')
    mappings = {(m['job_id'], m['local_id']): m for m in admin['mapping'] if m.get('field') == 'openings'}
    unit_map = {m['job_id']: m['unit_id'] for m in admin['mapping'] if 'unit_id' in m}
    producers = {}
    for pool, job in zip((*POOLS, 'generic'), BINDINGS[case]):
        payload = sources[f'outputs/generation/{job}.json']
        require(hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()==artifact_payload_hashes[job],
                'exact original producer payload/admin binding')
        originals = {o['id']: mappings[job, o['id']]['opaque_id'] for o in payload['openings']}
        require(all(mappings[job,o['id']]['index']==i and mappings[job,o['id']]['duplicate'] is False
                    for i,o in enumerate(payload['openings'])), 'original frozen source order/bijection')
        packet_unit = next(u for u in packet['units'] if u['unit_id'] == unit_map[job])
        require(set(originals.values()) == {c['id'] for c in packet_unit['artifact']['openings']}, 'exact original/local bijection')
        # Original packet payloads replace local card IDs; compare all other raw
        # facts without reconstructing or scoring their values.
        for local_card in payload['openings']:
            bound = next(c for c in packet_unit['artifact']['openings'] if c['id'] == originals[local_card['id']])
            require(all(identical(v, bound[k]) for k,v in local_card.items() if k != 'id'), 'original raw fact drift')
        producers[pool] = {'job_id': job, 'unit_id': unit_map[job], 'artifact': copy.deepcopy(payload),
                           'local_to_original': originals,
                           'local_to_qualified_producer': {x: qualified(job,x) for x in originals},
                           'raw_order': {x:i for i,x in enumerate(originals)}}
    events = sources['receipts/I13-upstream-I06-context-events.v1.json']['events']
    raw_jobs = list(BINDINGS[case])
    reviewer_jobs = [f'RG-I06-{case}-{i}' if diagnostic else f'RF-R-I06-{case}-{i}' for i in (1,2)]
    witness = []
    for job in raw_jobs + reviewer_jobs:
        starts = [e for e in events if e.get('job_id') == job and e['event_kind'] == 'native_spawn']
        finals = [e for e in events if e.get('job_id') == job and e['event_kind'] == 'native_terminal_join']
        prepares = [e for e in events if e.get('job_id') == job and e['event_kind'] == 'job_prepared']
        require(len(starts) == len(finals) == len(prepares) == 1, 'exact original native role start/FINAL/prepared')
        start, final, prepared = starts[0], finals[0], prepares[0]
        require(start.get('host_spawn_observed') is True and start.get('fresh_context') is True and
                start.get('turn') == 1 and final.get('terminal_observed') is True and
                final.get('terminal_witness') == 'parent_received_NATIVE_FINAL_ANSWER' and
                final['agent_handle'] == start['agent_handle'] and final['validation']['valid'] is True,
                'original actual native start/FINAL binding')
        validate_bindings(prepared['input_bindings'], corpus)
        require(prepared['prompt_ref'] in corpus and digest(corpus[prepared['prompt_ref']]) == prepared['prompt_sha256'], 'original actual prompt hash')
        require(final['output_ref'] in corpus and digest(corpus[final['output_ref']]) == final['validation']['output_sha256'], 'original actual output hash')
        witness.append({'prepared': copy.deepcopy(prepared), 'start': copy.deepcopy(start), 'FINAL': copy.deepcopy(final)})
    require(len({w['start']['agent_handle'] for w in witness[-2:]}) == 2, 'original fresh dual reviewers')
    old_post = ({'packet': copy.deepcopy(packet), 'map': copy.deepcopy(admin), 'lock': copy.deepcopy(lock)} if diagnostic else
                {'packet': sources[f'fixtures/generation-raw-first/I06-{case}-post.json'],
                 'map': sources[f'receipts/generation-raw-first-maps/I06-{case}-post.json'],
                 'lock': sources[f'reports/generation-raw-first-locked/I06-{case}-post.json']})
    if not diagnostic:
        require(lock['independent_review_complete'] is True, 'proper locked dual raw review before fresh D')
        raw_final_time = max(w['FINAL']['time_utc'] for w in witness[-2:])
        D_starts = [e for e in events if e.get('job_id') in {f'G{int(j[1:])+1:04d}' for j in raw_jobs} and e['event_kind']=='native_spawn']
        require(len(D_starts) == 3 and all(e['time_utc'] > raw_final_time for e in D_starts), 'original proper raw-before-D ordering')
    context = {'case_id': case, 'creation_valid': not diagnostic, 'diagnostic_only': diagnostic,
               'case': copy.deepcopy(packet['case']), 'raw_packet': copy.deepcopy(packet),
               'raw_admin': copy.deepcopy(admin), 'raw_lock': copy.deepcopy(lock),
               'carried_raw_rows': carried, 'producers': producers, 'old_post_context': old_post,
               'old_post_failure': not diagnostic and old_post['lock']['independent_review_complete'] is not True,
               'original_full_artifacts':{j:copy.deepcopy(sources[f'outputs/generation/{j}.json']) for j in
                   [*raw_jobs, *[f'G{int(j[1:])+1:04d}' for j in raw_jobs]]},
               'original_reviews':{j:copy.deepcopy(sources[
                   f'reviews/generation/{j}.json' if diagnostic else f'reviews/generation-raw-first/{j}.json']) for j in
                   reviewer_jobs+([] if diagnostic else [f'RF-P-I06-{case}-{i}' for i in (1,2)])},
               'native_raw_witnesses': witness, 'native_full_case_history': [copy.deepcopy(e) for e in events
                   if e.get('job_id') in set(raw_jobs + reviewer_jobs +
                     [f'G{int(j[1:])+1:04d}' for j in raw_jobs] +
                     ([] if diagnostic else [f'RF-P-I06-{case}-{i}' for i in (1,2)])) or e.get('case_id')==case],
               'source_refs': {'packet': packet_ref, 'map': map_ref, 'lock': lock_ref},
               'source_bytes_bindings':{p:digest(corpus[p]) for p in [packet_ref,map_ref,lock_ref,
                   f'cases/{case}.json','archives/case-archives.json','criteria-generation.v2.json',
                   'generation-review-contract.v2.json',*[f'outputs/generation/{j}.json' for j in raw_jobs],
                   'receipts/I13-upstream-I06-context-events.v1.json']},
               'raw_creation_credit': 0, 'generic_context_preserved': True,
               'fictional': False}
    context['context_sha256'] = digest(context)
    return context


def build_schedule():
    jobs, cells, reviews = [], [], []
    for case in CASES:
        phase = 'pilot' if case.endswith('-P') else 'confirmation'
        diagnostic = phase == 'pilot'
        for pool, comp in itertools.product(POOLS, COMPRESSORS):
            job = f'I13-{case}-{pool}-{comp}'
            raw_job = BINDINGS[case][POOLS.index(pool)]
            jobs.append({'job_id': job, 'study_id': 'I13', 'case_id': case, 'phase': phase,
                         'role': 'D', 'pool': pool, 'compressor': comp,
                         'input_refs': [f'cases/{case}.json', f'outputs/generation/{raw_job}.json'],
                         'input_bindings':[{'path':p,'sha256':ASSIGNED_SOURCE_HASHES[p]} for p in
                             (f'cases/{case}.json',f'outputs/generation/{raw_job}.json')],
                         'original_raw_job_id': raw_job, 'prompt_ref': f'{PROMPT_DIR}/{comp}.txt',
                         'output_ref': f'outputs/composition-i13/{job}.json',
                         'soft_saved_word_limit': 350, 'max_D': 6, 'max_P': 2,
                         'first_substantive_save_only': True, 'scored_retries': 0,
                         'planned_disposition': 'skipped_diagnostic_original_pilot' if diagnostic else 'pending_source_bound_admission',
                         'native_calls_if_gated': 0, 'raw_creation_credit': 0,
                         'requires': [ADMISSION, PHASE_DECISION, 'exact_original_raw_context']})
            for view in VIEWS:
                cells.append({'job_id': job + '-' + view, 'D_job_id': job, 'study_id': 'I13',
                              'case_id': case, 'phase': phase, 'pool': pool, 'compressor': comp,
                              'view': view, 'planned_disposition': 'diagnostic_gated' if diagnostic else 'pending_fresh_dual_lock',
                              'native_calls': 0})
    for index, cases in enumerate(SHARDS):
        diagnostic = index == 0
        for n in (1,2):
            job = f'RF-I13-S{index+1}-{n}'
            reviews.append({'job_id': job, 'reviewer_id': job, 'study_id': 'I13', 'role': 'preservation_review',
                            'phase': 'pilot' if diagnostic else 'confirmation', 'case_ids': list(cases),
                            'depends_on': [j['job_id'] for j in jobs if j['case_id'] in cases],
                            'prompt_ref': f'{PROMPT_DIR}/review.txt',
                            'packet_ref':f'fixtures/composition-i13-review-shards/S{index+1}.v1.json',
                            'output_ref': f'reviews/composition-i13/{job}.json', 'soft_saved_word_limit': 20000,
                            'scored_retries': 0, 'planned_disposition': 'administratively_gated_original_pilot' if diagnostic else 'pending_whole_shard',
                            'native_calls_if_gated': 0})
    return ({'version': VERSION, 'classification': 'prospective_unadmitted_not_execution',
             'study_id': 'I13', 'cases': list(CASES), 'jobs': jobs, 'view_cells': cells,
             'planned_denominators': {'D':24, 'reviews':6, 'views':48},
             'pilot_administrative_disposition': {'D_skipped':8, 'reviews_gated':2, 'views_gated':16,
                                                   'actual_native_calls':0, 'creation_valid':False},
             'confirmation_decision': 'independent informative original four-block justification required after pilot disposition',
             'budget': {'preparation_maximum':6, 'completion_audit_maximum':1,
                       'pilot_ceiling':11, 'pilot_actual_authorized_calls':0,
                       'confirmation_base':20, 'confirmation_ceiling':22,
                       'optional_scalar_calls': 'separate prospective admission only', 'no_pool_transfer':True,
                       'actual_overages_charged':True, 'equal_compute_claim':False}},
            {'version': VERSION, 'classification':'prospective_unadmitted_not_execution', 'jobs':reviews})


def build_prompts(compression_source):
    require('Source-bound repair:' in compression_source and 'Generation-source adapter:' in compression_source,
            'audited source-bound prompt sections')
    common, remainder = compression_source.split('Source-bound repair:', 1)
    repair, adapter = remainder.split('Generation-source adapter:', 1)
    adapter = 'Generation-source adapter:' + adapter
    common = common.split('Return JSON ', 1)[0]
    protocol = ('\nAssigned case_id, paths, local IDs and output path are supplied by parent after admission. '
                'Read only unchanged case plus one exact raw producer. Current local R IDs only; '
                'qualified previous lineage is context. No archives, graded answers, generic/sibling/old D, '
                'method menu, agents or web. First substantive JSON save only; zero retries. '
                'Same350 soft output words, max6 D and max2 optional P. Empty raw means no D/lineage. '
                'Optional P has zero preservation, inherited novelty/family and raw creation credit. '
                'The following is the literal complete output JSON schema; every required/allowed '
                'nested field, type and enum is explicit. Additional keys are prohibited. '
                'D and P IDs must be unique; every assigned current R exactly once in lineage, '
                'with reciprocal D source/lineage targets. No packet metadata echo.\n')
    schema = '\nBEGIN_LITERAL_JSON_SCHEMA\n' + json.dumps(D_SCHEMA, indent=2) + '\nEND_LITERAL_JSON_SCHEMA\n'
    prompts = {'ordinary_D': common + adapter + protocol + schema,
               'source_D': common + 'Source-bound repair:' + repair + adapter + protocol + schema}
    instructions = ('I13 fresh preservation review. Read only assigned whole shard packet and this instruction. '
        'Return first substantive JSON only at assigned output; zero retries, same20000 soft saved words. '
        'Every scheduled case and every expected row exactly once. Carry original raw row objects '
        '{table,row_id,identity,values,field_status} exactly including evidence/null/status/order, zero '
        'new raw judgment. new_review is fresh-only; raw/archive/candidate/attack/contradiction arrays '
        'empty. D retention keyed by compressor_id+source_card_id, lineage by D+source. '
        'Judge protected causal relation, complete rival/discriminating prediction and probe, all '
        'directional challenges/defeats, resources/stopping caveats, uncertainty and declared fit. '
        'Faithful raw mistakes are inherited; fresh unsupported assertions are separate. Ordinary D '
        'is judged by its common assigned compression instruction; source D additionally by audited '
        'explicit protected-meaning repair. All D post cards x ALL assigned current raw cards need '
        'source_pairs including undeclared sources. Optional P only fit/support/evidence, never '
        'inherited novelty/family/eligibility. Respect exact expected fixed_values/null_semantics; '
        'unavailable judgments null, never zero. Evidence is nonempty source-specific text. '
        'Pair relations direct equivalent|parameter|distinct|uncertain; no forced transitive family '
        'merge. Do not copy packet metadata into output; only schema fields. No model view grades. '
        'Scalar meanings: usefulness0=none,1=bounded useful,2=strong outcome relevance; '
        'observability0=no probe,1=outcome/fit probe,2=informative rival discriminator. '
        'The frozen criteria and exact per-unit prompt in the supplied source context own meanings.\n'
        'UNSCORED and unexecuted describe evidence ceilings, not automatic nulls. Evaluating a fictional '
        'proposal for textual source preservation, fit, support or instruction completeness does not '
        'claim that its physical/data/human effects occurred. Every assessable obligation with '
        'null_semantics=false requires a permitted typed grade/enumeration and source-specific evidence. '
        'Use supported uncertainty categories, false flags or conservative low grades where warranted '
        'by supplied text; never invent successful effects. Null only for actual null_semantics=true '
        'semantic fields or an exactly declared fixed null (such as a nonempty unit no-opening field). '
        'Copied original raw rows keep their exact existing values, including existing nulls and statuses.\n'
        'BEGIN_LITERAL_JSON_SCHEMA\n' + json.dumps(REVIEW_SCHEMA, indent=2) + '\nEND_LITERAL_JSON_SCHEMA\n')
    prompts['review'] = instructions
    prompts['maximal-capacity'] = instructions + (
        '\nUNSCORED native output structure/size only. Exactly3 fictional cases,444 rows. '
        'Read only ' + str(ROOT / FIXTURE_PACKET) + '. Assigned reviewer_id=CAPACITY-I13-1. '
        'Use the same reviewer_id inside every new_review. Save first substantive full JSON only '
        + str(ROOT / CAPACITY_BODY) + '. No agents/web/other writes/retries. '
        'Fictional sources/locks cannot prove actual phase/start/FINAL evidence, semantic adequacy, '
        'efficacy or admission. Final confirms actual file path and hash only.\n')
    prompts['independent-prelaunch'] = (
        'Prospective independent I13 runtime/source review only. Parent must spawn a fresh actual native '
        'reviewer after author FINAL and completed maximum native capacity validation. Read this prompt '
        'and only the exact assigned source pack ' + str(ROOT / INDEPENDENT_INPUTS) + '. '
        'Verify full24D/6review/48view schedule, diagnostic pilot8D/2reviews/16views gates, exact full '
        'I06 raw/generic/case/rubric/archive/graded-lock/native history reuse, all four proper raw-first '
        'contexts including preserved old H-C2 post failure, literal D/review schemas and common/adapter '
        'vs audited source-bound instruction, D-scoped retention,444native/612complete structure, actual '
        'start/FINAL/source closure/firstsave/zero retry enforcement, P10 partial/null/false-family/uncertain '
        'keys, complete merged-carrier source mappings and proposal separation. Use memory-only checks. '
        'No agents/web/trials/events/freezes/admission or other writes. First substantive JSON only '
        + str(ROOT / INDEPENDENT_BODY) + '; zero retries. Do not claim own FINAL or admission. '
        'Return only the literal complete schema fields below. No packet metadata echo.\n'
        'BEGIN_LITERAL_JSON_SCHEMA\n' + json.dumps(INDEPENDENT_BODY_SCHEMA,indent=2) + '\nEND_LITERAL_JSON_SCHEMA\n')
    return {f'{PROMPT_DIR}/{key}.txt': value for key,value in prompts.items()}


def witness_schema():
    binding = object_schema({'path': TEXT, 'sha256': TEXT})
    base = {'job_id': TEXT, 'study_id': {'const':'I13'}, 'phase': enum(['pilot','confirmation','capacity','preparation']),
            'agent_handle': TEXT, 'native_call_id': TEXT, 'turn': {'type':'integer', 'const':1},
            'prompt_binding': binding, 'input_bindings': array_schema(binding, minimum=1),
            'freeze_binding': binding, 'assessed_packet_payload_sha256':nullable(TEXT),
            'time_utc': TEXT, 'purpose': enum(['experiment','capacity','independent_prelaunch','code_author'])}
    start = object_schema({**base, 'event_kind':{'const':'native_spawn'},
                           'host_spawn_observed':{'const':True}, 'fresh_context':{'const':True}})
    final = object_schema({**base, 'event_kind':{'const':'native_terminal_join'},
                           'terminal_observed':{'const':True},
                           'terminal_witness':{'const':'parent_received_NATIVE_FINAL_ANSWER'},
                           'output_binding': nullable(binding), 'output_payload_sha256':nullable(TEXT),
                           'output_state':enum(['valid','invalid','missing']),
                           'saved_words': {'type':'integer'}, 'first_substantive_save': {'const':True},
                           'scored_retries': {'type':'integer','const':0}})
    return object_schema({'start':start, 'FINAL':final})


WITNESS_SCHEMA = witness_schema()


def validate_native_witness(witness, expected, corpus=None):
    require(not schema_errors(WITNESS_SCHEMA, witness), 'actual parent-observed native start/FINAL exact schema')
    start, final = witness['start'], witness['FINAL']
    shared = ['job_id','study_id','phase','agent_handle','native_call_id','turn','prompt_binding',
              'input_bindings','freeze_binding','assessed_packet_payload_sha256','purpose']
    require(all(identical(start[k], final[k]) for k in shared), 'native start/FINAL binding drift')
    try:
        times = [datetime.fromisoformat(part['time_utc'].replace('Z','+00:00')) for part in (start,final)]
        require(all(t.tzinfo is not None and t.utcoffset()==timezone.utc.utcoffset(t) for t in times), 'native UTC timestamp required')
    except (TypeError,ValueError) as exc:
        raise ValueError('actual native UTC timestamps required') from exc
    require(times[0] < times[1], 'native start precedes parent-observed FINAL')
    require(final['saved_words'] >= 0, 'actual saved word charge')
    for key,value in expected.items():
        require(key in final and identical(final[key], value), 'assigned native ' + key)
    for binding in [start['prompt_binding'], start['freeze_binding'], *start['input_bindings']]:
        normalized(binding['path'])
        require(re.fullmatch('[0-9a-f]{64}',binding['sha256']), 'native binding exact hash')
    if final['output_binding'] is not None:
        normalized(final['output_binding']['path'])
        require(re.fullmatch('[0-9a-f]{64}',final['output_binding']['sha256']) and final['output_state']!='missing', 'actual native output path/hash')
        require(final['output_payload_sha256'] is None and final['output_state']=='invalid' or
                type(final['output_payload_sha256']) is str and re.fullmatch('[0-9a-f]{64}',final['output_payload_sha256']),
                'actual native parsed output hash or unparsed invalid body')
    else:
        require(final['output_state']=='missing' and final['output_payload_sha256'] is None and final['saved_words']==0,
                'actual missing terminal has no output/payload and no saved words')
    if corpus is not None:
        validate_bindings([start['prompt_binding']],corpus)
        validate_bindings([start['freeze_binding']],corpus)
        validate_bindings(start['input_bindings'], corpus)
        if final['output_binding'] is not None:
            validate_bindings([final['output_binding']], corpus)
            output_bytes = corpus[final['output_binding']['path']]
            require(final['saved_words']==len(output_bytes.decode(errors='replace').split()), 'actual native word count/overages bound to bytes')
            try:
                payload_hash = digest(parse_json(output_bytes))
            except (ValueError,UnicodeError,TypeError):
                payload_hash = None
            require(final['output_payload_sha256']==payload_hash, 'actual native parsed payload hash')
            require(final['output_state']!='missing', 'observed output cannot be missing')
        else:
            require(final['output_state']=='missing' and final['output_payload_sha256'] is None and final['saved_words']==0,
                    'explicit observed missing output/null/zero saved words')
    return True


def reconcile_reviews(packet, reviews, observed_native_witnesses):
    require(packet['version']==VERSION and packet['expected_native_rows']==sum(c['expected_native_rows'] for c in packet['cases']) and
            packet['packet_id']=='I13-S-'+digest(packet['cases'])[:24], 'exact whole-shard assessed packet identity/count')
    for case in packet['cases']:
        require(identical(case,fresh_case(case['source_context'],case['D_units'])) and
                digest({k:v for k,v in case['source_context'].items() if k!='context_sha256'})==case['source_context']['context_sha256'],
                'planned fresh obligations/context exact even with invalid/missing review')
    require(len(reviews) == len(observed_native_witnesses) == 2, 'two distinct actual fresh whole-shard reviewers')
    starts = [w.get('start', {}) for w in observed_native_witnesses]
    require(len({w.get('agent_handle') for w in starts}) == 2 and
            len({w.get('native_call_id') for w in starts}) == 2, 'distinct fresh native handles/calls')
    require({w.get('job_id') for w in starts} == set(packet['reviewer_ids']), 'whole scheduled dual reviewer coverage')
    prior_handles = {w['start']['agent_handle'] for c in packet['cases'] for w in
                     c['source_context'].get('native_raw_witnesses',[])}
    prior_handles.update(e['agent_handle'] for c in packet['cases'] for e in
                         c['source_context'].get('native_full_case_history',[]) if 'agent_handle' in e)
    prior_handles.update(u['native_witness']['start']['agent_handle'] for c in packet['cases']
                         for u in c['D_units'] if 'native_witness' in u)
    require(not prior_handles & {w['agent_handle'] for w in starts}, 'fresh reviewers independent from all original/new producers')
    for review, witness in zip(reviews, observed_native_witnesses):
        purpose = 'experiment' if packet['live_admissible'] else 'capacity'
        validate_native_witness(witness, {'purpose':purpose, 'job_id':witness['start']['job_id']})
        require(witness['start']['assessed_packet_payload_sha256']==digest(packet), 'actual native reviewer exact whole shard packet payload')
        D_final_times = [u['native_witness']['FINAL']['time_utc'] for c in packet['cases']
                         for u in c['D_units'] if 'native_witness' in u]
        require(not D_final_times or witness['start']['time_utc'] > max(D_final_times),
                'fresh whole shard review after every D FINAL')
        require(not packet['live_admissible'] or all(not c['source_context']['fictional'] and
                c['source_context']['creation_valid'] for c in packet['cases']), 'fictional/diagnostic context cannot be real experiment')
        if review is not None:
            require(review.get('reviewer_id') == witness['start']['job_id'], 'review assigned observed handle identity')
        out = witness['FINAL']['output_binding']
        if witness['FINAL']['output_state'] == 'missing':
            require(review is None and out is None and witness['FINAL']['output_payload_sha256'] is None,
                    'missing output never inferred from status')
        else:
            require(out is not None and (review is None or witness['FINAL']['output_payload_sha256'] == digest(review)),
                    'exact parsed review payload binding required; actual byte hash witnessed separately')
    complete = all(review is not None and validate_review(packet, review)['valid'] and
                   witness['FINAL']['output_state']=='valid'
                   for review,witness in zip(reviews,observed_native_witnesses))
    cases = []
    for case in packet['cases']:
        rows, disputes = [], []
        bodies = ([next(c for c in r['cases'] if c['case_packet_id']==case['case_packet_id']) for r in reviews]
                  if complete else [None,None])
        for table, obligations in {**case['expected_matrix'], 'source_pairs':case['source_pair_matrix']}.items():
            cols = PAIR_COLUMNS if table=='source_pairs' else FRESH_COLUMNS[table]
            ids = PAIR_COLUMNS[:2] if table=='source_pairs' else FRESH_IDENTITIES[table]
            indexes = []
            for body in bodies:
                items = [] if body is None else body['source_pairs'] if table=='source_pairs' else body['new_review'][table]
                indexes.append({tuple(dict(zip(cols,r))[k] for k in ids): dict(zip(cols,r)) for r in items
                                if type(r) is list and len(r)==len(cols) and all(type(dict(zip(cols,r))[k]) is str for k in ids)})
            for ob in obligations:
                key = tuple(ob['identity'][k] for k in ids)
                values = {**ob['identity'], **ob['fixed_values']}
                statuses = {}
                for field in cols:
                    if field in values or field=='evidence':
                        continue
                    if not complete or ob['null_semantics']:
                        values[field], statuses[field] = None, 'unobservable'
                    elif identical(indexes[0][key][field], indexes[1][key][field]):
                        values[field], statuses[field] = copy.deepcopy(indexes[0][key][field]), 'agreed'
                    else:
                        family = table=='source_pairs' and field=='relation'
                        values[field], statuses[field] = None, 'family_unresolved' if family else 'scalar_unresolved'
                        disputes.append({'table':table, 'row_id':ob['row_id'], 'field':field,
                                         'reviewer_values':[indexes[0][key][field],indexes[1][key][field]],
                                         'scalar_adjudication_allowed':not family})
                values['evidence'] = (' | '.join(body['evidence'] for body in [index[key] for index in indexes])
                                      if complete else 'Fresh dual review invalid/missing; every planned judgment unobservable.')
                rows.append({'table':table, 'row_id':ob['row_id'], 'identity':copy.deepcopy(ob['identity']),
                             'values':values, 'field_status':statuses})
        cases.append({'case_packet_id':case['case_packet_id'], 'case_id':case['case_id'],
                      'carried_raw_rows':copy.deepcopy(case['carried_raw_rows']), 'fresh_rows':rows,
                      'disputes':disputes, 'independent_review_complete':complete,
                      'source_context_sha256':case['source_context']['context_sha256'],
                      'D_units':copy.deepcopy(case['D_units']), 'raw_creation_credit':0})
    return {'version':VERSION, 'packet_id':packet['packet_id'], 'cases':cases,
            'independent_review_complete':complete, 'native_witnesses':copy.deepcopy(observed_native_witnesses),
            'scalar_adjudication':'unused_unless_separately_prospectively_admitted',
            'forced_family_merges':0, 'live_admissible':packet['live_admissible'],
            'meaning_status':'locked_source_bound_model_judgments' if complete else 'gated_incomplete_review'}


def retention_status(row):
    if row is None:
        return 'unobservable'
    if any(s not in RESOLVED for s in row['field_status'].values()):
        return 'uncertain'
    v = row['values']
    if all(v[k]=='retained' for k in ('relation','discriminator','uncertainty')) and all(
            v[k] is True for k in ('lineage_consistent','fit_preserved','complete_protected_fields')):
        return 'retained'
    if any(v[k]=='lost' for k in ('relation','discriminator','uncertainty')) or any(
            v[k] is False for k in ('lineage_consistent','fit_preserved','complete_protected_fields')):
        return 'lost'
    return 'uncertain'


def build_views_and_memberships(source_context, new_locked_preservation):
    context, lock = source_context, new_locked_preservation
    require(lock['source_context_sha256'] == context['context_sha256'] and
            identical(lock['carried_raw_rows'],context['carried_raw_rows']), 'views exact unchanged raw context/carry')
    units = lock['D_units']
    require(len(units)==4, 'views all four planned D units')
    source_rows = {r['identity']['card_id']:r for r in context['carried_raw_rows'] if r['table']=='raw_rows'}
    relations = {frozenset((r['identity']['card_a'],r['identity']['card_b'])):r
                 for r in context['carried_raw_rows'] if r['table']=='candidate_pairs'}
    retentions = {(r['identity']['compressor_id'],r['identity']['source_card_id']):r
                  for r in lock['fresh_rows'] if r['table']=='retention_rows'}
    pairs = {(r['identity']['post_card_id'],r['identity']['source_card_id']):r
             for r in lock['fresh_rows'] if r['table']=='source_pairs'}
    post_rows = {r['identity']['card_id']:r for r in lock['fresh_rows'] if r['table']=='post_rows'}
    lineage_rows = {(r['identity']['unit_id'],r['identity']['source_id']):r
                    for r in lock['fresh_rows'] if r['table']=='lineage_rows'}
    status_rows, membership_rows, details = [], [], []
    for unit in units:
        job, pool = unit['unit_id'], unit['pool']
        producer = context['producers'][pool]
        raw_ids = list(producer['local_to_original'].values())
        pair = relations.get(frozenset(raw_ids)) if len(raw_ids)==2 else None
        unresolved_pair = len(raw_ids)==2 and (pair is None or pair['values']['relation'] not in ('equivalent','parameter','distinct') or
                          any(s not in RESOLVED for s in pair['field_status'].values()))
        merged_family = pair is not None and not unresolved_pair and pair['values']['relation'] in ('equivalent','parameter')
        candidates = []
        for order, source_id in enumerate(raw_ids):
            row = source_rows[source_id]
            v = {k:copy.deepcopy(row['values'][k]) if row['field_status'].get(k) in RESOLVED else None
                 for k in ('fit','usefulness','observability','intelligible','support','novelty','contract','family_confirmed')}
            v.update(id=source_id, family_id=min(raw_ids) if merged_family else source_id,
                     uncertain_links=unresolved_pair, raw_order=order,
                     retention=retention_status(retentions.get((job,source_id))))
            candidates.append(v)
        complete = context['creation_valid'] and lock['independent_review_complete'] and unit['execution']=='valid'
        # Use the audited function literally. Null contract excludes eligibility;
        # it is not in REQUIRED and is never silently imputed to met or zero.
        views = p10.views(candidates, context_complete=complete)
        cards = unit['artifact'].get('openings',[]) if isinstance(unit.get('artifact'),dict) else []
        proposals = unit['artifact'].get('proposals',[]) if isinstance(unit.get('artifact'),dict) else []
        mapped = {}
        for c in cards:
            declared = c.get('source_ids',[])
            declared = declared if type(declared) is list else []
            mapped[qualified(job,c['id'])] = list(dict.fromkeys(producer['local_to_original'][x] for x in declared
                if type(x) is str and x in producer['local_to_original']))
        supported_mapping = True
        for card_id, mapped_sources in mapped.items():
            post = post_rows.get(card_id)
            if (post is None or any(s not in RESOLVED for s in post['field_status'].values()) or
                    post['values']['fit_preserved'] is not True or post['values']['new_assertion'] is not False):
                supported_mapping = False
            for source_id in mapped_sources:
                relation = pairs.get((card_id,source_id))
                lineage = lineage_rows.get((job,source_id))
                # A faithful multi-source carrier can be directly distinct from
                # either single source. Retention and reciprocal lineage own the
                # mapping; direct pair relations never create raw families.
                if relation is None or relation['values']['relation'] not in ('equivalent','parameter','distinct') or any(
                        s not in RESOLVED for s in relation['field_status'].values()):
                    supported_mapping = False
                if (lineage is None or lineage['values']['targets_valid'] is not True or
                        lineage['values']['meaning_consistent'] is not True or any(
                        s not in RESOLVED for s in lineage['field_status'].values())):
                    supported_mapping = False
        if not supported_mapping:
            views = {'status':'not_evaluable', 'cause':'unsupported_or_unresolved_D_source_mapping',
                     'ordinary':None,'alternative':None}
        burdens = {}
        for view_name in VIEWS:
            selected = views[view_name]
            status_rows.append({'view_cell_id':job+'-'+view_name, 'case_id':context['case_id'],
                                'compressor_id':job, 'view':view_name, 'status':views['status'],
                                'source_ids':copy.deepcopy(selected), 'cause':views.get('cause'),
                                'diagnostic_only':context['diagnostic_only'], 'native_judgment_credit':0})
            visible = []
            for card in cards:
                cid = qualified(job,card['id'])
                selected_sources = None if selected is None else [x for x in mapped[cid] if x in selected]
                member = None if selected is None else bool(selected_sources)
                membership_rows.append({'view_cell_id':job+'-'+view_name, 'post_card_id':cid,
                                        'all_source_ids':mapped[cid], 'selected_source_ids':selected_sources,
                                        'member':member, 'raw_family_creation_credit':0})
                if member:
                    visible.append({'post_card_id':cid, 'card':copy.deepcopy(card),
                                    'complete_source_mapping':mapped[cid],
                                    'selected_source_ids':selected_sources})
            burdens[view_name] = None if selected is None else {
                'selected_source_ids':selected, 'displayed_D_carriers':visible,
                'actual_D_carrier_saved_words_proxy':sum(len(json.dumps(x['card'],ensure_ascii=False).split()) for x in visible),
                'source_full_text_saved_words_proxy':sum(len(json.dumps(c,ensure_ascii=False).split()) for c in producer['artifact']['openings']
                    if producer['local_to_original'][c['id']] in selected),
                'selected_scores_and_contracts':[c for c in candidates if c['id'] in selected]}
        details.append({'compressor_id':job, 'pool':pool, 'candidates':candidates, 'views':views,
                        'all_D_source_mapping':mapped, 'burden':burdens,
                        'optional_proposals':[{'post_card_id':qualified(job,c['id']), 'proposal':copy.deepcopy(c),
                                              'inherited_raw_grades':None,'raw_creation_credit':0,
                                              'preservation_credit':0} for c in proposals],
                        'identical_source_sets_by_two_source_design':views['ordinary'] is not None and views['ordinary']==views['alternative']})
    return {'case_id':context['case_id'], 'view_status_rows':status_rows, 'D_membership_rows':membership_rows,
            'details':details, 'native_view_judgment_credit':0,
            'claim':'Deterministic source exposure and actual text burden only; no visual novelty or human benefit established.'}


def fixture_inputs():
    cases = []
    for n in (1,2,3):
        case = f'UNSCORED-F{n}'
        producers = {}
        raw_rows, archive_rows, candidate_rows, unit_rows = [], [], [], []
        for pool in (*POOLS,'generic'):
            job = f'UNSCORED-RAW-{n}-{pool}'
            cards = [{'id':f'R{i}', 'kind':'question', 'claim':f'UNSCORED fictional causal relation {pool}/{i}.',
                      'delta':'Fictional intervention only; no measured discovery.',
                      'prediction':'Fictional rival predicts opposite direction; equality leaves uncertainty.',
                      'probe':'Fictional two-condition probe with strict capacity/stopping caveat; unexecuted.',
                      'fit':'preserves', 'assumptions':['UNSCORED; stipulated synthetic capacity only.'],
                      'source_refs':['valued_outcome']} for i in (1,2)]
            mapping = {c['id']:qualified(job,c['id']) for c in cards}
            producers[pool] = {'job_id':job,'unit_id':job, 'artifact':{'case_id':case,'role':'raw','openings':cards,'assessment':'UNSCORED'},
                               'local_to_original':mapping,'local_to_qualified_producer':mapping,
                               'raw_order':{'R1':0,'R2':1}}
            for cid in mapping.values():
                vals = {'card_id':cid,'intelligible':True,'usefulness':2,'observability':2,'fit':'preserves',
                        'support':'stipulated','novelty':'new','contract':'partial','family_confirmed':True,
                        'evidence':'UNSCORED original fictional locked raw evidence; no actual native raw judgment.'}
                raw_rows.append({'table':'raw_rows','row_id':'E-'+digest(['raw',cid])[:24],
                                 'identity':{'card_id':cid},'values':vals,
                                 'field_status':{k:'agreed' for k in vals if k not in ('card_id','evidence')}})
                for i in range(4):
                    aid = f'UNSCORED-ARCHIVE-{n}-{i}'
                    archive_rows.append({'table':'archive_pairs','row_id':'E-'+digest([cid,aid])[:24],
                        'identity':{'card_id':cid,'archive_id':aid},
                        'values':{'card_id':cid,'archive_id':aid,'relation':'distinct','evidence':'UNSCORED fictional archive distinction.'},
                        'field_status':{'relation':'agreed'}})
            unit_rows.append({'table':'unit_rows','row_id':'E-'+digest(job)[:24],'identity':{'unit_id':job},
                'values':{'unit_id':job,'execution':'valid','no_opening_reason_supported':None,'contract':'met',
                          'evidence':'UNSCORED fictional unit, no real execution.'}, 'field_status':{'contract':'agreed'}})
        for a,b in itertools.combinations([r['identity']['card_id'] for r in raw_rows],2):
            candidate_rows.append({'table':'candidate_pairs','row_id':'E-'+digest([a,b])[:24],
                'identity':{'card_a':a,'card_b':b},'values':{'card_a':a,'card_b':b,'relation':'distinct',
                'evidence':'UNSCORED direct fictional pair; no transitive merge.'},'field_status':{'relation':'agreed'}})
        context = {'case_id':case,'case':{'id':case,'valued_outcome':'UNSCORED capacity shape only.'},
                   'creation_valid':True,'diagnostic_only':False,'fictional':True,
                   'carried_raw_rows':raw_rows+archive_rows+candidate_rows+unit_rows,
                   'producers':producers,'generic_context_preserved':True,
                   'raw_packet':{'epistemic_status':'UNSCORED','criteria':copy.deepcopy(FROZEN_CRITERIA_GENERATION),
                                 'contract':copy.deepcopy(FROZEN_REVIEW_CONTRACT)},
                   'D_semantic_instructions':{
                       comp:build_prompts(FROZEN_COMPRESSION_SOURCE)[f'{PROMPT_DIR}/{comp}.txt'].split('BEGIN_LITERAL_JSON_SCHEMA')[0]
                       for comp in COMPRESSORS},
                   'rubric_binding':{'path':'criteria-generation.v2.json','sha256':ASSIGNED_SOURCE_HASHES['criteria-generation.v2.json']},
                   'raw_admin':{'epistemic_status':'UNSCORED'},
                   'raw_lock':{'epistemic_status':'UNSCORED'},'native_raw_witnesses':[],
                   'old_post_context':{'epistemic_status':'UNSCORED'},'old_post_failure':False,
                   'raw_creation_credit':0}
        context['context_sha256'] = digest(context)
        D_units = []
        for pool,comp in itertools.product(POOLS,COMPRESSORS):
            job = f'I13-{case}-{pool}-{comp}'
            cards = [{'id':f'D{i}','source_ids':['R1','R2'] if i==1 else ['R1'] if i<=3 else ['R2'],
                      'claim':'UNSCORED faithful fictional carrier; no new raw family.',
                      'discriminator':'Preserve both directions, equality uncertainty and all rival defeats.',
                      'fit':'preserves','probe':'UNSCORED strict resource/stop limits; no physical probe.',
                      'uncertainty':'Fictional and unexecuted.'} for i in range(1,7)]
            body = {'case_id':case,'role':'D','openings':cards,
                    'lineage':[{'source_id':f'R{i}','disposition':'merged',
                                'target_ids':[c['id'] for c in cards if f'R{i}' in c['source_ids']],
                                'reason':'UNSCORED full relation/test/resource uncertainty preserved.'} for i in (1,2)],
                    'proposals':[{'id':f'P{i}','claim':'UNSCORED separate proposal.','fit':'uncertain',
                                  'probe':'UNSCORED unexecuted proposal probe.','uncertainty':'No inherited grades.',
                                  'source_gap':'Fictional gap, zero preservation/creation credit.'} for i in (1,2)],
                    'decision':'UNSCORED capacity shape only.'}
            D_units.append({'unit_id':job,'pool':pool,'compressor':comp,'execution':'valid','artifact':body})
        cases.append({'source_context':context,'D_units':D_units})
    return {'classification':'UNSCORED_MEMORY_BUILDER_INPUTS','live_admissible':False,
            'reviewer_ids':['CAPACITY-I13-1','CAPACITY-I13-2'],'cases':cases}


def build_fixture_packet(inputs):
    require(inputs['classification']=='UNSCORED_MEMORY_BUILDER_INPUTS' and inputs['live_admissible'] is False,
            'fictional inputs explicitly UNSCORED')
    contexts = [copy.deepcopy(c['source_context']) for c in inputs['cases']]
    require(all(c['fictional'] is True for c in contexts), 'capacity sources cannot masquerade as original cases')
    packet = build_packet(contexts, {c['source_context']['case_id']:c['D_units'] for c in inputs['cases']},
                          inputs['reviewer_ids'],fixture=True)
    require(len(packet['cases'])==3 and packet['expected_native_rows']==444 and all(
            c['copied_raw_count']==48 and c['new_source_pair_count']==48 and
            sum(c['matrix_counts'].values())==52 for c in packet['cases']), 'complete maximum444 row identities')
    return packet


def fixture_review(packet, reviewer_id):
    """UNSCORED in-memory shape oracle; never saved as a native capacity body."""
    cases = []
    for case in packet['cases']:
        fresh = {'reviewer_id':reviewer_id,'columns':copy.deepcopy(FRESH_COLUMNS),
                 'limits':'UNSCORED memory-only shape; not an actual native capacity judgment.'}
        for table, obligations in case['expected_matrix'].items():
            rows = []
            for ob in obligations:
                values = {**ob['identity'], **ob['fixed_values']}
                for field in FRESH_COLUMNS[table]:
                    if field in values:
                        continue
                    values[field] = ('UNSCORED synthetic shape evidence.' if field=='evidence' else None if ob['null_semantics'] else
                        False if field=='new_assertion' else True if field in frozen.BOOLS else 'retained' if table=='retention_rows' else
                        'met' if field=='contract' else 'preserves' if field=='fit' else
                        'stipulated' if field=='support' else None)
                rows.append([values[k] for k in FRESH_COLUMNS[table]])
            fresh[table] = rows
        pairs = [[o['identity']['post_card_id'],o['identity']['source_card_id'],
                  None if o['null_semantics'] else 'equivalent','UNSCORED pair shape evidence.'] for o in case['source_pair_matrix']]
        cases.append({'case_packet_id':case['case_packet_id'],'carried_raw_rows':copy.deepcopy(case['carried_raw_rows']),
                      'new_review':fresh,'source_pairs':pairs})
    return {'packet_id':packet['packet_id'],'reviewer_id':reviewer_id,'cases':cases}


def fixture_locked_case(case):
    """Fictional preservation lock for deterministic rebuild, no native evidence."""
    review = fixture_review({'cases':[case],'packet_id':'UNSCORED'},'UNSCORED')['cases'][0]
    rows = []
    for table, obligations in {**case['expected_matrix'],'source_pairs':case['source_pair_matrix']}.items():
        cols = PAIR_COLUMNS if table=='source_pairs' else FRESH_COLUMNS[table]
        values = review['source_pairs'] if table=='source_pairs' else review['new_review'][table]
        for ob,row in zip(obligations,values):
            v = dict(zip(cols,row))
            rows.append({'table':table,'row_id':ob['row_id'],'identity':copy.deepcopy(ob['identity']),
                         'values':v,'field_status':{k:'agreed' for k in cols if k not in ob['identity'] and
                                                   k not in ob['fixed_values'] and k!='evidence'}})
    return {'case_id':case['case_id'],'case_packet_id':case['case_packet_id'],
            'source_context_sha256':case['source_context']['context_sha256'],
            'carried_raw_rows':copy.deepcopy(case['carried_raw_rows']),'D_units':copy.deepcopy(case['D_units']),
            'fresh_rows':rows,'independent_review_complete':True,'epistemic_status':'UNSCORED_FICTIONAL_LOCK',
            'live_admissible':False}


def build_complete_fixture(inputs):
    packet = build_fixture_packet(inputs)
    cases = []
    for case in packet['cases']:
        lock = fixture_locked_case(case)
        views = build_views_and_memberships(case['source_context'],lock)
        count = len(lock['carried_raw_rows'])+len(lock['fresh_rows'])+len(views['view_status_rows'])+len(views['D_membership_rows'])
        require(count==204 and len(views['view_status_rows'])==8 and len(views['D_membership_rows'])==48,
                'complete deterministic view/member identities204')
        cases.append({'case_id':case['case_id'],'lock':lock,'views':views,'complete_row_count':count})
    return {'classification':'UNSCORED_PURE_COMPLETE_REPORT_FIXTURE','live_admissible':False,
            'packet_id':packet['packet_id'],'cases':cases,'expected_total_rows':sum(c['complete_row_count'] for c in cases),
            'native_review_rows':444,'deterministic_view_and_membership_rows':168,'raw_creation_credit':0}


def source_closure_required():
    """Exact future audited closure and parent receipt schemas, without I/O.

    Freeze contains sources+author outputs+capacity body/receipt+independent
    receipt. It never includes itself or its downstream admission/phase receipt.
    Admission separately binds that exact freeze and independent receipt.
    """
    base = sorted(set(ASSIGNED_SOURCE_HASHES) | set(OWNED_PATHS))
    paths = sorted(set(base) | {CAPACITY_BODY,CAPACITY_RECEIPT,INDEPENDENT_RECEIPT,INDEPENDENT_BODY,INDEPENDENT_INPUTS})
    phase_paths = sorted({CONTRACT,FREEZE,ADMISSION,INDEPENDENT_RECEIPT,
        'reports/I06-pilot-diagnostic-summary.json','receipts/gates/I06-pilot-lock.json',
        'reports/I06-confirmation-results.json','receipts/gates/I06-confirmation-lock.json',
        'receipts/gates/I09-fidelity-advance.json','receipts/I09-method-mapping.json',
        'receipts/gates/I10-evidence-complete.v4.json','reports/I10-independent-completion-audit.v4.json',
        'contracts/I13-context-design-notes.v1.json',
        *[f'fixtures/generation-raw-first/I06-{case}-raw.json' for case in CASES[2:]],
        *[f'reports/generation-raw-first-locked/I06-{case}-raw.json' for case in CASES[2:]]})
    return {'version':VERSION,'exact_freeze_paths':paths,'immutable_assigned_hashes':copy.deepcopy(ASSIGNED_SOURCE_HASHES),
            'exact_capacity_source_paths':base,
            'exact_independent_source_paths':sorted(set(base)|{CAPACITY_BODY,CAPACITY_RECEIPT,INDEPENDENT_INPUTS}),
            'exact_confirmation_decision_source_paths':phase_paths,
            'excludes_recursive_downstream':[FREEZE,ADMISSION,PHASE_DECISION],
            'capacity_receipt_schema':object_schema({
                'classification':{'const':'structural_capacity_only_not_semantic_adequacy'},
                'study_id':{'const':'I13'}, 'packet_binding':object_schema({'path':{'const':FIXTURE_PACKET},'sha256':TEXT}),
                'output_binding':object_schema({'path':{'const':CAPACITY_BODY},'sha256':TEXT}),
                'native_witness':WITNESS_SCHEMA,'typed_review_valid':{'const':True},
                'expected_native_rows':{'type':'integer','const':444},
                'complete_fixture_rows':{'type':'integer','const':612},
                'source_bindings':array_schema(object_schema({'path':TEXT,'sha256':TEXT}),minimum=1)}),
            'independent_receipt_schema':object_schema({
                'study_id':{'const':'I13'}, 'classification':{'const':'pass'}, 'native_witness':WITNESS_SCHEMA,
                'author_native_witness':WITNESS_SCHEMA,
                'output_binding':object_schema({'path':{'const':INDEPENDENT_BODY},'sha256':TEXT}),
                'source_bindings':array_schema(object_schema({'path':TEXT,'sha256':TEXT}),minimum=1),
                'author_handle':TEXT,'reviewer_handle':TEXT,'literal_prompt_policy_verified':{'const':True},
                'exact_source_reuse_verified':{'const':True},'runtime_mechanics_verified':{'const':True},
                'experimental_admission_claim':{'const':False}}),
            'freeze_schema':object_schema({'version':{'const':VERSION},'study_id':{'const':'I13'},
                'source_bindings':array_schema(object_schema({'path':TEXT,'sha256':TEXT}),minimum=1),
                'independent_receipt_binding':object_schema({'path':{'const':INDEPENDENT_RECEIPT},'sha256':TEXT})}),
            'admission_schema':object_schema({'study_id':{'const':'I13'},'status':{'const':'pass'},
                'freeze_binding':object_schema({'path':{'const':FREEZE},'sha256':TEXT}),
                'capacity_receipt_binding':object_schema({'path':{'const':CAPACITY_RECEIPT},'sha256':TEXT}),
                'independent_receipt_binding':object_schema({'path':{'const':INDEPENDENT_RECEIPT},'sha256':TEXT}),
                'parent_verified':{'const':True},'raw_creation_credit':{'type':'integer','const':0}}),
            'confirmation_decision_schema':object_schema({'study_id':{'const':'I13'},'phase':{'const':'confirmation'},
                'status':{'const':'pass'},'case_ids':{'const':list(CASES[2:])},
                'pilot_creation_valid':{'const':False},'pilot_D_skipped':{'type':'integer','const':8},
                'pilot_reviews_gated':{'type':'integer','const':2},'pilot_views_gated':{'type':'integer','const':16},
                'informative_original_four_block_justification':TEXT,
                'independent_source_bound_verification':{'const':True},
                'source_bindings':array_schema(object_schema({'path':TEXT,'sha256':TEXT}),minimum=1)})}


def ready(parent_receipts, corpus):
    """No mutating operation can run without this exact external evidence."""
    closure = source_closure_required()
    for ref in (CAPACITY_RECEIPT,INDEPENDENT_RECEIPT,FREEZE,ADMISSION,PHASE_DECISION):
        require(ref in parent_receipts and ref in corpus and
                identical(parse_json(corpus[ref]),parent_receipts[ref]), 'required parent receipt ' + ref)
    cap, independent, freeze, admission, decision = [parent_receipts[r] for r in
        (CAPACITY_RECEIPT,INDEPENDENT_RECEIPT,FREEZE,ADMISSION,PHASE_DECISION)]
    for body,key in [(cap,'capacity_receipt_schema'),(independent,'independent_receipt_schema'),
                     (freeze,'freeze_schema'),(admission,'admission_schema'),(decision,'confirmation_decision_schema')]:
        require(not schema_errors(closure[key],body), 'exact parent receipt schema ' + key)
    validate_bindings(freeze['source_bindings'],corpus,closure['exact_freeze_paths'])
    validate_bindings([{'path':p,'sha256':h} for p,h in ASSIGNED_SOURCE_HASHES.items()],corpus)
    for body,expected_paths in [(cap,closure['exact_capacity_source_paths']),
        (independent,closure['exact_independent_source_paths']),
        (decision,closure['exact_confirmation_decision_source_paths'])]:
        validate_bindings(body['source_bindings'],corpus,expected_paths)
    for receipt_binding in [freeze['independent_receipt_binding'], admission['freeze_binding'],
                            admission['capacity_receipt_binding'],admission['independent_receipt_binding']]:
        validate_bindings([receipt_binding],corpus)
    validate_native_witness(cap['native_witness'],{'purpose':'capacity','phase':'capacity','output_binding':cap['output_binding']},corpus)
    validate_native_witness(independent['native_witness'],{'purpose':'independent_prelaunch','agent_handle':independent['reviewer_handle']},corpus)
    validate_native_witness(independent['author_native_witness'],{'purpose':'code_author','agent_handle':independent['author_handle'],
        'output_binding':{'path':CHECK,'sha256':digest(corpus[CHECK])}},corpus)
    require(cap['native_witness']['start']['time_utc'] > independent['author_native_witness']['FINAL']['time_utc'] and
            independent['native_witness']['start']['time_utc'] > cap['native_witness']['FINAL']['time_utc'],
            'actual author FINAL precedes native capacity; capacity FINAL precedes independent native review')
    validate_bindings([independent['output_binding']],corpus)
    independent_body = parse_json(corpus[INDEPENDENT_BODY])
    require(not schema_errors(INDEPENDENT_BODY_SCHEMA,independent_body) and independent_body['classification']=='pass' and
            all(independent_body['checks'].values()) and not any(x['severity']=='blocking' for x in independent_body['findings']),
            'actual independent complete passing body')
    require(independent['native_witness']['FINAL']['output_binding']==independent['output_binding'] and
            independent['native_witness']['FINAL']['output_payload_sha256']==digest(independent_body) and
            independent['native_witness']['start']['prompt_binding']['path']==f'{PROMPT_DIR}/independent-prelaunch.txt',
            'actual independent exact prompt/body/FINAL')
    require(independent['reviewer_handle'] != independent['author_handle'] and
            independent['reviewer_handle'] != cap['native_witness']['start']['agent_handle'], 'separate fresh independent prelaunch reviewer')
    packet = parse_json(corpus[FIXTURE_PACKET])
    inputs = parse_json(corpus[FIXTURE_INPUTS])
    require(identical(packet,build_fixture_packet(inputs)) and
            identical(parse_json(corpus[FIXTURE_COMPLETE]),build_complete_fixture(inputs)), 'pure444/612 fixture rebuild')
    require(validate_review(packet,parse_json(corpus[CAPACITY_BODY]))['valid'], 'actual native maximal typed444 output')
    require(cap['native_witness']['FINAL']['output_payload_sha256']==digest(parse_json(corpus[CAPACITY_BODY])) and
            cap['native_witness']['start']['assessed_packet_payload_sha256']==digest(packet) and
            cap['native_witness']['start']['job_id']=='CAPACITY-I13-1' and
            cap['native_witness']['start']['prompt_binding']['path']==f'{PROMPT_DIR}/maximal-capacity.txt' and
            FIXTURE_PACKET in {x['path'] for x in cap['native_witness']['start']['input_bindings']},
            'actual fresh native capacity current schema/packet/prompt/output payload witness')
    require(cap['packet_binding']['sha256']==digest(corpus[FIXTURE_PACKET]), 'capacity exact packet binding')
    for case in CASES[2:]:
        source_context(case,corpus)
    require(parse_json(corpus['receipts/gates/I09-fidelity-advance.json'])['status']=='pass' and
            parse_json(corpus['receipts/gates/I10-evidence-complete.v4.json'])['status']=='pass', 'I09 fidelity/I10 audited view readiness')
    return {'ready':True,'study_id':'I13','phase':'confirmation','pilot_trial_calls':0}


def prepare_D(job_id, parent_receipts, corpus, lifecycle):
    ready(parent_receipts,corpus)
    schedule,_ = build_schedule()
    job = next((j for j in schedule['jobs'] if j['job_id']==job_id),None)
    require(job is not None and job['phase']=='confirmation', 'original diagnostic pilot cannot prepare/start')
    require(job_id not in lifecycle, 'first preparation only; zero retries')
    context = source_context(job['case_id'],corpus)
    validate_source_reuse(context,context)
    source = context['producers'][job['pool']]
    require(source['job_id']==job['original_raw_job_id'], 'assigned exact raw producer')
    prompts = build_prompts(corpus['prompts/generation-v2/compression.txt'].decode())
    require(corpus[job['prompt_ref']].decode()==prompts[job['prompt_ref']], 'ordinary/source-bound literal instruction mismatch')
    used_handles = {e['agent_handle'] for e in context['native_full_case_history'] if 'agent_handle' in e}
    used_handles.update(parent_receipts[INDEPENDENT_RECEIPT][k] for k in ('author_handle','reviewer_handle'))
    used_handles.add(parent_receipts[CAPACITY_RECEIPT]['native_witness']['start']['agent_handle'])
    used_handles.update(s['start']['agent_handle'] for s in lifecycle.values() if 'start' in s)
    used_calls = {s['start']['native_call_id'] for s in lifecycle.values() if 'start' in s}
    return {'job':copy.deepcopy(job),'state':'prepared','study_id':'I13','phase':'confirmation',
            'source_context_sha256':context['context_sha256'],'prompt_binding':{'path':job['prompt_ref'],'sha256':digest(corpus[job['prompt_ref']])},
            'input_bindings':[{'path':p,'sha256':digest(corpus[p])} for p in job['input_refs']],
            'freeze_binding':{'path':FREEZE,'sha256':digest(corpus[FREEZE])},
            'used_agent_handles':sorted(used_handles),'used_native_call_ids':sorted(used_calls)}


def native_start(prepared, witness, parent_receipts, corpus):
    ready(parent_receipts,corpus)
    require(prepared['state']=='prepared', 'one fresh prepared native start')
    require(not schema_errors(WITNESS_SCHEMA['properties']['start'],witness), 'actual native host start exact schema')
    for key in ('prompt_binding','input_bindings','freeze_binding'):
        require(identical(witness[key],prepared[key]), 'prepared/start binding ' + key)
    validate_bindings(witness['input_bindings'],corpus)
    require(witness['job_id']==prepared['job']['job_id'] and witness['phase']=='confirmation' and
            witness['purpose']=='experiment', 'exact prospective native role')
    require(witness['assessed_packet_payload_sha256']==prepared.get('packet_payload_sha256'),
            'exact assigned whole shard packet payload before native review')
    require(witness['agent_handle'] not in prepared['used_agent_handles'] and
            witness['native_call_id'] not in prepared['used_native_call_ids'], 'fresh native handle/call cannot reuse prior context')
    return {**copy.deepcopy(prepared),'state':'started','start':copy.deepcopy(witness)}


def native_join(started, final, output_bytes, parent_receipts, corpus):
    ready(parent_receipts,corpus)
    require(started['state']=='started', 'actual started role terminal once')
    witness = {'start':started['start'],'FINAL':final}
    validate_native_witness(witness,{'job_id':started['job']['job_id'],'purpose':'experiment'})
    if output_bytes is None:
        require(final['output_binding'] is None and final['output_payload_sha256'] is None and
                final['output_state']=='missing', 'explicit observed missing terminal')
        body,valid = None,False
    else:
        require(type(output_bytes) is bytes and final['output_binding'] ==
                {'path':started['job']['output_ref'],'sha256':digest(output_bytes)}, 'actual first-save native output bytes/hash')
        require(final['saved_words']==len(output_bytes.decode(errors='replace').split()), 'actual words charged incl overage')
        try:
            body = parse_json(output_bytes)
        except (ValueError,TypeError,UnicodeError):
            require(final['output_payload_sha256'] is None, 'unparsed invalid JSON cannot claim a parsed payload hash')
            body,valid = None,False
        else:
            require(final['output_payload_sha256']==digest(body), 'actual parsed output payload hash')
            if started['job']['role']=='D':
                context = source_context(started['job']['case_id'],corpus)
                valid = validate_D(started['job']['case_id'],context['producers'][started['job']['pool']]['artifact'],body)['valid']
            else:
                valid = validate_review(started['packet'],body)['valid']
        require(final['output_state']==('valid' if valid else 'invalid'), 'terminal structural state derives from actual bytes')
    return {**copy.deepcopy(started),'state':final['output_state'],'artifact':body,
            'output_bytes_sha256':None if output_bytes is None else digest(output_bytes), 'native_witness':witness,
            'saved_words':final['saved_words'],
            'overage_words':max(0,final['saved_words']-started['job']['soft_saved_word_limit']), 'scored_retries':0}


def save_first(path, data, parent_receipts, corpus, started):
    """Future runtime first-save: guarded, no replacement, no retries/events."""
    ready(parent_receipts,corpus)
    path = normalized(path)
    schedule,reviews = build_schedule()
    allowed = {j['output_ref'] for j in schedule['jobs']+reviews['jobs'] if j['phase']=='confirmation'}
    require(path in allowed, 'exact admitted scheduled first-substantive output only')
    require(started['state']=='started' and started['job']['output_ref']==path,
            'only exact actual native started role may first-save')
    require(not schema_errors(WITNESS_SCHEMA['properties']['start'],started['start']), 'actual fresh native start required')
    target = ROOT / path
    require(target.resolve().is_relative_to(ROOT.resolve()), 'no symlink escape')
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return {'path':path,'sha256':digest(data)}


def prepare_review(job_id, parent_receipts, corpus, lifecycle):
    """Review the whole fixed shard after every assigned D terminal disposition."""
    ready(parent_receipts,corpus)
    schedule,review_schedule = build_schedule()
    job = next((j for j in review_schedule['jobs'] if j['job_id']==job_id),None)
    require(job is not None and job['phase']=='confirmation' and job_id not in lifecycle,
            'first scheduled confirming review only; original pilot administratively gated')
    units = {case:[] for case in job['case_ids']}
    for dependency in job['depends_on']:
        require(dependency in lifecycle and lifecycle[dependency]['state'] in ('valid','invalid','missing','skipped'),
                'all planned D terminal dispositions before fresh review')
        terminal = lifecycle[dependency]
        djob = next(j for j in schedule['jobs'] if j['job_id']==dependency)
        if terminal['state']=='skipped':
            require(terminal.get('parent_dependency_skip') is True and terminal.get('cause'),
                    'source-bound parent skip disposition required')
        else:
            validate_native_witness(terminal['native_witness'],{'purpose':'experiment','job_id':dependency},corpus)
        units[djob['case_id']].append({'unit_id':dependency,'pool':djob['pool'],
                                     'compressor':djob['compressor'],'execution':terminal['state'],
                                     'artifact':terminal.get('artifact'),
                                     **({'native_witness':copy.deepcopy(terminal['native_witness'])}
                                        if terminal['state']!='skipped' else
                                        {'parent_dependency_skip':True,'cause':terminal['cause'],
                                         'source_context_sha256':source_context(djob['case_id'],corpus)['context_sha256']})})
    contexts = [source_context(case,corpus) for case in job['case_ids']]
    shard_jobs = [j for j in review_schedule['jobs'] if j['case_ids']==job['case_ids']]
    packet = build_packet(contexts,units,[j['reviewer_id'] for j in shard_jobs])
    used_handles = {e['agent_handle'] for c in contexts for e in c['native_full_case_history'] if 'agent_handle' in e}
    used_handles.update(s['start']['agent_handle'] for s in lifecycle.values() if 'start' in s)
    used_handles.update(parent_receipts[INDEPENDENT_RECEIPT][k] for k in ('author_handle','reviewer_handle'))
    used_handles.add(parent_receipts[CAPACITY_RECEIPT]['native_witness']['start']['agent_handle'])
    inputs = [{'path':p,'sha256':digest(corpus[p])} for p in (PACK,EXTENSION,CONTRACT)]
    packet_bytes = (json.dumps(packet,indent=2,ensure_ascii=False)+'\n').encode()
    inputs.append({'path':job['packet_ref'],'sha256':digest(packet_bytes)})
    inputs.extend({'path':lifecycle[d]['job']['output_ref'],'sha256':lifecycle[d]['output_bytes_sha256']}
                  for d in job['depends_on'] if lifecycle[d]['state'] in ('valid','invalid'))
    return {'job':copy.deepcopy(job),'state':'prepared','study_id':'I13','phase':'confirmation',
            'packet':packet,'prompt_binding':{'path':job['prompt_ref'],'sha256':digest(corpus[job['prompt_ref']])},
            'input_bindings':inputs,
            'freeze_binding':{'path':FREEZE,'sha256':digest(corpus[FREEZE])},
            'packet_payload_sha256':digest(packet),'used_agent_handles':sorted(used_handles),
            'used_native_call_ids':sorted({s['start']['native_call_id'] for s in lifecycle.values() if 'start' in s})}


def save_review_packet(prepared, parent_receipts, corpus):
    """Future parent first-save of the shared exact packet, after D terminals."""
    ready(parent_receipts,corpus)
    require(prepared['state']=='prepared' and prepared['job']['role']=='preservation_review' and
            prepared['job']['phase']=='confirmation', 'only admitted fresh confirming shard packet')
    require(digest(prepared['packet'])==prepared['packet_payload_sha256'], 'exact prepared packet payload')
    validate_live_packet_sources(prepared['packet'],corpus)
    path = normalized(prepared['job']['packet_ref'])
    require(path in {j['packet_ref'] for j in build_schedule()[1]['jobs'] if j['phase']=='confirmation'},
            'exact scheduled packet path')
    body = (json.dumps(prepared['packet'],indent=2,ensure_ascii=False)+'\n').encode()
    result = {'path':path,'sha256':digest(body)}
    require(result in prepared['input_bindings'], 'parent prepared packet byte binding')
    if path in corpus:
        require(corpus[path]==body, 'shared second reviewer must reuse same exact first packet')
        return result
    target=ROOT/path
    require(target.resolve().is_relative_to(ROOT.resolve()), 'no packet symlink escape')
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as stream:
        stream.write(body);stream.flush();os.fsync(stream.fileno())
    return result


def lock_reviews(packet, reviews, witnesses, parent_receipts, corpus):
    ready(parent_receipts,corpus)
    require(packet['live_admissible'] is True, 'fictional capacity cannot create live lock')
    validate_live_packet_sources(packet,corpus)
    for witness in witnesses:
        validate_native_witness(witness,{'purpose':'experiment'},corpus)
    return reconcile_reviews(packet,reviews,witnesses)


def validate_live_packet_sources(packet, corpus):
    """Fresh D objects require their own actual native current source witnesses."""
    require(packet['live_admissible'] is True and
            tuple(c['case_id'] for c in packet['cases']) in SHARDS[1:], 'exact original confirming shard only')
    jobs={j['job_id']:j for j in build_schedule()[0]['jobs']}
    for case in packet['cases']:
        expected=source_context(case['case_id'],corpus)
        require(validate_source_reuse(expected,case['source_context'])['valid'], 'exact original reuse before packet/lock')
        require(identical(case,fresh_case(case['source_context'],case['D_units'])), 'fresh packet derives actual D obligations')
        for unit in case['D_units']:
            require(unit['unit_id'] in jobs, 'current scheduled D object only')
            job=jobs[unit['unit_id']]
            if unit['execution']=='skipped':
                require(unit.get('parent_dependency_skip') is True and type(unit.get('cause')) is str and unit['cause'] and
                        unit.get('source_context_sha256')==expected['context_sha256'], 'exact parent dependency skip; no native call')
                continue
            require('native_witness' in unit, 'fresh D cannot adopt old post artifact or file-only inference')
            validate_native_witness(unit['native_witness'], {'job_id':unit['unit_id'],'phase':'confirmation','purpose':'experiment',
                'assessed_packet_payload_sha256':None,
                'prompt_binding':{'path':job['prompt_ref'],'sha256':digest(corpus[job['prompt_ref']])},
                'input_bindings':job['input_bindings'],
                'freeze_binding':{'path':FREEZE,'sha256':digest(corpus[FREEZE])},
                'output_state':unit['execution']},corpus)
            final=unit['native_witness']['FINAL']
            if unit['execution']!='missing':
                require(final['output_binding']['path']==job['output_ref'], 'exact fresh D output path')
                try:body=parse_json(corpus[job['output_ref']])
                except (ValueError,UnicodeError):body=None
                assessed=unit.get('unassessable_original_artifact',unit.get('artifact'))
                require(identical(body,assessed), 'actual new D body byte/payload source binding')
    return True


def planned_view_dispositions(source_contexts, locked_cases):
    """Always cover all48 cells, including16diagnostic cells and empty/gated sets."""
    schedule,_ = build_schedule()
    actual = {}
    for context in source_contexts:
        if context['case_id'] in locked_cases:
            report = build_views_and_memberships(context,locked_cases[context['case_id']])
            actual.update({r['view_cell_id']:r for r in report['view_status_rows']})
    return [actual.get(cell['job_id'], {'view_cell_id':cell['job_id'],'case_id':cell['case_id'],
            'compressor_id':cell['D_job_id'],'view':cell['view'],'source_ids':None,
            'status':'not_evaluable','cause':'original_temporal_pilot_diagnostic' if cell['phase']=='pilot' else
            'missing_fresh_dual_preservation_lock','diagnostic_only':cell['phase']=='pilot','native_judgment_credit':0})
            for cell in schedule['view_cells']]


# Exact immutable author input union is installed below during preparation.
ASSIGNED_SOURCE_HASHES = {'EXPERIMENT-PROFILE.md': '27bb9e98eeecdf53cc55f77792f7128dc90fd163125350f91b0e0fd1ba525787', 'I10-exposure-schedule.v4.json': 'cbe00e7be45fc73af596f701192a0d9da3cf21ebca6e9b38529a53bc7b62b2e4', 'RUN.md': 'c8468538917f657c797d95dc18484680ee3d4341d6c70e4be193d9b325dcc576', 'archives/case-archives.json': 'a0e5ded7ba994a44c7d530aac681c81d260a98f3ba0a1d743a5b3fe2bf054720', 'cases/A-C1.json': '026905a4cffecc792dae3ae9e2dbff7644670f663da00662318f589cad091f5c', 'cases/A-C2.json': 'a666cefab6b0b63e850c0353045ddeef57d4d38dd8c481590910d40a82137de9', 'cases/A-P.json': 'bd596809f5d9930e93be1ef72b8a5ebfca4ec50dd7357627426db8ba8015645a', 'cases/H-C1.json': '050c271a3595dc3a964f63cd1bf95dfe9342cfbbfb2130bde762bfff8d1fc365', 'cases/H-C2.json': '145aec3f58a9c898599bad1ed6a5f7b1fd7bd397fe32b67ecf81cf522af72a6c', 'cases/H-P.json': '61ab55d6d7a9df67dbfe739a9d12f0f138840441dcca09252ec8745507e4eeaf', 'cases/case-bank.json': 'd519938ed680972939c959041843065834b5b9c29e979443bf93601b10806cb1', 'completion-requirements.json': '66c65b2be0f48a95a2e654f8bd70dba11f97a3498645ed9f279de905996b1d97', 'composition-assessment.draft.json': '657a1b7425b93863e96bed34ae4539bb06992da2da6faac7cf62d1072ea81bad', 'composition-i11-reviews.draft-v2.json': 'be74f5943ff9af472daea02d17562ce65a278b6d9b45c8390f1e91c293bf25a7', 'composition-i11-schedule.draft-v2.json': '1b32999f8e4b267752526197083a304d38f857e7e826bf0ac72d870262ac0e8e', 'composition-schedule.draft.json': '8bce429da74e5a8f1edc3a5209671de032a8a26a55f3cd37e216c58c9deb8756', 'contracts/I12-native-preparation-contract.v1.json': '00a5cd461760042ba4cc9648c88d9290e614afa0c6f0e30741e1a4f17326f65c', 'contracts/I13-context-design-notes.v1.json': 'c7d3679270643003c8a803b9484922ba1ca25db351e8c62be6d1ecee1a287603', 'contracts/I13-native-preparation-contract.v1.json': '93bfc31aac7edc00b3a63d846a1de16a83e5ceb594b3dda6cb68efddd315765d', 'criteria-generation.v2.json': '02c18895930a2d1c373206dad2f6bcb828b2f3b7133dd355624f888195c4e1d6', 'criteria.json': '6e6a6f2926b948d4bac43d773c9ca7653a3b64aaf43f72241749581034ccdce4', 'design/generation-raw-first-reviewed-round1/blind_generation_raw_first.py': '726a7be8cc4d0817c4765597041b9a6882154d5970e2e06f5fb44e4704832979', 'design/generation-raw-first-reviewed-round1/generation_raw_first_runtime.py': '91024ec2783971a3faa8bd8c4fa637fc5479d89ae9bd8c6d2d60332767ded690', 'design/generation-raw-first-reviewed-round1/generation_review_validation_raw_first.py': '117e7d4f2862c2ae1e0e5a2eaa098d315e6f7a4e5c95949cf02cb61880666093', 'design/generation-raw-first-successor.draft.json': 'e5c3bf8c952b00e809367ed2204bb844b1e0f9559dca841457ea7d905d3f18d5', 'design/generation-v2-final-repair.json': '7b8075d7db41bb7959e61a96b96b002f2260f1b8648ce0a9a314207afd367ce3', 'fixtures/D-H028.json': '8b59dcdd70316aba2d1e720b437bf34375720c9fcb06f1709f3c067c40a4cb98', 'fixtures/D-K2.json': '33b82cd08bdad5fd0444b20b6523c25974e61d60f101aafcaa7e49e0071c2918', 'fixtures/FA-C1.json': 'ab08a3a63b1211dfe316b62a5c60df1329893f7e8c5bbb2ea36cb9a64955cec7', 'fixtures/FA-C2.json': '075a0238254de1f7016372c23196e9f5c813dbec6f743aebf4f8473ae5d69bd6', 'fixtures/FA-P1.json': 'bcb18eadc2a32979843c8ce04c62746a20cb744ccd7bc73448bffdefa0d2018b', 'fixtures/FA-P2.json': '8b10b4df0636b375393b605fa8547895117fafd78cc44da70bc8d53d1d6d8706', 'fixtures/FH-C1.json': 'c6fa715f0e4612023573c0e84c2fa10eba1e8bbf34133c676fd70f8b3ba8438d', 'fixtures/FH-C2.json': '205323b7c5bf752a56f444ebac67cd13bcbdf3045bb1b0b19e064cbf798c8d21', 'fixtures/FH-P1.json': '06485a6435ec03ae67d5247a4c1780b9bba8357d5d81f67565bac6653e01e32a', 'fixtures/FH-P2.json': '2a8542d41361f8d7e06d73537a7cbcc03a9a87e707a39effa91731e686e865cc', 'fixtures/I01-adjudication-packet.json': 'ae08dbadad3842f3c7d18fa702d845773bf3ba31ea16ec66795145c41af9cf6a', 'fixtures/calibration-items.json': '0a542250de96a73e0989e698a722e90cc810fd5c3dcfda9743e99f9de3a011c9', 'fixtures/calibration-key.json': 'a14656073ed31b9cfc6b63b24a3ebf9ca017419c6aac25d8afc4b3af0d1f7652', 'fixtures/composition-i11-maximal-inputs.v2.json': '051c4cdea6b05749feb60422f180f477690c13812bae75c7260c08ce25007dff', 'fixtures/composition-i11-maximal-raw.v2.json': '04bccbb4f77164996caeb7b119440bbf6523c974c7bff198e50a4ebe39ab0e01', 'fixtures/fresh-compression-packets.json': '082e116f34be2683285aa4ded050aba3af460f3f6c73fbfd4333c63026c70549', 'fixtures/generation-blind-opaque/J-1e95a237f2b5fa924678.json': 'f4a3101ccb98dfc7599f490360db93d0ee991b513eb4d1e8b22f94b304cbe852', 'fixtures/generation-blind-opaque/J-e366c56698f5bc38c090.json': '96a94b694e59468173ee5d8254e0d9326f24cb06d928862175d199606d240a56', 'fixtures/generation-blind/I06-A-P.json': '96a94b694e59468173ee5d8254e0d9326f24cb06d928862175d199606d240a56', 'fixtures/generation-blind/I06-H-P.json': 'f4a3101ccb98dfc7599f490360db93d0ee991b513eb4d1e8b22f94b304cbe852', 'fixtures/generation-capacity-v2.json': '34e6ff19c626e88ae4ff196deff2db2158280cdc68ec5afb856b428911de82ac', 'fixtures/generation-raw-first-opaque/J-0ab2b401c3dee2ce2b01.json': '30642384f0514c3ee355454b50f736491e6d7c1bf7dc5ac1b0de3ca36de45cbf', 'fixtures/generation-raw-first-opaque/J-32b71b5a3624ae9de14f.json': '33b8ada197479e569e32581ae85a164e4e072f55103654434a6227a0612e6e87', 'fixtures/generation-raw-first-opaque/J-3dcb1db062c8daab475c.json': '7b63be1ba53ab974d67e343c693e4317457e4d448db6ba517c3de88e25c9f3dd', 'fixtures/generation-raw-first-opaque/J-49f6a29d61a196c57fba.json': 'ca29f3d215e9b6d080442f088963e6e19e8dea950034dbe019e2502698717668', 'fixtures/generation-raw-first-opaque/J-5ba6460ae3e9dc9f6a1d.json': '73e2cc60ef8ce1a5a1a360949b62ac985bbe6f278eb97cf29848573ef3777cb3', 'fixtures/generation-raw-first-opaque/J-630df3b297ce727e5d28.json': 'a044de8e09dd53bd237f2dd8b6ce7bb3e5d475e485043de199b620ca0368e1bb', 'fixtures/generation-raw-first-opaque/J-83ff91e2984aef7036d2.json': 'b65090a12b1e3acac5f7897772cc19b6781eaaef9f8f6f703963eddff52aa0e2', 'fixtures/generation-raw-first-opaque/J-b6a292f824d8090341e4.json': 'de5e03130dc33ebf7777bdecaaacda8557db14ff5527e9325f4a31e31a6f4e17', 'fixtures/generation-raw-first/I06-A-C1-post.json': 'de5e03130dc33ebf7777bdecaaacda8557db14ff5527e9325f4a31e31a6f4e17', 'fixtures/generation-raw-first/I06-A-C1-raw.json': 'a044de8e09dd53bd237f2dd8b6ce7bb3e5d475e485043de199b620ca0368e1bb', 'fixtures/generation-raw-first/I06-A-C2-post.json': '73e2cc60ef8ce1a5a1a360949b62ac985bbe6f278eb97cf29848573ef3777cb3', 'fixtures/generation-raw-first/I06-A-C2-raw.json': '7b63be1ba53ab974d67e343c693e4317457e4d448db6ba517c3de88e25c9f3dd', 'fixtures/generation-raw-first/I06-H-C1-post.json': '33b8ada197479e569e32581ae85a164e4e072f55103654434a6227a0612e6e87', 'fixtures/generation-raw-first/I06-H-C1-raw.json': 'ca29f3d215e9b6d080442f088963e6e19e8dea950034dbe019e2502698717668', 'fixtures/generation-raw-first/I06-H-C2-post.json': 'b65090a12b1e3acac5f7897772cc19b6781eaaef9f8f6f703963eddff52aa0e2', 'fixtures/generation-raw-first/I06-H-C2-raw.json': '30642384f0514c3ee355454b50f736491e6d7c1bf7dc5ac1b0de3ca36de45cbf', 'fixtures/raw-first-capacity-inputs.json': 'c357e219cd11b944c14ed4ef2e95fbc00233c4de476f95e0f0cedce5b489058b', 'fixtures/raw-first-capacity-post-lock.json': '761f28476da041f35e02ce5d41c1615d90fae518bbffd2f78ba12a66c3f328cd', 'fixtures/raw-first-capacity-post-raw.json': 'b23333217a8dc5e185987ede9bc080beba2d03a2678864a3962b3fb3d6fca651', 'fixtures/raw-first-capacity-post.json': '46e876acf9fa116d3613d8fcfbb0810b74b0be24f5e418a3cad9bca56ae1ef17', 'fixtures/raw-first-capacity-raw.json': '6e7034558e66430b447655da08fc8b295623aca8787ecaaedf432e3bf9267f55', 'freeze-I10-exposure.v4.json': 'f522800fea314934b5b21b34ab8211a9cd1e0fc7dc93dba072d677031d9454e5', 'freeze-I11-native.v3.json': 'f3d881176cd0bc0f76603c72dded9431ff6a333a116b0427c42da0a19a0add39', 'freeze-generation-adjudication-v2.json': '42144d9e8910b49e4715531ce9dc89799fb2a04c2731e234fe93da6c7da2b029', 'freeze-generation-raw-first.json': '459b131d1e523636c00abd663e97ddecf07cf752f28c7f5a18f6b4df2ac0afc1', 'freeze-generation-v2.json': 'f0c15a5fd35be889b042a4e176af570741f8dc509751137221887ef8bdc509f6', 'freeze-precompression-addendum.json': '223eb226ca45b3b49c79946386191ffe5d69fcda24d972ea716054bdac9efa0f', 'freeze-wave1.json': '50a296751b54088db611f479c4dd9b4d61970c36f84e3e298f998392c840f6a9', 'generation-adjudication-contract.v2.json': '90051ef9c03e7283d1541646ff4c447e97df6b21897fd364aaa5124d615037e7', 'generation-review-contract.v2.json': '57b77f25a917784fe888d59e10ba761b6d2202acc794dfd49efdd102bb878d4c', 'generation-review-schedule.raw-first.json': '5c20a762d3bc15396f2104dccc9f75a167fd42b1c344e6e67cfcbc7224678629', 'generation-review-schedule.v2.json': '5e92613d47ddef10ba09fc97ee255570219d7fe6c49e40321cc54d186127724f', 'generation-schedule.v2.json': '14d54e7d492c29ab0979ffa87c3eb9bf754feda7a42804e47132b4edb51c1fa7', 'inputs/H028-A.json': '309f089cfcd59d3f9d986ae9fdf2123cddceabb0349c30c3c4c44cf2220bc57c', 'inputs/H028-Z.json': '975631391476278f70ed9379cb95ab7d8a4b66226dac1f6d9e706bf499c79d14', 'inputs/H028-case.json': 'cfd391c5761adc9c3c771c1eb417c8c4e5d1017ddadc6d99625fcbd27fa280d9', 'inputs/K2-case.json': '423b3449bfa63944f6aaf1a813fc547ce8c634cbfde98457d8e2ec674759292d', 'inputs/K2-raw.json': 'fccbf0030c6d9c39c0c4f24283893d025621688d83c55558b3a7d526db2f603e', 'inputs/d-old-P09.txt': '555c6c65c832bc879089d7ef65a373cad95e5df15da6be0957763e99dfa70ea0', 'inputs/d-ordinary.txt': 'db78be51f4082de28fe8824771239f7e6f663e42b61d5691a684757310c90b92', 'inputs/diagnostic-bindings.json': '95746abb36688643b305e3926f3200623b6b1acb67445eace7c62a2257f3970e', 'inputs/plan/CLOSURE.md': '0cff3e06a0bb94121c18ff97632c0d533d67f592a668ed8012964d0aafbe6fec', 'inputs/plan/PLAN.md': 'e0f17a86051813f5395181b02aa0bb7a9f1ee27b765026b72857418f803f07ff', 'inputs/plan/SOURCES.json': 'ecfa158407834de29cba0ce406007c3e59db545faa7aeb73bd6b8b46be1a65df', 'inputs/plan/freeze-manifest.json': 'd34c7b8ef68d011142b215950a51a9802d105bb3efb31e07469410b994aa2941', 'inputs/plan/future.dispatch.json': '2dc876de0d03ad71ca1bd149c01556eb8107ef94e789e97d9529648ce04c8c79', 'inputs/plan/portfolio.json': '6c8c766cf2ce8bb53f5f53d7285a51ded7b7f5c4953844610a0d7783a6f8967b', 'inputs/prior-criteria.json': '90e37783fa13f0c5859ccaddd1a27bfec379ae821a008908e7ca0b7c0dbe4621', 'inputs/prior-strategy-contracts.json': '2dc9a964b6ec015a0c08628855774c6143bbb65dacd4cc4a95b1fbe055a0eff1', 'outputs/generation/G0235.json': '0608df942e7ec800f2b948502e6caa43e344f29d1bf7d7a4637c66089d47f161', 'outputs/generation/G0236.json': '974d729d4ff4d4bf53eaca98b39090216a4131dad2600d732b933fefad2f08de', 'outputs/generation/G0237.json': '7056072b29b3cb35a305da0e31271359ba07a3b9df3c854d9a2549535e2a7e11', 'outputs/generation/G0238.json': 'cd40bff835064e4e44908a78f129fbe60aa7a03b803a4d08b79da8c30ae251aa', 'outputs/generation/G0239.json': '9bb9073f9837c7cd9af68240e09b8980384585998f3e88f1cf0e2667d6a5c9a1', 'outputs/generation/G0240.json': 'e0a522743e7c714b51411e69418b59c3234d55316a17a016f57deb5d2082722d', 'outputs/generation/G0241.json': '00c71c7b36af623e1ae61000e9b6c25085b36ea6ca76ed0bce793cb9e48db9bc', 'outputs/generation/G0242.json': 'd7f186abe23d61638dd9f75d2bf90fcf554adcd02a01c6d9f373247a1c3cdc15', 'outputs/generation/G0243.json': '4e3db9171ba3a0e131b52595728f4750872879a968600b61a59f97f1a9f6f2a1', 'outputs/generation/G0244.json': '874d86d4e237268bc14313146997ac83af75bcd6b9ace1dd8187645de50d3dc2', 'outputs/generation/G0245.json': '68148cb766ae1ed1d214d9a47ef263b0becfe31d91cdf73ad9060209d2c98cb0', 'outputs/generation/G0246.json': 'b815fea11223d2e111c8ae7ef079093fb0432164d3b350e671e6744e36e314e9', 'outputs/generation/G0247.json': '4b7e550eed157fa73bca3961c64aa225aa522e4dc0e48782151c5d3b3e1f14e8', 'outputs/generation/G0248.json': 'e5b28b5d0691ad349d6014412d010e66c25691541f27c44f2716bd010f52e06a', 'outputs/generation/G0249.json': 'e26eab887d67433ea341631f5eee109a516c77b1cd5b1de668c0ce423671a2cf', 'outputs/generation/G0250.json': '96554c04f89e9e8af850bdb89afc115424a882f2c1b1b61291043a3bd8576902', 'outputs/generation/G0251.json': '44b4b7f12ef08d925d1ba0231f369176e5f4205052c2dc302f8caa22d98493a1', 'outputs/generation/G0252.json': 'bb0b58ed2fc1d0c33c2ee139d9e83bac66cbfd50329d61df264f6b4299b71824', 'outputs/generation/G0253.json': '66a8179bcd1084ddd831c4f634f8b3e23844200a67a2fe67efc7919ebaa8df56', 'outputs/generation/G0254.json': '845d328095c28f334a983266656f2f4d91892a7ddf1622300d9b454bba7236ce', 'outputs/generation/G0255.json': '05da967b1e333665a2cbeac681de74873a4ff204bd42aff283c3989e04fedfa5', 'outputs/generation/G0256.json': 'b17c2a009151b18a3b24ac3d321185b9180ebd5b49afb2c86bec0c1094b371dd', 'outputs/generation/G0257.json': 'a0a4e504074b2e8d5c62052e9bd8f1fc9596b9e02dea2a5176d17bf37a7aeb7b', 'outputs/generation/G0258.json': '5a9c2217625516c6ebb00f6b1841786e7449ae4a6686e1081317dc59b2ea9f8e', 'outputs/generation/G0259.json': 'd9a6342a66eba63d1442585b2c5623d0f1c2110c5611d21692cfc23e70a2b137', 'outputs/generation/G0260.json': '3407503a843d467b0d5e73de14f0b1267e69ff52e6e85e55aca50eb81e32137f', 'outputs/generation/G0261.json': '685292e4934b6efa5088240be5fe3c9a63ff8ee36c68a706ba233cdd99045707', 'outputs/generation/G0262.json': '2830c899bdfe12471c792c005ec011a952fa88e07eb2c48f2772a6e133cb0f21', 'outputs/generation/G0263.json': 'd289d8fb33ffdcb45e9455771cc473af318d03b66ad8f201b4d9472928c231ce', 'outputs/generation/G0264.json': 'd842d3985936db45757abf11d6785430f7c14916384100a95c2b14a63664da5d', 'outputs/generation/G0265.json': '6a1b3297a4622de6ac285ec2dfb7221f194c8d9fbee38bc2aa76fd841a74ec8c', 'outputs/generation/G0266.json': '7d5e6dac3d49978330db9925662725e6356f1136b879757afdf828153830bd55', 'outputs/generation/G0267.json': '04c23ba03a94475b377a9f8c67f0f28cf33b8c59765c2cab2cf963a7c193bb15', 'outputs/generation/G0268.json': '2777c7df1777258d8890ffba097075f98710386828c046677d2065a4e1721f90', 'outputs/generation/G0269.json': '6e45c6a0e360bb5a6b90aa8f8b1dd3430a7aff58cfc6597d01404535cd4267a1', 'outputs/generation/G0270.json': '3d2a9b54ec3cfe98e2475dedfa96998eb8c3771ea085d2df99c9ac0ddf3a47a6', 'prompts/I01-adjudicate.txt': 'f8eedfdb2d493960da47481da0d58d2027351fff91aeced2633e846a289a9d29', 'prompts/I10-view-v4-source-closure-review.txt': '23e3293eff3a765b9d09973d77b6de136560b96da71d2d55fa6371ff235a0685', 'prompts/I11-maximal-native-capacity.v2.txt': 'e3beb0a32b27917ce17ec5ddeb7cc13cbd509882059e992023b97a09fd5fed00', 'prompts/I11-native-code-author.v2.txt': '048e69159207f2c10062546f4b7294cd7eca0dc80e86713d2c8942d9992f833a', 'prompts/I11-native-independent-prelaunch.v2.txt': '4d6a7205556c1ac21ada09e472d81962662075b141105e1202b852bc4bf023f9', 'prompts/I11-native-repair-author.v3.txt': 'fb3ce90e1d41e19ee9208c4c343a0c618a1627371d328a7b2784c98a06b84f31', 'prompts/I12-native-author.v1.txt': '8fd93cbde2e4bd717aff4890cc68750a2d88d3e867fc11f2dd697c99a471c610', 'prompts/I13-native-author.v1.txt': 'bcdababfa179f1243b138972ebae79b13b1b2e0718c9b4bfb83c54f5346a35c9', 'prompts/anchor-review.txt': 'fdf19f14201fd529c84df4c481ebe959502d5cdeb890a475a763d26085c4bc6a', 'prompts/composition-draft/roles.json': 'e57d2f7bd265849e3bebecca16822c050645325ee94aaa76ed759be3150c4c14', 'prompts/composition-i11-draft-v2/I11-000-S1.txt': '4fe939aa22bb3b803a7e848dace38230600362945b5685d30525dacc44ba8f47', 'prompts/composition-i11-draft-v2/I11-000-S2.txt': 'd5547e630a26525d031ec13689e9e1e927bc7034515236999d3eb428c9c2695b', 'prompts/composition-i11-draft-v2/I11-000-S3.txt': 'd5547e630a26525d031ec13689e9e1e927bc7034515236999d3eb428c9c2695b', 'prompts/composition-i11-draft-v2/I11-001-S1.txt': '4fe939aa22bb3b803a7e848dace38230600362945b5685d30525dacc44ba8f47', 'prompts/composition-i11-draft-v2/I11-001-S2.txt': 'd5547e630a26525d031ec13689e9e1e927bc7034515236999d3eb428c9c2695b', 'prompts/composition-i11-draft-v2/I11-001-S3.txt': '02169b196745585ef2adc7bbec80e22e43490b577558959021fc109c5749acd7', 'prompts/composition-i11-draft-v2/I11-010-S1.txt': '4fe939aa22bb3b803a7e848dace38230600362945b5685d30525dacc44ba8f47', 'prompts/composition-i11-draft-v2/I11-010-S2.txt': '3b74cfbfc14054ff9b8fa7a122a288b82c830d9911778d025f0c8957364e0579', 'prompts/composition-i11-draft-v2/I11-010-S3.txt': 'd5547e630a26525d031ec13689e9e1e927bc7034515236999d3eb428c9c2695b', 'prompts/composition-i11-draft-v2/I11-011-S1.txt': '4fe939aa22bb3b803a7e848dace38230600362945b5685d30525dacc44ba8f47', 'prompts/composition-i11-draft-v2/I11-011-S2.txt': '3b74cfbfc14054ff9b8fa7a122a288b82c830d9911778d025f0c8957364e0579', 'prompts/composition-i11-draft-v2/I11-011-S3.txt': '02169b196745585ef2adc7bbec80e22e43490b577558959021fc109c5749acd7', 'prompts/composition-i11-draft-v2/I11-100-S1.txt': '3f161e8ec2c16f8b12fca7b827fce2311b3b8ce66c2219728eccf86036009da5', 'prompts/composition-i11-draft-v2/I11-100-S2.txt': 'd5547e630a26525d031ec13689e9e1e927bc7034515236999d3eb428c9c2695b', 'prompts/composition-i11-draft-v2/I11-100-S3.txt': 'd5547e630a26525d031ec13689e9e1e927bc7034515236999d3eb428c9c2695b', 'prompts/composition-i11-draft-v2/I11-101-S1.txt': '3f161e8ec2c16f8b12fca7b827fce2311b3b8ce66c2219728eccf86036009da5', 'prompts/composition-i11-draft-v2/I11-101-S2.txt': 'd5547e630a26525d031ec13689e9e1e927bc7034515236999d3eb428c9c2695b', 'prompts/composition-i11-draft-v2/I11-101-S3.txt': '02169b196745585ef2adc7bbec80e22e43490b577558959021fc109c5749acd7', 'prompts/composition-i11-draft-v2/I11-110-S1.txt': '3f161e8ec2c16f8b12fca7b827fce2311b3b8ce66c2219728eccf86036009da5', 'prompts/composition-i11-draft-v2/I11-110-S2.txt': '3b74cfbfc14054ff9b8fa7a122a288b82c830d9911778d025f0c8957364e0579', 'prompts/composition-i11-draft-v2/I11-110-S3.txt': 'd5547e630a26525d031ec13689e9e1e927bc7034515236999d3eb428c9c2695b', 'prompts/composition-i11-draft-v2/I11-111-S1.txt': '3f161e8ec2c16f8b12fca7b827fce2311b3b8ce66c2219728eccf86036009da5', 'prompts/composition-i11-draft-v2/I11-111-S2.txt': '3b74cfbfc14054ff9b8fa7a122a288b82c830d9911778d025f0c8957364e0579', 'prompts/composition-i11-draft-v2/I11-111-S3.txt': '02169b196745585ef2adc7bbec80e22e43490b577558959021fc109c5749acd7', 'prompts/composition-i11-draft-v2/I11-G-S1.txt': 'a0813df9e9bbc9d10708afa249306fc75f5afdad329c9947bcaa415bcc1edc31', 'prompts/composition-i11-draft-v2/I11-G-S2.txt': 'd17ee0ae6c782df57e7233eaeec2c8c10fbdb95ed8aa0f83e7f36fef6750b5e7', 'prompts/composition-i11-draft-v2/I11-G-S3.txt': 'd17ee0ae6c782df57e7233eaeec2c8c10fbdb95ed8aa0f83e7f36fef6750b5e7', 'prompts/d-old-P09.txt': '555c6c65c832bc879089d7ef65a373cad95e5df15da6be0957763e99dfa70ea0', 'prompts/d-ordinary.txt': 'db78be51f4082de28fe8824771239f7e6f663e42b61d5691a684757310c90b92', 'prompts/d-source-bound.txt': 'ad3da6621c98d0b1a68713c83d4cbcccc8f8f80d131152fe9a1f2ccd0107bd96', 'prompts/design-initial/d-source-bound.txt': '5d96f5eee64a40ca397aa19bfd595bc9e6ea72769159f8d546ef440058f19c83', 'prompts/generation-jobs/G0235.txt': '8b83af0f0c623c08e468073098f6a4b7661c6c8f6009af9698cfa83c3baa9486', 'prompts/generation-jobs/G0236.txt': 'acd24260cfb88bf343d9d73ee37dee559c4766440ea266536ed7eaa7180733c6', 'prompts/generation-jobs/G0237.txt': 'e249ef0f8c66b22468f459d8e32e225f4f65f552495d3e24f50a38f797f8ceb4', 'prompts/generation-jobs/G0238.txt': 'ea1a1ef4d0204b40f5828aac8650ef9efa54a5f402bf2967b57796a737df8d8a', 'prompts/generation-jobs/G0239.txt': 'b3ce3e3c033737e5692be931aabb1c158a4c21bca9279457b10b6be082b3ad58', 'prompts/generation-jobs/G0240.txt': 'd08e3b1a2412d57477c08c4fa92a6d8a173fd136869f2f854f472240e76e07c3', 'prompts/generation-jobs/G0241.txt': 'd4a570e80b3a90ae7482d611b3dbcc1c3d6eb8a9115ba3720be97fd53a2a6075', 'prompts/generation-jobs/G0242.txt': '78ef9e5a88001d27051efca9fda2f93a50284216905bd04bd4eecdb870f79fcc', 'prompts/generation-jobs/G0243.txt': '9b4103851be02ab74ee2dd17a2d90afd8a8ac4910c688513c0751f41a7f8f78e', 'prompts/generation-jobs/G0244.txt': '7df42e7e952097b4f7a958dffd322bc84f46883851b484108e72d5a68da624b5', 'prompts/generation-jobs/G0245.txt': 'c061affbae249dbaa6096e7860a117757889b932cc7d28b49c949688ed7cca4d', 'prompts/generation-jobs/G0246.txt': '9dac955f07737e77c4459707707af9718047683022bca963452493fb4b4853eb', 'prompts/generation-jobs/G0247.txt': 'bf6d580b1c447eeedd6d59884d7974a9f96c2fe023bfc2a4dff68cb424684f50', 'prompts/generation-jobs/G0248.txt': '6deb12e6cf4e9da5a604bdfa9de03e89b14646aa816f33c321768bcc00e3f735', 'prompts/generation-jobs/G0249.txt': '5b1bc71406c557e90939b5770cad1a073d62a84505c27746a726e8e81d8c1446', 'prompts/generation-jobs/G0250.txt': '6746a5cfc6c3668d6aaa7c7fa8fc5c72a0506d6f9e37fdc16d1f2549995da79e', 'prompts/generation-jobs/G0251.txt': 'a3458b7e825f6a5aa1424aea94e67213f78c030b11db1399327cfc4c121e233a', 'prompts/generation-jobs/G0252.txt': '6081f8cd61c63aca270ef5c5af87555cb348a10373258d39bfaceef7b167215a', 'prompts/generation-jobs/G0253.txt': '2a555e2c4ff076c5415bc024fa16f7ace8e385f76e285fb9965eeed2076388da', 'prompts/generation-jobs/G0254.txt': 'be6174789f5be809430bb376341cd18513798d713c16d0013c858db8f746c9bc', 'prompts/generation-jobs/G0255.txt': 'd8512010314197e21430a86b4c8a5bb25961f22bd5314a192b934d4b09ded4d1', 'prompts/generation-jobs/G0256.txt': '20afd1650c1f10abbdc535324f18b3079b40975936c7cfbe7660531a3626062e', 'prompts/generation-jobs/G0257.txt': '71cbc02935fb556addbac28d3a48424d78c2a15bd3e516d9ae89e8a516997f66', 'prompts/generation-jobs/G0258.txt': 'e56ca45bd577689017d8fd1e78c42cd79f61dffa5f571551de986cb558af1013', 'prompts/generation-jobs/G0259.txt': 'ad379d045ca93617b7783ee71af8cb195f934310bd72b2d9458a8c90c9343def', 'prompts/generation-jobs/G0260.txt': '5bb842cfa1bcd9f7b2c7061b052abdf53ec33c3cf8b1302811c8cb11c315cbfe', 'prompts/generation-jobs/G0261.txt': '5018c51181680ae0db8f55d6a1407fda4ee19ba28bd34d90fcb63e15dbac1e9c', 'prompts/generation-jobs/G0262.txt': '387dffda2d9e57cec7165bb9327e035a1ace41227bea5f6fef4b1a01c3024b9f', 'prompts/generation-jobs/G0263.txt': '96b5083f0372335638246cf53df6557204d886bb4006b76e6a8b97c743936288', 'prompts/generation-jobs/G0264.txt': '521751d57f32ce729fef95a43e4aee5a57ee8b2f216c33a9c1cf8d8f01e65df4', 'prompts/generation-jobs/G0265.txt': '03e58630c35a29535694fd29ed4bbe943108e03b897001a65e56b863beb39e32', 'prompts/generation-jobs/G0266.txt': '3230d1ce1391d7d009c29538e30777b713c6e19429cdb5b301fe08a14b15fa95', 'prompts/generation-jobs/G0267.txt': '4c07e1a2a4b5c677d7aa75e279c1da24ac41ffde29f9ae40a53767f5293527c6', 'prompts/generation-jobs/G0268.txt': '12ed32144d327e20d67bdcb35e367962711d008659f96627f911f5cb3b1456cf', 'prompts/generation-jobs/G0269.txt': '7b252336018d1556b81b203ae42f988b9796bd6f693062e1988172f0eda9b957', 'prompts/generation-jobs/G0270.txt': '201ecd70314a542ab9674ddce3232bcfc664bec91e5abdd736c275302f640d25', 'prompts/generation-raw-first-jobs/V-052a58575303a2a4fe38.txt': 'ce03dc5e2be198e266f496eff39bea7b0b31580390c961399c56f5e44f87b056', 'prompts/generation-raw-first-jobs/V-08582e99f3f35d86a38a.txt': 'da46d0b0cf67b3efaa5f775dd5d3e70d2568c62bc658e7aae39a164feda8ac02', 'prompts/generation-raw-first-jobs/V-0b59ebd7bc18efc0533d.txt': '2f2eb49317b5f1c686ae0a2550a247183350b2468a2b6c979f61f2257fe8a975', 'prompts/generation-raw-first-jobs/V-11585a365af4bb3d05f8.txt': '2bc618701761b2cf9173cb9fd465d746b09416bf348e6d1b8e27a162d01a64c4', 'prompts/generation-raw-first-jobs/V-2f386585bfcc1ec4ba29.txt': '0191bbf8dbd43b85952ad9129b1aacf46a47f7fb4701e7ba1fc3e2ec3ca6b779', 'prompts/generation-raw-first-jobs/V-3351942de061d49c58f8.txt': '1e67c5bbe3dd1db12dd4f24b3a7d41c86c55eee2fed7afb06dc2d2d5d20210df', 'prompts/generation-raw-first-jobs/V-6078d00dd270d7bbfcba.txt': '1398c08af66786cc67a9174bb24dd60b9a85368377872cc7b4af2689415cee25', 'prompts/generation-raw-first-jobs/V-797328fb328bba1e05bd.txt': 'e13eed5cc81f2a2c0f7a85ed009e585aff7abdfb2b8b9b91dd78979a69e43812', 'prompts/generation-raw-first-jobs/V-92221831353074e27507.txt': '41cbd171180432a1317fa8fe51987967f3ae71c37451d5e2e13acd76d1ee3e63', 'prompts/generation-raw-first-jobs/V-a09de67a61e4bd2550a8.txt': '50112e32635de70bc3bbd581bb8250217f1c9e6fc279a05e81192b677130a6ff', 'prompts/generation-raw-first-jobs/V-b823e3203fbaba2cf612.txt': '52ac44c765f90d4eebd94ef1de8420e94e023838ca42b2882121e6a78b45399a', 'prompts/generation-raw-first-jobs/V-b932f5cb4cbfe9c12398.txt': 'b63e5320d90b47c02021a737f70e046e517a7b50d3f51285e9d43ebdfae1ca32', 'prompts/generation-raw-first-jobs/V-d194a5ae7fed2a4cde4a.txt': '62733e5ae3f1a92a6ca328dfb50610a562f29c40a126e47da0e0be2a9247cbe7', 'prompts/generation-raw-first-jobs/V-e35452945a9db65df92d.txt': 'd16bdf2ff4610d03367a12c5f449076019efb5c1fedda050fa78ae52298b9d52', 'prompts/generation-raw-first-jobs/V-e644872bcf896547a43b.txt': 'f2647faedda5345763538551067930d6ec9399be69fc83faf179989556a4cc0c', 'prompts/generation-raw-first-jobs/V-f7398bbf160ffc9f0709.txt': 'ffa01646d4afe42fc7ee94288342e98376cfeab1728bc1a68779b57b9257a204', 'prompts/generation-review-jobs/V-05fa8c1b5fd98bbcb4d5.txt': '1a1b8e164ac44af582d86ee9b303975a9c63225b3b9feb398839226b70a016da', 'prompts/generation-review-jobs/V-0d8314479a0c88bde8b9.txt': '601ef655362472c0cd1ef18845a0c3d74d2af096c43ca021d25844c329b56404', 'prompts/generation-review-jobs/V-54ddca9fa1406112a36b.txt': 'ecbb4f0c190b547ff7a82be78a0fd29fed149e99183c5e343dba57af9f364c64', 'prompts/generation-review-jobs/V-acfed79facce27c397bb.txt': '9bb8439fc129d8203074c40c26b4fb0dc430a28368a3dd337d5e9fb7f19d91b0', 'prompts/generation-review-post-first.txt': '25f013bf33f269224c0f79aa4cd3b7dd83e5b1cc8418172bc70e255969811614', 'prompts/generation-review-raw-first.txt': '3b404b01c5fb105a2dd6dc06b42f3be2f76f095701c99b0722907ecd2bf517e4', 'prompts/generation-review-v2.txt': 'd082be756d4dd48dad9d646c7b3e21f79b1df27d561a8cc4062b0d2702fd1e54', 'prompts/generation-v2/I02-feedback.txt': '215840fc5a5440650b035df2fea1095e708225e28fc179c70c8ecc15d40d1235', 'prompts/generation-v2/I02-generic.txt': '68928558872ba26bbb8f1a1669843c7aa336bbdf3493075c0a72ea0727c34ff1', 'prompts/generation-v2/I02-necessity.txt': 'b36aed6e77e743600d2f6c84269aa5779f82df48e686de51bb5bbb38ec6a5af9', 'prompts/generation-v2/I02-ordinary.txt': 'a6f492450853f609a7476e0381d19fe6981845493bfff354d31dba47fed0e889', 'prompts/generation-v2/I03-construct.txt': '0bfbf66dee6830acf67c20676f1b9769b325c91086531d9c407cd5d2d5c60b79', 'prompts/generation-v2/I03-critique.txt': '4e663d34c325fc7b8aa14cd456d0deda15f8bc3824cf4f5284a0361e9f8533a3', 'prompts/generation-v2/I03-generic.txt': 'f2c6c2c280a7cec4b99b36b622f645905e172c77c6d3a2eb1e48aecbe02deb9d', 'prompts/generation-v2/I03-ordinary.txt': '0edf335693401595dcb9b05fadcbae3db21b65e33d4102b6403038a300527b81', 'prompts/generation-v2/I04-conversion-original.txt': '9caf83d8dee4d239c258a4985f79a1bd4d4339c4352e7026f09a112c7def35c7', 'prompts/generation-v2/I04-conversion-relocated.txt': '66dadf8a498867dcd2ed87302c8517985528483604faea8b0d2350d474066f55', 'prompts/generation-v2/I04-generic.txt': '68928558872ba26bbb8f1a1669843c7aa336bbdf3493075c0a72ea0727c34ff1', 'prompts/generation-v2/I04-ordinary-original.txt': 'a6f492450853f609a7476e0381d19fe6981845493bfff354d31dba47fed0e889', 'prompts/generation-v2/I04-ordinary-relocated.txt': '0be746cc292710c1c6054ec78c955d089a85c7a91d5b90f810dab60d882c62ee', 'prompts/generation-v2/I05-broken-interface.txt': '4da5d317b39a96d0025e861bf47a71a96884d9ef6a6cb681e830a6d7117341fe', 'prompts/generation-v2/I05-generic.txt': '68928558872ba26bbb8f1a1669843c7aa336bbdf3493075c0a72ea0727c34ff1', 'prompts/generation-v2/I05-intact-interface.txt': '39c79f2c89d51699b162c27a19e4a13afb62cf8103180b2e9f854ed61701b971', 'prompts/generation-v2/I05-ordinary.txt': 'a6f492450853f609a7476e0381d19fe6981845493bfff354d31dba47fed0e889', 'prompts/generation-v2/I05-parent-a.txt': 'cca290a65606ed5746084f44bfe79c9d588cb30ea4318375e0936572d4d1f7a6', 'prompts/generation-v2/I05-parent-b.txt': '2ffb53663a4c81033d94907ebcd7b58c66af732cf4481ccf0ec81f8f85d169ab', 'prompts/generation-v2/I06-backcast.txt': '6dd59b0fd52d2248a6e2b9e012577800a939f20b4c15f38ff29e56f93aa4f664', 'prompts/generation-v2/I06-generic.txt': '68928558872ba26bbb8f1a1669843c7aa336bbdf3493075c0a72ea0727c34ff1', 'prompts/generation-v2/I06-ordinary.txt': 'a6f492450853f609a7476e0381d19fe6981845493bfff354d31dba47fed0e889', 'prompts/generation-v2/I07-generic.txt': '68928558872ba26bbb8f1a1669843c7aa336bbdf3493075c0a72ea0727c34ff1', 'prompts/generation-v2/I07-ordinary.txt': 'a6f492450853f609a7476e0381d19fe6981845493bfff354d31dba47fed0e889', 'prompts/generation-v2/I07-protected-anomaly.txt': 'b183858318b3fbd197b0d6ce70b6f2146c50d12c9a0522e9bd44025f3b954e3a', 'prompts/generation-v2/I08-consensus.txt': '0035605a3c9e9335bccb2a89a5fc9581d56d7bc773fc2e5dc140ff497f0a9de3', 'prompts/generation-v2/I08-deferred.txt': 'd1650802b7279419f46873d358aa8b36587d918543d5a7acea7a05958a62ecf0', 'prompts/generation-v2/compression.txt': 'd70724f970abb4fabb814a95bb362a42006af2a32281a1c5bfd3623ced64df23', 'prompts/generation-v2/concern-beneficiary.txt': '3e5a98ce68ff2c74086e50d397468377f4e3b5b19bd419f749520f87262ff571', 'prompts/generation-v2/concern-evidence.txt': '1f2e817e84472b9d4fc7bb7d5ae51c9e710218f1efe5dbe792bfebc27e5bea12', 'prompts/generation-v2/concern-operations.txt': '1e4136976228ec04efad66bc118c6226d716f5c9064da844ef2be96e33112217', 'prompts/generation-v2/incumbent-seed.txt': '7432655dd12b9d0c17b08f3fe7e97bbf1b2a84686a94993e9f04641dd72f241b', 'prompts/prep-anchors.txt': '56184c3bf1fb481cd99ee9aec3a90f2d275ad145c9cf932a25ab7efee19057df', 'prompts/prep-archives.txt': 'fe30b5b83dbb2b570310190992c686d6e0dddd50238dcac62dc1a0092e8f38ca', 'prompts/prep-cases.txt': 'b155f37f8393b02c424248f19b3584a94b13700246e8d1c6d6a5e22a6bc0e964', 'prompts/prep-packets.txt': '8d3215fe7cfaacfdd16a19986e16b6210daf87a2f7873d6f2c70b58fe204b14f', 'prompts/prep-verify-fixtures.txt': 'c11956a5855b38d93d000cff6eade0cbe1974705bd33db5110c47d1219d74fd1', 'prompts/prep-verify-schedule.txt': '4249cc56f255930539dd190a0748f2c990da582da2a3d3ab84ad29a4279f4c14', 'prompts/raw-first-capacity-post.txt': 'b05e64595fe644069fe22d9a8e2f143ffd739b28c71ce1c6a3b13b5c76082cd5', 'prompts/raw-first-capacity-raw.txt': '6772fe3cd9ef7e0509ee95d16b062386f894894aad090a818f9f0585773b5975', 'prompts/review-compression.txt': '568cd1eb9bb6e8f444739b01e6346cf6ac9b2f4343fa5c36cc516a39c97038f9', 'receipts/I09-method-mapping.json': '5c857ec539d33f5d22dbadb526e8753178109f024b0153198def358f9ebd9c12', 'receipts/I10-code-review-inputs.v3.json': 'cbec6b5f6f3d47551320498f45d9c8266cdec18fb568b988a8ceb4c1b56594b4', 'receipts/I10-code-review-inputs.v4-closure.json': '85093cc85eb4efb4bd78236bdeec1019d48d6304a6ae598538cf821f3667f5d8', 'receipts/I10-completion-events.v4.json': 'da63f7c3c8a7513d1959ac8397312d13caca3abecb3ba94984ab4ef92249793e', 'receipts/I10-preparation-budget.v3.json': 'da8d216b08a569ba709ea0b4553a24190bac196809975586718d7adcb2db806e', 'receipts/I10-preparation-budget.v4-closure.json': 'f1fdd73a52ee285693563a8b30fdc0f0dc53284a91d62d84a513837dd62ad72b', 'receipts/I10-source-context-witness.v4.json': '4481d9e1cd9c10fdcfc1b90430e99bffaf9ffade6f21bda3b8e257e0aa3f1e5e', 'receipts/I11-composition-preparation-budget.v2.json': '0bf0a40185e2548ed2bae82503dec5953ccf2208bb66e65eb58278dc336d49fc', 'receipts/I11-native-code-author-inputs.v2.json': 'd80a0269302f172a81ca650af967daf8c3d8f838bfe149773591e2ec2deb34b8', 'receipts/I11-native-independent-prelaunch-inputs.v2.json': '3dadea2582c6b5e722f897939d4edfd62b084cb0bc12f5e8207fd7604addf991', 'receipts/I11-native-prelaunch-preparation-events.v2.json': '7f171487245fa4fad67584b3bfae65ad08f503e61bd35cddac3d8aae8c9b54a6', 'receipts/I11-native-repair-author-inputs.v3.json': '59e292d11b69882cc5e866fbaad83867bb0183a22eaf15ab6cefdc8dc0145047', 'receipts/I12-native-preparation-budget.v1.json': '4747f489165fd2f9eba7e97744bd931eedf8b6a0a3838e17d99775d1c00967db', 'receipts/I13-native-author-inputs.v1.json': '7e4cfb80e63c27a01e9931453741ca37ab4e857764b42fb6709c2d086844e190', 'receipts/I13-native-author-source-extension.v1.json': '0b846ef5ee60dab8c75f9d92792d278d6ad475af9f6e1b97ad72599edd101403', 'receipts/I13-native-preparation-budget.v1.json': '05b04b54eebb83d2c3d2f608e1e7aa2164141d585cc6037d2c662ffdb5d1aa21', 'receipts/I13-upstream-I06-context-events.v1.json': '6b1016298d26e851001d56b6a24af74f28de1b162305a6c26032bd92ab12fb5a', 'receipts/gates/I01-readiness.json': '1457656d76088ba622590ee8741e39e045a9e177bfb2c1160e13ccff7aa604d2', 'receipts/gates/I06-confirmation-lock.json': '86052d4fe8d1eeb5f7fe4961e80ee16649eeb14196796bf2f0e8fb9f540159fe', 'receipts/gates/I06-pilot-lock.json': '263ef010cbc450eb861607ad675240bff464ea5f0e140a621de0cc470c0cfe44', 'receipts/gates/I09-fidelity-advance.json': 'c8fd1426eeb9810d4ee1ffada8ea01a67d406a2aae0c4b20b8616fe25648888a', 'receipts/gates/I10-evidence-complete.v4.json': '7a87f52d8ec376da2bcfefcf0145f6cabbec095588ee313d7ffcce50802d8125', 'receipts/gates/I10-exposure-admission.v4.json': 'abaeae372fa0a5b9178bc10feccd812683a3725135419914650e4577a8c211d8', 'receipts/gates/I11-composition-native-admission.v3.json': '2becb3c1565f5dabb944a66c8c586217e970feff863118cc360a8a4203943c05', 'receipts/gates/generation-raw-first-admission.json': '0524f79ce75844b8660f239d0675cbd8beff61afef37e7442ccfbc15fdf73781', 'receipts/gates/generation-v2-prelaunch.json': '31c70c5bd69f6ccdab865b1c0d8b9f9a7c28aab1f806a6afb5007671b6010942', 'receipts/generation-archive-provenance.json': 'bbb3b904b1344e9afa0757c977fd5a21ede6fd3ee7f9dab8b13e2b57374276e0', 'receipts/generation-blind-maps-v2/J-1e95a237f2b5fa924678.json': '11d9dd0240b2f66199123f012c2beb8fea3fd66728ccd398498aaa53c768a3b6', 'receipts/generation-blind-maps-v2/J-e366c56698f5bc38c090.json': 'e4a8d90bffe3a181206e54327dd5453e71082652302f9f9d10541328420ea59e', 'receipts/generation-lock-repair-budget.json': '5e3926658834a27ad7af322333429904366773133528c563891d208bad872e46', 'receipts/generation-method-mapping.v2.json': '5a48eef67df99af4bfee9a6f2f3d7e3337b1c89ded772b616e83205ecc58b7f5', 'receipts/generation-raw-first-maps/I06-A-C1-post.json': '97c288ad7856d69d4338e3fe53a43e2d2d251113c9796cf2ffd62bc005d27f73', 'receipts/generation-raw-first-maps/I06-A-C1-raw.json': 'e2ff36bf131c8d09ea9f42f96f92a9fe891ea77f01d2eb4ac73d8e617a4f0b4f', 'receipts/generation-raw-first-maps/I06-A-C2-post.json': 'a7ca1b1e12217751d2b793e8d60023e1cfaeae22ebb72cdd6729ac27ae7a3f71', 'receipts/generation-raw-first-maps/I06-A-C2-raw.json': '6f4b0e3efd9e00a2e5a478787408bc768017a7aa8660e913ffd053978523455b', 'receipts/generation-raw-first-maps/I06-H-C1-post.json': '4099f5930238cbd30771e44e48cf2d334969ccb6467a75e3be34ced7b2c8febc', 'receipts/generation-raw-first-maps/I06-H-C1-raw.json': '26b10db603bed440b102d9c01ad863b1e69d415cc52343390b2d8b1e24f060a1', 'receipts/generation-raw-first-maps/I06-H-C2-post.json': '664fce2ed76cc252ba0c8f10daf75ac777c1dab16c30889d1fe03ab4edd739b2', 'receipts/generation-raw-first-maps/I06-H-C2-raw.json': 'a33475d607bb4ca0ba8263f5783a0e7e8c511bca85411fbabde6c3b1399e3e02', 'receipts/generation-raw-first-preparation-budget.json': 'ea65edefdcb84f660c9e6ed61bb52fd40804e1169abd73ae5773345d3d145593', 'reports/I06-A-C1-case-evidence.json': 'd52125541ca2f7af91aa55e1253f45de0e0d9251b9408bdbe848bc984ed47339', 'reports/I06-A-C2-case-evidence.json': '2a0403fde38295fae2303d578ae769cef6488110e3f41c98a4d25a875302f5d6', 'reports/I06-H-C1-case-evidence.json': 'b03380eea6c82b6bb4e47b10d6138ff31cd85c486c38e29295cb0751e909bb91', 'reports/I06-H-C2-case-evidence.json': 'be86666c0c27af62162fa53d18ca25c987170362149b1b0702f1f1ad35918f06', 'reports/I06-confirmation-prospective-admission.json': '7dd7440cfefd627d13d306d43cdbfcd695b5cb14df842c6c8f10efe8cc82d02b', 'reports/I06-confirmation-results.json': '09b0f188514b9afa948fc75c7eb3237bb80d3ffa9c62a528a61d5596e363a865', 'reports/I06-pilot-diagnostic-summary.json': 'e12a3bb859259edefcfa01b19c210e8e767482faee71298828e9a6210ec59c7e', 'reports/I10-DETERMINISTIC-EXPOSURE-RESULTS.md': '474ab02a6b55f3d6a6945221a028e4945e1ecbb285f2f46e8ad0c0d1b764c572', 'reports/I10-deterministic-exposure-results.v4.json': 'e77389f26aa1f1477f3617b266f5dc60760bc2eb84570ecc0c69fc1fb569eeff', 'reports/I10-exposure-v4/A-C1-backcast.json': 'dea9d717fae22e619cc2e9a446e2881e60aebcf5c1e44998dc86471620dda180', 'reports/I10-exposure-v4/A-C1-ordinary.json': 'c927651aec0167e70a1a3134019abff3df31bfb03795077713730d8a1395811d', 'reports/I10-exposure-v4/A-C2-backcast.json': '7cc9a69a83d483422743341f2fcacd0d1f08f2ee98afbe36c48ff334c1c55890', 'reports/I10-exposure-v4/A-C2-ordinary.json': 'ca71cc76e3ccb74d2548ba5820bd26b711812c8747ddc51275f231effd8909c8', 'reports/I10-exposure-v4/H-C1-backcast.json': 'aab2cad045022e0eb5eb6fa618c72c2dd2141a84075dafc0b77fb17958331580', 'reports/I10-exposure-v4/H-C1-ordinary.json': '90d11483f8d83fbf14aca6730059865c97bfb887d083f49edba47d4d3df63d9d', 'reports/I10-exposure-v4/H-C2-backcast.json': 'b0b3c84bc12c86a95160aafae463ba851b2da6ff095f564aa9a2e8f59903f725', 'reports/I10-exposure-v4/H-C2-ordinary.json': '3b90e4f6982da155396a610eeae90b6d00798aa82b85f17397a4f7aff69308be', 'reports/I10-independent-completion-audit.v4.json': 'f07698ee6138f31be8b1508624caf5c6ccb3185aa6ddb83b50ac27dad75a0839', 'reports/I10-v4-parent-read-closure.json': 'aec70271fb502232178bc19456459ef1479880d6d011454760a6287d29fe04eb', 'reports/I10-view-v3-independent-prelaunch-review.json': '557835abacfd8ac3bfe72f8e4bf37f334222c17063969943d37336d145c7c49a', 'reports/I10-view-v4-independent-repair-review.json': '93ee84174abb237c8ed7c4804b3898b593a29627185a8de49a1adf2138cbf9fc', 'reports/I10-view-v4-independent-source-closure.json': '7522c55c32af71263625620d45009d62c73a20f51b8d6b3ab610cf68247ef575', 'reports/I10-view-v4-repair-code-check.json': '944bccdc9ad2f4492f6c8ef872fc1724005bcb3344820de3fbd7509a2652c389', 'reports/I11-full-matrix-preparation.v2.json': 'e7f3b8f416efc16f84b54127c3a4f9b83eaf682da8d506d69b99feab1aefd04c', 'reports/I11-maximal-native-capacity-validation.v2.json': '871893f4fa4eaeac976d3937412864d332ea3c700b9e89d375e2d80aa8dcf005', 'reports/I11-native-independent-prelaunch-review.v2.json': '16f422de2605faff4d93ec7d92565f4a5d668aa087d6c7e0f688863e6eecff10', 'reports/I11-native-independent-prelaunch.v3.json': '2f9f12d7484a640057d9001340608c6c15e702a93923cdbb6b599e3135715b25', 'reports/I11-native-runtime-preparation-code-check.v2.json': '6095a65233bb499d95b123939dbcdc87d0293ebff8b2c8c462c2933fe76e049b', 'reports/I11-native-runtime-preparation-code-check.v3.json': '67f129b952e165e2e5168a66bc07f2dfe8789819f78f867c5f04c61934a9b20f', 'reports/composition-preparation.json': '47ae6e3feb1eb417090beff2815117014ea4d1cf273e6a522b73ec970a165c9c', 'reports/fixture-preflight.json': '41c28dcdc17070b088be0af3819d7b5da3929431f787ddd0d8e4fe038466ddac', 'reports/generation-capacity-prospective-rebudget.json': 'a4c94bed8c12eb2ddae0bf3e8bef25a0e46e60c65639ece35f0e978dd4103471', 'reports/generation-capacity-v2-parent-validation.json': 'b9855d7a2d9c2a143c5a48c6f8df49cd3aeaf94ac7578282b68bd85fea1cc1a3', 'reports/generation-disputes-v2-code-check.json': '92961d414105c2a18a1285ecdab8b937030acd83ec155f5b3b5c64eb69ad5068', 'reports/generation-lock-independent-verification.json': '3db6d547e52168b0956d567d45c5d4dfdc625a83e29141d79c0229df30f6922b', 'reports/generation-lock-repair-code-check.json': '44862033bd4c9a3e27328e5f9d063f1a4270bdb8e45ed6fc10e79ec0598cbc7d', 'reports/generation-lock-repair-verification.json': '1711b3ad8cf489c14baabd5d49af3f7b2d5fc8f2d13e4b2073d668f146d1f1bd', 'reports/generation-locked/I06-A-P.json': '285478ef18295e5288c2eeb47a7cacf310aff521676d0b2b0a48fa1f61cc5d68', 'reports/generation-locked/I06-H-P.json': '29f5cfd43e138926442bc50138014b48e7dc088b1a8d404b972d29e1f1957118', 'reports/generation-raw-assessment-order-gap.json': 'e3966d9d77774086ee89f598e262fb3fb6c05d055a4217228d5e128cd2de5a4a', 'reports/generation-raw-first-locked/I06-A-C1-post.json': '9bdec14c72262077c6b059fe3448c0f252854dad596faaeacef6ba81b8e00d7e', 'reports/generation-raw-first-locked/I06-A-C1-raw.json': 'e8f8efd04716e1d753b0d237b6a7a7336029c2490b0eb7f9e47b9a14a8e72446', 'reports/generation-raw-first-locked/I06-A-C2-post.json': 'bac19f8fd2208408a96a58a690b515cbb9f08ff274236b8ec4e91936c0034f18', 'reports/generation-raw-first-locked/I06-A-C2-raw.json': '22b1e85c93b36bc27f9fa592ec828f3f35937e77d04bae74450245a210d382ad', 'reports/generation-raw-first-locked/I06-H-C1-post.json': '785a5ae9c4b49a9deb4d029a0dbe32305343502ff74e57fb2cb05a723a269801', 'reports/generation-raw-first-locked/I06-H-C1-raw.json': '81b47cdbcab6b5fcc2b62f5fb0e4529804725ce8d10479b1700cd4aac74f9548', 'reports/generation-raw-first-locked/I06-H-C2-post.json': '10101304bd78f53a5f758b4ec4751af321afbe41a5f3f0b2bd74608825e839e2', 'reports/generation-raw-first-locked/I06-H-C2-raw.json': '02735b85503c4f089ad573a5daaac6ac19ef1fe45e10251902be5d96452a6413', 'reports/generation-v2-independent-verification.json': 'da420236379d80dde72a58300cbe16204f8bbed1f87c4732751902363df12e27', 'reports/generation-v2-repair-code-check.json': 'd8d191e979ccec860c26bf98f48e0cbe95782fd0f5e8f810a2eaef395d0ea458', 'reports/generation-v2-repair-verification.json': '1522a5f1e356ec5114398411d5eb7254e37ed46fcbfb9865b730d9ebb1420f8e', 'reports/raw-first-capacity-inputs.json': 'c2e697116fe5bf2b45454aeedab206f55165151a0bb7bf181c58d3af0e5f6763', 'reports/raw-first-capacity-validation.json': 'e64016b4327edca507cabc559a427c43d6c25f5eb114bc67a4a62d0f5180b6bc', 'reports/raw-first-independent-verification.json': '99f71bddfae5b1483c8c97c6d6d34ff5408719781e8f077be2e8b694d1926708', 'reports/raw-first-packet-code-check.json': '3e436a424f4b0b6c1d929be5862ad7c437682ea06e9e24899f132d71993548be', 'reports/raw-first-repair-code-check.json': '8d21f4029eeafaaede032978138a2d5bbbfa63fb899984dffbe27b485359f3e2', 'reports/raw-first-repair-verification.json': '5dd0097f8420bd1bb41fb41d09f592c5a572fb2a0a7057a121881ac9eec8f187', 'reports/raw-first-runtime-code-check-followup.json': 'a446e0e52989d40aac447c00d08391d70670ccd8ea3ad45a845cd998eaa499c9', 'reports/raw-first-runtime-code-check.json': 'ac889a932d46af22ea191c61e92deb1b35e58d55709659edf6dc4f96207f1c20', 'reports/raw-first-runtime-source-binding-check.json': '845a176b173b0af8b497a9fcb4f34bd6528e6c9a2806b6f951a5831267df247e', 'reports/schedule-preflight.json': '6d2f550831752dc9cab697a8d54b9b4230f995f262495ba157eef5850fd35215', 'review-schedule.json': '2d6eb94e011fcf106a43f665b383831d3b29087cf6290dbbfb32a0f0a9f5f3bb', 'reviews/composition-capacity/I11-maximal-raw-v2.json': '0a79296f4f9a246bb54072aea4dcc964d5b3d004f892846d79ff8487110b82ee', 'reviews/generation-capacity-v2.json': '3e4a1826fa8d7776ede7ecf189c240680ec18ee9e91b52b5c29f7b26237a9719', 'reviews/generation-opaque/V-05fa8c1b5fd98bbcb4d5.json': 'c35cc8f751b3d319d14b9c0de9388846dfb477426f71fc1cf54fa34a2a465529', 'reviews/generation-opaque/V-0d8314479a0c88bde8b9.json': 'f2ae2d86500df038919bcbb7cc0ab322ba215da553617d5a3ba748dbba1e3f92', 'reviews/generation-opaque/V-54ddca9fa1406112a36b.json': 'e5783bf130acb249aca4b2f1ef70d9cce7eee7957460baf5f21aae102a958577', 'reviews/generation-opaque/V-acfed79facce27c397bb.json': 'fa3bc94d41c1a2e7df5a7ebcb012cf0179c3def1b7c19f081477dff96404c434', 'reviews/generation-raw-first-opaque/V-052a58575303a2a4fe38.json': '42439d321a7efd2b0ec20d0d5dda698e1483fad39f06d8ee4422b671400a7e4b', 'reviews/generation-raw-first-opaque/V-08582e99f3f35d86a38a.json': '479459067a9605d84c70e4375c61925c50405eab20282efafc76688367f1d966', 'reviews/generation-raw-first-opaque/V-0b59ebd7bc18efc0533d.json': '91a2da598b3bcfa855921419ca776a8b195d99514874a166e719f0c57ca674ec', 'reviews/generation-raw-first-opaque/V-11585a365af4bb3d05f8.json': '5772e318646bf00e0e5a01ff038f6ae3338a4d007d2199f50f5a22ac6c715862', 'reviews/generation-raw-first-opaque/V-2f386585bfcc1ec4ba29.json': '523241b3e6c591ac047ac7e044ddcbdda9ac1c30d86e45fff99a1aac653f5109', 'reviews/generation-raw-first-opaque/V-3351942de061d49c58f8.json': '806c9fff8610f3a06a786c8ea626cc55f9e71a07b0e9f34e401b041ef7b87d46', 'reviews/generation-raw-first-opaque/V-6078d00dd270d7bbfcba.json': 'd93e5729714529e82548c36a1f2766cf5cf09c8ed712f3b63bd5f10157c27dc1', 'reviews/generation-raw-first-opaque/V-797328fb328bba1e05bd.json': '203d9d9d7df98cc2948ee50c181ab08723baffa4add3f8e3e56b78b4dc7a3265', 'reviews/generation-raw-first-opaque/V-92221831353074e27507.json': '21c53cb3f7ceb1953570bda391835726d7605648351d23b7374be68552328b85', 'reviews/generation-raw-first-opaque/V-a09de67a61e4bd2550a8.json': '291ff32ba28fb611fda2fdc109fab822a07d8b54729eda096a0b60b8b43e7af9', 'reviews/generation-raw-first-opaque/V-b823e3203fbaba2cf612.json': '75d3ad1c9c7ac442e0ddaaa393f6846d5be0bfa73ebb0f6384e3cec4aaf3b26c', 'reviews/generation-raw-first-opaque/V-b932f5cb4cbfe9c12398.json': '4662c4448a0b14f7ea8a1bfb4f5b4b70b9630f2bfd09730eaa1a9fad63adb6d1', 'reviews/generation-raw-first-opaque/V-d194a5ae7fed2a4cde4a.json': 'b258e338f124e3cf72d8411301d42d731183ed2177a6da54a82dba678116c75c', 'reviews/generation-raw-first-opaque/V-e35452945a9db65df92d.json': 'fdd146f007972f7f6d379b1499ae1583b450aac9a6cf20f9cbdaf8f832485dd6', 'reviews/generation-raw-first-opaque/V-e644872bcf896547a43b.json': '2eb28a11e216f7ad1a875885e697d70684ec42dc23d4a4f43e39b02ee3b42ba6', 'reviews/generation-raw-first-opaque/V-f7398bbf160ffc9f0709.json': 'f6ac85a18b6babcf7ca1df8b198546facdfc01cf2eca611bc5e22c65d487ba28', 'reviews/generation-raw-first/RF-P-I06-A-C1-1.json': '5772e318646bf00e0e5a01ff038f6ae3338a4d007d2199f50f5a22ac6c715862', 'reviews/generation-raw-first/RF-P-I06-A-C1-2.json': 'd93e5729714529e82548c36a1f2766cf5cf09c8ed712f3b63bd5f10157c27dc1', 'reviews/generation-raw-first/RF-P-I06-A-C2-1.json': '291ff32ba28fb611fda2fdc109fab822a07d8b54729eda096a0b60b8b43e7af9', 'reviews/generation-raw-first/RF-P-I06-A-C2-2.json': '479459067a9605d84c70e4375c61925c50405eab20282efafc76688367f1d966', 'reviews/generation-raw-first/RF-P-I06-H-C1-1.json': '203d9d9d7df98cc2948ee50c181ab08723baffa4add3f8e3e56b78b4dc7a3265', 'reviews/generation-raw-first/RF-P-I06-H-C1-2.json': '2eb28a11e216f7ad1a875885e697d70684ec42dc23d4a4f43e39b02ee3b42ba6', 'reviews/generation-raw-first/RF-P-I06-H-C2-1.json': '4662c4448a0b14f7ea8a1bfb4f5b4b70b9630f2bfd09730eaa1a9fad63adb6d1', 'reviews/generation-raw-first/RF-P-I06-H-C2-2.json': '21c53cb3f7ceb1953570bda391835726d7605648351d23b7374be68552328b85', 'reviews/generation-raw-first/RF-R-I06-A-C1-1.json': 'f6ac85a18b6babcf7ca1df8b198546facdfc01cf2eca611bc5e22c65d487ba28', 'reviews/generation-raw-first/RF-R-I06-A-C1-2.json': '806c9fff8610f3a06a786c8ea626cc55f9e71a07b0e9f34e401b041ef7b87d46', 'reviews/generation-raw-first/RF-R-I06-A-C2-1.json': '42439d321a7efd2b0ec20d0d5dda698e1483fad39f06d8ee4422b671400a7e4b', 'reviews/generation-raw-first/RF-R-I06-A-C2-2.json': '75d3ad1c9c7ac442e0ddaaa393f6846d5be0bfa73ebb0f6384e3cec4aaf3b26c', 'reviews/generation-raw-first/RF-R-I06-H-C1-1.json': '523241b3e6c591ac047ac7e044ddcbdda9ac1c30d86e45fff99a1aac653f5109', 'reviews/generation-raw-first/RF-R-I06-H-C1-2.json': 'b258e338f124e3cf72d8411301d42d731183ed2177a6da54a82dba678116c75c', 'reviews/generation-raw-first/RF-R-I06-H-C2-1.json': '91a2da598b3bcfa855921419ca776a8b195d99514874a166e719f0c57ca674ec', 'reviews/generation-raw-first/RF-R-I06-H-C2-2.json': 'fdd146f007972f7f6d379b1499ae1583b450aac9a6cf20f9cbdaf8f832485dd6', 'reviews/generation/RG-I06-A-P-1.json': 'e5783bf130acb249aca4b2f1ef70d9cce7eee7957460baf5f21aae102a958577', 'reviews/generation/RG-I06-A-P-2.json': 'c35cc8f751b3d319d14b9c0de9388846dfb477426f71fc1cf54fa34a2a465529', 'reviews/generation/RG-I06-H-P-1.json': 'f2ae2d86500df038919bcbb7cc0ab322ba215da553617d5a3ba748dbba1e3f92', 'reviews/generation/RG-I06-H-P-2.json': 'fa3bc94d41c1a2e7df5a7ebcb012cf0179c3def1b7c19f081477dff96404c434', 'reviews/raw-first-capacity-post.json': '157f6deac1e7a188ae309f60ba719a923bfbb6245a851135284464b8ef02c7f6', 'reviews/raw-first-capacity-raw.json': '06befc268b64f62bbba9c3c63612702240dd6fa1d1a12ea6a4a3a428fcc5abd0', 'schedule.json': 'ba3cb605f55e602855fc3ceb183d9b9c033900818172eefa0eb57680c8d3397d', 'tools/blind_compression.py': 'f78641ac047fc48f293c6d56656cad46c5efa973754bc66855e95dd672affaca', 'tools/blind_generation_raw_first.py': '726a7be8cc4d0817c4765597041b9a6882154d5970e2e06f5fb44e4704832979', 'tools/blind_generation_v2.py': '6f834d134180dfe7f0ec6090121548d1619d0ac44dfc7efdeee49ae71b368847', 'tools/composition_i11_runtime_v2.py': 'd86fb79ecdc0bb0cbbfe16883a911d2c4009f5d061082698a839467bb4e3e5eb', 'tools/composition_i11_runtime_v3.py': 'fede2c0d74ab030eb0838c9dc3607c6699a9c7e5c075b4dcf256ef65e7094bdd', 'tools/generation_disputes_v2.py': 'f5c1ee61a756793ae19e38dc5080388379c899262ca14d6b77a7cebd724608ee', 'tools/generation_publication_v3.py': '8cb365376840bf47d378dfb88d1d3cfa3bf95afa7cdcad16d6f4ae0c88c3d633', 'tools/generation_raw_first_runtime.py': '7208e66906a2adf90a223401825ac09fafd23aa848d626454e950b49e4b16108', 'tools/generation_review_runtime_v2.py': '2dc5c0572d99115861540cfc874b733fa8d62c01b9e6c48fbc595466187f4a26', 'tools/generation_review_validation_raw_first.py': '2a1ac13bc46333cc110151684813f98f191702c47b43681dcb2f5e3d72dc2003', 'tools/generation_review_validation_v2.py': 'c9d7c162e4c9a9588c3086151706138dff76d0a6368520f5c6e3ce08c268c83f', 'tools/generation_runtime_v2.py': '609b705cf40ad1396edba4ba93a687103a6f63eed3201efb74cf6a55b09503d9', 'tools/i10_source_context_v4.py': '8584247b0b63af6454c285d65a2495f14f1f596950e7a9751a7072a8062b85f3', 'tools/i10_source_pool_v4.py': '356fc5ab3caa3d4a1672e402665814bf72508724c30a409a1ebfd54f2fb5d539', 'tools/prepare_i11_full_matrix_v2.py': 'a81b9c29a7001641f43869e276978d3141525fa67dca8ad82e19bcca849006ba', 'tools/presentation_v4.py': 'b3d3e8bcc2412dbac361ff00411dd41bf92d3e31c09e54252979c7418ea3e130', 'tools/raw_first_case_metrics.py': 'd45b8babe9222cd514c2e1133556b11d57157f8f47d761667ef067b35530e8e6', 'tools/raw_first_i04_metrics.py': '6c0f2349389663549517d49574671861db966b74dd9c6b2b51239e60c9d45f35', 'tools/raw_first_i05_metrics.py': '587acd07f9172a16432a2410d14a1626526bb671bc238e32f7adae3fa306da0d', 'tools/raw_first_i05_supplement_metrics.py': '40ee60a84092f3c1fcbd894d5c04ec39ca5a2c596ed11877539d77331f676696', 'tools/raw_first_i08_metrics.py': '7955601dd301af218775cde579dc1133573a8063b562d9dc1a319eeb667b804b', 'tools/runtime.py': '4a455c0c3ab0593177693e98b225059f7b78a7181d3881d428ec1d957a71b118', 'tools/test_composition_i11_runtime_v2.py': '8f2d10b1eec12f6f49b0bf05432fadb1065d693c491cad07fe8ed29623a4a238', 'tools/test_composition_i11_runtime_v3.py': '19a3be80fc3d17cd7d639ecadd20d82c42e8f9c4a0cf03c7327e887f94f42438', 'tools/test_i10_source_context_v4.py': '7e6803077ca9f821342c82964ecbf00a5b2d39140be5c55fc85e8a3b074c20f0', 'tools/test_i10_source_pool_v4.py': '32786aa9eab6b6fe4de95b27b93e937167569728d7b459749d0446cef809d0a0', 'tools/test_presentation_v4.py': 'a9cbfa566e3e9b544b33d975a9d714e4456ba00fb614fbf5f282f2306463ffe9', 'tools/test_raw_first_i08_metrics.py': '0328e0072c98f9f4ce8e3379b8025e19730cc9f3d34c1d1eede63a196fdbb8d7'}

FROZEN_CRITERIA_GENERATION = {'version': 'hammer-novelty-generation-v2', 'state': 'candidate_before_generation_freeze', 'primary_unit': 'Current paired case block, source-ID retention row, and declared fixed-pool presentation; diagnostic and fresh strata separate. Shared cases/controls are not independent across studies.', 'scales': {'usefulness': {'0': 'No decision-relevant mechanism or discriminating question under the valued outcome', '1': 'Potentially useful, bounded decision/probe relevance with explicit assumptions', '2': 'Clear decision-relevant mechanism or feasible discriminator under supplied resources; still unexecuted'}, 'observability': {'0': 'No predicted observation', '1': 'Observable prediction without a different result from a nearest plausible rival', '2': 'Source-linked different predictions with feasible bounded probe and defeat condition'}, 'fit': {'preserves': 'Proposal/probe respects all hard constraints under supplied resources', 'uncertain': 'Indispensable resource/condition or compliance unconfirmed', 'conditional': 'Explicitly requires relaxing a hard constraint', 'violates': 'Contradicts an unrelaxed hard constraint'}, 'novelty': {'new': 'Locally distinct causal operation or discriminating question relative to supplied archive', 'equivalent': 'Same causal relation/discriminator as archive', 'parameter': 'Only magnitude/wording/timing variant without new causal test', 'uncertain': 'Equivalence or causal distinction cannot be resolved'}, 'support': ['stipulated', 'inference', 'speculative', 'unsupported'], 'retention': ['retained', 'lost', 'uncertain', 'unobservable'], 'contract': ['met', 'partial', 'not_met', 'inapplicable'], 'execution': ['valid', 'invalid', 'missing', 'skipped']}, 'raw_qualification': 'intelligible,new,usefulness>=1,fitpreserves,observability2,supportnotunsupported,raw_judgment_resolved (retention excluded),confirmedfamily,semanticcontractmet; recurrenceonlymodeloutputs', 'retained_qualification': 'raw qualification plus neutral D retention retained; D-only additions excluded from raw gain', 'equivalence': 'case-local operation + carrier + causal path + expected discriminator; words/labels insufficient; uncertain links kept, never transitive forced merge', 'comparison': 'Within each block qualified A/Q raw families versus primary comparator; secondary overlap with all intelligible concurrent ordinary+creative raw families including uncertain equivalence links. Shared Z overlap separately. Raw execution/review incompleteness gates raw exclusivity; D loss does not erase raw generation. Post-only additions attributed separately.', 'review': {'main': ['raw candidate exact coverage', 'archive equivalence family membership', 'semantic contract met/partial/not_met/inapplicable', 'rival predictions and defeat', 'fit/usefulness/observability/support', 'D relation retention and losses', 'D-only additions', 'every lineage disposition'], 'p08': ['decision-changing uncertainty', 'distinct competing predictions', 'feasible bounded probe', 'unresolved contradiction', 'fit/support', 'case-local distinction versus other arm and archive'], 'p09': ['each raw ID causal-relation retention', 'each raw ID discriminator retention', 'each raw ID uncertainty retention', 'lineage consistency', 'summary-only unsupported additions', 'fit', 'parked/rejected explicit'], 'coverage': 'two independent reviews per unit/pair with exact matrix and row IDs; saved calls do not imply coverage', 'adjudication': 'At most one scalar-only adjudication permaincase and perP08/P09batch, only declared differences with type/enum validation; agreed scalars exact. Family membership disputes conservatively unresolved, no forced merges.', 'blinding': 'administrative method and job names replaced by opaque IDs; semantic content and causal evidence preserved; recognizability can remain', 'stage_completeness': 'raw_assessment_complete and raw_execution_valid distinct from post_assessment_complete and execution_valid. A failed/missing D yields retention unobservable, does not erase valid raw dual coverage; gates retention/P10.', 'failure_gates': 'Missing/invalid independent review preserves source candidates with null semantic assessments in separate gated reports; all planned units/pairs/rankings disposed explicitly. Do not claim zero novelty.'}, 'p10': {'ordinary_key': ['fit preserves/uncertain/conditional/violates', 'descending usefulness', 'descending observability', 'raw order Z1,Z2,A1,A2,Q1,Q2 then lexical raw ID'], 'ordinary': 'first two retained distinct families, stable ID tie break', 'eligible': 'intelligible,new,usefulness>=1,fit preserves,observability2,retained,resolved,confirmed family,support not unsupported; reuse locked fields, no additional semantic assessment', 'alternative': 'ordinary first slot unchanged; highest-ranked eligible candidate family distinct from first and without uncertain-equivalence link; ordinary second fallback if none', 'gates': 'complete execution + two-review coverage + locked judgments/equivalence; otherwise not_evaluable with cause, never zero exposure', 'conservation': 'identical candidate set and fixed assessments, entering/displaced fields, family exposure, utility displacement, violations and text burden; no better human decision inference', 'strata': ['120 historical assessed attempts', '56 fresh assessed attempts'], 'semantic_contract_policy': 'Deliberately independent from raw operator-success qualification: a useful distinct retained mechanism may qualify despite partial/not_met operator form. Report entering/displaced candidate contract statuses separately. This cannot credit the generating operator with semantic success. Null/unresolved contract is ineligible. Historical contract field unavailable uses original locked rubric.'}, 'burden': {'raw_soft_words': 420, 'distill_soft_words': 350, 'review_soft_words': 6000, 'review_case_packets_max_per_shard': 1, 'meaning': 'Saved words/native role calls are proxies. Actual tokens/internal calls unknown. Full exact coverage precedes brevity; overage reported, never silently truncated.', 'prospective_change': 'Before first G native launch; exact raw/post/pair/addition assessment matrix. See generation-review-contract.v2.json. Original I01/I09 criteria remain immutable.'}, 'retry_policy': 'zero scored retries; failed dependency skips retained in denominators; unscored code/preflight repair before freeze allowed', 'claim_ceiling': 'Supplied synthetic facts, model proposals, model assessments and deterministic presentation outcomes separate; physical/operational/human-decision tests unexecuted.', 'study_contracts': 'inputs/plan/portfolio.json; explicit phase dependencies and zero scored retries apply. I11 final is three-stage raw generation, no compression.', 'p09_fit_policy': 'Source fidelity preserves declared raw status; inherited source-category conflict is separately reported, not counted as a new compression addition. Operational/probe fit may remain uncertain despite source-stipulated proposal fit.'}

FROZEN_REVIEW_CONTRACT = {'version': 'generation-review-v2', 'scope': 'I02-I08 exact matched case block including every shared seed/concern, raw/convergence, summary, optional addition and prior-ID disposition. Not a full Robot Talks evaluation.', 'columns': {'raw_rows': ['card_id', 'intelligible', 'usefulness', 'observability', 'fit', 'support', 'novelty', 'contract', 'family_confirmed', 'evidence'], 'archive_pairs': ['card_id', 'archive_id', 'relation', 'evidence'], 'candidate_pairs': ['card_a', 'card_b', 'relation', 'evidence'], 'post_rows': ['card_id', 'source_ids', 'fit_preserved', 'new_assertion', 'evidence'], 'retention_rows': ['source_card_id', 'relation', 'discriminator', 'uncertainty', 'lineage_consistent', 'fit_preserved', 'complete_protected_fields', 'evidence'], 'lineage_rows': ['unit_id', 'source_id', 'disposition', 'targets_valid', 'meaning_consistent', 'evidence'], 'addition_rows': ['card_id', 'fit', 'support', 'evidence'], 'attack_rows': ['unit_id', 'attack_id', 'construction_link_met', 'evidence'], 'contradiction_rows': ['unit_id', 'pair_id', 'incompatible_decision_commitments', 'evidence'], 'unit_rows': ['unit_id', 'execution', 'no_opening_reason_supported', 'contract', 'evidence']}, 'row_identity': 'Blinded packet expected_matrix declares exact row IDs. Every identity once; no omissions of empty/invalid/skipped units. Prefix raw/summary IDs with opaque unit ID. All case-local raw card pairs and raw×ordinary-archive pairs explicit. Semantic equivalence disputes remain uncertain, never scalar-adjudicated into forced families.', 'raw_qualification': 'Same frozen criteria scalar meanings: intelligible true, novelty new, usefulness>=1, observability2, fit preserves, support not unsupported, contract met, family_confirmed true, independently resolved. Feasible probe resources must be source-supported; no physical/human measured success inferred. Shared seed/concern can establish overlap but is not attributed as treatment discovery.', 'pair_relations': ['equivalent', 'parameter', 'distinct', 'uncertain'], 'protected_retention': 'Relation and full prediction/probe including all rivals, directional comparisons, challenge/defeat and capacity/resource caveats; uncertainty and declared fit. Summaries may have six post cards per two raw cards; evaluate all post IDs, every raw source and exact lineage. Faithful inherited raw errors are separate from new summary assertions. Park/reject disposition may preserve protected content in its reason; absent targets alone do not prove loss.', 'unit_contract': 'Apply only the assigned per-unit instruction; ordinary/generic controls are not required to perform the treatment. Honest no viable opening is a valid execution result, not a discovery or zero-valued missing assessment. Distinguish raw completeness from summary completeness.', 'family_assessment': 'Judge all explicit archive/candidate pairs from causal operation, carrier/path and prediction/test, not words. family_confirmed only if relevant comparisons resolve. Same-family overlap prevents exclusivity even if comparator fit/contract is partial. Preserve uncertain links and no forced transitive merges.', 'burden': {'soft_saved_words': 6000, 'source_previous_allowance': 2500, 'prospective_change': 'I05 maximal complete matrix exceeds200 obligations at max6 summaries and max2 additions per arm; provide6000 before any scored generation, retain original allowance and first blocked preflight. All arms/reviewers identical; actual cost reported. Native unscored maximal matrix still required before admission.', 'shard': 'one complete case block per independent review', 'review_calls': 'two per case, one bounded scalar adjudicator maximum; no retries'}, 'adjudication': 'Exact differences of scalar grades only; freeze agreed scalars. Pair/family differences retain uncertain; no family merges. One native scalar-only turn per case max. Invalid review and dependency skips keep source IDs and null judgments, never zero novelty.', 'phase_gate': 'Own-study pilot findings must be locked before confirmation. Negative/unresolved outcomes are preserved and can be confirmed where portfolio allows; explicit eliminate/stop rules dispose dependent roles as skipped. No output-conditioned case selection.'}

FROZEN_COMPRESSION_SOURCE = 'Read only the supplied case and exact raw source artifacts. Do not read archives, operator instructions, sibling outputs, old compressed answers, parent context, web or agents. Reduce the inputs into a decision-useful set, with all hard constraints and uncertainties visible. Do not invent a mechanism, observation or certainty. Save first substantive JSON only at the assigned path, zero retries/repair; use python3 if needed. Final only confirms completion. Aim <=350 output words with the same soft allowance across arms.\nReturn JSON {case_id,role:D,openings:[{id:D1...,source_ids,claim,discriminator,fit,probe,uncertainty}],lineage:[{source_id,disposition,target_ids,reason}],decision}. Max six retained openings. Every supplied raw ID appears exactly once in lineage. disposition is retained|merged|rejected|parked; targets refer to actual D IDs and must correctly carry that source; rejected/parked sources have no targets. Every D source_ids is a nonempty known unique list. fit is exactly preserves|uncertain|conditional|violates. claim,discriminator,probe,uncertainty,reason,decision are strings. Distinct meaningful relations may be merged only if retained explicitly; otherwise park them.\nSource-bound repair: protect each raw candidate\'s causal relation, complete rival/discriminating prediction including every challenge/comparison/defeat condition, uncertainty, stopping/resource caveat and explicitly declared fit status. Preserve the exact meaning; do not strengthen "may", comparative targets, feasibility or observations. Unknown resources do not mean permission to relax constraints. If the raw declared fit conflicts with its source constraints, mark the conflict explicitly rather than silently correcting or strengthening it. An omitted protected item must be acknowledged as lost; retained labels cannot conceal loss. For parked/rejected candidates, carry their protected relation/test/uncertainty in lineage.reason where feasible, otherwise explicitly mark the omitted protected item. Any genuinely new proposed idea goes in a separate optional proposals field; it receives no preservation credit and cannot alter retained source meaning. No proposal is required. Save the real artifact body as JSON; final message confirms file/hash only.\n\nGeneration-source adapter: assigned source JSON has openings, not raw_candidates. The current openings are the exact supplied raw pool; protect claim,delta,prediction,probe,fit,assumptions. claim/delta are causal relation; prediction/probe include rivals and defeat. Source_ids and lineage.source_id use current local R IDs only; previous qualified lineage remains source context, never additional current raw candidates. If current openings=[], return openings=[] and lineage=[], explain no raw opening; optional proposals cannot fabricate a retained source. The inherited max6 retained D openings remains. Optional proposals max2, each {id:P1/P2,claim,fit,probe,uncertainty,source_gap}; assess them separately, never as retained or credited raw creation.\n'
