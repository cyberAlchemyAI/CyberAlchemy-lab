"""Independent supplied Contestability Policy characterization and gap models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 domains={'Entity':['c1','c2','c3','raw','s1','d1','e1','q1','other'],'Field':[n for n in b.FIELDS]+['extra'],'Token':['empty','spec','identity','confidence']}
 functions={'fieldValue':[{'args':[e,f],'value':'empty' if e=='c3' and f in b.OPTIONAL else 'spec'} for e,f in itertools.product(domains['Entity'],domains['Field'])]}
 for n in ['normalizedIdValue','evidenceConfidenceValue','commitmentConfidenceValue']:functions[n]=[{'args':[e],'value':'identity' if n=='normalizedIdValue' else 'confidence'} for e in domains['Entity']]
 p={n:[] for n in b.SIGNATURE};p.update(ContestabilityPolicy=[['c1'],['c2'],['c3']],CanonicalInstance=[['c1']],PreservesExactD40Relation=[['c1']],RawDeclaredComplete=[['c1'],['raw']],ContradictionLinksPresent=[['c1']],ValidationLinksPresent=[['c1']],SubjectConfidenceSibling=[['s1']],SubjectResidueSibling=[['s1']],AttachedSubject=[['c1','s1']],FiledChallenge=[['e1','c1']],UnresolvedChallengeResidue=[['c1'],['c2']],ActualResidueRetained=[['c1']],DeclaresField=[[e,f] for e,f in itertools.product(['c1','c2','c3','raw'],b.FIELDS)])
 for n in b.QUALIFIERS+['NormalizedPolicyKind','SharedAuthorityScope','PolicyCarrier']:p[n]=[['c1'],['c2'],['c3']]
 return {'domains':domains,'constants':{'EMPTY':'empty','CP_ID':'identity',**{'F_'+n:n for n in b.FIELDS}},'functions':functions,'predicates':p}
def setfield(m,n,e,value):next(x for x in m['functions']['fieldValue'] if x['args']==[e,n])['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('normalized-canonical-review-surface-with-conditional-links-and-sibling-boundaries',lambda m:None,I=True)
 for n in b.OUTCOMES+['ActualPromotion']:add('independently-supplied-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['c1']))
 for n in b.QUALIFIERS: add('Policy-missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['c1']),T=False)
 add('genus-reverse-iff-missing-Policy',lambda m:m['predicates']['ContestabilityPolicy'].remove(['c2']),T=False)
 for n in ['NormalizedPolicyKind','SharedAuthorityScope','PolicyCarrier']:add('Policy-missing-normalized-axis-'+n,lambda m,n=n:m['predicates'][n].remove(['c1']),T=False)
 add('wrong-normalized-identity-Token',lambda m:next(x for x in m['functions']['normalizedIdValue'] if x['args']==['c1']).update(value='spec'),T=False)
 add('canonical-instance-missing-source-preservation',lambda m:m['predicates']['PreservesExactD40Relation'].remove(['c1']),T=False)
 add('canonical-instance-silent-sibling-merge',lambda m:m['predicates']['SilentSiblingIdentityMerge'].append(['c1']),T=False)
 add('raw-canonical-instance-not-qualified-policy',lambda m:m['predicates']['CanonicalInstance'].append(['raw']),T=False)
 for n in b.FIELDS:
  add('Policy-missing-declared-field-'+n,lambda m,n=n:m['predicates']['DeclaresField'].remove(['c1',n]),T=False)
  add('Policy-empty-required-or-present-link-value-'+n,lambda m,n=n:setfield(m,n,'c1','empty'),T=False)
 for n in b.ROLES+['ContainsOwnConfidence','ContainsOwnResidue','IntroducesThirdConfidenceAxis']:add('Policy-forbidden-role-or-content-'+n,lambda m,n=n:m['predicates'][n].append(['c1']),T=False)
 add('unrelated-entity-may-carry-confidence-residue-and-third-axis',lambda m:[m['predicates'][n].append(['raw']) for n in ['ContainsOwnConfidence','ContainsOwnResidue','IntroducesThirdConfidenceAxis']],I=True)
 add('extra-declared-field-allowed',lambda m:m['predicates']['DeclaresField'].append(['c1','extra']),I=True)
 add('raw-fields-do-not-force-qualified-genus',lambda m:None,I=True)
 add('absent-links-do-not-require-empty-values',lambda m:None,I=True)
 add('link-presence-must-not-use-empty-value',lambda m:m['predicates']['ContradictionLinksPresent'].append(['c3']),T=False)
 add('actual-unresolved-residue-not-retained-does-not-break-static-definition',lambda m:None,I=True)
 add('supplied-owner-closure-can-coexist-with-policy',lambda m:m['predicates']['OwnerReviewClosed'].append(['c2']),I=True)
 add('supplied-owner-waiver-can-coexist-with-policy',lambda m:m['predicates']['OwnerReviewWaived'].append(['c2']),I=True)
 add('supplied-owner-demotion-can-coexist-with-policy',lambda m:m['predicates']['OwnerReviewDemoted'].append(['c2']),I=True)
 add('declared-owner-route-not-connected-to-qualified-resolution',lambda m:None,I=True)
 add('genus-attachment-not-connected-to-actual-subject-relation',lambda m:m['predicates']['AttachedSubject'].clear(),I=False)
 add('confidence-Tokens-can-alias-no-quantitative-or-axis-semantics',lambda m:[x.update(value='spec') for n in ['evidenceConfidenceValue','commitmentConfidenceValue'] for x in m['functions'][n]],I=True)
 add('field-name-constants-can-alias-no-unique-names-axiom',lambda m:m['constants'].update(F_validation_edges='contradiction_edges'),I=True)
 add('no-actual-filing-required-by-static-definition',lambda m:m['predicates']['FiledChallenge'].clear(),I=False)
 add('nontotal-field-function',lambda m:m['functions']['fieldValue'].pop(),error='nontotal-function')
 add('ill-sorted-field-function-result',lambda m:setfield(m,'owner_route','c1','c1'),error='ill-sorted-function-result')
 add('ill-sorted-Field-constant',lambda m:m['constants'].update(F_owner_route='absent'),error='ill-sorted-constant')
 add('wrong-attachment-arity',lambda m:m['predicates'].update(AttachedSubject=[['c1']]),error='ill-sorted-model-tuple')
 add('duplicate-declaration-tuple',lambda m:m['predicates']['DeclaresField'].append(['c1','owner_route']),error='duplicate-predicate-tuple')
 add('empty-Token-domain',lambda m:m['domains'].update(Token=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['fieldValue'].append(copy.deepcopy(m['functions']['fieldValue'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.constitution/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ContestabilityPolicy-model-controls/v1-candidate','status':'PASS-for-exact-authored-ContestabilityPolicy-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied normalized review-surface,conditional field and sibling-boundary models. Exact identity/carrier/link/owner/confidence/residue and universal temporal retention semantics remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
