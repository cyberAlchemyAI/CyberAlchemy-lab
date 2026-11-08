/** HTTP routing over original generated per-Entry handlers. No listener or Auth identity.
 * The service artifact owner must supply its privately checked inventory, runtime-bound
 * generated handlers, and a fresh inspection callback. This helper alone grants no custody.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import type {GenericFixtureActor} from './entry-authorization.js';
import type {GenericServiceArtifactManifest} from './service-artifact-owner.js';

const at={path:'generic-service-http-dispatch',start:0,end:0};
const hex=/^[0-9a-f]{64}$/;
type Handler=(request:Request,actor:GenericFixtureActor|null)=>Promise<Response>;
type EntryManifest=Readonly<{
 entry?:unknown;
 profile?:{sha256?:unknown};
 expanded?:{capture_sha256?:unknown;executable_semantics_sha256?:unknown};
 runtime_contract?:{http?:{method?:unknown;route?:unknown;routes?:unknown;identity?:unknown}};
}>;
export type GenericServiceHttpRouteBinding=Readonly<{entry:string;manifest:EntryManifest;handler:Handler}>;
export type GenericServiceHttpDispatch=(request:Request,actor?:GenericFixtureActor|null)=>Promise<Response>;

/** Internal composition boundary: only the artifact owner can attest that the
 * inventory, manifests, runtime, and generated handlers come from one accepted source. */
export function createGenericServiceHttpDispatch(input:{
 readonly service:string;
 readonly inventory:GenericServiceArtifactManifest;
 /** Physical selected-profile file SHA from the accepted source inspection.
  * The inventory's profile_sha256 is a distinct semantic derivation digest. */
 readonly selectedProfileFileSha256:string;
 readonly bindings:readonly GenericServiceHttpRouteBinding[];
 readonly inspectCurrent:()=>GenericServiceArtifactManifest;
}):GenericServiceHttpDispatch{
 if(!input||typeof input.service!=='string'||!input.service||!input.inventory||!hex.test(input.selectedProfileFileSha256)||
    !Array.isArray(input.bindings)||typeof input.inspectCurrent!=='function')
  fail('InvalidContract',at,'checked service HTTP inputs required');
 const inventory=input.inventory,service=inventory.services.find(row=>row.service===input.service);
 if(!service||inventory.services.filter(row=>row.service===input.service).length!==1||!hex.test(inventory.inventory_sha256)||
    !hex.test(inventory.source_capture_sha256)||!hex.test(inventory.profile_sha256)||!hex.test(inventory.executable_semantics_sha256))
  fail('InvalidContract',at,'one checked service and pinned application identities required');
 const expected=service.entries.filter(row=>row.interaction==='request-response'),entries=new Set<string>(),paths=new Map<string,{entry:string;handler:Handler}>();
 if(input.bindings.length!==expected.length)fail('MissingMapping',at,'every selected request-response Entry needs one generated HTTP handler');
 for(const binding of input.bindings){
  const row=service.entries.find(candidate=>candidate.entry===binding.entry);
  if(!row||row.interaction!=='request-response'||row.http_export!=='createGeneratedHttpHandler'||entries.has(binding.entry))
   fail('InvalidContract',at,'only one inventory-pinned request-response Entry may become an HTTP route');
  if(typeof binding.handler!=='function')fail('InvalidContract',at,'original generated HTTP handler required');
  const manifest=binding.manifest,http=manifest?.runtime_contract?.http;
  const route='/entries/'+binding.entry.replaceAll('.','/');
  if(manifest?.entry!==binding.entry||manifest.profile?.sha256!==input.selectedProfileFileSha256||
     manifest.expanded?.capture_sha256!==inventory.source_capture_sha256||
     manifest.expanded?.executable_semantics_sha256!==inventory.executable_semantics_sha256||
     http?.method!=='POST'||http.route!==route||http.identity!=='injected-original-runtime-actor'||
     http.routes!==undefined||!/^\/[A-Za-z0-9/_-]+$/.test(route))
   fail('InvalidContract',at,'generated Entry HTTP route/source/profile differs from checked service inventory');
  const key='POST '+route;
  if(paths.has(key))fail('InvalidContract',at,'ambiguous generated HTTP route');
  entries.add(binding.entry);paths.set(key,{entry:binding.entry,handler:binding.handler});
 }
 const inventoryDigest=dataDigest(inventory);
 const current=()=>{
  const now=input.inspectCurrent();
  if(dataDigest(now)!==inventoryDigest)fail('StaleOwner',at,'service HTTP inventory/source/profile changed');
 };
 current();
 const response=(status:number,code:string,extra:Record<string,string>={})=>new Response(JSON.stringify({kind:'adapter-error',code}),
  {status,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store',...extra}});
 return Object.freeze(async(request:Request,actor:GenericFixtureActor|null=null):Promise<Response>=>{
  current();
  if(!(request instanceof Request))return response(400,'invalid-request');
  let path:string;try{path=new URL(request.url).pathname;}catch{return response(400,'invalid-request');}
  const target=paths.get(request.method+' '+path);
  if(target)return target.handler(request,actor);
  if([...paths.keys()].some(key=>key.endsWith(' '+path)))return response(405,'method-not-allowed',{allow:'POST'});
  return response(404,'route-not-found');
 });
}
