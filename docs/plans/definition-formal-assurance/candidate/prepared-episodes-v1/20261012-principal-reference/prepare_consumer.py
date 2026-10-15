"""Prepare exact Principal Reference current carrier comparisons, without effectful consumers."""
from pathlib import Path
import ast,json,hashlib
p=Path(__file__).resolve().parent;root=Path.cwd();u=root/'docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/definitions/cal.definition.principal-reference';prev=u.with_name('cal.definition.principal')
def ref(f):return {'path':str(f.relative_to(root)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
registry=root/'authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json';r=json.loads(registry.read_bytes());cur=[x for x in r['admitted_contracts'] if x['lifecycle_state']=='admitted-current'];context=json.loads((u/'context.json').read_bytes());direct=[x for x in cur if context['source_selection']['version_ref'] in x['semantic_definition_refs']];assert [x['artifact_type_ref'] for x in direct]==['cal.artifact-type.principal-reference/v1']
selected={'registry':ref(registry),'typed_receipt':ref(u/'types-logic-receipt.json'),'typed_separate_audit':ref(p/'typed-stage-audit-command-result.json'),'C70_decision':ref(root/'docs/decisions/0070-definition-complete-lab-model-admission/decision.json')}
for key in ['principal','principal-reference','authority-claim','delegation','person','person-reference','team','agent-instance']:
 row=next(x for x in cur if x['artifact_type_ref']=='cal.artifact-type.'+key+'/v1')
 for k,f in [('schema',root/row['schema_path']),('artifact',root/row['artifact_path']),('fixture-record.json',(root/row['schema_path']).parent/'fixtures/valid/record.json')]:selected[key+'-'+k]=ref(f)
with (p/'consumer-discovery.json').open('x') as f:json.dump({'schema_version':'definition-assurance-PrincipalReference-consumer-discovery/v1-candidate','authority_effect':'none','selected_inputs':selected,'direct_current_binding_types':[x['artifact_type_ref'] for x in direct],'accepted_maps':[],'semantic_ready':False,'full_delivery_complete':False},f,indent=2)
s=(prev/'inspect_carrier_consumers.py').read_text()
s=s.replace('20261012-principal\'','20261012-principal-reference\'').replace('../cal.definition.identity-lineage/','../cal.definition.principal/')
s=s.replace("==['cal.artifact-type.principal/v1']","==['cal.artifact-type.principal-reference/v1']").replace("'source-body-keeps-review-only-ceiling','defines Principal for review only'","'source-body-keeps-review-only-ceiling','defines Principal Reference for review only'")
s=s.replace("'direct-current-C70-Principal-contract'","'direct-current-C70-PrincipalReference-contract'").replace("'C65-Principal-Definition-distinct-from-C70-type'","'C65-PrincipalReference-Definition-distinct-from-C70-type'")
start=s.index(" for n,text in {");end=s.index("\n carrier_probes=[]",start)
s=s[:start]+""" for n,text in {'reference-is-Principal':'hyp:reference is Principal and identity authority','reference-authenticates':'hyp:route and issuer text authenticate the Principal','reference-grants-authority':'hyp:Principal reference grants authority without separate evidence','resolved-label-proves-resolution':'hyp:resolved label proves real Principal resolution','integrity-token-proves-fidelity':'hyp:any nonempty integrity token proves fidelity','privacy-label-proves-no-credentials':'hyp:privacy label proves no reusable credentials','consumer-name-proves-minimality':'hyp:consumer label proves minimum necessary data','C70-type-admission-accepts-maps':'hyp:C70 type admission accepts every formal carrier map'}.items():probe(n,lambda x,text=text:x['voices']['scientific_formal'].update(normative_statement=text),True)""" + s[end:]
start=s.index(" comparison=[];");end=s.index("\n for n,expected in wanted:",start)
true=['minimal-resolved-unresolved-reference-and-separate-current-evidence','unresolved-reference-unused-Principal-handle-empty','registry-only-unused-issuer-binding-absent-allowed','issuer-only-unused-registry-binding-absent-allowed','evidence-current-at-additional-time','reference-and-decision-scopes-distinct-allowed','inclusive-identity-and-record-with-populations-preserved','independently-supported-Decision-ActualAuthority']
empty=['no-selected-references-uses-decisions','references-without-modeled-uses','references-without-authority-decisions','no-independent-authority']
false=['both-resolved-and-unresolved','resolved-stable-identifier-mismatch','resolved-kind-mismatch','embedded-forbidden-or-unsupported-secretField','embedded-forbidden-or-unsupported-credentialField','consumer-needs-unembedded-field','decision-evidence-not-current-at-time','decision-evidence-wrong-scope','decision-evidence-wrong-resolved-Principal']
s=s[:start]+""" cp('PrincipalReference','registry-only-origin-without-required-issuer',lambda x:x['payload'].pop('issuer_ref'),False)
 cp('PrincipalReference','explicit-unresolved-state-has-no-payload-field',lambda x:x['payload'].update(resolution_state='unresolved'),False)
 cp('PrincipalReference','consumer-needed-classes-have-no-payload-field',lambda x:x['payload'].update(consumer_needed_fields=['kind']),False)
 cp('PrincipalReference','wrong-Principal-kind-token-shape-valid',lambda x:x['payload'].update(principal_kind='hyp:wrong-kind'),True)
 cp('PrincipalReference','symbolic-credential-content-shape-valid',lambda x:x['payload'].update(principal_ref='hyp:symbolic-credential-class'),True)
 cp('PrincipalReference','symbolic-secret-route-shape-valid',lambda x:x['payload'].update(resolution_route='hyp:symbolic-secret-class'),True)
 cp('PrincipalReference','unassessed-privacy-posture-shape-valid',lambda x:x['payload'].update(privacy_posture='hyp:no-data-classification-evidence'),True)
 cp('PrincipalReference','separate-current-evidence-has-no-payload-field',lambda x:x['payload'].update(current_grant_evidence_ref='hyp:unaccepted-evidence'),False)
 comparison=[];compiled=load('static-ir.json');controls=load('model-controls.json')['results'];wanted="""+repr([(n,(True,True)) for n in true]+[(n,(True,False)) for n in empty]+[(n,(False,True)) for n in false])+s[end:]
start=s.index(" issues=[");end=s.index("\n ];findings=",start)
issues=[
'Current C70 PrincipalReference/v1 directly binds exact C65 Principal Reference. Seven compared identity/claim/delegation/subject contracts bind their own meanings;type admission does not accept this formalization or create reference fixtures.',
'Definition shape and pure projections accept hypothetical assertions of identity,authentication,privacy absence,minimum consumer need,resolution or authority. These are read-only schema observations,not accepted meaning or actual outcomes.',
'PrincipalReference payload requires principal_ref,kind,issuer,route,integrity and privacy text. The source permits registry-only origin and explicitly unresolved state;the schema has no registry or resolution-state field. Accepted representation of these alternatives is absent.',
'Nonempty identifier,kind,issuer,route and integrity tokens accept wrong Principal/kind,unverified issuer,non-hash integrity and symbolic secret/credential classes. No real secret is used;shape alone does not prove authentic resolution,identity authority or data absence.',
'The six source data classes and exact consumer-needed class relation have no accepted carrier mapping. Privacy posture is not an absence/minimization proof;governance metadata and primary reference contents remain separately mapped.',
'AuthorityClaim and Delegation have separately admitted shapes but no accepted exact reference/evidence/Principal/scope/time/currentAt map. Unresolved references do not acquire identity or authority from opaque period,revocation or grant labels.',
'C70 admits only the exact integrated Governed Model ordinary instance with zero consumer/runtime/typed-relation activation. Principal,PrincipalReference,subject and Delegation fixtures are not joined or admitted as a resolved authorization instance. Local review/consumer bytes remain evidence.',
'Twenty-one independently evaluated PrincipalReference-only models retain unresolved selectors,conditional origins,minimum data and separate current evidence. T/I remain separate;source precedence,real privacy/current grant validity,common meanings and owner maps remain pending.'
]
s=s[:start]+" issues=[\n"+",\n".join(" "+repr(x) for x in issues)+s[end:]
s=s.replace('PRIN-CONSUMER-FINDING-','PREF-CONSUMER-FINDING-').replace('accepted_Principal_carrier_map','accepted_PrincipalReference_carrier_map').replace('accepted_Principal_map_refs','accepted_PrincipalReference_map_refs')
s=s.replace('actual_Principal_identity_recognition_authorization_or_grant_created','actual_Principal_reference_resolution_or_authority_created').replace('actual_Principal_recognition_authorization_or_grant_created','actual_PrincipalReference_resolution_or_authority_created')
s=s.replace('definition-assurance-Principal-carrier','definition-assurance-PrincipalReference-carrier').replace('PASS-for-exact-Principal-recognition-reference-grant-and-subject-contract-comparisons','PASS-for-exact-PrincipalReference-resolution-minimum-data-and-separate-evidence-comparisons').replace('Fresh Principal consumer observations differ','Fresh PrincipalReference consumer observations differ')
s=s.replace('seventeen Principal-only independent models','twenty-one PrincipalReference-only independent models')
s=s.replace("'Principal_recognition_observation'","'Principal_boundary_comparison_observation'")
insert=s.index("\n ck('fixtures-not-a-joined-")
s=s[:insert]+"""
 ck('PrincipalReference-source-alternatives-not-explicit-in-carrier',not any(n in pr_payload['properties'] for n in ['registry_ref','resolution_state','consumer_needed_fields','current_grant_evidence_ref']) and 'issuer_ref' in pr_payload['required'])
 ck('PrincipalReference-kind-and-privacy-are-shape-only',pr_payload['properties']['principal_kind']==pr_payload['properties']['privacy_posture']=={'minLength':1,'type':'string'})
""" +s[insert:]
insert=s.index("'fixture_join_observation':")
s=s[:insert]+"""'reference_carrier_observation':{'required_payload_fields':pr_payload['required'],'registry_only_origin_represented_explicitly':False,'unresolved_state_represented_explicitly':False,'consumer_needed_classes_represented_explicitly':False,'separate_current_evidence_represented_explicitly':False,'issuer_integrity_kind_privacy_nonempty_strings_only':True,'actual_resolution_or_data_classification_performed':False,'accepted_map_refs':[]}, """+s[insert:]
ast.parse(s)
with (u/'inspect_carrier_consumers.py').open('x') as f:f.write(s)
s=(p.parent/'20261012-principal/capture_consumer.py').read_text().replace("cal.definition.principal'","cal.definition.principal-reference'")
with (p/'capture_consumer.py').open('x') as f:f.write(s)
print('Prepared current Principal Reference carrier comparisons;not yet executed.')

