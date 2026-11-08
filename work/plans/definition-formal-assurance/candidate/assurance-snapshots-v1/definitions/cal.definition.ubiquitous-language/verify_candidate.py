"""Independent supplied context-language disposition,ambiguity,map and spelling/meaning controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['l1','l2','c1','c2','m1','m2','o','e1','e2','e3','b1','d1','bridge','aux','h1','other'];domains={'Entity':entities,'Token':['empty','id1','id2','rev','version','decision','pending','current','*']}
 values={'languageContext':'c1','languageModel':'m1','modelContext':'c1','bindingLanguage':'l1','bindingContext':'c1','bindingExpression':'e1','bindingDisposition':'d1','dispositionContext':'c1','dispositionConcept':'aux','expressionContext':'c1','ambiguityExpression':'e2','bridgeSourceContext':'c2','bridgeTargetContext':'c1','languageId':'id1','languageRevision':'rev','languageContextVersion':'version','bindingContextVersion':'version','expressionLabel':'pending','dispositionState':'current'}
 maps={n:lambda e,value=value:value for n,value in values.items()};maps.update(languageContext=lambda e:'c2' if e=='l2' else 'c1',languageModel=lambda e:'m2' if e=='l2' else 'm1',modelContext=lambda e:'c2' if e=='m2' else 'c1',languageId=lambda e:'id2' if e=='l2' else 'id1',expressionContext=lambda e:'c2' if e=='e3' else 'c1',expressionLabel=lambda e:'decision' if e in ['e1','e3'] else 'pending')
 functions={n:[{'args':[e],'value':f(e)} for e in entities] for n,f in maps.items()};p={n:[] for n in b.SIGNATURE};p.update(UbiquitousLanguage=[['l1'],['l2']],BoundedContextRole=[['c1'],['c2']],ContextModelRole=[['m1'],['m2']],OwnerRole=[['o']],OwnsLanguage=[['o','l1'],['o','l2']],BelongsToContext=[['l1','c1'],['l2','c2']],LanguageExpression=[['l1','e1'],['l1','e2'],['l2','e3']],ExpressionRole=[['e1'],['e2'],['e3']],ConceptRole=[['aux']],ConceptDispositionRole=[['d1']],CurrentBinding=[['b1']],LoadBearing=[['e1'],['e2'],['e3']],ExplicitUnresolved=[['l1','e2'],['l2','e3']],AmbiguousExpression=[['l1','e2']],ExplicitBridgeRole=[['bridge']],CrossContextReuse=[['l1','e3']],MappedPair=[['bridge','e3','e1']],HumanViewRole=[['h1']],GeneratedHumanView=[['h1','l1']])
 for n in b.QUALIFIERS:p[n]=[['l1'],['l2']]
 for n,role in b.MEMBER_ROLES.items():p[n]=[['l1','aux']];p[role]=[['aux']]
 for e in ['e1','e2','e3']:
  for f in ['e1','e2','e3']:
   if maps['expressionLabel'](e)==maps['expressionLabel'](f):p['SharedSpelling'].append([e,f])
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('context-owned-system-with-current-unresolved-ambiguity-and-map',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['l1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['l1']),T=False)
 add('reverse-genus-missing-language',lambda m:m['predicates']['UbiquitousLanguage'].remove(['l1']),T=False)
 for n in ['BoundedContextRole','ContextModelRole','OwnerRole','OwnsLanguage']:add('missing-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['languageId','languageRevision','languageContextVersion']:add('empty-'+n,lambda m,n=n:setfn(m,n,['l1'],'empty'),T=False)
 add('model-context-mismatch',lambda m:setfn(m,'modelContext',['m1'],'c2'),T=False)
 add('language-belongs-to-two-contexts',lambda m:m['predicates']['BelongsToContext'].append(['l1','c2']),T=False)
 add('missing-exact-context-relation',lambda m:m['predicates']['BelongsToContext'].remove(['l1','c1']),T=False)
 add('current-binding-language-not-a-language',lambda m:setfn(m,'bindingLanguage',['b1'],'other'),T=False)
 for n,val in [('bindingContext','c2'),('bindingContextVersion','*'),('bindingExpression','other'),('bindingDisposition','other'),('dispositionContext','c2'),('dispositionConcept','other'),('dispositionState','empty')]:
  add('bad-current-binding-'+n,lambda m,n=n,val=val:setfn(m,n,['d1' if n.startswith('disposition') else 'b1'],val),T=False)
 add('missing-current-disposition-role',lambda m:m['predicates']['ConceptDispositionRole'].clear(),T=False)
 add('missing-current-concept-role',lambda m:m['predicates']['ConceptRole'].clear(),T=False)
 add('load-bearing-neither-current-nor-unresolved',lambda m:m['predicates']['ExplicitUnresolved'].remove(['l1','e2']),T=False)
 add('load-bearing-current-and-unresolved',lambda m:m['predicates']['ExplicitUnresolved'].append(['l1','e1']),T=False)
 def conflicting(m):
  m['predicates']['CurrentBinding'].append(['other']);m['predicates']['ConceptDispositionRole'].append(['h1']);setfn(m,'bindingDisposition',['other'],'h1')
 add('two-current-dispositions-for-one-expression',conflicting,T=False)
 add('multiple-binding-records-same-disposition-allowed',lambda m:m['predicates']['CurrentBinding'].append(['other']),I=True)
 for n,role in b.MEMBER_ROLES.items():add('missing-member-role-'+role,lambda m,role=role:m['predicates'][role].clear(),T=False)
 add('missing-expression-role',lambda m:m['predicates']['ExpressionRole'].clear(),T=False)
 add('local-expression-context-mismatch',lambda m:setfn(m,'expressionContext',['e2'],'c2'),T=False)
 add('empty-expression-label',lambda m:setfn(m,'expressionLabel',['e2'],'empty'),T=False)
 add('ambiguity-without-record',lambda m:m['predicates']['LanguageAmbiguityRecord'].clear(),T=False)
 add('ambiguity-record-wrong-expression',lambda m:setfn(m,'ambiguityExpression',['aux'],'e1'),T=False)
 add('ambiguity-about-nonmember-expression',lambda m:m['predicates']['AmbiguousExpression'].append(['l1','e3']),T=False)
 add('mapped-reuse-without-bridge-role',lambda m:m['predicates']['ExplicitBridgeRole'].clear(),T=False)
 add('mapped-reuse-without-explicit-pair',lambda m:m['predicates']['MappedPair'].clear(),T=False)
 for n in ['bridgeSourceContext','bridgeTargetContext']:add('wrong-map-endpoint-'+n,lambda m,n=n:setfn(m,n,['bridge'],'other'),T=False)
 add('cross-context-reuse-declared-as-local-context',lambda m:m['predicates']['CrossContextReuse'].append(['l1','e2']),T=False)
 add('reuse-without-local-target-expression',lambda m:(m['predicates']['LanguageExpression'].remove(['l1','e1']),m['predicates']['CurrentBinding'].clear()),T=False)
 add('unmapped-cross-context-meaning-equivalence',lambda m:m['predicates']['MeaningEquivalent'].append(['e1','e3']),T=False)
 add('mapped-cross-context-meaning-equivalence-allowed',lambda m:m['predicates']['MeaningEquivalent'].append(['e3','e1']),I=True)
 add('same-context-meaning-equivalence-does-not-require-bridge',lambda m:m['predicates']['MeaningEquivalent'].append(['e1','e2']),I=True)
 add('missing-shared-spelling-for-equal-label',lambda m:m['predicates']['SharedSpelling'].remove(['e1','e3']),T=False)
 add('shared-spelling-for-distinct-labels',lambda m:m['predicates']['SharedSpelling'].append(['e1','e2']),T=False)
 add('shared-spelling-for-nonexpression',lambda m:m['predicates']['SharedSpelling'].append(['other','other']),T=False)
 for n in b.FORBIDDEN:add('forbidden-language-role-'+n,lambda m,n=n:m['predicates'][n].append(['l1']),T=False)
 add('human-view-is-independent-meaning-source',lambda m:m['predicates']['IndependentMeaningSource'].append(['h1']),T=False)
 add('human-view-without-view-role',lambda m:m['predicates']['HumanViewRole'].clear(),T=False)
 add('language-is-its-human-view',lambda m:(m['predicates']['GeneratedHumanView'].append(['l1','l1']),m['predicates']['HumanViewRole'].append(['l1'])),T=False)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['l1']),T=False)
 add('recorded-ambiguity-can-retain-resolved-expression',lambda m:(m['predicates']['AmbiguousExpression'].clear(),m['predicates']['AmbiguousExpression'].append(['l1','e1']),setfn(m,'ambiguityExpression',['aux'],'e1')),I=True)
 add('currentness-is-marker-not-time-proof',lambda m:[setfn(m,n,[e],'*') for n in ['languageRevision','languageContextVersion','bindingContextVersion','dispositionState'] for e in m['domains']['Entity']],I=True)
 add('explicit-map-does-not-assert-equivalent-meaning',lambda m:None,I=True)
 add('no-cross-context-use-required-by-universal-theory',lambda m:m['predicates']['CrossContextReuse'].clear(),I=False)
 add('no-ambiguity-required-by-universal-theory',lambda m:m['predicates']['AmbiguousExpression'].clear(),I=False)
 add('no-human-view-required-by-universal-theory',lambda m:m['predicates']['GeneratedHumanView'].clear(),I=False)
 add('empty-expression-set-without-current-bindings-allowed-by-theory',lambda m:(m['predicates']['LanguageExpression'].clear(),m['predicates']['CurrentBinding'].clear(),m['predicates']['AmbiguousExpression'].clear(),m['predicates']['CrossContextReuse'].clear()),I=False)
 add('no-selected-load-bearing-expressions-allowed-by-theory',lambda m:m['predicates']['LoadBearing'].clear(),I=False)
 add('nontotal-binding-disposition-function',lambda m:m['functions']['bindingDisposition'].pop(),error='nontotal-function')
 add('ill-sorted-language-id-result',lambda m:setfn(m,'languageId',['l1'],'l1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-mapped-pair-arity',lambda m:m['predicates'].update(MappedPair=[['bridge','e1']]),error='ill-sorted-model-tuple')
 add('duplicate-current-binding-tuple',lambda m:m['predicates']['CurrentBinding'].append(['b1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-context-function-tuple',lambda m:m['functions']['languageContext'].append(copy.deepcopy(m['functions']['languageContext'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.ontology-view/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-UbiquitousLanguage-model-controls/v1-candidate','status':'PASS-for-exact-authored-UbiquitousLanguage-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent typed context-owned language,unique current concept disposition or explicit unresolved expression,recorded ambiguities and explicit endpoint maps with separate spelling/meaning/human-view/authority guards. Actual concept/owner/currentness/consumer/source-owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
