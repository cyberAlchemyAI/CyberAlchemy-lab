"""Independent finite canonical configuration,stable successor identity and non-collapse models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['h1','h2','o1','d1','w1','sm1','rg1','rt1','rt2','ch1','p1','pr1','s1','u1','other'];manifests=['h1','h2'];domains={'Entity':entities,'Token':['empty','identity','other','*']}
 maps={'manifestOntology':lambda e:'o1','manifestDefinition':lambda e:'d1','manifestOwner':lambda e:'w1','manifestStateModel':lambda e:'sm1','manifestRelationRegistry':lambda e:'rg1','manifestRuntime':lambda e:'rt2' if e=='h2' else 'rt1','manifestChallengeRoute':lambda e:'ch1','manifestIdentity':lambda e:'identity'}
 functions={n:[{'args':[e],'value':fn(e)} for e in entities] for n,fn in maps.items()};p={n:[] for n in b.SIGNATURE}
 p.update(OntologyManifest=[[e] for e in manifests],GovernedIdentityOrRecord=[[e] for e in manifests],BoundedScope=[[e] for e in manifests],OntologyRole=[['o1']],DefinitionRole=[['d1']],OwnerRole=[['w1']],StateModelRole=[['sm1']],RelationRegistryRole=[['rg1']],RuntimeRole=[['rt1'],['rt2']],ChallengeRouteRole=[['ch1']],PolicyRole=[['p1']],ProjectionRole=[['pr1']],BoundPolicy=[[h,'p1'] for h in manifests],BoundProjection=[[h,'pr1'] for h in manifests],OntologyRepresents=[['o1','s1']],StableIdentityRevision=[['h1','h2']],ConsumerRole=[['u1']],ConsumerUse=[['h1','u1']],UseInApplicability=[['h1','u1']],CurrentManifest=[['h1']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in manifests]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('canonical-configured-Manifest-and-stable-identity-successor',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['h1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['h1']),T=False)
 add('reverse-genus-missing-Manifest',lambda m:m['predicates']['OntologyManifest'].remove(['h1']),T=False)
 for n in ['GovernedIdentityOrRecord','BoundedScope']:add('missing-'+n,lambda m,n=n:m['predicates'][n].remove(['h1']),T=False)
 add('empty-manifest-identity',lambda m:setfn(m,'manifestIdentity',['h1'],'empty'),T=False)
 add('Manifest-is-own-Ontology',lambda m:setfn(m,'manifestOntology',['h1'],'h1'),T=False)
 for field,role in b.FIELD_ROLES.items():add('missing-binding-role-'+field,lambda m,field=field,role=role:m['predicates'][role].clear(),T=False)
 for field in b.FIELD_ROLES:add('binding-to-untyped-reference-'+field,lambda m,field=field:setfn(m,field,['h1'],'other'),T=False)
 for n,e in [('BoundPolicy','p1'),('BoundProjection','pr1')]:add('empty-required-'+n,lambda m,n=n,e=e:m['predicates'][n].remove(['h1',e]),T=False)
 for n in ['PolicyRole','ProjectionRole']:add('bound-collection-without-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('stable-successor-not-Manifest',lambda m:m['predicates']['StableIdentityRevision'].append(['h1','other']),T=False)
 add('stable-successor-changes-identity',lambda m:setfn(m,'manifestIdentity',['h2'],'other'),T=False)
 add('stable-successor-changes-ontology',lambda m:setfn(m,'manifestOntology',['h2'],'other'),T=False)
 for n in b.ROLES:add('forbidden-sibling-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['h1']),T=False)
 add('Manifest-is-represented-subject-in-own-ontology',lambda m:m['predicates']['OntologyRepresents'].append(['o1','h1']),T=False)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['h1']),T=False)
 add('consumer-without-role',lambda m:m['predicates']['ConsumerRole'].clear(),T=False)
 add('consumer-outside-applicability',lambda m:m['predicates']['UseInApplicability'].clear(),T=False)
 add('same-identity-token-on-two-canonical-records-permitted',lambda m:None,I=True)
 add('changed-runtime-reference-without-actual-authorization-permitted',lambda m:None,I=True)
 add('declared-revision-preserves-no-other-config-field',lambda m:(m['predicates']['DefinitionRole'].append(['other']),setfn(m,'manifestDefinition',['h2'],'other')),I=True)
 add('configuration-role-values-may-overlap',lambda m:(m['predicates']['StateModelRole'].append(['d1']),[setfn(m,'manifestStateModel',[h],'d1') for h in ['h1','h2']]),I=True)
 add('Manifest-may-be-represented-in-another-ontology',lambda m:m['predicates']['OntologyRepresents'].append(['other','h1']),I=True)
 add('source-does-not-globally-disjoin-runtime-role',lambda m:(m['predicates']['RuntimeRole'].append(['h1']),setfn(m,'manifestRuntime',['h1'],'h1')),I=True)
 add('multiple-Policies-and-projections-permitted',lambda m:(m['predicates']['PolicyRole'].append(['other']),m['predicates']['ProjectionRole'].append(['other']),m['predicates']['BoundPolicy'].append(['h1','other']),m['predicates']['BoundProjection'].append(['h1','other'])),I=True)
 add('opaque-stable-identity-token-permitted',lambda m:[setfn(m,'manifestIdentity',[h],'*') for h in ['h1','h2']],I=True)
 add('successor-relation-not-required-by-theory-alone',lambda m:m['predicates']['StableIdentityRevision'].clear(),I=False)
 add('represented-subject-presence-not-required-by-theory-alone',lambda m:m['predicates']['OntologyRepresents'].clear(),I=False)
 add('consumer-use-presence-not-required-by-theory-alone',lambda m:m['predicates']['ConsumerUse'].clear(),I=False)
 add('actual-config-authorization-is-independent',lambda m:m['predicates']['ActualConfigurationChangeAuthorized'].append(['h2']),I=False)
 add('nontotal-runtime-binding-function',lambda m:m['functions']['manifestRuntime'].pop(),error='nontotal-function')
 add('ill-sorted-manifest-identity-result',lambda m:setfn(m,'manifestIdentity',['h1'],'rt1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-revision-relation-arity',lambda m:m['predicates'].update(StableIdentityRevision=[['h1']]),error='ill-sorted-model-tuple')
 add('duplicate-bound-Policy-tuple',lambda m:m['predicates']['BoundPolicy'].append(['h1','p1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-Ontology-function-tuple',lambda m:m['functions']['manifestOntology'].append(copy.deepcopy(m['functions']['manifestOntology'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.ontology-edge/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-OntologyManifest-model-controls/v1-candidate','status':'PASS-for-exact-authored-OntologyManifest-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent typed canonical stable ontology identity/configuration fields,nonempty Policy/projection bindings,successor identity and separate represented-state guards. Actual reference/version/cardinality/authorization/runtime/source-owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
