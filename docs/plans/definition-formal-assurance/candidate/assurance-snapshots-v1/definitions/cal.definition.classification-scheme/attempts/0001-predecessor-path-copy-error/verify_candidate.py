"""Independent finite denotation of selected Scheme contracts and introduction frames."""
import itertools,json
import build_candidate as b
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def base_model():
 domains={sort:[sort+'-a',sort+'-b'] for sort in b.SORTS};domains.update(SchemeVersion=['sv1','sv2'],State=['before','after'],Assignment=['old','successor'],Axis=['axis-old','axis-new'],Value=['value-old','value-new'],DefinitionVersion=['selected-def','successor-def'],SubjectRevision=['revision-old','revision-new'],MeaningToken=['meaning-old','meaning-new'],Use=['use'])
 functions={n:[{'args':list(xs),'value':domains[res][0]} for xs in itertools.product(*[domains[s] for s in args])] for n,(args,res) in b.FUNCTIONS.items()}
 predicates={n:[] for n in b.SIGNATURE}
 for n in ['ClassificationScheme','GovernedIdentity','BoundedScope','VersionedContract','HasAxesContract','HasValuesContract','HasDefinitionsContract','HasOwnerContract','HasChallengeContract']:predicates[n]=[['sv1'],['sv2']]
 predicates.update(DeclaredPolicy=[['sv1','PolicyRef-a'],['sv2','PolicyRef-a']],AxisIn=[['axis-old','sv1'],['axis-new','sv2']],ValueIn=[['axis-old','value-old','sv1'],['axis-new','value-new','sv2']],DefinitionIn=[['selected-def','sv1']],PresentVersion=[['sv1','before'],['sv1','after'],['sv2','after']],PresentAssignment=[['old','before'],['old','after']],AllowedVersionIntroduction=[['sv2','before','after']],UsesClassificationScheme=[['use']])
 return {'domains':domains,'constants':{'selectedDefinition':'selected-def'},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(name,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('new-exact-version-preserves-old-assignment-meaning-and-binding',lambda m:None)
 add('governed-record-is-sufficient-alternative-to-governed-identity',lambda m:m['predicates'].update(GovernedIdentity=[],GovernedRecord=[['sv1'],['sv2']]))
 add('neither-governed-identity-nor-record-rejected',lambda m:m['predicates'].update(GovernedIdentity=[]),False)
 for n in ['BoundedScope','VersionedContract','HasAxesContract','HasValuesContract','HasDefinitionsContract','HasOwnerContract','HasChallengeContract']:add('contract-missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['sv1']]),False)
 for n in b.POLICIES:
  add('policy-reference-without-declared-role-'+n,lambda m,n=n:setvalue(m,n+'Policy',['sv2'],'PolicyRef-b'),False)
 def separate_policies(m):
  for row in m['functions']['compatibilityPolicy']:row['value']='PolicyRef-b'
  m['predicates']['DeclaredPolicy'] += [['sv1','PolicyRef-b'],['sv2','PolicyRef-b']]
 add('distinct-policy-references-permitted-but-not-required',separate_policies)
 for n,value in [('assignmentVersionAt','sv2'),('assignmentAxisAt','axis-new'),('assignmentValueAt','value-new'),('assignmentSubjectAt','revision-new'),('assignmentMeaningAt','meaning-new')]:add('introduction-silently-changes-old-'+n,lambda m,n=n,value=value:setvalue(m,n,['old','after'],value),False)
 add('introduction-deletes-old-assignment',lambda m:m['predicates']['PresentAssignment'].remove(['old','after']),False)
 add('introduction-deletes-old-version',lambda m:m['predicates']['PresentVersion'].remove(['sv1','after']),False)
 add('introduction-new-version-not-fresh',lambda m:m['predicates']['PresentVersion'].append(['sv2','before']),False)
 add('introduction-new-version-not-present-after',lambda m:m['predicates']['PresentVersion'].remove(['sv2','after']),False)
 add('introduction-same-before-after-state-rejected',lambda m:m['predicates'].update(AllowedVersionIntroduction=[['sv2','before','before']]),False)
 def migrate(m):
  for n,value in [('assignmentVersionAt','sv2'),('assignmentAxisAt','axis-new'),('assignmentValueAt','value-new'),('assignmentSubjectAt','revision-new'),('assignmentMeaningAt','meaning-new')]:setvalue(m,n,['successor','after'],value)
  m['predicates']['PresentAssignment'].append(['successor','after'])
 add('separate-explicit-migration-successor-retains-old-record',migrate)
 add('old-assignment-value-not-allowed-in-exact-version',lambda m:m['predicates'].update(ValueIn=[['axis-old','value-old','sv2'],['axis-new','value-new','sv2']]),False)
 add('old-assignment-axis-not-declared-in-exact-version',lambda m:m['predicates'].update(AxisIn=[['axis-old','sv2'],['axis-new','sv2']]),False)
 def successor_use(m):setvalue(m,'useDefinition',['use'],'successor-def');m['predicates']['AdmittedDefinitionSuccessor']=[['successor-def']]
 add('use-resolves-separately-admitted-definition-successor',successor_use)
 add('same-term-label-does-not-resolve-unadmitted-definition-version',lambda m:setvalue(m,'useDefinition',['use'],'successor-def'),False)
 add('no-introduction-vacuous-frame-fails-required-connected-witness',lambda m:m['predicates'].update(AllowedVersionIntroduction=[]),True,False)
 add('no-assignment-vacuous-typing-fails-required-connected-witness',lambda m:m['predicates'].update(PresentAssignment=[]),True,False)
 add('no-term-use-vacuous-resolution-fails-required-use',lambda m:m['predicates'].update(UsesClassificationScheme=[]),True,False)
 add('nominally-distinct-version-family-fails-selected-same-family-I',lambda m:setvalue(m,'schemeFamily',['sv2'],'SchemeFamily-b'),True,False)
 def no_schemes(m):
  for n in ['ClassificationScheme','PresentAssignment','AllowedVersionIntroduction']:m['predicates'][n]=[]
 add('no-scheme-vacuous-T-fails-required-populations',no_schemes,True,False)
 for n in b.OUTCOMES:add('separately-supported-outcome-allowed-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['sv1'],['sv2']]))
 add('policy-function-nontotal',lambda m:m['functions']['cardinalityPolicy'].pop(),error='nontotal-function')
 add('ill-sorted-meaning-selector',lambda m:setvalue(m,'assignmentMeaningAt',['old','after'],'sv1'),error='ill-sorted-function-result')
 add('duplicate-assignment-tuple',lambda m:m['predicates']['PresentAssignment'].append(['old','before']),error='duplicate-predicate-tuple')
 add('bad-introduction-arity',lambda m:m['predicates'].update(AllowedVersionIntroduction=[['sv2','before']]),error='ill-sorted-model-tuple')
 add('bad-selected-definition-constant',lambda m:m['constants'].update(selectedDefinition='sv1'),error='ill-sorted-constant')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.classification-scheme/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-classification-scheme-model-controls/v1-candidate','status':'PASS-for-exact-authored-classification-scheme-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite versioned-contract models and seven targets outside T. Exact contract/assignment typing and selected version-introduction preservation frames are checked; no owner fidelity, world value correctness, immutable-assignment implementation, statistical independence, native enumeration or whole-definition acceptance.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
