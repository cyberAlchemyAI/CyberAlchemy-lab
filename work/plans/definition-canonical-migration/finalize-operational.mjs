import './qualify-history.mjs';
import assert from 'node:assert/strict';import {readFileSync,writeFileSync,readdirSync} from 'node:fs';import path from 'node:path';
import {captureRecovery} from '../../../implementation/lab-runtime/alchlang/shared-records/recovery.mjs';
import {activation} from '../../../implementation/lab-runtime/alchlang/shared-records/activation.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
const root=path.resolve(import.meta.dirname,'../../..'),here=import.meta.dirname,load=f=>JSON.parse(readFileSync(path.resolve(root,f))),put=(f,v)=>writeFileSync(path.resolve(root,f),JSON.stringify(v,null,2)+'\n'),B=f=>{const raw=readFileSync(path.resolve(root,f));return {path:f,sha256:digest(raw),bytes:raw.length};};
const original=load('implementation/lab-runtime/shared-workflow.json'),nativeFiles={};
assert.equal(load(path.relative(root,path.join(here,'batches/unit-23/COMPLETED.json'))).versions,377);
for(const [prefix,store]of [['native-store',path.resolve(root,original.historical_publication_store)],['current-store',path.resolve(root,original.native_store)]]){
 for(const name of ['config.json','baseline.json','HEAD.json',...readdirSync(path.join(store,'transactions')).filter(n=>/^[0-9]{10}\.json$/.test(n)).sort().map(n=>'transactions/'+n)])nativeFiles[prefix+'/'+name]=readFileSync(path.join(store,name)).toString('base64');
}
const archive=captureRecovery(activation({required:true}),nativeFiles),recovery=path.relative(root,path.join(here,'operational/RECOVERY.json.gz'));writeFileSync(path.resolve(root,recovery),archive);
const binding={...B(recovery),uncompressed_bytes:archive.readUInt32LE(archive.length-4)};assert(binding.uncompressed_bytes<=512*1024*1024);
original.recovery=binding;original.decision_ref='decision:definition-v2-canonical-migration-0077';original.decision=B('docs/decisions/0077-definition-v2-canonical-migration/decision.json');put('implementation/lab-runtime/shared-workflow.json',original);
put(path.relative(root,path.join(here,'operational/RECOVERY-BINDING.json')),{...binding,status:'captured-final-data-restoration-verified-separately',private_keys_included:false,runtime_code_included:false,native_transactions:readdirSync(path.resolve(root,original.native_store,'transactions')).length});
console.log(JSON.stringify({recovery:binding,selector:original.selector,decision:original.decision_ref}));
