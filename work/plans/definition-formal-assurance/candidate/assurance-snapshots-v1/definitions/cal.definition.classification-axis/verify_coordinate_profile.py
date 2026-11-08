"""Exact version/value records and finite coordinate choices; actual fixtures are not presumed joined."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def named(x):return isinstance(x,str) and bool(x.strip())
def base_profile():
 axes=[{'axis_ref':a,'scheme_version_ref':'scheme:toy@1','name':a,'purpose_ref':'purpose:'+a,'owner_ref':'role:axis-owner','allowed_value_refs':[a+':zero',a+':one']} for a in ['maturity','confidence']]
 values=[{'value_ref':a+':'+val,'axis_ref':a,'scheme_version_ref':'scheme:toy@1','label':val} for a,val in itertools.product(['maturity','confidence'],['zero','one'])]
 assignments=[{'assignment_id':'assignment:'+a,'subject_ref':'subject:toy','subject_version_ref':'subject:toy@1','scheme_version_ref':'scheme:toy@1','axis_ref':a,'value_ref':a+':zero','evidence_refs':['evidence:toy']} for a in ['maturity','confidence']]
 return {'selected_scheme_version_ref':'scheme:toy@1','axes':axes,'values':values,'assignments':assignments}
def record_errors(p):
 errors=[];sv=p['selected_scheme_version_ref'];axes={x.get('axis_ref'):x for x in p['axes']};values={x.get('value_ref'):x for x in p['values']}
 if not named(sv):errors.append('unnamed-selected-version')
 if len(axes)!=len(p['axes']):errors.append('duplicate-axis-reference')
 if len(values)!=len(p['values']):errors.append('duplicate-governed-value-reference')
 purposes=[]
 for a in p['axes']:
  if set(a)!= {'axis_ref','scheme_version_ref','name','purpose_ref','owner_ref','allowed_value_refs'}:errors.append('missing-or-extra-axis-field')
  for key in ['axis_ref','scheme_version_ref','name','purpose_ref','owner_ref']:
   if not named(a.get(key)):errors.append('unnamed-'+key)
  if a.get('scheme_version_ref')!=sv:errors.append('axis-wrong-exact-version')
  purposes.append(a.get('purpose_ref'));allowed=a.get('allowed_value_refs')
  if not isinstance(allowed,list) or not allowed or any(not named(x) for x in allowed) or len(allowed)!=len(set(allowed)):errors.append('invalid-allowed-value-reference-set');continue
  for ref in allowed:
   value=values.get(ref)
   if value is None or value.get('axis_ref')!=a.get('axis_ref') or value.get('scheme_version_ref')!=sv:errors.append('allowed-value-wrong-axis-version-or-unresolved')
 if len(purposes)!=len(set(purposes)):errors.append('equal-purpose-reference-needs-review')
 for value in p['values']:
  if set(value)!= {'value_ref','axis_ref','scheme_version_ref','label'} or any(not named(value.get(key)) for key in ['value_ref','axis_ref','scheme_version_ref','label']):errors.append('malformed-value')
  if value.get('axis_ref') not in axes or value.get('scheme_version_ref')!=sv:errors.append('value-wrong-axis-or-version')
 ids=[]
 for a in p['assignments']:
  ids.append(a.get('assignment_id'))
  if set(a)!= {'assignment_id','subject_ref','subject_version_ref','scheme_version_ref','axis_ref','value_ref','evidence_refs'}:errors.append('missing-or-extra-assignment-field')
  if any(not named(a.get(key)) for key in ['assignment_id','subject_ref','subject_version_ref','scheme_version_ref','axis_ref','value_ref']):errors.append('unnamed-assignment-binding')
  axis=axes.get(a.get('axis_ref'));value=values.get(a.get('value_ref'))
  if axis is None or value is None or value.get('axis_ref')!=a.get('axis_ref') or a.get('value_ref') not in axis.get('allowed_value_refs',[]):errors.append('assignment-value-wrong-axis-or-unresolved')
  if a.get('scheme_version_ref')!=sv or value is not None and value.get('scheme_version_ref')!=a.get('scheme_version_ref'):errors.append('assignment-wrong-version')
  ev=a.get('evidence_refs')
  if not isinstance(ev,list) or not ev or any(not named(x) for x in ev) or len(ev)!=len(set(ev)):errors.append('assignment-invalid-evidence')
 if len(ids)!=len(set(ids)):errors.append('duplicate-assignment-identity')
 return errors
def record_controls():
 rows=[]
 def add(id,change,reject=False):
  p=base_profile();change(p);e=record_errors(p)
  if bool(e)!=reject:raise ValueError('Wrong profile control '+id+' '+str(e))
  rows.append({'case_id':id,'profile':p,'errors':e,'expected_rejection':reject,'actual_canonical_assignment_write':False,'meaning_embedding_reviewed':False})
 add('versioned-distinct-axis-and-value-bindings',lambda p:None)
 for key in sorted(base_profile()['axes'][0]):add('axis-missing-'+key,lambda p,key=key:p['axes'][0].pop(key),True)
 for key in sorted(base_profile()['assignments'][0]):add('assignment-missing-'+key,lambda p,key=key:p['assignments'][0].pop(key),True)
 add('same-question-name-does-not-merge-different-purpose-references',lambda p:p['axes'][1].update(name=p['axes'][0]['name']))
 add('different-label-does-not-rescue-equal-purpose-reference',lambda p:p['axes'][1].update(purpose_ref=p['axes'][0]['purpose_ref']),True)
 add('same-raw-answer-label-across-axes-retains-distinct-value-identities',lambda p:None)
 add('axis-version-drift',lambda p:p['axes'][0].update(scheme_version_ref='scheme:toy@2'),True)
 add('value-version-drift',lambda p:p['values'][0].update(scheme_version_ref='scheme:toy@2'),True)
 add('assignment-version-drift',lambda p:p['assignments'][0].update(scheme_version_ref='scheme:toy@2'),True)
 add('value-from-other-axis',lambda p:p['assignments'][0].update(value_ref='confidence:zero'),True)
 add('unresolved-axis',lambda p:p['assignments'][0].update(axis_ref='unknown'),True)
 add('unresolved-value',lambda p:p['assignments'][0].update(value_ref='unknown'),True)
 add('empty-allowed-value-set',lambda p:p['axes'][0].update(allowed_value_refs=[]),True)
 add('duplicate-assignment-id',lambda p:p['assignments'][1].update(assignment_id=p['assignments'][0]['assignment_id']),True)
 add('duplicate-governed-value-id',lambda p:p['values'][1].update(value_ref=p['values'][0]['value_ref']),True)
 add('missing-exact-subject-revision',lambda p:p['assignments'][0].update(subject_version_ref=''),True)
 add('empty-assignment-evidence',lambda p:p['assignments'][0].update(evidence_refs=[]),True)
 add('classification-owner-not-subject-owner-proof',lambda p:p['axes'][0].update(owner_ref='role:different-axis-owner'))
 return rows
def base_cube():
 states=[{'state_id':'s'+str(a)+str(z),'scheme_version_ref':'scheme:toy@1','subject_version_ref':'subject:toy@1','answers':{'maturity':a,'confidence':z}} for a,z in itertools.product([0,1],repeat=2)]
 links=[{'axis':axis,'from':s['state_id'],'to':t['state_id']} for axis,s,t in itertools.product(['maturity','confidence'],states,states) if all(s['answers'][other]==t['answers'][other] for other in ['maturity','confidence'] if other!=axis)]
 return {'scheme_version_ref':'scheme:toy@1','subject_version_ref':'subject:toy@1','allowed_answers':{'maturity':[0,1],'confidence':[0,1]},'states':states,'links':links,'bridges':[]}
def cube_errors(cube):
 errors=[];states={s['state_id']:s for s in cube['states']}
 if not states:errors.append('empty-selected-state-population')
 if len(states)!=len(cube['states']):errors.append('duplicate-state-identity')
 for s in states.values():
  if s['scheme_version_ref']!=cube['scheme_version_ref'] or s['subject_version_ref']!=cube['subject_version_ref']:errors.append('state-context-version-mismatch')
  for a,allowed in cube['allowed_answers'].items():
   if a not in s['answers'] or s['answers'][a] not in allowed:errors.append('state-untyped-or-unallowed-answer')
 def coupled(a,z):return any(x.get('source')==a and x.get('target')==z and all(named(x.get(k)) for k in ['kind','owner','evidence','effect']) for x in cube['bridges'])
 for link in cube['links']:
  s=states.get(link['from']);t=states.get(link['to']);axis=link['axis']
  if s is None or t is None or axis not in cube['allowed_answers']:errors.append('unresolved-selected-link');continue
  for other in cube['allowed_answers']:
   if other!=axis and not coupled(axis,other) and s['answers'][other]!=t['answers'][other]:errors.append('unbridged-coordinate-cochange')
 for s in states.values():
  for axis,allowed in cube['allowed_answers'].items():
   for answer in allowed:
    witnesses=[states[link['to']] for link in cube['links'] if link['from']==s['state_id'] and link['axis']==axis and link['to'] in states and states[link['to']]['answers'].get(axis)==answer and states[link['to']]['scheme_version_ref']==s['scheme_version_ref'] and states[link['to']]['subject_version_ref']==s['subject_version_ref'] and all(other==axis or coupled(axis,other) or states[link['to']]['answers'].get(other)==s['answers'][other] for other in cube['allowed_answers'])]
    if not witnesses:errors.append('missing-independent-choice-'+s['state_id']+'-'+axis+'-'+str(answer))
 return errors
def cube_controls():
 rows=[]
 def add(id,change,reject=False):
  cube=base_cube();change(cube);e=cube_errors(cube)
  if bool(e)!=reject:raise ValueError('Wrong cube '+id+' '+str(e))
  rows.append({'case_id':id,'cube':cube,'errors':e,'expected_rejection':reject,'actual_runtime_execution':False,'mechanized_unbounded_proof':False,'scope':'All supplied finite coordinates/allowed answers/selected links; no world probability or reachable-state proof.'})
 add('complete-four-state-coordinate-cube',lambda c:None)
 def missing_corner(c):c['states']=[s for s in c['states'] if s['state_id']!='s11'];c['links']=[l for l in c['links'] if l['from']!='s11' and l['to']!='s11']
 add('missing-corner-breaks-required-choice',missing_corner,True)
 add('self-links-only-cannot-supply-alternative-values',lambda c:c.update(links=[l for l in c['links'] if l['from']==l['to']]),True)
 add('mixed-scheme-destination',lambda c:c['states'][1].update(scheme_version_ref='scheme:toy@2'),True)
 add('mixed-subject-revision-destination',lambda c:c['states'][1].update(subject_version_ref='subject:toy@2'),True)
 add('unbridged-cochange-link',lambda c:c['links'].append({'axis':'maturity','from':'s00','to':'s11'}),True)
 def coupled_diagonal(c):
  c['states']=[s for s in c['states'] if s['state_id'] in ['s00','s11']];c['links']=[{'axis':a,'from':s['state_id'],'to':t['state_id']} for a,s,t in itertools.product(['maturity','confidence'],c['states'],c['states'])];c['bridges']=[{'source':a,'target':z,'kind':'kind:toy','owner':'role:toy','evidence':'evidence:toy','effect':'effect:toy'} for a,z in [('maturity','confidence'),('confidence','maturity')]]
 add('explicit-two-way-couplings-allow-diagonal-state-space',coupled_diagonal)
 def one_way(c):coupled_diagonal(c);c['bridges']=c['bridges'][:1]
 add('one-way-coupling-does-not-lift-reverse-frame',one_way,True)
 def missing_effect(c):coupled_diagonal(c);c['bridges'][0].pop('effect')
 add('incomplete-effect-vector-does-not-lift-frame',missing_effect,True)
 add('unallowed-coordinate-answer',lambda c:c['states'][0]['answers'].update(maturity=2),True)
 return rows
def verify(write=False):
 context=json.loads((b.UNIT/'context.json').read_bytes());b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT);runtime=v.f.current_bindings()
 paths={'checker':b.UNIT/'verify_coordinate_profile.py','type_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json','legacy_model':b.ROOT/'authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json','kind_registry':b.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'}
 for kind in ['classification-scheme','classification-value','classification-assignment']:
  for name,suffix in [('descriptor','artifact.json'),('schema','schema.json'),('fixture','fixtures/valid/record.json')]:paths[kind+'-'+name]=b.ROOT/'authority/artifact-types'/kind/'v1'/suffix
 bindings={name:b.ref(path) for name,path in paths.items()};docs={name:b.r.parse(b.r.read_bytes(b.ROOT,ref['path']),name) for name,ref in bindings.items() if name!='checker'};checks=[]
 def check(id,result,detail):
  checks.append({'check_id':id,'result':bool(result),'detail':detail})
  if not result:raise ValueError('Actual observation failed '+id)
 source=b.source_ref(snap,'cal.definition.classification-axis');sibling=b.source_ref(snap,'cal.definition.classification-orthogonality-invariant');doc=b.co.source_document(snap,source);other=b.co.source_document(snap,sibling);source_inputs={'axis':{k:source[k] for k in ['path','sha256']},'invariant':{k:sibling[k] for k in ['path','sha256']}}
 check('distinct-current-targets-share-D22-source',source['definition_id']!=sibling['definition_id'] and doc['source_refs']==other['source_refs'],{'axis':source,'invariant':sibling,'identity_merge_reviewed':False})
 bound=[x for x in docs['legacy_model']['definition_bindings'] if x['definition_ref']==source['version_ref']];check('legacy-model-exact-axis-source-binding',len(bound)==1 and bound[0]['path']==source['path'] and bound[0]['sha256']==source['sha256'],bound)
 for kind in ['classification-scheme','classification-value','classification-assignment']:
  desc=docs[kind+'-descriptor'];schema=docs[kind+'-schema'];fixture=docs[kind+'-fixture'];rows=[x for x in docs['type_registry']['admitted_contracts'] if x['artifact_type_ref']==desc['artifact_type_ref']]
  check(kind+'-exact-current-admitted-contract',len(rows)==1 and rows[0]['artifact_sha256']==bindings[kind+'-descriptor']['sha256'] and rows[0]['schema_sha256']==bindings[kind+'-schema']['sha256'] and rows[0]['lifecycle_state']=='admitted-current',rows)
  check(kind+'-bound-schema-current',desc['schema_digest']==bindings[kind+'-schema']['sha256'],bindings[kind+'-schema'])
  b.c.Draft202012Validator.check_schema(schema);check(kind+'-individual-selected-fixture-shape-valid',not list(b.c.Draft202012Validator(schema).iter_errors(fixture)),bindings[kind+'-fixture'])
  sr=b.source_ref(snap,'cal.definition.'+kind);binding=desc['semantic_definition_bindings'];check(kind+'-exact-definition-binding',len(binding)==1 and all(binding[0][key]==sr[key] for key in ['path','sha256']) and binding[0]['definition_ref']==sr['version_ref'],sr)
 selected_axis_contracts=[x for x in docs['type_registry']['admitted_contracts'] if x['semantic_kind']=='classification-axis']
 check('no-dedicated-axis-carrier-in-selected-admitted-type-surface',selected_axis_contracts==[] and not (b.ROOT/'authority/artifact-types/classification-axis').exists(),{'claim_ceiling':'Selected local carrier surface only; Axis references may resolve through a separately owned representation not reviewed here.'})
 kinds=docs['kind_registry']['entries'];check('41-current-kind-axis-reference-declarations',len(kinds)==41 and len({x['axis_id'] for x in kinds})==41,{'count':41,'independent-value-semantics_proved':False})
 scheme=docs['classification-scheme-fixture'];value=docs['classification-value-fixture'];assignment=docs['classification-assignment-fixture'];sp=scheme['payload'];vp=value['payload'];ap=assignment['payload']
 join={'scheme-declares-value-axis':vp['axis_ref'] in sp['axis_refs'],'assignment-and-value-axis-match':ap['axis_ref']==vp['axis_ref'],'assignment-and-value-scheme-reference-match':ap['scheme_version_ref']==vp['scheme_ref'],'selected-value-scheme-literal-equals-selected-scheme-identity':vp['scheme_ref']==scheme['node_id'],'assignment-literal-value-equals-selected-value-identity':ap['value_ref']==value['node_id'],'selected-value-identity-in-selected-scheme-values':value['node_id'] in sp['value_refs'],'assignment-value-reference-in-selected-scheme-values':ap['value_ref'] in sp['value_refs']}
 check('individual-fixtures-are-not-presumed-one-literal-joined-instance',join=={'scheme-declares-value-axis':True,'assignment-and-value-axis-match':True,'assignment-and-value-scheme-reference-match':True,'selected-value-scheme-literal-equals-selected-scheme-identity':False,'assignment-literal-value-equals-selected-value-identity':False,'selected-value-identity-in-selected-scheme-values':False,'assignment-value-reference-in-selected-scheme-values':True},{'literal_observations':join,'whole_system_conformance':False,'mapping_reviewed':False})
 probes=[]
 for id,kind,change in [('unresolved-axis-string-still-shape-valid','classification-value',lambda x:x['payload'].update(axis_ref='axis:unresolved')),('mismatched-assignment-scheme-string-still-shape-valid','classification-assignment',lambda x:x['payload'].update(scheme_version_ref='classification-scheme:unresolved@99')),('mismatched-assignment-value-string-still-shape-valid','classification-assignment',lambda x:x['payload'].update(value_ref='classification-value:unresolved')),('empty-axis-list-still-shape-valid','classification-scheme',lambda x:x['payload'].update(axis_refs=[]))]:
  mutated=copy.deepcopy(docs[kind+'-fixture']);change(mutated);accepted=not list(b.c.Draft202012Validator(docs[kind+'-schema']).iter_errors(mutated));probes.append({'case_id':id,'schema_accepted':accepted,'actual_runtime_execution':False,'whole_source_conformance':False})
 if any(x['schema_accepted'] is not True for x in probes):raise ValueError('Actual schema boundary changed')
 record=record_controls();cubes=cube_controls()
 report={'schema_version':'definition-assurance-classification-coordinate-profile/v1-candidate','status':'PASS-for-versioned-records-finite-choice-cubes-and-actual-carrier-observations','authority_effect':'none','checker_bindings':[bindings['checker'],b.ref(b.UNIT/'build_candidate.py')],'input_refs':[b.ref(b.UNIT/'t.json'),b.ref(b.UNIT/'static-ir.json'),b.ref(b.UNIT/'legacy-source-section.md')],'runtime_bindings':runtime,'selected_inputs':bindings,'sibling_source_inputs':source_inputs,'profile_control_count':len(record),'rejected_profile_controls':sum(x['expected_rejection'] for x in record),'profile_controls':record,'finite_choice_cube_count':len(cubes),'rejected_choice_cubes':sum(x['expected_rejection'] for x in cubes),'finite_choice_cubes':cubes,'actual_check_count':len(checks),'actual_checks':checks,'actual_join_observations':join,'actual_boundary_probes':probes,'source_mapping_gaps':{'mapping_reviewed':False,'dedicated_axis_carrier_in_selected_type_registry':False,'exact_axis_reference_resolution_established':False,'individual_valid_fixtures_not_a_joined_source_model':True,'raw_answers_are_not_governed_value_identity':True,'scheme_version_subject_revision_and_immutable_assignment_maps_pending':True,'finite_choice_is_not_statistical_independence':True,'source_precedence_and_no_data_review_deferred':True,'before_downstream_temporal_obligation_deferred':True},'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'new_axes_values_assignments_created':0,'actual_admission_created':False,'actual_runtime_activated':False,'claim_ceiling':'Scoped finite coordinates and exact version/value records plus actual three carrier observations. Independently valid fixtures are not a coherent joined instance; shape does not prove resolution, cardinality semantics, world value correctness, immutable history, source fidelity or statistical/temporal independence.'}
 b.unchanged(list(bindings.values())+list(source_inputs.values())+report['input_refs']);b.r.verify(snap,b.ROOT);b.external_current(context)
 if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
 if write:b.put('coordinate-profile-checks.json',report)
 elif not b.r.same_json(report,json.loads((b.UNIT/'coordinate-profile-checks.json').read_bytes())):raise ValueError('Fresh coordinate profile differs')
 return report
def main():
 x=verify('--write' in b.sys.argv);print(json.dumps({'status':x['status'],'profile_controls':x['profile_control_count'],'rejected_profiles':x['rejected_profile_controls'],'finite_choice_cubes':x['finite_choice_cube_count'],'rejected_choice_cubes':x['rejected_choice_cubes'],'actual_checks':x['actual_check_count'],'actual_boundary_probes':len(x['actual_boundary_probes']),'source_embedding_reviewed':False,'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
