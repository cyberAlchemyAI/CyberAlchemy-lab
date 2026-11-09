import assert from 'node:assert/strict';
import path from 'node:path';
import {writeFileSync} from 'node:fs';
import {root,fingerprint} from './pack-reference-protocol-build.mjs';
import {callNative as call} from './runtime/native.mjs';
import {openJsonPort} from '../../../../../../implementation/artifact-runtime/json-pipe.mjs';
import {constructNativeData} from '../../../../../../implementation/artifact-runtime/construct-native-data.mjs';
import {readFrozenArtifact} from '../../../../../../implementation/artifact-runtime/frozen-artifact.mjs';
import {resolveArtifactReference} from '../../../../../../implementation/artifact-runtime/resolve-artifact-reference.mjs';
const R=path.resolve(root,'../../../../../..'),base=path.join(R,'workspaces/products/define/implementation/cli/alchlang/tests/fixtures/package'),checks=[],port=openJsonPort(path.join(R,'implementation/artifact-runtime/json-port.py'));
try{
 const snapshot=await readFrozenArtifact({port,call,schemaRoot:R,protocol:await call('Define.PackageGraph.FrozenInspectionProtocol',{marker:true}),read:(name,maximum)=>port.request({operation:'read-file',root:base,path:name,maximum})});
 const body=snapshot.documents.body,rows=snapshot.documents.capture.input_rows,members=new Map(rows.map(row=>[row.binding.path,snapshot.metadata.get('inputs/'+row.binding.path)])),protocol=await constructNativeData({port,call,selector:'Define.PackageConstruction.ReferenceProtocolParts'});
 const resolve=reference=>resolveArtifactReference({port,call,protocol,reference,body,bodyRef:snapshot.body_metadata.ref,rows,members});
 const external=body.handling.find(row=>row.disposition==='reuse').payload.meaning_ref;
 const reused=await resolve(external);assert.equal(reused.standing,'local-reference');checks.push('actual-external-reference-and-reported-standing');
 const applied=await resolve(body.applications[0].meaning_ref);assert.equal(applied.standing,'local-proposed');assert.equal(applied.entry.meaning_id,body.applications[0].meaning_ref.entry_id);checks.push('actual-embedded-working-meaning');
 const specialized=body.handling.find(row=>row.disposition==='specialize');await resolve(specialized.payload.parent_ref);checks.push('actual-specialization-parent-reference');
 for(const [label,patch]of [['identity',{identity:'unrelated:identity'}],['revision',{revision:'unrelated-revision'}],['selected-digest',{sha256:'0'.repeat(64)}],['source-id',{input_id:'unrelated-source'}],['kind',{kind:'unknown'}]]){await assert.rejects(()=>resolve({...external,...patch}));checks.push('negative-reference:'+label);}
 const receipt={schema_version:'define-native-reference-resolution-verification/v1',status:'PASS',source:fingerprint(),checks,check_count:checks.length,python_define_engine_imported:false,full_preparation_workflow:false};writeFileSync(path.join(root,'.local/NATIVE-REFERENCE-VERIFICATION.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));
}finally{await port.close();}