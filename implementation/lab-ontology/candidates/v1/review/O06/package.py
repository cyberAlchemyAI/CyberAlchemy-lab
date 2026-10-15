"""Exact independent review members, retained source gaps and no owner fabrication."""
import copy,hashlib,json,re
from pathlib import Path,PurePosixPath
from jsonschema import Draft202012Validator
HERE=Path(__file__).resolve().parent
ONTOLOGY=HERE.parents[1]
ROOT=ONTOLOGY.parents[3]
RUN=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
CONTEXT={'path':str((RUN/'context-O06.json').relative_to(ROOT)),'sha256':'933fbaab7a567f0041f7209bdf5c8a1bc05b712a85ad96a6f9ec14120a458f80'}
PINS={
 'O01':('implementation/lab-ontology/candidates/v1/receipts/O01-0006.json','6ff33d5f15ac0df045ff1e9b4ee582a5376c76d06d6aa24ac0f758f1a75b533b'),
 'O02':('implementation/lab-ontology/candidates/v1/receipts/O02/0004.json','3d9b8b3b3f9a8e3824432ecfe3c3cd6ace7893b6397315d8e3d44f5535b84c6d'),
 'O04':('implementation/lab-ontology/candidates/v1/receipts/O04/0001.json',None),
 'O05':('implementation/lab-ontology/candidates/v1/receipts/O05/0001.json','4375c986a84e1be17416517f0a55120895011728877ddee168cb1e7ded7ac562'),
 'O03':('implementation/lab-ontology/candidates/v1/receipts/query-coverage.json','3838485fadd399fc45ace7fb63f7c8f07a8190d6eb799cad59a768e5fea3502b'),
 'W09':('implementation/lab-workflows/candidates/v1/episodes/W09/receipts/0001.json','28952cff7345612a3f2d4a0784c5a2fd8a17e44677e3deedf83371a198ff0ae0')}
OWNER={'actual_owner_outcome':None,'selected_outcome':None,'actual_answering_principal_ref':None,'current_owner_authority_verified':False,'authority_effect':'none'}
AXES=['metadata_carrier_admission','ontology_representation_adoption','implementation_selection','property_schema_selection','profile_selection',
 'query_contract_selection','private_metadata_use_policy','exact_source_validation_read_policy','archive_retention','source_semantic_admission',
 'source_body_import','source_execution','public_export','runtime_activation','source_retirement','new_action_authorization','domain_instance_admission','global_relation_creation']
DENIED=AXES[9:]
EXCLUSIONS=['Source semantic meaning/admission','Original private body import/use beyond exact-byte and literal-selector validation','Source execution',
 'Public export','Live service activation or cutover','Source retirement','Secrets or Session memory','New operation permission','Whole repository/domain coverage','General efficacy or human pilot inference']
