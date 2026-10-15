#!/usr/bin/env python3
"""Freeze the candidate research question, method, falsifier and context before runs."""
from pathlib import Path
import sys,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'workflows'))
from research import *


def prepare(directory,*,inquiry_link=True):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    timestamp=now();records={}
    goal=read(ENGINEERING_INPUTS/'goal.json')
    goal.update(goal_id='goal:lab-research:bounded-replay-comparison',version=VERSION,
        name='Understand exact replay correctness and overhead',
        outcome='Preserve trustworthy finite replay comparison evidence and its limitations.',
        rationale='W04 requires a complete bounded research/experiment trace, including negative or inconclusive outcomes.',
        success_conditions=['Method and falsifier declared before run','Every selected sample preserved','Inference bounded by actual observations'],
        evidence_requirements=['original signed archive and pins','exact Method and design','original process outputs and timings'],
        claim_ceiling='Candidate subgoal of current full-plan development instruction; no full-plan achievement or Product acceptance.')
    validate(goal,'goal');goal_ref=ref(goal);records[goal_ref]=('goal',goal)
    product=read(ROOT/'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/product.json')
    project=read(ROOT/'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/project.json')
    capability=read(ROOT/'authority/admissions/cyberalchemy-lab-operational-foundation/v1/instances/artifacts/product-capability.json')
    product_ref=ref(product);project_ref=ref(project);capability_ref=ident(capability)+'@foundation.1'
    records[product_ref]=('product-identity',product);records[project_ref]=('project-identity',project);records[capability_ref]=('product-capability',capability)
    method=read(ROOT/'implementation/lab-bootstrap/candidates/v1/packages/0004/method/example.json')
    method.update(method_id='method:lab-research:pinned-replay-comparison',version=VERSION,name='Pinned finite replay approach comparison',
        scope='One exact archived signed branch, three paired uncached replay observations and bounded inference.',
        inputs=['exact archived original bytes and independent pins','selected direct/facade implementation closure','declared thresholds and order'],
        outputs=['all original observation rows and process bytes','bounded hypothesis assessment and verification-residue entropy'],
        actions=['declare method/falsifiers','resolve typed context','compare signed replay paths','preserve every row','evaluate exact finite evidence'],
        gates=['current independent host development permission','exact method/source selection','45-second call bound'],
        evidence_requirements=['archive and implementation byte hashes','AB/BA/AB sample order','preserve negative/inconclusive evidence'],
        boundary=['owned disposable public archive only','no signing or admission','no cache optimization','no Product SLA'],
        validation_rule='Recompute exact sample labels and ratios from original bound child outputs; keep process completion separate from inference.',
        residue_rule='Missing, timed-out or rejected observations remain visible and cannot be treated as positive evidence.',
        recomposition_rule='Join only observations from the same archive, procedure and exact selected code; preserve scope and non-governing posture.')
    validate(method,'method');method_ref=ref(method);records[method_ref]=('method',method)
    measurement_method=template('measurement-method','verification-residue')
    measurement_method.update(name='Finite verification-residue entropy',property='residue entropy',
        entropy_register='finite-probabilistic',source_operation_ref='protocol:W04-replay-comparison',
        residue_type_ref='protocol:W04-parity-mismatch-rejected-timeout-labels',observable_kind='shannon-entropy',
        mathematical_reading='H(R) = -sum p(label)*ln p(label), where p is frequency among the three declared replay comparisons.',
        scope_kind='probabilistic',procedure='Classify every paired replay observation as parity, mismatch, rejected or timeout; count labels and calculate empirical finite H(R).',
        conditions=['Same exact archive and selected implementation bytes','All three predeclared samples retained'],unit='nats',
        uncertainty_rule='Exact finite label calculation; no population uncertainty estimate or timing-entropy inference.',
        claim_status='review',authority_treatment='non-governing',
        interpretation='Dispersion within this finite observed verification-residue model only. Zero does not establish safety, acceptance or speed.')
    validate(measurement_method,'measurement-method');measurement_method_ref=ref(measurement_method);records[measurement_method_ref]=('measurement-method',measurement_method)
    inquiry=template('research-inquiry','replay-comparison')
    inquiry.update(project_ref=SCOPE,goal_refs=[goal_ref],question='Does the existing read-only replay facade preserve exact signed reconstruction while improving finite observed wall time by at least 20 percent versus the direct full verifier?',
        method_ref=method_ref,inclusions=['actual C12 archived signed branch','direct/facade uncached replay','all finite positive/negative/inconclusive observations'],
        exclusions=['live stores or private keys','persistent checkpoint/cache implementation','Product SLA or human acceptance'],
        stop_conditions=['three paired samples','45-second bound per subprocess','stop on changed authority, method or sources'],
        source_refs=['protocol:C12-original-signed-archive'],evidence_aggregate_refs=[],counterevidence_refs=[],finding_refs=[],
        created_at=timestamp,last_updated_at=timestamp,limitations=['Three paired samples on one archived branch','No population generalization'])
    validate(inquiry,'research-inquiry');inquiry_ref=ref(inquiry);records[inquiry_ref]=('research-inquiry',inquiry)
    hypothesis=template('hypothesis','facade-overhead');hypothesis['name']='Finite facade replay overhead hypothesis'
    hypothesis['payload']={'proposition':'The selected finite comparison exhibits a consistent facade/direct wall-time improvement of at least 20 percent while exact projection/HEAD agree; mixed timing evidence remains inconclusive.',
        'falsification_conditions':['Any observed projection/HEAD mismatch','All three parity-valid ratios exceed 0.8'],
        'observation_targets':['protocol:W04-all-original-sample-rows'],'disposition':'open'}
    hypothesis['evidence_refs']=[];hypothesis['relation_refs']=[{'relation_kind_ref':'relation.evidence-bears-on','direction':'target','counterpart_kind':'evidence-set','counterpart_ref':'evidence-set:lab-research:replay-comparison'}]
    validate(hypothesis,'hypothesis');hypothesis_ref=ref(hypothesis);records[hypothesis_ref]=('hypothesis',hypothesis)
    design=template('experiment-design','replay-comparison')
    design.update(project_ref=SCOPE,goal_refs=[goal_ref],research_refs=[inquiry_ref] if inquiry_link else [],
        product_evaluation_context={'product_ref':product_ref,'product_thesis_ref':product['current_thesis_ref'],
            'thesis_hypothesis_refs':[],'thesis_outcome_refs':[],'product_capability_refs':[capability_ref],
            'realization_binding_refs':[],'evaluation_purpose':'Bounded exact reconstruction and overhead evidence; no inference of Product usefulness or capability acceptance.'},
        question_or_hypothesis=hypothesis['payload']['proposition'],subject_ref=capability_ref,
        protocol_ref='protocol:W04-pinned-replay-comparison',conditions=['Same archived original bytes and pins','AB/BA/AB order','No cache/reuse algorithm'],
        variables_or_interventions=[{'kind':'intervention','name':'selected replay entrypoint','planned_value':'direct full_replay versus VerifiedLegacyReadStore.replay'}],
        measure_refs=[measurement_method_ref],environment='Local Python subprocesses, independent full signed replay of owned restored public archive.',
        prerequisites=['exact selected Method and falsifier','existing Product capability ordered pair','current host permission'],
        stop_rules=['three paired samples','45 seconds per call','abort on source/method/authority change'],run_refs=[],evidence_refs=[],finding_refs=[],
        limitations=['Both entrypoints use the same uncached verifier','Three shared-host samples only'],design_state='ready',created_at=timestamp,last_updated_at=timestamp)
    validate(design,'experiment-design');design_ref=ref(design);records[design_ref]=('experiment-design',design)
    intent=read(ENGINEERING_INPUTS/'intent.json');intent.update(node_id='intent:lab-research:replay-comparison',direction=goal['outcome'],motivation=goal['rationale'],
        target_pressure='Replay completion and Product context need a trustworthy bounded research trace.',
        current_output_hypothesis={'artifact_type_ref':'cal.artifact-type.finding/v1','description':'A bounded finite replay comparison Finding'},satisfaction_refs=[])
    validate(intent,'intent');intent_ref=ref(intent);records[intent_ref]=('intent',intent)
    work=read(ENGINEERING_INPUTS/'work.json');work['node_id']='work:lab-research:replay-comparison';work['name']='Candidate replay comparison Work'
    work['payload'].update(goal_refs=[goal_ref],work_statement=goal['outcome'],input_refs=[intent_ref,inquiry_ref,method_ref,design_ref,hypothesis_ref],
        output_refs=['finding:lab-research:replay-comparison@candidate.1','evaluation:lab-research:replay-comparison@candidate.1'],completion_state='candidate-prepared')
    validate(work,'work');work_ref=ref(work);records[work_ref]=('work',work)
    resolution=read(ENGINEERING_INPUTS/'intent-resolution.json');resolution['node_id']='intent-resolution:lab-research:replay-comparison'
    resolution['payload'].update(intent_ref=ident(intent),selected_subject_refs=[ident(work),ident(inquiry),ident(design)],
        satisfaction_test_refs=goal['success_conditions'],owner_decision_ref='protocol:deferred-owner-decision:R08')
    validate(resolution,'intent-resolution');resolution_ref=ref(resolution);records[resolution_ref]=('intent-resolution',resolution)
    coordination=read(ENGINEERING_INPUTS/'coordination-context.json');coordination.update(coordination_context_id='coordination:lab-research:replay-comparison',
        goal_ref=goal_ref,product_ref=product_ref,purpose=goal['outcome'])
    validate(coordination,'coordination-context');coordination_ref=ref(coordination);records[coordination_ref]=('coordination-context',coordination)
    procedure={'schema_version':'lab-W04-pinned-procedure/v1-candidate','authority_effect':'none','method_ref':method_ref,'design_ref':design_ref,
        'archive_sha256':byte_sha(ARCHIVE.read_bytes()),'source_bindings':[],
        'samples':3,'order':[['direct','facade'],['facade','direct'],['direct','facade']],
        'timeout_seconds':45,'ratio_threshold':0.8,'residue_labels':list(TRIAL_LABELS),
        'actual_owner_outcome':None,'claim_ceiling':'Finite candidate evidence only; raw timings are distinct from residue entropy.'}
    for p in [BRIDGE/'lab_runtime/replay.py',BRIDGE/'lab_runtime/store.py',EXAMPLE/'replay_child.py',PACKAGE/'workflows/research.py']:
        procedure['source_bindings'].append({'path':p.relative_to(ROOT).as_posix(),'sha256':byte_sha(p.read_bytes())})
    raw=encoded(procedure);(directory/'procedure.json').write_bytes(raw)
    selection={'schema_version':'lab-W04-exact-research-selection/v1-candidate','authority_effect':'none','actual_owner_outcome':None,'scope_ref':SCOPE,
        'records':[],'procedure':{'path':'procedure.json','sha256':byte_sha(raw)},'method_ref':method_ref,'measurement_method_ref':measurement_method_ref,
        'inquiry_ref':inquiry_ref,'hypothesis_ref':hypothesis_ref,'design_ref':design_ref,'work_ref':work_ref,'intent_ref':intent_ref,
        'resolution_ref':resolution_ref,'coordination_ref':coordination_ref,'goal_ref':goal_ref,'project_ref':project_ref,'product_ref':product_ref,'capability_ref':capability_ref}
    for version_ref,(semantic_kind,value) in records.items():
        name=semantic_kind+'.json';raw=encoded(value);(directory/name).write_bytes(raw)
        selection['records'].append({'kind':semantic_kind,'path':name,'identity_ref':ident(value),'version_ref':version_ref,'sha256':byte_sha(raw)})
    raw=encoded(selection);(directory/'selection.json').write_bytes(raw)
    return byte_sha(raw)


if __name__=='__main__':
    index=1
    while (EXAMPLE/f'packages/{index:04d}').exists():index+=1
    print(prepare(EXAMPLE/f'packages/{index:04d}'))
