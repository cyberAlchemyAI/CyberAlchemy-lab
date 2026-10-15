"""Independent finite denotation of axis purposes, bridges, labels and frame guards."""
import itertools,json
import build_candidate as b
import verifier as v
def load(name):return json.loads((b.UNIT/name).read_bytes())
def base_model():
 domains={sort:[sort+'-a',sort+'-b'] for sort in b.SORTS};domains.update(Axis=['a','z'],State=['s0','s1'],AxisValue=['v0','v1'])
 functions={n:[{'args':list(xs),'value':domains[res][0]} for xs in itertools.product(*[domains[s] for s in args])] for n,(args,res) in b.FUNCTIONS.items()}
 for row in functions['axisPurpose']:row['value']='Purpose-a' if row['args'][0]=='a' else 'Purpose-b'
 for row in functions['couplingTarget']:row['value']='z'
 for row in functions['axisValueAt']:
  if row['args']==['Object-a','a','s1']:row['value']='v1'
 predicates={n:[] for n in b.SIGNATURE}
 for n in ['CanonicalAxis','NamedAxis','OwnedAxis','DistinctOperationalPurpose']:predicates[n]=[['a'],['z']]
 predicates.update(AuthorityAxis=[['z']],ExplicitDirection=[['Relation-a']],ExplicitOwner=[['Relation-a']],ExplicitKind=[['Relation-a']],NamedKind=[['Kind-a']],HasEvidence=[['Relation-a','EvidenceRef-a']],HasEffectDescription=[['Relation-a','EffectDescription-a']],CanonicalLabel=[['Label-b']],ConvenienceLabel=[['Label-a']],GeneratedProjection=[['Label-a']],AllowedAxisChange=[['Object-a','a','s0','s1']])
 return {'domains':domains,'constants':{},'functions':functions,'predicates':predicates}
