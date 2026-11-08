import test from 'node:test';
import assert from 'node:assert/strict';
import {createGenericServiceHttpDispatch} from '../../src/generic/service-http-dispatch.ts';
import type {GenericServiceArtifactManifest} from '../../src/generic/service-artifact-owner.ts';

const hash=(letter:string)=>letter.repeat(64);
const identities={inventory_sha256:hash('a'),source_capture_sha256:hash('b'),profile_sha256:hash('c'),executable_semantics_sha256:hash('d')};
const selectedProfileFileSha256=hash('e');
const entry=(id:string,service:string,interaction:'request-response'|'event')=>({entry:id,service,interaction,
 http_export:interaction==='request-response'?'createGeneratedHttpHandler':null});
const inventory=Object.freeze({...identities,services:[
 {service:'Orders',entries:[entry('Orders.Create','Orders','request-response'),entry('Orders.Notify','Orders','event')]},
 {service:'Billing',entries:[entry('Billing.Read','Billing','request-response')]},
]}) as unknown as GenericServiceArtifactManifest;
const generated=(id:string,overrides:Record<string,unknown>={})=>({
 entry:id,profile:{sha256:selectedProfileFileSha256},expanded:{capture_sha256:identities.source_capture_sha256,
  executable_semantics_sha256:identities.executable_semantics_sha256},
 runtime_contract:{http:{method:'POST',route:'/entries/'+id.replaceAll('.','/'),identity:'injected-original-runtime-actor'}},
 ...overrides,
});
const binding=(id:string,calls:{entry:string;actor:unknown}[])=>({entry:id,manifest:generated(id),
 handler:async(_request:Request,actor:unknown)=>{calls.push({entry:id,actor});return new Response(id,{status:202});}});
const diagnostic=(code:string)=>(error:unknown)=>(error as {diagnostics?:{code:string}[]}).diagnostics?.[0]?.code===code;

test('dispatches only checked service routes and forwards the original actor to its generated handler',async()=>{
 const calls:{entry:string;actor:unknown}[]=[],actor={kind:'opaque-original-actor'};
 const dispatch=createGenericServiceHttpDispatch({service:'Orders',inventory,selectedProfileFileSha256,bindings:[binding('Orders.Create',calls)] as any,
  inspectCurrent:()=>inventory});
 const request=new Request('https://example.invalid/entries/Orders/Create',{method:'POST',headers:{authorization:'Bearer forged'}});
 const returned=await dispatch(request,actor as any);
 assert.equal(returned.status,202);assert.equal(await returned.text(),'Orders.Create');
 assert.deepEqual(calls,[{entry:'Orders.Create',actor}]);
 const absent=await dispatch(new Request('https://example.invalid/entries/Billing/Read',{method:'POST'}));
 assert.equal(absent.status,404);
 const method=await dispatch(new Request('https://example.invalid/entries/Orders/Create',{method:'GET'}));
 assert.equal(method.status,405);assert.equal(method.headers.get('allow'),'POST');
 assert.equal(calls.length,1);
});

test('rejects Event routes, missing handlers, and mismatched source/profile/HTTP metadata',()=>{
 const calls:{entry:string;actor:unknown}[]=[],base={service:'Orders',inventory,selectedProfileFileSha256,inspectCurrent:()=>inventory};
 assert.throws(()=>createGenericServiceHttpDispatch({...base,bindings:[]}),diagnostic('MissingMapping'));
 assert.throws(()=>createGenericServiceHttpDispatch({...base,bindings:[binding('Orders.Notify',calls)] as any}),diagnostic('InvalidContract'));
 assert.throws(()=>createGenericServiceHttpDispatch({...base,bindings:[{...binding('Orders.Create',calls),
  manifest:generated('Orders.Create',{profile:{sha256:hash('f')}})}] as any}),diagnostic('InvalidContract'));
 assert.throws(()=>createGenericServiceHttpDispatch({...base,selectedProfileFileSha256:hash('f'),
  bindings:[binding('Orders.Create',calls)] as any}),diagnostic('InvalidContract'));
 assert.throws(()=>createGenericServiceHttpDispatch({...base,bindings:[{...binding('Orders.Create',calls),
  manifest:generated('Orders.Create',{expanded:{capture_sha256:hash('f'),executable_semantics_sha256:identities.executable_semantics_sha256}})}] as any}),diagnostic('InvalidContract'));
 assert.throws(()=>createGenericServiceHttpDispatch({...base,bindings:[{...binding('Orders.Create',calls),
  manifest:generated('Orders.Create',{runtime_contract:{http:{routes:[],identity:'injected-original-runtime-actor'}}})}] as any}),diagnostic('InvalidContract'));
});

test('rechecks the original inventory before every dispatch',async()=>{
 const calls:{entry:string;actor:unknown}[]=[],base={service:'Orders',inventory,selectedProfileFileSha256,bindings:[binding('Orders.Create',calls)] as any};
 let current=inventory;
 const dispatch=createGenericServiceHttpDispatch({...base,inspectCurrent:()=>current});
 current={...inventory,profile_sha256:hash('f')} as GenericServiceArtifactManifest;
 await assert.rejects(()=>dispatch(new Request('https://example.invalid/entries/Orders/Create',{method:'POST'})),diagnostic('StaleOwner'));
 assert.equal(calls.length,0);
});
