import fs from 'node:fs';
import path from 'node:path';
import {publishAtomicDirectory} from './atomic-publication.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {MAX_SOURCE_FILE_BYTES} from '../input/limits.js';
import {assertSelectedReconciledProject as assertReconciledProjectPlan,decodeSelectedReconciledCompilation as decodeReconciledCompilationSelection,selectSelectedReconciledArtifacts as selectReconciledArtifacts,selectedReconciledIdentity,type SelectedReconciledProject as ReconciledProjectPlan} from './selected-reconciled-project.js';
import {reconciledLayoutDefinitionSha256,reconciledOutputView} from './reconciled-output-layout.js';
import {APPLICATION_LAYOUT,PROJECT_LAYOUT,type OutputLayout} from './output-layout.js';
import {selectedReconciledExtension} from './selected-reconciled-project.js';

export const RECONCILED_OUTPUT_DEFINITION_SHA256='0dba8ac41c500eef7ef7742019e35f18b87955006566d639e41480ef7ecf7e93';
export const RECONCILED_OUTPUT_RECEIPT_PATH='.domainspec/reconciled-build.json';
const receiptPath=(layout:OutputLayout|undefined)=>layout===undefined?RECONCILED_OUTPUT_RECEIPT_PATH:layout===APPLICATION_LAYOUT.id?APPLICATION_LAYOUT.receipt:PROJECT_LAYOUT.receipt;
export class ReconciledOutputError extends Error {
 readonly exitCode=22;
 constructor(readonly code:string,readonly pointer:string,message:string){super(message);this.name='ReconciledOutputError';}
}
const fail=(code:string,pointer:string,message:string):never=>{throw new ReconciledOutputError('DS_RECONCILED_'+code,pointer,message);};
function freeze<T>(v:T):T{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
function absolute(value:unknown,pointer:string):string {
 if(typeof value!=='string'||!path.isAbsolute(value)||path.resolve(value)!==value)fail('PATH',pointer,'normalized absolute path required');
 return value as string;
}
function present(file:string):boolean {try{fs.lstatSync(file);return true;}catch(error){if((error as NodeJS.ErrnoException).code==='ENOENT')return false;throw error;}}
/** Bounded regular-file read; no symlink or special-file fallback. */
function readRegular(file:string,limit:number):Buffer {
 if(fs.realpathSync(file)!==file)throw Error('symbolic path is unsupported');
 const fd=fs.openSync(file,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW|fs.constants.O_NONBLOCK);
 try{
  const stat=fs.fstatSync(fd);if(!stat.isFile()||stat.size>limit)throw Error('bounded regular file required');
  const buffer=Buffer.alloc(Math.min(stat.size+1,limit+1));let offset=0;
  while(offset<buffer.length){const count=fs.readSync(fd,buffer,offset,buffer.length-offset,null);if(!count)break;offset+=count;}
  if(offset!==stat.size||offset>limit)throw Error('file changed or exceeds bound');
  return buffer.subarray(0,offset);
 }finally{fs.closeSync(fd);}
}
export function readReconciledCompilationSelection(file:unknown){
 const selected=absolute(file,'/compilation-selection');
 try{return decodeReconciledCompilationSelection(JSON.parse(readRegular(selected,MAX_SOURCE_FILE_BYTES).toString('utf8')));}
 catch(error){return fail('SELECTION','/compilation-selection',error instanceof Error?error.message:'invalid selection JSON');}
}
export function createReconciledOutputReceipt(plan:ReconciledProjectPlan,roots:readonly string[]|null=null,outputLayout?:OutputLayout){
 assertReconciledProjectPlan(plan);const view=reconciledOutputView(plan,roots,outputLayout);
 const body={schema_version:'domainspec.reconciled-output-receipt/v1-candidate' as const,definition_sha256:RECONCILED_OUTPUT_DEFINITION_SHA256,
  ...selectedReconciledExtension(plan.selection),
  ...(outputLayout===undefined?{}:{output_layout:outputLayout,layout_definition_sha256:reconciledLayoutDefinitionSha256(outputLayout),source_view_sha256:selectReconciledArtifacts(plan).view_sha256}),
  ...selectedReconciledIdentity(plan),project_plan_sha256:plan.plan_sha256,
  selection_sha256:sha256(canonicalJson(plan.selection)),
  source_capsule_sha256:plan.source_capsule_sha256,roots:view.roots,view_sha256:view.view_sha256,checking_scope:view.checking_scope,
  artifacts:view.artifacts.map(({content,...artifact})=>artifact),verification_scope:'artifact-currentness' as const,
  native_compilation:'not-performed' as const,semantic_observation:'not-performed' as const,formal_verification:'not-performed' as const,authority_effect:'none' as const};
 return freeze({...body,receipt_sha256:sha256(canonicalJson(body))});
}
export type ReconciledOutputReceipt=ReturnType<typeof createReconciledOutputReceipt>;

/** Local materialization only; a checked plan cannot be replaced with caller files. */
export function publishReconciledProject(plan:ReconciledProjectPlan,targetRoot:unknown,roots:readonly string[]|null=null,outputLayout?:OutputLayout){
 assertReconciledProjectPlan(plan);const view=reconciledOutputView(plan,roots,outputLayout),receipt=createReconciledOutputReceipt(plan,roots,outputLayout);
 const selectedReceiptPath=receiptPath(outputLayout);
 const target=absolute(targetRoot,'/target-root'),parent=path.dirname(target);
 if(present(target))fail('OUTPUT_EXISTS','/target-root','target already exists');
 let stat:fs.Stats;try{stat=fs.lstatSync(parent);}catch{return fail('OUTPUT_PARENT','/target-root','parent must exist');}
 if(!stat!.isDirectory()||stat!.isSymbolicLink()||fs.realpathSync(parent)!==parent)fail('OUTPUT_PARENT','/target-root','parent must be a real directory without symbolic ancestors');
 try{
  publishAtomicDirectory(target,[...view.artifacts,{relative_path:selectedReceiptPath,content:canonicalJson(receipt)+'\n'}],'.domainspec-reconciled-');
 }catch(error){
  if((error as NodeJS.ErrnoException).code==='DS_ATOMIC_EXISTS')return fail('OUTPUT_EXISTS','/target-root','target appeared during publication');
  if((error as NodeJS.ErrnoException).code==='DS_NATIVE_PERMISSION')return fail('OUTPUT_UNAVAILABLE','/target-root',error instanceof Error?error.message:'output writing unavailable');
  if(error instanceof ReconciledOutputError)throw error;
  return fail('OUTPUT_ATOMIC','/target-root',error instanceof Error?error.message:'local output failed');
 }
 return freeze({target_root:target,receipt_path:selectedReceiptPath,receipt});
}

/** Exact content/inventory verification, not native compilation or formal proof. */
export function verifyReconciledProject(plan:ReconciledProjectPlan,targetRoot:unknown,roots:readonly string[]|null=null,outputLayout?:OutputLayout){
 assertReconciledProjectPlan(plan);const view=reconciledOutputView(plan,roots,outputLayout),receipt=createReconciledOutputReceipt(plan,roots,outputLayout),target=absolute(targetRoot,'/target-root');
 const selectedReceiptPath=receiptPath(outputLayout);
 const checks:{id:string;result:'pass'|'fail'}[]=[];
 let real=false;try{const stat=fs.lstatSync(target);real=stat.isDirectory()&&!stat.isSymbolicLink()&&fs.realpathSync(target)===target;}catch{/* absent output */}
 checks.push({id:'real-target-directory',result:real?'pass':'fail'});
 const expectedReceipt=canonicalJson(receipt)+'\n';let receiptCurrent=false;
 if(real)try{receiptCurrent=readRegular(path.join(target,selectedReceiptPath),Buffer.byteLength(expectedReceipt)).toString('utf8')===expectedReceipt;}catch{/* failed receipt check */}
 checks.push({id:'receipt-current',result:receiptCurrent?'pass':'fail'});
 const expectedFiles=[selectedReceiptPath,...view.artifacts.map(a=>a.relative_path)],expectedPaths=new Set(expectedFiles);
 for(const file of expectedFiles){let parent=path.posix.dirname(file);while(parent!=='.'){expectedPaths.add(parent);parent=path.posix.dirname(parent);}}
 for(const a of view.artifacts){let current=false;if(real)try{const bytes=readRegular(path.join(target,a.relative_path),a.size_bytes);current=bytes.length===a.size_bytes&&sha256(bytes)===a.sha256;}catch{/* failed artifact check */}checks.push({id:'artifact:'+a.relative_path,result:current?'pass':'fail'});}
 const observed=new Set<string>();let inventory=real,count=0;
 const walk=(folder:string):void=>{
  if(!inventory)return;
  for(const entry of fs.readdirSync(folder,{withFileTypes:true})){
   if(++count>expectedPaths.size+1){inventory=false;return;}
   const file=path.join(folder,entry.name),relative=path.relative(target,file).split(path.sep).join('/'),stat=fs.lstatSync(file);
   observed.add(relative);if(stat.isSymbolicLink()||!expectedPaths.has(relative)){inventory=false;return;}
   if(stat.isDirectory())walk(file);else if(!stat.isFile()||!expectedFiles.includes(relative)){inventory=false;return;}
  }
 };
 if(real)try{walk(target);}catch{inventory=false;}
 checks.push({id:'exact-path-inventory',result:inventory&&observed.size===expectedPaths.size?'pass':'fail'});
 return freeze({schema_version:'domainspec.reconciled-output-verification/v1-candidate' as const,result:checks.every(c=>c.result==='pass')?'pass' as const:'fail' as const,
  verification_scope:'artifact-currentness' as const,checks,expected_receipt_sha256:receipt.receipt_sha256,project_plan_sha256:plan.plan_sha256,view_sha256:view.view_sha256,
  native_compilation:'not-performed' as const,semantic_observation:'not-performed' as const,formal_verification:'not-performed' as const,authority_effect:'none' as const});
}
