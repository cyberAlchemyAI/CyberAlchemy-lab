"""Actual candidate-design audit; distinguish it from owner/source acceptance."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LAB=HERE.parents[6]
PLAN=LAB/'docs/plans/definition-formal-assurance/candidate/foundations-first-v1'
sys.path.insert(0,str(ROOT/'units/M08'))
from finite_models import satisfies


def load(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):
    if path.exists():raise ValueError('Do not overwrite review evidence: '+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def produce_review():
    assertions=0
    def require(value,message):
        nonlocal assertions
        assertions+=1
        if not value:raise ValueError(message)
    names=['definition-kinds.json','statement-roles.json','signatures.json','logical-language.json','denotation.json','composition.json','obligation-types.json']
    docs={name:load(ROOT/'foundations'/name) for name in names}
    kinds=docs[names[0]]
    forms={r[0]:r for r in kinds['axes']['definitional_form']}
    require({'primitive-declaration','explicit-abbreviation','axiomatic-implicit','inductive','recursive','operational','unresolved'}<=set(forms),'Forms missing')
    require(len(forms)==len(kinds['axes']['definitional_form']),'Duplicate kind')
    require(kinds['assignment_policy']['automatic_axiom_adoption'] is False,'Axiom auto-adoption')
    require(kinds['assignment_policy']['automatic_identity_merging'] is False,'Label identity merging')
    for annotation in kinds['source_clause_annotations']:
        source=next(s for s in kinds['source_bindings'] if s['definition_id']==annotation['definition_id'])
        path=LAB/source['path']
        require(sha(path)==source['sha256'],'Current source changed')
        src=load(path)
        text=src['voices']['scientific_formal']['normative_statement']
        excerpt=annotation['excerpt'];offset=annotation['start_character']
        require(text[offset:offset+len(excerpt)]==excerpt,'Altered clause excerpt')
        require(hashlib.sha256(excerpt.encode()).hexdigest()==annotation['excerpt_sha256'],'Excerpt binding wrong')
        require(set(annotation['definitional_forms'])<=set(forms),'Unbound form assignment')
        require(set(annotation['statement_roles'])<=set(kinds['axes']['statement_role']),'Unbound role assignment')
        require(annotation['statement_roles']==['definition'],'Artifact concept made an axiom instance')
        require(annotation['fidelity_review']=='not-owner-reviewed','Fabricated source acceptance')
    require(len(kinds['source_bindings'])==8,'Not all eight foundation sources read')
    require(any(len(c['forms'])>1 and 'unresolved' in c['forms'] for c in kinds['synthetic_controls']),'Mixed/unknown case lost')
    roles=docs[names[1]]
    require('not by default' in roles['roles']['hypothesis']['theory_entry'],'Hypothesis auto-adopted')
    require('query only' in roles['roles']['proof-obligation']['theory_entry'],'Target is an axiom')
    require(roles['source_findings'][0]['status']=='unresolved','Correspondence conflict hidden')
    require('result_sort' in docs[names[2]]['declaration_kinds']['total-function']['fields'],'Function signature incomplete')
    language=docs[names[3]]
    require(set(language['core']['formula_forms'])=={'predicate-application','equality','not','and','or','implies','iff','forall','exists'},'Static core mismatch')
    require({'finite-static','inductive-fixed-point','temporal','normative-deontic','empirical-probabilistic'}<=set(language['profiles']),'Extensions concealed')
    require(docs[names[4]]['world_policy']['default'].startswith('open'),'Undeclared closed-world assumption')
    require(len(docs[names[4]]['information_states'])==5,'Information/logic outcomes collapsed')
    require(set(docs[names[5]]['relationships'])=={'alias','subtype','overlap-distinct','disjoint','independent-axis','unresolved'},'Relation classes missing')
    require('Do not assume' in docs[names[5]]['invariant_contexts']['implementation_preservation'],'Invariant circular proof')
    required={r['id'] for r in docs[names[6]]['obligation_types']}
    require({'source-fidelity','consistency','joint-inhabitation','permitted-distinction','universal-property','transition-preservation','conservativity','currentness-applicability'}<=required,'Required obligation types omitted')
    current_cases=ROOT/'units/M08/attempt-002/worked-examples.json'
    examples=load(current_cases)
    require(sha(LAB/examples['module_binding']['path'])==examples['module_binding']['sha256'],'Selected evidence runtime stale')
    replays=0
    for case in examples['cases']:
        result=case.get('actual_result',{})
        if 'model' not in result:continue
        signature=case['signature']
        signature={**signature,'constants':{},'functions':{},'fixed_predicates':{n:{tuple(t) for t in e} for n,e in signature['fixed_predicates'].items()}}
        model={n:{tuple(t) for t in e} for n,e in result['model'].items()}
        require(all(satisfies(f,signature,model) for f in case['formulas']),'Selected witness replay failed')
        replays+=1
    historical=load(ROOT/'units/M08/attempt-001/worked-examples.json')
    require(sha(ROOT/'units/M08/attempt-001/finite_models.py')==historical['module_binding']['sha256'],'Historical runtime not preserved')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'units/M08'),'-p','test_controls.py','-v'],capture_output=True,text=True)
    require(tests.returncode==0,'Worked controls failed: '+tests.stderr)
    require('Ran 16 tests' in tests.stderr,'Unexpected test denominator')
    test_log=HERE/'test-output.txt'
    if test_log.exists():raise ValueError('Preserve prior test log')
    test_log.write_text(tests.stdout+tests.stderr)
    baseline=load(PLAN.parent/'detailed-plan-v1/source-baseline.json')
    for row in baseline['definitions']:
        require(sha(LAB/row['source_path'])==row['source_sha256'],'Canonical selected source modified')
    taskplan=load(PLAN/'dag.json')
    tasks={t['id']:t for t in taskplan['tasks']}
    evaluations={
      'M01':('Classification axes, source clause annotations, distinct forms and mixed/unresolved controls verified.',['foundations/definition-kinds.json']),
      'M02':('Logical roles reviewed; investigation/target assumptions prohibited; source precedence ambiguity retained.',['foundations/statement-roles.json','units/M08/test_controls.py']),
      'M03':('Signature and typing contract reviewed; total functions/equality, unaligned carriers and free variables exercised.',['foundations/signatures.json','units/M08/test_controls.py']),
      'M04':('Static first-order grammar reviewed; exact finite scope and unimplemented extension entry contracts explicit.',['foundations/logical-language.json','units/M08/finite_models.py']),
      'M05':('Independent denotation contract reviewed; Boolean truth table and 64 quantified relational assignments compared against direct expectations.',['foundations/denotation.json','units/M08/test_controls.py']),
      'M06':('Composition and relationship contracts reviewed; alias, proper subtype, joint contradiction, invariant preservation and recursive leastness controls executed.',['foundations/composition.json','units/M08/attempt-002/worked-examples.json']),
      'M07':('Complete obligation categories and strength policy reviewed; consistency/population guards and bounded/universal distinction controls executed.',['foundations/obligation-types.json','units/M08/test_controls.py']),
      'M08':('Eight current source case annotations and 15 finite case records produced; 10 direct model witnesses replayed; 16 tests passed.',['units/M08/attempt-002/worked-examples.json','units/M08/finite_models.py','units/M08/test_controls.py']),
    }
    for ident,(evaluation,evidence) in evaluations.items():
        criteria={'schema_version':'definition-assurance-candidate-criterion-review/v1','unit_id':ident+'.1','authority_effect':'none',
                  'review_actor':'Codex /root','review_kind':'agent candidate-design self-review; not independent or source-owner review',
                  'task_acceptance':tasks[ident]['acceptance'],'disposition':'PASS for the stated candidate-design/worked-control scope',
                  'actual_evaluation':evaluation,'evidence':[{'path':str((ROOT/p).relative_to(LAB)),'sha256':sha(ROOT/p)} for p in evidence],
                  'source_fidelity':'not-owner-reviewed; whole-definition assurance not established','excluded_claims':['all-definition consistency','generic soundness theorem','canonical admission','independent owner acceptance']}
        write(ROOT/f'units/{ident}/criterion-review.json',criteria)
        if ident!='M01':
            write(ROOT/f'units/{ident}/context.json',{'task_id':ident+'.1','authority_effect':'none','mode':'standard','scope':'Selected task production and candidate review only',
                  'criterion':tasks[ident]['acceptance'],'prerequisites':tasks[ident]['depends_on'],'controlling_sources':criteria['evidence'],
                  'source_precedence':'Ambiguous source correspondence is explicitly unresolved; no source-owner acceptance is fabricated.',
                  'runtime':'local; no delegation','decision':'Use declared static model and exact bounded examples; keep unsupported meanings and fidelity out of readiness claims.'})
    write(ROOT/'units/M08/receipt.json',{'unit_id':'M08.1','authority_effect':'none','selected_attempt':'attempt-002','cases':15,'source_case_annotations':8,
          'witness_replays':replays,'tests':16,'test_result':'PASS','current_evidence_ref':str(current_cases.relative_to(LAB)),
          'historical_attempt':'attempt-001 exact runtime and evidence retained','source_fidelity':'whole sources not owner-reviewed'})
    selected=[ROOT/'foundations'/name for name in names]+[current_cases,ROOT/'units/M08/finite_models.py',ROOT/'units/M08/test_controls.py',test_log,HERE/'REVIEW.md']
    review={'schema_version':'definition-assurance-foundation-model-review/v1-candidate','unit_id':'M09.1','authority_effect':'none',
            'review_actor':'Codex /root','review_kind':'agent design self-review; same author, no independent or source-owner acceptance',
            'disposition':'Accept the static candidate model for controlled prototype/decoder work; do not grant full-definition assurance.',
            'validated_assertions':assertions,'contracts':7,'source_examples':8,'worked_case_records':15,'model_witnesses_replayed':replays,
            'tests':16,'test_result':'PASS','exact_reviewed_inputs':[{'path':str(p.relative_to(LAB)),'sha256':sha(p)} for p in selected],
            'core_decision':'Classical many-sorted first-order static core; exact finite worked profile; role-separated assumptions and queries.',
            'required_unresolved':[
              {'id':'FID-HYP-001','issue':'Hypothesis investigation meaning versus inherited adopted-Premise expression','blocks':'Whole-source Hypothesis fidelity/readiness; not representation of an unresolved record.'},
              {'id':'EXT-001','issue':'Required recursive/temporal/deontic/empirical clauses need actual selected extension support','blocks':'Evidence for those clauses until supported semantics and minimum strength exist.'},
              {'id':'FID-ALL','issue':'Actual full-source interpretation fidelity not reviewed by semantic owners','blocks':'Whole-definition readiness and any all-definition assurance/admission claim.'},
              {'id':'PROOF-001','issue':'No generic mechanized evaluator or requirement-generation theorem','blocks':'Any claim of that strength; controlled finite evidence retains handwritten-checker trust.'}],
            'next_work':'A01 strict input contract/decoder candidate; retain full project scope while final episode scope answer is pending.'}
    write(ROOT/'foundations/foundation-review.json',review)
    write(HERE/'receipt.json',{'unit_id':'M09.1','authority_effect':'none','review_ref':str((ROOT/'foundations/foundation-review.json').relative_to(LAB)),
          'review_sha256':sha(ROOT/'foundations/foundation-review.json'),'disposition':'candidate agent review completed; no owner acceptance asserted'})
    write(HERE/'episode-status.json',{'authority_effect':'none','goal_objective':'complete the formalization episode and the end produce a complete review and explaining each formalization aspect',
          'previous_goal_turn_classification':'progress: concrete contracts, worked evidence and actual review produced',
          'foundation_candidate_episode':'design artifacts and agent review delivered; source-owner fidelity remains separate',
          'overall_goal':'active; completion not established for the full 183-definition scope',
          'scope_question':'User clarification requested; no answer yet. Full project goal retained rather than silently narrowed.',
          'next_unit':'A01.1 candidate decoder',
          'completion_audit':[
            {'requirement':'Definition forms, logical roles and semantics prioritized','evidence':'M01-M07 concrete contracts and criterion reviews','status':'achieved at candidate-design scope'},
            {'requirement':'Worked formalization checks with actual evidence','evidence':'15 cases, 10 direct model witnesses, 16 tests','status':'achieved at declared finite scope'},
            {'requirement':'Review explaining each formalization aspect','evidence':'units/M09/REVIEW.md and exact model review','status':'foundation review delivered; full-project end review remains pending'},
            {'requirement':'All 183 meanings faithfully translated and reviewed if full project scope applies','evidence':'183 selected source digests verified; annotations are not full translations','status':'not achieved'},
            {'requirement':'Complete combined current theory and required populations if full project scope applies','evidence':'No full-current theory check performed','status':'not achieved'},
            {'requirement':'Reusable addition/revision workflow if full project scope applies','evidence':'Production decoder/provider/invalidation still pending','status':'not achieved'}]})
    return {'candidate_review':'delivered','assertions':assertions,'tests':16,'cases':15,'witness_replays':replays,'overall_goal':'active; full-scope completion unproven'}


def check_review():
    review=load(ROOT/'foundations/foundation-review.json')
    for row in review['exact_reviewed_inputs']:
        if sha(LAB/row['path'])!=row['sha256']:raise ValueError('Stale review binding: '+row['path'])
    for ident in [f'M{i:02}' for i in range(1,9)]:
        row=load(ROOT/f'units/{ident}/criterion-review.json')
        for artifact in row['evidence']:
            if sha(LAB/artifact['path'])!=artifact['sha256']:raise ValueError('Stale criterion binding')
    receipt=load(HERE/'receipt.json')
    if sha(LAB/receipt['review_ref'])!=receipt['review_sha256']:raise ValueError('Changed model review')
    return {'result':'PASS','meaning':'Exact current candidate review bindings only; no all-definition assurance or owner acceptance.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    print(json.dumps(check_review() if args.check else produce_review(),indent=2))
