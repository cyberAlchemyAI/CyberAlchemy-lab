import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {validateProfilePackageV2} from '../../src/profile-engine/contracts-v2.ts';
import {evaluateProfile} from '../../src/profile-engine/evaluate.ts';
// Open questions: actual composed dependency and installed matrix BA08/15/18.
test('v2 package metadata supports distinct entries and explicitly selects local versus one shared Operation transport',()=>{
 const root=path.resolve(import.meta.dirname,'../../profiles'),tables={applications:{fields:{id:'string' as const,source:'string' as const,selector:'string' as const},rows:[{id:'receiveNotice',source:'orders.alch',selector:'ReceiveNotice'},{id:'acknowledge',source:'ack.alch',selector:'ReceiveNotice'}]}};
 for(const id of ['node-http-entry-local-v2','node-http-shared-ports-v2']){
  const raw=JSON.parse(readFileSync(path.join(root,id,'profile.json'),'utf8')),pkg=validateProfilePackageV2(raw),result=evaluateProfile(pkg,tables),apps=result.emissions.filter(e=>e.role==='application-operation');
  assert.deepEqual(apps.map(e=>[e.fields.id,e.fields.project_ref,e.fields.route]),[['receiveNotice','orders.alch','/receiveNotice'],['acknowledge','ack.alch','/acknowledge']]);
  const shared=result.emissions.filter(e=>e.role==='shared-http-port');assert.equal(shared.length,pkg.application_runtime.transport==='shared'?1:0);if(shared.length){assert.equal(shared[0]!.fields.artifact_path,'runtime/application-http.mts');assert.deepEqual(JSON.parse(JSON.stringify(shared[0]!.fields.technical)),{kind:'application-operation'});}
  const missing=structuredClone(raw);missing.application_runtime.transport_asset='unknown';assert.throws(()=>validateProfilePackageV2(missing),/RUNTIME_ASSET/);
  const reclassified=structuredClone(raw);reclassified.assets.find((a:any)=>a.id==='application-http').kind='data';assert.throws(()=>validateProfilePackageV2(reclassified),/RUNTIME_ASSET/);
 }
});
