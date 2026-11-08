"""Exact pre-selection transforms for a disjoint one-Lesson native family.

Apply only to newly staged, unselected source/mapper/Context code. The current
native family and API33 package are never mutation targets.
"""
from __future__ import annotations

import ast


class TransformFault(ValueError):
    pass


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise TransformFault('closed native successor anchor differs: ' + old[:100])
    return text.replace(old, new, 1)


def counted(text: str, old: str, new: str, count: int) -> str:
    if text.count(old) != count:
        raise TransformFault('closed native successor anchor count differs: ' + old[:100])
    return text.replace(old, new)


LESSON_CONSTRUCTION = '''    lesson = fixture('operational-lesson')
    lesson.update(node_id=LESSON, name='Verify exact native representation gaps',
        owner_ref=PRINCIPAL, scope_ref=scope, evidence_refs=[T03_EVIDENCE],
        challenge_route='protocol:T03-technical-fixture-review', successor_refs=[],
        relation_refs=[{'relation_kind_ref':'relation.governed-by','direction':'source',
            'counterpart_kind':'policy','counterpart_ref':T03_RETENTION}],
        claim_ceiling='Current synthetic technical candidate; no canonical admission, application, effectiveness or external effect.')
    lesson['payload'].update(
        lesson_statement='Before accepting API33 artifact.query parity, verify each native representation gap against the exact selected mapping and source bytes.',
        scope_refs=[scope], applicability=T03_FAMILY,
        exclusions=['outside the exact API33 current source and mapped disposition'],
        predicted_benefit='No silent loss of representable artifacts in canonical or SQL queries.',
        falsifier='An exact source and mapping check passes while a representable artifact is omitted.',
        evidence_refs=[T03_EVIDENCE], counterevidence_refs=[],
        retention_policy_ref=T03_RETENTION,
        expires_at=json.loads((Path(__file__).parent/'episode-contract.json').read_bytes())['expires_at'],
        classification_assignment_refs=[], status='candidate')
'''


