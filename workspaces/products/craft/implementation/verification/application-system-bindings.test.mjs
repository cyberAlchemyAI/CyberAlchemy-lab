/** Focused finite original-owner join validation; full generated execution is
 * connected-applications-recovery.test.mjs. Open Questions: connected design. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {APPLICATION_SYSTEM_BINDINGS,validateApplicationSystemJoin,assertApplicationSystemSlotFree,selectApplicationSystemBinding} from '../profiles/ai/native/application/application-system-bindings.mjs';
const preference=APPLICATION_SYSTEM_BINDINGS.find(row=>row.slot==='query');
test('grouped preference join accepts genuine Maps and detaches trusted static inputs',()=>{
 const rows=[{contactId:'8'}],inputs=new Map([['preferences-1',rows]]),checked=validateApplicationSystemJoin({inputs,workerSubject:'alice'},preference);
 assert.equal(checked.inputs.get('preferences-1')[0].contactId,'8');rows[0].contactId='9';inputs.clear();assert.equal(checked.inputs.get('preferences-1')[0].contactId,'8');assert.ok(Object.isFrozen(checked.inputs.get('preferences-1')[0]));
});
test('grouped preference join rejects ambiguous or invalid input containers without invoking getters',()=>{
 let invoked=false;const withGetter={get inputs(){invoked=true;throw Error('untrusted getter');}};
 for(const value of [withGetter,{inputs:new Proxy(new Map(),{})},{inputs:new Map([['x',[{contactId:'-1'}]]])},{inputs:new Map([['x',[{contactId:'8',email:'injected'}]]])},{inputs:new Map(),extra:true}])assert.throws(()=>validateApplicationSystemJoin(value,preference),{code:'InvalidContract'});
 assert.equal(invoked,false);
});
test('join sizes and required producer run IDs are bounded independently',()=>{
 assert.throws(()=>validateApplicationSystemJoin({inputs:new Map([['x',Array.from({length:17},()=>({contactId:'8'}))]])},preference),{code:'ResourceLimit'});
 assert.throws(()=>validateApplicationSystemJoin({run:{id:'1',run:'18446744073709551616'}},APPLICATION_SYSTEM_BINDINGS[1]),{code:'InvalidContract'});
 const checked=validateApplicationSystemJoin({run:{id:'1',run:'201'},publicSubject:'alice'},APPLICATION_SYSTEM_BINDINGS[1]);assert.deepEqual({...checked.run},{id:'1',run:'201'});
});
test('finite joins require exact family, port, effect and codec; manual resources cannot shadow generated joins',()=>{
 const binding=APPLICATION_SYSTEM_BINDINGS[1],children=new Map([['support',{family:binding.consumer}],['rag',{family:binding.producer}]]),edge={...binding,source:'support',target:'rag'};
 assert.equal(selectApplicationSystemBinding(edge,children),binding);for(const delta of [{effect:'write'},{input_codec:'anything'},{targetPort:'unknown'}])assert.throws(()=>selectApplicationSystemBinding({...edge,...delta},children),{code:'UnsupportedCapability'});
 assert.throws(()=>assertApplicationSystemSlotFree({rag:{}},binding),{code:'InvalidContract'});assert.throws(()=>assertApplicationSystemSlotFree({query:{}},preference),{code:'InvalidContract'});
});
