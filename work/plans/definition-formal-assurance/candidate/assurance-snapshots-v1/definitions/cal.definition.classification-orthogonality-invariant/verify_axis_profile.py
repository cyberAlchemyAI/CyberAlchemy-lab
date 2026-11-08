"""Bounded records/frames and actual catalog observations; no semantic-uniqueness oracle."""
import ast,copy,json
import build_candidate as b
import verifier as v
AXIS_FIELDS={'axis_id','purpose_ref','question','owner_ref','canonical','redundant','data_state','review_reason'}
BRIDGE_FIELDS={'coupling_id','source_axis','target_axis','relation_kind_ref','direction','owner_ref','evidence_refs','effect_ref'}
def named(x):return isinstance(x,str) and bool(x.strip())
def bridge_errors(row,axis_ids):
 errors=[]
 if set(row)!=BRIDGE_FIELDS:errors.append('missing-or-extra-bridge-field')
 for n in sorted(BRIDGE_FIELDS-{'evidence_refs'}):
  if not named(row.get(n)):errors.append('unnamed-'+n)
 if row.get('source_axis') not in axis_ids or row.get('target_axis') not in axis_ids:errors.append('unresolved-axis-endpoint')
 if row.get('direction')!='source-to-target':errors.append('unreviewed-direction-or-symmetry-policy')
 evidence=row.get('evidence_refs')
 if not isinstance(evidence,list) or not evidence or any(not named(x) for x in evidence) or len(evidence)!=len(set(evidence)):errors.append('invalid-evidence')
 return errors
def profile_errors(profile):
 errors=[];axes=profile['axes'];axis_ids={x.get('axis_id') for x in axes};purposes=[]
 if len(axis_ids)!=len(axes):errors.append('duplicate-axis-identity')
 for a in axes:
  if set(a)!=AXIS_FIELDS:errors.append('missing-or-extra-axis-field')
  for n in ['axis_id','purpose_ref','question','owner_ref']:
   if not named(a.get(n)):errors.append('unnamed-'+n)
  for n in ['canonical','redundant']:
   if not isinstance(a.get(n),bool):errors.append('nonboolean-'+n)
  if a.get('canonical') is True:
   purposes.append(a.get('purpose_ref'))
   if a.get('redundant') is True:errors.append('redundant-canonical-axis')
  if a.get('data_state') not in ['available','known-unavailable','unknown']:errors.append('invalid-data-state')
  reason=a.get('review_reason')
  if a.get('data_state')=='known-unavailable' and (not isinstance(reason,dict) or set(reason)!= {'kind','ref'} or reason.get('kind') not in ['unique-question','routing-decision','validation-effect'] or not named(reason.get('ref'))):errors.append('no-data-review-reason-missing')
 if len(purposes)!=len(set(purposes)):errors.append('equal-canonical-purpose-reference')
 valid=[]
 for row in profile['couplings']:
  e=bridge_errors(row,axis_ids);errors+=e
  if not e:valid.append(row)
 for d in profile['dependencies']:
  if set(d)!= {'source_axis','target_axis'} or d.get('source_axis') not in axis_ids or d.get('target_axis') not in axis_ids:errors.append('malformed-dependency');continue
  if not any(row['source_axis']==d['source_axis'] and row['target_axis']==d['target_axis'] for row in valid):errors.append('dependency-lacks-exact-ordered-bridge')
 for l in profile['labels']:
  if set(l)!= {'label_id','canonical','convenience','generated','redundant'} or not named(l.get('label_id')):errors.append('malformed-label')
  if any(not isinstance(l.get(n),bool) for n in ['canonical','convenience','generated','redundant']):errors.append('nonboolean-label-role')
  if l.get('canonical') is True and l.get('redundant') is True:errors.append('redundant-canonical-label')
  if l.get('convenience') is True and (l.get('generated') is not True or l.get('canonical') is True):errors.append('convenience-label-not-generated-only')
 return errors
def base_profile():
 return {'axes':[{'axis_id':'maturity','purpose_ref':'purpose:lifecycle-readiness','question':'How mature is this candidate?','owner_ref':'role:shared-owner','canonical':True,'redundant':False,'data_state':'unknown','review_reason':None},{'axis_id':'confidence','purpose_ref':'purpose:evidence-confidence','question':'What evidence supports it?','owner_ref':'role:shared-owner','canonical':True,'redundant':False,'data_state':'unknown','review_reason':None}], 'dependencies':[], 'couplings':[], 'labels':[{'label_id':'convenience:ready','canonical':False,'convenience':True,'generated':True,'redundant':False}]}
