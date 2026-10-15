from pathlib import Path
import sys,json,copy,uuid
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;B=H.parent;sys.path.insert(0,str(B.parent))
from v3.p03.context import C,write,require
from v3.execution.extension_runtime import Client,schema_validate
from v3.e03 import fulfillment_adapter as m
policy=C.decode((B/'p01/request-fixture.json').read_bytes())['resource_policy'];out=H/'evidence'/uuid.uuid4().hex;out.mkdir(parents=True);controls=[];cases=[]
def test(n,v):require(v,n);controls.append({'name':n,'result':'pass'});print(n,'PASS',flush=True)
def ref(n):return {'id':n,'version':'v1'}
f={'profile':'verified-fulfillment-v1','context':ref('ctx'),'subject':ref('request'),'target':ref('requirement'),'scope':'review','epoch':5}
s={'revision':ref('source'),'frame':f,'request':ref('request'),'requirement':ref('requirement'),'linked':True,'criteria':[ref('criterion1'),ref('criterion2')],'actions':[{'ref':ref('action'),'request':ref('request'),'requirement':ref('requirement'),'frame':f,'outputs':[ref('output')],'accepted':True}],'outputs':[{'ref':ref('output'),'action':ref('action'),'accepted':True}],'evaluations':[]}
for i in [1,2]:s['evaluations'].append({'ref':ref('evaluation'+str(i)),'criterion':ref('criterion'+str(i)),'request':s['request'],'requirement':s['requirement'],'action':ref('action'),'output':ref('output'),'frame':f,'value':'yes'})
base={'schema':'relational.fulfillment-request/v1','profile':'verified-fulfillment-v1','source':s,'source_identity':C.identity(s)}
def stamp(r):r['source_identity']=C.identity(r['source']);return r
def local(n,r,v=None,error=None):
 try:schema_validate(m.SCHEMA,r);p=m.normalize(r,None)
 except Exception as e:test(n,error is not None and error in str(e));return
 test(n,error is None and p['verdict']==v)
# Preflight controls precede expensive owned full proofs.
local('independent-all-two-criteria',base,'yes')
r=copy.deepcopy(base);r['source']['evaluations'].pop();local('missing-named-criterion-unknown',stamp(r),'unknown')
r=copy.deepcopy(base);r['source']['evaluations'][0]['value']='no';local('explicit-denial-no',stamp(r),'no')
r=copy.deepcopy(base);r['source']['actions'][0]['accepted']=False;local('unaccepted-action-not-completion',stamp(r),'unknown')
r=copy.deepcopy(base);r['source']['linked']=False;local('evaluations-without-link-not-completion',stamp(r),'no')
r=copy.deepcopy(base);r['source']['actions'][0]['requirement']['version']='v2';local('stale-requirement',stamp(r),error='stale action')
r=copy.deepcopy(base);r['source']['evaluations'][0]['request']=ref('other');local('wrong-request',stamp(r),error='stale evaluation')
r=copy.deepcopy(base);r['source']['evaluations'][0]['output']=ref('unrelated');local('unrelated-output',stamp(r),error='unrelated/missing')
r=copy.deepcopy(base);r['source']['evaluations'][0]['frame']=copy.deepcopy(f);r['source']['evaluations'][0]['frame']['epoch']=6;local('wrong-evaluation-epoch',stamp(r),error='stale evaluation')
r=copy.deepcopy(base);e=copy.deepcopy(r['source']['evaluations'][0]);e['ref']=ref('other-evaluation');e['value']='no';r['source']['evaluations'].append(e);local('conflicting-completion-identities',stamp(r),error='contradictory criterion')
r=copy.deepcopy(base);r['source']['criteria']=[];local('empty-criteria-cannot-vacuously-fulfill',stamp(r),error='minItems')
r=copy.deepcopy(base);r['source_identity']='0'*64;local('source-identity-drift',r,error='identity mismatch')
linked=copy.deepcopy(base);linked['source']['actions']=[];linked['source']['outputs']=[];linked['source']['evaluations']=[];stamp(linked);local('active-intent-without-action',linked,'unknown')
client=Client('E03',policy)
for name,r,v in [('complete-two-criteria',base,'yes'),('linked-without-action',linked,'unknown')]:
 ri=write(out/(name+'-request.json'),r);a=client.qualify(json.dumps(r).encode());ra=write(out/(name+'-result.json'),a);cases.append({'name':name,'input':ri,'answer':ra});print(name,a['status'],a.get('reason',''),flush=True)
 test(name+'-full-kernel',a['status']=='fresh-extension-candidate');test(name+'-exact-verdict',a['value']['value']['verdict']==v);test(name+'-no-authority',not a['value']['value']['application_authorized']);test(name+'-saved-no-event',not Client('E03',policy).live_event(a))
 if v=='yes':test('positive-live-event',client.live_event(a))
write(H/'controls.json',{'result':'pass','controls':controls,'cases':cases,'full_witnesses_required':2,'preflight_tests':'Independent expected verdicts and malformed-key controls before two actual owned complete witnesses.','authority_effect':'none'})
