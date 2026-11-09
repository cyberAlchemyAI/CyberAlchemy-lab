import {observedPolicyFacts} from './test-value-observations.mjs';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,symlinkSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import path from 'node:path';
import assert from 'node:assert/strict';
import {generate,root,node,fingerprint} from './pack-engine-build.mjs';
import {evaluateArtifact} from '../../../../../../implementation/artifact-runtime/pure-operation.mjs';
if(process.execPath!==node){const child=spawnSync(node,[import.meta.filename],{stdio:'inherit'});process.exit(child.status??1);}
const R=path.resolve(root,'../../../../../..'),generic=path.join(R,'implementation/artifact-runtime/json-port.py');
const hash=raw=>createHash('sha256').update(raw).digest('hex');
const binding=file=>{const raw=readFileSync(path.join(R,file));return {path:file,bytes:raw.length,sha256:hash(raw),digest_kind:'original-file-sha256'};};
const checks=[];
function port(value,allowed=true){const run=spawnSync('python3',['-B',generic],{input:JSON.stringify(value),encoding:'utf8',maxBuffer:8*1024*1024});const result=JSON.parse(run.stdout);if(allowed)assert.equal(run.status,0,JSON.stringify(result));else assert.notEqual(run.status,0);return result;}
async function policy(name,value,expected='Returned'){
 value=observedPolicyFacts(name,value);
 const artifact=generate(name),result=await evaluateArtifact(artifact.output,artifact.member,{value});assert.equal(result.ok,true,JSON.stringify(result));const answer=JSON.parse(new TextDecoder().decode(result.wire));assert.equal(answer.tag,expected,JSON.stringify(answer));
}
const candidate='authority/definitions/candidates/0018-construction-chain';
const reuse=JSON.parse(readFileSync(path.join(R,candidate,'SOURCE-SELECTION.json'))).definitions.filter(row=>row.standing!=='admitted').map(row=>row.path);
const authored=JSON.parse(readFileSync(path.join(R,candidate,'INDEX.json'))).new_definitions.map(row=>candidate+'/'+row.path);
const schema=binding('authority/artifact-types/definition/v2/schema.json'),generator=binding('authority/artifact-types/definition/v2/generator.py');
let batches=0;
for(const file of [...reuse,...authored]){
 const original=binding(file),body=port({operation:'observe',root:R,binding:original}).result.value;
 assert.equal(port({operation:'schema-check',root:R,binding:original,schema_binding:schema}).result.valid,true);checks.push('actual-definition-schema:'+body.definition_id);
 const b={path:original.path,bytes:String(original.bytes),sha256:original.sha256,digest_kind:'original-file-sha256'};await policy('VerifyBinding',{selected:b,observed:b});checks.push('actual-binding:'+body.definition_id);
 const formal=body.voices.scientific_formal;
 await policy('VerifyMaterialization',{owner_route:body.semantic_owner_ref,selected_scope:body.scope.authority_scope_ref,actual_scope:body.scope.authority_scope_ref,selected_statement:formal.normative_statement,actual_statement:formal.normative_statement,selected_boundaries:body.boundaries,actual_boundaries:body.boundaries,selected_notation:formal.notation,actual_notation:formal.notation,selected_schema:schema.sha256,actual_schema:body.schema_digest,selected_generator:generator.sha256,actual_generator:body.source_direction.generator_sha256,successor:false,parent_identity:null,parent_revision:null,actual_identity:body.definition_id,actual_revision:body.version});checks.push('actual-materialization-policy:'+body.definition_id);
 const selectors=port({operation:'leaves',root:R,binding:original}).result.selectors;
 for(let offset=0;offset<selectors.length;offset+=100){
  const selected=selectors.slice(offset,offset+100),observed=port({operation:'observe-many',root:R,binding:original,selectors:selected}).result.observations;
  const rows=observed.map(row=>({target:row.selector,target_value_digest:row.canonical_value_sha256,source_value_digest:row.canonical_value_sha256}));
  await policy('VerifyLineageBatch',{expected_targets:selected,observations:rows});batches++;
  if(offset===0){const altered=structuredClone(rows);altered[0].source_value_digest='0'.repeat(64);await policy('VerifyLineageBatch',{expected_targets:selected,observations:altered},'Rejected');checks.push('negative:actual-field-mismatch:'+body.definition_id);}
 }
 checks.push('actual-complete-leaf-batches:'+body.definition_id);
}
port({operation:'decode',bytes_base64:Buffer.from('{"x":1,"x":2}').toString('base64')},false);checks.push('negative:duplicate-JSON-key');
port({operation:'decode',bytes_base64:Buffer.from('{"x":1.5}').toString('base64')},false);checks.push('negative:unsupported-number');
const directory=mkdtempSync(path.join(root,'.local/generic-port-')),destination=path.join(directory,'published'),payload=Buffer.from('{"value":1}\n');
const publish={operation:'publish',destination,members:[{path:'record.json',bytes_base64:payload.toString('base64')}]};port(publish);port(publish,false);assert.deepEqual(readFileSync(path.join(destination,'record.json')),payload);checks.push('atomic-publication-preserves-existing-destination');
const source=path.join(directory,'source');mkdirSync(source);writeFileSync(path.join(source,'value.json'),payload);symlinkSync(path.join(source,'value.json'),path.join(source,'link.json'));
port({operation:'observe',root:source,binding:{path:'link.json',sha256:hash(payload),bytes:payload.length,digest_kind:'original-file-sha256'}},false);checks.push('negative:symlink-source');
const report={schema_version:'define-alchlang-real-source-policy-verification/v1',status:'PASS',source:fingerprint(),definitions:5,lineage_batches:batches,checks,check_count:checks.length,negative_controls:checks.filter(x=>x.startsWith('negative:')).length,python_define_engine_imported:false,scope:'Generic source observations and generated AlchLang binding/materialization/lineage decisions only; complete CLI cutover is not inferred.'};
writeFileSync(path.join(root,'.local/pack-engine/REAL-SOURCE-VERIFICATION.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({status:'PASS',checks:checks.length,definitions:5,lineage_batches:batches}));