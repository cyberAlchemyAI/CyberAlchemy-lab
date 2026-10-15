"""Richer migration is explicitly distinct from fixed-frame recursive extension."""
from pathlib import Path
import sys,copy
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'s15'));import contracts as c
s=c.s
F0={'relation.conforms-to','relation.declares-effect-on','relation.materializes-consequence'}
MAPPED={'relation.acts-for','relation.inherits-contract'}
def selected_graph(b):
 g=copy.deepcopy(b['graph']);g['assertions']=[e for e in g['assertions'] if e['kind'] in F0]
 out=c.legacy.r.resolve(g,b['registry']);s.require(out['status']=='supported' and not out['errors'],'invalid selected source graph: '+str(out['errors']))
 return g

def classify(before,after):
 c.validate_baseline(before);c.validate_baseline(after)
 c.reference_stability(before['graph'],after['graph'])
 for key in ['registry','producers','interpretations','context','profile_identity','catalog_identity','toolchain','authority_effect']:
  s.require(before[key]==after[key],'richer append migration requires unchanged '+key)
 for key in before['inference']:
  if key!='domain':s.require(before['inference'][key]==after['inference'][key],'richer append migration changes inference '+key)
 s.require(after['inference']['domain'][:len(before['inference']['domain'])]==before['inference']['domain'],'domain must append exact old values')
 for key in ['nodes','assertions','assessments']:
  s.require(after['graph'][key][:len(before['graph'][key])]==before['graph'][key],'graph '+key+' must append exact old values')
 s.require(before['graph']['graph_id']==after['graph']['graph_id'],'graph identity changed')
 old,new=selected_graph(before),selected_graph(after)
 unknown=sorted({e['kind'] for e in after['graph']['assertions'] if e['kind'] not in F0})
 s.require(not unknown,'richer append migration currently selected F0 only; additional mapped stress registration needs S07/S09: '+str(unknown))
 return {'change_class':'richer-migration','before_identity':s.identity(before),'after_identity':s.identity(after),'old_selected_graph':old,'new_selected_graph':new,'target':'Successor.Transition.InitialViewRelation','model_conservativity':'not-claimed; domain/initial-observation growth','authority_effect':'none'}
def example(before):
 a=copy.deepcopy(before);node={'ref':{'id':'new-contract','version':'v2'},'kind':'contract','content_identity':'3'*64};a['graph']['nodes'].append(node);a['inference']['domain'].append({'kind':'reference',**node['ref']})
 subject=next(e['source'] for e in a['graph']['assertions'] if e['kind']=='relation.conforms-to');token='assessment:new-contract'
 a['graph']['assessments'].append({'ref':token,'mode':'conformance','subject':subject,'target':node['ref'],'scope':'new-scope','role':'','output_digest':'','accepted':True})
 version=next(k['version'] for k in a['registry']['kinds'] if k['id']=='relation.conforms-to')
 a['graph']['assertions'].append({'id':'new-conformance','kind':'relation.conforms-to','kind_version':version,'source':subject,'target':node['ref'],'qualifiers':{'conformance_scope':'new-scope','exact_version_ref':'v2','conformance_evidence_refs':token}})
 a['inference']['domain'].append({'kind':'scope','value':'new-scope'})
 return a
