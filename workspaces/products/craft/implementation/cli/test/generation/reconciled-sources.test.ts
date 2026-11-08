import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import test from 'node:test';
import {execFileSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import {getReconciledSource,getReconciledSourceCapsule,findReconciledSourceByDigest,validateReconciledSourceCapsule,RECONCILED_SOURCE_CAPSULE_SHA256} from '../../src/generation/reconciled-sources.ts';
import {canonicalJson,sha256} from '../../src/input/source-manifest.ts';
import {materializeReconciledSources} from '../../tools/materialize-reconciled-sources.mjs';

const cli=path.resolve(import.meta.dirname,'../..'),project=path.resolve(cli,'../..');
const selection=JSON.parse(fs.readFileSync(path.join(cli,'contracts/reconciled-source-selection.json'),'utf8'));
const projectCompositionIds=['composed_project','composed_workflow'];
const compositionIds=['operation_value_composition','composed_operation',...projectCompositionIds];
const previous132Selection={...selection,sources:selection.sources.filter((s:any)=>!compositionIds.includes(s.id))};
const previous132Sources=getReconciledSourceCapsule().sources.filter(s=>!compositionIds.includes(s.id));

test('composed project successor preserves all 134 previous sources',()=>{
 const capsule=getReconciledSourceCapsule();
 const predecessor={...selection,sources:selection.sources.filter((s:any)=>!projectCompositionIds.includes(s.id))};
 const sources=capsule.sources.filter(s=>!projectCompositionIds.includes(s.id));
 assert.equal(sources.length,134);
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(predecessor)),sources})),'6c94826ef57a34c2a85968cc6a48bd592d7eba8eca48feb7867a7242cb6c9e20');
 assert.equal(sha256(getReconciledSource('composed_project')),'15795f5e18f1bbf04a29ecce1ed941cf8e8bb7e59275d6bc34d57597b159620d');
 assert.equal(sha256(getReconciledSource('composed_workflow')),'f33b6d4f7dbaf976ed3aa1892f29735ff4ad2fb0a6c77cd2d8c7f7f6bb4d445b');
});

test('composition successor preserves all 132 preceding sources and pins both composition contracts',()=>{
 const capsule=getReconciledSourceCapsule();
 assert.equal(previous132Sources.length,132);
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous132Selection)),sources:previous132Sources})),'b564464b6f4fe2875ac862337ae517e9179008de74bed2828ba491c1d019ff9b');
 assert.equal(sha256(getReconciledSource('operation_value_composition')),'b66f8dda9f9a699be28eceeb9081779d4eb6cf54abdd4f7507d323302faa36d3');
 assert.equal(sha256(getReconciledSource('composed_operation')),'277649b65efc5fb8a39bedab056c5e78b4930a8c22b0870f72374d4e962a8026');
});

test('public Mapping successor preserves all 131 immediately preceding sources',()=>{
 const capsule=getReconciledSourceCapsule();
 const predecessor={...previous132Selection,sources:previous132Selection.sources.filter((s:any)=>s.id!=='public_mapping_value_object')};
 const sources=previous132Sources.filter(s=>s.id!=='public_mapping_value_object');
 assert.equal(sources.length,131);
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(predecessor)),sources})),'df4baa0d29b6a05f83002bd68065701637eb39a07616d446b5a2f2d8c9233b9b');
 assert.equal(sha256(getReconciledSource('public_mapping')),'5de04e24cbd6a137b3f3120b5fbfbba2775339f26cfb3d56498eaf6ae8e067b3');
 assert.equal(sha256(getReconciledSource('public_mapping_value_object')),'924538cd28276e3076e06c011ce47cbe73c8d232c230ae9d2407f3abf012caf8');
});

