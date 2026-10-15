"""Independent finite exact-revision representation,typed facet and subject-boundary models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['n1','n2','o1','o2','s1','r1','ic1','d1','c1','l1','br1','ch1','p1','u1','other'];nodes=['n1','n2'];domains={'Entity':entities,'Token':['empty','id1','id2','v1','digest','other','*']}
 maps={'nodeOntology':lambda e:'o2' if e=='n2' else 'o1','nodeSubject':lambda e:'s1','nodeRevision':lambda e:'r1','nodeSubjectIdentityCarrier':lambda e:'ic1','nodeSubjectDefinition':lambda e:'d1','nodeConfidence':lambda e:'c1','nodeLifecycle':lambda e:'l1','nodeBranch':lambda e:'br1','nodeContestability':lambda e:'ch1','revisionSubject':lambda e:'s1','nodeIdentity':lambda e:'id2' if e=='n2' else 'id1','revisionVersion':lambda e:'v1','revisionDigest':lambda e:'digest'}
 functions={n:[{'args':[e],'value':fn(e)} for e in entities] for n,fn in maps.items()};p={n:[] for n in b.SIGNATURE}
 p.update(OntologyNode=[[e] for e in nodes],GovernedIdentityOrRecord=[[e] for e in nodes],BoundedScope=[[e] for e in nodes],OntologyRole=[['o1'],['o2']],SubjectRole=[['s1']],SubjectRevisionRole=[['r1']],IdentityCarrierRole=[['ic1']],DefinitionRole=[['d1']],ConfidenceStateRole=[['c1']],LifecycleStateRole=[['l1']],BranchStateRole=[['br1']],ContestabilityStateRole=[['ch1']],ProvenanceRole=[['p1']],HasProvenance=[[e,'p1'] for e in nodes],ConsumerRole=[['u1']],ConsumerUse=[['n1','u1']],UseInApplicability=[['n1','u1']],CurrentNode=[['n1']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in nodes]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('independent-cross-ontology-representations-of-one-exact-revision',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['n1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['n1']),T=False)
 add('reverse-genus-missing-Node',lambda m:m['predicates']['OntologyNode'].remove(['n1']),T=False)
 for n in ['GovernedIdentityOrRecord','BoundedScope']:add('missing-'+n,lambda m,n=n:m['predicates'][n].remove(['n1']),T=False)
 add('empty-independent-Node-identity',lambda m:setfn(m,'nodeIdentity',['n1'],'empty'),T=False)
 for field,role in b.FIELD_ROLES.items():add('missing-binding-role-'+field,lambda m,field=field,role=role:m['predicates'][role].clear(),T=False)
 for field in b.FIELD_ROLES:add('binding-to-untyped-reference-'+field,lambda m,field=field:setfn(m,field,['n1'],'other'),T=False)
 add('revision-subject-does-not-match-represented-subject',lambda m:setfn(m,'revisionSubject',['r1'],'other'),T=False)
 for field in ['revisionVersion','revisionDigest']:add('empty-exact-revision-'+field,lambda m,field=field:setfn(m,field,['r1'],'empty'),T=False)
 add('Node-without-provenance',lambda m:m['predicates']['HasProvenance'].remove(['n1','p1']),T=False)
 add('untyped-provenance-member',lambda m:m['predicates']['ProvenanceRole'].clear(),T=False)
 def collapse(m,field):
  m['predicates'][b.FIELD_ROLES[field]].append(['n1']);setfn(m,field,['n1'],'n1')
  if field=='nodeSubject':
   m['predicates']['SubjectRevisionRole'].append(['other']);setfn(m,'nodeRevision',['n1'],'other');setfn(m,'revisionSubject',['other'],'n1')
  if field=='nodeRevision':setfn(m,'revisionSubject',['n1'],'s1')
 for field in ['nodeSubject','nodeRevision','nodeSubjectIdentityCarrier','nodeSubjectDefinition']:add('Node-collapses-with-own-'+field,lambda m,field=field:collapse(m,field),T=False)
 add('Node-as-global-truth-proof',lambda m:m['predicates']['GlobalTruthProof'].append(['n1']),T=False)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['n1']),T=False)
 add('consumer-without-role',lambda m:m['predicates']['ConsumerRole'].clear(),T=False)
 add('consumer-outside-applicability',lambda m:m['predicates']['UseInApplicability'].clear(),T=False)
 add('same-identity-token-on-two-Node-records-not-forbidden',lambda m:setfn(m,'nodeIdentity',['n2'],'id1'),I=True)
 add('multiple-typed-provenance-members-permitted',lambda m:(m['predicates']['ProvenanceRole'].append(['other']),m['predicates']['HasProvenance'].append(['n1','other'])),I=True)
 add('confidence-branch-facet-role-overlap-permitted',lambda m:(m['predicates']['BranchStateRole'].append(['c1']),setfn(m,'nodeBranch',['n1'],'c1')),I=True)
 add('identity-carrier-and-Definition-referent-overlap-not-forbidden',lambda m:(m['predicates']['IdentityCarrierRole'].append(['d1']),setfn(m,'nodeSubjectIdentityCarrier',['n1'],'d1')),I=True)
 add('opaque-nonempty-revision-version-and-digest',lambda m:(setfn(m,'revisionVersion',['r1'],'*'),setfn(m,'revisionDigest',['r1'],'*')),I=True)
 add('two-representations-in-one-ontology-permitted',lambda m:setfn(m,'nodeOntology',['n2'],'o1'),I=False)
 add('same-subject-version-digest-on-two-revision-entities-permitted',lambda m:(m['predicates']['SubjectRevisionRole'].append(['other']),setfn(m,'nodeRevision',['n2'],'other')),I=False)
 add('Node-may-be-subject-of-another-Node',lambda m:(m['predicates']['SubjectRole'].append(['n1']),m['predicates']['SubjectRevisionRole'].append(['other']),setfn(m,'nodeSubject',['n2'],'n1'),setfn(m,'nodeRevision',['n2'],'other'),setfn(m,'revisionSubject',['other'],'n1')),I=False)
 add('consumer-presence-not-required-by-universal-theory',lambda m:m['predicates']['ConsumerUse'].clear(),I=False)
 add('currentness-marker-not-required-by-universal-theory',lambda m:m['predicates']['CurrentNode'].clear(),I=False)
 add('nontotal-revision-function',lambda m:m['functions']['nodeRevision'].pop(),error='nontotal-function')
 add('ill-sorted-Node-identity-result',lambda m:setfn(m,'nodeIdentity',['n1'],'s1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-provenance-relation-arity',lambda m:m['predicates'].update(HasProvenance=[['n1']]),error='ill-sorted-model-tuple')
 add('duplicate-provenance-tuple',lambda m:m['predicates']['HasProvenance'].append(['n1','p1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-subject-function-tuple',lambda m:m['functions']['nodeSubject'].append(copy.deepcopy(m['functions']['nodeSubject'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.ontology-manifest/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-OntologyNode-model-controls/v1-candidate','status':'PASS-for-exact-authored-OntologyNode-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent typed exact-revision representation with separate subject/carrier/Definition,revision coherence,provenance and confidence/lifecycle/branch/contestability facets. Actual version/hash/provenance/confidence/global truth/authority/runtime/source-owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
