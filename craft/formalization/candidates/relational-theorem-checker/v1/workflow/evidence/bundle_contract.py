"""Closed R03 transport and identity checks; these do not establish readiness."""
from pathlib import Path
import importlib.util
import sys

HERE=Path(__file__).resolve().parent
PROOF=HERE.parent/'proof-verifier'
sys.path.insert(0,str(PROOF))
spec=importlib.util.spec_from_file_location('r02_exact_proof_verifier',PROOF/'verifier.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
s=v.s;g=v.g;i=v.i
SCHEMA='relational.evidence-bundle/v1-candidate'
PROOF_TARGETS=set(v.CATALOG)-{'independence-witnesses'}
WITNESS_TARGETS={'inhabited-model','independence-witnesses'}
class UnsupportedScope(ValueError):
 pass

ROLE_SCHEMA={'proof-submission':v.SCHEMA,
 'model-witness':'relational.scoped-model-evidence/v1-candidate',
 'search-result':'relational.bounded-search-result/v1-candidate'}


def policy():
 return {'schema':'relational.bundle-policy/v1-candidate','bundle_schema':SCHEMA,
  'required_set':'E02 generator from current bound proposal; client cannot select IDs, scope, hard flags or policy',
  'artifact_schemas':ROLE_SCHEMA,'proof_targets':sorted(PROOF_TARGETS),'witness_targets':sorted(WITNESS_TARGETS),
  'methods':['builtin','proof-submission','checked-model-witness','bounded-search'],
  'builtin':'Verifier executes the required check; an empty artifact map is a request to compute evidence, never evidence that it passed.',
  'proof_submission':'Exact R02 checking plus actual proposed extension hypotheses; a generic lemma cannot replace a model witness.',
  'bounded_search':'No theorem or readiness from provider success, exhaustion or a missing witness.',
  'dimensions':['selected-data-compatibility','invariant-preservation','model-conservativity'],
  'rule_execution_profile':'Captured empty-rule baseline, unchanged graph/registry, fresh ordinary unary ReviewSignal heads and old-predicate positive bodies; other meanings require another preservation/conservativity profile.',
  'aggregation':'Readiness only after every independently required hard obligation has current allowed verified evidence.',
  'currentness':'Full bound baseline, source, graph, rules, profile, artifact and verifier identities before/after execution.',
  'artifact_transport':'Strict bounded JSON, original-byte hashes, resolved workspace containment and independently expected schema/role. Local CLI filesystem ownership only; no HTTP artifact service is implemented.',
  'declaration_sources':'Before and after source bindings must resolve inside the workspace, match original-byte hashes and decode as strict JSON objects within 4 MiB before classification or source projection.',
  'authority_effect':'none','full_source_semantics':'unsupported; inherited source-level obligations remain visible'}


def source_boundary(proposal):
 """Fence raw declaration bytes before older projection helpers read them."""
 s.require(isinstance(proposal,dict),'proposal must be a JSON object')
 for stage in ['before','after']:
  snapshot=proposal.get(stage)
  s.require(isinstance(snapshot,dict) and isinstance(snapshot.get('registry'),dict),'missing proposal registry: '+stage)
  kinds=snapshot['registry'].get('kinds')
  s.require(isinstance(kinds,list),'registry declarations must be a list: '+stage)
  for row in kinds:
   s.require(isinstance(row,dict) and 'source' in row,'missing declaration source binding: '+stage)
   _,raw=v.safe_binding(row['source'],limit=4*1024*1024)
   try:document=i.c.d.decode(raw)
   except RecursionError as error:raise ValueError('declaration JSON parser depth limit exceeded') from error
   s.require(isinstance(document,dict),'declaration source must be a strict JSON object')


def execution_profile(proposal):
 source_boundary(proposal)
 required=g.generate(proposal)
 if not required['supported']:raise UnsupportedScope('unsupported structural or semantic change profile')
 if required['classification']['rule_change']:
  if proposal['after']['graph']!=proposal['before']['graph'] or proposal['before']['rules']:
   raise UnsupportedScope('mixed graph/rule or nonempty old-rule baseline requires another captured inference profile')
  for rule in proposal['after']['rules']:
   if rule.get('head',{}).get('predicate')!='ReviewSignal' or any(term.get('predicate') not in {'Conforms','Admitted','CheckedRoot'} for term in rule.get('body',[])):
    raise UnsupportedScope('old-predicate heads or fresh recursive bodies require another model-expansion profile')
  i.capture(proposal)  # Independent typed/range/domain checks still apply.
 return required


def dependencies(proposal):
 execution_profile(proposal)
 proof=v.current_dependencies(proposal)
 paths=set();pending=[]
 for task_id in ['R01','R02','C06','E02','I06']:
  task=s.task(task_id);s.require(task['status']=='accepted','unaccepted bundle prerequisite: '+task_id)
  binding=task['validation']['acceptance_ref'];s.check_binding(binding);pending.append(s.ROOT/binding['path'])
 while pending:
  path=Path(pending.pop()).resolve()
  if path in paths:continue
  paths.add(path)
  if path.suffix=='.json':
   doc=s.read(path)
   if doc.get('schema')=='relational.task-acceptance/v1':
    for binding in doc['artifacts']+doc['dependency_bindings']:
     s.check_binding(binding);pending.append(s.ROOT/binding['path'])
 paths.update(HERE/name for name in ['bundle_contract.py','semantic_replay.py','aggregate.py','bundle-verifier','aggregate-verifier'])
 result={'schema':'relational.bundle-dependencies/v1-candidate',
  'proposal_identity':g.c.identity(proposal),'baseline_identity':proposal['baseline_identity'],
  'proof_dependencies':proof,'bundle_policy_identity':g.c.identity(policy()),
  'bindings':[s.binding(path) for path in sorted(paths)],'authority_effect':'none'}
 result['dependency_identity']=g.c.identity(result)
 return result


def methods_for(name):
 result={'builtin'}
 if name in PROOF_TARGETS:result.add('proof-submission')
 if name in WITNESS_TARGETS:result.update({'checked-model-witness','bounded-search'})
 return result


def artifact(binding,role):
 _,data=v.safe_binding(binding,limit=4*1024*1024)
 doc=i.c.d.decode(data)
 s.require(isinstance(doc,dict),'artifact must be a JSON object')
 expected=ROLE_SCHEMA[role]
 s.require(doc.get('schema') in expected if isinstance(expected,set) else doc.get('schema')==expected,
  'artifact schema does not match independently expected role: '+role)
 return doc


def make_bundle(proposal):
 required=execution_profile(proposal)
 return {'schema':SCHEMA,'proposal_identity':required['proposal_identity'],
  'baseline_identity':proposal['baseline_identity'],'policy_identity':g.c.identity(policy()),
  'dependencies':dependencies(proposal),
  'obligations':[{'id':o['id'],'name':o['name'],'hard':True,'scope':o['scope'],
   'method':'builtin','artifacts':{}} for o in required['obligations']]}


def validate_transport(proposal,bundle,check_dependencies=True):
 """Validate complete identities and typed roles; truth must be rechecked later."""
 source_boundary(proposal)
 s.require(isinstance(bundle,dict) and set(bundle)=={'schema','proposal_identity','baseline_identity','policy_identity','dependencies','obligations'},'unknown or missing bundle fields')
 required=g.generate(proposal)
 s.require(required['supported'],'unsupported change meaning; no bundle readiness')
 s.require(bundle['schema']==SCHEMA,'unsupported bundle schema')
 s.require(bundle['proposal_identity']==required['proposal_identity'] and bundle['baseline_identity']==proposal['baseline_identity'],'bundle belongs to another proposal or baseline')
 s.require(bundle['policy_identity']==g.c.identity(policy()),'bundle cannot weaken independently selected obligation policy')
 s.require(isinstance(bundle['obligations'],list),'bundle obligations must be a list')
 entries={}
 for entry in bundle['obligations']:
  s.require(isinstance(entry,dict) and set(entry)=={'id','name','hard','scope','method','artifacts'},'client verdicts, status or weakened result fields are not evidence')
  s.require(isinstance(entry['id'],str) and entry['id'] not in entries,'duplicate or invalid obligation identity')
  entries[entry['id']]=entry
 s.require(set(entries)=={o['id'] for o in required['obligations']},'complete independent obligation set omitted, duplicated or injected')
 loaded={}
 for obligation in required['obligations']:
  entry=entries[obligation['id']];name=obligation['name']
  s.require(entry['name']==name and entry['scope']==obligation['scope'] and entry['hard'] is True,'obligation name/scope/hard policy weakened')
  s.require(entry['method'] in methods_for(name),'evidence method does not discharge independently expected obligation: '+name)
  expected_roles={'builtin':set(),'proof-submission':{'proof-submission'},
   'checked-model-witness':{'model-witness'},'bounded-search':{'search-result'}}[entry['method']]
  s.require(isinstance(entry['artifacts'],dict) and set(entry['artifacts'])==expected_roles,'missing or substituted artifact role')
  loaded[obligation['id']]={}
  for role,binding in entry['artifacts'].items():
   doc=artifact(binding,role)
   s.require(doc.get('proposal_identity')==required['proposal_identity'],'artifact belongs to another proposal')
   if role=='proof-submission':
    s.require(doc.get('obligation_id')==obligation['id'],'proof artifact belongs to another obligation')
    s.require(doc.get('required_statement')==v.CATALOG[name][1],'artifact required statement weakened or substituted')
   if role=='model-witness':
    s.require(set(doc)=={'schema','proposal_identity','witness'},'unknown or missing scoped model evidence fields')
    _,raw=v.safe_binding(doc['witness'],limit=4*1024*1024)
    witness=i.c.d.decode(raw)
    s.require(isinstance(witness,dict),'model witness must be a JSON object')
    if required['classification']['rule_change']:
     s.require(witness.get('schema')=='relational.inference-model/v1','expected captured inference model role')
     s.require(witness.get('normal_form_identity')==i.capture(proposal)['after_normal']['normal_form_identity'],'model witness belongs to another inference context')
    else:
     s.require(set(witness)=={'proposal_identity','graph','claim'} and witness.get('proposal_identity')==required['proposal_identity'],'expected scoped registry model request')
    claim=witness.get('claim',{})
    expected_claim='non-entailment' if name=='independence-witnesses' else 'model-existence'
    s.require(isinstance(claim,dict) and claim.get('kind')==expected_claim,'model existence and non-entailment claims cannot substitute for one another')
   loaded[obligation['id']][role]={'wrapper':doc,'witness':witness} if role=='model-witness' else doc
 if check_dependencies:
  s.require(bundle['dependencies']==dependencies(proposal),'bundle dependencies stale, incomplete or substituted')
 return {'required':required,'entries':entries,'loaded_artifacts':loaded,
  'transport_valid':True,'semantic_verification_complete':False,
  'readiness':'unresolved','authority_effect':'none'}
