"""Prospective I12 mechanics; import, fixtures and validators grant no admission.

Preparation authors only code/drafts. All lifecycle planning is pure; the parent
performs native calls, exclusive publication and observed-event persistence.
Frozen helpers are called through private function globals and memory paths.
"""
from pathlib import Path, PurePosixPath
from itertools import combinations
from types import FunctionType, SimpleNamespace
import copy
import hashlib
import json
import re

import composition_i11_runtime_v3 as audited
import blind_generation_v2 as base
import blind_generation_raw_first as raw
import generation_review_validation_v2 as core_validation
import generation_review_validation_raw_first as raw_validation
import generation_disputes_v2 as disputes

R = Path(__file__).resolve().parents[1]
VERSION = 'composition-I12-native-v2'
SCHEDULE = 'composition-i12-schedule.draft-v2.json'
REVIEWS = 'composition-i12-reviews.draft-v2.json'
PACK = 'receipts/I12-native-author-inputs.v2.json'
AUTHOR_PROMPT = 'prompts/I12-native-author.v1.txt'
CONTRACT = 'contracts/I12-native-preparation-contract.v2.json'
BUDGET = 'receipts/I12-native-preparation-budget.v1.json'
CODE = 'tools/composition_i12_runtime_v2.py'
TESTS = 'tools/test_composition_i12_runtime_v2.py'
CHECK = 'reports/I12-native-runtime-preparation-code-check.v2.json'
FREEZE = 'freeze-I12-native.v2.json'
INDEPENDENT = 'reports/I12-native-independent-prelaunch.v2.json'
INDEPENDENT_OUTPUT = 'reports/I12-native-independent-prelaunch-review.v2.json'
ADMISSION = 'receipts/gates/I12-composition-native-admission.v2.json'
EVENTS = 'receipts/events.jsonl'
FIXTURE_RAW = 'fixtures/composition-i12-maximal-raw.v2.json'
FIXTURE_POST = 'fixtures/composition-i12-maximal-post.v2.json'
FIXTURE_INPUTS = 'fixtures/composition-i12-maximal-inputs.v2.json'
PROMPT_DIR = 'prompts/composition-i12-draft-v2'
CASES = ('H-P', 'A-P', 'H-C1', 'H-C2', 'A-C1', 'A-C2')
ARMS = ('OC', 'IC', 'OD', 'ID', 'GC')
SHARED = ('incumbent-seed', 'concern-beneficiary', 'concern-operations', 'concern-evidence')
TERMINAL = {'valid', 'invalid', 'missing', 'skipped'}
PAIR_COLUMNS = ['post_card_id', 'source_card_id', 'relation', 'evidence']
PAIR_RELATIONS = ['equivalent', 'parameter', 'distinct', 'uncertain']
RAW_COUNTS = dict(raw_rows=27, archive_pairs=108, candidate_pairs=351, post_rows=0,
                  retention_rows=0, lineage_rows=50, addition_rows=0, attack_rows=0,
                  contradiction_rows=180, unit_rows=14)
POST_COUNTS = dict(RAW_COUNTS, post_rows=30, retention_rows=10, lineage_rows=60,
                   addition_rows=10, unit_rows=19)
CAPACITY = {p: {'job_id': 'CAP-I12-MAXIMAL-' + p.upper() + '-V2',
    'prompt_ref': PROMPT_DIR + '/capacity-' + p + '.txt',
    'output_ref': 'reviews/composition-capacity/I12-maximal-' + p + '-v2.json',
    'validation_ref': 'reports/I12-maximal-native-' + p + '-capacity-validation.v2.json',
    'expected_rows': 730 if p == 'raw' else 855,
    'packet_ref': FIXTURE_RAW if p == 'raw' else FIXTURE_POST} for p in ('raw', 'post')}
json_text = audited.json_text
require = audited.require
sha = audited.sha
canonical_hash = raw.canonical_hash
field_paths = audited.field_paths


def relative(value):
    return (type(value) is str and bool(value) and '\\' not in value and ':' not in value
        and not value.startswith('/') and str(PurePosixPath(value)) == value
        and all(p not in ('..', '.') for p in value.split('/')))


def read(path):
    return json_text(Path(path).read_text())


def save_new(path, value):
    """Exclusive publication only, never invoked by memory tests."""
    data = value if isinstance(value, bytes) else (json.dumps(value, indent=2,
        ensure_ascii=False, allow_nan=False) + '\n').encode()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(data)


def bindings_valid(items, root=R):
    require(type(items) is list and bool(items), 'nonempty source bindings')
    seen = set()
    for x in items:
        require(type(x) is dict and set(x) == {'path', 'sha256'}, 'exact source binding keys')
        require(relative(x['path']) and re.fullmatch('[0-9a-f]{64}', x['sha256']) is not None,
                'normalized path and SHA256')
        require(x['path'] not in seen, 'duplicate bound path')
        seen.add(x['path'])
        require(sha(Path(root) / x['path']) == x['sha256'], 'source drift: ' + x['path'])


def schema_object(properties, optional=()):
    return {'type': 'object', 'properties': properties,
        'required': [k for k in properties if k not in optional], 'additionalProperties': False}


def string_schema(enum=None):
    return {'type': 'string', **({'enum': enum} if enum else {'minLength': 1, 'nonblank': True})}


def array_schema(items, maximum=None, minimum=0, unique=False):
    return {'type': 'array', 'items': items, 'minItems': minimum,
        **({'maxItems': maximum} if maximum is not None else {}),
        **({'uniqueItems': True} if unique else {})}


TEXT = string_schema()
STRINGS = array_schema(TEXT, unique=True)
FIT = string_schema(['preserves', 'uncertain', 'conditional', 'violates'])
RAW_CARD_SCHEMA = schema_object({'id': string_schema(['R1', 'R2']),
    'kind': string_schema(['mechanism', 'hypothesis', 'question']),
    'claim': TEXT, 'delta': TEXT, 'prediction': TEXT, 'probe': TEXT,
    'fit': FIT, 'assumptions': STRINGS, 'source_refs': array_schema(TEXT, minimum=1, unique=True)})
RAW_LINEAGE_SCHEMA = schema_object({'source_id': TEXT,
    'disposition': string_schema(['retained', 'changed', 'merged', 'parked', 'rejected']),
    'target_ids': STRINGS, 'reason': TEXT})
D_CARD_SCHEMA = schema_object({'id': string_schema(['D1', 'D2', 'D3', 'D4', 'D5', 'D6']),
    'source_ids': array_schema(TEXT, minimum=1, unique=True), 'claim': TEXT,
    'discriminator': TEXT, 'fit': FIT, 'probe': TEXT, 'uncertainty': TEXT})
D_LINEAGE_SCHEMA = schema_object({'source_id': TEXT,
    'disposition': string_schema(['retained', 'merged', 'rejected', 'parked']),
    'target_ids': STRINGS, 'reason': TEXT})
PROPOSAL_SCHEMA = schema_object({'id': string_schema(['P1', 'P2']),
    'claim': TEXT, 'fit': FIT, 'probe': TEXT, 'uncertainty': TEXT, 'source_gap': TEXT})


def role_schema(operation):
    if operation == 'compression':
        return schema_object({'case_id': string_schema(list(CASES)), 'role': string_schema(['D']),
            'openings': array_schema(D_CARD_SCHEMA, 6), 'lineage': array_schema(D_LINEAGE_SCHEMA),
            'decision': TEXT, 'proposals': array_schema(PROPOSAL_SCHEMA, 2)}, optional=('proposals',))
    properties = {'case_id': string_schema(list(CASES)),
        'role': string_schema(['convergence' if operation in ('consensus', 'deferred') else 'raw']),
        'openings': array_schema(RAW_CARD_SCHEMA, 1 if operation == 'seed' else 2),
        'assessment': TEXT, 'lineage': array_schema(RAW_LINEAGE_SCHEMA)}
    if operation == 'seed':
        properties['seed_status'] = string_schema(['viable', 'no_viable_seed'])
    if operation in ('consensus', 'deferred'):
        properties.update(contradictions=array_schema(schema_object({
            'pair': array_schema(TEXT, 2, 2, True), 'evidence': TEXT}), unique=True),
            contradiction_count={'type': 'integer', 'minimum': 0})
    return schema_object(properties)


def schema_errors(value, schema, path='$'):
    errors = []
    typ = schema['type']
    accepted = {'object': dict, 'array': list, 'string': str, 'integer': int,
                'boolean': bool, 'null': type(None)}
    if isinstance(typ, list):
        return [] if any(not schema_errors(value, dict(schema, type=t), path) for t in typ) else [path + ': union type']
    if type(value) is not accepted[typ]:
        return [path + ': exact ' + typ + ' type']
    if 'enum' in schema and value not in schema['enum']:
        errors.append(path + ': enum')
    if typ == 'object':
        if set(value) - set(schema['properties']) or set(schema['required']) - set(value):
            errors.append(path + ': exact required/optional keys')
        for k in set(value) & set(schema['properties']):
            errors.extend(schema_errors(value[k], schema['properties'][k], path + '.' + k))
    elif typ == 'array':
        if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', len(value)):
            errors.append(path + ': array bounds')
        if schema.get('uniqueItems') and len({canonical_hash(x) for x in value}) != len(value):
            errors.append(path + ': unique items')
        for i, x in enumerate(value):
            errors.extend(schema_errors(x, schema['items'], path + '[' + str(i) + ']'))
    elif typ == 'string':
        if len(value) < schema.get('minLength', 0) or schema.get('nonblank') and not value.strip():
            errors.append(path + ': nonblank string')
    elif typ == 'integer' and value < schema.get('minimum', value):
        errors.append(path + ': minimum')
    return errors


OPERATIONS = {
 'seed': 'Give exactly one incumbent R1 supported by the case, or openings=[] with seed_status=no_viable_seed and an explicit reason. Do not invent a viable seed.',
 'concern-beneficiary': 'Independently identify beneficiary outcome concerns and their central predictions from the assigned case. Keep decision-changing uncertainty explicit.',
 'concern-operations': 'Independently identify operational/resource/constraint concerns and their central predictions from the assigned case.',
 'concern-evidence': 'Independently identify evidence/probe/defeat-condition concerns and their central predictions from the assigned case.',
 'ordinary': 'Using the assigned incumbent, propose ordinary next candidates and informative probes within the stipulated case constraints.',
 'interface': 'Preserve the known parent functions and change only their linking interface. Specify a joint prediction, a link-broken control preserving each parent, and distinguishing/defeat observations. A juxtaposition alone is insufficient.',
 'generic': 'Using the assigned incumbent, propose creative next candidates and informative probes within the stipulated case constraints.',
 'consensus': 'Seek immediate consensus from the incumbent, the three fixed concerns and the assigned challenger. Preserve caveats; a vote is not evidence. Count each decision-relevant incompatible central-prediction pair once.',
 'deferred': 'Defer consensus from the incumbent, the three fixed concerns and the assigned challenger. Preserve opposed central predictions and uncertainty first; select the smallest separating probe or explicitly report none. Count each decision-relevant incompatible central-prediction pair once.',
 'compression': 'Compress only the assigned current raw pool, protecting claim,delta,prediction,probe,fit,assumptions and every rival/comparison/defeat/resource/stopping caveat. Preserve exact uncertainty and strength; acknowledge any loss in lineage.reason. Every current local R ID needs one lineage disposition; source_ids/lineage.source_id use local R IDs only. Previous qualified lineage is context, never additional current candidates. Every retained/merged target must carry that source. Optional proposals are separate fresh additions, cap2, with zero raw creation/preservation credit. Empty raw means empty retained openings/lineage.'}


