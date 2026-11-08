"""Cold synthetic API33 Lesson inputs; never a signed Source8 admission.

The selected native family has no current Lesson and its Context generator
refuses one. This fixture exercises the original rule contract while a
versioned Source/Mapper/Context successor is prepared separately.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[4]
RULES_PATH = ROOT / 'product/lab/release-candidates/v1/interface/lesson-selection-rules-v2/rules.py'
EVIDENCE = 'implementation/lab-runtime/local-host/working/api33-native-dispositions-independent-review-0003/REVIEW.md'
EVIDENCE_SHA = 'd76090f5e8e501282c9234b00cad68b8d53a36b81be8549cc119c990615b3c29'
RULES_SHA = 'c6cf7da53b31b1f125780875e759b2b02352251c405e4ca5cad5822ccddc5fa7'
PROJECT = 'project:cyberalchemy-v2-to-lab-migration'
FAMILY = 'family:api33-native-disposition-review'
LESSON_ID = 'operational-lesson:T03-api33-native-disposition-review-0001'
RETENTION = 'protocol:T03-retain-public-technical-evidence-exclude-session-memory/v1'
INSTRUCTION = 'instruction:inspect-exact-native-disposition-before-query-acceptance'
MANIFEST = Path(__file__).resolve().parent / 'source-manifest.json'
EXPECTED_FILES = {
    'implementation/lab-runtime/local-host/t03-current-learning-fixture-0001/fixture.py',
    'implementation/lab-runtime/local-host/t03-current-learning-fixture-0001/test_fixture.py',
    'implementation/lab-runtime/local-host/t03-current-learning-fixture-0001/README.md',
}
EXPECTED_INPUTS = {
    'product/lab/release-candidates/v1/interface/lesson-selection-rules-v2/rules.py',
    EVIDENCE,
    'authority/artifact-types/operational-lesson/v1/schema.json',
    'product/lab/release-candidates/v1/interface/lesson-selection-contract-v1/routing.schema.json',
    'product/lab/release-candidates/v1/interface/lesson-selection-contract-v1/applicability.schema.json',
    'product/lab/release-candidates/v1/interface/lesson-selection-contract-v1/domain-profile.schema.json',
    'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-947e6c2a5b3d10f8/mapped/packages/0001/mapping.json',
    'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-947e6c2a5b3d10f8/context/packages/0001/lesson-selection.json',
}


def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(raw):
    return sha256(raw).hexdigest()


def bind(ref, raw):
    return {'ref': ref, 'sha256': digest(raw)}


def verify_manifest():
    manifest = json.loads(MANIFEST.read_bytes())
    rows = manifest['files'] + manifest['input_bindings']
    if (set(manifest) != {'schema_version', 'files', 'input_bindings', 'claim_ceiling'}
            or manifest['schema_version'] != 'lab-t03-synthetic-lesson-source/v1'
            or {r['path'] for r in manifest['files']} != EXPECTED_FILES
            or {r['path'] for r in manifest['input_bindings']} != EXPECTED_INPUTS
            or len(rows) != len({r['path'] for r in rows})
            or any(set(r) != {'path', 'sha256'} for r in rows)):
        raise ValueError('fixture source inventory differs')
    for row in rows:
        path = ROOT / row['path']
        if path.resolve() != path or not path.is_file() or digest(path.read_bytes()) != row['sha256']:
            raise ValueError('fixture selected byte differs: ' + row['path'])
    return manifest


def rules_module():
    if digest(RULES_PATH.read_bytes()) != RULES_SHA:
        raise ValueError('selected Lesson rule bytes changed')
    spec = importlib.util.spec_from_file_location('t03_selected_lesson_rules', RULES_PATH)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build(now: datetime):
    """Return exact bytes and facts for a synthetic, non-admitted candidate."""
    if now.tzinfo is None:
        raise ValueError('aware fixture time required')
    now = now.astimezone(timezone.utc)
    verify_manifest()
    if not (ROOT / EVIDENCE).is_file() or digest((ROOT / EVIDENCE).read_bytes()) != EVIDENCE_SHA:
        raise ValueError('independent technical observation unavailable')
    selected_rules = rules_module()
    source_cut = {
        'branch_ref': 'branch:T03-synthetic-lesson-fixture-0001',
        'commit_sequence': 1,
        'commit_sha256': digest(b'T03 synthetic source; no signed store commit'),
        'source_profile_sha256': digest(b'T03 synthetic profile; no runtime profile'),
        'store_ref': 'T03-synthetic-lesson-fixture-0001',
        'streams': [],
    }
    assignment = {'scope_ref': PROJECT, 'identity_ref': 'agent-assignment:T03-synthetic-0001',
                  'version_ref': 'agent-assignment:T03-synthetic-0001@1',
                  'carrier_ref': 'cal.artifact-type.agent-assignment/v1',
                  'byte_sha256': digest(b'T03 synthetic assignment; no signed source')}
    session_ref = 'agent-session:T03-synthetic-0001'
    source_raw = b'T03 exact synthetic technical source; no signed Source8 claim'
    source_binding = bind('fixture:T03-technical-source', source_raw)
    evidence_raw = (ROOT / EVIDENCE).read_bytes()
    evidence_binding = bind(EVIDENCE, evidence_raw)
    lesson = {
        'schema_version': 'cyberalchemy-lab-operational-lesson/v1',
        'node_id': LESSON_ID, 'kind': 'operational-lesson',
        'name': 'Check native representation gaps before accepting API33 query parity',
        'lifecycle_state': 'candidate', 'authority_effect': 'none',
        'owner_ref': 'principal:T03-synthetic-technical-fixture',
        'scope_ref': PROJECT, 'evidence_refs': [EVIDENCE],
        'challenge_route': 'protocol:T03-technical-fixture-review',
        'successor_refs': [],
        'relation_refs': [{'relation_kind_ref': 'relation.governed-by', 'direction': 'source',
                           'counterpart_kind': 'policy', 'counterpart_ref': RETENTION}],
        'payload': {
            'lesson_statement': 'Before accepting API33 artifact.query parity, verify each native representation gap against the exact selected mapping and source bytes.',
            'scope_refs': [PROJECT], 'applicability': FAMILY,
            'exclusions': ['outside the exact API33 current source and mapped disposition'],
            'predicted_benefit': 'No silent loss of representable artifacts in canonical or SQL queries.',
            'falsifier': 'An exact source and mapping check passes while a representable artifact is omitted.',
            'evidence_refs': [EVIDENCE], 'counterevidence_refs': [],
            'retention_policy_ref': RETENTION,
            'expires_at': (now + timedelta(hours=24)).isoformat(),
            'classification_assignment_refs': [], 'status': 'candidate'},
        'claim_ceiling': 'Synthetic technical candidate for cold rule tests only; no native Source8 admission, host grant, application, or owner outcome.'}
    lesson_raw = compact(lesson)
    artifact = {'scope_ref': PROJECT, 'identity_ref': LESSON_ID,
                'version_ref': LESSON_ID + '@1.0.0-candidate.1',
                'carrier_ref': 'cal.artifact-type.operational-lesson/v1',
                'byte_sha256': digest(lesson_raw)}
    review = {'lesson': artifact, 'source_cut': source_cut, 'domain_scope_ref': PROJECT,
              'disposition': 'reviewed-for-controlled-use', 'effective_state': 'local-admitted-current',
              'fixture_only': True, 'authority_effect': 'none'}
    retention = {'policy_ref': RETENTION, 'retain_project_evidence': True,
                 'exclude_session_memory': True, 'authority_effect': 'none'}
    assessment = {'lesson': artifact, 'source_cut': source_cut,
                  'exclusion_text': lesson['payload']['exclusions'][0],
                  'excluded': False, 'authority_effect': 'none'}
    applicability = {'schema_version': 'lab-lesson-applicability/v1-candidate',
                     'lesson': artifact, 'source_cut': source_cut, 'project_ref': PROJECT,
                     'family': FAMILY, 'source_binding': source_binding,
                     'required_instruction_refs': [INSTRUCTION], 'excluded_tags': [],
                     'influence_ref': 'influence:T03-inspect-only', 'counterevidence': [],
                     'authority_effect': 'none'}
    session = {'session_ref': session_ref, 'assignment': assignment,
               'source_cut': source_cut, 'authority_effect': 'none'}
    inventory = {'source_cut': source_cut, 'lessons': [artifact],
                 'complete': True, 'authority_effect': 'none'}
    instruction = {**session, 'instruction_refs': [INSTRUCTION],
                   'veto_lesson_influence': False}
    basis = {**session, 'project_ref': PROJECT, 'family': FAMILY,
             'source_binding': source_binding, 'tags': []}
    def witness(label, value):
        raw = compact(value)
        return bind('fixture:T03-' + label, raw), raw
    session_b, session_raw = witness('session', session)
    inventory_b, inventory_raw = witness('inventory', inventory)
    instruction_b, instruction_raw = witness('instruction', instruction)
    basis_b, basis_raw = witness('basis', basis)
    review_b, review_raw = witness('review', review)
    retention_b, retention_raw = witness('retention', retention)
    assessment_b, assessment_raw = witness('exclusion', assessment)
    applicability_b, applicability_raw = witness('applicability', applicability)
    domain = {'schema_version': 'lab-lesson-selection-domain/v1-candidate',
              'scope_ref': PROJECT, 'source_cut': source_cut,
              'context_basis_binding': basis_b,
              'selection_method_binding': bind('lesson-selection-rules-v2/rules.py', RULES_PATH.read_bytes()),
              'supported_lesson_statuses': ['candidate'],
              'supported_retention_policy_refs': [RETENTION],
              'reviewed_use_postures': [{'disposition': review['disposition'],
                                          'effective_state': review['effective_state'],
                                          'fixture_only': True}],
              'authority_effect': 'none', 'actual_owner_outcome': None}
    domain_b, domain_raw = witness('domain', domain)
    route = {'schema_version': 'lab-lesson-selection-routing/v1-candidate',
             'source_cut': source_cut, 'assignment': assignment,
             'session_binding': session_b, 'inventory_binding': inventory_b,
             'instruction_precedence_binding': instruction_b,
             'domain_profile_binding': domain_b,
             'lessons': [{'lesson': artifact, 'review_binding': review_b,
                          'applicability_rule_binding': applicability_b}],
             'authority_effect': 'none', 'actual_owner_outcome': None}
    originals = {item['ref']: raw for item, raw in [
        (source_binding, source_raw), (evidence_binding, evidence_raw),
        (session_b, session_raw), (inventory_b, inventory_raw),
        (instruction_b, instruction_raw), (basis_b, basis_raw),
        (review_b, review_raw), (retention_b, retention_raw),
        (assessment_b, assessment_raw), (applicability_b, applicability_raw),
        (domain_b, domain_raw)]}
    fact = selected_rules.LessonFact(artifact, lesson_raw, PROJECT, True,
        selected_rules.ReviewFact(review_b, review['disposition'], review['effective_state'], True),
        applicability_b, retention_b,
        ((lesson['payload']['exclusions'][0], False),),
        (evidence_binding,), (), False)
    facts = selected_rules.ContextFacts('selection:T03-synthetic-0001', session_ref,
        assignment, source_cut, PROJECT, FAMILY, source_binding, (INSTRUCTION,),
        (), False, now, session_b, inventory_b, basis_b, instruction_b, (fact,))
    def read(binding):
        raw = originals[binding['ref']]
        if digest(raw) != binding['sha256']:
            raise ValueError('fixture original changed')
        return raw
    return selected_rules, lesson, route, facts, read, originals
