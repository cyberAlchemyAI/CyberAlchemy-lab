/** Candidate test harness. Runs only against reviewed, clean-installed CLI archives. */
import assert from 'node:assert/strict';
import {cpSync,mkdirSync,readFileSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {DatabaseSync} from 'node:sqlite';
import {createGenericHttpCompositionOwner} from '@domainspec-v2/cli/generic';
import * as fixtures from '@domainspec-v2/cli/generic/testing';

export const rootEntry='Schedule.ReserveBookingEntry';
export const childEntry='Schedule.ReadDayScheduleEntry';
export const subject='c09-schedule-alice';
export const fixtureRoot=realpathSync(new URL('../fixture',import.meta.url));
export const json=p=>JSON.parse(readFileSync(p,'utf8'));
export const wire=x=>new Uint8Array(Buffer.from(JSON.stringify(x)));
export const key=x=>Buffer.from(x,'utf8').toString('base64url');
let serial=0;

function environment(){
  assert.equal(process.env.C09_RUNTIME_GATE,'reviewed-product-and-test-freeze');
  assert.ok(process.env.C09_WORK);
  for(const spec of ['@domainspec-v2/cli/generic','@domainspec-v2/cli/generic/testing']){
    const file=realpathSync(new URL(import.meta.resolve(spec)));
    assert.ok(file.includes(path.sep+'node_modules'+path.sep));
    assert.equal(file.endsWith('.ts'),false);
  }
  return path.resolve(process.env.C09_WORK);
}
export async function cleanup(actions,primary){
  const errors=[];
  for(const action of actions)try{await action();}catch(error){errors.push(error);}
  if(primary!==undefined)throw errors.length?new AggregateError([primary,...errors],'Primary and cleanup errors',{cause:primary}):primary;
  if(errors.length)throw new AggregateError(errors,'Cleanup errors');
}
function accept(owner,handle,dir){
  const review=owner.review(handle,'independent-C09-schedule');
  owner.accept(handle,{decision_id:'C09-Schedule-'+(++serial),owner:'independent-C09-schedule',outcome:'accepted',reviewed_digest:review.review_sha256},path.join(dir,'review-'+serial+'.json'));
}
export async function generate(){
  const dir=path.join(environment(),'schedule-case-'+process.pid+'-'+(++serial));
  mkdirSync(dir,{recursive:true,mode:0o700});
  const authored=path.join(dir,'authored');cpSync(fixtureRoot,authored,{recursive:true});
  const owner=createGenericHttpCompositionOwner();let handle,primary;
  try{
    handle=await owner.prepare({sourcePath:path.join(authored,'business.alch'),profilePath:path.join(authored,'contracts/selected-profile.json'),httpProfilePath:path.join(authored,'contracts/http-profile.json')});
    accept(owner,handle,dir);
    const outputDirectory=path.join(dir,'generated');
    const manifest=await owner.generate(handle,{entry:rootEntry,outputDirectory});
    const generated=await import(pathToFileURL(path.join(outputDirectory,'application.mjs')).href);
    assert.equal(typeof generated.createGeneratedApplicationOwner,'function');
    return {dir,authored,manifest,createOwner:generated.createGeneratedApplicationOwner,oracle:json(path.join(authored,'http-oracle.json')),rows:json(path.join(authored,'fixture-rows.json')),base:json(path.join(authored,'contracts/selected-profile.json'))};
  }catch(error){primary=error;throw error;}
  finally{await cleanup([()=>handle?owner.dispose(handle):undefined],primary);}
}
export async function open(source,{storePath,grants=[rootEntry,childEntry]}={}){
  const dir=path.join(source.dir,'schedule-epoch-'+(++serial));mkdirSync(dir,{mode:0o700});
  const owner=source.createOwner();let handle,auth,runtime;
  try{
    handle=await owner.prepare();accept(owner,handle,dir);
    auth=await fixtures.createGenericAuthFixture(owner,handle,{ownedDirectory:path.join(dir,'auth'),subjects:[{id:subject,evidence:'C09-schedule-evidence-'+serial,session:'C09-schedule-session-'+serial}],grants:grants.map(entry=>({subject,entry}))});
    if(storePath)runtime=await owner.openRuntime(handle,{service:'ScheduleService',storePath,mode:'reopen',nativeAuth:auth.nativeAuth});
    else{const setup=await fixtures.prepareGenericFixtureRuntime(owner,handle,{service:'ScheduleService',ownedDirectory:path.join(dir,'store'),nativeAuth:auth.nativeAuth});runtime=setup.runtime;storePath=setup.storePath;fixtures.loadGenericFixture(setup.fixture,wire(source.rows));}
    let closed=false;
    return {owner,handle,auth,runtime,storePath,bind:route=>owner.bindHttp(handle,runtime,'ScheduleHttp.'+route),async close(){if(closed)return;closed=true;await cleanup([()=>runtime.close(),()=>auth.close(),()=>owner.dispose(handle)]);}};
  }catch(error){await cleanup([()=>runtime?.close(),()=>auth?.close(),()=>handle?owner.dispose(handle):undefined],error);}
}
export async function withRuntime(fn,options={}){
  const source=await generate(),runtime=await open(source,options);let primary;
  try{return await fn(runtime,source);}catch(error){primary=error;throw error;}
  finally{await cleanup([()=>runtime.close()],primary);}
}
export function associate(runtime,handler,request){runtime.auth.associateRequest(handler,request,subject);return request;}
export function reserve(input,clientKey){return new Request('https://example.test/api/reservations',{method:'POST',headers:{'content-type':'application/json','x-craft-command-key':key(clientKey)},body:JSON.stringify(input)});}
export function read(dayId){return new Request('https://example.test/api/days/'+dayId);}
export async function response(value,status){
  assert.equal(value.status,status);assert.equal(value.headers.get('content-type'),'application/json; charset=utf-8');
  assert.equal(value.headers.get('cache-control'),'no-store');
  const body=await value.json();assert.equal(body.schema_version,'craft.generic-http-result/v1-candidate');
  assert.equal(body.fuel.total_fuel_used,body.fuel.operation_fuel_used+body.fuel.response_fuel_used);
  return body;
}
export function snapshot(runtime){
  const db=new DatabaseSync(runtime.storePath,{readOnly:true});
  try{
    const quote=x=>'"'+x.replaceAll('"','""')+'"';
    return {rows:runtime.runtime.inspect().storage.tables.map(table=>({entity:table.entity,rows:db.prepare('SELECT hex('+quote(table.row_column)+') AS row,hex('+quote(table.revision_column)+') AS revision FROM '+quote(table.physical_name)+' ORDER BY row').all()})),metadata:db.prepare('SELECT hex(revision_counter) AS revision,command_count,command_bytes FROM _craft_generic_metadata WHERE id=1').get(),journal_count:db.prepare('SELECT count(*) AS n FROM _craft_generic_commands_v1').get().n};
  }finally{db.close();}
}