def prompt_text(operation):
    common = ('Preparation template for a future native first-save role. Read only the exact assigned case '
        'and source artifacts. No archives, sibling outputs, parent history, web or agents. These resources/observations '
        'and known_parent_functions are stipulations, never measured effects. Preserve valued outcome '
        'and all hard constraints. No invented equipment, observations, efficacy or permissions. '
        'Use explicit no-opening with reason when appropriate. Zero retries/overwrite. '
        'Soft saved-word limit=' + ('350' if operation == 'compression' else '420') +
        '; overages charged equally. Final only artifact path/hash; parent observes FINAL separately.\n'
        'Current raw source_refs use exact case field paths or assigned <Gjob>:<Rlocal> IDs. '
        'Raw lineage covers every qualified prior current ID exactly once. retained/changed have '
        'exactly one existing current target; merged nonempty targets; parked/rejected empty. '
        'Convergence contradictions use unordered distinct <Gjob>:<Rlocal>:prediction IDs from '
        'all assigned current prior cards, evidence is nonblank; contradiction_count=len(contradictions). '
        'D uses the assigned current local R IDs, administered separately. '
        + base.MARKER + '\n')
    if operation == 'compression':
        common = common.replace(base.MARKER, '')
    return common + OPERATIONS[operation] + '\nReturn exactly this complete nested JSON Schema; no other keys:\n' + json.dumps(role_schema(operation), indent=2) + '\n'


def make_schedule():
    jobs, reviews, index = [], [], 801
    def add(case, arm, semantic_role, operation, priors):
        nonlocal index
        key = f'G{index:04d}'
        index += 1
        role = 'compression' if semantic_role == 'compression' else 'convergence' if semantic_role == 'convergence' else 'raw'
        j = {'job_id': key, 'study_id': 'I12', 'case_id': case,
            'phase': 'pilot' if case.endswith('-P') else 'confirmation', 'arm': arm,
            'role': role, 'semantic_role': semantic_role, 'operation': operation,
            'prompt_ref': f'{PROMPT_DIR}/{operation}.txt',
            'output_ref': f'outputs/composition-i12/{key}.json',
            'input_refs': [f'cases/{case}.json', *[p['output_ref'] for p in priors]],
            'depends_on': [p['job_id'] for p in priors],
            'requires_gates': ['I12-composition-native-admission', 'I05-I08-phase-readiness', 'I09-fidelity']
                + ([] if case.endswith('-P') else ['I12-pilot-lock'])
                + (['I12-dual-raw-lock'] if role == 'compression' else []),
            'maximum_current_openings': 6 if role == 'compression' else 1 if operation == 'seed' else 2,
            'maximum_optional_proposals': 2 if role == 'compression' else 0,
            'soft_saved_word_limit': 350 if role == 'compression' else 420}
        jobs.append(j)
        return j
    for case in CASES:
        shared = [add(case, 'shared', label, 'seed' if label == 'incumbent-seed' else label, []) for label in SHARED]
        for arm in ARMS:
            challenger = add(case, arm, 'challenger', 'generic' if arm == 'GC' else 'interface' if arm[0] == 'I' else 'ordinary', [shared[0]])
            converger = add(case, arm, 'convergence', 'deferred' if arm.endswith('D') else 'consensus', [*shared, challenger])
            add(case, arm, 'compression', 'compression', [converger])
        selected = [j for j in jobs if j['case_id'] == case]
        for phase in ('raw', 'post'):
            for n in (1, 2):
                key = f'RF-{"R" if phase == "raw" else "P"}-I12-{case}-{n}'
                reviews.append({'job_id': key, 'study_id': 'I12', 'case_id': case,
                    'phase': 'pilot' if case.endswith('-P') else 'confirmation',
                    'review_phase': phase, 'prompt_ref': f'{PROMPT_DIR}/review-{phase}.txt',
                    'depends_on': [j['job_id'] for j in selected if phase == 'post' or j['role'] != 'compression'],
                    'requires_raw_lock': phase == 'post',
                    'output_ref': f'reviews/composition-i12/{key}.json', 'soft_saved_word_limit': 20000})
    return ({'classification': 'draft_unadmitted_zero_scored_credit', 'jobs': jobs,
        'phase_budgets': {'pilot': {'G_D': 38, 'raw_post_reviews': 8, 'base': 46, 'maximum': 48},
                         'confirmation': {'G_D': 76, 'raw_post_reviews': 16, 'base': 92, 'maximum': 96}},
        'optional_scalar_turn': 'unused unless separately admitted; never automatic',
        'meaning': 'Four factorial cells; GC outside factorial. Instruction-process only; no whole Robot Talks/two-lane, physical efficacy or human-effect claim.'},
        {'classification': 'draft_unadmitted_dual_raw_then_dual_post', 'jobs': reviews})


def validate_schedule(schedule, reviews):
    expected = make_schedule()
    require(canonical_hash(schedule) == canonical_hash(expected[0]) and
            canonical_hash(reviews) == canonical_hash(expected[1]), 'exact 114 generation/D and 24 dual phase reviews')
    require(all(type(j[k]) is int for j in schedule['jobs'] for k in
        ('maximum_current_openings', 'maximum_optional_proposals', 'soft_saved_word_limit')),
        'exact integer budgets')
    require(all(type(j['soft_saved_word_limit']) is int and type(j['requires_raw_lock']) is bool
        for j in reviews['jobs']), 'typed review budget/phase gate')
    return {'valid': True, 'G_D': 114, 'raw_roles': 84, 'D_roles': 30, 'reviews': 24}


def validate_generation(job, body, case, priors):
    errors = schema_errors(body, role_schema(job['operation']))
    def need(ok, message):
        if not ok:
            errors.append(message)
    if type(body) is not dict or errors:
        return {'valid': False, 'errors': errors, 'semantic_validity': 'not asserted'}
    need(body['case_id'] == job['case_id'], 'assigned case ID')
    need(type(priors) is dict and set(priors) == set(job['depends_on']), 'exact assigned prior artifacts')
    if type(priors) is not dict:
        return {'valid': False, 'errors': errors, 'semantic_validity': 'not asserted'}
    source = {}
    for producer, artifact in priors.items():
        need(type(artifact) is dict and type(artifact.get('openings')) is list, 'typed prior source')
        for c in artifact.get('openings', []) if type(artifact) is dict and type(artifact.get('openings')) is list else []:
            need(type(c) is dict and c.get('id') in ('R1', 'R2'), 'known prior current R IDs')
            if type(c) is dict and type(c.get('id')) is str:
                need(producer + ':' + c['id'] not in source, 'unique prior current ID')
                source[producer + ':' + c['id']] = c
    current = [c['id'] for c in body['openings']]
    need(len(current) == len(set(current)), 'unique current IDs')
    is_D = job['role'] == 'compression'
    prior = {c['id'] for c in source.values()} if is_D else set(source)
    if is_D:
        need(len(priors) == 1 and len(prior) == len(source), 'D one immediate current raw pool')
        proposals = body.get('proposals', [])
        need(len({p['id'] for p in proposals}) == len(proposals), 'unique optional proposal IDs')
        for c in body['openings']:
            need(set(c['source_ids']) <= prior, 'D known current local source IDs only')
        if not prior:
            need(not body['openings'] and not body['lineage'], 'empty current raw cannot fabricate retained source')
    else:
        for c in body['openings']:
            need(set(c['source_refs']) <= set(source) | field_paths(case), 'only case fields/assigned qualified current source IDs')
    seen = []
    for row in body['lineage']:
        source_id, disposition, targets = row['source_id'], row['disposition'], row['target_ids']
        seen.append(source_id)
        need(source_id in prior and set(targets) <= set(current), 'known lineage source/current targets')
        need(len(targets) == 1 if disposition in ('retained', 'changed') else
            bool(targets) if disposition == 'merged' else not targets, 'lineage disposition target cardinality')
        if is_D:
            actual = {c['id'] for c in body['openings'] if source_id in c['source_ids']}
            need(set(targets) == actual, 'D lineage and source membership agree; no hidden loss')
    need(len(seen) == len(set(seen)) and set(seen) == prior, 'full unique prior-ID disposition coverage')
    if job['operation'] == 'seed':
        need((body['seed_status'] == 'viable' and current == ['R1']) or
             (body['seed_status'] == 'no_viable_seed' and not current), 'exactly one R1 or explicit no viable seed')
    if job['role'] == 'convergence':
        allowed = {p + ':prediction' for p in source}
        pairs = [tuple(sorted(c['pair'])) for c in body['contradictions']]
        need(all(set(c['pair']) <= allowed and len(set(c['pair'])) == 2 for c in body['contradictions']), 'known distinct qualified prior prediction IDs')
        need(len(set(pairs)) == len(pairs), 'unordered contradiction pair uniqueness')
        need(body['contradiction_count'] == len(pairs), 'exact contradiction count')
    return {'valid': not errors, 'errors': errors, 'semantic_validity': 'not asserted; protected meaning and evidence need fresh source-bound native judgments'}


def load_input_pack(root=R):
    root = Path(root)
    schedule, reviews = read(root / SCHEDULE), read(root / REVIEWS)
    validate_schedule(schedule, reviews)
    return {'schedule': schedule, 'reviews': reviews,
        'contract': read(root / 'generation-review-contract.v2.json'),
        'criteria': read(root / 'criteria-generation.v2.json'), 'archives': read(root / 'archives/case-archives.json'),
        'cases': {c: read(root / f'cases/{c}.json') for c in CASES},
        'prompts': {j['prompt_ref']: (root / j['prompt_ref']).read_text() for j in schedule['jobs']}}


class MemoryPath:
    def __init__(self, files, name=''):
        self.files, self.name = files, name
    def __truediv__(self, key):
        return MemoryPath(self.files, str(key))
    def read_bytes(self):
        return self.files[self.name]
    def read_text(self):
        return self.read_bytes().decode()


def isolated_builders(pack):
    """Same audited private-function adapter pattern; no helper globals touched."""
    paths = {'generation-schedule.v2.json': pack['schedule'],
             'generation-review-schedule.v2.json': pack['reviews'],
             'generation-review-contract.v2.json': pack['contract'],
             'criteria-generation.v2.json': pack['criteria'], 'archives/case-archives.json': pack['archives'],
             **{f'cases/{c}.json': value for c, value in pack['cases'].items()}}
    files = {p: (json.dumps(v, sort_keys=True, ensure_ascii=False) + '\n').encode() for p, v in paths.items()}
    files.update({p: text.encode() for p, text in pack['prompts'].items()})
    adapter = MemoryPath(files)
    def builder_path(value):
        return adapter if value is adapter else Path(value)
    private = FunctionType(base.build_packet.__code__, dict(base.build_packet.__globals__,
        Path=builder_path, read=lambda p: json_text(p.read_text())), base.build_packet.__name__, base.build_packet.__defaults__)
    private_base = SimpleNamespace(**{**vars(base), 'build_packet': private})
    private_raw = FunctionType(raw.build_raw.__code__, dict(raw.build_raw.__globals__, base=private_base),
        raw.build_raw.__name__, raw.build_raw.__defaults__)
    private_post = FunctionType(raw.build_post.__code__, dict(raw.build_post.__globals__,
        base=private_base, build_raw=private_raw), raw.build_post.__name__, raw.build_post.__defaults__)
    return adapter, private_raw, private_post


def builder_tuple(pack):
    return tuple(pack[k] for k in ('schedule', 'reviews', 'contract', 'criteria', 'archives'))


def expected_source_pairs(core):
    units = {u['unit_id']: u for u in core['units']}
    result = []
    for u in core['units']:
        if u['content_kind'] != 'summary':
            continue
        require(len(u['source_unit_ids']) == 1, 'one assigned immediate summary source pool')
        source = units[u['source_unit_ids'][0]]
        for post in u['artifact'].get('openings', []) if type(u['artifact'].get('openings')) is list else []:
            for card in source['artifact'].get('openings', []) if type(source['artifact'].get('openings')) is list else []:
                if type(post) is dict and type(post.get('id')) is str and type(card) is dict and type(card.get('id')) is str:
                    identity = {'post_card_id': post['id'], 'source_card_id': card['id']}
                    result.append({'row_id': base.opaque('E', 'source_pairs|' + json.dumps(identity, sort_keys=True, separators=(',', ':'))),
                        'identity': identity, 'null_semantics': u['execution'] != 'valid' or source['execution'] != 'valid', 'fixed_values': {}})
    result.sort(key=lambda x: canonical_hash(x['identity']))
    require(len({tuple(x['identity'].values()) for x in result}) == len(result), 'unique D x all assigned current source pairs')
    return result


