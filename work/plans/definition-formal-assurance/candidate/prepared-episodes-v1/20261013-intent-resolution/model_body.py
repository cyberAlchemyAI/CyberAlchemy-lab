"""Independent nonvacuous controls for necessary declarations and coverage."""
import copy,json
import build_candidate as b
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def getfn(m,name,arg):return next(r['value'] for r in m['functions'][name] if r['args']==[arg])
def setfn(m,name,arg,value):next(r for r in m['functions'][name] if r['args']==[arg])['value']=value
def refresh(m):
    for fields,carrier in b.GROUPS:
        for name in fields:m['predicates'][name+'BindingDeclared']=[[r['args'][0],r['value']] for r in m['functions'][name]]
    selected=[r[0] for r in m['predicates']['ResolutionApplicable']]
    m['predicates']['ResolutionSelectsOutputDeclared']=[[x,o] for x in selected for col,o in m['predicates']['OutputCollectionContainsDeclared'] if col==getfn(m,'resolutionOutputs',x)]
    m['predicates']['ResolutionOutputAddressesIntentDeclared']=[[x,o,getfn(m,'resolutionIntent',x)] for x,o in m['predicates']['ResolutionSelectsOutputDeclared']]
    m['predicates']['ResolutionOutputUnderTestDeclared']=[[x,o,getfn(m,'resolutionSatisfactionTest',x)] for x,o in m['predicates']['ResolutionSelectsOutputDeclared']]
def base_model():
    domains={s:[s+'0',s+'1',s+'Outside'] for s in b.SORTS}
    domains.update(ResolutionReference=['r0','r1','r2','r3','rOutside'],IntentReference=['i0','i1','i2','iOutside'],OwnerDecisionReference=['d0','d1','d2','d3','dOutside'],OwnerReference=['owner0','owner1','ownerOutside'],AttributorReference=['attr0','attr1','attrOutside'],OutputCollectionReference=['allOutputs','productOnly','projectOnly','otherOnly','emptyOutside'],OutputReference=['product','project','goal','research','capability','other','mixed','outputOutside'],SatisfactionTestReference=['test0','test1','test2','testOutside'],ScopeReference=['scope0','scope1','narrow0','scopeOutside'],UseReference=['u0','u1','u2','uOutside'],DefinitionVersionReference=['dvSelected','dvHypothetical','dvOutside'],Token=['empty','token'])
    m={'domains':domains,'constants':{'EMPTY':'empty','SELECTED_DEFINITION':'dvSelected'},'functions':{},'predicates':{n:[] for n in b.SIGNATURE}}
    for n,(args,result) in b.FUNCTIONS.items():m['functions'][n]=[{'args':[a],'value':'token' if n in b.HANDLES.values() else domains[result][0]} for a in domains[args[0]]]
    for sort in b.SORTS:
        if sort!='Token':m['predicates'][sort+'Declared']=[[a] for a in domains[sort]]
    selected=['r0','r1','r2','r3']
    for n in ['ResolutionApplicable','ResolutionInScopeDeclared','ResolutionBoundedScopeDeclared',*['Resolution'+n+'SeparatelyGovernedDeclared' for n in b.FACETS],*['Resolution'+n+'NeedsSeparateContractDeclared' for n in b.CONTRACTS]]:m['predicates'][n]=[[r] for r in selected]
    m['predicates']['ResolutionGovernedIdentityDeclared']=[['r0'],['r2'],['r3']];m['predicates']['ResolutionGovernedRecordDeclared']=[['r1'],['r2']]
    for i in range(4):setfn(m,'resolutionOwnerDecision','r'+str(i),'d'+str(i))
    for r,i,col,test,scope in [('r0','i0','allOutputs','test0','scope0'),('r1','i0','productOnly','test0','scope1'),('r2','i1','projectOnly','test1','scope0'),('r3','i2','otherOnly','test2','scope1')]:
        for n,value in [('resolutionIntent',i),('resolutionOutputs',col),('resolutionSatisfactionTest',test),('resolutionScope',scope)]:setfn(m,n,r,value)
    m['predicates']['IntentExactVersionDeclared']=[['i0'],['i1'],['i2']];m['predicates']['OwnerDecisionDeclared']=[['d0'],['d1'],['d2'],['d3']]
    m['predicates']['DecisionOwnerDeclared']=[[d,'owner0'] for d in ['d0','d1','d2','d3']]+[['d0','owner1']]
    m['predicates']['DecisionAttributionDeclared']=[[d,'attr0'] for d in ['d0','d1','d2','d3']]+[['d0','attr1']]
    outputs=domains['OutputReference'][:-1];m['predicates']['OutputGovernedDeclared']=[[o] for o in outputs]
    m['predicates']['OutputCollectionContainsDeclared']=[['allOutputs',o] for o in outputs]+[['productOnly','product'],['projectOnly','project'],['otherOnly','other']]
    for kind in b.OUTPUT_KINDS:m['predicates']['Output'+kind+'Declared']=[[kind.lower()]]
    m['predicates']['OutputProductDeclared'].append(['mixed']);m['predicates']['OutputGoalDeclared'].append(['mixed'])
    m['predicates']['ResolutionActualAuthorityEffect']=[['r3']]
    for n in ['UseApplicable','UseInScopeDeclared','UseWithinApplicabilityDeclared','UseRespectsExclusionsDeclared']:m['predicates'][n]=[['u0'],['u1'],['u2']]
    for use,res,scope in [('u0','r0','narrow0'),('u1','r1','scope1'),('u2','r2','scope0')]:
        setfn(m,'useResolution',use,res);setfn(m,'useScope',use,scope);setfn(m,'useDefinitionVersion',use,'dvSelected')
    m['predicates']['UseScopeWithinResolutionDeclared']=[['narrow0','scope0'],['scope1','scope1'],['scope0','scope0']];m['predicates']['DefinitionVersionAdmissionDeclared']=[['dvSelected']];m['predicates']['UseActualAuthorityEffect']=[['u2']]
    refresh(m);return m
