import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {cpSync,mkdtempSync,readFileSync,readdirSync,rmSync,writeFileSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import test from 'node:test';
import {buildService,compileService} from '../src/service-builder.js';
import {parseServiceSource} from '../src/service-profile.js';

const implementation=path.resolve(import.meta.dirname,'..');
const sourcePath=path.resolve(implementation,'../extensions/inference-router-v1/service.alch');
const source=readFileSync(sourcePath,'utf8');
const temporary=(t:{after(fn:()=>void):void})=>{const directory=mkdtempSync(path.join(os.tmpdir(),'alch-service-test-'));t.after(()=>rmSync(directory,{recursive:true,force:true}));return directory;};
const files=(root:string):string[]=>readdirSync(root,{withFileTypes:true}).flatMap(entry=>entry.isDirectory()?files(path.join(root,entry.name)):[path.join(root,entry.name)]);
const sha=(value:Buffer|string)=>createHash('sha256').update(value).digest('hex');
const request=(pathName:string,body:unknown,method='POST')=>new Request('http://localhost'+pathName,{method,headers:{authorization:'Bearer internal-secret','content-type':'application/json'},body:JSON.stringify(body)});

test('one service .alch source declares and compiles multiple explicit entry points',async t=>{
 const root=temporary(t),output=path.join(root,'bundle'),result=await buildService(sourcePath,output);assert.equal(result.entries,2);
 const api=await import(pathToFileURL(path.join(output,'app/service/index.mjs')).href);
 assert.deepEqual(api.routes,[{id:'Capabilities',method:'POST',path:'/internal/capabilities'},{id:'PublicError',method:'POST',path:'/internal/public-error'}]);
 const capabilities={providers:[{binding_id:'local-one',binding_version:'v1',model:'small',enabled:true,tenant_allowed:true,task:'text.generate',context_limit:4096,output_limit:512,streaming:true,rank:1}],strategies:['balanced'],retention_ms:1000};
 const direct=await api.invoke('Capabilities',capabilities);assert.equal(direct.status,'ok');assert.deepEqual(direct.value.routing_strategies,['balanced']);
 const response=await api.handler(request('/internal/public-error',{code:'UNKNOWN_MODEL',request_id:'request-1'}),{INFERENCE_INTERNAL_TOKEN:'internal-secret'});assert.equal(response.status,200);assert.deepEqual(await response.json(),{status:'ok',http_status:404,body:{request_id:'request-1',error:{code:'UNKNOWN_MODEL'}}});
 assert.equal((await api.handler(request('/missing',{}),{})).status,404);assert.equal((await api.handler(request('/internal/capabilities',{},'PUT'),{})).status,405);
 await assert.rejects(api.invoke('Missing',{}),/SERVICE_ENTRY_NOT_FOUND/);
 const deployment=JSON.parse(readFileSync(path.join(output,'deployment.json'),'utf8'));assert.equal(deployment.schema_version,'alchlang.portable-http-service/v1');assert.equal(deployment.routes.length,2);assert.deepEqual(deployment.environment_references,['INFERENCE_INTERNAL_TOKEN']);
 const ontology=JSON.parse(readFileSync(path.join(output,'provenance/service/ontology.json'),'utf8'));assert.equal(ontology.schema_version,'alchlang.service-ontology/v1');assert.equal(ontology.nodes.filter((node:any)=>node.kind==='entry').length,2);assert.equal(ontology.references.length,2);assert.equal(ontology.ontology_admitted,false);
 const trace=JSON.parse(readFileSync(path.join(output,'evidence/service/assembly-trace.json'),'utf8'));assert.deepEqual(trace.pipeline,['alch-source','composition-ontology','craft-project','compiled-entry','service-assembly']);for(const entry of trace.entries){assert.match(entry.composition_ontology_sha256,/^[a-f0-9]{64}$/);assert.match(entry.craft_project_sha256,/^[a-f0-9]{64}$/);assert.match(entry.compiler_certificate_sha256,/^[a-f0-9]{64}$/);}
 assert.equal(trace.source.path,'service.alch');assert.equal(trace.source.sha256,sha(source));assert.ok(!JSON.stringify(ontology).includes(path.dirname(sourcePath)));
 const manifest=JSON.parse(readFileSync(path.join(output,'manifest.json'),'utf8'));for(const [relative,digest]of Object.entries(manifest.files))assert.equal(sha(readFileSync(path.join(output,relative))),digest);
});

test('service builds are deterministic and bind every entry to exact function source',async t=>{
 const root=temporary(t),first=path.join(root,'first'),second=path.join(root,'second'),relocated=path.join(root,'relocated-input');cpSync(path.dirname(sourcePath),relocated,{recursive:true});await buildService(sourcePath,first);await buildService(path.join(relocated,'service.alch'),second);
 const firstFiles=files(first).map(file=>path.relative(first,file)).sort(),secondFiles=files(second).map(file=>path.relative(second,file)).sort();assert.deepEqual(firstFiles,secondFiles);
 for(const relative of firstFiles)assert.deepEqual(readFileSync(path.join(first,relative)),readFileSync(path.join(second,relative)),relative);
 const compiled=compileService(sourcePath);assert.deepEqual(compiled.entries.map(entry=>entry.source),['discovery/capabilities.alch','discovery/public-error.alch']);for(const entry of compiled.entries)assert.equal(entry.source_sha256,sha(readFileSync(path.resolve(path.dirname(sourcePath),entry.source))));
});

test('service source fails closed for incomplete bindings and route collisions',()=>{
 assert.equal(parseServiceSource(source).entries.length,2);
 assert.throws(()=>parseServiceSource(source.replace('function PublicErrorFunction','function MissingFunction')),/ALCH_SERVICE: entry function binding/);
 assert.throws(()=>parseServiceSource(source.replace(/\nentry PublicError:[\s\S]*$/,'')),/ALCH_SERVICE: a service requires at least two entries|every function import/);
 const root=mkdtempSync(path.join(path.dirname(sourcePath),'service-invalid-'));try{
  const capabilitySource=readFileSync(path.resolve(path.dirname(sourcePath),'discovery/capabilities.alch'));
  writeFileSync(path.join(root,'capabilities.alch'),capabilitySource);writeFileSync(path.join(root,'capabilities-copy.alch'),capabilitySource);
  const duplicate=source.replace('./discovery/capabilities.alch','./capabilities.alch').replace('./discovery/public-error.alch','./capabilities-copy.alch');
  const service=path.join(root,'service.alch');writeFileSync(service,duplicate);assert.throws(()=>compileService(service),/ALCH_SERVICE: duplicate route POST \/internal\/capabilities/);
 }finally{rmSync(root,{recursive:true,force:true});}
});


test('service provenance survives relocation while internal source checks retain real paths',t=>{
 const root=temporary(t),first=path.join(root,'first'),second=path.join(root,'second');
 cpSync(path.dirname(sourcePath),first,{recursive:true});
 cpSync(path.dirname(sourcePath),second,{recursive:true});
 const a=compileService(path.join(first,'service.alch'));
 const b=compileService(path.join(second,'service.alch'));
 assert.notEqual(a.sourcePath,b.sourcePath);
 assert.deepEqual(a.ontology,b.ontology);
 assert.equal(a.ontology.source.path,'service.alch');
 assert.equal(a.ontology.source.sha256,createHash('sha256').update(source).digest('hex'));
 assert.ok(!JSON.stringify(a.ontology).includes(root));
});