def wrap_packet(core, admin, pack):
    mapped = {'generation-schedule.v2.json': SCHEDULE, 'generation-review-schedule.v2.json': REVIEWS}
    # Builder bytes are memory canonicalizations, not claimed saved-file hashes.
    admin['memory_input_bindings'] = admin.pop('input_bindings')
    for item in admin['memory_input_bindings']:
        item['path'] = mapped.get(item['path'], item['path'])
    admin.update(version=VERSION + '-opaque-map', custom_schedule_sha256=canonical_hash(pack['schedule']),
        review_schedule_sha256=canonical_hash(pack['reviews']))
    pairs = expected_source_pairs(core)
    wrapper = {'version': VERSION + '-wrapper', 'packet_id': core['packet_id'], 'phase': core['phase'],
        'core_packet': core, 'core_packet_sha256': canonical_hash(core),
        'raw_core_context_sha256': raw.raw_context_hash(core),
        'opaque_map_sha256': canonical_hash(admin),
        'custom_schedule_sha256': canonical_hash(pack['schedule']), 'review_schedule_sha256': canonical_hash(pack['reviews']),
        'source_pair_contract': {'columns': PAIR_COLUMNS, 'identity': PAIR_COLUMNS[:2], 'relations': PAIR_RELATIONS,
            'raw_creation_credit': 0, 'assessment_origin': 'fresh_post_only'},
        'expected_source_pairs': pairs, 'matrix_counts': {**core['matrix_counts'], 'source_pairs': len(pairs)},
        'expected_total_rows': core['expected_total_rows'] + len(pairs),
        'planned_units': [{'unit_id': u['unit_id'], 'content_kind': u['content_kind'],
            'source_unit_ids': u['source_unit_ids']} for u in core['units']]}
    validate_packet(wrapper)
    return wrapper, admin


def build_raw_case(case, artifacts, dispositions, pack=None):
    pack = pack if pack is not None else load_input_pack()
    root, builder, _ = isolated_builders(pack)
    core, admin = builder('I12', case, artifacts, dispositions, root, builder_tuple(pack))
    return wrap_packet(core, admin, pack)


def build_post_case(case, artifacts, dispositions, raw_packet, raw_lock, pack=None):
    pack = pack if pack is not None else load_input_pack()
    validate_packet(raw_packet)
    validate_raw_lock(raw_packet, raw_lock)
    root, _, builder = isolated_builders(pack)
    core, admin = builder('I12', case, artifacts, dispositions, raw_packet['core_packet'],
        raw_lock['core_lock'], root, builder_tuple(pack))
    wrapper, admin = wrap_packet(core, admin, pack)
    wrapper['raw_wrapper_sha256'] = canonical_hash(raw_packet)
    wrapper['raw_wrapper_lock_sha256'] = canonical_hash(raw_lock)
    wrapper['raw_opaque_map_sha256'] = raw_packet['opaque_map_sha256']
    return wrapper, admin


def rederive_core_identities(core):
    """Independent complete identity derivation; no count can hide truncated obligations."""
    units = {u['unit_id']: u for u in core['units']}
    require(len(units) == len(core['units']), 'unique core units')
    cards = {u['unit_id']: [x['id'] for x in u['artifact'].get('openings', [])
        if type(x) is dict and type(x.get('id')) is str] if type(u['artifact'].get('openings')) is list else [] for u in core['units']}
    raw_ids = sorted(c for u in core['units'] if u['content_kind'] == 'source' for c in cards[u['unit_id']])
    wanted = {t: [] for t in base.TABLES}
    def row(t, **identity):
        wanted[t].append(identity)
    for c in raw_ids:
        row('raw_rows', card_id=c)
        for archive in core['archive']:
            row('archive_pairs', card_id=c, archive_id=archive['id'])
    for a, b in combinations(raw_ids, 2):
        row('candidate_pairs', card_a=a, card_b=b)
    for uid, u in units.items():
        require(all(s in units for s in u['source_unit_ids']), 'every assigned prior unit present')
        priors = [c for s in u['source_unit_ids'] for c in cards[s]]
        lineage = u['artifact'].get('lineage', [])
        emitted = [r['source_id'] for r in lineage if type(r) is dict and type(r.get('source_id')) is str] if type(lineage) is list else []
        for s in dict.fromkeys(priors + emitted):
            row('lineage_rows', unit_id=uid, source_id=s)
        if u['content_kind'] == 'summary':
            for s in priors:
                row('retention_rows', source_card_id=s)
            for c in cards[uid]:
                row('post_rows', card_id=c)
            proposals = u['artifact'].get('proposals', [])
            for p in proposals if type(proposals) is list else []:
                if type(p) is dict and type(p.get('id')) is str:
                    row('addition_rows', card_id=p['id'])
        for a in u['artifact'].get('attacks', []) if type(u['artifact'].get('attacks')) is list else []:
            if type(a) is dict and type(a.get('attack_id')) is str:
                row('attack_rows', unit_id=uid, attack_id=a['attack_id'])
        is_converger = u['content_kind'] == 'source' and len(u['source_unit_ids']) == 5
        require(('prediction_commitment_pairs' in u) == is_converger, 'convergence full prediction-pair metadata cannot be removed')
        if is_converger:
            commitments = sorted(c + ':prediction' for c in priors)
            declarations = u['artifact'].get('contradictions', [])
            declared = [tuple(sorted(z['pair'])) for z in declarations if type(z) is dict and
                type(z.get('pair')) is list and len(z['pair']) == 2 and all(type(v) is str for v in z['pair'])] if type(declarations) is list else []
            pairs = list(dict.fromkeys(list(combinations(commitments, 2)) + sorted(declared)))
            require({tuple(x['pair']) for x in u['prediction_commitment_pairs']} == set(pairs) and
                len(u['prediction_commitment_pairs']) == len(pairs), 'every prior central-prediction unordered pair')
            for pair in pairs:
                row('contradiction_rows', unit_id=uid, pair_id=uid + ':' + base.opaque('K', '|'.join(pair)))
        row('unit_rows', unit_id=uid)
    return wanted


def validate_packet(packet):
    require(type(packet) is dict and packet.get('version') == VERSION + '-wrapper', 'exact I12 wrapper required')
    core = packet['core_packet']
    require(packet['packet_id'] == core['packet_id'] and packet['phase'] == core['phase'] in ('raw', 'post'), 'wrapper/core exact phase and ID')
    require(packet['core_packet_sha256'] == canonical_hash(core) and
        packet['raw_core_context_sha256'] == raw.raw_context_hash(core), 'full core and exact raw context binding')
    require(core['contract']['columns'] == core_validation.EXACT_COLUMNS and set(core['expected_matrix']) == set(base.TABLES), 'untouched exact ten-table core')
    require(packet['source_pair_contract'] == {'columns': PAIR_COLUMNS, 'identity': PAIR_COLUMNS[:2],
        'relations': PAIR_RELATIONS, 'raw_creation_credit': 0, 'assessment_origin': 'fresh_post_only'} and
        type(packet['source_pair_contract']['raw_creation_credit']) is int, 'exact wrapper source pair contract')
    require(packet['planned_units'] == [{'unit_id': u['unit_id'], 'content_kind': u['content_kind'],
        'source_unit_ids': u['source_unit_ids']} for u in core['units']], 'all planned unit bindings')
    require(len(core['units']) == (14 if core['phase'] == 'raw' else 19), 'all 14/19 scheduled units including missing/invalid/skipped')
    require(sum(u['content_kind'] == 'source' for u in core['units']) == 14 and
        sum(u['content_kind'] == 'summary' for u in core['units']) == (0 if core['phase'] == 'raw' else 5), 'source/summary denominators')
    sources = [u for u in core['units'] if u['content_kind'] == 'source']
    shared = {u['unit_id'] for u in sources if not u['source_unit_ids']}
    challengers = [u for u in sources if len(u['source_unit_ids']) == 1]
    convergers = [u for u in sources if len(u['source_unit_ids']) == 5]
    require(len(shared) == 4 and len(challengers) == len(convergers) == 5, 'full original shared/challenger/convergence read graph')
    seed = {u['source_unit_ids'][0] for u in challengers}
    require(len(seed) == 1 and seed <= shared, 'identical seed only for challengers')
    challenger_ids = {u['unit_id'] for u in challengers}
    require(all(set(u['source_unit_ids'][:4]) == shared and u['source_unit_ids'][-1] in challenger_ids for u in convergers)
        and len({u['source_unit_ids'][-1] for u in convergers}) == 5, 'same exact shared input set plus own challenger')
    if core['phase'] == 'post':
        summaries = [u for u in core['units'] if u['content_kind'] == 'summary']
        require(all(len(u['source_unit_ids']) == 1 for u in summaries) and
            {u['source_unit_ids'][0] for u in summaries} == {u['unit_id'] for u in convergers}, 'one D for each own converger')
    wanted = rederive_core_identities(core)
    for t, identities in wanted.items():
        actual = [r['identity'] for r in core['expected_matrix'][t]]
        require(len(actual) == len(identities) and {canonical_hash(x) for x in actual} ==
            {canonical_hash(x) for x in identities}, 'full independently rederived core identities: ' + t)
        for row in core['expected_matrix'][t]:
            require(type(row['null_semantics']) is bool and type(row['fixed_values']) is dict, 'strict core obligation null/fixed types')
            require(row['row_id'] == base.opaque('E', t + '|' + json.dumps(row['identity'], sort_keys=True, separators=(',', ':'))), 'core identity hash')
    require(all(type(ob['null_semantics']) is bool and set(ob) == {'row_id','identity','null_semantics','fixed_values'} for ob in packet['expected_source_pairs']), 'exact typed extension obligations')
    require(packet['expected_source_pairs'] == expected_source_pairs(core), 'every D x all current assigned source pair; no truncation/drift')
    counts = {t: len(v) for t, v in core['expected_matrix'].items()}
    require(all(type(x) is int for x in core['matrix_counts'].values()) and core['matrix_counts'] == counts and
        type(core['expected_total_rows']) is int and core['expected_total_rows'] == sum(counts.values()), 'full core counts/types')
    require(packet['matrix_counts'] == dict(counts, source_pairs=len(packet['expected_source_pairs'])) and
        all(type(x) is int for x in packet['matrix_counts'].values()) and type(packet['expected_total_rows']) is int and
        packet['expected_total_rows'] == core['expected_total_rows'] + len(packet['expected_source_pairs']), 'full wrapper row counts/types')
    return True


def validate_raw_lock(packet, locked):
    validate_packet(packet)
    require(packet['phase'] == 'raw' and type(locked) is dict, 'raw wrapper lock')
    require(locked['case_packet_id'] == packet['packet_id'] and locked['raw_wrapper_sha256'] == canonical_hash(packet)
        and locked['opaque_map_sha256'] == packet['opaque_map_sha256'] and
        locked['custom_schedule_sha256'] == packet['custom_schedule_sha256'] and
        locked['source_pairs'] == [], 'exact full raw wrapper/map/schedule lock; raw extension empty')
    rows = raw.locked_rows(packet['core_packet'], locked['core_lock'])
    require(type(locked['fixture_only']) is bool, 'explicit fixture-only status')
    if locked['fixture_only']:
        require(locked['native_witnesses'] == [], 'synthetic lock has no actual native witness')
    else:
        require(len(locked['native_witnesses']) == 2, 'live lock two observed native witnesses')
    return rows


