import assert from 'node:assert/strict';import{readFileSync,writeFileSync,mkdirSync,mkdtempSync}from'node:fs';import path from'node:path';import{build,root,craftRoot,sha}from'./build.mjs';import{createSourceOperationCompiler}from'../../../../implementation/artifact-runtime/compile-source-operation.mjs';import{evaluateArtifact}from'../../../../implementation/artifact-runtime/pure-operation.mjs';
const b=build(),compiler=await createSourceOperationCompiler(path.join(craftRoot,'cli')),base=path.join(root,'.local/fixtures');mkdirSync(base,{recursive:true});const directory=mkdtempSync(path.join(base,'run-')),compiled=new Map(),checks=[];
async function call(name,input){let value=compiled.get(name);if(!value){const out=path.join(directory,name);compiler.compile({modelRoot:path.join(b.output,'model'),selector:'Lab.SharedDesign.'+name,outputDirectory:out});value={out,sha:sha(readFileSync(path.join(out,'manifest.json')))};compiled.set(name,value);}const r=await evaluateArtifact(value.out,'operation.mjs',input,{manifest_sha256:value.sha});assert.equal(r.ok,true,JSON.stringify(r));const output=JSON.parse(new TextDecoder().decode(r.wire));if(output.tag!=='Returned')throw Error(output.fields.code);return output.fields.value;}
const check=async(name,fn)=>{await fn();checks.push(name);console.log('PASS '+name);},hash='a'.repeat(64),other='b'.repeat(64),B=(ref='fixture:body',digest=hash)=>({ref,sha256:digest,bytes:'10'});
const review=(ref='fixture:definition')=>({target:B(ref),expected_owner:'role:definition-owner',scope:'scope:fixture',source_cut:hash,source_current:true,fields_receipt:B('fixture:schema-proof'),consumer_bindings_current:true,disposition:null});
function accept(value){return {...value,disposition:{target:value.target,previous:null,owner:value.expected_owner,scope:value.scope,source_cut:value.source_cut,outcome:'Accepted',role_assignment:B('fixture:role'),verification_receipt:B('fixture:owner-proof')}};}
const V=(subject,scope,cut,predicate,issuer="fixture:verifier")=>({subject,scope,cut,predicate,issuer,policy:B("fixture:policy"),proof:B("fixture:proof")});
const five=Array.from({length:5},(_,i)=>review('fixture:definition:'+i)),fiveArgs={expected:five.map(x=>x.target),reviews:five};
await check('five-pending-source-targets-remain-owner-pending',async()=>assert.deepEqual(await call('ReviewFiveDefinitions',fiveArgs),Array(5).fill('NeedsOwnerReview')));
await check('duplicate-definition-target-refused',()=>assert.rejects(()=>call('ReviewFiveDefinitions',{...fiveArgs,reviews:[five[0],five[0],...five.slice(2)]}),/five-exact-definition-targets-required/));
await check('different-source-bytes-refused',()=>assert.rejects(()=>call('ReviewFiveDefinitions',{...fiveArgs,reviews:[{...five[0],target:B(five[0].target.ref,other)},...five.slice(1)]}),/five-exact-definition-targets-required/));
for(const[name,patch,expected]of[['stale',{source_current:false},'Stale'],['unverified',{fields_receipt:null},'NeedsEvidence'],['old-consumer-bindings',{consumer_bindings_current:false},'NeedsContextUpdate']])await check('definition-review-'+name,async()=>assert.equal((await call('ReviewFiveDefinitions',{...fiveArgs,reviews:[{...five[0],...patch},...five.slice(1)]}))[0],expected));
await check('accepted-fixture-does-not-create-an-owner-decision',async()=>assert.deepEqual(await call('ReviewFiveDefinitions',{...fiveArgs,reviews:five.map(accept)}),Array(5).fill('CandidateOnly')));
await check('wrong-owner-evidence-refused',async()=>{const x=accept(five[0]);x.disposition.owner='role:other';assert.equal((await call('ReviewFiveDefinitions',{...fiveArgs,reviews:[x,...five.slice(1)]}))[0],'InvalidEvidence');});
const compatibility={expected_owner:'role:definition-owner',expected_scope:'scope:fixture',cut:hash,fidelity:V(B(),'scope:fixture',hash,'representation-fidelity'),source_edges:[],target_edges:[],intent:'CreateV2',source_carrier:'V2',target_carrier:'V2',source_body:B(),target_body:B(),selected_schema:B('fixture:schema'),observed_schema:B('fixture:schema'),schema_receipt:B('fixture:schema-proof'),target_schema_valid:true,carrier_current:true,carrier_admission:B('fixture:carrier-admission'),source_normative:hash,target_normative:hash,source_relations:[],target_relations:[],allowed_target_relations:['relation.successor-of','relation.originates-from'],relation_mappings:[],lineage:null,meaning_review:null};
await check('native-supported-v2-create-is-candidate-plan',async()=>assert.equal(await call('SelectCompatibility',{value:compatibility}),'CandidateV2'));
await check('retained-v1-read-does-not-require-current-carrier',async()=>assert.equal(await call('SelectCompatibility',{value:{...compatibility,intent:'ReadRetained',source_carrier:'V1',target_carrier:'V1',carrier_current:false,carrier_admission:null}}),'HistoricalRead'));
await check('changed-bytes-under-same-version-refused',async()=>assert.equal(await call('SelectCompatibility',{value:{...compatibility,target_body:B('fixture:body',other)}}),'IdentityRewriteRefused'));
await check('automatic-v2-to-v1-downcast-refused',async()=>assert.equal(await call('SelectCompatibility',{value:{...compatibility,intent:'Downgrade',target_carrier:'V1'}}),'AutomaticDowngradeRefused'));
await check('schema-binding-not-a-declared-pass-flag',async()=>assert.equal(await call('SelectCompatibility',{value:{...compatibility,observed_schema:B('fixture:schema',other)}}),'NeedsEvidence'));
const upgrade={...compatibility,intent:'Upgrade',source_carrier:'V1',target_body:B('fixture:successor'),fidelity:V(B('fixture:successor'),'scope:fixture',hash,'representation-fidelity'),source_relations:['relation.supersedes'],target_relations:['relation.successor-of'],source_edges:[B('fixture:edge1')],target_edges:[B('fixture:edge2')]};
await check('v1-supersedes-needs-explicit-relation-review',async()=>assert.equal(await call('SelectCompatibility',{value:upgrade}),'NeedsRelationReview'));
await check('unsupported-v2-target-kind-not-dropped',async()=>assert.equal(await call('SelectCompatibility',{value:{...upgrade,target_relations:['relation.supersedes']}}),'UnsupportedRelation'));
await check('reviewed-relation-mapping-alone-does-not-approve-upgrade',async()=>assert.equal(await call('SelectCompatibility',{value:{...upgrade,relation_mappings:[{old_kind:'relation.supersedes',new_kind:'relation.successor-of',review:B('fixture:mapping-review'),source_edge:B('fixture:edge1'),target_edge:B('fixture:edge2')}]}}),'NeedsOwnerReview'));
const ordinaryUpgrade={...upgrade,source_relations:['relation.originates-from'],target_relations:['relation.originates-from'],target_edges:upgrade.source_edges,lineage:B('fixture:lineage'),meaning_review:{...accept(review()).disposition,target:upgrade.target_body,previous:upgrade.source_body}};
await check('exact-reviewed-successor-plan-preserves-old-body',async()=>assert.equal(await call('SelectCompatibility',{value:ordinaryUpgrade}),'CandidateSuccessor'));
await check('meaning-change-not-called-representation-only',async()=>assert.equal(await call('SelectCompatibility',{value:{...ordinaryUpgrade,target_normative:other}}),'NeedsMeaningChange'));
const context={workspace:'workspace:fixture',kind:'Product',project:null,work:null,linked_projects:[],runtime_ref:'lab:shared-runtime',host:null,host_project_only:true,custody:null,store:null,source_cut:hash,current_source_cut:hash,effect_requested:false};
await check('product-inspection-does-not-invent-project',async()=>assert.equal(await call('AssessExecutionContext',{value:context}),'ContextPlanReady'));
await check('product-effect-requires-selected-host',async()=>assert.equal(await call('AssessExecutionContext',{value:{...context,effect_requested:true}}),'NeedsHost'));
await check('native-project-host-needs-actual-project',async()=>assert.equal(await call('AssessExecutionContext',{value:{...context,effect_requested:true,host:B('fixture:host')}}),'NeedsProject'));
await check('work-without-project-refused',async()=>assert.equal(await call('AssessExecutionContext',{value:{...context,work:'work:fixture'}}),'WrongScope'));
await check('unlinked-project-refused',async()=>assert.equal(await call('AssessExecutionContext',{value:{...context,project:'project:other'}}),'WrongScope'));
await check('selected-actual-project-context-is-still-not-permission',async()=>assert.equal(await call('AssessExecutionContext',{value:{...context,project:'project:fixture',linked_projects:['project:fixture'],host:B('fixture:host'),custody:B('fixture:custody'),store:'store:fixture',effect_requested:true}}),'ContextPlanReady'));
const creation={kind:'Definition',context_decision:'ContextPlanReady',original:B(),selected_carrier:'cal.artifact-type.definition/v2',verification_receipt:B('fixture:validated-body'),target_scope:'scope:fixture',source_cut:hash,public_route_compiled:false};
await check('creation-public-route-remains-unwired',async()=>assert.equal((await call('PlanCreationRoute',{value:creation})).decision,'NeedsRouteWiring'));
await check('compiled-draft-plan-is-unsigned-and-inert',async()=>{const x=await call('PlanCreationRoute',{value:{...creation,public_route_compiled:true}});assert.equal(x.entry_ref,'Lab.CreateDefinitionEntry');assert.equal(x.unsigned,true);assert.equal(x.authority_effect,'none');});
await check('definition-creation-does-not-downgrade-to-v1',async()=>assert.equal((await call('PlanCreationRoute',{value:{...creation,selected_carrier:'cal.artifact-type.definition/v1'}})).decision,'InvalidEvidence'));
const selector=B("fixture:selector");
const snapshot={expected_selector:selector,bundle:B('fixture:bundle'),operation:'operation:fixture',workspace:'workspace:fixture',cut:hash,expected_head:hash,predecessor:B('fixture:registry'),registry:B('fixture:postimage'),index:B('fixture:index'),source:B('fixture:snapshot'),targets:hash,draft_only:true,readers:V(B('fixture:snapshot'),'workspace:fixture',hash,'qualified-readers'),migration:V(B('fixture:postimage'),'workspace:fixture',hash,'registry-migration')};
const publication={snapshot,expected_selector:selector,observed_selector:selector,bundle:B('fixture:bundle'),bundle_review:V(B('fixture:bundle'),'workspace:fixture',hash,'closed-publication-bundle'),canonical_permission:null,observed_receipt:null,native_head:hash,workspace:'workspace:fixture',source_cut:hash,expected_registry:B('fixture:registry'),observed_registry:B('fixture:registry'),proposed_registry:B('fixture:postimage'),expected_targets:hash,proposal:B('fixture:proposal'),operation_ref:'operation:fixture',target_bodies:five.map(x=>x.target),semantic_reviews:five,registry_contract_current:false,registry_contract:null,permission:null,permission_proposal:null,native_receipt:null,publication_receipt:null,published_postimage:null};
await check('five-pending-meanings-block-publication-plan',async()=>assert.equal(await call('PlanPublication',{value:publication}),'NeedsOwnerReview'));
const reviewed={...publication,semantic_reviews:five.map(accept)};
await check('registry-v2-contract-must-be-selected-separately',async()=>assert.equal(await call('PlanPublication',{value:reviewed}),'NeedsRegistryContract'));
const permitted={...reviewed,canonical_permission:V(publication.bundle,publication.workspace,hash,'canonical-publication'),registry_contract_current:true,registry_contract:B('fixture:registry-contract'),permission:B('fixture:permission'),permission_proposal:publication.proposal};
await check('partial-owner-coverage-cannot-publish-whole-bundle',async()=>assert.equal(await call('PlanPublication',{value:{...permitted,semantic_reviews:[accept(five[0])]}}),'NeedsOwnerReview'));
await check('registry-cas-change-requires-new-postimage-review',async()=>assert.equal(await call('PlanPublication',{value:{...permitted,observed_registry:B('fixture:registry',other)}}),'NeedsPublicationRebase'));
await check('permission-and-proposal-must-match',async()=>assert.equal(await call('PlanPublication',{value:{...permitted,permission_proposal:B('fixture:wrong-proposal')}}),'NeedsPermission'));
await check('local-native-commit-not-implied-by-review',async()=>assert.equal(await call('PlanPublication',{value:permitted}),'NeedsNativeCommit'));
const committed={...permitted,native_receipt:{head:hash,workspace:publication.workspace,operation_ref:publication.operation_ref,proposal:publication.proposal,targets:hash,source_cut:hash,outcome:'Committed',proof:B('fixture:native-proof')}};
await check('native-unknown-inspect-before-redispatch',async()=>assert.equal(await call('PlanPublication',{value:{...committed,native_receipt:{...committed.native_receipt,outcome:'Unknown'}}}),'InspectOriginalOperation'));
await check('actual-native-receipt-must-match-targets',async()=>assert.equal(await call('PlanPublication',{value:{...committed,native_receipt:{...committed.native_receipt,targets:other}}}),'InvalidEvidence'));
await check('matching-native-commit-produces-publication-plan-only',async()=>assert.equal(await call('PlanPublication',{value:committed}),'PublicationPlanReady'));
await check('already-observed-postimage-preserves-receipt',async()=>assert.equal(await call('PlanPublication',{value:{...committed,observed_receipt:{operation:committed.operation_ref,selector_before:selector,selected_source:snapshot.source,bundle:committed.bundle,predecessor:committed.expected_registry,postimage:committed.proposed_registry,evidence:V(committed.proposed_registry,committed.workspace,hash,'observed-publication')}}}),'PreservePublicationReceipt'));
const join={run_ref:'join:fixture',workspace:'workspace:fixture',phase:'NativeUnknown',source_cut:hash,current_source_cut:other,original_operation:'operation:fixture',native_outcome:'Unknown',publication_outcome:'Unobserved'};
await check('unknown-is-reconciled-even-after-source-change',async()=>assert.equal(await call('PlanJoinContinuation',{value:join}),'InspectOriginalOperation'));
await check('known-refusal-preserves-original-operation',async()=>assert.equal(await call('PlanJoinContinuation',{value:{...join,native_outcome:'Refused'}}),'PreserveRefusal'));
await check('join-can-stage-publication-after-local-commit',async()=>assert.equal(await call('ValidateJoinTransition',{phase:'LocalCommitted',signal:'PreparePublication'}),true));
await check('join-cannot-skip-from-proposed-to-published',()=>assert.rejects(()=>call('ValidateJoinTransition',{phase:'Proposed',signal:'ObservePublication'}),/invalid-join-transition/));
const life={reviewed_current:B(),operation:'operation:fixture',reviewed_operation:'operation:fixture',proposal:B('fixture:transition'),reviewed_intent:'Withdraw',reviewed_successor:null,expected_owner:'role:definition-owner',scope:'scope:fixture',transition_review:V(B('fixture:transition'),'scope:fixture',hash,'lifecycle-review','role:definition-owner'),impact_review:V(B('fixture:transition'),'scope:fixture',hash,'impact-closure'),permission_review:V(B('fixture:transition'),'scope:fixture',hash,'lifecycle-permission'),intent:'Withdraw',current:B(),successor:null,owner_review:{...accept(review()).disposition,target:B()},source_cut:hash,closure_cut:hash,closure_receipt:B('fixture:closure'),unresolved_dependents:'0',consumer_manifest:B('fixture:consumers'),truncated:false,permission:B('fixture:permission')};
await check('withdrawal-needs-complete-consumer-impact',async()=>assert.equal(await call('PlanLifecycleImpact',{value:{...life,truncated:true}}),'NeedsImpactClosure'));
await check('successor-relation-does-not-implicitly-withdraw',async()=>assert.equal(await call('PlanLifecycleImpact',{value:{...life,intent:'Revise'}}),'NeedsEvidence'));
await check('explicit-reviewed-withdrawal-remains-a-plan',async()=>assert.equal(await call('PlanLifecycleImpact',{value:life}),'LifecyclePlanReady'));
const stages=['Definitions','Artifacts','Business','Bridge','System','AlchLang','Generation'].map(stage=>({stage,subject:B('fixture:stage:'+stage),source_cut:hash}));const handoffs=stages.slice(0,-1).map((x,i)=>({source_stage:x.stage,target_stage:stages[i+1].stage,input_subject:x.subject,output_subject:stages[i+1].subject,source_cut:hash,contract:B('fixture:handoff:'+i)}));
const spec={obligation:'obligation:fixture',source:B('fixture:spec'),executor:B('fixture:executor'),fixture:B('fixture:case')};
const chain={selected_targets:five.map(x=>x.target),admitted_targets:[],review_targets:five.map(x=>x.target),selection:B('fixture:selection'),selection_review:V(B('fixture:selection'),'construction',hash,'complete-selection'),specifications:[spec],source_cut:hash,stages,handoffs,required_obligations:['obligation:fixture'],specified_checks:['obligation:fixture'],unresolved_mappings:'0',definitions:five.map(accept),definition_targets:five.map(x=>x.target),definition_selection_receipt:B('fixture:meaning-selection'),construction_compatibility:B('fixture:construction-route'),prototype_selection:B('fixture:product-prototype'),language_selection:B('fixture:alchlang'),native_closure:B('fixture:native-closure'),resolved_capabilities_receipt:B('fixture:capabilities'),effects_requested:false,permission:null};
await check('seven-stage-six-adjacent-handoff-entry-plan',async()=>assert.equal(await call('AssessConstructionEntry',{value:chain}),'GenerationEntryPlanReady'));
await check('missing-adjacent-handoff-blocks-conformance',async()=>assert.equal(await call('AssessConstructionEntry',{value:{...chain,handoffs:handoffs.slice(1)}}),'NeedsCoverage'));
await check('skipped-stage-pair-blocks-conformance',async()=>assert.equal(await call('AssessConstructionEntry',{value:{...chain,handoffs:[{...handoffs[0],target_stage:'Business'},...handoffs.slice(1)]}}),'NeedsCoverage'));
await check('stale-stage-cut-invalidates-dependent-chain',async()=>assert.equal(await call('AssessConstructionEntry',{value:{...chain,stages:[{...stages[0],source_cut:other},...stages.slice(1)]}}),'NeedsCoverage'));
await check('entry-check-specification-cannot-be-empty',async()=>assert.equal(await call('AssessConstructionEntry',{value:{...chain,specifications:[]}}),'NeedsCoverage'));
await check('pending-meanings-block-conformant-entry-not-candidate-compilation',async()=>assert.equal(await call('AssessConstructionEntry',{value:{...chain,definitions:five}}),'NeedsOwnerReview'));
await check('alchlang-does-not-erase-inherited-construction-route',async()=>assert.equal(await call('AssessConstructionEntry',{value:{...chain,construction_compatibility:null}}),'NeedsConstructionCompatibility'));
await check('profile-name-without-native-closure-is-insufficient',async()=>assert.equal(await call('AssessConstructionEntry',{value:{...chain,native_closure:null}}),'NeedsEvidence'));
await check('effect-permission-remains-separate-from-generation',async()=>assert.equal(await call('AssessConstructionEntry',{value:{...chain,effects_requested:true}}),'NeedsPermission'));
const completion={expected_entry:B('fixture:entry'),assessed_entry:B('fixture:entry'),entry_receipt:{entry:B('fixture:entry'),selection:chain.selection,specifications:[spec],evidence:V(B('fixture:entry'),'construction',hash,'construction-entry')},assessment:V(B('fixture:output'),'construction',hash,'independent-conformance'),results:[{specification:spec,output:B('fixture:output'),passed:true}],entry_decision:'GenerationEntryPlanReady',expected_source_cut:hash,observed_source_cut:hash,output_manifest:B('fixture:output'),assessed_output:B('fixture:output'),independent_assessment:B('fixture:conformance'),independence_review:B('fixture:independence'),required_checks:['obligation:fixture'],passed_checks:['obligation:fixture'],failed_checks:'0',unknown_checks:'0'};
await check('completion-requires-independent-output-bound-evidence',async()=>assert.equal(await call('AssessConstructionCompletion',{value:{...completion,assessed_output:B('fixture:wrong-output')}}),'NeedsCompletionEvidence'));
await check('own-generated-output-is-not-independent-conformance',async()=>assert.equal(await call('AssessConstructionCompletion',{value:{...completion,independence_review:null}}),'NeedsCompletionEvidence'));
await check('unknown-result-does-not-count-as-pass',async()=>assert.equal(await call('AssessConstructionCompletion',{value:{...completion,unknown_checks:'1'}}),'NeedsCompletionEvidence'));
await check('complete-synthetic-observations-produce-conformance-plan-only',async()=>assert.equal(await call('AssessConstructionCompletion',{value:completion}),'ConformancePlanReady'));

