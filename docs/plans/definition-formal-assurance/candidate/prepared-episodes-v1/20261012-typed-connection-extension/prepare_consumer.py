"""Prepare exact C64 versus eight current pair/instance/projection/contestability carriers."""
from pathlib import Path
import ast
p=Path(__file__).resolve().parent;u=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.typed-connection-extension-rule');prev=u.with_name('cal.definition.constraint-cycle-safety-invariant')
s=(prev/'inspect_carrier_consumers.py').read_text()
s=s.replace('20261012-constraint-cycle-safety','20261012-typed-connection-extension').replace('../cal.definition.principal-reference/','../cal.definition.constraint-cycle-safety-invariant/')
s=s.replace("+typed['retained_initial_effect_payload_refs']","+typed['retained_successful_preparation_refs']+typed['retained_preparation_failure_refs']")
s=s.replace(";invariant=[x for x in current if b.source_ref(snap,'cal.definition.invariant')['version_ref'] in x['semantic_definition_refs']]","")
s=s.replace("ck('no-current-direct-invariant-carrier',direct==[]);ck('no-current-generic-Invariant-carrier',invariant==[])","ck('no-current-direct-C64-rule-carrier',direct==[])")
s=s.replace("'OntologyEdge':'ontology-edge','Review':'review'","'OntologyEdge':'ontology-edge','CapabilityBinding':'capability-realization-binding','ChallengeContract':'challenge-contract'")
s=s.replace("'C53-Definition-distinct-from-current-carriers',load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0053-FULL-DEFINITION-QUEUE-ADMISSION'","'C64-Definition-distinct-from-current-carriers',load('source-checks.json')['current_registry_admission_ref']=='CAL-DECISION-0064-TYPED-CONNECTION-EXTENSION-RULE-ADMISSION'")
start=s.index(" dr=docs['source'];");end=s.index('\n probes=[]',start)
s=s[:start]+""" dr=docs['source'];ck('positive-C64-ordered-pair-question-and-scope-source',all(x in dr['voices']['scientific_formal']['normative_statement'] for x in ['finite closed set of exact ordered','same unique semantic question','Ontology-local']))
 ck('two-symbolic-consumer-routes-not-activation',dr['primary_consumer_refs']==['CAL-AXIS-ORTHOGONAL-RELATION-MODEL-0002','cal.artifact-type.relation-kind/successor'])
 rk=docs['RelationKind_fixture']['payload'];pairs={(x['source_kind'],x['target_kind']) for x in rk['allowed_endpoint_pairs']};source_kinds={x for x,y in pairs};target_kinds={y for x,y in pairs};cross={(x,y) for x in source_kinds for y in target_kinds};ck('RelationKind-fixture-exact-index-projections',source_kinds==set(rk['source_kinds']) and target_kinds==set(rk['target_kinds']))
 ck('RelationKind-fixture-Cartesian-cross-and-self-pair-observations',('experiment-run','product') in cross-pairs and ('product','product') in pairs and len(pairs)<len(cross))
 ck('binding-v2-has-lifecycle-and-contract-coordinates',all(n in docs['CapabilityBinding_schema']['properties'] for n in ['binding_version','capability_version_ref','binding_state','adoption_decision_ref','contract','realization_refs','conformance_refs','owner_route','challenge_route']) and 'payload' not in docs['CapabilityBinding_schema']['properties'])
 ck('ChallengeContract-covered-subject-and-owner-shapes',all(n in docs['ChallengeContract_schema']['properties']['payload']['properties'] for n in ['challengeable_subject_kinds','owner_route','resolution_gate_ref','required_evidence_kinds']))
""" +s[end:]
s=s.replace('exact-selected-ConstraintCycleSafety-Definition','exact-selected-TypedConnectionExtension-Definition')
start=s.index(" for n,text in {");end=s.index('\n carrier_probes=[]',start)
s=s[:start]+""" for n,text in {'Cartesian-is-authorized':'hyp:source and target lists authorize Cartesian connections','registration-is-connection':'hyp:registered kinds create every connection','reverse-is-implicit':'hyp:every ordered pair authorizes its reverse','validation-is-admission':'hyp:candidate validation admits the connection','local-is-global':'hyp:local ontology use creates global pairs','dual-projection-writers':'hyp:generic and specialized projections are both writable authority','question-change-is-reuse':'hyp:reuse may change unique question','conformance-creates-authority':'hyp:connection conformance proves runtime authority'}.items():probe(n,lambda x,text=text:x['voices']['scientific_formal'].update(normative_statement=text),True)""" +s[end:]
s=s.replace('actual_constraint_guard_or_authority_enforced','actual_connection_or_instance_authority_enforced').replace('overclaimed-watch-safety-and-authority','overclaimed-pair-admission-and-instance-authority').replace('hyp:cycle safety,no obstruction,valid witness,owner acceptance and promotion proved','hyp:global pairs,endpoint resolution,qualifier validity,instance conformance and runtime authority proved')
s=s.replace('hyp:unresolved-or-wrong-constraint','hyp:unresolved-or-wrong-pair')
start=s.index(" cp('Review'");end=s.index('\n comparison=[]',start)
s=s[:start]+""" cp('RelationKind','open-qualifier-contract-rejected',lambda x:x['payload']['qualifier_contract'].update(closed=False),False)
 cp('RelationKind','wildcard-pair-kind-rejected',lambda x:x['payload'].update(allowed_endpoint_pairs=[{'source_kind':'*','target_kind':'product'}]),False)
 cp('RelationKind','duplicate-pair-row-rejected',lambda x:x['payload']['allowed_endpoint_pairs'].append(dict(x['payload']['allowed_endpoint_pairs'][0])),False)
 cp('RelationKind','missing-required-value-axis-is-not-cross-validated',lambda x:x['payload']['qualifier_contract'].update(required_axes=['hyp:not-in-properties']),True)
 cp('RelationKind','question-prose-change-shape-valid',lambda x:x['payload'].update(unique_question='hyp:different-semantic-question'),True)
 cp('ChallengeContract','opaque-owner-and-gate-not-contestability-proof',lambda x:x['payload'].update(owner_route='hyp:unreachable-owner',resolution_gate_ref='hyp:unresolved-gate'),True)
 cp('CapabilityBinding','specialized-canonical-map-not-a-schema-field',lambda x:x.update(canonical_authority_mapping='projects-as'),False)
 cp('CapabilityBinding','candidate-without-adoption-is-valid-shape',lambda x:None,True)
 cp('CapabilityBinding','adopted-without-decision-or-conformance-rejected',lambda x:x.update(binding_state='adopted'),False)
 cp('CapabilityBinding','adopted-with-opaque-decision-and-conformance-shape-valid',lambda x:x.update(binding_state='adopted',adoption_decision_ref='hyp:unresolved-decision',conformance_refs=['hyp:unverified-conformance']),True)
 cp('OntologyEdge','local-without-global-binding-shape-valid',lambda x:x['payload'].update(edge_mode='local-interpretation',global_typed_relation_binding=None,local_interpretation={'interpretation':'hyp:local-only','local_scope':'hyp:exact-ontology','owner_ref':'hyp:owner','evidence_refs':['hyp:evidence']}),True)
 cp('OntologyEdge','local-and-global-binding-together-rejected',lambda x:x['payload'].update(edge_mode='local-interpretation',local_interpretation={'interpretation':'hyp:local-only','local_scope':'hyp:ontology','owner_ref':'hyp:owner','evidence_refs':['hyp:evidence']}),False)
""" +s[end:]
start=s.index(' wanted=[');end=s.index('\n for n,expected in wanted:',start)
tt=['closed-ordered-pairs-candidate-reuse-distinct-admitted-local-and-instance','register-additional-kind-without-connection','local-unused-global-bindings-absent','nonconforming-unused-pair-binding-absent','unused-contract-handle-empty','admitted-carrier-and-governed-internal-alternatives-inclusive']
tf=['no-selected-contracts-pairs-proposals-instances','no-independent-authority','admitted-contract-can-be-ineffective','changed-question-can-remain-rejected']
ft=['cartesian-cross-pair-not-authorized','reverse-pair-not-implicit','candidate-pair-not-available','validated-proposal-without-admission-not-available','dual-canonical-authority','same-kind-reuse-question-changed','conforming-instance-wrong-direction','reuse-successor-cannot-drop-old-pair','reuse-successor-cannot-add-unproposed-pair','conforming-instance-wrong-target-kind','second-writable-specialized-projection']
s=s[:start]+' wanted='+repr([(n,(True,True)) for n in tt]+[(n,(True,False)) for n in tf]+[(n,(False,True)) for n in ft])+s[end:]
s=s.replace('accepted_ConstraintCycleSafety','accepted_TypedConnectionExtension')
start=s.index(' issues=[');end=s.index('\n ];findings=',start)
issues=[
'No current Artifact Type directly binds exact C64 Typed Connection Extension Rule. Definition/v2 and eight compared carriers retain their own exact current meanings;type admission does not accept this translation.',
'Definition/v1 shape and pure projections accept hypothetical Cartesian/reverse/registration/local/validation inference,changed-question reuse and dual-writer claims. Those are prose shape observations,not accepted semantics.',
'RelationKind/v2 exact fixture has23ordered pairs,22source kinds and8target kinds:176Cartesian possibilities with153undeclared cross pairs. experiment-run/product stays undeclared and product/product is explicitly declared. Whole schema rejects wildcard/duplicate pairs but does not cross-check pair rows against separate kind lists or required qualifier axes against property names.',
'TypedRelation/v3 has41conditional branches. Its selected materializes-consequence fixture enforces exact endpoint-kind alternatives and three closed qualifier fields;opaque refs/digests still do not resolve endpoints or prove admission/conformance. Full conditional shape remains separate from accepted C64 version/pair/qualifier maps.',
'OntologyEdge/v1 enforces local-interpretation versus global-projection binding shape. Valid local-only fixtures do not supply global pairs;an independent admitted global contract and accepted mapping remain required. Event/digest/reference shape does not promote a local edge.',
'CapabilityRealizationBinding/v2 preserves candidate/adopted/superseded lifecycle and contract/conformance coordinates;adopted shape needs decision/conformance references but does not validate their authority. It has no explicit C64 projects-as/represented-by/single-writer mapping field. ChallengeContract,v1 owner/gate/evidence fields likewise need exact contestability maps.',
'C70/C74 positive admissions remain accurately bound:one integrated Governed Model ordinary instance at C70,and14carrier types/4typed relations at C74 with zero runtime/external effects. They do not admit C64 extension proposals,pairs,endpoint carriers or this formal translation by inference.',
'Twenty-one independent C64-only T/I comparisons retain exact row closure,registration/local independence,changed-question rejection,admitted-but-ineffective contracts and strict ordered-pair/qualifier/authority/conformance guards. Source-owner maps,common denotations,real admission/availability/validation and whole proof remain pending.'
]
s=s[:start]+' issues=[\'+\n'.replace("'+",'')+','.join(repr(x) for x in issues)+s[end:]
s=s.replace('CCS-CONSUMER-FINDING-','TCX-CONSUMER-FINDING-')
start=s.index("'retained_failed_consumer_comparison_refs':");end=s.index(",'source_consumer_observation':",start)
s=s[:start]+"'retained_failed_consumer_comparison_refs':[]"+s[end:]
s=s.replace("'generic_Invariant_binding_types':[],","")
s=s.replace("'declared_primary_consumer_refs':[]","'declared_primary_consumer_refs':dr['primary_consumer_refs']")
s=s.replace('actual_guard_execution_edge_promotion_or_authority_created','actual_endpoint_pair_instance_or_authority_created').replace('guard_consumer_activation_inferred','rule_consumer_activation_inferred').replace('actual_reference_resolution_or_guard_map_accepted','actual_reference_resolution_or_rule_map_accepted')
s=s.replace('definition-assurance-ConstraintCycleSafety','definition-assurance-TypedConnectionExtension').replace('PASS-for-exact-ConstraintCycleSafety-and-seven-separate-current-carrier-comparisons','PASS-for-exact-TypedConnectionExtension-and-eight-separate-current-carrier-comparisons').replace('Fresh Constraint Cycle Safety consumer observations differ','Fresh Typed Connection Extension consumer observations differ')
s=s.replace("'generic_Invariant_binding_types',","")
s=s.replace('Exact C53 positive source,twenty-three separate meanings,seven C70/C74A carrier shapes and21independent guard models only. No actual watch enforcement,cycle/safety theorem,review/witness/owner validity,accepted map,live promotion or whole proof.','Exact C64 positive source,twenty-nine separate meanings,eight C70/C74A carrier shapes and21independent ordered-pair/version/authority/conformance models only. No actual endpoint resolution,connection admission,global availability,instance validation,accepted map,authority or whole proof.')
s=s.replace("'source_consumer_observation':","'ordered_pair_fixture_observation':{'declared_pairs':len(pairs),'source_kinds':len(source_kinds),'target_kinds':len(target_kinds),'Cartesian_cross_pairs':len(cross),'Cartesian_undeclared_pairs':len(cross-pairs),'experiment_run_product_declared':('experiment-run','product') in pairs,'product_self_pair_declared':('product','product') in pairs,'projection_or_pair_admission_inferred':False},'source_consumer_observation':")
ast.parse(s)
with (u/'inspect_carrier_consumers.py').open('x') as f:f.write(s)
s=(p.parent/'20261012-constraint-cycle-safety/capture_consumer.py').read_text();assert 'cal.definition.constraint-cycle-safety-invariant' in s;s=s.replace('cal.definition.constraint-cycle-safety-invariant','cal.definition.typed-connection-extension-rule')
with (p/'capture_consumer.py').open('x') as f:f.write(s)
print('Prepared exact eight-carrier C64 comparison;not executed.')

