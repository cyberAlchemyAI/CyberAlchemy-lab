"""Independent Parent-Instance reference,claim,registration,scope,behavior and owner-route controls."""
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
 constants={'EMPTY':'empty','MEANING_ID':'semantic-parent-instance-authority-separation','MEANING_KIND':'invariant-kind','MEANING_CARRIER':'type-invariant','MEANING_SCOPE':'shared-authority','SOURCE_D64':'cav2-d64','SPECIALIZATION_KIND':'specialization','VERSION_MODE':'version','STATE_MODE':'state'}
 bindings=['bVersion','bState','bOutside'];parents=['pShared','pOutside'];insts=['iVersion','iState','iOutside'];snapshots=['snapVersion','snapState','snapLatest','snapOutside'];claims=['cParentVersion','cParentState','cInstanceVersion','cInstanceState','cParentOutside','cInstanceOutside'];subjects=['sParent','sOtherParent','sInstanceVersion','sInstanceState','sInstanceOutside'];contracts=['contractVersion','contractState','contractLatest','contractOutside','contractLocalVersion','contractLocalState','contractLocalOutside'];life=['lifeParent','lifeOtherParent','lifeInstanceVersion','lifeInstanceState','lifeInstanceOutside'];boundaries=['boundaryParent','boundaryOtherParent','boundaryInstanceVersion','boundaryInstanceState','boundaryInstanceOutside'];registrations=['regVersion','regState','regOutside'];relations=['relVersion','relState','relOutside'];projects=['projectShared','projectOutside'];changes=['changeShared','changeLocal','changeAbsorb','changeOutside'];tokens=list(constants[n] for n,s in b.CONSTANTS.items() if s=='Token')+['version-1','state-1','version-2','state-outside','package-version','package-state','package-outside','pending-adoption-decision','conformance-reference','recomposition-path','recursive-stop-reference','goal-reference','project-evidence-reference','shared-printed-label','same-maturity','opaque'];domains={'Invariant':['inv1'],'ParentModel':parents,'Instance':insts,'Subject':subjects,'Snapshot':snapshots,'ReferenceMode':['version','state'],'Contract':contracts,'AuthorityClaim':claims,'Principal':['owner1','owner2'],'Scope':['sharedScope','localScope','outsideScope'],'Lifecycle':life,'Boundary':boundaries,'Binding':bindings,'Relation':relations,'Project':projects,'Registration':registrations,'Behavior':['baseBehavior','alternativeBehavior','localBehavior','unsupportedBehavior'],'Change':changes,'Route':['parentRoute','instanceRoute','outsideRoute'],'Token':tokens}
 binding_instance=dict(zip(bindings,insts));binding_snapshot=dict(zip(bindings,['snapVersion','snapState','snapOutside']));binding_parent_claim=dict(zip(bindings,['cParentVersion','cParentState','cParentOutside']));binding_instance_claim=dict(zip(bindings,['cInstanceVersion','cInstanceState','cInstanceOutside']));binding_registration=dict(zip(bindings,registrations));binding_relation=dict(zip(bindings,relations));binding_package=dict(zip(bindings,['package-version','package-state','package-outside']));snapshot_contract=dict(zip(snapshots,['contractVersion','contractState','contractLatest','contractOutside']));snapshot_mode=dict(zip(snapshots,['version','state','version','state']));snapshot_handle=dict(zip(snapshots,['version-1','state-1','version-2','state-outside']));instance_contract=dict(zip(insts,['contractLocalVersion','contractLocalState','contractLocalOutside']));instance_subject=dict(zip(insts,subjects[2:]));instance_life=dict(zip(insts,life[2:]));instance_boundary=dict(zip(insts,boundaries[2:]));claim_subject=dict(zip(claims,['sParent','sParent','sInstanceVersion','sInstanceState','sOtherParent','sInstanceOutside']));claim_contract=dict(zip(claims,['contractVersion','contractState','contractLocalVersion','contractLocalState','contractOutside','contractLocalOutside']));registration_binding=dict(zip(registrations,bindings));relation_binding=dict(zip(relations,bindings));life_subject=dict(zip(life,subjects));boundary_subject=dict(zip(boundaries,subjects));change_binding=dict(zip(changes,['bVersion','bVersion','bVersion','bOutside']));change_route=dict(zip(changes,['parentRoute','instanceRoute','instanceRoute','outsideRoute']))
 def parent_for(binding):return 'pOutside' if binding=='bOutside' else 'pShared'
 def project_for(binding):return 'projectOutside' if binding=='bOutside' else 'projectShared'
 def scope_for(binding):return 'outsideScope' if binding=='bOutside' else 'localScope'
 def owner_for_instance(inst):return 'owner2' if inst=='iOutside' else 'owner1'
 def parent_owner(parent):return 'owner2' if parent=='pOutside' else 'owner1'
 meta=dict(zip(['invariantIdentity','invariantKind','invariantCarrier','invariantOwnerScope','invariantSourceD64'],['MEANING_ID','MEANING_KIND','MEANING_CARRIER','MEANING_SCOPE','SOURCE_D64']));maps={n:(lambda x,n=n:constants[meta[n]]) for n in meta};maps.update(bindingInvariant=lambda q:'inv1',bindingParent=parent_for,bindingInstance=lambda q:binding_instance[q],bindingSnapshot=lambda q:binding_snapshot[q],bindingParentClaim=lambda q:binding_parent_claim[q],bindingInstanceClaim=lambda q:binding_instance_claim[q],bindingProject=project_for,bindingRegistration=lambda q:binding_registration[q],bindingRelation=lambda q:binding_relation[q],bindingInheritedContract=lambda q:snapshot_contract[binding_snapshot[q]],bindingExtensionScope=scope_for,bindingPackage=lambda q:binding_package[q],snapshotParent=lambda s:'pOutside' if s=='snapOutside' else 'pShared',snapshotMode=lambda s:snapshot_mode[s],snapshotHandle=lambda s:snapshot_handle[s],snapshotContract=lambda s:snapshot_contract[s],parentLatestSnapshot=lambda p:'snapOutside' if p=='pOutside' else 'snapLatest',parentSubject=lambda p:'sOtherParent' if p=='pOutside' else 'sParent',parentOwner=parent_owner,parentAuthorityScope=lambda p:'outsideScope' if p=='pOutside' else 'sharedScope',parentLifecycle=lambda p:'lifeOtherParent' if p=='pOutside' else 'lifeParent',parentBoundary=lambda p:'boundaryOtherParent' if p=='pOutside' else 'boundaryParent',parentOwnerRoute=lambda p:'outsideRoute' if p=='pOutside' else 'parentRoute',instanceSubject=lambda i:instance_subject[i],instanceOwner=owner_for_instance,instanceAuthorityScope=lambda i:'outsideScope' if i=='iOutside' else 'localScope',instanceLocalContract=lambda i:instance_contract[i],instanceLifecycle=lambda i:instance_life[i],instanceBoundary=lambda i:instance_boundary[i],instanceOwnerRoute=lambda i:'outsideRoute' if i=='iOutside' else 'instanceRoute',claimSubject=lambda c:claim_subject[c],claimScope=lambda c:'outsideScope' if c.endswith('Outside') else 'sharedScope' if c.startswith('cParent') else 'localScope',claimPrincipal=lambda c:'owner2' if c.endswith('Outside') else 'owner1',claimContract=lambda c:claim_contract[c],lifecycleSubject=lambda l:life_subject[l],lifecycleStatus=lambda l:'same-maturity',boundarySubject=lambda q:boundary_subject[q],boundaryLabel=lambda q:'shared-printed-label',relationSnapshot=lambda rel:binding_snapshot[relation_binding[rel]],relationInstance=lambda rel:binding_instance[relation_binding[rel]],relationKind=lambda rel:'specialization',changeBinding=lambda x:change_binding[x],changeRoute=lambda x:change_route[x])
 for field in ['Project','Snapshot','Instance','ParentClaim','InstanceClaim','InheritedContract','ExtensionScope','Package']:
  maps['registration'+field]=lambda reg,field=field:maps['binding'+field](registration_binding[reg])
 maps.update(registrationSpecializationRelation=lambda r:binding_relation[registration_binding[r]],registrationParentOwner=lambda r:parent_owner(parent_for(registration_binding[r])),registrationInstanceOwner=lambda r:owner_for_instance(binding_instance[registration_binding[r]]),registrationAdoptionDecision=lambda r:'pending-adoption-decision',registrationConformanceEvidence=lambda r:'conformance-reference',registrationChallengeRoute=lambda r:'instanceRoute',registrationDriftRoute=lambda r:'parentRoute',registrationRecompositionPath=lambda r:'recomposition-path',registrationRecursiveStop=lambda r:'recursive-stop-reference',registrationGoals=lambda r:'goal-reference',registrationEvidence=lambda r:'project-evidence-reference')
 assert maps.keys()==b.FUNCTIONS.keys(),(maps.keys()-b.FUNCTIONS.keys(),b.FUNCTIONS.keys()-maps.keys())
 functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};p={n:[] for n in b.SIGNATURE};p.update(ParentInstanceInvariant=[['inv1']],PreservesClassification=[['inv1']],PreservesSourceRelations=[['inv1']],NotSilentlyMerged=[['inv1']],GovernedParentModel=[['pShared']],LocallyOwnedInstance=[['iVersion'],['iState']],ExactReferenceDeclared=[['snapVersion'],['snapState']],SemanticAuthorityClaim=[[c] for c in claims],BindingApplies=[['bVersion'],['bState']],TypedRelationDeclared=[['relVersion'],['relState']],ProjectDeclared=[['projectShared']],RegistrationDeclared=[['regVersion'],['regState']],InheritedRealization=[['bVersion','baseBehavior'],['bState','alternativeBehavior']],InstanceRealizes=[['iVersion','baseBehavior'],['iVersion','localBehavior'],['iState','alternativeBehavior'],['iState','localBehavior'],['iOutside','unsupportedBehavior']],ParentAllows=[['snapVersion','baseBehavior'],['snapVersion','alternativeBehavior'],['snapState','baseBehavior'],['snapState','alternativeBehavior'],['snapLatest','baseBehavior'],['snapOutside','unsupportedBehavior']],SpecializationScopePermits=[['bVersion','baseBehavior'],['bState','alternativeBehavior']],ChangeRequested=[[x] for x in changes],RelevantChange=[[x] for x in changes[:-1]],SharedModelChange=[['changeShared'],['changeOutside']],LocalInstanceChange=[['changeLocal']],AbsorbsInstanceLocalMeaning=[['changeAbsorb']],ApplicablePromotionOrAdoptionPathDeclared=[['changeAbsorb']])
 for n in ['DownstreamReliesOnParent','IndependentLocalOwnershipRequired','ProjectCreatesOrEvolvesInstance','SemanticAuthoritySeparated','CoordinationBoundarySeparated','LifecycleSeparated',*b.REGISTER_MARKERS]:p[n]=[['bVersion'],['bState']]
 for n in ['ProjectMembershipSignal','FilePlacementSignal','RepositoryPermissionSignal','GenericResponsibilitySignal']:p[n]=[['bOutside']]
 for n in b.PARENT_RIGHTS:p[n]=[[c] for c in ['cParentVersion','cParentState','cParentOutside']]
 for n in b.INSTANCE_RIGHTS:p[n]=[[c] for c in ['cInstanceVersion','cInstanceState','cInstanceOutside']]
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':p}
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('version-state-same-owner-separated-claims-labels-behavior-and-owner-routes',lambda m:None,I=True)
 for prefix,names,subject in [('Invariant',b.INV_OUTCOMES,'inv1'),('Binding',b.BIND_OUTCOMES,'bVersion'),('Change',b.CHANGE_OUTCOMES,'changeShared')]:
  for n in names:add('independent-'+prefix+'-actual-'+n,lambda m,prefix=prefix,n=n,subject=subject:m['predicates'][prefix+'Actual'+n].append([subject]))
 for n in ['PreservesClassification','PreservesSourceRelations','NotSilentlyMerged']:add('missing-normalized-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in ['invariantIdentity','invariantKind','invariantCarrier','invariantOwnerScope','invariantSourceD64']:add('wrong-normalized-'+n,lambda m,n=n:setfn(m,n,'inv1','opaque'),T=False)
 for n in ['DownstreamReliesOnParent','IndependentLocalOwnershipRequired','ProjectCreatesOrEvolvesInstance']:add('missing-applicability-guard-'+n,lambda m,n=n:m['predicates'][n].remove(['bVersion']),T=False)
 add('missing-governed-parent',lambda m:m['predicates']['GovernedParentModel'].clear(),T=False)
 add('missing-locally-owned-instance',lambda m:m['predicates']['LocallyOwnedInstance'].remove(['iVersion']),T=False)
 add('missing-declared-Project',lambda m:m['predicates']['ProjectDeclared'].clear(),T=False)
 add('missing-exact-reference-declaration',lambda m:m['predicates']['ExactReferenceDeclared'].remove(['snapVersion']),T=False)
 add('missing-typed-specialization-relation',lambda m:m['predicates']['TypedRelationDeclared'].remove(['relVersion']),T=False)
 add('aliased-version-and-state-modes',lambda m:m['constants'].update(VERSION_MODE='state'),T=False)
 add('empty-exact-parent-reference',lambda m:setfn(m,'snapshotHandle','snapVersion','empty'),T=False)
 add('wrong-snapshot-parent',lambda m:setfn(m,'snapshotParent','snapVersion','pOutside'),T=False)
 add('declared-reference-mode-requires-independent-source-map',lambda m:setfn(m,'snapshotMode','snapVersion','state'),I=False)
 for n,val in [('relationSnapshot','snapLatest'),('relationInstance','iState'),('relationKind','opaque')]:add('wrong-exact-specialization-'+n,lambda m,n=n,val=val:setfn(m,n,'relVersion',val),T=False)
 add('wrong-inherited-snapshot-contract',lambda m:setfn(m,'bindingInheritedContract','bVersion','contractLatest'),T=False)
 add('latest-may-equal-bound-version-without-forcing-old-reference-policy',lambda m:setfn(m,'parentLatestSnapshot','pShared','snapVersion'),I=False)
 for claim in ['cParentVersion','cInstanceVersion']:add('missing-semantic-authority-claim-'+claim,lambda m,claim=claim:m['predicates']['SemanticAuthorityClaim'].remove([claim]),T=False)
 for n in b.PARENT_RIGHTS:add('missing-parent-condition-'+n,lambda m,n=n:m['predicates'][n].remove(['cParentVersion']),T=False)
 for n in b.INSTANCE_RIGHTS:add('missing-instance-authority-'+n,lambda m,n=n:m['predicates'][n].remove(['cInstanceVersion']),T=False)
 for claim,fields in [('cParentVersion',[('claimSubject','sInstanceVersion'),('claimPrincipal','owner2'),('claimScope','localScope'),('claimContract','contractLatest')]),('cInstanceVersion',[('claimSubject','sParent'),('claimPrincipal','owner2'),('claimScope','sharedScope'),('claimContract','contractVersion')])]:
  for n,val in fields:add('wrong-scoped-'+claim+'-'+n,lambda m,n=n,val=val,claim=claim:setfn(m,n,claim,val),T=False)
 add('collapsed-parent-instance-claim-identity',lambda m:setfn(m,'bindingInstanceClaim','bVersion','cParentVersion'),T=False)
 def distinct_principal(m):
  setfn(m,'instanceOwner','iVersion','owner2');setfn(m,'claimPrincipal','cInstanceVersion','owner2');setfn(m,'registrationInstanceOwner','regVersion','owner2')
 add('different-principals-also-allowed-with-exact-local-claim',distinct_principal,I=True)
 def shared_scope(m):setfn(m,'instanceAuthorityScope','iVersion','sharedScope');setfn(m,'claimScope','cInstanceVersion','sharedScope')
 add('scope-label-overlap-not-disjointness-proof',shared_scope,I=True)
 def collapsed_subject(m):
  for n,arg in [('instanceSubject','iVersion'),('claimSubject','cInstanceVersion'),('boundarySubject','boundaryInstanceVersion'),('lifecycleSubject','lifeInstanceVersion')]:setfn(m,n,arg,'sParent')
 add('nominal-carriers-do-not-justify-collapsed-common-subject',collapsed_subject,T=False)
 for n in ['SemanticAuthoritySeparated','CoordinationBoundarySeparated','LifecycleSeparated',*b.REGISTER_MARKERS]:add('missing-separated-or-registered-'+n,lambda m,n=n:m['predicates'][n].remove(['bVersion']),T=False)
 for n,val in [('instanceBoundary','boundaryParent'),('instanceLifecycle','lifeParent')]:add('collapsed-instance-'+n,lambda m,n=n,val=val:setfn(m,n,'iVersion',val),T=False)
 for n,arg,val in [('boundarySubject','boundaryInstanceVersion','sParent'),('lifecycleSubject','lifeInstanceVersion','sParent')]:add('wrong-independent-'+n,lambda m,n=n,arg=arg,val=val:setfn(m,n,arg,val),T=False)
 add('equal-status-and-boundary-labels-preserve-separate-identities',lambda m:None,I=True)
 add('missing-Project-registration',lambda m:m['predicates']['RegistrationDeclared'].remove(['regVersion']),T=False)
 for field,val in [('Project','projectOutside'),('Snapshot','snapLatest'),('Instance','iState'),('ParentClaim','cParentState'),('InstanceClaim','cInstanceState'),('InheritedContract','contractLatest'),('ExtensionScope','sharedScope'),('Package','package-state'),('SpecializationRelation','relState'),('ParentOwner','owner2'),('InstanceOwner','owner2')]:add('wrong-registration-'+field,lambda m,n='registration'+field,val=val:setfn(m,n,'regVersion',val),T=False)
 for field in ['Package','AdoptionDecision','ConformanceEvidence','RecompositionPath','RecursiveStop','Goals','Evidence']:add('empty-required-registration-'+field,lambda m,n='registration'+field:setfn(m,n,'regVersion','empty'),T=False)
 add('declared-challenge-route-not-actual-route-acceptance',lambda m:setfn(m,'registrationChallengeRoute','regVersion','outsideRoute'),I=True)
 add('missing-inherited-instance-behavior',lambda m:m['predicates']['InstanceRealizes'].remove(['iVersion','baseBehavior']),T=False)
 add('missing-exact-parent-behavior-allowance',lambda m:m['predicates']['ParentAllows'].remove(['snapVersion','baseBehavior']),T=False)
 add('missing-declared-specialization-scope',lambda m:m['predicates']['SpecializationScopePermits'].remove(['bVersion','baseBehavior']),T=False)
 def beyond_parent(m):m['predicates']['InheritedRealization'].append(['bVersion','unsupportedBehavior']);m['predicates']['InstanceRealizes'].append(['iVersion','unsupportedBehavior']);m['predicates']['SpecializationScopePermits'].append(['bVersion','unsupportedBehavior'])
 add('realization-outside-parent-contract',beyond_parent,T=False)
 def beyond_scope(m):m['predicates']['InheritedRealization'].append(['bVersion','unsupportedBehavior']);m['predicates']['InstanceRealizes'].append(['iVersion','unsupportedBehavior']);m['predicates']['ParentAllows'].append(['snapVersion','unsupportedBehavior'])
 add('realization-outside-declared-extension-scope',beyond_scope,T=False)
 add('empty-inherited-relation-exposes-population-vacuity',lambda m:m['predicates']['InheritedRealization'].clear(),I=False)
 def full_realization(m):m['predicates']['InheritedRealization'].append(['bVersion','alternativeBehavior']);m['predicates']['InstanceRealizes'].append(['iVersion','alternativeBehavior']);m['predicates']['SpecializationScopePermits'].append(['bVersion','alternativeBehavior'])
 add('realizing-full-parent-allowance-is-not-universal-proper-subtype',full_realization,I=True)
 add('independent-local-behavior-outside-inherited-relation',lambda m:None,I=True)
 add('silent-instance-parent-redefinition',lambda m:m['predicates']['SilentlyRedefinesParent'].append(['iVersion']),T=False)
 for change,val in [('changeShared','instanceRoute'),('changeLocal','parentRoute'),('changeAbsorb','parentRoute')]:add('wrong-owner-route-'+change,lambda m,change=change,val=val:setfn(m,'changeRoute',change,val),T=False)
 add('absorption-missing-applicable-promotion-or-adoption-path',lambda m:m['predicates']['ApplicablePromotionOrAdoptionPathDeclared'].clear(),T=False)
 add('missing-exact-relevant-change',lambda m:m['predicates']['RelevantChange'].remove(['changeShared']),T=False)
 add('unrequested-change-still-marked-relevant',lambda m:m['predicates']['ChangeRequested'].remove(['changeShared']),T=False)
 def unselect_shared(m):m['predicates']['ChangeRequested'].remove(['changeShared']);m['predicates']['RelevantChange'].remove(['changeShared'])
 add('unselected-shared-request-does-not-create-owner-action',unselect_shared,I=False)
 add('outside-scope-change-not-forced-through-parent-routes',lambda m:setfn(m,'changeRoute','changeOutside','instanceRoute'),I=True)
 def signals(m):
  for n in ['ProjectMembershipSignal','FilePlacementSignal','RepositoryPermissionSignal','GenericResponsibilitySignal']:m['predicates'][n].append(['bVersion'])
 add('membership-and-placement-signals-do-not-supply-authority',signals,I=True)
 for n in b.COLLAPSED+b.INFER_FLAGS:add('forbidden-collapse-or-inference-'+n,lambda m,n=n:m['predicates'][n].append(['inv1']),T=False)
 add('missing-relation-reference-table-entry',lambda m:m['functions']['relationSnapshot'].pop(),error='nontotal-function')
 add('ill-sorted-relation-reference-result',lambda m:setfn(m,'relationSnapshot','relVersion','cParentVersion'),error='ill-sorted-function-result')
 add('ill-sorted-reference-mode-constant',lambda m:m['constants'].update(VERSION_MODE='pShared'),error='ill-sorted-constant')
 add('wrong-specialization-relation-arity',lambda m:m['predicates'].update(InheritedRealization=[['bVersion']]),error='ill-sorted-model-tuple')
 add('duplicate-applicability-tuple',lambda m:m['predicates']['BindingApplies'].append(['bVersion']),error='duplicate-predicate-tuple')
 add('empty-snapshot-domain',lambda m:m['domains'].update(Snapshot=[]),error='empty-or-malformed-domain')
 add('duplicate-reference-function-tuple',lambda m:m['functions']['relationSnapshot'].append(copy.deepcopy(m['functions']['relationSnapshot'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.governance-axis-independence-invariant/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-PIAS-model-controls/v1-candidate','status':'PASS-for-exact-authored-PIAS-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed normalized parent/instance invariant,exact snapshot/contract/scoped-claim/registration and specialization/change-route guards checked on supplied models. Actual authority,adoption,conformance,records,recomposition,recursive termination,owner and consumer alignment remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