test('selected source capsule is complete, immutable and deterministically materialized',()=>{
 const capsule=getReconciledSourceCapsule();
 assert.equal(capsule.sources.length,136);assert.equal(capsule.capsule_sha256,RECONCILED_SOURCE_CAPSULE_SHA256);
 const previous131Selection={...previous132Selection,sources:previous132Selection.sources.filter((s:any)=>s.id!=='public_mapping_value_object')};
 const previous131Sources=previous132Sources.filter(s=>s.id!=='public_mapping_value_object');
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous131Selection)),sources:previous131Sources})),'df4baa0d29b6a05f83002bd68065701637eb39a07616d446b5a2f2d8c9233b9b','current 131-source predecessor capsule');
 assert.equal(sha256(getReconciledSource('configuration')),'9ac018e42080483f373219049b466d8a515cb3e7748181ea8e635b1162af8317');
 const historicalQualification=JSON.parse(fs.readFileSync(path.join(project,'development/reconciliation-v1/profile-compiler-reconciliation/evidence/r12-realization-matrix/qualification.json'),'utf8'));
 assert.equal(historicalQualification.source_capsule_sha256,'9886ea42053d5c0b918123649317776214b5e92139161f2602e11dde796cffe8','historical R12 evidence stays bound to its original capsule');
 assert.deepEqual(historicalQualification.denominators,{metatypes:13,languages:3,cells:39,passed_cells:39,missing_cells:0,skipped_cells:0});
 const previous130Selection={...previous131Selection,sources:previous131Selection.sources.filter((s:any)=>s.id!=='realization_matrix')};
 const previous130Sources=previous131Sources.filter(s=>s.id!=='realization_matrix');
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous130Selection)),sources:previous130Sources})),'792794a6eeeb0f1ad221b9be37c17e1ed73c6032fb9363c238a002feb5d7114b','all 130 predecessor sources remain unchanged');
 const previous129Selection={...previous130Selection,sources:previous130Selection.sources.filter((s:any)=>s.id!=='rust_native_verification')};
 const previous129Sources=previous130Sources.filter(s=>s.id!=='rust_native_verification');
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous129Selection)),sources:previous129Sources})),'6304ae9a09f666f2d9a548b6a3dd649e2b36a1fb9a5725d70ef6e74e82b2282d','all 129 predecessor sources remain unchanged');
 const latestRustIds=['rust_event','rust_operation','rust_state_machine','rust_workflow','rust_interface'];
 const previous124Selection={...previous129Selection,sources:previous129Selection.sources.filter((s:any)=>!latestRustIds.includes(s.id))};
 const previous124Sources=previous129Sources.filter(s=>!latestRustIds.includes(s.id));
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous124Selection)),sources:previous124Sources})),'e133ca03f68fb9a52a71b4bc5d2491383e720ff2c23e4addc41e6b82a587d07d','all 124 predecessor sources remain unchanged');
 const secondRustIds=['rust_calculation','rust_query','rust_mapping','rust_policy'];
 const previous120Selection={...previous129Selection,sources:previous129Selection.sources.filter((s:any)=>![...latestRustIds,...secondRustIds].includes(s.id))};
 const previous120Sources=previous129Sources.filter(s=>![...latestRustIds,...secondRustIds].includes(s.id));
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous120Selection)),sources:previous120Sources})),'85a001d48377d21319544a7f22da1f1fb926c3f55df061da4d6fcdfb6c64bac6','all 120 predecessor sources remain unchanged');
 const rustIds=[...latestRustIds,...secondRustIds,'rust_project','rust_enum','rust_rule','rust_factory'];
 const previous116Selection={...previous129Selection,sources:previous129Selection.sources.filter((s:any)=>!rustIds.includes(s.id))};
 const previous116Sources=previous129Sources.filter(s=>!rustIds.includes(s.id));
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous116Selection)),sources:previous116Sources})),'408307cd761c35f68f88147509b563acd45f15967680625ae729220aff6aa3be','all 116 predecessor sources remain unchanged');
 {
 const selection=previous116Selection,capsule={sources:previous116Sources,schema_version:'domainspec.reconciled-source-capsule/v1-candidate',authority_effect:'none'};
 const previous115Selection={...selection,sources:selection.sources.filter((s:any)=>s.id!=='python_complete_verification')};
 const previous115Sources=capsule.sources.filter(s=>s.id!=='python_complete_verification');
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous115Selection)),sources:previous115Sources})),'34f5f3ee09c05420f96688e319c26c4bcbed90f7712b5c840098bb0706f21117','all 115 predecessor sources remain unchanged');
 {
 const selection=previous115Selection,capsule={sources:previous115Sources,schema_version:'domainspec.reconciled-source-capsule/v1-candidate',authority_effect:'none'};
 const publicMappingIds=['python_public_mapping_semantic','python_public_mapping_observer','python_public_mapping_semantics'];
 const previous112Selection={...selection,sources:selection.sources.filter((s:any)=>!publicMappingIds.includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous112Selection)),sources:capsule.sources.filter(s=>!publicMappingIds.includes(s.id))})),'8a40fd0891e14042f208cd559c84acd11604f392d80422b4d35377eef4fa5e1a','all 112 predecessor sources remain unchanged');
 const interfaceIds=[...publicMappingIds,'python_interface_semantic','python_interface_observer','python_interface_semantics'];
 const previous109Selection={...selection,sources:selection.sources.filter((s:any)=>!interfaceIds.includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous109Selection)),sources:capsule.sources.filter(s=>!interfaceIds.includes(s.id))})),'cfcb51ca48528855d4756add71e7deec0eac699fbdc80be01b6c5a5fdb9ceb3a','all 109 predecessor sources remain unchanged');
 const pythonWorkflowIds=[...interfaceIds,'python_workflow_semantic','python_workflow_observer','python_workflow_materialization_observer','python_workflow_semantics'];
 const previous105Selection={...selection,sources:selection.sources.filter((s:any)=>!pythonWorkflowIds.includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous105Selection)),sources:capsule.sources.filter(s=>!pythonWorkflowIds.includes(s.id))})),'72d6497bba0c2cad2e091d404955eda4a0e5efb7d7efd0e9befe6106becc5099','all 105 predecessor sources remain unchanged');
 const operationIds=[...pythonWorkflowIds,'python_operation_semantic','python_operation_semantics'];
 const previous103Selection={...selection,sources:selection.sources.filter((s:any)=>!operationIds.includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous103Selection)),sources:capsule.sources.filter(s=>!operationIds.includes(s.id))})),'0689a839b927193be0f1cf138a14a251b9da8f1e30402ec69edfd91b11fd9753','all 103 predecessor sources remain unchanged');
 const stateMachineIds=[...operationIds,'python_state_machine_semantic','python_state_machine_observer','python_state_machine_semantics'];
 const previous100Selection={...selection,sources:selection.sources.filter((s:any)=>!stateMachineIds.includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous100Selection)),sources:capsule.sources.filter(s=>!stateMachineIds.includes(s.id))})),'cf75932b2dcb0a4157bf846208f67e75f1a7032809a67690d9aafca242328eb7','all 100 predecessor sources remain unchanged');
 const eventIds=[...stateMachineIds,'python_event_semantic','python_event_observer','python_event_semantics'];
 const previous97Selection={...selection,sources:selection.sources.filter((s:any)=>!eventIds.includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous97Selection)),sources:capsule.sources.filter(s=>!eventIds.includes(s.id))})),'3cfb47e82c73ccfd6dcf8d66b94c346c8b21200ba73c32860f6e307251be192e','all 97 predecessor sources remain unchanged');
 const factoryIds=[...eventIds,'python_factory_semantic','python_factory_semantics'];
 const previous95Selection={...selection,sources:selection.sources.filter((s:any)=>!factoryIds.includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous95Selection)),sources:capsule.sources.filter(s=>!factoryIds.includes(s.id))})),'45c8d07efdc1f3706f216c8e59c14aeecc469e5c10dcc1060b9ebe9c79f11385','all 95 predecessor sources remain unchanged');
 const sumIds=[...factoryIds,'python_sum_semantic','python_owned_semantics'];
 const previous93Selection={...selection,sources:selection.sources.filter((s:any)=>!sumIds.includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous93Selection)),sources:capsule.sources.filter(s=>!sumIds.includes(s.id))})),'c84976c4b9b5763b32234ff710af2d5d015c68ce021f0ad9ce402039cf3fedad','all 93 predecessor sources remain unchanged');
 const ownedIds=[...sumIds,'python_owned_observation','python_owned_observer'];
 const previous91Selection={...selection,sources:selection.sources.filter((s:any)=>!ownedIds.includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous91Selection)),sources:capsule.sources.filter(s=>!ownedIds.includes(s.id))})),'cea8f2ab1fc072899f528e882412e19179d8bbe30f935ecba493b24b9e4614d1','all 91 predecessor sources remain unchanged');
 const enumIds=[...ownedIds,'python_enum_semantic','python_enum_observer','python_enum_semantics'];
 const previous88Selection={...selection,sources:selection.sources.filter((s:any)=>!enumIds.includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous88Selection)),sources:capsule.sources.filter(s=>!enumIds.includes(s.id))})),'f45b613e6549d7ed942da3880cba29e9bccdc9a6d57c0a4bb18c7505e4e2e299','all 88 predecessor sources remain unchanged');
 const dataIds=[...enumIds,'python_data_semantic','python_query_observer','python_mapping_observer','python_data_semantics','python_decision_semantic','python_rule_observer','python_policy_observer','python_operation_observer'];
 for (const [id, digest] of Object.entries({python_data_semantic:'b3487fa4251af241bc1c8b3eb1102f23861d1034a1cefb07ec739f9cc7b116d0',python_query_observer:'08c92082e288705a5b283a9222f87d6c26efed7ca7df4da3033b18ca50ba7f60',python_mapping_observer:'ec95e86efa845e5d863c5ba34c303090707ec6053d7cb88b6a88a77b2e411d96'})) assert.equal(sha256(getReconciledSource(id)),digest,'unchanged data predecessor:'+id);
 const previous80Selection={...selection,sources:selection.sources.filter((s:any)=>!dataIds.includes(s.id))},previous80Sources=capsule.sources.filter(s=>!dataIds.includes(s.id));
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous80Selection)),sources:previous80Sources})),'220f912dce563046de4a5ecaf6ee0c9bd61e7a7fd5a28bea35da5cf98eeb3591','all 80 predecessor sources remain unchanged');
 {
 const selection=previous80Selection,capsule={sources:previous80Sources,schema_version:'domainspec.reconciled-source-capsule/v1-candidate',authority_effect:'none'};
 const semanticIds=['python_semantic','python_calculation_observer','python_calculation_semantics'];
 const previous77Selection={...selection,sources:selection.sources.filter((s:any)=>!semanticIds.includes(s.id))},previous77Sources=capsule.sources.filter(s=>!semanticIds.includes(s.id));
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous77Selection)),sources:previous77Sources})),'bdcb2f993514b67916612bebd49785da62d0cef1038ff8f2112cdef82aa67974','all 77 predecessor sources remain unchanged');
 {
 const selection=previous77Selection,capsule={sources:previous77Sources,schema_version:'domainspec.reconciled-source-capsule/v1-candidate',authority_effect:'none'};
 const nativeIds=['python_native','python_native_observer'];
 const previous75Selection={...selection,sources:selection.sources.filter((s:any)=>!nativeIds.includes(s.id))},previous75Sources=capsule.sources.filter(s=>!nativeIds.includes(s.id));
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous75Selection)),sources:previous75Sources})),'78fb6d8485e9d42e3d3c62fcb655884225a4e760f510d36bdb7d52961aa7b5cb','all 75 predecessor sources remain unchanged');
 {
 const selection=previous75Selection,capsule={sources:previous75Sources,schema_version:'domainspec.reconciled-source-capsule/v1-candidate',authority_effect:'none'};
 const previous74Selection={...selection,sources:selection.sources.filter((s:any)=>s.id!=='python_verification')};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous74Selection)),sources:capsule.sources.filter(s=>s.id!=='python_verification')})),'d779d494ab79aa95fab86979ceca0b44b80763163eefdd6549075208f03e1252','all 74 predecessor sources remain unchanged');
 const previous73Selection={...selection,sources:selection.sources.filter((s:any)=>!['python_cli','python_verification'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous73Selection)),sources:capsule.sources.filter(s=>!['python_cli','python_verification'].includes(s.id))})),'4fe8d364fddc60bc6c50c1f164abe87f789962a08b8492071814c72b14d05ab1','all 73 predecessor sources remain unchanged');
 const added=['python','reference_factory','python_project','python_cli','python_verification'];
 const predecessorSelection={...selection,sources:selection.sources.filter((s:any)=>!added.includes(s.id))};
 const predecessorSources=capsule.sources.filter(s=>!added.includes(s.id));
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(predecessorSelection)),sources:predecessorSources})),'b642432315fbe8415a80f65bbdf4d77e253ae557bb65598cb3499432bbac6f9a','all 70 predecessor sources remain unchanged');
 {
 const selection=predecessorSelection,capsule={sources:predecessorSources,schema_version:'domainspec.reconciled-source-capsule/v1-candidate',authority_effect:'none'};
 const compositionIds=['semantic_composition_binding','semantic_composition_reference','semantic_composition_cases','composition_effect_audit','semantic_composition_controls','semantic_composition_public'];
 const previous64Selection={...selection,sources:selection.sources.filter((s:any)=>!compositionIds.includes(s.id))},previous64Sources=capsule.sources.filter(s=>!compositionIds.includes(s.id));
 assert.equal(previous64Sources.length,64);
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous64Selection)),sources:previous64Sources})),'8fc571b7b32a2852690230bcb3dedb549b6ac5749d838167b1a6322473634b3b','all 64 predecessor sources remain unchanged');
 const workflowIds=['semantic_workflow_controls','semantic_workflow_outcomes','semantic_workflow_values','semantic_workflow_binding','semantic_workflow_execution','semantic_workflow_cases','workflow_effect_audit','workflow_orchestration_audit'];
 const previous56Selection={...previous64Selection,sources:previous64Selection.sources.filter((s:any)=>!workflowIds.includes(s.id))},previous56Sources=previous64Sources.filter(s=>!workflowIds.includes(s.id));
 assert.equal(previous56Sources.length,56);
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous56Selection)),sources:previous56Sources})),'b4885d485ba7b3c61bb09d30c222d3d1806d5d6f8c3e76a57000015bde2c4520','all 56 predecessor sources remain unchanged');
 {
 const selection=previous56Selection,capsule={schema_version:'domainspec.reconciled-source-capsule/v1-candidate',authority_effect:'none',sources:previous56Sources};
 const previous55Selection={...selection,sources:selection.sources.filter((s:any)=>s.id!=='semantic_operation_controls')};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous55Selection)),sources:capsule.sources.filter(s=>s.id!=='semantic_operation_controls')})),'b5db3c0811ff771516b5f2a2d87dc335dd5feb6938aef281731e81ab1dc6c7b9','all 55 predecessor sources remain unchanged');
 const previous54Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous54Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls'].includes(s.id))})),'31a38c6203d461d05ec4b4a4ccb8ca792625ca14571164d6d5d095936c51a8e1','all 54 predecessor sources remain unchanged');
 const previous53Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous53Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls'].includes(s.id))})),'fa3062920af7587b598f845a8ec4e8292e723b30fc5962417d61b50b51c90914','all 53 predecessor sources remain unchanged');
 const previous52Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous52Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls'].includes(s.id))})),'0f39cc36c303d5eaf8f9b0354460d74e1ba6a787c1ddf410b65af9acbcaeae40','all 52 predecessor sources remain unchanged');
 const previous51Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous51Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls'].includes(s.id))})),'80533ba1dfba83558402fb0d87f6887461702417bb0d2a36bfada2b0d5f6d1d0','all 51 predecessor sources remain unchanged');
 const previous50Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous50Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit'].includes(s.id))})),'9e94d725a01c12c6134c661c48ce9a988d0b6efcd91654caebacc33de9586f28','all 50 predecessor sources remain unchanged');
 const previous49Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous49Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls'].includes(s.id))})),'a24001a5b1cf6350e6466263b8bba1786b351967d2c0a141b41a78d8b6aadbab','all 49 predecessor sources remain unchanged');
 const previous48Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous48Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls'].includes(s.id))})),'0dc4a19d9c9a5f285214a48f89adaf22f3703777b59e9ace6380fc40e49da01b','all 48 predecessor sources remain unchanged');
 const previous47Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_rule_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous47Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_rule_controls'].includes(s.id))})),'3740ede9766eb711b7889a35d3a90d90ad2227ff75c9634ebd0d3730248743c1','all 47 predecessor sources remain unchanged');
 const previous46Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_factory_controls','semantic_rule_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous46Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_factory_controls','semantic_rule_controls'].includes(s.id))})),'508dcaa20de3d0eaa0b64f8c643952a1bf883b80fc8f273cc1a957bb29e576bd','all 46 predecessor sources remain unchanged');
 const previous45Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_factory_controls','semantic_record_witness','semantic_rule_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous45Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_factory_controls','semantic_record_witness','semantic_rule_controls'].includes(s.id))})),'65403bb70366107ec867e013cf19fbe8a79b5cfe13fd685693abc63a472467a5','all 45 predecessor sources remain unchanged');
 const previous44Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_sum_controls','semantic_record_witness','semantic_factory_controls','semantic_rule_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous44Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_sum_controls','semantic_record_witness','semantic_factory_controls','semantic_rule_controls'].includes(s.id))})),'bd8b953f0eee55c7d7f2fbc289f4f9c8a4b787ce281ff3c51b5c1219f2027b51','all 44 predecessor sources remain unchanged');
 const previous43Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_enum_controls','semantic_sum_controls','semantic_record_witness','semantic_factory_controls','semantic_rule_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous43Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_enum_controls','semantic_sum_controls','semantic_record_witness','semantic_factory_controls','semantic_rule_controls'].includes(s.id))})),'d3d5f8766a7d64ea73b93e44635c3aebd8df69158f6c6762d99ea001eb339fb5','all 43 predecessor sources remain unchanged');
 const previous42Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_controls','semantic_enum_controls','semantic_sum_controls','semantic_record_witness','semantic_factory_controls','semantic_rule_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous42Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_controls','semantic_enum_controls','semantic_sum_controls','semantic_record_witness','semantic_factory_controls','semantic_rule_controls'].includes(s.id))})),'6e6b062a8980ebaa9c940a8602d50a69bdc5de31ff76e7e1ef111dd88a32ea0a','all 42 predecessor sources remain unchanged');
 const previous41Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','verification_entrypoints','semantic_controls','semantic_enum_controls','semantic_sum_controls','semantic_record_witness','semantic_factory_controls','semantic_rule_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous41Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','verification_entrypoints','semantic_controls','semantic_enum_controls','semantic_sum_controls','semantic_record_witness','semantic_factory_controls','semantic_rule_controls'].includes(s.id))})),'5970613257f1e5bd53d8c6b47d0e62864666f8407b691949d433c5014f8c21e6','all 41 predecessor sources remain unchanged');
 const previous40Selection={...selection,sources:selection.sources.filter((s:any)=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','verification_artifact_coverage','verification_entrypoints','semantic_controls','semantic_enum_controls','semantic_sum_controls','semantic_record_witness','semantic_factory_controls','semantic_rule_controls'].includes(s.id))};
 assert.equal(sha256(canonicalJson({schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previous40Selection)),sources:capsule.sources.filter(s=>!['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','verification_artifact_coverage','verification_entrypoints','semantic_controls','semantic_enum_controls','semantic_sum_controls','semantic_record_witness','semantic_factory_controls','semantic_rule_controls'].includes(s.id))})),'c277a07a72b4b455ab9738d3cbfd8a33fac4070f0bf383c45447570351991b71','all 40 predecessor sources remain unchanged');
 const newIds=['semantic_operation_controls','semantic_interface_controls','semantic_query_controls','semantic_mapping_controls','semantic_event_controls','state_machine_effect_audit','semantic_state_machine_controls','semantic_policy_controls','semantic_rule_controls','semantic_factory_controls','semantic_record_witness','public_composition_integration','resolved_composition_bindings','verification_artifact_coverage','verification_entrypoints','semantic_controls','semantic_enum_controls','semantic_sum_controls'];
 const previousSelection={...selection,sources:selection.sources.filter((s:any)=>!newIds.includes(s.id))};
 const previousBody={schema_version:capsule.schema_version,authority_effect:capsule.authority_effect,selection_sha256:sha256(canonicalJson(previousSelection)),sources:capsule.sources.filter(s=>!newIds.includes(s.id))};
 assert.equal(sha256(canonicalJson(previousBody)),'603decdaa145fb235da690d41f06608911ec793443c3a283b3a4acd2f9a32dfa','all 38 predecessor source rows remain unchanged');
 }
 }
 }
 }
 }
 }
 }
 assert.equal(capsule.selection_sha256,sha256(canonicalJson(selection)));
 assert.ok(Object.isFrozen(capsule)&&Object.isFrozen(capsule.sources));
 for(const row of capsule.sources){
  assert.ok(Object.isFrozen(row));assert.equal(getReconciledSource(row.id),row.content);
  assert.equal(findReconciledSourceByDigest(row.sha256),row);
  assert.equal(row.content,fs.readFileSync(path.join(project,row.path),'utf8'));
  assert.equal(row.sha256,sha256(row.content));assert.equal(row.size_bytes,Buffer.byteLength(row.content));
 }
 const generated=fs.readFileSync(path.join(cli,'src/generation/reconciled-sources.generated.ts'),'utf8');
 assert.equal(materializeReconciledSources(selection,(p:string)=>fs.readFileSync(path.join(project,p),'utf8')),generated);
 assert.equal(execFileSync(process.execPath,['tools/materialize-reconciled-sources.mjs','--check'],{cwd:cli,encoding:'utf8'}).includes('"status":"pass"'),true);
 assert.equal(findReconciledSourceByDigest('0'.repeat(64)),null);
});

