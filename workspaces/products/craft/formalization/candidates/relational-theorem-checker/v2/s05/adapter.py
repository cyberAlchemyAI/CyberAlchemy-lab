"""Checked contextual projection. JSON decoding/normalization remain tested boundaries."""
from pathlib import Path
import sys,copy,json,tempfile,subprocess,os,hashlib
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'s15'));import contracts as c
sys.path.insert(0,str(BASE/'s17'));import resources as resource
sys.path.insert(0,str(BASE/'s18'));import transition
sys.path.insert(0,str(c.s.V1/'inference/derivations'));import derivation_checker as render
s=c.s
class Unsupported(ValueError):pass

def decode(raw):
 limits=s.read(BASE/'s17/preflight-bounds.json')['limits'];s.require(len(raw if isinstance(raw,bytes) else raw.encode())<=limits['input_bytes'],'input byte envelope exceeded')
 # Scan nesting outside strings before json.loads can recurse. Decoder remains a tested boundary.
 depth=0;quoted=False;escape=False
 for char in raw.decode('utf-8') if isinstance(raw,bytes) else raw:
  if quoted:
   if escape:escape=False
   elif char=='\\':escape=True
   elif char=='"':quoted=False
  elif char=='"':quoted=True
  elif char in '[{':
   depth+=1
   if depth>limits['json_depth']:raise resource.Exhausted('unknown-resource: JSON nesting ceiling')
  elif char in ']}':depth-=1
 return c.decode(raw)

def ordered_modules():
 core=s.core_modules({'RelationalInput','RelationalSemantics','SemanticLogic','InferenceCore','ReferenceChecker','DerivationSoundness','ClosureAdequacy','ProtectedLineage','StressTypes','ObligationSemantics'})
 return core+[(n,BASE/f's00/{n}.lean') for n in ['RequirementSemantics','RequiredStatements']]+[(n,BASE/f's02/{n}.lean') for n in ['ContextProjection','ProjectionProofs']]+[(n,BASE/f's16/{n}.lean') for n in ['ProducerPolicy','SupportedObservations','SupportLineage']]

def predict(b):
 g=transition.selected_graph(b);normal=c.f.normalize(b['inference']);preds={p['id']:p for p in normal['predicates']};facts=[];supports=[]
 ids={'source_identity':s.identity(b['graph']),'selected_graph_identity':s.identity(g),'profile_identity':b['profile_identity'],'catalog_identity':b['catalog_identity'],'context_identity':s.identity(b['context'])}
 def add(id,values,witness):
  atom={'predicate':{k:preds[id][k] for k in ['id','version','hash']},'values':values}
  s.require(all(v in normal['domain'] for v in values),'projection value outside declared domain: '+id)
  if atom not in facts:facts.append(atom)
  supports.append({'schema':'relational.source-support/v2','atom':atom,**ids,'witness':witness})
 for e in g['assertions']:
  if e['kind']=='relation.conforms-to':
   witness={'kind':'conformance','assertion_id':e['id'],'assessment_token':e['qualifiers']['conformance_evidence_refs']}
   add('ConformsTo',[{'kind':'reference',**e['source']},{'kind':'reference',**e['target']},{'kind':'scope','value':e['qualifiers']['conformance_scope']}],witness)
 for n in g['nodes']:add('TargetKind',[{'kind':'reference',**n['ref']},{'kind':'text','value':n['kind']}],{'kind':'node-kind','node_ref':n['ref']})
 for e in g['assertions']:
  if e['kind']=='relation.conforms-to':add('Conforms',[{'kind':'reference',**e['source']}],{'kind':'existential-conformance','assertion_id':e['id'],'assessment_token':e['qualifiers']['conformance_evidence_refs']})
 return {'graph':g,'facts':facts,'supports':supports,'normal':normal,'unhandled_kinds':sorted({e['kind'] for e in b['graph']['assertions'] if e['kind'] not in transition.F0}),**ids}

def support_check(b,rows):
 expected=predict(b)['supports'];validator=__import__('jsonschema').Draft202012Validator(s.read(HERE/'support.schema.json'))
 for row in rows:validator.validate(row)
 s.require(rows==expected,'support inventory missing/stale/substituted; exact projector support witnesses required')
 return True