def transform(role: str, filename: str, text: str) -> str:
    if role == 'source' and filename == 'records.py':
        text = once(text, 'import json\n', 'import json\nfrom pathlib import Path\n')
        text = once(text, "IMPLEMENTATION = 'implementation:' + PREFIX + '-source-reader'",
                    "IMPLEMENTATION = 'implementation:' + PREFIX + '-source-reader'\nLESSON = 'operational-lesson:' + PREFIX\nT03_EVIDENCE = 'implementation/lab-runtime/local-host/working/api33-native-dispositions-independent-review-0003/REVIEW.md'\nT03_RETENTION = 'protocol:T03-retain-public-technical-evidence-exclude-session-memory/v1'\nT03_FAMILY = 'family:api33-native-disposition-review'")
        text = once(text, "    return {'principal': principal,", LESSON_CONSTRUCTION + "    return {'principal': principal,")
        text = once(text, "'implementation': implementation, 'agent-capability': capability}",
                    "'implementation': implementation, 'agent-capability': capability, 'operational-lesson': lesson}")
    elif role == 'source' and filename == 'build.py':
        for old, new in [
            ("len(items)==21,'all eleven sources and ten Typed Relations required'", "len(items)==22,'all twelve sources and ten Typed Relations required'"),
            ("len(cores)==21 and post!=before['projection'],'twenty-one independent prospective cores required'", "len(cores)==22 and post!=before['projection'],'twenty-two independent prospective cores required'"),
            ("'authored_current_artifacts':11,'authored_current_typed_relations':10", "'authored_current_artifacts':12,'authored_current_typed_relations':10"),
            ("'independent_participation_decision_cores':21", "'independent_participation_decision_cores':22"),
            ("'actual_original_targets':23,'records':21", "'actual_original_targets':24,'records':22"),
        ]:
            text = once(text, old, new)
    elif role == 'mapped' and filename == 'build.py':
        replacements = [
            ("records.ASSIGNMENT,records.COORDINATION,records.CONTEXT,records.CAPABILITY,records.IMPLEMENTATION,", "records.ASSIGNMENT,records.COORDINATION,records.CONTEXT,records.CAPABILITY,records.IMPLEMENTATION,records.LESSON,"),
            ("len(current)==15,'exact fifteen source nodes required'", "len(current)==16,'exact sixteen source nodes required'"),
            ("output['cut']['semantic_cursor']==25 and output['governance_cursor']==25", "output['cut']['semantic_cursor']==26 and output['governance_cursor']==26"),
            ("len(output['governed_nodes'])==15", "len(output['governed_nodes'])==16"),
            ("'node_count':15,'edge_count':10,'exact_governance_joins':25", "'node_count':16,'edge_count':10,'exact_governance_joins':26"),
            ("'node_count':15,'edge_count':10}),flush=True", "'node_count':16,'edge_count':10}),flush=True"),
        ]
        for old, new in replacements:
            text = once(text, old, new)
        text = counted(text, "'semantic_cursor':25", "'semantic_cursor':26", 2)
        text = counted(text, "'governance_cursor':25", "'governance_cursor':26", 2)
    elif role == 'context' and filename == 'generation.py':
        for old, new in [
            ("len(refs)==25,'mapped source closure incomplete'", "len(refs)==26,'mapped source closure incomplete'"),
            ("len(by_subject)==25 and native['cut']['semantic_cursor']==native['governance_cursor']==25", "len(by_subject)==26 and native['cut']['semantic_cursor']==native['governance_cursor']==26"),
            ("    require(not lessons,'current Operational Lessons require explicit applicability and mapped projection closure')", "    require(len(lessons)==1 and lessons[0]['version_ref'] in refs,'one current Operational Lesson requires exact mapped projection closure')\n    lesson_subject=lessons[0]\n    lesson_body=lesson_subject['record']\n    source.view.handle.operations.validate_record(lesson_body,'cal.artifact-type.operational-lesson/v1',source.view.data['projection'])\n    require(lesson_subject['kind']=='operational-lesson' and lesson_body['scope_ref']==source.sources.scope_ref\n        and source.sources.scope_ref in lesson_body['payload']['scope_refs']\n        and lesson_body['payload']['applicability']==records.T03_FAMILY\n        and lesson_body['payload']['status']=='candidate','exact current Lesson scope/family/status differs')\n    lesson_dispositions=[{'lesson':refs[lesson_subject['version_ref']]['artifact'],\n        'disposition':'retained-context-material-pending-explicit-applicability','authority_effect':'none'}]"),
            ("generated=now();expires=EL.instant", "generated=now();require(generated<EL.instant(lesson_body['payload']['expires_at']),'current Lesson expired before Context construction');expires=EL.instant"),
            ("len(node_ids)==15 and len(edge_ids)==10", "len(node_ids)==16 and len(edge_ids)==10"),
            ("'protocol:R03-native-require-exact:25'", "'protocol:R03-native-require-exact:26'"),
            ("len(bodies)==30,'complete twenty-five projected and five view/ontology carriers required'", "len(bodies)==31,'complete twenty-six projected and five view/ontology carriers required'"),
            ("'current_catalog_lessons':0,'selected_lesson_refs':[],'selection_rule':'Actual current source catalog checked; new lessons require explicit applicability closure.'", "'current_catalog_lessons':1,'inventory_dispositions':lesson_dispositions,'selected_lesson_refs':[],'selection_rule':'Exact current signed Lesson is retained; live independent lesson.select must decide applicability.'"),
        ]:
            text = once(text, old, new)
        text = counted(text, "semantic_cursor=25,governance_join_policy_ref=join_ref", "semantic_cursor=26,governance_join_policy_ref=join_ref", 2)
    elif role == 'context' and filename == 'build.py':
        for old, new in [
            ("'actual_generated_artifact_carriers':30,'ontology_nodes':15,'ontology_edges':10", "'actual_generated_artifact_carriers':31,'ontology_nodes':16,'ontology_edges':10"),
            ("'generated_carriers':30,'posture':'ready'", "'generated_carriers':31,'posture':'ready'"),
        ]:
            text = once(text, old, new)
    else:
        return text
    ast.parse(text)
    return text
