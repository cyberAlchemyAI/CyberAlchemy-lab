import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {main} from '../../../implementation/lab-runtime/alchlang/shared-records/cli.mjs';
import {signPacket} from '../../../implementation/lab-runtime/alchlang/shared-records/security.mjs';
import {nativePort} from '../../../implementation/lab-runtime/alchlang/shared-records/ports.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {bind} from '../../../implementation/lab-runtime/alchlang/shared-records/snapshots.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..');
const load=f=>JSON.parse(readFileSync(f)),bytes=x=>Buffer.from(JSON.stringify(x));
const put=(f,v)=>writeFileSync(f,JSON.stringify(v,null,2)+'\n');
const proposal=load(path.join(here,'source-transition/proposal.json'));
const approval=load(path.join(here,'source-transition/approval.json'));
const cut=proposal.source_snapshot_digest,issuer='principal:lab-shared-operator';
const key=readFileSync(path.join(process.env.HOME,'.config/cyberalchemy-lab/shared-records/operator.pem'));
const trust=load(path.join(here,'trust.json'));
const existing=structuredClone(trust.principals[issuer].grants);
for(const grant of existing)if(grant.cut!==cut&&!trust.principals[issuer].grants.some(g=>g.operation===grant.operation&&g.predicate===grant.predicate&&g.cut===cut))trust.principals[issuer].grants.push({...grant,cut});
const registryAdmission=JSON.parse(Buffer.from(trust.registry_contract.admission_artifact,'base64'));
const currentType=load(path.join(root,'authority/artifact-types/definition-registry/current.json'));
assert.equal(currentType.status,'owner-admitted-current');
assert.equal(digest(readFileSync(path.join(here,'registry-descriptor.json'))),registryAdmission.descriptor_sha256);
const observation={...registryAdmission,observed_source_cut:cut,
 original_owner_admission:bind('registry-admission.json',readFileSync(path.join(here,'registry-admission.json')))};
put(path.join(here,'source-transition/registry-admission-observation.json'),observation);
const observedBytes=bytes(observation);
trust.registry_contract.admission_artifact=observedBytes.toString('base64');
trust.registry_contract.admission=signPacket(bytes({version:1,predicate:'artifact-type-admission',
 operation:'PlanPublication',scope:'workspace:cyberalchemy-lab:lab',cut,artifact:{sha256:digest(observedBytes),bytes:observedBytes.length}}),issuer,key);
put(path.join(here,'trust.json'),trust);
const oldRequest=load(path.join(here,'native-apply.json'));
const input=JSON.parse(Buffer.from(oldRequest.construction.artifact,'base64')).input;
const oldCut=input.value.source_cut;
function recut(value){
 if(Array.isArray(value))return value.map(recut);
 if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,recut(v)]));
 return value===oldCut?cut:value;
}
const value=recut(input.value);
for(const item of load(path.join(here,'authorization.json')).accepted_definitions)
 assert.equal(digest(readFileSync(path.join(root,item.source.path))),item.source.sha256);
value.permission=bind('source-transition/approval.json',readFileSync(path.join(here,'source-transition/approval.json')));
const artifact=bytes({operation:'AssessConstructionEntry',scope:oldRequest.construction.scope,cut,input:{value}});
const construction={operation:'AssessConstructionEntry',scope:oldRequest.construction.scope,cut,artifact:artifact.toString('base64'),
 receipt:signPacket(bytes({version:1,predicate:'verified-planning-input',operation:'AssessConstructionEntry',scope:oldRequest.construction.scope,cut,
 artifact:{sha256:digest(artifact),bytes:artifact.length}}),issuer,key)};
const request={...oldRequest,store:path.join(root,'.local/lab-runtime/shared/current-store'),proposal,approval,
 approval_artifact:readFileSync(path.join(here,'source-transition/approval.json')).toString('base64'),construction};
put(path.join(here,'source-transition/apply.json'),request);
const applied=await main(['native-apply','--file',path.join(here,'source-transition/apply.json')]);
const observed=nativePort({action:'replay',store:request.store,require_current:true});
const receipt={status:'PASS',old_source_cut:oldCut,current_source_cut:cut,
 original_store:oldRequest.store,current_store:request.store,
 reason:'The new canonical Decision changes the repository admission inventory. Preserve the original signed branch and explicitly prepare a fresh data branch at that admitted epoch; no source pins or signed history are rewritten.',
 unchanged_definition_bodies:5,canonical_readmission:false,runtime_copies:0,
 fresh:observed.freshness,head:observed.head,application:applied};
put(path.join(here,'receipts/source-transition.json'),receipt);
const activeFile=path.join(root,'implementation/lab-runtime/shared-workflow.json'),active=load(activeFile);
active.native_store='.local/lab-runtime/shared/current-store';active.native_source_cut=cut;
active.historical_publication_store='.local/lab-runtime/shared/native-store';
put(activeFile,active);
console.log(JSON.stringify({status:'PASS',freshness:observed.freshness.status,source_cut:cut}));
