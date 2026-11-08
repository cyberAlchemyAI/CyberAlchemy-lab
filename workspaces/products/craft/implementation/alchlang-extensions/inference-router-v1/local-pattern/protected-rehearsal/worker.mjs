import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {once} from 'node:events';
import {importJWK} from '../../../../../../../../../auth-foundation/implementation/authentication-https/node_modules/jose/dist/webapi/index.js';
import {verifier} from '../../../../../../../../../auth-foundation/implementation/authentication-https/src/identity.mjs';
import {createTenantSecurityPort,createTenantAuthorizer} from '../../security/auth-foundation.mjs';
import {createProtectedServer} from '../../security/host.mjs';
// Disposable rehearsal worker. IPC is trusted test input, not a public interface.
// Open Questions and identity-fixture boundary: README.md.
let server;
process.once('message',async config=>{
 try{
  const load=p=>import(pathToFileURL(join(config.bundle,p)).href);
  const [service,admission,invocation,stream,custody,requirement,catalog]=await Promise.all([
   load('public-service/app/service/index.mjs'),load('public-admission/app/function/index.mjs'),load('provider-invocation/app/invocation/index.mjs'),load('provider-stream/app/stream/index.mjs'),load('request-custody/app/custody/index.mjs'),load('security-requirement/app/function/index.mjs'),load('security-catalog/app/function/index.mjs')]);
  const key=await importJWK(config.publicKey,'RS256');
  const security=createTenantSecurityPort({verifyToken:verifier({issuer:config.issuer},key),assertActive:async()=>{},authorize:createTenantAuthorizer({binary:config.binary,policy:config.policy})});
  server=createProtectedServer({...config.host,security,token:'isolated-rehearsal',serviceFactory:service.createHandler,servicePlan:service.plan,modelsMapper:service.functions.Models,capabilitiesMapper:service.functions.Capabilities,errorMapper:service.functions.Errors,admissionMapper:admission.invoke,invocationFactory:invocation.createInvocation,streamFactory:stream.createSession,custodyFactory:custody.createCustody,requirementMapper:requirement.invoke,catalogMapper:catalog.invoke,estimateContext:({max_output_tokens})=>65536+max_output_tokens,store:{durable:{path:config.database,key:Buffer.from(config.key,'hex')}}});
  server.listen(0,'127.0.0.1');await once(server,'listening');process.send({ready:true,url:'http://127.0.0.1:'+server.address().port});
 }catch{process.send?.({ready:false});process.exitCode=1;process.disconnect();}
});
const stop=()=>{if(!server){process.exitCode=1;process.disconnect();return;}server.closeAllConnections();server.close(()=>process.disconnect());};
process.once('SIGTERM',stop);process.once('SIGINT',stop);
