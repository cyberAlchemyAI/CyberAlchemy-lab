import test from 'node:test';
import assert from 'node:assert/strict';
import https from 'node:https';
import {readFile} from 'node:fs/promises';
import {once} from 'node:events';
import {createHttpsIngress} from './server.mjs';
const tls=new URL('../../../../../../../../../auth-foundation/implementation/authentication-https/.runtime/tls/',import.meta.url);
const [key,cert,ca]=await Promise.all(['frontend.key','frontend.crt','ca.crt'].map(name=>readFile(new URL(name,tls))));
const origin='https://localhost:14444';
test('TLS ingress rejects unsafe configuration',()=>{for(const value of ['http://localhost:14444','https://localhost:14444/path','https://remote.invalid:14444'])assert.throws(()=>createHttpsIngress({origin:value,key,cert,handler:async()=>new Response()}));});
test('real TLS preserves separate cookies and trusted URL while rejecting host and forwarding spoofing',async()=>{
 let calls=0;const server=createHttpsIngress({origin,key,cert,handler:async request=>{calls++;assert.equal(new URL(request.url).origin,origin);const headers=new Headers();headers.append('set-cookie','__Host-one=1; Secure; HttpOnly; Path=/');headers.append('set-cookie','__Host-two=2; Secure; HttpOnly; Path=/');return new Response(await request.text(),{headers});}});
 server.listen(14444,'127.0.0.1');await once(server,'listening');
 const request=(headers={})=>new Promise((resolve,reject)=>{const req=https.request(origin+'/test',{ca,servername:'localhost',method:'POST',headers},res=>{let body='';res.on('data',c=>body+=c);res.on('end',()=>resolve({status:res.statusCode,headers:res.headers,body}));});req.on('error',reject);req.end('payload');});
 try{const valid=await request();assert.equal(valid.status,200);assert.equal(valid.body,'payload');assert.equal(valid.headers['set-cookie'].length,2);for(const headers of [{host:'other.invalid'},{forwarded:'host=localhost:14444'},{'x-forwarded-proto':'https'}])assert.equal((await request(headers)).status,400);assert.equal(calls,1);}finally{server.closeAllConnections();await new Promise(r=>server.close(r));}
});
