from pathlib import Path
import sys,copy
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import stress_adapter as a
s=a.s;c=a.c

def refresh(q):
 b=q['baseline'];e=next(e for e in b['graph']['assertions'] if e['id']==q['assertion_id'])
 for k,v in {'source_identity':s.identity(b['graph']),'registry_identity':s.identity(b['registry']),'context_identity':s.identity(b['context']),'assertion_identity':s.identity(e),'typed_identity':s.identity(q['typed'])}.items():q['interpretation'][k]=v
 q['interpretation']['record_identity']=s.identity({k:v for k,v in q['interpretation'].items() if k!='record_identity'})
 return q

def example(operation):
 b=c.fixture();file=s.V1/('relation-stress/v1/implementation/examples/'+('acts-for.json' if operation=='delegation' else 'inherits-contract.json'));t=s.read(file)
 b['graph']['nodes']=[];b['graph']['assertions']=[];b['graph']['assessments']=[]
 def node(ref,kind):
  b['graph']['nodes'].append({'ref':ref,'kind':kind,'content_identity':s.identity({'ref':ref,'kind':kind})})
 if operation=='delegation':
  e=t['edge'];node(e['agent'],'agent-instance');node(e['principal'],'principal');node(e['delegation'],'delegation')
  kind='relation.acts-for';source,target=e['agent'],e['principal'];qual={'delegation_ref':'delegation-token','scope_ref':'scope-token','effective_period':'opaque-period','revocation_state':'opaque-revocation'}
  fields={'delegation_ref':e['delegation'],'scope_ref':e['scope'],'effective_period':e['period'],'revocation_state':e['revokedAt']};b['context']={**t['snapshot']['ref'],'epoch':t['snapshot']['epoch']};b['inference']['snapshot_epoch']=t['snapshot']['epoch']
 else:
  e=t['graph']['inheritances'][0];node(e['subject'],'capability-instance');node(e['contract'],'contract');node(e['binding'],'capability-realization-binding')
  kind='relation.inherits-contract';source,target=e['subject'],e['contract'];qual={'binding_ref':'binding-token','contract_version_ref':'contract-version-token'}
  fields={'binding_ref':e['binding'],'contract_version_ref':e['contract'],'scope':e['scope'],'condition_ref':{'id':e['condition'],'version':'condition-v1'}}
  b['context']={'id':'snapshot','version':'v1','epoch':5};b['inference']['snapshot_epoch']=5
 version=next(k['version'] for k in b['registry']['kinds'] if k['id']==kind)
 assertion={'id':e['id'],'kind':kind,'kind_version':version,'source':source,'target':target,'qualifiers':qual};b['graph']['assertions']=[assertion]
 b['inference']['domain']=[{'kind':'reference',**n['ref']} for n in b['graph']['nodes']]+[{'kind':'text','value':n['kind']} for n in b['graph']['nodes']]+[{'kind':'effect','value':'admission'},{'kind':'scope','value':'repo'},{'kind':'epoch','value':5}]
 b['source_bindings']=[s.binding(s.V1/'registry/normalized-registry.json'),s.binding(file)]
 q={'schema':'relational.interpretation-request/v2','operation':operation,'baseline':b,'assertion_id':e['id'],'interpretation':{'record_id':'interpretation:'+e['id'],'record_version':'v2','fields':fields,'evidence':s.binding(file)},'typed':t,'evaluations':[]}
 return refresh(q)
def holds(q,status='holds'):
 q=copy.deepcopy(q);key=a.condition_key(q,q['typed']['graph']['inheritances'][0]);q['evaluations']=[{'id':'evaluation-1','key':key,'status':status,'evidence':'supplied-condition-assessment'}];return q
