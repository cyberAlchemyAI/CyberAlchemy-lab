import test,{before,after} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {buildCustody,loadCustody} from '../../../implementation/dist/custody-builder.js';
const source=fileURLToPath(new URL('../request-custody.alch',import.meta.url));
const directory=mkdtempSync(join(tmpdir(),'custody-build-'));let built;
before(async()=>{built=await buildCustody(source,join(directory,'bundle'));});
after(()=>rmSync(directory,{recursive:true,force:true}));
test('standalone custody bundle binds every file and invokes compiled decision policy',async()=>{
 for(const [file,sha]of Object.entries(built.manifest.files))assert.equal(createHash('sha256').update(readFileSync(join(built.output,file))).digest('hex'),sha,file);
 const generated=await import(pathToFileURL(join(built.output,built.manifest.entry)).href);
 assert.equal(generated.contract.identity.defaults.max_output_tokens,256);
 assert.equal((await generated.policy({exists:true,matches:true,pending:false,stream:false,succeeded:true},{},{localOnly:true})).status,'replay');
 await assert.rejects(buildCustody(source,built.output),/output exists/);
});
test('authored identity defaults lower into contract; invalid lifecycle fails at build boundary',async()=>{
 const changed=source.replace('request-custody.alch','.custody-test-'+process.pid+'.alch');
 try{writeFileSync(changed,readFileSync(source,'utf8').replace('"max_output_tokens":256','"max_output_tokens":128'));assert.equal((await loadCustody(changed)).compiled.contract.identity.defaults.max_output_tokens,128);
 for(const [from,to]of [['"attempts":1','"attempts":2'],['"exclude":["request_id"]','"exclude":["request_id","routing_strategy"]'],['target node-http','target rust'],['"./idempotency-policy.alch"','"../idempotency-policy.alch"']]){writeFileSync(changed,readFileSync(source,'utf8').replace(from,to));await assert.rejects(loadCustody(changed));}
 }finally{rmSync(changed,{force:true});}
});
test('generated factory rejects raised limits and missing memory binding',async()=>{
 const {createCustody}=await import(pathToFileURL(join(built.output,built.manifest.entry)).href);
 assert.throws(()=>createCustody({maxEntries:129}),/INVALID_LIMITS/);
 assert.throws(()=>createCustody({dispatch:async()=>{}}),/CUSTODY_BINDING_REQUIRED/);
});
