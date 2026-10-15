"""Explicit Promotion/domain-adoption hypotheses and bounded current-catalog observations."""
import ast,copy,itertools,json,re,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
CONTEXT_AXES=['candidate','version','kind','origin_domain','exercise_domain','purpose','surface']
LADDER=['source-evidence','candidate','owner-routed-review','promoted-authority','optional-pressure']
DOMAIN_PATH=['domain-owned-source','origin-exercise','import-candidate','generalized-proposal','cross-context-exercise','challenge-review','CAV2-owner-decision','promoted-version','separate-domain-adoption']
def baseline():
 context={'candidate':'hyp:candidate','version':'hyp:v1','kind':'Definition','origin_domain':'hyp:origin','exercise_domain':'hyp:other','purpose':'hyp:reusable-method','surface':'hyp:CAV2'}
 return {'lifecycle_fields':{'stages':LADDER,'per_stage_gates':{n:'hyp:gate-'+n for n in LADDER},'owner_route':'hyp:CAV2-owner-route','stop_rule':'hyp:stop-or-demote'},'field_maps':{n:'hyp:map-'+n for n in b.FIELDS},'context':context,'query':copy.deepcopy(context),'origin_owner':'hyp:origin','origin_exercised':True,'other_exercised':True,'independently_owned':True,'materially_distinct':True,'challenge_and_contrary_evidence_reviewed':True,'CAV2_owner_promoted_label':False,'promotion_decision':None,'independent_qualification':False,'support':{n:None for n in ['origin_owner_authentication','exercise_owner_authentication','CAV2_owner_authentication','source_fidelity','version_identity','challenge_evidence','promotion_evidence_ceiling']},'origin_object_ref':'hyp:origin-local-object','origin_object_retained':True,'adoption_decision':None,'provenance_event':{'event_id':'hyp:upstream-provenance','owner_role':'hyp:origin-provenance-owner','principal_ref':'hyp:same-principal','origin_version':'hyp:upstream-v0'},'implicit_effects':[],'actual_promotion_or_adoption_verified':False,'source_owner_reviewed':False}
def supported(p):
 p.update(CAV2_owner_promoted_label=True,independent_qualification=True,support={n:'hyp:independent-'+n for n in p['support']},promotion_decision={'event_id':'hyp:CAV2-promotion-decision','owner_role':'hyp:CAV2-owner','candidate':p['context']['candidate'],'version':p['context']['version'],'declared_effect':'hyp:CAV2-local-authority-only'})
def adopting(p):
 p.update(adoption_decision={'event_id':'hyp:domain-adoption-decision','owner_role':'hyp:consuming-domain-owner','principal_ref':'hyp:same-principal','candidate':p['query']['candidate'],'version':p['query']['version'],'domain':'hyp:consuming-domain','support':'hyp:separate-domain-owner-support'})
