"""Supplied Principal recognition/reference/representation/current-grant declaration controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
def getfn(m,n,*args):return next(x['value'] for x in m['functions'][n] if x['args']==list(args))
def refresh(m):
 for fields,carrier in b.GROUPS:
  for n in fields:m['predicates'][n+'BindingDeclared']=[[x['args'][0],x['value']] for x in m['functions'][n]]
def base_model():
 ds={'PrincipalReference':['p0','p1','p2','p3','pOutside'],'PrincipalIdentityReference':['pid0','pid1','pid2','pid3','pidOutside'],'BoundaryReference':['b0','b1','b2','b3','bOutside'],'IssuerReference':['issuer0','issuer1','issuerOutside'],'ScopeReference':['identityScope','recognitionScope','scope0','scope1','scopeOutside'],'PrincipalUseReference':['u0','u1','u2','uOutside'],'RepresentationReference':['r0','r1','r2','r3','rOutside'],'SubjectReference':['s0','s1','s2','s3','s4','s5','sOutside'],'SubjectIdentityReference':['sid0','sid1','sid2','sid3','sidOutside'],'LifecycleReference':['life0','life1','life2','life3','lifeOutside'],'SubjectKindReference':['personKind','teamKind','agentKind','serviceKind','otherKind','kindOutside'],'AuthorizationReference':['a0','a1','a2','a3','aOutside'],'GrantReference':['g0','g1','gOutside'],'TimeReference':['t0','t1','tOutside'],'Token':['empty','reference','other']}
 def mapn(n,values):return lambda x:values.get(x,ds[b.FUNCTIONS[n][1]][-1])
 maps={'principalIdentity':mapn('principalIdentity',{'p'+str(i):'pid'+str(i) for i in range(4)}),'principalBoundary':mapn('principalBoundary',{'p'+str(i):'b'+str(i) for i in range(4)}),'principalScope':mapn('principalScope',{'p'+str(i):'identityScope' for i in range(4)}),'principalIssuer':mapn('principalIssuer',{'p0':'issuer0','p1':'issuer1','p2':'issuer0','p3':'issuer1'}),'boundaryIssuer':mapn('boundaryIssuer',{'b0':'issuer0','b1':'issuer1','b2':'issuer0','b3':'issuer1'}),'boundaryScope':mapn('boundaryScope',{'b'+str(i):'recognitionScope' for i in range(4)}),'usePrincipal':mapn('usePrincipal',{'u0':'p0','u1':'p1','u2':'p2'}),'useIdentity':mapn('useIdentity',{'u0':'pid0','u1':'pid1','u2':'pid2'}),'useIssuerBoundary':mapn('useIssuerBoundary',{'u0':'b0','u1':'b1','u2':'b2'}),'representationPrincipal':mapn('representationPrincipal',{'r0':'p0','r1':'p1','r2':'p2','r3':'p2'}),'representationBeforeSubject':mapn('representationBeforeSubject',{'r0':'s0','r1':'s1','r2':'s2','r3':'s3'}),'representationAfterSubject':mapn('representationAfterSubject',{'r0':'s4','r1':'s5','r2':'s2','r3':'s3'}),'subjectIdentity':mapn('subjectIdentity',{'s0':'sid0','s4':'sid0','s1':'sid1','s5':'sid1','s2':'sid2','s3':'sid3'}),'subjectLifecycle':mapn('subjectLifecycle',{'s0':'life0','s4':'life0','s1':'life1','s5':'life1','s2':'life2','s3':'life3'}),'subjectKind':mapn('subjectKind',{'s0':'personKind','s4':'personKind','s1':'teamKind','s5':'teamKind','s2':'agentKind','s3':'serviceKind'}),'authorizationPrincipal':mapn('authorizationPrincipal',{'a0':'p0','a1':'p1','a2':'p2','a3':'p1'}),'authorizationScope':mapn('authorizationScope',{'a0':'scope0','a1':'scope1','a2':'scope0','a3':'scope1'}),'authorizationTime':mapn('authorizationTime',{'a0':'t0','a1':'t1','a2':'t0','a3':'t1'}),'authorizationGrant':mapn('authorizationGrant',{'a0':'g0','a1':'g1'}),'grantIssuer':mapn('grantIssuer',{'g0':'issuer1','g1':'issuer0'})}
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['PrincipalReference','PrincipalUseReference','RepresentationReference','AuthorizationReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['PrincipalApplicable','PrincipalInScopeDeclared','PrincipalGovernedDeclared','PrincipalRecognizedIdentityDeclared','PrincipalBoundedScopeDeclared']:preds[n]=[['p'+str(i)] for i in range(4)]
 preds.update(PrincipalIdentityBackedDeclared=[['p0'],['p2'],['p3']],PrincipalRecordBackedDeclared=[['p1'],['p2']],PrincipalIdentityGovernedDeclared=[['pid'+str(i)] for i in range(4)],BoundaryRecordedDeclared=[['b'+str(i)] for i in range(4)],BoundaryAuthenticationDeclared=[['b0']],BoundaryAuthorizationDeclared=[['b1']],BoundaryOwnershipDeclared=[['b1'],['b2']],BoundaryAccountabilityDeclared=[['b3']],PrincipalActualAuthority=[['p1']])
 for n in ['UseApplicable','UseInScopeDeclared','UseRecordedDeclared','UseExactResolutionDeclared']:preds[n]=[['u0'],['u1'],['u2']]
 for n in ['RepresentationApplicable','RepresentationInScopeDeclared','RepresentationRecordedDeclared']:preds[n]=[['r'+str(i)] for i in range(4)]
 preds['SubjectGovernedDeclared']=[['s'+str(i)] for i in range(6)]
 preds.update(KindPersonDeclared=[['personKind']],KindTeamDeclared=[['teamKind']],KindAgentDeclared=[['agentKind']],KindServiceDeclared=[['serviceKind']])
 for n in ['AuthorizationApplicable','AuthorizationInScopeDeclared','AuthorizationRecordedDeclared']:preds[n]=[['a'+str(i)] for i in range(4)]
 preds.update(AuthorizationConsequentialDeclared=[['a0'],['a1']],AuthorizationExactCurrentGrantDeclared=[['a0'],['a1']],GrantRecordedDeclared=[['g0'],['g1']],GrantCurrentAtDeclared=[['g0','t0'],['g1','t1']],GrantAppliesToPrincipalDeclared=[['g0','p0'],['g1','p1'],['g1','p2']],GrantAppliesToScopeDeclared=[['g0','scope0'],['g1','scope1']])
 m={'domains':ds,'constants':{'EMPTY':'empty'},'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(n,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':n,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('exact-recognition-reference-subject-and-current-scoped-grant')
 add('no-selected-Principal-uses-representations-authorizations',lambda m:m['predicates'].update(PrincipalApplicable=[],PrincipalInScopeDeclared=[],UseApplicable=[],UseInScopeDeclared=[],RepresentationApplicable=[],RepresentationInScopeDeclared=[],AuthorizationApplicable=[],AuthorizationInScopeDeclared=[]),I=False)
 add('Principals-without-reference-uses',lambda m:m['predicates'].update(UseApplicable=[],UseInScopeDeclared=[]),I=False)
 add('Principals-without-representations',lambda m:m['predicates'].update(RepresentationApplicable=[],RepresentationInScopeDeclared=[]),I=False)
 add('Principals-without-authorizations',lambda m:m['predicates'].update(AuthorizationApplicable=[],AuthorizationInScopeDeclared=[]),I=False)
 add('no-independent-authority',lambda m:m['predicates'].update(PrincipalActualAuthority=[]),I=False)
 for prefix,names,selected in [('Principal',b.ROOT_ACTUAL,['p0','p1','p2','p3']),('Use',b.USE_ACTUAL,['u0','u1','u2']),('Representation',b.REP_ACTUAL,['r0','r1','r2','r3']),('Authorization',b.AUTH_ACTUAL,['a0','a1','a2','a3'])]:
  add('all-'+prefix+'-actual-outcomes-independently-supplied',lambda m,prefix=prefix,names=names,selected=selected:[m['predicates'].update({prefix+'Actual'+n:[[x] for x in selected]}) for n in names],I=False)
  for n in names:add('independently-supported-'+prefix+'-Actual'+n,lambda m,prefix=prefix,n=n,arg=selected[0]:m['predicates'][prefix+'Actual'+n].append([arg]))
 for names,arg,outside in [(b.ROOT_EXCLUDED,'p0','pOutside'),(b.USE_EXCLUDED,'u0','uOutside'),(b.REP_EXCLUDED,'r0','rOutside'),(b.AUTH_EXCLUDED,'a0','aOutside')]:
  for n in names:
   add('selected-excluded-'+n,lambda m,n=n,arg=arg:m['predicates'][n].append([arg]),T=False,I=None)
   add('outside-excluded-'+n,lambda m,n=n,outside=outside:m['predicates'][n].append([outside]))
 add('additional-overlapping-recognition-kind',lambda m:m['predicates']['BoundaryOwnershipDeclared'].append(['b0']))
 add('inclusive-identity-and-record-with-populations-preserved',lambda m:(m['predicates']['PrincipalRecordBackedDeclared'].append(['p0']),m['predicates']['PrincipalRecordBackedDeclared'].remove(['p2'])))
 add('separate-Principal-and-boundary-scope-allowed',lambda m:change(m,'boundaryScope','b0','scope1'))
 add('represented-subject-kind-change-with-preserved-identity-lifecycle',lambda m:change(m,'subjectKind','s4','agentKind'))
 add('unnamed-subject-kind-with-preserved-identity-lifecycle',lambda m:change(m,'subjectKind','s4','otherKind'))
 add('same-subject-reference-preservation-allowed',lambda m:change(m,'representationAfterSubject','r0','s0'))
 add('same-recognition-and-grant-issuer-allowed',lambda m:change(m,'grantIssuer','g0','issuer0'))
 add('grant-applies-to-additional-Principal',lambda m:m['predicates']['GrantAppliesToPrincipalDeclared'].append(['g0','p1']))
 add('grant-applies-to-additional-scope',lambda m:m['predicates']['GrantAppliesToScopeDeclared'].append(['g0','scope1']))
 add('grant-current-at-additional-time',lambda m:m['predicates']['GrantCurrentAtDeclared'].append(['g0','t1']))
 add('nonconsequential-grant-binding-absent-allowed',lambda m:m['predicates'].update(authorizationGrantBindingDeclared=[x for x in m['predicates']['authorizationGrantBindingDeclared'] if x[0]!='a2']))
 add('unused-grant-handle-empty-allowed',lambda m:setfn(m,b.HANDLES['GrantReference'],'gOutside','empty'))
 for n,arg in [('PrincipalInScopeDeclared','p0'),('PrincipalGovernedDeclared','p0'),('PrincipalRecognizedIdentityDeclared','p0'),('PrincipalBoundedScopeDeclared','p0'),('PrincipalIdentityGovernedDeclared','pid0'),('BoundaryRecordedDeclared','b0'),('BoundaryAuthenticationDeclared','b0'),('UseInScopeDeclared','u0'),('UseRecordedDeclared','u0'),('UseExactResolutionDeclared','u0'),('RepresentationInScopeDeclared','r0'),('RepresentationRecordedDeclared','r0'),('SubjectGovernedDeclared','s0'),('AuthorizationInScopeDeclared','a0'),('AuthorizationRecordedDeclared','a0'),('AuthorizationExactCurrentGrantDeclared','a0'),('GrantRecordedDeclared','g0')]:add('missing-selected-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 add('neither-governed-identity-nor-record-criterion',lambda m:m['predicates']['PrincipalIdentityBackedDeclared'].remove(['p0']),T=False,I=None)
 add('Principal-issuer-boundary-mismatch',lambda m:change(m,'principalIssuer','p0','issuer1'),T=False,I=None)
 add('reference-use-identity-mismatch',lambda m:change(m,'useIdentity','u0','pid1'),T=False,I=None)
 add('reference-use-issuer-boundary-mismatch',lambda m:change(m,'useIssuerBoundary','u0','b1'),T=False,I=None)
 add('representation-changes-subject-identity',lambda m:change(m,'subjectIdentity','s4','sid1'),T=False,I=None)
 add('representation-changes-subject-lifecycle',lambda m:change(m,'subjectLifecycle','s4','life1'),T=False,I=None)
 add('consequential-grant-not-current-at-evaluation-time',lambda m:m['predicates']['GrantCurrentAtDeclared'].remove(['g0','t0']),T=False,I=None)
 add('consequential-grant-not-applicable-to-Principal',lambda m:m['predicates']['GrantAppliesToPrincipalDeclared'].remove(['g0','p0']),T=False,I=None)
 add('consequential-grant-not-applicable-to-scope',lambda m:m['predicates']['GrantAppliesToScopeDeclared'].remove(['g0','scope0']),T=False,I=None)
 add('consequential-authorization-wrong-scope',lambda m:change(m,'authorizationScope','a0','scope1'),T=False,I=None)
 add('consequential-authorization-wrong-time',lambda m:change(m,'authorizationTime','a0','t1'),T=False,I=None)
 targets={id(b.PRINCIPAL_FIELDS):'p0',id(b.BOUNDARY_FIELDS):'b0',id(b.USE_FIELDS):'u0',id(b.REPRESENTATION_FIELDS):'r0',id(b.SUBJECT_FIELDS):'s0',id(b.AUTHORIZATION_FIELDS):'a0',id(b.AUTHORIZATION_GRANT_FIELDS):'a0',id(b.GRANT_FIELDS):'g0'}
 for fields,carrier in b.GROUPS:
  arg=targets[id(fields)]
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   value=getfn(base_model(),n,arg);alt=next(x for x in base_model()['domains'][sort] if x!=value)
   add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   declared={'PrincipalReference':'PrincipalApplicable','PrincipalUseReference':'UseApplicable','RepresentationReference':'RepresentationApplicable','AuthorizationReference':'AuthorizationApplicable'}.get(sort,sort+'Declared')
   add('undeclared-selected-target-'+n,lambda m,declared=declared,value=value:m['predicates'][declared].remove([value]),T=False,I=None)
 selected={'PrincipalReference':'p0','PrincipalIdentityReference':'pid0','BoundaryReference':'b0','IssuerReference':'issuer0','ScopeReference':'identityScope','PrincipalUseReference':'u0','RepresentationReference':'r0','SubjectReference':'s0','SubjectIdentityReference':'sid0','LifecycleReference':'life0','SubjectKindReference':'personKind','AuthorizationReference':'a0','GrantReference':'g0','TimeReference':'t0'}
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=selected[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 add('malformed-empty-domain',lambda m:m['domains'].update(PrincipalReference=[]),error='empty-or-malformed-domain')
 add('malformed-missing-domain',lambda m:m['domains'].pop('BoundaryReference'),error='model-signature-denominator-mismatch')
 add('malformed-missing-function',lambda m:m['functions'].pop('principalIdentity'),error='model-signature-denominator-mismatch')
 add('malformed-partial-function',lambda m:m['functions']['principalIdentity'].pop(),error='nontotal-function')
 add('malformed-function-range',lambda m:setfn(m,'principalIdentity','p0','foreign'),error='ill-sorted-function-result')
 add('malformed-function-argument',lambda m:m['functions']['principalIdentity'][0].update(args=['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-range',lambda m:m['predicates']['PrincipalApplicable'].append(['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-arity',lambda m:m['predicates']['GrantCurrentAtDeclared'].append(['g0']),error='ill-sorted-model-tuple')
 return rows
def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}

def verify(write=False):
    context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT)
    runtime=v.f.current_bindings();bindings=[b.ref(p) for p in [b.UNIT/'build_candidate.py',b.UNIT/'verify_candidate.py',b.IMPL/'verifier.py',b.IMPL/'ir.py',b.IMPL/'contracts.py',b.BASE/'units/A04/correspondence.py']]
    core=load('t.json')['payload'];typed=load('static-ir.json');packet=load('correspondence.json');counts=load('denominator.json')
    if not b.r.same_json(typed,b.ir.compile_interpretation(core,snap)) or not b.r.same_json(packet['interpretation'],core):raise ValueError('Substituted interpretation/IR')
    account=b.co.check(packet,snap,required_dependencies=[x['version_ref'] for x in core['depends_on']],required_conflicts=[x['finding_id'] for x in packet['source_precedence']['conflicts']])
    if not account['character_accounting_complete'] or not b.r.same_json(account,load('correspondence-check.json')):raise ValueError('Incomplete source account')
    if core['assumptions'] or packet['assumption_links'] or core['source_fidelity']!='pending':raise ValueError('Assumed target or owner fidelity')
    T=[x for x in typed['clauses'] if x['disposition']=='encoded'];I=[x for x in typed['populations'] if x['requirement']=='required']
    if len(T)!=counts['encoded_clauses'] or len(I)!=counts['required_populations']:raise ValueError('Changed theory/population denominator')
    ids={x['symbol_id']:b.ir.qualified(core['source'],core['scope'],x['symbol_id']) for x in core['declarations']}
    def evaluate(model):
        e=v.Denotation(typed['declarations'],model)
        tc=[{'clause_id':x['clause_id'],'truth':e.truth(x['formal_statement'])} for x in T]
        pc=[{'population_id':x['population_id'],'truth':e.truth(x['statement'])} for x in I]
        return all(x['truth'] for x in tc),all(x['truth'] for x in pc),tc,pc
    results=[]
    for case in controls():
        model=qualify(case['model'],ids)
        try:
            t,i,tc,pc=evaluate(model)
            if case['expected_error'] is not None or t!=case['expected_T'] or (case['expected_I'] is not None and i!=case['expected_I']):raise ValueError('Wrong authored control: '+case['case_id']+' '+str((t,i)))
            result={'case_id':case['case_id'],'status':'independently-evaluated-authored-model','model':model,'model_sha256':b.ir.digest(model),
                    'primary_theory_satisfied':t,'required_population_satisfied':i,'primary_clause_results':tc,'population_results':pc}
        except v.VerificationFault as error:
            if error.code!=case['expected_error']:raise
            result={'case_id':case['case_id'],'status':'rejected-model-structure','code':error.code,'model':model,'model_sha256':b.ir.digest(model)}
        results.append(result)
    queries=[];composed=b.ir.compose([typed])
    for q in load('query-policy.json')['queries']:
        model=base_model()
        model=qualify(model,ids);e=v.Denotation(typed['declarations'],model)
        target=v.renamed(q['target'],ids);witness=v.renamed(q['witness_condition'],ids)
        b.ir.check_composed_formula(composed,target);b.ir.check_composed_formula(composed,witness)
        if q['selected_in_T'] is not False or evaluate(model)[:2]!=(True,True) or e.truth(target) is not False or e.truth(witness) is not True:raise ValueError('Target assumed or no valid countermodel: '+q['query_id'])
        queries.append({'query_id':q['query_id'],'target_false':True,'witness_condition_true':True,'model':model,'model_sha256':b.ir.digest(model),'mechanized_proof':False})
    prior=json.loads((b.BASE/'definitions/cal.definition.identity-lineage/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Principal-model-controls/v1-candidate','status':'PASS-for-exact-authored-Principal-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Necessary Principal recognition/reference,independent subject identity/lifecycle and consequential exact current scoped grant declarations checked on supplied models;actual recognition,issuer authenticity,Person identity,capability,Role,grant authority,permission,fidelity and whole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
