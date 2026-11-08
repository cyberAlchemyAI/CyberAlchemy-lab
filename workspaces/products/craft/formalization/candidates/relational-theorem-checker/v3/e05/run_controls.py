from pathlib import Path
import sys,json,copy,uuid
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;B=H.parent;sys.path.insert(0,str(B.parent))
from v3.p03.context import C,write,require,binding,check
from v3.execution import support as s
from v3.execution.extension_runtime import Client,schema_validate
from v3.e05 import adapter as m
policy=C.decode((B/'p01/request-fixture.json').read_bytes())['resource_policy'];out=H/'evidence'/uuid.uuid4().hex;out.mkdir(parents=True);controls=[];cases=[]
def test(n,v):require(v,n);controls.append({'name':n,'result':'pass'});print(n,'PASS',flush=True)
for task in ['P09','E00','E01','E02','E03','E04']:test(task+'-receipt-current',s.task(task)['status']=='accepted')
sources=[{'task':'P09','binding':binding(B/'p09/rich-combined-request.json'),'selector':'before-graph'}]
for task in ['E00','E01','E02','E03','E04']:
 report=C.decode((B/task.lower()/'controls.json').read_bytes());chosen=None
 for case in report['cases']:
  a=C.decode(check(case['answer']).read_bytes())
  if a.get('status')=='fresh-extension-candidate':
   chosen=case['answer']
   if task!='E00' or a['value']['value']['active_origins']:break
 require(chosen is not None,'accepted actual source missing');sources.append({'task':task,'binding':chosen,'selector':'extension-result'})
value={'a':0,'bool':False,'escapes':'quote" slash\\ newline\n tab\t nul\x00 end','unicode':'é e\u0301 Ω 🙂','references':{'id':'request','version':'v2'},'scope':'review','hash':'f'*64,'array':[True,1,None], 'é':1,'Ω':2,'🙂':3}
base={'schema':'relational.canonical-ir-request/v1','profile':'canonical-typed-ir-v1','sources':sources,'values':[{'label':'unicode-typed-key-challenge','identity':C.identity(value),'value':value}]}
def local(n,r,error=None):
 try:schema_validate(m.SCHEMA,r);p=m.normalize(r,None)
 except Exception as e:test(n,error is not None and error in str(e));return
 test(n,error is None);return p
p=local('whole-six-source-IR-batch',base);test('all-seven-whole-values-selected',len(p['items'])==7)
v=m.normalize_value(value);test('canonical-object-field-order',list(v)==sorted(v));test('natural-and-boolean-distinct',m.ir(0)!=m.ir(False));test('unicode-composed-distinct',m.semantic('é')!=m.semantic('e\u0301'))
for name,raw in [('duplicate-key',b'{"id":"a","id":"b"}'),('nonfinite',b'{"n":NaN}')]:
 try:C.decode(raw)
 except Exception:test(name+'-raw-refusal',True)
 else:raise ValueError(name+' accepted')
r=copy.deepcopy(base);r['values'][0]['identity']='0'*64;local('changed-content-hash-refused',r,error='identity mismatch')
r=copy.deepcopy(base);r['sources'][0]['binding']['sha256']='0'*64;local('changed-source-binding-refused',r,error='stale')
for name,bad in [('float-canonicalization-not-silent',0.0),('fraction-rejected',0.5),('negative-natural',-1),('invalid-scalar','\ud800')]:
 try:m.normalize_value(bad)
 except Exception:test(name,True)
 else:raise ValueError(name+' accepted')
# Existing atomic core query normalizes 0.0 explicitly; this new IR requires the
# resulting natural. It never changes or bypasses the original exact input checks.
legacy=C.decode(b'{"epoch":0.0}');test('raw-core-number-retained-until-explicit-normalization',type(legacy['epoch']) is float and m.ir(0)=='(.natural 0)')
client=Client('E05',policy);ri=write(out/'batch-request.json',base);a=client.qualify(json.dumps(base,ensure_ascii=False).encode());ra=write(out/'batch-result.json',a);cases.append({'name':'complete-core-and-five-extension-batch','input':ri,'answer':ra});print('whole-batch',a['status'],a.get('reason',''),flush=True)
test('actual-full-batch-kernel',a['status']=='fresh-extension-candidate');test('whole-value-equality',a['value']['value']['items']==p['items']);test('fresh-IR-event',client.live_event(a));test('saved-IR-no-new-event',not Client('E05',policy).live_event(a));test('no-IR-authority',not a['value']['value']['application_authorized'])
write(H/'controls.json',{'result':'pass','controls':controls,'cases':cases,'full_witnesses_required':1,'whole_decoded_values':7,'bridge_scope':'Whole core semantic graph and E00–E04 semantic results plus independent scalar/escaping/type/key challenge; original raw exact inputs retained.','authority_effect':'none'})
