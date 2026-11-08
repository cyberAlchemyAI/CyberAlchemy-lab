import {closeSync,constants,fstatSync,lstatSync,mkdirSync,mkdtempSync,openSync,readdirSync,readSync,writeSync,type BigIntStats} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {lowerDirectBusinessV2,assertLoweredDirectBusinessV2Current} from './business-authoring-carriers.js';
import {deriveDirectBusinessApplicationBindingsV2,type DerivedDirectBusinessBindingsV2} from './business-application-bindings.js';
import {deriveDirectBusinessApplicationActionsV2,type DirectOperationActionsV2} from './business-application-actions.js';
import {prepareDirectApplicationExecutableV2,assertPreparedDirectApplicationExecutableV2Current,type PreparedDirectExecutableV2,type DirectBusinessCoreSurfaceV2} from './application-executable.js';
import type {ResolvedBusinessSpecV2} from './business-authoring-protocol-v2.js';
import type {AuthoringBusinessInputV2} from './business-authoring-identity-protocol-v2.js';
import type {LoweredDirectBusinessV2} from './business-authoring-stages-v2.js';

export interface PreparedDirectBusinessAuthoringApplicationV2 {
 readonly kind:'prepared-direct-business-authoring-application-v2';readonly lowered:LoweredDirectBusinessV2;
 readonly bindings:DerivedDirectBusinessBindingsV2;readonly actions:DirectOperationActionsV2;
 readonly executable:PreparedDirectExecutableV2;readonly authority_effect:'none';
}
const directApplicationPreparations=new WeakSet<object>();
/** Source-to-Core preparation only. It requires original Core input custody;
 * it does not manufacture acceptance or call the legacy formal construction.
 * Open Questions: original joined graph witness at G01; native binding at U08. */
export function prepareDirectBusinessAuthoringApplicationV2(business:ResolvedBusinessSpecV2,input:AuthoringBusinessInputV2,core:DirectBusinessCoreSurfaceV2):PreparedDirectBusinessAuthoringApplicationV2 {
 const lowered=lowerDirectBusinessV2(business),bindings=deriveDirectBusinessApplicationBindingsV2(lowered),actions=deriveDirectBusinessApplicationActionsV2(bindings);
 const executable=prepareDirectApplicationExecutableV2(bindings,actions,input,core);
 const result=Object.freeze({kind:'prepared-direct-business-authoring-application-v2' as const,lowered,bindings,actions,executable,authority_effect:'none' as const});
 directApplicationPreparations.add(result);assertPreparedDirectBusinessAuthoringApplicationV2Current(result);return result;
}
export function assertPreparedDirectBusinessAuthoringApplicationV2Current(value:PreparedDirectBusinessAuthoringApplicationV2):void {
 if(!value||typeof value!=='object'||!directApplicationPreparations.has(value))throw Error('BUSINESS_DIRECT_PREPARATION_UNREGISTERED');
 assertLoweredDirectBusinessV2Current(value.lowered);assertPreparedDirectApplicationExecutableV2Current(value.executable);
 if(value.executable.bindings!==value.bindings||value.executable.actions!==value.actions||value.bindings.lowered!==value.lowered)throw Error('BUSINESS_DIRECT_PREPARATION_CORRESPONDENCE');
}
export type VersionedBusinessAuthoringPreparationRequest=
 |Readonly<{source_contract:'alchlang.business-spec/v2-candidate';business:ResolvedBusinessSpecV2;input:AuthoringBusinessInputV2;core:DirectBusinessCoreSurfaceV2}>
 |Readonly<{source_contract:'alchlang.business-spec/v1-candidate';accepted:AcceptedBusinessReviewDecision;requests:BusinessMaterializationRequestSurface;compiler:DomainSpecCompiler}>;
