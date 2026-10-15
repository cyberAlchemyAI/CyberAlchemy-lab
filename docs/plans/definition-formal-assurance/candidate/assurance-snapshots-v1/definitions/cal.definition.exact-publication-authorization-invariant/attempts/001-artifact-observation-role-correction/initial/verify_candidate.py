"""Independent typed two-decision,exact-binding,private-default and source-query controls."""
import copy,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def fval(m,n,arg):return next(x['value'] for x in m['functions'][n] if x['args']==[arg])
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def has(m,n,*args):return list(args) in m['predicates'][n]
def recompute(m):
 p=m['predicates'];releases=[];approvals=[];pub=[]
 for r in m['domains']['Release']:
  for q in m['domains']['Request']:
   if has(m,'ReleaseDeclaredValid',r) and fval(m,'releasePublisher',r)==fval(m,'qPublisher',q) and fval(m,'releaseEpoch',r)==fval(m,'sourceEpoch',fval(m,'releaseSource',r)) and all(fval(m,'release'+n,r)==fval(m,'q'+n,q) for n in b.RELEASE_TOKEN_FIELDS):releases.append([r,q])
 p['ReleaseFor']=releases
 for a in m['domains']['Approval']:
  for q in m['domains']['Request']:
   sources=[s for s in m['domains']['Source'] if has(m,'Contributes',s,fval(m,'qOutput',q))]
   covered=all(any([r,q] in releases and fval(m,'releaseSource',r)==s and has(m,'ApprovalReferences',a,r) for r in m['domains']['Release']) for s in sources)
   if has(m,'ApprovalDeclaredValid',a) and has(m,'Generated',q) and has(m,'PrivacyPass',q) and fval(m,'approvalOutput',a)==fval(m,'qOutput',q) and fval(m,'approvalPublisher',a)==fval(m,'qPublisher',q) and all(fval(m,'approval'+n,a)==fval(m,'q'+n,q) for n in b.APPROVAL_TOKEN_FIELDS) and covered:approvals.append([a,q])
 p['ExactApprovalFor']=approvals
 for q in m['domains']['Request']:
  sources=[s for s in m['domains']['Source'] if has(m,'Contributes',s,fval(m,'qOutput',q))];covered=all(any([r,q] in releases and fval(m,'releaseSource',r)==s for r in m['domains']['Release']) for s in sources)
  if covered and has(m,'PrivacyPass',q) and any([a,q] in approvals for a in m['domains']['Approval']):pub.append([q])
 p['Publishable']=pub;p['HasPublicationReceipt']=[[q] for q in m['domains']['Request'] if any(has(m,'PublicationReceipt',r) and fval(m,'receiptRequest',r)==q for r in m['domains']['Receipt'])]
