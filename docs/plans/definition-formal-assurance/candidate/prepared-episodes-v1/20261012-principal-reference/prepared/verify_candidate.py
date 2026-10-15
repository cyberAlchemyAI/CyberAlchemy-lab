"""Supplied Principal Reference minimal-data,resolution and current-evidence models;no real secrets."""
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
 ds={'ReferenceRecord':['r'+str(i) for i in range(6)]+['rOutside'],'PrincipalReference':['p0','p1','p2','pOutside'],'StableIdentifierReference':['id0','id1','id2','idUn2','idUn4','idUn5','idOutside'],'PrincipalKindReference':['humanKind','teamKind','serviceKind','agentKind','otherKind','kindOutside'],'IssuerReference':['issuer0','issuer1','issuerOutside'],'RegistryReference':['registry0','registry1','registryOutside'],'ResolutionRouteReference':['route0','route1','routeOutside'],'IntegrityReference':['integrity0','integrity1','integrityOutside'],'ScopeReference':['referenceScope','scope0','scope1','scopeOutside'],'ConsumerReference':['c'+str(i) for i in range(5)]+['cOutside'],'ReferenceUseReference':['u'+str(i) for i in range(5)]+['uOutside'],'DataFieldReference':['idField','kindField','issuerField','registryField','routeField','integrityField','secretField','credentialField','excessField','otherField','fieldOutside'],'AuthorityDecisionReference':['d'+str(i) for i in range(5)]+['dOutside'],'GrantEvidenceReference':['e0','e1','e2','eOutside'],'TimeReference':['t0','t1','tOutside'],'Token':['empty','reference','other']}
 def mapn(n,values):return lambda x:values.get(x,ds[b.FUNCTIONS[n][1]][-1])
 maps={'referenceStableIdentifier':mapn('referenceStableIdentifier',{'r0':'id0','r1':'id1','r2':'idUn2','r3':'id2','r4':'idUn4','r5':'idUn5'}),'referenceKind':mapn('referenceKind',{'r0':'humanKind','r1':'teamKind','r2':'serviceKind','r3':'serviceKind','r4':'agentKind','r5':'otherKind'}),'referenceRoute':mapn('referenceRoute',{'r'+str(i):'route0' if i<3 else 'route1' for i in range(6)}),'referenceIntegrity':mapn('referenceIntegrity',{'r'+str(i):'integrity0' if i<3 else 'integrity1' for i in range(6)}),'referenceScope':mapn('referenceScope',{'r'+str(i):'referenceScope' for i in range(6)}),'referenceIssuer':mapn('referenceIssuer',{'r0':'issuer0','r2':'issuer0','r3':'issuer1','r4':'issuer1'}),'referenceRegistry':mapn('referenceRegistry',{'r1':'registry0','r2':'registry0','r3':'registry1','r5':'registry1'}),'referencePrincipal':mapn('referencePrincipal',{'r0':'p0','r1':'p1','r3':'p2'}),'principalStableIdentifier':mapn('principalStableIdentifier',{'p0':'id0','p1':'id1','p2':'id2'}),'principalKind':mapn('principalKind',{'p0':'humanKind','p1':'teamKind','p2':'serviceKind'}),'useReference':mapn('useReference',{'u0':'r0','u1':'r1','u2':'r2','u3':'r0','u4':'r3'}),'useConsumer':mapn('useConsumer',{'u'+str(i):'c'+str(i) for i in range(5)}),'decisionReference':mapn('decisionReference',{'d0':'r0','d1':'r1','d2':'r2','d3':'r3','d4':'r5'}),'decisionGrantEvidence':mapn('decisionGrantEvidence',{'d0':'e0','d1':'e1','d2':'e0','d3':'e2','d4':'e1'}),'decisionScope':mapn('decisionScope',{'d0':'scope0','d1':'scope1','d2':'scope0','d3':'scope0','d4':'scope1'}),'decisionTime':mapn('decisionTime',{'d0':'t0','d1':'t1','d2':'t0','d3':'t1','d4':'t1'}),'evidencePrincipal':mapn('evidencePrincipal',{'e0':'p0','e1':'p1','e2':'p2'}),'evidenceScope':mapn('evidenceScope',{'e0':'scope0','e1':'scope1','e2':'scope0'})}
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['ReferenceRecord','ReferenceUseReference','AuthorityDecisionReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['ReferenceApplicable','ReferenceInScopeDeclared','ReferenceGovernedDeclared','ReferenceBoundedDeclared','ReferenceMinimalDeclared']:preds[n]=[['r'+str(i)] for i in range(6)]
 preds.update(ReferenceIdentityBackedDeclared=[['r0'],['r2'],['r3']],ReferenceRecordBackedDeclared=[['r1'],['r2'],['r4'],['r5']],ReferenceAccountabilityLinkageDeclared=[['r0'],['r2'],['r3'],['r4']],ReferenceAuthorizationLinkageDeclared=[['r1'],['r2'],['r3'],['r5']],ReferenceIssuerPresentDeclared=[['r0'],['r2'],['r3'],['r4']],ReferenceRegistryPresentDeclared=[['r1'],['r2'],['r3'],['r5']],ReferenceResolvedDeclared=[['r0'],['r1'],['r3']],ReferenceUnresolvedDeclared=[['r2'],['r4'],['r5']],ReferenceActualAuthority=[['r1']],PrincipalGovernedDeclared=[['p0'],['p1'],['p2']],PrincipalIdentityAuthorityDeclared=[['p0'],['p1'],['p2']],ConsumerRecordedDeclared=[['c'+str(i)] for i in range(5)],FieldAllowedMinimumDeclared=[[x] for x in ds['DataFieldReference'][:6]],FieldSecretDeclared=[['secretField']],FieldCredentialDeclared=[['credentialField']],FieldExcessIdentityDeclared=[['excessField']])
 field_values={'ID_FIELD':'idField','KIND_FIELD':'kindField','ISSUER_FIELD':'issuerField','REGISTRY_FIELD':'registryField','ROUTE_FIELD':'routeField','INTEGRITY_FIELD':'integrityField'}
 for n in ['UseApplicable','UseInScopeDeclared','UseRecordedDeclared']:preds[n]=[['u'+str(i)] for i in range(5)]
 for n in ['DecisionApplicable','DecisionInScopeDeclared','DecisionRecordedDeclared']:preds[n]=[['d'+str(i)] for i in range(5)]
 for n in ['EvidenceRecordedDeclared','EvidenceResolvedSeparatelyDeclared','EvidenceIndependentOfReferenceDeclared']:preds[n]=[['e0'],['e1'],['e2']]
 preds['EvidenceCurrentAtDeclared']=[['e0','t0'],['e1','t1'],['e2','t1']]
 for r in ds['ReferenceRecord'][:-1]:
  fields=['idField','kindField','routeField','integrityField']
  if [r] in preds['ReferenceIssuerPresentDeclared']:fields.append('issuerField')
  if [r] in preds['ReferenceRegistryPresentDeclared']:fields.append('registryField')
  preds['ReferenceEmbedsFieldDeclared'] += [[r,f] for f in fields]
 for i in range(5):
  ref=maps['useReference']('u'+str(i));preds['ConsumerNeedsFieldDeclared'] += [['c'+str(i),f] for rr,f in preds['ReferenceEmbedsFieldDeclared'] if rr==ref]
 m={'domains':ds,'constants':{'EMPTY':'empty',**field_values},'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(n,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':n,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('minimal-resolved-unresolved-reference-and-separate-current-evidence')
 add('no-selected-references-uses-decisions',lambda m:m['predicates'].update(ReferenceApplicable=[],ReferenceInScopeDeclared=[],UseApplicable=[],UseInScopeDeclared=[],DecisionApplicable=[],DecisionInScopeDeclared=[]),I=False)
 add('references-without-modeled-uses',lambda m:m['predicates'].update(UseApplicable=[],UseInScopeDeclared=[]),I=False)
 add('references-without-authority-decisions',lambda m:m['predicates'].update(DecisionApplicable=[],DecisionInScopeDeclared=[]),I=False)
 add('no-independent-authority',lambda m:m['predicates'].update(ReferenceActualAuthority=[]),I=False)
 for prefix,names,selected in [('Reference',b.ROOT_ACTUAL,['r'+str(i) for i in range(6)]),('Use',b.USE_ACTUAL,['u'+str(i) for i in range(5)]),('Decision',b.DECISION_ACTUAL,['d'+str(i) for i in range(5)])]:
  add('all-'+prefix+'-actual-outcomes-independently-supplied',lambda m,prefix=prefix,names=names,selected=selected:[m['predicates'].update({prefix+'Actual'+n:[[x] for x in selected]}) for n in names],I=False)
  for n in names:add('independently-supported-'+prefix+'-Actual'+n,lambda m,prefix=prefix,n=n,arg=selected[0]:m['predicates'][prefix+'Actual'+n].append([arg]))
 for names,arg,outside in [(b.ROOT_EXCLUDED,'r0','rOutside'),(b.USE_EXCLUDED,'u0','uOutside'),(b.DECISION_EXCLUDED,'d0','dOutside')]:
  for n in names:
   add('selected-excluded-'+n,lambda m,n=n,arg=arg:m['predicates'][n].append([arg]),T=False,I=None)
   add('outside-excluded-'+n,lambda m,n=n,outside=outside:m['predicates'][n].append([outside]))
 add('unresolved-reference-unused-Principal-handle-empty',lambda m:setfn(m,b.HANDLES['PrincipalReference'],'pOutside','empty'))
 add('unresolved-reference-Principal-binding-absent-allowed',lambda m:m['predicates'].update(referencePrincipalBindingDeclared=[x for x in m['predicates']['referencePrincipalBindingDeclared'] if x[0]!='r2']))
 add('registry-only-unused-issuer-binding-absent-allowed',lambda m:m['predicates'].update(referenceIssuerBindingDeclared=[x for x in m['predicates']['referenceIssuerBindingDeclared'] if x[0]!='r1']))
 add('issuer-only-unused-registry-binding-absent-allowed',lambda m:m['predicates'].update(referenceRegistryBindingDeclared=[x for x in m['predicates']['referenceRegistryBindingDeclared'] if x[0]!='r0']))
 add('unused-issuer-handle-empty-allowed',lambda m:setfn(m,b.HANDLES['IssuerReference'],'issuerOutside','empty'))
 add('unused-registry-handle-empty-allowed',lambda m:setfn(m,b.HANDLES['RegistryReference'],'registryOutside','empty'))
 add('evidence-current-at-additional-time',lambda m:m['predicates']['EvidenceCurrentAtDeclared'].append(['e0','t1']))
 add('reference-and-decision-scopes-distinct-allowed',lambda m:change(m,'referenceScope','r0','scope1'))
 add('inclusive-identity-and-record-with-populations-preserved',lambda m:(m['predicates']['ReferenceRecordBackedDeclared'].append(['r0']),m['predicates']['ReferenceRecordBackedDeclared'].remove(['r2'])))
 add('inclusive-accountability-and-authorization-with-populations-preserved',lambda m:(m['predicates']['ReferenceAuthorizationLinkageDeclared'].append(['r0']),m['predicates']['ReferenceAuthorizationLinkageDeclared'].remove(['r2'])))
 for n,arg in [('ReferenceInScopeDeclared','r0'),('ReferenceGovernedDeclared','r0'),('ReferenceBoundedDeclared','r0'),('ReferenceMinimalDeclared','r0'),('PrincipalGovernedDeclared','p0'),('PrincipalIdentityAuthorityDeclared','p0'),('UseInScopeDeclared','u0'),('UseRecordedDeclared','u0'),('ConsumerRecordedDeclared','c0'),('DecisionInScopeDeclared','d0'),('DecisionRecordedDeclared','d0'),('EvidenceRecordedDeclared','e0'),('EvidenceResolvedSeparatelyDeclared','e0'),('EvidenceIndependentOfReferenceDeclared','e0')]:add('missing-selected-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 add('neither-identity-nor-record-criterion',lambda m:m['predicates']['ReferenceIdentityBackedDeclared'].remove(['r0']),T=False,I=None)
 add('neither-accountability-nor-authorization-linkage',lambda m:m['predicates']['ReferenceAccountabilityLinkageDeclared'].remove(['r0']),T=False,I=None)
 add('neither-issuer-nor-registry',lambda m:m['predicates']['ReferenceIssuerPresentDeclared'].remove(['r0']),T=False,I=None)
 add('neither-resolved-nor-explicitly-unresolved',lambda m:m['predicates']['ReferenceResolvedDeclared'].remove(['r0']),T=False,I=None)
 add('both-resolved-and-unresolved',lambda m:m['predicates']['ReferenceUnresolvedDeclared'].append(['r0']),T=False,I=None)
 add('resolved-stable-identifier-mismatch',lambda m:change(m,'referenceStableIdentifier','r0','id1'),T=False,I=None)
 add('resolved-kind-mismatch',lambda m:change(m,'referenceKind','r0','teamKind'),T=False,I=None)
 add('missing-core-embedded-identifier-data',lambda m:m['predicates']['ReferenceEmbedsFieldDeclared'].remove(['r0','idField']),T=False,I=None)
 add('issuer-presence-without-embedded-issuer-field',lambda m:m['predicates']['ReferenceEmbedsFieldDeclared'].remove(['r0','issuerField']),T=False,I=None)
 for field in ['secretField','credentialField','excessField','otherField']:add('embedded-forbidden-or-unsupported-'+field,lambda m,field=field:m['predicates']['ReferenceEmbedsFieldDeclared'].append(['r0',field]),T=False,I=None)
 for n in ['FieldSecretDeclared','FieldCredentialDeclared','FieldExcessIdentityDeclared']:add('minimum-id-field-classified-'+n,lambda m,n=n:m['predicates'][n].append(['idField']),T=False,I=None)
 add('minimum-id-field-not-declared-allowed',lambda m:m['predicates']['FieldAllowedMinimumDeclared'].remove(['idField']),T=False,I=None)
 add('embedded-field-not-needed-by-consumer',lambda m:m['predicates']['ConsumerNeedsFieldDeclared'].remove(['c0','idField']),T=False,I=None)
 add('consumer-needs-unembedded-field',lambda m:m['predicates']['ConsumerNeedsFieldDeclared'].append(['c0','registryField']),T=False,I=None)
 add('decision-evidence-not-current-at-time',lambda m:m['predicates']['EvidenceCurrentAtDeclared'].remove(['e0','t0']),T=False,I=None)
 add('decision-evidence-wrong-scope',lambda m:change(m,'evidenceScope','e0','scope1'),T=False,I=None)
 add('decision-evidence-wrong-resolved-Principal',lambda m:change(m,'evidencePrincipal','e0','p1'),T=False,I=None)
 targets={id(b.REFERENCE_FIELDS):'r0',id(b.ISSUER_FIELDS):'r0',id(b.REGISTRY_FIELDS):'r1',id(b.RESOLUTION_FIELDS):'r0',id(b.PRINCIPAL_FIELDS):'p0',id(b.USE_FIELDS):'u0',id(b.DECISION_FIELDS):'d0',id(b.EVIDENCE_FIELDS):'e0'}
 for fields,carrier in b.GROUPS:
  arg=targets[id(fields)]
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   value=getfn(base_model(),n,arg);alt=next(x for x in base_model()['domains'][sort] if x!=value)
   add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   declared={'ReferenceRecord':'ReferenceApplicable','ReferenceUseReference':'UseApplicable','AuthorityDecisionReference':'DecisionApplicable'}.get(sort,sort+'Declared')
   add('undeclared-selected-target-'+n,lambda m,declared=declared,value=value:m['predicates'][declared].remove([value]),T=False,I=None)
 selected={'ReferenceRecord':'r0','PrincipalReference':'p0','StableIdentifierReference':'id0','PrincipalKindReference':'humanKind','IssuerReference':'issuer0','RegistryReference':'registry0','ResolutionRouteReference':'route0','IntegrityReference':'integrity0','ScopeReference':'referenceScope','ConsumerReference':'c0','ReferenceUseReference':'u0','DataFieldReference':'idField','AuthorityDecisionReference':'d0','GrantEvidenceReference':'e0','TimeReference':'t0'}
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=selected[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 add('malformed-empty-domain',lambda m:m['domains'].update(ReferenceRecord=[]),error='empty-or-malformed-domain')
 add('malformed-missing-domain',lambda m:m['domains'].pop('PrincipalReference'),error='model-signature-denominator-mismatch')
 add('malformed-missing-function',lambda m:m['functions'].pop('referenceStableIdentifier'),error='model-signature-denominator-mismatch')
 add('malformed-partial-function',lambda m:m['functions']['referenceStableIdentifier'].pop(),error='nontotal-function')
 add('malformed-function-range',lambda m:setfn(m,'referenceStableIdentifier','r0','foreign'),error='ill-sorted-function-result')
 add('malformed-function-argument',lambda m:m['functions']['referenceStableIdentifier'][0].update(args=['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-range',lambda m:m['predicates']['ReferenceApplicable'].append(['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-arity',lambda m:m['predicates']['EvidenceCurrentAtDeclared'].append(['e0']),error='ill-sorted-model-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.principal/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-PrincipalReference-model-controls/v1-candidate','status':'PASS-for-exact-authored-PrincipalReference-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Necessary minimal reference/metadata,resolved-or-explicitly-unresolved,consumer-needed data and separate independent current-grant-evidence declarations checked on supplied models;real resolution,identity authority,data absence,grant validity,permission,fidelity and whole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
