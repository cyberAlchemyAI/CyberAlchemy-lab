/** Public, source-bound Workflow driver. Hosts supply paths and original
 * runtime/Auth resources; source/profile/compatibility bindings are derived.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {constants,closeSync,lstatSync,mkdirSync,openSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {DatabaseSync} from 'node:sqlite';
import {types as host} from 'node:util';
import {dataDigest,canonicalJson,type Json} from '../profile-engine/contracts.js';
import {coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {parseCoreCommerceJson} from '../commerce/commerce-core-source-owner.js';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import {requireGenericWorkflowRuntime,type GenericCompositionHandle} from './public-sdk.js';
import {assertGenericWorkflowRuntimeSource,assertGenericWorkflowReceiverSource} from './execution-session.js';
import type {GenericTransactionApplicationRuntime} from './invocation-owner.js';
import type {GenericFixtureActor} from './entry-authorization.js';
import {GenericWorkflowStore,type WorkflowClaim} from './workflow-store.js';
import {createGenericWorkflowWorker,workflowCompatibilitySha256} from './workflow-worker.js';
import type {GenericWorkflowStagePort} from './workflow-worker.js';

const at={path:'generic-workflow-driver',start:0,end:0};
const pin=pinCoreImplementation(import.meta.url,[]);
export interface GenericWorkflowDriverOptions {
 readonly runtime:GenericTransactionApplicationRuntime;
 readonly receiver?:GenericTransactionApplicationRuntime;
 readonly actors:ReadonlyMap<string,GenericFixtureActor>;
 readonly journal:Readonly<{directory:string;mode:'create'|'reopen'}>;
 readonly stagePorts?:ReadonlyMap<string,GenericWorkflowStagePort>;
}
function closedValues(value:unknown,names:readonly string[]):void{
 if(host.isProxy(value)||!value||typeof value!=='object'||Array.isArray(value)||
  Reflect.ownKeys(value).some(key=>typeof key!=='string'||!names.includes(key))||
  Reflect.ownKeys(value).length!==names.length||
  Object.values(Object.getOwnPropertyDescriptors(value)).some(d=>!d.enumerable||!Object.hasOwn(d,'value')))
  fail('InvalidContract',at,'closed plain Workflow resource options required');
}
export function openGenericWorkflowDriver(owner:unknown,handle:GenericCompositionHandle,options:GenericWorkflowDriverOptions){
 pin.assertCurrent();
 const binding=requireGenericWorkflowRuntime(owner,handle);
 binding.assertCurrent();
 closedValues(options,['runtime','actors','journal',...(Object.hasOwn(options,'receiver')?['receiver']:[]),...(Object.hasOwn(options,'stagePorts')?['stagePorts']:[])]);
 closedValues(options.journal,['directory','mode']);
 const {runtime,receiver}=options,{directory,mode}=options.journal;
 assertGenericWorkflowRuntimeSource(runtime,binding.contract);
 if(binding.contract.steps.some(s=>s.kind==='event-await')){
  if(!receiver)fail('InvalidContract',at,'original Event receiver required by selected Workflow');
  assertGenericWorkflowReceiverSource(runtime,receiver,binding.contract);
 }else if(receiver)fail('InvalidContract',at,'local-only Workflow does not select an Event receiver');
 if(typeof directory!=='string'||!path.isAbsolute(directory)||path.normalize(directory)!==directory||
  directory.length>4096||/[\u0000-\u001f\u007f]/.test(directory)||!['create','reopen'].includes(mode))
  fail('InvalidContract',at,'normalized absolute owned journal directory and create/reopen mode required');
 if(!(options.actors instanceof Map)||host.isProxy(options.actors)||options.actors.size>128)
  fail('InvalidContract',at,'bounded original Entry actor map required');
 const actors=new Map(options.actors);
 const source=binding.contract,compatibility=workflowCompatibilitySha256(source);
 const storeId='workflow-'+dataDigest({service:source.service,workflow:source.workflow});
 // create owns a new private directory; reopen never creates a missing journal.
 if(mode==='create')mkdirSync(directory,{mode:0o700});
 const directoryStat=lstatSync(directory,{bigint:true});
 if(!directoryStat.isDirectory()||directoryStat.isSymbolicLink()||realpathSync(directory)!==directory||
  (process.platform!=='win32'&&(directoryStat.mode&0o077n)!==0n))
  fail('InvalidContract',at,'original private canonical journal directory required');
 const file=path.join(directory,'workflow.sqlite');
 if(mode==='create'){
  const fd=openSync(file,constants.O_CREAT|constants.O_EXCL|constants.O_RDWR|constants.O_NOFOLLOW,0o600);closeSync(fd);
 }
 const fileStat=lstatSync(file,{bigint:true});
 if(!fileStat.isFile()||fileStat.isSymbolicLink()||fileStat.nlink!==1n)
  fail('InvalidContract',at,'one original regular journal file required');
 const pathCurrent=()=>{
  try{
   pin.assertCurrent();
   const parent=lstatSync(directory,{bigint:true}),actual=lstatSync(file,{bigint:true});
   if(realpathSync(directory)!==directory||parent.dev!==directoryStat.dev||parent.ino!==directoryStat.ino||
    parent.mode!==directoryStat.mode||actual.dev!==fileStat.dev||actual.ino!==fileStat.ino||
    actual.mode!==fileStat.mode||actual.nlink!==1n||!actual.isFile()||actual.isSymbolicLink())
    fail('StaleOwner',at,'original Workflow journal path was replaced');
  }catch{return fail('StaleOwner',at,'original Workflow journal path is unavailable or replaced');}
 };
 const owned={store_id:storeId,owner_service:source.service,compatibility_sha256:compatibility};
 // Probe an existing journal read-only. Foreign, incomplete or incompatible
 // databases cannot be initialized or repaired as a side effect of reopen.
 if(mode==='reopen'){
  pathCurrent();
  const probe=new DatabaseSync(file,{readOnly:true});
  try{new GenericWorkflowStore(probe,owned);}finally{probe.close();}
  pathCurrent();
 }
 const db=new DatabaseSync(file);
 let closed=false,closing=false,closePromise:Promise<void>|undefined;
 const active=new Set<Promise<unknown>>();
 try{
  pathCurrent();
  const journal=new GenericWorkflowStore(db,owned,pathCurrent);
  if(options.stagePorts&&(!(options.stagePorts instanceof Map)||host.isProxy(options.stagePorts)||options.stagePorts.size>64))fail('InvalidContract',at,'bounded original stage port map required');
  const worker=createGenericWorkflowWorker({source,runtime,...(receiver?{receiver}:{}),actors,journal,journal_store_id:storeId,...(options.stagePorts?{stagePorts:options.stagePorts}:{})});
  const current=()=>{
   if(closed||closing)fail('DisposedOwner',at,'Workflow driver is closing or closed');
   binding.assertCurrent();pathCurrent();
   assertGenericWorkflowRuntimeSource(runtime,source);
   if(receiver)assertGenericWorkflowReceiverSource(runtime,receiver,source);
   journal.assertOwner(owned);
  };
  const run=<T>(action:()=>Promise<T>):Promise<T>=>{
   current();
   const pending=Promise.resolve().then(action);active.add(pending);
   void pending.then(()=>active.delete(pending),()=>active.delete(pending));
   return pending;
  };
  return Object.freeze({
   inspectDefinition(){current();return Object.freeze({workflow:source.workflow,service:source.service,
    source_closure_sha256:source.source_closure_sha256,profile_sha256:source.profile_sha256,
    compatibility_sha256:compatibility,journal_path:file});},
   scheduleStart(input:Uint8Array,clientKey:string){
    return run(async()=>{
     if(host.isProxy(input)||!(input instanceof Uint8Array)||input.byteLength>1048576)
      fail('InvalidContract',at,'bounded Workflow input bytes required');
     let text:string;
     try{text=new TextDecoder('utf-8',{fatal:true}).decode(input);}catch{return fail('InvalidContract',at,'Workflow input must be UTF-8');}
     const value=parseCoreCommerceJson(text,'workflow-input.json') as Json;
     return worker.scheduleStart(canonicalJson(value),clientKey);
    });
   },
   claimNext(leaseMs:number){current();return worker.claimNext(leaseMs);},
   renewClaim(claim:WorkflowClaim,leaseMs:number){current();return worker.renewClaim(claim,leaseMs);},
   advance(claim:WorkflowClaim){return run(()=>worker.advance(claim));},
   inspect(instance:string){current();return worker.inspect(instance);},
   close():Promise<void>{
    if(closePromise)return closePromise;
    closing=true;
    closePromise=(async()=>{await Promise.allSettled([...active]);try{db.close();}finally{closed=true;}})();
    return closePromise;
   }
  });
 }catch(error){db.close();throw error;}
}
export type GenericWorkflowDriver=ReturnType<typeof openGenericWorkflowDriver>;
