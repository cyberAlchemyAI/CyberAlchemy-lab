import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {sha,verifyFiles,verifyProduct} from './package.mjs';
// Product identity tests; Open Questions: OPERATOR.md.
test('workspace reference kit matches its exact candidate manifest',()=>{assert.ok(verifyProduct().files>865);});
test('changed or missing product input fails closed',()=>{const dir=mkdtempSync(join(tmpdir(),'product-identity-'));try{writeFileSync(join(dir,'input'),'original');const m={schema_version:'alch.inference-reference-product/v1-candidate',files:{input:sha('original')}};assert.equal(verifyFiles(dir,m),1);writeFileSync(join(dir,'input'),'changed');assert.throws(()=>verifyFiles(dir,m),/PRODUCT_SOURCE_DRIFT/);rmSync(join(dir,'input'));assert.throws(()=>verifyFiles(dir,m));}finally{rmSync(dir,{recursive:true,force:true});}});
test('empty or malformed manifests cannot claim verification',()=>{for(const m of [{},{schema_version:'alch.inference-reference-product/v1-candidate',files:{}},{schema_version:'alch.inference-reference-product/v1-candidate',files:{x:'invalid'}}])assert.throws(()=>verifyFiles('.',m));});
