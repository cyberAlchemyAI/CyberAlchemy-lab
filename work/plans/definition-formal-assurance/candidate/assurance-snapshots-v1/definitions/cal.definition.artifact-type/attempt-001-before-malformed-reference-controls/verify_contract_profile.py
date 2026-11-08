"""Bounded synthetic registration and read-only exact v1/v2/v3 carrier evidence."""
import copy,json,types
import build_candidate as b
import verifier as v

FIELDS={'type_ref','version','artifact_kind','semantic_definition_refs','schema','direction','projection','validation_rules','owner_route','lifecycle','claim_ceiling'}
def text(x):return isinstance(x,str) and bool(x.strip())
def closed(x,keys):return isinstance(x,dict) and set(x)==set(keys)
def profile_ok(p,catalog,schemas,admission_requested=False):
 if not closed(p,FIELDS):return False
 if any(not text(p[k]) for k in ['type_ref','version','artifact_kind','owner_route','lifecycle','claim_ceiling']):return False
 refs=p['semantic_definition_refs']
 if not isinstance(refs,list) or not refs or any(not text(x) for x in refs) or len(set(refs))!=len(refs):return False
 if any(x not in catalog or not catalog[x]['resolvable'] for x in refs):return False
 if admission_requested and any(catalog[x]['posture']!='admitted' or catalog[x]['current'] is not True for x in refs):return False
 s=p['schema']
 if not closed(s,['ref','sha256']) or s['ref'] not in schemas:return False
 selected=schemas[s['ref']]
 if s['sha256']!=b.ir.digest(selected) or selected.get('type')!='object' or selected.get('additionalProperties') is not False:return False
 d=p['direction']
 if not closed(d,['canonical','human_projection','policy']) or not text(d['canonical']) or not text(d['human_projection']) or d['canonical']==d['human_projection'] or d['policy']!='generated-only':return False
 projection=p['projection']
 if not closed(projection,['generator_ref','sha256','deterministic_declared']) or not text(projection['generator_ref']) or not isinstance(projection['sha256'],str) or len(projection['sha256'])!=64 or any(x not in '0123456789abcdef' for x in projection['sha256']) or projection['deterministic_declared'] is not True:return False
 rules=p['validation_rules']
 return isinstance(rules,list) and bool(rules) and all(text(x) for x in rules) and len(set(rules))==len(rules)

