import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,mkdirSync,symlinkSync} from 'node:fs';
import path from 'node:path';
import {generate,root,node,fingerprint,selected} from './package-graph-build.mjs';
import {evaluateArtifact} from '../../../../../../implementation/artifact-runtime/pure-operation.mjs';
import {openJsonPort} from '../../../../../../implementation/artifact-runtime/json-pipe.mjs';
const R=path.resolve(root,'../../../../../..'),checks=[],directory=mkdtempSync(path.join(root,'.local/byte-custody-proof-'));
async function native(name,args){const artifact=generate(name),result=await evaluateArtifact(artifact.output,artifact.member,args);assert.equal(result.ok,true,JSON.stringify(result));const value=JSON.parse(new TextDecoder().decode(result.wire));if(artifact.member==='operation.mjs'){if(value.tag!=='Returned')throw Error(value.fields.code);return value.fields.value;}return value;}
const policy=await native('PrivacyProtocol',{marker:true}),port=openJsonPort(path.join(R,'implementation/artifact-runtime/json-port.py'));
try{
 for(const [label,raw,expected]of [
 ['ordinary-JSON',Buffer.from('{"value":1}\n'),null],['ordinary-text',Buffer.from('Text evidence.\n'),null],
 ['private-marker',Buffer.from('-----BEGIN PRIVATE KEY-----'),/private-material/],
 ['private-key-field',Buffer.from('{"nested":{"PRIVATE_KEY":"dummy-fixture"}}'),/private-material/],
 ['session-memory',Buffer.from('{"session_memory":{}}'),/private-material/],
 ['binary-data',Buffer.from([0,255]),/unsupported-member-encoding/],
 ['duplicate-keys',Buffer.from('{"value":1,"value":2}'),/duplicate-key/],
 ['unsupported-number',Buffer.from('{"value":0.5}'),/unsupported-number/]]){
  const stored=await port.request({operation:'store-bytes',bytes_base64:raw.toString('base64')});
  const value=await port.request({operation:'probe-bytes',ref:stored.ref,markers:policy.markers,keys:policy.keys});
  if(expected)await assert.rejects(()=>native('VerifyPrivacy',{value}),expected);else assert.equal(await native('VerifyPrivacy',{value}),true);
  checks.push(label);
 }
 const raw=Buffer.from('{ "exact": "source bytes" }\n');writeFileSync(path.join(directory,'source.json'),raw);
 const source=await port.request({operation:'read-file',root:directory,path:'source.json',maximum:policy.maximum_file_bytes});assert.equal(source.binding.bytes,raw.length);checks.push('anchored-original-byte-observation');
 const destination=path.join(directory,'published');await port.request({operation:'publish-refs',destination,members:[{path:'result.json',ref:source.ref}]});assert.deepEqual(readFileSync(path.join(destination,'result.json')),raw);checks.push('atomic-exact-byte-publication');
 await assert.rejects(()=>port.request({operation:'publish-refs',destination,members:[{path:'changed.json',ref:source.ref}]}));assert.deepEqual(readFileSync(path.join(destination,'result.json')),raw);checks.push('existing-destination-preserved');
 symlinkSync(path.join(directory,'source.json'),path.join(directory,'linked.json'));await assert.rejects(()=>port.request({operation:'read-file',root:directory,path:'linked.json',maximum:policy.maximum_file_bytes}));checks.push('symlink-read-refused');
 assert.equal(await native('VerifyDeclaredBudget',{value:{manifest_bytes:'1024',parts:[['1','2']]}}),true);await assert.rejects(()=>native('VerifyDeclaredBudget',{value:{manifest_bytes:'1024',parts:[['16777216']]}}),/package-budget/);checks.push('native-package-byte-budget');
 const report={schema_version:'define-byte-custody-privacy-verification/v1',status:'PASS',source:fingerprint(),checks,check_count:checks.length,python_define_engine_imported:false,scope:'Native privacy and budget policies plus generic original-byte I/O; full package workflow not inferred.'};writeFileSync(path.join(root,'.local/BYTE-CUSTODY-VERIFICATION.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}finally{await port.close();}