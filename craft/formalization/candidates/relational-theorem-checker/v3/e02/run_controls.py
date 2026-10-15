from pathlib import Path
import sys,json,copy,uuid
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;B=H.parent;sys.path.insert(0,str(B.parent))
from v3.p03.context import C,write,require
from v3.execution.extension_runtime import Client,schema_validate
from v3.e02 import chain_adapter as m
policy=C.decode((B/'p01/request-fixture.json').read_bytes())['resource_policy'];client=Client('E02',policy)
out=H/'evidence'/uuid.uuid4().hex;out.mkdir(parents=True);controls=[];cases=[]
def test(n,ok):require(ok,n);controls.append({'name':n,'result':'pass'});print(n,'PASS',flush=True)
def ref(id):return {'id':id,'version':'v1'}
a,b,c=map(ref,['Alice','Bob','Carol']);f={'profile':'bounded-redelegation-v1','context':ref('ctx'),'subject':a,'target':c,'scope':'review','epoch':5}
source={'profile':'bounded-redelegation-v1','revision':ref('source'),'frame':f,'principals':[{'ref':x,'roles':['principal','agent']} for x in [a,b,c]],'hops':[],'assessments':[]}
for n,(p,g) in enumerate([(a,b),(b,c)]):
 h={'ref':ref('hop'+str(n)),'principal':p,'agent':g,'scopes':['review'],'actions':['approve'],'start':0,'finish':10,'redelegate':True};source['hops'].append(h)
 for kind,v in [('gate','yes'),('revocation','no')]:source['assessments'].append({'ref':ref(kind+str(n)),'hop':h['ref'],'kind':kind,'frame':f,'value':v})
base={'schema':'relational.chain-request/v1','profile':'bounded-redelegation-v1','source':source,'source_identity':C.identity(source),'query':{'principal':a,'agent':c,'scope':'review','action':'approve','epoch':5,'max_depth':2}}
def stamp(r):r['source_identity']=C.identity(r['source']);return r
def local(n,r,verdict=None,error=None):
 try:schema_validate(m.SCHEMA,r);p=m.normalize(r,None)
 except Exception as e:test(n,error is not None and error in str(e));return
 test(n,error is None and p['verdict']==verdict)
def actual(n,r,v):
 ri=write(out/(n+'-request.json'),r);answer=client.qualify(json.dumps(r).encode());ra=write(out/(n+'-result.json'),answer);cases.append({'name':n,'input':ri,'answer':ra});print(n,answer['status'],answer.get('reason',''),flush=True)
 test(n+'-kernel',answer['status']=='fresh-extension-candidate');test(n+'-verdict',answer['value']['value']['verdict']==v);test(n+'-fresh',client.live_event(answer));test(n+'-saved',not Client('E02',policy).live_event(answer));test(n+'-no-authority',not answer['value']['value']['application_authorized'])
actual('two-hop-positive',base,'yes')
r=copy.deepcopy(base);r['source']['hops'][1]['scopes'].append('administration');actual('child-widens-no',stamp(r),'no')
r=copy.deepcopy(base);r['source']['assessments'][0]['value']='unknown';actual('unknown-ancestor',stamp(r),'unknown')
for name,change,expected in [
 ('expired-ancestor',lambda r:r['source']['hops'][0].update(finish=5),'no'),
 ('revoked-ancestor',lambda r:r['source']['assessments'][1].update(value='yes'),'no'),
 ('missing-gate',lambda r:r['source']['assessments'].pop(0),'unknown'),
 ('redelegation-denied',lambda r:r['source']['hops'][0].update(redelegate=False),'no'),
 ('broken-join',lambda r:r['source']['hops'][1].update(principal=c),'no'),
 ('cycle-no-starting-authority',lambda r:r['source']['hops'][1].update(agent=a),'no')]:
 r=copy.deepcopy(base);change(r);local(name,stamp(r),expected)
r=copy.deepcopy(base);r['source']['assessments'][0]['frame']=copy.deepcopy(f);r['source']['assessments'][0]['frame']['context']['version']='v2';local('wrong-assessment-context',stamp(r),error='frame mismatch')
r=copy.deepcopy(base);r['source']['assessments'].append(copy.deepcopy(r['source']['assessments'][0]));local('contradictory-duplicate',stamp(r),error='duplicate/conflicting')
r=copy.deepcopy(base);r['query']['epoch']=6;local('wrong-epoch',r,error='frame mismatch')
r=copy.deepcopy(base);r['source_identity']='0'*64;local('stale-source-identity',r,error='identity mismatch')
r=copy.deepcopy(base);r['source']['principals'][1]['roles']=['agent'];local('intermediate-needs-dual-role',stamp(r),error='roles missing')
r=copy.deepcopy(base);r['query']['max_depth']=1;local('depth-explicit-no-within-bound',r,'no')
r=copy.deepcopy(base);r['query']['max_depth']=4
for n in range(7):h=copy.deepcopy(r['source']['hops'][0]);h['ref']=ref('extra'+str(n));r['source']['hops'].append(h)
local('work-cutoff-no-partial-positive',stamp(r),error='exceeds 4096')
# The unchanged direct API stays independently selectable and source-bound.
from v3.execution import support as s
receipt=s.read(B/'p09/task-acceptance.json')
for bnd in receipt['artifacts']+receipt['inputs']:s.check(bnd)
test('accepted-direct-profile-sources-unchanged',True)
write(H/'controls.json',{'result':'pass','controls':controls,'cases':cases,'full_witnesses_required':3,'preflight_tests':'In-process closed-schema/normalizer controls; three separately supervised full actual witnesses.','authority_effect':'none'})
