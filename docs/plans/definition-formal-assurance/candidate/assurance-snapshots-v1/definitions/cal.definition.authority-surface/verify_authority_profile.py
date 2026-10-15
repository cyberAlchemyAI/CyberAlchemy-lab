"""Hypothetical Surface permission/citation frames and exact current carrier observations."""
import copy,json,types
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
AXES=['surface','source_version','project','specific_scope','owner_role','purpose']
PURPOSES=['normative-meaning','structural-rule','promotion-decision','contract']
SUPPORT=['owner_authentication','role_and_membership','boundary','policy','current_version','source_fidelity','responsible_owner_decision']
def baseline():
 context=dict(zip(AXES,['hyp:surface','hyp:v1','hyp:project','hyp:scope','hyp:owner-role',PURPOSES[0]]))
 return {'context':context,'query':copy.deepcopy(context),'project_local':True,'declared_purposes':PURPOSES.copy(),'qualified_purposes':[],'independent_qualification':False,'support':dict.fromkeys(SUPPORT),'blocked':False,'citation':{'evidence':'hyp:e1','scope':'hyp:scope','cited':True},'promotion':None,'actually_verified':False,'source_owner_accepted':False,'implicit_effects':[]}
def supported(p):p.update(qualified_purposes=[p['context']['purpose']],independent_qualification=True,support={n:'hyp:separate-'+n for n in SUPPORT})
def promoted(p):p.update(promotion={'evidence':p['citation']['evidence'],'scope':p['citation']['scope'],'version':'hyp:evidence-v1','owner_role':'hyp:responsible-evidence-owner','decision':'hyp:separate-promotion-decision','qualified':True})
def evaluate(p):
 es=[]
 def ck(ok,msg):
  if not ok:es.append(msg)
 ck(set(p)==set(baseline()),'closed selected hypothetical profile')
 ck(set(p['context'])==set(p['query'])==set(AXES) and all(p['context'].values()) and all(p['query'].values()),'six explicit context axes')
 ck(p['context']['purpose'] in PURPOSES,'selected defining purpose')
 ck(set(p['support'])==set(SUPPORT),'seven support axes')
 for n in ['project_local','independent_qualification','blocked','actually_verified','source_owner_accepted']:ck(type(p[n]) is bool,'Boolean '+n)
 ck(isinstance(p['declared_purposes'],list) and isinstance(p['qualified_purposes'],list) and all(n in PURPOSES for n in p['qualified_purposes']) and len(p['qualified_purposes'])==len(set(p['qualified_purposes'])),'selected qualified purpose vocabulary and uniqueness')
 if p['independent_qualification']:ck(all(p['support'].values()),'separately supplied authentication/role/boundary/policy/version/fidelity/decision hypotheses')
 ck(set(p['citation'])=={'evidence','scope','cited'} and bool(p['citation']['evidence']) and bool(p['citation']['scope']) and type(p['citation']['cited']) is bool,'citation axes')
 pr=p['promotion']
 if pr is not None:ck(set(pr)=={'evidence','scope','version','owner_role','decision','qualified'} and all(pr.values()) and pr['qualified'] is True,'separate responsible owner/exact evidence version/scope/decision hypotheses')
 ck(p['actually_verified'] is False and p['source_owner_accepted'] is False and not p['implicit_effects'],'no actual grant/rewrite/promotion or owner acceptance fabricated')
 permitted=None if es else bool(p['project_local'] and p['context']==p['query'] and p['context']['purpose'] in p['qualified_purposes'] and p['independent_qualification'] and not p['blocked'])
 evidence=None if es else bool(pr is not None and pr['evidence']==p['citation']['evidence'] and pr['scope']==p['query']['specific_scope'] and pr['qualified'])
 return es,{'qualified_defining_permission_under_stronger_hypotheses':permitted,'separate_evidence_promotion_under_stronger_hypotheses':evidence,'citation_alone_supplies_authority':False,'actual_permission_or_promotion_verified':False,'source_fidelity_accepted':False}
