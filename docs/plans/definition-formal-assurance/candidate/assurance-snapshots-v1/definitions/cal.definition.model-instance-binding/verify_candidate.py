"""Independently evaluate exact binding endpoints,explicit clauses and bounded overrides."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['b1','b2','p1','i1','o1','o2','ci','ce','co','cp','cu','a1','e1','g1','qc','qh','qa','qr','qi','raw'];bindings=['b1','b2'];domains={'Entity':entities,'Token':['empty','pv1','iv1','iv2','ps','is','other']}
 maps={'parent':lambda x:'p1','instance':lambda x:'i1','parentOwner':lambda x:'o1','instanceOwner':lambda x:'o2','parentVersion':lambda x:'pv1','instanceVersion':lambda x:'iv2' if x=='b2' else 'iv1','parentAuthorityScope':lambda x:'ps','instanceAuthorityScope':lambda x:'is','clauseProvenance':lambda x:'pv1'}
 functions={n:[{'args':[x],'value':fn(x)} for x in entities] for n,fn in maps.items()};p={n:[] for n in b.SIGNATURE}
 for n in ['ModelInstanceBinding',*b.QUALIFIERS,'Governed','Bounded','ParentOwnsContractRequired']:p[n]=[[x] for x in bindings]
 p.update(ParentModelRole=[['p1']],LocalInstanceRole=[['i1']],OwnerRole=[['o1'],['o2']],ClauseRole=[[x] for x in ['ci','ce','co','cp','cu']],AuthorityCitationRole=[['a1']],EvidenceCitationRole=[['e1']],GenericProjectionRole=[['g1']],ReadOnly=[['g1']],RelevantClause=[[x,c] for x in bindings for c in ['ci','ce','co','cp','cu']],InExtensionScope=[[x,c] for x in bindings for c in ['ce','co']],LocalControl=[[x,'ce'] for x in bindings],AuthorityCitation=[[x,'co','a1'] for x in bindings],EvidenceCitation=[[x,'co','e1'] for x in bindings],GenericProjection=[['b1','g1']],ReplacementBinding=[['b1','b2']],SuccessorBinding=[['b1','b2']],RawAssociation=[['raw']],CurrentBinding=[['b1']])
 for n,c in zip(b.DISPOSITIONS,['ci','ce','co','cp','cu']):p[n]=[[x,c] for x in bindings]
 for n,c in zip(b.CLAIMS,['qc','qh','qa','qr','qi']):p['Claims'+n]=[['b1',c]];p[n+'ClaimRole']=[[c]]
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':p}
def setfn(m,n,x,value):next(row for row in m['functions'][n] if row['args']==[x])['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('typed-exact-binding-all-dispositions-citations-separate-claims-and-successor',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['b1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['b1']),T=False)
 add('reverse-genus-missing-binding',lambda m:m['predicates']['ModelInstanceBinding'].remove(['b1']),T=False)
 for n in ['Governed','Bounded','ParentOwnsContractRequired']:add('missing-required-'+n,lambda m,n=n:m['predicates'][n].remove(['b1']),T=False)
 for n,x in [('ParentModelRole','p1'),('LocalInstanceRole','i1'),('OwnerRole','o1'),('ClauseRole','ci')]:add('missing-type-'+n,lambda m,n=n,x=x:m['predicates'][n].remove([x]),T=False)
 add('parent-instance-identity-collapse',lambda m:setfn(m,'instance','b1','p1'),T=False)
 add('binding-parent-identity-collapse',lambda m:setfn(m,'parent','b1','b1'),T=False)
 add('binding-instance-identity-collapse',lambda m:setfn(m,'instance','b1','b1'),T=False)
 for n in ['parentVersion','instanceVersion','parentAuthorityScope','instanceAuthorityScope']:add('empty-exact-token-'+n,lambda m,n=n:setfn(m,n,'b1','empty'),T=False)
 add('unresolved-opaque-revisions-still-admissible-in-T',lambda m:(setfn(m,'instanceVersion','b1','other'),setfn(m,'instanceVersion','b2','iv2')),I=True)
 add('equal-parent-and-instance-version-tokens-permitted',lambda m:setfn(m,'instanceVersion','b1','pv1'),I=True)
 add('same-owner-for-parent-and-instance-permitted',lambda m:setfn(m,'instanceOwner','b1','o1'),I=True)
 add('equal-authority-scope-tokens-permitted',lambda m:setfn(m,'instanceAuthorityScope','b1','ps'),I=True)
 for n,c in zip(b.DISPOSITIONS,['ci','ce','co','cp','cu']):add('relevant-clause-without-disposition-'+n,lambda m,n=n,c=c:m['predicates'][n].remove(['b1',c]),T=False)
 add('disposition-not-in-relevant-universe',lambda m:m['predicates']['RelevantClause'].remove(['b1','ce']),T=False)
 add('inherited-clause-wrong-parent-provenance',lambda m:setfn(m,'clauseProvenance','ci','other'),T=False)
 add('inherited-clause-silently-weakened',lambda m:m['predicates']['SilentlyWeakened'].append(['ci']),T=False)
 add('local-control-outside-extension',lambda m:m['predicates']['LocalControl'].append(['b1','ci']),T=False)
 add('override-outside-extension',lambda m:m['predicates']['InExtensionScope'].remove(['b1','co']),T=False)
 for n in ['AuthorityCitation','EvidenceCitation']:add('override-missing-'+n,lambda m,n=n:m['predicates'][n].remove(['b1','co','a1' if n=='AuthorityCitation' else 'e1']),T=False)
 for n in ['AuthorityCitationRole','EvidenceCitationRole']:add('override-untyped-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('inherited-and-overridden-clause-overlap-permitted',lambda m:m['predicates']['Inherited'].append(['b1','co']),I=True)
 add('prohibited-and-overridden-overlap-not-resolved-by-T',lambda m:m['predicates']['Prohibited'].append(['b1','co']),I=True)
 add('undeclared-raw-clause-outside-universe-permitted',lambda m:m['predicates']['ClauseRole'].append(['raw']),I=True)
 add('citation-outside-override-unconstrained',lambda m:m['predicates']['AuthorityCitation'].append(['b1','raw','raw']),I=True)
 add('read-only-projection-missing',lambda m:m['predicates']['ReadOnly'].clear(),T=False)
 add('projection-untyped',lambda m:m['predicates']['GenericProjectionRole'].clear(),T=False)
 add('canonical-binding-used-as-own-generic-projection',lambda m:m['predicates']['GenericProjection'].append(['b1','b1']),T=False)
 for n in ['TransfersParentOwnership','TransfersUnrestrictedAuthority']:add('forbidden-'+n,lambda m,n=n:m['predicates'][n].append(['b1']),T=False)
 for n,c in zip(b.CLAIMS,['qc','qh','qa','qr','qi']):
  add('claim-missing-type-'+n,lambda m,n=n:m['predicates'][n+'ClaimRole'].clear(),T=False)
  other=next(x for x in b.CLAIMS if x!=n);add('claim-role-collapse-'+n,lambda m,other=other,c=c:m['predicates'][other+'ClaimRole'].append([c]),T=False)
 add('changed-replacement-without-successor',lambda m:m['predicates']['SuccessorBinding'].clear(),T=False)
 add('successor-self-loop',lambda m:m['predicates']['SuccessorBinding'].append(['b1','b1']),T=False)
 add('replacement-to-nonbinding',lambda m:m['predicates']['ReplacementBinding'].append(['b1','raw']),T=False)
 add('successor-to-nonbinding',lambda m:m['predicates']['SuccessorBinding'].append(['b1','raw']),T=False)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['b1']),T=False)
 add('change-without-declared-replacement-unconstrained',lambda m:(m['predicates']['ReplacementBinding'].clear(),m['predicates']['SuccessorBinding'].clear()))
 add('same-configuration-successor-permitted',lambda m:setfn(m,'instanceVersion','b2','iv1'))
 add('binding-can-have-no-relevant-clauses-if-populations-unsatisfied',lambda m:([m['predicates'][n].clear() for n in ['RelevantClause',*b.DISPOSITIONS,'AuthorityCitation','EvidenceCitation','LocalControl']]),I=False)
 add('nontotal-parent-function',lambda m:m['functions']['parent'].pop(),error='nontotal-function')
 add('ill-sorted-parent-function',lambda m:setfn(m,'parent','b1','pv1'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-citation-arity',lambda m:m['predicates'].update(AuthorityCitation=[['b1','co']]),error='ill-sorted-model-tuple')
 add('duplicate-clause-tuple',lambda m:m['predicates']['Inherited'].append(['b1','ci']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['parent'].append(copy.deepcopy(m['functions']['parent'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.semantic-event-history/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ModelInstanceBinding-model-controls/v1-candidate','status':'PASS-for-exact-authored-ModelInstanceBinding-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent exact typed endpoints,explicit clause dispositions,provenance,bounded override citations,separate claims,read-only projection and conditional successor requirements. Actual resolvers,authority,evidence,temporal storage and owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
