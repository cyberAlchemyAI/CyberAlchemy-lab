"""Independent finite immutable-binding/successor/no-inference denotation controls."""
import itertools,json
import build_candidate as b
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def base_model():
 domains={sort:[sort+'-old',sort+'-new'] for sort in b.SORTS};domains.update(Assignment=['old','new','other'],Subject=['subject','other-subject'],SubjectRevision=['subject@1','subject@2','other@1'],SchemeVersion=['sv1','sv2'],Axis=['result','evidence'],Value=['v1','v2'],SharedIdentity=['assignment-old','assignment-new','subject-id','other-id','changed-subject-id'],State=['before','after'],Use=['use'],DefinitionVersion=['selected-def','successor-def'])
 functions={n:[{'args':list(xs),'value':domains[res][0]} for xs in itertools.product(*[domains[s] for s in args])] for n,(args,res) in b.FUNCTIONS.items()}
 for n,res in b.FIELDS.items():
  for row in functions[n]:
   if row['args'][0]=='new':row['value']=domains[res][1] if res!='Subject' and res!='Axis' else domains[res][0]
 for row in functions['recordIdentityAt']:row['value']='assignment-new' if row['args'][0]=='new' else 'assignment-old'
 for row in functions['subjectOfRevision']:row['value']='other-subject' if row['args']==['other@1'] else 'subject'
 for row in functions['subjectIdentityAt']:row['value']='subject-id' if row['args'][0]=='subject' else 'other-id'
 for row in functions['valueScheme']:row['value']='sv2' if row['args']==['v2'] else 'sv1'
 predicates={n:[] for n in b.SIGNATURE}
 for n in ['ClassificationAssignment','GovernedRecord','BoundedScope','ImmutableRecord','AttributableRecord','HasBasisContract','HasEvidenceContract','HasLifecycleContract','HasOwnerContract','HasChallengeContract']:predicates[n]=[['old'],['new']]
 predicates.update(NamedBasis=[[x] for x in domains['Basis']],RecordedAction=[[x] for x in domains['AgentAction']],RecordedMethod=[[x] for x in domains['MethodRef']],RecordedImplementation=[[x] for x in domains['ImplementationRef']],RecordedEvidenceSet=[[x] for x in domains['EvidenceSet']],PresentAssignment=[['old','before'],['old','after'],['new','after']],AxisDeclaredIn=[['result','sv1'],['result','sv2']],AllowedValue=[['v1','result','sv1'],['v2','result','sv2']],AttributionRecorded=[['old','AgentAction-old','before'],['old','AgentAction-old','after'],['new','AgentAction-new','after']],AllowedRecordStep=[['before','after']],AllowedCorrection=[['old','new','before','after']],SuccessorOf=[['new','old']],MethodInUse=[['old','before'],['old','after'],['new','after']],ImplementationInUse=[['old','before'],['old','after'],['new','after']],UsesClassificationAssignment=[['use']])
 return {'domains':domains,'constants':{'selectedDefinition':'selected-def','otherAxis':'evidence'},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(name,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('fresh-successor-exact-new-revision-value-version-retains-old-record',lambda m:None)
 add('governed-identity-alternative-to-record-valid',lambda m:m['predicates'].update(GovernedRecord=[],GovernedIdentity=[['old'],['new']]))
 add('neither-governed-record-nor-identity-rejected',lambda m:m['predicates'].update(GovernedRecord=[]),False)
 for n in ['BoundedScope','ImmutableRecord','AttributableRecord','HasBasisContract','HasEvidenceContract','HasLifecycleContract','HasOwnerContract','HasChallengeContract']:add('missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['old']]),False)
 for n,res in b.FIELDS.items():
  value=base_model()['domains'][res][1]
  if n=='recordIdentityAt':value='assignment-new'
  add('old-record-overwrite-'+n,lambda m,n=n,value=value:setvalue(m,n,['old','after'],value),False)
 add('record-step-deletes-predecessor',lambda m:m['predicates']['PresentAssignment'].remove(['old','after']),False)
 add('record-step-changes-subject-identity',lambda m:setvalue(m,'subjectIdentityAt',['subject','after'],'changed-subject-id'),False)
 add('wrong-subject-revision-owner',lambda m:setvalue(m,'subjectRevisionAt',['new','after'],'other@1'),False)
 add('axis-not-declared-in-exact-scheme',lambda m:m['predicates'].update(AxisDeclaredIn=[['result','sv1']]),False)
 add('value-not-allowed-under-exact-axis-version',lambda m:m['predicates'].update(AllowedValue=[['v1','result','sv1']]),False)
 add('value-axis-does-not-match-assignment',lambda m:setvalue(m,'valueAxis',['v2'],'evidence'),False)
 add('value-version-does-not-match-assignment',lambda m:setvalue(m,'valueScheme',['v2'],'sv1'),False)
 for n in ['NamedBasis','RecordedAction','AttributionRecorded','RecordedEvidenceSet','RecordedMethod','RecordedImplementation']:add('missing-selected-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[]),False)
 add('method-and-implementation-not-used-no-execution-invented',lambda m:m['predicates'].update(MethodInUse=[],ImplementationInUse=[],RecordedMethod=[],RecordedImplementation=[]))
 add('correction-missing-allowed-record-step',lambda m:m['predicates'].update(AllowedRecordStep=[]),False)
 add('correction-without-exact-successor-link',lambda m:m['predicates'].update(SuccessorOf=[]),False)
 add('reversed-successor-direction-rejected',lambda m:m['predicates'].update(SuccessorOf=[['old','new']]),False)
 add('correction-reuses-already-recorded-successor',lambda m:m['predicates']['PresentAssignment'].append(['new','before']),False)
 add('correction-uses-old-record-as-successor',lambda m:m['predicates'].update(AllowedCorrection=[['old','old','before','after']]),False,False)
 add('correction-successor-not-present-after',lambda m:m['predicates']['PresentAssignment'].remove(['new','after']),False)
 add('correction-predecessor-not-present-before',lambda m:m['predicates']['PresentAssignment'].remove(['old','before']),False)
 def wrong_subject(m):setvalue(m,'subjectAt',['new','after'],'other-subject');setvalue(m,'subjectRevisionAt',['new','after'],'other@1')
 add('selected-same-subject-correction-retargets-identity',wrong_subject,False)
 add('no-correction-vacuous-frame-fails-required-correction-I',lambda m:m['predicates'].update(AllowedCorrection=[]),True,False)
 def metadata_correction(m):setvalue(m,'valueAt',['new','after'],'v1');setvalue(m,'schemeAt',['new','after'],'sv1')
 add('metadata-only-correction-permitted-but-fails-value-change-witness-I',metadata_correction,True,False)
 add('same-subject-revision-permitted-for-new-value-correction',lambda m:setvalue(m,'subjectRevisionAt',['new','after'],'subject@1'))
 add('assignment-alone-other-axis-inference-rejected',lambda m:m['predicates'].update(AllowedAssignmentOnlyInference=[['old','evidence','before']]),False)
 add('own-axis-inference-policy-is-separately-scoped',lambda m:m['predicates'].update(AllowedAssignmentOnlyInference=[['old','result','before']]))
 add('independently-supported-other-axis-facts-can-be-true',lambda m:m['predicates'].update(OtherAxisFact=[['subject','evidence','before'],['subject','evidence','after']]))
 def successor_use(m):setvalue(m,'useDefinition',['use'],'successor-def');m['predicates']['AdmittedDefinitionSuccessor']=[['successor-def']]
 add('use-resolves-separately-admitted-definition-successor',successor_use)
 add('same-term-name-is-not-admitted-definition-successor',lambda m:setvalue(m,'useDefinition',['use'],'successor-def'),False)
 add('no-term-use-vacuous-T-fails-required-use-I',lambda m:m['predicates'].update(UsesClassificationAssignment=[]),True,False)
 for n in b.OUTCOMES:add('separately-supported-outcome-permitted-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['old'],['new']]))
 def empty(m):
  for n in ['ClassificationAssignment','PresentAssignment','AllowedCorrection','MethodInUse','ImplementationInUse']:m['predicates'][n]=[]
 add('no-records-vacuous-T-fails-connected-I',empty,True,False)
 add('other-axis-witness-not-own-axis-constant',lambda m:m['constants'].update(otherAxis='result'),True,False)
 add('nontotal-record-selector',lambda m:m['functions']['recordIdentityAt'].pop(),error='nontotal-function')
 add('ill-sorted-revision-owner',lambda m:setvalue(m,'subjectOfRevision',['subject@1'],'old'),error='ill-sorted-function-result')
 add('duplicate-present-record',lambda m:m['predicates']['PresentAssignment'].append(['old','before']),error='duplicate-predicate-tuple')
 add('bad-correction-arity',lambda m:m['predicates'].update(AllowedCorrection=[['old','new','before']]),error='ill-sorted-model-tuple')
 add('ill-sorted-other-axis-constant',lambda m:m['constants'].update(otherAxis='subject'),error='ill-sorted-constant')
 return rows
def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}
def verify(write=False):
    context=load('context.json');b.unchanged(context['sources']);snap=b.snapshot();b.r.verify(snap,b.ROOT)
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
            if case['expected_error'] is not None or (t,i)!=(case['expected_T'],case['expected_I']):raise ValueError('Wrong authored control: '+case['case_id']+' '+str((t,i)))
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
    prior=json.loads((b.BASE/'definitions/cal.definition.classification-value/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-classification-assignment-model-controls/v1-candidate','status':'PASS-for-exact-authored-classification-assignment-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite immutable assignment models and eight targets outside T. Exact subject-revision/axis/value/version, recorded attribution and selected immutable predecessor/correction/subject-identity/no-other-axis frames are checked; no owner fidelity, world value correctness, immutable-assignment implementation, statistical independence, native enumeration or whole-definition acceptance.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
