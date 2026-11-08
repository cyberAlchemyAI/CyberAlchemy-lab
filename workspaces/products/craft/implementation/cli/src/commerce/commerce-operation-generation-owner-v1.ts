/** Source construction owner. It emits/imports actual source artifacts, but
 * creates no native basis, late assembly, invocation or commit authority.
 * Open Questions: implementation/craft-alchlang-commerce-2026-10-16/evidence/EC18/CONTEXT.md. */
import path from 'node:path';
import {mkdirSync} from 'node:fs';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {stripTypeScriptTypes} from 'node:module';
import {createHash} from 'node:crypto';
import {dataDigest} from '../profile-engine/contracts.js';
import {pinCoreImplementation,pinCorePhysicalCaptures,writeCoreExclusiveFile,type CorePhysicalFile} from './commerce-core-physical.js';
import {CoreCommerceSourceError} from './commerce-core-syntax.js';
import {assertCommerceLocalPlanOwnerV1,type CommerceLocalPlanOwnerV1,type CommerceLocalOperationHandleV1} from './commerce-local-plan-owner-v1.js';
import {renderCommerceEffectfulTransactionSourcesV1,type CommerceEffectSourceBundleV1} from '../generation/commerce-effectful-operation-source-v1.js';
import {renderCommerceOperationControlSourcesV1} from '../generation/commerce-operation-control-source-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['../generation/commerce-effectful-operation-source-v1'+ext,'../generation/commerce-operation-control-source-v1'+ext,'../generation/commerce-recovery-plan-v1'+ext,'commerce-transaction-source-failure-v1'+ext,'commerce-local-plan-owner-v1'+ext,'commerce-core-physical'+ext,'../profile-engine/contracts'+ext]);
function bad(code:string):never {const error=new Error(code);Object.assign(error,{code});throw error;}
export interface CommerceGeneratedEffectSourceV1 {readonly kind:'original-generated-native-effect-source/v1-candidate'}
export interface CommerceImportedEffectSourceV1 {readonly kind:'original-imported-native-effect-source/v1-candidate'}
export interface CommerceOperationGenerationOwnerV1 {
 generate(operation:CommerceLocalOperationHandleV1):CommerceGeneratedEffectSourceV1;
 generateControl(operation:CommerceLocalOperationHandleV1):CommerceGeneratedEffectSourceV1;
 files(source:CommerceGeneratedEffectSourceV1):CommerceEffectSourceBundleV1;
 materialize(source:CommerceGeneratedEffectSourceV1,directory:string):CommerceImportedEffectSourceV1;
 inspect(imported:CommerceImportedEffectSourceV1):Readonly<Record<string,unknown>>;
 importDataComponent(imported:CommerceImportedEffectSourceV1):Promise<Readonly<{qualification:string;transactions:readonly unknown[];whole_operation_available:false}>>;
 importControlComponent(imported:CommerceImportedEffectSourceV1):Promise<Readonly<{qualification:string;control_source_available:true;original_runtime_assembly:false}>>;
 assertCurrent():void;
}
const owners=new WeakSet<object>();
export function assertCommerceOperationGenerationOwnerV1(owner:CommerceOperationGenerationOwnerV1):void {if(!owner||typeof owner!=='object'||!owners.has(owner))bad('ForeignOwner');owner.assertCurrent();}
export function createCommerceOperationGenerationOwnerV1(plans:CommerceLocalPlanOwnerV1):CommerceOperationGenerationOwnerV1 {
 assertCommerceLocalPlanOwnerV1(plans);pin.assertCurrent();type Source={op:CommerceLocalOperationHandleV1;bundle:CommerceEffectSourceBundleV1};type Imported={source:Source;directory:string;files:readonly CorePhysicalFile[];physical:ReturnType<typeof pinCorePhysicalCaptures>};const sources=new WeakMap<object,Source>(),imports=new WeakMap<object,Imported>();
 const current=()=>{pin.assertCurrent();plans.assertCurrent();};
 const source=(h:CommerceGeneratedEffectSourceV1)=>{current();const row=h&&typeof h==='object'?sources.get(h):undefined;if(!row)bad('ForeignSource');plans.assertOperationCurrent(row.op);return row;};
 const imported=(h:CommerceImportedEffectSourceV1)=>{current();const row=h&&typeof h==='object'?imports.get(h):undefined;if(!row)bad('ForeignImport');plans.assertOperationCurrent(row.source.op);try{row.physical.assertCurrent();}catch(error){if(error instanceof CoreCommerceSourceError&&error.diagnostics[0]?.code==='StaleOwner')bad('StaleImport');throw error;}return row;};
 const owner:CommerceOperationGenerationOwnerV1=Object.freeze({
  generate(op:CommerceLocalOperationHandleV1){current();const view=plans.inspectOperation(op),bundle=renderCommerceEffectfulTransactionSourcesV1({operation:view.operation,source_capture_sha256:view.source_capture_sha256,effect_plan:view.plan,transactions:view.transactions});const h=Object.freeze({kind:'original-generated-native-effect-source/v1-candidate' as const});sources.set(h,{op,bundle});return h;},
  generateControl(op:CommerceLocalOperationHandleV1){current();const view=plans.inspectOperation(op),bundle=renderCommerceOperationControlSourcesV1({operation:view.operation,source_capture_sha256:view.source_capture_sha256,effect_plan:view.plan,transactions:view.transactions});const h=Object.freeze({kind:'original-generated-native-effect-source/v1-candidate' as const});sources.set(h,{op,bundle});return h;},
  files(h:CommerceGeneratedEffectSourceV1){return source(h).bundle;},
  materialize(h:CommerceGeneratedEffectSourceV1,directory:string){const s=source(h);if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory)bad('OutputPath');mkdirSync(directory,{mode:0o700});const files:CorePhysicalFile[]=[];for(const f of s.bundle.files){files.push(writeCoreExclusiveFile(path.join(directory,f.path),f.text));files.push(writeCoreExclusiveFile(path.join(directory,f.path.replace(/\.ts$/,'.js')),stripTypeScriptTypes(f.text)));}files.push(writeCoreExclusiveFile(path.join(directory,'effect-source-manifest.json'),JSON.stringify(s.bundle.manifest,null,2)+'\n'));const physical=pinCorePhysicalCaptures(files);current();const out=Object.freeze({kind:'original-imported-native-effect-source/v1-candidate' as const});imports.set(out,{source:s,directory,files,physical});imported(out);return out;},
  inspect(h:CommerceImportedEffectSourceV1){const s=imported(h);return Object.freeze({manifest:s.source.bundle.manifest,directory:s.directory,members:s.files.map(f=>({...f.file,fingerprint:f.fingerprint})),source_code_sha256:createHash('sha256').update(s.source.bundle.files.map(f=>f.text).join('')).digest('hex'),manifest_sha256:dataDigest(s.source.bundle.manifest),native_handles_created:false,qualification:'physically-generated-import-component-only;not-complete-operation-or-native-assembly',authority_effect:'none'});},
  async importDataComponent(h:CommerceImportedEffectSourceV1){const s=imported(h),loaded=await import(pathToFileURL(path.join(s.directory,'effectful-transactions.js')).href);imported(h);if(typeof loaded.executeTransaction!=='function'||typeof loaded.assertWholeOperationGenerationAvailable!=='function'||!Array.isArray(loaded.transactions))bad('MissingGeneratedExport');let unavailable=false;try{loaded.assertWholeOperationGenerationAvailable();}catch(e){unavailable=(e as Error).message==='OuterOperationAndRecoveryGenerationNotYetJoined';}if(!unavailable)bad('FalseWholeOperationSupport');return Object.freeze({qualification:String(loaded.qualification),transactions:loaded.transactions,whole_operation_available:false as const});},
  async importControlComponent(h:CommerceImportedEffectSourceV1){const s=imported(h);if(s.source.bundle.manifest.outer_control_generation!==true)bad('MissingControlSource');const loaded=await import(pathToFileURL(path.join(s.directory,'operation-control.js')).href);imported(h);if(typeof loaded.runOperation!=='function'||typeof loaded.controlSourceQualification!=='string')bad('MissingGeneratedControlExport');return Object.freeze({qualification:loaded.controlSourceQualification,control_source_available:true as const,original_runtime_assembly:false as const});},assertCurrent:current,
 });owners.add(owner);current();return owner;
}