test('caller content, recomputed hashes, unknown IDs and active values cannot substitute compiler sources',()=>{
 const capsule=getReconciledSourceCapsule();
 for(const id of ['missing','../development/source','__proto__',null,{}])assert.throws(()=>getReconciledSource(id as any),/DS_RECONCILED_SOURCES/);
 for(const mutate of [
  (v:any)=>{v.sources[0].content+=' ';},
  (v:any)=>{v.sources[0].path='another/source';},
  (v:any)=>{v.sources.reverse();},
  (v:any)=>{v.extra=true;},
  (v:any)=>{v.sources[0].content+=' ';v.sources[0].sha256=sha256(v.sources[0].content);v.sources[0].size_bytes=Buffer.byteLength(v.sources[0].content);const {capsule_sha256,...body}=v;v.capsule_sha256=sha256(canonicalJson(body));},
 ]){const changed=structuredClone(capsule);mutate(changed);assert.throws(()=>validateReconciledSourceCapsule(changed),/DS_RECONCILED_SOURCES/);}
 let reads=0;const active={...capsule};Object.defineProperty(active,'sources',{enumerable:true,get(){reads++;return capsule.sources;}});
 assert.throws(()=>validateReconciledSourceCapsule(active),/inert data/);assert.equal(reads,0);
 assert.deepEqual(validateReconciledSourceCapsule(structuredClone(capsule)),capsule);
});

