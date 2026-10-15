"""Pure bounded record checks and actual read-only carrier/catalog observations."""
import copy,json
import build_candidate as b
import verifier as v
ROLES={'decision','validation','promotion','implementation'}
FIELDS={'relation_id','source_ref','target_ref','scope_ref','relation_kind_ref','owner_ref','evidence_refs','review_effect'}
def errors(use,records):
 if set(use)!= {'source_ref','target_ref','scope_ref','reliance_roles'} or not isinstance(use['reliance_roles'],list) or any(x not in ROLES for x in use['reliance_roles']):return ['malformed-selected-use']
 if not use['reliance_roles']:return []
 diagnostics=[]
 for record in records:
  local=[]
  if set(record)!=FIELDS:local.append('missing-or-extra-vector-field')
  for name in ['relation_id','source_ref','target_ref','scope_ref','relation_kind_ref','owner_ref']:
   if not isinstance(record.get(name),str) or not record[name].strip():local.append('unnamed-'+name)
  if any(record.get(key)!=use[key] for key in ['source_ref','target_ref','scope_ref']):local.append('ordered-endpoint-or-scope-mismatch')
  ev=record.get('evidence_refs')
  if not isinstance(ev,list) or not ev or any(not isinstance(x,str) or not x.strip() for x in ev) or len(ev)!=len(set(ev)):local.append('invalid-explicit-evidence')
  effect=record.get('review_effect')
  if not isinstance(effect,dict) or set(effect)!= {'role','description','authority_effect'} or effect.get('role') not in ['validation','promotion'] or not isinstance(effect.get('description'),str) or not effect['description'].strip() or effect.get('authority_effect')!='none':local.append('invalid-description-not-permission')
  if not local:return []
  diagnostics.extend(local)
 return diagnostics or ['no-explicit-representative']
def base_record():return {'relation_id':'relation:example','source_ref':'schema:example','target_ref':'contract:example','scope_ref':'scope:example','relation_kind_ref':'relation:constrains-example','owner_ref':'role:example-owner','evidence_refs':['evidence:example'],'review_effect':{'role':'validation','description':'Require exact contract-shape check before review; no effect executed.','authority_effect':'none'}}
def controls():
 use={'source_ref':'schema:example','target_ref':'contract:example','scope_ref':'scope:example','reliance_roles':['decision']};rows=[]
 def add(id,mutate,expected=False):
  u=copy.deepcopy(use);records=[base_record()];mutate(u,records);observed=errors(u,records)
  if bool(observed)!=expected:raise ValueError('Wrong profile control '+id+' '+str(observed))
  rows.append({'case_id':id,'selected_use':u,'records':records,'errors':observed,'expected_rejection':expected,'actual_runtime_execution':False})
 add('explicit-relied-vector-no-executed-effect',lambda u,rs:None)
 for name in FIELDS:add('missing-'+name,lambda u,rs,name=name:rs[0].pop(name),True)
 add('reverse-ordered-endpoints',lambda u,rs:rs[0].update(source_ref=u['target_ref'],target_ref=u['source_ref']),True)
 add('different-selected-scope',lambda u,rs:rs[0].update(scope_ref='scope:other'),True)
 add('empty-owner',lambda u,rs:rs[0].update(owner_ref=' '),True)
 add('empty-evidence',lambda u,rs:rs[0].update(evidence_refs=[]),True)
 add('duplicate-evidence',lambda u,rs:rs[0].update(evidence_refs=['evidence:example']*2),True)
 add('review-description-is-not-authority',lambda u,rs:rs[0]['review_effect'].update(authority_effect='grant'),True)
 add('unknown-effect-role',lambda u,rs:rs[0]['review_effect'].update(role='blocking'),True)
 add('explicit-neutral-promotion-description',lambda u,rs:rs[0]['review_effect'].update(role='promotion',description='none'))
 add('no-representative-for-relied-use',lambda u,rs:rs.clear(),True)
 add('unrelied-idea-needs-no-record',lambda u,rs:(u.update(reliance_roles=[]),rs.clear()))
 add('every-unrelated-link-is-not-required-to-be-a-coupling',lambda u,rs:(u.update(reliance_roles=[]),rs[0].clear()))
 for role in sorted(ROLES):add(role+'-relies-on-constraint',lambda u,rs,role=role:u.update(reliance_roles=[role]))
 def self_link(u,rs):u['target_ref']=u['source_ref'];rs[0]['target_ref']=u['source_ref']
 add('no-universal-self-link-prohibition',self_link)
 return rows
