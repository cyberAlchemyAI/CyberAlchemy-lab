"""Independent reusable-policy/exact-version/no-payload/normative-revision controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['p1','p2','pn','c1','c2','raw'];profiles=['p1','p2','pn'];fields=b.FIELDS+['extra'];ver=lambda e:'v2' if e in ['p2','pn'] else 'v1';domains={'Entity':entities,'Field':fields,'Token':['empty','spec','v1','v2','product','other']}
 functions={'fieldValue':[{'args':[e,f],'value':ver(e) if f=='version' else 'spec'} for e,f in itertools.product(entities,fields)],'profileVersion':[{'args':[e],'value':ver(e)} for e in entities],'conformanceVersion':[{'args':[c,p],'value':ver(p)} for c,p in itertools.product(entities,entities)]}
 p={n:[] for n in b.SIGNATURE};p.update(ContextProfile=[[e] for e in profiles],DeclaresField=[[e,f] for e,f in itertools.product(profiles+['raw'],b.FIELDS)],Governed=[[e] for e in profiles],Bounded=[[e] for e in profiles],ContextInstanceRole=[['c1'],['c2']],PurposeSpecificRelevanceBoundary=[['c1'],['c2']],ClaimsConformance=[['c1','p1']],NamesExactProfileVersion=[['c1','p1']],GovernsContext=[['p1','c1'],['p1','c2']],RevisionOf=[['pn','p1']],RetainsPriorContextMeaningRequired=[['pn']],SuccessionExplicitRequired=[['pn']],RawDeclaredComplete=[['raw']],AllowedAnchorKind=[['p1','product']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in profiles]
 return {'domains':domains,'constants':{'EMPTY':'empty',**{'F_'+n:n for n in b.FIELDS}},'functions':functions,'predicates':p}
def setfield(m,e,f,value):next(x for x in m['functions']['fieldValue'] if x['args']==[e,f])['value']=value
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('reusable-profile-many-contexts-exact-conformance-and-revision',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['p1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['p1']),T=False)
 add('reverse-genus-iff-missing',lambda m:m['predicates']['ContextProfile'].remove(['p1']),T=False)
 for n in b.FIELDS:add('missing-field-'+n,lambda m,n=n:m['predicates']['DeclaresField'].remove(['p1',n]),T=False)
 for n in ['Governed','Bounded']:add('missing-formal-'+n,lambda m,n=n:m['predicates'][n].remove(['p1']),T=False)
 for n in b.ROLES:add('forbidden-Profile-role-'+n,lambda m,n=n:m['predicates'][n].append(['p1']),T=False)
 for n in b.PAYLOAD_FLAGS:add('forbidden-Profile-payload-'+n,lambda m,n=n:m['predicates'][n].append(['p1']),T=False)
 for n in b.INFER_FLAGS:add('forbidden-Profile-inference-'+n,lambda m,n=n:m['predicates'][n].append(['p1']),T=False)
 for n in ['version','owner','lifecycle','challenge_route']:add('empty-own-'+n,lambda m,n=n:setfield(m,'p1',n,'empty'),T=False)
 add('empty-profile-version',lambda m:setfn(m,'profileVersion',['p1'],'empty'),T=False)
 add('profile-version-and-own-field-disagree',lambda m:setfield(m,'p1','version','v2'),T=False)
 add('claiming-context-without-role',lambda m:m['predicates']['ContextInstanceRole'].remove(['c1']),T=False)
 add('claiming-untyped-Profile',lambda m:m['predicates']['ClaimsConformance'].append(['c1','raw']),T=False)
 add('claim-without-exact-version-name',lambda m:m['predicates']['NamesExactProfileVersion'].clear(),T=False)
 add('claim-names-other-version',lambda m:setfn(m,'conformanceVersion',['c1','p1'],'v2'),T=False)
 add('Context-claims-two-Profiles-candidate-single-Profile-scope',lambda m:(m['predicates']['ClaimsConformance'].append(['c1','p2']),m['predicates']['NamesExactProfileVersion'].append(['c1','p2'])),T=False)
 add('governed-Context-without-purpose-boundary',lambda m:m['predicates']['PurposeSpecificRelevanceBoundary'].remove(['c2']),T=False)
 add('governance-of-untyped-Context',lambda m:m['predicates']['GovernsContext'].append(['p1','raw']),T=False)
 add('revision-of-non-Profile',lambda m:m['predicates']['RevisionOf'].append(['pn','raw']),T=False)
 add('revision-from-non-Profile',lambda m:m['predicates']['RevisionOf'].append(['raw','p1']),T=False)
 for n in ['RetainsPriorContextMeaningRequired','SuccessionExplicitRequired']:add('missing-revision-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('revision-silently-reinterprets-old-governed-Context',lambda m:m['predicates']['SilentReinterpretation'].append(['pn','c2']),T=False)
 add('unused-Profile-without-governed-Contexts-permitted',lambda m:None,I=True)
 add('governed-Context-without-conformance-permitted',lambda m:None,I=True)
 add('Product-kind-policy-is-not-Product-anchor',lambda m:None,I=True)
 add('revision-with-same-version-not-forbidden-by-generic-norm',lambda m:(setfn(m,'profileVersion',['pn'],'v1'),setfield(m,'pn','version','v1')),I=True)
 add('unrelated-silent-reinterpretation-outside-declared-old-governance',lambda m:m['predicates']['SilentReinterpretation'].append(['pn','raw']),I=True)
 for n in ['allowed_anchor_kinds','cardinalities','identity_rules','source_constraints','freshness','exclusions','succession']:add('opaque-empty-policy-field-'+n,lambda m,n=n:setfield(m,'p1',n,'empty'),I=True)
 add('unresolved-owner-token-is-not-qualified-owner',lambda m:setfield(m,'p1','owner','other'),I=True)
 add('field-name-constants-may-alias',lambda m:m['constants'].update(F_cardinalities='identity_rules'),I=True)
 add('extra-field-declaration-permitted',lambda m:m['predicates']['DeclaresField'].append(['p1','extra']),I=True)
 add('nontotal-version-function',lambda m:m['functions']['profileVersion'].pop(),error='nontotal-function')
 add('ill-sorted-conformance-version-result',lambda m:setfn(m,'conformanceVersion',['c1','p1'],'p1'),error='ill-sorted-function-result')
 add('ill-sorted-field-constant',lambda m:m['constants'].update(F_owner='absent'),error='ill-sorted-constant')
 add('wrong-conformance-arity',lambda m:m['predicates'].update(ClaimsConformance=[['c1']]),error='ill-sorted-model-tuple')
 add('duplicate-governance-tuple',lambda m:m['predicates']['GovernsContext'].append(['p1','c1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-version-function-tuple',lambda m:m['functions']['profileVersion'].append(copy.deepcopy(m['functions']['profileVersion'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.context-migration-manifest/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ContextProfile-model-controls/v1-candidate','status':'PASS-for-exact-authored-ContextProfile-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied reusable policy,exact conformance versions and normative revision preservation. Actual record/cardinality/source/freshness/owner/resolution and history semantics pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
