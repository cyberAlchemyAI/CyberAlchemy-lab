import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import path from 'node:path';
import {loadTrust,verifyImplementation} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
import {captureRecovery} from '../../../implementation/lab-runtime/alchlang/shared-records/recovery.mjs';
import {verifyOperationalReadiness} from '../../../implementation/lab-runtime/alchlang/shared-records/readiness.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {build} from '../../../implementation/lab-runtime/alchlang/shared-records/build.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),runtime=path.join(root,'implementation/lab-runtime/alchlang/shared-records');
const load=f=>JSON.parse(readFileSync(f)),relative=f=>path.relative(root,f);
const put=(f,v)=>{mkdirSync(path.dirname(f),{recursive:true});writeFileSync(f,JSON.stringify(v,null,2)+'\n');return f;};
const binding=f=>({path:relative(f),sha256:digest(readFileSync(f)),bytes:readFileSync(f).length});
const trust=loadTrust(path.join(here,'runtime-trust.json')),implementation=verifyImplementation(trust.implementation);
const receipts={};
for(const name of ['HARDENING','INTEGRATION','PUBLICATION','REGISTRY']){
 const file=path.join(runtime,name+'-VERIFICATION.json'),receipt=load(file);
 assert.equal(receipt.status,'PASS');assert.equal(receipt.implementation,implementation,name+' stale verification');
 receipts[name]=binding(file);
}
assert.equal(load(path.join(here,'LIVE-WORKFLOW-VERIFICATION.json')).status,'PASS');
const configFile=path.join(root,'implementation/lab-runtime/shared-workflow.json'),config=load(configFile);
const active={...config,root,...Object.fromEntries(['database','journal','native_store'].map(k=>[k,path.join(root,config[k])]))};
const native=load(path.join(here,'ORIGINAL-NATIVE-STATE.json'));
for(const [name,bytes]of Object.entries(native))assert.deepEqual(readFileSync(path.join(root,'.local/lab-runtime/shared',name)),Buffer.from(bytes,'base64'),'original native file changed '+name);
const ready=await verifyOperationalReadiness(active,trust);
const archive=captureRecovery(active,native),archiveFile=path.join(here,'operational/RECOVERY.json.gz');writeFileSync(archiveFile,archive);
const generation=build();
put(path.join(here,'GENERATION-RECEIPT.json'),{status:'PASS',implementation,model_source:generation.source,generated_files:generation.files,compiler:'original Craft Core 0.7.0-candidate.0 / CLI 1.3.0',chain:binding(path.join(here,'CHAIN-HANDOFFS.json'))});
const selectedFile=path.join(root,'authority/profiles/shared-records/current.json');
put(selectedFile,{schema_version:'lab-shared-implementation-selection/v1',status:'selected-and-verified',authorization:binding(path.join(here,'AUTHORIZATION.json')),implementation,
 execution_manifest:binding(path.join(here,'EXECUTION-MANIFEST.json')),contracts:binding(path.join(here,'CONTRACTS.json')),chain:binding(path.join(here,'CHAIN-HANDOFFS.json')),
 receipts,recovery:binding(archiveFile),readiness:ready,semantic_decisions:'Existing original owner decisions remain unchanged; this selection authorizes technical repair and qualification only.'});
config.trust=relative(path.join(here,'runtime-trust.json'));config.execution_selection=binding(selectedFile);config.recovery=binding(archiveFile);put(configFile,config);
console.log(JSON.stringify({status:'PASS',implementation,readiness:ready,recovery:binding(archiveFile)}));
