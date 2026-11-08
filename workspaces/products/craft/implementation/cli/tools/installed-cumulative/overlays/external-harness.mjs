/** Independent C10 installed application tests.
 * Open Questions: README.md#open-questions. No product runtime before frozen gate.
 */
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,readFileSync,realpathSync,writeFileSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createServer} from 'node:http';
import {once} from 'node:events';
import {DatabaseSync} from 'node:sqlite';
import {createGenericHttpCompositionOwner} from '@domainspec-v2/cli/generic';
import * as nativeFixtures from '@domainspec-v2/cli/generic/testing';
const here=path.dirname(fileURLToPath(import.meta.url));
let serial=0;
export const json=p=>JSON.parse(readFileSync(p,'utf8'));
export const bytes=x=>new Uint8Array(Buffer.from(JSON.stringify(x)));
export const key=s=>Buffer.from(s,'utf8').toString('base64url');
export const faultCode=e=>e?.diagnostics?.[0]?.code??e?.code;
export function environment(){
 assert.equal(process.env.C10_RUNTIME_GATE,'reviewed-product-and-test-freeze');
 assert.ok(process.env.C10_WORK&&process.env.C10_FIXTURES);
 for(const spec of ['@domainspec-v2/cli/generic','@domainspec-v2/cli/generic/testing']){
  const p=realpathSync(new URL(import.meta.resolve(spec)));
  assert.ok(p.includes(path.sep+'node_modules'+path.sep));
  assert.equal(p.endsWith('.ts'),false);
 }
 return{work:path.resolve(process.env.C10_WORK),fixtures:path.resolve(process.env.C10_FIXTURES)};
}
export async function cleanup(actions,primary){
 const errors=[];
 for(const action of actions)try{await action();}catch(e){errors.push(e);}
 if(primary!==undefined)throw errors.length?new AggregateError([primary,...errors],'Primary and cleanup errors',{cause:primary}):primary;
 if(errors.length)throw new AggregateError(errors,'Cleanup errors');
}
function accept(owner,handle,dir){
 const label='independent-C10';
 const review=owner.review(handle,label);
 owner.accept(handle,{decision_id:'C10-'+(++serial),owner:label,outcome:'accepted',reviewed_digest:review.review_sha256},path.join(dir,'review-'+serial+'.json'));
}
/** A controlled protocol peer, never a business callback passed to the product. */
export async function provider(replies){
 const queue=[...replies],requests=[],sockets=new Set(),timers=new Map();
 const bodyGates=new Map();
 for(const reply of queue)if(reply.bodyGate){
  assert.equal(bodyGates.has(reply.bodyGate),false,'unique controlled peer body gate');
  let release;const promise=new Promise(resolve=>{release=resolve;});
  bodyGates.set(reply.bodyGate,{promise,release,waiting:false,released:false});
 }
 let closing=false,closePromise;
 const server=createServer(async(req,res)=>{
  const record={method:req.method,target:req.url,headers:req.rawHeaders.slice(),bodyBytes:0,receivedAt:performance.now()};
  requests.push(record);
  req.on('data',chunk=>{record.bodyBytes+=chunk.length;});
  const reply=queue.shift();
  if(!reply){res.writeHead(599,{'content-type':'text/plain'});res.end('unexpected extra provider request');return;}
  try{
   if(reply.headersDelayMs)await delay(reply.headersDelayMs);
   if(closing||res.destroyed)return;
   res.writeHead(reply.status??200,reply.headers??{'content-type':'application/json'});
   res.flushHeaders();record.headersAt=performance.now();
   if(reply.closeAfterHeaders){res.destroy();return;}
   if(reply.chunks){
    for(const part of reply.chunks){
     if(part.delayMs)await delay(part.delayMs);
     if(closing||res.destroyed)return;
     res.write(part.bytes);record.lastChunkAt=performance.now();
    }
    res.end();
   }else{
    if(reply.bodyGate){const gate=bodyGates.get(reply.bodyGate);gate.waiting=true;record.bodyGate=reply.bodyGate;await gate.promise;gate.waiting=false;}
    if(reply.bodyDelayMs)await delay(reply.bodyDelayMs);
    if(!closing&&!res.destroyed)res.end(reply.body??'');
   }
  }catch(error){record.peerError=String(error);res.destroy();}
  finally{record.finishedAt=performance.now();}
 });
 function delay(ms){return new Promise(resolve=>{const timer=setTimeout(()=>{timers.delete(timer);resolve();},ms);timers.set(timer,resolve);});}
 server.on('connection',socket=>{sockets.add(socket);socket.on('close',()=>sockets.delete(socket));});
 server.listen(0,'127.0.0.1');await once(server,'listening');
 const address=server.address();assert.equal(typeof address,'object');
 return{origin:'http://127.0.0.1:'+address.port,requests,
  bodyGateSnapshot(id){const g=bodyGates.get(id);assert.ok(g);return Object.freeze({waiting:g.waiting,released:g.released});},
  releaseBodyGate(id){const g=bodyGates.get(id);assert.ok(g&&g.waiting&&!g.released);g.released=true;g.release();},
  close(){
   if(closePromise)return closePromise;
   closePromise=(async()=>{
   closing=true;
   for(const g of bodyGates.values())g.release();
   for(const [timer,resolve] of timers){clearTimeout(timer);resolve();}
   timers.clear();
   const closingSockets=[...sockets],closedSockets=closingSockets.map(socket=>new Promise(resolve=>socket.once('close',resolve)));
   for(const socket of closingSockets)socket.destroy();
   const done=new Promise((resolve,reject)=>server.close(error=>error?reject(error):resolve()));
   server.closeAllConnections();
   await Promise.all([done,...closedSockets]);
   assert.equal(server.listening,false);assert.equal(sockets.size,0);
   })();return closePromise;
  }};
}
export function replyFromCase(c){
 const file=path.join(here,c.file);
 return{status:c.status,headers:c.headers,body:readFileSync(file)};
}
export function prepareFixtureInputs(name,peer){
 const env=environment(),dir=path.join(env.work,'case-'+process.pid+'-'+(++serial));
 mkdirSync(dir,{recursive:true,mode:0o700});
 const authored=path.join(dir,'authored');cpSync(path.join(env.fixtures,name),authored,{recursive:true});
 const oracle=json(path.join(authored,'independent-oracle.json'));
 const config={schema_version:'craft.generic-external-read-config/v1-candidate',bindings:[{binding:oracle.configuration_binding,origin:peer.origin}]};
 // Capture the actual canonical peer destination before the original source owner reads it.
 writeFileSync(path.join(authored,'contracts/external-config.json'),JSON.stringify(config,null,2)+'\n',{flag:'wx',mode:0o600});
 return{dir,authored,oracle};
}
export async function generate(name,peer,{rowsOverride}={}){
 const {dir,authored,oracle}=prepareFixtureInputs(name,peer);
 const owner=createGenericHttpCompositionOwner();let handle,primary;
 try{
  handle=await owner.prepare({sourcePath:path.join(authored,'business.alch'),profilePath:path.join(authored,'contracts/selected-profile.json'),httpProfilePath:path.join(authored,'contracts/http-profile.json'),externalProfilePath:path.join(authored,'contracts/external-profile.json')});
  accept(owner,handle,dir);
  const out=path.join(dir,'generated');
  const manifest=await owner.generate(handle,{entry:oracle.root_entry,outputDirectory:out});
  const module=await import(pathToFileURL(path.join(out,'application.mjs')).href);
  assert.equal(typeof module.createGeneratedApplicationOwner,'function');
  assert.equal(peer.requests.length,0,'generation itself must not fetch business data');
  return{dir,authored,out,manifest,oracle,createOwner:module.createGeneratedApplicationOwner,rows:rowsOverride??json(path.join(authored,'fixture-rows.json'))};
 }catch(error){primary=error;throw error;}
 finally{await cleanup([()=>handle?owner.dispose(handle):undefined],primary);}
}
export async function open(f,{storePath,grants}={}){
 const dir=path.join(f.dir,'epoch-'+(++serial));mkdirSync(dir,{mode:0o700});
 const owner=f.createOwner();let handle,auth,runtime;
 try{
  handle=await owner.prepare();accept(owner,handle,dir);
  const entries=grants??[f.oracle.root_entry,f.oracle.child_entry];
  auth=await nativeFixtures.createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(dir,'auth'),subjects:[{id:f.oracle.subject,evidence:'C10-evidence-'+serial,session:'C10-session-'+serial}],grants:entries.map(entry=>({subject:f.oracle.subject,entry}))});
  if(storePath)runtime=await owner.openRuntime(handle,{service:f.oracle.service,storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
  else{
   const setup=await nativeFixtures.prepareGenericFixtureRuntime(owner,handle,{service:f.oracle.service,ownedDirectory:path.join(dir,'store'),nativeAuth:auth.nativeAuth});
   runtime=setup.runtime;storePath=setup.storePath;nativeFixtures.loadGenericFixture(setup.fixture,bytes(f.rows));
  }
  let closed=false;const cleanupStages=[];
  const cleanupStage=async(stage,action)=>{try{await action();cleanupStages.push({stage,returned:true});}catch(error){cleanupStages.push({stage,returned:false,error});throw error;}};
  const storageTables=runtime.inspect().storage.tables.map(t=>({...t}));
  return{owner,handle,auth,runtime,storePath,storageTables,cleanupStages,principal:f.oracle.subject,
   bind:()=>owner.bindHttp(handle,runtime,f.oracle.route_id),
   async close(){if(closed)return;closed=true;await cleanup([()=>cleanupStage('runtime',()=>runtime.close()),()=>cleanupStage('auth',()=>auth.close()),()=>cleanupStage('composition',()=>owner.dispose(handle))]);}
  };
 }catch(error){await cleanup([()=>runtime?.close(),()=>auth?.close(),()=>handle?owner.dispose(handle):undefined],error);}
}
export function post(r,f,handler,input=f.oracle.operation_input,command='c10-command'){
 const request=new Request('https://example.test/api/approvals',{method:'POST',headers:{'content-type':'application/json','x-craft-command-key':key(command)},body:JSON.stringify(input)});
 r.auth.associateRequest(handler,request,r.principal);return request;
}
export async function readHttp(response,status){
 assert.equal(response.status,status);
 assert.equal(response.headers.get('content-type'),'application/json; charset=utf-8');
 assert.equal(response.headers.get('cache-control'),'no-store');
 const body=await response.json();assert.equal(body.schema_version,'craft.generic-http-result/v1-candidate');
 const fuel=body.fuel;
 assert.ok(fuel);assert.deepEqual(Object.keys(fuel).sort(),['operation_fuel_used','response_fuel_used','total_fuel_used']);
 for(const amount of Object.values(fuel))assert.ok(Number.isSafeInteger(amount)&&amount>=0);
 assert.equal(fuel.total_fuel_used,fuel.operation_fuel_used+fuel.response_fuel_used);
 return body;
}
export function snapshot(r){
 const db=new DatabaseSync(r.storePath,{readOnly:true});
 try{
  const quote=s=>'"'+s.replaceAll('"','""')+'"';
  return{rows:r.storageTables.map(t=>({entity:t.entity,rows:db.prepare('SELECT hex('+quote(t.row_column)+') AS row,hex('+quote(t.revision_column)+') AS revision FROM '+quote(t.physical_name)+' ORDER BY row').all().map(x=>({...x}))})),metadata:{...db.prepare('SELECT hex(revision_counter) AS revision,command_count,command_bytes FROM _craft_generic_metadata WHERE id=1').get()},journalCount:db.prepare('SELECT count(*) AS n FROM _craft_generic_commands_v1').get().n};
 }finally{db.close();}
}
export async function withApplication(name,replies,fn,options={}){
 environment();
 const peer=await provider(replies);let f,r,primary;
 try{f=await generate(name,peer,options);r=await open(f,options);return await fn({f,r,peer});}
 catch(error){primary=error;throw error;}
 finally{await cleanup([()=>r?.close(),()=>peer.close()],primary);}
}