def evaluate(p):
 es=[]
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected hypothetical Promotion profile')
 fields=p['lifecycle_fields'];ck(set(fields)=={'stages','per_stage_gates','owner_route','stop_rule'} and bool(fields['stages']) and set(fields['per_stage_gates'])==set(fields['stages']) and all(fields['per_stage_gates'].values()) and bool(fields['owner_route']) and bool(fields['stop_rule']),'explicit four lifecycle fields and gates for selected stages')
 ck(set(p['field_maps'])==set(b.FIELDS) and all(p['field_maps'].values()),'four exact field mapping hypotheses')
 ck(set(p['context'])==set(p['query'])==set(CONTEXT_AXES) and all(p['context'].values()) and all(p['query'].values()),'seven explicit selected context axes')
 for n in ['origin_exercised','other_exercised','independently_owned','materially_distinct','challenge_and_contrary_evidence_reviewed','CAV2_owner_promoted_label','independent_qualification','origin_object_retained']:ck(type(p[n]) is bool,'Boolean hypothesis '+n)
 ck(p['origin_object_retained'] and bool(p['origin_object_ref']),'origin object retained separately')
 ck(not p['implicit_effects'] and p['actual_promotion_or_adoption_verified'] is False and p['source_owner_reviewed'] is False,'no real effect or owner review fabricated')
 if p['independent_qualification']:ck(set(p['support'])==set(baseline()['support']) and all(p['support'].values()),'independent selected origin/exercise/CAV2/fidelity/version/challenge/evidence support')
 pr=p['promotion_decision'];ad=p['adoption_decision'];pv=p['provenance_event']
 ck(set(pv)==set(baseline()['provenance_event']) and all(pv.values()),'exact upstream event/owner-role/principal/version hypotheses')
 if pr is not None:ck(set(pr)=={'event_id','owner_role','candidate','version','declared_effect'} and all(pr.values()) and pr['candidate']==p['context']['candidate'] and pr['version']==p['context']['version'] and pr['declared_effect']=='hyp:CAV2-local-authority-only','selected promotion exact candidate/version/local effect')
 if ad is not None:
  ck(set(ad)=={'event_id','owner_role','principal_ref','candidate','version','domain','support'} and all(ad.values()),'separate adoption event fields and support hypotheses')
  ck(ad['event_id']!=pv['event_id'] and (pr is None or ad['event_id']!=pr['event_id']),'provenance/promotion/adoption event identities distinct')
  ck(ad['owner_role']!=pv['owner_role'],'separate provenance/adoption owner-role hypotheses; principal may be shared')
 origin=p['origin_owner']==p['context']['origin_domain'];cross=p['other_exercised'];formal=bool(origin and p['origin_exercised'] and cross and p['independently_owned'] and p['materially_distinct'] and p['challenge_and_contrary_evidence_reviewed'] and p['CAV2_owner_promoted_label']);prose=bool(origin and p['origin_exercised'] and cross and (p['independently_owned'] or p['materially_distinct']) and p['challenge_and_contrary_evidence_reviewed'] and p['CAV2_owner_promoted_label'])
 different_domain_labels=p['context']['origin_domain']!=p['context']['exercise_domain'];qualified=None if es else bool(formal and different_domain_labels and p['context']==p['query'] and p['independent_qualification'] and pr is not None)
 adopted=None if es else bool(qualified and ad is not None and ad['candidate']==p['query']['candidate'] and ad['version']==p['query']['version'])
 return es,{'printed_formal_AND_requirements_under_hypotheses':formal,'prose_OR_branch_under_hypotheses':prose,'source_precedence_reviewed':False,'origin_and_exercise_domain_labels_differ_under_hypothesis':different_domain_labels,'qualified_CAV2_promotion_under_stronger_hypotheses':qualified,'separate_version_exact_adoption_under_hypotheses':adopted,'actual_promotion_or_adoption_verified':False,'proof_result_or_receipt_self_promotes':False}
