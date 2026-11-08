"""Independent finite governed act/result, exact-answer and inference-policy controls."""
import itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={sort:[sort+'-1',sort+'-2'] for sort in b.SORTS};domains.update(Episode=['e1','e2'],Act=['act1','act2'],Result=['r1','r2'],Subject=['subject','other-subject'],SubjectRevision=['subject@1','subject@2'],SchemeVersion=['sv1','sv2'],Axis=['kind','evidence'],Question=['kind-question','evidence-question'],Assignment=['a-kind1','a-evidence','a-kind2'],Value=['kind-value1','evidence-value','kind-value2'],AgentAction=['action1','action2'],SharedIdentity=['episode-id','assignment-1','assignment-2','assignment-3','subject-id'],DefinitionVersion=['selected-def','successor-def'],Use=['use'])
 functions={n:[{'args':list(xs),'value':domains[res][0]} for xs in itertools.product(*[domains[s] for s in args])] for n,(args,res) in b.FUNCTIONS.items()}
 for row in functions['assignmentAxis']:row['value']='evidence' if row['args']==['a-evidence'] else 'kind'
 for row in functions['assignmentValue']:row['value']={'a-kind1':'kind-value1','a-evidence':'evidence-value','a-kind2':'kind-value2'}[row['args'][0]]
 for row in functions['valueAxis']:row['value']='evidence' if row['args']==['evidence-value'] else 'kind'
 for row in functions['axisQuestion']:row['value']='evidence-question' if row['args']==['evidence'] else 'kind-question'
 for row in functions['subjectIdentity']:row['value']='subject-id'
 for i,row in enumerate(functions['assignmentIdentity']):row['value']='assignment-'+str(i+1)
 predicates={n:[] for n in b.SIGNATURE};predicates.update(Classification=[['e1']],GovernedRecord=[['e1']],BoundedScope=[['e1']],GovernedAct=[['act1']],GovernedResult=[['r1']],NamedAxis=[['kind'],['evidence']],NamedQuestion=[['kind-question'],['evidence-question']],RecordedAssignment=[[a] for a in domains['Assignment']],RecordedAgentAction=[['action1']],UsesClassification=[['use']],ActProducesResult=[['act1','r1']],ActionRecordsAct=[['action1','act1']],ResultAssignment=[['r1',a] for a in domains['Assignment']],AxisDeclaredIn=[['kind','sv1'],['evidence','sv1']],ValueAllowed=[['kind-value1','kind','sv1'],['evidence-value','evidence','sv1'],['kind-value2','kind','sv1']])
 return {'domains':domains,'constants':{'selectedDefinition':'selected-def'},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(name,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('governed-act-result-three-exact-answers-two-questions-one-scheme',lambda m:None)
 add('governed-identity-alternative-to-record-valid',lambda m:m['predicates'].update(GovernedRecord=[],GovernedIdentity=[['e1']]))
 add('neither-governed-identity-nor-record-rejected',lambda m:m['predicates'].update(GovernedRecord=[]),False)
 for n in ['BoundedScope','GovernedAct','GovernedResult','RecordedAgentAction','ActProducesResult','ActionRecordsAct']:add('missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[]),False)
 for n in ['actSubjectRevision','resultSubjectRevision']:add('wrong-'+n,lambda m,n=n:setvalue(m,n,[{'actSubjectRevision':'act1','resultSubjectRevision':'r1'}[n]],'subject@2'),False)
 for n in ['actScheme','resultScheme']:add('wrong-'+n,lambda m,n=n:setvalue(m,n,[{'actScheme':'act1','resultScheme':'r1'}[n]],'sv2'),False)
 add('producer-action-mismatch',lambda m:setvalue(m,'actProducerAction',['act1'],'action2'),False)
 add('wrong-selected-act',lambda m:setvalue(m,'episodeAct',['e1'],'act2'),False)
 add('wrong-selected-result',lambda m:setvalue(m,'episodeResult',['e1'],'r2'),False,False)
 add('mixed-exact-subject-revisions-in-one-result',lambda m:setvalue(m,'assignmentSubjectRevision',['a-evidence'],'subject@2'),False)
 add('mixed-exact-scheme-versions-in-one-result',lambda m:setvalue(m,'assignmentScheme',['a-evidence'],'sv2'),False)
 add('assignment-not-recorded',lambda m:m['predicates'].update(RecordedAssignment=[['a-kind1'],['a-kind2']]),False)
 add('unnamed-axis',lambda m:m['predicates'].update(NamedAxis=[['kind']]),False)
 add('unnamed-question',lambda m:m['predicates'].update(NamedQuestion=[['kind-question']]),False)
 add('axis-not-declared-in-exact-scheme',lambda m:m['predicates'].update(AxisDeclaredIn=[['kind','sv1']]),False)
 add('value-from-wrong-axis',lambda m:setvalue(m,'valueAxis',['evidence-value'],'kind'),False)
 add('value-from-wrong-version',lambda m:setvalue(m,'valueScheme',['evidence-value'],'sv2'),False)
 add('unallowed-exact-answer',lambda m:m['predicates'].update(ValueAllowed=[['kind-value1','kind','sv1'],['kind-value2','kind','sv1']]),False)
 add('different-axes-collapsed-into-one-question',lambda m:setvalue(m,'axisQuestion',['evidence'],'kind-question'),False)
 add('same-axis-multiple-values-permitted-no-universal-single-value-rule',lambda m:None)
 add('one-value-per-axis-valid-but-fails-selected-multi-value-I',lambda m:m['predicates'].update(ResultAssignment=[['r1','a-kind1'],['r1','a-evidence']]),True,False)
 add('one-axis-two-values-valid-but-fails-selected-two-question-I',lambda m:m['predicates'].update(ResultAssignment=[['r1','a-kind1'],['r1','a-kind2']]),True,False)
 add('one-answer-valid-but-fails-richer-selected-I',lambda m:m['predicates'].update(ResultAssignment=[['r1','a-kind1']]),True,False)
 add('empty-result-is-not-selected-assigning-declared-values',lambda m:m['predicates'].update(ResultAssignment=[]),False,False)
 add('additional-unselected-result-links-not-universally-forbidden',lambda m:m['predicates']['ActProducesResult'].append(['act1','r2']))
 def shared(m):
  for n in ['Classification','GovernedRecord','BoundedScope']:m['predicates'][n].append(['e2'])
 add('two-concept-records-may-reference-one-act-result-pair',shared)
 add('concept-and-assignment-id-tokens-may-lexically-overlap',lambda m:setvalue(m,'episodeIdentity',['e1'],'assignment-1'))
 def successor(m):setvalue(m,'useDefinition',['use'],'successor-def');m['predicates']['AdmittedDefinitionSuccessor']=[['successor-def']]
 add('use-resolves-separately-admitted-definition-successor',successor)
 add('same-term-name-not-admitted-definition-successor',lambda m:setvalue(m,'useDefinition',['use'],'successor-def'),False)
 add('no-use-vacuous-resolution-fails-required-use-I',lambda m:m['predicates'].update(UsesClassification=[]),True,False)
 for n in b.SOURCE_OUTCOMES:add('classification-alone-may-not-authorize-'+n,lambda m,n=n:m['predicates'].__setitem__('AllowedClassificationOnly'+n,[['e1']]),False)
 for n in b.OUTCOMES:add('independently-supported-world-outcome-permitted-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['e1']]))
 add('no-classification-vacuous-T-fails-connected-I',lambda m:m['predicates'].update(Classification=[]),True,False)
 add('nontotal-exact-revision-selector',lambda m:m['functions']['episodeSubjectRevision'].pop(),error='nontotal-function')
 add('ill-sorted-value-axis-result',lambda m:setvalue(m,'valueAxis',['evidence-value'],'r1'),error='ill-sorted-function-result')
 add('duplicate-result-assignment-tuple',lambda m:m['predicates']['ResultAssignment'].append(['r1','a-kind1']),error='duplicate-predicate-tuple')
 add('ill-sorted-act-result-arity',lambda m:m['predicates'].update(ActProducesResult=[['act1']]),error='ill-sorted-model-tuple')
 add('ill-sorted-definition-constant',lambda m:m['constants'].update(selectedDefinition='sv1'),error='ill-sorted-constant')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.classification-assignment/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-classification-model-controls/v1-candidate','status':'PASS-for-exact-authored-classification-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite classification composition models and thirteen targets outside T. Exact governed act/result/subject-revision/Scheme/answer composition and selected classification-only inference policy are checked; no owner fidelity, world value correctness, immutable-assignment implementation, statistical independence, native enumeration or whole-definition acceptance.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