def witness_source(predicted,expected=True):
 n=predicted['normal'];preds={p['id']:p for p in n['predicates']};v='{ conformance := '+render.key_lean(preds['ConformsTo'])+', targetKind := '+render.key_lean(preds['TargetKind'])+', unary := '+render.key_lean(preds['Conforms'])+' }'
 source='import SupportLineage\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Successor.Transport.Witness\nopen Inference\ndef graph : Relational.Graph := '+c.f.d.graph_lean(predicted['graph'])+'\ndef v : Successor.Vocabulary := '+v+'\ndef facts : List Atom := '+c.f.d.rows(predicted['facts'],render.atom_lean)+'\n'
 source+='def inventoryExact : Bool := decide (Relational.Inv graph ∧ (∀ a ∈ facts, a ∈ Observation.observed v graph) ∧ (∀ a ∈ Observation.observed v graph, a ∈ facts))\n'
 source+='theorem checked_inventory : inventoryExact = '+str(expected).lower()+' := by decide\n#print axioms checked_inventory\nend Successor.Transport.Witness\n'
 return source

def project(request,build=None):
 __import__('jsonschema').Draft202012Validator(s.read(HERE/'request.schema.json')).validate(request)
 b=request['baseline'];resource.preflight(b);c.validate_baseline(b)
 s.require(request['profile_identity']==b['profile_identity'] and request['catalog_identity']==b['catalog_identity'],'request profile/catalog substitution')
 predicted=predict(b);support_check(b,predicted['supports'])
 if build is None:
  tmp=Path(tempfile.mkdtemp(prefix='v2-projection-',dir=HERE/'runs'));return project(request,tmp)
 build=Path(build);build.mkdir(parents=True,exist_ok=True)
 # Qualified build reuse is permitted only after all module source and binary identities
 # are rechecked. It is not a readiness cache; the actual instance recompiles each time.
 module_files=ordered_modules();audit=build/'dependency-build.json'
 if audit.exists():
  deps=s.read(audit)
  s.require([x['source'] for x in deps['modules']]==[s.binding(p) for _,p in module_files],'stale proof dependency build')
  for x in deps['modules']:s.check(x['source']);s.check(x['olean'])
 else:s.write(audit,{'modules':s.compile_modules(build,module_files)})
 name='ProjectionWitness_'+s.identity(request)[:20];path=build/(name+'.lean');path.write_text(witness_source(predicted));logs=s.compile_modules(build,[(name,path)])
 s.require(path.read_text()==witness_source(predicted),'instance source changed during compilation')
 return {'schema':'relational.projection-result/v2','status':'observed','projection_checked':True,'readiness':'pending-full-obligation-replay','full_graph_semantics':'selected F0 projection only; unhandled meanings '+str(predicted['unhandled_kinds']),'facts':predicted['facts'],'supports':predicted['supports'],'unhandled_kinds':predicted['unhandled_kinds'],'source_identity':predicted['source_identity'],'profile_identity':b['profile_identity'],'catalog_identity':b['catalog_identity'],'baseline_identity':s.identity(b),'context_identity':predicted['context_identity'],'kernel_evidence':logs,'budget':resource.preflight(b),'truth_boundary':['supplied accepted assessments; no authenticity proof','tested JSON/source-to-Lean projection','same pinned Lean kernel'],'authority_effect':'none'}

def request(b):return {'schema':'relational.projection-request/v2','operation':'project','baseline':b,'profile_identity':b['profile_identity'],'catalog_identity':b['catalog_identity']}
def main():
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('request',type=Path);p.add_argument('--output',type=Path);args=p.parse_args()
 try:out=project(decode(args.request.read_bytes()));code=0
 except (resource.Exhausted,subprocess.TimeoutExpired) as e:out={'status':'unknown-resource','reason':str(e),'complete_closure':False,'readiness':'blocked','authority_effect':'none'};code=3
 except Unsupported as e:out={'status':'unsupported','reason':str(e),'readiness':'blocked','authority_effect':'none'};code=4
 except Exception as e:out={'status':'invalid','reason':str(e).splitlines()[0],'readiness':'blocked','authority_effect':'none'};code=2
 if args.output:s.write(args.output,out)
 print(json.dumps(out,indent=2));return code
if __name__=='__main__':sys.exit(main())
