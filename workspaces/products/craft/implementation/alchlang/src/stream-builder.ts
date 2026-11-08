import {readFileSync,realpathSync,mkdtempSync,mkdirSync,writeFileSync,cpSync,rmSync,readdirSync,linkSync,lstatSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadModuleTree,assertModuleSources} from './module-source.js';
import {buildFunction,checkFunction} from './function-builder.js';
import {loadDomainSpecCompiler} from './domainspec-cli.js';
import {digest} from './domainspec-profile.js';
import {expandedModuleShape as shape} from './outbound-composition.js';
// Candidate syntax/lowering and generated session. Open Questions: ../STREAMS.md.
const fail=(s:string):never=>{throw Error('ALCH_STREAM: '+s);};
function pure(t:any){if(t.parsed.model.endpoint.target!=='node-http')fail('Node frame module required');for(const b of Object.values(t.parsed.model.integrations) as any[])if(b.transport!=='module-local')fail('pure frame modules required');for(const child of Object.values(t.children))pure(child);}
export async function loadStream(file:string){
 file=realpathSync(file);const source=readFileSync(file,'utf8');if(path.extname(file)!=='.alch'||Buffer.byteLength(source)>65536)fail('source bounds');const top:any={},imports:any={},frames:any={},transitions:any[]=[];
 for(const line of source.split(/\r?\n/)){
  if(!line.trim()||line.startsWith('#'))continue;
  const imp=/^import ([A-Z][A-Za-z0-9]*) from ("[^"\n]+")$/.exec(line);if(imp){if(Object.hasOwn(imports,imp[1]))fail('duplicate import');imports[imp[1]]=JSON.parse(imp[2]);continue;}
  const transition=/^transition ([a-z][a-z0-9_]*) (start|delta|complete|fail|cancel) ([a-z][a-z0-9_]*)$/.exec(line);if(transition){transitions.push({from:transition[1],event:transition[2],to:transition[3]});continue;}
  const frame=/^frame (start|delta|complete|fail) ([A-Z][A-Za-z0-9]*) ("[^"]+")$/.exec(line);if(frame){if(Object.hasOwn(frames,frame[1]))fail('duplicate frame');frames[frame[1]]={module:frame[2],event:JSON.parse(frame[3])};continue;}
  const m=/^([a-z-]+) (.+)$/.exec(line);if(!m||Object.hasOwn(top,m[1]))fail('unknown/duplicate declaration');top[m![1]]=m![2];
 }
 const names=['domain','profile','target','initial','open','terminal','provider-events','errors','max-bytes','max-event-bytes','max-frame-bytes'];if(names.some(k=>!Object.hasOwn(top,k))||Object.keys(top).some(k=>!names.includes(k)))fail('closed declarations');if(top.profile!=='response-stream-v1'||top.target!=='node-http'||!/^[-a-z0-9]+ "[^"\n]+"$/.test(top.domain))fail('profile/target');
 const trees:any={},modules:any={};if(Object.keys(imports).length!==4)fail('four frame imports required');
 for(const [name,p]of Object.entries(imports) as [string,string][]){if(!p.startsWith('./')||!p.endsWith('.alch'))fail('relative import');const resolved=realpathSync(path.resolve(path.dirname(file),p)),relative=path.relative(path.dirname(file),resolved);if(relative==='..'||relative.startsWith('../')||path.isAbsolute(relative))fail('import escape');const tree=loadModuleTree(resolved);pure(tree);trees[name]=tree;modules[name]={input:shape(tree,{type:tree.parsed.model.endpoint.input}),output:shape(tree,{type:tree.parsed.model.endpoint.output})};}
 const json=(key:string)=>{try{return JSON.parse(top[key]);}catch{return fail('JSON declaration '+key);}};
 const compiler=await loadDomainSpecCompiler(),compiled=compiler.compileStreamLifecycle({schema_version:'domainspec.stream-lifecycle/v1-candidate',initial:json('initial'),open:json('open'),terminal:json('terminal'),provider_events:json('provider-events'),errors:json('errors'),limits:{max_bytes:json('max-bytes'),max_event_bytes:json('max-event-bytes'),max_frame_bytes:json('max-frame-bytes')},transitions,frames,modules});return {file,source,trees,compiled};
}
function assertSources(l:any){if(readFileSync(l.file,'utf8')!==l.source)fail('source drift');for(const t of Object.values(l.trees))assertModuleSources(t as any);}
const files=(dir:string):string[]=>readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)]);
export async function checkStream(file:string){const l=await loadStream(file);for(const t of Object.values(l.trees) as any[])await checkFunction(t.path);assertSources(l);return {status:'valid',...l.compiled,authority_effect:'none'};}
export async function buildStream(file:string,output:string){
 const l=await loadStream(file);output=path.resolve(output);try{lstatSync(output);fail('output exists');}catch(e){if((e as any).code!=='ENOENT')throw e;}const stage=mkdtempSync(path.join(path.dirname(output),'.alch-stream-'));
 try{
  mkdirSync(path.join(stage,'modules'));for(const [name,t]of Object.entries(l.trees) as [string,any][])await buildFunction(t.path,path.join(stage,'modules',name),t);
  mkdirSync(path.join(stage,'app/stream'),{recursive:true});for(const name of ['stream-runtime','sse-adapter'])cpSync(fileURLToPath(new URL('./'+name+'.js',import.meta.url)),path.join(stage,'app/stream',name+'.js'));writeFileSync(path.join(stage,'package.json'),'{"type":"module","private":true}\n');
  writeFileSync(path.join(stage,'source.alch'),l.source);writeFileSync(path.join(stage,'stream.json'),JSON.stringify(l.compiled.contract,null,2)+'\n');
  writeFileSync(path.join(stage,'app/stream/index.mjs'),Object.keys(l.trees).map(k=>`import {invoke as ${k}} from '../../modules/${k}/app/function/index.mjs';`).join('\n')+`\nimport {createStreamSession} from './stream-runtime.js';\nimport contract from '../../stream.json' with {type:'json'};\nexport const modules={${Object.keys(l.trees).join(',')}};\nexport const createSession=session=>createStreamSession(contract,modules,session);\nexport {contract};\n`);
  writeFileSync(path.join(stage,'trace.json'),JSON.stringify({...l.compiled.trace,source:{path:l.file,sha256:digest(l.source)},modules:Object.fromEntries(Object.entries(l.trees).map(([k,t]:any)=>[k,{source_sha256:digest(t.source),manifest_sha256:digest(readFileSync(path.join(stage,'modules',k,'manifest.json')))}]))},null,2)+'\n');assertSources(l);
  const inventory=Object.fromEntries(files(stage).sort().map(p=>[path.relative(stage,p),digest(readFileSync(p))]));const manifest={schema_version:'alchlang.stream-build/v1-candidate',entry:'app/stream/index.mjs',source_sha256:digest(l.source),files:inventory,authority_effect:'none'};writeFileSync(path.join(stage,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');mkdirSync(output);
  for(const f of files(stage).sort((a,b)=>Number(a===path.join(stage,'manifest.json'))-Number(b===path.join(stage,'manifest.json')))){const dest=path.join(output,path.relative(stage,f));mkdirSync(path.dirname(dest),{recursive:true});linkSync(f,dest);}return {status:'built',output,manifest,authority_effect:'none'};
 }finally{rmSync(stage,{recursive:true,force:true});}
}