await check('publication-rejects-reviews-from-another-cut',async()=>assert.equal(await call('PlanPublication',{value:{...committed,semantic_reviews:committed.semantic_reviews.map(x=>({...x,source_cut:other,disposition:{...x.disposition,source_cut:other}}))}}),'NeedsOwnerReview'));
await check('publication-refuses-unbound-historical-receipt',async()=>assert.equal(await call('PlanPublication',{value:{...committed,native_receipt:null,permission:null,publication_receipt:B('fixture:unrelated'),published_postimage:committed.proposed_registry}}),'InvalidEvidence'));
await check('publication-needs-separate-canonical-authorization',async()=>assert.equal(await call('PlanPublication',{value:{...committed,canonical_permission:null}}),'NeedsPermission'));
await check('upgrade-rejects-unrelated-owner-scope-cut',async()=>assert.equal(await call('SelectCompatibility',{value:{...ordinaryUpgrade,meaning_review:{...ordinaryUpgrade.meaning_review,owner:'role:other',scope:'scope:other',source_cut:other}}}),'NeedsOwnerReview'));
await check('retained-read-rejects-a-different-body',async()=>assert.equal(await call('SelectCompatibility',{value:{...compatibility,intent:'ReadRetained',source_carrier:'V1',target_carrier:'V1',target_body:B('fixture:different-version',other)}}),'InvalidEvidence'));
await check('lifecycle-refuses-unreviewed-successor',async()=>assert.equal(await call('PlanLifecycleImpact',{value:{...life,intent:'Revise',successor:B('fixture:unreviewed')}}),'InvalidEvidence'));
await check('completed-join-preserves-history',async()=>assert.equal(await call('PlanJoinContinuation',{value:{...join,phase:'Completed',current_source_cut:hash,native_outcome:'Committed',publication_outcome:'Committed'}}),'PreserveCompleted'));
await check('native-unknown-can-resolve-to-proven-refusal',async()=>assert.equal(await call('ValidateJoinTransition',{phase:'NativeUnknown',signal:'ObserveRefusal'}),true));
await check('completion-refuses-mismatched-entry-receipt',async()=>assert.equal(await call('AssessConstructionCompletion',{value:{...completion,entry_receipt:{...completion.entry_receipt,entry:B('fixture:other-entry')}}}),'NeedsCoverage'));
await check('construction-supports-full-46-target-selection',async()=>{const admitted_targets=Array.from({length:41},(_,i)=>B('fixture:admitted:'+i));const selected_targets=[...admitted_targets,...chain.review_targets];assert.equal(await call('AssessConstructionEntry',{value:{...chain,admitted_targets,selected_targets,definition_targets:selected_targets}}),'GenerationEntryPlanReady');});

