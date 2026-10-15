import copy,json
import build_candidate as b
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def getfn(m,name,arg):return next(row['value'] for row in m['functions'][name] if row['args']==[arg])
def setfn(m,name,arg,value):next(row for row in m['functions'][name] if row['args']==[arg])['value']=value
def refresh(m):
 for fields,carrier in b.GROUPS:
  for name in fields:m['predicates'][name+'BindingDeclared']=[[row['args'][0],row['value']] for row in m['functions'][name]]
 selected=[row[0] for row in m['predicates']['ImplementationApplicable']]
 for kind,field in [('Interface','Interfaces'),('Evidence','Evidence')]:m['predicates']['Implementation'+kind+'LinkDeclared']=[[x,item] for x in selected for col,item in m['predicates'][kind+'CollectionContainsDeclared'] if col==getfn(m,'implementation'+field,x)]
def base_model():
 domains={sort:[sort+'0',sort+'1',sort+'Outside'] for sort in b.SORTS}
 domains.update(ImplementationReference=['impl0','impl1','impl2','impl3','implOutside'],IdentityReference=['id0','id2','id3','idOutside'],RevisionReference=['rev0','rev1','rev2','rev3','revOutside'],PostureReference=['build','deployment','both','postureOutside'],InterfaceCollectionReference=['ifEmpty','ifSingle','ifMulti','ifOutside'],InterfaceReference=['if0','if1','ifOutside'],EvidenceCollectionReference=['evEmpty','evShared','evAlternative','evOutside'],EvidenceReference=['ev0','ev1','evOutside'],ScopeReference=['scope0','scope1','narrow0','scopeOutside'],UseReference=['use0','use1','use2','useOutside'],DefinitionVersionReference=['dvSelected','dvHypothetical','dvOutside'],Token=['empty','token'])
 m={'domains':domains,'constants':{'EMPTY':'empty','SELECTED_DEFINITION':'dvSelected'},'functions':{},'predicates':{name:[] for name in b.SIGNATURE}}
 for name,(args,result) in b.FUNCTIONS.items():m['functions'][name]=[{'args':[arg],'value':'token' if name in b.HANDLES.values() else domains[result][0]} for arg in domains[args[0]]]
 for sort in b.SORTS:
  if sort!='Token':m['predicates'][sort+'Declared']=[[value] for value in domains[sort]]
 selected=domains['ImplementationReference'][:-1]
 for name in ['ImplementationApplicable','ImplementationInScopeDeclared','ImplementationTechnicalRealizationDeclared','ImplementationStableIdentityDeclared','ImplementationBoundedScopeDeclared',*['Implementation'+facet+'SeparatelyGovernedDeclared' for facet in b.FACETS],*['Implementation'+facet+'NeedsSeparateContractDeclared' for facet in b.CONTRACTS]]:m['predicates'][name]=[[value] for value in selected]
 m['predicates']['ImplementationGovernedIdentityDeclared']=[['impl0'],['impl2'],['impl3']];m['predicates']['ImplementationGovernedRecordDeclared']=[['impl1'],['impl2']]
 for i in range(4):setfn(m,'implementationVersion','impl'+str(i),'rev'+str(i))
 for impl,identity in [('impl2','id2'),('impl3','id3'),('implOutside','idOutside')]:setfn(m,'implementationIdentity',impl,identity)
 setfn(m,'implementationBuildOrDeploymentPosture','impl0','build');setfn(m,'implementationBuildOrDeploymentPosture','impl1','deployment');setfn(m,'implementationBuildOrDeploymentPosture','impl2','both');setfn(m,'implementationBuildOrDeploymentPosture','impl3','build')
 m['predicates']['PostureBuildDeclared']=[['build'],['both']];m['predicates']['PostureDeploymentDeclared']=[['deployment'],['both']]
 m['predicates']['InterfaceCollectionContainsDeclared']=[['ifSingle','if0'],['ifMulti','if0'],['ifMulti','if1']];m['predicates']['EvidenceCollectionContainsDeclared']=[['evShared','ev0'],['evAlternative','ev1']]
 for impl,col in [('impl1','ifMulti'),('impl2','ifSingle'),('impl3','ifSingle')]:setfn(m,'implementationInterfaces',impl,col)
 for impl in ['impl1','impl2']:setfn(m,'implementationEvidence',impl,'evShared')
 setfn(m,'implementationScope','impl1','scope1')
 m['predicates']['ImplementationActualAuthorityEffect']=[['impl3']];m['predicates']['ImplementationActualBuildCorrectness']=[['impl3']]
 for name in ['UseApplicable','UseInScopeDeclared','UseWithinApplicabilityDeclared','UseRespectsExclusionsDeclared']:m['predicates'][name]=[['use0'],['use1'],['use2']]
 for use,impl in [('use0','impl0'),('use1','impl1'),('use2','impl2')]:setfn(m,'useImplementation',use,impl);setfn(m,'useDefinitionVersion',use,'dvSelected')
 setfn(m,'useScope','use0','narrow0');setfn(m,'useScope','use1','scope1');setfn(m,'useScope','use2','scope0')
 m['predicates']['UseScopeWithinImplementationDeclared']=[['narrow0','scope0'],['scope1','scope1'],['scope0','scope0']];m['predicates']['DefinitionVersionAdmissionDeclared']=[['dvSelected']];m['predicates']['UseActualAuthorityEffect']=[['use2']]
 refresh(m);return m
