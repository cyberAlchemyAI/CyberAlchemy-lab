"""Explicit Context anchor/view hypotheses and bounded current carrier observations."""
import ast,copy,json,types
import build_candidate as b
import verifier as v
AXES=['context','revision','kind','product','project','goal','purpose','owner','subject_scope','consumer','source_policy','bounded_context','source_epoch','request','resolver','view']
SUPPORT=['identity','source_precedence','field_map','anchor_role_resolution','goal_project_membership','owner_qualification','consumer_use','DDD_boundary','source_policy_epoch','resolver_contract']
def load(n):return json.loads((b.UNIT/n).read_bytes())
def raw_profile():
 context={n:'hyp:'+n for n in AXES};context.update(kind='project',goal=None)
 return {'qualified':False,'context':context,'query':copy.deepcopy(context),'support':{n:None for n in SUPPORT},'product_refs':['hyp:p'],'project_refs':['hyp:j'],'goal_refs':[],'consumer_refs':['hyp:u'],'bounded_context_refs':[],'goal_belongs_to_project':False,'context_current':False,'view_current':True,'actual_instance_or_resolver_admitted':False,'actual_reference_resolution_verified':False,'actual_consumer_understood_or_used':False,'actual_authority_or_runtime_verified':False}
def assess(p):
 errors=[];kind=p['context']['kind'];projects=p['project_refs'];goals=p['goal_refs']
 if len(p['product_refs'])!=1 or len(projects)>1 or len(goals)>1 or not p['consumer_refs']:errors.append('anchor-or-consumer-cardinality')
 if kind not in ['product','project','goal'] or kind=='product' and (projects or goals) or kind=='project' and (len(projects)!=1 or goals) or kind=='goal' and (len(projects)!=1 or len(goals)!=1 or not p['goal_belongs_to_project']):errors.append('kind-anchor-or-goal-membership')
 if any(p[n] for n in ['actual_instance_or_resolver_admitted','actual_reference_resolution_verified','actual_consumer_understood_or_used','actual_authority_or_runtime_verified']):errors.append('actual-world-claim-not-supported')
 if p['qualified']:
  for n in SUPPORT:
   if not p['support'][n]:errors.append('missing-support:'+n)
 allowed=p['qualified'] and all(p['support'].values()) and p['context']==p['query'] and p['context_current'] and p['view_current'] and not errors
 return errors,{'consumer_use_allowed_under_hypotheses':bool(allowed),'actual_consumer_use_or_resolution_verified':False,'source_fidelity_accepted':False}
def profiles():
 rows=[]
 def add(id,change,reject=False,use=False):
  p=raw_profile();change(p);errors,observations=assess(p)
  if bool(errors)!=reject or observations['consumer_use_allowed_under_hypotheses']!=use:raise ValueError('Wrong authored profile '+id)
  rows.append({'case_id':id,'profile':p,'errors':errors,'observations':observations,'expected_rejection':reject,'expected_use':use,'actual_runtime_execution':False})
 def qualify(p):p.update(qualified=True,context_current=True,support={n:'hyp:support:'+n for n in SUPPORT})
 add('current-view-without-current-qualified-context',lambda p:None)
 add('qualified-project-context-and-exact-view-hypotheses',qualify,use=True)
 for n in SUPPORT:
  def missing(p,n=n):qualify(p);p['support'][n]=None
  add('missing-'+n,missing,True)
 for n in AXES:
  def mismatch(p,n=n):qualify(p);p['query'][n]='hyp:other'
  add('query-context-mismatch-'+n,mismatch)
 for id,change in [('no-product',lambda p:p.update(product_refs=[])),('two-products',lambda p:p.update(product_refs=['hyp:p1','hyp:p2'])),('two-projects',lambda p:p.update(project_refs=['hyp:j1','hyp:j2'])),('two-goals',lambda p:p.update(goal_refs=['hyp:g1','hyp:g2'])),('no-consumer',lambda p:p.update(consumer_refs=[])),('project-without-project',lambda p:p.update(project_refs=[])),('project-with-goal',lambda p:p.update(goal_refs=['hyp:g'])),('unknown-kind',lambda p:p['context'].update(kind='composite'))]:add(id,change,True)
 def product(p):qualify(p);p['context']['kind']=p['query']['kind']='product';p['context']['project']=p['query']['project']=None;p['project_refs']=[]
 def goal(p):qualify(p);p['context']['kind']=p['query']['kind']='goal';p['context']['goal']=p['query']['goal']='hyp:g';p.update(goal_refs=['hyp:g'],goal_belongs_to_project=True)
 add('qualified-product-kind',product,use=True);add('qualified-goal-kind',goal,use=True)
 def no_project(p):goal(p);p['project_refs']=[]
 def no_membership(p):goal(p);p['goal_belongs_to_project']=False
 add('goal-without-project-source-rule',no_project,True);add('goal-without-selected-project-membership',no_membership,True)
 for n in ['context_current','view_current']:
  def stale(p,n=n):qualify(p);p[n]=False
  add('not-current-'+n,stale)
 for n in ['actual_instance_or_resolver_admitted','actual_reference_resolution_verified','actual_consumer_understood_or_used','actual_authority_or_runtime_verified']:add('unsupported-'+n,lambda p,n=n:p.update(**{n:True}),True)
 return rows
