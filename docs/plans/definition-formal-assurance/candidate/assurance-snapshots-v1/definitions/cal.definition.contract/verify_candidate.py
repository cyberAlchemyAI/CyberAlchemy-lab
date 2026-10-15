"""Independent Contract member,party-or-subject,version/use and compliance-boundary controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['cParty','cSubject','cBoth','scope1','scope2','uExact','uSuccessor','memberO','memberP','memberF','memberI','memberB','memberE','memberH','party','subject','aux','impl'];tokens=['empty','v1','v2','selected','successor','opaque','other'];domains={'Entity':entities,'Token':tokens}
 maps={'contractScope':lambda e:'scope1','useScope':lambda e:'scope1','useContract':lambda e:'cSubject' if e=='uSuccessor' else 'cParty','contractVersion':lambda e:'v1','useDefinition':lambda e:'successor' if e=='uSuccessor' else 'selected'}
 functions={n:[{'args':[e],'value':f(e)} for e in entities] for n,f in maps.items()};p={n:[] for n in b.SIGNATURE};p.update(Contract=[['cParty'],['cSubject'],['cBoth']],GovernedIdentityRole=[['cParty'],['cBoth']],GovernedRecordRole=[['cSubject'],['cBoth']],ScopeRole=[['scope1'],['scope2']],ContractUse=[['uExact'],['uSuccessor']],AdmittedSuccessorOf=[['successor','selected']])
 for n in b.QUALIFIERS:p[n]=[['cParty'],['cSubject'],['cBoth']]
 for n,e in zip(b.REQUIRED_MEMBERS,['memberO','memberP','memberF','memberI','memberB','memberE','memberH']):p[n]=[[c,e] for c in ['cParty','cSubject','cBoth']];p[b.MEMBER_ROLES[n]]=[[e]]
 p['ContractParty']=[['cParty','party'],['cBoth','party']];p['ContractSubject']=[['cSubject','subject'],['cBoth','subject']];p['PartyRole']=[['party']];p['SubjectRole']=[['subject']]
 return {'domains':domains,'constants':{'EMPTY':'empty','SELECTED_DEFINITION':'selected'},'functions':functions,'predicates':p}
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('party-only-subject-only-and-both-contracts-with-qualified-uses',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['cParty']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['cParty']),T=False)
 add('reverse-genus-contract-omitted',lambda m:m['predicates']['Contract'].remove(['cParty']),T=False)
 add('empty-contract-version',lambda m:setfn(m,'contractVersion',['cParty'],'empty'),T=False)
 add('scope-without-role',lambda m:m['predicates']['ScopeRole'].clear(),T=False)
 add('contract-scope-non-scope',lambda m:setfn(m,'contractScope',['cParty'],'aux'),T=False)
 add('neither-governed-identity-nor-record',lambda m:m['predicates']['GovernedRecordRole'].remove(['cSubject']),T=False)
 add('both-governed-identity-and-record-permitted',lambda m:None,I=True)
 for n,role in b.MEMBER_ROLES.items():
  add('missing-member-role-'+role,lambda m,role=role:m['predicates'][role].clear(),T=False)
  add('member-owned-by-noncontract-'+n,lambda m,n=n:m['predicates'][n].append(['impl',m['predicates'][n][0][1]]),T=False)
 for n in b.REQUIRED_MEMBERS:add('missing-required-category-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('neither-party-nor-subject',lambda m:m['predicates']['ContractParty'].remove(['cParty','party']),T=False)
 add('party-and-subject-on-one-contract-permitted',lambda m:m['predicates']['ContractSubject'].append(['cParty','subject']),I=False)
 add('no-parties-removing-exclusive-example-not-vacuity-proof',lambda m:(m['predicates']['ContractParty'].clear(),m['predicates']['ContractSubject'].append(['cParty','subject'])),I=False)
 add('no-subjects-removing-exclusive-example-not-vacuity-proof',lambda m:(m['predicates']['ContractSubject'].clear(),m['predicates']['ContractParty'].append(['cSubject','party'])),I=False)
 add('same-member-multiple-normative-roles-no-deontic-proof',lambda m:(m['predicates']['ProhibitionRole'].append(['memberP']),m['predicates']['ContractProhibition'].append(['cParty','memberP'])),I=True)
 add('extra-obligation-same-contract-allowed',lambda m:(m['predicates']['ObligationRole'].append(['aux']),m['predicates']['ContractObligation'].append(['cParty','aux'])),I=True)
 add('opaque-contract-version-token-allowed',lambda m:setfn(m,'contractVersion',['cParty'],'opaque'),I=True)
 add('use-of-noncontract',lambda m:setfn(m,'useContract',['uExact'],'impl'),T=False)
 add('use-definition-neither-exact-nor-admitted-successor',lambda m:setfn(m,'useDefinition',['uExact'],'other'),T=False)
 add('successor-marker-missing',lambda m:m['predicates']['AdmittedSuccessorOf'].clear(),T=False)
 add('successor-direction-reversed',lambda m:m['predicates'].update(AdmittedSuccessorOf=[['selected','successor']]),T=False)
 add('use-scope-mismatch-with-two-valid-scopes',lambda m:setfn(m,'useScope',['uExact'],'scope2'),T=False)
 add('use-scope-not-a-scope',lambda m:setfn(m,'useScope',['uExact'],'aux'),T=False)
 add('declared-successor-is-not-actual-admission-proof',lambda m:None,I=True)
 for n in b.FORBIDDEN:
  add('contract-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['cParty']),T=False)
  add('contract-use-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['uExact']),T=False)
 for n in b.INFER_FLAGS:
  add('contract-forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['cParty']),T=False)
  add('use-forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['uExact']),T=False)
 add('no-uses-required-by-universal-theory',lambda m:m['predicates']['ContractUse'].clear(),I=False)
 add('all-uses-exact-removes-successor-example',lambda m:setfn(m,'useDefinition',['uSuccessor'],'selected'),I=False)
 add('all-uses-successor-removes-exact-example',lambda m:setfn(m,'useDefinition',['uExact'],'successor'),I=False)
 add('all-contracts-governed-record-removes-identity-example',lambda m:(m['predicates']['GovernedIdentityRole'].clear(),m['predicates']['GovernedRecordRole'].append(['cParty'])),I=False)
 add('all-contracts-governed-identity-removes-record-example',lambda m:(m['predicates']['GovernedRecordRole'].clear(),m['predicates']['GovernedIdentityRole'].append(['cSubject'])),I=False)
 add('nontotal-contract-scope-function',lambda m:m['functions']['contractScope'].pop(),error='nontotal-function')
 add('ill-sorted-contract-version-result',lambda m:setfn(m,'contractVersion',['cParty'],'cParty'),error='ill-sorted-function-result')
 add('ill-sorted-selected-definition-constant',lambda m:m['constants'].update(SELECTED_DEFINITION='absent'),error='ill-sorted-constant')
 add('wrong-member-arity',lambda m:m['predicates'].update(ContractObligation=[['cParty']]),error='ill-sorted-model-tuple')
 add('duplicate-contract-tuple',lambda m:m['predicates']['Contract'].append(['cParty']),error='duplicate-predicate-tuple')
 add('empty-token-domain',lambda m:m['domains'].update(Token=[]),error='empty-or-malformed-domain')
 add('duplicate-use-function-tuple',lambda m:m['functions']['useContract'].append(copy.deepcopy(m['functions']['useContract'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.bounded-context/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Contract-model-controls/v1-candidate','status':'PASS-for-exact-authored-Contract-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent typed governed contract requirements and Definition/scope use guards;actual compliance,normative consistency,grant,breach,owner and consumer/source-owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
