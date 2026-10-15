"""Independent Gate function,vocabulary,record,flag,risk and defer controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def fval(m,n,args):
 args=[args] if isinstance(args,str) else args
 return next(x['value'] for x in m['functions'][n] if x['args']==args)
def setfn(m,n,args,value):
 args=[args] if isinstance(args,str) else args
 next(x for x in m['functions'][n] if x['args']==args)['value']=value
def base_model():
 constants={'EMPTY':'empty','MEANING_ID':'semantic-gate','MEANING_KIND':'definition-kind','MEANING_CARRIER':'type-definition','MEANING_SCOPE':'shared-authority','SOURCE_D5':'cav2-d5','SOURCE_D37':'cav2-d37','PASS':'pass','FLAG':'flag','BLOCK':'block','DEFER':'defer'}
 tokens=[constants[n] for n in b.CONSTANTS if b.CONSTANTS[n]=='Token']+[n.lower() for n in b.GATE_TOKEN_FIELDS]+['continue','continue-risk','stop','defer-owner','named-risk','named-followup','named-residue','opaque'];inv=['iPass','iFlag','iBlock','iDefer','iNarrowPass','iNarrowBlock','iUnrecorded'];records=['rPass','rFlag','rBlock','rDefer','rNarrowPass','rNarrowBlock','rUnused'];domains={'Meaning':['meaning1'],'GateConfig':['gDefault','gNarrow'],'Invocation':inv,'Scope':['scope1','scope2'],'Input':['input1','input2'],'Evidence':['evidence1','evidence2'],'Criteria':['criteria1','criteria2'],'Verdict':['pass','flag','block','defer','custom'],'Record':records,'Route':['ownerRoute','anotherRoute'],'Token':tokens}
 contexts={'iPass':['gDefault','scope1','input1','evidence1','criteria1'],'iFlag':['gDefault','scope1','input2','evidence1','criteria1'],'iBlock':['gDefault','scope1','input1','evidence2','criteria1'],'iDefer':['gDefault','scope1','input1','evidence1','criteria2'],'iNarrowPass':['gNarrow','scope1','input1','evidence1','criteria1'],'iNarrowBlock':['gNarrow','scope1','input2','evidence1','criteria1'],'iUnrecorded':['gDefault','scope1','input1','evidence1','criteria1']}
 def G(g,s,x,e,c):
  if g=='gNarrow':return 'pass' if x=='input1' else 'block'
  if s=='scope1' and x=='input2' and e=='evidence1' and c=='criteria1':return 'flag'
  if s=='scope1' and x=='input1' and e=='evidence2' and c=='criteria1':return 'block'
  if s=='scope1' and x=='input1' and e=='evidence1' and c=='criteria2':return 'defer'
  return 'pass'
 iv=dict(zip(inv,records));ri=dict(zip(records,inv));meaningKeys=dict(zip(['meaningIdentity','meaningKind','meaningCarrier','meaningOwnerScope','meaningSourceD5','meaningSourceD37'],['MEANING_ID','MEANING_KIND','MEANING_CARRIER','MEANING_SCOPE','SOURCE_D5','SOURCE_D37']));maps={n:(lambda m,n=n:constants[meaningKeys[n]]) for n in meaningKeys};maps.update(gateMeaning=lambda g:'meaning1',gateOwnerRoute=lambda g:'ownerRoute',gateScope=lambda g:'scope1',invGate=lambda i:contexts[i][0],invScope=lambda i:contexts[i][1],invInput=lambda i:contexts[i][2],invEvidence=lambda i:contexts[i][3],invCriteria=lambda i:contexts[i][4],invVerdict=lambda i:G(*contexts[i]),invRecord=lambda i:iv[i],G=G,recordOwnerRoute=lambda r:'ownerRoute',recordScope=lambda r:contexts[ri[r]][1],recordInput=lambda r:contexts[ri[r]][2],recordEvidenceBasis=lambda r:contexts[ri[r]][3],recordCriteria=lambda r:contexts[ri[r]][4],recordVerdict=lambda r:G(*contexts[ri[r]]),recordDeferredOwnerRoute=lambda r:'anotherRoute',recordLocation=lambda r:'recordlocation',recordEffect=lambda r:('empty' if r=='rUnused' else {'pass':'continue','flag':'continue-risk','block':'stop','defer':'defer-owner'}[G(*contexts[ri[r]])]),recordRisk=lambda r:'named-risk' if r=='rFlag' else 'empty',recordFollowUp=lambda r:'named-followup' if r=='rFlag' else 'empty',recordResidue=lambda r:'named-residue' if r=='rBlock' else 'empty')
 for n in b.GATE_TOKEN_FIELDS:maps['gate'+n]=lambda g,n=n:n.lower()
 functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};p={n:[] for n in b.SIGNATURE};p.update(GateMeaning=[['meaning1']],PreservesClassification=[['meaning1']],PreservesSourceRelations=[['meaning1']],NotSilentlyMerged=[['meaning1']],Gate=[['gDefault'],['gNarrow']],ExplicitCheckpoint=[['gDefault'],['gNarrow']],NarrowerVocabulary=[['gNarrow']],PromotionGate=[['gDefault']],PromotionOwnerRouteExplicit=[['gDefault']],GateInvocation=[[i] for i in inv],Admissible=[[i] for i in inv[:-1]],RiskPresent=[['iFlag']],ResiduePresent=[['iBlock']],UsedValidator=[['iPass'],['iFlag']],UsedHumanDecision=[['iPass'],['iDefer']],RecordedVerdict=[[r] for r in records[:-1]],NamedRisk=[['rFlag']],NamedFollowUp=[['rFlag']],ResidueRecorded=[['rBlock']],DownstreamEffectRecorded=[[r] for r in records[:-1]],ContinueDeclared=[['rPass'],['rNarrowPass']],ContinueWithRiskDeclared=[['rFlag']],StopDeclared=[['rBlock'],['rNarrowBlock']],DeferDeclared=[['rDefer']],DeclaredVerdictMeaning=[[v] for v in ['pass','flag','block','defer']],AllowsVerdict=[['gDefault',v] for v in ['pass','flag','block','defer']]+[['gNarrow','pass'],['gNarrow','block']],EffectMatchesPolicy=[[iv[i],contexts[i][0]] for i in inv[:-1]])
 for n in b.DECLARATIONS:p[n]=[['gDefault'],['gNarrow']]
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':p}
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('default-four-verdicts-narrow-two-records-and-unrecorded-invocation',lambda m:None,I=True)
 for n in b.GATE_OUTCOMES:add('independent-gate-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['gDefault']),I=True)
 for n in b.INV_OUTCOMES:add('independent-invocation-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['iPass']),I=True)
 for n in ['PreservesClassification','PreservesSourceRelations','NotSilentlyMerged']:add('missing-normalized-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['meaningIdentity','meaningKind','meaningCarrier','meaningOwnerScope','meaningSourceD5','meaningSourceD37']:add('wrong-normalized-'+n,lambda m,n=n:setfn(m,n,'meaning1','opaque'),T=False)
 add('normalized-meaning-omitted',lambda m:m['predicates']['GateMeaning'].clear(),T=False)
 for n in ['ExplicitCheckpoint']+b.DECLARATIONS:add('missing-gate-'+n,lambda m,n=n:m['predicates'][n].remove(['gDefault']),T=False)
 add('gate-characterization-reverse-direction',lambda m:m['predicates']['Gate'].remove(['gDefault']),T=False)
 for n in b.GATE_TOKEN_FIELDS:add('empty-gate-'+n,lambda m,n=n:setfn(m,'gate'+n,'gDefault','empty'),T=False)
 add('promotion-without-explicit-owner-route',lambda m:m['predicates']['PromotionOwnerRouteExplicit'].clear(),T=False)
 add('generic-gate-does-not-have-to-be-promotion',lambda m:None,I=True)
 for n in b.CODE_NAMES:add('missing-default-verdict-'+n,lambda m,n=n:m['predicates']['AllowsVerdict'].remove(['gDefault',m['constants'][n]]),T=False)
 add('flag-and-pass-codes-collapsed',lambda m:m['constants'].update(FLAG='pass'),T=False)
 add('default-extra-custom-code-requires-owner-vocabulary-decision',lambda m:(m['predicates']['AllowsVerdict'].append(['gDefault','custom']),m['predicates']['DeclaredVerdictMeaning'].append(['custom'])),T=False)
 add('narrow-vocabulary-empty',lambda m:m['predicates'].update(AllowsVerdict=[x for x in m['predicates']['AllowsVerdict'] if x[0]!='gNarrow']),T=False)
 add('narrow-custom-meaning-not-declared',lambda m:m['predicates']['AllowsVerdict'].append(['gNarrow','custom']),T=False)
 add('explicit-narrow-custom-declared-meaning-allowed-pending-owner-fidelity',lambda m:(m['predicates']['AllowsVerdict'].append(['gNarrow','custom']),m['predicates']['DeclaredVerdictMeaning'].append(['custom'])),I=True)
 add('missing-default-verdict-meaning',lambda m:m['predicates']['DeclaredVerdictMeaning'].remove(['flag']),T=False)
 add('invocation-scope-outside-gate-scope',lambda m:setfn(m,'invScope','iPass','scope2'),T=False)
 add('invocation-result-does-not-match-decision-function',lambda m:setfn(m,'invVerdict','iPass','block'),T=False)
 add('five-argument-G-output-mutated-with-stale-record',lambda m:setfn(m,'G',['gDefault','scope1','input1','evidence1','criteria1'],'block'),T=False)
 add('nontargeted-total-G-context-may-differ-no-observed-runtime-claim',lambda m:setfn(m,'G',['gDefault','scope2','input2','evidence2','criteria2'],'defer'),I=True)
 add('unrecorded-result-not-admissible',lambda m:None,I=True)
 add('admissible-without-invocation',lambda m:m['predicates']['GateInvocation'].remove(['iPass']),T=False)
 add('admissible-without-record',lambda m:m['predicates']['RecordedVerdict'].remove(['rPass']),T=False)
 add('unrecorded-invocation-promoted-to-admissible',lambda m:m['predicates']['Admissible'].append(['iUnrecorded']),T=False)
 add('record-conditions-are-not-sufficient-for-admissibility',lambda m:m['predicates']['Admissible'].remove(['iPass']),I=False)
 for n,value in [('recordOwnerRoute','anotherRoute'),('recordScope','scope2'),('recordInput','input2'),('recordEvidenceBasis','evidence2'),('recordCriteria','criteria2'),('recordVerdict','block'),('recordLocation','opaque')]:add('record-mismatch-'+n,lambda m,n=n,value=value:setfn(m,n,'rPass',value),T=False)
 add('missing-downstream-effect-record',lambda m:m['predicates']['DownstreamEffectRecorded'].remove(['rPass']),T=False)
 add('empty-recorded-effect',lambda m:setfn(m,'recordEffect','rPass','empty'),T=False)
 add('effect-policy-coherence-missing',lambda m:m['predicates']['EffectMatchesPolicy'].remove(['rPass','gDefault']),T=False)
 add('pass-without-declared-continuation',lambda m:m['predicates']['ContinueDeclared'].remove(['rPass']),T=False)
 for n in ['NamedRisk','NamedFollowUp','ContinueWithRiskDeclared']:add('flag-missing-'+n,lambda m,n=n:m['predicates'][n].remove(['rFlag']),T=False)
 for n in ['recordRisk','recordFollowUp']:add('flag-empty-'+n,lambda m,n=n:setfn(m,n,'rFlag','empty'),T=False)
 add('flag-is-silent-pass',lambda m:m['predicates']['SilentPass'].append(['rFlag']),T=False)
 add('block-without-stop-declaration',lambda m:m['predicates']['StopDeclared'].remove(['rBlock']),T=False)
 add('defer-without-owner-route-effect',lambda m:m['predicates']['DeferDeclared'].clear(),T=False)
 add('defer-owner-route-not-distinct',lambda m:setfn(m,'recordDeferredOwnerRoute','rDefer','ownerRoute'),T=False)
 add('present-risk-without-recorded-name',lambda m:m['predicates']['NamedRisk'].clear(),T=False)
 add('present-residue-not-recorded',lambda m:m['predicates']['ResidueRecorded'].clear(),T=False)
 add('present-residue-empty-name',lambda m:setfn(m,'recordResidue','rBlock','empty'),T=False)
 add('risk-presence-on-pass-needs-its-own-record',lambda m:m['predicates']['RiskPresent'].append(['iPass']),T=False)
 add('validator-and-human-inputs-may-coexist',lambda m:None,I=True)
 add('admissible-record-may-lack-either-consumer-marker',lambda m:m['predicates']['UsedValidator'].remove(['iFlag']),I=True)
 for n in b.COLLAPSED+b.INFER_FLAGS:add('forbidden-gate-collapse-or-inference-'+n,lambda m,n=n:m['predicates'][n].append(['gDefault']),T=False)
 add('missing-five-argument-G-table-entry',lambda m:m['functions']['G'].pop(),error='nontotal-function')
 add('ill-sorted-G-result',lambda m:setfn(m,'G',['gDefault','scope1','input1','evidence1','criteria1'],'scope1'),error='ill-sorted-function-result')
 add('ill-sorted-verdict-constant',lambda m:m['constants'].update(PASS='ownerRoute'),error='ill-sorted-constant')
 add('wrong-vocabulary-relation-arity',lambda m:m['predicates'].update(AllowsVerdict=[['gDefault']]),error='ill-sorted-model-tuple')
 add('duplicate-admissible-predicate-tuple',lambda m:m['predicates']['Admissible'].append(['iPass']),error='duplicate-predicate-tuple')
 add('empty-verdict-domain',lambda m:m['domains'].update(Verdict=[]),error='empty-or-malformed-domain')
 add('duplicate-G-table-entry',lambda m:m['functions']['G'].append(copy.deepcopy(m['functions']['G'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.contract/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Gate-model-controls/v1-candidate','status':'PASS-for-exact-authored-Gate-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent declared Gate kind/subject/actor/scope and scoped stage facts;actual authorization,delivery,observation,trace,owner and consumer/source-owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
