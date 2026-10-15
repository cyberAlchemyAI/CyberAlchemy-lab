#!/usr/bin/env python3
"""Prepare scoped engineering inputs before execution; admit nothing."""
from pathlib import Path
import copy,json,sys
HERE=Path(__file__).resolve().parent;PACKAGE=HERE.parents[1]
sys.path.insert(0,str(PACKAGE/'workflows'))
from engineering import *


def prepare(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    original=ORIGINAL.read_bytes();output=corrected_source(original)
    goal=read(ROOT/'authority/artifact-types/goal/v1/fixtures/valid/goal.json')
    goal.update(goal_id='goal:lab-engineering:registered-interfaces',name='Support explicitly registered engineering Tools',
        outcome='Exact selected engineering interface works while default and rejected authority boundaries remain enforced.',
        rationale='W03 requires bounded source correction beyond the W02 counter interface.',success_conditions=list(EXPECTED_CHECKS),
        evidence_requirements=['exact before/after bytes','independent behavior and default regression receipts'],
        accountable_owner_ref='principal:repository-owner@candidate.1',claim_ceiling='Candidate W03 Goal scoped to the user complete-the-plan instruction; no full-plan achievement or admission.')
    validate_record(goal,'goal');goal_ref=goal['goal_id']+'@candidate.1'
    intent=read(ROOT/'authority/artifact-types/intent/v1/fixtures/valid/record.json')
    intent.update(node_id='intent:lab-engineering:registered-interfaces',direction=goal['outcome'],motivation=goal['rationale'],
        target_pressure='The exact W02 evaluator rejects every selected non-counter interface.',scope_ref=SCOPE,
        current_output_hypothesis={'artifact_type_ref':'cal.artifact-type.implementation/v1','description':'A separately reviewed registered-interface evaluator successor'},
        satisfaction_refs=list(EXPECTED_CHECKS))
    intent.pop('claim_ceiling',None)
    intent['constraints'].append('Scoped candidate Intent from current user development instruction; R08 owns admission.')
    validate_record(intent,'intent');intent_ref=intent['node_id']+'@candidate.1'
    work=artifact('work','registered-interface-correction',{'project_ref':SCOPE,'goal_refs':[goal_ref],
        'work_statement':'Correct the selected authority interface limitation and independently verify exact behavior.',
        'input_refs':[intent_ref,'protocol:W03-define','protocol:W03-design','protocol:W03-plan'],
        'output_refs':[],'completion_state':'candidate-prepared'},
        [{'relation_kind_ref':'relation.member-of','direction':'source','counterpart_kind':'project','counterpart_ref':SCOPE}])
    work_ref=work['node_id']+'@candidate.1'
    resolution=artifact('intent-resolution','registered-interface-selection',{'intent_ref':intent['node_id'],
        'selected_subject_refs':[work['node_id'],goal['goal_id']],'excluded_subject_refs':['canonical-admission','live-stores','external-effects'],
        'satisfaction_test_refs':list(EXPECTED_CHECKS),'owner_decision_ref':'protocol:deferred-owner-decision:R08'})
    resolution['claim_ceiling']='Candidate development scoping only. Owner Decision remains explicitly deferred R08; no actual Decision outcome is fabricated.'
    coord=read(ROOT/'authority/artifact-types/coordination-context/v2/fixtures/valid/product-project-goal.json')
    coord.update(coordination_context_id='coordination:lab-engineering:registered-interfaces',version='candidate.1',
        goal_ref=goal_ref,project_ref=SCOPE,purpose=work['payload']['work_statement'],
        product_ref='product:cyberalchemy-lab@foundation.1',owner_ref='principal:repository-owner@candidate.1',
        lifecycle_state='draft',revision_history=[],evidence_refs=['protocol:current-user-development-instruction'],
        bounded_context_refs=[],residue_refs=['protocol:deferred-owner-decision:R08'])
    coord['source_direction']['generator_sha256']=byte_sha((ROOT/'authority/artifact-types/coordination-context/v2/generator.py').read_bytes())
    validate_record(coord,'coordination-context')
    implementation=artifact('implementation','bounded-actor-authority',{'implementation_kind':'bounded-local-actor-evaluator',
        'conforms_to_schema_refs':['protocol:W02-exact-actor-and-Tool-contracts'],
        'realizes_capability_refs':[CAPABILITY+'@foundation.1'],
        'execution_entrypoint_ref':'protocol:W02-evaluator:'+byte_sha(original),
        'environment_contract_ref':'protocol:W03-pinned-Python-environment'},
        [{'relation_kind_ref':'relation.realizes','direction':'source','counterpart_kind':'product-capability','counterpart_ref':CAPABILITY}])
    rows=[]
    for kind,value,name,version in [('goal',goal,'goal.json','candidate.1'),('intent',intent,'intent.json','candidate.1'),
        ('work',work,'work.json','candidate.1'),('intent-resolution',resolution,'intent-resolution.json','candidate.1'),
        ('coordination-context',coord,'coordination-context.json','candidate.1'),('implementation',implementation,'original-implementation.json','w02-snapshot.1')]:
        raw=encoded(value);(directory/name).write_bytes(raw);rows.append({'path':name,'kind':kind,'identity_ref':identity(value),
            'version_ref':identity(value)+'@'+version,'sha256':byte_sha(raw),'posture':'isolated-candidate-current'})
    spec=importlib.util.spec_from_file_location('w03_coord_generator',ROOT/'authority/artifact-types/coordination-context/v2/generator.py')
    generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)
    (directory/'COORDINATION-CONTEXT.md').write_text(generator.render_instance(coord))
    (directory/'registered_evaluator.py').write_bytes(output)
    manifest={'schema_version':'lab-W03-scoped-input-selection/v1-candidate','authority_effect':'none','scope_ref':SCOPE,
        'records':rows,'intent_ref':intent_ref,'resolution_ref':resolution['node_id']+'@candidate.1','work_ref':work_ref,
        'goal_ref':goal_ref,'coordination_ref':coord['coordination_context_id']+'@candidate.1',
        'original_implementation_ref':implementation['node_id']+'@w02-snapshot.1',
        'original_source_sha256':byte_sha(original),'output_source_sha256':byte_sha(output),
        'owner_decision_status':'explicitly-deferred-R08','actual_owner_outcome':None}
    for name in ['define','design','plan']:
        value={'authority_effect':'none','record_class':'protocol-'+name,'work_ref':work_ref,
            'intent_ref':intent_ref,'source_sha256':byte_sha(original),'expected_output_sha256':byte_sha(output),
            'constraints':['owned local source correction only','no public caller grants','preserve all W02 guards and frozen bytes'],
            'satisfaction_obligations':list(EXPECTED_CHECKS),'owner_outcome':None}
        raw=encoded(value);filename=name+'.json';(directory/filename).write_bytes(raw)
        manifest[name]={'path':filename,'sha256':byte_sha(raw)}
    (directory/'input-manifest.json').write_bytes(encoded(manifest))
    return byte_sha(encoded(manifest))


if __name__=='__main__':
    index=1
    while (HERE/f'packages/{index:04d}').exists():index+=1
    print(prepare(HERE/f'packages/{index:04d}'))
