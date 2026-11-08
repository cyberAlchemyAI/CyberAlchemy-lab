"""Independent scoped Surface genus, disjunctive powers, identity and promotion model controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Entity':['s1','s2','s3','s4','e1','e2','e3','p1','d1','c1'],'Token':['empty','norm','rules','promotion','contract','scope1','scope2','project','label','carrier','owner-scope'],'State':['before','after']};functions={}
 for n,(args,result) in b.FUNCTIONS.items():
  rows=[]
  for e in domains['Entity']:
   value=('scope2' if e=='s2' else 'scope1') if n=='scopeValue' else {'projectValue':'project','labelValue':'label','carrierValue':'carrier','ownerScopeValue':'owner-scope'}[n]
   rows.append({'args':[e],'value':value})
  functions[n]=rows
 p={n:[] for n in b.SIGNATURE};p.update(AuthoritySurface=[['s1'],['s2'],['s3'],['s4']],ProjectLocalSurface=[['s1'],['s2'],['s3'],['s4'],['c1']],CanCiteEvidence=[['s1'],['s2'],['s3'],['s4']],Evidence=[['e1'],['e2'],['e3']],RawDeclaredComplete=[['c1']],AllowedToDefine=[['s1','norm','scope1'],['s2','rules','scope2'],['s3','promotion','scope1'],['s4','contract','scope1']],DeclaredUse=[['c1',n,'scope1'] for n in ['norm','rules','promotion','contract']],CitesEvidence=[['s1','e1'],['s2','e2']],EvidenceBecameAuthority=[['e2','scope1']],ResponsibleOwnerPromoted=[['e2','scope1'],['e3','scope1']],InProject=[[e,'project'] for e in ['s1','s2','s3','s4']])
 return {'domains':domains,'constants':{'EMPTY':'empty','NormativeMeaning':'norm','StructuralRule':'rules','PromotionDecision':'promotion','Contract':'contract'},'functions':functions,'predicates':p}
def setvalue(m,n,e,value):next(x for x in m['functions'][n] if x['args']==[e])['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('four-disjunctive-scoped-Surfaces-no-real-grant-or-citation-promotion',lambda m:None,I=True)
 for n in b.OUTCOMES+['DefinitionArtifact','Container','PathNamedAuthority','AuthenticatedSurface']:add('independently-supplied-marker-'+n,lambda m,n=n:m['predicates'][n].append(['s1']),I=True)
 add('independently-supplied-actual-authority-marker',lambda m:m['predicates']['ActualAuthority'].append(['s1','scope1']),I=True)
 add('independently-supplied-actual-definition-effect',lambda m:m['predicates']['ActualDefinedEffect'].append(['s1','norm','scope1','after']),I=True)
 for power in ['norm','rules','promotion','contract']:
  def one_power(m,power=power):m['predicates']['AllowedToDefine']=[x for x in m['predicates']['AllowedToDefine'] if x[0]!='s1']+[['s1',power,'scope1']]
  add('one-selected-defining-purpose-'+power,one_power)
 add('Surface-not-project-local',lambda m:m['predicates']['ProjectLocalSurface'].remove(['s1']),T=False)
 add('Surface-with-empty-specific-scope',lambda m:setvalue(m,'scopeValue','s1','empty'),T=False)
 add('Surface-without-qualified-permission',lambda m:m['predicates']['AllowedToDefine'].remove(['s1','norm','scope1']),T=False)
 add('Surface-with-only-wrong-scope-permission',lambda m:m['predicates'].update(AllowedToDefine=[['s1','norm','scope2'],['s2','rules','scope2'],['s3','promotion','scope1'],['s4','contract','scope1']]),T=False)
 add('other-purpose-does-not-replace-one-of-four-defining-purposes',lambda m:m['predicates'].update(AllowedToDefine=[['s1','project','scope1'],['s2','rules','scope2'],['s3','promotion','scope1'],['s4','contract','scope1']]),T=False)
 add('qualified-local-characterization-without-Surface-reverse-iff-required',lambda m:m['predicates']['AuthoritySurface'].remove(['s1']),T=False)
 add('raw-fields-cannot-force-Surface',lambda m:m['predicates']['AuthoritySurface'].append(['c1']),T=False)
 add('Surface-missing-citation-capability',lambda m:m['predicates']['CanCiteEvidence'].remove(['s1']),T=False)
 add('evidence-authority-without-responsible-owner-promotion',lambda m:m['predicates']['ResponsibleOwnerPromoted'].remove(['e2','scope1']),T=False)
 add('promotion-in-another-scope-does-not-satisfy-source-necessity',lambda m:m['predicates'].update(ResponsibleOwnerPromoted=[['e2','scope2'],['e3','scope1']]),T=False)
 add('cited-evidence-made-authority-without-owner-promotion',lambda m:m['predicates']['EvidenceBecameAuthority'].append(['e1','scope1']),T=False)
 add('cited-promoted-evidence-auto-transferred-to-Surface-scope',lambda m:m['predicates']['EvidenceBecameAuthority'].append(['e2','scope2']),T=False)
 def all_powers(m):m['predicates']['AllowedToDefine'] += [['s1',p,'scope1'] for p in ['rules','promotion','contract']]
 add('all-four-powers-also-permitted-but-not-required',all_powers,I=True)
 def raw_qualifies(m):m['predicates']['AllowedToDefine'].append(['c1','norm','scope1']);m['predicates']['AuthoritySurface'].append(['c1']);m['predicates']['CanCiteEvidence'].append(['c1'])
 add('separately-supplied-qualified-permission-changes-candidate-classification',raw_qualifies,I=False)
 add('no-actual-citation-alternative-theory-model-rich-I-fails',lambda m:m['predicates'].update(CitesEvidence=[]),I=False)
 add('no-evidence-authority-alternative-theory-model-rich-I-fails',lambda m:m['predicates'].update(EvidenceBecameAuthority=[]),I=False)
 add('responsible-promotion-may-remain-without-evidence-authority',lambda m:m['predicates']['ResponsibleOwnerPromoted'].append(['e1','scope2']),I=True)
 add('citation-capability-need-not-create-actual-citation',lambda m:m['predicates']['CanCiteEvidence'].append(['c1']),I=True)
 add('owner-scope-token-can-differ-from-Surface-specific-scope',lambda m:setvalue(m,'ownerScopeValue','s1','scope2'),I=True)
 def labels(m):
  for e,label in zip(['s1','s2','s3','s4'],['norm','rules','promotion','contract']):setvalue(m,'labelValue',e,label)
 add('all-different-labels-alternative-model-no-rich-equal-label-witness',labels,I=False)
 def alias_powers(m):m['constants']['StructuralRule']='norm';m['predicates']['AllowedToDefine'].remove(['s2','rules','scope2']);m['predicates']['AllowedToDefine'].append(['s2','norm','scope2'])
 add('unreviewed-purpose-constant-denotations-can-alias',alias_powers,I=True)
 add('actual-effect-outside-selected-scope-not-operationally-constrained-by-static-T',lambda m:m['predicates']['ActualDefinedEffect'].append(['s1','norm','scope2','after']),I=True)
 add('nontotal-scope-function',lambda m:m['functions']['scopeValue'].pop(),error='nontotal-function')
 add('ill-sorted-scope-function-result',lambda m:setvalue(m,'scopeValue','s1','s1'),error='ill-sorted-function-result')
 add('ill-sorted-power-constant',lambda m:m['constants'].update(NormativeMeaning='absent'),error='ill-sorted-constant')
 add('wrong-qualified-permission-arity',lambda m:m['predicates'].update(AllowedToDefine=[['s1','norm']]),error='ill-sorted-model-tuple')
 add('duplicate-citation-tuple',lambda m:m['predicates']['CitesEvidence'].append(['s1','e1']),error='duplicate-predicate-tuple')
 add('empty-Token-carrier',lambda m:m['domains'].update(Token=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['scopeValue'].append(copy.deepcopy(m['functions']['scopeValue'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.authority-promotion/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-AuthoritySurface-model-controls/v1-candidate','status':'PASS-for-exact-authored-AuthoritySurface-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied scoped genus/differentia, citation capability and necessary evidence-promotion models. Four-purpose Token identity, actual qualified permission/owner/project/scope/promotion and universal rewrite prevention remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
