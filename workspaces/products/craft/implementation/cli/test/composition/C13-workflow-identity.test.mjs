/** Durable identity must survive recapture without ignoring any semantic input.
 * Open questions: docs/GENERIC-APPLICATIONS.md#open-questions.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {workflowPersistentContract,workflowCompatibilitySha256} from '../../dist/generic/workflow-worker.js';
import {dataDigest} from '../../dist/profile-engine/contracts.js';
const hash=text=>dataDigest(text);
const source={schema_version:'craft.generic-workflow-source/v1-candidate',
 workflow:'Demo.Flow',service:'DemoService',source_site:'demo.alch:1:2',
 source_capture_sha256:hash('physical-original'),source_closure_sha256:hash('complete-file-inventory'),
 profile_sha256:hash('profile'),base_application_sha256:hash('application'),
 parameters:[{name:'id',type:{kind:'scalar',name:'UInt64'}}],correlation:'id',
 durable_state:'Demo.State',start_entry:'Demo.Begin',start_entry_contract_sha256:hash('start'),
 start_parameters:[{name:'id',type:{kind:'scalar',name:'UInt64'}}],
 steps:[{name:'commit',kind:'provider-command',entry:'Demo.Commit',entry_contract_sha256:hash('entry'),
  source_site:'demo.alch:3:4',provider_write_bindings:['Demo.Provider'],
  on_unknown:'resume-original-command',on_definite_failure:'compensate',
  provider_failure_compensation_precondition:'proven-no-provider-effect'}],
 compensation_order:[],recovery:'needed-compensations-only/reverse-completion-v1',authority_effect:'none'};
test('C13 same checked closure and semantics retain durable identity across physical recapture',()=>{
 const recaptured={...source,source_capture_sha256:hash('different-directory-and-inodes')};
 assert.notDeepEqual(source,recaptured);
 assert.deepEqual(workflowPersistentContract(source),workflowPersistentContract(recaptured));
 assert.equal(workflowCompatibilitySha256(source),workflowCompatibilitySha256(recaptured));
});
test('C13 every durable semantic field and the complete file closure still bind compatibility',()=>{
 const baseline=workflowCompatibilitySha256(source);
 for(const change of [
  {source_closure_sha256:hash('changed-file')},{profile_sha256:hash('changed-profile')},
  {base_application_sha256:hash('changed-application')},{start_entry:'Demo.Other'},
  {start_entry_contract_sha256:hash('changed-start')},{source_site:'demo.alch:2:3'},
  {parameters:[]},{correlation:'other'},{durable_state:'Demo.OtherState'},
  {steps:[{...source.steps[0],entry_contract_sha256:hash('changed-entry')}]},
  {steps:[{...source.steps[0],provider_write_bindings:['Demo.OtherProvider']}]},
  {compensation_order:['commit']},{recovery:'different-recovery'}
 ])assert.notEqual(workflowCompatibilitySha256({...source,...change}),baseline,JSON.stringify(change));
 assert.throws(()=>workflowPersistentContract({...source,source_closure_sha256:undefined}),/SOURCE_CLOSURE/);
});