def profiles():
 rows=[]
 def add(id,change,bad=False,qualified=False,adopted=False):
  p=baseline();change(p);es,obs=evaluate(p)
  if bool(es)!=bad or obs['qualified_CAV2_promotion_under_stronger_hypotheses']!=(None if bad else qualified) or obs['separate_version_exact_adoption_under_hypotheses']!=(None if bad else adopted):raise ValueError('Unexpected Promotion profile '+id+' '+str((es,obs)))
  rows.append({'case_id':id,'profile':p,'errors':es,'expected_rejection':bad,'expected_qualified':None if bad else qualified,'expected_adopted':None if bad else adopted,'observations':obs,'actual_runtime_execution':False})
 add('evidence-and-complete-names-do-not-self-promote',lambda p:None)
 add('selected-independent-promotion-still-only-hypothesis',supported,qualified=True)
 add('selected-promotion-plus-separate-exact-domain-adoption',lambda p:supported(p) or adopting(p),qualified=True,adopted=True)
 for n in CONTEXT_AXES:add('promotion-does-not-transfer-'+n,lambda p,n=n:supported(p) or p['query'].update({n:'hyp:other-'+n}))
 for n in b.FIELDS:add('missing-'+n+'-field-map',lambda p,n=n:p['field_maps'].update({n:None}),bad=True)
 for n in baseline()['support']:add('selected-promotion-missing-'+n,lambda p,n=n:supported(p) or p['support'].update({n:None}),bad=True)
 for n in ['origin_exercised','other_exercised','independently_owned','materially_distinct','challenge_and_contrary_evidence_reviewed','CAV2_owner_promoted_label']:add('missing-selected-'+n,lambda p,n=n:supported(p) or p.update({n:False}))
 add('wrong-origin-owner',lambda p:supported(p) or p.update(origin_owner='hyp:other-owner'))
 add('same-domain-label-formal-predicates-do-not-prove-domain-disequality',lambda p:supported(p) or p['context'].update(exercise_domain=p['context']['origin_domain']) or p['query'].update(exercise_domain=p['context']['origin_domain']))
 add('same-domain-materially-distinct-context-prose-OR-alternative-unresolved',lambda p:supported(p) or p.update(independently_owned=False) or p['context'].update(exercise_domain=p['context']['origin_domain']) or p['query'].update(exercise_domain=p['context']['origin_domain']))
 add('neither-cross-context-condition',lambda p:supported(p) or p.update(independently_owned=False,materially_distinct=False))
 add('promotion-label-without-exact-decision',lambda p:supported(p) or p.update(promotion_decision=None))
 add('wrong-version-promotion-decision',lambda p:supported(p) or p['promotion_decision'].update(version='hyp:v2'),bad=True)
 add('wrong-candidate-promotion-decision',lambda p:supported(p) or p['promotion_decision'].update(candidate='hyp:other'),bad=True)
 add('promotion-decision-claims-origin-rewrite',lambda p:supported(p) or p['promotion_decision'].update(declared_effect='hyp:rewrite-origin'),bad=True)
 add('promotion-with-adoption-of-another-version',lambda p:supported(p) or adopting(p) or p['adoption_decision'].update(version='hyp:v2'),qualified=True)
 add('promotion-with-adoption-of-another-candidate',lambda p:supported(p) or adopting(p) or p['adoption_decision'].update(candidate='hyp:other'),qualified=True)
 add('adoption-without-CAV2-promotion-stays-unqualified-under-selected-profile',adopting)
 add('one-human-principal-separate-role-and-event-decisions',lambda p:supported(p) or adopting(p),qualified=True,adopted=True)
 add('provenance-and-adoption-same-event',lambda p:supported(p) or adopting(p) or p['adoption_decision'].update(event_id=p['provenance_event']['event_id']),bad=True)
 add('promotion-and-adoption-same-event',lambda p:supported(p) or adopting(p) or p['adoption_decision'].update(event_id=p['promotion_decision']['event_id']),bad=True)
 add('provenance-adoption-owner-role-collapsed',lambda p:supported(p) or adopting(p) or p['adoption_decision'].update(owner_role=p['provenance_event']['owner_role']),bad=True)
 add('origin-object-erased',lambda p:p.update(origin_object_retained=False),bad=True)
 add('missing-stop-rule',lambda p:p['lifecycle_fields'].update(stop_rule=None),bad=True)
 add('missing-one-stage-gate',lambda p:p['lifecycle_fields']['per_stage_gates'].pop(LADDER[0]),bad=True)
 add('missing-stages',lambda p:p['lifecycle_fields'].update(stages=[]),bad=True)
 add('implicit-promotion-or-activation',lambda p:p.update(implicit_effects=['hyp:automatic-domain-activation']),bad=True)
 for n in ['actual_promotion_or_adoption_verified','source_owner_reviewed']:add('actual-claim-not-created-'+n,lambda p,n=n:p.update({n:True}),bad=True)
 return rows