/** Explicit dispatch selects the successor before the claim-backed legacy branch. */
export function prepareVersionedBusinessAuthoringApplication(request:VersionedBusinessAuthoringPreparationRequest):PreparedDirectBusinessAuthoringApplicationV2|PreparedBusinessAuthoringApplication {
 if(request.source_contract==='alchlang.business-spec/v2-candidate')return prepareDirectBusinessAuthoringApplicationV2(request.business,request.input,request.core);
 if(request.source_contract==='alchlang.business-spec/v1-candidate')return prepareBusinessAuthoringApplication(request.accepted,request.requests,request.compiler);
 throw Error('BUSINESS_SOURCE_VERSION');
}
import {materializeAcceptedBusinessApplication,assertMaterializedBusinessApplicationCurrent,type MaterializedBusinessApplication,type BusinessMaterializationRequestSurface,type BusinessMaterializationEngine} from './business-authoring-carriers.js';
import type {AcceptedBusinessReviewDecision} from './business-authoring-review.js';
import {deriveBusinessApplicationBindings,assertDerivedBusinessApplicationCurrent} from './business-application-bindings.js';
import {deriveBusinessApplicationActions} from './business-application-actions.js';
import {compileApplicationExecutable} from './application-executable.js';
import type {DomainSpecCompiler,DomainSpecGraph} from './domainspec-cli.js';
import type {BusinessApplicationInput} from './business-application-protocol.js';
import {businessCanonical,businessHash,businessReject} from './business-authoring-model.js';

