/** Source-selected presentation overlay over original generated application owners.
 * Open Questions: docs/ERROR-PRESENTATION.md#open-questions. */
import {mkdirSync,readFileSync,readdirSync,writeFileSync,lstatSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {dataDigest,captureJson} from './contracts.js';
import {readCorePhysicalFile,pinCorePhysicalCaptures} from '../commerce/commerce-core-physical.js';
import {coreRelativePath} from '../commerce/commerce-core-syntax.js';
import {createTechnicalProfileSourceOwner,type CheckedTechnicalProfileSource} from './technical-profile-source.js';
import {requireGenericCompositionRuntime,createGenericBundledApplicationOwner,type GenericCompositionHandle} from '../generic/public-sdk.js';
import {createGenericErrorPresentationBinding,inspectGenericErrorPresentation,assertGenericErrorPresentationRuntime,renderGenericPlatformError} from '../generic/error-presentation.js';
import {createGenericHttpHandler} from '../generic/http-adapter.js';
import {createGenericEntryHttpHandler,type GenericHttpEntryConfig} from '../generic/http-entry.js';
import type {GenericTransactionApplicationRuntime,GenericRuntimeOptions} from '../generic/invocation-owner.js';
function inventory(root:string,relative=''):ReturnType<typeof readCorePhysicalFile>[] {const all:ReturnType<typeof readCorePhysicalFile>[]=[];for(const name of readdirSync(path.join(root,relative)).sort()){const rel=path.posix.join(relative,name),file=path.join(root,rel),stat=lstatSync(file);if(stat.isSymbolicLink())throw Error('ERROR_PRESENTATION_PHYSICAL_OUTPUT');if(stat.isDirectory())all.push(...inventory(root,rel));else if(stat.isFile())all.push(readCorePhysicalFile(file));else throw Error('ERROR_PRESENTATION_REGULAR_OUTPUT');if(all.length>512)throw Error('ERROR_PRESENTATION_OUTPUT_BOUND');}return all;}
export function createTechnicalErrorPresentationApplicationOwner(input:{sourceOwner:ReturnType<typeof createTechnicalProfileSourceOwner>;sourceHandle:CheckedTechnicalProfileSource;sdk:{generate:(handle:GenericCompositionHandle,request:{entry:string;outputDirectory:string})=>unknown};application:GenericCompositionHandle}){
 const binding=createGenericErrorPresentationBinding({sourceOwner:input.sourceOwner,sourceHandle:input.sourceHandle,businessOwner:input.sdk,businessHandle:input.application});
 return Object.freeze({emit({entry,outputDirectory}:{entry:string;outputDirectory:string}){
  const selected=inspectGenericErrorPresentation(binding);if(!selected.entries.includes(entry))throw Error('ERROR_PRESENTATION_ENTRY_NOT_SELECTED');
  const original=requireGenericCompositionRuntime(input.sdk,input.application);original.assertCurrent();mkdirSync(outputDirectory);
  input.sdk.generate(input.application,{entry,outputDirectory:path.join(outputDirectory,'application')});
  input.sourceOwner.publishSelection(input.sourceHandle,path.join(outputDirectory,'error-profile'));
  const table=input.sourceOwner.inspectErrorPresentation(input.sourceHandle);writeFileSync(path.join(outputDirectory,'error-table.json'),JSON.stringify(table,null,2)+'\n',{flag:'wx'});
  const system=JSON.parse(readFileSync(path.join(outputDirectory,'application/system-graph.json'),'utf8')),bridge=JSON.parse(readFileSync(path.join(outputDirectory,'application/business-system-bridge.json'),'utf8'));
  const node={id:'error-presentation:'+table.presentation_version,kind:'source-selected-error-presentation',artifact:'error-table.json',producer:table.producer,reason_type:table.reason_type,source:table.source};system.nodes.push(node);system.edges.push(...selected.entries.map(entry=>({from:node.id,to:'entry:'+entry,kind:'presents-rejected-outcome',entry})).filter(e=>system.nodes.some((n:any)=>n.id===e.to)));bridge.links.push(...selected.entries.map(entry=>({business:entry,system:node.id,operation:table.producer,source:table.source,presentation_version:table.presentation_version})));
  for(const [name,value]of [['system-graph.json',system],['business-system-bridge.json',bridge]] as const)writeFileSync(path.join(outputDirectory,name),JSON.stringify(value,null,2)+'\n',{flag:'wx'});
  writeFileSync(path.join(outputDirectory,'application.mjs'),"import {createErrorPresentedBundledApplicationOwner} from '@domainspec-v2/cli/generic';\nexport function createGeneratedApplicationOwner(){return createErrorPresentedBundledApplicationOwner(import.meta.url);}\n",{flag:'wx'});
  const files=inventory(outputDirectory).map(f=>({path:path.relative(outputDirectory,f.file.path).split(path.sep).join('/'),sha256:f.file.sha256,bytes:f.file.bytes}));
  const manifest={schema_version:'craft.error-presented-application/v1',entry,presentation_version:table.presentation_version,selection:'error-profile/selection.json',original:'application/application.mjs',files,authority_effect:'none'};
  original.assertCurrent();input.sourceOwner.assertCurrent(input.sourceHandle);writeFileSync(path.join(outputDirectory,'error-application.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});return manifest;
 }});
}
/** Reopen actual captured source and original generated app; tables are never trusted as raw JSON. */
export function createErrorPresentedBundledApplicationOwner(moduleUrl:string){
 const url=new URL(moduleUrl);if(url.protocol!=='file:')throw Error('ERROR_PRESENTATION_FILE_REQUIRED');const directory=path.dirname(fileURLToPath(url)),manifestFile=readCorePhysicalFile(path.join(directory,'error-application.json')),manifest=JSON.parse(manifestFile.text);
 if(manifest.schema_version!=='craft.error-presented-application/v1'||manifest.original!=='application/application.mjs'||manifest.selection!=='error-profile/selection.json'||!Array.isArray(manifest.files)||!manifest.files.length||manifest.files.length>512)throw Error('ERROR_PRESENTATION_MANIFEST');
 const seen=new Set<string>();const captures=[manifestFile];for(const f of manifest.files){if(!coreRelativePath(f.path)||seen.has(f.path)||!/^[a-f0-9]{64}$/.test(f.sha256)||!Number.isSafeInteger(f.bytes))throw Error('ERROR_PRESENTATION_FILE_IDENTITY');seen.add(f.path);const actual=readCorePhysicalFile(path.join(directory,f.path));if(actual.file.sha256!==f.sha256||actual.file.bytes!==f.bytes)throw Error('ERROR_PRESENTATION_OUTPUT_CHANGED');captures.push(actual);}
 for(const required of ['application.mjs',manifest.original,manifest.selection,'error-table.json','system-graph.json','business-system-bridge.json'])if(!seen.has(required))throw Error('ERROR_PRESENTATION_INCOMPLETE_OUTPUT');
 const physical=pinCorePhysicalCaptures(captures),handles=new WeakMap<object,{sdk:any;source:ReturnType<typeof createTechnicalProfileSourceOwner>;selected:CheckedTechnicalProfileSource;binding?:ReturnType<typeof createGenericErrorPresentationBinding>}>();
 const current=(handle:GenericCompositionHandle)=>{physical.assertCurrent();const r=handles.get(handle);if(!r)throw Error('ERROR_PRESENTATION_FOREIGN_HANDLE');r.sdk.assertCurrent(handle);r.source.assertCurrent(r.selected);return r;};
 return Object.freeze({async prepare(){physical.assertCurrent();const inner=path.join(directory,manifest.original),text=readCorePhysicalFile(inner).text,start=text.indexOf('const bundle='),end=text.lastIndexOf(';\nexport function createGeneratedApplicationOwner()');if(start<0||end<=start)throw Error('ERROR_PRESENTATION_ORIGINAL_BUNDLE_REQUIRED');const sdk=createGenericBundledApplicationOwner(pathToFileURL(inner).href,JSON.parse(text.slice(start+'const bundle='.length,end))),handle=await sdk.prepare(),source=createTechnicalProfileSourceOwner(),selected=source.prepareCompiled(path.join(directory,manifest.selection));if(source.inspectErrorPresentation(selected).presentation_version!==manifest.presentation_version)throw Error('ERROR_PRESENTATION_IDENTITY_CHANGED');handles.set(handle,{sdk,source,selected});return handle;},
  review(handle:GenericCompositionHandle,label:string){return current(handle).sdk.review(handle,label);},
  accept(handle:GenericCompositionHandle,request:any,file:string){const r=current(handle),result=r.sdk.accept(handle,request,file);r.binding=createGenericErrorPresentationBinding({sourceOwner:r.source,sourceHandle:r.selected,businessOwner:r.sdk,businessHandle:handle});return result;},
  inspect(handle:GenericCompositionHandle){const r=current(handle);return {...r.sdk.inspect(handle),error_presentation:r.binding?inspectGenericErrorPresentation(r.binding):r.source.inspectErrorPresentation(r.selected)};},
  assertCurrent(handle:GenericCompositionHandle){current(handle);},
  openRuntime(handle:GenericCompositionHandle,options:GenericRuntimeOptions){return current(handle).sdk.openRuntime(handle,options);},
  bindHttp(handle:GenericCompositionHandle,runtime:GenericTransactionApplicationRuntime,routeId:string){const r=current(handle);if(!r.binding)throw Error('ERROR_PRESENTATION_ACCEPTANCE_REQUIRED');return createGenericHttpHandler(r.sdk,handle,runtime,routeId,{errorPresentation:r.binding});},
  bindEntryHttp(handle:GenericCompositionHandle,runtime:GenericTransactionApplicationRuntime,config:GenericHttpEntryConfig){const r=current(handle);if(!r.binding)throw Error('ERROR_PRESENTATION_ACCEPTANCE_REQUIRED');return createGenericEntryHttpHandler(runtime,{...config,errorPresentation:r.binding});},
  bindServiceHttp(handle:GenericCompositionHandle,runtime:GenericTransactionApplicationRuntime,options:{service:string}){
   if(!options||Object.keys(options).join(',')!=='service'||typeof options.service!=='string')throw Error('ERROR_PRESENTATION_SERVICE_OPTIONS');const r=current(handle);if(!r.binding)throw Error('ERROR_PRESENTATION_ACCEPTANCE_REQUIRED');assertGenericErrorPresentationRuntime(r.binding,runtime);
   const inspected=r.sdk.inspect(handle),contract=inspected.http_contract;if(!contract)throw Error('ERROR_PRESENTATION_CHECKED_HTTP_ROUTES_REQUIRED');
   const routes=contract.entries.filter((entry:any)=>entry.route.service===options.service).map((entry:any)=>{runtime.entry(entry.route.entry);return {id:entry.route.id,method:entry.route.method,path:(contract.profile.route_prefix+entry.route.path).split('/'),handler:createGenericHttpHandler(r.sdk,handle,runtime,entry.route.id,{errorPresentation:r.binding!})};});if(!routes.length)throw Error('ERROR_PRESENTATION_SERVICE_ROUTES_REQUIRED');
   const matching=(a:string[],b:string[])=>a.length===b.length&&a.every((v,i)=>v.startsWith('{')&&v.endsWith('}')?!!b[i]:v===b[i]);
   const dispatch=async(request:Request)=>{current(handle);runtime.assertCurrent();if(!(request instanceof Request))return renderGenericPlatformError('MalformedRequest',400);let parts:string[];try{parts=new URL(request.url).pathname.split('/');}catch{return renderGenericPlatformError('MalformedRequest',400);}const candidates=routes.filter((row:any)=>matching(row.path,parts)),selected=candidates.find((row:any)=>row.method===request.method);if(selected)return selected.handler(request);if(candidates.length){const response=renderGenericPlatformError('MethodNotAllowed',405);response.headers.set('allow',[...new Set(candidates.map((row:any)=>row.method))].sort().join(', '));return response;}return renderGenericPlatformError('RouteNotFound',404);};
   return Object.freeze(Object.assign(dispatch,{handlerForRoute:(id:string)=>{current(handle);const route=routes.find((row:any)=>row.id===id);if(!route)throw Error('ERROR_PRESENTATION_ROUTE_REQUIRED');return route.handler;}}));
  },
  originalBinding(handle:GenericCompositionHandle){const r=current(handle);return {sdk:r.sdk,handle,errorPresentation:r.binding};},
  dispose(handle:GenericCompositionHandle){const r=current(handle);r.source.dispose(r.selected);r.sdk.dispose(handle);handles.delete(handle);},
 });
}
