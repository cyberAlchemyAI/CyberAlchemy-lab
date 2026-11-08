"""Supplied Registry entry,binding,overlay and discriminator models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
NAMES=['Zero','Current','Historical','Both','Conflict','Candidate','HistDisc','Move','Authority','Outside']
def getfn(m,n,*args):return next(x['value'] for x in m['functions'][n] if x['args']==list(args))
def recompute(m):
 p=m['predicates'];cs=m['constants'];get=lambda n,*args:getfn(m,n,*args);ops=[x[0] for x in p['ResolutionApplicable']];types=m['domains']['ArtifactTypeReference'];p['ExplicitMatchDeclared']=[];p['DiscriminatorMatchDeclared']=[];p['MatchDeclared']=[];p['ResultMatchDeclared']=[];p['ResolvedTypeStateDeclared']=[]
 for o in ops:
  r=get('operationRegistry',o);a=get('operationCarrier',o);z=get('operationResult',o);matches=[]
  for t in types:
   registered=[r,t] in p['RegistryTypeRegisteredDeclared'];s=get('registryTypeState',r,t);explicit=registered and s in [cs['CURRENT'],cs['HISTORICAL']] and [a,t] in p['CarrierExplicitTypeReferenceDeclared'];disc=registered and s==cs['CURRENT'] and any(x[0]==r and x[1]==t and [a,x[2],x[3]] in p['CarrierDiscriminatorFieldDeclared'] for x in p['RegistryDiscriminatorDeclared'])
   if explicit:p['ExplicitMatchDeclared'].append([o,t])
   if disc:p['DiscriminatorMatchDeclared'].append([o,t])
   if explicit or disc:matches.append(t);p['MatchDeclared'].append([o,t]);p['ResultMatchDeclared'].append([z,t])
  kind=cs['UNRESOLVED'] if not matches else cs['RESOLVED'] if len(matches)==1 else cs['AMBIGUOUS'];setfn(m,'resultKind',z,kind)
  if len(matches)==1:
   t=matches[0];s=get('registryTypeState',r,t);setfn(m,'resultSelectedType',z,t);setfn(m,'resultSelectedState',z,s);p['ResolvedTypeStateDeclared'].append([z,t,s])
 p['SameCanonicalInputDeclared']=[[o,other] for o in ops for other in ops if get('operationCarrier',o)==get('operationCarrier',other) and get('operationRegistry',o)==get('operationRegistry',other)]
def base_model():
 ds={'OperationReference':['op'+n for n in NAMES],'CarrierReference':['carrier'+n for n in NAMES if n!='Move'],'RegistryReference':['registryMain','registryOutside'],'ArtifactTypeReference':['typeCurrent','typeSecond','typeHistorical','typeCandidate','typeOutside'],'LifecycleState':['state'+n for n in b.STATE_NAMES]+['stateFuture','stateOutside'],'ResultReference':['result'+n for n in NAMES],'ResultKind':['kind'+n for n in b.KIND_NAMES]+['kindOutside'],'DiscriminatorPath':['pathSchema','pathOther','pathOutside'],'DiscriminatorValue':['valueCurrent','valueSecond','valueHistorical','valueCandidate','valueUnknown','valueOutside'],'PathMetadata':['pathOriginal','pathMoved','pathOutside'],'Token':['empty','none','reference','differentReference']}
 cs={'EMPTY':'empty','NONE':'none',**{n:'state'+n for n in b.STATE_NAMES},**{n:'kind'+n for n in b.KIND_NAMES}}
 def suffix(x,prefix):return x[len(prefix):]
 maps={'operationCarrier':lambda o:'carrierCurrent' if o=='opMove' else 'carrier'+suffix(o,'op'),'operationRegistry':lambda o:'registryOutside' if o=='opOutside' else 'registryMain','operationResult':lambda o:'result'+suffix(o,'op'),'operationPath':lambda o:'pathMoved' if o=='opMove' else 'pathOutside' if o=='opOutside' else 'pathOriginal','registryTypeState':lambda r,t:'stateFuture' if r=='registryOutside' or t=='typeOutside' else 'stateHISTORICAL' if t=='typeHistorical' else 'stateCANDIDATE' if t=='typeCandidate' else 'stateCURRENT','registryTypePath':lambda r,t:'pathOutside' if r=='registryOutside' or t=='typeOutside' else 'pathSchema','registryTypeValue':lambda r,t:'valueOutside' if r=='registryOutside' or t=='typeOutside' else 'value'+suffix(t,'type'),'resultRegistry':lambda z:'registryOutside' if z=='resultOutside' else 'registryMain','resultKind':lambda z:'kindUNRESOLVED','resultSelectedType':lambda z:'typeOutside','resultSelectedState':lambda z:'stateFuture','resultAuthorityEffect':lambda z:'none'}
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};p={n:[] for n in b.SIGNATURE};ops=ds['OperationReference'][:-1]
 for s in b.SORTS:
  if s not in ['OperationReference','Token']:p[s+'Declared']=[[x] for x in ds[s] if not x.endswith('Outside')]
 for n in ['ResolutionApplicable','OperationInScopeDeclared','DeterministicOperationDeclared']:p[n]=[[o] for o in ops]
 for n,s in b.FACETS.items():p[n+'BindingDeclared']=[[o,maps[n](o)] for o in ops]
 p['CanonicalMachineCarrierDeclared']=[[x] for x in ds['CarrierReference'][:-1]];registered=[['registryMain',t] for t in ds['ArtifactTypeReference'][:-1]];p['RegistryTypeRegisteredDeclared']=registered;p['RegistryTypeStateBindingDeclared']=[[r,t,maps['registryTypeState'](r,t)] for r,t in registered];p['RegistryDiscriminatorDeclared']=[[r,t,maps['registryTypePath'](r,t),maps['registryTypeValue'](r,t)] for r,t in registered]
 p['CarrierExplicitTypeReferenceDeclared']=[['carrierHistorical','typeHistorical'],['carrierBoth','typeCurrent'],['carrierConflict','typeHistorical'],['carrierCandidate','typeCandidate']]
 p['CarrierDiscriminatorFieldDeclared']=[['carrier'+n,'pathSchema','valueCurrent'] for n in ['Current','Both','Conflict']]+[['carrierAuthority','pathSchema','valueSecond'],['carrierHistDisc','pathSchema','valueHistorical']]+[['carrier'+n,'pathSchema','valueUnknown'] for n in ['Zero','Historical','Candidate']]
 p['ResolutionActualAuthority']=[['opAuthority']];m={'domains':ds,'constants':cs,'functions':functions,'predicates':p};recompute(m);return m

def controls():
 rows=[]
 def add(id,mutation,T=True,I=None,error=None):
  m=base_model();mutation(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('exact-union-three-results-historical-state-and-moved-input',lambda m:None,I=True)
 for n in b.ACTUAL:
  if n!='Authority':add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['ResolutionActual'+n].append(['opAuthority']),I=True)
 add('selected-empty-operation-handle',lambda m:setfn(m,b.HANDLES['OperationReference'],'opZero','empty'),T=False)
 add('outside-empty-operation-handle',lambda m:setfn(m,b.HANDLES['OperationReference'],'opOutside','empty'),I=True)
 add('scope-applicability-disagreement',lambda m:m['predicates']['OperationInScopeDeclared'].remove(['opZero']),T=False)
 add('deterministic-operation-marker-missing',lambda m:m['predicates']['DeterministicOperationDeclared'].remove(['opZero']),T=False)
 add('canonical-machine-carrier-marker-missing',lambda m:m['predicates']['CanonicalMachineCarrierDeclared'].remove(['carrierCurrent']),T=False)
 for n,s in b.FACETS.items():
  value=getfn(base_model(),n,'opZero');alternate=next(x for x in base_model()['domains'][s] if x!=value)
  add('missing-facet-declaration-'+n,lambda m,s=s,value=value:m['predicates'][s+'Declared'].remove([value]),T=False)
  add('empty-facet-handle-'+n,lambda m,s=s,value=value:setfn(m,b.HANDLES[s],value,'empty'),T=False)
  add('missing-exact-binding-'+n,lambda m,n=n,value=value:m['predicates'][n+'BindingDeclared'].remove(['opZero',value]),T=False)
  add('conflicting-extra-binding-'+n,lambda m,n=n,alternate=alternate:m['predicates'][n+'BindingDeclared'].append(['opZero',alternate]),T=False)
 for s,value in [('ArtifactTypeReference','typeCurrent'),('LifecycleState','stateCURRENT'),('DiscriminatorPath','pathSchema'),('DiscriminatorValue','valueCurrent')]:
  add('registered-facet-not-declared-'+s,lambda m,s=s,value=value:m['predicates'][s+'Declared'].remove([value]),T=False)
  add('registered-facet-empty-handle-'+s,lambda m,s=s,value=value:setfn(m,b.HANDLES[s],value,'empty'),T=False)
 add('missing-registered-state-binding',lambda m:m['predicates']['RegistryTypeStateBindingDeclared'].remove(['registryMain','typeCurrent','stateCURRENT']),T=False)
 add('conflicting-registered-state-binding',lambda m:m['predicates']['RegistryTypeStateBindingDeclared'].append(['registryMain','typeCurrent','stateHISTORICAL']),T=False)
 add('missing-registered-discriminator-binding',lambda m:m['predicates']['RegistryDiscriminatorDeclared'].remove(['registryMain','typeCurrent','pathSchema','valueCurrent']),T=False)
 add('conflicting-registered-discriminator-binding',lambda m:m['predicates']['RegistryDiscriminatorDeclared'].append(['registryMain','typeCurrent','pathSchema','valueSecond']),T=False)
 for n,tuple in [('ExplicitMatchDeclared',['opHistorical','typeHistorical']),('DiscriminatorMatchDeclared',['opCurrent','typeCurrent']),('MatchDeclared',['opCurrent','typeCurrent']),('ResultMatchDeclared',['resultCurrent','typeCurrent'])]:
  add('missing-eligible-'+n,lambda m,n=n,tuple=tuple:m['predicates'][n].remove(tuple),T=False)
 for n,tuple in [('ExplicitMatchDeclared',['opZero','typeCurrent']),('DiscriminatorMatchDeclared',['opHistDisc','typeHistorical']),('MatchDeclared',['opZero','typeOutside']),('ResultMatchDeclared',['resultZero','typeCurrent'])]:add('unwitnessed-extra-'+n,lambda m,n=n,tuple=tuple:m['predicates'][n].append(tuple),T=False)
 add('candidate-explicit-added-to-admitted-match',lambda m:m['predicates']['ExplicitMatchDeclared'].append(['opCandidate','typeCandidate']),T=False)
 add('historical-discriminator-added-to-current-match',lambda m:m['predicates']['DiscriminatorMatchDeclared'].append(['opHistDisc','typeHistorical']),T=False)
 add('candidate-reference-declares-resolver-admission',lambda m:m['predicates']['ResolverAdmitsTypeDeclared'].append(['opCandidate','typeCandidate']),T=False)
 for result,kind in [('resultZero','kindRESOLVED'),('resultCurrent','kindUNRESOLVED'),('resultConflict','kindRESOLVED'),('resultBoth','kindAMBIGUOUS'),('resultConflict','kindUNRESOLVED')]:add('wrong-cardinality-'+result+'-'+kind,lambda m,result=result,kind=kind:setfn(m,'resultKind',result,kind),T=False)
 for n in b.KIND_NAMES[1:]:add('result-kind-constants-collapse-'+n,lambda m,n=n:m['constants'].update({n:'kindRESOLVED'}),T=False)
 for n in b.STATE_NAMES[1:]:add('lifecycle-constants-collapse-'+n,lambda m,n=n:m['constants'].update({n:'stateCURRENT'}),T=False)
 add('none-and-empty-collapse',lambda m:m['constants'].update(NONE='empty'),T=False)
 add('unsupported-selected-result-kind',lambda m:setfn(m,'resultKind','resultZero','kindOutside'),T=False)
 add('result-kind-not-declared',lambda m:m['predicates']['ResultKindDeclared'].remove(['kindRESOLVED']),T=False)
 add('result-registry-identity-mismatch',lambda m:setfn(m,'resultRegistry','resultCurrent','registryOutside'),T=False)
 add('resolved-selected-type-not-a-match',lambda m:setfn(m,'resultSelectedType','resultCurrent','typeSecond'),T=False)
 add('historical-resolved-state-misreported-current',lambda m:setfn(m,'resultSelectedState','resultHistorical','stateCURRENT'),T=False)
 add('missing-exact-resolved-type-state',lambda m:m['predicates']['ResolvedTypeStateDeclared'].remove(['resultHistorical','typeHistorical','stateHISTORICAL']),T=False)
 add('conflicting-extra-resolved-type-state',lambda m:m['predicates']['ResolvedTypeStateDeclared'].append(['resultHistorical','typeHistorical','stateCURRENT']),T=False)
 add('unresolved-fabricates-resolved-type-state',lambda m:m['predicates']['ResolvedTypeStateDeclared'].append(['resultZero','typeCurrent','stateCURRENT']),T=False)
 add('ambiguous-fabricates-resolved-type-state',lambda m:m['predicates']['ResolvedTypeStateDeclared'].append(['resultConflict','typeCurrent','stateCURRENT']),T=False)
 add('resolution-authority-effect-present',lambda m:setfn(m,'resultAuthorityEffect','resultCurrent','reference'),T=False)
 for n in ['PathEvidenceDeclared','FilenameEvidenceDeclared','ExtensionEvidenceDeclared','NearestNameEvidenceDeclared']:add('prohibited-'+n,lambda m,n=n:m['predicates'][n].append(['opCurrent']),T=False)
 for n in ['ResultValidationEffectDeclared','ResultConformanceEffectDeclared','ResultAdmissionEffectDeclared']:add('prohibited-'+n,lambda m,n=n:m['predicates'][n].append(['resultCurrent']),T=False)
 add('same-input-relation-omits-moved-carrier',lambda m:m['predicates']['SameCanonicalInputDeclared'].remove(['opCurrent','opMove']),T=False)
 add('same-input-relation-merges-different-carriers',lambda m:m['predicates']['SameCanonicalInputDeclared'].append(['opCurrent','opHistorical']),T=False)
 add('path-only-moved-operation-reports-other-kind',lambda m:setfn(m,'resultKind','resultMove','kindUNRESOLVED'),T=False)
 add('outside-prohibited-path-evidence-permitted',lambda m:m['predicates']['PathEvidenceDeclared'].append(['opOutside']),I=True)
 add('outside-result-extra-match-permitted',lambda m:m['predicates']['ResultMatchDeclared'].append(['resultOutside','typeCandidate']),I=True)
 add('unresolved-nominated-type-ignored',lambda m:setfn(m,'resultSelectedType','resultZero','typeCurrent'),I=True)
 add('ambiguous-nominated-state-ignored',lambda m:setfn(m,'resultSelectedState','resultConflict','stateHISTORICAL'),I=True)
 add('outside-carrier-extra-discriminator-permitted',lambda m:m['predicates']['CarrierDiscriminatorFieldDeclared'].append(['carrierOutside','pathOther','valueSecond']),I=True)
 add('missing-independent-authority-is-population-loss',lambda m:m['predicates']['ResolutionActualAuthority'].clear(),I=False)
 add('moved-path-witness-loss',lambda m:setfn(m,'operationPath','opMove','pathOriginal'),T=False)
 def coherent_path_change(m):
  setfn(m,'operationPath','opMove','pathOriginal');next(x for x in m['predicates']['operationPathBindingDeclared'] if x[0]=='opMove')[1]='pathOriginal'
 add('coherent-metadata-change-loses-only-movement-population',coherent_path_change,I=False)
 def unknown_state(m):
  setfn(m,'registryTypeState',['registryMain','typeCandidate'],'stateFuture');next(x for x in m['predicates']['RegistryTypeStateBindingDeclared'] if x[1]=='typeCandidate')[2]='stateFuture';recompute(m)
 add('unknown-nonadmitted-state-not-global-vocabulary-error',unknown_state,I=False)
 def historical_shared_discriminator(m):
  setfn(m,'registryTypeValue',['registryMain','typeHistorical'],'valueCurrent');next(x for x in m['predicates']['RegistryDiscriminatorDeclared'] if x[1]=='typeHistorical')[3]='valueCurrent';m['predicates']['CarrierDiscriminatorFieldDeclared'].append(['carrierHistDisc','pathSchema','valueCurrent']);recompute(m)
 add('historical-and-current-share-discriminator-no-global-uniqueness',historical_shared_discriminator,I=False)
 def conflicting_current(m):
  setfn(m,'registryTypeValue',['registryMain','typeSecond'],'valueCurrent');next(x for x in m['predicates']['RegistryDiscriminatorDeclared'] if x[1]=='typeSecond')[3]='valueCurrent';recompute(m)
 add('two-current-types-one-registered-discriminator',conflicting_current,T=False)
 def explicit_second(m):m['predicates']['CarrierExplicitTypeReferenceDeclared'].append(['carrierZero','typeSecond']);recompute(m)
 add('coherent-new-explicit-reference-changes-result',explicit_second,I=True)
 def nonregistered_explicit(m):m['predicates']['CarrierExplicitTypeReferenceDeclared'].append(['carrierZero','typeOutside']);recompute(m)
 add('unregistered-explicit-reference-remains-unresolved',nonregistered_explicit,I=True)
 add('operation-selector-result-is-type',lambda m:setfn(m,'operationCarrier','opZero','typeCurrent'),error='ill-sorted-function-result')
 add('missing-signature-symbol',lambda m:m['predicates'].pop('MatchDeclared'),error='model-signature-denominator-mismatch')
 add('nontotal-registry-state-function',lambda m:m['functions']['registryTypeState'].pop(),error='nontotal-function')
 add('ill-sorted-current-constant',lambda m:m['constants'].update(CURRENT='kindRESOLVED'),error='ill-sorted-constant')
 add('wrong-discriminator-binding-arity',lambda m:m['predicates'].update(RegistryDiscriminatorDeclared=[['registryMain','typeCurrent','pathSchema']]),error='ill-sorted-model-tuple')
 add('duplicate-match-tuple',lambda m:m['predicates']['MatchDeclared'].append(['opCurrent','typeCurrent']),error='duplicate-predicate-tuple')
 add('empty-result-kind-domain',lambda m:m['domains'].update(ResultKind=[]),error='empty-or-malformed-domain')
 add('duplicate-registry-function-tuple',lambda m:m['functions']['registryTypeState'].append(copy.deepcopy(m['functions']['registryTypeState'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.artifact-type-request/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ArtifactTypeResolution-model-controls/v1-candidate','status':'PASS-for-exact-authored-ArtifactTypeResolution-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed exact explicit-admitted/current-discriminator union,distinct cardinalities,recorded states,no effect and metadata movement checked on supplied models. Actual execution,registry fidelity,validation,admission,owner activation,consumer alignment and whole fidelity remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
