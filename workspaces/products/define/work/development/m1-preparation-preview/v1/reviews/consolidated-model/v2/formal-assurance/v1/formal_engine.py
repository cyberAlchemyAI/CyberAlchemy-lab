"""Typed interpreted theory and finite witnesses for the exact revised cohort.

This is a bounded author interpretation, not a source-to-logic equivalence theorem.
"""
import copy
import itertools
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[9]
sys.path.insert(0,str(ROOT/'craft/formalization/candidates/definition-assurance-v1'))
import ir
import verifier


def load(path):return json.loads((ROOT/path).read_text())
def V(name):return {'op':'var','name':name}
def P(name,*args):return {'op':'pred','name':name,'args':list(args) or [V('x')]}
def AND(*args):return {'op':'and','args':list(args)}
def OR(*args):return {'op':'or','args':list(args)}
def NOT(arg):return {'op':'not','arg':arg}
def BIN(op,left,right):return {'op':op,'left':left,'right':right}
def Q(op,var,body,sort='Entity'):return {'op':op,'var':var,'sort':sort,'body':body}
def C(entity):return {'op':'const','name':'entity_'+entity}


def build():
    base='define/development/m1-preparation-preview/v1/steps/09-assurance-evidence-closure/'
    old=load(base+'formal-core.json')
    original=load(base+'witnesses.json')['finite_models'][0]['model']
    declarations=copy.deepcopy(old['declarations'])
    frames=copy.deepcopy(old['frames'])
    frames['Pack']+=['EmbeddedMeaningBindingsValid','SeparateAssessmentBindingsValid','MaterializationSelectionExplicit']
    frames['Define']+=['MeaningBindingSeparationOutcome','AssessmentProvenanceOutcome','ExplicitMaterializationOutcome']
    frames.update({
        'DefinitionApplication':['VersionExact','ApplicationRevisionExact','WellFormedApplication'],
        'ModelInstanceBinding':['ExactParentInstanceRevisions','InheritedAuthorityClauses','DeclaredExtensionOverrideScope','BindingConformanceAdoption','BindingOwnerSuccessionChallenge'],
        'MeasurementResult':['ExactMeasurementExecution','ValuesUnitsUncertainty','ToolImplementationTimestamps','RawEvidenceReceipt','ResultValidityPosture'],
        'CapabilityRealizationBinding':['ExactCapabilityImplementationAssociation','RealizationAdoptionPosture','DeploymentCompatibilityConformance','RealizationOwnerSuccessionChallenge'],
    })
    model=copy.deepcopy(original)
    entities=model['domains']['Entity']
    new_entities=['DefinitionApplication','ModelInstanceBinding','MeasurementResult','CapabilityRealizationBinding','assessment']
    for entity in new_entities:
        entities.append(entity);model['constants']['entity_'+entity]=entity
        declarations.append({'symbol_id':'entity_'+entity,'kind':'constant','result_sort':'Entity'})
    domains={'Parameter':['S','A','F','E','tolerance'],'Value':['snapshot','account','filter','output','retry','number'],'ValueType':['string','object','number'],'Meaning':['criterion','other']}
    for sort,values in domains.items():
        declarations.append({'symbol_id':sort,'kind':'sort','domain_policy':'nonempty'});model['domains'][sort]=values
    unary=['ApplicationRevisionExact','ExactTaskContextUse','MeaningSelectionExact','ParameterContractDeclared','ValueProvenanceRecorded','MeaningUnchanged','RequiredReferencesResolved','ApplicabilityEstablished','WellFormedApplication','FullyBoundApplication','EmbeddedMeaningBindingsValid','SeparateAssessmentBindingsValid','MaterializationSelectionExplicit','MeaningBindingSeparationOutcome','AssessmentProvenanceOutcome','ExplicitMaterializationOutcome','PreservesMeaningAndBindingSeparation','PreservesAssessmentProvenance','AssessmentIdentityExact','AssessmentInputEvidenceExact','AssessmentProducerPosture','AssessmentCoverageLimits','PreparationSelectionPurposeScopeOwner','EmissionSelected','DefinitionApplication','ModelInstanceBinding','MeasurementResult','CapabilityRealizationBinding']
    unary+=sum([frames[x] for x in new_entities[:4]],[])
    for name in sorted(set(unary)-set(model['predicates'])):
        declarations.append({'symbol_id':name,'kind':'predicate','argument_sorts':['Entity']});model['predicates'][name]=[]
    relations={
        'SelectMeaning':['Entity','Meaning'],'ParameterAllowed':['Meaning','Parameter'],'ParameterRequired':['Meaning','Parameter'],
        'DeclaredParameterType':['Meaning','Parameter','ValueType'],'ValueHasType':['Value','ValueType'],
        'BindValue':['Entity','Parameter','Value'],'MissingParameterGap':['Entity','Parameter'],
        'EmbeddedApplication':['Entity','Entity'],'EmbeddedAssessment':['Entity','Entity'],'AssessesApplication':['Entity','Entity'],
        'SelectedMeaningCaptured':['Entity'],'WorkingMeaning':['Meaning'],'AdmittedMeaning':['Meaning'],
    }
    for name,sorts in relations.items():
        declarations.append({'symbol_id':name,'kind':'predicate','argument_sorts':sorts});model['predicates'][name]=[]
    x,m,n,p,v,w,t,a,y=map(V,['x','m','n','p','v','w','t','a','y'])
    exists_binding=Q('exists','v',P('BindValue',x,p,v),'Value')
    unique_meaning=Q('exists','m',AND(P('SelectMeaning',x,m),Q('forall','n',BIN('implies',P('SelectMeaning',x,n),BIN('eq',n,m)),'Meaning')),'Meaning')
    permitted_typed=Q('forall','p',Q('forall','v',BIN('implies',P('BindValue',x,p,v),Q('exists','m',AND(P('SelectMeaning',x,m),P('ParameterAllowed',m,p),Q('exists','t',AND(P('DeclaredParameterType',m,p,t),P('ValueHasType',v,t)),'ValueType')),'Meaning')),'Value'),'Parameter')
    single_value=Q('forall','p',Q('forall','v',Q('forall','w',BIN('implies',AND(P('BindValue',x,p,v),P('BindValue',x,p,w)),BIN('eq',v,w)),'Value'),'Value'),'Parameter')
    gaps=Q('forall','m',BIN('implies',P('SelectMeaning',x,m),Q('forall','p',BIN('iff',P('MissingParameterGap',x,p),AND(P('ParameterRequired',m,p),NOT(exists_binding))),'Parameter')),'Meaning')
    wf=AND(unique_meaning,*(P(name,x) for name in ['MeaningSelectionExact','ExactTaskContextUse','ParameterContractDeclared','ValueProvenanceRecorded','MeaningUnchanged','SelectedMeaningCaptured']),permitted_typed,single_value,gaps)
    all_required=Q('forall','m',BIN('implies',P('SelectMeaning',x,m),Q('forall','p',BIN('implies',P('ParameterRequired',m,p),exists_binding),'Parameter')),'Meaning')
    fully=AND(P('WellFormedApplication',x),all_required,P('RequiredReferencesResolved',x),P('ApplicabilityEstablished',x))
    embedded=Q('forall','a',BIN('implies',P('EmbeddedApplication',x,a),P('WellFormedApplication',a)))
    assessment=Q('forall','y',BIN('implies',P('EmbeddedAssessment',x,y),AND(*(P(name,y) for name in ['AssessmentIdentityExact','AssessmentInputEvidenceExact','AssessmentProducerPosture','AssessmentCoverageLimits']),Q('exists','a',AND(P('EmbeddedApplication',x,a),P('AssessesApplication',y,a),Q('forall','n',BIN('implies',P('AssessesApplication',y,n),BIN('eq',n,a))))))))
    materialization=BIN('implies',P('EmissionSelected',x),P('PreparationSelectionPurposeScopeOwner',x))
    new_derived={'WellFormedApplication':wf,'FullyBoundApplication':fully,'EmbeddedMeaningBindingsValid':embedded,'SeparateAssessmentBindingsValid':assessment,'MaterializationSelectionExplicit':materialization}
    sorts={d['symbol_id']:d['symbol_id'] for d in declarations if d['kind']=='sort'}
    symbols={d['symbol_id']:d for d in declarations if d['kind']!='sort'}
    def typed(f):return ir.formula(f,sorts,symbols)
    theory=[]
    for index,formula in enumerate(old['axioms']):
        if index<len(old['frames']):
            role=list(old['frames'])[index]
            formula=Q('forall','x',BIN('iff',P(role),AND(*(P(name) for name in frames[role]))))
        elif formula.get('op')=='forall' and formula.get('body',{}).get('op')=='forall' and formula['body'].get('body',{}).get('left',{}).get('name')=='ConformingDefineResult':
            formula=copy.deepcopy(formula)
            formula['body']['body']['right']['args'] += [P('PreservesMeaningAndBindingSeparation',V('d')),P('PreservesAssessmentProvenance',V('d'))]
        theory.append(typed(formula))
    for role in new_entities[:4]:theory.append(typed(Q('forall','x',BIN('iff',P(role),AND(*(P(name) for name in frames[role]))))))
    for name,formula in new_derived.items():theory.append(typed(Q('forall','x',BIN('iff',P(name),formula))))
    theory.append(typed(Q('forall','m',BIN('implies',P('WorkingMeaning',m),NOT(P('AdmittedMeaning',m))),'Meaning')))
    # Equality of a source parameter type is meaningful only when required
    # parameters are declared. This is an explicit interpreted population rule.
    theory.append(typed(Q('forall','m',Q('forall','p',BIN('implies',P('ParameterRequired',m,p),P('ParameterAllowed',m,p)),'Parameter'),'Meaning')))
    def add(name,*row):
        row=list(row)
        if row not in model['predicates'][name]:model['predicates'][name].append(row)
    for role,features in frames.items():
        for name in features:
            if name not in new_derived and name not in old['relational_pack_features']:add(name,role)
    for name in ['MeaningSelectionExact','ExactTaskContextUse','ParameterContractDeclared','ValueProvenanceRecorded','MeaningUnchanged','SelectedMeaningCaptured','RequiredReferencesResolved','ApplicabilityEstablished']:
        add(name,'DefinitionApplication')
    add('SelectMeaning','DefinitionApplication','criterion');add('WorkingMeaning','criterion')
    for parameter,value,type_name in [('S','snapshot','string'),('A','account','string'),('F','filter','object'),('E','output','string')]:
        add('ParameterAllowed','criterion',parameter);add('ParameterRequired','criterion',parameter);add('DeclaredParameterType','criterion',parameter,type_name);add('BindValue','DefinitionApplication',parameter,value)
    for value,type_name in [('snapshot','string'),('account','string'),('output','string'),('retry','string'),('filter','object'),('number','number')]:add('ValueHasType',value,type_name)
    add('EmbeddedApplication','Pack','DefinitionApplication');add('EmbeddedAssessment','Pack','assessment');add('AssessesApplication','assessment','DefinitionApplication')
    for name in ['AssessmentIdentityExact','AssessmentInputEvidenceExact','AssessmentProducerPosture','AssessmentCoverageLimits']:add(name,'assessment')
    for name in ['PreservesMeaningAndBindingSeparation','PreservesAssessmentProvenance']:add(name,'Pack')
    new_core={'schema_version':'cal.define-application-interpreted-theory/v1','authority_effect':'none','declarations':declarations,'axioms':theory,'frames':frames,'derived_rules':{**old['relational_pack_features'],**new_derived},'source_formulas':'formal-correspondence.json','assumptions':['Source-to-predicate interpretation is author supplied and requires scoped human fidelity acceptance.','Record identity/revision and typed population boundaries are supplied by the exact carrier; formula leaves do not authenticate ownership.','Assessment binding validity is distinct from correctness/conformance of the actual method and result.','Only the explicitly modeled finite relation populations and rule assignments are checked.'],'limits':['Not all natural-language clauses are mechanized; clause coverage records each disposition.','No whole-repository consistency, temporal theorem, production runtime conformance, owner authentication or admission.','Uses ir.formula and Denotation directly, not the full native provider/effect API or an admitted assurance receipt.']}
    return new_core,model