// B06.2 checked preparation only. Open questions: B07.2 request/API realization;
// docs/BUSINESS-AUTHORING-CONTRACTS.md owns the source-preview limitations.
interface Identity {readonly dev:bigint;readonly ino:bigint;readonly mode:bigint;readonly size:bigint;readonly mtime:bigint;readonly ctime:bigint}
interface Scratch {readonly root:string;readonly directories:ReadonlyMap<string,Identity>;readonly files:ReadonlyMap<string,Identity>;readonly expected:Readonly<Record<string,string>>}
export interface BusinessAuthoringApplicationLineage {
 readonly kind:'business-authoring-checked-lineage';readonly model_id:string;
 readonly original_business_source:Readonly<{path:string;sha256:string;bytes:number}>;
 readonly decision_record:Readonly<{path:string;sha256:string;bytes:number}>;
 readonly materialization_sha256:string;readonly generated_legacy_source_sha256:string;readonly generated_semantics_sha256:string;
 readonly checked_graph_manifest_sha256:string;readonly execution:'not-performed';readonly authority_effect:'none';
}
export interface PreparedBusinessAuthoringApplication {
 readonly kind:'prepared-business-authoring-application';readonly materialized:MaterializedBusinessApplication;
 readonly input:BusinessApplicationInput;readonly derived:ReturnType<typeof deriveBusinessApplicationBindings>;
 readonly actions:ReturnType<typeof deriveBusinessApplicationActions>;readonly workspace:string;readonly graph:DomainSpecGraph;
 readonly executable:ReturnType<typeof compileApplicationExecutable>;readonly lineage:BusinessAuthoringApplicationLineage;readonly authority_effect:'none';
}
type Owner={compiler:DomainSpecCompiler;materialized:MaterializedBusinessApplication;input:BusinessApplicationInput;scratch:Scratch;fingerprint:string};
const current=new WeakMap<object,Owner>();
function fail(message:string):never{return businessReject('BUSINESS_AUTHORING_PREPARATION','business.alch',1,1,message);}
const identity=(s:BigIntStats):Identity=>({dev:s.dev,ino:s.ino,mode:s.mode,size:s.size,mtime:s.mtimeNs,ctime:s.ctimeNs});
const sameNode=(a:Identity,b:Identity)=>a.dev===b.dev&&a.ino===b.ino&&a.mode===b.mode;
const sameFile=(a:Identity,b:Identity)=>sameNode(a,b)&&a.size===b.size&&a.mtime===b.mtime&&a.ctime===b.ctime;
const ownPath=fileURLToPath(import.meta.url);
const implementation=():string=>{
 const owners=()=>{let cursor=path.parse(ownPath).root;const values:string[]=[];
  for(const part of ['',...ownPath.slice(cursor.length).split(path.sep).filter(Boolean)]){if(part)cursor=path.join(cursor,part);const stat=lstatSync(cursor,{bigint:true});if(stat.isSymbolicLink())fail('implementation path symlink is forbidden');values.push(`${stat.dev}:${stat.ino}`);}return values;};
 const ancestry=owners(),before=lstatSync(ownPath,{bigint:true});if(!before.isFile()||before.size>16777216n)fail('bounded original regular preparation implementation required');
 const fd=openSync(ownPath,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK),parts:Buffer[]=[];let total=0;
 try{const opened=fstatSync(fd,{bigint:true});if(!opened.isFile()||!sameFile(identity(opened),identity(before)))fail('implementation changed while opening');
  for(;;){const buffer=Buffer.alloc(65536),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;total+=count;if(total>16777216)fail('implementation byte budget exceeded');parts.push(buffer.subarray(0,count));}
  if(!sameFile(identity(fstatSync(fd,{bigint:true})),identity(before)))fail('implementation changed during capture');
 }finally{closeSync(fd);}
 if(BigInt(total)!==before.size||!sameFile(identity(lstatSync(ownPath,{bigint:true})),identity(before))||businessCanonical(owners())!==businessCanonical(ancestry))fail('implementation path or ancestry changed');
 return businessHash(businessCanonical({ancestry,sha256:businessHash(Buffer.concat(parts)),mtime:String(before.mtimeNs),ctime:String(before.ctimeNs)}));
};
const executingImplementation=implementation();
function assertImplementation():void {if(implementation()!==executingImplementation)fail('preparation implementation changed');}
function relativeParts(relative:string):string[] {
 const parts=relative.split('/');if(!relative||path.isAbsolute(relative)||relative.includes('\\')||relative.includes('\0')||parts.length>16||parts.some(p=>!p||p==='.'||p==='..'))fail('bounded portable generated path required');return parts;
}
/** Descriptor-anchored effects stay in this newly owned Linux scratch inode. */
function populate(root:string,expected:Readonly<Record<string,string>>):Scratch {
 const directories=new Map<string,Identity>(),files=new Map<string,Identity>();
 const rootFd=openSync(root,constants.O_RDONLY|constants.O_DIRECTORY|constants.O_NOFOLLOW|constants.O_NONBLOCK);
 directories.set('',identity(fstatSync(rootFd,{bigint:true})));let total=0;
 try{
  const rows=Object.entries(expected);if(rows.length>10000)fail('generated file inventory exceeds budget');
  for(const [relative,body] of rows){
   const parts=relativeParts(relative),bytes=Buffer.from(body,'utf8');total+=bytes.length;if(total>64*1024*1024)fail('generated scratch exceeds byte budget');
   const opened:number[]=[];let parent=rootFd,prefix='';
   try{
    for(const part of parts.slice(0,-1)){
     prefix=prefix?prefix+'/'+part:part;const anchored=`/proc/self/fd/${parent}/${part}`;
     if(!directories.has(prefix))mkdirSync(anchored,{mode:0o700});
     const fd=openSync(anchored,constants.O_RDONLY|constants.O_DIRECTORY|constants.O_NOFOLLOW|constants.O_NONBLOCK);opened.push(fd);
     const stat=identity(fstatSync(fd,{bigint:true})),prior=directories.get(prefix);if(prior&&!sameNode(prior,stat))fail('generated parent directory was replaced');
     directories.set(prefix,stat);parent=fd;
    }
    const fd=openSync(`/proc/self/fd/${parent}/${parts.at(-1)!}`,constants.O_WRONLY|constants.O_CREAT|constants.O_EXCL|constants.O_NOFOLLOW|constants.O_NONBLOCK,0o600);
    try{let offset=0;while(offset<bytes.length){const count=writeSync(fd,bytes,offset,bytes.length-offset,null);if(count<=0)fail('complete generated-file write required');offset+=count;}files.set(relative,identity(fstatSync(fd,{bigint:true})));}finally{closeSync(fd);}
   }finally{for(const fd of opened.reverse())closeSync(fd);}
  }
 }finally{closeSync(rootFd);}
 const scratch={root,directories,files,expected};assertScratch(scratch);return scratch;
}
function scratchBytes(fd:number,expectedBytes:number):Buffer {
 const parts:Buffer[]=[];let total=0;
 for(;;){const buffer=Buffer.alloc(Math.min(65536,expectedBytes-total+1)),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;total+=count;if(total>expectedBytes)fail('scratch file grew beyond its exact captured byte budget');parts.push(buffer.subarray(0,count));}
 if(total!==expectedBytes)fail('scratch file byte count changed');return Buffer.concat(parts);
}
function assertScratch(scratch:Scratch):void {
 const foundFiles:string[]=[],foundDirectories:string[]=[];let bytes=0;
 const walk=(relative:string,depth:number):void=>{
  if(depth>16)fail('scratch depth exceeds budget');const directory=path.join(scratch.root,relative),stat=lstatSync(directory,{bigint:true}),expected=scratch.directories.get(relative);
  if(!stat.isDirectory()||stat.isSymbolicLink()||!expected||!sameNode(identity(stat),expected))fail('scratch directory ownership changed');foundDirectories.push(relative);
  for(const entry of readdirSync(directory,{withFileTypes:true})){
   const key=relative?relative+'/'+entry.name:entry.name;if(foundFiles.length+foundDirectories.length>12000)fail('scratch inventory exceeds budget');
   if(entry.isSymbolicLink())fail('scratch symlinks are forbidden');
   if(entry.isDirectory())walk(key,depth+1);
   else if(entry.isFile()){
    const physical=scratch.files.get(key),body=scratch.expected[key];if(!physical||body===undefined)fail('extra scratch file');
    const file=path.join(scratch.root,key),before=lstatSync(file,{bigint:true});if(!before.isFile()||before.isSymbolicLink()||!sameFile(identity(before),physical))fail('scratch file physical identity changed');
    bytes+=Number(before.size);if(bytes>64*1024*1024)fail('scratch byte budget exceeded');
    const fd=openSync(file,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);
    try{if(!sameFile(identity(fstatSync(fd,{bigint:true})),physical)||businessHash(scratchBytes(fd,Buffer.byteLength(body)))!==businessHash(body)||!sameFile(identity(fstatSync(fd,{bigint:true})),physical))fail('scratch file content changed');}finally{closeSync(fd);}
    if(!sameFile(identity(lstatSync(file,{bigint:true})),physical))fail('scratch path changed during verification');foundFiles.push(key);
   }else fail('scratch contains a nonregular entry');
  }
 };
 walk('',0);
 if(businessCanonical(foundFiles.sort())!==businessCanonical([...scratch.files.keys()].sort())||businessCanonical(foundDirectories.sort())!==businessCanonical([...scratch.directories.keys()].sort()))fail('scratch inventory differs');
 const root=lstatSync(scratch.root,{bigint:true});if(!root.isDirectory()||!sameNode(identity(root),scratch.directories.get('')!))fail('scratch root changed');
}
const fingerprint=(value:PreparedBusinessAuthoringApplication)=>businessHash(businessCanonical({execution:value.actions.execution,graph:value.graph,executable:value.executable,lineage:value.lineage}));

