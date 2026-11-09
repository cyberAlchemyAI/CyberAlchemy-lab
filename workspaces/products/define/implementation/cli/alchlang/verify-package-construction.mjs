import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,mkdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {generate,root,node,fingerprint} from './package-construction-build.mjs';
import {evaluateArtifact} from '../../../../../../implementation/artifact-runtime/pure-operation.mjs';
if(process.execPath!==node){const child=spawnSync(node,[import.meta.filename],{stdio:'inherit'});process.exit(child.status??1);}
const R=path.resolve(root,'../../../../../..');const hash=raw=>createHash('sha256').update(raw).digest('hex');
const dir=mkdtempSync(path.join(root,'.local/package-construction-'));
const pack={pack_id:'pack:construction-proof',revision:1,claim_ceiling:'Candidate preparation only.'};
const packRaw=Buffer.from(JSON.stringify(pack)+'\n');writeFileSync(path.join(dir,'pack.json'),packRaw);
const rows=[['capture.json',Buffer.from('{}\n')],['inputs/value.txt',Buffer.from('exact evidence\n')],['pack.json',packRaw],['report.json',Buffer.from('{}\n')]];
async function mapping(name,value){const artifact=generate(name),result=await evaluateArtifact(artifact.output,artifact.member,{value});assert.equal(result.ok,true,JSON.stringify(result));return JSON.parse(new TextDecoder().decode(result.wire));}
const steps=[await mapping('ManifestHeader',{pack_ordinal:'2',pack_sha256:hash(packRaw),pack_bytes:String(packRaw.length)})];
for(let ordinal=0;ordinal<rows.length;ordinal++){const [name,raw]=rows[ordinal];steps.push(await mapping('ManifestMember',{ordinal:String(ordinal),path:name,extension:path.extname(name).slice(1),sha256:hash(raw),bytes:String(raw.length)}));}
const request={operation:'construct-json',root:dir,sources:[{id:'pack',binding:{path:'pack.json',sha256:hash(packRaw),bytes:packRaw.length,digest_kind:'original-file-sha256'}}],batches:steps};
const encoded=spawnSync('python3',['-B',path.join(R,'implementation/artifact-runtime/json-port.py')],{input:JSON.stringify(request),encoding:'utf8'});assert.equal(encoded.status,0,encoded.stdout||encoded.stderr);const result=JSON.parse(encoded.stdout).result;
assert.deepEqual(result.value,JSON.parse(readFileSync(path.join(root,'tests/fixtures/expected-manifest.json'))));
const report={schema_version:'define-package-construction-verification/v1',status:'PASS',source:fingerprint(),checks:['generated-manifest-header','generated-member-roles-and-media','generic-original-byte-copy','exact-legacy-manifest-equivalence'],check_count:4,define_engine_used_as:'retained exact compatibility fixture; no Define engine',full_cli_cutover:false};
writeFileSync(path.join(root,'.local/PACKAGE-CONSTRUCTION-VERIFICATION.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));