import test from 'node:test';
import assert from 'node:assert/strict';
import {deriveGenericCausalIdentityData,sameGenericCausalIdentityData} from '../../src/generic/external-write-identity.ts';

const limits={schema_version:'craft.generic-causal-identity-limits/v1-candidate',max_child_depth:4,max_local_call_frames:4,max_site_occurrences:32,max_total_occurrences:128,max_tuple_bytes:8192,wrapper_depth:0};
const root={schema_version:'craft.generic-root-command/v1-candidate',application_namespace:'ReviewDesk',service:'ReviewDeskService',principal:{kind:'customer',subject:'reviewer-1',tenant:null},root_entry:'ReviewDesk.ApproveEntry',client_key:'approval-17'};
const effect=(ordinal=0)=>({schema_version:'craft.generic-external-effect/v1-candidate',parent:root,site:{operation:'ReviewDesk.ApproveRequest',binding:'capture'},local_calls:[],interface_ref:'CaptureApi',contract_operation_ref:'Capture',ordinal});

test('external effect identity is stable for the same causal tuple and changes with source-order occurrence',()=>{
  const first=deriveGenericCausalIdentityData(effect(),limits);
  const replay=deriveGenericCausalIdentityData(structuredClone(effect()),limits);
  const next=deriveGenericCausalIdentityData(effect(1),limits);
  assert.equal(first.canonical_json,replay.canonical_json);
  assert.equal(first.sha256,replay.sha256);
  assert.equal(sameGenericCausalIdentityData(effect(),structuredClone(effect()),limits),true);
  assert.notEqual(first.sha256,next.sha256);
  assert.equal(sameGenericCausalIdentityData(effect(),effect(1),limits),false);
});

test('external effect identity rejects a cyclic or forged causal parent before hashing',()=>{
  const cycle=effect();cycle.parent=cycle;
  assert.throws(()=>deriveGenericCausalIdentityData(cycle,limits),/cyclic causal parent/);
  assert.throws(()=>deriveGenericCausalIdentityData({...effect(),parent:{...root,client_key:''}},limits),/bounded Unicode scalar count/);
});