def validate_review(packet, review, raw_packet=None, raw_lock=None):
    """Pure exact WRAPPER/core/extension/carry structural validator."""
    errors = []
    try:
        validate_packet(packet)
        require(type(review) is dict and set(review) == {'case_packet_id', 'reviewer_id', 'core_review', 'source_pairs'}, 'exact four-field review wrapper')
        require(review['case_packet_id'] == packet['packet_id'] and type(review['reviewer_id']) is str
            and review['reviewer_id'] in packet['core_packet']['review_job_ids'] and
            review['core_review']['reviewer_id'] == review['reviewer_id'], 'same wrapper/core packet/assigned reviewer binding')
        if packet['phase'] == 'post':
            validate_raw_lock(raw_packet, raw_lock)
            require(packet['raw_wrapper_sha256'] == canonical_hash(raw_packet) and
                packet['raw_wrapper_lock_sha256'] == canonical_hash(raw_lock) and
                packet['raw_opaque_map_sha256'] == raw_packet['opaque_map_sha256'], 'full post wrapper/raw lock/map binding')
        result = raw_validation.validate_review(packet['core_packet'], review['core_review'],
            raw_packet['core_packet'] if raw_packet else None, raw_lock['core_lock'] if raw_lock else None)
        errors.extend(result['errors'])
        rows = review['source_pairs']
        require(type(rows) is list, 'source-pair rows list')
        expected = {tuple(ob['identity'][k] for k in PAIR_COLUMNS[:2]): ob for ob in packet['expected_source_pairs']}
        seen = set()
        for row in rows:
            require(type(row) is list and len(row) == 4 and all(type(x) is str and x.strip() for x in row[:2]), 'exact source-pair row width/identity types')
            key = tuple(row[:2])
            require(key not in seen and key in expected, 'unique known assigned source-pair identity')
            seen.add(key)
            ob = expected[key]
            require((row[2] is None if ob['null_semantics'] else type(row[2]) is str and row[2] in PAIR_RELATIONS)
                and type(row[3]) is str and bool(row[3].strip()), 'source-pair enum/nonblank evidence/null fixed semantics')
        require(seen == set(expected), 'exact complete source-pair coverage')
        return {'valid': not errors, 'errors': errors, 'phase': packet['phase'],
            'expected_rows': packet['expected_total_rows'], 'core_rows': packet['core_packet']['expected_total_rows'],
            'source_pair_rows': len(rows), 'row_counts': packet['matrix_counts'],
            'carried_rows': result.get('carried_rows', 0), 'fresh_rows': result.get('fresh_rows', 0) + len(rows),
            'carried_independent_grade_credit': 0, 'semantic_validity': 'not asserted; capacity checks structure/size only'}
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        return {'valid': False, 'errors': errors + [str(exc)], 'semantic_validity': 'not asserted', 'carried_independent_grade_credit': 0}


def validate_paths(packet_path, review_path, raw_packet_path=None, raw_lock=None):
    try:
        packet, review = read(packet_path), read(review_path)
        rp = read(raw_packet_path) if raw_packet_path else None
        result = validate_review(packet, review, rp, raw_lock)
        result.update(output_sha256=sha(review_path), saved_words=len(Path(review_path).read_text().split()),
            soft_saved_word_limit=20000, overage_words=max(0, len(Path(review_path).read_text().split()) - 20000))
        return result
    except (OSError, ValueError, UnicodeError) as exc:
        return {'valid': False, 'errors': ['missing/malformed/duplicate-key JSON: ' + str(exc)], 'semantic_validity': 'not asserted'}


def fixture_lock(packet):
    """UNSCORED planned null lock; cannot satisfy any live gate."""
    core = packet['core_packet']
    rows = []
    for table, obligations in core['expected_matrix'].items():
        for ob in obligations:
            fixed = raw.native_fixed_values(core, table, ob)
            values = {k: copy.deepcopy(ob['identity'].get(k, fixed.get(k))) for k in core['contract']['columns'][table]}
            values['evidence'] = 'UNSCORED fictional capacity lock; no independent native grade exists.'
            rows.append({'table': table, 'row_id': ob['row_id'], 'identity': copy.deepcopy(ob['identity']),
                'values': values, 'field_status': {k: 'unobservable' for k in values if k not in ob['identity'] and k not in fixed and k != 'evidence'}})
    lock = {'case_packet_id': core['packet_id'], 'rows': rows, 'disputes': [], 'family_disagreements': [],
        'independent_review_complete': False, 'meaning_status': 'gated_incomplete_review',
        'raw_packet_sha256': canonical_hash(core), 'raw_packet_context_sha256': raw.raw_context_hash(core),
        'source_bindings': [{'path': FIXTURE_RAW, 'sha256': canonical_hash(packet)}]}
    result = {'case_packet_id': packet['packet_id'], 'core_lock': lock, 'source_pairs': [],
        'raw_wrapper_sha256': canonical_hash(packet), 'opaque_map_sha256': packet['opaque_map_sha256'],
        'custom_schedule_sha256': packet['custom_schedule_sha256'], 'fixture_only': True, 'native_witnesses': []}
    validate_raw_lock(packet, result)
    return result


def reconcile_reviews(packet, reviews, prepared, starts, finals, output_payloads, source_bindings, raw_packet=None, raw_lock=None):
    """Pure dual-review lock. Core scalar/family compare stays frozen; extension separate."""
    require(len(reviews) == len(prepared) == len(starts) == len(finals) == len(output_payloads) == 2, 'exact dual review terminals')
    require(type(source_bindings) is list and source_bindings and all(relative(x['path']) and re.fullmatch('[0-9a-f]{64}', x['sha256']) for x in source_bindings), 'bound actual raw wrapper/core/map/schedule/review source hashes')
    require(len({x['agent_handle'] for x in starts}) == len({x['native_call_id'] for x in starts}) == 2, 'two distinct fresh reviewers')
    for p, s, f, payload, body in zip(prepared, starts, finals, output_payloads, reviews):
        digest = hashlib.sha256(payload).hexdigest() if payload is not None else None
        if payload is not None:
            try:
                require(canonical_hash(json_text(payload.decode())) == canonical_hash(body), 'review parsed bytes binding')
            except (ValueError, UnicodeError):
                require(body is None, 'malformed review must not invent parsed body')
        else:
            require(body is None, 'missing review must not invent body')
        start_valid(p['job_id'], s['agent_handle'], s, p, [])
        final_valid(p['job_id'], s['agent_handle'], f, p, s, digest)
    valid = [validate_review(packet, r, raw_packet, raw_lock) for r in reviews]
    complete = all(x['valid'] for x in valid)
    core = packet['core_packet']
    if complete:
        require({r['reviewer_id'] for r in reviews} == set(core['review_job_ids']), 'exact dual reviewer IDs')
        core_lock = disputes.compare(core, *[r['core_review'] for r in reviews])
        for row in core_lock['rows']:
            ob = next(x for x in core['expected_matrix'][row['table']] if x['row_id'] == row['row_id'])
            if ob['null_semantics']:
                row['field_status'] = {k: 'unobservable' for k in row['field_status']}
    else:
        # The audited pure reconciler supplies every planned null row and denominator.
        fake = [{'validation': {'valid': False}, 'terminal_observed': True,
            'terminal_witness': 'parent_received_NATIVE_FINAL_ANSWER', 'agent_handle': x['agent_handle'],
            'native_call_id': x['native_call_id']} for x in starts]
        old_starts = [dict(x, host_spawn_observed=True) for x in starts]
        core_lock = audited.reconcile_raw(core, [None, None], fake, old_starts)
    if packet['phase'] == 'post':
        carried = {(r['table'], r['row_id']): r for r in packet['core_packet']['raw_first']['carried_rows']}
        core_lock['rows'] = [copy.deepcopy(carried.get((r['table'], r['row_id']), r)) for r in core_lock['rows']]
    core_lock.update(independent_review_complete=complete,
        meaning_status='locked_source_bound_model_judgments' if complete else 'gated_incomplete_review',
        raw_packet_sha256=canonical_hash(core), raw_packet_context_sha256=raw.raw_context_hash(core),
        scalar_adjudication='unused unless separately admitted', family_merge_credit=0, source_bindings=copy.deepcopy(source_bindings))
    ext = []
    indexes = [{tuple(x[:2]): x for x in r['source_pairs']} if v['valid'] else {} for r, v in zip(reviews, valid)]
    for ob in packet['expected_source_pairs']:
        key = tuple(ob['identity'][k] for k in PAIR_COLUMNS[:2])
        a, b = [ix.get(key) for ix in indexes]
        resolved = complete and a[2] == b[2] and not ob['null_semantics']
        ext.append({'table': 'source_pairs', 'row_id': ob['row_id'], 'identity': ob['identity'],
            'values': {**ob['identity'], 'relation': a[2] if resolved else None,
                'evidence': json.dumps([a[3], b[3]]) if complete else 'Independent review unavailable/invalid; relation remains null.'},
            'field_status': {'relation': 'agreed' if resolved else 'family_unresolved' if complete and not ob['null_semantics'] else 'unobservable'}})
    return {'case_packet_id': packet['packet_id'], 'core_lock': core_lock, 'source_pairs': ext,
        'raw_wrapper_sha256': canonical_hash(packet), 'opaque_map_sha256': packet['opaque_map_sha256'],
        'custom_schedule_sha256': packet['custom_schedule_sha256'], 'source_bindings': copy.deepcopy(source_bindings), 'fixture_only': False,
        'native_witnesses': copy.deepcopy(finals), 'independent_review_complete': complete,
        'extension_family_merge_credit': 0, 'extension_raw_creation_credit': 0}


def review_schema():
    properties = {'reviewer_id': TEXT, 'columns': {'type': 'object', 'const': core_validation.EXACT_COLUMNS}, 'limits': TEXT}
    for table, columns in core_validation.EXACT_COLUMNS.items():
        specs = []
        for field in columns:
            if field in core_validation.IDENTITIES[table] or field == 'evidence':
                spec = TEXT
            elif field in core_validation.BOOLS:
                spec = {'type': ['boolean', 'null']}
            elif field in ('usefulness', 'observability'):
                spec = {'type': ['integer', 'null'], 'enum': [0, 1, 2, None]}
            elif field == 'source_ids':
                spec = array_schema(TEXT, unique=True)
            elif field == 'relation':
                spec = {'type': ['string', 'null'], 'enum': (['retained', 'lost', 'uncertain', 'unobservable'] if table == 'retention_rows' else PAIR_RELATIONS) + [None]}
            else:
                spec = {'type': ['string', 'null'], 'enum': core_validation.ENUMS[field] + [None]}
            specs.append(spec)
        properties[table] = {'type': 'array', 'items': {'type': 'array', 'prefixItems': specs,
            'items': False, 'minItems': len(specs), 'maxItems': len(specs)}}
    return schema_object({'case_packet_id': TEXT, 'reviewer_id': TEXT,
        'core_review': schema_object(properties), 'source_pairs': {'type': 'array', 'items': {
            'type': 'array', 'prefixItems': [TEXT, TEXT,
                {'type': ['string', 'null'], 'enum': PAIR_RELATIONS + [None]}, TEXT],
            'items': False, 'minItems': 4, 'maxItems': 4}}})


def review_prompt(phase, capacity=False):
    return (('Explicitly UNSCORED fictional maximal capacity; assess structure/size only. No efficacy or semantic adequacy claim. ' if capacity else '') +
        'Future fresh independent native ' + phase + ' reviewer. Read only this prompt and assigned exact opaque wrapper packet. '
        'No administrative map, other review, parent history, web or agents. First substantive JSON only assigned output; zero retries/overwrite. '
        'Soft saved-word limit20000; overages charged. Return all obligations, never truncate a core table or strip wrapper. '
        'Outer case_packet_id equals core_packet.packet_id; outer and core reviewer_id equal the assigned opaque phase reviewer. '
        'The old core review has exactly reviewer_id,columns,limits and its ten table arrays; add no core ID field. '
        'All ten table columns equal core_packet.contract.columns. Each identity, native fixed value and null_semantics comes from exact expected_matrix. '
        'Every row requires nonblank source-specific evidence. Null/unobservable/unresolved is distinct from zero. For every assessable obligation with null_semantics=false, supply the schema-required boolean, grade or enumeration based on the source and rubric. A fictional or UNSCORED assessment still needs permitted typed values; UNSCORED limits effect claims and does not license blanket nulls. Use permitted uncertain/partial/speculative categories or conservative low grades when justified; never invent observations. Null is allowed only for actual null/inapplicability/fixed-null obligations. Evidence must state the limitation. '
        'For post: copy every raw_first.carried_rows complete values and evidence exactly, with zero fresh independent/raw creation credit. '
        'Carried field_status is held exactly in the bound packet/lock. Fresh summary/proposal/retention and extension assessments remain separate. '
        'source_pairs are [] for raw; post requires every D card times every current card of its assigned source, even undeclared sources. '
        'Columns are post_card_id,source_card_id,relation,evidence. Relation equivalent|parameter|distinct|uncertain, null only when null_semantics; evidence always nonblank. '
        'Do not force family merges or invent missing review judgments. No automatic scalar turn. Final only actual saved path/hash.\n'
        'Exact full nested JSON Schema:\n' + json.dumps(review_schema(), indent=2) + '\n')


