"""Freeze exact observed W09 candidate criteria without closing the full plan."""
from control import *
import re

def proof():
    dest=HERE/'receipts/0001';dest.mkdir(parents=True,exist_ok=False)
    audit=load(HERE/'runs/0007/audit/result.json');require(audit['result']=='PASS' and audit['remaining_runtime_gaps']==0 and audit['all_Sessions_closed'] and not audit['candidate_postimage_collisions'],'actual audit incomplete')
    checks=[]
    for domain,n in [('engineering',33),('research',41),('failure',52),('learning',53),('replay',14)]:
        p=HERE/'runs/0005/units'/domain/'result.json';v=load(p)
        require(v['result']=='PASS' and v['tests']==n and len(v['checks'])==n and all(r['result']=='PASS' for r in v['checks']),'actual preserved suite incomplete')
        checks += [{**r,'suite':domain,'evidence_binding':bind(p)} for r in v['checks']]
    p=HERE/'runs/0003/scenarios/engineering-default-regression.json';v=load(p)
    require(v['result']=='PASS' and v['tests']==42 and len(v['checks'])==42 and all(r['result']=='PASS' for r in v['checks']),'actual default regression incomplete')
    checks += [{**r,'suite':'preserved-default-authority','evidence_binding':bind(p)} for r in v['checks']]
    for attempt,count,suite in [('0001',23,'W09-current-host-guards'),('0008',12,'W09-genesis-reader-guards')]:
        p=HERE/'attempts'/attempt/'guards.stderr.log';text=p.read_text();rows=re.findall(r'^(test_\S+) \(([^\n]+)\) \.\.\. ok$',text,re.M)
        require(len(rows)==count and 'Ran '+str(count)+' tests' in text and text.rstrip().endswith('OK'),'actual W09 guard results incomplete')
        checks += [{'test':identity+'.'+name,'suite':suite,'result':'PASS','evidence_binding':bind(p)} for name,identity in rows]
    require(len(checks)==270 and len({(r['suite'],r['test']) for r in checks})==270,'declared check identity/count differs')
    schemas=[{'task':'W09','criterion':'both representative workflow paths','result':'PASS','evidence':audit['case_bindings'][:2]},
        {'task':'W09','criterion':'eligible failure evidence, real later Lesson application and assessment','result':'PASS','evidence':[audit['case_bindings'][2]]},
        {'task':'W09','criterion':'uncertainty and negative results retained','result':'PASS','evidence':[bind(HERE/'runs/0001/scenarios/research/assessment.json'),bind(HERE/'runs/0004/scenarios/learning/episode-index.json')]},
        {'task':'W09','criterion':'exact typed axes and closed ephemeral Sessions; candidate L1 nonregression','result':'PASS','evidence':[bind(HERE/'runs/0007/audit/result.json')]}]
    review={'schema_version':'lab-W09-candidate-review-selection/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
        'selected_case_bindings':audit['case_bindings'],'scope':'Three source-bound candidate cases only; no human/operational pilot claim.',
        'selected_runtime_source_bindings':[bind(HERE/p) for p in ['control.py','control_v2.py','worker_v2.py','worker_v3.py','signed.py','audit_v2.py']],
        'constructor_selections':[bind(SELECTION_PATH),bind(HERE/'packages/0002-learning-successor/selection.json')],
        'historical_only':[selection()['historical_Lesson_binding'],bind(HERE/'runs/0001/scenarios/learning/branch.snapshot')],
        'excluded_targets':['Failed/historical candidate postimages','Expired historical Lesson current application permission','Disposable store-scoped Lesson as a canonical or permanent operational target'],
        'new_scoped_Lesson_use':'Proof-scoped controlled current-time use in its owned branch only; future use requires fresh applicable context, review and independent host permission.',
        'final_assembly_obligations':['S02 bind actual entrypoints/environments, separate schema/semantic/executable targets and remaining evidence.',
            'R08 actual answering-owner recognition and exact final outcome remain absent.', 'A01/A02/A03/A04 retain original admitted provisioning, operation and release obligations.']}
    emit(dest/'review-selection.json',review)
    files={}
    for manifest in HERE.glob('attempts/*/*source-manifest.json'):
        for b in load(manifest)['files']:
            original(b);require(b['path'] not in files or files[b['path']]==b,'source manifests conflict');files[b['path']]=b
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and '.pyc'!=p.suffix and p.name not in ['0001.json']:
            b=bind(p);require(b['path'] not in files or files[b['path']]==b,'observed file changed from frozen source');files[b['path']]=b
    for b in files.values():original(b)
    require(not any(p.endswith('.pem') or p.endswith('.sqlite') for p in files),'private key/cache in proof closure')
    receipt={'schema_version':'lab-W09-real-candidate-integration-evidence/v1-candidate','task':'W09','result':'PASS','task_complete':True,
        'authority_effect':'none','actual_owner_outcome':None,'canonical_effects_applied':0,'runtime_activation':False,'human_pilot':False,
        'tests':270,'checks':checks,'validation_checks':audit['checks'],'criteria':schemas,'files':list(sorted(files.values(),key=lambda b:b['path'])),
        'source_bindings':[bind(RUN/'context-W09.json')],'audit_binding':bind(HERE/'runs/0007/audit/result.json'),
        'review_selection_binding':bind(dest/'review-selection.json'),'fresh_domain_cases':3,'actual_signed_coupling_witnesses':2,
        'later_Lesson_application':True,'Research_hypothesis_disposition':load(HERE/'runs/0001/scenarios/research/assessment.json')['disposition'],
        'typed_connections_checked':audit['typed_connections_checked'],'remaining_runtime_gaps':0,'candidate_postimage_collisions':0,
        'cold_contexts':3,'completed_case_Sessions_closed':True,'private_keys_exported':False,'Session_memory_exported':False,
        'failed_attempts_preserved':True,'remaining_obligations':[],
        'admitted_operation_route':'R08/A01/A02/A03','full_plan_complete':False,
        'claim_ceiling':'Complete original W09 candidate-development criteria only: actual bounded Engineering and Research observations, independently scoped signed current Lesson and real subsequent repair/assessment, preserved negative/counterevidence, exact cold replay and candidate L1 guards. No canonical admission, production or human pilot, broader ontology domain mapping, generic API completeness, confirmed causal effectiveness or general Product benefit.'}
    emit(HERE/'receipts/0001.json',receipt);print(encoded({'result':'PASS','receipt_binding':bind(HERE/'receipts/0001.json'),'tests':270,'files':len(files),'typed_connections':audit['typed_connections_checked'],'full_plan_complete':False}).decode(),end='')
if __name__=='__main__':proof()