def frames():
 rows=[]
 def base():return {'operation':'stage-candidate','candidate_before':'hyp:c1','candidate_after':'hyp:c1','version':'hyp:v1','origin_object_before':'hyp:origin-object','origin_object_after':'hyp:origin-object','history_retained':True,'stage_before':DOMAIN_PATH[0],'stage_after':DOMAIN_PATH[2],'gate_marker':'hyp:stage-gate','owner_route_marker':'hyp:owner-route','cross_context_marker':None,'challenge_marker':None,'promotion_decision_marker':None,'adoption_decision_marker':None,'adopted_version':None,'independent_grants_before':['hyp:independent-grant'],'independent_grants_after':['hyp:independent-grant'],'permanent_adapter_created':False,'live_coupling_created':False,'actual_transition_verified':False}
 def errors(f):
  es=[]
  def ck(ok,msg):
   if not ok:es.append(msg)
  ck(f['operation'] in ['stage-candidate','exercise','promote-CAV2','adopt-domain','stop','demote','revise-proposal','reject-proposal'],'selected finite operation')
  ck(f['candidate_before']==f['candidate_after'] and f['origin_object_before']==f['origin_object_after'],'candidate/origin object retained')
  ck(f['history_retained'] and bool(f['gate_marker']) and bool(f['owner_route_marker']),'history and selected stage gate/owner route')
  ck(f['stage_before'] in DOMAIN_PATH and f['stage_after'] in DOMAIN_PATH,'selected domain-originated stages')
  if f['operation']=='promote-CAV2':ck(bool(f['cross_context_marker']) and bool(f['challenge_marker']) and bool(f['promotion_decision_marker']),'separate cross-context/challenge/CAV2-decision hypotheses')
  if f['operation']=='adopt-domain':ck(bool(f['promotion_decision_marker']) and bool(f['adoption_decision_marker']) and f['promotion_decision_marker']!=f['adoption_decision_marker'] and f['adopted_version']==f['version'],'separate exact-version adoption decision after selected promotion')
  ck(f['independent_grants_before']==f['independent_grants_after'],'independent grants not implicitly changed')
  ck(f['permanent_adapter_created'] is False and f['live_coupling_created'] is False and f['actual_transition_verified'] is False,'no permanent coupling or actual transition generated')
  return es
 def add(id,change,bad=False):
  f=base();change(f);es=errors(f)
  if bool(es)!=bad:raise ValueError('Unexpected finite Promotion frame '+id)
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'universal_temporal_proof':False,'actual_runtime_execution':False})
 def promote(f):f.update(operation='promote-CAV2',stage_before=DOMAIN_PATH[5],stage_after=DOMAIN_PATH[7],cross_context_marker='hyp:cross-exercise',challenge_marker='hyp:challenge',promotion_decision_marker='hyp:CAV2-promotion')
 def adopt(f):promote(f);f.update(operation='adopt-domain',stage_before=DOMAIN_PATH[7],stage_after=DOMAIN_PATH[8],adoption_decision_marker='hyp:domain-adoption',adopted_version=f['version'])
 add('staged-candidate-no-promotion-effect',lambda f:None)
 add('separate-selected-CAV2-promotion',promote)
 add('separate-selected-domain-adoption',adopt)
 for op in ['exercise','stop','demote','revise-proposal','reject-proposal']:add(op+'-retains-origin-and-history',lambda f,op=op:f.update(operation=op,stage_after=DOMAIN_PATH[1]))
 for n in ['cross_context_marker','challenge_marker','promotion_decision_marker']:add('promotion-missing-'+n,lambda f,n=n:promote(f) or f.update({n:None}),True)
 add('automatic-adoption-without-owner-decision',lambda f:adopt(f) or f.update(adoption_decision_marker=None),True)
 add('adoption-wrong-version',lambda f:adopt(f) or f.update(adopted_version='hyp:v2'),True)
 add('adoption-decision-is-promotion-decision',lambda f:adopt(f) or f.update(adoption_decision_marker=f['promotion_decision_marker']),True)
 for n in ['history_retained','gate_marker','owner_route_marker']:add('missing-'+n,lambda f,n=n:f.update({n:False if n=='history_retained' else None}),True)
 add('failed-exercise-erases-origin',lambda f:f.update(operation='reject-proposal',origin_object_after=None),True)
 add('candidate-identity-overwritten',lambda f:f.update(candidate_after='hyp:c2'),True)
 add('independent-grants-implicitly-changed',lambda f:f.update(independent_grants_after=[]),True)
 for n in ['permanent_adapter_created','live_coupling_created','actual_transition_verified']:add('not-created-'+n,lambda f,n=n:f.update({n:True}),True)
 return rows

def relation_conditions(schema,kind):
 def mentions(x):return isinstance(x,dict) and (x.get('const')==kind or any(mentions(v) for v in x.values())) or isinstance(x,list) and any(mentions(v) for v in x)
 def visit(x):
  if isinstance(x,dict):return ([x] if 'if' in x and mentions(x['if']) else [])+sum([visit(v) for v in x.values()],[])
  if isinstance(x,list):return sum([visit(v) for v in x],[])
  return []
 found=visit(schema)
 if len(found)!=1:raise ValueError('Ambiguous relation condition '+kind)
 return [{'source_kind':x['properties']['source']['properties']['kind']['const'],'target_kind':x['properties']['target']['properties']['kind']['const']} for x in found[0]['then']['properties']['payload']['oneOf']]

