import assert from 'node:assert/strict';
import test from 'node:test';
import {stripTypeScriptTypes} from 'node:module';
import {renderConfiguredEvent, type EventSource} from '../../src/generation/configured-event-source.js';

test('generated Event UInt64 references enforce both bounds before any clock effect', async () => {
  const source: EventSource = {description:'Bounded unsigned reference',event_type:'order-submitted',version:'1',
    occurrence_id:{field_id:'id',type_ref:{kind:'primitive',name:'string'},required:true},occurred_at_policy:'generated',
    payload:[{field_id:'order',type_ref:{kind:'reference',selector:'commerce:order'},required:true}]};
  const rendered=renderConfiguredEvent(source,new Map([['commerce:order',{selector:'commerce:order',projection:['id'],ontology_property:'ORDER#id',scalar:'UInt64'}]]));
  const javascript=stripTypeScriptTypes(rendered);
  const {make}=await import('data:text/javascript;base64,'+Buffer.from(javascript).toString('base64'));
  let calls=0;
  const clock=()=>{calls++;return 'explicit-time';};
  const input=(value:unknown)=>({occurrence:{id:'event-1'},payload:{order:value}});
  for(const value of [-1n,-1,'-1',18446744073709551616n,'18446744073709551616',NaN,Infinity,1.5,'1.5',{},null]) {
    assert.throws(()=>make(input(value),clock),/EVENT_INPUT/,String(value));
  }
  assert.equal(calls,0,'rejection cannot trigger a generated-clock call');
  for(const value of [0n,0,'0',18446744073709551615n,'18446744073709551615']) {
    const event=make(input(value),clock);assert.equal(event.payload.order,BigInt(value));assert.ok(Object.isFrozen(event.payload));
  }
  assert.equal(calls,5);
});
