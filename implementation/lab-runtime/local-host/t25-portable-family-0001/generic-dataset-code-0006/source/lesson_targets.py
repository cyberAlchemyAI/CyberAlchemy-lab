"""One controlled operational Lesson and its complete typed evidence closure."""
import cal_installed_runtime_selection_v1 as _INSTALL_SELECTION
_INSTALL_SELECTION.guard()
import copy
import json
from .base import ROOT, require
from . import records
LESSON = 'operational-lesson:' + records.PREFIX + '-bounded-Session-review'
EVIDENCE_SET = 'evidence-set:' + records.PREFIX + '-bounded-Session-review'

def targets(projection, scope, config, end):
    lesson = records.common('operational-lesson', LESSON, scope)
    lesson['name'] = 'Use the exact scoped API30 discrepancy evidence before later Session reuse'
    lesson['relation_refs'] = [records.relation_ref('relation.derives-from', 'evidence-set', EVIDENCE_SET + '@' + records.VERSION)]
    lesson['evidence_refs'] = [EVIDENCE_SET + '@' + records.VERSION]
    lesson['payload'].update(lesson_statement='Controlled fixture: inspect the signed bounded Project State view for API30 discrepancies, preserve an exact evidence receipt, then independently assess before a later Session uses the result.', applicability='Only this signed fixture source, current bounded Session, and exact scoped Project State/API30 inspection.', exclusions=['original protected Source8', 'expired or revoked source or permission', 'sibling Session', 'unstated applicability', 'canonical admission', 'external tool authority', 'actual human learning'], predicted_benefit='A source-pinned discrepancy result can be assessed and consumed without carrying Session-private memory forward.', falsifier='Any source, permission, mapped Context, Lesson evidence or later-use binding differs from the selected cut.', expires_at=end, retention_policy_ref='protocol:' + records.PREFIX + '-lesson-retention/v1', scope_refs=[scope], status='fixture-reviewed-for-runtime-test', classification_assignment_refs=[], evidence_refs=[EVIDENCE_SET + '@' + records.VERSION], counterevidence_refs=[])
    evidence = records.common('evidence-set', EVIDENCE_SET, scope)
    evidence['name'] = 'Controlled API30 Session review evidence boundary'
    evidence['relation_refs'] = [records.relation_ref('relation.member-of', 'project', scope)]
    evidence['payload'].update(source_refs=['product/lab/release-candidates/v1/interface/current-participation-v5/source-manifest.json'], item_refs=['product/lab/release-candidates/v1/interface/api-integration-v30/source-manifest.json'], coverage_statement='Fixture-only source and API30 inspection scope; runtime observations and assessment require separate actual receipts.', limitations=['No protected Source8 authority', 'No actual human outcome', 'No canonical admission or broad effectiveness'])
    result = [{'category': 'artifact-instance', 'operation': 'admit', 'version_ref': body['node_id'] + '@' + records.VERSION, 'carrier_ref': 'cal.artifact-type.' + body['kind'] + '/v1', 'record': body, 'predecessor_ref': None, 'decision_ref': 'decision:' + records.PREFIX + ':' + body['kind'], 'contract': None} for body in (evidence, lesson)]
    projects = [s for s in projection['subjects'].values() if s['identity'] == scope and s['carrier_ref'] == 'cal.artifact-type.project-identity/v1' and (s['effective_state'] in ('admitted-current', 'local-admitted-current'))]
    require(len(projects) == 1, 'exact current Project endpoint absent')
    template = json.loads((ROOT / 'authority/artifact-types/candidates/0013-governance-transaction-surface/impacted-carrier-successors/typed-relation/v3/fixtures/valid/record.json').read_bytes())
    pairs = [('lesson-evidence', 'relation.derives-from', {'kind': 'operational-lesson', 'ref': LESSON, 'version_ref': LESSON + '@' + records.VERSION}, {'kind': 'evidence-set', 'ref': EVIDENCE_SET, 'version_ref': EVIDENCE_SET + '@' + records.VERSION}, {'derivation_role': 'Controlled Lesson derives from exact current fixture Evidence Set'}), ('evidence-project', 'relation.member-of', {'kind': 'evidence-set', 'ref': EVIDENCE_SET, 'version_ref': EVIDENCE_SET + '@' + records.VERSION}, {'kind': 'project', 'ref': scope, 'version_ref': projects[0]['version_ref']}, {'membership_role': 'Controlled review evidence in selected Project'})]
    for name, predicate, left, right, qualifiers in pairs:
        body = copy.deepcopy(template)
        identity = 'typed-relation:' + records.PREFIX + ':' + name
        body.update(node_id=identity, name=name, owner_ref=records.PRINCIPAL, scope_ref=scope, relation_refs=[], successor_refs=[], evidence_refs=[records.EVIDENCE], claim_ceiling=records.CLAIM)
        body['payload'].update(relation_kind_ref=predicate, source=left, target=right, qualifiers=qualifiers, relation_evidence_refs=[records.EVIDENCE])
        result.append({'category': 'typed-relation', 'operation': 'admit', 'version_ref': identity + '@' + records.VERSION, 'carrier_ref': 'cal.artifact-type.typed-relation/v3', 'record': body, 'predecessor_ref': None, 'decision_ref': 'decision:' + records.PREFIX + ':' + name, 'contract': None})
    return result
