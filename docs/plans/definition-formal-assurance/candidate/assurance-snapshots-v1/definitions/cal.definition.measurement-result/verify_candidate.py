"""Supplied Result record,snapshot,successor and use models;actual outcomes remain independent."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 domains={s:[s.lower()+'A',s.lower()+'Outside'] for s in b.SORTS};domains.update(Result=['rOriginal','rSuccessor','rSameValue','rOutside'],MethodExecution=['e0','e1','e2','eOutside'],ResultSnapshot=['sBefore','sAfter','sOutside'],ResultCorrection=['h0','hAlternative','hOutside'],ResultUse=['aInterpret','aAccept','aFinding','aOutside'],Value=['value0','value1','valueOutside'],ValidityPosture=['posture0','posture1','postureOutside'],Token=['empty','reference','extra']);active=['rOriginal','rSuccessor','rSameValue'];maps={}
 for n,s in b.FIELDS.items():
  def field(r,n=n,s=s):
   if n=='resultExecution':return {'rOriginal':'e0','rSuccessor':'e1','rSameValue':'e2','rOutside':'eOutside'}[r]
   if n=='resultValue':return 'valueOutside' if r=='rOutside' else 'value1' if r=='rSuccessor' else 'value0'
   if n=='resultValidityPosture':return 'postureOutside' if r=='rOutside' else 'posture1' if r=='rSuccessor' else 'posture0'
   return domains[s][-1] if r=='rOutside' else domains[s][0]
  maps[n]=field
 for n in b.BOUND_FIELDS:maps['execution'+n]=lambda e,n=n:maps['result'+n]({'e0':'rOriginal','e1':'rSuccessor','e2':'rSameValue','eOutside':'rOutside'}[e])
 maps['snapshotResult']=lambda s:'rOutside' if s=='sOutside' else 'rOriginal'
 for n in b.FIELDS:maps['snapshot'+n[6:]]=lambda s,n=n:maps[n](maps['snapshotResult'](s))
 maps.update(correctionOriginal=lambda h:'rOutside' if h=='hOutside' else 'rOriginal',correctionSuccessor=lambda h:'rOutside' if h=='hOutside' else 'rSameValue' if h=='hAlternative' else 'rSuccessor',correctionOriginalSnapshot=lambda h:'sOutside' if h=='hOutside' else 'sBefore',correctionPreservedSnapshot=lambda h:'sOutside' if h=='hOutside' else 'sAfter',useResult=lambda a:'rOutside' if a=='aOutside' else 'rOriginal')
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['MeasurementResult','ResultInScopeDeclared','ImmutableRecordDeclared','AttributableRecordDeclared','GovernedDeclared','BoundedDeclared']:predicates[n]=[[r] for r in active]
 for n,s in b.FIELDS.items():predicates[s+'Declared']=[[x] for x in dict.fromkeys(maps[n](r) for r in active)]
 for n in ['ResultSnapshotApplicable','SnapshotInScopeDeclared']:predicates[n]=[['sBefore'],['sAfter']]
 for n in ['ResultCorrectionApplicable','CorrectionInScopeDeclared','OriginalPreservedDeclared','OriginalEvidencePreservedDeclared']:predicates[n]=[['h0']]
 for n in ['ResultUseApplicable','UseInScopeDeclared','SeparateGovernedActDeclared']:predicates[n]=[['aInterpret'],['aAccept'],['aFinding']]
 predicates.update(SuccessorResultDeclared=[['rOriginal','rSuccessor']],InterpretationUseDeclared=[['aInterpret']],AcceptanceUseDeclared=[['aAccept']],FindingUseDeclared=[['aFinding']])
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('exact-record-preserved-original-distinct-successor-and-separate-uses',lambda m:None,I=True)
 for n in b.RESULT_OUTCOMES:add('independent-Result-actual-'+n,lambda m,n=n:m['predicates']['ResultActual'+n].append(['rSameValue']),I=True)
 for n in b.CORRECTION_OUTCOMES:add('independent-Correction-actual-'+n,lambda m,n=n:m['predicates']['CorrectionActual'+n].append(['h0']),I=False)
 for n in b.USE_OUTCOMES:add('independent-Use-actual-'+n,lambda m,n=n:m['predicates']['UseActual'+n].append(['aInterpret']),I=False)
 add('different-validity-postures-without-claim-support',lambda m:None,I=True)
 add('distinct-Results-can-retain-identical-value',lambda m:None,I=True)
 add('outside-Result-empty-handle',lambda m:setfn(m,b.HANDLES['Result'],'rOutside','empty'),I=True)
 add('outside-snapshot-content-can-differ',lambda m:setfn(m,'snapshotValue','sOutside','value0'),I=True)
 add('outside-correction-can-name-itself-as-successor',lambda m:setfn(m,'correctionSuccessor','hOutside','rOutside'),I=True)
 add('outside-use-can-be-ungoverned',lambda m:m['predicates']['AcceptanceUseDeclared'].append(['aOutside']),I=True)
 def same_value_correction(m):setfn(m,'correctionSuccessor','h0','rSameValue');m['predicates']['SuccessorResultDeclared']=[['rOriginal','rSameValue']]
 add('legitimate-correction-need-not-change-numerical-value',same_value_correction,I=True)
 def two_successors(m):
  for n in ['ResultCorrectionApplicable','CorrectionInScopeDeclared','OriginalPreservedDeclared','OriginalEvidencePreservedDeclared']:m['predicates'][n].append(['hAlternative'])
  m['predicates']['SuccessorResultDeclared'].append(['rOriginal','rSameValue'])
 add('multiple-declared-successors-not-globally-forbidden',two_successors,I=True)
 def no_correction(m):
  for n in ['ResultCorrectionApplicable','CorrectionInScopeDeclared']:m['predicates'][n]=[]
 add('Result-record-does-not-force-a-correction',no_correction,I=False)
 def no_use(m):
  for n in ['ResultUseApplicable','UseInScopeDeclared']:m['predicates'][n]=[]
 add('Result-record-does-not-force-interpretation-acceptance-or-Finding-use',no_use,I=False)
 def no_snapshot(m):
  for n in ['ResultSnapshotApplicable','SnapshotInScopeDeclared','ResultCorrectionApplicable','CorrectionInScopeDeclared']:m['predicates'][n]=[]
 add('Result-declaration-does-not-force-actual-storage-state',no_snapshot,I=False)
 def all_actual(m):
  for n in b.RESULT_OUTCOMES:m['predicates']['ResultActual'+n]=[[r] for r in ['rOriginal','rSuccessor','rSameValue']]
 add('actual-outcomes-can-exist-independently-of-absence-witness',all_actual,I=False)
 for n in ['ResultInScopeDeclared','ImmutableRecordDeclared','AttributableRecordDeclared','GovernedDeclared','BoundedDeclared']:add('missing-record-'+n,lambda m,n=n:m['predicates'][n].remove(['rOriginal']),T=False)
 add('declared-scope-without-Result-membership',lambda m:m['predicates']['MeasurementResult'].remove(['rOriginal']),T=False)
 for s in dict.fromkeys(b.FIELDS.values()):add('missing-record-component-'+s,lambda m,s=s:m['predicates'][s+'Declared'].clear(),T=False)
 for s in b.HANDLES:
  args={'Result':'rOriginal','ResultSnapshot':'sBefore','ResultCorrection':'h0','ResultUse':'aInterpret','MethodExecution':'e0','Value':'value0','ValidityPosture':'posture0'};arg=args.get(s,base_model()['domains'][s][0]);add('empty-selected-'+s+'-handle',lambda m,s=s,arg=arg:setfn(m,b.HANDLES[s],arg,'empty'),T=False)
 for n in b.ROLES:add('forbidden-Result-as-'+n,lambda m,n=n:m['predicates'][n].append(['rOriginal']),T=False)
 for n in b.BOUND_FIELDS:
  alt=base_model()['domains'][b.FIELDS['result'+n]][-1];add('wrong-exact-execution-'+n,lambda m,n=n,alt=alt:setfn(m,'execution'+n,'e0',alt),T=False)
 for n in b.FIELDS:
  alt=base_model()['domains'][b.FIELDS[n]][-1];add('silent-snapshot-mutation-'+n[6:],lambda m,n=n,alt=alt:setfn(m,'snapshot'+n[6:],'sAfter',alt),T=False)
 add('missing-snapshot-scope',lambda m:m['predicates']['SnapshotInScopeDeclared'].remove(['sBefore']),T=False)
 add('snapshot-declared-scope-without-membership',lambda m:m['predicates']['ResultSnapshotApplicable'].remove(['sBefore']),T=False)
 add('snapshot-binds-outside-Result',lambda m:setfn(m,'snapshotResult','sBefore','rOutside'),T=False)
 add('missing-correction-scope',lambda m:m['predicates']['CorrectionInScopeDeclared'].remove(['h0']),T=False)
 add('correction-declared-scope-without-membership',lambda m:m['predicates']['ResultCorrectionApplicable'].remove(['h0']),T=False)
 add('correction-overwrites-original-identity',lambda m:setfn(m,'correctionSuccessor','h0','rOriginal'),T=False)
 add('correction-original-outside-Result',lambda m:setfn(m,'correctionOriginal','h0','rOutside'),T=False)
 add('correction-successor-outside-Result',lambda m:setfn(m,'correctionSuccessor','h0','rOutside'),T=False)
 for n in ['SuccessorResultDeclared','OriginalPreservedDeclared','OriginalEvidencePreservedDeclared']:add('missing-correction-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['correctionOriginalSnapshot','correctionPreservedSnapshot']:add('correction-outside-'+n,lambda m,n=n:setfn(m,n,'h0','sOutside'),T=False)
 for n in ['UseInScopeDeclared','SeparateGovernedActDeclared']:add('missing-use-'+n,lambda m,n=n:m['predicates'][n].remove(['aInterpret']),T=False)
 add('use-declared-scope-without-membership',lambda m:m['predicates']['ResultUseApplicable'].remove(['aInterpret']),T=False)
 for n,a in zip(b.USE_KINDS,['aInterpret','aAccept','aFinding']):add('unclassified-use-'+n,lambda m,n=n,a=a:m['predicates'][n].remove([a]),T=False)
 add('use-binds-outside-Result',lambda m:setfn(m,'useResult','aInterpret','rOutside'),T=False)
 add('missing-symbol',lambda m:m['predicates'].pop('MeasurementResult'),error='model-signature-denominator-mismatch')
 add('partial-total-function',lambda m:m['functions']['resultValue'].pop(),error='nontotal-function')
 add('ill-sorted-constant',lambda m:m['constants'].update(EMPTY='value0'),error='ill-sorted-constant')
 add('wrong-successor-arity',lambda m:m['predicates'].update(SuccessorResultDeclared=[['rOriginal']]),error='ill-sorted-model-tuple')
 add('duplicate-Result-tuple',lambda m:m['predicates']['MeasurementResult'].append(['rOriginal']),error='duplicate-predicate-tuple')
 add('empty-validity-domain',lambda m:m['domains'].update(ValidityPosture=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['resultValue'].append(copy.deepcopy(m['functions']['resultValue'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.measurement-method/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-MeasurementResult-model-controls/v1-candidate','status':'PASS-for-exact-authored-MeasurementResult-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed exact Result component/execution declarations,immutable snapshot equalities,necessary successor-preservation guards and separate governed uses checked on supplied models. Actual validity,support,immutable storage,provenance,execution,retention,authority,owner acceptance and consumer maps remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