def setvalue(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def dependent(m):m['predicates'].update(Dependent=[['a','z']],TypedCoupling=[['Relation-a']])
def controls():
 rows=[]
 def add(name,change,T=True,I=True,error=None):
  m=base_model();change(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('distinct-owned-purposes-and-independent-authority-value',lambda m:None)
 for n in ['NamedAxis','OwnedAxis','DistinctOperationalPurpose']:add('canonical-axis-missing-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['a']]),False)
 add('redundant-canonical-axis-rejected',lambda m:m['predicates'].update(RedundantAxis=[['a']]),False)
 add('distinct-flags-do-not-overcome-equal-semantic-purpose',lambda m:setvalue(m,'axisPurpose',['z'],'Purpose-a'),False)
 add('same-owner-does-not-merge-distinct-purpose',lambda m:None)
 add('silent-inference-between-canonical-axes-rejected',lambda m:m['predicates'].update(SilentInference=[['a','z']]),False)
 add('dependence-without-coupling-rejected',lambda m:m['predicates'].update(Dependent=[['a','z']]),False)
 add('complete-explicit-dependence-can-coexist-with-no-cochange',dependent)
 for n in ['TypedCoupling','ExplicitDirection','ExplicitOwner','ExplicitKind','NamedKind','HasEvidence','HasEffectDescription']:
  def remove(m,n=n):dependent(m);m['predicates'][n]=[]
  add('dependent-bridge-missing-'+n,remove,False)
 for n,args,new in [('couplingSource',['Relation-a'],'z'),('couplingTarget',['Relation-a'],'a')]:
  def mismatch(m,n=n,args=args,new=new):dependent(m);setvalue(m,n,args,new)
  add('wrong-ordered-'+n,mismatch,False)
 def reverse_dependency(m):dependent(m);m['predicates']['Dependent']=[['z','a']]
 add('one-forward-bridge-is-not-reverse-dependency',reverse_dependency,False)
 def self_dep(m):dependent(m);m['predicates']['Dependent']=[['a','a']];setvalue(m,'couplingTarget',['Relation-a'],'a')
 add('no-universal-self-dependency-prohibition-invented',self_dep)
 def bridged_change(m):dependent(m);setvalue(m,'axisValueAt',['Object-a','z','s1'],'v1')
 add('explicit-bridge-permits-modeled-allowed-cochange',bridged_change)
 add('unbridged-allowed-change-cannot-advance-other-authority-axis',lambda m:setvalue(m,'axisValueAt',['Object-a','z','s1'],'v1'),False)
 def outside(m):m['predicates']['AllowedAxisChange']=[];setvalue(m,'axisValueAt',['Object-a','z','s1'],'v1')
 add('outside-allowed-change-guard-is-not-certified',outside)
 def bridge_not_silent(m):dependent(m);m['predicates']['SilentInference']=[['a','z']]
 add('explicit-bridge-does-not-license-silent-inference',bridge_not_silent,False)
 add('canonical-redundant-label-rejected',lambda m:m['predicates'].update(RedundantLabel=[['Label-b']]),False)
 add('convenience-label-needs-generated-projection',lambda m:m['predicates'].update(GeneratedProjection=[]),False)
 add('convenience-label-cannot-become-canonical-truth',lambda m:m['predicates']['CanonicalLabel'].append(['Label-a']),False)
 add('no-convenience-label-population-forced',lambda m:m['predicates'].update(ConvenienceLabel=[],GeneratedProjection=[]))
 def nodata(m):m['predicates'].update(ReviewedAxis=[['a']],KnownNoData=[['a']],NamedUniqueQuestion=[['a']])
 add('known-no-data-review-names-unique-question',nodata)
 for n in ['NamedRoutingDecision','NamedValidationEffect']:
  def alternative(m,n=n):nodata(m);m['predicates']['NamedUniqueQuestion']=[];m['predicates'][n]=[['a']]
  add('known-no-data-review-names-'+n,alternative)
 def missing_reason(m):nodata(m);m['predicates']['NamedUniqueQuestion']=[]
 add('known-no-data-review-cannot-omit-all-three-reasons',missing_reason,False)
 def contradiction(m):nodata(m);m['predicates']['DataAvailable']=[['a']]
 add('known-absent-and-available-data-cannot-both-hold',contradiction,False)
 add('available-data-does-not-require-statistical-proof',lambda m:m['predicates'].update(ReviewedAxis=[['a']],DataAvailable=[['a']]))
 add('unknown-data-is-not-known-absent',lambda m:m['predicates'].update(ReviewedAxis=[['a']]))
 for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'].__setitem__(n,[['a'],['z']]))
 add('one-canonical-axis-vacuous-comparison-fails-distinct-population',lambda m:m['predicates'].update(CanonicalAxis=[['a']]),True,False)
 add('no-canonical-axis-vacuous-T-not-I',lambda m:m['predicates'].update(CanonicalAxis=[]),True,False)
 add('unmarked-admissible-axis-still-needs-purpose',lambda m:m['predicates'].update(CanonicalAxis=[],AdmissibleAxis=[['a']],DistinctOperationalPurpose=[]),False,False)
 add('ill-sorted-purpose-selector',lambda m:setvalue(m,'axisPurpose',['a'],'v0'),error='ill-sorted-function-result')
 add('nontotal-axis-value-state-function',lambda m:m['functions']['axisValueAt'].pop(),error='nontotal-function')
 add('ill-sorted-axis-change-tuple',lambda m:m['predicates'].update(AllowedAxisChange=[['Object-a','a','s0']]),error='ill-sorted-model-tuple')
 add('duplicate-axis-tuple',lambda m:m['predicates']['CanonicalAxis'].append(['a']),error='duplicate-predicate-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.typed-coupling-invariant/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-classification-orthogonality-model-controls/v1-candidate','status':'PASS-for-exact-authored-classification-orthogonality-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent authored finite models and nine targets outside T: semantic-purpose uniqueness, explicit coupling, labels, no-data review and guarded authority-axis frame. No actual compliance, semantic-purpose fidelity, statistics/Hilbert bridge, temporal ordering, native enumeration or whole-definition acceptance.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
