import {readFileSync,realpathSync,mkdtempSync,mkdirSync,writeFileSync,cpSync,rmSync,readdirSync,linkSync,lstatSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadModuleTree,assertModuleSources} from './module-source.js';
import {buildFunction,checkFunction} from './function-builder.js';
import {loadDomainSpecCompiler} from './domainspec-cli.js';
import {digest} from './domainspec-profile.js';
import {expandedModuleShape as shape} from './outbound-composition.js';
// Candidate syntax/lowering and generated custody binding. Open Questions: ../CUSTODY.md.
const fail=(s:string):never=>{throw Error('ALCH_CUSTODY: '+s);};
function pure(t:any){if(t.parsed.model.endpoint.target!=='node-http')fail('Node policy module required');for(const b of Object.values(t.parsed.model.integrations) as any[])if(b.transport!=='module-local')fail('pure policy modules required');for(const child of Object.values(t.children))pure(child);}
export async function loadCustody(file:string){
 file=realpathSync(file);const source=readFileSync(file,'utf8');if(path.extname(file)!=='.alch'||Buffer.byteLength(source)>65536)fail('source bounds');const top:any={};let imported:string|undefined;
 for(const line of source.split(/\r?\n/)){
  if(!line.trim()||line.startsWith('#'))continue;
  const imp=/^import Policy from ("[^"\n]+")$/.exec(line);if(imp){if(imported)fail('duplicate import');imported=JSON.parse(imp[1]);continue;}
  const m=/^([a-z-]+) (.+)$/.exec(line);if(!m||Object.hasOwn(top,m[1]))fail('unknown/duplicate declaration');top[m![1]]=m![2];
 }
 const names=['domain','profile','target','limits','identity','decisions','lifecycle'];if(names.some(k=>!Object.hasOwn(top,k))||Object.keys(top).some(k=>!names.includes(k)))fail('closed declarations');if(top.profile!=='request-custody-v1'||top.target!=='node-http'||!/^[-a-z0-9]+ "[^"\n]+"$/.test(top.domain))fail('profile/target');
 if(!imported?.startsWith('./')||!imported.endsWith('.alch'))fail('relative policy import');const resolved=realpathSync(path.resolve(path.dirname(file),imported!)),relative=path.relative(path.dirname(file),resolved);if(relative==='..'||relative.startsWith('../')||path.isAbsolute(relative))fail('import escape');
 const tree=loadModuleTree(resolved);pure(tree);const trees={Policy:tree};const json=(key:string)=>{try{return JSON.parse(top[key]);}catch{return fail('JSON declaration '+key);}};
 const compiler=await loadDomainSpecCompiler(),compiled=compiler.compileRequestCustody({schema_version:'domainspec.request-custody/v1-candidate',limits:json('limits'),identity:json('identity'),decisions:json('decisions'),lifecycle:json('lifecycle'),module:{input:shape(tree,{type:tree.parsed.model.endpoint.input}),output:shape(tree,{type:tree.parsed.model.endpoint.output})}});return {file,source,trees,compiled};
}
function assertSources(l:any){if(readFileSync(l.file,'utf8')!==l.source)fail('source drift');for(const t of Object.values(l.trees))assertModuleSources(t as any);}
const files=(dir:string):string[]=>readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)]);
export async function checkCustody(file:string){const l=await loadCustody(file);for(const t of Object.values(l.trees) as any[])await checkFunction(t.path);assertSources(l);return {status:'valid',...l.compiled,authority_effect:'none'};}
export async function buildCustody(file:string,output:string){
 const l=await loadCustody(file);output=path.resolve(output);try{lstatSync(output);fail('output exists');}catch(e){if((e as any).code!=='ENOENT')throw e;}const stage=mkdtempSync(path.join(path.dirname(output),'.alch-custody-'));
 try{
  mkdirSync(path.join(stage,'modules'));for(const [name,t]of Object.entries(l.trees) as [string,any][])await buildFunction(t.path,path.join(stage,'modules',name),t);
  mkdirSync(path.join(stage,'app/custody'),{recursive:true});for(const name of ['custody-runtime'])cpSync(fileURLToPath(new URL('./'+name+'.js',import.meta.url)),path.join(stage,'app/custody',name+'.js'));writeFileSync(path.join(stage,'package.json'),'{"type":"module","private":true}\n');
  writeFileSync(path.join(stage,'source.alch'),l.source);writeFileSync(path.join(stage,'custody.json'),JSON.stringify(l.compiled.contract,null,2)+'\n');
  writeFileSync(path.join(stage,'app/custody/index.mjs'),`import {invoke as policy} from '../../modules/Policy/app/function/index.mjs';\nimport {createCustodyDispatcher} from './custody-runtime.js';\nimport contract from '../../custody.json' with {type:'json'};\nexport const createCustody=options=>createCustodyDispatcher(contract,{...options,policy:options?.policy??(input=>policy(input,{}, {localOnly:true}))});\nexport {contract,policy};\n`);
  writeFileSync(path.join(stage,'trace.json'),JSON.stringify({...l.compiled.trace,source:{path:l.file,sha256:digest(l.source)},modules:Object.fromEntries(Object.entries(l.trees).map(([k,t]:any)=>[k,{source_sha256:digest(t.source),manifest_sha256:digest(readFileSync(path.join(stage,'modules',k,'manifest.json')))}]))},null,2)+'\n');assertSources(l);
  const inventory=Object.fromEntries(files(stage).sort().map(p=>[path.relative(stage,p),digest(readFileSync(p))]));const manifest={schema_version:'alchlang.custody-build/v1-candidate',entry:'app/custody/index.mjs',source_sha256:digest(l.source),files:inventory,authority_effect:'none'};writeFileSync(path.join(stage,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');mkdirSync(output);
  for(const f of files(stage).sort((a,b)=>Number(a===path.join(stage,'manifest.json'))-Number(b===path.join(stage,'manifest.json')))){const dest=path.join(output,path.relative(stage,f));mkdirSync(path.dirname(dest),{recursive:true});linkSync(f,dest);}return {status:'built',output,manifest,authority_effect:'none'};
 }finally{rmSync(stage,{recursive:true,force:true});}
}
