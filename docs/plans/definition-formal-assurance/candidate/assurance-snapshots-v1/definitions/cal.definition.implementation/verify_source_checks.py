"""Independent exact-source, admission, projection, span and finite countermodel checks."""
import ast,json
import build_candidate as b
import verify_candidate as models
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def verify(write=False):
 context=load('context.json');snapshot=b.snapshot();b.unchanged(context['sources']);b.external_current(context);assert b.r.verify(snapshot,b.ROOT)['files']==201;source=context['source_selection'];doc=b.co.source_document(snapshot,source);core=load('t.json')['payload'];packet=load('correspondence.json');checks=[]
 def check(name,condition):
  if not condition:raise ValueError('Source check failed: '+name)
  checks.append({'check_id':name,'result':'PASS-for-exact-candidate-check'})
 check('exact-current-Implementation-source',source==b.source_ref(snapshot,'cal.definition.implementation') and source['sha256']=='c25fcb2b31e8fee007261a645627fe8aae61d5778a51781a35cc549dc7aa79c1')
 decision=json.loads((b.ROOT/'docs/decisions/0065-integrated-lab-definition-model-admission/decision.json').read_bytes());check('C65-positive60-version-qualified-admissions',decision['status']=='owner-admitted' and len(decision['admitted_definitions'])==60 and any(row['definition_ref']==source['version_ref'] and row['path']==source['path'] and row['sha256']==source['sha256'] for row in decision['admitted_definitions']));authorization=decision['authorization'];check('C65-exact-authorization',b.ref(b.ROOT/authorization['path'])['sha256']==authorization['sha256'])
 registry=json.loads((b.ROOT/'authority/definitions/registry.json').read_bytes());entry=next(row for row in registry['entries'] if row['definition_id']==source['definition_id']);check('registry-current-positive-C65-lineage',entry['admission_decision_ref']==decision['decision_id'] and entry['sha256']==source['sha256'] and entry['lifecycle_state']=='admitted')
 check('historical-candidate-body-preserved',doc['classification']['lifecycle_posture_ref']=='CAL-LIFECYCLE-DEFINITION-V1:candidate-authored')
 schema=json.loads((b.ROOT/'authority/artifact-types/definition/v1/schema.json').read_bytes());check('authoritative-Definition-schema',not list(b.c.Draft202012Validator(schema).iter_errors(doc)))
 generator=b.ROOT/'authority/artifact-types/definition/v1/generator.py';namespace={};nodes=[node for node in ast.parse(generator.read_bytes()).body if isinstance(node,ast.FunctionDef) and node.name in ['esc','bullets','render']];exec(compile(ast.Module(body=nodes,type_ignores=[]),str(generator),'exec'),namespace);projection=(b.ROOT/source['path']).with_name('DEFINITION.md');check('pure-generated-human-projection',namespace['render'](doc).encode()==projection.read_bytes())
 embedded=context['embedded_review_source'];reference=doc['source_refs'][0];check('embedded-review-unadmitted-context-only',embedded['source_ref']==reference and reference['admission_posture']=='candidate-unadmitted' and reference['source_admission_ref'] is None and b.ref(b.ROOT/embedded['observed_current']['path'])==embedded['observed_current'] and embedded['observed_current']['sha256']==reference['content_sha256']=='1c92c720e176027597db09579276f9ea6e1d13b3d52bda233f9b0c4543dcb5eb')
 scientific=doc['voices']['scientific_formal'];check('source-governed-technical-realization-coordinates',scientific['normative_statement']=='An Implementation is a governed technical realization with stable identity, version, owner, lifecycle, source binding, build or deployment posture, interfaces, and evidence bindings. It is distinct from Product, Product Capability, Agent, model, Tool, runtime instance, and proof of conformance or value.')
 check('source-governed-identity-or-record-and-bounded-scope',scientific['formal_expression']=='Implementation(x) => governed_identity_or_record(x) and bounded_scope(x); Implementation(x) =/=> authority_effect(x).')
 check('source-five-separately-governed-facets',scientific['boundary_conditions'][2]=='Identity, lifecycle, evidence, authority, and relation effects remain separately governed.')
 check('source-exact-or-admitted-successor-use',scientific['testable_conditions'][0]=='Every use of Implementation resolves to this exact Definition version or an admitted successor.')
 check('source-use-applicability-and-exclusions',scientific['testable_conditions'][1]=='Every claimed instance or use stays within the applicability statement and exclusions.')
 check('source-five-term-alone-noninferences',scientific['testable_conditions'][2]=='No consumer infers admission, authority, success, identity equivalence, or external effect from the term alone.')
 check('source-separate-contract-boundary',doc['boundaries'][1]=='The term supplies meaning only; carrier shape, relation availability, runtime behavior, and authority effect require separate admitted contracts.')
 check('nine-coordinate-realization-and-three-coordinate-use',len(b.FIELDS)==9 and len(b.USE_FIELDS)==3 and 'capability' not in json.dumps(b.FIELDS).lower())
 check('source-qualified-no-new-canonical-types',all(row['scope']==b.SCOPE for row in core['declarations']) and core['semantic_status']=='candidate')
 check('exact-source-unit-inventory',packet['source_units']==b.co.inventory(doc))
 account=b.co.check(packet,snapshot,required_dependencies=[row['version_ref'] for row in core['depends_on']],required_conflicts=[row['finding_id'] for row in packet['source_precedence']['conflicts']]);check('complete-character-account-including-dependencies-and-findings',account==load('correspondence-check.json') and account['character_accounting_complete'])
 check('all-source-clauses-are-selected-spans',[row['source_selector'] for row in core['clauses']]==[row['source_selector'] for row in b.selected_clauses(doc)] and all(row['formal_statement']==spec['formula'] and row['disposition']==spec['disposition'] for row,spec in zip(core['clauses'],b.selected_clauses(doc))))
 check('no-assumed-outcome-or-accepted-fidelity',not core['assumptions'] and not packet['assumption_links'] and core['source_fidelity']=='pending' and packet['source_precedence']['review_ref'] is None and packet['review_packet']['review_status']=='pending')
 check('all21-source-owner-findings-preserved',[row['description'] for row in packet['source_precedence']['conflicts']]==b.LOSSES and len(b.LOSSES)==21 and all(row['status']=='unresolved' for row in packet['source_precedence']['conflicts']))
 check('source-and-IR-agree',packet['interpretation']==core and load('static-ir.json')==b.ir.compile_interpretation(core,snapshot))
 stack=[row['formal_statement'] for row in core['clauses'] if row['disposition']=='encoded']
 while stack:
  node=stack.pop()
  if isinstance(node,dict):
   assert not(node.get('op')=='pred' and any(node.get('name','').startswith(prefix+'Actual') for prefix in ['Implementation','Use']));stack.extend(node.values())
  elif isinstance(node,list):stack.extend(node)
 check('actual-target-predicates-absent-from-T',True)
 analysis=load('clause-analysis.json');check('inclusive-governed-and-posture-modes',analysis['governed_identity_or_record_inclusive'] is analysis['build_or_deployment_posture_inclusive'] is True);check('no-invented-capability-or-succession-policy',analysis['mandatory_capability_endpoint_added'] is analysis['successor_or_global_version_policy_added'] is analysis['hypothetical_successor_is_actual_admission'] is False)
 controls=load('model-controls.json');cases={row['case_id']:row for row in controls['results']};check('complete179-controls-and-eight-malformed',len(cases)==controls['control_count']==len(models.controls())==179 and sum(row['status']=='rejected-model-structure' for row in controls['results'])==8)
 for name in ['governed-technical-realizations-nine-coordinates-inclusive-postures-scoped-uses','hypothetical-admitted-successor-use-not-actual-admission','unused-revision-handle-empty','unused-posture-handle-empty']:
  check(name,cases[name]['primary_theory_satisfied'] is cases[name]['required_population_satisfied'] is True)
 for name in ['no-selected-realizations-or-uses','no-selected-uses','both-governed-modes-reduced-to-record','both-postures-reduced-to-deployment','all-interface-nominations-singleton-or-empty','shared-evidence-separated','same-version-nomination-for-shared-identity','all-use-scopes-equal-realization-scopes']:
  check('independent-T-versus-I-'+name,cases[name]['primary_theory_satisfied'] is True and cases[name]['required_population_satisfied'] is False)
 for name in ['neither-governed-identity-nor-record','posture-neither-build-nor-deployment','missing-explicit-Interface-link','missing-explicit-Evidence-link','extra-Interface-link-outside-collection','extra-Evidence-link-outside-collection','use-scope-not-within-implementation','use-targets-unselected-realization','unknown-definition-use-without-successor-or-admission','hypothetical-successor-without-admission','hypothetical-admission-without-successor']:
  check(name,cases[name]['primary_theory_satisfied'] is False)
 typed=load('static-ir.json');queries=load('query-policy.json')['queries'];check('all40-independent-query-targets',queries==b.query_specs() and len(queries)==40)
 ids={row['symbol_id']:b.ir.qualified(core['source'],core['scope'],row['symbol_id']) for row in core['declarations']};model=models.qualify(models.base_model(),ids);countermodels={row['query_id']:row for row in controls['nonentailment_countermodels']};composed=b.ir.compose([typed])
 for query in queries:
  target=v.renamed(query['target'],ids);witness=v.renamed(query['witness_condition'],ids);b.ir.check_composed_formula(composed,target);b.ir.check_composed_formula(composed,witness);evaluator=v.Denotation(typed['declarations'],model);check('countermodel-'+query['query_id'],query['selected_in_T'] is False and evaluator.truth(target) is False and evaluator.truth(witness) is True and countermodels[query['query_id']]['model']==model)
 texts=dict(b.co.string_leaves(doc));obligations=load('source-query-obligation.json')['obligations'];clauses={row['clause_id']:row for row in core['clauses']}
 for obligation in obligations:
  excerpt=texts[obligation['selector']][obligation['start_character']:obligation['end_character']];clause=clauses[obligation['clause_id']];assert obligation['source']==source and excerpt==obligation['excerpt'] and b.r.digest(excerpt.encode())==obligation['excerpt_sha256']==clause['excerpt_sha256'] and obligation['query_id'] in countermodels and obligation['actual_outcome_target_in_T'] is False
 check('complete-exact-span-query-obligations',{row['clause_id'] for row in obligations}=={row['clause_id'] for row in core['clauses'] if row['disposition']!='explanatory'})
 prior=json.loads((b.BASE/'definitions/cal.definition.coordination-context/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']);b.external_current(context)
 report={'schema_version':'Implementation-source-checks/v1-candidate','status':'PASS-exact-Implementation-source-conditions','authority_effect':'none','checks':checks,'source_query_obligations':len(obligations),'projection_bytes':len(projection.read_bytes()),'checker_bindings':[b.ref(b.UNIT/name) for name in ['build_candidate.py','verify_candidate.py','verify_source_checks.py']],'source':source,'source_fidelity':'pending','semantic_ready':False,'accepted_source_map':False,'actual_Implementation_built_deployed_conformant_or_authorized':False,'actual_successor_Definition_created_or_admitted':False,'whole_definition_proof':False,'prior_candidate_files_preserved':len(prior['files'])}
 if write:b.put('source-checks.json',report)
 elif report!=load('source-checks.json'):raise ValueError('Fresh source checks differ')
 return report
if __name__=='__main__':
 report=verify('--write' in b.sys.argv);print(json.dumps({'result':report['status'],'checks':len(report['checks']),'source_query_obligations':report['source_query_obligations'],'semantic_ready':False},indent=2))
