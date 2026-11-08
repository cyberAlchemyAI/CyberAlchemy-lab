"""Planned finite Evidence controls;not an actual unit or whole proof."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 suffixes=['Support','Weakening','Unevaluable','Stale','Mismatch','Assessed','SupportTwo','Outside'];records=['e'+n for n in suffixes];provs=['p'+n for n in suffixes];contents=['content'+n for n in suffixes];claims=['claim','outsideClaim'];subjects=['subject','outsideSubject'];scopes=['scope','outsideScope'];times=['time','oldTime','outsideTime'];conditions=['currentCondition','otherCondition'];assessments=['assessment','outsideAssessment'];tokens=['empty','reference','same-label']
 domains={'EvidenceRecord':records,'Claim':claims,'Subject':subjects,'Scope':scopes,'Provenance':provs,'Time':times,'CurrentnessCondition':conditions,'Content':contents,'Assessment':assessments,'Token':tokens}
 def selected(e,main,outside):return outside if e.endswith('Outside') or e in ['outsideClaim','outsideAssessment'] else main
 maps={'evidenceClaim':lambda e:selected(e,'claim','outsideClaim'),'evidenceSubject':lambda e:selected(e,'subject','outsideSubject'),'evidenceScope':lambda e:selected(e,'scope','outsideScope'),'evidenceProvenance':lambda e:'p'+e[1:],'evidenceTime':lambda e:'oldTime' if e=='eStale' else selected(e,'time','outsideTime'),'evidenceCurrentness':lambda e:'otherCondition' if e=='eStale' or e.endswith('Outside') else 'currentCondition','evidenceContent':lambda e:'content'+e[1:],'evidenceHandle':lambda e:'same-label','claimSubject':lambda c:selected(c,'subject','outsideSubject'),'claimScope':lambda c:selected(c,'scope','outsideScope'),'claimCurrentness':lambda c:'currentCondition' if c=='claim' else 'otherCondition','claimHandle':lambda c:'same-label','subjectHandle':lambda s:'reference','scopeHandle':lambda s:'reference','provenanceHandle':lambda p:'reference','provenanceOriginRef':lambda p:'reference','timeHandle':lambda t:'reference','currentnessHandle':lambda c:'reference','contentHandle':lambda c:'reference','assessmentEvidence':lambda a:'eAssessed' if a=='assessment' else 'eOutside','assessmentClaim':lambda a:selected(a,'claim','outsideClaim'),'assessmentSubject':lambda a:selected(a,'subject','outsideSubject'),'assessmentScope':lambda a:selected(a,'scope','outsideScope'),'assessmentHandle':lambda a:'reference'}
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE};active=records[:-1]
 for n in ['Evidence','ObservationOrRecordDeclared','ProvenanceBoundDeclared','InspectableDeclared']:predicates[n]=[[e] for e in active]
 predicates.update(ClaimExplicit=[['claim']],SubjectDeclared=[['subject']],ScopeDeclared=[['scope']],ProvenanceInspectableDeclared=[[p] for p in provs[:-1]],TimeDeclared=[['time'],['oldTime']],CurrentnessConditionDeclared=[[c] for c in conditions],ContentInspectableDeclared=[[c] for c in contents[:-1]],CurrentClaimDeclared=[['claim']],ApplicableAssessmentDeclared=[['assessment']],StaleDeclared=[['eStale']],MismatchDeclared=[['eMismatch']],ConformanceRoleDeclared=[['eAssessed']],AssessmentIncluded=[['eAssessed','assessment']],SupportDeclared=[[e,'claim','subject','scope'] for e in ['eSupport','eSupportTwo','eAssessed']],WeakeningDeclared=[['eWeakening','claim','subject','scope']],UnevaluableDeclared=[['eUnevaluable','claim','subject','scope']],SilentCurrentSupportDeclared=[['eSupport','claim']])
 return {'domains':domains,'constants':{'EMPTY':'empty'},'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('bounded-records-force-currentness-assessment-without-actual-outcomes',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-'+n,lambda m,n=n:m['predicates']['Actual'+n].append(['eSupport']),I=True)
 add('shared-printed-handles-do-not-collapse-evidence-and-claim',lambda m:None,I=True)
 add('stale-declared-historical-support-is-not-silent-current-support',lambda m:m['predicates']['SupportDeclared'].append(['eStale','claim','subject','scope']),I=True)
 add('mismatched-record-remains-evidence-without-silent-support',lambda m:None,I=True)
 add('force-declarations-need-not-be-disjoint',lambda m:m['predicates']['WeakeningDeclared'].append(['eSupport','claim','subject','scope']),I=True)
 for n in ['DecisionRoleDeclared','AuthorityRoleDeclared','AdmissionRoleDeclared']:add('independently-assessment-qualified-'+n,lambda m,n=n:m['predicates'][n].append(['eAssessed']),I=True)
 add('outside-record-claim-map-not-governing',lambda m:setfn(m,'evidenceClaim','eOutside','claim'),I=True)
 for n in ['ObservationOrRecordDeclared','ProvenanceBoundDeclared','InspectableDeclared']:add('missing-record-'+n,lambda m,n=n:m['predicates'][n].remove(['eSupport']),T=False)
 for n,value in [('ClaimExplicit','claim'),('SubjectDeclared','subject'),('ScopeDeclared','scope'),('ProvenanceInspectableDeclared','pSupport'),('TimeDeclared','time'),('CurrentnessConditionDeclared','currentCondition'),('ContentInspectableDeclared','contentSupport')]:add('missing-selected-'+n,lambda m,n=n,value=value:m['predicates'][n].remove([value]),T=False)
 for n,arg in [('evidenceHandle','eSupport'),('claimHandle','claim'),('subjectHandle','subject'),('scopeHandle','scope'),('provenanceHandle','pSupport'),('provenanceOriginRef','pSupport'),('timeHandle','time'),('currentnessHandle','currentCondition'),('contentHandle','contentSupport')]:add('empty-bound-'+n,lambda m,n=n,arg=arg:setfn(m,n,arg,'empty'),T=False)
 for n,value in [('claimSubject','outsideSubject'),('claimScope','outsideScope')]:add('claim-binding-mismatch-'+n,lambda m,n=n,value=value:setfn(m,n,'claim',value),T=False)
 for n in ['SupportDeclared','WeakeningDeclared','UnevaluableDeclared']:
  for i,value in [(1,'outsideClaim'),(2,'outsideSubject'),(3,'outsideScope')]:
   def extra(m,n=n,i=i,value=value):
    t=['eSupport','claim','subject','scope'];t[i]=value;m['predicates'][n].append(t)
   add('out-of-bound-'+n+'-'+str(i),extra,T=False)
 add('silent-support-without-current-claim',lambda m:m['predicates']['CurrentClaimDeclared'].remove(['claim']),T=False)
 add('silent-support-wrong-claim',lambda m:m['predicates']['SilentCurrentSupportDeclared'].append(['eSupport','outsideClaim']),T=False)
 add('silent-support-wrong-currentness-condition',lambda m:setfn(m,'evidenceCurrentness','eSupport','otherCondition'),T=False)
 for n in ['StaleDeclared','MismatchDeclared']:add('silent-support-with-'+n,lambda m,n=n:m['predicates'][n].append(['eSupport']),T=False)
 add('silent-current-support-without-bounded-support-declaration',lambda m:m['predicates']['SupportDeclared'].remove(['eSupport','claim','subject','scope']),T=False)
 for n in ['ClaimItselfRole','ProofByExistenceRole']:add('excluded-role-'+n,lambda m,n=n:m['predicates'][n].append(['eSupport']),T=False)
 for n in ['DecisionRoleDeclared','AuthorityRoleDeclared','AdmissionRoleDeclared','ConformanceRoleDeclared']:add('role-without-applicable-assessment-'+n,lambda m,n=n:m['predicates'][n].append(['eSupport']),T=False)
 add('included-assessment-not-applicable',lambda m:m['predicates']['ApplicableAssessmentDeclared'].remove(['assessment']),T=False)
 for n,value in [('assessmentEvidence','eSupport'),('assessmentClaim','outsideClaim'),('assessmentSubject','outsideSubject'),('assessmentScope','outsideScope')]:add('wrong-assessment-'+n,lambda m,n=n,value=value:setfn(m,n,'assessment',value),T=False)
 add('assessment-handle-empty',lambda m:setfn(m,'assessmentHandle','assessment','empty'),T=False)
 add('no-weakening-example-T-without-I',lambda m:m['predicates'].update(WeakeningDeclared=[]),I=False)
 add('no-silent-current-support-example-T-without-I',lambda m:m['predicates'].update(SilentCurrentSupportDeclared=[]),I=False)
 add('no-assessment-qualified-role-example-T-without-I',lambda m:m['predicates'].update(ConformanceRoleDeclared=[]),I=False)
 add('missing-total-provenance-entry',lambda m:m['functions']['evidenceProvenance'].pop(),error='nontotal-function')
 add('ill-sorted-evidence-claim-result',lambda m:setfn(m,'evidenceClaim','eSupport','subject'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='claim'),error='ill-sorted-constant')
 add('wrong-support-relation-arity',lambda m:m['predicates'].update(SupportDeclared=[['eSupport','claim','scope']]),error='ill-sorted-model-tuple')
 add('duplicate-assessment-inclusion-tuple',lambda m:m['predicates']['AssessmentIncluded'].append(['eAssessed','assessment']),error='duplicate-predicate-tuple')
 add('empty-provenance-domain',lambda m:m['domains'].update(Provenance=[]),error='empty-or-malformed-domain')
 add('duplicate-currentness-function-tuple',lambda m:m['functions']['evidenceCurrentness'].append(copy.deepcopy(m['functions']['evidenceCurrentness'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.evaluation/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Evidence-model-controls/v1-candidate','status':'PASS-for-exact-authored-Evidence-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Declared provenance-bound inspectable records with explicit claim/subject/scope,scoped force,currentness and applicable-assessment guards checked on supplied models. Existence/collection/volume and handles do not create actual proof,truth,adequacy,provenance,currentness,conformance,admission or authority. Accepted claim/scope/assessment/consumer maps and owner fidelity remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