def controls():
 baseline=base_model();rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  model=copy.deepcopy(baseline);mutation(model);rows.append({'case_id':name,'model':model,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,name,arg,value):setfn(m,name,arg,value);refresh(m)
 add('governed-technical-realizations-nine-coordinates-inclusive-postures-scoped-uses')
 def no_selected(m):
  for name in ['ImplementationApplicable','ImplementationInScopeDeclared','UseApplicable','UseInScopeDeclared']:m['predicates'][name]=[]
  refresh(m)
 add('no-selected-realizations-or-uses',no_selected,I=False)
 def no_uses(m):m['predicates']['UseApplicable']=[];m['predicates']['UseInScopeDeclared']=[]
 add('no-selected-uses',no_uses,I=False)
 for prefix,outcomes,subject in [('Implementation',b.ACTUAL,'impl0'),('Use',b.USE_ACTUAL,'use0')]:
  for outcome in outcomes:add('independently-supported-'+prefix+outcome,lambda m,prefix=prefix,outcome=outcome,subject=subject:m['predicates'][prefix+'Actual'+outcome].append([subject]))
 for name in b.EXCLUDED:
  add('selected-excluded-'+name,lambda m,name=name:m['predicates'][name].append(['impl0']),T=False,I=None);add('outside-excluded-'+name,lambda m,name=name:m['predicates'][name].append(['implOutside']))
 for prefix,subject,outside in [('Implementation','impl0','implOutside'),('Use','use0','useOutside')]:
  for outcome in b.INFERRED:
   name=prefix+'TermInfers'+outcome+'Declared';add('selected-term-inference-'+name,lambda m,name=name,subject=subject:m['predicates'][name].append([subject]),T=False,I=None);add('outside-term-inference-'+name,lambda m,name=name,outside=outside:m['predicates'][name].append([outside]))
 for name in ['ImplementationTechnicalRealizationDeclared','ImplementationStableIdentityDeclared','ImplementationBoundedScopeDeclared','ImplementationInScopeDeclared',*['Implementation'+facet+'SeparatelyGovernedDeclared' for facet in b.FACETS],*['Implementation'+facet+'NeedsSeparateContractDeclared' for facet in b.CONTRACTS]]:add('missing-'+name,lambda m,name=name:m['predicates'][name].remove(['impl0']),T=False,I=None)
 add('neither-governed-identity-nor-record',lambda m:m['predicates']['ImplementationGovernedIdentityDeclared'].remove(['impl0']),T=False,I=None)
 add('both-governed-modes-reduced-to-record',lambda m:m['predicates']['ImplementationGovernedIdentityDeclared'].remove(['impl2']),I=False)
 add('posture-neither-build-nor-deployment',lambda m:m['predicates']['PostureBuildDeclared'].remove(['build']),T=False,I=None)
 add('both-postures-reduced-to-deployment',lambda m:m['predicates']['PostureBuildDeclared'].remove(['both']),I=False)
 for kind,impl,item in [('Interface','impl1','if0'),('Evidence','impl1','ev0')]:
  add('missing-explicit-'+kind+'-link',lambda m,kind=kind,impl=impl,item=item:m['predicates']['Implementation'+kind+'LinkDeclared'].remove([impl,item]),T=False,I=None)
  other='ifOutside' if kind=='Interface' else 'evOutside';add('extra-'+kind+'-link-outside-collection',lambda m,kind=kind,impl=impl,other=other:m['predicates']['Implementation'+kind+'LinkDeclared'].append([impl,other]),T=False,I=None)
  sort=kind+'Reference';add('undeclared-selected-'+kind+'-member',lambda m,sort=sort,item=item:m['predicates'][sort+'Declared'].remove([item]),T=False,I=None);add('empty-selected-'+kind+'-member-handle',lambda m,sort=sort,item=item:setfn(m,b.HANDLES[sort],item,'empty'),T=False,I=None)
 def all_interfaces_single(m):m['predicates']['InterfaceCollectionContainsDeclared'].remove(['ifMulti','if1']);refresh(m)
 add('all-interface-nominations-singleton-or-empty',all_interfaces_single,I=False)
 add('shared-evidence-separated',lambda m:change(m,'implementationEvidence','impl2','evAlternative'),I=False)
 add('same-version-nomination-for-shared-identity',lambda m:change(m,'implementationVersion','impl1','rev0'),I=False)
 add('use-scope-not-within-implementation',lambda m:m['predicates']['UseScopeWithinImplementationDeclared'].remove(['narrow0','scope0']),T=False,I=None)
 for name in ['UseWithinApplicabilityDeclared','UseRespectsExclusionsDeclared','UseInScopeDeclared']:add('missing-'+name,lambda m,name=name:m['predicates'][name].remove(['use0']),T=False,I=None)
 add('all-use-scopes-equal-realization-scopes',lambda m:change(m,'useScope','use0','scope0'),I=False)
 add('use-targets-unselected-realization',lambda m:change(m,'useImplementation','use0','implOutside'),T=False,I=None)
 add('unknown-definition-use-without-successor-or-admission',lambda m:change(m,'useDefinitionVersion','use1','dvHypothetical'),T=False,I=None)
 def successor_hypothesis(m,relation=True,admission=True):
  change(m,'useDefinitionVersion','use1','dvHypothetical')
  if relation:m['predicates']['DefinitionVersionAdmittedSuccessorDeclared'].append(['dvSelected','dvHypothetical'])
  if admission:m['predicates']['DefinitionVersionAdmissionDeclared'].append(['dvHypothetical'])
 add('hypothetical-admitted-successor-use-not-actual-admission',successor_hypothesis)
 add('hypothetical-successor-without-admission',lambda m:successor_hypothesis(m,admission=False),T=False,I=None)
 add('hypothetical-admission-without-successor',lambda m:successor_hypothesis(m,relation=False),T=False,I=None)
 add('selected-Definition-admission-declaration-missing',lambda m:m['predicates']['DefinitionVersionAdmissionDeclared'].remove(['dvSelected']),T=False,I=None)
 add('selected-Definition-reference-undeclared',lambda m:m['predicates']['DefinitionVersionReferenceDeclared'].remove(['dvSelected']),T=False,I=None)
 add('empty-selected-Definition-handle',lambda m:setfn(m,b.HANDLES['DefinitionVersionReference'],'dvSelected','empty'),T=False,I=None)
 add('unused-revision-handle-empty',lambda m:setfn(m,b.HANDLES['RevisionReference'],'revOutside','empty'))
 add('unused-posture-handle-empty',lambda m:setfn(m,b.HANDLES['PostureReference'],'postureOutside','empty'))
 for fields,arg in [(b.FIELDS,'impl0'),(b.USE_FIELDS,'use0')]:
  for name,sort in fields.items():
   value=getfn(baseline,name,arg);other=next(x for x in baseline['domains'][sort] if x!=value)
   add('missing-exact-binding-'+name,lambda m,name=name,arg=arg:m['predicates'].update({name+'BindingDeclared':[x for x in m['predicates'][name+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   add('conflicting-exact-binding-'+name,lambda m,name=name,arg=arg,other=other:m['predicates'][name+'BindingDeclared'].append([arg,other]),T=False,I=None)
   if sort not in b.MAP:add('undeclared-selected-target-'+name,lambda m,sort=sort,value=value:m['predicates'][sort+'Declared'].remove([value]),T=False,I=None)
   add('empty-selected-handle-'+name,lambda m,sort=sort,value=value:setfn(m,b.HANDLES[sort],value,'empty'),T=False,I=None)
 for sort,arg in [('ImplementationReference','impl0'),('UseReference','use0')]:add('empty-selected-root-handle-'+sort,lambda m,sort=sort,arg=arg:setfn(m,b.HANDLES[sort],arg,'empty'),T=False,I=None)
 for name,mutation,error in [('empty-domain',lambda m:m['domains'].update(ImplementationReference=[]),'empty-or-malformed-domain'),('missing-domain',lambda m:m['domains'].pop('OwnerReference'),'model-signature-denominator-mismatch'),('missing-function',lambda m:m['functions'].pop('implementationIdentity'),'model-signature-denominator-mismatch'),('partial-function',lambda m:m['functions']['implementationOwner'].pop(),'nontotal-function'),('function-range',lambda m:setfn(m,'implementationOwner','impl0','foreign'),'ill-sorted-function-result'),('predicate-arity',lambda m:m['predicates']['UseScopeWithinImplementationDeclared'].append(['narrow0']),'ill-sorted-model-tuple'),('predicate-range',lambda m:m['predicates']['ImplementationApplicable'].append(['foreign']),'ill-sorted-model-tuple'),('missing-constant',lambda m:m['constants'].pop('SELECTED_DEFINITION'),'model-signature-denominator-mismatch')]:add('malformed-'+name,mutation,error=error)
 return rows
def qualify(model,ids):return {bucket:{ids[name]:value for name,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}

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
    prior=json.loads((b.BASE/'definitions/cal.definition.coordination-context/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Implementation-model-controls/v1-candidate','status':'PASS-for-exact-authored-Implementation-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Necessary technical-realization nominations, inclusive posture, explicit interfaces and evidence, separated governance, scoped exact-version uses and noninference guards checked on supplied models; actual outcomes, fidelity and whole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
