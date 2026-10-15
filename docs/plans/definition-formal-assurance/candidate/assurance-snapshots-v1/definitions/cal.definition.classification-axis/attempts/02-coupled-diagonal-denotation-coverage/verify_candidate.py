"""Finite versioned coordinate models and independent choice/frame denotation."""
import itertools,json
import build_candidate as b
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def base_model():
 domains={sort:[sort+'-a',sort+'-b'] for sort in b.SORTS};domains.update(Axis=['a','z'],Object=['subject'],State=['s00','s10','s01','s11'],AnswerValue=['zero','one'],SchemeVersion=['sv1','sv2'],SharedIdentity=['axis-a','axis-z','subject-id'],OwnerRoute=['axis-owner','subject-owner'],Kind=['kind'],EvidenceRef=['ev'],EffectDescription=['eff'],Relation=['r','other'])
 functions={n:[{'args':list(xs),'value':domains[res][0]} for xs in itertools.product(*[domains[s] for s in args])] for n,(args,res) in b.FUNCTIONS.items()}
 for row in functions['axisPurpose']:row['value']='Purpose-a' if row['args'][0]=='a' else 'Purpose-b'
 for row in functions['axisIdentity']:row['value']='axis-a' if row['args'][0]=='a' else 'axis-z'
 for row in functions['subjectIdentity']:row['value']='subject-id'
 for row in functions['subjectOwner']:row['value']='subject-owner'
 for row in functions['couplingTarget']:row['value']='z'
 for row in functions['answerAt']:
  _,axis,_,state=row['args'];row['value']='one' if state[1 if axis=='a' else 2]=='1' else 'zero'
 predicates={n:[] for n in b.SIGNATURE}
 for n in ['ClassificationAxis','NamedAxis','NamedDimension','OwnedAxis','DistinctOperationalPurpose','AdmissibleAxis']:predicates[n]=[['a'],['z']]
 predicates.update(AxisDeclaredIn=[[a,'sv1'] for a in ['a','z']],ValueAllowed=[[a,val,'sv1'] for a,val in itertools.product(['a','z'],['zero','one'])],Applies=[['subject',a,'sv1',s] for a,s in itertools.product(['a','z'],domains['State'])],IndependentSelection=[['subject',a,'sv1',s] for a,s in itertools.product(['a','z'],domains['State'])],ExplicitKind=[['r']],NamedKind=[['kind']],ExplicitDirection=[['r']],ExplicitOwner=[['r']],HasEvidence=[['r','ev']],HasEffectDescription=[['r','eff']])
 for a,s,t in itertools.product(['a','z'],domains['State'],domains['State']):
  if s[2 if a=='a' else 1]==t[2 if a=='a' else 1]:predicates['AllowedSelection'].append(['subject',a,'sv1',s,t])
 return {'domains':domains,'constants':{'selectedScheme':'sv1'},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def dependent(m):m['predicates'].update(Dependent=[['a','z']],TypedCoupling=[['r']])
def controls():
 rows=[]
 def add(name,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('four-state-independent-coordinate-cube-in-exact-scheme',lambda m:None)
 for n in ['NamedAxis','NamedDimension','OwnedAxis','DistinctOperationalPurpose']:add('axis-missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['a']]),False)
 add('distinct-axis-cannot-share-selected-semantic-purpose',lambda m:setvalue(m,'axisPurpose',['z'],'Purpose-a'),False)
 add('admissible-redundant-axis-rejected',lambda m:m['predicates'].update(RedundantAxis=[['a']]),False)
 def proposal(m):m['predicates'].update(AdmissibleAxis=[],RedundantAxis=[['a']],Dependent=[['a','z']])
 add('unadmitted-proposal-not-assumed-to-govern-downstream',proposal)
 add('missing-selected-scheme-declaration',lambda m:m['predicates'].update(AxisDeclaredIn=[['a','sv1']]),False)
 add('value-from-other-version-cannot-replace-current-allowed-values',lambda m:m['predicates'].update(ValueAllowed=[[a,val,'sv2'] for a,val in itertools.product(['a','z'],['zero','one'])]),False,False)
 add('unallowed-answer-at-classified-coordinate',lambda m:setvalue(m,'answerAt',['subject','a','sv1','s00'],'AnswerValue-outside-domain'),error='ill-sorted-function-result')
 def wrong_typed(m):m['domains']['AnswerValue'].append('outside');setvalue(m,'answerAt',['subject','a','sv1','s00'],'outside')
 add('well-sorted-but-not-allowed-answer-rejected',wrong_typed,False)
 add('other-scheme-selected-with-no-bindings',lambda m:m['constants'].update(selectedScheme='sv2'),False,False)
 add('applies-with-no-exact-scheme-declaration',lambda m:m['predicates']['Applies'].append(['subject','a','sv2','s00']),False)
 add('independent-selection-with-unclassified-input',lambda m:m['predicates']['IndependentSelection'].append(['subject','a','sv2','s00']),False)
 add('no-independent-selection-vacuous-T-fails-variation-I',lambda m:m['predicates'].update(IndependentSelection=[]),True,False)
 add('independent-selection-needs-actual-alternative-state',lambda m:m['predicates'].update(AllowedSelection=[x for x in m['predicates']['AllowedSelection'] if x[-2]==x[-1]]),False)
 add('missing-classified-destination-breaks-allowed-selection',lambda m:m['predicates']['Applies'].remove(['subject','a','sv1','s10']),False)
 def collapse(m):
  for row in m['functions']['answerAt']:row['value']='one' if row['args'][-1][1]=='1' else 'zero'
 add('one-hidden-status-coordinate-cannot-serve-independent-axes',collapse,False)
 add('uncoupled-coordinate-cochange-rejected',lambda m:m['predicates']['AllowedSelection'].append(['subject','a','sv1','s00','s11']),False)
 def cochange(m):dependent(m);m['predicates']['AllowedSelection'].append(['subject','a','sv1','s00','s11'])
 add('explicit-forward-coupling-allows-selected-cochange',cochange)
 def reverse_change(m):dependent(m);m['predicates']['AllowedSelection'].append(['subject','z','sv1','s00','s11'])
 add('forward-coupling-does-not-lift-reverse-frame',reverse_change,False)
 add('explicit-dependency-does-not-force-cochange',dependent)
 add('admissible-dependency-without-coupling',lambda m:m['predicates'].update(Dependent=[['a','z']]),False)
 for n in ['TypedCoupling','ExplicitKind','NamedKind','ExplicitDirection','ExplicitOwner','HasEvidence','HasEffectDescription']:
  def missing(m,n=n):dependent(m);m['predicates'][n]=[]
  add('bridge-missing-'+n,missing,False)
 for n,val in [('couplingSource','z'),('couplingTarget','a')]:
  def mismatch(m,n=n,val=val):dependent(m);setvalue(m,n,['r'],val)
  add('bridge-wrong-ordered-'+n,mismatch,False)
 def self_link(m):dependent(m);m['predicates']['Dependent']=[['a','a']];setvalue(m,'couplingTarget',['r'],'a')
 add('self-dependency-not-unconditionally-forbidden',self_link)
 def constant_axis(m):
  m['predicates']['ValueAllowed']=[x for x in m['predicates']['ValueAllowed'] if x[0]!='z' or x[1]=='zero']
  for row in m['functions']['answerAt']:
   if row['args'][1]=='z':row['value']='zero'
 add('no-universal-two-value-cardinality-for-every-axis',constant_axis)
 add('axis-descriptor-can-itself-be-classified-subject',lambda m:setvalue(m,'subjectIdentity',['subject'],'axis-a'))
 add('same-owner-permitted-with-distinct-axis-and-subject',lambda m:setvalue(m,'subjectOwner',['subject'],'axis-owner'))
 for n in b.OUTCOMES:add('outcome-independent-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['a'],['z']]))
 add('actual-value-correctness-not-inferred-from-shape',lambda m:m['predicates'].update(ActualValueCorrect=[x[:] for x in m['predicates']['Applies']]))
 def one_axis(m):
  m['predicates']['ClassificationAxis']=[['a']];m['predicates']['AdmissibleAxis']=[['a']]
  for n in ['Applies','IndependentSelection','AllowedSelection']:m['predicates'][n]=[x for x in m['predicates'][n] if x[1]=='a']
 add('one-axis-vacuous-pair-fails-distinct-axis-I',one_axis,True,False)
 def no_axes(m):
  for n in ['ClassificationAxis','AdmissibleAxis','Applies','IndependentSelection','AllowedSelection']:m['predicates'][n]=[]
 add('no-axes-vacuous-T-fails-connected-I',no_axes,True,False)
 add('nontotal-versioned-answer-selector',lambda m:m['functions']['answerAt'].pop(),error='nontotal-function')
 add('bad-applies-arity',lambda m:m['predicates'].update(Applies=[['subject','a','sv1']]),error='ill-sorted-model-tuple')
 add('duplicate-axis-tuple',lambda m:m['predicates']['ClassificationAxis'].append(['a']),error='duplicate-predicate-tuple')
 add('ill-sorted-scheme-constant',lambda m:m['constants'].update(selectedScheme='subject'),error='ill-sorted-constant')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.classification-orthogonality-invariant/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-classification-axis-model-controls/v1-candidate','status':'PASS-for-exact-authored-classification-axis-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite coordinate models and nine targets outside T. Exact scheme/value typing, actual alternative states and uncoupled-coordinate frames are checked; no owner fidelity, world value correctness, immutable-assignment implementation, statistical independence, native enumeration or whole-definition acceptance.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
