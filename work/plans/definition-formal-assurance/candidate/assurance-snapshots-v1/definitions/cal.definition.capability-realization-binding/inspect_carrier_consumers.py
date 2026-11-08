"""Full CRB coordinate observations and finite theory comparisons; maps remain pending."""
from pathlib import Path
import ast,copy,json,sys
import build_candidate as b
import verify_candidate as a
import verifier as v

def load(path):return json.loads(path.read_bytes())
def pure(path,names):
 nodes=[x for x in ast.parse(path.read_bytes()).body if isinstance(x,ast.FunctionDef) and x.name in names]
 assert {x.name for x in nodes}==set(names)
 namespace={'json':json,'Any':object};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace);return namespace

# Selectors are proposed correspondences, not denotation equalities or accepted maps.
SELECTORS={
'bindingCapabilityRevision':('capability_version_ref','Resolve exact Capability revision and its capability_ref; text is not resolution.'),
'bindingImplementationRevisions':('realization_refs','Resolve one-or-more exact Implementation revision members from broader realization records.'),
'bindingRealizationRole':('realization_refs[*].realization_kind','Interpret realization kinds without treating kind names as resolved Implementation revisions.'),
'bindingAdoptionPosture':('binding_state','Separate adopted/candidate posture from actual adoption and from the lifecycle interpretation.'),
'bindingCompatibility':(None,'Map compatibility meaning from explicit contracts or external evidence; no direct compatibility field is selected.'),
'bindingConformanceEvidence':('conformance_refs','Resolve applicable conformance evidence and its purpose; candidate empty lists and opaque references do not prove conformance.'),
'bindingDeploymentApplicability':('scope_ref','Review whether this general scope supplies deployment applicability; do not silently equate them.'),
'bindingOwner':('owner_ref','Resolve the owner principal, role and bounded authority separately from nomination.'),
'bindingLifecycle':('binding_state','Provide a lifecycle map distinct from the separately proposed adoption-posture map.'),
'bindingSuccessionRoute':('successor_refs / owner_route','Map successor references and an owner route to succession handling; forward identity strings alone are not a route or history.'),
'bindingChallengeHandling':('challenge_route','Resolve an accountable challenge handler and process, rather than only a nonempty route.'),
'bindingAssociation':('node_id','Map canonical association identity and Binding revision identity; node_id and binding_version roles require review.'),
'bindingCanonicalAuthority':(None,'Declare exactly one canonical relation authority for the association through an accepted representation map.'),
'bindingAdoptionEvidence':('adoption_decision_ref','Map a decision reference to appropriate adoption evidence without equating the decision and evidence collection.'),
'bindingDeploymentEvidence':(None,'Select deployment evidence separately; no direct deployment-evidence field is present.'),
'bindingOutcomeEvidence':('observation_refs','Map observations to outcome evidence and claim scope without inferring successful operation or Product value.'),
'bindingProjection':(None,'Select optional at-most-one Typed Relation projection independently of the generated human RECORD.md view.'),
'bindingDigest':(None,'Specify exact Binding content bytes and digest algorithm when a Typed Relation projection is selected.'),
'associationCanonicalAuthority':(None,'Review the common association-to-authority carrier and exactly-one declared counterpart.'),
'projectionBinding':(None,'Map the optional Typed Relation to the exact Binding revision.'),
'projectionAssociation':(None,'Map the optional Typed Relation to the same association without becoming second writable authority.'),
'projectionDigest':(None,'Map the projection digest to exact Binding content; nominated equality does not establish authenticity.'),
'changeOriginalBinding':(None,'Select authenticated before-state revision or explicit source-owned history for a change.'),
'changeDesiredCapability':(None,'Select intended Capability endpoint independently of a potentially in-place successor.'),
'changeDesiredImplementations':(None,'Select intended exact Implementation member set and compare members extensionally.'),
'changeDesiredAdoptionPosture':(None,'Select intended posture independently of the successor record and actual adoption.'),
'changeSuccessorBinding':('successor_refs','Resolve a distinct successor revision matching changed intended state; self-reference is not required succession.')}