def maximal_fixture_pack(source_pack):
    pack = copy.deepcopy(source_pack)
    jobs = [j for j in pack['schedule']['jobs'] if j['case_id'] == 'H-P']
    remap = {j['job_id']: f'G{9001+i:04d}' for i, j in enumerate(jobs)}
    outputs = {j['output_ref']: f'UNSCORED-memory-only/{remap[j["job_id"]]}.json' for j in jobs}
    for j in jobs:
        j['job_id'] = remap[j['job_id']]
        j['depends_on'] = [remap[k] for k in j['depends_on']]
        j['output_ref'] = outputs[j['output_ref']]
        j['input_refs'] = [outputs.get(p, p) for p in j['input_refs']]
    pack['schedule'] = {'classification': 'UNSCORED_FICTIONAL_MAXIMAL', 'jobs': jobs}
    pack['reviews'] = {'classification': 'UNSCORED_FICTIONAL_MAXIMAL',
        'jobs': [j for j in pack['reviews']['jobs'] if j['case_id'] == 'H-P']}
    artifacts, dispositions = {}, {}
    for ordinal, job in enumerate(jobs):
        priors = {p: artifacts[p] for p in job['depends_on']}
        qualified = [p + ':' + c['id'] for p, a in priors.items() for c in a['openings']]
        prefix = f'UNSCORED fictional unit {ordinal+1} {job["semantic_role"]}'
        if job['role'] == 'compression':
            body = {'case_id': 'H-P', 'role': 'D', 'openings': [
                {'id': f'D{i}', 'source_ids': ['R1' if i <= 3 else 'R2'],
                 'claim': prefix + f' retained fictional alternative {i}; source relation remains hypothetical.',
                 'discriminator': 'Stipulated signal versus sham and link-broken control; stop if unavailable.',
                 'fit': 'uncertain', 'probe': 'Fictional bounded comparison only; no equipment/data access or probe executed.',
                 'uncertainty': 'May fail; resource capacity, rival and defeat conditions remain unknown.'} for i in range(1, 7)],
                'lineage': [{'source_id': f'R{i}', 'disposition': 'merged',
                    'target_ids': [f'D{n}' for n in (range(1, 4) if i == 1 else range(4, 7))],
                    'reason': 'Fictional full source accounting; claim/delta, prediction/probe, fit, assumptions, rival, defeat and stopping caveats remain hypothetical.'} for i in (1, 2)],
                'decision': 'UNSCORED structure only; no actual decision or retention success asserted.',
                'proposals': [{'id': f'P{i}', 'claim': prefix + f' fresh speculative proposal {i}.',
                    'fit': 'uncertain', 'probe': 'No real test or observations.', 'uncertainty': 'Unsupported fictional addition.',
                    'source_gap': 'Separately assessed addition; no source preservation/raw creation credit.'} for i in (1, 2)]}
        else:
            body = {'case_id': 'H-P', 'role': 'convergence' if job['role'] == 'convergence' else 'raw',
                'openings': [{'id': f'R{i}', 'kind': 'question', 'claim': prefix + f' fictional mechanism {i}.',
                    'delta': 'Stipulate a link-only change preserving parent functions; no discovered transformation.',
                    'prediction': f'Fictional alternative {i} may differ from rival under sham/control; no measured signal.',
                    'probe': 'Stipulated bounded probe with resource/stopping/defeat caveats; no physical or human execution.',
                    'fit': 'uncertain', 'assumptions': ['Fictional resources, evidence and feasibility remain unverified.'],
                    'source_refs': ['valued_outcome', *qualified]} for i in range(1, 2 if job['operation'] == 'seed' else 3)],
                'assessment': 'UNSCORED fictional maximal capacity; no real generated discovery or semantic score.',
                'lineage': [{'source_id': p, 'disposition': 'changed', 'target_ids': ['R1'],
                    'reason': 'Fictional explicit disposition only; no measured advantage.'} for p in qualified]}
            if job['operation'] == 'seed':
                body['seed_status'] = 'viable'
            if job['role'] == 'convergence':
                body.update(contradictions=[], contradiction_count=0)
        result = validate_generation(job, body, pack['cases']['H-P'], priors)
        require(result['valid'], 'fixture artifact structure: ' + repr(result['errors']))
        artifacts[job['job_id']] = body
        dispositions[job['job_id']] = {'execution': 'valid', 'cause': 'UNSCORED fictional memory source; no native trial/grade/event.'}
    source_ids = {j['job_id'] for j in jobs if j['role'] != 'compression'}
    raw_packet, raw_map = build_raw_case('H-P', {k: v for k, v in artifacts.items() if k in source_ids},
        {k: v for k, v in dispositions.items() if k in source_ids}, pack)
    lock = fixture_lock(raw_packet)
    post_packet, post_map = build_post_case('H-P', artifacts, dispositions, raw_packet, lock, pack)
    require(raw_packet['core_packet']['matrix_counts'] == RAW_COUNTS and raw_packet['expected_total_rows'] == 730, 'maximal raw exact 730 identities')
    require(post_packet['core_packet']['matrix_counts'] == POST_COUNTS and post_packet['expected_total_rows'] == 855
        and len(post_packet['expected_source_pairs']) == 60, 'maximal post exact 855 identities/60 source pairs')
    return {'classification': 'UNSCORED_FICTIONAL_MAXIMAL_STRUCTURE_ONLY', 'input_pack': pack,
        'artifacts': artifacts, 'dispositions': dispositions, 'raw_lock': lock,
        'raw_opaque_map': raw_map, 'post_opaque_map': post_map,
        'raw_packet': raw_packet, 'post_packet': post_packet,
        'capacity_assignments': {p: {'job_id': CAPACITY[p]['job_id'], 'packet_ref': CAPACITY[p]['packet_ref'],
            'prompt_ref': CAPACITY[p]['prompt_ref'], 'output_ref': CAPACITY[p]['output_ref'],
            'assignable_reviewer_ids': (raw_packet if p == 'raw' else post_packet)['core_packet']['review_job_ids'],
            'assigned_reviewer_id': (raw_packet if p == 'raw' else post_packet)['core_packet']['review_job_ids'][0],
            'expected_rows': CAPACITY[p]['expected_rows'], 'saved_word_soft_limit': 20000} for p in ('raw', 'post')},
        'synthetic_lock_live_gate_eligible': False, 'actual_native_witnesses': []}


def fixture_review(packet, reviewer=None):
    """Memory tests only; invented values never used as native capacity outcomes."""
    core = packet['core_packet']
    carried = {(r['table'], r['row_id']): r for r in core['raw_first']['carried_rows']}
    review = {'reviewer_id': reviewer or core['review_job_ids'][0],
        'columns': copy.deepcopy(core_validation.EXACT_COLUMNS), 'limits': 'UNSCORED memory validator specimen; no native or semantic grade.'}
    for table, obligations in core['expected_matrix'].items():
        rows = []
        for ob in obligations:
            key = (table, ob['row_id'])
            if key in carried:
                rows.append([copy.deepcopy(carried[key]['values'][c]) for c in review['columns'][table]])
                continue
            row = []
            for field in review['columns'][table]:
                if field in ob['identity']:
                    value = ob['identity'][field]
                elif field in ob['fixed_values']:
                    value = ob['fixed_values'][field]
                elif field == 'evidence':
                    value = 'UNSCORED memory-only specimen referring to exact obligation ' + ob['row_id']
                elif ob['null_semantics']:
                    value = None
                elif field in core_validation.BOOLS:
                    value = False
                elif field in ('usefulness', 'observability'):
                    value = 0
                elif field == 'relation':
                    value = 'uncertain'
                else:
                    value = core_validation.ENUMS[field][0]
                row.append(copy.deepcopy(value))
            rows.append(row)
        review[table] = rows
    return {'case_packet_id': packet['packet_id'], 'reviewer_id': review['reviewer_id'], 'core_review': review,
        'source_pairs': [[ob['identity'][k] for k in PAIR_COLUMNS[:2]] +
            [None if ob['null_semantics'] else 'uncertain', 'UNSCORED memory-only source-pair specimen.'] for ob in packet['expected_source_pairs']]}


def start_valid(key, handle, witness, prepared, log):
    require(type(handle) is str and bool(handle.strip()), 'actual native handle')
    require(type(witness) is dict and witness.get('native_start_observed') is True and
        witness.get('fresh_context') is True and type(witness.get('turn')) is int and witness['turn'] == 1,
        'actual fresh native turn1 start')
    for field in ('job_id', 'study_id', 'case_id', 'phase', 'prompt_ref', 'prompt_sha256',
                  'source_freeze_sha256', 'output_ref'):
        require(witness.get(field) == prepared.get(field) and field in witness and field in prepared,
            'start exact bound ' + field)
    require(witness['job_id'] == key and witness.get('agent_handle') == handle and
        type(witness.get('native_call_id')) is str and bool(witness['native_call_id'].strip()), 'actual handle/call identity')
    require(not any(e.get('event_kind') == 'native_spawn' and (e.get('agent_handle') == handle or
        e.get('native_call_id') == witness['native_call_id']) for e in log), 'fresh handle/call; zero retries')


def final_valid(key, handle, witness, prepared, started, digest):
    require(type(witness) is dict and witness.get('native_final_observed') is True and
        witness.get('terminal_witness') == 'parent_received_NATIVE_FINAL_ANSWER', 'actual parent-observed native FINAL')
    for field in ('job_id', 'study_id', 'case_id', 'phase', 'prompt_ref', 'prompt_sha256', 'source_freeze_sha256', 'output_ref'):
        require(field in witness and field in prepared and witness[field] == prepared[field], 'FINAL exact bound ' + field)
    require(type(witness.get('turn')) is int and witness['turn'] == 1 and witness['job_id'] == key and
        witness.get('agent_handle') == handle == started['agent_handle'] and
        witness.get('native_call_id') == started['native_call_id'] and 'output_sha256' in witness and
        witness['output_sha256'] == digest and (digest is None or type(digest) is str and re.fullmatch('[0-9a-f]{64}', digest)),
        'FINAL actual turn/handle/call/output hash or explicit missing')


def state_from_events(jobs, events):
    states = {k: 'pending' for k in jobs}
    prepared, started, handles, calls = {}, {}, set(), set()
    for e in events:
        if e.get('runtime_version') != VERSION:
            continue
        key = e.get('job_id')
        require(key in jobs, 'scheduled event job only')
        job = jobs[key]
        require(all(e.get(f) == job[f] for f in ('study_id', 'case_id', 'phase')), 'explicit scheduled event labels')
        kind = e.get('event_kind')
        if kind == 'job_prepared':
            require(states[key] == 'pending', 'first preparation only; zero retries')
            states[key], prepared[key] = 'ready', e
        elif kind == 'native_spawn':
            require(states[key] == 'ready', 'start after prepare only')
            start_valid(key, e.get('agent_handle'), e, prepared[key], [])
            require(e['agent_handle'] not in handles and e['native_call_id'] not in calls, 'fresh native handles/calls')
            handles.add(e['agent_handle']); calls.add(e['native_call_id'])
            states[key], started[key] = 'running', e
        elif kind == 'native_terminal_join':
            require(states[key] == 'running' and e.get('execution') in {'valid', 'invalid', 'missing'}, 'one actual FINAL join')
            final_valid(key, e.get('agent_handle'), e, prepared[key], started[key], e.get('output_sha256'))
            require(e['execution'] != 'missing' or e['output_sha256'] is None, 'missing output is null, not zero')
            require(e['execution'] == 'missing' or e['output_sha256'] is not None, 'saved valid/invalid requires output hash')
            states[key] = e['execution']
        elif kind == 'dependency_disposition':
            require(states[key] == 'pending' and e.get('status') == 'skipped' and
                type(e.get('cause')) is str and bool(e['cause'].strip()) and e.get('semantic_assessment') is None,
                'explicit ungraded planned skip')
            states[key] = 'skipped'
        else:
            raise ValueError('unknown I12 lifecycle event')
    return states