def base_bridge():return {'coupling_id':'coupling:example','source_axis':'maturity','target_axis':'confidence','relation_kind_ref':'kind:declared-dependence-example','direction':'source-to-target','owner_ref':'role:bridge-owner','evidence_refs':['evidence:example'],'effect_ref':'effect:description-example'}
def record_controls():
 rows=[]
 def add(id,change,reject=False):
  p=base_profile();change(p);e=profile_errors(p)
  if bool(e)!=reject:raise ValueError('Wrong record control '+id+' '+str(e))
  rows.append({'case_id':id,'profile':p,'errors':e,'expected_rejection':reject,'mapping_reviewed':False,'semantic_purpose_uniqueness_proved':False})
 add('distinct-purpose-shared-owner-no-data-unknown',lambda p:None)
 for n in sorted(AXIS_FIELDS):add('missing-axis-'+n,lambda p,n=n:p['axes'][0].pop(n),True)
 add('different-question-strings-with-same-purpose-not-new-axis',lambda p:p['axes'][1].update(purpose_ref=p['axes'][0]['purpose_ref']),True)
 add('same-question-with-distinct-purpose-ids-needs-meaning-review',lambda p:p['axes'][1].update(question=p['axes'][0]['question']))
 add('redundant-canonical-axis',lambda p:p['axes'][0].update(redundant=True),True)
 add('status-string-is-not-boolean-canonical-role',lambda p:p['axes'][0].update(canonical='yes'),True)
 add('convenience-cannot-be-canonical-copy',lambda p:p['labels'][0].update(canonical=True),True)
 add('convenience-requires-generated-projection',lambda p:p['labels'][0].update(generated=False),True)
 add('redundant-canonical-label',lambda p:p['labels'][0].update(canonical=True,convenience=False,redundant=True),True)
 add('known-no-data-needs-named-review-reason',lambda p:p['axes'][0].update(data_state='known-unavailable'),True)
 for reason in ['unique-question','routing-decision','validation-effect']:
  add('known-no-data-with-'+reason,lambda p,reason=reason:p['axes'][0].update(data_state='known-unavailable',review_reason={'kind':reason,'ref':'reason:example'}))
 add('available-data-does-not-require-statistics',lambda p:p['axes'][0].update(data_state='available'))
 add('explicit-dependence-without-bridge',lambda p:p['dependencies'].append({'source_axis':'maturity','target_axis':'confidence'}),True)
 def coupled(p):p['dependencies']=[{'source_axis':'maturity','target_axis':'confidence'}];p['couplings']=[base_bridge()]
 add('complete-explicit-coupling',coupled)
 for n in sorted(BRIDGE_FIELDS):
  def missing(p,n=n):coupled(p);p['couplings'][0].pop(n)
  add('missing-bridge-'+n,missing,True)
 def reverse(p):coupled(p);p['couplings'][0].update(source_axis='confidence',target_axis='maturity')
 add('reversed-bridge-does-not-cover-forward-dependency',reverse,True)
 def symmetry(p):coupled(p);p['couplings'][0]['direction']='symmetric'
 add('symmetry-policy-needs-separate-reviewed-embedding',symmetry,True)
 add('labels-can-have-no-instance',lambda p:p.update(labels=[]))
 return rows
def frame_errors(trace,bridges):
 errors=[];ids={'maturity','confidence'};valid=[r for r in bridges if not bridge_errors(r,ids)]
 for n,step in enumerate(trace['steps']):
  if not step['allowed']:continue
  for other in trace['authority_axes']:
   if other==step['changed_axis']:continue
   bridged=any(r['source_axis']==step['changed_axis'] and r['target_axis']==other for r in valid)
   if step['before'][other]!=step['after'][other] and not bridged:errors.append('unbridged-authority-cochange-step-'+str(n))
 return errors
def frame_controls():
 def step(cochange=False,allowed=True):return {'allowed':allowed,'changed_axis':'maturity','before':{'maturity':0,'confidence':0},'after':{'maturity':1,'confidence':1 if cochange else 0}}
 cases=[('independent-authority-axis-stable',[step()],[],False),('unbridged-cochange',[step(True)],[],True),('explicit-bridge-cochange',[step(True)],[base_bridge()],False),('reverse-bridge-not-forward',[step(True)],[dict(base_bridge(),source_axis='confidence',target_axis='maturity')],True),('missing-effect-bridge-cannot-lift-frame',[step(True)],[{k:v for k,v in base_bridge().items() if k!='effect_ref'}],True),('outside-allowed-guard-not-certified',[step(True,False)],[],False),('explicit-bridge-does-not-force-cochange',[step()],[base_bridge()],False),('later-unbridged-cochange-visible',[step(),step(True)],[],True)]
 rows=[]
 for id,steps,bridges,reject in cases:
  trace={'authority_axes':['confidence'],'steps':steps};e=frame_errors(trace,bridges)
  if bool(e)!=reject:raise ValueError('Wrong finite frame '+id)
  rows.append({'case_id':id,'trace':trace,'bridges':bridges,'errors':e,'expected_rejection':reject,'actual_runtime_execution':False,'mechanized_unbounded_proof':False,'guard_scope':'only explicitly allowed sampled changes; outside guard gives no compliance claim'})
 return rows
