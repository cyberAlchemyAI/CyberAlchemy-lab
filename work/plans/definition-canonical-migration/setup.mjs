import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';import path from 'node:path';
import {captureImplementation,loadTrust} from '../../../implementation/lab-runtime/alchlang/shared-records/implementation.mjs';
import {bind} from '../../../implementation/lab-runtime/alchlang/shared-records/snapshots.mjs';
import {digest} from '../../../implementation/lab-runtime/alchlang/shared-records/verified-projection.mjs';
import {signPacket} from '../../../implementation/lab-runtime/alchlang/shared-records/security.mjs';
const here=import.meta.dirname,root=path.resolve(here,'../../..'),D=path.join(root,'docs/decisions/0077-definition-v2-canonical-migration'),load=f=>JSON.parse(readFileSync(f));
const put=(f,v)=>{mkdirSync(path.dirname(f),{recursive:true});writeFileSync(f,JSON.stringify(v,null,2)+'\n');return f;};
const relative=f=>path.relative(root,f),binding=f=>({path:relative(f),sha256:digest(readFileSync(f)),bytes:readFileSync(f).length});
const context=load(path.join(here,'NATIVE-CONTEXT.json')),cut=context.cut,scope='workspace:cyberalchemy-lab:lab',issuer='principal:lab-shared-operator';
const trust=load(path.join(root,'work/plans/shared-definitions-records-r5/runtime-trust.json'));
const implementation=captureImplementation();const mf=put(path.join(here,'EXECUTION-MANIFEST.json'),implementation);trust.implementation=binding(mf);
for(const principal of Object.values(trust.principals)){for(const grant of [...principal.grants])if(!principal.grants.some(g=>g.cut===cut&&g.predicate===grant.predicate&&g.operation===grant.operation&&g.scope===grant.scope))principal.grants.push({...grant,cut});}
const authFile=path.join(D,'authorization.json'),auth=binding(authFile),authorization=load(authFile);
const decisionFile=path.join(D,'decision.json');put(decisionFile,{schema_version:'lab-exact-owner-decision/v1',decision_ref:'decision:definition-v2-canonical-migration-0077',status:'owner-accepted-executing',selected_outcome:'accept-exact-183-representations-and-publish-in-verified-batches',principal_ref:'person:<vrondelli>',authorization:auth,accepted_versions:authorization.accepted_definitions.map(x=>x.version),source_cut:cut,owner_signature_claim:false,delegation:'Existing private operator key signs mechanical runtime approvals and attestations under this exact instruction.'});
for(const owner of [...new Set(authorization.accepted_definitions.map(x=>x.owner))]){
 const file=path.join(D,owner==='role:definition-owner'?'definition-owner-role.json':'craft-owner-role.json');
 put(file,{schema_version:'lab-shared-exact-role-assignment/v1',issued_by:'role:repository-owner',principal_ref:'person:<vrondelli>',role_ref:owner,status:'active',basis:auth,scope:authorization.accepted_definitions.filter(x=>x.owner===owner).map(x=>x.version),delegation:{runtime_signer:issuer,owner_signature_claim:false,purpose:'Exact authorized canonical migration only'}});
 for(const target of authorization.accepted_definitions.filter(x=>x.owner===owner)){
  const body=load(path.join(root,target.source.path));assert.equal(digest(readFileSync(path.join(root,target.source.path))),target.source.sha256);
  const out=path.join(D,'dispositions',target.version.split('@')[0]+'.json');
  put(out,{schema_version:'lab-exact-definition-owner-disposition/v1',decision_ref:'decision:definition-v2-canonical-migration-0077:'+body.definition_id,target:target.version,original:target.source,owner,principal_ref:'person:<vrondelli>',role_assignment:binding(file),scope:body.scope.authority_scope_ref,source_cut:cut,outcome:'Accepted',canonical_admission:true,authorization:auth,previous:load(path.join(root,'work/plans/definition-catalog-v2-layout/MAPPING.json')).entries.find(e=>e.definition_id===body.definition_id).source.body,reason:'Explicit owner acceptance in the current user instruction of this exact generated representation; all semantic fields remain unchanged.'});
 }
}
function material(file){const b=bind(relative(file),readFileSync(file));trust.materials[b.ref]={path:relative(file),sha256:b.sha256};return b;}
material(authFile);for(const owner of ['definition-owner-role.json','craft-owner-role.json'])material(path.join(D,owner));
for(const target of authorization.accepted_definitions){material(path.join(root,target.source.path));material(path.join(D,'dispositions',target.version.split('@')[0]+'.json'));}
const privatePem=readFileSync(path.join(process.env.HOME,'.config/cyberalchemy-lab/shared-records/operator.pem'));
const observed=JSON.parse(Buffer.from(trust.registry_contract.admission_artifact,'base64'));
trust.registry_contract.admission=signPacket(Buffer.from(JSON.stringify({version:1,predicate:'artifact-type-admission',operation:'PlanPublication',scope,cut,artifact:{sha256:digest(Buffer.from(trust.registry_contract.admission_artifact,'base64')),bytes:Buffer.from(trust.registry_contract.admission_artifact,'base64').length}})),issuer,privatePem);
const tf=put(path.join(here,'runtime-trust.json'),trust);
const selectedFile=path.join(root,'authority/profiles/shared-records/current.json');
put(selectedFile,{schema_version:'lab-shared-implementation-selection/v1',status:'selected-for-authorized-source-transition',authorization:{...auth,verbatim:authorization.verbatim},implementation:implementation.digest,execution_manifest:binding(mf),chain:binding(path.join(here,'CHAIN.json')),prior_selection:binding(path.join(here,'PREVIOUS-EXECUTION-SELECTION.json')),scope:'User-authorized repair and exact migration; readiness remains separately checked.'});
const config=load(path.join(root,'implementation/lab-runtime/shared-workflow.json'));config.trust=relative(tf);config.execution_selection=binding(selectedFile);put(path.join(root,'implementation/lab-runtime/shared-workflow.json'),config);
console.log(JSON.stringify({status:'selected',implementation:implementation.digest,source_cut:cut,accepted:authorization.accepted_definitions.length}));