INVALIDATION=['Source bytes changed','Target/postimage changed','Exact scope or requested effect changed','Owner authority unresolved or changed','Final package changed or independent member omitted']
def require(v,message):
 if not v:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def encoded(v):return (json.dumps(v,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())
def parse(raw):
 def pairs(rows):
  value={}
  for k,v in rows:require(k not in value,'duplicate JSON key');value[k]=v
  return value
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def binding(p):
 p=Path(p);p=ROOT/p if not p.is_absolute() else p
 return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def bound(b,allow_external=False):
 require(type(b) is dict and set(b)=={'path','sha256'},'closed exact file binding required')
 name=b['path'];p=PurePosixPath(name);require(type(name) is str and (not p.is_absolute() or allow_external) and '..' not in p.parts and p.as_posix()==name and '\\' not in name and re.fullmatch('[0-9a-f]{64}',b['sha256']),'unsafe original binding')
 f=Path(name) if p.is_absolute() else ROOT/name;require(f.is_file() and (f.resolve().is_relative_to(ROOT) or allow_external and p.is_absolute()) and not f.is_symlink() and not any(x.is_symlink() for x in f.parents),'unsafe original location')
 raw=f.read_bytes();require(sha(raw)==b['sha256'],'source changed: '+name);return raw
def original(b):return parse(bound(b))
def put(p,value):
 with p.open('xb') as f:f.write(encoded(value))
def pins():
 ctx=original(CONTEXT);lookup={b['path']:b for b in ctx['source_bindings']};result={}
 for name,(path,h) in PINS.items():
  b={'path':path,'sha256':h or lookup[path]['sha256']};require(lookup[path]==b,'independent prerequisite pin differs')
  value=original(b);require(value['result']=='PASS' and value.get('task_complete',True) and value['actual_owner_outcome'] is None,'complete scoped prerequisite required '+name)
  for f in value['files']:bound({k:f[k] for k in ['path','sha256']},allow_external=True)
  result[name]=b
 for b in ctx['source_bindings']:bound(b)
 return result

def member(ref,kind,targets,evidence,axes,scope,effect,dependencies=None,postimage=None):
 require(set(axes)<=set(AXES) and not set(axes)&set(DENIED),'undeclared or excluded requested effect')
 return {**OWNER,'member_ref':ref,'member_class':kind,'admission_posture':'candidate-unadmitted',
  'targets':targets,'evidence':evidence,'requested_effect':effect,'requested_axes':{a:a in axes for a in AXES},'scope':scope,
  'proposed_owner_roles':['role:repository-owner'],'dependencies':dependencies or [],'exclusions':EXCLUSIONS,'invalidation':INVALIDATION,
  'postimage_binding':postimage,'application_route':'S02/R08 exact owner response and A01 accepted closure only; no preparation-time dispatch'}

def expected(output):
 """Derive original targets and selected effects; caller flags cannot broaden them."""
 receipt_pins=pins();output=Path(output);require(output.is_absolute() and output.resolve().is_relative_to(HERE/'packages') and not output.is_symlink() and not any(p.is_symlink() for p in output.parents),'candidate package root required')
 members=[];files={};post=output/'postimages';proposals=output/'proposals'
 def copy_target(source,name):
  b=binding(source);raw=bound(b);p=post/name;files[p]=raw;return b,binding_from_bytes(p,raw)
 def protocol(ref,kind,paths,axes,effect,scope=None):
  targets=[binding(p) for p in sorted(paths)];require(targets,'empty protocol target closure')
  members.append(member(ref,kind,targets,list(receipt_pins.values()),axes,scope or {'protocol_only':True,'Artifact_Type_added':False,'runtime_execution_granted':False},effect))
 def glob(folder):return [p for p in (ONTOLOGY/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
 profile=ONTOLOGY/'profiles/lab-ontology-profile.json'
 protocol('protocol:O06:governed-subject-representation-profile','representation-profile',[profile],['profile_selection'],
  'Select the exact closed representation profile, namespaces, independent axes and local ordered signatures; no global signature or source meaning is added.')
 native=[p for p in glob('adapters/native') if p.suffix in ['.rs','.toml','.lock','.json']]
 protocol('protocol:O06:native-lifecycle-extension','native-implementation-selection',native,['implementation_selection'],
  'Select the exact inherited/delta native implementation and entrypoint contract for representation lifecycle; actual permanent binding/adoption dispatch remains S02/R08/A01.',
  {'implementation_source_only':True,'existing_admitted_reducer_unchanged':True,'operation_grant':False,'runtime_binding_materialization_required_at':'S02','cross_family_atomicity_claimed':False})
 props=[ONTOLOGY/'adapters/lifecycle/profiles/node-properties.schema.json',ONTOLOGY/'adapters/lifecycle/profiles/relation-properties.schema.json']
 protocol('protocol:O06:closed-native-property-schemas','native-property-contract',props,['property_schema_selection'],
  'Select exact rich node/relation property schemas with their independent source/schema/mapping witnesses.')
 rich=[p for p in glob('adapters/lifecycle') if p.suffix in ['.py','.json'] and 'withdrawal' not in p.parts]
 protocol('protocol:O06:rich-domain-translation','rich-translation-selection',rich,['implementation_selection','profile_selection'],
  'Select exact rich source/Definition/semantic/governance translation and challenge joins; carrier, represented subject and source authority remain distinct.')
 withdrawals=[p for p in glob('adapters/lifecycle/withdrawal') if p.suffix in ['.py','.json']]
 protocol('protocol:O06:source-withdrawal-reconciliation','source-effect-mapping-selection',withdrawals,['implementation_selection'],
  'Select exact signed source-withdrawal/eligibility reconciliation code; source withdrawal and ontology retirement/removal remain separate operation-authorized effects.')
 confidence=original(binding(ONTOLOGY/'adapters/lifecycle/profiles/translation-profile.json'))['confidence'];conf_file=proposals/'unknown-confidence.json';files[conf_file]=encoded(confidence)
 members.append(member('protocol:O06:unknown-confidence','confidence-vocabulary',[binding_from_bytes(conf_file,files[conf_file]),binding(ONTOLOGY/'adapters/lifecycle/profiles/translation-profile.json')],
  [receipt_pins['O02']],['profile_selection'],{'scheme_ref':confidence['scheme_ref'],'allowed_levels':confidence['allowed_levels'],'no_positive_assessment':True},
  'Select the exact not-assessed sentinel for evidence and commitment; no assessment, owner reliance or action permission is inferred.',postimage=binding_from_bytes(conf_file,files[conf_file])))
 query=original(original(receipt_pins['O03'])['selection_binding']);qpaths=[ROOT/b['path'] for b in query['files'] if b['path'].endswith('.py')]
 protocol('protocol:O06:three-lens-query-adapter','query-implementation-selection',qpaths,['implementation_selection'],
  'Select the exact bounded deterministic Python lens adapter; incomplete mappings, absent alignment and stale/unknown/expired sources remain explicit.',
  {'Python_normative':True,'Rust_graph_acceleration_selected':False,'governed_genesis':'hash-sealed; zero approval signatures','ephemeral_scope_lifetime_seconds':900,'exact_endpoint_mapping_is_separate':True})
 qcontracts=[ROOT/b['path'] for b in query['files'] if '/contracts/' in b['path']]+[ONTOLOGY/'coverage/REPLAY-DESIGN-ERRATUM.md']
 protocol('protocol:O06:three-lens-query-contract','query-contract-selection',qcontracts,['query_contract_selection'],
  'Select exact closed query request/response/claim contracts and mandatory replay evidence correction; historical D73, current D75 and source-native cuts remain separate.')
 migration=[p for p in glob('migration/adapters') if p.suffix in ['.py','.json']]
 protocol('protocol:O06:source-metadata-generator','metadata-generator-selection',migration,['implementation_selection'],
  'Select the exact original-byte/selector/source-qualified metadata generator; no governed Implementation realization or domain fulfillment is invented.')
 local=ONTOLOGY/'migration/adapters/translation-profile.json';protocol('protocol:O06:legacy-local-vocabulary','source-local-profile-selection',[local],['profile_selection'],
  'Select the exact twenty-predicate qualified source-local interpretation profile; 49 directed and one symmetric edge remain distinct from global Typed Relations.')
 srcroot=ONTOLOGY/'migration/candidate/0001';core=original(binding(srcroot/'core.json'));index=original(binding(srcroot/'record-index.json'));archive=original(binding(srcroot/'native.snapshot'))
 require(len(index)==220 and len(core['dispositions'])==140,'original selected adaptation closure differs')
 import_refs=[];adoptions=[]
 for row in index:
  require(row['kind'] in ['source','ontology-node','ontology-edge','generated-output'],'unexpected metadata carrier')
  b= binding(srcroot/row['path']);require(b['sha256']==row['sha256'],'original metadata carrier digest differs');record=original(b)
  source,target=copy_target(srcroot/row['path'],row['path']);ref='protocol:O06:metadata:'+row['version_ref'];import_refs.append(ref)
  destination='authority/ontology-imports/legacy-product-source/v1/'+row['path']
  scope={'exact_identity_ref':row['node_id'],'exact_version_ref':row['version_ref'],'carrier_ref':row['carrier_ref'],'schema_binding':row['schema_binding'],
   'original_candidate_owner_ref':record['owner_ref'],'fixture_owner_is_final_owner':False,'source_scope_ref':record['scope_ref'],'visibility':'private-source-qualified-metadata',
   'proposed_destination':destination,'destination_is_prospective':True,'source_semantic_admission':False,'domain_instance_conformance':False,
   'ontology_governance_adoption_included':False,'recorded_body_posture_retained':record.get('record_state',record.get('lifecycle_state'))}
  members.append(member(ref,'metadata-carrier-admission',[target,source],[receipt_pins['O05'],receipt_pins['O03']],['metadata_carrier_admission'],scope,
   'Admit only this exact private source-qualified metadata carrier snapshot under its independent instance admission; no source meaning or current ontology adoption is inferred.',
   dependencies=['protocol:O06:private-metadata-use','protocol:O06:legacy-local-vocabulary'],postimage=target))
  if row['kind'] in ['ontology-node','ontology-edge']:
   payload=record['payload'];semantic=payload.get('semantic_event_ref',payload.get('governance_binding',{}).get('semantic_event_ref'))
   matches=[]
   import base64
   for name,envelope in archive['files'].items():
    if name.startswith('governance/'):
     event=parse(base64.b64decode(envelope['base64_original_bytes'],validate=True))
     if event['semantic_ref']==semantic:matches.append(event)
   require(len(matches)==1,'exact predecessor governance tuple unavailable');g=matches[0]
   intent={'schema_version':'lab-O06-representation-adoption-intent/v1-candidate','subject_carrier_version_ref':row['version_ref'],'metadata_record_binding':source,
    'semantic_tuple':semantic,'predecessor_governance_tuple':{'event_id':g['event_id'],'event_digest':g['event_digest'],'governance_cursor':g['governance_cursor']},
    'archive_binding':binding(srcroot/'native.snapshot'),'owner_outcome_required':True,'verified_owner_required':True,'actual_owner_outcome':None,'authority_effect':'none',
    'consequence_rule':{'preserve_original_semantic_bytes':True,'append_new_governance_event_after_exact_R08_member_acceptance':True,'old_candidate_event_relabeling_allowed':False,
     'resulting_candidate_or_maturity_status':'admitted-representation','evidence_confidence':'not-assessed','commitment_confidence':'not-assessed',
     'provenance_requires_actual_owner_Decision_binding':True,'owner_route_requires_verified_current_accountable_owner':True,'source_meaning_admitted':False,
     'new_Cuts_and_Views_regenerated_without_new_semantic_Decision':True,'old_rich_carrier_remains_exact_historical_projection':True},
    'final_event_bytes_and_owner_core_must_be_materialized_at':'S02','permanent_runtime_installation_authorized':False}
   path=proposals/'adoption'/ (sha(row['version_ref'].encode())+'.json');files[path]=encoded(intent);adoptions.append(binding_from_bytes(path,files[path]));adopt_ref='protocol:O06:ontology-adoption:'+row['version_ref']
   members.append(member(adopt_ref,'representation-adoption-intent',[binding_from_bytes(path,files[path]),source],[receipt_pins['O05'],receipt_pins['O02']],['ontology_representation_adoption'],
    {'exact_semantic_tuple':semantic,'exact_predecessor_governance_tuple':intent['predecessor_governance_tuple'],'namespace':'lab.legacy-source-assertion.cav2-product-thesis','source_meaning_admitted':False},
    'Adopt only the exact source-qualified native representation through separately generated owner-bound governance consequences; archived metadata admission, epistemic truth and operation rights remain separate.',
    dependencies=[ref,'protocol:O06:native-lifecycle-extension','protocol:O06:closed-native-property-schemas','protocol:O06:unknown-confidence'],postimage=binding_from_bytes(path,files[path])))
 dispositions={'schema_version':'lab-O06-source-disposition-selection/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
  'original_core_binding':binding(srcroot/'core.json'),'source_selection_binding':core['selection_binding'],'items':core['dispositions'],
  'excluded_packages':core['excluded_packages'],'deferred_source_epoch':core['deferred_source_epoch'],'original_residual_questions':core['outside_references'],
  'resolved_scoped_questions':{'qualified_local_vocabulary':'Exact O05 translation profile with twenty predicates; no global axis inferred.',
   'domain_conformance':'No domain instances proposed; original metadata and independently scoped representation only.',
   'unavailable_originals':'Nine remain blocked; no current-byte replacement or source alias.',
   'private_use':'Private local metadata retention and byte/literal-selector validation policy only; actual owner/access authority remains required at S02/R08 and each operation.'},
  'admitted_source_effects_applied':0,'source_retirements':0,'public_body_export_allowed':False}
 dp=proposals/'source-dispositions.json';files[dp]=encoded(dispositions)
 members.append(member('protocol:O06:source-dispositions','source-disposition-selection',[binding_from_bytes(dp,files[dp]),binding(srcroot/'core.json')],[receipt_pins['O04'],receipt_pins['O05']],[],
  {'selected_items':140,'blocked_exact_revisions':9,'excluded_packages':len(core['excluded_packages']),'deferred_epoch_retained':True},
  'Retain every exact original disposition, blocked revision, excluded package and separately observed source epoch; no source retirement, replacement or domain conformance follows.',postimage=binding_from_bytes(dp,files[dp])))
 use={'schema_version':'lab-O06-private-source-use-proposal/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
  'source_selection_binding':core['selection_binding'],'proposed_owner_roles':['role:repository-owner'],'source_owner_and_access_authority_verified':False,
  'allowed_purposes':['private local source-qualified metadata retention','exact original byte hashing','exact literal source selector validation','private exact owner review'],
  'source_validation_read_only':True,'current_operation_authority_required':True,'body_import':False,'semantic_admission':False,'execution':False,'public_export':False,
  'service_activation':False,'source_retirement':False,'secrets_or_Session_memory_allowed':False}
 up=proposals/'private-source-use.json';files[up]=encoded(use)
 members.append(member('protocol:O06:private-metadata-use','private-source-use-policy',[binding_from_bytes(up,files[up])],[receipt_pins['O04'],receipt_pins['O05']],
  ['private_metadata_use_policy','exact_source_validation_read_policy'],{'proposal_only':True,'owner_access_authority_required':True,'new_operation_permission_granted':False},
  'Select the exact private metadata/byte-selector validation data-use policy; establish actual source/target ownership and access authority before final selection and every operation.',postimage=binding_from_bytes(up,files[up])))
 protocol('protocol:O06:original-native-archive-retention','source-history-retention',[srcroot/'native.snapshot',srcroot/'manifest.json',srcroot/'core.json'],['archive_retention'],
  'Retain the exact original candidate native archive for verified recovery; candidate event bytes are not relabeled as admitted and contain no keys or Session memory.',
  {'semantic_cursor':88,'governance_cursor':88,'replay_source_of_underlying_events':'candidate-owned original canonical-format events','archive_is_live_store':False,'private_metadata_only':True})
 qreceipt=original(receipt_pins['O03']);observations={}
 for scope,relative in [('historical-D73','coverage/questions/0017-historical/result.json'),('current-D75','coverage/questions/0015-D75/result.json'),('native-O05','coverage/questions/0014-native/result.json')]:
  result=original(binding(ONTOLOGY/relative));observations[scope]={'result_binding':binding(ONTOLOGY/relative),'questions':{}}
  for name,entry in result['questions'].items():
   response=original(entry['response_binding']);observations[scope]['questions'][name]={'response_binding':entry['response_binding'],'result_status':response['result_status'],
    'source_snapshot':{k:response['source_snapshot'][k] for k in ['manifest_digest','source_cut_digest','histories','admission_epoch']},
    'coverage':response['coverage'],'gaps':response['gaps'],'authority_effect':'none'}
 op=proposals/'query-coverage-and-gap-selection.json';files[op]=encoded(observations)
 members.append(member('protocol:O06:query-coverage-residue','query-evidence-selection',[binding_from_bytes(op,files[op])],[receipt_pins['O03']],[],
  {'unknown_or_unmapped_not_repaired':True,'historical_and_current_cuts_distinct':True,'whole_repository_claim':False},
  'Retain the exact historical/current/native query cuts, partitions, frontier and unresolved alignment/admission/revision/schema gaps; no complete-repository or domain truth claim.',postimage=binding_from_bytes(op,files[op])))
 members.append(member('protocol:O06:W09-bounded-work-evidence','operational-evidence-selection',[receipt_pins['W09'],original(receipt_pins['W09'])['review_selection_binding']],
  [receipt_pins['W09']],[],{'actual_bounded_examples':3,'Research_hypothesis':'negative','Lessons_proof_scoped_only':True,'current_application_permission':False,'human_pilot':False,'general_causal_efficacy_claim':False},
  'Retain actual bounded Engineering/Research/Learning and cold context evidence, including negative and counterevidence; no current Lesson permission or broader effectiveness is inferred.'))
 require(len({m['member_ref'] for m in members})==len(members),'duplicate independent member')
 refs={m['member_ref'] for m in members};require(all(set(m['dependencies'])<=refs for m in members),'missing member dependency')
 value={'schema_version':'lab-O06-review-preparation/v1-candidate','task':'O06','status':'prepared-for-final-S02-R08-review',**OWNER,
  'complete_final_package':False,'final_checkpoint':'R08','application_task':'A01','admitted_coherence_task':'A03','candidate_coherence_task':'O07',
  'atomicity':'One final actual response may resolve independently scoped members; the eventual selected S02 bundle is indivisible, and a rejected/revised scope blocks dependent effects.',
  'source_context_binding':CONTEXT,'prerequisite_bindings':receipt_pins,'members':members,'counts':{'members':len(members),'metadata_carriers':len(index),'representation_adoption_intents':len(adoptions),
   'source_items':140,'blocked_source_revisions':9,'original_nodes':38,'original_local_edges':50,'global_relations_created':0,'excluded_packages':len(core['excluded_packages'])},
  'source_disposition_binding':binding_from_bytes(dp,files[dp]),'query_gap_binding':binding_from_bytes(op,files[op]),'replay_design_correction_binding':binding(ONTOLOGY/'coverage/REPLAY-DESIGN-ERRATUM.md'),
  'actual_effects':{a:False for a in AXES},'canonical_effects_applied':0,'local_transactions_applied':0,'ontology_events_appended':0,'source_retirements':0,
  'runtime_activation':False,'human_pilot':False,'private_body_exports':0,'Session_memory_exports':0,
  'final_assembly_obligations':['Verify actual answering principal and current accountable/source/target owner authority; no preparation flag is authority.',
   'Materialize exact final carrier registry/instance postimages, native Implementation/binding/environment/entrypoint and profile/effect selection members.',
   'Materialize exact owner-bound ontology governance successor consequences at S02; preserve semantic bytes/unknown confidence and regenerate current Cuts/Views after accepted application.',
   'Join complete API/client/SQLite/workflow/query/ontology evidence and remaining R07/S02 criteria without importing source semantic meaning.',
   'Freeze complete selected S02 package and Decision cores before the one actual R08 response; a rejected/revised scope blocks affected canonical application.',
   'Recheck all exact source, target, privacy/ownership and evidence cuts at final review/application; changed bytes or scope require successor review.',
   'Keep private archived snapshots, missing originals, excluded/deferred packages, query gaps and negative/counterevidence explicit; no retirement/activation or source executable follows.'],
  'original_operational_owner_obligation_route':'R08/A01; no actual disposition supplied by O06 preparation','claim_ceiling':'Exact independent candidate ontology/profile/metadata/adoption review preparation only. No owner outcome, canonical admission/adoption, source semantics/body import, operation grant, activation, public export, retirement, human pilot or full-plan completion.'}
 files[output/'preparation.json']=encoded(value);return value,files

def binding_from_bytes(p,raw):return {'path':Path(p).relative_to(ROOT).as_posix(),'sha256':sha(raw)}
def source_guard():
 manifest=original(binding(HERE/'manifest.json'))
 require(manifest['schema_version']=='lab-O06-source-closure/v1-candidate' and manifest['authority_effect']=='none' and manifest['actual_owner_outcome'] is None,'invalid frozen source closure')
 for b in manifest['files']:bound(b,allow_external=True)
 return manifest

def validate(v,output):
 source_guard()
 wanted,files=expected(output)
 require(v==wanted,'prepared member/effect/target/owner/coverage selection differs from exact original reconstruction')
 Draft202012Validator(original(binding(HERE/'preparation.schema.json'))).validate(v)
 entries=list(Path(output).rglob('*'));require(all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in entries),'unsafe candidate package entry');actual={p for p in entries if p.is_file()};require(actual==set(files),'unexpected/missing exact package file')
 for p,raw in files.items():
  require(not p.is_symlink() and p.read_bytes()==raw,'exact candidate postimage differs')
  if p.parent.name=='adoption':schema_path=HERE/'schemas/adoption-intent.schema.json'
  elif p.parent.name=='proposals':schema_path=HERE/'schemas'/f'{p.stem}.schema.json'
  else:schema_path=None
  if schema_path:Draft202012Validator(original(binding(schema_path))).validate(parse(raw))
 for row in original(binding(ONTOLOGY/'migration/candidate/0001/record-index.json')):
  raw=(Path(output)/'postimages'/row['path']).read_bytes();Draft202012Validator(original(row['schema_binding'])).validate(parse(raw))
 return {'result':'PASS','members':len(v['members']),'metadata_carriers':220,'adoption_intents':88,'source_items':140,'blocked_revisions':9,'authority_effect':'none','actual_owner_outcome':None}
def build(output):
 source_guard();output=Path(output);require(not output.exists(),'refuse package overwrite');v,files=expected(output)
 output.mkdir(parents=True,exist_ok=False)
 for p,raw in files.items():
  p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as stream:stream.write(raw)
 result=validate(v,output);print(encoded({**result,'preparation_binding':binding(output/'preparation.json')}).decode(),end='');return result

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True);parser.add_argument('--manifest-sha256',required=True)
 args=parser.parse_args();require(binding(HERE/'manifest.json')['sha256']==args.manifest_sha256,'independent frozen source closure required');build(Path(args.output))
