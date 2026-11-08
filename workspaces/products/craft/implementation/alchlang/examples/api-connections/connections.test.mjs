// Open Questions: README.md and ../../docs/API-CONNECTIONS.md.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createFindHttpHandler,createExampleFindService,createFindHttpClient} from './connections.mjs';

export async function runApiConnections({generatedRoot,exampleRoot}) {
  const root=path.resolve(generatedRoot); const files=fs.readdirSync(root,{recursive:true}).map(String);
  const load=async suffix=>{const candidates=files.filter(file=>file.split(path.sep).join('/').endsWith(suffix));assert.equal(candidates.length,1,'exact generated module: '+suffix);return import(pathToFileURL(path.join(root,candidates[0])).href);};
  const [api,summary,commerceTotal,billingTotal]=await Promise.all([
    load('features/commerce/src/application/interfaces/api.js'),
    load('features/commerce/src/application/mappings/summary.js'),
    load('features/commerce/src/domain/calculations/total.js'),
    load('features/billing/src/domain/calculations/total.js'),
  ]);
  const {order}=JSON.parse(fs.readFileSync(path.join(exampleRoot,'values.json'),'utf8'));
  const observations=[]; const check=async(id,fn)=>{await fn();observations.push({id,result:'pass'});};
  const headers={'x-interface-version':'1.0.0'}; const request={method:'POST',path:'/orders/find',headers,body:'"1"'};
  let serviceCalls=0,transportCalls=0;
  const nativeService=createExampleFindService({summary,commerceTotal,billingTotal,order});
  const service={async find(id){serviceCalls++;return nativeService.find(id);}};
  const handler=createFindHttpHandler({api,service});
  await check('inbound-generated-calculation-mapping-interface',async()=>{
    const response=await handler(request);assert.equal(response.status,200);assert.deepEqual(JSON.parse(response.body),{id:'1',net:'93',fee:'5'});assert.equal(serviceCalls,1);
  });
  await check('invalid-request-version-route-zero-service-calls',async()=>{
    const before=serviceCalls;
    for(const [edit,status] of [[{body:'"bad"'},400],[{body:'{"id":"1"}'},400],[{body:'garbage'},400],[{headers:{'x-interface-version':'2.0.0'}},409],[{method:'GET'},404],[{path:'/different'},404]])assert.equal((await handler({...request,...edit})).status,status);
    assert.equal(serviceCalls,before);
  });
  await check('invalid-service-result-and-missing-service-value',async()=>{
    const broken=createFindHttpHandler({api,service:{async find(){return {id:'1',net:'93'};}}});assert.equal((await broken(request)).status,502);
    assert.equal((await handler({...request,body:'"2"'})).status,404);
  });
  const fetchImpl=async(url,init)=>{transportCalls++;assert.equal(url,'https://example.invalid/orders/find');assert.ok(init.signal instanceof AbortSignal);const response=await handler({method:init.method,path:new URL(url).pathname,headers:init.headers,body:init.body});return new Response(response.body,{status:response.status,headers:response.headers});};
  const client=createFindHttpClient({api,baseUrl:'https://example.invalid',fetchImpl});
  await check('outbound-injected-transport-to-inbound-handler',async()=>{
    const result=await client.find('1');assert.deepEqual(result,{id:1n,net:93n,fee:5n});assert.ok(Object.isFrozen(result));assert.equal(transportCalls,1);
  });
  await check('outbound-invalid-request-zero-fetch-calls',async()=>{
    const before=transportCalls;await assert.rejects(()=>client.find('bad'),/INTERFACE_VALUE/);assert.equal(transportCalls,before);
    assert.throws(()=>createFindHttpClient({api,baseUrl:'https://example.invalid',fetchImpl,version:'2.0.0'}),/UNSUPPORTED_INTERFACE_VERSION/);
    assert.equal(transportCalls,before);
  });
  await check('outbound-http-content-type-shape-and-byte-failures',async()=>{
    for(const [response,expected] of [[new Response('{}',{status:503,headers:{'content-type':'application/json'}}),/REMOTE_HTTP_503/],[new Response('{}',{headers:{'content-type':'text/plain'}}),/REMOTE_CONTENT_TYPE/],[new Response('{"id":"1","net":"93"}',{headers:{'content-type':'application/json'}}),/INTERFACE_VALUE/],[new Response(' '.repeat(65537),{headers:{'content-type':'application/json'}}),/REMOTE_RESPONSE_BOUND/]]) {
      const broken=createFindHttpClient({api,baseUrl:'https://example.invalid',fetchImpl:async()=>response});await assert.rejects(()=>broken.find('1'),expected);
    }
  });
  await check('outbound-timeout-observed-by-supplied-transport',async()=>{
    const timed=createFindHttpClient({api,baseUrl:'https://example.invalid',timeoutMs:5,fetchImpl:async(_url,{signal})=>new Promise((_resolve,reject)=>signal.addEventListener('abort',()=>reject(new Error('ABORTED')),{once:true}))});
    await assert.rejects(()=>timed.find('1'),/ABORTED/);
  });
  await check('exact-large-uint64-id-roundtrip',async()=>{
    const largeOrder={...order,id:'9007199254740993'};
    const largeService=createExampleFindService({summary,commerceTotal,billingTotal,order:largeOrder});
    const largeHandler=createFindHttpHandler({api,service:largeService});
    const response=await largeHandler({...request,body:'"9007199254740993"'});assert.equal(response.status,200);assert.equal(JSON.parse(response.body).id,'9007199254740993');
    assert.throws(()=>api.endpointValues.find.request.normalize(9007199254740992),/INTERFACE_VALUE/);
  });
  assert.equal(api.descriptor.transport_execution,'not-performed');
  return {schema_version:'alchlang.api-connection-witness/v1-candidate',result:'pass',observations,generated_root:root,interface_selector:api.descriptor.selector,interface_source:api.descriptor.source,transport:'handwritten HTTP-shaped handler and injectable fetch client; in-memory Response only',network_calls:0,listeners:0,authority_effect:'none',open_questions:['Own-host authentication, authorization, persistence and external provider integration require separate selected bindings and tests.']};
}

if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const args=process.argv.slice(2);if(args.length!==4||args[0]!=='--generated-root'||args[2]!=='--example-root')throw Error('Usage: node connections.test.mjs --generated-root <compiled-generated-dir> --example-root <Craft reconciled-commerce-dir>');
  console.log(JSON.stringify(await runApiConnections({generatedRoot:args[1],exampleRoot:args[3]}),null,2));
}