def verify(write=False):
 context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);b.r.verify(b.snapshot(),b.ROOT)
 runtime=v.f.current_bindings();bindings=[b.ref(p) for p in [b.UNIT/'verify_contract_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'resolver.py']]
 schema={'type':'object','additionalProperties':False,'properties':{'value':{'type':'string'}},'required':['value']}
 schemas={'synthetic.closed-schema@1':schema,'synthetic.open-schema@1':{**schema,'additionalProperties':True}}
 catalog={'synthetic.meaning@candidate.1':{'resolvable':True,'posture':'candidate','current':True},'synthetic.meaning@admitted.1':{'resolvable':True,'posture':'admitted','current':True},'synthetic.meaning@historical.1':{'resolvable':True,'posture':'admitted','current':False}}
 base={'type_ref':'synthetic.type/example@1','version':'1','artifact_kind':'example','semantic_definition_refs':['synthetic.meaning@candidate.1'],
 'schema':{'ref':'synthetic.closed-schema@1','sha256':b.ir.digest(schema)},'direction':{'canonical':'example.json','human_projection':'EXAMPLE.md','policy':'generated-only'},
 'projection':{'generator_ref':'synthetic.generator@1','sha256':'a'*64,'deterministic_declared':True},'validation_rules':['synthetic-shape'],
 'owner_route':'synthetic:owner','lifecycle':'synthetic:candidate','claim_ceiling':'Shape evidence only; no admission or world truth.'}
 controls=[]
 def add(name,change,expected,admission=False):
  p=copy.deepcopy(base);change(p);actual=profile_ok(p,catalog,schemas,admission)
  if actual!=expected:raise ValueError('Wrong profile control: '+name)
  controls.append({'case_id':name,'profile':p,'admission_necessary_condition_requested':admission,'accepted':actual,'actual_admission':False})
 add('candidate-binding-permits-candidate-authoring',lambda p:None,True)
 add('candidate-binding-blocks-Type-admission-necessary-condition',lambda p:None,False,True)
 add('admitted-current-binding-passes-necessary-condition-without-admission-act',lambda p:p.update(semantic_definition_refs=['synthetic.meaning@admitted.1']),True,True)
 add('multiple-meanings-are-permitted',lambda p:p.update(semantic_definition_refs=['synthetic.meaning@candidate.1','synthetic.meaning@admitted.1']),True)
 add('all-bindings-must-qualify-before-admission',lambda p:p.update(semantic_definition_refs=['synthetic.meaning@candidate.1','synthetic.meaning@admitted.1']),False,True)
 add('historical-admitted-binding-is-not-current-admission-binding',lambda p:p.update(semantic_definition_refs=['synthetic.meaning@historical.1']),False,True)
 for field in ['semantic_definition_refs','owner_route','lifecycle','claim_ceiling','validation_rules']:
  add('missing-'+field,lambda p,field=field:p.pop(field),False)
 add('empty-semantic-bindings',lambda p:p.update(semantic_definition_refs=[]),False)
 add('unresolved-exact-binding',lambda p:p.update(semantic_definition_refs=['synthetic.meaning@unknown.1']),False)
 add('bare-meaning-name-is-not-version-selection',lambda p:p.update(semantic_definition_refs=['synthetic.meaning']),False)
 add('duplicate-semantic-binding',lambda p:p['semantic_definition_refs'].append('synthetic.meaning@candidate.1'),False)
 add('wrong-schema-digest',lambda p:p['schema'].update(sha256='b'*64),False)
 add('open-schema-is-not-closed-representation',lambda p:p.update(schema={'ref':'synthetic.open-schema@1','sha256':b.ir.digest(schemas['synthetic.open-schema@1'])}),False)
 add('projection-cannot-be-canonical-input',lambda p:p['direction'].update(human_projection='example.json'),False)
 add('bidirectional-edits-not-selected-direction',lambda p:p['direction'].update(policy='editable-both'),False)
 add('unproven-generator-flag-not-filled-by-default',lambda p:p['projection'].update(deterministic_declared=False),False)
 add('bool-is-not-exact-version',lambda p:p.update(version=True),False)
 add('implicit-admission-extra-field',lambda p:p.update(implicit_admission=True),False)
 actual=[];selected={};projections=[]
 def capture(name,path):
  p=b.ROOT/path;reference=b.ref(p);raw=b.r.read_bytes(b.ROOT,path)
  if b.r.digest(raw)!=reference['sha256']:raise ValueError('Capture race')
  selected[name]=reference;return raw
 registry=b.r.parse(capture('registry','authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json'),'selected-artifact-registry')
 definitions=b.r.parse(capture('definition_registry','authority/definitions/registry.json'),'selected-definition-registry')
 def check(id,ok,detail=None):
  if not ok:raise ValueError('Actual carrier check failed: '+id)
  actual.append({'check_id':id,'result':True,'detail':detail})
 artifacts={};schemas_actual={}
 for version in ['v1','v2','v3']:
  folder='authority/artifact-types/artifact-type/'+version
  artifact=b.r.parse(capture(version+'_artifact',folder+'/artifact.json'),version+'-artifact');schema_actual=b.r.parse(capture(version+'_schema',folder+'/schema.json'),version+'-schema');b.c.Draft202012Validator.check_schema(schema_actual)
  check(version+'-exact-schema-and-shape',not list(b.c.Draft202012Validator(schema_actual).iter_errors(artifact)) and artifact['schema_digest']==selected[version+'_schema']['sha256'])
  entry=next(x for x in registry['admitted_contracts'] if x['artifact_type_ref']=='cal.artifact-type.artifact-type/'+version)
  check(version+'-selected-admission-overlay-exact-bytes',entry['artifact_path']==selected[version+'_artifact']['path'] and entry['artifact_sha256']==selected[version+'_artifact']['sha256'] and entry['schema_path']==selected[version+'_schema']['path'] and entry['schema_sha256']==selected[version+'_schema']['sha256'],{'embedded_status':artifact['status'],'registry_lifecycle':entry['lifecycle_state'],'decision_ref':entry['admission_decision_ref']})
  artifacts[version]=artifact;schemas_actual[version]=schema_actual
 check('v3-current-selection',registry['current_by_identity']['cal.artifact-type.artifact-type']=='cal.artifact-type.artifact-type/v3')
 old=artifacts['v2']['predecessor'];new=artifacts['v3']['predecessor_contract']
 check('v2-preserves-v1-exact-reference',old['artifact_path']==selected['v1_artifact']['path'] and old['artifact_sha256']==selected['v1_artifact']['sha256'] and old['schema_sha256']==selected['v1_schema']['sha256'])
 check('v3-preserves-v2-exact-reference',new['path']==selected['v2_artifact']['path'] and new['sha256']==selected['v2_artifact']['sha256'] and new['schema_sha256']==selected['v2_schema']['sha256'])
 for version in ['v2','v3']:
  artifact=artifacts[version];check(version+'-nonempty-new-semantic-bindings',bool(artifact['semantic_definition_refs']) and all(x.get('semantic_definition_refs') for x in artifact['registered_types']))
  for i,binding in enumerate(artifact['semantic_definition_bindings']):
   doc=b.r.parse(capture(version+'_meaning_'+str(i),binding['path']),'bound-meaning');version_ref=doc['definition_id']+'@'+doc['version']
   entry=next(x for x in definitions['entries'] if x['definition_id']==doc['definition_id'] and x['version']==doc['version'])
   check(version+'-meaning-'+str(i)+'-exact-current-source',version_ref==binding['definition_ref'] and selected[version+'_meaning_'+str(i)]['sha256']==binding['sha256']==entry['sha256'] and definitions['current_lookup'][doc['definition_id']]==version_ref and entry['lifecycle_state']=='admitted',{'embedded_binding_posture':binding['admission_posture'],'source_registry_posture':entry['lifecycle_state'],'admission_ref':entry['admission_decision_ref']})
  generator_path='authority/artifact-types/artifact-type/v2/generator.py' if version=='v2' else artifact['source_direction']['shared_generator_path']
  raw=capture(version+'_generator',generator_path);module=types.ModuleType('_bound_artifact_'+version);module.__file__=str(b.ROOT/generator_path);exec(compile(raw,str(b.ROOT/generator_path),'exec'),module.__dict__)
  original=copy.deepcopy(artifact);render=module.render if version=='v2' else module.render_artifact;first=render(artifact).encode();second=render(artifact).encode();expected=capture(version+'_human','authority/artifact-types/artifact-type/'+version+'/ARTIFACT.md')
  digest=artifact['source_direction']['generator_sha256'] if version=='v2' else artifact['source_direction']['shared_generator_sha256']
  check(version+'-two-render-parity-and-unmodified-input',first==second==expected and artifact==original and digest==selected[version+'_generator']['sha256']);projections.append({'version':version,'bytes':len(first),'sha256':b.r.digest(first)})
  if version=='v3':
   witness_path='authority/artifact-types/artifact-type/v3/'+artifact['validation_contract']['positive_projection'];first=module.render_instance(artifact,artifact).encode();second=module.render_instance(artifact,artifact).encode();expected=capture('v3_self_human',witness_path)
   check('v3-bounded-self-witness-projection-parity',first==second==expected and artifact==original)
   check('v3-bounded-self-registration',artifact['registered_types'][0]['artifact_type_ref']==artifact['artifact_type_ref'] and artifact['registered_types'][0]['schema_sha256']==artifact['schema_digest'])
 fixture_rows=[]
 fixture_paths=['authority/artifact-types/artifact-type/v2/fixtures/invalid/new-registration-without-definition-ref.json']+['authority/artifact-types/artifact-type/v3/'+x for x in artifacts['v3']['validation_contract']['negative_witnesses']]
 for i,path in enumerate(fixture_paths):
  fixture=b.r.parse(capture('fixture_'+str(i),path),'hostile-artifact-fixture');version='v2' if i==0 else 'v3';errors=[x.message for x in b.c.Draft202012Validator(schemas_actual[version]).iter_errors(fixture)];check('actual-hostile-fixture-'+str(i),bool(errors));fixture_rows.append({'path':path,'rejected':True,'schema_errors':errors})
 b.unchanged(list(selected.values())+context['sources']+bindings);b.r.verify(b.snapshot(),b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-artifact-type-contract-profile/v1-candidate','authority_effect':'none','status':'PASS-for-bounded-registration-and-selected-actual-carriers',
 'checker_bindings':bindings,'runtime_bindings':runtime,'selected_inputs':selected,'synthetic_catalog':catalog,'synthetic_schema_catalog':schemas,'profile_controls':controls,'profile_control_count':len(controls),'rejected_profile_controls':sum(not x['accepted'] for x in controls),
 'actual_checks':actual,'actual_check_count':len(actual),'actual_hostile_fixtures':fixture_rows,'actual_hostile_fixture_count':len(fixture_rows),'selected_carriers':3,'v1_declared_registration_count':len(artifacts['v1']['registered_types']),'projections':projections,
 'source_profile_embedding_reviewed':False,'unbounded_generator_determinism':False,'actual_admission_created':False,'new_type_instances_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,
 'claim_ceiling':'Synthetic necessary registration/admission conditions and read-only v1/v2/v3 exact schema/lineage/meaning/projection/hostile checks. Selected overlay admission is pre-existing recorded evidence, not an act/authenticated principal. No global registry completeness, live activation, generator determinism theorem or reviewed source-carrier embedding.'}
 if write:b.put('contract-profile-checks.json',report)
 elif not b.r.same_json(report,json.loads((b.UNIT/'contract-profile-checks.json').read_bytes())):raise ValueError('Fresh profile differs')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({k:x[k] for k in ['status','profile_control_count','rejected_profile_controls','actual_check_count','actual_hostile_fixture_count','selected_carriers','v1_declared_registration_count','source_profile_embedding_reviewed','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
