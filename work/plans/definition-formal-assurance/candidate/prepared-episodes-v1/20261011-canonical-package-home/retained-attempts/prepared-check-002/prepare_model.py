from pathlib import Path
import ast
p=Path(__file__).resolve().parent;dest=p/'prepared';old=Path('docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.artifact-type-resolution/verify_candidate.py').read_text();head=old[:old.index('NAMES=')]
body='''def getfn(m,n,*args):return next(x['value'] for x in m['functions'][n] if x['args']==list(args))
def refresh(m):
 p=m['predicates'];get=lambda n,*args:getfn(m,n,*args)
 for n in b.MOVEMENT_FACETS:
  p[(n+'BindingDeclared') if n!='movementAggregate' else 'MovementAggregateBindingDeclared']=[[x[0],get(n,x[0])] for x in p['MovementInScopeDeclared']]
 p['FacetKindBindingDeclared']=[[x[0],get('facetKind',x[0])] for x in p['FacetInScopeDeclared']]
def base_model():
 ds={s:[] for s in b.SORTS};ds.update(AggregateReference=['aggMain','aggSecond','aggOutside'],HomeReference=['homeMain','homeSecond','homeOutside'],CarrierReference=['carrierMain','carrierSecond','carrierOutside'],OwnerReference=['ownerMain','ownerSecond','ownerOutside'],UnitReference=['unitMain','unitSecond','unitOutside'],RecoveryBoundaryReference=['recoveryMain','recoverySecond','recoveryOutside'],ManifestReference=['manifestMain','manifestSecond','manifestOutside'],FacetReference=['facet'+str(i) for i in range(8)]+['facetOutside'],FacetKind=['kind'+n for n in b.KIND_NAMES]+['kindFuture','kindOutside'],SemanticIdentity=['idMain','idSecond']+['idFacet'+str(i) for i in range(8)]+['idChanged','idOutside'],AuthorityScope=['authorityMain','authoritySecond']+['authorityFacet'+str(i) for i in range(8)]+['authorityChanged','authorityOutside'],TypedRelationReference=['relation'+str(i) for i in range(8)]+['relationOutside'],GlobalViewReference=['viewReference','viewProjection','viewOutside'],LocationReference=['locationMain','locationMoved','locationOutside'],ContextReference=['contextMain','contextSecond','contextChanged','contextOutside'],MovementReference=['movePlain','moveDecision','moveOutside'],Token=['empty','none','reference','differentReference'])
 cs={'EMPTY':'empty','NONE':'none',**{n:'kind'+n for n in b.KIND_NAMES}}
 def suffix(x,prefix):return x[len(prefix):]
 def byagg(prefix,a):return prefix+suffix(a,'agg')
 def fagg(f):return 'aggOutside' if f=='facetOutside' else 'aggMain' if int(suffix(f,'facet'))<7 else 'aggSecond'
 maps={n:(lambda a,n=n,s=s:'none' if n=='aggregateEffect' else 'locationMain' if n=='aggregateLocation' and a!='aggOutside' else byagg({'aggregateHome':'home','aggregateOwner':'owner','aggregateUnit':'unit','aggregateRecovery':'recovery','aggregateManifest':'manifest','aggregateLocation':'location','aggregateIdentity':'id','aggregateContext':'context','aggregateAuthority':'authority'}[n],a)) for n,s in b.FACETS.items()}
 maps.update(homeOwner=lambda h:'owner'+suffix(h,'home'),homeUnit=lambda h:'unit'+suffix(h,'home'),homeRecovery=lambda h:'recovery'+suffix(h,'home'),unitRecovery=lambda u:'recovery'+suffix(u,'unit'),carrierAggregate=lambda c:'agg'+suffix(c,'carrier'),carrierHome=lambda c:'home'+suffix(c,'carrier'),manifestAggregate=lambda m:'agg'+suffix(m,'manifest'),manifestOwner=lambda m:'owner'+suffix(m,'manifest'),manifestUnit=lambda m:'unit'+suffix(m,'manifest'),facetAggregate=fagg,facetHome=lambda f:byagg('home',fagg(f)),facetOwner=lambda f:byagg('owner',fagg(f)),facetUnit=lambda f:byagg('unit',fagg(f)),facetIdentity=lambda f:'idFacet'+suffix(f,'facet') if f!='facetOutside' else 'idOutside',facetAuthority=lambda f:'authorityFacet'+suffix(f,'facet') if f!='facetOutside' else 'authorityOutside',facetContext=lambda f:byagg('context',fagg(f)),facetKind=lambda f:'kindOutside' if f=='facetOutside' else 'kind'+b.KIND_NAMES[int(suffix(f,'facet'))%7],facetRelation=lambda f:'relation'+suffix(f,'facet'),relationFacet=lambda r:'facet'+suffix(r,'relation'),relationAggregate=lambda r:fagg('facet'+suffix(r,'relation')))
 maps['movementAggregate']=lambda m:'aggOutside' if m=='moveOutside' else 'aggMain'
 for family,prefix in [('Identity','id'),('Context','context'),('Authority','authority'),('Location','location')]:
  maps['movementBefore'+family]=lambda m,prefix=prefix:prefix+('Outside' if m=='moveOutside' else 'Main')
  maps['movementAfter'+family]=lambda m,prefix=prefix,family=family:prefix+'Outside' if m=='moveOutside' else 'locationMoved' if family=='Location' else prefix+'Changed' if m=='moveDecision' else prefix+'Main'
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};p={n:[] for n in b.SIGNATURE};aggregates=['aggMain','aggSecond']
 for s in b.SORTS:
  if s not in ['AggregateReference','Token']:p[s+'Declared']=[[x] for x in ds[s] if not x.endswith('Outside')]
 p['HomeApplicable']=p['AggregateInScopeDeclared']=[[a] for a in aggregates]
 for n in b.FACETS:p[n+'BindingDeclared']=[[a,maps[n](a)] for a in aggregates]
 p['HomeInScopeDeclared']=[['homeMain'],['homeSecond']];p['HomeForAggregateDeclared']=[[a,maps['aggregateHome'](a)] for a in aggregates]
 for n in ['homeOwner','homeUnit','homeRecovery']:p[n+'BindingDeclared']=[[h,maps[n](h)] for h in ['homeMain','homeSecond']]
 p['UnitRecoveryBindingDeclared']=[[u,maps['unitRecovery'](u)] for u in ['unitMain','unitSecond']]
 p['CarrierInScopeDeclared']=[['carrierMain'],['carrierSecond']];p['CarrierInAggregateDeclared']=[[c,maps['carrierAggregate'](c)] for c in ['carrierMain','carrierSecond']];p['CanonicalAtDeclared']=[[c,maps['carrierHome'](c)] for c in ['carrierMain','carrierSecond']]
 for n in ['manifestAggregate','manifestOwner','manifestUnit']:p[n[0].upper()+n[1:]+'BindingDeclared']=[[x,maps[n](x)] for x in ['manifestMain','manifestSecond']]
 p['FacetInScopeDeclared']=[[f] for f in ds['FacetReference'][:-1]];p['FacetMemberDeclared']=[[maps['facetAggregate'](f),f] for f in ds['FacetReference'][:-1]];p['FacetAggregateEdgeDeclared']=[[f,maps['facetAggregate'](f),maps['facetRelation'](f)] for f in ds['FacetReference'][:-1]]
 p['ViewInScopeDeclared']=[['viewReference'],['viewProjection']];p['ViewReferencesCarrierDeclared']=[['viewReference','carrierMain']];p['ViewProjectsCarrierDeclared']=[['viewProjection','carrierMain']];p['MovementInScopeDeclared']=[['movePlain'],['moveDecision']];p['SemanticDecisionDeclared']=[['moveDecision']];p['HomeActualAuthority']=[['aggSecond']]
 model={'domains':ds,'constants':cs,'functions':functions,'predicates':p};refresh(model);return model

def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def coherent_fn(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('necessary-owner-unit-carrier-facet-index-and-movement-declarations')
 add('no-applicable-aggregate',lambda m:m['predicates'].update(HomeApplicable=[],AggregateInScopeDeclared=[],CarrierInScopeDeclared=[],CarrierInAggregateDeclared=[],FacetInScopeDeclared=[],FacetMemberDeclared=[],MovementInScopeDeclared=[]),I=False)
 add('absent-canonical-carrier-population',lambda m:m['predicates'].update(CarrierInScopeDeclared=[],CarrierInAggregateDeclared=[]),I=False)
 add('absent-view-scope-populations',lambda m:m['predicates'].update(ViewInScopeDeclared=[]),I=False)
 add('absent-no-decision-movement-population',lambda m:m['predicates'].update(MovementInScopeDeclared=[['moveDecision']]),I=False)
 add('decision-gated-change-permitted',lambda m:m['predicates'].update(SemanticDecisionDeclared=[['movePlain'],['moveDecision']]),I=False)
 add('authority-decision-gated-change-permitted',lambda m:(m['predicates'].update(AuthorityDecisionDeclared=[['movePlain']]),coherent_fn(m,'movementAfterAuthority','movePlain','authorityChanged')),I=False)
 add('future-facet-kind-not-global-vocabulary-error',lambda m:coherent_fn(m,'facetKind','facet0','kindFuture'),I=False)
 add('matching-owner-unit-outside-governed-candidate-domain-ignored',lambda m:(setfn(m,'homeOwner','homeOutside','ownerMain'),setfn(m,'homeUnit','homeOutside','unitMain')))
 add('outside-canonical-at-and-path-inferences-ignored',lambda m:(m['predicates']['CanonicalAtDeclared'].append(['carrierOutside','homeOutside']),m['predicates']['PathOwnerInferenceDeclared'].append(['aggOutside'])))
 add('same-facet-id-across-independent-aggregates-not-global-injectivity',lambda m:setfn(m,'facetIdentity','facet7','idFacet0'))
 for name in b.ACTUAL:add('independently-supported-actual-'+name,lambda m,name=name:m['predicates']['HomeActual'+name].append(['aggMain']),I=False)
 for n in b.EXCLUDED:add('prohibited-'+n,lambda m,n=n:m['predicates'][n].append(['aggMain']),T=False,I=None)
 for n,s in b.FACETS.items():
  add('missing-binding-'+n,lambda m,n=n:m['predicates'].update({n+'BindingDeclared':m['predicates'][n+'BindingDeclared'][1:]}),T=False,I=None)
  if s!='Token':add('conflicting-binding-'+n,lambda m,n=n,s=s:m['predicates'][n+'BindingDeclared'].append(['aggMain',m['domains'][s][-1]]),T=False,I=None)
 add('aggregate-home-empty-reference',lambda m:setfn(m,b.HANDLES['HomeReference'],'homeMain','empty'),T=False,I=None)
 add('home-owner-mismatch',lambda m:setfn(m,'homeOwner','homeMain','ownerSecond'),T=False,I=None)
 add('home-unit-mismatch',lambda m:setfn(m,'homeUnit','homeMain','unitSecond'),T=False,I=None)
 add('unit-recovery-mismatch',lambda m:setfn(m,'unitRecovery','unitMain','recoverySecond'),T=False,I=None)
 add('extra-governed-home-hidden-by-selector',lambda m:(m['predicates']['HomeInScopeDeclared'].append(['homeOutside']),m['predicates']['HomeReferenceDeclared'].append(['homeOutside']),setfn(m,'homeOwner','homeOutside','ownerMain'),setfn(m,'homeUnit','homeOutside','unitMain')),T=False,I=None)
 add('missing-home-for-aggregate-relation',lambda m:m['predicates'].update(HomeForAggregateDeclared=[['aggSecond','homeSecond']]),T=False,I=None)
 add('carrier-second-home-hidden-by-selector',lambda m:m['predicates']['CanonicalAtDeclared'].append(['carrierMain','homeSecond']),T=False,I=None)
 add('carrier-no-canonical-home-relation',lambda m:m['predicates'].update(CanonicalAtDeclared=[['carrierSecond','homeSecond']]),T=False,I=None)
 add('carrier-home-does-not-carry-aggregate',lambda m:setfn(m,'carrierHome','carrierMain','homeSecond'),T=False,I=None)
 add('missing-carrier-aggregate-member',lambda m:m['predicates'].update(CarrierInAggregateDeclared=[['carrierSecond','aggSecond']]),T=False,I=None)
 for n in ['manifestAggregate','manifestOwner','manifestUnit']:
  add('manifest-incorrect-'+n,lambda m,n=n:setfn(m,n,'manifestMain',m['domains'][b.FUNCTIONS[n][1]][1]),T=False,I=None)
  field=n[0].upper()+n[1:]+'BindingDeclared';add('manifest-missing-'+n,lambda m,field=field:m['predicates'].update({field:m['predicates'][field][1:]}),T=False,I=None)
 add('colocated-facet-identities-collapsed',lambda m:setfn(m,'facetIdentity','facet1','idFacet0'),T=False,I=None)
 add('colocated-facet-authority-scopes-collapsed',lambda m:setfn(m,'facetAuthority','facet1','authorityFacet0'),T=False,I=None)
 add('facet-collapsed-with-aggregate-identity',lambda m:setfn(m,'facetIdentity','facet0','idMain'),T=False,I=None)
 add('facet-wrong-home',lambda m:setfn(m,'facetHome','facet0','homeSecond'),T=False,I=None)
 add('facet-different-lifecycle-owner-colocated',lambda m:setfn(m,'facetOwner','facet0','ownerSecond'),T=False,I=None)
 add('facet-independent-unit-colocated',lambda m:setfn(m,'facetUnit','facet0','unitSecond'),T=False,I=None)
 add('facet-missing-typed-edge',lambda m:m['predicates'].update(FacetAggregateEdgeDeclared=m['predicates']['FacetAggregateEdgeDeclared'][1:]),T=False,I=None)
 add('typed-edge-wrong-target',lambda m:setfn(m,'relationAggregate','relation0','aggSecond'),T=False,I=None)
 add('global-view-duplicates-canonical-carrier',lambda m:m['predicates']['ViewContainsCanonicalCopyDeclared'].append(['viewReference','carrierMain']),T=False,I=None)
 for suffix,value in [('Identity','idChanged'),('Context','contextChanged'),('Authority','authorityChanged')]:add('no-decision-movement-changes-'+suffix,lambda m,suffix=suffix,value=value:coherent_fn(m,'movementAfter'+suffix,'movePlain',value),T=False,I=None)
 add('movement-aggregate-binding-missing',lambda m:m['predicates'].update(MovementAggregateBindingDeclared=[['moveDecision','aggMain']]),T=False,I=None)
 add('movement-before-identity-not-bound-to-aggregate',lambda m:coherent_fn(m,'movementBeforeIdentity','movePlain','idChanged'),T=False,I=None)
 for n,s in [('aggregateHome','HomeReference'),('aggregateOwner','OwnerReference'),('aggregateUnit','UnitReference'),('facetRelation','TypedRelationReference'),('movementAfterIdentity','SemanticIdentity')]:add('malformed-total-output-'+n,lambda m,n=n:m['functions'][n][0].update(value='not-in-sort'),T=None,I=None,error='sort-mismatch')
 add('malformed-empty-home-domain',lambda m:m['domains'].update(HomeReference=[]),T=None,I=None,error='empty-sort-domain')
 add('malformed-missing-function',lambda m:m['functions'].pop('homeOwner'),T=None,I=None,error='missing-function')
 add('malformed-duplicate-function-tuple',lambda m:m['functions']['homeOwner'].append(copy.deepcopy(m['functions']['homeOwner'][0])),T=None,I=None,error='duplicate-function-tuple')
 return rows
'''
tail=old[old.index('def qualify('):].replace('cal.definition.artifact-type-request/delivery-manifest.json','cal.definition.artifact-type-resolution/delivery-manifest.json').replace('ArtifactTypeResolution','CanonicalPackageHome')
tail=tail.replace('Typed exact explicit-admitted/current-discriminator union,distinct cardinalities,recorded states,no effect and metadata movement checked on supplied models. Actual execution,registry fidelity,validation,admission,owner activation,consumer alignment and whole fidelity remain pending.','Typed declared owner/unit/home,carrier uniqueness,manifest fields,distinct facets,typed edges,reference-only views and movement invariance checked on supplied finite models. Actual ownership,canonical source correctness,migration,consumer alignment and whole fidelity remain pending.')
code=head+body+tail;ast.parse(code)
with (dest/'verify_candidate.py').open('x') as f:f.write(code)
# Fix the inherited operation variable in the prepared query builder before native execution.
f=dest/'build_candidate.py';s=f.read_text();target="allof([('AggregateReference','o')],implies(APP,pred('HomeActual'+n,O)))";assert target in s;s=s.replace(target,"allof([('AggregateReference','a')],implies(APP,pred('HomeActual'+n,A)))");ast.parse(s);f.write_text(s)
print('Prepared CPH finite models and hostile controls; no native unit created.')
