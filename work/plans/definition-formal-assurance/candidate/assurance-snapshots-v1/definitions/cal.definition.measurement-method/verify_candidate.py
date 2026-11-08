"""Evaluate supplied Method specification/execution models and independent actual-outcome countermodels."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 domains={s:[s.lower()+'A',s.lower()+'Outside'] for s in b.SORTS};domains.update(Method=['mResidue','mRevision','mOther','mOutside'],Execution=['e0','e1','eOutside'],MethodChange=['hProc','hUncertainty','hOutside'],MethodVersion=['v1','v2','vOutside'],Property=['pResidue','pOther','pOutside'],ActualSubject=['subjectA','subjectB','subjectOutside'],Tool=['toolA','toolB','toolOutside'],ToolVersion=['toolV1','toolV2','toolVOutside'],Implementation=['implA','implB','implOutside'],ImplementationVersion=['implV1','implV2','implVOutside'],Token=['empty','reference','extra']);active=['mResidue','mRevision','mOther']
 maps={}
 for n,s in b.FIELDS.items():
  def field(m,n=n,s=s):
   if n=='methodVersion':return {'mResidue':'v1','mRevision':'v2','mOther':'v1','mOutside':'vOutside'}[m]
   if n=='methodProperty':return 'pOutside' if m=='mOutside' else 'pOther' if m=='mOther' else 'pResidue'
   return domains[s][-1] if m=='mOutside' else domains[s][0]
  maps[n]=field
 for n,s in b.EXEC_FIELDS.items():
  def exe(e,n=n,s=s):
   if n=='executionMethod':return 'mOutside' if e=='eOutside' else 'mResidue'
   if n=='executionMethodVersion':return 'vOutside' if e=='eOutside' else 'v1'
   if n in ['executionSubject','executionTool','executionToolVersion','executionImplementation','executionImplementationVersion']:return domains[s][{'e0':0,'e1':1,'eOutside':2}[e]]
   return domains[s][-1] if e=='eOutside' else domains[s][0]
  maps[n]=exe
 maps.update(changeFromMethod=lambda h:'mOutside' if h=='hOutside' else 'mResidue',changeToMethod=lambda h:'mOutside' if h=='hOutside' else 'mRevision')
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['MeasurementMethod','MethodSpecificationInScopeDeclared','VersionedProcedureDeclared','ReproducibilitySpecified','GovernedDeclared','BoundedDeclared']:predicates[n]=[[m] for m in active]
 for n,s in b.FIELDS.items():predicates[s+'Declared']=[[x] for x in dict.fromkeys(maps[n](m) for m in active)]
 for n,s in b.EXEC_FIELDS.items():
  if s!='Method':
   for e in ['e0','e1']:
    row=[maps[n](e)]
    if row not in predicates[s+'Declared']:predicates[s+'Declared'].append(row)
 for n in ['MethodExecution','ExecutionInScopeDeclared','WithinMethodConditionsDeclared']:predicates[n]=[['e0'],['e1']]
 for n in ['MethodChangeApplicable','ChangeInScopeDeclared']:predicates[n]=[['hProc'],['hUncertainty']]
 predicates.update(ProcedureChangedDeclared=[['hProc']],UncertaintyTreatmentChangedDeclared=[['hUncertainty']],ResidueUseDeclared=[['mResidue']],OtherGovernedPropertyUseDeclared=[['mOther']],ToolVersionBoundTo=[['toolV1','toolA'],['toolV2','toolB']],ImplementationVersionBoundTo=[['implV1','implA'],['implV2','implB']])
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('three-complete-specifications-separate-subject-executions-and-two-change-kinds',lambda m:None,I=True)
 for n in b.METHOD_OUTCOMES:add('independent-Method-actual-'+n,lambda m,n=n:m['predicates']['MethodActual'+n].append(['mRevision']),I=True)
 for n in b.EXEC_OUTCOMES:add('independent-Execution-actual-'+n,lambda m,n=n:m['predicates']['ExecutionActual'+n].append(['e1']),I=True)
 add('Method-without-Execution-specification',lambda m:None,I=True)
 add('different-actual-subjects-under-one-specification',lambda m:None,I=True)
 add('different-governed-properties-across-specifications',lambda m:None,I=True)
 add('Tool-and-Implementation-choices-can-vary-under-declared-contract',lambda m:None,I=True)
 add('outside-Method-empty-handle',lambda m:setfn(m,b.HANDLES['Method'],'mOutside','empty'),I=True)
 add('outside-execution-wrong-Method-version-allowed',lambda m:setfn(m,'executionMethodVersion','eOutside','v1'),I=True)
 add('outside-change-declaration-not-selected',lambda m:m['predicates']['ProcedureChangedDeclared'].append(['hOutside']),I=True)
 add('one-Method-can-support-more-than-one-use-label',lambda m:m['predicates']['OtherGovernedPropertyUseDeclared'].append(['mResidue']),I=True)
 def no_outcome_witness(m):
  for n in b.METHOD_OUTCOMES:m['predicates']['MethodActual'+n]=[[x] for x in ['mResidue','mRevision','mOther']]
  for n in b.EXEC_OUTCOMES:m['predicates']['ExecutionActual'+n]=[['e0'],['e1']]
 add('actual-outcomes-permitted-independently-of-no-outcome-witness',no_outcome_witness,I=False)
 def no_execution(m):
  for n in ['MethodExecution','ExecutionInScopeDeclared','WithinMethodConditionsDeclared']:m['predicates'][n]=[]
 add('all-specifications-without-executions-still-satisfy-T',no_execution,I=False)
 def all_executed(m):setfn(m,'executionMethod','e1','mRevision');setfn(m,'executionMethodVersion','e1','v2');m['predicates']['MeasurementMethod'].remove(['mOther']);m['predicates']['MethodSpecificationInScopeDeclared'].remove(['mOther'])
 add('T-can-have-all-selected-Methods-executed',all_executed,I=False)
 for n in ['MethodSpecificationInScopeDeclared','VersionedProcedureDeclared','ReproducibilitySpecified','GovernedDeclared','BoundedDeclared']:add('missing-Method-'+n,lambda m,n=n:m['predicates'][n].remove(['mResidue']),T=False)
 add('declared-scope-without-Method-membership',lambda m:m['predicates']['MeasurementMethod'].remove(['mResidue']),T=False)
 for s in dict.fromkeys(b.FIELDS.values()):add('missing-component-'+s,lambda m,s=s:m['predicates'][s+'Declared'].clear(),T=False)
 for s in b.HANDLE_SORTS:
  args={'Method':'mResidue','MethodChange':'hProc','ActualSubject':'subjectA','ToolVersion':'toolV1','ImplementationVersion':'implV1','CalibrationState':'calibrationstateA'}
  arg=args.get(s,base_model()['domains'][s][0]);add('empty-selected-'+s+'-handle',lambda m,s=s,arg=arg:setfn(m,b.HANDLES[s],arg,'empty'),T=False)
 for n in b.ROLES:add('forbidden-Method-as-'+n,lambda m,n=n:m['predicates'][n].append(['mResidue']),T=False)
 for n in ['ExecutionInScopeDeclared','WithinMethodConditionsDeclared']:add('missing-execution-'+n,lambda m,n=n:m['predicates'][n].remove(['e0']),T=False)
 add('execution-declared-scope-without-membership',lambda m:m['predicates']['MethodExecution'].remove(['e0']),T=False)
 add('execution-binds-outside-Method',lambda m:setfn(m,'executionMethod','e0','mOutside'),T=False)
 for s in ['ActualSubject','ToolVersion','ImplementationVersion','CalibrationState']:add('missing-execution-component-'+s,lambda m,s=s:m['predicates'][s+'Declared'].clear(),T=False)
 add('execution-wrong-declared-Method-version',lambda m:setfn(m,'executionMethodVersion','e0','v2'),T=False)
 add('execution-Tool-version-not-bound-to-Tool',lambda m:m['predicates']['ToolVersionBoundTo'].remove(['toolV1','toolA']),T=False)
 add('execution-Implementation-version-not-bound-to-Implementation',lambda m:m['predicates']['ImplementationVersionBoundTo'].remove(['implV1','implA']),T=False)
 add('missing-change-scope',lambda m:m['predicates']['ChangeInScopeDeclared'].remove(['hProc']),T=False)
 add('change-declared-scope-without-membership',lambda m:m['predicates']['MethodChangeApplicable'].remove(['hProc']),T=False)
 add('change-from-outside-Method',lambda m:setfn(m,'changeFromMethod','hProc','mOutside'),T=False)
 add('change-to-outside-Method',lambda m:setfn(m,'changeToMethod','hProc','mOutside'),T=False)
 add('procedure-only-change-reuses-version',lambda m:setfn(m,'changeToMethod','hProc','mResidue'),T=False)
 add('uncertainty-only-change-reuses-version',lambda m:setfn(m,'changeToMethod','hUncertainty','mResidue'),T=False)
 def both_flags(m):setfn(m,'changeToMethod','hProc','mResidue');m['predicates']['UncertaintyTreatmentChangedDeclared'].append(['hProc'])
 add('both-change-kinds-reuse-version',both_flags,T=False)
 def no_change_same(m):setfn(m,'changeToMethod','hProc','mResidue');m['predicates']['ProcedureChangedDeclared'].clear()
 add('unchanged-selected-declaration-can-keep-version',no_change_same,I=False)
 def no_change_distinct(m):m['predicates']['ProcedureChangedDeclared'].clear()
 add('unchanged-selected-declaration-can-have-distinct-version',no_change_distinct,I=False)
 add('version-labels-have-no-imposed-order',lambda m:setfn(m,'methodVersion','mRevision','vOutside'),T=False)
 # Above deliberately fails because vOutside has no declared-version guard;label ordering itself is never evaluated.
 def opaque_version(m):setfn(m,'methodVersion','mRevision','vOutside');m['predicates']['MethodVersionDeclared'].append(['vOutside'])
 add('any-declared-distinct-version-label-allowed',opaque_version,I=True)
 add('missing-symbol',lambda m:m['predicates'].pop('MeasurementMethod'),error='model-signature-denominator-mismatch')
 add('partial-total-function',lambda m:m['functions']['methodProperty'].pop(),error='nontotal-function')
 add('ill-sorted-constant',lambda m:m['constants'].update(EMPTY='subjectA'),error='ill-sorted-constant')
 add('wrong-version-binding-arity',lambda m:m['predicates'].update(ToolVersionBoundTo=[['toolV1']]),error='ill-sorted-model-tuple')
 add('duplicate-Method-tuple',lambda m:m['predicates']['MeasurementMethod'].append(['mResidue']),error='duplicate-predicate-tuple')
 add('empty-calibration-contract-domain',lambda m:m['domains'].update(CalibrationContract=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['methodProperty'].append(copy.deepcopy(m['functions']['methodProperty'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.interface-claim-support-compatibility-invariant/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-MeasurementMethod-model-controls/v1-candidate','status':'PASS-for-exact-authored-MeasurementMethod-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed Method component declarations,exact execution references and necessary procedure/uncertainty version guards checked on supplied finite models. Actual calibration,reproducibility,correct execution,suitability,results,authority,source-owner fidelity and consumer maps remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
