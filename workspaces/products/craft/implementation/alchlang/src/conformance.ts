import {loadDomainSpecCompiler} from './domainspec-cli.js';
import {loadModuleTree,assertModuleSources,assertModuleBundle,moduleSourceDigests} from './module-source.js';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {buildFunction,checkFunction} from './function-builder.js';
import {buildRustFunction} from './rust-function-builder.js';
import {parseDeclarativeSource} from './declarative-profile.js';
const hash=(bytes:string|Buffer)=>createHash('sha256').update(bytes).digest('hex');
const json=(file:string)=>JSON.parse(readFileSync(file,'utf8'));
const canonical=(v:any):any=>Array.isArray(v)?v.map(canonical):v&&typeof v==='object'?Object.fromEntries(Object.keys(v).sort().map(k=>[k,canonical(v[k])])):v;
const equal=(a:any,b:any)=>isDeepStrictEqual(canonical(a),canonical(b));
export function normalizeEvents(events:any[]){return events.map(e=>Object.fromEntries(['kind','binding','module','transport','declaration','node_kind','index','phase','code','passed','accepted','total','count',...(e.node_kind==='Rule'?['value']:[])].filter(k=>Object.hasOwn(e,k)).map(k=>[k,e[k]])));}
export function normalizeRequest(request:any){const url=new URL(request.url);return {...request,...(request.body!==undefined?{body:JSON.parse(request.body)}:{}),url:undefined,origin:url.origin,path:url.pathname,fragment:url.hash,query:[...url.searchParams].sort(([a,x],[b,y])=>a<b?-1:a>b?1:x<y?-1:x>y?1:0)};}
export function compareExecutions(node:any,rust:any,expected:any){return {output:equal(node.outcome,rust.outcome),oracle:equal(node.outcome,expected)&&equal(rust.outcome,expected),requests:equal(node.requests.map(normalizeRequest),rust.requests.map(normalizeRequest)),decisions:equal(normalizeEvents(node.events),normalizeEvents(rust.events)),complete:node.capture.complete&&rust.capture.complete,consumed:node.unused_responses===0&&rust.unused_responses===0};}
function fault(error:any){return error?.code??String(error?.message??'').match(/CALCULATION_(?:OVERFLOW|UNDERFLOW|DIVIDE_BY_ZERO|INEXACT)/)?.[0]??'FUNCTION_INTERNAL';}
export async function runConformance(sourcePath:string,fixturePath:string,outPath:string){
 const P=(await loadDomainSpecCompiler()).applicationPaths;
 const source=readFileSync(sourcePath,'utf8');const tree=loadModuleTree(sourcePath),parsed=tree.parsed;
 if(parsed.model.portability!=='node-rust-v1'||parsed.model.endpoint.target!=='node-http')throw Error('CONFORMANCE_PROFILE: use portability node-rust-v1 with a node-http source');
 const fixtureBytes=readFileSync(fixturePath);const fixtures=JSON.parse(fixtureBytes.toString('utf8'));if(!Array.isArray(fixtures)||!fixtures.length||fixtures.length>1000)throw Error('CONFORMANCE_FIXTURES');
 const names=new Set();for(const f of fixtures){if(!f||typeof f.name!=='string'||names.has(f.name)||!Object.hasOwn(f,'input')||!f.expected||!['succeeded','failed'].includes(f.expected.status)||Object.keys(f).some(k=>!['name','input','expected','env','responses'].includes(k)))throw Error('CONFORMANCE_FIXTURE');names.add(f.name);if(f.env&&(!f.env||typeof f.env!=='object'||Array.isArray(f.env)||Object.values(f.env).some(v=>typeof v!=='string')))throw Error('CONFORMANCE_ENV');if(f.responses&&(!Array.isArray(f.responses)||f.responses.some((r:any)=>!r||Object.keys(r).some(k=>!['status','body','raw','error'].includes(k))||r.status!==undefined&&(!Number.isInteger(r.status)||r.status<200||r.status>599)||r.error!==undefined&&!['FUNCTION_INTEGRATION_TIMEOUT','FUNCTION_INTEGRATION_FAILED'].includes(r.error))))throw Error('CONFORMANCE_RESPONSES');if(Buffer.byteLength(JSON.stringify(f))>1000000)throw Error('CONFORMANCE_FIXTURE_LIMIT');}
 await checkFunction(sourcePath,'node-http');await checkFunction(sourcePath,'rust-http');
 const out=path.resolve(outPath);mkdirSync(out);const nodeDir=path.join(out,'node'),rustDir=path.join(out,'rust');
 await buildFunction(sourcePath,nodeDir);await buildRustFunction(sourcePath,rustDir);
 assertModuleSources(tree);for(const dir of [nodeDir,rustDir])assertModuleBundle(tree,dir,P);
 for(const dir of [nodeDir,rustDir])if(readFileSync(path.join(dir,P.source),'utf8')!==source)throw Error('CONFORMANCE_SOURCE_DRIFT');
 if(readFileSync(sourcePath,'utf8')!==source||!readFileSync(fixturePath).equals(fixtureBytes))throw Error('CONFORMANCE_INPUT_DRIFT');
 const load=(name:string)=>import(pathToFileURL(path.join(nodeDir,name)).href);
 const [{createBoundary,FunctionFault},{execute,validateInput},{default:api}]=await Promise.all([load(P.runtime),load(P.behavior),load(P.api)]);
 const model=json(path.join(nodeDir,P.model)),bindings=json(path.join(nodeDir,P.bindings));const {createInvoker}=await load(P.entry);const cases=[];
 for(const f of fixtures){
  const events:any[]=[],requests:any[]=[];let used=0,bytes=0,complete=true;
  const observe=(e:any)=>{if(e.kind==='module-error'&&e.code==='FUNCTION_MODULE_TIMEOUT')complete=false;const n=Buffer.byteLength(JSON.stringify(e,(_,v)=>typeof v==='bigint'?v.toString():v));if(events.length>=10000||bytes+n>2097152){complete=false;return;}bytes+=n;events.push(e);};
  const boundary=createInvoker(observe);let outcome;
  try{const result=await boundary.invoke(structuredClone(f.input),f.env??{},{observeRequest:(r:any)=>requests.push(r),fetch:async()=>{const r=f.responses?.[used++];if(!r)throw new FunctionFault('CONFORMANCE_RESPONSE_REQUIRED');if(r.error)throw new FunctionFault(r.error);return new Response(r.raw??JSON.stringify(r.body),{status:r.status??200});}});outcome={status:'succeeded',result:JSON.parse(JSON.stringify(result))};}catch(error){outcome={status:'failed',code:fault(error)};}
  const node={outcome,events,requests,capture:{complete},unused_responses:(f.responses?.length??0)-used};
  const rust=JSON.parse(execFileSync(path.join(rustDir,P.binary),['conform'],{input:JSON.stringify({input:f.input,env:f.env??{},responses:f.responses??[]}),encoding:'utf8',timeout:30000,maxBuffer:32*1024*1024}));
  const checks=compareExecutions(node,rust,f.expected);cases.push({name:f.name,status:Object.values(checks).every(Boolean)?'pass':checks.complete?'fail':'not_evaluable',checks,node:{outcome,requests:requests.map(normalizeRequest),decisions:normalizeEvents(events)},rust:{outcome:rust.outcome,requests:rust.requests.map(normalizeRequest),decisions:normalizeEvents(rust.events)}});
 }
 const report={schema_version:'alchlang.portable-conformance/v1',status:cases.every(c=>c.status==='pass')?'pass':'fail',profile:'node-rust-v1',source_sha256:hash(source),dependency_sources:moduleSourceDigests(tree),fixtures_sha256:hash(fixtureBytes),builds:{node:hash(readFileSync(path.join(nodeDir,'manifest.json'))),rust:hash(readFileSync(path.join(rustDir,'manifest.json')))},count:cases.length,cases,execution:'controlled responses; no provider network or ambient credentials',claim:'Finite fixture conformance of outputs, errors, request preparation and decision traces. Transport timing, full intermediate payloads and deployment are outside this evidence.',authority_effect:'none'};
 writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});return report;
}
