"""Prepare complete generic Method consumer comparison using exact current sources."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/CAV2-D32');prev=u.with_name('CAV2-D20');s=(prev/'inspect_carrier_consumers.py').read_text()
s=s.replace('Craft Method consumer','generic Method consumer').replace('20261012-craft-method','20261012-generic-method').replace('definitions/cal.definition.typed-connection-extension-rule/','definitions/CAV2-D20/').replace('9735','9852')
s=s.replace("and 'CAV2-D20@1.0.0-candidate.1' in x.get('semantic_definition_refs',[])","and 'CAV2-D32@1.0.0-candidate.1' in x.get('semantic_definition_refs',[])")
s=s.replace("ck('one-direct-current-binding',len(direct)==1 and direct[0]['artifact_type_ref']=='cal.artifact-type.method-binding/v1')","ck('no-direct-generic-summary-binding',direct==[])")
s=s.replace("ck('direct-binding-C30C31-distinct',direct[0]['admission_decision_ref']==c30['decision_id'] and binding['admission_row']['identity_ref']=='CAL-METHOD-BINDING-CRAFT-PRODUCT-CAV2-D20')","ck('C30-type-C31-binding-distinct',all(x['admission_row']['decision_overlay_status']=='admitted-current' for x in contracts) and binding['admission_row']['identity_ref']=='CAL-METHOD-BINDING-CRAFT-PRODUCT-CAV2-D20')\n complete_bindings=[x for x in contracts if 'CAV2-D32@1.0.0-candidate.1' in x['complete_semantic_definition_refs']];ck('two-complete-generic-artifact-bindings',{x['admission_row']['artifact_type_ref'] for x in complete_bindings}=={'cal.artifact-type.method-binding/v1','cal.artifact-type.identity-graph/v1'})")
s=s.replace("dp('exact-CraftMethod-Definition'","dp('exact-GenericMethod-Definition'")
start=s.index(" for label,text in {");end=s.index('\n carrier_probes=',start)
claims={'named-form-is-authority':'hyp:named Method specialization inherits execution authority','admission-is-application':'hyp:Method admission is its application decision','collection-handle-is-population':'hyp:a collection reference proves nonempty real contents','role-identification-is-repetition-proof':'hyp:field role labels prove successful repeated applications','workflow-is-Method':'hyp:every workflow engine is the Method'}
s=s[:start]+" for label,text in "+repr(claims)+".items():dp(label,lambda x,text=text:x['voices']['scientific_formal'].update(normative_statement=text),True)"+s[end:]
s=s.replace("for field in ['construction_approval','canonical_authority_mapping','owner_closure']:","for field in ['method_application_approval','generic_form_mapping','field_identification_mapping']:")
start=s.index(" core=json.loads");s=s[:start]+" for kind in schemas:\n  for field in b.METHOD_FIELDS:cp(kind,'unsupported-native-selector-'+field,lambda x,field=field:x.update({field:'hyp:unreviewed-mapping'}),False)\n cp('method-binding','generic-Method-reference-shape-valid',lambda x:x.update(method_ref='CAV2-D32'),True,True)\n cp('method-binding','named-Method-reference-shape-valid',lambda x:x.update(method_ref='hyp:named-specialization'),True,True)\n"+s[start:]
start=s.index(' wanted=');end=s.index('\n issues=[',start)
tt=['exact-eleven-field-Method-overlapping-roles-separate-decisions','unnamed-Method-unused-form-binding-absent','unused-form-handle-empty','unclassified-additional-field-handle-unused','outside-Method-field-role-not-a-selected-obligation','overlap-field-roles-remain-valid','no-exclusive-transformation-alternative','same-role-admission-decision-reuse-not-forbidden']
tf=['no-selected-Method-admission-application','no-independent-authority','no-admission-records-application-does-not-fabricate-one','no-application-records-Method-does-not-fabricate-one','no-field-role-records-Method-still-has-explicit-tuple']
negative=['same-Method-admission-application-decision-collapse','separate-decisions-required-even-across-different-Methods','named-specialization-missing','minimum-form-coordinates-missing','reusable-field-not-identifiable','specialized-field-not-identifiable','marked-field-empty-handle','no-declared-transformation-alternative']
s=s[:start]+' wanted='+repr(tt+tf+negative)+'''
 for name in wanted:
  case=cases[name];raw=copy.deepcopy(case['model']);isolated=name in ['same-Method-admission-application-decision-collapse','separate-decisions-required-even-across-different-Methods']
  if isolated:
   app='p0' if name.startswith('same-Method') else 'p1';decision=a.getfn(raw,'applicationDecision',app);method=a.getfn(raw,'applicationMethod',app)
   if [decision,method] not in raw['predicates']['ApplicationDecisionForMethodDeclared']:raw['predicates']['ApplicationDecisionForMethodDeclared'].append([decision,method])
  model=a.qualify(raw,ids);e=v.Denotation(ir['declarations'],model);t=all([e.truth(x) for x in T]);i=all([e.truth(x) for x in I]);assert t==case['expected_T'] and (case['expected_I'] is None or i==case['expected_I']);primitive={n:e.truth(v.renamed(z,ids)) for n,z in b.THEORY.items()}
  if isolated:assert [n for n,truth in primitive.items() if not truth]==['separate-decisions'],(name,primitive)
  comparison.append({'case_id':name,'T':t,'I':i,'model':model,'model_sha256':b.ir.digest(model),'primitive_results':primitive,'decision_separation_isolated':isolated,'exact_role_relations_retained':isolated,'claim_scope':'Generic Method candidate only;no carrier common denotation inferred'})
 unclassified={'population_id':'POP-REQ-AdditionalUnclassifiedField','population_statement':next(x['statement'] for x in ir['populations'] if x['population_id']=='POP-REQ-AdditionalUnclassifiedField'),'Method_field_membership_relation_encoded':False,'actual_additional_Method_field_membership_established':False,'interpretation':'A globally declared Field unclassified relative to a selected Method;actual membership and coordinate-to-field map pending.'}
 ck('unclassified-field-membership-gap-retained','MethodFieldDeclared' not in b.SIGNATURE and 'fieldMethod' not in b.FUNCTIONS)
'''+s[end:]
start=s.index(' issues=[');end=s.index('\n ];findings=',start)
issues=[
'No current registry summary directly names generic Method CAV2-D32,but complete immutable current MethodBinding/v1 and IdentityGraph/v1 artifacts explicitly bind it. Preserve exact summary and complete binding scopes;absence from a summary does not erase real semantic use.',
'C29 admits exact generic Method meaning;C30 admits six identity Artifact Types;C31 admits six carriers and five graph relations with schema/identity-contract PASS while implementation/runtime remain not_evaluable. Candidate body labels do not erase those separate positive overlays or accept this translation.',
'Definition schema accepts hypothetical inherited-authority,admission/application collapse,collection-cardinality,role-label repeatability and workflow identity overclaims. Pure rendering and complete source accounting do not accept those meanings.',
'MethodBinding whole schema and isolated semantic_errors differ:identity collapse can pass shape but fail the semantic helper,while generic/named Method refs,switched Product/Project kind and unresolved owner/evidence/challenge strings can pass both without actual subject or permission resolution.',
'IdentityGraph whole schema can accept duplicated nodes,unresolved endpoints and incorrect relation signatures while the pure semantic helper rejects them. Its exact admitted graph is separate from a generic Method minimum-form or application denotation.',
'None of the six compared identity schemas directly exposes the proposed eleven camel-case selectors;an added selector field is rejected. Indirect references may still describe a Method. Accepted collection contents/cardinality,form specialization,minimum-coordinate and rule-adequacy maps remain pending.',
'Reusable/specialized role markers provide conditional reference identifiability and permit overlap. The globally declared unclassified field population does not prove additional Method-field membership;coordinate/field-membership and actual repeatability maps remain explicit gaps.',
'Twenty-one freshly evaluated T/I comparisons include two decision-collapse models preserving exact role relations so only the separate-decisions primitive fails. This isolates the guard without proving real decision validity,owner acceptance,application permission,source fidelity,whole translation or whole proof.'
]
s=s[:start]+' issues='+repr(issues)[:-1]+s[end:]
s=s.replace('CRM-CONSUMER-FINDING-','GMD-CONSUMER-FINDING-').replace('CraftMethod','GenericMethod').replace('Fresh Craft Method consumer observations differ','Fresh generic Method consumer observations differ').replace('actual_construction_closure_or_authority_created','actual_Method_application_permission_or_authority_created')
s=s.replace("'direct_current_definition_binding_types':direct,","'direct_current_definition_binding_types':direct,'complete_generic_definition_binding_types':[x['admission_row']['artifact_type_ref'] for x in complete_bindings],'unclassified_field_observation':unclassified,")
s=s.replace('Exact meanings,whole six carrier schemas,pure projection/semantic helper observations and candidate-only T/I models;no accepted map,actual construction,closure,implementation/runtime conformance or whole proof.','Exact generic Method and complete current binding scopes,whole six identity schemas,pure helpers and isolated candidate-only T/I models;no accepted form/field/decision/application map,permission,repeatability,source fidelity or whole proof.')
ast.parse(s)
with (u/'inspect_carrier_consumers.py').open('x') as f:f.write(s)
s=(p.parent/'20261012-craft-method/capture_consumer.py').read_text().replace('definitions/CAV2-D20','definitions/CAV2-D32')
with (p/'capture_consumer.py').open('x') as f:f.write(s)
print('Prepared six-contract generic Method comparison and two isolated decision-separation models;not executed.')
