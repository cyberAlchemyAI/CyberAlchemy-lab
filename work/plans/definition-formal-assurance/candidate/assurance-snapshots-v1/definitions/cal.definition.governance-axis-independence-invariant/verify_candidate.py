"""Independent supplied Governance-Axis posture,information,frame,record and inference controls."""
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
 constants={n:n.lower() for n in b.CONSTANTS};constants.update(MEANING_ID='semantic-governance-axis-independence',MEANING_KIND='invariant-kind',MEANING_CARRIER='type-invariant',MEANING_SCOPE='shared-authority',SOURCE_D23='cav2-d23')
 axes=[n.lower() for n in b.AXES]+['custom'];moves=['mStatus','mEvidence','mOwner','mInfo','mExtra','mReaffirm','mUnrecorded'];records=['r'+x[1:] for x in moves];posts=['p1','p2','p3','p4','pStatus','pEvidence','pOwner','pInfo','pExtra','pUnrecorded'];arts=['a1','a2','a3','a4'];domains={'Invariant':['inv1'],'Artifact':arts,'Posture':posts,'Move':moves,'Axis':axes,'Value':[constants[n] for n,s in b.CONSTANTS.items() if s=='Value'],'InfoState':[n.lower() for n in b.STATES],'ChangeRecord':records,'Scope':['scope1','scope2'],'Token':[constants[n] for n,s in b.CONSTANTS.items() if s=='Token']+['local-reference','opaque']}
 after={'mStatus':'pStatus','mEvidence':'pEvidence','mOwner':'pOwner','mInfo':'pInfo','mExtra':'pExtra','mReaffirm':'p1','mUnrecorded':'pUnrecorded'};intended={'mStatus':'status','mEvidence':'evidence','mOwner':'owner','mInfo':'status','mExtra':'status','mReaffirm':'status','mUnrecorded':'status'};recordmap=dict(zip(moves,records));recordmove=dict(zip(records,moves));subject={p:('a'+p[1:] if p in ['p1','p2','p3','p4'] else 'a1') for p in posts}
 def value(p,axis):
  table={('p1','status'):'mature',('p1','evidence'):'weak',('p2','kind'):'imported',('p2','evidence'):'well',('p3','kind'):'ontology_candidate',('p4','kind'):'hypothesis',('p4','commitment'):'committed'}
  if p not in ['p1','p2','p3','p4']:
   if (p,axis) in {('pStatus','status'),('pOwner','owner'),('pExtra','status'),('pExtra','custom'),('pUnrecorded','status')}:return 'new_value'
   if p in ['pEvidence','pOwner','pUnrecorded'] and axis=='evidence':return 'well'
   return table.get(('p1',axis),'old_value')
  return table.get((p,axis),'old_value')
 def info(p,axis):return 'source_local' if (p,axis)==('p2','provenance') else 'unknown' if (p,axis)==('p3','residue') else 'deferred' if (p,axis)==('pInfo','status') else 'known'
 def source(p,axis):return 'local-reference' if (p,axis)==('p2','provenance') else 'empty'
 meta=dict(zip(['invariantIdentity','invariantKind','invariantCarrier','invariantOwnerScope','invariantSourceD23'],['MEANING_ID','MEANING_KIND','MEANING_CARRIER','MEANING_SCOPE','SOURCE_D23']));maps={n:(lambda i,n=n:constants[meta[n]]) for n in meta};maps.update(artifactScope=lambda a:'scope1',L=lambda a:'p'+a[1:],postureSubject=lambda p:subject[p],postureScope=lambda p:'scope1',componentValue=value,componentInfo=info,componentSource=source,moveInvariant=lambda m:'inv1',moveSubject=lambda m:'a1',before=lambda m:'p1',after=lambda m:after[m],intendedAxis=lambda m:intended[m],moveScope=lambda m:'scope1',moveRecord=lambda m:recordmap[m],recordSubject=lambda r:'a1',recordScope=lambda r:'scope1',recordBefore=lambda r:'p1',recordAfter=lambda r:after[recordmove[r]])
 for side in ['Before','After']:
  for part,calc in [('Value',value),('Info',info),('Source',source)]:maps['record'+side+part]=lambda r,axis,side=side,calc=calc:calc('p1' if side=='Before' else after[recordmove[r]],axis)
 functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};p={n:[] for n in b.SIGNATURE};p.update(GovernanceAxisInvariant=[['inv1']],PreservesClassification=[['inv1']],PreservesSourceRelations=[['inv1']],NotSilentlyMerged=[['inv1']],AuthorityBearingArtifact=[[a] for a in arts],LifecyclePosture=[[p] for p in posts],GovernanceMove=[[m] for m in moves],ValidMove=[[m] for m in moves[:5]],IdempotentReaffirmation=[['mReaffirm']],CoreAxis=[[a] for a in axes[:-1]],AllowedInfoState=[[s] for s in domains['InfoState']],RecordedGovernanceRecord=[['rOwner'],['rExtra']],RecordedAxisChange=[['rOwner','evidence'],['rExtra','custom']],DeclaredAdditionalAxis=[['mExtra','custom']],AppliesAxis=[[m,a] for m in moves for a in axes[:-1]]+[['mExtra','custom']],ComponentDeclared=[[p,a] for p in posts for a in axes[:-1]]+[['p1','custom'],['pExtra','custom']],DeclaredUseful=[['a3']])
 for n,(axis,code) in b.TRAIT_CODES.items():p[n]=[[a] for a in arts if value('p'+a[1:],axis.lower())==constants[code]]
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':p}
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('core-seven-info-states-intended-only-recorded-extra-and-source-patterns',lambda m:None,I=True)
 for prefix,names,subject in [('Invariant',b.INV_OUTCOMES,'inv1'),('Move',b.MOVE_OUTCOMES,'mStatus'),('Artifact',b.ART_OUTCOMES,'a2')]:
  for n in names:add('independent-'+prefix+'-actual-'+n,lambda m,n=n,prefix=prefix,subject=subject:m['predicates'][prefix+'Actual'+n].append([subject]))
 for n in ['PreservesClassification','PreservesSourceRelations','NotSilentlyMerged']:add('missing-normalized-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['invariantIdentity','invariantKind','invariantCarrier','invariantOwnerScope','invariantSourceD23']:add('wrong-normalized-'+n,lambda m,n=n:setfn(m,n,'inv1','opaque'),T=False)
 for n in b.AXES:add('missing-core-axis-'+n,lambda m,n=n:m['predicates']['CoreAxis'].remove([n.lower()]),T=False)
 for n in b.AXES[1:]:add('aliased-core-axis-'+n,lambda m,n=n:m['constants'].update({n:'kind'}),T=False)
 for n in b.STATES[1:]:add('aliased-information-state-'+n,lambda m,n=n:m['constants'].update({n:'known'}),T=False)
 for n in b.STATES:add('missing-allowed-information-state-'+n,lambda m,n=n:m['predicates']['AllowedInfoState'].remove([n.lower()]),T=False)
 for n in b.AXES:add('missing-core-component-'+n,lambda m,n=n:m['predicates']['ComponentDeclared'].remove(['p1',n.lower()]),T=False)
 add('source-local-without-source-reference',lambda m:setfn(m,'componentSource',['p2','provenance'],'empty'),T=False)
 add('unknown-information-treated-as-false',lambda m:m['predicates']['UnknownTreatedAsFalse'].append(['p3']),T=False)
 add('unknown-component-value-may-change-without-becoming-false',lambda m:setfn(m,'componentValue',['p3','residue'],'new_value'),I=True)
 add('unknown-information-witness-is-separate-population',lambda m:setfn(m,'componentInfo',['p3','residue'],'known'),I=False)
 add('wrong-L-posture-subject',lambda m:setfn(m,'postureSubject','p1','a2'),T=False)
 add('wrong-L-posture-scope',lambda m:setfn(m,'postureScope','p1','scope2'),T=False)
 add('missing-authority-bearing-subject',lambda m:m['predicates']['AuthorityBearingArtifact'].remove(['a1']),T=False)
 add('missing-lifecycle-before-posture',lambda m:m['predicates']['LifecyclePosture'].remove(['p1']),T=False)
 add('wrong-move-before-subject',lambda m:setfn(m,'before','mStatus','p2'),T=False)
 add('wrong-move-after-subject',lambda m:setfn(m,'after','mStatus','p2'),T=False)
 add('wrong-move-subject',lambda m:setfn(m,'moveSubject','mStatus','a2'),T=False)
 add('wrong-artifact-scope',lambda m:setfn(m,'artifactScope','a1','scope2'),T=False)
 add('wrong-move-scope',lambda m:setfn(m,'moveScope','mStatus','scope2'),T=False)
 add('undeclared-intended-extra-axis',lambda m:setfn(m,'intendedAxis','mStatus','custom'),T=False)
 add('missing-exact-applicable-axis',lambda m:m['predicates']['AppliesAxis'].remove(['mStatus','kind']),T=False)
 add('missing-additional-axis-declaration-but-old-applicability',lambda m:m['predicates']['DeclaredAdditionalAxis'].clear(),T=False)
 def unselect_extra(m):m['predicates']['DeclaredAdditionalAxis'].clear();m['predicates']['AppliesAxis'].remove(['mExtra','custom'])
 add('unselected-extra-axis-not-a-complete-schema-claim',unselect_extra,I=False)
 add('recorded-other-change-without-record-presence',lambda m:m['predicates']['RecordedGovernanceRecord'].remove(['rOwner']),T=False)
 add('recorded-other-change-without-axis-entry',lambda m:m['predicates']['RecordedAxisChange'].remove(['rOwner','evidence']),T=False)
 for n,value in [('recordSubject','a2'),('recordScope','scope2'),('recordBefore','p2'),('recordAfter','p2')]:add('wrong-additional-record-'+n,lambda m,n=n,value=value:setfn(m,n,'rOwner',value),T=False)
 for side in ['Before','After']:
  for part,value in [('Value','new_value' if side=='Before' else 'old_value'),('Info','unknown'),('Source','opaque')]:add('wrong-additional-record-'+side+part,lambda m,n='record'+side+part,value=value:setfn(m,n,['rExtra','custom'],value),T=False)
 add('unchanged-intended-value-not-a-valid-move',lambda m:setfn(m,'componentValue',['pStatus','status'],'mature'),T=False)
 add('unchanged-intended-information-not-a-valid-move',lambda m:setfn(m,'componentInfo',['pInfo','status'],'known'),T=False)
 def source_only(m):setfn(m,'componentValue',['pStatus','status'],'mature');setfn(m,'componentSource',['pStatus','status'],'local-reference')
 add('intended-source-binding-change-counts-provisionally',source_only,I=True)
 add('idempotent-reaffirmation-marked-valid',lambda m:m['predicates']['ValidMove'].append(['mReaffirm']),T=False)
 add('coherent-records-do-not-force-validity',lambda m:m['predicates']['ValidMove'].clear(),I=False)
 add('unrecorded-additional-change-marked-valid',lambda m:m['predicates']['ValidMove'].append(['mUnrecorded']),T=False)
 def recorded_repair(m):m['predicates']['ValidMove'].append(['mUnrecorded']);m['predicates']['RecordedGovernanceRecord'].append(['rUnrecorded']);m['predicates']['RecordedAxisChange'].append(['rUnrecorded','evidence'])
 add('declared-explicit-record-repairs-extra-change-not-actual-authority',recorded_repair)
 for axis in [n.lower() for n in b.AXES if n!='STATUS']:add('unrecorded-other-axis-value-'+axis,lambda m,axis=axis:setfn(m,'componentValue',['pStatus',axis],'new_value'),T=False)
 add('unrecorded-other-axis-info-change',lambda m:setfn(m,'componentInfo',['pStatus','evidence'],'unknown'),T=False)
 add('unrecorded-other-axis-source-reference-change',lambda m:setfn(m,'componentSource',['pStatus','provenance'],'local-reference'),T=False)
 def extra_info_record(m):
  setfn(m,'componentInfo',['pExtra','custom'],'source_local');setfn(m,'componentSource',['pExtra','custom'],'local-reference');setfn(m,'recordAfterInfo',['rExtra','custom'],'source_local');setfn(m,'recordAfterSource',['rExtra','custom'],'local-reference')
 add('explicit-extra-axis-source-local-information-record',extra_info_record,I=True)
 for ax in [n.lower() for n in b.AXES]:
  for other in [n.lower() for n in b.AXES if n.lower()!=ax]:add('silent-cross-axis-'+ax+'-to-'+other,lambda m,ax=ax,other=other:m['predicates']['SilentAxisSubstitution'].append(['mStatus',ax,other]),T=False)
 add('same-axis-marker-is-not-cross-axis-substitution',lambda m:m['predicates']['SilentAxisSubstitution'].append(['mStatus','status','status']),I=True)
 for n in b.COLLAPSED+b.INFER_FLAGS:add('forbidden-invariant-collapse-or-inference-'+n,lambda m,n=n:m['predicates'][n].append(['inv1']),T=False)
 add('missing-component-value-table-entry',lambda m:m['functions']['componentValue'].pop(),error='nontotal-function')
 add('ill-sorted-information-result',lambda m:setfn(m,'componentInfo',['p1','status'],'a1'),error='ill-sorted-function-result')
 add('ill-sorted-core-axis-constant',lambda m:m['constants'].update(STATUS='a1'),error='ill-sorted-constant')
 add('wrong-applicability-arity',lambda m:m['predicates'].update(AppliesAxis=[['mStatus']]),error='ill-sorted-model-tuple')
 add('duplicate-valid-move-tuple',lambda m:m['predicates']['ValidMove'].append(['mStatus']),error='duplicate-predicate-tuple')
 add('empty-axis-domain',lambda m:m['domains'].update(Axis=[]),error='empty-or-malformed-domain')
 add('duplicate-component-table-entry',lambda m:m['functions']['componentValue'].append(copy.deepcopy(m['functions']['componentValue'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.gate/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-GAI-model-controls/v1-candidate','status':'PASS-for-exact-authored-GAI-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed normalized invariant,core lifecycle/info states and necessary scoped move/frame/exact-record guards checked on authored models. Actual component meanings,universal independence,authority,record writes,transition execution,owner and consumer alignment remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
