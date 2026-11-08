/** Installed cumulative HTTP harness using original generated owners/native Auth.
 * Open Questions: ../README.md#open-questions. */
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,readFileSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {createGenericHttpCompositionOwner} from '@domainspec-v2/cli/generic';
import * as fixtures from '@domainspec-v2/cli/generic/testing';
export const json=p=>JSON.parse(readFileSync(p,'utf8'));
export const code=e=>e?.diagnostics?.[0]?.code??e?.code;
export const rootEntry='ReviewDesk.CommitRequestApprovalEntry';
export const childEntry='ReviewDesk.ReadStoredRequestEntry';
export const alternateEntry='ReviewDesk.CommitRequestApprovalAlternateEntry';
export const subject='c09-alice';
export const wire=x=>new Uint8Array(Buffer.from(JSON.stringify(x)));
export const key=x=>Buffer.from(x,'utf8').toString('base64url');
let serial=0;
export function environment(){
 assert.equal(process.env.C09_RUNTIME_GATE,'reviewed-product-and-test-freeze');
 assert.ok(process.env.C09_WORK&&process.env.C09_FIXTURES);
 for(const spec of ['@domainspec-v2/cli/generic','@domainspec-v2/cli/generic/testing']){const f=realpathSync(new URL(import.meta.resolve(spec)));assert.ok(f.includes(path.sep+'node_modules'+path.sep));assert.equal(f.endsWith('.ts'),false);}
 return{work:path.resolve(process.env.C09_WORK),fixtures:path.resolve(process.env.C09_FIXTURES)};
}
export async function cleanup(actions,primary){const errors=[];for(const action of actions)try{await action();}catch(e){errors.push(e);}if(primary!==undefined)throw errors.length?new AggregateError([primary,...errors],'Primary and cleanup errors',{cause:primary}):primary;if(errors.length)throw new AggregateError(errors,'Cleanup errors');}
function accept(owner,h,dir){const r=owner.review(h,'independent-C09');owner.accept(h,{decision_id:'C09-'+(++serial),owner:'independent-C09',outcome:'accepted',reviewed_digest:r.review_sha256},path.join(dir,'review-'+serial+'.json'));}
export async function generate(name='approval'){
 const env=environment(),dir=path.join(env.work,'case-'+process.pid+'-'+(++serial));mkdirSync(dir,{recursive:true,mode:0o700});const authored=path.join(dir,'authored');cpSync(path.join(env.fixtures,name),authored,{recursive:true});
 const owner=createGenericHttpCompositionOwner();let h,primary;
 try{const input={sourcePath:path.join(authored,'business.alch'),profilePath:path.join(authored,'contracts/selected-profile.json'),httpProfilePath:path.join(authored,'contracts/http-profile.json')};const oracle=json(path.join(authored,'http-oracle.json'));if(oracle.additional_source_paths.length)input.additionalSourcePaths=oracle.additional_source_paths.map(p=>path.join(authored,p));h=await owner.prepare(input);accept(owner,h,dir);const out=path.join(dir,'generated'),manifest=await owner.generate(h,{entry:rootEntry,outputDirectory:out});const mod=await import(pathToFileURL(path.join(out,'application.mjs')).href);assert.equal(typeof mod.createGeneratedApplicationOwner,'function');return{dir,authored,out,manifest,createOwner:mod.createGeneratedApplicationOwner,oracle,rows:json(path.join(authored,'fixture-rows.json')),base:json(path.join(authored,'contracts/selected-profile.json'))};}catch(e){primary=e;throw e;}finally{await cleanup([()=>h?owner.dispose(h):undefined],primary);}
}
export async function open(f,{storePath,grants,principal=subject}={}){
 const dir=path.join(f.dir,'epoch-'+(++serial));mkdirSync(dir,{mode:0o700});const owner=f.createOwner();let handle,auth,runtime;
 try{handle=await owner.prepare();accept(owner,handle,dir);const entries=grants??[rootEntry,childEntry,alternateEntry,'ReviewDesk.ReadScalarRequestEntry','ReviewDesk.ReadHttpOwnedRequestEntry'];auth=await fixtures.createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(dir,'auth'),subjects:[{id:principal,evidence:'C09-evidence-'+serial,session:'C09-session-'+serial}],grants:entries.map(entry=>({subject:principal,entry}))});
 if(storePath)runtime=await owner.openRuntime(handle,{service:'ReviewDeskService',storePath,mode:'reopen',nativeAuth:auth.nativeAuth});else{const setup=await fixtures.prepareGenericFixtureRuntime(owner,handle,{service:'ReviewDeskService',ownedDirectory:path.join(dir,'store'),nativeAuth:auth.nativeAuth});runtime=setup.runtime;storePath=setup.storePath;fixtures.loadGenericFixture(setup.fixture,wire(f.rows));}
 let closed=false;return{owner,handle,auth,runtime,storePath,principal,bind:id=>owner.bindHttp(handle,runtime,'ReviewDeskHttp.'+id),async close(){if(closed)return;closed=true;await cleanup([()=>runtime.close(),()=>auth.close(),()=>owner.dispose(handle)]);}};
 }catch(e){await cleanup([()=>runtime?.close(),()=>auth?.close(),()=>handle?owner.dispose(handle):undefined],e);}
}
export async function withRuntime(fn,options={}){const f=await generate(options.fixture??'approval');const r=await open(f,options);let primary;try{return await fn(r,f);}catch(e){primary=e;throw e;}finally{await cleanup([()=>r.close()],primary);}}
export function post(id='23',clientKey='http-α-23',headers={}){return new Request('https://example.test/api/approvals',{method:'POST',headers:{'content-type':'application/json','x-craft-command-key':key(clientKey),...headers},body:JSON.stringify({id})});}
export function associate(r,h,request){r.auth.associateRequest(h,request,r.principal);return request;}
export async function response(response,status){assert.equal(response.status,status);assert.equal(response.headers.get('content-type'),'application/json; charset=utf-8');assert.equal(response.headers.get('cache-control'),'no-store');const body=await response.json();assert.equal(body.schema_version,'craft.generic-http-result/v1-candidate');const fuel=body.fuel;assert.deepEqual(Object.keys(fuel).sort(),['operation_fuel_used','response_fuel_used','total_fuel_used']);for(const x of Object.values(fuel))assert.ok(Number.isSafeInteger(x)&&x>=0);assert.equal(fuel.total_fuel_used,fuel.operation_fuel_used+fuel.response_fuel_used);return body;}
export function fault(body,code,cause=null,{zero=false}={}){assert.deepEqual(Object.keys(body).sort(),['cause_code','code','fuel','kind','observation','schema_version']);assert.equal(body.kind,'fault');assert.equal(body.code,code);assert.equal(body.cause_code,cause);if(zero){assert.deepEqual(body.observation,{kind:'not-invoked'});assert.equal(body.fuel.total_fuel_used,0);}}
export function returned(body,value,kind){assert.deepEqual(Object.keys(body).sort(),['fuel','kind','observation','schema_version','value']);assert.equal(body.kind,'returned');assert.deepEqual(body.value,value);assert.equal(body.observation.kind,kind);}
export function snapshot(r){const db=new DatabaseSync(r.storePath,{readOnly:true});try{const quote=x=>'"'+x.replaceAll('"','""')+'"';return{rows:r.runtime.inspect().storage.tables.map(t=>({entity:t.entity,rows:db.prepare('SELECT hex('+quote(t.row_column)+') AS row,hex('+quote(t.revision_column)+') AS revision FROM '+quote(t.physical_name)+' ORDER BY row').all().map(x=>({...x}))})),metadata:{...db.prepare('SELECT hex(revision_counter) AS revision,command_count,command_bytes FROM _craft_generic_metadata WHERE id=1').get()},journal_count:db.prepare('SELECT count(*) AS n FROM _craft_generic_commands_v1').get().n};}finally{db.close();}}
export function lifetime(r){const db=new DatabaseSync(r.auth.inspect().databasePath,{readOnly:true});try{return{observed_at:new Date().toISOString(),expiry:db.prepare('SELECT expires_at FROM auth_sessions').all().map(x=>x.expires_at)};}finally{db.close();}}
