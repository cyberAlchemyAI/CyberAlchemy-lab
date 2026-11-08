"""Supplied exact Source/material/reference/integrity/provenance and version-use models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 domains={s:[s.lower()+'A',s.lower()+'Outside'] for s in b.SORTS};domains.update(Source=['s0','s1','sOutside'],Material=['m0','m1','mOutside'],OriginReference=['ref0','ref1','refOutside'],SourceUse=['uCurrent','uSuccessor','uOutside'],DefinitionVersion=['current','successor','unresolved'],Token=['empty','reference','extra'])
 constants={'EMPTY':'empty','CURRENT_VERSION':'current'};maps={}
 for n,sort in b.FIELDS.items():maps[n]=lambda s,sort=sort:domains[sort][-1] if s=='sOutside' else domains[sort][0]
 maps['sourceReference']=lambda s:{'s0':'ref0','s1':'ref1','sOutside':'refOutside'}[s]
 maps.update(useSource=lambda u:'sOutside' if u=='uOutside' else 's0',useVersion=lambda u:{'uCurrent':'current','uSuccessor':'successor','uOutside':'unresolved'}[u],useScope=lambda u:'sourcescopeOutside' if u=='uOutside' else 'sourcescopeA')
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['SourceApplicable','SourceInScopeDeclared','ExactOriginDeclared','ProvenanceBearingDeclared','GovernedIdentityOrRecordDeclared','BoundedScopeDeclared']:predicates[n]=[['s0'],['s1']]
 for n,sort in b.FIELDS.items():predicates[sort+'Declared']=[[x] for x in dict.fromkeys(maps[n](s) for s in ['s0','s1'])]
 predicates.update(ReferenceResolvableDeclared=[['ref0'],['ref1']],MaterialDeclared=[['m0'],['m1']],SourceObtainedMaterialDeclared=[['s0','m0'],['s0','m1'],['s1','m1']],MaterialAsContent=[['m0']],MaterialAsEvidence=[['m0']],MaterialAsData=[['m1']],MaterialAsClaim=[['m1']],DefinitionVersionDeclared=[['current'],['successor']],AdmittedSuccessorVersionDeclared=[['successor']])
 for n in ['SourceUseApplicable','UseInScopeDeclared','UseWithinApplicabilityAndExclusionsDeclared']:predicates[n]=[['uCurrent'],['uSuccessor']]
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('exact-origin-inclusive-material-roles-and-current-successor-uses',lambda m:None,I=True)
 for n in b.ACTUAL:add('independent-Source-actual-'+n,lambda m,n=n:m['predicates']['SourceActual'+n].append(['s1']),I=True)
 for n in b.USE_ACTUAL:add('independent-Use-actual-'+n,lambda m,n=n:m['predicates']['UseActual'+n].append(['uCurrent']),I=False)
 add('outside-Source-empty-handle',lambda m:setfn(m,'sourceHandle','sOutside','empty'),I=True)
 add('outside-reference-need-not-be-declared-resolvable',lambda m:setfn(m,'originReferenceHandle','refOutside','empty'),I=True)
 add('outside-material-can-lack-all-four-role-flags',lambda m:m['predicates']['SourceObtainedMaterialDeclared'].append(['sOutside','mOutside']),I=True)
 add('outside-material-empty-handle',lambda m:setfn(m,'materialHandle','mOutside','empty'),I=True)
 add('outside-use-can-have-unresolved-empty-version',lambda m:setfn(m,'definitionVersionHandle','unresolved','empty'),I=True)
 add('same-material-can-be-obtained-from-multiple-Sources',lambda m:m['predicates']['SourceObtainedMaterialDeclared'].append(['s1','m0']),I=True)
 add('distinct-source-records-can-reference-same-origin-reference',lambda m:setfn(m,'sourceReference','s1','ref0'),I=True)
 for n in b.ROLES:add('one-inclusive-role-can-be-absent-'+n,lambda m,n=n:m['predicates']['MaterialAs'+n].clear(),I=False)
 for n in ['SourceInScopeDeclared','ExactOriginDeclared','ProvenanceBearingDeclared','GovernedIdentityOrRecordDeclared','BoundedScopeDeclared']:add('missing-Source-'+n,lambda m,n=n:m['predicates'][n].remove(['s0']),T=False)
 add('Source-declared-scope-without-membership',lambda m:m['predicates']['SourceApplicable'].remove(['s0']),T=False)
 for sort in b.FIELDS.values():add('missing-declared-component-'+sort,lambda m,sort=sort:m['predicates'][sort+'Declared'].clear(),T=False)
 add('selected-reference-without-resolvable-declaration',lambda m:m['predicates']['ReferenceResolvableDeclared'].remove(['ref0']),T=False)
 add('selected-Source-without-any-obtained-material',lambda m:m['predicates'].update(SourceObtainedMaterialDeclared=[['s1','m1']]),T=False)
 add('obtained-material-without-declaration',lambda m:m['predicates']['MaterialDeclared'].remove(['m0']),T=False)
 def no_role(m):
  for n in ['Content','Evidence']:m['predicates']['MaterialAs'+n].clear()
 add('selected-obtained-material-without-any-listed-role',no_role,T=False)
 for sort,arg in [('Source','s0'),('Material','m0'),('OriginReference','ref0'),('IntegrityBoundary','integrityboundaryA'),('ProvenanceReference','provenancereferenceA'),('SourceScope','sourcescopeA'),('Context','contextA'),('SourceUse','uCurrent'),('DefinitionVersion','current')]:add('empty-selected-'+sort+'-handle',lambda m,sort=sort,arg=arg:setfn(m,b.HANDLES[sort],arg,'empty'),T=False)
 for n in ['UseInScopeDeclared','UseWithinApplicabilityAndExclusionsDeclared']:add('missing-use-'+n,lambda m,n=n:m['predicates'][n].remove(['uCurrent']),T=False)
 add('use-declared-scope-without-membership',lambda m:m['predicates']['SourceUseApplicable'].remove(['uCurrent']),T=False)
 add('use-binds-outside-Source',lambda m:setfn(m,'useSource','uCurrent','sOutside'),T=False)
 add('use-version-without-declaration',lambda m:m['predicates']['DefinitionVersionDeclared'].remove(['current']),T=False)
 add('successor-without-admission-declaration',lambda m:m['predicates']['AdmittedSuccessorVersionDeclared'].clear(),T=False)
 add('use-version-neither-current-nor-successor',lambda m:setfn(m,'useVersion','uCurrent','unresolved'),T=False)
 add('use-scope-does-not-match-Source-scope',lambda m:setfn(m,'useScope','uCurrent','sourcescopeOutside'),T=False)
 add('missing-symbol',lambda m:m['predicates'].pop('SourceApplicable'),error='model-signature-denominator-mismatch')
 add('partial-total-function',lambda m:m['functions']['sourceReference'].pop(),error='nontotal-function')
 add('ill-sorted-constant',lambda m:m['constants'].update(EMPTY='s0'),error='ill-sorted-constant')
 add('wrong-obtained-material-arity',lambda m:m['predicates'].update(SourceObtainedMaterialDeclared=[['s0']]),error='ill-sorted-model-tuple')
 add('duplicate-Source-tuple',lambda m:m['predicates']['SourceApplicable'].append(['s0']),error='duplicate-predicate-tuple')
 add('empty-Material-domain',lambda m:m['domains'].update(Material=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['sourceReference'].append(copy.deepcopy(m['functions']['sourceReference'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.review/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Source-model-controls/v1-candidate','status':'PASS-for-exact-authored-Source-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed exact Source origins,obtained material,inclusive roles,declared reference/integrity/provenance and current/successor use guards checked on supplied models. Actual resolution,authenticity,integrity,truth,currentness,completeness,authority,admissibility,license,owner acceptance and consumer maps remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