def controls():
    baseline=base_model();rows=[]
    def add(name,mutation=lambda m:None,T=True,I=True,error=None):
        model=copy.deepcopy(baseline);mutation(model);rows.append({'case_id':name,'model':model,'expected_T':T,'expected_I':I,'expected_error':error})
    def change(m,name,arg,value):setfn(m,name,arg,value);refresh(m)
    add('attributable-owner-decisions-exact-Intent-open-governed-outputs-and-tests')
    def none_selected(m):
        for n in ['ResolutionApplicable','ResolutionInScopeDeclared','UseApplicable','UseInScopeDeclared']:m['predicates'][n]=[]
        refresh(m)
    add('no-selected-resolutions-or-uses',none_selected,I=False)
    def no_uses(m):m['predicates']['UseApplicable']=[];m['predicates']['UseInScopeDeclared']=[]
    add('no-selected-uses',no_uses,I=False)
    for prefix,outcomes,subject in [('Resolution',b.ACTUAL,'r0'),('Use',b.USE_ACTUAL,'u0')]:
        for n in outcomes:add('independently-supported-'+prefix+n,lambda m,prefix=prefix,n=n,subject=subject:m['predicates'][prefix+'Actual'+n].append([subject]),I=None)
    for n in b.EXCLUDED:
        add('selected-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['r0']),T=False,I=None);add('outside-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['rOutside']))
    for prefix,subject,outside in [('Resolution','r0','rOutside'),('Use','u0','uOutside')]:
        for n in b.INFERRED:
            symbol=prefix+'TermInfers'+n+'Declared';add('selected-term-inference-'+symbol,lambda m,symbol=symbol,subject=subject:m['predicates'][symbol].append([subject]),T=False,I=None);add('outside-term-inference-'+symbol,lambda m,symbol=symbol,outside=outside:m['predicates'][symbol].append([outside]))
    for n in ['ResolutionBoundedScopeDeclared','ResolutionInScopeDeclared',*['Resolution'+n+'SeparatelyGovernedDeclared' for n in b.FACETS],*['Resolution'+n+'NeedsSeparateContractDeclared' for n in b.CONTRACTS]]:add('missing-'+n,lambda m,n=n:m['predicates'][n].remove(['r0']),T=False,I=None)
    add('neither-governed-identity-nor-record',lambda m:m['predicates']['ResolutionGovernedIdentityDeclared'].remove(['r0']),T=False,I=None)
    add('both-governed-modes-reduced-to-record',lambda m:m['predicates']['ResolutionGovernedIdentityDeclared'].remove(['r2']),I=False)
    add('Intent-without-exact-version-nomination',lambda m:m['predicates']['IntentExactVersionDeclared'].remove(['i0']),T=False,I=None)
    add('owner-decision-designation-missing',lambda m:m['predicates']['OwnerDecisionDeclared'].remove(['d0']),T=False,I=None)
    def remove_decision_links(m,n):m['predicates'][n]=[r for r in m['predicates'][n] if r[0]!='d0']
    add('owner-decision-without-owner',lambda m:remove_decision_links(m,'DecisionOwnerDeclared'),T=False,I=None)
    add('owner-decision-without-attribution',lambda m:remove_decision_links(m,'DecisionAttributionDeclared'),T=False,I=None)
    add('multiple-owners-reduced-to-one',lambda m:m['predicates']['DecisionOwnerDeclared'].remove(['d0','owner1']),I=False)
    add('multiple-attributors-reduced-to-one',lambda m:m['predicates']['DecisionAttributionDeclared'].remove(['d0','attr1']),I=False)
    for relation,sort,value,other in [('DecisionOwnerDeclared','OwnerReference','owner0','owner1'),('DecisionAttributionDeclared','AttributorReference','attr0','attr1')]:
        def bad_nomination(m,relation=relation,sort=sort,value=value,other=other):
            m['predicates'][relation].remove(['d0',other]);m['predicates'][sort+'Declared'].remove([value])
        add('no-declared-nominee-'+relation,bad_nomination,T=False,I=None)
        def empty_nomination(m,relation=relation,sort=sort,value=value,other=other):
            m['predicates'][relation].remove(['d0',other]);setfn(m,b.HANDLES[sort],value,'empty')
        add('no-nonempty-nominee-'+relation,empty_nomination,T=False,I=None)
    add('empty-selected-output-collection',lambda m:change(m,'resolutionOutputs','r0','emptyOutside'),T=False,I=None)
    add('missing-selected-output-link',lambda m:m['predicates']['ResolutionSelectsOutputDeclared'].remove(['r0','product']),T=False,I=None)
    add('extra-output-link-outside-collection',lambda m:m['predicates']['ResolutionSelectsOutputDeclared'].append(['r0','outputOutside']),T=False,I=None)
    add('selected-output-not-governed',lambda m:m['predicates']['OutputGovernedDeclared'].remove(['product']),T=False,I=None)
    add('selected-output-without-any-role',lambda m:m['predicates']['OutputOtherDeclared'].remove(['other']),T=False,I=None)
    add('missing-output-addresses-Intent-link',lambda m:m['predicates']['ResolutionOutputAddressesIntentDeclared'].remove(['r0','product','i0']),T=False,I=None)
    add('missing-output-under-satisfaction-test-link',lambda m:m['predicates']['ResolutionOutputUnderTestDeclared'].remove(['r0','product','test0']),T=False,I=None)
    add('wrong-output-Intent-target',lambda m:(m['predicates']['ResolutionOutputAddressesIntentDeclared'].remove(['r0','product','i0']),m['predicates']['ResolutionOutputAddressesIntentDeclared'].append(['r0','product','i1'])),T=False,I=None)
    add('wrong-output-test-target',lambda m:(m['predicates']['ResolutionOutputUnderTestDeclared'].remove(['r0','product','test0']),m['predicates']['ResolutionOutputUnderTestDeclared'].append(['r0','product','test1'])),T=False,I=None)
    for sort,subject in [('OutputReference','product'),('SatisfactionTestReference','test0'),('IntentReference','i0'),('OwnerDecisionReference','d0')]:
        add('undeclared-selected-'+sort,lambda m,sort=sort,subject=subject:m['predicates'][sort+'Declared'].remove([subject]),T=False,I=None)
        add('empty-selected-'+sort+'-handle',lambda m,sort=sort,subject=subject:setfn(m,b.HANDLES[sort],subject,'empty'),T=False,I=None)
    add('mixed-output-roles-reduced-to-one',lambda m:m['predicates']['OutputGoalDeclared'].remove(['mixed']),I=False)
    def all_single(m):
        for r,col in [('r0','productOnly'),('r1','productOnly'),('r2','projectOnly'),('r3','otherOnly')]:setfn(m,'resolutionOutputs',r,col)
        refresh(m)
    add('all-output-collections-singleton',all_single,I=False)
    def unique_intents(m):change(m,'resolutionIntent','r1','i2');change(m,'resolutionIntent','r3','iOutside');m['predicates']['IntentExactVersionDeclared'].append(['iOutside'])
    add('each-selected-resolution-different-Intent',unique_intents,I=False)
    add('shared-test-separated',lambda m:change(m,'resolutionSatisfactionTest','r1','testOutside'),I=False)
    add('use-targets-unselected-resolution',lambda m:change(m,'useResolution','u0','rOutside'),T=False,I=None)
    for n in ['UseInScopeDeclared','UseWithinApplicabilityDeclared','UseRespectsExclusionsDeclared']:add('missing-'+n,lambda m,n=n:m['predicates'][n].remove(['u0']),T=False,I=None)
    add('use-scope-not-within-resolution',lambda m:m['predicates']['UseScopeWithinResolutionDeclared'].remove(['narrow0','scope0']),T=False,I=None)
    add('all-use-scopes-equal-resolution-scopes',lambda m:change(m,'useScope','u0','scope0'),I=False)
    add('unknown-definition-use-without-successor-or-admission',lambda m:change(m,'useDefinitionVersion','u1','dvHypothetical'),T=False,I=None)
    def successor(m,relation=True,admission=True):
        change(m,'useDefinitionVersion','u1','dvHypothetical')
        if relation:m['predicates']['DefinitionVersionAdmittedSuccessorDeclared'].append(['dvSelected','dvHypothetical'])
        if admission:m['predicates']['DefinitionVersionAdmissionDeclared'].append(['dvHypothetical'])
    add('hypothetical-admitted-successor-use-not-actual-admission',successor)
    add('hypothetical-successor-without-admission',lambda m:successor(m,admission=False),T=False,I=None)
    add('hypothetical-admission-without-successor',lambda m:successor(m,relation=False),T=False,I=None)
    add('selected-Definition-admission-declaration-missing',lambda m:m['predicates']['DefinitionVersionAdmissionDeclared'].remove(['dvSelected']),T=False,I=None)
    for fields,carrier in b.GROUPS:
        subject='r0' if carrier=='ResolutionReference' else 'u0';outside='rOutside' if carrier=='ResolutionReference' else 'uOutside'
        for name,sort in fields.items():
            value=getfn(baseline,name,subject)
            add('missing-binding-'+name,lambda m,name=name,subject=subject,value=value:m['predicates'][name+'BindingDeclared'].remove([subject,value]),T=False,I=None)
            other=next(v for v in baseline['domains'][sort] if v!=value)
            add('extra-binding-'+name,lambda m,name=name,subject=subject,other=other:m['predicates'][name+'BindingDeclared'].append([subject,other]),T=False,I=None)
            outside_other=next(v for v in baseline['domains'][sort] if v!=getfn(baseline,name,outside))
            add('outside-extra-binding-'+name,lambda m,name=name,outside=outside,outside_other=outside_other:m['predicates'][name+'BindingDeclared'].append([outside,outside_other]))
            if sort not in b.MAP:add('undeclared-selected-target-'+name,lambda m,sort=sort,value=value:m['predicates'][sort+'Declared'].remove([value]),T=False,I=None)
            add('empty-selected-target-'+name,lambda m,sort=sort,value=value:setfn(m,b.HANDLES[sort],value,'empty'),T=False,I=None)
    for sort,subject in [('ResolutionReference','r0'),('UseReference','u0')]:add('empty-selected-root-'+sort,lambda m,sort=sort,subject=subject:setfn(m,b.HANDLES[sort],subject,'empty'),T=False,I=None)
    for sort in b.SORTS:
        if sort=='Token':continue
        unused=baseline['domains'][sort][-1]
        # Scope, version and collection outside values remain unused in this baseline.
        add('unused-'+sort+'-handle-empty',lambda m,sort=sort,unused=unused:setfn(m,b.HANDLES[sort],unused,'empty'))
    add('undeclared-model-predicate',lambda m:m['predicates'].update({'UnknownPredicate':[]}),T=None,I=None,error='model-signature-denominator-mismatch')
    add('duplicate-domain-element',lambda m:m['domains']['IntentReference'].append('i0'),T=None,I=None,error='empty-or-malformed-domain')
    add('empty-sort-domain',lambda m:m['domains'].__setitem__('OwnerReference',[]),T=None,I=None,error='empty-or-malformed-domain')
    add('missing-total-function-case',lambda m:m['functions']['resolutionIntent'].pop(),T=None,I=None,error='nontotal-function')
    add('function-result-outside-sort',lambda m:setfn(m,'resolutionIntent','r0','absent'),T=None,I=None,error='ill-sorted-function-result')
    add('predicate-argument-outside-sort',lambda m:m['predicates']['ResolutionApplicable'].append(['absent']),T=None,I=None,error='ill-sorted-model-tuple')
    return rows
def qualify(model,ids):
    return {'domains':{ids[n]:values for n,values in model['domains'].items()},'constants':{ids.get(n,n):value for n,value in model['constants'].items()},'functions':{ids.get(n,n):rows for n,rows in model['functions'].items()},'predicates':{ids.get(n,n):rows for n,rows in model['predicates'].items()}}
