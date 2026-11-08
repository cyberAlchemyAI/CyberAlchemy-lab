import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {deriveGenericEventOccurrence} from '../../src/generic/event-occurrence.js';

const profile=JSON.parse(readFileSync(fileURLToPath(new URL('../../../../../../../implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C12/event-handoff-contract-003/PROFILE-SELECTION.json',import.meta.url)),'utf8')) as {conformance_vectors:Array<{tuple:[string,string,string,string,string];expected_sha256:string}>};

test('C12 occurrence identity matches the frozen cross-domain and source-order vectors',()=>{
 for(const vector of profile.conformance_vectors){const [producer,causal,selector,version,ordinal]=vector.tuple;
  assert.equal(deriveGenericEventOccurrence({producer_namespace:producer,causal_command_tuple_sha256:causal,event_selector:selector,event_version:Number(version),emission_ordinal:Number(ordinal)}),vector.expected_sha256);
 }
 assert.equal(new Set(profile.conformance_vectors.map(v=>v.expected_sha256)).size,profile.conformance_vectors.length);
});

test('C12 occurrence identity refuses caller-style IDs and malformed causal material',()=>{
 const base={producer_namespace:'RequestService',causal_command_tuple_sha256:'a'.repeat(64),event_selector:'RequestService.RequestApproved',event_version:1,emission_ordinal:0};
 assert.throws(()=>deriveGenericEventOccurrence({...base,causal_command_tuple_sha256:'R-001'}));
 assert.throws(()=>deriveGenericEventOccurrence({...base,causal_command_tuple_sha256:'A'.repeat(64)}));
 assert.throws(()=>deriveGenericEventOccurrence({...base,event_selector:'PermitService'}));
 assert.throws(()=>deriveGenericEventOccurrence({...base,event_version:2}));
 assert.throws(()=>deriveGenericEventOccurrence({...base,emission_ordinal:-1}));
});
