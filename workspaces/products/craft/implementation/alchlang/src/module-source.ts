import {readFileSync,realpathSync} from 'node:fs';
import path from 'node:path';
import {parseDeclarativeSource} from './declarative-profile.js';
import {moduleImports,type ModuleInterface} from './module-types.js';
import {digest} from './domainspec-profile.js';
// Explicit commerce file owner; it is distinct from legacy function modules and
// from original Core/native graph owners. Open Questions: EC06/CONTEXT.md.
export {captureCommerceSource,inspectCommerceSource,assertCommerceSourceCurrent,disposeCommerceSource} from './commerce-source-capture.js';
export type ModuleTree={path:string;source:string;parsed:ReturnType<typeof parseDeclarativeSource>;children:Record<string,ModuleTree>};
export function loadModuleTree(sourcePath:string):ModuleTree{
 const root=realpathSync(path.dirname(path.resolve(sourcePath))),active=new Set<string>();let total=0,count=0;
 function load(file:string,depth:number):ModuleTree{
  if(depth>8||++count>32)throw Error('ALCH_MODULE: import graph limit');const resolved=realpathSync(file),relative=path.relative(root,resolved);if(relative.startsWith('..'+path.sep)||relative==='..'||path.isAbsolute(relative)||path.extname(resolved)!=='.alch')throw Error('ALCH_MODULE: import escapes module root');
  if(active.has(resolved))throw Error('ALCH_MODULE: import cycle '+resolved);active.add(resolved);const source=readFileSync(resolved,'utf8');total+=Buffer.byteLength(source);if(Buffer.byteLength(source)>1048576||total>4194304)throw Error('ALCH_MODULE: source limit');
  const children:Record<string,ModuleTree>={},interfaces:Record<string,ModuleInterface>={};for(const row of moduleImports(source)){if(children[row.alias])throw Error('ALCH_MODULE: duplicate alias');const child=load(path.resolve(path.dirname(resolved),row.file),depth+1);if(child.parsed.model.portability!=='node-rust-v1')throw Error('ALCH_MODULE: imported function must select node-rust-v1');children[row.alias]=child;const m=child.parsed.model;interfaces[row.alias]={source_sha256:digest(child.source),source_text:child.source,input:m.endpoint.input,output:m.endpoint.output,schemas:m.schemas,statuses:m.endpoint.statuses};}
  const parsed=parseDeclarativeSource(source,interfaces);if(Object.keys(children).length&&parsed.model.portability!=='node-rust-v1')throw Error('ALCH_MODULE: importing function must select node-rust-v1');active.delete(resolved);return {path:resolved,source,parsed,children};
 }return load(path.resolve(sourcePath),0);
}
export function assertModuleSources(tree:ModuleTree){if(readFileSync(tree.path,'utf8')!==tree.source)throw Error('FUNCTION_MODULE_SOURCE_DRIFT: '+tree.path);for(const child of Object.values(tree.children))assertModuleSources(child);}
export function moduleEnvironment(tree:ModuleTree,includeAuth=true):string[]{
 const env:string[]=includeAuth?[tree.parsed.model.endpoint.authEnv]:[];
 for(const b of Object.values(tree.parsed.model.integrations) as any[]){env.push(...[b.urlEnv,b.secretEnv].filter(Boolean));if(b.transport==='module-local'&&tree.children[b.module])env.push(...moduleEnvironment(tree.children[b.module],false));}
 return [...new Set(env)].sort();
}
export function moduleSourceDigests(tree:ModuleTree,prefix='.'):Record<string,string>{return {[prefix]:digest(tree.source),...Object.fromEntries(Object.entries(tree.children).flatMap(([alias,child])=>Object.entries(moduleSourceDigests(child,prefix==='.'?alias:prefix+'.'+alias))))};}
export function assertModuleBundle(tree:ModuleTree,directory:string,paths:Readonly<Record<string,string>>){
 if(readFileSync(path.join(directory,paths.source),'utf8')!==tree.source)throw Error('CONFORMANCE_MODULE_SOURCE_DRIFT');
 if(Object.keys(tree.children).length){const lock=JSON.parse(readFileSync(path.join(directory,paths.modules),'utf8'));if(JSON.stringify(Object.keys(lock).sort())!==JSON.stringify(Object.keys(tree.children).sort()))throw Error('CONFORMANCE_MODULE_SET');for(const [alias,child]of Object.entries(tree.children)){const folder=path.join(directory,'modules',alias);if(lock[alias].source_sha256!==digest(child.source)||lock[alias].manifest_sha256!==digest(readFileSync(path.join(folder,'manifest.json'))))throw Error('CONFORMANCE_MODULE_BINDING');assertModuleBundle(child,folder,paths);}}
}
