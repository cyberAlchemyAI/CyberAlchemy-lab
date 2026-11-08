import {readFileSync,realpathSync,mkdtempSync,mkdirSync,writeFileSync,cpSync,rmSync,readdirSync,linkSync,lstatSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadModuleTree,assertModuleSources} from './module-source.js';
import {buildFunction,checkFunction} from './function-builder.js';
import {loadDomainSpecCompiler} from './domainspec-cli.js';
import {digest} from './domainspec-profile.js';
// Alch syntax/lowering only; normalized validation belongs to DomainSpec. Open Questions: ../OUTBOUND.md.
const fail=(s:string):never=>{throw Error('ALCH_OUTBOUND: '+s);};
function shape(tree:any,s:any,active:string[]=[]):any{const {type,items,...rest}=s;const expand=(t:string):any=>{if(!Object.hasOwn(tree.parsed.model.schemas,t))return t;if(active.includes(t))return fail('recursive interface');return Object.fromEntries(Object.entries(tree.parsed.model.schemas[t]).map(([k,v])=>[k,shape(tree,v,[...active,t])]));};return {type:type==='list'?'list':expand(type),...(type==='list'?{items:expand(items)}:{}),...rest};}
function local(tree:any){if(tree.parsed.model.endpoint.target!=='node-http')fail('node target required');for(const b of Object.values(tree.parsed.model.integrations) as any[])if(!['provided','provided-or-http','module-local'].includes(b.transport))fail('local-only modules required');for(const t of Object.values(tree.children))local(t);}
export async function loadOutbound(file:string){
 file=realpathSync(file);const source=readFileSync(file,'utf8');if(path.extname(file)!=='.alch'||Buffer.byteLength(source)>65536)fail('source bound');
 const top:any={},imports:any={},steps:any[]=[];let block:any;
 for(const [i,line]of source.split(/\r?\n/).entries()){
  if(!line.trim()||line.trimStart().startsWith('#'))continue;
  if(line.startsWith('  ')){const m=/^  ([a-z_]+) (.+)$/.exec(line);if(!m||!block||Object.hasOwn(block,m[1]))fail('step clause '+(i+1));try{block[m![1]]=JSON.parse(m![2]);}catch{fail('JSON clause '+(i+1));}continue;}
  block=undefined;const imp=/^import ([A-Z][A-Za-z0-9]*) from ("[^"\n]+")$/.exec(line);if(imp){if(Object.hasOwn(imports,imp[1]))fail('duplicate import');imports[imp[1]]=JSON.parse(imp[2]);continue;}
  const step=/^step ([A-Z][A-Za-z0-9]*) (local|binding|http):$/.exec(line);if(step){block={id:step[1],kind:step[2]};steps.push(block);continue;}
  const m=/^([a-z-]+) (.+)$/.exec(line);if(!m||Object.hasOwn(top,m[1]))fail('declaration '+(i+1));top[m![1]]=m![2];
 }
 const required=['domain','profile','target','input','output','deadline-ms','max-bytes','max-concurrent','max-attempts'];if(required.some(k=>!Object.hasOwn(top,k))||Object.keys(top).some(k=>!required.includes(k)))fail('closed declarations');if(!['outbound-invocation-v1','outbound-invocation-v2'].includes(top.profile)||top.target!=='node-http'||!/^[-a-z0-9]+ "[^"\n]+"$/.test(top.domain))fail('profile/target');
 for(const k of ['deadline-ms','max-bytes','max-concurrent','max-attempts'])if(!/^[1-9][0-9]*$/.test(top[k]))fail('bound');
 const trees:any={},interfaces:any={};
 if(Object.keys(imports).length>32)fail('imports bound');
 for(const [name,p]of Object.entries(imports) as [string,string][]){if(!p.startsWith('./')||!p.endsWith('.alch'))fail('relative import');const resolved=realpathSync(path.resolve(path.dirname(file),p)),relative=path.relative(path.dirname(file),resolved);if(relative==='..'||relative.startsWith('../')||path.isAbsolute(relative))fail('import escape');const tree=loadModuleTree(resolved);local(tree);trees[name]=tree;interfaces[name]={input:shape(tree,{type:tree.parsed.model.endpoint.input}),output:shape(tree,{type:tree.parsed.model.endpoint.output})};}
 const m=/^([A-Z][A-Za-z0-9]*)\.input$/.exec(top.input);if(!m||!interfaces[m[1]])fail('input type reference');
 const compiler=await loadDomainSpecCompiler();const compiled=compiler.compileOutboundComposition({schema_version:top.profile==='outbound-invocation-v2'?'domainspec.outbound-composition/v2-candidate':'domainspec.outbound-composition/v1-candidate',input:interfaces[m![1]].input,modules:interfaces,limits:{deadline_ms:Number(top['deadline-ms']),max_bytes:Number(top['max-bytes']),max_concurrent:Number(top['max-concurrent']),max_attempts:Number(top['max-attempts'])},steps,output:top.output});
 return {file,source,trees,compiled};
}
const files=(dir:string):string[]=>readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)]);
function assertSources(l:any){if(readFileSync(l.file,'utf8')!==l.source)fail('source drift');for(const tree of Object.values(l.trees))assertModuleSources(tree as any);}
export async function checkOutbound(file:string){const l=await loadOutbound(file);for(const t of Object.values(l.trees) as any[])await checkFunction(t.path);assertSources(l);return {status:'valid',...l.compiled,authority_effect:'none'};}
export async function buildOutbound(file:string,output:string){
 const l=await loadOutbound(file);output=path.resolve(output);try{lstatSync(output);fail('output exists');}catch(e){if((e as any).code!=='ENOENT')throw e;}
 const stage=mkdtempSync(path.join(path.dirname(output),'.alch-outbound-'));
 try{
  mkdirSync(path.join(stage,'modules'));for(const [name,t]of Object.entries(l.trees) as [string,any][])await buildFunction(t.path,path.join(stage,'modules',name),t);
  mkdirSync(path.join(stage,'app/invocation'),{recursive:true});cpSync(fileURLToPath(new URL('./outbound-runtime.js',import.meta.url)),path.join(stage,'app/invocation/runtime.mjs'));
  writeFileSync(path.join(stage,'source.alch'),l.source);writeFileSync(path.join(stage,'composition.json'),JSON.stringify(l.compiled.contract,null,2)+'\n');
  writeFileSync(path.join(stage,'app/invocation/index.mjs'),Object.keys(l.trees).map(k=>`import {invoke as ${k}} from '../../modules/${k}/app/function/index.mjs';`).join('\n')+`\nimport {createOutbound} from './runtime.mjs';\nimport contract from '../../composition.json' with {type:'json'};\nexport const modules={${Object.keys(l.trees).join(',')}};\nexport const createInvocation=(dependencies,options)=>createOutbound(contract,modules,dependencies,options);\nexport {contract};\n`);
  writeFileSync(path.join(stage,'trace.json'),JSON.stringify({...l.compiled.trace,source:{path:l.file,sha256:digest(l.source)},modules:Object.fromEntries(Object.entries(l.trees).map(([k,t]:any)=>[k,{source_sha256:digest(t.source),manifest_sha256:digest(readFileSync(path.join(stage,'modules',k,'manifest.json')))}]))},null,2)+'\n');
  assertSources(l);const inventory=Object.fromEntries(files(stage).sort().map(p=>[path.relative(stage,p),digest(readFileSync(p))]));const manifest={schema_version:'alchlang.outbound-build/v1-candidate',source_sha256:digest(l.source),entry:'app/invocation/index.mjs',files:inventory,authority_effect:'none'};writeFileSync(path.join(stage,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');mkdirSync(output);
  for(const f of files(stage).sort((a,b)=>Number(a===path.join(stage,'manifest.json'))-Number(b===path.join(stage,'manifest.json')))){const dest=path.join(output,path.relative(stage,f));mkdirSync(path.dirname(dest),{recursive:true});linkSync(f,dest);}return {status:'built',output,manifest,authority_effect:'none'};
 }finally{rmSync(stage,{recursive:true,force:true});}
}

export {shape as expandedModuleShape};
