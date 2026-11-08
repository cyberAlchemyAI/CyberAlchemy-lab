"""Independent canonical Map/Relationship closure and abstract reverse-index finite controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['m1','m2','r1','r2','c1','c2','c3','raw','i1'];maps=['m1','m2'];relations=['r1','r2'];fields=b.FIELDS+['extra'];domains={'Entity':entities,'Field':fields,'Token':['empty','spec','id1','id2','other']}
 functions={'fieldValue':[{'args':[e,f],'value':'spec'} for e,f in itertools.product(entities,fields)],'mapIdValue':[{'args':[e],'value':'id1' if e=='m1' else 'id2'} for e in entities],'sourceEndpoint':[{'args':[e],'value':'c2' if e=='r2' else 'c1'} for e in entities],'targetEndpoint':[{'args':[e],'value':'c2'} for e in entities]}
 p={n:[] for n in b.SIGNATURE};p.update(ContextMap=[[e] for e in maps],Relationship=[[e] for e in relations],BoundedContextEndpoint=[['c1'],['c2'],['c3']],DeclaresField=[[e,f] for e,f in itertools.product(maps+['raw'],b.MAP_FIELDS)]+[[e,f] for e,f in itertools.product(relations,b.REL_FIELDS)],Member=[['m1','c1'],['m1','c2'],['m1','c3']],ContainsRelationship=[['m1','r1'],['m1','r2']],CanonicalMembershipOwner=[[e,e] for e in maps],CanonicalRelationshipsOwner=[[e,e] for e in maps],ReverseIndexContains=[['c1','id1'],['c2','id1'],['c3','id1']],EndpointBackreference=[['c3','m2']],ReverseIndexDisposable=[[e] for e in maps],DeterministicRebuildRequired=[[e] for e in maps],GeneratedIndex=[['i1']],RawDeclaredComplete=[['m1'],['raw']],Proximity=[['c1','c3']],ImportLink=[['c1','c3']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in maps]
 for n in b.REL_QUALIFIERS:p[n]=[[e] for e in relations]
 return {'domains':domains,'constants':{'EMPTY':'empty',**{'F_'+n:n for n in b.FIELDS}},'functions':functions,'predicates':p}
def setfield(m,e,f,value):next(x for x in m['functions']['fieldValue'] if x['args']==[e,f])['value']=value
def setfn(m,n,e,value):next(x for x in m['functions'][n] if x['args']==[e])['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('two-canonical-Maps-typed-closed-relations-and-abstract-reverse-index',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['m1']))
 add('independent-actual-relationship',lambda m:m['predicates']['ActualRelationship'].append(['c1','c3']))
 for n in b.QUALIFIERS:add('Map-missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['m1']),T=False)
 add('Map-reverse-genus-iff-missing',lambda m:m['predicates']['ContextMap'].remove(['m1']),T=False)
 for n in b.MAP_FIELDS:add('Map-missing-field-'+n,lambda m,n=n:m['predicates']['DeclaresField'].remove(['m1',n]),T=False)
 for n in b.REL_FIELDS:add('Relationship-missing-field-'+n,lambda m,n=n:m['predicates']['DeclaresField'].remove(['r1',n]),T=False)
 for n in b.REL_QUALIFIERS:add('Relationship-missing-qualifier-'+n,lambda m,n=n:m['predicates'][n].remove(['r1']),T=False)
 for n in ['direction','relationship_kind','information_boundary','authority_boundary','owners']:add('Relationship-empty-required-'+n,lambda m,n=n:setfield(m,'r1',n,'empty'),T=False)
 add('map-contains-untyped-relationship',lambda m:m['predicates']['ContainsRelationship'].append(['m1','raw']),T=False)
 add('map-has-untyped-endpoint',lambda m:m['predicates']['Member'].append(['m1','raw']),T=False)
 add('source-endpoint-not-in-same-map',lambda m:m['predicates']['ContainsRelationship'].append(['m2','r1']),T=False)
 add('source-function-target-not-BoundedContext',lambda m:setfn(m,'sourceEndpoint','r1','raw'),T=False)
 add('target-function-target-not-BoundedContext',lambda m:setfn(m,'targetEndpoint','r1','raw'),T=False)
 for n in ['CanonicalMembershipOwner','CanonicalRelationshipsOwner']:
  add('missing-self-canonical-owner-'+n,lambda m,n=n:m['predicates'][n].remove(['m1','m1']),T=False)
  add('second-canonical-owner-'+n,lambda m,n=n:m['predicates'][n].append(['m1','raw']),T=False)
 add('missing-reverse-hit',lambda m:m['predicates']['ReverseIndexContains'].remove(['c1','id1']),T=False)
 add('invented-reverse-hit',lambda m:m['predicates']['ReverseIndexContains'].append(['c1','id2']),T=False)
 add('canonical-endpoint-backreference-forbidden',lambda m:m['predicates']['CanonicalEndpointBackreference'].append(['c1']),T=False)
 for n in ['BackreferenceEstablishes','BackreferenceAmends','BackreferenceRevokes']:add('backreference-forbidden-effect-'+n,lambda m,n=n:m['predicates'][n].append(['c3','m2']),T=False)
 add('index-overrides-canonical-membership',lambda m:m['predicates']['IndexOverridesCanonicalMembership'].append(['i1']),T=False)
 for n in ['ReverseIndexDisposable','DeterministicRebuildRequired']:add('missing-regeneration-requirement-'+n,lambda m,n=n:m['predicates'][n].remove(['m1']),T=False)
 for n in b.ROLES:add('map-forbidden-role-'+n,lambda m,n=n:m['predicates'][n].append(['m1']),T=False)
 add('empty-map-permitted-by-generic-candidate',lambda m:None,I=True)
 add('unused-declared-endpoint-permitted',lambda m:None,I=True)
 add('reflexive-relationship-permitted-by-generic-candidate',lambda m:None,I=True)
 add('owner-approved-marker-with-empty-owner-Token',lambda m:setfield(m,'m1','owner_refs','empty'),I=True)
 for n in ['version','evidence_refs','lifecycle','drift_route']:add('map-opaque-empty-'+n,lambda m,n=n:setfield(m,'m1',n,'empty'),I=True)
 for n in ['contract_refs','translation_refs']:add('relationship-declared-empty-'+n,lambda m,n=n:setfield(m,'r1',n,'empty'),I=True)
 add('direction-opaque-other-Token-no-closed-taxonomy',lambda m:setfield(m,'r1','direction','other'),I=True)
 add('map-ids-may-alias-no-accepted-identity-bridge',lambda m:setfn(m,'mapIdValue','m2','id1'),I=True)
 add('field-name-constants-may-alias',lambda m:m['constants'].update(F_version='lifecycle'),I=True)
 add('extra-field-declaration-permitted',lambda m:m['predicates']['DeclaresField'].append(['m1','extra']),I=True)
 add('nontotal-map-id-function',lambda m:m['functions']['mapIdValue'].pop(),error='nontotal-function')
 add('ill-sorted-endpoint-function',lambda m:setfn(m,'sourceEndpoint','r1','spec'),error='ill-sorted-function-result')
 add('ill-sorted-field-constant',lambda m:m['constants'].update(F_id='absent'),error='ill-sorted-constant')
 add('wrong-member-arity',lambda m:m['predicates'].update(Member=[['m1']]),error='ill-sorted-model-tuple')
 add('duplicate-reverse-hit',lambda m:m['predicates']['ReverseIndexContains'].append(['c1','id1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-endpoint-function-tuple',lambda m:m['functions']['sourceEndpoint'].append(copy.deepcopy(m['functions']['sourceEndpoint'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.context-lineage-record/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ContextMap-model-controls/v1-candidate','status':'PASS-for-exact-authored-ContextMap-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied Map/Relationship canonical ownership,endpoint closure,abstract reverse lookup and normative-regeneration structures. Actual endpoint/owner/value/index maps and universal rebuild proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
