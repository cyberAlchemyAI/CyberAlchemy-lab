from pathlib import Path
import copy
import json
import sys
import uuid
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,binding,check,require,write
from v3.execution.extension_runtime import Client
policy=C.decode((BASE/'p01/request-fixture.json').read_bytes())['resource_policy']
seed=C.decode((BASE/'p09/rich-combined-request.json').read_bytes())
run_id=uuid.uuid4().hex;out=HERE/'evidence'/run_id;out.mkdir(parents=True);controls=[];cases=[]
client=Client('E01',policy)
def test(name,ok):require(ok,name);controls.append({'name':name,'result':'pass'});print(name,'PASS',flush=True)
def source(name,accepted_values,comma=False,duplicate=False,wrong_kind=False):
    s=copy.deepcopy(seed);graph=s['proposal']['before']['graph'];first=graph['assessments'][0]
    rows=[]
    for n,accepted in enumerate(accepted_values):
        a=copy.deepcopy(first);a['ref']='assessment:conformance'+('' if n==0 else '-'+str(n));a['accepted']=accepted
        if comma:a['ref']='assessment:conformance,other'
        rows.append(a)
    graph['assessments']=rows+[graph['assessments'][1]]
    if duplicate:
        a=copy.deepcopy(rows[0]);a['accepted']=not a['accepted'];graph['assessments'].append(a)
    if comma:graph['assertions'][0]['qualifiers']['conformance_evidence_refs']=rows[0]['ref']
    if wrong_kind:next(n for n in graph['nodes'] if n['ref']==first['target'])['kind']='principal'
    s['proposal']['after']['graph']=copy.deepcopy(graph);s['proposal']['baseline_identity']=C.identity(s['proposal']['before'])
    p=out/(name+'-source.json');write(p,s)
    b=s['proposal']['before'];selected=graph['assertions'][0];f={'profile':b['profile_identity'],'context':{k:b['context'][k] for k in ['id','version']},
        'subject':selected['source'],'target':selected['target'],'scope':selected['qualifiers']['conformance_scope'],'epoch':b['context']['epoch']}
    refs=[{'token':a['ref'],'source_identity':C.identity(graph)} for a in rows]
    return {'schema':'relational.evidence-collection-request/v1','profile':'evidence-collection-v1','source':binding(p),'source_assertion':selected['id'],
        'frame':f,'references':refs,'legacy_token':''}
def actual(name,r,expected,conforms=None,count=None):
    input_ref=write(out/(name+'-request.json'),r);a=client.qualify(json.dumps(r,ensure_ascii=False).encode());answer_ref=write(out/(name+'-result.json'),a)
    cases.append({'name':name,'input':input_ref,'answer':answer_ref});(HERE/'control-progress.json').write_text(json.dumps({'cases':cases,'controls':controls},indent=2)+'\n')
    print(name,a['status'],a.get('reason',''),flush=True);test(name+'-status',a['status']==expected)
    if conforms is not None:
        v=a['value']['value'];test(name+'-conformance',v['conforms']==conforms);test(name+'-all-supports',len(v['supports'])==count)
        test(name+'-roots-unchanged',v['roots_before']==v['roots_after'] and not v['application_authorized'])
        test(name+'-fresh-event',client.live_event(a))
        test(name+'-saved-new-client-no-event',not Client('E01',policy).live_event(a))
        forged=copy.deepcopy(a);forged['value']['value']['conforms']=not v['conforms'];test(name+'-changed-result-no-event',not client.live_event(forged))
        return v
    test(name+'-refusal-no-event',not client.live_event(a))

two=source('two-current-supports',[True,True]);v=actual('two-current-supports',two,'fresh-extension-candidate',True,2)
test('supports-in-source-order',[a['ref'] for a in v['supports']]==[r['token'] for r in two['references']])
actual('mixed-distinct-assessments',source('mixed',[False,True]),'fresh-extension-candidate',True,1)
actual('all-rejected',source('rejected',[False,False]),'fresh-extension-candidate',False,0)
legacy=source('opaque-comma',[True],comma=True);legacy['profile']='legacy-single-token-adapter-v1';legacy['legacy_token']=legacy['references'][0]['token'];legacy['references']=[]
v=actual('legacy-comma-is-one-token',legacy,'fresh-extension-candidate',True,1);test('legacy-comma-never-split',len(v['references'])==1 and v['references'][0]['token']=='assessment:conformance,other')
bad=copy.deepcopy(two);bad['references']=[];actual('empty-collection',bad,'invalid')
bad=copy.deepcopy(two);bad['references'].append(copy.deepcopy(bad['references'][0]));actual('duplicate-reference',bad,'invalid')
bad=copy.deepcopy(two);bad['references'][0]['source_identity']='0'*64;actual('stale-source-revision',bad,'invalid')
bad=copy.deepcopy(two);bad['references'][0]['token']='nonexistent';actual('missing-assessment-token',bad,'invalid')
bad=copy.deepcopy(two);bad['frame']['target']['version']='v2';actual('wrong-contract-revision',bad,'invalid')
bad=copy.deepcopy(two);bad['frame']['scope']='other-scope';actual('wrong-scope',bad,'invalid')
bad=copy.deepcopy(two);bad['frame']['context']['version']='v3';actual('wrong-context',bad,'invalid')
bad=copy.deepcopy(two);bad['frame']['epoch']=1;actual('wrong-epoch',bad,'invalid')
actual('contradictory-source-token',source('contradictory',[True],duplicate=True),'invalid')
actual('wrong-endpoint-kind',source('wrong-kind',[True],wrong_kind=True),'invalid')
bad=source('forged-registry',[True],wrong_kind=True);file=check(bad['source']);forged=C.decode(file.read_bytes())
for before_after in ['before','after']:
    kind=next(k for k in forged['proposal'][before_after]['registry']['kinds'] if k['id']=='relation.conforms-to')
    kind['pairs'].append({'source_kind':'capability-instance','target_kind':'principal'})
forged['proposal']['baseline_identity']=C.identity(forged['proposal']['before'])
new_source=write(out/'forged-registry-definition-source.json',forged);bad['source']=new_source
actual('forged-registry-definition',bad,'invalid')
bad=copy.deepcopy(legacy);bad['profile']='evidence-collection-v1';bad['legacy_token']='';bad['references']=[{'token':'assessment:conformance','source_identity':v['source_identity']}];actual('accidental-comma-splitting-refused',bad,'invalid')
write(HERE/'controls.json',{'result':'pass','run_id':run_id,'controls':controls,'cases':cases,'new_complete_collection_witnesses':4,
    'policy':'any-current-accepted-exact-match; retain all supports; reject malformed listed evidence','authority_effect':'none'})
print('E01 controls complete:',len(controls),flush=True)