def derive(core,model):
    """Evaluate derived definitions before role membership; no direct frame-tag seed."""
    m=copy.deepcopy(model)
    declarations=core['declarations']
    for name,formula in core['derived_rules'].items():
        den=verifier.Denotation(declarations,m)
        m['predicates'][name]=[]
        for entity in m['domains']['Entity']:
            den.steps=0  # Each independent expression receives the fixed component budget.
            if den.truth(formula,{'x':entity}):m['predicates'][name].append([entity])
    for role,features in core['frames'].items():
        m['predicates'][role]=[[entity] for entity in m['domains']['Entity'] if all([entity] in m['predicates'][name] for name in features)]
    m['predicates']['DefineProductInstance']=[row for row in m['predicates']['Define'] if row in m['predicates']['ProductCapability']]
    # The exact revised result formula is the final inherited result axiom.
    result_axiom=next(f for f in core['axioms'] if f.get('op')=='forall' and f.get('body',{}).get('op')=='forall' and f['body'].get('body',{}).get('left',{}).get('name')=='ConformingDefineResult')
    den=verifier.Denotation(declarations,m);m['predicates']['ConformingDefineResult']=[]
    for x,d in itertools.product(m['domains']['Entity'],repeat=2):
        den.steps=0
        if den.truth(result_axiom['body']['body']['right'],{'x':x,'d':d}):m['predicates']['ConformingDefineResult'].append([x,d])
    return m


