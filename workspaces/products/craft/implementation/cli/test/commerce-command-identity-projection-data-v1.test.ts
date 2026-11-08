import test from 'node:test';
import assert from 'node:assert/strict';
import {checkCommerceCommandPrincipalDataV1,selectCommerceCheckedScopePathDataV1} from '../src/commerce/commerce-command-identity-projection-v1.js';

const code=(name:string)=>(error:any)=>error?.code===name;

test('data-only nested selectors and principal kinds fail closed',()=>{
 const scope=Object.freeze(Object.assign(Object.create(null),{
  command:Object.freeze(Object.assign(Object.create(null),{commandId:'stock-1',requestFingerprint:'a'.repeat(64)})),
  confirmed:Object.freeze(Object.assign(Object.create(null),{metadata:Object.freeze(Object.assign(Object.create(null),{eventId:'evt_'+ 'b'.repeat(64)}))})),
 }));
 assert.equal(selectCommerceCheckedScopePathDataV1(scope,'command.commandId'),'stock-1');
 assert.equal(selectCommerceCheckedScopePathDataV1(scope,'command.requestFingerprint'),'a'.repeat(64));
 assert.equal(selectCommerceCheckedScopePathDataV1(scope,'confirmed.metadata.eventId'),'evt_'+ 'b'.repeat(64));
 assert.throws(()=>selectCommerceCheckedScopePathDataV1(scope,'command.missing'),code('InputType'));
 assert.throws(()=>selectCommerceCheckedScopePathDataV1(scope,'command..commandId'),code('InputType'));
 assert.throws(()=>selectCommerceCheckedScopePathDataV1({get command(){throw Error('getter ran');}},'command.commandId'),code('InputType'));
 assert.throws(()=>selectCommerceCheckedScopePathDataV1(new Proxy(scope,{}),'command.commandId'),code('InputType'));
 assert.equal(checkCommerceCommandPrincipalDataV1('selected-service',{kind:'service',id:'orders'}),'orders');
 assert.equal(checkCommerceCommandPrincipalDataV1('authenticated-principal',{kind:'customer',id:'customer-1'}),'customer-1');
 assert.throws(()=>checkCommerceCommandPrincipalDataV1('selected-service',{kind:'customer',id:'customer-1'}),code('ForeignPrincipal'));
 assert.throws(()=>checkCommerceCommandPrincipalDataV1('authenticated-principal',{kind:'service',id:'orders'}),code('ForeignPrincipal'));
 assert.throws(()=>checkCommerceCommandPrincipalDataV1('authenticated-principal',{kind:'customer',get id(){throw Error('getter ran');}}),code('ForeignPrincipal'));
});
