"""Independent Request-input,normalized-metadata and no mutation/effect controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['r1','r2','d1','d2','c1','c2','u1','u2','raw'];requests=['r1','r2'];fields=b.FIELDS+['extra'];domains={'Entity':entities,'Field':fields,'Token':['empty','spec','reqID','use1','sel1','out1','exclude1','other','*']}
 functions={'fieldValue':[{'args':[e,f],'value':'spec'} for e,f in itertools.product(entities,fields)],'normalizedIdValue':[{'args':[e],'value':'reqID'} for e in entities],'requestedContext':[{'args':[e],'value':'c1'} for e in entities]}
 p={n:[] for n in b.SIGNATURE};p.update(ContextRequest=[[e] for e in requests],NormalizedDefinitionTarget=[['d1'],['d2']],ContextResolutionScope=[['d1'],['d2']],DefinitionCarrier=[['d1'],['d2']],CanonicalDefinitionInstance=[['d1']],PreservesExactD66Relation=[['d1']],ContextRole=[['c1'],['c2']],ConsumerRole=[['u1'],['u2']],DeclaresField=[[e,f] for e,f in itertools.product(requests+['raw'],b.FIELDS)],DeclaredContextTarget=[[e,'c1'] for e in requests],ConsumerRef=[['r1','u1'],['r2','u2']],IntendedUse=[[e,'use1'] for e in requests],Selector=[[e,'sel1'] for e in requests],OutputConstraint=[[e,'out1'] for e in requests],ExcludedItem=[['r1','exclude1']],UseToken=[['use1']],ExactSelectorToken=[['sel1']],OutputConstraintToken=[['out1']],ExclusionToken=[['exclude1']],RawDeclaredComplete=[['raw']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in requests]
 return {'domains':domains,'constants':{'EMPTY':'empty','NORMALIZED_REQUEST_ID':'reqID',**{'F_'+n:n for n in b.FIELDS}},'functions':functions,'predicates':p}
def setfield(m,e,f,value):next(x for x in m['functions']['fieldValue'] if x['args']==[e,f])['value']=value
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('typed-bounded-inputs-shared-Context-and-separate-Definition-metadata',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['r1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['r1']),T=False)
 add('reverse-genus-iff-missing',lambda m:m['predicates']['ContextRequest'].remove(['r1']),T=False)
 for n in b.FIELDS:add('missing-field-'+n,lambda m,n=n:m['predicates']['DeclaresField'].remove(['r1',n]),T=False)
 for n in ['ContextResolutionScope','DefinitionCarrier']:add('normalized-definition-missing-'+n,lambda m,n=n:m['predicates'][n].remove(['d1']),T=False)
 add('normalized-definition-wrong-identity',lambda m:setfn(m,'normalizedIdValue',['d1'],'other'),T=False)
 add('canonical-definition-without-target',lambda m:m['predicates']['NormalizedDefinitionTarget'].remove(['d1']),T=False)
 add('canonical-definition-without-D66-relation',lambda m:m['predicates']['PreservesExactD66Relation'].clear(),T=False)
 add('canonical-definition-silent-sibling-merge',lambda m:m['predicates']['SilentSiblingIdentityMerge'].append(['d1']),T=False)
 add('requested-Context-untyped',lambda m:m['predicates']['ContextRole'].remove(['c1']),T=False)
 add('requested-Context-equals-request',lambda m:(setfn(m,'requestedContext',['r1'],'r1'),m['predicates']['DeclaredContextTarget'].remove(['r1','c1']),m['predicates']['DeclaredContextTarget'].append(['r1','r1'])),T=False)
 add('missing-declared-Context-target',lambda m:m['predicates']['DeclaredContextTarget'].remove(['r1','c1']),T=False)
 add('second-declared-Context-target',lambda m:m['predicates']['DeclaredContextTarget'].append(['r1','c2']),T=False)
 add('consumer-without-role',lambda m:m['predicates']['ConsumerRole'].remove(['u1']),T=False)
 add('request-without-consumer',lambda m:m['predicates']['ConsumerRef'].remove(['r1','u1']),T=False)
 for n,role,token in [('IntendedUse','UseToken','use1'),('Selector','ExactSelectorToken','sel1'),('OutputConstraint','OutputConstraintToken','out1'),('ExcludedItem','ExclusionToken','exclude1')]:
  add('input-without-role-'+n,lambda m,role=role,token=token:m['predicates'][role].remove([token]),T=False)
  if n!='ExcludedItem':add('request-without-'+n,lambda m,n=n,token=token:m['predicates'][n].remove(['r1',token]),T=False)
  add('empty-input-token-'+n,lambda m,n=n,role=role,token=token:(m['predicates'][n].remove(['r1',token]),m['predicates'][n].append(['r1','empty']),m['predicates'][role].append(['empty'])),T=False)
 for n in ['owner_ref','scope_ref','freshness_requirement']:add('empty-attribution-or-freshness-'+n,lambda m,n=n:setfield(m,'r1',n,'empty'),T=False)
 for n in ['MutatesContext','GrantsSourceAuthority',*b.INFER_FLAGS]:add('forbidden-request-effect-'+n,lambda m,n=n:m['predicates'][n].append(['r1']),T=False)
 for n in [*b.ROLES,'SiblingMeaningImportedWithoutExplicitReference']:add('forbidden-request-sibling-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['r1']),T=False)
 add('empty-exclusions-permitted',lambda m:None,I=True)
 add('many-named-consumers-permitted',lambda m:m['predicates']['ConsumerRef'].append(['r1','u2']),I=True)
 add('literal-glob-token-marked-exact-without-parser',lambda m:(m['predicates']['Selector'].append(['r1','*']),m['predicates']['ExactSelectorToken'].append(['*'])),I=True)
 add('opaque-freshness-token-not-evaluated',lambda m:setfield(m,'r1','freshness_requirement','other'),I=True)
 for n in ['context_ref','consumer_refs','intended_uses','selectors','exclusions','output_constraints']:add('opaque-empty-field-with-nonempty-relation-'+n,lambda m,n=n:setfield(m,'r1',n,'empty'),I=True)
 add('normalized-target-without-canonical-D66-preservation-marker',lambda m:None,I=True)
 add('noncanonical-normalized-target-sibling-marker-unconstrained',lambda m:m['predicates']['SilentSiblingIdentityMerge'].append(['d2']),I=True)
 add('normalized-id-on-nontarget-Entity-unconstrained',lambda m:setfn(m,'normalizedIdValue',['raw'],'other'),I=True)
 add('field-name-constants-may-alias',lambda m:m['constants'].update(F_context_ref='consumer_refs'),I=True)
 add('extra-field-declaration-permitted',lambda m:m['predicates']['DeclaresField'].append(['r1','extra']),I=True)
 add('nontotal-requested-Context-function',lambda m:m['functions']['requestedContext'].pop(),error='nontotal-function')
 add('ill-sorted-requested-Context-function',lambda m:setfn(m,'requestedContext',['r1'],'spec'),error='ill-sorted-function-result')
 add('ill-sorted-field-constant',lambda m:m['constants'].update(F_owner_ref='absent'),error='ill-sorted-constant')
 add('wrong-selector-arity',lambda m:m['predicates'].update(Selector=[['r1']]),error='ill-sorted-model-tuple')
 add('duplicate-consumer-tuple',lambda m:m['predicates']['ConsumerRef'].append(['r1','u1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-requested-Context-function-tuple',lambda m:m['functions']['requestedContext'].append(copy.deepcopy(m['functions']['requestedContext'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.context-profile/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ContextRequest-model-controls/v1-candidate','status':'PASS-for-exact-authored-ContextRequest-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied Request inputs,normalized metadata and no mutation/effect inference. Inherited Context basis and actual record/value/precedence/resolution meaning remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
