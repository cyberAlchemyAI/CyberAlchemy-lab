from pathlib import Path
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import stress_adapter as a
s=a.s;HERE=Path(__file__).resolve().parent
text={'type':'string','minLength':1};sha={'type':'string','pattern':'^[0-9a-f]{64}$'}
def obj(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
def arr(p):return {'type':'array','items':p}
ref=obj({'id':text,'version':text});nat={'type':'integer','minimum':0};opt={'oneOf':[nat,{'type':'null'}]};binding=obj({'path':text,'sha256':sha})
base=s.read(s.BASE/'s15/baseline.schema.json');base.pop('$schema',None)
old=a.typed.schema('request');defs=old['$defs'];typedBranches=[row for row in old['oneOf'] if row['properties']['operation'].get('const') in ['evaluate-acts-for','close-inherits-contract']]
key=obj({'profile':text,'condition':ref,'context':ref,'subject':ref,'target':ref,'scope':text,'epoch':opt})
evaluation=obj({'id':text,'key':key,'status':{'enum':['holds','does-not-hold','unknown']},'evidence':text})
rows=[]
for operation in ['delegation','inheritance']:
 fields=obj({'delegation_ref':ref,'scope_ref':text,'effective_period':defs['period'],'revocation_state':opt}) if operation=='delegation' else obj({'binding_ref':ref,'contract_version_ref':ref,'scope':text,'condition_ref':ref})
 record=obj({'record_id':text,'record_version':text,'record_identity':sha,'source_identity':sha,'registry_identity':sha,'context_identity':sha,'assertion_identity':sha,'typed_identity':sha,'fields':fields,'evidence':binding})
 rows.append(obj({'schema':{'const':'relational.interpretation-request/v2'},'operation':{'const':operation},'baseline':base,'assertion_id':text,'interpretation':record,'typed':{'oneOf':typedBranches},'evaluations':arr(evaluation)}))
s.write(HERE/'interpretation.schema.json',{'$schema':'https://json-schema.org/draft/2020-12/schema','$defs':defs,'oneOf':rows})