def frames():
 rows=[]
 def add(id,change=lambda f:None,reject=False):
  anchors={'product':'hyp:p','project':'hyp:j','goal':None,'purpose':'hyp:purpose'};f={'operation':'refresh','anchors_before':anchors,'anchors_after':copy.deepcopy(anchors),'context_before':'hyp:c1','context_after':'hyp:c1','source_epoch_before':'hyp:e1','source_epoch_after':'hyp:e1','request_before':'hyp:r1','request_after':'hyp:r1','view_before':'hyp:v1','view_after':'hyp:v1','view_epoch_after':'hyp:e1','view_request_after':'hyp:r1','owner_qualified':True,'old_context_retained':True,'old_lifecycle_after':'active','successor_recorded':False,'actual_transition_verified':False};change(f);errors=[];material=f['anchors_before']!=f['anchors_after']
  if not f['owner_qualified'] or f['actual_transition_verified']:errors.append('owner-or-actual-claim')
  if material and (f['context_before']==f['context_after'] or not f['successor_recorded'] or f['old_lifecycle_after']!='superseded' or not f['old_context_retained']):errors.append('material-change-needs-successor-supersession-history')
  if not material and f['context_before']!=f['context_after']:errors.append('preserving-refresh-changed-identity')
  if f['view_epoch_after']!=f['source_epoch_after'] or f['view_request_after']!=f['request_after']:errors.append('stale-or-misbound-view')
  if (f['source_epoch_before']!=f['source_epoch_after'] or f['request_before']!=f['request_after']) and f['view_before']==f['view_after']:errors.append('old-immutable-view-reused')
  if bool(errors)!=reject:raise ValueError('Wrong authored frame '+id)
  rows.append({'case_id':id,'frame':f,'errors':errors,'expected_rejection':reject,'actual_runtime_execution':False,'universal_temporal_proof':False})
 for op in ['refresh','interface','pause','resume']:add('preserving-'+op,lambda f,op=op:f.update(operation=op))
 add('source-epoch-refresh-new-view-same-context',lambda f:f.update(source_epoch_after='hyp:e2',view_after='hyp:v2',view_epoch_after='hyp:e2'))
 add('new-request-new-view-same-context',lambda f:f.update(request_after='hyp:r2',view_after='hyp:v2',view_request_after='hyp:r2'))
 add('stale-view-on-new-source-epoch',lambda f:f.update(source_epoch_after='hyp:e2'),True)
 add('stale-view-on-new-request',lambda f:f.update(request_after='hyp:r2'),True)
 add('preserved-anchors-changed-context-id',lambda f:f.update(context_after='hyp:c2'),True)
 for n in ['product','project','goal','purpose']:
  def material(f,n=n):f['anchors_after'][n]='hyp:other';f.update(context_after='hyp:c2',old_lifecycle_after='superseded',successor_recorded=True)
  add('qualified-material-'+n,material)
  add('material-'+n+'-silent-same-identity',lambda f,n=n:f['anchors_after'].update(**{n:'hyp:other'}),True)
 def dropped(f):f['anchors_after']['purpose']='hyp:other';f.update(context_after='hyp:c2',old_lifecycle_after='superseded',successor_recorded=True,old_context_retained=False)
 add('material-change-erases-old-context',dropped,True)
 add('owner-unqualified-refresh',lambda f:f.update(owner_qualified=False),True)
 add('actual-runtime-transition-claim',lambda f:f.update(actual_transition_verified=True),True)
 return rows
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings();registry_path=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';reg=json.loads(registry_path.read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];source=load('t.json')['payload']['source'];direct=[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']];paths={'registry':registry_path};selected={};checks=[]
 def ck(id,value):checks.append({'check_id':id,'result':bool(value)})
 ck('one-current-direct-Context-binding',direct==['cal.artifact-type.context/v1'])
 for semantic in ['context','context-request','context-view','bounded-context','definition']:
  rows=[x for x in current if x['semantic_kind']==semantic]
  if len(rows)!=1:raise ValueError('Ambiguous related carrier '+semantic)
  row=rows[0];selected[semantic]=row;folder=(b.ROOT/row['artifact_path']).parent;descriptor=json.loads((folder/'artifact.json').read_bytes());paths[semantic+'_descriptor']=folder/'artifact.json';paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=folder/descriptor['validation_contract']['positive_witness']
  if semantic=='context':
   for n,relative in [('generator',descriptor['source_direction']['shared_generator_path']),('validator',descriptor['validation_contract']['shared_validator_path']),('root_descriptor',descriptor['artifact_type_root_binding']['path'])]:paths[n]=b.ROOT/relative
   paths['artifact_projection']=folder/'ARTIFACT.md';paths['fixture_projection']=folder/descriptor['validation_contract']['positive_projection']
   for rel in descriptor['validation_contract']['negative_witnesses']:paths['negative_'+b.Path(rel).stem]=folder/rel
 refs={n:b.ref(q) for n,q in paths.items()};raws={n:q.read_bytes() for n,q in paths.items()};docs={n:json.loads(raws[n]) for n,q in paths.items() if q.suffix=='.json'};observations=[];unknown=[]
 for semantic,row in selected.items():
  validator=b.c.Draft202012Validator(docs[semantic+'_schema']);b.c.Draft202012Validator.check_schema(docs[semantic+'_schema']);fixture=docs[semantic+'_fixture'];ck(semantic+'-exact-descriptor-schema',row['artifact_sha256']==refs[semantic+'_descriptor']['sha256'] and row['schema_sha256']==refs[semantic+'_schema']['sha256']);ck(semantic+'-positive-fixture',not list(validator.iter_errors(fixture)));observations.append({'semantic_kind':semantic,'artifact_type_ref':row['artifact_type_ref'],'fixture_shape_valid':True,'whole_Context_alignment_verified':False,'declared_validator_executed':False});x=copy.deepcopy(fixture);x.update(owner_ref='absent:owner',scope_ref='absent:scope');errors=list(validator.iter_errors(x));unknown.append({'semantic_kind':semantic,'record':x,'schema_accepted':not errors,'errors':[e.message for e in errors],'actual_reference_or_owner_resolution_verified':False})
 artifact=docs['context_descriptor'];schema=docs['context_schema'];fixture=docs['context_fixture'];sv=b.c.Draft202012Validator(schema);binding=artifact['semantic_definition_bindings'];ck('dedicated-context-binding-exact-source',len(binding)==1 and binding[0]['definition_ref']==source['version_ref'] and all(binding[0][k]==source[k] for k in ['path','sha256']))
 hostiles=[]
 for n in paths:
  if n.startswith('negative_'):
   errors=list(sv.iter_errors(docs[n]));hostiles.append({'path':refs[n]['path'],'schema_rejected':bool(errors),'errors':[e.message for e in errors]})
 ck('four-context-hostiles-reject',len(hostiles)==4 and all(x['schema_rejected'] for x in hostiles))
 module=types.ModuleType('_pure_Context_generator');exec(compile(raws['generator'],str(paths['generator']),'exec'),module.__dict__);before=copy.deepcopy([artifact,fixture]);ck('generator-validator-root-digests',artifact['source_direction']['shared_generator_sha256']==refs['generator']['sha256'] and artifact['validation_contract']['shared_validator_sha256']==refs['validator']['sha256'] and artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256']);ck('two-exact-artifact-renders',module.render_artifact(artifact).encode()==module.render_artifact(artifact).encode()==raws['artifact_projection']);ck('two-exact-fixture-renders',module.render_instance(artifact,fixture).encode()==module.render_instance(artifact,fixture).encode()==raws['fixture_projection']);ck('render-inputs-preserved',before==[artifact,fixture])
 probes=[]
 def probe(id,change,expected):
  x=copy.deepcopy(fixture);change(x);errors=list(sv.iter_errors(x));accepted=not errors
  if accepted!=expected:raise ValueError('Unexpected Context schema probe '+id)
  probes.append({'case_id':id,'record':x,'schema_accepted':accepted,'errors':[e.message for e in errors],'actual_anchor_resolution_successor_or_source_fidelity_verified':False})
 probe('goal-kind-null-project-shape-gap',lambda x:x.update(context_kind='goal',goal_ref='absent:goal',project_ref=None),True)
 probe('goal-kind-unresolved-nonnull-parent-and-goal',lambda x:x.update(context_kind='goal',goal_ref='absent:goal',project_ref='absent:project'),True)
 probe('goal-kind-null-goal-rejects',lambda x:x.update(context_kind='goal',goal_ref=None),False)
 probe('product-kind-project-present-rejects',lambda x:x.update(context_kind='product'),False)
 probe('product-kind-no-project-no-goal-accepts',lambda x:x.update(context_kind='product',project_ref=None,goal_ref=None),True)
 probe('project-kind-null-project-rejects',lambda x:x.update(project_ref=None),False)
 probe('project-kind-goal-present-rejects',lambda x:x.update(goal_ref='absent:goal'),False)
 probe('unknown-kind-rejects',lambda x:x.update(context_kind='composite'),False)
 probe('whitespace-product-ref-rejects',lambda x:x.update(product_ref='   '),False)
 probe('unresolved-product-owner-route-accepts',lambda x:x.update(product_ref='absent:product',owner_ref='absent:owner',owner_route='absent:route'),True)
 probe('empty-consumers-rejects',lambda x:x.update(consumer_refs=[]),False)
 probe('empty-DDD-refs-accepts',lambda x:x.update(bounded_context_refs=[]),True)
 probe('101-DDD-refs-rejects-unmentioned-source-upper-bound',lambda x:x.update(bounded_context_refs=['absent:ddd:'+str(i) for i in range(101)]),False)
 probe('101-consumers-rejects-unmentioned-source-upper-bound',lambda x:x.update(consumer_refs=['absent:consumer:'+str(i) for i in range(101)]),False)
 probe('unresolved-consumer-accepts',lambda x:x.update(consumer_refs=['absent:consumer']),True)
 probe('empty-source-policy-list-rejects',lambda x:x.update(source_policy_refs=[]),False)
 probe('superseded-without-successor-ref-rejects',lambda x:x.update(lifecycle_state='superseded'),False)
 probe('superseded-with-unresolved-successor-ref-accepts',lambda x:x.update(lifecycle_state='superseded',successor_refs=['absent:successor']),True)
 probe('same-id-changed-purpose-no-lineage-required-by-shape',lambda x:x.update(purpose='Different work purpose'),True)
 probe('same-id-changed-product-no-lineage-required-by-shape',lambda x:x.update(product_ref='absent:other-product'),True)
 probe('unknown-lifecycle-rejects',lambda x:x.update(lifecycle_state='promoted'),False)
 probe('literal-status-admitted-rejects',lambda x:x.update(status='admitted'),False)
 for state in ['draft','active','retired']:probe('lifecycle-'+state+'-does-not-prove-activation',lambda x,state=state:x.update(lifecycle_state=state),True)
 ck('goal-null-project-schema-gap-retained',probes[0]['schema_accepted'] is True)
 ck('source-tuple-current-root-field-shape-observed','payload' not in schema['properties'] and all(n in schema['properties'] for n in ['context_kind','product_ref','project_ref','goal_ref','purpose','consumer_refs','bounded_context_refs','revision_history','successor_refs']))
 validator_tree=ast.parse(raws['validator']);functions=[n for n in validator_tree.body if isinstance(n,ast.FunctionDef) and n.name=='validate_package'];ck('bound-validator-body-observed-schema-package-not-context-owner-or-parent-resolution',len(functions)==1 and 'Draft202012Validator' in ast.unparse(functions[0]) and not any(token in ast.unparse(functions[0]) for token in ['belongs_to','context_kind','goal_ref','project_ref']))
 current_def=b.c.Draft202012Validator(docs['definition_schema']);source_doc=json.loads((b.ROOT/source['path']).read_bytes());errors=list(current_def.iter_errors(source_doc));shape={'source_schema_version':source_doc['schema_version'],'selected_current_definition_type':selected['definition']['artifact_type_ref'],'current_schema_accepted':not errors,'errors':[{'path':'/'+'/'.join(map(str,e.path)),'message':e.message} for e in errors],'instance_migrated':False,'exact_source_admission_invalidated':False};ck('historical-source-current-Definition-v2-four-errors',bool(errors) and {x['path'] for x in shape['errors']}=={'/classification/artifact_type_ref','/schema_ref','/schema_version','/source_direction/generator_ref'})
 comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs']);ck('same-source-siblings-remain-distinct',{'cal.definition.context-request','cal.definition.context-view'}<={x['definition_id'] for x in comparison['separate_qualified_sources']} and comparison['comparison_assembled_into_primary_T'] is False)
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 ps=profiles();fs=frames();bindings=[b.ref(q) for q in [b.UNIT/'verify_authority_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=load('../cal.definition.contestability-policy/delivery-manifest.json');b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-Context-profile/v1-candidate','status':'PASS-for-hypothetical-qualified-Context-view-use-and-bounded-current-carrier-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json','legacy-source-section.md']],'selected_inputs':refs,'profile_control_count':len(ps),'rejected_profile_controls':sum(x['expected_rejection'] for x in ps),'profiles':ps,'finite_history_frame_count':len(fs),'rejected_history_frames':sum(x['expected_rejection'] for x in fs),'finite_history_frames':fs,'actual_check_count':len(checks),'actual_checks':checks,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'dedicated_current_carrier_selection':{'direct_definition_binding_types':direct,'dedicated_current_carrier_established':True,'exact_definition_binding':binding[0]},'related_carrier_observations':observations,'negative_fixture_checks':hostiles,'related_unknown_reference_probes':unknown,'Context_schema_probes':probes,'root_field_mapping_observations':{'source_tuple_fields':b.FIELDS,'carrier_required_fields':schema['required'],'possible_locators_not_accepted_maps':{'id':'node_id','kind':'context_kind','owner_route':'owner_route',**{n:n for n in b.FIELDS if n not in ['id','kind','owner_route']}},'whole_field_reference_identity_and_normative_change_map_accepted':False,'additional_bounded_ref_and_consumer_maximum':100,'goal_nonnull_project_requirement_in_schema_established':False,'bound_validator_executed':False,'package_validator_static_source_inspected':True},'historical_source_current_definition_shape':shape,'profile_context_axes':AXES,'profile_support_axes':SUPPORT,'actual_instance_resolver_reference_consumer_or_temporal_effect_created':False,'new_authorities_or_relations_created':0,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'claim_ceiling':'Static source/kind/cardinality and hypothetical exact Context/View frames with selected current direct carrier observations. Goal-null-project schema gap,unresolved references,same-ID changed anchors and101-item caps retained. Bound package-validator source inspected but not executed. No source-owner/field/resolver/trace fidelity,actual reference resolution,consumer understanding or temporal/runtime effect proof.'}
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh profile differs')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({k:x[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
