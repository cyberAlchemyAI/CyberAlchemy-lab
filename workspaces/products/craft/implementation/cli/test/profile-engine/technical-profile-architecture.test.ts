import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {lowerTechnicalProfileArchitecture,type TechnicalProfileArchitectureEnvelope,type TechnicalProfileArchitectureTopology} from '../../src/profile-engine/technical-profile-architecture.js';
import {createProfileFixture} from './profile-fixture.js';
import {prepareProfileProject,planProfileProject,generateProfileProject,disposeProfileProject} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/profile-engine.js';

const repositoryRoot=path.resolve(import.meta.dirname,'../../../../../../..');
function fixture(shared=false){
 const file=path.join(repositoryRoot,'goals/plans/craft-technical-profiles-2026-10-31/examples',shared?'architecture-shared.profile.json':'architecture-entry-local.profile.json');
 const envelope=JSON.parse(readFileSync(file,'utf8')) as TechnicalProfileArchitectureEnvelope;
 const nodes=Object.keys(envelope.bindings).map(id=>({id,binding:id}));
 const edge=(source:string,sourcePort:string,target:string,targetPort:string,contract='entry')=>({source,sourcePort,target,targetPort,contract,kind:'Dependency'});
 const edges=[edge('entryA','invoke','businessA','entry'),edge('entryB','invoke','businessB','entry'),edge('dispatcher','first','entryA','handler'),edge('dispatcher','second','entryB','handler'),...(shared?[edge('entryA','transport','http','fetch','httpTransport'),edge('entryB','transport','http','fetch','httpTransport')]:[])];
 const topology:TechnicalProfileArchitectureTopology={requestBytes:'1024',nodes,edges};
 return {repositoryRoot,envelope,topology,provenance:{source_capture_sha256:'a'.repeat(64),mapping_contract_sha256:'b'.repeat(64)}};
}

test('architecture lowering keeps original generic recipes and locks source topology without accepting a new role',()=>{
 const local=lowerTechnicalProfileArchitecture(fixture()),shared=lowerTechnicalProfileArchitecture(fixture(true));
 assert.deepEqual(local,lowerTechnicalProfileArchitecture(fixture()));
 assert.notEqual(local.manifest.generated_package_sha256,shared.manifest.generated_package_sha256);
 assert.equal(local.package.capabilities.some(c=>c.role==='shared-http-port'),false);
 assert.equal(shared.package.capabilities.some(c=>c.role==='shared-http-port'),true);
 assert.equal(shared.package.capabilities.some(c=>c.role==='application-operation'),false,'source did not declare a wider application role');
 assert.equal(shared.package.rules.find(r=>r.op==='emit'&&r.role==='http-entry')?.from,'intents');
 assert.equal(shared.package.rules.find(r=>r.op==='emit'&&r.role==='http-entry')?.fields.technical?.literal?.request_bytes,1024);
 assert.ok(shared.files['shared-port.tpl']);
 assert.equal(JSON.stringify(shared.package).includes(repositoryRoot),false,'package must not depend on checkout location');
 const changed=fixture(true);changed.topology={...changed.topology,requestBytes:'2048'};
 assert.notEqual(lowerTechnicalProfileArchitecture(changed).manifest.generated_package_sha256,shared.manifest.generated_package_sha256);
});

test('architecture lowering rejects unbound, duplicate, crossed and effect-widening plans',()=>{
 let f=fixture(true);f.topology={...f.topology,edges:f.topology.edges.slice(0,-1)};assert.throws(()=>lowerTechnicalProfileArchitecture(f),/unbound/);
 f=fixture(true);f.topology={...f.topology,edges:[...f.topology.edges,f.topology.edges[0]!]};assert.throws(()=>lowerTechnicalProfileArchitecture(f),/exactly once/);
 f=fixture(true);f.topology={...f.topology,edges:f.topology.edges.map((e,i)=>i===0?{...e,contract:'httpTransport'}:e)};assert.throws(()=>lowerTechnicalProfileArchitecture(f),/directional/);
 f=fixture(true);f.envelope={...f.envelope,resource_requirements:[{id:'database'}]};assert.throws(()=>lowerTechnicalProfileArchitecture(f),/effect consumer/);
 f=fixture(true);f.envelope={...f.envelope,target:{...f.envelope.target,consumer:'craft.generic-transaction/v1'}};assert.throws(()=>lowerTechnicalProfileArchitecture(f),/stateful families/);
 f=fixture(true);f.topology={...f.topology,requestBytes:'65537'};assert.throws(()=>lowerTechnicalProfileArchitecture(f),/requestBytes/);
 f=fixture(true);f.envelope={...f.envelope,bindings:{...f.envelope.bindings,http:{...f.envelope.bindings.http!,recipe_ref:'unimplemented'}}};assert.throws(()=>lowerTechnicalProfileArchitecture(f),/unregistered/);
});

