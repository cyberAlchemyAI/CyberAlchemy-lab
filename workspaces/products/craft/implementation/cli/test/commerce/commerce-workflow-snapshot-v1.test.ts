import test from 'node:test';
import assert from 'node:assert/strict';
import {
 assertCommerceWorkflowSnapshotOwnerV1,createCommerceWorkflowSnapshotOwnerV1,
 CommerceWorkflowSnapshotErrorV1,type CommerceWorkflowSnapshotOwnerV1,
} from '../../src/commerce/commerce-workflow-snapshot-v1.js';

test('worker snapshot custody cannot be reconstructed from a matching object',()=>{
 const copied=Object.freeze({
  read(){return {kind:'rejected',code:'resource-not-found',authority_effect:'none'};},
  inspect(){return null;},recheck(){return null;},assertCurrent(){},dispose(){},
 }) as unknown as CommerceWorkflowSnapshotOwnerV1;
 assert.throws(()=>assertCommerceWorkflowSnapshotOwnerV1(copied),
  (error:unknown)=>error instanceof CommerceWorkflowSnapshotErrorV1&&error.code==='ForeignOwner');
});

test('a shaped Workflow binding cannot construct a worker snapshot owner',()=>{
 const forged=Object.freeze({inspect(){throw Error('must not inspect fake binding');},assertCurrent(){}});
 assert.throws(()=>createCommerceWorkflowSnapshotOwnerV1(forged as never,null as never,null as never,
  null as never,null as never,null as never,null as never),
  (error:unknown)=>Boolean(error&&typeof error==='object'&&
   (error as {diagnostics?:readonly {code:string}[]}).diagnostics?.[0]?.code==='ForeignOwner'));
});
