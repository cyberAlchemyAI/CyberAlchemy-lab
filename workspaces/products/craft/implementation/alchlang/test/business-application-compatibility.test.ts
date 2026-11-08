import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {prepareProfileProject,generateProfileProject,disposeProfileProject} from '../src/profile-engine.js';
// Open questions: frozen/installed matrix BA15/18. This composite is authored package data.
test('v2 mixed function services and business application retain separate meaning and runtime paths',async t=>{
 const alch=path.resolve(import.meta.dirname,'..'),repo=path.resolve(alch,'../../../../../..'),cli=path.join(repo,'craft/projects/domainspec-v2/impl/cli'),root=mkdtempSync(path.join(os.tmpdir(),'mixed-profile-'));t.after(()=>rmSync(root,{recursive:true,force:true}));
 cpSync(path.join(cli,'test/profile-engine/fixtures/quote-business'),root,{recursive:true});cpSync(path.join(cli,'test/profile-engine/fixtures/business-notice'),path.join(root,'notice'),{recursive:true});cpSync(path.join(cli,'profiles/node-http-entry-local-v2'),path.join(root,'profile'),{recursive:true});
 const pkg=JSON.parse(readFileSync(path.join(root,'profile/profile.json'),'utf8')),functions=JSON.parse(readFileSync(path.join(cli,'profiles/node-http-entry-local-v1/profile.json'),'utf8'));pkg.id='mixed-node-http';pkg.capabilities.push(...functions.capabilities.filter((c:any)=>['domain-function','http-entry'].includes(c.role)));pkg.rules.push(...functions.rules.filter((r:any)=>['domain-function','http-entry'].includes(r.role)));pkg.assets.push(...functions.assets);for(const asset of functions.assets)cpSync(path.join(cli,'profiles/node-http-entry-local-v1',asset.path),path.join(root,'profile',asset.path));writeFileSync(path.join(root,'profile/profile.json'),JSON.stringify(pkg));
 const file=path.join(root,'project.json'),project=JSON.parse(readFileSync(file,'utf8')),notice=JSON.parse(readFileSync(path.join(root,'notice/project.json'),'utf8'));project.schema_version='craft.profile-project/v2-candidate';project.application_models=[{id:'commerce',source:'notice/domain.alch',semantics:'notice/business-semantics.json'}];project.application_intents=notice.application_intents;project.profiles=[{id:pkg.id,version:'1.0.0',path:'profile'}];writeFileSync(file,JSON.stringify(project));
 const prepared=await prepareProfileProject(file);t.after(()=>disposeProfileProject(prepared));assert.equal(prepared.composition.functions.length,2);assert.equal(prepared.composition.applications.length,1);const output=path.join(root,'generated');generateProfileProject(prepared,output);const service=await import(pathToFileURL(path.join(output,'app/index.mjs')).href),request=(route:string,body:unknown)=>new Request('https://example.invalid/'+route,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});
 const quote=await service.handler(request('requestQuote',{request_id:'R1',sku:'S1',quantity:3}),{DEPENDENCY_INVENTORY_URL:'https://inventory.invalid/stock'},{fetch:async()=>new Response('{"sku":"S1","stock":5,"unit_price_minor":1250}')});assert.equal(quote.status,200);assert.equal((await quote.json()).total_minor,'3750');
 const application=await service.handler(request('receiveNotice',{payload:{id:'7'}}));assert.equal(application.status,200);assert.equal((await application.json()).value.id,'7');
});
