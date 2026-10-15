"""Supplied aggregate/home,carrier,facet,index and movement models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
def getfn(m,n,*args):return next(x['value'] for x in m['functions'][n] if x['args']==list(args))
def refresh(m):
 p=m['predicates'];arts=[x[0] for x in p['ArtifactApplicable']]
 for n in b.FACETS:p[n+'BindingDeclared']=[[a,getfn(m,n,a)] for a in arts]
 origins=[getfn(m,'artifactOrigin',a) for a in arts]
 for n in b.ORIGIN_FIELDS:p[n+'BindingDeclared']=[[o,getfn(m,n,o)] for o in origins]
def base_model():
 labels=['Declared','Authority','Integrity','Future','Blocked','BlockedAuthority','Outside'];ds={s:[] for s in b.SORTS}
 prefixes={'ArtifactReference':'a','RepresentationReference':'rep','OriginRecordReference':'origin','OriginStatementReference':'statement','ArtifactStateReference':'state','ReceiptReference':'receipt','ActorReference':'actor','IdentityPolicyReference':'policy','SignatureReference':'signature','SemanticIdentity':'id'}
 for s,prefix in prefixes.items():ds[s]=[prefix+x for x in labels]
 ds['SemanticIdentity']+=['invariantIdentity','artifactSiblingIdentity'];ds.update(InvariantReference=['invariantMain','invariantOther'],CanonicalKind=['kindFine','kindCoarse','kindOutside'],AuthorityKind=['authorityMain','authorityOutside'],Durability=['durableMain','durableOutside'],OwnerReference=['ownerMain','ownerOutside'],ProducerReference=['producerMain','producerAlternative','producerCandidate'],ProcessReference=['processMain','processOutside'],ProcessVersionReference=['versionMain','versionOutside'],AssuranceLevel=['declared','integrity','actorAttested','unknownLevel'],SourceReference=['sourceApproved','sourceD51','sourceOutside'],ProjectionReference=['projectionHuman','projectionLabel','projectionOutside'],DirectoryReference=['directoryMain','directoryOutside'],ScopeReference=['sharedScope','outsideScope'],TypeReference=['documentType','invariantType','outsideType'],Token=['empty','none','reference'])
 cs={'EMPTY':'empty','NONE':'none','CURRENT_INVARIANT':'invariantMain','INVARIANT_TARGET':'invariantIdentity','ARTIFACT_SIBLING':'artifactSiblingIdentity','SHARED_SCOPE':'sharedScope','INVARIANT_TYPE':'invariantType','D51_SOURCE':'sourceD51','DECLARED':'declared','INTEGRITY':'integrity','ACTOR':'actorAttested'}
 suffix=lambda x,prefix:x[len(prefix):];art=lambda x,prefix:'a'+suffix(x,prefix)
 maps={n:(lambda a,n=n,s=s:'none' if s=='Token' else 'kindCoarse' if n=='artifactKind' and a=='aAuthority' else 'kindFine' if n=='artifactKind' else 'authorityMain' if n=='artifactAuthorityKind' else 'durableMain' if n=='artifactDurability' else 'ownerMain' if n=='artifactOwner' else 'sourceApproved' if n=='artifactOriginSource' else 'integrity' if n=='artifactAssurance' and a=='aIntegrity' else 'actorAttested' if n=='artifactAssurance' and a=='aFuture' else 'declared' if n=='artifactAssurance' else 'invariantMain' if n=='artifactInvariant' else 'directoryMain' if n=='artifactDirectory' else 'documentType' if n=='artifactType' else prefixes[s]+suffix(a,'a')) for n,s in b.FACETS.items()}
 maps.update(originArtifact=lambda o:art(o,'origin'),originProducer=lambda o:'producerCandidate' if suffix(o,'origin') in ['Blocked','BlockedAuthority'] else 'producerMain',originProcess=lambda o:'processMain',originVersion=lambda o:'versionMain',originStatement=lambda o:'statement'+suffix(o,'origin'),originOwner=lambda o:'ownerMain')
 maps.update(invariantIdentity=lambda x:'invariantIdentity',invariantScope=lambda x:'sharedScope',invariantType=lambda x:'invariantType',invariantSource=lambda x:'sourceD51',representationArtifact=lambda x:art(x,'rep'),representationState=lambda x:'state'+suffix(x,'rep'),representationType=lambda x:'documentType',kindAuthority=lambda x:'authorityMain',kindDurability=lambda x:'durableMain',kindType=lambda x:'documentType',kindOriginSource=lambda x:'sourceApproved',authorityKindCanonical=lambda x:'kindCoarse' if x=='authorityMain' else 'kindOutside',receiptStatement=lambda x:'statement'+suffix(x,'receipt'),receiptState=lambda x:'state'+suffix(x,'receipt'),receiptActor=lambda x:'actor'+suffix(x,'receipt'),receiptPolicy=lambda x:'policy'+suffix(x,'receipt'),receiptSignature=lambda x:'signature'+suffix(x,'receipt'),signatureStatement=lambda x:'statement'+suffix(x,'signature'),signatureState=lambda x:'state'+suffix(x,'signature'),signatureActor=lambda x:'actor'+suffix(x,'signature'),projectionArtifact=lambda x:'aDeclared' if x!='projectionOutside' else 'aOutside',projectionSource=lambda x:'repDeclared' if x!='projectionOutside' else 'repOutside',projectionEffect=lambda x:'none')
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys(),(maps.keys()-b.FUNCTIONS.keys(),b.FUNCTIONS.keys()-maps.keys())
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};p={n:[] for n in b.SIGNATURE}
 for s in b.SORTS:
  if s not in ['ArtifactReference','Token']:p[s+'Declared']=[[x] for x in ds[s] if not x.endswith('Outside')]
 selected=['a'+x for x in labels[:-1]];canonical=['a'+x for x in labels[:4]]
 p['ArtifactApplicable']=[[a] for a in selected];p['ArtifactInScopeDeclared']=[[a] for a in selected];p['CanonicalDeclared']=[[a] for a in canonical];p['AllowedOriginDeclared']=[[a] for a in canonical];p['HonestAssuranceDeclared']=[[a] for a in selected];p['OwnerOriginAdmittedDeclared']=[[a] for a in selected];p['CurrentReviewArtifactDeclared']=[[a] for a in selected if a!='aFuture']
 p['MachineCanonicalDeclared']=[[a,maps['artifactMachine'](a)] for a in selected];p['OriginRecordForDeclared']=[[a,maps['artifactOrigin'](a)] for a in selected];p['CanonicalKindMemberDeclared']=[['kindFine'],['kindCoarse']];p['AuthorityKindMemberDeclared']=[['authorityMain']];p['AuthorityKindCanonicalBindingDeclared']=[['authorityMain','kindCoarse']];p['KindOriginSourceBindingDeclared']=[[k,'sourceApproved'] for k in ['kindFine','kindCoarse']]
 p['AllowedTupleDeclared']=[[k,producer,'processMain','versionMain','sourceApproved'] for k in ['kindFine','kindCoarse'] for producer in ['producerMain','producerAlternative']];p['SourceCurrentDeclared']=[['sourceApproved']];p['SourceOwnerApprovedDeclared']=[['sourceApproved']];p['ProducerAdmittedDeclared']=[['producerMain'],['producerAlternative']];p['ProducerCandidateOnlyDeclared']=[['producerCandidate']]
 p['OwnerStatementDeclared']=[['ownerMain','statement'+x] for x in ['Declared','Authority','Blocked','BlockedAuthority']];p['L1ReceiptValidDeclared']=[['receiptIntegrity']];p['L2ReceiptValidDeclared']=[['receiptFuture']];p['IdentifiedActorDeclared']=[['actorFuture']];p['IdentityPolicyCurrentDeclared']=[['policyFuture']];p['ExternalSignatureValidDeclared']=[['signatureFuture']]
 p['ProjectionInScopeDeclared']=[['projectionHuman'],['projectionLabel']];p['HumanViewDeclared']=[['projectionHuman']];p['ConvenienceLabelDeclared']=[['projectionLabel']];p['GeneratedProjectionDeclared']=[[x,'aDeclared','repDeclared'] for x in ['projectionHuman','projectionLabel']];p['RepresentationActualAuthority']=[['aAuthority'],['aBlockedAuthority']]
 m={'domains':ds,'constants':cs,'functions':funcs,'predicates':p};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('exact-representation-origin-assurance-and-independent-authority')
 add('no-applicable-artifacts',lambda m:m['predicates'].update(ArtifactApplicable=[],ArtifactInScopeDeclared=[],ProjectionInScopeDeclared=[]),I=False)
 add('no-human-view-witness',lambda m:m['predicates'].update(HumanViewDeclared=[]),I=False)
 add('no-convenience-label-witness',lambda m:m['predicates'].update(ConvenienceLabelDeclared=[]),I=False)
 add('no-future-L2-witness',lambda m:m['predicates'].update(ArtifactApplicable=[x for x in m['predicates']['ArtifactApplicable'] if x!=['aFuture']],ArtifactInScopeDeclared=[x for x in m['predicates']['ArtifactInScopeDeclared'] if x!=['aFuture']]),I=False)
 add('single-allowed-alternative',lambda m:m['predicates'].update(AllowedTupleDeclared=[x for x in m['predicates']['AllowedTupleDeclared'] if x[1]!='producerAlternative']),I=False)
 add('outside-path-inference-not-scoped',lambda m:m['predicates']['DirectoryInfersAuthorityDeclared'].append(['aOutside']))
 add('external-actual-execution-can-exist',lambda m:m['predicates']['RepresentationActualProcessExecution'].append(['aDeclared']))
 for n in b.ACTUAL:add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['RepresentationActual'+n].append(['aDeclared']))
 for n in b.EXCLUDED:add('prohibited-'+n,lambda m,n=n:m['predicates'][n].append(['aDeclared']),T=False,I=None)
 for n,s in b.FACETS.items():
  add('missing-binding-'+n,lambda m,n=n:m['predicates'].update({n+'BindingDeclared':m['predicates'][n+'BindingDeclared'][1:]}),T=False,I=None)
  if s!='Token':add('conflicting-binding-'+n,lambda m,n=n,s=s:m['predicates'][n+'BindingDeclared'].append(['aDeclared',m['domains'][s][-1]]),T=False,I=None)
 for n in b.ORIGIN_FIELDS:add('missing-origin-binding-'+n,lambda m,n=n:m['predicates'].update({n+'BindingDeclared':m['predicates'][n+'BindingDeclared'][1:]}),T=False,I=None)
 for name,rel,extra in [('hidden-second-representation','MachineCanonicalDeclared',['aDeclared','repAuthority']),('hidden-second-origin-record','OriginRecordForDeclared',['aDeclared','originAuthority'])]:add(name,lambda m,rel=rel,extra=extra:m['predicates'][rel].append(extra),T=False,I=None)
 for rel in ['MachineCanonicalDeclared','OriginRecordForDeclared','KindOriginSourceBindingDeclared','AuthorityKindCanonicalBindingDeclared','GeneratedProjectionDeclared']:add('missing-exact-relation-'+rel,lambda m,rel=rel:m['predicates'].update({rel:m['predicates'][rel][1:]}),T=False,I=None)
 for n,val in [('representationArtifact','aAuthority'),('representationState','stateAuthority'),('representationType','invariantType')]:add('representation-mismatch-'+n,lambda m,n=n,val=val:setfn(m,n,'repDeclared',val),T=False,I=None)
 for n,val in [('originArtifact','aAuthority'),('originOwner','ownerOutside')]:add('origin-mismatch-'+n,lambda m,n=n,val=val:change(m,n,'originDeclared',val),T=False,I=None)
 for n,val in [('originProducer','producerCandidate'),('originProcess','processOutside'),('originVersion','versionOutside'),('originStatement','statementAuthority')]:add('stale-origin-binding-'+n,lambda m,n=n,val=val:setfn(m,n,'originDeclared',val),T=False,I=None)
 add('candidate-producer-claimed-allowed',lambda m:(m['predicates']['AllowedOriginDeclared'].append(['aBlocked']),m['predicates']['CanonicalDeclared'].append(['aBlocked'])),T=False,I=None)
 add('source-candidate-still-claimed-allowed',lambda m:m['predicates']['SourceCandidateOnlyDeclared'].append(['sourceApproved']),T=False,I=None)
 add('source-not-owner-approved-still-claimed-allowed',lambda m:m['predicates'].update(SourceOwnerApprovedDeclared=[]),T=False,I=None)
 add('source-stale-still-claimed-allowed',lambda m:m['predicates'].update(SourceCurrentDeclared=[]),T=False,I=None)
 add('removed-allowed-set-still-claimed-allowed',lambda m:m['predicates'].update(AllowedTupleDeclared=[]),T=False,I=None)
 add('producer-not-admitted-still-claimed-allowed',lambda m:m['predicates'].update(ProducerAdmittedDeclared=[]),T=False,I=None)
 for n,val in [('artifactAuthorityKind','authorityOutside'),('artifactDurability','durableOutside'),('artifactType','invariantType')]:add('artifact-free-choice-'+n,lambda m,n=n,val=val:change(m,n,'aDeclared',val),T=False,I=None)
 add('authority-kind-maps-noncanonical-kind',lambda m:(setfn(m,'authorityKindCanonical','authorityMain','kindOutside'),m['predicates'].update(AuthorityKindCanonicalBindingDeclared=[['authorityMain','kindOutside']])),T=False,I=None)
 for n,val in [('invariantIdentity','artifactSiblingIdentity'),('invariantScope','outsideScope'),('invariantType','documentType'),('invariantSource','sourceApproved')]:add('target-mismatch-'+n,lambda m,n=n,val=val:setfn(m,n,'invariantMain',val),T=False,I=None)
 add('wrong-governing-invariant',lambda m:change(m,'artifactInvariant','aDeclared','invariantOther'),T=False,I=None)
 add('unsupported-owner-declared-statement',lambda m:m['predicates'].update(OwnerStatementDeclared=m['predicates']['OwnerStatementDeclared'][1:]),T=False,I=None)
 add('invalid-L1-receipt-declaration',lambda m:m['predicates'].update(L1ReceiptValidDeclared=[]),T=False,I=None)
 for n,val in [('receiptStatement','statementDeclared'),('receiptState','stateDeclared')]:add('L1-mismatch-'+n,lambda m,n=n,val=val:setfn(m,n,'receiptIntegrity',val),T=False,I=None)
 for rel in ['L2ReceiptValidDeclared','IdentifiedActorDeclared','IdentityPolicyCurrentDeclared','ExternalSignatureValidDeclared']:add('unsupported-future-'+rel,lambda m,rel=rel:m['predicates'].update({rel:[]}),T=False,I=None)
 for n,val in [('receiptStatement','statementDeclared'),('receiptState','stateDeclared'),('receiptActor','actorDeclared'),('receiptPolicy','policyDeclared'),('receiptSignature','signatureDeclared')]:add('L2-mismatch-'+n,lambda m,n=n,val=val:setfn(m,n,'receiptFuture',val),T=False,I=None)
 for n,val in [('signatureStatement','statementDeclared'),('signatureState','stateDeclared'),('signatureActor','actorDeclared')]:add('signature-mismatch-'+n,lambda m,n=n,val=val:setfn(m,n,'signatureFuture',val),T=False,I=None)
 add('future-L2-presently-unavailable',lambda m:m['predicates']['CurrentReviewArtifactDeclared'].append(['aFuture']),T=False,I=None)
 add('unknown-assurance-level',lambda m:change(m,'artifactAssurance','aDeclared','unknownLevel'),T=False,I=None)
 add('projection-claims-canonical',lambda m:m['predicates']['ProjectionCanonicalDeclared'].append(['projectionHuman']),T=False,I=None)
 add('projection-wrong-source',lambda m:setfn(m,'projectionSource','projectionHuman','repAuthority'),T=False,I=None)
 add('projection-external-effect',lambda m:setfn(m,'projectionEffect','projectionHuman','reference'),T=False,I=None)
 for n in ['artifactMachine','originProducer','representationState','receiptActor','signatureState']:add('malformed-output-'+n,lambda m,n=n:m['functions'][n][0].update(value='not-in-sort'),T=None,I=None,error='ill-sorted-function-result')
 add('malformed-empty-artifact-domain',lambda m:m['domains'].update(ArtifactReference=[]),T=None,I=None,error='empty-or-malformed-domain')
 add('malformed-missing-function',lambda m:m['functions'].pop('originProducer'),T=None,I=None,error='model-signature-denominator-mismatch')
 add('malformed-duplicate-function-tuple',lambda m:m['functions']['originProducer'].append(copy.deepcopy(m['functions']['originProducer'][0])),T=None,I=None,error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.canonical-package-manifest/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-CanonicalRepresentationInvariant-model-controls/v1-candidate','status':'PASS-for-exact-authored-CanonicalRepresentationInvariant-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed exact declared machine representation,origin eligibility,kind inheritance,honest assurance,future L2 and generated projections checked on supplied finite models;actual execution,authenticity,truth,authority,source fidelity and whole proof remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
