import assert from 'node:assert/strict';
import path from 'node:path';
import {readFileSync,writeFileSync,mkdtempSync,mkdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {root,node,fingerprint} from './local-capture-build.mjs';
import {callNative as call} from './runtime/native.mjs';
import {openJsonPort} from '../../../../../../implementation/artifact-runtime/json-pipe.mjs';
import {captureLocalSnapshot} from '../../../../../../implementation/artifact-runtime/capture-snapshot.mjs';
const R=path.resolve(root,'../../../../../..'),base=path.join(R,'workspaces/products/define/implementation/cli/alchlang/tests/fixtures/package'),capturedAt='2026-11-09T00:00:00+00:00',raw=readFileSync(path.join(base,'request.json')),checks=[];
const expected=JSON.parse(readFileSync(path.join(root,'tests/fixtures/expected-capture.json')));
const guard=mkdtempSync(path.join(root,'.local/capture-no-legacy-'));writeFileSync(path.join(guard,'sitecustomize.py'),`import sys,importlib.abc\nclass NoLegacy(importlib.abc.MetaPathFinder):\n def find_spec(self,fullname,path=None,target=None):\n  if fullname.split('.')[0]=='define_core':raise RuntimeError('legacy-Define-engine-forbidden')\nsys.meta_path.insert(0,NoLegacy())\n`);process.env.PYTHONPATH=guard;
const port=openJsonPort(path.join(R,'implementation/artifact-runtime/json-port.py'));
try{
 const stored=await port.request({operation:'store-bytes',bytes_base64:raw.toString('base64')});
 const result=await captureLocalSnapshot({port,call,protocol:await call('Define.PackageConstruction.LocalCaptureProtocolValue',{marker:true}),requestRef:stored.ref,read:(name,maximum)=>port.request({operation:'read-file',root:path.join(base,'inputs'),path:name,maximum}),schemaRoot:R,capturedAt});
 assert.deepEqual(result.capture,expected.capture);checks.push('actual-retained-request-exact-capture-equivalence');
 const directory=mkdtempSync(path.join(root,'.local/capture-equivalence-'));
 await port.request({operation:'publish-refs',destination:path.join(directory,'snapshot'),members:Array.from(result.members,([path,row])=>({path,ref:row.ref}))});
 for(const [name,encoded]of Object.entries(expected.members))assert.deepEqual(readFileSync(path.join(directory,'snapshot',name)),Buffer.from(encoded,'base64'));checks.push('exact-source-catalog-and-encoding-bytes-equivalence');
 await assert.rejects(()=>call('Define.PackageConstruction.VerifyLocalSourcePath',{path:'define-source-catalog.json'}));checks.push('reserved-source-path-refused');
 await assert.rejects(()=>call('Define.PackageConstruction.VerifyLocalCaptureStatistics',{value:{count:'241',request_bytes:'1',parts:[]}}));checks.push('capture-count-bound');
 await assert.rejects(()=>call('Define.PackageConstruction.VerifyLocalCaptureStatistics',{value:{count:'1',request_bytes:'1048577',parts:[]}}));checks.push('request-byte-bound');
 await assert.rejects(()=>call('Define.PackageConstruction.VerifyLocalCaptureStatistics',{value:{count:'1',request_bytes:'1',parts:[['12582913']]}}));checks.push('selected-source-byte-bound');
 const changed=JSON.parse(raw),first=changed.source_bindings[0];changed.source_bindings.push({...first,sha256:'0'.repeat(64)});
 const changedRef=await port.request({operation:'encode-ref',value:changed});
 await assert.rejects(async()=>captureLocalSnapshot({port,call,protocol:await call('Define.PackageConstruction.LocalCaptureProtocolValue',{marker:true}),requestRef:changedRef.ref,read:(name,maximum)=>port.request({operation:'read-file',root:path.join(base,'inputs'),path:name,maximum}),schemaRoot:R,capturedAt}),/original-binding-mismatch/);checks.push('conflicting-declared-source-epoch-refused');
 const receipt={schema_version:'define-native-local-capture-verification/v1',status:'PASS',source:fingerprint(),checks,check_count:checks.length,legacy_engine_use:'retained exact compatibility fixture; no engine',legacy_engine_runtime_imports:'actively blocked',full_preparation_workflow:false};writeFileSync(path.join(root,'.local/NATIVE-LOCAL-CAPTURE-VERIFICATION.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));
}finally{await port.close();}