import test from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {createGenericDemoPayFetchPort} from '../../src/generic/service-provider-port.ts';

test('C14 generated service provider port sends the checked DemoPay request to configured transport',async()=>{
 const seen=[];
 const server=createServer(async(request,response)=>{
  const chunks=[];for await(const chunk of request)chunks.push(chunk);
  seen.push({method:request.method,path:request.url,headers:request.headers,body:Buffer.concat(chunks).toString('utf8')});
  response.writeHead(200,{'content-type':'application/json; charset=utf-8','demopay-protocol':'1'});
  response.end(JSON.stringify({kind:'accepted'}));
 });
 server.listen(0,'127.0.0.1');await once(server,'listening');
 try{
  const endpoint=`http://127.0.0.1:${server.address().port}/`;
  assert.throws(()=>createGenericDemoPayFetchPort('http://example.com/'),/C14_PROVIDER_ENDPOINT/);
  assert.throws(()=>createGenericDemoPayFetchPort(endpoint+'v1/capture'),/C14_PROVIDER_ENDPOINT/);
  const port=createGenericDemoPayFetchPort(endpoint),body=Buffer.from('{"attemptKey":"a"}');
  await assert.rejects(port.exchange({origin:'https://untrusted.invalid',method:'POST',path:'/v1/capture',
   headers:{'content-type':'application/json; charset=utf-8','demopay-protocol':'1'},body,signal:new AbortController().signal}),/C14_PROVIDER_REQUEST/);
  const result=await port.exchange({origin:'https://demopay.invalid',method:'POST',path:'/v1/capture',
   headers:{'content-type':'application/json; charset=utf-8','demopay-protocol':'1'},body,signal:new AbortController().signal});
  assert.equal(result.status,200);
  assert.equal(result.headers['demopay-protocol'],'1');
  assert.equal(Buffer.from(result.body).toString('utf8'),'{"kind":"accepted"}');
  assert.deepEqual(seen.map(row=>[row.method,row.path,row.body]),[['POST','/v1/capture',body.toString('utf8')]]);
 }finally{server.close();await once(server,'close');}
});