def verify(write=False):
 context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings()
 paths={'checker':b.UNIT/'verify_axis_profile.py','legacy_model':b.ROOT/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json','legacy_validator':b.ROOT/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/validate.py','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json','kind_schema':b.ROOT/'authority/artifact-types/relation-kind/v2/schema.json','definition_schema':b.ROOT/'authority/artifact-types/definition/v1/schema.json'}
 bindings={name:b.ref(p) for name,p in paths.items()};raws={name:b.r.read_bytes(b.ROOT,ref['path']) for name,ref in bindings.items()};docs={name:b.r.parse(raws[name],name) for name in ['legacy_model','kind_registry','kind_schema','definition_schema']};checks=[]
 def check(id,result,detail):
  checks.append({'check_id':id,'result':bool(result),'detail':detail})
  if not result:raise ValueError('Actual observation failed '+id)
 source=b.source_ref(snap,'cal.definition.classification-orthogonality-invariant');axis=b.source_ref(snap,'cal.definition.classification-axis');source_doc=b.co.source_document(snap,source);axis_doc=b.co.source_document(snap,axis)
 source_inputs={'invariant':{'path':source['path'],'sha256':source['sha256']},'axis':{'path':axis['path'],'sha256':axis['sha256']}}
 check('two-distinct-current-target-identities-share-D22',source['definition_id']!=axis['definition_id'] and source_doc['source_refs']==axis_doc['source_refs'],{'invariant':source,'axis':axis,'meaning':'Shared lineage is source evidence, not semantic equivalence.'})
 check('target-specific-normative-voices-differ',source_doc['voices']['scientific_formal']['normative_statement']!=axis_doc['voices']['scientific_formal']['normative_statement'],{'normative_digests':[b.r.digest(x['voices']['scientific_formal']['normative_statement'].encode()) for x in [source_doc,axis_doc]]})
 model=docs['legacy_model'];bound=[x for x in model['definition_bindings'] if x['definition_ref']==source['version_ref']]
 check('legacy-model-exact-invariant-binding',len(bound)==1 and bound[0]['path']==source['path'] and bound[0]['sha256']==source['sha256'],bound)
 selected={};kinds=[]
 for row in docs['kind_registry']['entries']:
  p=b.ROOT/row['instance_path'];ref=b.ref(p);selected[row['relation_kind_id']]=ref;d=b.r.parse(b.r.read_bytes(b.ROOT,ref['path']),'kind')
  check('exact-current-kind-'+row['relation_kind_id'],ref['sha256']==row['instance_sha256'] and not list(b.c.Draft202012Validator(docs['kind_schema']).iter_errors(d)),ref);kinds.append(d['payload'])
 axis_ids=[x['axis_id'] for x in kinds];questions=[x['unique_question'] for x in kinds]
 check('41-distinct-kind-axis-ids-and-question-strings',len(kinds)==len(set(axis_ids))==len(set(questions))==41,{'nominal_axis_ids':41,'different_printed_questions':41,'semantic_purpose_uniqueness_proved':False})
 norms=model['normalizations'];normalized=[x['previous_relation_kind'] for x in norms];axes={x['relation_kind_id'] for x in model['entries']}
 check('42-old-names-map-to-23-declared-axes',len(norms)==len(set(normalized))==42 and len(axes)==23 and all(x['axis_relation_kind'] in axes for x in norms),{'old_names':42,'declared_axes':23,'meaning_preservation_proved':False})
 grouped={a:[x for x in norms if x['axis_relation_kind']==a] for a in sorted(axes)}
 distinguish=[{'axis':a,'old_names':[x['previous_relation_kind'] for x in rows],'qualifier_signatures':[json.dumps(x['fixed_qualifiers'],sort_keys=True) for x in rows]} for a,rows in grouped.items() if len(rows)>1]
 check('merged-old-names-retain-different-fixed-qualifier-signatures',all(len(set(x['qualifier_signatures']))==len(x['qualifier_signatures']) for x in distinguish),{'groups':distinguish,'scope':'Declared qualifier identity only, not a semantic meaning oracle.'})
 # Execute only the exact bounded hostile loop from the selected validator, not main's writers.
 tree=ast.parse(raws['legacy_validator'],filename=str(paths['legacy_validator']));main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
 loops=[x for x in main.body if isinstance(x,ast.For) and isinstance(x.target,ast.Name) and x.target.id=='hostile']
 if len(loops)!=1:raise ValueError('Ambiguous selected bounded hostile loop')
 namespace={'model':model,'axes':axes,'hostile_results':[]};exec(compile(ast.Module(body=loops,type_ignores=[]),str(paths['legacy_validator']),'exec'),namespace)
 hostile=namespace['hostile_results'];check('10-bounded-legacy-hostile-declaration-checks',len(hostile)==10 and all(x['result']=='PASS' for x in hostile),{'scope':'Existing loop sets derived={asserted}; it checks declared forbidden tokens, not consumer inference, independent variability or combined theory.'})
 classifications=[]
 for row in snap['current_entries']:
  doc=b.co.source_document(snap,{k:row[k] for k in ['definition_id','version_ref','path','sha256']});classifications.append({'definition_id':row['definition_id'],'semantic_kind':doc['classification']['semantic_kind'],'artifact_type_ref':doc['classification']['artifact_type_ref'],'source_classification_lifecycle_posture_ref':doc['classification']['lifecycle_posture_ref'],'effective_registry_state':row['effective_state']})
 check('183-current-definition-artifacts-share-artifact-kind-not-content-role',len(classifications)==183 and all(x['semantic_kind']=='definition' and x['artifact_type_ref']=='cal.artifact-type.definition/v1' for x in classifications),{'count':183,'logical_content_roles_not_inferred':True})
 record=record_controls();frames=frame_controls();formal_probe={'case_id':'unique-distinction-OR-can-bypass-recorded-dependency','unique_operational_distinction':True,'has_dependency':True,'every_dependency_explicit':False,'inherited_OR_branch_admissible':True,'candidate_target_normative_dependency_satisfied':False,'precedence_owner_reviewed':False}
 report={'schema_version':'definition-assurance-classification-axis-profile/v1-candidate','status':'PASS-for-bounded-axis-records-frames-and-actual-declarations','authority_effect':'none','checker_bindings':[bindings['checker'],b.ref(b.UNIT/'build_candidate.py')],'input_refs':[b.ref(b.UNIT/'t.json'),b.ref(b.UNIT/'static-ir.json'),b.ref(b.UNIT/'legacy-source-section.md')],'runtime_bindings':runtime,'selected_inputs':bindings,'kind_inputs':selected,'sibling_source_inputs':source_inputs,'profile_control_count':len(record),'rejected_profile_controls':sum(x['expected_rejection'] for x in record),'profile_controls':record,'finite_frame_trace_count':len(frames),'rejected_frame_traces':sum(x['expected_rejection'] for x in frames),'finite_frame_traces':frames,'actual_check_count':len(checks),'actual_checks':checks,'legacy_hostile_checks':hostile,'current_classification_observations':classifications,'formal_precedence_probe':formal_probe,'source_mapping_gaps':{'mapping_reviewed':False,'purpose_reference_identity_not_semantic_inequivalence_proof':True,'current_kind_nominal_count':41,'legacy_model_axis_count':23,'shared_D22_source_does_not_merge_sibling_targets':True,'before_downstream_governance_not_temporally_encoded':True,'boundary_schema_or_residue_alternatives_unresolved':True,'statistical_and_Hilbert_semantics_deferred':True,'closed_finite_profile_not_live_compliance':True},'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'new_axes_or_labels_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'claim_ceiling':'Finite illustrative records/frames, exact source/sibling/catalog/normalization observations and selected bounded legacy loop. Nominal axis/question/qualifier distinctions do not prove semantic purpose uniqueness, statistical independence, Hilbert equivalence, runtime no-inference or jointly aligned theory.'}
 b.unchanged(list(bindings.values())+list(selected.values())+list(source_inputs.values())+report['input_refs']);b.r.verify(snap,b.ROOT);b.external_current(context)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('axis-profile-checks.json',report)
 elif not b.r.same_json(report,json.loads((b.UNIT/'axis-profile-checks.json').read_bytes())):raise ValueError('Fresh profile differs')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profile_controls':x['profile_control_count'],'rejected_profiles':x['rejected_profile_controls'],'finite_frame_traces':x['finite_frame_trace_count'],'rejected_frame_traces':x['rejected_frame_traces'],'actual_checks':x['actual_check_count'],'legacy_hostile_checks':len(x['legacy_hostile_checks']),'nominal_current_kind_axes':41,'semantic_purpose_uniqueness_proved':False,'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