def profiles():
 rows=[]
 def add(id,change,bad=False,permission=False,evidence=False):
  p=baseline();change(p);es,obs=evaluate(p)
  if bool(es)!=bad or obs['qualified_defining_permission_under_stronger_hypotheses']!=(None if bad else permission) or obs['separate_evidence_promotion_under_stronger_hypotheses']!=(None if bad else evidence):raise ValueError('Unexpected profile '+id+' '+str((es,obs)))
  rows.append({'case_id':id,'profile':p,'errors':es,'expected_rejection':bad,'expected_permission':None if bad else permission,'expected_evidence_promotion':None if bad else evidence,'observations':obs,'actual_runtime_execution':False})
 add('complete-declared-fields-and-citation-no-grant',lambda p:None)
 add('independent-selected-permission-hypotheses',supported,permission=True)
 add('separate-owner-promotion-hypotheses',promoted,evidence=True)
 add('separate-permission-and-evidence-promotion',lambda p:supported(p) or promoted(p),permission=True,evidence=True)
 for purpose in PURPOSES:add('one-purpose-is-enough-'+purpose,lambda p,purpose=purpose:p['context'].update(purpose=purpose) or p['query'].update(purpose=purpose) or supported(p),permission=True)
 add('all-four-qualified-also-allowed',lambda p:supported(p) or p.update(qualified_purposes=PURPOSES.copy()),permission=True)
 for n in AXES:add('permission-does-not-transfer-'+n,lambda p,n=n:supported(p) or p['query'].update({n:'hyp:other-'+n}))
 for n in SUPPORT:add('selected-qualification-missing-'+n,lambda p,n=n:supported(p) or p['support'].update({n:None}),bad=True)
 add('owner-markers-without-independent-qualification',lambda p:supported(p) or p.update(independent_qualification=False))
 add('no-selected-qualified-purpose',lambda p:supported(p) or p.update(qualified_purposes=[]))
 add('locality-missing',lambda p:supported(p) or p.update(project_local=False))
 add('explicit-block-overrides-selected-qualification',lambda p:supported(p) or p.update(blocked=True))
 add('raw-declared-purposes-not-needed-once-independent-purpose-supplied',lambda p:supported(p) or p.update(declared_purposes=[]),permission=True)
 add('no-actual-citation-does-not-revoke-separate-permission',lambda p:supported(p) or p['citation'].update(cited=False),permission=True)
 add('promotion-in-other-scope-no-citation-transfer',lambda p:promoted(p) or p['promotion'].update(scope='hyp:other-scope'))
 add('promotion-of-other-evidence-no-citation-transfer',lambda p:promoted(p) or p['promotion'].update(evidence='hyp:other-evidence'))
 add('uncited-independently-promoted-evidence',lambda p:promoted(p) or p['citation'].update(cited=False),evidence=True)
 for n in ['version','owner_role','decision','qualified']:add('promotion-missing-'+n,lambda p,n=n:promoted(p) or p['promotion'].update({n:False if n=='qualified' else None}),bad=True)
 add('unknown-defining-purpose',lambda p:p['context'].update(purpose='hyp:unknown'),bad=True)
 add('duplicate-qualified-purpose',lambda p:supported(p) or p['qualified_purposes'].append(p['context']['purpose']),bad=True)
 add('missing-project-context',lambda p:p['context'].update(project=None),bad=True)
 for n in ['actually_verified','source_owner_accepted']:add('actual-claim-not-generated-'+n,lambda p,n=n:p.update({n:True}),bad=True)
 add('implicit-rewrite-or-runtime',lambda p:p.update(implicit_effects=['hyp:silent-definition-rewrite']),bad=True)
 return rows
