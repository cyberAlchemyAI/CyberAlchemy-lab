from pathlib import Path
from ..p03.context import C,BASE,require,binding,check
from ..p06.worker_context import ResourceExhausted
from ..execution.extension_runtime import lean_string,load_extension,schema_validate
H=Path(__file__).resolve().parent;SCHEMA=H/'ir.schema.json'
SCOPE='Canonical typed semantic transport after decoding; universal IR denotation theorem plus finite actual whole-value comparison, no universal raw-byte parser proof.'
def modules():return [('CanonicalIR',H/'CanonicalIR.lean'),('ImportCorrectness',H/'ImportCorrectness.lean')]
def normalize_value(v,depth=0,counter=None):
 if counter is None:counter=[0]
 counter[0]+=1
 if depth>32 or counter[0]>8192:raise ResourceExhausted('IR total tree/depth ceiling; no partial import')
 if v is None or type(v) is bool:return v
 if type(v) is int:require(0<=v<=1000000000,'IR natural out of bounds');return v
 if type(v) is str:
  require(len(v)<=16384 and not any(0xD800<=ord(c)<=0xDFFF for c in v),'invalid Unicode scalar/length');return v
 if type(v) is list:return [normalize_value(x,depth+1,counter) for x in v]
 if type(v) is dict:
  require(len(v)<=128 and all(type(k) is str for k in v),'IR record key/count')
  return {normalize_value(k,depth+1,counter):normalize_value(v[k],depth+1,counter) for k in sorted(v)}
 raise ValueError('IR permits typed naturals/Booleans, not floating semantic numbers')
def normalize(r,ctx):
 items=[];refs=[];labels=set();count=[0]
 for source in r['sources']:
  task=source['task'];file=check(source['binding']);require(file.is_relative_to(BASE) and file.stat().st_size<=4194304,'IR source scope/size')
  receipt_ref=binding(BASE/task.lower()/'task-acceptance.json');receipt=C.decode(check(receipt_ref).read_bytes());require(receipt['result']=='accepted' and source['binding'] in receipt['artifacts']+receipt['inputs'],'IR source is not accepted exact evidence')
  decoded=C.decode(file.read_bytes());refs += [source['binding'],receipt_ref]
  if task=='P09':
   require(source['selector']=='before-graph','core selector mismatch');C.validate('request',decoded);value=decoded['proposal']['before']['graph']
  else:
   require(source['selector']=='extension-result' and decoded.get('extension')==task and decoded.get('status')=='fresh-extension-candidate','extension selector/source mismatch');value=decoded['value']['value'];schema_validate(load_extension(task).SCHEMA,value,True)
  label=task+'-'+source['selector'];require(label not in labels,'duplicate IR source');labels.add(label);value=normalize_value(value,counter=count);items.append({'label':label,'identity':C.identity(value),'value':value})
 for item in r['values']:
  require(item['label'] not in labels and item['identity']==C.identity(item['value']),'duplicate label/value identity mismatch');labels.add(item['label']);items.append({**item,'value':normalize_value(item['value'],counter=count)})
 require(items and len(items)<=16,'nonempty bounded IR batch required')
 return {'request':r,'items':items,'source_bindings':refs}
def seq(xs,render):
 out='.nil'
 for x in reversed(xs):out='(.cons '+render(x)+' '+out+')'
 return out
def ir(v):
 if v is None:return '.null'
 if type(v) is bool:return '(.boolean '+('true' if v else 'false')+')'
 if type(v) is int:return '(.natural '+str(v)+')'
 if type(v) is str:return '(.text '+primary_scalars(v)+')'
 if type(v) is list:return '(.array '+seq(v,ir)+')'
 out='.nil'
 for k in reversed(sorted(v)):out='(.field '+primary_scalars(k)+' '+ir(v[k])+' '+out+')'
 return '(.record '+out+')'
def primary_scalars(v):return '['+', '.join(str(ord(c)) for c in v)+']'
def scalars(v):
 raw=v.encode('utf-32-be');return '['+', '.join(str(int.from_bytes(raw[i:i+4],'big')) for i in range(0,len(raw),4))+']'
def semantic(v):
 if v is None:return '.null'
 if type(v) is bool:return '(.boolean '+('true' if v else 'false')+')'
 if type(v) is int:return '(.natural '+str(v)+')'
 if type(v) is str:return '(.scalars '+scalars(v)+')'
 if type(v) is list:return '(.array '+seq(v,semantic)+')'
 out='.nil'
 for k in reversed(sorted(v)):out='(.field '+scalars(k)+' '+semantic(v[k])+' '+out+')'
 return '(.record '+out+')'
def render(p):
 lines=['import ImportCorrectness','set_option maxRecDepth 8192','set_option maxHeartbeats 4000000','open RelationalExtensions.Canonical','namespace IRInstance']
 for n,item in enumerate(p['items']):
  lines+=['def transport'+str(n)+' : IR := '+ir(item['value']),'def meaning'+str(n)+' : Meaning := '+semantic(item['value']),
  'theorem exact_import'+str(n)+' : importChecked transport'+str(n)+' = some meaning'+str(n)+' := by rfl',
  'theorem denotation'+str(n)+' : meaning'+str(n)+' = denote transport'+str(n)+' := imported_denotation _ _ exact_import'+str(n),
  '#print axioms exact_import'+str(n),'#print axioms denotation'+str(n)]
 lines+=['theorem duplicate_fields_rejected : importChecked (.record (.field [105,100] .null (.field [105,100] .null .nil))) = none := by rfl','theorem unordered_fields_rejected : importChecked (.record (.field [118,101,114,115,105,111,110] .null (.field [105,100] .null .nil))) = none := by rfl','theorem invalid_scalar_rejected : importChecked (.text [55296]) = none := by rfl','theorem malformed_array_rejected : importChecked (.array (.field [] .null .nil)) = none := by rfl','#print axioms invalid_scalar_rejected','#print axioms malformed_array_rejected','#print axioms duplicate_fields_rejected','#print axioms unordered_fields_rejected','end IRInstance',''];return '\n'.join(lines)
def result(p):return {'schema':'relational.canonical-ir-result/v1','profile':p['request']['profile'],'items':p['items'],'sources':p['request']['sources'],'assurance':'Universal canonical IR import preserves typed denotation; whole finite decoded-value witnesses; raw JSON/parser/emitter/host remain assumptions.','authority_effect':'none','application_authorized':False}