/** The compiler is the trusted public Core SDK, sharing the original registered handles. */
export function prepareBusinessAuthoringApplication(accepted:AcceptedBusinessReviewDecision,requests:BusinessMaterializationRequestSurface,compiler:DomainSpecCompiler):PreparedBusinessAuthoringApplication {
 assertImplementation();const engine=compiler.profileEngine,prepareInput=engine.prepareAuthoringBusinessInput,assertInput=engine.assertAuthoringBusinessInputCurrent;
 if(typeof prepareInput!=='function'||typeof assertInput!=='function')fail('build Core with the explicit authoring input owner before checked preparation');
 const materializationEngine=engine as unknown as BusinessMaterializationEngine;
 if(typeof materializationEngine.assertBusinessAuthoringRequestsCurrent!=='function'||typeof materializationEngine.validateBusinessApplication!=='function')fail('Core materialization capabilities required');
 const materialized=materializeAcceptedBusinessApplication(accepted,requests,materializationEngine);
 const input=prepareInput.call(engine,accepted.accepted,requests,materialized.compatibility),owned=input as BusinessApplicationInput&{kind?:string;accepted?:unknown;requests?:unknown};assertInput.call(engine,input);
 if(owned.kind!=='business-authoring-input'||owned.accepted!==accepted.accepted||owned.requests!==requests)fail('original v3 owner adapter correspondence required');
 const derived=deriveBusinessApplicationBindings(input,materialized.model_id,engine),actions=Object.freeze(deriveBusinessApplicationActions(input,derived,compiler));
 const workspace=mkdtempSync(path.join(os.tmpdir(),'alch-authoring-application-'));
 try{
  const scratch=populate(workspace,actions.prepared.projectFiles),graph=compiler.compileProject(workspace).graph,executable=compileApplicationExecutable(actions.prepared,graph,compiler);
  const business=accepted.prepared.preview.business;
  const lineage:BusinessAuthoringApplicationLineage=Object.freeze({kind:'business-authoring-checked-lineage',model_id:materialized.model_id,original_business_source:Object.freeze({path:business.source.path,sha256:business.source.sha256,bytes:business.source.bytes}),decision_record:accepted.decision.capture.file,materialization_sha256:materialized.materialization_sha256,generated_legacy_source_sha256:materialized.source_sha256,generated_semantics_sha256:materialized.semantics_sha256,checked_graph_manifest_sha256:graph.source_manifest.manifest_sha256,execution:'not-performed',authority_effect:'none'});
  const value=Object.freeze({kind:'prepared-business-authoring-application' as const,materialized,input,derived,actions,workspace,graph,executable,lineage,authority_effect:'none' as const});
  current.set(value,{compiler,materialized,input,scratch,fingerprint:fingerprint(value)});assertPreparedBusinessAuthoringApplicationCurrent(value);return value;
 }catch(error){if(error&&typeof error==='object'&&Object.isExtensible(error))Object.defineProperty(error,'scratch_path',{value:workspace,enumerable:true});throw error;}
}
export function assertPreparedBusinessAuthoringApplicationCurrent(value:PreparedBusinessAuthoringApplication):void {
 const state=value&&typeof value==='object'?current.get(value):undefined;if(!state)fail('original current checked preparation required; disposed/cloned handles reject');
 assertImplementation();assertMaterializedBusinessApplicationCurrent(state.materialized);state.compiler.profileEngine.assertAuthoringBusinessInputCurrent!(state.input);assertDerivedBusinessApplicationCurrent(value.derived);
 if(value.materialized!==state.materialized||value.input!==state.input||value.workspace!==state.scratch.root||fingerprint(value)!==state.fingerprint)fail('checked preparation data changed');
 assertScratch(state.scratch);state.compiler.profileEngine.assertBusinessApplicationPlanCurrent(value.graph,value.executable.plan);
}
/** Revoke this owner and preserve bounded scratch for inspection; never delete by a raced path. */
export function disposePreparedBusinessAuthoringApplication(value:PreparedBusinessAuthoringApplication):void {
 if(!value||typeof value!=='object'||!current.has(value))fail('original current preparation required for disposal');current.delete(value);
}