def verify(write=False):
 context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings()
 paths={'checker':b.UNIT/'verify_coupling_profile.py','typed_schema':b.ROOT/'authority/artifact-types/typed-relation/v2/schema.json','typed_descriptor':b.ROOT/'authority/artifact-types/typed-relation/v2/artifact.json','typed_fixture':b.ROOT/'authority/artifact-types/typed-relation/v2/fixtures/valid/record.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','legacy_model':b.ROOT/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json','legacy_examples':b.ROOT/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/examples.json','extension_examples':b.ROOT/'authority/relation-kinds/candidates/0005-definition-complete-extension/examples.json'}
 bindings={name:b.ref(p) for name,p in paths.items()};documents={name:b.r.parse(b.r.read_bytes(b.ROOT,ref['path']),name) for name,ref in bindings.items() if name!='checker'}
 checks=[]
 def check(id,result,detail):
  checks.append({'check_id':id,'result':bool(result),'detail':detail})
  if not result:raise ValueError('Actual check failed '+id)
 schema=documents['typed_schema'];b.c.Draft202012Validator.check_schema(schema);fixture=documents['typed_fixture'];descriptor=documents['typed_descriptor'];kindreg=documents['kind_registry']
 check('selected-schema-digest-current',descriptor['schema_digest']==bindings['typed_schema']['sha256'],bindings['typed_schema'])
 check('selected-fixture-closed-schema-valid',not list(b.c.Draft202012Validator(schema).iter_errors(fixture)),bindings['typed_fixture'])
 type_entries=[x for x in documents['type_registry']['admitted_contracts'] if x['artifact_type_ref']=='cal.artifact-type.typed-relation/v2']
 check('exact-current-type-selected',len(type_entries)==1 and type_entries[0]['schema_sha256']==bindings['typed_schema']['sha256'],type_entries)
 source=b.source_ref(snap,'cal.definition.typed-coupling-invariant')
 bound=[x for x in documents['legacy_model']['definition_bindings'] if x['definition_ref']==source['version_ref']]
 check('legacy-model-exact-invariant-binding',len(bound)==1 and bound[0]['path']==source['path'] and bound[0]['sha256']==source['sha256'],bound)
 kinds={};kind_inputs={}
 for row in kindreg['entries']:
  p=b.ROOT/row['instance_path'];ref=b.ref(p);check('descriptor-current-'+row['relation_kind_id'],ref['sha256']==row['instance_sha256'],ref);kind_inputs[row['relation_kind_id']]=ref;kinds[row['relation_kind_id']]=json.loads(p.read_bytes())['payload']
 check('41-current-kinds-selected',len(kinds)==41 and kindreg['count']==41,{'count':len(kinds)})
 example_results=[]
 for catalog in ['legacy_examples','extension_examples']:
  for id,ex in documents[catalog].items():
   k=kinds[id];pairs={(p['source_kind'],p['target_kind']) for p in k['allowed_endpoint_pairs']}
   def endpoint_kind(ref):
    if ref.startswith('cal.artifact-type.'):return 'artifact-type'
    if ref.startswith('cal.definition.'):return 'definition'
    if ref.startswith('CA2-PRODUCT-'):return 'product'
    key=ref.split(':',1)[0];return 'method' if key=='measurement-method' else key
   pair=(endpoint_kind(ex['source_ref']),endpoint_kind(ex['target_ref']));contract=k['qualifier_contract'];qs={'type':'object','properties':contract['properties'],'required':contract['required_axes'],'additionalProperties':False}
   qualifier_errors=[e.message for e in b.c.Draft202012Validator(qs).iter_errors(ex['qualifiers'])];result=pair in pairs and not qualifier_errors and bool(ex['owner_ref']) and bool(ex['evidence_refs']) and ex['authority_effect']=='none'
   example_results.append({'catalog':catalog,'relation_kind_id':id,'ordered_pair':list(pair),'qualifier_errors':qualifier_errors,'selected_current_kind_pair_qualifiers_and_metadata_pass':result,'dedicated_review_effect_field_present':any(key in ex for key in ['review_effect','validation_effect','promotion_effect','blocking_effect'])})
 mismatches=[(x['catalog'],x['relation_kind_id'],x['qualifier_errors']) for x in example_results if not x['selected_current_kind_pair_qualifiers_and_metadata_pass']]
 check('selected-63-historical-example-observations-retain-one-mismatch',len(example_results)==63 and mismatches==[('legacy_examples','relation.conforms-to',["['receipt:remaining-18-model-validation'] is not of type 'string'"])],{'count':len(example_results),'compatible':62,'mismatches':mismatches,'scope':'Historical example mismatch retained; neither example nor current contract rewritten.'})
 # Actual probes check selected current shape, never mutate the fixture or canonical validators.
 probes=[]
 for id,change in [('literal-review-effect-extra-field',lambda x:x.update(review_effect={'role':'validation','description':'none','authority_effect':'none'})),('existing-authority-none-does-not-declare-review-effect',lambda x:None)]:
  x=copy.deepcopy(fixture);change(x);probes.append({'case_id':id,'schema_accepted':not list(b.c.Draft202012Validator(schema).iter_errors(x)),'actual_runtime_execution':False,'whole_source_conformance':False})
 if [x['schema_accepted'] for x in probes]!=[False,True]:raise ValueError('Unexpected carrier-shape boundary')
 records=controls();gap={'mapping_reviewed':False,'historical_qualifier_mismatches':mismatches,'dedicated_effect_fields_absent_from_selected_carrier':['review_effect','validation_effect','promotion_effect','blocking_effect'],'none_authority_field_is_not_review_effect_mapping':True,'historical_examples_without_dedicated_effect_field':sum(not x['dedicated_review_effect_field_present'] for x in example_results),'legacy_selected_source_section_adds_blocking_and_before_influence':True,'current_candidate_logic_encodes_neither_blocking_role_nor_temporal_before':True,'common_kind_operational_effect_is_not_an_executed_effect':True,'selected_typed_schema_kind_count':len(schema['properties']['payload']['properties']['relation_kind_ref']['enum']),'selected_current_catalog_kind_count':len(kinds)}
 report={'schema_version':'definition-assurance-typed-coupling-profile/v1-candidate','status':'PASS-for-bounded-coupling-records-and-actual-carrier-observations','authority_effect':'none','checker_bindings':[bindings['checker'],b.ref(b.UNIT/'build_candidate.py')],'input_refs':[b.ref(b.UNIT/'t.json'),b.ref(b.UNIT/'static-ir.json'),b.ref(b.UNIT/'legacy-source-section.md')],'runtime_bindings':runtime,'selected_inputs':bindings,'kind_inputs':kind_inputs,'profile_control_count':len(records),'rejected_profile_controls':sum(x['expected_rejection'] for x in records),'profile_controls':records,'actual_check_count':len(checks),'actual_checks':checks,'actual_example_check_count':len(example_results),'actual_example_results':example_results,'actual_boundary_probes':probes,'source_carrier_mapping_gaps':gap,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'source_profile_embedding_reviewed':False,'new_relations_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'claim_ceiling':'Exact conditional synthetic records and actual selected schema/catalog observations. No live reliance, required effect mapping, prohibition of all self-links, owner fidelity, historical model promotion, source-conformant embedding, forbidden-cycle proof or unbounded before-influence compliance.'}
 b.unchanged(list(bindings.values())+list(kind_inputs.values())+report['input_refs']);b.r.verify(snap,b.ROOT);b.external_current(context)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('coupling-profile-checks.json',report)
 elif not b.r.same_json(report,json.loads((b.UNIT/'coupling-profile-checks.json').read_bytes())):raise ValueError('Fresh profile differs')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profile_controls':x['profile_control_count'],'rejected_profiles':x['rejected_profile_controls'],'actual_checks':x['actual_check_count'],'actual_examples':x['actual_example_check_count'],'actual_boundary_probes':len(x['actual_boundary_probes']),'mapping_reviewed':False,'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
