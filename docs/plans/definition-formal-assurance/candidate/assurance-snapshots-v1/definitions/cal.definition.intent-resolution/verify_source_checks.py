"""Independent exact-source, nomination guards and noninference checks."""
import ast,json
import build_candidate as b
import verify_candidate as models
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def verify(write=False):
    context=load('context.json');snapshot=b.snapshot();b.unchanged(context['sources']);b.external_current(context);assert b.r.verify(snapshot,b.ROOT)['files']==201;source=context['source_selection'];doc=b.co.source_document(snapshot,source);core=load('t.json')['payload'];packet=load('correspondence.json');checks=[]
    def check(name,value):
        if not value:raise ValueError('Source check failed: '+name)
        checks.append({'check_id':name,'result':'PASS-for-exact-candidate-check'})
    check('exact-current-IntentResolution-source',source==b.source_ref(snapshot,'cal.definition.intent-resolution') and source['sha256']=='cf84080dba84433926c7f11759057ca4277458152518aaa243d61a948e96c136')
    decision=json.loads((b.ROOT/'docs/decisions/0065-integrated-lab-definition-model-admission/decision.json').read_bytes());check('C65-positive-exact-selection',decision['status']=='owner-admitted' and len(decision['admitted_definitions'])==60 and any(r['definition_ref']==source['version_ref'] and r['path']==source['path'] and r['sha256']==source['sha256'] for r in decision['admitted_definitions']));auth=decision['authorization'];check('C65-authorization-bound',b.ref(b.ROOT/auth['path'])['sha256']==auth['sha256'])
    check('C65-no-type-or-consumer-activation',decision['admission_result']['artifact_types_admitted']==decision['admission_result']['consumer_activations']==decision['admission_result']['relation_kinds_admitted']==0)
    registry=json.loads((b.ROOT/'authority/definitions/registry.json').read_bytes());entry=next(r for r in registry['entries'] if r['definition_id']==source['definition_id']);check('registry-positive-C65-lineage',entry['admission_decision_ref']==decision['decision_id'] and entry['sha256']==source['sha256'] and entry['lifecycle_state']=='admitted')
    check('historical-body-posture-preserved',doc['classification']['lifecycle_posture_ref']=='CAL-LIFECYCLE-DEFINITION-V1:candidate-authored')
    schema=b.ROOT/'authority/artifact-types/definition/v1/schema.json';check('schema-digest-and-shape',b.ref(schema)['sha256']==doc['schema_digest'] and not list(b.c.Draft202012Validator(json.loads(schema.read_bytes())).iter_errors(doc)))
    generator=b.ROOT/'authority/artifact-types/definition/v1/generator.py';check('generator-digest',b.ref(generator)['sha256']==doc['source_direction']['generator_sha256']);namespace={};nodes=[n for n in ast.parse(generator.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name in ['esc','bullets','render']];exec(compile(ast.Module(body=nodes,type_ignores=[]),str(generator),'exec'),namespace);projection=(b.ROOT/source['path']).with_name('DEFINITION.md');check('exact-pure-human-projection',namespace['render'](doc).encode()==projection.read_bytes())
    embedded=context['embedded_review_source'];sr=doc['source_refs'][0];check('review-source-exact-and-postures-separate',embedded['source_ref']==sr and sr['admission_posture']=='candidate-unadmitted' and sr['source_admission_ref'] is None and sr['selector']=='whole-file' and b.ref(b.ROOT/embedded['observed_current']['path'])==embedded['observed_current'] and sr['content_sha256']==embedded['observed_current']['sha256']=='1c92c720e176027597db09579276f9ea6e1d13b3d52bda233f9b0c4543dcb5eb')
    scientific=doc['voices']['scientific_formal'];check('source-owner-decision-one-exact-Intent-and-test',scientific['normative_statement']=='An Intent Resolution is an attributable owner decision selecting which governed Product, Project, Goal, Research, Capability, or other output will address one exact Intent and under what satisfaction test. It does not embed Implementation in Intent, prove delivery or satisfaction, or authorize unrelated work.')
    check('source-governed-identity-or-record-bounded-scope-and-no-effect-inference',scientific['formal_expression']=='IntentResolution(x) => governed_identity_or_record(x) and bounded_scope(x); IntentResolution(x) =/=> authority_effect(x).')
    check('source-five-separately-governed-facets',scientific['boundary_conditions'][2]=='Identity, lifecycle, evidence, authority, and relation effects remain separately governed.')
    check('source-exact-or-admitted-successor-use',scientific['testable_conditions'][0]=='Every use of Intent Resolution resolves to this exact Definition version or an admitted successor.')
    check('source-use-within-applicability-and-exclusions',scientific['testable_conditions'][1]=='Every claimed instance or use stays within the applicability statement and exclusions.')
    check('source-term-alone-noninference',scientific['testable_conditions'][2]=='No consumer infers admission, authority, success, identity equivalence, or external effect from the term alone.')
    check('source-separate-contract-requirement',doc['boundaries'][1]=='The term supplies meaning only; carrier shape, relation availability, runtime behavior, and authority effect require separate admitted contracts.')
    check('source-example-selects-multiple-outputs',doc['voices']['domain_context']['examples'][0]=='IR-17 selects product:ontology, project:lab-semantic-closure, and capability:typed-meaning to address intent:complete-lab-model.')
    check('five-proposed-resolution-and-three-use-coordinates',len(b.FIELDS)==5 and len(b.USE_FIELDS)==3)
    check('existential-ownership-and-attribution-without-unique-functions','decisionOwner' not in b.FUNCTIONS and 'decisionAttributor' not in b.FUNCTIONS and b.SIGNATURE['DecisionOwnerDeclared']==['OwnerDecisionReference','OwnerReference'])
    check('inclusive-open-output-kinds',b.OUTPUT_KINDS==['Product','Project','Goal','Research','Capability','Other'])
    check('no-Research-or-Capability-source-substitution',not any(r['definition_id'] in ['cal.definition.research-inquiry','cal.definition.product-capability','cal.definition.agent-capability'] for r in core['depends_on']) and len(context['unavailable_requested_dependency_labels'])==3)
    check('source-qualified-proposed-symbols',all(r['scope']==b.SCOPE for r in core['declarations']) and core['semantic_status']=='candidate')
    check('complete-exact-source-inventory',packet['source_units']==b.co.inventory(doc))
    account=b.co.check(packet,snapshot,required_dependencies=[r['version_ref'] for r in core['depends_on']],required_conflicts=[r['finding_id'] for r in packet['source_precedence']['conflicts']]);check('complete-character-dependency-and-finding-account',account==load('correspondence-check.json') and account['character_accounting_complete'])
    check('exact-clause-formulas-and-dispositions',len(core['clauses'])==len(b.selected_clauses(doc)) and all(r['formal_statement']==s['formula'] and r['disposition']==s['disposition'] and r['source_selector']==s['source_selector'] for r,s in zip(core['clauses'],b.selected_clauses(doc))))
    check('no-assumptions-or-accepted-fidelity',not core['assumptions'] and not packet['assumption_links'] and core['source_fidelity']=='pending' and packet['source_precedence']['review_ref'] is None and packet['review_packet']['review_status']=='pending')
    check('all19-owner-findings-unresolved',[r['description'] for r in packet['source_precedence']['conflicts']]==b.LOSSES and len(b.LOSSES)==19 and all(r['status']=='unresolved' for r in packet['source_precedence']['conflicts']))
    typed=load('static-ir.json');check('source-and-IR-agree',packet['interpretation']==core and typed==b.ir.compile_interpretation(core,snapshot))
    stack=[r['formal_statement'] for r in core['clauses'] if r['disposition']=='encoded']
    while stack:
        node=stack.pop()
        if isinstance(node,dict):
            assert not(node.get('op')=='pred' and any(node.get('name','').startswith(prefix+'Actual') for prefix in ['Resolution','Use']));stack.extend(node.values())
        elif isinstance(node,list):stack.extend(node)
    check('actual-targets-absent-from-T',True)
    analysis=load('clause-analysis.json');check('no-invented-uniqueness-or-outcome-proof',analysis['single_resolution_per_Intent_policy_added'] is analysis['selection_or_test_proves_actual_satisfaction'] is analysis['hypothetical_successor_is_actual_admission'] is analysis['successor_or_global_version_policy_added'] is False)
    check('multiple-owners-attributors-outputs-and-other-kind',analysis['multiple_owners_and_attributors_allowed'] is analysis['multiple_outputs_allowed'] is analysis['open_other_output_kind'] is True)
    controls=load('model-controls.json');cases={r['case_id']:r for r in controls['results']};check('complete-independent-controls-and-six-malformed',len(cases)==controls['control_count']==len(models.controls()) and sum(r['status']=='rejected-model-structure' for r in controls['results'])==6)
    for name in ['attributable-owner-decisions-exact-Intent-open-governed-outputs-and-tests','hypothetical-admitted-successor-use-not-actual-admission','unused-OutputReference-handle-empty','unused-SatisfactionTestReference-handle-empty']:check(name,cases[name]['primary_theory_satisfied'] is cases[name]['required_population_satisfied'] is True)
    for name in ['no-selected-resolutions-or-uses','no-selected-uses','both-governed-modes-reduced-to-record','multiple-owners-reduced-to-one','multiple-attributors-reduced-to-one','mixed-output-roles-reduced-to-one','all-output-collections-singleton','each-selected-resolution-different-Intent','shared-test-separated','all-use-scopes-equal-resolution-scopes']:check('separate-T-I-'+name,cases[name]['primary_theory_satisfied'] is True and cases[name]['required_population_satisfied'] is False)
    for name in ['owner-decision-without-owner','owner-decision-without-attribution','Intent-without-exact-version-nomination','empty-selected-output-collection','selected-output-not-governed','missing-output-addresses-Intent-link','missing-output-under-satisfaction-test-link','wrong-output-Intent-target','wrong-output-test-target','unknown-definition-use-without-successor-or-admission','hypothetical-successor-without-admission','hypothetical-admission-without-successor']:check(name,cases[name]['primary_theory_satisfied'] is False)
    queries=load('query-policy.json')['queries'];check('all35-query-targets-independent',queries==b.query_specs() and len(queries)==35)
    ids={r['symbol_id']:b.ir.qualified(core['source'],core['scope'],r['symbol_id']) for r in core['declarations']};model=models.qualify(models.base_model(),ids);cm={r['query_id']:r for r in controls['nonentailment_countermodels']};composed=b.ir.compose([typed]);baseline=v.Denotation(typed['declarations'],model)
    check('independent-baseline-satisfies-all-T-and-I',all(baseline.truth(r['formal_statement']) for r in typed['clauses'] if r['disposition']=='encoded') and all(baseline.truth(r['statement']) for r in typed['populations'] if r['requirement']=='required'))
    for q in queries:
        target=v.renamed(q['target'],ids);witness=v.renamed(q['witness_condition'],ids);b.ir.check_composed_formula(composed,target);b.ir.check_composed_formula(composed,witness);e=v.Denotation(typed['declarations'],model);check('countermodel-'+q['query_id'],q['selected_in_T'] is False and e.truth(target) is False and e.truth(witness) is True and cm[q['query_id']]['model']==model)
    texts=dict(b.co.string_leaves(doc));obligations=load('source-query-obligation.json')['obligations'];clauses={r['clause_id']:r for r in core['clauses']}
    for o in obligations:
        excerpt=texts[o['selector']][o['start_character']:o['end_character']];clause=clauses[o['clause_id']];assert o['source']==source and excerpt==o['excerpt'] and b.r.digest(excerpt.encode())==o['excerpt_sha256']==clause['excerpt_sha256'] and o['query_id'] in cm and o['actual_outcome_target_in_T'] is False
    check('complete-source-span-query-obligations',{o['clause_id'] for o in obligations}=={r['clause_id'] for r in core['clauses'] if r['disposition']!='explanatory'})
    prior=json.loads((b.BASE/'definitions/cal.definition.intent/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']);assert len(prior['files'])==10703;b.external_current(context)
    report={'schema_version':'IntentResolution-source-checks/v1-candidate','status':'PASS-exact-IntentResolution-source-conditions','authority_effect':'none','checks':checks,'source_query_obligations':len(obligations),'projection_bytes':len(projection.read_bytes()),'checker_bindings':[b.ref(b.UNIT/n) for n in ['build_candidate.py','verify_candidate.py','verify_source_checks.py']],'source':source,'source_fidelity':'pending','semantic_ready':False,'accepted_source_map':False,'actual_IntentResolution_delivery_satisfaction_or_authority_established':False,'actual_successor_Definition_created_or_admitted':False,'whole_definition_proof':False,'prior_candidate_files_preserved':len(prior['files'])}
    if write:b.put('source-checks.json',report)
    elif report!=load('source-checks.json'):raise ValueError('Fresh source checks differ')
    return report
if __name__=='__main__':
    report=verify('--write' in b.sys.argv);print(json.dumps({'result':report['status'],'checks':len(report['checks']),'source_query_obligations':report['source_query_obligations'],'semantic_ready':False},indent=2))