def coverage(jobs, events, artifacts=None, locked=None):
    states = state_from_events(jobs, events)
    return {'planned': len(jobs), 'actual_native_starts': sum(e.get('event_kind') == 'native_spawn'
        and e.get('runtime_version') == VERSION for e in events),
        **{s: sum(v == s for v in states.values()) for s in ('pending', 'ready', 'running', *sorted(TERMINAL))},
        'empty_valid': sum(states[k] == 'valid' and a.get('openings') == [] for k, a in (artifacts or {}).items() if k in states),
        'null_semantic_fields': sum(v is None for row in (locked or {}).get('core_lock', {}).get('rows', [])
            for k, v in row['values'].items() if k in row['field_status'])}


def prepare_job(job, jobs, states, artifacts, context):
    """Pure future planner. Parent must recheck ready/phase sources at actual publication/start."""
    require(states[job['job_id']] == 'pending' and context.get('output_exists') is False
        and context.get('prompt_exists') is False, 'first save/preparation only')
    require(context.get('admission_valid') is True and context.get('source_bound_phase_readiness') is True,
        'separate admission and parent I05/I08/I09 readiness required')
    base_receipt = {k: job[k] for k in ('job_id', 'study_id', 'case_id', 'phase', 'output_ref')}
    def skip(cause):
        return dict(base_receipt, runtime_version=VERSION, event_kind='dependency_disposition',
            status='skipped', cause=cause, semantic_assessment=None)
    if job['phase'] == 'confirmation' and context.get('confirmation_allowed') is not True:
        return skip('original_I12_pilot_policy_prevents_confirmation')
    bad = [k for k in job['depends_on'] if states[k] in {'invalid', 'missing', 'skipped'}]
    if bad:
        return skip('invalid_missing_or_skipped_prior: ' + ','.join(bad))
    require(all(states[k] in TERMINAL for k in job['depends_on']), 'all assigned prior dispositions terminal')
    if 'review_phase' not in job:
        require(all(states[k] == 'valid' for k in job['depends_on']), 'valid generation priors')
        seed = next((k for k in job['depends_on'] if jobs[k].get('operation') == 'seed'), None)
        if seed is not None and artifacts[seed].get('seed_status') == 'no_viable_seed':
            return skip('no_viable_shared_seed')
    if job.get('role') == 'compression' or job.get('review_phase') == 'post':
        lock = context.get('raw_lock')
        packet = context.get('raw_packet')
        validate_raw_lock(packet, lock)
        require(lock['fixture_only'] is False and context.get('dual_raw_final_observed') is True and
            context.get('raw_lock_source_binding_valid') is True, 'actual dual raw reviews and lock before every D preparation/start')
    input_refs = job.get('input_refs', []) if 'review_phase' not in job else context['review_input_refs']
    inputs = {p: context['source_hashes'][p] for p in input_refs}
    require(all(relative(p) and re.fullmatch('[0-9a-f]{64}', d) for p, d in inputs.items()), 'exact normalized source bindings')
    text = context['template'] + '\nExact assigned job binding: ' + json.dumps(base_receipt, sort_keys=True) + '\n'
    text += 'Exact allowed inputs and producer IDs: ' + json.dumps({p: {'sha256': d,
        'producer_job_id': next((j['job_id'] for j in jobs.values() if j['output_ref'] == p), None)} for p, d in inputs.items()}, sort_keys=True) + '\n'
    text += 'Write only first substantive JSON to ' + job['output_ref'] + '.\n'
    review_binding = {}
    if 'review_phase' in job:
        packet = context['review_packet']
        validate_packet(packet)
        require(packet['phase'] == job['review_phase'] and context['assigned_reviewer_id'] in packet['core_packet']['review_job_ids'], 'exact phase packet and assigned opaque reviewer')
        review_binding = {'assigned_reviewer_id': context['assigned_reviewer_id'],
            'wrapper_sha256': canonical_hash(packet), 'core_packet_sha256': packet['core_packet_sha256'],
            'opaque_map_sha256': packet['opaque_map_sha256'], 'custom_schedule_sha256': packet['custom_schedule_sha256']}
        text += 'Exact review binding: ' + json.dumps(review_binding, sort_keys=True) + '\n'
    return dict(base_receipt, **review_binding, runtime_version=VERSION, event_kind='job_prepared',
        prompt_ref=context['assigned_prompt_ref'], prompt_sha256=hashlib.sha256(text.encode()).hexdigest(),
        prompt_text=text, source_freeze_sha256=context['source_freeze_sha256'],
        input_bindings=[{'path': p, 'sha256': d} for p, d in sorted(inputs.items())],
        soft_saved_word_limit=job['soft_saved_word_limit'], scored_retries=0)


def phase_gate(job, receipt, policy_sha256, source_validator):
    """Mechanical binding/coverage checks; parent supplies completed upstream semantics."""
    require(not schema_errors(receipt, receipt_schemas()['phase_readiness']), 'exact typed parent phase-readiness schema')
    require(receipt.get('study_id') == 'I12' and receipt.get('phase') == job['phase'] and
        receipt.get('policy_source_sha256') == policy_sha256 and receipt.get('status') == 'pass', 'source-bound phase readiness')
    require(set(receipt.get('upstream', {})) == {'I05', 'I08', 'I09'}, 'all upstream dependencies')
    for key, row in receipt['upstream'].items():
        require(row.get('status') == 'pass' and row.get('native_terminals_observed') is True and
            row.get('complete_dual_assessments') is True and row.get('locked_decision') is True and
            (key != 'I09' or row.get('fidelity_ready') is True), 'parent upstream phase/fidelity completed source judgment')
        source_validator(row['source_bindings'])
    if job['phase'] == 'confirmation':
        policy = next(x for x in read(R / 'inputs/plan/portfolio.json')['studies'] if x['id'] == 'I12')
        require(receipt.get('decision_status') in policy['decision_statuses'] and
            receipt.get('failure_or_elimination') == policy['failure_or_elimination'] and
            type(receipt.get('confirmation_allowed')) is bool, 'original I12 pilot policy')
        source_validator(receipt['pilot_lock_bindings'])
        require({x['path'] for x in receipt['pilot_lock_bindings']} == {packet_ref(c, 'lock', p) for c in CASES[:2] for p in ('raw','post')}, 'both exact pilot raw and post locks')
        return receipt['confirmation_allowed'] is True and receipt['decision_status'] == 'advance_screen'
    return True


def authored_paths():
    return {CODE, TESTS, CHECK, SCHEDULE, REVIEWS, FIXTURE_RAW, FIXTURE_POST, FIXTURE_INPUTS,
        *[f'{PROMPT_DIR}/{x}.txt' for x in OPERATIONS],
        f'{PROMPT_DIR}/review-raw.txt', f'{PROMPT_DIR}/review-post.txt',
        f'{PROMPT_DIR}/capacity-raw.txt', f'{PROMPT_DIR}/capacity-post.txt',
        f'{PROMPT_DIR}/independent-prelaunch.txt'}


def source_paths(original_bindings, include_independent=True):
    """Exact prospective union, no freeze/admission/event-log hash cycle."""
    result = {x['path'] for x in original_bindings} | authored_paths() | {PACK, AUTHOR_PROMPT, CONTRACT, BUDGET}
    for c in CAPACITY.values():
        result.update([c['output_ref'], c['validation_ref']])
    if include_independent:
        result.update([INDEPENDENT, INDEPENDENT_OUTPUT])
    require(all(relative(p) for p in result) and not result & {FREEZE, ADMISSION, EVENTS}, 'exact acyclic prospective sources')
    return result


def capacity_source_paths(phase):
    return {FIXTURE_RAW, FIXTURE_POST, FIXTURE_INPUTS, CODE, TESTS, CHECK, CONTRACT, BUDGET,
        SCHEDULE, REVIEWS, CAPACITY[phase]['prompt_ref'], CAPACITY[phase]['output_ref']}


def receipt_schemas():
    binding = schema_object({'path': TEXT, 'sha256': TEXT})
    common = {'job_id': TEXT, 'study_id': TEXT, 'case_id': TEXT, 'phase': TEXT,
        'prompt_ref': TEXT, 'prompt_sha256': TEXT, 'source_freeze_sha256': TEXT,
        'output_ref': TEXT, 'agent_handle': TEXT, 'native_call_id': TEXT, 'turn': {'type': 'integer', 'enum': [1]}}
    start = schema_object(dict(common, native_start_observed={'type': 'boolean', 'enum': [True]},
        fresh_context={'type': 'boolean', 'enum': [True]}))
    final = schema_object(dict(common, native_final_observed={'type': 'boolean', 'enum': [True]},
        terminal_witness=string_schema(['parent_received_NATIVE_FINAL_ANSWER']), output_sha256={'type': ['string', 'null']}))
    capacity = schema_object({'classification': string_schema(['pass']), 'study_id': string_schema(['I12']),
        'capacity_phase': string_schema(['raw', 'post']), 'expected_rows': {'type': 'integer'},
        'actual_native_starts': {'type': 'integer', 'enum': [1]}, 'actual_native_terminal_joins': {'type': 'integer', 'enum': [1]},
        'native_start': start, 'native_final': final,
        'structural_validation': schema_object({'valid': {'type': 'boolean', 'enum': [True]},
            'output_sha256': TEXT, 'expected_rows': {'type': 'integer'}, 'core_rows': {'type': 'integer'},
            'source_pair_rows': {'type': 'integer'}}),
        'saved_word_soft_limit': {'type': 'integer', 'enum': [20000]}, 'saved_words': {'type': 'integer', 'minimum': 0},
        'overage_words': {'type': 'integer', 'minimum': 0}, 'source_bindings': array_schema(binding, minimum=1),
        'wrapper_sha256': TEXT, 'core_sha256': TEXT, 'opaque_map_sha256': TEXT,
        'custom_schedule_sha256': TEXT, 'raw_core_context_sha256': TEXT, 'assigned_reviewer_id': TEXT,
        'claim_ceiling': string_schema(['structure_and_size_only'])})
    independent = schema_object({'classification': string_schema(['independent_prelaunch_pass']),
        'study_id': string_schema(['I12']), 'source_bindings': array_schema(binding, minimum=1),
        'native_start': start, 'native_final': final, 'independent_from_author_and_capacity': {'type': 'boolean', 'enum': [True]},
        'runtime_source_audit_pass': {'type': 'boolean', 'enum': [True]},
        'independent_native_final_observed': {'type': 'boolean', 'enum': [True]}})
    gate = schema_object({'status': string_schema(['pass']), 'study_id': string_schema(['I12']),
        'freeze_sha256': TEXT, 'independent_prelaunch_sha256': TEXT,
        'raw_capacity_validation_sha256': TEXT, 'post_capacity_validation_sha256': TEXT,
        'parent_observed_receipts_complete': {'type': 'boolean', 'enum': [True]}})
    freeze = schema_object({'study_id': string_schema(['I12']), 'classification': string_schema(['exact_native_source_freeze']),
        'files': array_schema(binding, minimum=1)})
    return {'native_start': start, 'native_final': final, 'capacity_validation': capacity,
        'independent_prelaunch': independent, 'admission': gate, 'freeze': freeze,
        'phase_readiness': schema_object({'study_id': string_schema(['I12']),
            'phase': string_schema(['pilot','confirmation']), 'status': string_schema(['pass']),
            'policy_source_sha256': TEXT, 'upstream': schema_object({
                key: schema_object({'status': string_schema(['pass']),
                    'native_terminals_observed': {'type':'boolean','enum':[True]},
                    'complete_dual_assessments': {'type':'boolean','enum':[True]},
                    'locked_decision': {'type':'boolean','enum':[True]},
                    'source_bindings': array_schema(binding, minimum=1),
                    **({'fidelity_ready': {'type':'boolean','enum':[True]}} if key=='I09' else {})})
                for key in ('I05','I08','I09')}),
            'decision_status': string_schema(['advance_screen','no_advantage','no_opening','infeasible_probe','unresolved','protocol_invalid']),
            'failure_or_elimination': TEXT, 'confirmation_allowed': {'type':'boolean'},
            'pilot_lock_bindings': array_schema(binding,4,4)}, optional=('decision_status','failure_or_elimination','confirmation_allowed','pilot_lock_bindings'))}


