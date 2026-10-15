"""Prepared Implementation source-qualified technical realization, scope, version use and noninference guards."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=Path.cwd();BASE=ROOT/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1'
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co
def var(n):return {'op':'var','name':n}
def const(n):return {'op':'const','name':n}
def pred(n,*args):return {'op':'pred','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def fn(n,*args):return {'op':'fn','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def both(*args):return {'op':'and','args':list(args)}
def either(*args):return {'op':'or','args':list(args)}
def neg(a):return {'op':'not','arg':a}
def implies(a,z):return either(neg(a),z)
def eq(a,z):return {'op':'eq','left':a,'right':z}
def bind(bindings,body):
 for op,sort,name in reversed(bindings):body={'op':op,'sort':sort,'var':name,'body':body}
 return body
def allof(bindings,body):return bind([('forall',sort,name) for sort,name in bindings],body)
def exists(bindings,body):return bind([('exists',sort,name) for sort,name in bindings],body)
def ref(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(n,value):
 with (UNIT/n).open('x') as out:json.dump(value,out,sort_keys=True,separators=(',',':'));out.write('\n')
 return ref(UNIT/n)
def snapshot():return json.loads((BASE/'current-snapshot.json').read_bytes())
def unchanged(refs):
 for x in refs:
  if ref(ROOT/x['path'])!=x:raise ValueError('Changed selected input '+x['path'])
def external_current(context):
 for x in context['external_sources']:
  if r.digest(Path(x['absolute_path']).read_bytes())!=x['sha256']:raise ValueError('External source drift')
def source_ref(snap,id):
 row=next(x for x in snap['current_entries'] if x['definition_id']==id)
 return {k:row[k] for k in ['definition_id','version_ref','path','sha256']}


"""Necessary owner-decision, exact Intent, output selection and use guards."""
SCOPE='scope:candidate:IntentResolution-owner-decision-exact-intent-governed-output-test-scoped-use-v1'
SORTS=['ResolutionReference','IntentReference','OwnerDecisionReference','OwnerReference','AttributorReference','OutputCollectionReference','OutputReference','SatisfactionTestReference','ScopeReference','UseReference','DefinitionVersionReference','Token']
CONSTANTS={'EMPTY':'Token','SELECTED_DEFINITION':'DefinitionVersionReference'}
FIELDS={'resolutionIntent':'IntentReference','resolutionOwnerDecision':'OwnerDecisionReference','resolutionOutputs':'OutputCollectionReference','resolutionSatisfactionTest':'SatisfactionTestReference','resolutionScope':'ScopeReference'}
USE_FIELDS={'useResolution':'ResolutionReference','useDefinitionVersion':'DefinitionVersionReference','useScope':'ScopeReference'}
GROUPS=[(FIELDS,'ResolutionReference'),(USE_FIELDS,'UseReference')]
HANDLES={sort:sort[0].lower()+sort[1:]+'Handle' for sort in SORTS if sort!='Token'}
FUNCTIONS={name:([carrier],sort) for fields,carrier in GROUPS for name,sort in fields.items()};FUNCTIONS.update({name:([sort],'Token') for sort,name in HANDLES.items()})
OUTPUT_KINDS=['Product','Project','Goal','Research','Capability','Other']
INFERRED=['Admission','Authority','Success','IdentityEquivalence','ExternalEffect','Delivery','Satisfaction']
FACETS=['Identity','Lifecycle','Evidence','Authority','RelationEffects']
CONTRACTS=['CarrierShape','RelationAvailability','RuntimeBehavior','AuthorityEffect']
EXCLUDED=['ResolutionEmbedsImplementationInIntentDeclared','ResolutionAuthorizesUnrelatedWorkDeclared']
ACTUAL=['IntentReferenceResolution','OwnerDecisionAuthenticity','OwnerAuthorization','AttributionAuthenticity','OutputGovernance','OutputSuitability','SatisfactionTestResolution','SatisfactionTestAdequacy','Delivery','Satisfaction','IntentContinuity','ImplementationSeparation','ScopeCompliance','IdentityFidelity','LifecycleOperation','EvidenceAuthenticity','RelationOperation','CarrierAdmission','InstanceAdmission','RuntimeActivation','AuthorityEffect','Publication','Release','Deployment','ExternalEffect','SourceFidelity','WholeProof']
USE_ACTUAL=['DefinitionResolution','SuccessorAdmissionAuthenticity','ApplicabilityCompliance','ExclusionCompliance','ScopeCompliance','AuthorityEffect','SourceFidelity','WholeProof']
SIGNATURE={name:['ResolutionReference'] for name in ['ResolutionApplicable','ResolutionInScopeDeclared','ResolutionBoundedScopeDeclared','ResolutionGovernedIdentityDeclared','ResolutionGovernedRecordDeclared',*EXCLUDED,*['Resolution'+n+'SeparatelyGovernedDeclared' for n in FACETS],*['Resolution'+n+'NeedsSeparateContractDeclared' for n in CONTRACTS],*['ResolutionTermInfers'+n+'Declared' for n in INFERRED],*['ResolutionActual'+n for n in ACTUAL]]}
SIGNATURE.update({name:['UseReference'] for name in ['UseApplicable','UseInScopeDeclared','UseWithinApplicabilityDeclared','UseRespectsExclusionsDeclared',*['UseTermInfers'+n+'Declared' for n in INFERRED],*['UseActual'+n for n in USE_ACTUAL]]})
SIGNATURE.update({name:['OutputReference'] for name in ['OutputGovernedDeclared',*['Output'+n+'Declared' for n in OUTPUT_KINDS]]})
SIGNATURE.update(IntentExactVersionDeclared=['IntentReference'],OwnerDecisionDeclared=['OwnerDecisionReference'],DefinitionVersionAdmissionDeclared=['DefinitionVersionReference'])
for sort in SORTS:
    if sort!='Token':SIGNATURE[sort+'Declared']=[sort]
for fields,carrier in GROUPS:SIGNATURE.update({name+'BindingDeclared':[carrier,sort] for name,sort in fields.items()})
SIGNATURE.update(DecisionOwnerDeclared=['OwnerDecisionReference','OwnerReference'],DecisionAttributionDeclared=['OwnerDecisionReference','AttributorReference'],OutputCollectionContainsDeclared=['OutputCollectionReference','OutputReference'],ResolutionSelectsOutputDeclared=['ResolutionReference','OutputReference'],ResolutionOutputAddressesIntentDeclared=['ResolutionReference','OutputReference','IntentReference'],ResolutionOutputUnderTestDeclared=['ResolutionReference','OutputReference','SatisfactionTestReference'],DefinitionVersionAdmittedSuccessorDeclared=['DefinitionVersionReference','DefinitionVersionReference'],UseScopeWithinResolutionDeclared=['ScopeReference','ScopeReference'])
MAP={'ResolutionReference':'ResolutionApplicable','UseReference':'UseApplicable'}
def iff(a,z):return {'op':'iff','left':a,'right':z}
def member(sort):return MAP.get(sort,sort+'Declared')
def guard(sort,value):return both(pred(member(sort),value),neg(eq(fn(HANDLES[sort],value),const('EMPTY'))))
def exact(fields,value):return both(*[both(guard(sort,fn(name,value)),allof([(sort,'target')],iff(pred(name+'BindingDeclared',value,'target'),eq(var('target'),fn(name,value))))) for name,sort in fields.items()])
def selected(sort,name,body):return allof([(sort,name)],implies(pred(member(sort),name),body))
X=var('x');U=var('u');APP=pred('ResolutionApplicable',X);USE=pred('UseApplicable',U);D=fn('resolutionOwnerDecision',X);O=var('output')
ROOT_RULE=both(allof([('ResolutionReference','x')],iff(APP,pred('ResolutionInScopeDeclared',X))),selected('ResolutionReference','x',both(guard('ResolutionReference',X),exact(FIELDS,X),pred('ResolutionBoundedScopeDeclared',X),either(pred('ResolutionGovernedIdentityDeclared',X),pred('ResolutionGovernedRecordDeclared',X)),pred('IntentExactVersionDeclared',fn('resolutionIntent',X)),pred('OwnerDecisionDeclared',D),exists([('OwnerReference','owner')],both(guard('OwnerReference',var('owner')),pred('DecisionOwnerDeclared',D,'owner'))),exists([('AttributorReference','attributor')],both(guard('AttributorReference',var('attributor')),pred('DecisionAttributionDeclared',D,'attributor'))))))
OUTPUT_RULE=selected('ResolutionReference','x',both(exists([('OutputReference','output')],pred('ResolutionSelectsOutputDeclared',X,O)),allof([('OutputReference','output')],both(iff(pred('ResolutionSelectsOutputDeclared',X,O),pred('OutputCollectionContainsDeclared',fn('resolutionOutputs',X),O)),implies(pred('ResolutionSelectsOutputDeclared',X,O),both(guard('OutputReference',O),pred('OutputGovernedDeclared',O),either(*[pred('Output'+n+'Declared',O) for n in OUTPUT_KINDS]),pred('ResolutionOutputAddressesIntentDeclared',X,O,fn('resolutionIntent',X)),pred('ResolutionOutputUnderTestDeclared',X,O,fn('resolutionSatisfactionTest',X))))))))
FACET_RULE=selected('ResolutionReference','x',both(*[pred('Resolution'+n+'SeparatelyGovernedDeclared',X) for n in FACETS]))
CONTRACT_RULE=selected('ResolutionReference','x',both(*[pred('Resolution'+n+'NeedsSeparateContractDeclared',X) for n in CONTRACTS]))
BOUNDARIES=selected('ResolutionReference','x',both(*[neg(pred(n,X)) for n in EXCLUDED]))
ROOT_NONINFERENCE=selected('ResolutionReference','x',both(*[neg(pred('ResolutionTermInfers'+n+'Declared',X)) for n in INFERRED]))
USE_NONINFERENCE=selected('UseReference','u',both(*[neg(pred('UseTermInfers'+n+'Declared',U)) for n in INFERRED]))
VERSION_ALLOWED=either(eq(fn('useDefinitionVersion',U),const('SELECTED_DEFINITION')),both(pred('DefinitionVersionAdmittedSuccessorDeclared',const('SELECTED_DEFINITION'),fn('useDefinitionVersion',U)),pred('DefinitionVersionAdmissionDeclared',fn('useDefinitionVersion',U))))
USE_SCOPE=selected('UseReference','u',both(pred('UseWithinApplicabilityDeclared',U),pred('UseRespectsExclusionsDeclared',U),pred('UseScopeWithinResolutionDeclared',fn('useScope',U),fn('resolutionScope',fn('useResolution',U)))))
USE_RULE=both(guard('DefinitionVersionReference',const('SELECTED_DEFINITION')),pred('DefinitionVersionAdmissionDeclared',const('SELECTED_DEFINITION')),allof([('UseReference','u')],iff(USE,pred('UseInScopeDeclared',U))),selected('UseReference','u',both(guard('UseReference',U),exact(USE_FIELDS,U),VERSION_ALLOWED)),USE_SCOPE)
THEORY={'owner-decision-exact-Intent-and-bounded-record':ROOT_RULE,'governed-output-selection-addresses-Intent-under-test':OUTPUT_RULE,'five-separately-governed-facets':FACET_RULE,'no-Implementation-embedding-or-unrelated-work-authorization':BOUNDARIES,'separate-contract-requirements':CONTRACT_RULE,'exact-Definition-or-admitted-successor-use':USE_RULE,'term-alone-does-not-infer-effects':both(ROOT_NONINFERENCE,USE_NONINFERENCE)}
LOSSES=[
    'C65 admits the exact Definition; immutable candidate body and embedded candidate-unadmitted source posture do not accept this translation or an Intent Resolution instance.',
    'The exact integrated-model review is context only; unselected narrative meanings are not imported into the normative voice.',
    'Proposed nominal sorts and auxiliary functions preserve relationships without creating canonical Definitions or an authoritative five-field carrier tuple.',
    'One exact Intent is nominated per selected resolution; exactness declarations and nonempty handles do not authenticate an actual Intent version.',
    'A Resolution is an owner decision in the source; its proposed owner-decision projection requires an accepted genus and identity map rather than mere reference shape.',
    'Attribution and ownership are independently nominated; at least one of each is required without a unique-owner or unique-attributor rule.',
    'Governed identity or record is inclusive; bounded scope is a necessary declaration rather than verified scope compliance or authorization.',
    'At least one governed output is selected, and multiple outputs are allowed by the example; no single-output or unique-resolution-per-Intent rule is invented.',
    'Product, Project, Goal, Research and Capability are inclusive roles with an open other-output category, not an exhaustive universal type taxonomy.',
    'Research and Capability lack exact current Definition term matches; related Research Inquiry or Product Capability meanings are not silently substituted.',
    'Every selected output has declared Intent and satisfaction-test links; those links do not prove actual suitability, delivery or satisfaction.',
    'Outputs, tests and Intent nominations may be shared; equal reference values do not establish accepted cross-definition denotations.',
    'A declared satisfaction test neither evaluates a real result nor establishes test adequacy, evidence completeness or owner acceptance.',
    'Implementation embedding and unrelated-work authorization are prohibited declared claims; independently justified authority remains possible.',
    'Identity, lifecycle, evidence, authority and relation effects remain separate; carrier shape and runtime still require separately admitted contracts.',
    'Exact Definition or hypothetically declared admitted-successor use requires scoped applicability and exclusion declarations; no actual successor is minted.',
    'No automatic output construction, parent-to-instance authority transfer, runtime activation, publication, release, deployment or external effect follows from the term.',
    'Finite T/I models and source accounts establish the reported partial candidate behavior, not accepted common meaning, source fidelity or a whole-definition proof.',
    'Original T/O/E/R/J artifacts, owner and consumer correspondence, cycle review and the final complete episode explanation remain required.'
]
def declarations():return [{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'constant','symbol_id':n,'scope':SCOPE,'result_sort':s} for n,s in CONSTANTS.items()]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':a,'result_sort':s,'definedness_policy':None} for n,(a,s) in FUNCTIONS.items()]+[{'kind':'predicate' if len(a)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':a} for n,a in SIGNATURE.items()]
def required_populations():
    def xw(body):return exists([('ResolutionReference','x')],both(APP,body))
    def uw(body):return exists([('UseReference','u')],both(USE,body))
    def ow(body):return xw(exists([('OutputReference','output')],both(pred('ResolutionSelectsOutputDeclared',X,O),body)))
    gi,gr=pred('ResolutionGovernedIdentityDeclared',X),pred('ResolutionGovernedRecordDeclared',X)
    rows={'Resolution':('ResolutionReference',xw(APP)),'OutsideResolution':('ResolutionReference',exists([('ResolutionReference','x')],neg(APP))),'GovernedIdentityOnly':('ResolutionReference',xw(both(gi,neg(gr)))),'GovernedRecordOnly':('ResolutionReference',xw(both(gr,neg(gi)))),'BothGovernedModes':('ResolutionReference',xw(both(gi,gr))),'WithoutActualOutcomes':('ResolutionReference',xw(both(*[neg(pred('ResolutionActual'+n,X)) for n in ACTUAL]))),'IndependentAuthority':('ResolutionReference',xw(pred('ResolutionActualAuthorityEffect',X))),'MultipleOwners':('OwnerReference',xw(exists([('OwnerReference','a'),('OwnerReference','b')],both(pred('DecisionOwnerDeclared',D,'a'),pred('DecisionOwnerDeclared',D,'b'),neg(eq(var('a'),var('b'))))))),'MultipleAttributors':('AttributorReference',xw(exists([('AttributorReference','a'),('AttributorReference','b')],both(pred('DecisionAttributionDeclared',D,'a'),pred('DecisionAttributionDeclared',D,'b'),neg(eq(var('a'),var('b'))))))),'MultipleOutputs':('OutputReference',xw(exists([('OutputReference','output'),('OutputReference','other')],both(pred('ResolutionSelectsOutputDeclared',X,O),pred('ResolutionSelectsOutputDeclared',X,'other'),neg(eq(O,var('other'))))))),'SharedOutput':('OutputReference',exists([('ResolutionReference','x'),('ResolutionReference','other'),('OutputReference','output')],both(APP,pred('ResolutionApplicable','other'),neg(eq(X,var('other'))),pred('ResolutionSelectsOutputDeclared',X,O),pred('ResolutionSelectsOutputDeclared','other',O)))),'SameIntentDifferentResolutions':('IntentReference',exists([('ResolutionReference','x'),('ResolutionReference','other')],both(APP,pred('ResolutionApplicable','other'),neg(eq(X,var('other'))),eq(fn('resolutionIntent',X),fn('resolutionIntent','other'))))),'SharedSatisfactionTest':('SatisfactionTestReference',exists([('ResolutionReference','x'),('ResolutionReference','other')],both(APP,pred('ResolutionApplicable','other'),neg(eq(X,var('other'))),eq(fn('resolutionSatisfactionTest',X),fn('resolutionSatisfactionTest','other'))))),'MixedOutputRoles':('OutputReference',ow(both(pred('OutputProductDeclared',O),pred('OutputGoalDeclared',O)))),'Use':('UseReference',uw(USE)),'OutsideUse':('UseReference',exists([('UseReference','u')],neg(USE))),'ExactDefinitionUse':('DefinitionVersionReference',uw(eq(fn('useDefinitionVersion',U),const('SELECTED_DEFINITION')))),'NarrowerUseScope':('ScopeReference',uw(neg(eq(fn('useScope',U),fn('resolutionScope',fn('useResolution',U)))))),'UseWithoutActualOutcomes':('UseReference',uw(both(*[neg(pred('UseActual'+n,U)) for n in USE_ACTUAL]))),'IndependentUseAuthority':('UseReference',uw(pred('UseActualAuthorityEffect',U)))}
    for kind in OUTPUT_KINDS:rows[kind+'OutputOnly']=('OutputReference',ow(both(pred('Output'+kind+'Declared',O),*[neg(pred('Output'+other+'Declared',O)) for other in OUTPUT_KINDS if other!=kind])))
    return rows
def query_specs():
    return [{'query_id':prefix+'-not-Actual'+n,'target':allof([(sort,name)],implies(app,pred(prefix+'Actual'+n,name))),'witness_condition':exists([(sort,name)],both(app,neg(pred(prefix+'Actual'+n,name)))),'selected_in_T':False,'source_condition':'selected-'+prefix.lower(),'source_fidelity':'pending'} for prefix,sort,name,app,outcomes in [('Resolution','ResolutionReference','x',APP,ACTUAL),('Use','UseReference','u',USE,USE_ACTUAL)] for n in outcomes]
def selected_clauses(doc):
    chosen={'/voices/scientific_formal/normative_statement':(both(ROOT_RULE,OUTPUT_RULE,BOUNDARIES,ROOT_NONINFERENCE),['genus-differentia']),'/voices/scientific_formal/formal_expression':(both(ROOT_RULE,ROOT_NONINFERENCE),['axiomatic-implicit']),'/scope/applicability':(both(ROOT_RULE,OUTPUT_RULE),['genus-differentia']),'/scope/exclusions/0':(both(BOUNDARIES,ROOT_NONINFERENCE),['operational']),'/scope/exclusions/1':(ROOT_NONINFERENCE,['operational']),'/voices/scientific_formal/boundary_conditions/0':(both(ROOT_RULE,OUTPUT_RULE),['operational']),'/voices/scientific_formal/boundary_conditions/1':(both(BOUNDARIES,ROOT_NONINFERENCE),['operational']),'/voices/scientific_formal/boundary_conditions/2':(FACET_RULE,['operational']),'/voices/scientific_formal/testable_conditions/0':(USE_RULE,['operational']),'/voices/scientific_formal/testable_conditions/1':(both(ROOT_RULE,USE_SCOPE),['operational']),'/voices/scientific_formal/testable_conditions/2':(both(ROOT_NONINFERENCE,USE_NONINFERENCE),['operational']),'/boundaries/0':(both(BOUNDARIES,ROOT_NONINFERENCE),['operational']),'/boundaries/1':(CONTRACT_RULE,['operational'])}
    texts=dict(co.string_leaves(doc));rows=[]
    for unit in co.inventory(doc):
        selector=unit['selector'];formula,forms=chosen.get(selector,(None,['unresolved']));disposition='encoded' if formula is not None else 'explanatory' if selector.startswith('/voices/') and any(s in selector for s in ['/domain_context/','/plain_language/','/notation/']) else 'deferred';rows.append({'source_selector':selector,'start_character':0,'excerpt':texts[selector],'formula':formula,'forms':forms,'disposition':disposition,'unit_id':unit['unit_id']})
    return rows

def main():
    context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);external_current(context);snap=snapshot();r.verify(snap,ROOT);source=context['source_selection']
    assert source['definition_id']=='cal.definition.intent-resolution' and source['sha256']=='cf84080dba84433926c7f11759057ca4277458152518aaa243d61a948e96c136'
    doc=co.source_document(snap,source);units=co.inventory(doc);clauses=[];links=[]
    reasons={'encoded':'Necessary nominated owner decision, exact Intent, one or more governed outputs, test and bounded scope, separate effects and scoped exact Definition-use guards; actual outcomes remain independent.','explanatory':'Notation, intuition and example explain the source without creating authority, an exhaustive output taxonomy or mandatory realization.','deferred':'Authority scope and historical candidate no-effect ceiling remain explicit source obligations.'}
    for spec in selected_clauses(doc):
        cid='IRES-'+str(len(clauses)+1).zfill(3);disposition=spec['disposition'];clauses.append({'clause_id':cid,'source_selector':spec['source_selector'],'excerpt_sha256':r.digest(spec['excerpt'].encode()),'start_character':spec['start_character'],'disposition':disposition,'forms':spec['forms'],'roles':['definition'] if disposition=='encoded' else ['explanation-example'] if disposition=='explanatory' else ['unresolved'],'formal_statement':spec['formula'],'rationale':reasons[disposition]});links.append({'unit_id':spec['unit_id'],'clause_id':cid,'end_character':len(spec['excerpt']),'excerpt':spec['excerpt']})
    deps=[source_ref(snap,name) for name in context['direct_dependency_names']];primary=clauses[0]['clause_id'];req=required_populations()
    populations=[{'population_id':'POP-REQ-'+name,'carrier':carrier,'predicate_ref':None,'requirement':'required','statement':formula,'scope':SCOPE,'rationale':'Nonvacuous owner-decision, multiple nomination, open output role, shared selection, exact Intent, scope, use and independent-outcome witnesses.','review_ref':None} for name,(carrier,formula) in req.items()]+[{'population_id':'POP-UNRESOLVED-'+name,'carrier':args[0],'predicate_ref':name if len(args)==1 else None,'requirement':'unresolved','statement':None,'scope':SCOPE,'rationale':'Actual populations and accepted owner or consumer denotations remain unresolved.','review_ref':None} for name,args in SIGNATURE.items()]
    core={'source':source,'interpretation_id':'interpretation:IntentResolution-owner-decision-exact-intent-governed-outputs-test-use-v1','profile_ref':'profile:definition-assurance-partial-types-logic-v1','scope':SCOPE,'semantic_status':'candidate','source_fidelity':'pending','logic_features':['first-order','equality'],'declarations':declarations(),'clauses':clauses,'depends_on':deps,'relations':[],'assumptions':[],'populations':populations}
    findings=[{'finding_id':'IRES-FINDING-'+str(i+1).zfill(3),'description':loss,'selectors':['/voices/scientific_formal/normative_statement','/voices/scientific_formal/formal_expression','/scope/applicability'],'status':'unresolved','owner_route':'role:definition-owner with Intent, output, owner-decision, attribution, satisfaction-test, scope, evidence and authority owners'} for i,loss in enumerate(LOSSES)]
    packet={'schema_version':'definition-assurance-correspondence/v1-candidate','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'authority_effect':'none','source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':[{'clause_id':primary,'dependency_ref':dep,'kind':'semantic-use','rationale':'Separately qualified semantic dependency or explicit boundary comparison; no accepted common carrier, concept equivalence or whole prior theory imported.'} for dep in deps],'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':LOSSES},'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},'review_packet':{'instances':[{'case_id':'owner-selects-several-governed-outputs-under-test','scenario':'A resolution selects Product, Project, Capability and other output nominations for one exact Intent under a declared satisfaction test; owners and attributors can be multiple.','expected_interpretation':'Necessary nominated relationships hold while actual owner authority, suitable delivery and satisfaction remain independent.','rationale':'The source example permits several outputs, and attribution is distinct from authorization.','related_clause_ids':[primary]}],'counterexamples':[{'case_id':'declared-selected-output-without-test-link','scenario':'The resolution nominates a satisfaction-test handle but a selected output has no matching under-test link.','expected_interpretation':'The output-under-test necessary guard fails.','rationale':'Nominating a test coordinate alone cannot replace the selected relationship.','related_clause_ids':[primary]}],'known_losses':LOSSES,'review_status':'pending','review_ref':None}}
    account=co.check(packet,snap,required_dependencies=[d['version_ref'] for d in deps],required_conflicts=[f['finding_id'] for f in findings]);assert account['character_accounting_complete']
    for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',ir.compile_interpretation(core,snap)),('correspondence-check.json',account)]:put(name,value)
    queries=query_specs();put('query-policy.json',{'authority_effect':'none','queries':queries,'targets_not_assumptions':True,'whole_definition_proof_claimed':False});obligations=[]
    for clause,link in zip(clauses,links):
        if clause['disposition']=='explanatory':continue
        selector=clause['source_selector'];targets=['Resolution-not-ActualSourceFidelity','Resolution-not-ActualWholeProof']
        if selector in ['/voices/scientific_formal/normative_statement','/scope/applicability','/voices/scientific_formal/boundary_conditions/0']:targets+=['Resolution-not-ActualIntentReferenceResolution','Resolution-not-ActualOwnerDecisionAuthenticity','Resolution-not-ActualOwnerAuthorization','Resolution-not-ActualAttributionAuthenticity','Resolution-not-ActualOutputGovernance','Resolution-not-ActualOutputSuitability','Resolution-not-ActualSatisfactionTestResolution','Resolution-not-ActualSatisfactionTestAdequacy']
        if selector.startswith('/boundaries/') or selector.startswith('/scope/exclusions/') or '/boundary_conditions/' in selector:targets+=['Resolution-not-ActualDelivery','Resolution-not-ActualSatisfaction','Resolution-not-ActualImplementationSeparation','Resolution-not-ActualAuthorityEffect','Resolution-not-ActualScopeCompliance']
        if selector=='/voices/scientific_formal/formal_expression':targets+=['Resolution-not-ActualIdentityFidelity','Resolution-not-ActualScopeCompliance','Resolution-not-ActualAuthorityEffect']
        if selector.endswith('/boundary_conditions/2'):targets+=['Resolution-not-ActualLifecycleOperation','Resolution-not-ActualEvidenceAuthenticity','Resolution-not-ActualRelationOperation']
        if selector.endswith('/testable_conditions/0'):targets+=['Use-not-ActualDefinitionResolution','Use-not-ActualSuccessorAdmissionAuthenticity']
        if selector.endswith('/testable_conditions/1'):targets+=['Use-not-ActualApplicabilityCompliance','Use-not-ActualExclusionCompliance','Use-not-ActualScopeCompliance']
        if selector.endswith('/testable_conditions/2'):targets+=['Resolution-not-ActualInstanceAdmission','Resolution-not-ActualAuthorityEffect','Resolution-not-ActualExternalEffect','Use-not-ActualAuthorityEffect']
        if selector=='/claim_ceiling':targets+=['Resolution-not-ActualCarrierAdmission','Resolution-not-ActualInstanceAdmission','Resolution-not-ActualRuntimeActivation','Resolution-not-ActualPublication','Resolution-not-ActualRelease','Resolution-not-ActualDeployment','Resolution-not-ActualExternalEffect']
        for target in dict.fromkeys(targets):
            assert target in {q['query_id'] for q in queries};obligations.append({'source':source,'selector':selector,'start_character':0,'end_character':link['end_character'],'excerpt':link['excerpt'],'excerpt_sha256':clause['excerpt_sha256'],'clause_id':clause['clause_id'],'query_id':target,'selected_in_T':False,'necessary_declaration_guard_in_T':clause['disposition']=='encoded','actual_outcome_target_in_T':False})
    put('source-query-obligation.json',{'authority_effect':'none','obligations':obligations,'source_fidelity':'pending','whole_definition_proof_claimed':False})
    counts={'source_units':len(units),'mapped_clauses':len(clauses),**{name+'_clauses':sum(c['disposition']==name for c in clauses) for name in ['encoded','explanatory','deferred']},'declarations':len(core['declarations']),'required_populations':len(req),'unresolved_populations':len(SIGNATURE),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)};put('denominator.json',counts)
    put('clause-analysis.json',{'authority_effect':'none','source':source,'encoded_spans':counts['encoded_clauses'],'unique_encoded_source_formula_values':len({json.dumps(c['formal_statement'],sort_keys=True) for c in clauses if c['disposition']=='encoded'}),'primitive_theory_formulas':len(THEORY),'known_losses':LOSSES,'actual_outcome_queries_assumed_in_T':False,'whole_prior_theories_imported':False,'source_precedence_reviewed':False,'mechanized_proof':False,'governed_identity_or_record_inclusive':True,'multiple_outputs_allowed':True,'open_other_output_kind':True,'multiple_owners_and_attributors_allowed':True,'single_resolution_per_Intent_policy_added':False,'hypothetical_successor_is_actual_admission':False,'successor_or_global_version_policy_added':False,'selection_or_test_proves_actual_satisfaction':False})
    put('comparison-selection.json',{'authority_effect':'none','separate_qualified_sources':deps,'selected_refs':[{'path':d['path'],'sha256':d['sha256']} for d in deps]+context['sources'],'comparison_assembled_into_primary_T':False,'source_precedence_reviewed':False,'external_context_refs':context['external_sources'],'embedded_review_context':context['embedded_review_source'],'source_fidelity':'pending','claim_ceiling':'Necessary declared owner decision, exact Intent, governed output selection and satisfaction-test links only; no actual delivery, satisfaction, authority, accepted denotations, fidelity or whole proof.'})
    c.validate(json.loads((UNIT/'t.json').read_bytes()),'interpretation');unchanged(context['sources']);external_current(context);print(json.dumps(counts,indent=2,sort_keys=True))
if __name__=='__main__':main()