def base_model():
 constants={'EMPTY':'empty','EXACT_ID':'exact-id','INVARIANT_KIND':'invariant-kind','INVARIANT_CARRIER':'invariant-carrier','REPOSITORY_SCOPE':'repository-scope','CAV2_D57':'cav2-d57'};fieldvals={n:n.lower() for n in b.REQUEST_TOKEN_FIELDS};fieldvals['Bytes']='final-bytes';fieldvals['Digest']='final-digest'
 tokens=list(constants.values())+list(fieldvals.values())+['draft-bytes','draft-digest','source-a-epoch','source-b-epoch','opaque']
 domains={'Invariant':['invariant1'],'Request':['ready','draft'],'Output':['final-output','draft-output'],'Source':['sourceA','sourceB'],'Release':['releaseA','releaseB'],'Approval':['exactApproval','refusedApproval'],'Receipt':['draftReceipt','unusedReceipt'],'Principal':['ownerA','ownerB','publisher','tool'],'Token':tokens}
 maps={n:(lambda i,n=n:constants[{'invariantIdentity':'EXACT_ID','invariantKind':'INVARIANT_KIND','invariantCarrier':'INVARIANT_CARRIER','invariantOwnerScope':'REPOSITORY_SCOPE','invariantSource':'CAV2_D57'}[n]]) for n in ['invariantIdentity','invariantKind','invariantCarrier','invariantOwnerScope','invariantSource']};maps.update(qOutput=lambda q:'final-output' if q=='ready' else 'draft-output',qPublisher=lambda q:'publisher',sourceOwner=lambda s:'ownerA' if s=='sourceA' else 'ownerB',sourceEpoch=lambda s:'source-a-epoch' if s=='sourceA' else 'source-b-epoch',releaseSource=lambda r:'sourceA' if r=='releaseA' else 'sourceB',releaseOwner=lambda r:'ownerA' if r=='releaseA' else 'ownerB',releasePublisher=lambda r:'publisher',releaseEpoch=lambda r:'source-a-epoch' if r=='releaseA' else 'source-b-epoch',approvalOutput=lambda a:'final-output' if a=='exactApproval' else 'draft-output',approvalPublisher=lambda a:'publisher',receiptRequest=lambda r:'draft')
 for n in b.REQUEST_TOKEN_FIELDS:maps['q'+n]=lambda q,n=n:('draft-'+n.lower() if q=='draft' and n in ['Bytes','Digest'] else fieldvals[n])
 for n in b.RELEASE_TOKEN_FIELDS:maps['release'+n]=lambda r,n=n:fieldvals[n]
 for n in b.APPROVAL_TOKEN_FIELDS:maps['approval'+n]=lambda a,n=n:('draft-'+n.lower() if a=='refusedApproval' and n in ['Bytes','Digest'] else fieldvals[n])
 functions={n:[{'args':[e],'value':maps[n](e)} for e in domains[args[0]]] for n,(args,result) in b.FUNCTIONS.items()};p={n:[] for n in b.SIGNATURE};p.update(ExactPublicationAuthorizationInvariant=[['invariant1']],PreservesClassification=[['invariant1']],PreservesSourceRelations=[['invariant1']],NotSilentlyMerged=[['invariant1']],SourceOwnerRole=[['ownerA'],['ownerB']],PublisherRole=[['publisher'],['ownerB']],GeneratorPrincipal=[['tool']],ValidatorPrincipal=[['tool']],ReleaseDecision=[['releaseA'],['releaseB']],ReleaseDeclaredValid=[['releaseA'],['releaseB']],OutputApprovalDecision=[['exactApproval'],['refusedApproval']],ApprovalDeclaredValid=[['exactApproval']],ApprovalApprove=[['exactApproval']],ApprovalRefuse=[['refusedApproval']],PrivacyPass=[['ready']],PrivateDefault=[['ready'],['draft']],PublicationReceipt=[['draftReceipt']],Contributes=[[s,o] for s in domains['Source'] for o in domains['Output']],ApprovalReferences=[['exactApproval','releaseA'],['exactApproval','releaseB']])
 for n in b.PRODUCERS:p[n]=[['draft']]
 p['Generated'].append(['ready']);m={'domains':domains,'constants':constants,'functions':functions,'predicates':p};recompute(m);return m
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('two-exact-owner-releases-privacy-and-exact-output-approval',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-actual-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['ready']),I=False if n in b.OUTCOMES else None)
 for n in ['PreservesClassification','PreservesSourceRelations','NotSilentlyMerged']:add('missing-normalized-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['invariantIdentity','invariantKind','invariantCarrier','invariantOwnerScope','invariantSource']:add('wrong-normalized-'+n,lambda m,n=n:setfn(m,n,'invariant1','opaque'),T=False)
 add('normalized-invariant-omitted',lambda m:m['predicates']['ExactPublicationAuthorizationInvariant'].clear(),T=False)
 for n in b.RELEASE_TOKEN_FIELDS:
  add('empty-release-'+n,lambda m,n=n:setfn(m,'release'+n,'releaseA','empty'),T=False)
  add('release-'+n+'-mismatch-with-stale-match',lambda m,n=n:setfn(m,'release'+n,'releaseA','opaque'),T=False)
 for n in b.APPROVAL_TOKEN_FIELDS:
  add('empty-approval-'+n,lambda m,n=n:setfn(m,'approval'+n,'exactApproval','empty'),T=False)
  add('approval-'+n+'-mismatch-with-stale-approval',lambda m,n=n:setfn(m,'approval'+n,'exactApproval','opaque'),T=False)
 for n in b.REQUEST_TOKEN_FIELDS:
  add('request-'+n+'-change-expires-permission',lambda m,n=n:(setfn(m,'q'+n,'ready','opaque'),recompute(m)),I=False)
 add('source-owner-mismatch',lambda m:setfn(m,'releaseOwner','releaseA','ownerB'),T=False)
 add('release-publisher-role-missing',lambda m:m['predicates']['PublisherRole'].remove(['publisher']),T=False)
 add('source-owner-role-missing',lambda m:m['predicates']['SourceOwnerRole'].remove(['ownerA']),T=False)
 add('release-valid-without-decision',lambda m:m['predicates']['ReleaseDecision'].remove(['releaseA']),T=False)
 add('revoked-release-retains-valid-marker',lambda m:m['predicates']['ReleaseRevoked'].append(['releaseA']),T=False)
 add('release-revocation-invalidates-current-permission',lambda m:(m['predicates']['ReleaseDeclaredValid'].remove(['releaseA']),m['predicates']['ReleaseRevoked'].append(['releaseA']),recompute(m)),I=False)
 add('changed-source-epoch-invalidates-owner-release',lambda m:(setfn(m,'sourceEpoch','sourceA','opaque'),recompute(m)),I=False)
 add('uncovered-contributing-source-invalidates-permission',lambda m:(m['predicates']['ReleaseDeclaredValid'].remove(['releaseB']),recompute(m)),I=False)
 add('owner-release-does-not-bind-future-bytes',lambda m:(setfn(m,'qBytes','ready','opaque'),setfn(m,'qDigest','ready','opaque'),recompute(m)),I=False)
 add('approval-valid-without-approval-record',lambda m:m['predicates']['OutputApprovalDecision'].remove(['exactApproval']),T=False)
 add('approval-valid-without-approve-choice',lambda m:m['predicates']['ApprovalApprove'].clear(),T=False)
 add('approval-valid-with-refusal',lambda m:m['predicates']['ApprovalRefuse'].append(['exactApproval']),T=False)
 add('approval-revoked-but-valid',lambda m:m['predicates']['ApprovalRevoked'].append(['exactApproval']),T=False)
 add('approval-withdrawal-reverts-to-private-permission-absent',lambda m:(m['predicates']['ApprovalDeclaredValid'].clear(),recompute(m)),I=False)
 add('approval-output-mismatch',lambda m:setfn(m,'approvalOutput','exactApproval','draft-output'),T=False)
 add('approval-publisher-mismatch',lambda m:setfn(m,'approvalPublisher','exactApproval','ownerB'),T=False)
 add('approval-missing-one-source-release-reference',lambda m:(m['predicates']['ApprovalReferences'].remove(['exactApproval','releaseB']),recompute(m)),I=False)
 add('privacy-pass-does-not-supply-missing-final-approval',lambda m:(m['predicates']['PrivacyPass'].append(['draft']),recompute(m)),I=True)
 add('privacy-pass-removal-invalidates-ready-permission',lambda m:(m['predicates']['PrivacyPass'].clear(),recompute(m)),I=False)
 add('generation-removal-invalidates-exact-approval',lambda m:(m['predicates']['Generated'].remove(['ready']),recompute(m)),I=False)
 add('asserted-publishability-without-privacy-approval',lambda m:m['predicates']['Publishable'].append(['draft']),T=False)
 add('all-contributors-vacuous-empty-source-set-exposes-closure-obligation',lambda m:(m['predicates']['Contributes'].clear(),recompute(m)),I=False)
 add('private-default-missing-without-permission',lambda m:m['predicates']['PrivateDefault'].remove(['draft']),T=False)
 add('permission-may-remain-private',lambda m:None,I=True)
 add('publication-receipt-does-not-grant-missing-permission',lambda m:None,I=True)
 add('missing-optional-receipt-does-not-revoke-permission',lambda m:(m['predicates']['PublicationReceipt'].clear(),recompute(m)),I=False)
 add('receipt-retargeting-does-not-change-permission',lambda m:(setfn(m,'receiptRequest','draftReceipt','ready'),recompute(m)),I=False)
 for role,assigned in [('SourceOwnerRole','ExplicitOwnerAssignment'),('PublisherRole','ExplicitPublisherAssignment')]:
  add('tool-cannot-assume-'+role,lambda m,role=role:m['predicates'][role].append(['tool']),T=False)
  add('separate-explicit-tool-'+role+'-assignment-allowed',lambda m,role=role,assigned=assigned:(m['predicates'][role].append(['tool']),m['predicates'][assigned].append(['tool'])),I=True)
 def sameprincipal(m):
  m['predicates']['PublisherRole'].append(['ownerA'])
  for n,sort in [('qPublisher','Request'),('releasePublisher','Release'),('approvalPublisher','Approval')]:
   for e in m['domains'][sort]:setfn(m,n,e,'ownerA')
  recompute(m)
 add('distinct-authority-roles-may-use-one-principal',sameprincipal,I=True)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['ready']),T=False)
 add('missing-function-value',lambda m:m['functions']['qDigest'].pop(),error='nontotal-function')
 add('ill-sorted-request-output',lambda m:setfn(m,'qOutput','ready','publisher'),error='ill-sorted-function-result')
 add('ill-sorted-invariant-identity-constant',lambda m:m['constants'].update(EXACT_ID='ready'),error='ill-sorted-constant')
 add('wrong-approval-relation-arity',lambda m:m['predicates'].update(ExactApprovalFor=[['exactApproval']]),error='ill-sorted-model-tuple')
 add('duplicate-release-match-tuple',lambda m:m['predicates']['ReleaseFor'].append(['releaseA','ready']),error='duplicate-predicate-tuple')
 add('empty-request-domain',lambda m:m['domains'].update(Request=[]),error='empty-or-malformed-domain')
 add('duplicate-q-output-function-tuple',lambda m:m['functions']['qOutput'].append(copy.deepcopy(m['functions']['qOutput'][0])),error='duplicate-function-tuple')
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
    report={'schema_version':'definition-assurance-ExactPublicationAuthorizationInvariant-model-controls/v1-candidate','status':'PASS-for-exact-authored-ExactPublicationAuthorizationInvariant-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent declared ExactPublicationAuthorizationInvariant kind/subject/actor/scope and scoped stage facts;actual authorization,delivery,observation,trace,owner and consumer/source-owner maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