def validate_readiness(bundle, original_bindings, source_validator, file_hash, events):
    """Pure receipt validation. Native authenticity/evidence quality are parent enforcement."""
    schemas = receipt_schemas()
    require(set(bundle) == {'raw_capacity', 'post_capacity', 'independent', 'freeze', 'admission', 'fixture_inputs', 'raw_capacity_review', 'post_capacity_review'}, 'separate capacity/audit/freeze/gate receipts')
    source_validator(original_bindings)
    fixture = bundle['fixture_inputs']
    raw_packet, post_packet = fixture['raw_packet'], fixture['post_packet']
    validate_packet(raw_packet); validate_packet(post_packet)
    handles, calls = [], []
    for phase in ('raw', 'post'):
        cap, spec = bundle[phase + '_capacity'], CAPACITY[phase]
        require(not schema_errors(cap, schemas['capacity_validation']), 'exact typed capacity receipt schema')
        require(cap['capacity_phase'] == phase and cap['expected_rows'] == spec['expected_rows'], 'both exact maximal capacities separately required')
        source_validator(cap['source_bindings'])
        require({x['path'] for x in cap['source_bindings']} == capacity_source_paths(phase), 'exact capacity source closure')
        packet = raw_packet if phase == 'raw' else post_packet
        require(cap['wrapper_sha256'] == canonical_hash(packet) and cap['core_sha256'] == packet['core_packet_sha256'] and
            cap['opaque_map_sha256'] == packet['opaque_map_sha256'] and cap['custom_schedule_sha256'] == packet['custom_schedule_sha256'] and
            cap['raw_core_context_sha256'] == packet['raw_core_context_sha256'], 'capacity full wrapper/core/map/custom schedule/context binding')
        review = bundle[phase + '_capacity_review']
        result = validate_review(packet, review, raw_packet if phase == 'post' else None, fixture['raw_lock'] if phase == 'post' else None)
        require(result['valid'] and cap['assigned_reviewer_id'] == review['reviewer_id'], 'actual saved capacity review parent validation and explicit assigned reviewer')
        digest = file_hash(spec['output_ref'])
        require(cap['structural_validation'] == {'valid': True, 'output_sha256': digest,
            'expected_rows': spec['expected_rows'], 'core_rows': 730 if phase == 'raw' else 795,
            'source_pair_rows': 0 if phase == 'raw' else 60}, 'actual parent structural full-matrix validator')
        p, s, f = cap['native_start'], cap['native_start'], cap['native_final']
        require(p['job_id'] == spec['job_id'] and p['study_id'] == 'I12' and p['case_id'] == 'UNSCORED-MAXIMAL'
            and p['phase'] == 'preparation' and p['prompt_ref'] == spec['prompt_ref'] and
            p['prompt_sha256'] == file_hash(spec['prompt_ref']) and p['output_ref'] == spec['output_ref'], 'explicit capacity native assignment')
        snapshot = sorted([x for x in cap['source_bindings'] if x['path'] != spec['output_ref']], key=lambda x: x['path'])
        require(s['source_freeze_sha256'] == canonical_hash(snapshot), 'capacity preparation source snapshot binding')
        start_valid(spec['job_id'], s['agent_handle'], s, p, [])
        final_valid(spec['job_id'], s['agent_handle'], f, p, s, digest)
        for kind, witness in [('native_spawn', s), ('preparation_terminal_join', f)]:
            matches = [e for e in events if e.get('event_kind') == kind and e.get('job_id') == spec['job_id']]
            require(len(matches) == 1 and matches[0].get('witness') == witness, 'actual parent-recorded capacity start/FINAL required')
        require(cap['overage_words'] == max(0, cap['saved_words'] - 20000), 'saved-word overages charged')
        handles.append(s['agent_handle']); calls.append(s['native_call_id'])
    independent = bundle['independent']
    require(not schema_errors(independent, schemas['independent_prelaunch']), 'separate typed independent receipt')
    source_validator(independent['source_bindings'])
    require({x['path'] for x in independent['source_bindings']} == source_paths(original_bindings, False), 'exact independent audited source union')
    s, f = independent['native_start'], independent['native_final']
    require(s['job_id'] == 'PREP-I12-INDEPENDENT-PRELAUNCH' and s['study_id'] == 'I12' and
        s['case_id'] == 'PRELAUNCH' and s['phase'] == 'preparation' and s['output_ref'] == INDEPENDENT_OUTPUT and
        s['prompt_ref'] == f'{PROMPT_DIR}/independent-prelaunch.txt' and s['prompt_sha256'] == file_hash(s['prompt_ref']), 'independent exact native assignment')
    start_valid(s['job_id'], s['agent_handle'], s, s, [])
    # Independent writes a review; parent later writes the separate receipt.
    # The freeze includes both; neither source union hashes itself.
    final_valid(s['job_id'], s['agent_handle'], f, s, s, file_hash(INDEPENDENT_OUTPUT))
    require(s['source_freeze_sha256'] == canonical_hash(independent['source_bindings']), 'independent audited-source snapshot binding')
    for kind, witness in [('native_spawn', s), ('preparation_terminal_join', f)]:
        observed = [e for e in events if e.get('event_kind') == kind and e.get('job_id') == s['job_id']]
        require(len(observed) == 1 and observed[0].get('witness') == witness, 'actual independent start/FINAL hash outside receipt')
    handles.append(s['agent_handle']); calls.append(s['native_call_id'])
    require(len(set(handles)) == len(handles) and len(set(calls)) == len(calls), 'separate fresh raw/post/independent calls')
    manifest, gate = bundle['freeze'], bundle['admission']
    require(not schema_errors(manifest, schemas['freeze']) and not schema_errors(gate, schemas['admission']), 'separate typed source freeze/admission')
    source_validator(manifest['files'])
    require({x['path'] for x in manifest['files']} == source_paths(original_bindings), 'exact future freeze source closure including separate independent receipt')
    require(gate['freeze_sha256'] == file_hash(FREEZE) and gate['independent_prelaunch_sha256'] == file_hash(INDEPENDENT)
        and gate['raw_capacity_validation_sha256'] == file_hash(CAPACITY['raw']['validation_ref']) and
        gate['post_capacity_validation_sha256'] == file_hash(CAPACITY['post']['validation_ref']), 'separate source-bound admission gate')
    return {'ready': True, 'freeze_sha256': gate['freeze_sha256'],
        'live_launch_requires_parent_phase_readiness': ['I05', 'I08', 'I09'],
        'claim_ceiling': 'native structure/size and source audit only; no efficacy'}


def ready(root=R):
    root = Path(root)
    original = read(root / PACK)['assigned_source_bindings']
    bundle = {'raw_capacity': read(root / CAPACITY['raw']['validation_ref']),
        'post_capacity': read(root / CAPACITY['post']['validation_ref']), 'independent': read(root / INDEPENDENT),
        'freeze': read(root / FREEZE), 'admission': read(root / ADMISSION), 'fixture_inputs': read(root / FIXTURE_INPUTS),
        'raw_capacity_review': read(root / CAPACITY['raw']['output_ref']), 'post_capacity_review': read(root / CAPACITY['post']['output_ref'])}
    budget = read(root / BUDGET)
    require(budget['scored_retries'] == 0 and budget['preparation_native_call_maximum'] == 6 and
        budget['completion_audit_native_call_maximum'] == 1 and budget['review_saved_word_soft_limit'] == 20000 and
        budget['experimental_pilot_base_and_maximum'] == [46, 48] and
        budget['experimental_confirmation_base_and_maximum'] == [92, 96], 'same separate nontransferable budget')
    events = [json_text(line) for line in (root / EVENTS).read_text().splitlines() if line.strip()]
    validate_budget(budget, events)
    return validate_readiness(bundle, original, lambda b: bindings_valid(b, root), lambda p: sha(root / p), events)


def independent_prompt():
    return ('Preparation-only separate independent prelaunch auditor. UNSCORED, zero admission authority. '
        'Read exactly the prospective audited source union declared by source_paths(original_bindings,False). '
        'Verify actual two capacity starts/parent-observed FINALs and parent full730/full855 validators; inspect code, '
        'strict schemas, 114/24 roles, exact read identity, every source pair, raw-before-D, carry/protected fields, '
        'null/skip/denominator behavior, zero retries, isolated frozen globals and source closure. '
        'No live trials, events, gate, freeze or progress mutation. Save only the separately assigned independent review first-save. Parent writes its separate receipt after actual FINAL. '
        'The parent adds its observed terminal/output hash outside that receipt to avoid a self-hash cycle. '
        'Require I05/I08 phase readiness and I09 fidelity separately before live launch. '
        'No whole Robot Talks/two-lane, physical efficacy or human-effect assertion.\n'
        'Prospective receipt schema:\n' + json.dumps(receipt_schemas()['independent_prelaunch'], indent=2) + '\n')


def check_D_ready(job, context):
    if job.get('role') == 'compression' or job.get('review_phase') == 'post':
        validate_raw_lock(context['raw_packet'], context['raw_lock'])
        require(context['raw_lock']['fixture_only'] is False and context.get('dual_raw_final_observed') is True
            and context.get('raw_lock_source_binding_valid') is True, 'live dual raw review lock before D prepare/spawn')


def verify_prepared(prepared, context):
    require(prepared['source_freeze_sha256'] == context['source_freeze_sha256'] and
        hashlib.sha256(context['actual_prompt_bytes']).hexdigest() == prepared['prompt_sha256'], 'prepared source/prompt byte drift')
    require(context.get('admission_valid') is True and context.get('source_bound_phase_readiness') is True, 'recheck admission and upstream phase sources')
    for x in prepared['input_bindings']:
        require(relative(x['path']) and context['source_hashes'].get(x['path']) == x['sha256'], 'prepared exact input source drift')


def spawn_job(job, prepared, witness, log, context):
    """Pure guarded native-start event planning; parent starts the actual call."""
    require(state_from_events({job['job_id']: job}, [e for e in log if e.get('job_id') == job['job_id']])[job['job_id']] == 'ready', 'one prepared first native start')
    require(context.get('output_exists') is False, 'native start before first substantive save')
    verify_prepared(prepared, context)
    check_D_ready(job, context)
    start_valid(job['job_id'], witness['agent_handle'], witness, prepared, log)
    return dict(witness, runtime_version=VERSION, event_kind='native_spawn')


def join_job(job, prepared, started, final, output_bytes, case=None, priors=None,
             packet=None, raw_packet=None, raw_lock=None):
    """Pure real-byte terminal validator; no repair/retry/save/event side effects."""
    digest = hashlib.sha256(output_bytes).hexdigest() if output_bytes is not None else None
    final_valid(job['job_id'], started['agent_handle'], final, prepared, started, digest)
    body = None
    try:
        require(output_bytes is not None, 'missing substantive output')
        body = json_text(output_bytes.decode())
        if 'review_phase' in job:
            require(packet is not None and prepared.get('wrapper_sha256') == canonical_hash(packet)
                and prepared.get('opaque_map_sha256') == packet['opaque_map_sha256'], 'review actual packet/map binding')
            result = validate_review(packet, body, raw_packet, raw_lock)
            require(body['reviewer_id'] == prepared['assigned_reviewer_id'], 'exact prepared assigned reviewer')
        else:
            result = validate_generation(job, body, case, priors or {})
    except (ValueError, UnicodeError, KeyError, TypeError, AttributeError) as exc:
        result = {'valid': False, 'errors': ['missing/malformed/duplicate-key/binding: ' + str(exc)], 'semantic_validity': 'not asserted'}
    saved_words = len(output_bytes.decode(errors='replace').split()) if output_bytes is not None else None
    result.update(output_sha256=digest, saved_words=saved_words,
        soft_saved_word_limit=job['soft_saved_word_limit'],
        overage_words=max(0, saved_words - job['soft_saved_word_limit']) if saved_words is not None else None)
    return dict(final, runtime_version=VERSION, event_kind='native_terminal_join',
        execution='missing' if output_bytes is None else 'valid' if result['valid'] else 'invalid',
        validation=result, parsed_body=body)