test('materialization rejects missing bytes, drift, duplicate identities and escaping source paths',()=>{
 const read=(p:string)=>fs.readFileSync(path.join(project,p),'utf8');
 assert.throws(()=>materializeReconciledSources(selection,()=>undefined),/source drift/);
 assert.throws(()=>materializeReconciledSources(selection,(p:string)=>read(p)+' '),/source drift/);
 for(const mutate of [
  (v:any)=>v.sources.push(v.sources[0]),
  (v:any)=>v.sources.push({...v.sources[0],id:'different'}),
  (v:any)=>{v.sources[0].path='../escape';},
  (v:any)=>{v.sources[0].path='/absolute';},
  (v:any)=>{v.sources[0].path='part\\file';},
  (v:any)=>{v.sources[0].path='part/../file';},
  (v:any)=>{v.sources[0].sha256='not-a-digest';},
  (v:any)=>{v.extra=true;},
 ]){const changed=structuredClone(selection);mutate(changed);assert.throws(()=>materializeReconciledSources(changed,read),/DS_SOURCE_MATERIALIZATION/);}
});

test('compiled capsule works after relocation with filesystem access limited to emitted code',t=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'ds-source-capsule-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
 const deps=path.resolve(import.meta.dirname,'../../node_modules'),src=path.join(cli,'src'),dist=path.join(root,'dist');
 const typescriptPackage=JSON.parse(fs.readFileSync(path.join(deps,'typescript/package.json'),'utf8'));
 assert.equal(process.version,'v26.8.1');assert.equal(typescriptPackage.version,'7.0.2');
 const args=[path.join(deps,'typescript/bin/tsc'),'--ignoreConfig','--strict','--skipLibCheck','--declaration','--types','node','--typeRoots',path.join(deps,'@types'),'--target','ES2022','--module','NodeNext','--rootDir',src,'--outDir',dist,path.join(src,'generation/reconciled-sources.ts')];
 try{execFileSync(process.execPath,args,{cwd:root,encoding:'utf8'});}catch(e:any){throw Error(String(e.stdout)+String(e.stderr));}
 fs.writeFileSync(path.join(root,'package.json'),JSON.stringify({type:'module'}));
 const moved=path.join(root,'relocated');fs.renameSync(dist,moved);
 const moduleUrl=pathToFileURL(path.join(moved,'generation/reconciled-sources.js')).href;
 const check=`import assert from 'node:assert/strict';import fs from 'node:fs';
  import {getReconciledSourceCapsule,getReconciledSource} from ${JSON.stringify(moduleUrl)};
  assert.throws(()=>fs.readFileSync(${JSON.stringify(path.join(project,selection.sources[0].path))}),{code:'ERR_ACCESS_DENIED'});
 assert.equal(getReconciledSourceCapsule().sources.length,136);
  assert.ok(getReconciledSource('composed_project').length>0);
  assert.ok(getReconciledSource('composed_workflow').length>0);
  assert.ok(getReconciledSource('operation_value_composition').length>0);
  assert.ok(getReconciledSource('composed_operation').length>0);
  assert.equal(getReconciledSourceCapsule().capsule_sha256,${JSON.stringify(RECONCILED_SOURCE_CAPSULE_SHA256)});
  assert.ok(getReconciledSource('operation_action').length>0);
  assert.ok(getReconciledSource('python').includes('python.validated-extensible-entity-factory/v1'));
  assert.ok(getReconciledSource('reference_factory').length>0);
  assert.ok(getReconciledSource('python_project').includes('domainspec.python-project-planning-contract'));
 assert.ok(getReconciledSource('python_cli').includes('domainspec.python-cli-integration-contract'));
 assert.ok(getReconciledSource('python_complete_verification').includes('domainspec.python-complete-verification-contract'));
  assert.ok(getReconciledSource('python_verification').includes('domainspec.python-verification-projection-contract'));
  assert.ok(getReconciledSource('python_native_observer').includes('native binding inventory'));
  assert.ok(getReconciledSource('rust_project').includes('domainspec.reconciled-rust-compilation'));
  assert.ok(getReconciledSource('rust_factory').includes('identity-only Entity Eq/Hash'));
  assert.ok(getReconciledSource('rust_calculation').includes('checked operations'));
  assert.ok(getReconciledSource('rust_query').includes('asynchronous trait'));
  assert.ok(getReconciledSource('rust_mapping').includes('does not construct an Entity'));
  assert.ok(getReconciledSource('rust_policy').includes('without importing or executing the target'));
  assert.ok(getReconciledSource('rust_event').includes('rust-event-generation-contract'));
  assert.ok(getReconciledSource('rust_operation').includes('one atomic state-and-outbox commit'));
  assert.ok(getReconciledSource('rust_state_machine').includes('pure native Rust reducer'));
  assert.ok(getReconciledSource('rust_workflow').includes('forward Workflow orchestrator'));
  assert.ok(getReconciledSource('rust_interface').includes('asynchronous provider trait'));
  assert.ok(getReconciledSource('rust_native_verification').includes('Cargo check offline'));
  assert.ok(getReconciledSource('realization_matrix').includes('exactly 39 explicit metatype-language cells'));
  console.log('relocated-capsule-pass');`;
 assert.equal(execFileSync(process.execPath,['--permission','--allow-fs-read='+root,'--input-type=module','--eval',check],{cwd:root,encoding:'utf8'}).trim(),'relocated-capsule-pass');
});