def frames():
 rows=[]
 def base():return {'operation':'cite-evidence','surface_before':'hyp:s1','surface_after':'hyp:s1','scope_before':'hyp:scope1','scope_after':'hyp:scope1','source_version_before':'hyp:v1','source_version_after':'hyp:v1','meaning_before':'hyp:meaning1','meaning_after':'hyp:meaning1','independent_permissions_before':['hyp:permission1'],'independent_permissions_after':['hyp:permission1'],'evidence_authority_before':[],'evidence_authority_after':[],'separate_owner_decision':None,'history_retained':True,'actual_transition_verified':False}
 observations=['cite-evidence','render-projection','record-inventory','log-observation','research','run-implementation','validate-shape']
 def add(id,change,bad=False):
  f=base();change(f);es=[]
  def ck(ok,msg):
   if not ok:es.append(msg)
  ck(f['operation'] in observations+['promote-evidence','revise-definition','revoke-permission'],'selected finite operation')
  ck(f['surface_before']==f['surface_after'] and f['scope_before']==f['scope_after'] and f['history_retained'] is True,'identity/specific scope/history retained')
  if f['operation'] in observations:ck(f['source_version_before']==f['source_version_after'] and f['meaning_before']==f['meaning_after'] and f['independent_permissions_before']==f['independent_permissions_after'] and f['evidence_authority_before']==f['evidence_authority_after'],'observational operations preserve selected meaning/permission/evidence authority')
  if f['operation']=='promote-evidence':ck(bool(f['separate_owner_decision']) and f['meaning_before']==f['meaning_after'] and f['independent_permissions_before']==f['independent_permissions_after'],'separate evidence promotion decision cannot rewrite meaning or Surface permissions')
  if f['operation']=='revise-definition':ck(bool(f['separate_owner_decision']) and f['source_version_before']!=f['source_version_after'],'separate meaning revision version and owner decision')
  if f['operation']=='revoke-permission':ck(bool(f['separate_owner_decision']) and f['meaning_before']==f['meaning_after'] and f['evidence_authority_before']==f['evidence_authority_after'],'revocation does not rewrite meaning/evidence authority')
  ck(f['actual_transition_verified'] is False,'no actual transition generated')
  if bool(es)!=bad:raise ValueError('Unexpected frame '+id)
  rows.append({'case_id':id,'frame':f,'errors':es,'expected_rejection':bad,'universal_temporal_proof':False,'actual_runtime_execution':False})
 for op in observations:add(op+'-preserves-independent-state',lambda f,op=op:f.update(operation=op))
 def promote(f):f.update(operation='promote-evidence',separate_owner_decision='hyp:evidence-owner-decision',evidence_authority_after=['hyp:e1@v1:scope1'])
 def revise(f):f.update(operation='revise-definition',separate_owner_decision='hyp:definition-owner-decision',source_version_after='hyp:v2',meaning_after='hyp:meaning2')
 def revoke(f):f.update(operation='revoke-permission',separate_owner_decision='hyp:permission-owner-decision',independent_permissions_after=[])
 add('separate-evidence-promotion',promote);add('separate-meaning-revision',revise);add('separate-permission-revocation',revoke)
 for n,value in [('meaning_after','hyp:meaning2'),('source_version_after','hyp:v2'),('independent_permissions_after',[]),('evidence_authority_after',['hyp:e1']),('surface_after','hyp:s2'),('scope_after','hyp:scope2'),('history_retained',False),('actual_transition_verified',True)]:add('citation-cannot-change-'+n,lambda f,n=n,value=value:f.update({n:value}),True)
 for fn,name in [(promote,'promotion'),(revise,'revision'),(revoke,'revocation')]:add(name+'-missing-separate-decision',lambda f,fn=fn:fn(f) or f.update(separate_owner_decision=None),True)
 add('evidence-promotion-cannot-rewrite-meaning',lambda f:promote(f) or f.update(meaning_after='hyp:new'),True)
 add('revision-must-name-new-version',lambda f:revise(f) or f.update(source_version_after=f['source_version_before']),True)
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
RELATED=['definition','constitution','contract','decision','decision-scope','policy','authority-claim','authority-boundary','evidence-set','responsibility']
def verify(write=False):
 context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings()
 root=b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries';paths={'type_registry':root/'artifact-type-registry.json','kind_registry':root/'relation-kind-registry.json','root_descriptor':b.ROOT/'authority/artifact-types/artifact-type/v2/artifact.json'}
 reg=json.loads(paths['type_registry'].read_bytes());kr=json.loads(paths['kind_registry'].read_bytes());current=[x for x in reg['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];selected={}
 for semantic in RELATED+['typed-relation']:
  rows=[x for x in current if x['semantic_kind']==semantic]
  if len(rows)!=1:raise ValueError('Ambiguous current carrier '+semantic)
  row=rows[0];selected[semantic]=row;folder=(b.ROOT/row['artifact_path']).parent;artifact=json.loads((folder/'artifact.json').read_bytes());paths[semantic+'_descriptor']=folder/'artifact.json';paths[semantic+'_schema']=b.ROOT/row['schema_path'];paths[semantic+'_fixture']=folder/artifact['validation_contract']['positive_witness']
  if semantic!='typed-relation':
   paths[semantic+'_generator']=b.ROOT/artifact['source_direction']['shared_generator_path'];paths[semantic+'_validator']=b.ROOT/artifact['validation_contract'].get('shared_validator_path',artifact['validation_contract'].get('validator_path'));paths[semantic+'_artifact_projection']=folder/'ARTIFACT.md';paths[semantic+'_fixture_projection']=folder/artifact['validation_contract']['positive_projection']
   for relative in artifact['validation_contract']['negative_witnesses']:paths[semantic+'_negative_'+b.Path(relative).stem]=folder/relative
   if semantic=='definition':paths['definition_instance_generator']=folder/'generator.py'
 for row in kr['entries']:paths[row['relation_kind_ref']]=b.ROOT/row['instance_path']
 refs={n:b.ref(p) for n,p in paths.items()};raws={n:p.read_bytes() for n,p in paths.items()};docs={n:json.loads(raws[n]) for n,p in paths.items() if p.suffix=='.json'};checks=[]
 def ck(id,test):checks.append({'check_id':id,'result':bool(test)})
 source=load('t.json')['payload']['source'];surface_rows=[x for x in current if x['semantic_kind']=='authority-surface'];direct=[x['artifact_type_ref'] for x in current if source['version_ref'] in x['semantic_definition_refs']];ck('no-current-Surface-carrier-or-direct-definition-binding',not surface_rows and not direct)
 observations=[];negatives=[];probes=[];renderer_bindings=[]
 for semantic,row in selected.items():
  artifact=docs[semantic+'_descriptor'];schema=docs[semantic+'_schema'];fixture=docs[semantic+'_fixture'];validator=b.c.Draft202012Validator(schema);b.c.Draft202012Validator.check_schema(schema)
  ck(semantic+'-current-exact-descriptor-schema-binding',row['artifact_sha256']==refs[semantic+'_descriptor']['sha256'] and row['schema_sha256']==refs[semantic+'_schema']['sha256']);ck(semantic+'-positive-fixture-valid',not list(validator.iter_errors(fixture)))
  if semantic in RELATED:
   mod=types.ModuleType('_pure_'+semantic);exec(compile(raws[semantic+'_generator'],str(paths[semantic+'_generator']),'exec'),mod.__dict__);before=copy.deepcopy([artifact,fixture]);ck(semantic+'-bound-artifact-render-and-digest',mod.render_artifact(artifact).encode()==mod.render_artifact(artifact).encode()==raws[semantic+'_artifact_projection'] and artifact['source_direction']['shared_generator_sha256']==refs[semantic+'_generator']['sha256'])
   if semantic=='definition':
    im=types.ModuleType('_definition_instance');exec(compile(raws['definition_instance_generator'],str(paths['definition_instance_generator']),'exec'),im.__dict__);render=lambda:im.render(fixture);bound=fixture['source_direction']['generator_sha256']==refs['definition_instance_generator']['sha256']
   else:render=lambda:mod.render_instance(artifact,fixture);bound=artifact['validation_contract']['shared_validator_sha256']==refs[semantic+'_validator']['sha256']
   parity=render().encode()==render().encode()==raws[semantic+'_fixture_projection'];ck(semantic+'-two-fixture-renders-exact',parity);ck(semantic+'-declared-binding-observed',bound if semantic!='definition' else not bound);renderer_bindings.append({'semantic_kind':semantic,'two_render_projection_parity':parity,'declared_generator_or_validator_digest_matches_current_file':bound,'accepted_meaning_alignment':False})
   ck(semantic+'-render-inputs-and-current-root-preserved',before==[artifact,fixture] and artifact['artifact_type_root_binding']['sha256']==refs['root_descriptor']['sha256'])
   for name in [n for n in paths if n.startswith(semantic+'_negative_')]:
    es=list(validator.iter_errors(docs[name]));negatives.append({'semantic_kind':semantic,'path':refs[name]['path'],'schema_rejected':bool(es),'errors':[x.message for x in es]})
   cases=[('unresolved-owner-scope-reference',lambda x:x.update(owner_ref='absent:owner',scope_ref='absent:scope'),True),('grant-authority-effect',lambda x:x.update(authority_effect='grant'),False),('Surface-kind-is-not-related-carrier-kind',lambda x:x.update(kind='authority-surface'),False)] if semantic!='definition' else [('unresolved-semantic-owner-and-authority-scope',lambda x:x.update(semantic_owner_ref='absent:owner') or x['scope'].update(authority_scope_ref='absent:scope'),True),('implicit-authority-field',lambda x:x.update(implicit_authority=True),False),('Surface-label-not-current-Definition-schema',lambda x:x.update(schema_version='authority-surface/v1'),False)]
   for id,change,expected in cases:
    candidate=copy.deepcopy(fixture);change(candidate);es=list(validator.iter_errors(candidate));accepted=not es
    if accepted!=expected:raise ValueError('Unexpected related schema probe '+semantic+' '+id)
    probes.append({'semantic_kind':semantic,'case_id':id,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_reference_resolution_or_permission_verified':False})
  observations.append({'semantic_kind':semantic,'artifact_type_ref':row['artifact_type_ref'],'fixture_shape_valid':True,'declared_validator_executed':False,'actual_Surface_permission_or_promotion_verified':False,'Surface_meaning_alignment_established':False,'semantic_definition_refs':row['semantic_definition_refs']})
 source_doc=b.co.source_document(snap,source);es=list(b.c.Draft202012Validator(docs['definition_schema']).iter_errors(source_doc));source_v2={'schema_version':source_doc['schema_version'],'current_definition_schema_accepts_selected_source':not es,'errors':[x.message for x in es],'source_migrated':False,'admitted_source_invalidated':False}
 ck('selected-Definition-v1-not-migrated-to-current-Definition-v2',bool(es) and source_doc['schema_version']=='cyberalchemy-lab-definition/v1');ck('all-related-hostile-fixtures-rejected',bool(negatives) and all(x['schema_rejected'] for x in negatives))
 endpoints=[]
 for row in kr['entries']:
  id=row['relation_kind_ref'];p=docs[id]['payload'];ck('current-Kind-'+id,row['lifecycle_state']=='admitted-current' and row['instance_sha256']==refs[id]['sha256'] and row['exact_endpoint_pair_count']==len(p['allowed_endpoint_pairs']) and row['required_qualifier_axes']==p['qualifier_contract']['required_axes']);endpoints += [{'relation_kind_ref':id,'pair':pair} for pair in p['allowed_endpoint_pairs'] if 'authority-surface' in pair.values()]
 ck('no-Surface-endpoint-in-all-41-current-Kinds',len(kr['entries'])==41 and not endpoints)
 gaps=[];pairs=[];tv=b.c.Draft202012Validator(docs['typed-relation_schema'])
 for id in ['relation.governed-by','relation.scopes-authority-over','relation.evidence-bears-on','relation.originates-from','relation.successor-of']:
  p=docs[id]['payload'];allowed=relation_conditions(docs['typed-relation_schema'],id);gaps.append({'relation_kind_ref':id,'current_Kind_pairs':len(p['allowed_endpoint_pairs']),'current_TR_schema_pairs':len(allowed),'missing_TR_pairs':[x for x in p['allowed_endpoint_pairs'] if x not in allowed],'extra_TR_pairs':[x for x in allowed if x not in p['allowed_endpoint_pairs']],'meaning_alignment_reviewed':False})
  testpairs=p['allowed_endpoint_pairs'] if id not in ['relation.originates-from','relation.successor-of'] else [x for x in p['allowed_endpoint_pairs'] if x['source_kind'] in RELATED]
  for pair in testpairs:
   candidate=copy.deepcopy(docs['typed-relation_fixture']);candidate['payload'].update(relation_kind_ref=id,source={'kind':pair['source_kind'],'ref':'hyp:source','version_ref':'hyp:source-v1'},target={'kind':pair['target_kind'],'ref':'hyp:target','version_ref':'hyp:target-v1'},qualifiers={n:'hyp:qualifier' for n in p['qualifier_contract']['required_axes']});es=list(tv.iter_errors(candidate));accepted=not es
   if accepted!=(pair in allowed):raise ValueError('Kind/TR pair observation mismatch')
   pairs.append({'relation_kind_ref':id,'pair':pair,'record':candidate,'schema_accepted':accepted,'errors':[x.message for x in es],'actual_relation_or_authority_created':False})
 ck('governed-by-six-pairs-missing-from-current-TR',gaps[0]['current_Kind_pairs']==29 and gaps[0]['current_TR_schema_pairs']==23 and gaps[0]['missing_TR_pairs']==[{'source_kind':n,'target_kind':'policy'} for n in ['admission-transaction','authority-boundary','decision-bundle','decision-checkpoint','user-decision-preference','workflow-decision-profile']] and not gaps[0]['extra_TR_pairs'])
 ck('Boundary-to-DecisionScope-current-TR-gap',gaps[1]['current_Kind_pairs']==3 and gaps[1]['current_TR_schema_pairs']==2 and gaps[1]['missing_TR_pairs']==[{'source_kind':'authority-boundary','target_kind':'decision-scope'}] and not gaps[1]['extra_TR_pairs'])
 ck('evidence-lineage-and-successor-do-not-transfer-authority','truth' in docs['relation.evidence-bears-on']['payload']['forbidden_inferences'] and docs['relation.originates-from']['payload']['forbidden_inferences']==['derivation','successor','authority-transfer'] and docs['relation.successor-of']['payload']['forbidden_inferences']==['automatic-supersession','identity-equality','authority-transfer'])
 ck('formal-scaffold-remains-non-grant','Identity, carrier, and owner scope are independent axes' in source_doc['voices']['scientific_formal']['formal_expression'] and not any(x['disposition']=='encoded' and x['source_selector']=='/voices/scientific_formal/formal_expression' for x in load('t.json')['payload']['clauses']))
 if not all(x['result'] for x in checks):raise ValueError(json.dumps(checks))
 ps=profiles();fs=frames();bindings=[b.ref(p) for p in [b.UNIT/'verify_authority_profile.py',b.UNIT/'build_candidate.py',b.IMPL/'contracts.py',b.IMPL/'verifier.py']];prior=load('../cal.definition.authority-promotion/delivery-manifest.json');b.unchanged(prior['files']+context['sources']+list(refs.values())+bindings);b.external_current(context);b.r.verify(snap,b.ROOT)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 report={'schema_version':'definition-assurance-AuthoritySurface-profile/v1-candidate','status':'PASS-for-explicit-Surface-permission-hypotheses-and-bounded-current-catalog-observations','authority_effect':'none','checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','source-checks.json','comparison-selection.json']],'selected_inputs':refs,'profile_control_count':len(ps),'rejected_profile_controls':sum(x['expected_rejection'] for x in ps),'profiles':ps,'finite_history_frame_count':len(fs),'rejected_history_frames':sum(x['expected_rejection'] for x in fs),'finite_history_frames':fs,'actual_check_count':len(checks),'actual_checks':checks,'current_type_registry_rows':len(reg['admitted_contracts']),'admitted_current_type_rows':len(current),'current_Kind_rows':len(kr['entries']),'current_Surface_carrier_selection':{'semantic_kind_rows':surface_rows,'direct_definition_binding_types':direct,'dedicated_Surface_carrier_established':False,'scope':'selected admitted-current Type registry only'},'Surface_endpoint_roles':endpoints,'related_carrier_observations':observations,'related_renderer_binding_observations':renderer_bindings,'current_Definition_fixture_generator_binding':{'declared_sha256':docs['definition_fixture']['source_direction']['generator_sha256'],'current_file_ref':refs['definition_instance_generator'],'digest_matches':False,'two_render_projection_parity':True,'canonical_file_changed':False},'negative_fixture_checks':negatives,'actual_related_schema_probes':probes,'selected_source_current_Definition_schema_probe':source_v2,'Kind_TR_schema_gaps':gaps,'all_selected_current_Kind_TR_pair_observations':pairs,'source_mapping_gaps':{'genus_iff_and_source_precedence_reviewed':False,'purpose_constants_and_project_scope_owner_identity_aligned':False,'real_qualified_permission_and_responsible_owner_promotion_verified':False,'universal_temporal_rewrite_prevention_established':False},'new_authorities_or_relations_created':0,'actual_permission_or_promotion_created':False,'actual_runtime_activated':False,'semantic_ready':False,'source_fidelity':'pending','mechanized_proof':False,'claim_ceiling':'Explicit hypothetical permission/promotion qualification and finite frames; exact current related-carrier shapes, pure bound projections, hostile probes and Kind/TR observations. Current Definition/v2 does not migrate the selected Definition/v1 source; shape validity cannot resolve owner/scope or grant actual authority. No Surface carrier binding, actual permission, source-owner fidelity or universal temporal/rewrite-prevention proof.'}
 if write:b.put('authority-profile-checks.json',report)
 elif not b.r.same_json(report,load('authority-profile-checks.json')):raise ValueError('Fresh Surface profile differs')
 return report
def main():
 r=verify('--write' in b.sys.argv);print(json.dumps({k:r[k] for k in ['status','profile_control_count','rejected_profile_controls','finite_history_frame_count','rejected_history_frames','actual_check_count','current_type_registry_rows','admitted_current_type_rows','current_Kind_rows','semantic_ready']},indent=2,sort_keys=True))
if __name__=='__main__':main()