def packet_ref(case, kind, phase):
    require(case in CASES and phase in ('raw','post') and kind in ('packet','map','lock'), 'scheduled packet reference')
    directory = {'packet':'fixtures/composition-i12','map':'receipts/composition-i12-maps','lock':'reports/composition-i12-locked'}[kind]
    return f'{directory}/I12-{case}-{phase}.json'


def capacity_prompt(phase, fixture):
    assigned = fixture['capacity_assignments'][phase]
    text = review_prompt(phase, capacity=True)
    text += '\nExact preparation assignment: ' + json.dumps(assigned, sort_keys=True) + '\n'
    text += 'Read only this prompt, ' + str(R / assigned['packet_ref']) + '.\n'
    text += 'Write first substantive complete WRAPPER JSON only ' + str(R / assigned['output_ref']) + '.\n'
    text += 'Use assigned_reviewer_id=' + assigned['assigned_reviewer_id'] + '. Never write maps, locks, receipts, events or progress.\n'
    return text


def validate_budget(budget, events, schedule=None):
    """Actual observed starts charged in separate, nontransferable allocations."""
    require(type(budget['preparation_native_call_maximum']) is int and budget['preparation_native_call_maximum'] == 6
        and type(budget['completion_audit_native_call_maximum']) is int and budget['completion_audit_native_call_maximum'] == 1
        and budget['experimental_pilot_base_and_maximum'] == [46,48]
        and budget['experimental_confirmation_base_and_maximum'] == [92,96]
        and type(budget['scored_retries']) is int and budget['scored_retries'] == 0, 'separate I12 budget authority')
    starts = [e.get('witness', e) for e in events if e.get('event_kind') == 'native_spawn'
        and e.get('witness', e).get('study_id') == 'I12']
    require(len({e.get('agent_handle') for e in starts}) == len(starts) and
        len({e.get('native_call_id') for e in starts}) == len(starts), 'fresh actual starts; no retries or double charges')
    counts = {phase: sum(e.get('phase') == phase for e in starts)
        for phase in ('preparation','completion_audit','pilot','confirmation')}
    require(sum(counts.values()) == len(starts), 'explicit scheduled phase on every actual I12 start')
    require(counts['preparation'] <= 6 and counts['completion_audit'] <= 1
        and counts['pilot'] <= 48 and counts['confirmation'] <= 96, 'no budget transfer; all overages charged')
    return {'actual_observed_starts': len(starts), **counts, 'scored_retries': 0,
        'shared_sources_charged_once': True, 'automatic_scalar_turns': 0}


def factorial_contrasts(cells):
    """Interval arithmetic only; GC never enters factorial coefficients."""
    require(set(cells) == set(ARMS), 'all five cells, GC separately reported')
    for v in cells.values():
        require(v is None or type(v) is list and len(v) == 2 and all(type(x) is int for x in v)
            and v[0] <= v[1], 'typed locked-count bounds or unresolved null')
    def contrast(coefficients):
        if any(cells[k] is None for k in coefficients):
            return None
        low = sum((cells[k][0] if c > 0 else cells[k][1]) * c for k, c in coefficients.items())
        high = sum((cells[k][1] if c > 0 else cells[k][0]) * c for k, c in coefficients.items())
        return [low, high]
    return {'interface_at_consensus': contrast({'IC':1,'OC':-1}),
        'interface_at_deferred': contrast({'ID':1,'OD':-1}),
        'deferred_at_ordinary': contrast({'OD':1,'OC':-1}),
        'deferred_at_interface': contrast({'ID':1,'IC':-1}),
        'interaction': contrast({'ID':1,'IC':-1,'OD':-1,'OC':1}),
        'generic_benchmark_minus_ordinary_consensus': contrast({'GC':1,'OC':-1})}


def case_metrics(raw_packet, raw_lock, post_packet, post_lock, raw_map, post_map, pack, events):
    """Pure reporting of already locked judgments; never generates a semantic grade."""
    import raw_first_case_metrics as old_metrics
    validate_raw_lock(raw_packet, raw_lock); validate_packet(post_packet)
    require(raw_packet['opaque_map_sha256'] == canonical_hash(raw_map) and
        post_packet['opaque_map_sha256'] == canonical_hash(post_map) and
        raw_packet['custom_schedule_sha256'] == canonical_hash(pack['schedule']), 'exact source/maps/custom schedule for reporting')
    require(post_packet['raw_wrapper_sha256'] == canonical_hash(raw_packet) and
        post_packet['raw_wrapper_lock_sha256'] == canonical_hash(raw_lock) and
        post_lock['raw_wrapper_sha256'] == canonical_hash(post_packet), 'bound full raw/post wrapper locks')
    case = raw_map['case_id']
    selected = [j for j in pack['schedule']['jobs'] if j['case_id'] == case]
    judges = [j for j in pack['reviews']['jobs'] if j['case_id'] == case]
    require(len(selected) == 19 and len(judges) == 4, 'all I12 source/D/dual phase review denominators')
    jobs = {j['job_id']:j for j in selected + judges}
    states = state_from_events(jobs, [e for e in events if e.get('job_id') in jobs])
    raw_rows = raw_lock['core_lock']['rows']; post_rows = post_lock['core_lock']['rows']
    locked = {(r['table'],r['row_id']):r for r in raw_rows}
    current = {(r['table'],r['row_id']):r for r in post_rows}
    require(len(current) == post_packet['core_packet']['expected_total_rows'] and
        set(current) == {(t,o['row_id']) for t,rows in post_packet['core_packet']['expected_matrix'].items() for o in rows}, 'full post locked-row identities')
    require(type(post_lock['core_lock']['independent_review_complete']) is bool, 'explicit post completeness')
    for row in post_rows:
        require(set(row) == {'table','row_id','identity','values','field_status'} and
            set(row['values']) == set(post_packet['core_packet']['contract']['columns'][row['table']]), 'typed complete post locked columns')
        require(type(row['values']['evidence']) is str and bool(row['values']['evidence'].strip()) and
            type(row['field_status']) is dict and all(v in raw.STATUSES for v in row['field_status'].values()), 'post evidence/status types')
    require(all(current.get(k) == row for k,row in locked.items()), 'exact raw values/evidence/field_status in post reporting')
    require({r['row_id'] for r in post_lock['source_pairs']} == {o['row_id'] for o in post_packet['expected_source_pairs']}
        and len(post_lock['source_pairs']) == len(post_packet['expected_source_pairs']), 'full separate source-pair locked identities')
    raw_evaluable = (not raw_lock['fixture_only'] and raw_lock['core_lock']['independent_review_complete']
        and all(states[j['job_id']] == 'valid' for j in selected if j['role'] != 'compression'))
    post_evaluable = raw_evaluable and post_lock['core_lock']['independent_review_complete']
    units = {x['job_id']:x for x in raw_map['mapping'] if 'unit_id' in x}
    card_map = {x['opaque_id']:x for x in raw_map['mapping'] if x.get('field') == 'openings'}
    by_card = {r['identity']['card_id']:r for r in raw_rows if r['table']=='raw_rows'}
    pair_index = old_metrics.relation_index(raw_rows)
    output = {}
    shared_ids = [c for c,mapping in card_map.items() if jobs[mapping['job_id']]['arm']=='shared']
    for arm in ARMS:
        entries = {}
        arm_jobs = [j for j in selected if j['arm']==arm]
        for job in arm_jobs:
            ids = [c for c,identity in card_map.items() if identity['job_id']==job['job_id']]
            qualified = [c for c in ids if old_metrics.qualification(by_card[c])['status']=='eligible'] if raw_evaluable else []
            prior_units = set(job['depends_on'])
            prior_ids = [c for c,mapping in card_map.items() if mapping['job_id'] in prior_units]
            distinct = {c:old_metrics.exclusivity(c,prior_ids,pair_index) for c in qualified} if raw_evaluable else None
            source_distinct = [c for c in qualified if distinct[c]['status']=='exclusive'] if raw_evaluable else []
            entries[job['semantic_role']] = {'job_id':job['job_id'],'execution':states[job['job_id']],
                'candidate_count':len(ids), 'qualified_family_bounds':old_metrics.family_bounds(qualified,pair_index) if raw_evaluable and job['role']!='compression' else None,
                'new_probe_family_bounds':old_metrics.family_bounds(source_distinct,pair_index) if raw_evaluable and job['role']!='compression' else None,
                'direct_prior_exclusivity':distinct, 'fresh_shared_source_creation_credit':0,
                'raw_archive_and_incumbent_relations':[r for r in raw_rows if r['table']=='archive_pairs' and r['identity']['card_id'] in ids]}
        converger = next(j for j in arm_jobs if j['role']=='convergence')
        source_cards = [c for c,mapping in card_map.items() if mapping['job_id']==converger['job_id']]
        retention = [r for r in post_rows if r['table']=='retention_rows' and r['identity']['source_card_id'] in source_cards]
        retained = [r for r in retention if all(v in ('agreed','adjudicated') for v in r['field_status'].values())
            and all(r['values'][k]=='retained' for k in ('relation','discriminator','uncertainty'))
            and all(r['values'][k] is True for k in ('lineage_consistent','fit_preserved','complete_protected_fields'))]
        entries['fully_retained_raw_candidates'] = len(retained) if post_evaluable else None
        entries['contradiction_and_contract_rows'] = [r for r in raw_rows if r['table'] in ('contradiction_rows','unit_rows')
            and r['identity']['unit_id']==units[converger['job_id']]['unit_id']]
        output[arm] = entries
    terminals = [e for e in events if e.get('event_kind')=='native_terminal_join' and e.get('job_id') in jobs]
    overages = [{'job_id':e['job_id'],'saved_words':e['validation']['saved_words'],
        'soft_limit':jobs[e['job_id']]['soft_saved_word_limit'],
        'excess_words':max(0,e['validation']['saved_words']-jobs[e['job_id']]['soft_saved_word_limit'])}
        for e in terminals if type(e.get('validation',{}).get('saved_words')) is int]
    return {'study_id':'I12','case_id':case,'raw_comparison_evaluable':raw_evaluable,
        'post_retention_evaluable':post_evaluable,'arms':output,
        'qualified_family_contrasts':factorial_contrasts({a:output[a]['convergence']['qualified_family_bounds'] for a in ARMS}),
        'new_probe_contrasts':factorial_contrasts({a:output[a]['convergence']['new_probe_family_bounds'] for a in ARMS}),
        'shared_source_cards':len(shared_ids),'shared_convergence_creation_credit':0,
        'denominators':{'planned_G_D_roles':19,'planned_reviews':4,'raw_cards':len(by_card),
            'post_cards':len(post_packet['core_packet']['expected_matrix']['post_rows']),
            'optional_proposals':len(post_packet['core_packet']['expected_matrix']['addition_rows']),
            'source_pairs':len(post_packet['expected_source_pairs']),**coverage(jobs,[e for e in events if e.get('job_id') in jobs])},
        'separate_source_pair_relations':copy.deepcopy(post_lock['source_pairs']),
        'optional_proposal_rows':[r for r in post_rows if r['table']=='addition_rows'],
        'saved_words_proxy':sum(x['saved_words'] for x in overages),'soft_word_overages':overages,
        'carried_raw_rows':len(raw_rows),'carried_independent_grade_credit':0,
        'meaning':'Arithmetic over source-bound locked model judgments. GC outside factorial; no transitive family merges, whole Robot Talks/two-lane effect, physical efficacy or human benefit.'}