await check('snapshot-refuses-local-authority-effect',async()=>assert.equal(await call('PlanPublication',{value:{...committed,snapshot:{...snapshot,draft_only:false}}}),'InvalidEvidence'));
await check('snapshot-refuses-unqualified-readers',async()=>assert.equal(await call('PlanPublication',{value:{...committed,snapshot:{...snapshot,readers:{...snapshot.readers,subject:B('fixture:unrelated-source')}}}}),'InvalidEvidence'));
await check('snapshot-refuses-mismatched-migration-postimage',async()=>assert.equal(await call('PlanPublication',{value:{...committed,snapshot:{...snapshot,migration:{...snapshot.migration,subject:B('fixture:unrelated-registry')}}}}),'InvalidEvidence'));
await check('construction-refuses-omitted-selected-definitions',async()=>assert.equal(await call('AssessConstructionEntry',{value:{...chain,definitions:chain.definitions.slice(1),definition_targets:chain.definition_targets.slice(1)}}),'NeedsCoverage'));
const transition={observed_operation:join.original_operation,observed_run:join.run_ref,observed_phase:'NativeUnknown',observed_signal:'ObserveRefusal',observed_outcome:'Refused',join_key:{id:'1',operation_key:'2',run_ref:join.run_ref,workspace:join.workspace,operation:join.original_operation,evidence:V(B(join.run_ref),join.workspace,hash,'stable-join-identity')},phase:'NativeUnknown',signal:'ObserveRefusal',revision:'2',observed_revision:'2',cut:hash,past_fact:B('fixture:refusal'),evidence:V(B('fixture:refusal'),join.workspace,hash,'join-transition')};
await check('join-accepts-correlated-transition-plan',async()=>assert.equal(await call('AssessJoinTransition',{value:transition}),true));
await check('join-refuses-stale-revision',()=>assert.rejects(()=>call('AssessJoinTransition',{value:{...transition,observed_revision:'1'}}),/join-revision-conflict/));
await check('join-refuses-unrelated-transition-evidence',()=>assert.rejects(()=>call('AssessJoinTransition',{value:{...transition,past_fact:B('fixture:other-fact')}}),/join-transition-unverified/));
await check('upgrade-refuses-dropped-exact-relation-edge',async()=>assert.equal(await call('SelectCompatibility',{value:{...ordinaryUpgrade,target_edges:[],target_relations:[]}}),'NeedsRelationReview'));
await check('construction-refuses-overlapping-selection-partitions',async()=>assert.equal(await call('AssessConstructionEntry',{value:{...chain,admitted_targets:[chain.review_targets[0]],review_targets:chain.review_targets.slice(0,-1)}}),'NeedsCoverage'));
await check('publication-rebases-on-stale-source-selector',async()=>assert.equal(await call('PlanPublication',{value:{...committed,observed_selector:B('fixture:other-selector')}}),'NeedsPublicationRebase'));
await check('join-refuses-unknown-as-proven-refusal',()=>assert.rejects(()=>call('AssessJoinTransition',{value:{...transition,observed_outcome:'Unknown'}}),/join-refusal-unproven/));
await check('join-refuses-another-operation-observation',()=>assert.rejects(()=>call('AssessJoinTransition',{value:{...transition,observed_operation:'operation:other'}}),/join-observation-mismatch/));
await check('completion-refuses-assessment-from-another-entry',async()=>assert.equal(await call('AssessConstructionCompletion',{value:{...completion,assessed_entry:B('fixture:other-entry')}}),'NeedsCoverage'));

