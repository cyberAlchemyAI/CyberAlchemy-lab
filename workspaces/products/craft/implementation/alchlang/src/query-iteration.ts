import {readFileSync,realpathSync,mkdtempSync,mkdirSync,writeFileSync,cpSync,rmSync,readdirSync,linkSync,lstatSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadModuleTree,assertModuleSources,type ModuleTree} from './module-source.js';
import {buildFunction,checkFunction} from './function-builder.js';
import {digest} from './domainspec-profile.js';
// Closed candidate syntax; no executable snippets. Open questions: ../QUERY-ITERATION.md.
const fail=(why:string):never=>{throw Error('QUERY_ITERATION: '+why);};
const fileKeys=['source-query','input-mapping','item-query'];
const fieldKeys=['source-field','input-field','item-field','output-field'];
const numeric={'max-items':100,'max-output-bytes':65536,'max-input-bytes':262144,'timeout-ms':5000};
const fixed={profile:'query-iteration-v1',concurrency:'1',order:'input','partial-result':'reject'};
function shape(tree:ModuleTree,s:any,active:string[]=[]):any{
 const {type,items,...rest}=s;
 const expand=(t:string):any=>{if(!tree.parsed.model.schemas[t])return t;if(active.includes(t))return fail('recursive iteration interface');return Object.fromEntries(Object.entries(tree.parsed.model.schemas[t]).sort(([a],[b])=>a.localeCompare(b)).map(([k,v])=>[k,shape(tree,v,[...active,t])]));};
 return {type:type==='list'?'list':expand(type),...(type==='list'?{items:expand(items)}:{}),...Object.fromEntries(Object.entries(rest).sort(([a],[b])=>a.localeCompare(b)))};
}
function pure(tree:ModuleTree){
 if(tree.parsed.model.endpoint.target!=='node-http')fail('node-http modules required');
 for(const b of Object.values(tree.parsed.model.integrations) as any[])if(b.transport!=='module-local')fail('effectful dependency');
 for(const child of Object.values(tree.children))pure(child);
}
export function loadQueryIteration(sourcePath:string){
 sourcePath=realpathSync(sourcePath);if(path.extname(sourcePath)!=='.alch')fail('source extension');
 const source=readFileSync(sourcePath,'utf8');if(Buffer.byteLength(source)>16384)fail('source limit');
 const values:Record<string,string>={};
 for(const line of source.split(/\r?\n/)){if(!line.trim()||line.startsWith('#'))continue;const match=/^([a-z-]+) (.+)$/.exec(line);if(!match||Object.hasOwn(values,match[1]))fail('invalid or duplicate declaration');values[match![1]]=match![2];}
 if(!/^[-a-z0-9]+ "[^"\n]+"$/.test(values.domain??''))fail('domain declaration');
 const allowed=['domain',...fileKeys,...fieldKeys,...Object.keys(numeric),...Object.keys(fixed)];
 if(Object.keys(values).length!==allowed.length||Object.keys(values).some(k=>!allowed.includes(k)))fail('missing or unknown declaration');
 for(const [k,v]of Object.entries(fixed))if(values[k]!==v)fail('unsupported '+k);
 for(const k of fieldKeys)if(!/^[a-z][a-z0-9_]*$/.test(values[k])||['constructor','prototype','__proto__'].includes(values[k]))fail('invalid field');
 for(const [k,max]of Object.entries(numeric))if(!/^[1-9][0-9]*$/.test(values[k])||Number(values[k])>max)fail('invalid bound '+k);
 const root=path.dirname(sourcePath),trees:Record<string,ModuleTree>={};
 for(const key of fileKeys){let file;try{file=JSON.parse(values[key]);}catch{fail('quoted module path required');}if(typeof file!=='string'||!file.startsWith('./')||!file.endsWith('.alch'))fail('relative module required');
  const target=realpathSync(path.resolve(root,file)),rel=path.relative(root,target);if(rel==='..'||rel.startsWith('..'+path.sep)||path.isAbsolute(rel))fail('module escape');trees[key]=loadModuleTree(target);pure(trees[key]);}
 const [s,m,i]=fileKeys.map(k=>trees[k]);
 const field=(t:ModuleTree,name:string,output:boolean)=>{const schema=t.parsed.model.schemas[output?t.parsed.model.endpoint.output:t.parsed.model.endpoint.input];if(!Object.hasOwn(schema,name))fail('unknown interface field '+name);const f=schema[name];if(f.optional||f.nullable)fail('required interface field '+name);return f;};
 const equal=(a:any,b:any)=>{if(JSON.stringify(a)!==JSON.stringify(b))fail('incompatible interface');};
 const selected=field(s,values['source-field'],true);if(selected.type!=='list')fail('source must return a list');
 equal(shape(s,{type:s.parsed.model.endpoint.input}),shape(m,field(m,'context',false)));
 equal(shape(s,{type:selected.items}),shape(m,field(m,'item',false)));
 if(Object.keys(m.parsed.model.schemas[m.parsed.model.endpoint.input]).sort().join(',')!=='context,item')fail('mapping input must contain context and item only');
 equal(shape(m,field(m,values['input-field'],true)),shape(i,{type:i.parsed.model.endpoint.input}));field(i,values['item-field'],true);
 const plan={sourceField:values['source-field'],inputField:values['input-field'],itemField:values['item-field'],outputField:values['output-field'],maxItems:Number(values['max-items']),maxOutputBytes:Number(values['max-output-bytes']),maxInputBytes:Number(values['max-input-bytes']),timeoutMs:Number(values['timeout-ms'])};
 const interfaces={context:shape(s,{type:s.parsed.model.endpoint.input}),item:shape(s,{type:selected.items}),itemInput:shape(i,{type:i.parsed.model.endpoint.input}),itemOutput:shape(i,field(i,values['item-field'],true))};
 return {sourcePath,source,trees,plan,interfaces};
}
export async function checkQueryIteration(sourcePath:string){const loaded=loadQueryIteration(sourcePath);for(const tree of Object.values(loaded.trees)){await checkFunction(tree.path);assertModuleSources(tree);}if(readFileSync(loaded.sourcePath,'utf8')!==loaded.source)fail('source drift');return {status:'valid',profile:'query-iteration-v1',plan:loaded.plan,interfaces:loaded.interfaces,authority_effect:'none'};}
const files=(dir:string):string[]=>readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)]);
export async function buildQueryIteration(sourcePath:string,output:string){
 const loaded=loadQueryIteration(sourcePath);output=path.resolve(output);try{lstatSync(output);fail('output exists');}catch(e){if((e as any).code!=='ENOENT')throw e;}
 const stage=mkdtempSync(path.join(path.dirname(output),'.alch-iteration-'));
 try{
  for(const [key,tree]of Object.entries(loaded.trees))await buildFunction(tree.path,path.join(stage,key),tree);
  mkdirSync(path.join(stage,'app/function'),{recursive:true});
  cpSync(fileURLToPath(new URL('./query-iteration-runtime.js',import.meta.url)),path.join(stage,'app/function/runtime.mjs'));
  writeFileSync(path.join(stage,'app/function/index.mjs'),fileKeys.map((k,n)=>`import {invoke as f${n}} from '../../${k}/app/function/index.mjs';`).join('\n')+`\nimport {createQueryIteration} from './runtime.mjs';\nexport const invoke=createQueryIteration(${JSON.stringify(loaded.plan)},f0,f1,f2);\n`);
  writeFileSync(path.join(stage,'source.alch'),loaded.source);
  for(const tree of Object.values(loaded.trees))assertModuleSources(tree);if(readFileSync(loaded.sourcePath,'utf8')!==loaded.source)fail('source drift');
  const inventory=Object.fromEntries(files(stage).sort().map(p=>[path.relative(stage,p),digest(readFileSync(p))]));
  const manifest={profile:'query-iteration-v1',schema_version:'alchlang.query-iteration-build/v1-candidate',source_sha256:digest(loaded.source),plan:loaded.plan,interfaces:loaded.interfaces,modules:Object.fromEntries(Object.entries(loaded.trees).map(([k,t])=>[k,{source_sha256:digest(t.source)}])),files:inventory,authority_effect:'none'};
  writeFileSync(path.join(stage,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');mkdirSync(output);
  for(const f of files(stage).sort((a,b)=>Number(a===path.join(stage,'manifest.json'))-Number(b===path.join(stage,'manifest.json')))){const dest=path.join(output,path.relative(stage,f));mkdirSync(path.dirname(dest),{recursive:true});linkSync(f,dest);}
  return {status:'built',profile:'query-iteration-v1',output,authority_effect:'none'};
 }finally{rmSync(stage,{recursive:true,force:true});}
}
