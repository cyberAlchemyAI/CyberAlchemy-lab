"""First individually grounded postimage; never infer missing model relations."""
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[6]
HERE=Path(__file__).resolve().parent
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T10'
SELECTION=ROOT/'product/lab/release-candidates/v1/release-validation/0001/final-materializer-selection-0276.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():raise RuntimeError('preserve previous construction bytes')
    p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def main():
    context=json.loads((RUN/'context.json').read_text())
    for row in context['selected_sources']:
        if sha(ROOT/row['path'])!=row['sha256']:raise RuntimeError('selected original changed')
    selection=json.loads(SELECTION.read_text());models=[m for m in selection['members']if m['axes'].get('carrier_ref')=='cal.artifact-type.governed-model/v1']
    assert len(models)==29
    records=[]
    for index,m in enumerate(models):
        member=m['member_ref'];axes=m['axes'];body=json.loads((ROOT/axes['body_binding']['path']).read_text())
        preparation=json.loads((ROOT/m['original_preparation_binding']['path']).read_text())
        original=[x for x in preparation.get('members',[])if x.get('member_ref',x.get('member_id'))==member]
        # Preserve exact original controls/body independently of any alternative.
        raw=(ROOT/axes['body_binding']['path']).read_bytes();destination=HERE/'original-models'/f'{index:02d}.json'
        destination.parent.mkdir(exist_ok=True);destination.write_bytes(raw)
        refs=[]
        for row in axes['original_control_bindings']:
            p=ROOT/row['path'];target=HERE/'original-control-bytes'/row['sha256']
            target.parent.mkdir(exist_ok=True)
            if not target.exists():target.write_bytes(p.read_bytes())
            assert sha(target)==row['sha256'];refs.append({'original_binding':row,'retained_binding':binding(target)})
        disposition={'original_index':index,'member_ref':member,'original_axes':axes,
            'original_body_binding':axes['body_binding'],'retained_original_body_binding':binding(destination),
            'retained_original_controls':refs,'original_preparation_binding':m['original_preparation_binding'],
            'original_member_semantics':original[0] if len(original)==1 else None,
            'supported_model_relation':None,'selected_candidate_binding':None,
            'status':'EXACT-MEMBER-REQUIRES-INDIVIDUAL-DESIGN-DISPOSITION',
            'admission_or_runtime_use_allowed':False,'owner_authority_resolved':False,'actual_owner_outcome':None,
            'authority_effect':'none','remaining':'Trace this exact member to a legitimate actual counterpart, or prepare a meaning-preserving alternate carrier for accountable approval. No generic relation, predecessor, Decision or Implementation.'}
        if member=='protocol:C10:source-profile':
            implementation=next(x for x in selection['members']if x['member_ref']=='protocol:C10:successor-runtime')
            ib=implementation['axes']['body_binding'];counterpart=json.loads((ROOT/ib['path']).read_text())
            assert counterpart['node_id']=='implementation:cyberalchemy-lab:repeatable-operation'
            candidate=copy.deepcopy(body)
            candidate['relation_refs']=[{'relation_kind_ref':'relation.instance-of','direction':'target',
                'counterpart_kind':'implementation','counterpart_ref':counterpart['node_id']}]
            candidate['payload']['version_ref']=candidate['node_id']+'@completion.0011.T10-candidate.1'
            candidate['claim_ceiling'] += ' Candidate relationship is grounded in original profiles.select exact control consumption; no governing owner, admission, native currentness or execution permission inferred.'
            out=HERE/'candidate-models'/'source-profile.json';save(out,candidate)
            code_root=ROOT/'implementation/lab-runtime/candidates/repeatable-operation'
            code=[binding(p)for p in sorted((code_root/'lab_runtime').rglob('*.py'))]
            code +=[binding(code_root/'lab.py')]
            tests=[binding(p)for p in sorted((code_root/'tests').glob('*.py'))]
            c09=ROOT/'implementation/lab-integration/candidates/v1/receipts/C09/0001/receipt.json'
            disposition.update(status='GROUNDED-GOVERNED-MODEL-CANDIDATE-PENDING-INDEPENDENT-REVIEW',
                selected_candidate_binding=binding(out),supported_model_relation=candidate['relation_refs'][0],
                counterpart_original_member_ref=implementation['member_ref'],counterpart_binding=ib,
                code_bindings=code,test_source_bindings=tests,historical_actual_evidence_bindings=[binding(c09)],
                exact_consumer={'path':'implementation/lab-runtime/candidates/repeatable-operation/lab_runtime/profiles.py',
                    'function':'select','control_flow':'CLI selects exact d75 row; profiles.select independently checks profile/policy/executable/content/review controls and original source closure.',
                    'test_function':'Profiles.test_* in original test_profiles.py; historical results stay historical'},
                remaining='Independent semantic relation review, actual governing owner/scopes, native proposal/full source closure and R08 exact outcome before any use. Existing Implementation body stays unchanged.')
        save(HERE/'dispositions'/f'{index:02d}.json',disposition);records.append({'member_ref':member,'disposition_binding':binding(HERE/'dispositions'/f'{index:02d}.json'),'status':disposition['status']})
    save(HERE/'disposition-ledger-initial.json',{'schema_version':'lab-T10-member-dispositions/v1-candidate',
        'original_selection_binding':binding(SELECTION),'original_member_count':29,'members':records,
        'original_members_removed':0,'original_refusals_preserved':True,'grounded_candidate_models':1,
        'remaining_individual_representations':28,'task_complete':False,'authority_effect':'none'})
    print(json.dumps({'members_preserved':29,'grounded_model_candidates':1,'remaining':28}))

if __name__=='__main__':main()