const { projectVerified, digest } = await import('./verified-projection.mjs');
const wire = value => Buffer.from(JSON.stringify(value));
const scope = 'fixture:projection';
function signedFixture(operation, value) {
  const envelope = { operation, scope, cut: hash, input: { value } };
  const artifactBytes = wire(envelope);
  const receiptBytes = wire({
    version: 1, predicate: 'verified-planning-input', operation, scope, cut: hash,
    artifact: { sha256: digest(artifactBytes), bytes: artifactBytes.length }
  });
  const trustedDigest = digest(receiptBytes);
  return {
    operation, scope, cut: hash, artifactBytes, receiptBytes,
    authenticate: async bytes => digest(bytes) === trustedDigest ? trustedDigest : null
  };
}
async function dispatchVerified(fixture) {
  return call(fixture.operation, await projectVerified(fixture));
}
const projectionCases = [
  ['publication-index', 'PlanPublication', committed,
    { ...committed, snapshot: { ...snapshot, index: B('fixture:different-index') } }, 'PublicationPlanReady'],
  ['construction-executor', 'AssessConstructionCompletion', completion,
    { ...completion, entry_receipt: { ...completion.entry_receipt, specifications: [{ ...spec, executor: B('fixture:different-executor') }] },
      results: [{ specification: { ...spec, executor: B('fixture:different-executor') }, output: B('fixture:output'), passed: true }] }, 'ConformancePlanReady'],
  ['compatibility-schema', 'SelectCompatibility', ordinaryUpgrade,
    { ...ordinaryUpgrade, selected_schema: B('fixture:other-schema'), observed_schema: B('fixture:other-schema') }, 'CandidateSuccessor']
];
for (const [name, operation, original, modified, expected] of projectionCases) {
  const fixture = signedFixture(operation, original);
  await check('verified-original-' + name, async () => assert.equal(await dispatchVerified(fixture), expected));
  await check('regression-rejects-' + name, () => assert.rejects(
    () => dispatchVerified({ ...fixture, artifactBytes: wire({ operation, scope, cut: hash, input: { value: modified } }) }),
    /receipt-artifact-mismatch/
  ));
}
const badCommit = { ...transition, signal:'ObserveNativeCommit', observed_signal:'ObserveNativeCommit', observed_outcome:'Unknown' };
await check('regression-rejects-commit-with-unknown-outcome', () => assert.rejects(
  () => dispatchVerified(signedFixture('AssessJoinTransition', badCommit)), /join-outcome-incompatible/
));
const edgeTable = JSON.parse(readFileSync(path.join(root,'../JOIN-TRANSITIONS.json'))).edges;
for (const edge of edgeTable) {
  for (const outcome of ['Unobserved','Committed','Replayed','Unknown','Refused','NotDispatched']) {
    const value = { ...transition, phase: edge.phase, observed_phase: edge.phase, signal: edge.signal,
      observed_signal: edge.signal, observed_outcome: outcome };
    const name = 'join-outcome-' + edge.phase + '-' + edge.signal + '-' + outcome;
    await check(name, async () => {
      if (edge.outcomes.includes(outcome)) assert.equal(await call('AssessJoinTransition',{value}),true);
      else await assert.rejects(() => call('AssessJoinTransition',{value}),/join-outcome-incompatible|join-refusal-unproven/);
    });
  }
}
const authenticated = signedFixture('PlanPublication', committed);
await check('projection-rejects-untrusted-receipt', () => assert.rejects(
  () => dispatchVerified({...authenticated, receiptBytes:Buffer.from('{}')}), /receipt-authentication-failed/
));
await check('projection-rejects-cross-operation-replay', () => assert.rejects(
  () => dispatchVerified({...authenticated, operation:'PlanLifecycleImpact'}), /receipt-context-mismatch/
));
const result={schema_version:'shared-lab-design-prototype-verification/v1',status:'PASS',source:b.source,manifest_sha256:b.manifest_sha256,manifest_bytes:readFileSync(path.join(b.output,'manifest.json')).length,checks,check_count:checks.length,scope:'Original checked candidate model and pure planning selections; positive authority facts are synthetic fixtures, never actual owner decisions',stateful_join_initialization_executed:false,active_runtime_wired:false,production_stores_accessed:false,actual_five_owner_outcomes:null};writeFileSync(path.join(root,'../DESIGN-VERIFICATION.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));