test('source-lowered packages generate and execute existing business functions with distinct actual transport structure',async t=>{
 for(const shared of [false,true]){
  const lowered=lowerTechnicalProfileArchitecture(fixture(shared)),f=createProfileFixture(t);
  for(const [file,text]of Object.entries(lowered.files)){const target=path.join(f.root,'profile',file);mkdirSync(path.dirname(target),{recursive:true});writeFileSync(target,text);}
  const projectPath=path.join(f.root,'project.json'),project=JSON.parse(readFileSync(projectPath,'utf8'));
  project.profiles=[{id:lowered.package.id,version:lowered.package.version,path:'profile'}];writeFileSync(projectPath,JSON.stringify(project));
  const prepared=await prepareProfileProject(projectPath);t.after(()=>disposeProfileProject(prepared));
  const plan=planProfileProject(prepared),ports=plan.composition.components.filter((component:any)=>component.role==='shared-http-port');
  assert.equal(ports.length,shared?1:0);
  for(const entry of plan.composition.components.filter((component:any)=>component.role==='http-entry')){
   assert.equal(entry.owner,lowered.package.id);if(shared)assert.ok(entry.depends_on.includes(ports[0]!.id));
   assert.match(plan.files[entry.artifact_paths[0]]!,/"request_bytes":1024/);
  }
  const output=path.join(f.root,'generated');generateProfileProject(prepared,output);
  const service=await import(pathToFileURL(path.join(output,'app/index.mjs')).href),oracle=JSON.parse(readFileSync(path.join(f.root,'oracle.json'),'utf8'));
  for(const c of oracle.cases){const response=await service.handler(new Request('https://test.invalid/'+c.intent,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(c.input)}),{DEPENDENCY_INVENTORY_URL:'https://inventory.invalid/stock'},{fetch:async()=>new Response(JSON.stringify(c.external))});const body=await response.json();if(c.expected_error)assert.equal(body.error,c.expected_error);else assert.deepEqual(body,c.expected);}
 }
});

test('the same lowered package expands a different checked intent name and count without compiler changes',async t=>{
 const lowered=lowerTechnicalProfileArchitecture(fixture(true)),f=createProfileFixture(t);
 for(const [file,text]of Object.entries(lowered.files)){const target=path.join(f.root,'profile',file);mkdirSync(path.dirname(target),{recursive:true});writeFileSync(target,text);}
 const projectPath=path.join(f.root,'project.json'),project=JSON.parse(readFileSync(projectPath,'utf8'));
 writeFileSync(path.join(f.root,'health-summary.alch'),'domain health-summary "Report the service readiness contract"\nowner service-owner\nlogic sfol-v1\n\nschema HealthRequest:\n  unit: boolean const true\n\nschema HealthResponse:\n  status: string const "healthy"\n\nmapping HealthSummary:\n  meaning "State the authored readiness result."\n  target HealthResponse\n  field status = "healthy"\n\nresult DescribeHealth:\n  when true yield HealthSummary\n');
 project.domain_sources.push('health-summary.alch');project.public_intents.push({id:'healthSummary',source:'health-summary.alch',result_ref:'DescribeHealth',input_ref:'HealthRequest',output_ref:'HealthResponse',access:{kind:'public'},outcomes:[{code:'healthy',kind:'success'}]});project.profiles=[{id:lowered.package.id,version:lowered.package.version,path:'profile'}];writeFileSync(projectPath,JSON.stringify(project));
 const prepared=await prepareProfileProject(projectPath);t.after(()=>disposeProfileProject(prepared));const plan=planProfileProject(prepared);
 assert.equal(plan.composition.components.filter((component:any)=>component.role==='http-entry').length,3);
 assert.equal(plan.composition.components.filter((component:any)=>component.role==='shared-http-port').length,1);
 const output=path.join(f.root,'generated');generateProfileProject(prepared,output);
 const service=await import(pathToFileURL(path.join(output,'app/index.mjs')).href);
 const response=await service.handler(new Request('https://test.invalid/healthSummary',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({unit:true})}),{},{});assert.deepEqual(await response.json(),{status:'healthy'});
});
