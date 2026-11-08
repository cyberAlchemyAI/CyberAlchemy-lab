import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createProfileFixture,useShippedProfile} from './profile-fixture.js';
import {prepareProfileProject,generateProfileProject,disposeProfileProject} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/profile-engine.js';
// Independent API failure expectations. Open questions: application composition PE14.
test('first public service retains independent behavior and external/input failure boundaries',async t=>{
 const f=useShippedProfile(createProfileFixture(t)),prepared=await prepareProfileProject(path.join(f.root,'project.json'));t.after(()=>disposeProfileProject(prepared));const output=path.join(f.root,'output');generateProfileProject(prepared,output);const service=await import(pathToFileURL(path.join(output,'app/index.mjs')).href);
 const request=(input:any,method='POST',headers={'content-type':'application/json'})=>new Request('https://test.invalid/requestQuote',{method,headers,body:JSON.stringify(input)}),input={request_id:'R1',sku:'S1',quantity:3},env={DEPENDENCY_INVENTORY_URL:'https://inventory.invalid/stock'};
 let calls=0;const fetch=async()=>{calls++;return new Response('{"sku":"S1","stock":5,"unit_price_minor":1250}');};
 const oracle=JSON.parse(readFileSync(path.join(f.root,'oracle.json'),'utf8'));
 for(const c of oracle.cases){const result=await service.handler(new Request('https://test.invalid/'+c.intent,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(c.input)}),env,{fetch:async()=>new Response(JSON.stringify(c.external))});const body=await result.json();if(c.expected_error)assert.equal(body.error,c.expected_error,c.id);else assert.deepEqual(body,c.expected,c.id);}
 const cases:[string,any,number,string][]=[
  ['missing environment',{},503,'FUNCTION_ENV_REQUIRED'],
  ['remote HTTP failure',{fetch:async()=>new Response('{}',{status:503})},502,'FUNCTION_INTEGRATION_STATUS'],
  ['malformed JSON',{fetch:async()=>new Response('invalid')},502,'FUNCTION_INTEGRATION_SCHEMA'],
  ['wrong wire type',{fetch:async()=>new Response('{"sku":"S1","stock":"wrong","unit_price_minor":1250}')},502,'FUNCTION_INTEGRATION_SCHEMA'],
  ['extra wire field',{fetch:async()=>new Response('{"sku":"S1","stock":5,"unit_price_minor":1250,"hidden":true}')},502,'FUNCTION_INTEGRATION_SCHEMA'],
  ['response byte limit',{fetch:async()=>new Response('x'.repeat(9000))},502,'FUNCTION_INTEGRATION_LIMIT'],
  ['remote deadline',{fetch:async(_url:any,options:any)=>new Promise((_resolve,reject)=>options.signal.addEventListener('abort',()=>reject(Error('aborted')),{once:true}))},504,'FUNCTION_INTEGRATION_TIMEOUT'],
 ];
 for(const [name,io,status,error]of cases){const response=await service.handler(request(input),name==='missing environment'?{}:env,io);assert.equal(response.status,status,name);assert.equal((await response.json()).error,error,name);}
 const invalid=await service.handler(request({...input,quantity:0}),env,{fetch});assert.equal(invalid.status,400);assert.equal(calls,0);
 const wrongMethod=await service.handler(request(input,'PUT'),env,{fetch});assert.equal(wrongMethod.status,405);assert.equal(calls,0);
 const controller=new AbortController();controller.abort();const cancelled=await service.handler(request(input),env,{fetch,signal:controller.signal});assert.equal((await cancelled.json()).error,'FUNCTION_CANCELLED');assert.equal(calls,0);
});
test('single-entry and invented public behavior reject before output creation',async t=>{
 for(const mode of ['single','invented']){const f=createProfileFixture(t),file=path.join(f.root,'project.json'),project=JSON.parse(readFileSync(file,'utf8'));if(mode==='single')project.public_intents.pop();else project.public_intents[1].result_ref='InventedResult';writeFileSync(file,JSON.stringify(project));await assert.rejects(()=>prepareProfileProject(file),/PROFILE_SCHEMA_|PROFILE_PUBLIC_INTENT_UNKNOWN_REF/);}
});