RENDERED=['evidence-set','admission-transaction','decision-bundle','decision-checkpoint','decision','policy','authority-boundary']
HISTORIES=['governance-event-history','semantic-event-history']
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings()
 paths={'type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json'}
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];selected={}
 for semantic in RENDERED+HISTORIES+['typed-relation']:
  rows=[x for x in current if x['semantic_kind']==semantic]
  if len(rows)!=1:raise ValueError('Ambiguous current carrier '+semantic)
  row=rows[0];selected[semantic]=row;root=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((root/'artifact.json').read_bytes());paths[semantic+'_descriptor']=root/'artifact.json';paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=root/'fixtures/valid/record.json'
  if semantic in RENDERED:paths[semantic+'_generator']=b.ROOT/artifact['source_direction']['shared_generator_path'];paths[semantic+'_validator']=b.ROOT/artifact['validation_contract']['shared_validator_path'];paths[semantic+'_artifact_projection']=root/'ARTIFACT.md';paths[semantic+'_fixture_projection']=root/'fixtures/valid/RECORD.md'
  if semantic in HISTORIES:paths[semantic+'_generator']=b.ROOT/artifact['source_direction']['generator_path'];paths[semantic+'_artifact_projection']=root/'ARTIFACT.md';paths[semantic+'_fixture_projection']=root/'fixtures/valid/RECORD.md';paths[semantic+'_validator']=root/'validate.py'
  if semantic!='typed-relation':
   for p in sorted((root/'fixtures/invalid').glob('*.json')):paths[semantic+'_negative_'+p.stem]=p
 for row in kr['entries']:paths[row['relation_kind_ref']]=b.ROOT/row['instance_path']
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'};checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 source=load('t.json')['payload']['source'];promotionrows=[x for x in current if x['semantic_kind']=='authority-promotion'];direct=[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']]
 ck('no-dedicated-current-Promotion-type-or-direct-definition-binding',not promotionrows and not direct)
 absent={kind:[x['artifact_type_ref'] for x in current if x['semantic_kind']==kind] for kind in ['authority-promotion','gate','discipline','provenance','evidence','validation','validation-receipt']};ck('seven-selected-semantic-kinds-have-no-current-carrier-row',not any(absent.values()))
 observations=[];negatives=[];probes=[]
 for semantic,row in selected.items():
  artifact=docs[semantic+'_descriptor'];schema=docs[semantic+'_schema'];fixture=docs[semantic+'_fixture'];validator=b.c.Draft202012Validator(schema);b.c.Draft202012Validator.check_schema(schema)
  ck(semantic+'-current-descriptor-and-schema-binding',row['artifact_sha256']==refs[semantic+'_descriptor']['sha256'] and row['schema_sha256']==refs[semantic+'_schema']['sha256'])
  ck(semantic+'-current-valid-fixture',not list(validator.iter_errors(fixture)))
  if semantic in RENDERED:
   mod=types.ModuleType('_bound_'+semantic);exec(compile(raws[semantic+'_generator'],str(paths[semantic+'_generator']),'exec'),mod.__dict__);before=copy.deepcopy([artifact,fixture])
   ck(semantic+'-declared-generator-validator-root-digests',artifact['source_direction']['shared_generator_sha256']==refs[semantic+'_generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs[semantic+'_validator']['sha256'] and artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'])
   ck(semantic+'-two-artifact-renders-exact',mod.render_artifact(artifact).encode()==mod.render_artifact(artifact).encode()==raws[semantic+'_artifact_projection'])
   ck(semantic+'-two-fixture-renders-exact',mod.render_instance(artifact,fixture).encode()==mod.render_instance(artifact,fixture).encode()==raws[semantic+'_fixture_projection'])
   ck(semantic+'-renderer-does-not-mutate',before==[artifact,fixture])
  if semantic in HISTORIES:
   # Execute only the inspected pure render function and the exact artifact-render argument expression; never the package writer.
   tree=ast.parse(raws[semantic+'_generator']);functions=[node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='render_record'];calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='write_text' and isinstance(node.func.value,ast.BinOp) and isinstance(node.func.value.right,ast.Constant) and node.func.value.right.value=='ARTIFACT.md']
   if len(functions)!=1 or len(calls)!=1:raise ValueError('Ambiguous bounded history renderer')
   namespace={'json':json};exec(compile(ast.Module(body=functions,type_ignores=[]),str(paths[semantic+'_generator']),'exec'),namespace);before=copy.deepcopy([artifact,fixture]);expression=compile(ast.Expression(body=calls[0].args[0]),str(paths[semantic+'_generator']),'eval');render=lambda:eval(expression,{'item':artifact,'version':row['artifact_type_ref'].rsplit('/',1)[1]})
   ck(semantic+'-two-extracted-artifact-renders-exact',render().encode()==render().encode()==raws[semantic+'_artifact_projection'])
   ck(semantic+'-two-extracted-record-renders-exact',namespace['render_record'](fixture).encode()==namespace['render_record'](fixture).encode()==raws[semantic+'_fixture_projection'])
   ck(semantic+'-inputs-preserved-and-current-root-binding',before==[artifact,fixture] and artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'])
  if semantic!='typed-relation':
   for name in [n for n in paths if n.startswith(semantic+'_negative_')]:
    errors=list(validator.iter_errors(docs[name]));negatives.append({'semantic_kind':semantic,'path':refs[name]['path'],'schema_rejected':bool(errors),'errors':[x.message for x in errors]})
   for id,change,expected in [('unresolved-owner-and-scope-reference',lambda x:x.update(owner_ref='absent:Owner',scope_ref='absent:Scope'),True),('grant-authority-effect',lambda x:x.update(authority_effect='grant'),False),('Promotion-kind-cannot-replace-related-kind',lambda x:x.update(kind='authority-promotion'),False)]:
    candidate=copy.deepcopy(fixture);change(candidate);errors=list(validator.iter_errors(candidate));accepted=not errors
    if accepted!=expected:raise ValueError('Unexpected Promotion related carrier probe '+semantic+' '+id)
    probes.append({'semantic_kind':semantic,'case_id':id,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in errors],'actual_reference_resolution_or_promotion_verified':False})
  observations.append({'semantic_kind':semantic,'artifact_type_ref':row['artifact_type_ref'],'declared_validator_executed':False,'fixture_shape_valid':True,'Promotion_lifecycle_or_event_alignment_established':False,'actual_owner_authentication_promotion_or_adoption_verified':False})
 ck('all-related-negative-fixtures-rejected',bool(negatives) and all(x['schema_rejected'] for x in negatives))
 endpoints=[]
 for row in kr['entries']:
  id=row['relation_kind_ref'];p=docs[id]['payload'];ck('current-Kind-'+id,row['lifecycle_state']=='admitted-current' and row['instance_sha256']==refs[id]['sha256'] and row['exact_endpoint_pair_count']==len(p['allowed_endpoint_pairs']) and row['required_qualifier_axes']==p['qualifier_contract']['required_axes']);endpoints += [{'relation_kind_ref':id,'pair':pair} for pair in p['allowed_endpoint_pairs'] if 'authority-promotion' in pair.values()]
 ck('no-Promotion-endpoint-in-all-current-Kinds',len(kr['entries'])==41 and not endpoints)
 gaps=[];pair_observations=[];tv=b.c.Draft202012Validator(docs['typed-relation_schema'])
 for id in ['relation.governed-by','relation.scopes-authority-over','relation.originates-from','relation.successor-of']:
  p=docs[id]['payload'];pairs=relation_conditions(docs['typed-relation_schema'],id);gaps.append({'relation_kind_ref':id,'current_Kind_pairs':len(p['allowed_endpoint_pairs']),'current_TR_schema_pairs':len(pairs),'missing_TR_pairs':[x for x in p['allowed_endpoint_pairs'] if x not in pairs],'extra_TR_pairs':[x for x in pairs if x not in p['allowed_endpoint_pairs']],'meaning_alignment_reviewed':False})
  testpairs=p['allowed_endpoint_pairs'] if id!='relation.successor-of' else [x for x in p['allowed_endpoint_pairs'] if x['source_kind'] in HISTORIES]
  for pair in testpairs:
   candidate=copy.deepcopy(docs['typed-relation_fixture']);candidate['payload'].update(relation_kind_ref=id,source={'kind':pair['source_kind'],'ref':'Source:hyp','version_ref':'Source@hyp'},target={'kind':pair['target_kind'],'ref':'Target:hyp','version_ref':'Target@hyp'},qualifiers={n:'hyp:qualifier' for n in p['qualifier_contract']['required_axes']});errors=list(tv.iter_errors(candidate));accepted=not errors
   if accepted!=(pair in pairs):raise ValueError('Current Kind/TR pair differs')
   pair_observations.append({'relation_kind_ref':id,'pair':pair,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in errors],'actual_relation_or_authority_created':False})
 ck('governed-by-six-current-gaps',gaps[0]['current_Kind_pairs']==29 and gaps[0]['current_TR_schema_pairs']==23 and gaps[0]['missing_TR_pairs']==[{'source_kind':n,'target_kind':'policy'} for n in ['admission-transaction','authority-boundary','decision-bundle','decision-checkpoint','user-decision-preference','workflow-decision-profile']] and not gaps[0]['extra_TR_pairs'])
 ck('scope-Boundary-to-DecisionScope-gap',gaps[1]['current_Kind_pairs']==3 and gaps[1]['current_TR_schema_pairs']==2 and gaps[1]['missing_TR_pairs']==[{'source_kind':'authority-boundary','target_kind':'decision-scope'}] and not gaps[1]['extra_TR_pairs'])
 ck('origin-lineage-does-not-transfer-authority',docs['relation.originates-from']['payload']['forbidden_inferences']==['derivation','successor','authority-transfer'])
 ck('succession-does-not-automatically-transfer-authority-or-identity',docs['relation.successor-of']['payload']['forbidden_inferences']==['automatic-supersession','identity-equality','authority-transfer'])
 history_probes=[]
 for semantic in HISTORIES:
  schema=docs[semantic+'_schema'];fixture=docs[semantic+'_fixture'];validator=b.c.Draft202012Validator(schema);cursor='cursor' if semantic=='semantic-event-history' else 'governance_cursor';latest='latest_cursor' if semantic=='semantic-event-history' else 'latest_governance_cursor'
  cases=[('duplicate-event-shape-does-not-validate-replay',lambda x:x['payload']['events'].append(copy.deepcopy(x['payload']['events'][0])),True),('arbitrary-well-shaped-chain-digest',lambda x:x['payload'].update(chain_digest='0'*64),True),('latest-cursor-does-not-prove-consistent-event-index',lambda x:x['payload'].update({latest:9999}),True),('unresolved-event-record-reference',lambda x:x['payload']['events'][0].update(record_ref='absent:EventRecord'),True),('append-only-false-rejected',lambda x:x['payload'].update(append_only=False),False)]
  if semantic=='governance-event-history':cases.append(('semantic-patch-forbidden-false-rejected',lambda x:x['payload'].update(semantic_patch_forbidden=False),False))
  for id,change,expected in cases:
   candidate=copy.deepcopy(fixture);change(candidate);es=list(validator.iter_errors(candidate));accepted=not es
   if accepted!=expected:raise ValueError('Unexpected history shape probe '+semantic+' '+id)
   history_probes.append({'semantic_kind':semantic,'case_id':id,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_replay_or_owner_authentication_verified':False})
 se=docs['semantic-event-history_fixture']['payload']['events'][0];ge=docs['governance-event-history_fixture']['payload']['events'][0]['semantic_event_ref'];joins={'semantic_event_id_literal_matches':se['event_id']==ge['semantic_event_id'],'semantic_event_digest_literal_matches':se['event_digest']==ge['semantic_event_digest'],'semantic_cursor_literal_matches':se['cursor']==ge['semantic_cursor'],'actual_event_records_or_chain_replay_verified':False,'exact_Promotion_provenance_and_adoption_owner_map_verified':False};ck('three-history-literal-joins-not-replay-or-adoption',all(joins[n] is True for n in ['semantic_event_id_literal_matches','semantic_event_digest_literal_matches','semantic_cursor_literal_matches']) and joins['actual_event_records_or_chain_replay_verified'] is False)
 source_doc=b.co.source_document(snap,source);formal=source_doc['voices']['scientific_formal']['formal_expression'];normative=source_doc['voices']['scientific_formal']['normative_statement'];policy=(b.UNIT/'legacy-promotion-policy-context.md').read_text();model=(b.UNIT/'legacy-model-context.md').read_text()
 ck('actual-source-prose-OR-versus-printed-formal-AND-retained', 'another independently owned domain or materially distinct context' in normative and 'exists d1: independently_owned(d1)\n                 and materially_distinct(d1, d0)' in formal)
 ck('contextual-policy-retains-domain-branch-and-separate-adoption','## Domain-Originated Generalization' in policy and 'CAV2 promotion does not adopt' in policy and 'separate adoption by each domain' in policy)
 ck('contextual-policy-gate-vocabulary-and-open-extraction-question','## Pass, Flag, Block' in policy and 'Status: OPEN.' in policy and 'candidate local policy' in policy)
 ck('contextual-Model-review-mode-enforcement-not-scan','review-mode' in model and 'kind-enumeration scan is pending' in model and load('source-checks.json')['contextual_document_admitted_into_primary_theory'] is False and load('source-checks.json')['contextual_policy_admitted_into_primary_theory'] is False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 ps=profiles();fs=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=load('../cal.definition.authority-model/delivery-manifest.json');b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-AuthorityPromotion-profile/v1-candidate','status':'PASS-for-explicit-Promotion-adoption-hypotheses-and-bounded-current-catalog-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json','legacy-model-context.md','legacy-promotion-policy-context.md']],'selected_inputs':refs,'profile_control_count':len(ps),'rejected_profile_controls':sum(x['expected_rejection'] for x in ps),'profiles':ps,'finite_history_frame_count':len(fs),'rejected_history_frames':sum(x['expected_rejection'] for x in fs),'finite_history_frames':fs,'actual_check_count':len(checks),'actual_checks':checks,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'current_Kind_rows':len(kr['entries']),'current_Promotion_carrier_selection':{'semantic_kind_rows':promotionrows,'direct_definition_binding_types':direct,'dedicated_Promotion_carrier_established':False,'scope':'selected admitted-current Type registry only'},'selected_semantic_kind_absences':absent,'Promotion_endpoint_roles':endpoints,'related_carrier_observations':observations,'negative_fixture_checks':negatives,'actual_related_schema_probes':probes,'history_schema_probes':history_probes,'history_literal_join_observations':joins,'Kind_TR_schema_gaps':gaps,'all_selected_current_Kind_TR_pair_observations':pair_observations,'source_precedence_conflict':{'printed_formula_requires':'independently-owned AND materially-distinct second exercised domain','normative_branch_allows':'independently-owned domain OR materially-distinct context','reviewed':False},'contextual_table_selection':{'generic_ladder':LADDER,'domain_originated_path':DOMAIN_PATH,'whole_referenced_documents_admitted_into_primary_theory':False,'deterministic_kind_scan_executed':False,'complete_per_kind_instances_and_ladders_aligned':False},'source_mapping_gaps':{'exact_tuple_stage_stop_demote_and_per_kind_maps_reviewed':False,'independence_material_distinction_origin_ownership_and_version_identity_reviewed':False,'real_Promotion_provenance_adoption_owner_and_causal_alignment_established':False,'universal_temporal_noncollapse_and_carrier_conformance_established':False},'new_authorities_or_relations_created':0,'actual_promotion_or_adoption_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Explicit hypothetical lifecycle/generalization/independent owner/version-exact adoption and selected finite frames. Actual bounded source/current-carrier schema, generator and Kind/TR observations; pure history render AST slices only, package writers/validators not executed. Literal event joins and shape acceptance do not prove chain replay, real owner decisions or promotion/adoption. Legacy full Model/policy remain contextual; prose OR/formal AND unresolved. No actual authority effect or whole-source/universal proof.'}
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh Promotion profile differs')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({k:r[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','current_type_registry_rows','admitted_current_type_rows','current_Kind_rows','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
