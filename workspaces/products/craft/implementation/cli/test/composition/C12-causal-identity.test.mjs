import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {deriveGenericCausalIdentityData} from '../../src/generic/external-write-identity.ts';
import {canonicalJson} from '../../src/profile-engine/contracts.ts';

const limits={schema_version:'craft.generic-causal-identity-limits/v1-candidate',max_child_depth:4,max_local_call_frames:4,max_site_occurrences:32,max_total_occurrences:128,max_tuple_bytes:8192,wrapper_depth:0};
const root=(principal,version='craft.generic-root-command/v2-candidate')=>({schema_version:version,application_namespace:'ReviewDesk',service:'ReviewDeskService',principal,root_entry:'ReviewDesk.CommitEntry',client_key:'approval-17'});
const effect=(parent,version='craft.generic-external-effect/v2-candidate')=>({schema_version:version,parent,site:{operation:'ReviewDesk.CommitRequestApproval',binding:'capture'},local_calls:[],interface_ref:'ReviewDesk.Provider',contract_operation_ref:'ReviewDesk.Capture',ordinal:0});
const operator=()=>root({kind:'operator',subject:'operator-1',tenant:null});
const service=()=>root({kind:'service',service:'AuditService',subject:'relay-1',tenant:null});
const customer=()=>root({kind:'customer',subject:'customer-1',tenant:null},'craft.generic-root-command/v1-candidate');

test('V4 operator and service effects have exact distinct tagged causal commitments',()=>{
 for(const parent of [operator(),service()]){
  const tuple=effect(parent),derived=deriveGenericCausalIdentityData(tuple,limits),replay=deriveGenericCausalIdentityData(structuredClone(tuple),limits);
  assert.equal(derived.canonical_json,canonicalJson(tuple));
  assert.equal(derived.sha256,createHash('sha256').update(derived.canonical_json).digest('hex'));
  assert.equal(derived.sha256,replay.sha256);
 }
 assert.notEqual(deriveGenericCausalIdentityData(effect(operator()),limits).sha256,deriveGenericCausalIdentityData(effect(service()),limits).sha256);
});

test('V1 customer effect keeps its existing exact canonical bytes',()=>{
 const tuple=effect(customer(),'craft.generic-external-effect/v1-candidate'),derived=deriveGenericCausalIdentityData(tuple,limits);
 assert.equal(derived.canonical_json,canonicalJson(tuple));
 assert.equal(derived.sha256,createHash('sha256').update(canonicalJson(tuple)).digest('hex'));
 assert.equal(derived.sha256,'d9e1444ba99c46c456da8857e969bfa887d7247ca9282ce41d27a90a76475021');
});

test('cross-version roots, effects and principals are rejected',()=>{
 const invalid=[
  effect(operator(),'craft.generic-external-effect/v1-candidate'),
  effect(customer()),
  effect(root({kind:'operator',subject:'operator-1',tenant:null},'craft.generic-root-command/v1-candidate'),'craft.generic-external-effect/v1-candidate'),
  effect(root({kind:'service',service:'AuditService',subject:'relay-1',tenant:null},'craft.generic-root-command/v1-candidate'),'craft.generic-external-effect/v1-candidate'),
  effect(root({kind:'customer',subject:'customer-1',tenant:null})),
  effect({...operator(),principal:{kind:'operator',service:'ReviewDeskService',subject:'operator-1',tenant:null}}),
  effect({...service(),principal:{kind:'service',subject:'relay-1',tenant:null}}),
  effect({...service(),principal:{kind:'service',service:'AuditService',subject:'relay-1',tenant:'tenant-1'}}),
  effect({schema_version:'craft.generic-child-command/v1-candidate',parent:operator(),site:{operation:'ReviewDesk.CommitRequestApproval',binding:'child'},local_calls:[],target_service:'ReviewDeskService',target_entry:'ReviewDesk.CommitEntry',ordinal:0}),
 ];
 for(const tuple of invalid)assert.throws(()=>deriveGenericCausalIdentityData(tuple,limits),undefined,JSON.stringify(tuple));
});
