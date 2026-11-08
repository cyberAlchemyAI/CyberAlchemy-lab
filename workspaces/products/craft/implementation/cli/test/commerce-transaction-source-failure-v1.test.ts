import test from 'node:test';
import assert from 'node:assert/strict';
import {commerceTransactionFailureActionsV1,commerceTransactionFailureAtV1} from '../src/commerce/commerce-transaction-source-failure-v1.js';
import type {TransactionPlanV1} from '../src/commerce/commerce-data-v1.js';

test('native source failure must identify the exact original transaction action and path',()=>{
 const guard={kind:'reject',code:'invalid-checkout'} as const;
 const error={kind:'fail',code:'calculation-failed'} as const;
 const plan={body:[
  {kind:'guard',on_false:guard},
  {kind:'for',body:[{kind:'let',on_error:error}]},
 ]} as unknown as TransactionPlanV1;
 const path='$.body[4].transaction';
 const found=commerceTransactionFailureActionsV1(path,plan);
 assert.deepEqual(found.map(row=>row.action_path),[
  path+'.body[0].on_false',
  path+'.body[1].body[0].on_error',
 ]);
 assert.deepEqual(commerceTransactionFailureAtV1(path,plan,path+'.body[0]',guard),found[0]);
 assert.equal(commerceTransactionFailureAtV1(path,plan,path+'.body[0].condition',guard),null);
 assert.deepEqual(commerceTransactionFailureAtV1(path,plan,path+'.body[1].body[0].value.expression',error),found[1]);
 assert.equal(commerceTransactionFailureAtV1(path,plan,path+'.body[1].body[0].value.expression',guard),null);
 assert.equal(commerceTransactionFailureAtV1(path,plan,'$.body[5].transaction.body[0]',guard),null);
});
