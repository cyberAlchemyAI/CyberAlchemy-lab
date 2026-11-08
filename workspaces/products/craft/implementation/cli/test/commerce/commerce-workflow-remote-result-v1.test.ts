import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync} from 'node:fs';
import path from 'node:path';
import {tmpdir} from 'node:os';
import {randomUUID} from 'node:crypto';
import {assertCommerceWorkflowRemoteResultOwnerV1,createCommerceWorkflowRemoteResultOwnerV1,
 CommerceWorkflowRemoteResultErrorV1} from '../../src/commerce/commerce-workflow-remote-result-v1.js';

const foreign=(error:unknown)=>error instanceof CommerceWorkflowRemoteResultErrorV1&&error.code==='ForeignOwner';

test('a result-shaped object cannot impersonate an original executed Workflow result owner',()=>{
 const fabricated={execute:async()=>({kind:'returned',handle:{kind:'original-protected-workflow-remote-result/v1-candidate'}}),
  inspect:()=>({result_kind:'returned'}),select:()=>({outcome:'selected'}),assertCurrent:()=>{},dispose:()=>{}};
 assert.throws(()=>assertCommerceWorkflowRemoteResultOwnerV1(fabricated as never),foreign);
});

test('a forged protected call is rejected before generating or executing target code',async()=>{
 const directory=path.join(tmpdir(),'commerce-workflow-remote-result-'+randomUUID());
 const fabricated={inspect:()=>({phase:'Dispatched'}),recheck:()=>({phase:'Dispatched'}),claimOriginalCall:()=>({phase:'Dispatched'})};
 await assert.rejects(createCommerceWorkflowRemoteResultOwnerV1(
  null as never,null as never,null as never,null as never,null as never,null as never,
  null as never,null as never,null as never,null as never,directory,fabricated as never,
  null as never,null as never,null as never,null as never,null as never),
  (error:unknown)=>Boolean(error&&typeof error==='object'&&'code'in error&&error.code==='ForeignOwner'));
 assert.equal(existsSync(directory),false);
});
