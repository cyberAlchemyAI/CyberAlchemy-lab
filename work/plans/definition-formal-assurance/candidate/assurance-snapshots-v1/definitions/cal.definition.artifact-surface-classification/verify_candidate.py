"""Supplied package role,self-entry and exact declared type-resolution models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
def base_model():
 ds={'PackageReference':['pPrimary','pAuthority','pOutside'],'GovernedFileReference':['fManifest','fInstance','fComponent','fGenerated','fEvidence','fFixture','fTransient','fAuthorityManifest','fOutside'],'SurfaceRole':['role'+n for n in b.ROLE_NAMES]+['roleOutside'],'RegistryReference':['rCurrent','rOutside'],'ArtifactTypeReference':['tManifest','tOther','tOutside'],'ArtifactTypeKey':['keyManifest','keyOther','keyOutside'],'PackageHomeReference':['hDeclared','hAuthority','hOutside'],'Token':['empty','reference','differentReference']}
 constants={'EMPTY':'empty','CANONICAL_MANIFEST_TYPE':'keyManifest',**{n:'role'+n for n in b.ROLE_NAMES}};role_map={'fManifest':'INSTANCE','fInstance':'INSTANCE','fComponent':'COMPONENT','fGenerated':'GENERATED','fEvidence':'EVIDENCE','fFixture':'FIXTURE','fTransient':'TRANSIENT','fAuthorityManifest':'INSTANCE'};maps={'packageHome':lambda p:'hOutside' if p=='pOutside' else 'hAuthority' if p=='pAuthority' else 'hDeclared','packageRegistry':lambda p:'rOutside' if p=='pOutside' else 'rCurrent','packageManifestFile':lambda p:'fOutside' if p=='pOutside' else 'fAuthorityManifest' if p=='pAuthority' else 'fManifest','selectedRole':lambda p,f:'roleOutside' if p=='pOutside' or f=='fOutside' else 'role'+role_map[f],'selectedResolvedType':lambda p,f:'tManifest' if f in ['fManifest','fAuthorityManifest'] else 'tOther' if f!='fOutside' else 'tOutside','typeKey':lambda t:'key'+t[1:]}
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 predicates['PackageApplicable']=[['pPrimary'],['pAuthority']];predicates['PackageInScopeDeclared']=copy.deepcopy(predicates['PackageApplicable'])
 for s in b.SORTS:
  if s not in ['PackageReference','Token']:predicates[s+'Declared']=[[x] for x in ds[s][:-1]]
 governed=[['pPrimary',f] for f in ds['GovernedFileReference'][:-2]]+[['pAuthority','fAuthorityManifest']]
 predicates.update(CanonicalPackageHomeDeclared=[['pPrimary','hDeclared'],['pAuthority','hAuthority']],GovernedDeclared=governed,RoleAssignmentDeclared=[[p,f,maps['selectedRole'](p,f)] for p,f in governed],CanonicalSubjectDeclared=[['pPrimary','fManifest'],['pPrimary','fInstance'],['pAuthority','fAuthorityManifest']],ManifestSelfEntryDeclared=[['pPrimary','fManifest'],['pAuthority','fAuthorityManifest']],ArtifactTypeAdmittedDeclared=[['rCurrent','tManifest'],['rCurrent','tOther']],ResolvedTypeDeclared=[['rCurrent','fManifest','tManifest'],['rCurrent','fInstance','tOther'],['rCurrent','fAuthorityManifest','tManifest']],SurfaceActualAuthority=[['pAuthority']])
 return {'domains':ds,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('six-explicit-roles-self-entry-one-resolved-type-and-independent-authority',lambda m:None,I=True)
 for n in b.ACTUAL:
  if n=='Authority':continue
  add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['SurfaceActual'+n].append(['pAuthority']),I=True)
 add('selected-empty-package-handle',lambda m:setfn(m,b.HANDLES['PackageReference'],'pPrimary','empty'),T=False)
 add('outside-empty-package-handle',lambda m:setfn(m,b.HANDLES['PackageReference'],'pOutside','empty'),I=True)
 for n,s,value in [('packageHome','PackageHomeReference','hDeclared'),('packageRegistry','RegistryReference','rCurrent'),('packageManifestFile','GovernedFileReference','fManifest')]:
  add('missing-package-facet-'+n,lambda m,s=s,value=value:m['predicates'][s+'Declared'].remove([value]),T=False)
  add('empty-package-facet-'+n,lambda m,s=s,value=value:setfn(m,b.HANDLES[s],value,'empty'),T=False)
 add('package-scope-disagreement',lambda m:m['predicates']['PackageInScopeDeclared'].remove(['pPrimary']),T=False)
 add('package-home-qualification-not-declared',lambda m:m['predicates']['CanonicalPackageHomeDeclared'].remove(['pPrimary','hDeclared']),T=False)
 add('manifest-self-entry-marker-absent',lambda m:m['predicates']['ManifestSelfEntryDeclared'].remove(['pPrimary','fManifest']),T=False)
 add('manifest-omitted-from-governed-files',lambda m:m['predicates']['GovernedDeclared'].remove(['pPrimary','fManifest']),T=False)
 add('manifest-is-not-canonical-instance-role',lambda m:setfn(m,'selectedRole',['pPrimary','fManifest'],'roleCOMPONENT'),T=False)
 add('manifest-wrong-exact-type-key',lambda m:setfn(m,'typeKey','tManifest','keyOther'),T=False)
 add('manifest-wrong-nominated-type',lambda m:setfn(m,'selectedResolvedType',['pPrimary','fManifest'],'tOther'),T=False)
 for n in b.ROLE_NAMES:
  add('recognized-role-not-declared-'+n,lambda m,n=n:m['predicates']['SurfaceRoleDeclared'].remove(['role'+n]),T=False)
 for n in b.ROLE_NAMES[1:]:add('role-constant-collapsed-'+n,lambda m,n=n:m['constants'].update({n:'roleINSTANCE'}),T=False)
 add('unknown-seventh-role-declared',lambda m:m['predicates']['SurfaceRoleDeclared'].append(['roleOutside']),T=False)
 add('unknown-role-selected',lambda m:setfn(m,'selectedRole',['pPrimary','fComponent'],'roleOutside'),T=False)
 for f in base_model()['domains']['GovernedFileReference'][:-2]:
  role=next(x[2] for x in base_model()['predicates']['RoleAssignmentDeclared'] if x[:2]==['pPrimary',f])
  add('missing-explicit-role-assignment-'+f,lambda m,f=f,role=role:m['predicates']['RoleAssignmentDeclared'].remove(['pPrimary',f,role]),T=False)
 add('two-distinct-explicit-role-assignments',lambda m:m['predicates']['RoleAssignmentDeclared'].append(['pPrimary','fComponent','roleGENERATED']),T=False)
 add('changed-role-function-without-exact-declaration',lambda m:setfn(m,'selectedRole',['pPrimary','fComponent'],'roleGENERATED'),T=False)
 for f in ['fComponent','fGenerated','fEvidence','fFixture','fTransient']:add('noncanonical-role-claims-canonical-subject-'+f,lambda m,f=f:m['predicates']['CanonicalSubjectDeclared'].append(['pPrimary',f]),T=False)
 for f in ['fManifest','fInstance']:add('canonical-instance-subject-marker-missing-'+f,lambda m,f=f:m['predicates']['CanonicalSubjectDeclared'].remove(['pPrimary',f]),T=False)
 for t in ['tManifest','tOther']:
  add('canonical-type-ref-not-declared-'+t,lambda m,t=t:m['predicates']['ArtifactTypeReferenceDeclared'].remove([t]),T=False)
  add('canonical-type-admission-not-declared-'+t,lambda m,t=t:m['predicates']['ArtifactTypeAdmittedDeclared'].remove(['rCurrent',t]),T=False)
 add('canonical-type-empty-handle',lambda m:setfn(m,b.HANDLES['ArtifactTypeReference'],'tOther','empty'),T=False)
 add('canonical-type-key-not-declared',lambda m:m['predicates']['ArtifactTypeKeyDeclared'].remove(['keyManifest']),T=False)
 add('canonical-type-key-empty-handle',lambda m:setfn(m,b.HANDLES['ArtifactTypeKey'],'keyManifest','empty'),T=False)
 add('missing-canonical-type-resolution',lambda m:m['predicates']['ResolvedTypeDeclared'].remove(['rCurrent','fInstance','tOther']),T=False)
 add('two-distinct-canonical-type-results',lambda m:m['predicates']['ResolvedTypeDeclared'].append(['rCurrent','fInstance','tManifest']),T=False)
 add('unknown-nominated-canonical-type',lambda m:setfn(m,'selectedResolvedType',['pPrimary','fInstance'],'tOutside'),T=False)
 add('changed-nominee-without-corresponding-resolution',lambda m:setfn(m,'selectedResolvedType',['pPrimary','fInstance'],'tManifest'),T=False)
 def changed_registry(m,complete):
  m['predicates']['RegistryReferenceDeclared'].append(['rOutside']);setfn(m,'packageRegistry','pPrimary','rOutside')
  if complete:
   m['predicates']['ArtifactTypeAdmittedDeclared'] += [['rOutside',t] for t in ['tManifest','tOther']];m['predicates']['ResolvedTypeDeclared'] += [['rOutside','fManifest','tManifest'],['rOutside','fInstance','tOther']]
 add('changed-registry-without-exact-resolution-and-admission',lambda m:changed_registry(m,False),T=False)
 add('changed-registry-with-exact-declared-correspondence',lambda m:changed_registry(m,True),I=True)
 add('type-reference-key-injectivity-not-invented',lambda m:setfn(m,'typeKey','tOther','keyManifest'),I=True)
 add('selected-transient-canonical-dependency-is-rejected',lambda m:m['predicates']['CanonicalDependencyDeclared'].append(['pPrimary','fTransient']),T=False)
 add('nontransient-dependency-declaration-is-not-actual-satisfaction',lambda m:m['predicates']['CanonicalDependencyDeclared'].append(['pPrimary','fEvidence']),I=True)
 add('outside-transient-dependency-unconstrained',lambda m:m['predicates']['CanonicalDependencyDeclared'].append(['pOutside','fTransient']),I=True)
 add('outside-file-canonical-subject-claim-outside-selected-membership',lambda m:m['predicates']['CanonicalSubjectDeclared'].append(['pPrimary','fOutside']),I=True)
 add('outside-file-handle-can-be-empty',lambda m:setfn(m,b.HANDLES['GovernedFileReference'],'fOutside','empty'),I=True)
 add('file-handle-change-does-not-determine-role',lambda m:setfn(m,b.HANDLES['GovernedFileReference'],'fComponent','differentReference'),I=True)
 add('unselected-registry-extra-resolution-does-not-affect-selected-one',lambda m:m['predicates']['ResolvedTypeDeclared'].append(['rOutside','fInstance','tOutside']),I=True)
 add('role-result-is-an-artifact-type',lambda m:setfn(m,'selectedRole',['pPrimary','fManifest'],'tManifest'),error='ill-sorted-function-result')
 add('missing-symbol',lambda m:m['predicates'].pop('GovernedDeclared'),error='model-signature-denominator-mismatch')
 add('nontotal-role-function',lambda m:m['functions']['selectedRole'].pop(),error='nontotal-function')
 add('ill-sorted-manifest-type-constant',lambda m:m['constants'].update(CANONICAL_MANIFEST_TYPE='fManifest'),error='ill-sorted-constant')
 add('wrong-resolution-arity',lambda m:m['predicates'].update(ResolvedTypeDeclared=[['rCurrent','fManifest']]),error='ill-sorted-model-tuple')
 add('duplicate-governed-tuple',lambda m:m['predicates']['GovernedDeclared'].append(['pPrimary','fManifest']),error='duplicate-predicate-tuple')
 add('empty-role-domain',lambda m:m['domains'].update(SurfaceRole=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['selectedRole'].append(copy.deepcopy(m['functions']['selectedRole'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.artifact-lifetime/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ArtifactSurface-model-controls/v1-candidate','status':'PASS-for-exact-authored-ArtifactSurface-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed package roles,explicit role assignments,manifest self-entry and unique declared type resolution checked on supplied models. Actual enumeration,classification,resolution,admission,canonical-subject legitimacy,Conformance,owner fidelity and consumer alignment remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
