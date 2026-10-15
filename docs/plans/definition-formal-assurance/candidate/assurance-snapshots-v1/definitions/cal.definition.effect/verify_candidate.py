"""Independent exact Effect kind/actor/scope and scoped stage/fact controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 effects=['eState','eRights','eObligations','eExternal','eInterpretation'];singlefacts=['fDeclared','fAuthorized','fAttempted','fDelivered','fObserved'];entities=effects+['kind1','subject1','scope1','decision','action','actorBoth']+singlefacts+['fAll','uExact','uSuccessor','scope2','aux'];tokens=['empty','selected','successor','kind-id','opaque','other'];domains={'Entity':entities,'Token':tokens}
 maps={'effectKind':lambda e:'kind1','effectSubject':lambda e:'subject1','effectScope':lambda e:'scope1','factEffect':lambda e:'eState','factScope':lambda e:'scope1','useEffect':lambda e:'eInterpretation' if e=='uSuccessor' else 'eState','useScope':lambda e:'scope1','kindIdentity':lambda e:'kind-id','useDefinition':lambda e:'successor' if e=='uSuccessor' else 'selected'}
 functions={n:[{'args':[e],'value':f(e)} for e in entities] for n,f in maps.items()};p={n:[] for n in b.SIGNATURE};p.update(Effect=[[e] for e in effects],EffectKindRole=[['kind1']],EffectSubjectRole=[['subject1']],ScopeRole=[['scope1'],['scope2']],GovernedIdentityRole=[['eState'],['eRights'],['eObligations']],GovernedRecordRole=[['eObligations'],['eExternal'],['eInterpretation']],DecisionRole=[['decision'],['actorBoth']],ActionRole=[['action'],['actorBoth']],EffectFactRole=[[f] for f in singlefacts+['fAll']],EffectUse=[['uExact'],['uSuccessor']],AdmittedSuccessorOf=[['successor','selected']],ActorIntends=[['decision','eState']],ActorAuthorizes=[['decision','eRights']],ActorRecords=[['decision','eObligations'],['actorBoth','eObligations']],ActorObserves=[['decision','eExternal'],['action','eInterpretation']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in effects]
 for n,e in zip(b.CATEGORIES,effects):p[n]=[[e]]
 for n,f in zip(b.STAGES,singlefacts):p[n]=[[f],['fAll']]
 return {'domains':domains,'constants':{'EMPTY':'empty','SELECTED_DEFINITION':'selected'},'functions':functions,'predicates':p}
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('five-effect-categories-source-actors-single-and-overlapping-stage-facts',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['eState']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['eState']),T=False)
 add('reverse-genus-effect-omitted',lambda m:m['predicates']['Effect'].remove(['eState']),T=False)
 add('effect-with-no-change-category',lambda m:m['predicates']['GovernedStateChange'].clear(),T=False)
 add('multiple-change-categories-allowed',lambda m:m['predicates']['RightsChange'].append(['eState']),I=True)
 for n in ['EffectKindRole','EffectSubjectRole','ScopeRole']:add('missing-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['effectKind','effectSubject','effectScope']:add('wrong-reference-'+n,lambda m,n=n:setfn(m,n,['eState'],'aux'),T=False)
 add('empty-kind-identity',lambda m:setfn(m,'kindIdentity',['kind1'],'empty'),T=False)
 add('opaque-kind-identity-token',lambda m:setfn(m,'kindIdentity',['kind1'],'opaque'),I=True)
 add('two-kind-entities-same-identity-no-registry-uniqueness-claim',lambda m:(m['predicates']['EffectKindRole'].append(['aux']),setfn(m,'effectKind',['eRights'],'aux')),I=True)
 add('neither-governed-identity-nor-record',lambda m:m['predicates']['GovernedRecordRole'].remove(['eExternal']),T=False)
 add('both-governed-identity-and-record-allowed',lambda m:None,I=True)
 for n in ['DecisionRole','ActionRole']:add('missing-actor-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in b.LINK_NAMES:
  add('link-from-nonactor-'+n,lambda m,n=n:m['predicates'][n].append(['aux','eState']),T=False)
  add('link-to-noneffect-'+n,lambda m,n=n:m['predicates'][n].append(['decision','aux']),T=False)
 add('effect-without-source-actor-link',lambda m:m['predicates']['ActorIntends'].clear(),T=False)
 add('wrong-actor-link-direction',lambda m:m['predicates']['ActorIntends'].append(['eState','decision']),T=False)
 add('decision-or-action-inclusive-overlap-allowed',lambda m:None,I=True)
 add('type-level-Decision-neighbor-noncollapse-not-imported-as-role-exclusion',lambda m:m['predicates']['DecisionRole'].append(['eState']),I=True)
 add('fact-for-noneffect',lambda m:setfn(m,'factEffect',['fDeclared'],'aux'),T=False)
 add('fact-scope-mismatch-two-valid-scopes',lambda m:setfn(m,'factScope',['fDeclared'],'scope2'),T=False)
 add('fact-scope-without-role',lambda m:setfn(m,'factScope',['fDeclared'],'aux'),T=False)
 for n in b.STAGES:
  add('stage-without-fact-role-'+n,lambda m,n=n:m['predicates'][n].append(['aux']),T=False)
  add('remove-single-stage-witness-'+n,lambda m,n=n:m['predicates'][n].remove(m['predicates'][n][0]),I=False)
 add('missing-declared-fact-role',lambda m:m['predicates']['EffectFactRole'].remove(['fDeclared']),T=False)
 add('no-overlap-witness-required-by-universal-theory',lambda m:m['predicates']['StageDeclared'].remove(['fAll']),I=False)
 add('additional-fact-with-no-stage-label-allowed',lambda m:m['predicates']['EffectFactRole'].append(['aux']),I=True)
 add('authorization-marker-does-not-prove-delivery',lambda m:None,I=True)
 add('all-stage-labels-may-coexist-no-exclusion-assumed',lambda m:None,I=True)
 add('use-of-noneffect',lambda m:setfn(m,'useEffect',['uExact'],'aux'),T=False)
 add('use-definition-neither-exact-nor-declared-successor',lambda m:setfn(m,'useDefinition',['uExact'],'other'),T=False)
 add('successor-marker-missing',lambda m:m['predicates']['AdmittedSuccessorOf'].clear(),T=False)
 add('successor-direction-reversed',lambda m:m['predicates'].update(AdmittedSuccessorOf=[['selected','successor']]),T=False)
 add('use-scope-mismatch',lambda m:setfn(m,'useScope',['uExact'],'scope2'),T=False)
 add('use-scope-without-role',lambda m:setfn(m,'useScope',['uExact'],'aux'),T=False)
 for n in b.INFER_FLAGS:
  for e,label in [('eState','effect'),('fDeclared','fact'),('uExact','use')]:add(label+'-forbidden-inference-'+n,lambda m,n=n,e=e:m['predicates'][n].append([e]),T=False)
 add('no-uses-required-by-universal-theory',lambda m:m['predicates']['EffectUse'].clear(),I=False)
 add('all-uses-exact-removes-successor-population',lambda m:setfn(m,'useDefinition',['uSuccessor'],'selected'),I=False)
 add('all-uses-successor-removes-exact-population',lambda m:setfn(m,'useDefinition',['uExact'],'successor'),I=False)
 add('nontotal-effect-kind-function',lambda m:m['functions']['effectKind'].pop(),error='nontotal-function')
 add('ill-sorted-kind-identity-result',lambda m:setfn(m,'kindIdentity',['kind1'],'kind1'),error='ill-sorted-function-result')
 add('ill-sorted-selected-definition-constant',lambda m:m['constants'].update(SELECTED_DEFINITION='absent'),error='ill-sorted-constant')
 add('wrong-actor-link-arity',lambda m:m['predicates'].update(ActorIntends=[['decision']]),error='ill-sorted-model-tuple')
 add('duplicate-effect-tuple',lambda m:m['predicates']['Effect'].append(['eState']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-fact-function-tuple',lambda m:m['functions']['factEffect'].append(copy.deepcopy(m['functions']['factEffect'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.contract/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Effect-model-controls/v1-candidate','status':'PASS-for-exact-authored-Effect-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent declared Effect kind/subject/actor/scope and scoped stage facts;actual authorization,delivery,observation,trace,owner and consumer/source-owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
