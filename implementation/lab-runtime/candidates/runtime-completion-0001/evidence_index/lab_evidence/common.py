"""Closed, finite inputs over the accepted independently anchored reader."""
from lab_contracts.codec import canonical, closed, need, parse, sha
from lab_contracts.validation import validate

LIMIT = 16 * 1024 * 1024
POLICY_LIMIT = 32 * 1024 * 1024
STAGES = {'static', 'inert-contract', 'authorized-candidate-runtime',
          'final-qualification', 'human-observation', 'authorized-effect',
          'post-effect-verification'}
OUTCOMES = {'PASS', 'FAIL', 'ERROR', 'NOT_RUN', 'BLOCKED', 'UNKNOWN'}
PUBLIC_SELECTOR_FIELDS = {
    'lab-eligibility-context/v1': ['selection_binding','subject_bindings','evidence_bindings',
        'review_enrollments','policy_review_binding','policy_reviewer_identity','policy_author_identity',
        'public_retention_bindings','privacy_class','task_subject_bindings'],
    'lab-historical-selection/v1': ['documents','public_retention_bindings','privacy_class']}


def text(value):
    need(type(value) is str and 0 < len(value) <= 16384, 'TEXT_BOUND')


def sequence(value, maximum=20000):
    need(type(value) is list and len(value) <= maximum, 'ARRAY_BOUND')


def unique(value):
    sequence(value)
    for item in value:
        text(item)
    need(len(set(value)) == len(value), 'DUPLICATE_ID')


def binding(value):
    validate('ByteBinding', value)
    # This index only exports already reviewed public metadata. Protected
    # records require a separately selected public receipt; never follow them.
    need(value['kind'] != 'protected-input', 'PUBLIC_INDEX_ONLY')


def key(value):
    binding(value)
    return canonical(value)


def load(reader, expected, version, fields, *, max_bytes=LIMIT):
    binding(expected)
    value = parse(reader.read(expected, max_bytes=max_bytes), max_bytes=max_bytes)
    closed(value, ['schema_version', *fields])
    need(value['schema_version'] == version, 'SCHEMA_VERSION')
    return value


def digest(value):
    return sha(canonical(value))


def public_selector(reader, expected):
    binding(expected)
    value=parse(reader.read(expected,max_bytes=LIMIT),max_bytes=LIMIT)
    need(type(value) is dict and type(value.get('schema_version')) is str and
         value['schema_version'] in PUBLIC_SELECTOR_FIELDS,'PUBLIC_SELECTOR_VERSION')
    closed(value,['schema_version',*PUBLIC_SELECTOR_FIELDS[value['schema_version']]])
    need(value['privacy_class']=='reviewed-public-selector','PUBLIC_SELECTOR_CLASS')
    sequence(value['public_retention_bindings'],8192)
    for selected in value['public_retention_bindings']:binding(selected)
    # The enclosing bytes are independently selected for public retention.
    # They carry only this closed metadata shape; no arbitrary extra payload.
    if value['schema_version']=='lab-historical-selection/v1':
        sequence(value['documents'],256)
        for doc in value['documents']:
            closed(doc,['id','binding']);text(doc['id']);binding(doc['binding'])
    else:
        binding(value['selection_binding']);binding(value['policy_review_binding'])
        task_subjects(value['task_subject_bindings'])
        text(value['policy_reviewer_identity']);text(value['policy_author_identity'])
        sequence(value['subject_bindings'],256)
        for row in value['subject_bindings']:
            closed(row,['role','binding']);text(row['role']);binding(row['binding'])
        sequence(value['evidence_bindings'],4096)
        for selected in value['evidence_bindings']:binding(selected)
        sequence(value['review_enrollments'],4096)
        for entry in value['review_enrollments']:
            closed(entry,['review_binding','reviewer_identity','author_identity','evidence_core_digest'])
            binding(entry['review_binding']);text(entry['reviewer_identity']);text(entry['author_identity'])
            need(type(entry['evidence_core_digest']) is str and len(entry['evidence_core_digest'])==64
                 and all(c in '0123456789abcdef' for c in entry['evidence_core_digest']),'REVIEW_DIGEST')
    return value


def task_subjects(rows):
    """Exact later-task scope pairs; never override shared source or ancestry."""
    sequence(rows,4);result={}
    for row in rows:
        closed(row,['task_id','subject_bindings'])
        task=row['task_id']
        need(task in {'T27','T28','T29','T30'} and task not in result,'TASK_SUBJECT_ID')
        sequence(row['subject_bindings'],2);roles={}
        for item in row['subject_bindings']:
            closed(item,['role','binding']);binding(item['binding'])
            need(item['role'] in {'current-effect-scope','current-authority-review'} and
                 item['role'] not in roles,'TASK_SUBJECT_OVERRIDE')
            roles[item['role']]=item['binding']
        need(set(roles)=={'current-effect-scope','current-authority-review'},'TASK_SUBJECT_COVERAGE')
        result[task]=roles
    return result
