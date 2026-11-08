import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {buildRustFunction} from '../../implementation/dist/rust-function-builder.js';
import {checkFunction} from '../../implementation/dist/function-builder.js';
import {loadDomainSpecCompiler} from '../../implementation/dist/domainspec-cli.js';
import {digest} from '../../implementation/dist/domainspec-profile.js';
const here=import.meta.dirname,source=path.join(here,'quantity-price.alch'),out=path.join(here,'evidence/bundle');
assert.equal((await checkFunction(source)).status,'valid');
const build=await buildRustFunction(source,out),compiler=await loadDomainSpecCompiler();let stdout='',stderr='';
assert.equal(compiler.runCli(['verify',path.join(out,'domain/project'),'--language','rust','--target-root',path.join(out,'domain/generated')],{stdout(v){stdout+=v;},stderr(v){stderr+=v;}}),0,stderr);
const verification=JSON.parse(stdout);assert.equal(verification.result,'pass');
const fixtures=JSON.parse(fs.readFileSync(path.join(here,'../medusa-quantity-price-v1/fixtures.json'),'utf8')),cases=[];
for(const f of fixtures){const input=JSON.stringify({request:f.request,snapshot:f.snapshot}),result=JSON.parse(execFileSync(path.join(out,'alch-function'),['invoke'],{input,encoding:'utf8'}));for(const [key,value]of Object.entries(f.expected))assert.deepEqual(result[key],value,f.name);const raw=execFileSync(path.join(out,'alch-function'),['trace'],{input,encoding:'utf8',maxBuffer:8*1024*1024}),trace=JSON.parse(raw);assert.equal(trace.outcome.status,'succeeded');assert.deepEqual(trace.outcome.result,result);assert.equal(trace.capture.complete,true);if(f===fixtures[0])fs.writeFileSync(path.join(here,'evidence/quoted-trace.json'),raw,{flag:'wx'});cases.push({name:f.name,result:'pass',trace_result_parity:'pass'});}
const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json'),'utf8'));for(const [name,sha]of Object.entries(manifest.files))assert.equal(digest(fs.readFileSync(path.join(out,name))),sha,name);
assert.equal(Object.keys(manifest.files).filter(p=>p.endsWith('.js')||p.endsWith('.mjs')).length,0);
fs.writeFileSync(path.join(here,'evidence/product-test.json'),JSON.stringify({schema_version:'alchlang.rust-product-test/v1',build,verification,fixtures:cases,native_trace_parity:20,bundle_files_verified:Object.keys(manifest.files).length,binary_sha256:manifest.files['alch-function'],toolchain:manifest.toolchain,authority_effect:'none'},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:'pass',fixtures:cases.length,target:'rust-http',native_trace_parity:20}));