def verify(core,model):
    # Validate the same complete signature independently for each axiom. Each
    # query retains Denotation's component limit; no larger solver guarantee.
    for i,formula in enumerate(core['axioms']):
        den=verifier.Denotation(core['declarations'],model)
        if not den.truth(formula):return False,i
    return True,None


def query(core,model,formula):
    sorts={d['symbol_id']:d['symbol_id'] for d in core['declarations'] if d['kind']=='sort'}
    symbols={d['symbol_id']:d for d in core['declarations'] if d['kind']!='sort'}
    typed=ir.formula(formula,sorts,symbols)
    return verifier.Denotation(core['declarations'],model).truth(typed),typed


def evidence(core,base_model):
    model=derive(core,base_model)
    ok,failed=verify(core,model)
    if not ok:raise ValueError('joint interpreted theory failed at axiom '+str(failed))
    comparisons=set(tuple(sorted(x)) for x in load('define/development/m1-preparation-preview/v1/steps/09-assurance-evidence-closure/interpretations.json')['comparison_pairs'])
    comparisons |= {tuple(sorted(['DefinitionApplication',name])) for name in core['frames'] if name!='DefinitionApplication'}
    comparisons |= set(itertools.combinations(sorted(['DefinitionApplication','Pack','Define','Definition','EvaluationProfile','LifecycleProfile']),2))
    pairs=[]
    for a,b in sorted(comparisons):
        for left,right in [(a,b),(b,a)]:
            statement=Q('exists','x',AND(P(left),NOT(P(right))))
            truth,typed=query(core,model,statement)
            if not truth:raise ValueError('missing non-collapse witness '+left+'/'+right)
            witness=next(e for e in model['domains']['Entity'] if [e] in model['predicates'][left] and [e] not in model['predicates'][right])
            pairs.append({'left':left,'right':right,'statement':typed,'witness':witness,'model':'joint','result':'CHECKED_INTERPRETED_NON_ENTAILMENT_COUNTERMODEL'})
    worlds=[{'name':'joint','model':model,'all_axioms_satisfied':True}]
    no_assessment=copy.deepcopy(base_model)
    for name in ['EmbeddedAssessment','AssessesApplication','ExecutionOccurred','AssessmentOccurred','ExactMeasurementExecution']:no_assessment['predicates'][name]=[]
    no_assessment=derive(core,no_assessment);ok,_=verify(core,no_assessment)
    if not ok:raise ValueError('optional-assessment world inconsistent')
    worlds.append({'name':'without-assessment','model':no_assessment,'all_axioms_satisfied':True})
    permission=copy.deepcopy(base_model);permission['predicates']['MayExecute'].append(['subject'])
    permission=derive(core,permission);ok,_=verify(core,permission)
    if not ok:raise ValueError('independent permission world inconsistent')
    worlds.append({'name':'independent-permission','model':permission,'all_axioms_satisfied':True})
    partial=copy.deepcopy(base_model);partial['predicates']['BindValue'].remove(['DefinitionApplication','F','filter']);partial['predicates']['MissingParameterGap']=[['DefinitionApplication','F']]
    partial=derive(core,partial);ok,_=verify(core,partial)
    if not ok or ['DefinitionApplication'] not in partial['predicates']['WellFormedApplication'] or ['DefinitionApplication'] in partial['predicates']['FullyBoundApplication']:raise ValueError('partial application collapsed')
    worlds.append({'name':'partial-with-explicit-gap','model':partial,'all_axioms_satisfied':True})
    overlaps=[]
    for a,b in [('Pack','GovernedModel'),('Define','ProductCapability'),('EvaluationProfile','Policy'),('LifecycleProfile','Policy')]:
        m=copy.deepcopy(base_model)
        for field in core['frames'][b]:
            if [a] not in m['predicates'][field]:m['predicates'][field].append([a])
        m=derive(core,m);ok,_=verify(core,m)
        if not ok or not ([a] in m['predicates'][b]):raise ValueError('overlap witness failed '+a+'/'+b)
        name='overlap:'+a+'/'+b;worlds.append({'name':name,'model':m,'all_axioms_satisfied':True});overlaps.append({'left':a,'right':b,'model':name,'claim':'Interpreted distinction does not assert complete-source disjointness'})
    boundaries=[]
    for role in ['DefinitionApplication','Pack','Define']:
        premise=P('FullyBoundApplication',C(role)) if role=='DefinitionApplication' else P(role,C(role))
        for effect in ['CanonicalAuthority','OwnerAdmissionSelected','AdmissionApplied','MayExecute','GoalAchieved','ConsumerReady']:
            statement=BIN('implies',premise,P(effect,C('subject')))
            truth,typed=query(core,model,statement)
            if truth:raise ValueError('unwanted authority entailment '+role+'/'+effect)
            boundaries.append({'premise':role,'consequent':effect,'statement':typed,'model':'joint','result':'CHECKED_NON_ENTAILMENT'})
        statement=BIN('implies',premise,Q('exists','x',P('Evaluation')))
        truth,typed=query(core,no_assessment,statement)
        if truth:raise ValueError('preparation implied actual Evaluation '+role)
        boundaries.append({'premise':role,'consequent':'actual Evaluation','statement':typed,'model':'without-assessment','result':'CHECKED_NON_ENTAILMENT'})
    truth,typed=query(core,model,BIN('implies',P('FullyBoundApplication',C('DefinitionApplication')),Q('exists','m',P('AdmittedMeaning',V('m')),'Meaning')))
    if truth:raise ValueError('binding implies meaning admission')
    boundaries.append({'premise':'FullyBoundApplication','consequent':'selected meaning admission','statement':typed,'model':'joint','result':'CHECKED_NON_ENTAILMENT'})
    controls=[]
    def negative(name,mutate):
        m=copy.deepcopy(model);mutate(m)
        try:accepted,axiom=verify(core,m);error=None
        except verifier.VerificationFault as e:accepted=False;axiom=None;error=e.code
        if accepted:raise ValueError('counterexample missed '+name)
        controls.append({'case':name,'expected':'rejected asserted theory','accepted':accepted,'failed_axiom':axiom,'error':error,'result':'PASS'})
    negative('undeclared tolerance binding',lambda m:m['predicates']['BindValue'].append(['DefinitionApplication','tolerance','number']))
    negative('wrong parameter type',lambda m:m['predicates']['BindValue'].append(['DefinitionApplication','F','number']))
    negative('multiple values for one parameter',lambda m:m['predicates']['BindValue'].append(['DefinitionApplication','E','retry']))
    negative('multiple selected meanings',lambda m:m['predicates']['SelectMeaning'].append(['DefinitionApplication','other']))
    negative('missing required parameter without gap',lambda m:m['predicates']['BindValue'].remove(['DefinitionApplication','F','filter']))
    negative('spurious parameter gap',lambda m:m['predicates']['MissingParameterGap'].append(['DefinitionApplication','F']))
    negative('binding changes selected meaning',lambda m:m['predicates']['MeaningUnchanged'].remove(['DefinitionApplication']))
    negative('value provenance missing',lambda m:m['predicates']['ValueProvenanceRecorded'].remove(['DefinitionApplication']))
    negative('assessment points outside owning Pack',lambda m:m['predicates']['AssessesApplication'].__setitem__(0,['assessment','subject']))
    negative('assessment lacks exact evidence',lambda m:m['predicates']['AssessmentInputEvidenceExact'].remove(['assessment']))
    negative('assessment producer missing',lambda m:m['predicates']['AssessmentProducerPosture'].remove(['assessment']))
    negative('materialization selected without purpose scope owner',lambda m:m['predicates']['EmissionSelected'].append(['Pack']))
    negative('Pack preparation grants authority',lambda m:m['predicates']['PreparationGrantsNewAuthority'].append(['Pack']))
    negative('false Define result with lost assessment provenance',lambda m:m['predicates']['PreservesAssessmentProvenance'].remove(['Pack']))
    negative('working proposal relabeled admitted',lambda m:m['predicates']['AdmittedMeaning'].append(['criterion']))
    negative('typed foreign parameter',lambda m:m['predicates']['BindValue'].append(['DefinitionApplication','foreign','number']))
    # A label-only alias must collapse, unlike distinct declared obligations.
    alias=copy.deepcopy(core);alias['declarations'].append({'symbol_id':'ApplicationAlias','kind':'predicate','argument_sorts':['Entity']});am=copy.deepcopy(model);am['predicates']['ApplicationAlias']=copy.deepcopy(am['predicates']['DefinitionApplication'])
    statement=Q('forall','x',BIN('iff',P('DefinitionApplication'),P('ApplicationAlias')))
    truth,_=query(alias,am,statement)
    if not truth:raise ValueError('label-only collapse control missed')
    controls.append({'case':'identical encoded obligations under different labels','result':'PASS','observed':'equivalence detected; no non-collapse claimed'})
    return {'worlds':worlds,'pairs':pairs,'overlaps':overlaps,'boundaries':boundaries,'controls':controls,'pair_count':len(comparisons)}