def inspect(write=False):
 root,unit=b.ROOT,b.UNIT;prepared=root/'docs/plans/definition-formal-assurance/candidate/prepared-episodes-v1/20261012-capability-realization-binding'
 typed_receipt=load(unit/'types-logic-receipt.json');frozen=typed_receipt['inputs']+typed_receipt['checker_bindings'];prior=load(b.BASE/'definitions/cal.definition.capability-instance/delivery-manifest.json')['files'];context=load(unit/'context.json');snapshot=b.snapshot();runtime=v.f.current_bindings()
 b.unchanged(frozen+prior+context['sources']);assert len(prior)==10287 and b.r.verify(snapshot,root)['files']==201
 terminal=load(prepared/'typed-stage-audit-command-result.json');assert terminal['exit_code']==0 and not(prepared/terminal['stderr']).read_bytes()
 discovery=load(prepared/'consumer-discovery.json');b.unchanged(list(discovery['selected_inputs'].values()));assert discovery['actual_check_count']==167 and load(prepared/'consumer-discovery-command-result.json')['exit_code']==0
 selected={'typed_receipt':b.ref(unit/'types-logic-receipt.json'),'typed_audit':b.ref(prepared/'typed-stage-audit-command-result.json'),'discovery':b.ref(prepared/'consumer-discovery.json'),'checker':b.ref(Path(__file__).resolve())};checks=[]
 def ck(name,ok):assert ok,name;checks.append({'check_id':name,'result':True})
 registry_path=root/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';registry=load(registry_path);selected['registry']=b.ref(registry_path);current=[row for row in registry['admitted_contracts'] if row['artifact_type_ref'] in registry['current_by_identity'].values()]
 ck('143contracts121current',len(registry['admitted_contracts'])==143 and len(current)==121)
 core=load(unit/'t.json')['payload'];ir=load(unit/'static-ir.json');complete=[]
 for row in current:
  artifact=load(root/row['artifact_path']);ck('catalog-current-bytes-'+row['artifact_type_ref'],b.ref(root/row['artifact_path'])['sha256']==row['artifact_sha256'] and b.ref(root/row['schema_path'])['sha256']==row['schema_sha256'])
  versions=artifact.get('semantic_definition_refs',[]);old=artifact.get('definition_binding',{})
  if old.get('definition_id'):versions=versions+[old['definition_id']+'@'+old.get('version','')]
  if core['source']['version_ref'] in versions:complete.append(row['artifact_type_ref'])
 ck('one-current-complete-CRBv2-binding',complete==['cal.artifact-type.capability-realization-binding/v2'])
 contracts={};schemas={};fixtures={};projections=[]
 for version in ['v1','v2']:
  folder=root/'authority/artifact-types/capability-realization-binding'/version;artifact=load(folder/'artifact.json');schema=load(folder/'schema.json');fixture_path=folder/artifact['validation_contract']['positive_witness'];fixture=load(fixture_path);b.c.Draft202012Validator.check_schema(schema);validator=b.c.Draft202012Validator(schema)
  for label,path in [('artifact',folder/'artifact.json'),('schema',folder/'schema.json'),('fixture',fixture_path),('artifact-projection',folder/'ARTIFACT.md'),('fixture-projection',folder/artifact['validation_contract']['positive_projection'])]:selected[version+'-'+label]=b.ref(path)
  ck(version+'-positive-fixture-shape',not list(validator.iter_errors(fixture)))
  ck(version+'-candidate-bodies-positive-overlay-distinct',artifact['status']==fixture['status']=='candidate-unadmitted' and artifact['authority_effect']==fixture['authority_effect']=='none')
  row=next(row for row in registry['admitted_contracts'] if row['artifact_type_ref']==artifact['artifact_type_ref']);ck(version+'-current-historical-overlay',row['lifecycle_state']==('admitted-historical' if version=='v1' else 'admitted-current'))
  gp=root/artifact['source_direction']['shared_generator_path'] if version=='v1' else folder/artifact['source_direction']['generator'];selected[version+'-generator']=b.ref(gp);generator=pure(gp,['render_artifact','render_instance']);before=copy.deepcopy(fixture);one=generator['render_instance'](artifact,fixture);two=generator['render_instance'](artifact,fixture)
  ck(version+'-two-exact-fixture-projections',one==two==(folder/artifact['validation_contract']['positive_projection']).read_text() and before==fixture);ck(version+'-exact-artifact-projection',generator['render_artifact'](artifact)==(folder/'ARTIFACT.md').read_text())
  declared_generator=artifact['source_direction'].get('shared_generator_sha256',artifact['source_direction'].get('generator_sha256'));ck(version+'-exact-generator-schema-bindings',declared_generator==selected[version+'-generator']['sha256'] and artifact['schema_digest']==selected[version+'-schema']['sha256'])
  contracts[version],schemas[version],fixtures[version]=artifact,validator,fixture;projections.append({'version':version,'fixture_projection':selected[version+'-fixture-projection'],'pure_functions_only':True,'owned_instance':False})
 ck('v1-v2-schemas-identical-meanings-distinct',schemas['v1'].schema==schemas['v2'].schema and contracts['v1']['semantic_definition_refs']==['cal.definition.product-capability@1.0.0-candidate.1'] and contracts['v2']['semantic_definition_refs']==[core['source']['version_ref']])
 decisions={}
 for key,folder in [('C60','0060-capability-realization-binding-v1-admission'),('C70','0070-definition-complete-lab-model-admission')]:
  path=root/'docs/decisions'/folder/'decision.json';decision=load(path);selected[key+'-decision']=b.ref(path);authorization=root/decision['authorization']['path'];selected[key+'-authorization']=b.ref(authorization);ck(key+'-exact-owner-authorized-scope',decision['status']=='owner-admitted' and selected[key+'-authorization']['sha256']==decision['authorization']['sha256']);decisions[key]=decision
 d60,d70=decisions['C60'],decisions['C70'];ck('C60-one-type-no-instance-activation',d60['admission_result']['artifact_types_admitted']==1 and d60['admission_result']['instances_admitted']==d60['admission_result']['consumer_activations']==0 and d60['admitted_artifact_type']['sha256']==selected['v1-artifact']['sha256']);ck('C70-exact-type-effects-no-CRB-instance',d70['effects']['artifact_types_admitted']==93 and d70['effects']['artifact_type_predecessors_to_historical']==9 and d70['effects']['consumer_activations']==d70['effects']['runtime_activations']==d70['effects']['typed_relation_instances_admitted']==0 and 'No ordinary Artifact Type instance other than the exact integrated Governed Model instance is admitted.' in d70['excluded_effects'])
 # The current package writes validation.json; execute only its exact two-node non-collapse expression.
 validator_path=root/'authority/artifact-types/capability-realization-binding/v2/validate.py';selected['current-package-validator']=b.ref(validator_path);main=next(n for n in ast.parse(validator_path.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='main');nodes=[]
 for node in main.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='endpoint_results' for t in node.targets):nodes.append(node)
  if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and node.value.args and isinstance(node.value.args[0],ast.Constant) and node.value.args[0].value=='binding-capability-realization-non-collapse':nodes.append(node)
 ck('exact-current-pure-expression-extracted',len(nodes)==2);expression=compile(ast.Module(body=nodes,type_ignores=[]),str(validator_path),'exec')
 def helper(doc):
  rows=[];namespace={'artifact':contracts['v2'],'witness':doc,'check':lambda name,ok,detail:rows.append({'check_id':name,'result':ok,'detail':detail})};exec(expression,namespace);assert len(rows)==1;return rows[0]
 meaning_sources=[context['source_selection']]+core['depends_on'];meanings=[];ds=root/'authority/artifact-types/definition/v1/schema.json';dg=root/'authority/artifact-types/definition/v1/generator.py';selected['Definition-schema']=b.ref(ds);selected['Definition-generator']=b.ref(dg);dv=b.c.Draft202012Validator(load(ds));generator=pure(dg,['esc','bullets','render'])
 for source in meaning_sources:
  path=root/source['path'];doc=load(path);projection=path.with_name('DEFINITION.md');selected[source['definition_id']]=b.ref(path);selected[source['definition_id']+'-projection']=b.ref(projection);ck(source['definition_id']+'-exact-current',b.source_ref(snapshot,source['definition_id'])==source);ck(source['definition_id']+'-Definition-shape',not list(dv.iter_errors(doc)));before=copy.deepcopy(doc);rendered=generator['render'](doc);ck(source['definition_id']+'-two-pure-projections',rendered==generator['render'](doc)==projection.read_text() and doc==before);meanings.append({'source':source,'projection':selected[source['definition_id']+'-projection'],'accepted_map_refs':[],'whole_theory_imported':False})
 definition_probes=[];source_doc=load(root/core['source']['path'])
 def dp(name,mutate,expected):
  doc=copy.deepcopy(source_doc);mutate(doc);errors=sorted(e.message for e in dv.iter_errors(doc));ck('Definition-probe-'+name,(not errors)==expected);definition_probes.append({'case_id':name,'schema_accepted':not errors,'schema_errors':errors,'model_sha256':b.ir.digest(doc),'accepted_semantic_map':False})
 dp('exact-source',lambda x:None,True)
 for field in dv.schema['required']:dp('missing-'+field,lambda x,field=field:x.pop(field),False)
 for field in ['accepted_mapping','actual_adoption','whole_proof']:dp('unknown-'+field,lambda x,field=field:x.update({field:True}),False)
 for name,text in [('shape-proves-adoption','A schema-valid Binding is adopted and deployed.'),('projection-is-second-writer','The projected relation is another writable canonical authority.'),('zero-Implementation-endpoints','A Binding requires no Implementation revisions.'),('collection-name-change-is-endpoint-change','Changing a collection handle always changes an Implementation endpoint.'),('posture-proves-authority','Adopted posture establishes an authority effect.')]:dp(name,lambda x,text=text:x['voices']['scientific_formal'].update(normative_statement=text),True)
 probes=[]
 def cp(name,mutate,shape,guard=None,version='v2'):
  doc=copy.deepcopy(fixtures[version]);mutate(doc);before=copy.deepcopy(doc);errors=sorted(e.message for e in schemas[version].iter_errors(doc));result=None
  try:result=helper(doc)
  except (KeyError,TypeError):pass
  ck('carrier-probe-'+version+'-'+name,(not errors)==shape and (guard is None or (result is not None and result['result']==guard)) and doc==before);probes.append({'case_id':name,'version':version,'schema_accepted':not errors,'schema_errors':errors,'isolated_current_expression':result,'current_whole_package_executed':False,'model':doc,'model_sha256':b.ir.digest(doc),'accepted_map':False})
 for version in ['v1','v2']:cp('exact-fixture',lambda x:None,True,True,version)
 for field in schemas['v2'].schema['required']:cp('missing-'+field,lambda x,field=field:x.pop(field),False)
 for field in ['node_id','binding_version','capability_ref','capability_version_ref','scope_ref','owner_ref','owner_route','challenge_route']:
  cp('opaque-'+field,lambda x,field=field:x.update({field:'hyp:unresolved-'+field}),True,True);cp('empty-'+field,lambda x,field=field:x.update({field:''}),False)
 cp('Binding-ID-is-Capability',lambda x:x.update(node_id=x['capability_ref']),True,False);cp('Binding-ID-is-Capability-version',lambda x:x.update(node_id=x['capability_version_ref']),True,False)
 for target in ['node_id','capability_ref','capability_version_ref']:cp('realization-is-'+target,lambda x,target=target:x['realization_refs'][0].update(realization_ref=x[target]),True,False)
 cp('empty-realizations',lambda x:x.update(realization_refs=[]),False,True);cp('duplicate-realization-records',lambda x:x['realization_refs'].append(copy.deepcopy(x['realization_refs'][0])),True,True)
 cp('multiple-realization-records',lambda x:x['realization_refs'].append({**x['realization_refs'][0],'realization_ref':'hyp:second-realization'}),True,True)
 for kind in ['capability-instance','agent-capability','implementation','service','workflow']:cp('realization-kind-'+kind,lambda x,kind=kind:x['realization_refs'][0].update(realization_kind=kind),True,True)
 cp('empty-realization-reference',lambda x:x['realization_refs'][0].update(realization_ref=''),False,True)
 cp('direct-Implementation-version-field',lambda x:x['realization_refs'][0].update(implementation_version_ref='hyp:implementation@1'),False,True)
 cp('candidate-null-decision-empty-conformance',lambda x:x.update(adoption_decision_ref=None,conformance_refs=[]),True,True)
 cp('adopted-without-required-evidence',lambda x:x.update(binding_state='adopted'),False,True)
 cp('adopted-with-opaque-evidence',lambda x:x.update(binding_state='adopted',adoption_decision_ref='hyp:decision',conformance_refs=['hyp:conformance']),True,True)
 cp('superseded-without-successor',lambda x:x.update(binding_state='superseded'),False,True)
 cp('superseded-with-self-successor',lambda x:x.update(binding_state='superseded',successor_refs=[x['node_id']]),True,True)
 cp('changed-endpoint-same-node-version',lambda x:x['realization_refs'][0].update(realization_ref='hyp:changed'),True,True)
 cp('changed-posture-same-node-version',lambda x:x.update(binding_state='retired'),True,True)
 for field in ['canonical_relation_authority_ref','typed_relation_projection','binding_digest','compatibility_ref','deployment_applicability_ref','adoption_evidence_refs','deployment_evidence_refs','outcome_evidence_refs','change_before_snapshot','change_desired_state']:
  cp('unreviewed-direct-'+field,lambda x,field=field:x.update({field:'hyp:unreviewed'}),False,True)
 cp('authority-self-grant',lambda x:x.update(authority_effect='activate'),False,True)
 cp('operation-value-authority-prose-overclaim',lambda x:x.update(limitations=['This Binding is operational,valuable andauthorized.']),True,True)
 for relative in contracts['v2']['validation_contract']['negative_witnesses']:
  path=root/'authority/artifact-types/capability-realization-binding/v2'/relative;selected['negative-'+relative]=b.ref(path);ck('negative-fixture-'+relative,bool(list(schemas['v2'].iter_errors(load(path)))))
 matrix=[]
 coordinates={n:(carrier,sort) for fields,carrier in b.GROUPS for n,sort in fields.items()};ck('all27coordinate-obligations-covered',set(coordinates)==set(SELECTORS) and len(coordinates)==27)
 for number,(name,(carrier,sort)) in enumerate(coordinates.items(),1):
  selector,obligation=SELECTORS[name];matrix.append({'map_id':'CRB-CONSUMER-MAP-'+str(number).zfill(3),'candidate_symbol':name,'candidate_argument_sort':carrier,'candidate_result_sort':sort,'proposed_carrier_selector':selector,'direct_top_level_selector_present':selector in schemas['v2'].schema['properties'] if selector else False,'meaning_obligation':obligation,'status':'pending-owner-correspondence','accepted_map_refs':[]})
 ids={x['symbol_id']:b.ir.qualified(core['source'],core['scope'],x['symbol_id']) for x in core['declarations']};T=[x for x in ir['clauses'] if x['disposition']=='encoded'];I=[x for x in ir['populations'] if x['requirement']=='required'];cases={x['case_id']:x for x in a.controls()};comparisons=[]
 names=['exact-association-members-authority-evidence-projection-and-changes','no-selected-bindings-projections-or-changes','no-independent-authority-effect-population','no-conformance-population','optional-projections-all-absent','no-selected-changes','all-endpoint-collections-singleton','separate-evidence-contents-permitted','missing-BindingGovernedDeclared','missing-BindingBoundedDeclared','capability-revision-not-declared-exact','implementation-revision-not-declared-exact','member-not-in-nominated-collection','nominated-member-missing-Binding-counterpart','missing-single-canonical-authority','second-canonical-authority-for-association','nominated-authority-mismatches-association','evidence-purpose-role-collapsed','missing-adoption-evidence-purpose-binding','extra-wrong-evidence-purpose-binding','projection-missing-readonly-declaration','projection-second-writable-authority','projection-digest-differs','second-projection-for-selected-Binding','projection-relation-without-nomination','projection-points-to-other-Binding','projection-association-mismatch','changed-state-inplace-successor-cCap','changed-state-inplace-successor-cImpl','changed-state-inplace-successor-cPosture','missing-required-successor-relation','wrong-successor-intended-state','Capability-change-removed-no-successor-required','Implementation-member-change-removed-no-successor-required','posture-change-removed-no-successor-required','no-change-successor-reference-may-be-original','no-change-unused-successor-binding-absent','without-projection-unused-projection-binding-absent','without-projection-unused-digest-binding-absent','unused-digest-handle-empty','unused-projection-handle-empty']
 isolates={}
 for name in ['missing-BindingGovernedDeclared','missing-BindingBoundedDeclared']:isolates[name]=['governed-and-bounded']
 for name in ['member-not-in-nominated-collection','nominated-member-missing-Binding-counterpart']:isolates[name]=['exact-endpoints-and-member-cardinality']
 for name in ['missing-single-canonical-authority','second-canonical-authority-for-association','nominated-authority-mismatches-association']:isolates[name]=['single-canonical-association-authority']
 for name in ['evidence-purpose-role-collapsed','missing-adoption-evidence-purpose-binding','extra-wrong-evidence-purpose-binding']:isolates[name]=['separate-evidence-purpose-roles']
 for name in ['projection-missing-readonly-declaration','projection-second-writable-authority','projection-digest-differs','second-projection-for-selected-Binding','projection-relation-without-nomination','projection-points-to-other-Binding','projection-association-mismatch']:isolates[name]=['optional-readonly-digest-bound-projection']
 for name in ['changed-state-inplace-successor-cCap','changed-state-inplace-successor-cImpl','changed-state-inplace-successor-cPosture','missing-required-successor-relation','wrong-successor-intended-state']:isolates[name]=['endpoint-or-posture-change-successor']
 def compare(name,raw,expected_t,expected_i,failures=None):
  model=a.qualify(raw,ids);e=v.Denotation(ir['declarations'],model);clauses=[{'clause_id':x['clause_id'],'truth':e.truth(x['formal_statement'])} for x in T];populations=[{'population_id':x['population_id'],'truth':e.truth(x['statement'])} for x in I];t,i=all(x['truth'] for x in clauses),all(x['truth'] for x in populations);ck('typed-'+name,t==expected_t and(expected_i is None or i==expected_i));other=v.Denotation(ir['declarations'],model);primitives={n:other.truth(v.renamed(formula,ids)) for n,formula in b.THEORY.items()}
  if failures is not None:ck('isolated-'+name,[n for n,truth in primitives.items() if not truth]==failures)
  comparisons.append({'case_id':name,'model':model,'model_sha256':b.ir.digest(model),'T':t,'I':i,'primary_clause_results':clauses,'population_results':populations,'primitive_results':primitives,'semantic_guard_isolated':failures is not None,'expected_only_failed_primitives':failures or [],'T_I_steps':e.steps,'primitive_steps':other.steps,'accepted_common_carrier_map':False})
 for name in names:
  case=cases[name];compare(name,copy.deepcopy(case['model']),case['expected_T'],case['expected_I'],isolates.get(name))
 empty=a.base_model();empty['predicates']['ImplementationCollectionContainsDeclared']=[x for x in empty['predicates']['ImplementationCollectionContainsDeclared'] if x[0]!='colMulti'];a.refresh(empty);compare('isolated-nonempty-collection-with-no-members',empty,False,False,['exact-endpoints-and-member-cardinality'])
 issues=[
'C60 admits one historical Artifact Type andzeroinstances;C66 admits exact CRB meaning;C70 admits currentv2type butordinaryinstance onlyintegrated GovernedModel. None accepts this translation oradopts aBinding.',
'V1 andv2schemas arebyte-identical whileprimary meanings differ: historical ProductCapability versus specializedCRB. Shape inheritance isnot complete source correspondence.',
'The carrier accepts five realization kinds andthefixture namesa workflow. The source requires exact Implementation revisions;everykind needs explicit version/Implementation resolution,not an inferred alias.',
'Nonempty realization arrays passduplicate records andopaque endpoints. Candidate T separately enforces actual nominated membership andexact-version declarations. No collection shape proves concrete resolution.',
'Current package noncollapse expression rejectsrawBinding/Capability/realization ID collapse independently ofschema. Its exact raw-string policy isnot an acceptedcommon identity-carrier map orwholepackage acceptance.',
'binding_state suppliescandidate/adopted/retired/superseded labels. Adoption posture andoperational lifecycle remain distinctcandidate types andneed separate maps;opaque adopteddecision/evidence strings are not actualadoption.',
'No directcanonical relationauthority fieldorcommonassociationauthority mapisselected. Exactly-one candidate guardsrejectmissing/second authorities,while successfulcarrier shapecannotdischarge thatsource condition.',
'Human RECORD.md projection isnot the optional digest-boundTypedRelation projection. No directTypedRelation/digest/read-only fieldisselected. Concrete ownership,digestbyte selection andwrite enforcement remain unresolved.',
'Conformance refs,adoption decision andobservation refs aredifferentcarrierroles. Fourpurposeevidence functions sharea candidatecarrier withoutforcingdifferentcontent;directpurpose fieldsreject andmapping remains unaccepted.',
'Supersededstate demandssuccessorstrings butselfsuccessorpasses shape/isolatedexpression. Changedendpoint orposture cankeepthe same node/version in standalonecopies. Before/intended-state anddistinctrevision succession need ownerhistory maps.',
'Candidate member-setdelta isextensional. Aliased equalmembercollections require no successor;changedCapability/member/posture requires distinctmatchedsuccessor. Nominalversion strings andforwardreferences donotprove actualhistory orrevisioncreation.',
'Compatibility,deployapplicability,owner/challenge andcontract rolesneedprecisemaps. General scope,policy listsandowner stringsdo notprovecompatibility,permission,actualdeployment,operation orProductvalue.',
'FreshT/Icomparisons andisolatedprimitives testqualifiedsuppliedmodels. Separatewitnesses,Definition schemaacceptance andpureprojection bytesdo notacceptfidelity,sharedmeaning,wholetranslation orwholeproof.']
 findings=[{'finding_id':'CRB-CONSUMER-FINDING-'+str(n).zfill(3),'issue':issue,'status':'unresolved','accepted_map_refs':[],'owner_route':'role:definition-owner with endpoint,authority,projection,evidence,lifecycle andsuccession owners'} for n,issue in enumerate(issues,1)]
 b.unchanged(frozen+prior+context['sources']+list(selected.values()));ck('201sources-current',b.r.verify(snapshot,root)['files']==201);ck('runtime-unchanged',runtime==v.f.current_bindings())
 report={'schema_version':'definition-assurance-CRB-consumer-inspection/v1-candidate','result':'PASS-exact-CRB-source-coordinate-and-finite-consumer-comparisons','authority_effect':'none','source':core['source'],'selected_inputs':selected,'checks':checks,'check_count':len(checks),'meaning_observations':meanings,'complete_current_definition_binding_types':complete,'historical_primary_meanings':contracts['v1']['semantic_definition_refs'],'current_primary_meanings':contracts['v2']['semantic_definition_refs'],'positive_C60_result':d60['admission_result'],'positive_C70_effects':d70['effects'],'source_coordinate_correspondence':matrix,'source_coordinate_account_complete':True,'accepted_semantic_correspondence_complete':False,'definition_shape_probes':definition_probes,'definition_shape_probe_count':len(definition_probes),'definition_shape_acceptances':sum(x['schema_accepted'] for x in definition_probes),'carrier_shape_probes':probes,'carrier_shape_probe_count':len(probes),'carrier_shape_acceptances':sum(x['schema_accepted'] for x in probes),'projection_observations':projections,'typed_comparison_models':comparisons,'typed_comparison_count':len(comparisons),'isolated_primitive_comparison_count':sum(x['semantic_guard_isolated'] for x in comparisons),'unresolved_consumer_findings':findings,'accepted_semantic_map_refs':[],'current_package_expression_extracted_read_only':True,'bound_package_validator_executed':False,'canonical_or_candidate_carrier_writer_executed':False,'native_or_live_consumer_executed':False,'actual_Binding_adoption_deployment_conformance_operation_value_or_authority_created':False,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_inventory_refresh_complete':False,'frozen_inputs_preserved':17,'frozen_checker_bindings_preserved':5,'prior_candidate_files_preserved':10287,'source_files_current':201,'runtime_bindings':runtime,'claim_ceiling':'Complete proposed coordinate observations,exact carrier/source/projection andfinite T/I comparisons only;accepted maps,actualoutcomes,fidelity andwholeproof remainpending.'}
 if write:b.put('carrier-consumer-inspection.json',report)
 else:assert b.r.same_json(report,load(unit/'carrier-consumer-inspection.json')),'Fresh CRB consumer observations differ'
 return report
if __name__=='__main__':
 r=inspect('--write' in sys.argv);print(json.dumps({k:r[k] for k in ['result','check_count','definition_shape_probe_count','definition_shape_acceptances','carrier_shape_probe_count','carrier_shape_acceptances','typed_comparison_count','isolated_primitive_comparison_count','source_coordinate_account_complete','accepted_semantic_correspondence_complete','semantic_ready']},indent=2))
