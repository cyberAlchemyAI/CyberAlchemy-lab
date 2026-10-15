"""Independent Context anchor/cardinality and normative-versus-actual models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['cP','cJ','cG','cJ2','raw','p1','p2','j1','j2','g1','g2','u1','u2','b1','s1','v1','eStable','eChange'];contexts=['cP','cJ','cG','cJ2']
 domains={'Entity':entities,'Field':b.FIELDS+['extra'],'Kind':b.KINDS+['OTHER_KIND'],'Lifecycle':b.LIFECYCLES+['OTHER_STATE'],'Token':['empty','spec','identity','changed']}
 functions={'fieldValue':[{'args':[e,f],'value':'spec'} for e,f in itertools.product(entities,domains['Field'])],'normalizedIdValue':[{'args':[e],'value':'identity'} for e in entities],'contextKindValue':[{'args':[e],'value':{'cP':'PRODUCT','cJ':'PROJECT','cG':'GOAL','cJ2':'PROJECT'}.get(e,'OTHER_KIND')} for e in entities],'contextLifecycleValue':[{'args':[e],'value':'ACTIVE' if e in ['cJ','cG'] else 'DRAFT'} for e in entities]}
 p={n:[] for n in b.SIGNATURE};p.update(Context=[[x] for x in contexts],CanonicalInstance=[['cP']],PreservesExactD66Relation=[['cP']],RawDeclaredComplete=[['cP'],['raw']],ProductRole=[['p1'],['p2']],ProjectRole=[['j1'],['j2']],GoalRole=[['g1'],['g2']],ConsumerRole=[['u1'],['u2']],BoundedContextRole=[['b1']],ContextViewRole=[['v1']],ProductRef=[[x,'p1'] for x in contexts],ProjectRef=[['cJ','j1'],['cG','j1'],['cJ2','j1']],GoalRef=[['cG','g1']],GoalBelongsProject=[['g1','j1']],ConsumerRef=[[x,'u1'] for x in contexts]+[['cP','u2']],BoundedContextRef=[['cJ','b1']],SourceRelevant=[['cP','s1'],['cJ','s1']],CurrentViewFor=[['v1','cG']],ValidatorPassed=[['cJ']],DefinitionTermAdmitted=[['cP']],PreservingRefreshEvent=[['cP','eStable']],SameIdentityRequired=[['cP','eStable']],MaterialAnchorChange=[['cJ','eChange']],SuccessorContextRequired=[['cJ','eChange']],SupersedeEarlierRequired=[['cJ','eChange']],DeclaresField=[[e,f] for e,f in itertools.product(contexts+['raw'],b.FIELDS)])
 for n in b.QUALIFIERS+['NormalizedDefinitionKind','ContextResolutionScope','DefinitionCarrier']:p[n]=[[x] for x in contexts]
 constants={'EMPTY':'empty','CONTEXT_ID':'identity',**{'F_'+n:n for n in b.FIELDS},**{n:n for n in b.KINDS+b.LIFECYCLES}}
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':p}
def setfn(m,n,e,value):next(x for x in m['functions'][n] if x['args']==[e])['value']=value
def setfield(m,f,e,value):next(x for x in m['functions']['fieldValue'] if x['args']==[e,f])['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('four-qualified-Contexts-three-kinds-exact-anchors-and-normative-change-gaps',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independently-supplied-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['cP']))
 for n in ['SourceTrue','SourceCurrent','SourceAuthoritative','SourceAccepted','SourceExecutable']:add('independently-supplied-source-marker-'+n,lambda m,n=n:m['predicates'][n].append(['s1']))
 for n in b.QUALIFIERS:add('Context-missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['cP']),T=False)
 add('qualified-genus-reverse-iff-missing-Context',lambda m:m['predicates']['Context'].remove(['cJ2']),T=False)
 for n in ['NormalizedDefinitionKind','ContextResolutionScope','DefinitionCarrier']:add('Context-missing-normalized-axis-'+n,lambda m,n=n:m['predicates'][n].remove(['cP']),T=False)
 add('wrong-normalized-identity-value',lambda m:setfn(m,'normalizedIdValue','cP','changed'),T=False)
 add('canonical-source-preservation-missing',lambda m:m['predicates']['PreservesExactD66Relation'].remove(['cP']),T=False)
 add('canonical-silent-sibling-identity-merge',lambda m:m['predicates']['SilentSiblingIdentityMerge'].append(['cP']),T=False)
 for n in b.FIELDS:add('Context-missing-declared-field-'+n,lambda m,n=n:m['predicates']['DeclaresField'].remove(['cP',n]),T=False)
 for n in b.ROLES:add('Context-forbidden-role-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['cP']),T=False)
 add('no-Product-ref',lambda m:m['predicates']['ProductRef'].remove(['cP','p1']),T=False)
 add('two-distinct-Product-refs',lambda m:m['predicates']['ProductRef'].append(['cP','p2']),T=False)
 add('two-distinct-Project-refs',lambda m:m['predicates']['ProjectRef'].append(['cJ','j2']),T=False)
 add('two-distinct-Goal-refs',lambda m:m['predicates']['GoalRef'].append(['cG','g2']),T=False)
 add('product-kind-with-Project-ref',lambda m:m['predicates']['ProjectRef'].append(['cP','j1']),T=False)
 add('product-kind-with-Goal-ref',lambda m:m['predicates']['GoalRef'].append(['cP','g1']),T=False)
 add('project-kind-without-Project-ref',lambda m:m['predicates']['ProjectRef'].remove(['cJ','j1']),T=False)
 add('project-kind-with-Goal-ref',lambda m:m['predicates']['GoalRef'].append(['cJ','g1']),T=False)
 add('goal-kind-without-Project-ref',lambda m:m['predicates']['ProjectRef'].remove(['cG','j1']),T=False)
 add('goal-kind-without-Goal-ref',lambda m:m['predicates']['GoalRef'].remove(['cG','g1']),T=False)
 add('goal-not-belonging-to-selected-Project',lambda m:m['predicates']['GoalBelongsProject'].remove(['g1','j1']),T=False)
 add('goal-belongs-to-another-Project-not-selected-one',lambda m:m['predicates'].update(GoalBelongsProject=[['g1','j2']]),T=False)
 for rel,role,target in [('ProductRef','ProductRole','p1'),('ProjectRef','ProjectRole','j1'),('GoalRef','GoalRole','g1'),('ConsumerRef','ConsumerRole','u1'),('BoundedContextRef','BoundedContextRole','b1')]:add('reference-target-missing-role-'+role,lambda m,role=role,target=target:m['predicates'][role].remove([target]),T=False)
 add('Context-without-consumer',lambda m:m['predicates']['ConsumerRef'].remove(['cG','u1']),T=False)
 add('unknown-Context-kind',lambda m:setfn(m,'contextKindValue','cP','OTHER_KIND'),T=False)
 add('unknown-Context-lifecycle',lambda m:setfn(m,'contextLifecycleValue','cP','OTHER_STATE'),T=False)
 for life in b.LIFECYCLES:add('allowed-lifecycle-'+life,lambda m,life=life:setfn(m,'contextLifecycleValue','cJ2',life),I=True)
 add('kind-enum-tags-cannot-alias',lambda m:m['constants'].update(PROJECT='PRODUCT'),T=False)
 add('lifecycle-enum-tags-cannot-alias',lambda m:m['constants'].update(RETIRED='DRAFT'),T=False)
 add('stable-refresh-without-required-same-identity',lambda m:m['predicates']['SameIdentityRequired'].clear(),T=False)
 add('material-change-without-required-successor',lambda m:m['predicates']['SuccessorContextRequired'].clear(),T=False)
 add('material-change-without-required-supersession',lambda m:m['predicates']['SupersedeEarlierRequired'].clear(),T=False)
 add('normative-change-requirements-do-not-create-actual-successor',lambda m:None,I=True)
 add('separate-actual-successor-can-coexist-with-required-change',lambda m:m['predicates']['ActualSuccessorCreated'].append(['cJ','eChange']))
 add('separate-actual-supersession-can-coexist-with-required-change',lambda m:m['predicates']['ActualEarlierSuperseded'].append(['cJ','eChange']))
 add('separate-actual-stability-can-coexist-with-required-refresh',lambda m:m['predicates']['ActualIdentityStable'].append(['cP','eStable']))
 add('field-Tokens-may-be-empty-no-accepted-field-value-bridge',lambda m:setfield(m,'purpose','cP','empty'),I=True)
 add('owner-route-Token-not-authenticated-by-owner-qualified-marker',lambda m:setfield(m,'owner_route','cP','empty'),I=True)
 add('field-name-constants-can-alias-outside-explicit-tag-distinctness',lambda m:m['constants'].update(F_goal_ref='project_ref'),I=True)
 add('empty-BoundedContext-reference-set-permitted',lambda m:m['predicates']['BoundedContextRef'].clear(),I=True)
 add('additional-eligible-consumer-permitted',lambda m:m['predicates']['ConsumerRef'].append(['cG','u2']),I=True)
 add('extra-declared-field-permitted',lambda m:m['predicates']['DeclaresField'].append(['cP','extra']),I=True)
 add('source-relevance-not-source-truth-or-authority',lambda m:None,I=True)
 add('current-View-not-current-Context',lambda m:None,I=True)
 add('active-Context-not-active-Project-or-Goal',lambda m:None,I=True)
 add('passed-validator-not-consumer-understanding-or-use',lambda m:None,I=True)
 add('changed-purpose-not-computed-materiality-predicate',lambda m:setfield(m,'purpose','cJ','changed'),I=True)
 add('nontotal-kind-function',lambda m:m['functions']['contextKindValue'].pop(),error='nontotal-function')
 add('ill-sorted-kind-function-result',lambda m:setfn(m,'contextKindValue','cP','ACTIVE'),error='ill-sorted-function-result')
 add('ill-sorted-kind-constant',lambda m:m['constants'].update(PRODUCT='absent'),error='ill-sorted-constant')
 add('wrong-Product-ref-arity',lambda m:m['predicates'].update(ProductRef=[['cP']]),error='ill-sorted-model-tuple')
 add('duplicate-Product-ref-tuple',lambda m:m['predicates']['ProductRef'].append(['cP','p1']),error='duplicate-predicate-tuple')
 add('empty-Kind-domain',lambda m:m['domains'].update(Kind=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['contextKindValue'].append(copy.deepcopy(m['functions']['contextKindValue'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.contestability-policy/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Context-model-controls/v1-candidate','status':'PASS-for-exact-authored-Context-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied Context genus,cardinality/kind/reference-role and normative refresh/successor models. Actual reference resolution,field/materiality/owner/consumer maps and universal temporal identity preservation remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
