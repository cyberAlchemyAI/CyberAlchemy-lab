import test from 'node:test';
import assert from 'node:assert/strict';
import {validateTechnicalTopologyRoot} from '../../src/profile-engine/technical-profile-topology.ts';

test('finite topology consumers admit only their selected root vocabulary',()=>{
 for(const [consumer,value]of [
  ['craft.profile-engine/v1',{nodes:[],edges:[],requestBytes:'1024'}],
  ['craft.technical-profile-composition/v1',{nodes:[],edges:[]}],
  ['craft.technical-profile-runtime/v1',{nodes:[],edges:[]}],
  ['craft.technical-profile-runtime/v1',{nodes:[],edges:[],providerStages:[]}],
 ] as const){const result=validateTechnicalTopologyRoot(consumer,value);assert.equal(result.status,'closed-finite-consumer');assert.deepEqual(JSON.parse(JSON.stringify(result.topology)),value);assert.ok(Object.isFrozen(result.topology));}
});
test('unknown root slots reject instead of surviving as ignored provenance',()=>{
 for(const [consumer,value]of [
  ['craft.profile-engine/v1',{nodes:[],edges:[],requestBytes:'1024',unsupportedConsumerSlot:true}],
  ['craft.technical-profile-composition/v1',{nodes:[],edges:[],runtimePolicy:'IgnoreMe'}],
  ['craft.technical-profile-runtime/v1',{nodes:[],edges:[],tlsRequired:true}],
  ['craft.profile-engine/v1',{nodes:[],edges:[],requestBytes:'1024',providerStages:[]}],
  ['craft.technical-profile-composition/v1',{nodes:[],edges:[],providerStages:[]}],
  ['craft.technical-profile-runtime/v1',{nodes:[],edges:[],requestBytes:'1024'}],
 ] as const)assert.throws(()=>validateTechnicalTopologyRoot(consumer,value),/unknown topology root slot/);
});
test('selected required roots reject missing fields and malformed containers',()=>{
 for(const value of [null,[],{}, {nodes:[]},{nodes:{},edges:[]},{nodes:[],edges:{}}])assert.throws(()=>validateTechnicalTopologyRoot('craft.technical-profile-composition/v1',value));
 assert.throws(()=>validateTechnicalTopologyRoot('craft.profile-engine/v1',{nodes:[],edges:[]}),/missing topology root slot/);
});
test('unresolved consumers retain inert inspection and never gain finite admission',()=>{
 for(const consumer of [null,'craft.future-consumer/v1','toString','__proto__']){
  const result=validateTechnicalTopologyRoot(consumer,{unknownSlot:true});assert.equal(result.status,'unverified-consumer');assert.equal((result.topology as any).unknownSlot,true);
 }
});
test('root capture rejects executable/accessor data without invoking it',()=>{
 let invoked=false;const value={nodes:[],edges:[],get extra(){invoked=true;return true;}};
 assert.throws(()=>validateTechnicalTopologyRoot('craft.technical-profile-composition/v1',value),/inert enumerable/);assert.equal(invoked,false);
 assert.throws(()=>validateTechnicalTopologyRoot('craft.future-consumer/v1',{callback:()=>true}),/JSON value/);
});
