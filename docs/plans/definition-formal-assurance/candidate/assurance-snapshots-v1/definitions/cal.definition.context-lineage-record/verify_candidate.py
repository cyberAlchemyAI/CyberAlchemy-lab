"""Independent finite lineage kinds,fields,no-inference and normative-history controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['r'+str(i) for i in range(6)]+['raw','directory'];records=entities[:6]
 domains={'Entity':entities,'Field':b.FIELDS+['extra'],'Kind':b.KINDS+['OTHER'],'Token':['empty','spec']}
 functions={'fieldValue':[{'args':[e,f],'value':'spec'} for e,f in itertools.product(entities,domains['Field'])],'lineageKindValue':[{'args':[e],'value':b.KINDS[i] if i<6 else 'OTHER'} for i,e in enumerate(entities)]}
 p={n:[] for n in b.SIGNATURE};p.update(ContextLineageRecord=[[e] for e in records],DeclaresField=[[e,f] for e,f in itertools.product(records+['raw'],b.FIELDS)],RawDeclaredComplete=[['r0'],['raw']],DirectoryContinuous=[['directory']],HistoryRetentionRequired=[['r4'],['r5']],PredecessorPresent=[['r1'],['r2'],['r3'],['r4']])
 for n in b.QUALIFIERS+['RecordsIdentityHistory','PredecessorVersionExact','SuccessorVersionsExact','PreservedScopeIndependentlyStated','ChangedScopeIndependentlyStated']:p[n]=[[e] for e in records]
 return {'domains':domains,'constants':{'EMPTY':'empty',**{'F_'+n:n for n in b.FIELDS},**{n:n for n in b.KINDS}},'functions':functions,'predicates':p}
def setfn(m,e,value):next(x for x in m['functions']['lineageKindValue'] if x['args']==[e])['value']=value
def setfield(m,e,f,value):next(x for x in m['functions']['fieldValue'] if x['args']==[e,f])['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('six-dispositions-with-optional-predecessor-and-no-actual-outcomes',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independently-supplied-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['r0']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['r0']),T=False)
 add('reverse-genus-iff-missing-lineage',lambda m:m['predicates']['ContextLineageRecord'].remove(['r0']),T=False)
 for f in b.FIELDS:add('missing-declared-field-'+f,lambda m,f=f:m['predicates']['DeclaresField'].remove(['r0',f]),T=False)
 for f in ['decision_ref','evidence_refs','challenge_route']:add('empty-required-field-'+f,lambda m,f=f:setfield(m,'r0',f,'empty'),T=False)
 for f in ['source_version','destination_versions','preserved_scope','changed_scope','residue']:add('opaque-field-'+f+'-empty-with-marker',lambda m,f=f:setfield(m,'r0',f,'empty'),I=True)
 for n in b.ROLES:add('forbidden-role-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['r0']),T=False)
 for n in ['RecordsIdentityHistory','PredecessorVersionExact','SuccessorVersionsExact','PreservedScopeIndependentlyStated','ChangedScopeIndependentlyStated']:add('missing-marker-'+n,lambda m,n=n:m['predicates'][n].remove(['r0']),T=False)
 for n in ['InfersEquivalence','InfersAdmission']:add('forbidden-inferred-'+n,lambda m,n=n:m['predicates'][n].append(['r0']),T=False)
 add('unknown-lineage-kind',lambda m:setfn(m,'r0','OTHER'),T=False)
 add('kind-tags-aliased',lambda m:m['constants'].update(SPLIT='SUCCESSOR'),T=False)
 for n in b.KINDS:add('allowed-kind-'+n,lambda m,n=n:None,I=True)
 add('superseded-history-requirement-absent',lambda m:m['predicates']['HistoryRetentionRequired'].remove(['r4']),T=False)
 add('withdrawn-history-requirement-absent',lambda m:m['predicates']['HistoryRetentionRequired'].remove(['r5']),T=False)
 add('required-history-without-actual-history',lambda m:None,I=True)
 add('predecessor-absent-optional-marker',lambda m:m['predicates']['PredecessorPresent'].clear(),I=True)
 add('independent-scopes-may-have-equal-Tokens',lambda m:None,I=True)
 add('field-name-constants-can-alias',lambda m:m['constants'].update(F_source_version='destination_versions'),I=True)
 add('extra-declared-field-allowed',lambda m:m['predicates']['DeclaresField'].append(['r0','extra']),I=True)
 add('directory-continuity-not-identity-continuity',lambda m:None,I=True)
 add('owner-qualified-marker-not-owner-resolution',lambda m:None,I=True)
 add('nontotal-kind-function',lambda m:m['functions']['lineageKindValue'].pop(),error='nontotal-function')
 add('ill-sorted-kind-function',lambda m:setfn(m,'r0','spec'),error='ill-sorted-function-result')
 add('ill-sorted-kind-constant',lambda m:m['constants'].update(SPLIT='absent'),error='ill-sorted-constant')
 add('wrong-declared-field-arity',lambda m:m['predicates'].update(DeclaresField=[['r0']]),error='ill-sorted-model-tuple')
 add('duplicate-declared-field-tuple',lambda m:m['predicates']['DeclaresField'].append(['r0','id']),error='duplicate-predicate-tuple')
 add('empty-kind-domain',lambda m:m['domains'].update(Kind=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['lineageKindValue'].append(copy.deepcopy(m['functions']['lineageKindValue'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.context/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ContextLineageRecord-model-controls/v1-candidate','status':'PASS-for-exact-authored-ContextLineageRecord-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied lineage genus,tuple,kind,no-inference and normative-history structures. Actual record/context/version/owner maps and universal immutable/history semantics remain unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
