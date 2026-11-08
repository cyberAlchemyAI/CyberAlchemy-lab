import path from 'node:path';
import {ProfileRejected,reject} from './contracts.js';
import {validateProfilePackageV2,type ProfilePackageV2} from './contracts-v2.js';
import {validateBusinessAuthoringContract} from './business-authoring-contracts.js';
import type {BusinessAuthoringProject,BusinessWireConvention,BUSINESS_AUTHORING_CONTRACT,BUSINESS_AUTHORING_RECIPE,BUSINESS_AUTHORING_LOGIC} from './business-authoring-protocol.js';

// B05.1 captures selection only. Open questions: docs/BUSINESS-AUTHORING-CONTRACTS.md.
export interface ProfilePackageV3 extends Omit<ProfilePackageV2,'schema_version'|'engine'> {
 readonly schema_version:'craft.profile-package/v3-candidate';
 readonly engine:'craft.profile-engine/v3-candidate';
 readonly authoring:Readonly<{
  contract:typeof BUSINESS_AUTHORING_CONTRACT;input_schema:'alchlang.business-spec/v1-candidate';
  recipe_ref:typeof BUSINESS_AUTHORING_RECIPE;logic_profile:typeof BUSINESS_AUTHORING_LOGIC;
  target:'node-typescript';effects:'none';wire:BusinessWireConvention;
 }>;
}
function unique(values:readonly string[],at:string):void {
 if(new Set(values).size!==values.length)reject('BUSINESS_PROFILE_DUPLICATE_ID',at,'one distinct identity/path required');
}
/** Every path in a selected package is owned; identity manifests use explicit absolute files. */
export function assertBusinessAuthoringRelativePath(value:string,at:string):void {
 if(!value||path.isAbsolute(value)||path.win32.isAbsolute(value)||/^[A-Za-z]:/.test(value)||/[\\\u0000-\u001f\u007f]/u.test(value)||value.split('/').some(part=>!part||part==='.'||part==='..'))
  reject('BUSINESS_PROFILE_PATH_ESCAPE',at,'portable owned relative path required');
}
export function validateBusinessAuthoringProject(input:unknown):BusinessAuthoringProject {
 const data=validateBusinessAuthoringContract<BusinessAuthoringProject>('project',input);
 unique(data.models.map(model=>model.id),'/models');unique(data.models.map(model=>model.source),'/models/source');
 unique(data.profiles.map(profile=>profile.id),'/profiles');unique(data.profiles.map(profile=>profile.path),'/profiles/path');
 unique(data.decisions.map(decision=>decision.model_id),'/decisions/model_id');unique(data.decisions.map(decision=>decision.path),'/decisions/path');
 for(const [i,model] of data.models.entries())assertBusinessAuthoringRelativePath(model.source,`/models/${i}/source`);
 for(const [i,profile] of data.profiles.entries()){
  assertBusinessAuthoringRelativePath(profile.path,`/profiles/${i}/path`);
  if(!/^\d+\.\d+\.\d+$/.test(profile.version))reject('BUSINESS_PROFILE_VERSION',`/profiles/${i}/version`,'exact package version required');
 }
 for(const [i,decision] of data.decisions.entries()){
  assertBusinessAuthoringRelativePath(decision.path,`/decisions/${i}/path`);
  if(!data.models.some(model=>model.id===decision.model_id))reject('BUSINESS_PROFILE_DECISION_MODEL',`/decisions/${i}/model_id`,'decision must select a declared model');
 }
 unique([...data.models.map(model=>model.source),...data.decisions.map(decision=>decision.path)],'/models/decisions');
 return data;
}
export function validateProfilePackageV3(input:unknown):ProfilePackageV3 {
 const data=validateBusinessAuthoringContract<ProfilePackageV3>('package',input);
 // Share the existing finite technical rule/role/asset validator, never its loader or snapshot registry.
 const {authoring:_authoring,...technical}=data;
 try{validateProfilePackageV2({...technical,schema_version:'craft.profile-package/v2-candidate',engine:'craft.profile-engine/v2-candidate'});}
 catch(error){if(error instanceof ProfileRejected)reject(error.code.replace(/^PROFILE_/,'BUSINESS_PROFILE_'),error.pointer,error.message);throw error;}
 for(const [i,dependency] of data.dependencies.entries())assertBusinessAuthoringRelativePath(dependency.path,`/dependencies/${i}/path`);
 for(const [i,asset] of data.assets.entries())assertBusinessAuthoringRelativePath(asset.path,`/assets/${i}/path`);
 unique(data.dependencies.map(dependency=>dependency.path),'/dependencies/path');
 unique([data.application_runtime.formal_profile_asset,data.application_runtime.identity_algorithm_asset,data.application_runtime.settlement_asset,data.application_runtime.transport_asset],'/application_runtime');
 const shared=data.capabilities.some(capability=>capability.role==='shared-http-port');
 if(shared!==(data.application_runtime.transport==='shared'))reject('BUSINESS_PROFILE_TRANSPORT_COMPATIBILITY','/application_runtime/transport','shared transport requires exactly its explicit shared role');
 // The selected native Operation HTTP contract currently bounds body reading to thirty seconds.
 if(data.authoring.wire.timeout_ms>30000)reject('BUSINESS_PROFILE_WIRE_COMPATIBILITY','/authoring/wire/timeout_ms','selected transport supports at most 30000 milliseconds');
 return data;
}
