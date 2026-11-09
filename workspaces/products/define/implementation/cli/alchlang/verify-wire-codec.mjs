import {exampleData} from './runtime/example.mjs';
import assert from 'node:assert/strict';
import {writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {generate,root,node,fingerprint} from './package-construction-build.mjs';
import {evaluateArtifact} from '../../../../../../implementation/artifact-runtime/pure-operation.mjs';
if(process.execPath!==node){const child=spawnSync(node,[import.meta.filename],{stdio:'inherit'});process.exit(child.status??1);}
const R=path.resolve(root,'../../../../../..'),checks=[];
async function codec(name){const a=generate(name),r=await evaluateArtifact(a.output,a.member,{marker:true});assert.equal(r.ok,true,JSON.stringify(r));return JSON.parse(new TextDecoder().decode(r.wire));}
const exported=await codec('ExportWireCodec'),imported=await codec('ImportWireCodec');
function port(value,plan,allowed=true){const p=spawnSync('python3',['-B',path.join(R,'implementation/artifact-runtime/json-port.py')],{input:JSON.stringify({operation:'represent-json',value,plan}),encoding:'utf8',maxBuffer:4*1024*1024});if(allowed){assert.equal(p.status,0,p.stdout||p.stderr);return JSON.parse(p.stdout).result.value;}assert.notEqual(p.status,0);return JSON.parse(p.stdout);}
const request=(await exampleData()).request;
const native=port(request,imported),roundtrip=port(native,exported);assert.deepEqual(roundtrip,request);checks.push('actual-current-User-Journey-roundtrip');
const opaque={revision:7,bytes:12,identity:'opaque-value',value_schema:{revision:9},nested:{bindings:{revision:13}}};
const sample={...structuredClone(request),applications:[]};
const carrier={bindings:opaque,value_schema:{type:'object',enum:[opaque]},revision:3};
const encoded=port(carrier,imported);assert.equal(encoded.revision,'3');assert.equal(typeof encoded.bindings,'string');const decoded=port(encoded,exported);assert.deepEqual(decoded,carrier);checks.push('opaque-task-values-and-schema-literals-preserved');
for(const reference of [{kind:'external',input_id:'source',identity:'meaning:one',revision:'17',carrier_ref:'carrier',selector:'',sha256:'a'.repeat(64)},{kind:'embedded',pack_id:'p',pack_revision:1,entry_kind:'working-meaning',entry_id:'m',revision:2,selector:'/working_meanings/0',sha256:'b'.repeat(64)}]){
 assert.deepEqual(port(port(reference,imported),exported),reference);checks.push('exact-'+reference.kind+'-reference-representation');
}
const h={concept_id:'concept:reuse',disposition:'reuse',payload:{meaning_ref:{kind:'external',input_id:'source',identity:'meaning:one',revision:'17',carrier_ref:'carrier',selector:'',sha256:'a'.repeat(64)},applicability:'Candidate'}};
const hn=port(h,imported);assert.equal(hn.fields.value.meaning_ref.kind,'external');assert.equal(hn.fields.value.meaning_ref.tag,undefined);assert.deepEqual(port(hn,exported),h);checks.push('Reuse-keeps-concrete-reference-carrier');
const bad={...request,identity_ref:'collision',identity:'other'};port(bad,imported,false);checks.push('field-alias-collision-refused');
const remote={rules:[{schema:JSON.stringify({$ref:'https://invalid.example/schema'}),actions:[]}],opaque_fields:[]};port({},remote,false);checks.push('external-schema-resolution-refused');
const report={schema_version:'define-wire-codec-verification/v1',status:'PASS',source:fingerprint(),checks,check_count:checks.length,legacy_engine_use:'native real-Definition example; no Define engine',full_cli_cutover:false};writeFileSync(path.join(root,'.local/WIRE-CODEC-VERIFICATION.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));