import path from 'node:path';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {PROJECT_LAYOUT, outputImport} from './output-layout.js';
import {
  isReconciledPythonProject,
  isReconciledRustProject,
  selectSelectedReconciledArtifacts,
  type SelectedReconciledProject,
} from './selected-reconciled-project.js';
import {rustSnake} from './configured-rust-values.js';
import {assertReconciledProjectPlan,selectReconciledArtifacts,COMPOSED_RECONCILED_COMPILATION_VERSION,type ComposedReconciledProjectPlan} from './reconciled-project.js';

export const RECONCILED_PROJECT_LAYOUT_DEFINITION_SHA256 = '2c2e0ebb5e8003db5edc5d5d9375ac0c139aae1efa15b3cc4d9feb4152ae1f07';

type Artifact = Readonly<{relative_path:string;content:string;size_bytes:number;sha256:string}>;
type Module = Readonly<{relative_path:string;sha256:string;imports?:readonly Readonly<{specifier:string;target_path:string|null;target_sha256:string|null}>[];[key:string]:unknown}>;
const fail = (message:string):never => {throw Object.assign(new Error('DS_RECONCILED_PROJECT_LAYOUT: '+message),{code:'DS_RECONCILED_BUILD_LAYOUT',pointer:'/output-layout',exitCode:22});};
const compare = (left:{relative_path:string},right:{relative_path:string}) => left.relative_path < right.relative_path ? -1 : left.relative_path > right.relative_path ? 1 : 0;
const escape = (value:string) => value.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const artifact = (relative_path:string,content:string):Artifact => Object.freeze({relative_path,content,size_bytes:Buffer.byteLength(content),sha256:sha256(content)});

function checkedPaths(paths:ReadonlyMap<string,string>):void {
  const exact=new Set<string>(),folded=new Set<string>();
  for(const projected of paths.values()){
    if(!projected||path.posix.normalize(projected)!==projected||projected.startsWith('/')||projected.includes('\\')||projected.split('/').includes('..'))fail('unsafe projected path:'+projected);
    if(exact.has(projected)||folded.has(projected.toLowerCase()))fail('projected path collision:'+projected);
    exact.add(projected);folded.add(projected.toLowerCase());
  }
}

function replaceTypeScriptSpecifier(content:string,from:string,to:string):string {
  if(from===to)return content;
  const expression=new RegExp(`(\\b(?:from|import)\\s+)(["'])${escape(from)}\\2`,'g');
  let count=0;const result=content.replace(expression,(_match,prefix,quote)=>{count++;return prefix+quote+to+quote;});
  if(!count)fail('missing TypeScript import declaration:'+from);
  return result;
}

function typescriptPath(root:string,relative:string):string {
  const feature=new RegExp('^'+escape(root)+'/features/([^/]+)/src/(domain|application)/(.+)$').exec(relative);
  if(feature)return `${PROJECT_LAYOUT.source}/${PROJECT_LAYOUT.features}/${feature[1]}/${feature[2]}/${feature[3]}`;
  const runtime=new RegExp('^'+escape(root)+'/runtime/(.+)$').exec(relative);
  if(runtime)return `${PROJECT_LAYOUT.source}/${PROJECT_LAYOUT.shared}/${runtime[1]}`;
  const composition=/^compositions\/(.+)$/.exec(relative);
  if(composition)return `${PROJECT_LAYOUT.source}/compositions/${composition[1]}`;
  return fail('unmapped TypeScript artifact:'+relative);
}

function projectTypeScript(plan:Pick<SelectedReconciledProject|ComposedReconciledProjectPlan,'selection'>,source:ReturnType<typeof selectSelectedReconciledArtifacts>){
  const root=plan.selection.module_root,paths=new Map(source.artifacts.map(row=>[row.relative_path,typescriptPath(root,row.relative_path)]));checkedPaths(paths);
  const modules=source.modules as readonly Module[],byModule=new Map(modules.map(row=>[row.relative_path,row]));
  const projected=source.artifacts.map(row=>{
    const module=byModule.get(row.relative_path);let content=row.content;
    if(module){
      const rewrites=new Map<string,string>();
      for(const dependency of module.imports??[]){
        if(dependency.target_path===null)continue;
        const target=paths.get(dependency.target_path)??fail('unmapped TypeScript import target:'+dependency.target_path);
        const specifier=outputImport(paths.get(row.relative_path)!,target).replace(/\.ts$/,'.js'),known=rewrites.get(dependency.specifier);
        if(known!==undefined&&known!==specifier)fail('ambiguous TypeScript import target:'+dependency.specifier);
        rewrites.set(dependency.specifier,specifier);
      }
      for(const [from,to] of rewrites)content=replaceTypeScriptSpecifier(content,from,to);
    }
    return artifact(paths.get(row.relative_path)!,content);
  }).sort(compare);
  const projectedArtifacts=new Map(projected.map(row=>[row.relative_path,row]));
  return {
    artifacts:projected,
    modules:modules.map(module=>{
      const relative_path=paths.get(module.relative_path)??fail('unmapped TypeScript module:'+module.relative_path),current=projectedArtifacts.get(relative_path)!;
      return {...module,relative_path,sha256:current.sha256,...(module.imports?{imports:module.imports.map(dependency=>{
        if(dependency.target_path===null)return dependency;
        const target_path=paths.get(dependency.target_path)??fail('unmapped TypeScript import target:'+dependency.target_path),target=projectedArtifacts.get(target_path)!;
        return {...dependency,specifier:outputImport(relative_path,target_path).replace(/\.ts$/,'.js'),target_path,target_sha256:target.sha256};
      })}:{})};
    }).sort(compare),
  };
}

const pythonRoot = (root:string) => root.split('/').map(part=>part.replaceAll('-','_')).join('/');
function pythonPath(root:string,relative:string):string {
  const feature=new RegExp('^'+escape(root)+'/features/([^/]+)/src/(domain|application)/(.+)$').exec(relative);
  if(feature)return `${PROJECT_LAYOUT.source}/${root}/${PROJECT_LAYOUT.features}/${feature[1]}/${feature[2]}/${feature[3]}`;
  const featureSourcePackage=new RegExp('^'+escape(root)+'/features/([^/]+)/src/__init__\\.py$').exec(relative);
  if(featureSourcePackage)return `${PROJECT_LAYOUT.source}/${root}/${PROJECT_LAYOUT.features}/${featureSourcePackage[1]}/__init__.py`;
  const runtime=new RegExp('^'+escape(root)+'/runtime/(.+)$').exec(relative);
  if(runtime)return `${PROJECT_LAYOUT.source}/${root}/${PROJECT_LAYOUT.shared}/${runtime[1]}`;
  if(relative.endsWith('/__init__.py')&&(relative===root+'/__init__.py'||relative.startsWith(root+'/')))return `${PROJECT_LAYOUT.source}/${relative}`;
  return fail('unmapped Python artifact:'+relative);
}
function pythonBasePath(root:string,base:string):string {
  const feature=new RegExp('^'+escape(root)+'/features/([^/]+)/src(?:/(.*))?$').exec(base);
  if(feature)return `${PROJECT_LAYOUT.source}/${root}/${PROJECT_LAYOUT.features}/${feature[1]}${feature[2]?'/'+feature[2]:''}`;
  const runtime=new RegExp('^'+escape(root)+'/runtime(?:/(.*))?$').exec(base);
  if(runtime)return `${PROJECT_LAYOUT.source}/${root}/${PROJECT_LAYOUT.shared}${runtime[1]?'/'+runtime[1]:''}`;
  if(base===root||base.startsWith(root+'/'))return `${PROJECT_LAYOUT.source}/${base}`;
  return fail('unmapped Python import base:'+base);
}
function projectedPythonSpecifier(oldPath:string,newPath:string,specifier:string,root:string):string {
  if(!specifier.startsWith('.'))return specifier;
  const dots=/^\.+/.exec(specifier)![0].length,oldDirectory=path.posix.dirname(oldPath).split('/');
  if(dots>oldDirectory.length)fail('Python import escapes package:'+specifier);
  const base=[...oldDirectory.slice(0,oldDirectory.length-dots+1),...specifier.slice(dots).split('.').filter(Boolean)].join('/');
  const target=pythonBasePath(root,base).slice((PROJECT_LAYOUT.source+'/').length).split('/');
  const from=path.posix.dirname(newPath).slice((PROJECT_LAYOUT.source+'/').length).split('/');
  let common=0;while(common<from.length&&common<target.length&&from[common]===target[common])common++;
  if(common===0)fail('Python projected import loses package root:'+specifier);
  return '.'.repeat(from.length-common+1)+target.slice(common).join('.');
}
function replacePythonSpecifier(content:string,from:string,to:string):string {
  if(from===to)return content;
  const expression=new RegExp(`(^|\\n)(from\\s+)${escape(from)}(\\s+import\\s+)`,'g');
  let count=0;const result=content.replace(expression,(_match,line,prefix,suffix)=>{count++;return line+prefix+to+suffix;});
  if(!count)fail('missing Python import declaration:'+from);
  return result;
}
function projectPython(plan:SelectedReconciledProject,source:ReturnType<typeof selectSelectedReconciledArtifacts>){
  const root=pythonRoot(plan.selection.module_root),obsoleteSourcePackage=new RegExp('^'+escape(root)+'/features/[^/]+/src/__init__\\.py$');
  const sourceArtifacts=source.artifacts.filter(row=>!obsoleteSourcePackage.test(row.relative_path));
  const modules=(source.modules as readonly Module[]).filter(row=>!obsoleteSourcePackage.test(row.relative_path));
  const paths=new Map(source.artifacts.map(row=>[row.relative_path,pythonPath(root,row.relative_path)]));
  checkedPaths(new Map(sourceArtifacts.map(row=>[row.relative_path,paths.get(row.relative_path)!])));
  const byModule=new Map(modules.map(row=>[row.relative_path,row]));
  const projected=sourceArtifacts.map(row=>{
    const module=byModule.get(row.relative_path);let content=row.content;
    if(module)for(const specifier of new Set((module.imports??[]).filter(item=>item.target_path!==null).map(item=>item.specifier))){
      content=replacePythonSpecifier(content,specifier,projectedPythonSpecifier(row.relative_path,paths.get(row.relative_path)!,specifier,root));
    }
    return artifact(paths.get(row.relative_path)!,content);
  }).sort(compare);
  const projectedArtifacts=new Map(projected.map(row=>[row.relative_path,row]));
  return {artifacts:projected,modules:modules.map(module=>{
    const relative_path=paths.get(module.relative_path)??fail('unmapped Python module:'+module.relative_path),current=projectedArtifacts.get(relative_path)!;
    return {...module,relative_path,sha256:current.sha256,...(module.imports?{imports:module.imports.map(dependency=>{
      if(dependency.target_path===null)return dependency;
      const target_path=paths.get(dependency.target_path)??fail('unmapped Python import target:'+dependency.target_path),target=projectedArtifacts.get(target_path)!;
      return {...dependency,specifier:projectedPythonSpecifier(module.relative_path,relative_path,dependency.specifier,root),target_path,target_sha256:target.sha256};
    })}:{})};
  }).sort(compare)};
}

function rustModulePath(module:Module):string {
  const selector=typeof module.selector==='string'?module.selector:fail('Rust module selector'),[feature,node,...extra]=selector.split(':');
  if(!feature||!node||extra.length)fail('Rust qualified selector:'+selector);
  const match=/\/src\/(domain|application)\/([^/]+)\/[^/]+\.rs$/.exec(module.relative_path);
  const layer=match?.[1],role=match?.[2];
  if(!feature||!node||!layer||!role)fail('unmapped Rust module:'+module.relative_path);
  return `${PROJECT_LAYOUT.source}/${PROJECT_LAYOUT.features}/${rustSnake(feature!)}/${layer}/${role}/${rustSnake(node!)}.rs`;
}
function rustReference(root:string,relative:string):string {
  const prefix=root+'/src/';if(!relative.startsWith(prefix)||!relative.endsWith('.rs'))fail('Rust native module path:'+relative);
  return 'crate::'+relative.slice(prefix.length,-3).split('/').join('::');
}
function rustProjectedReference(relative:string):string {
  if(!relative.startsWith('src/')||!relative.endsWith('.rs'))fail('Rust projected module path:'+relative);
  return 'crate::'+relative.slice(4,-3).split('/').join('::');
}
function projectRust(plan:SelectedReconciledProject,source:ReturnType<typeof selectSelectedReconciledArtifacts>){
  const root=plan.selection.module_root,modules=source.modules as readonly Module[],paths=new Map(modules.map(row=>[row.relative_path,rustModulePath(row)]));checkedPaths(paths);
  const references=[...paths].map(([oldPath,newPath])=>[rustReference(root,oldPath),rustProjectedReference(newPath)] as const).sort(([left],[right])=>right.length-left.length);
  const original=new Map(source.artifacts.map(row=>[row.relative_path,row])),projected:Artifact[]=[];
  for(const module of modules){
    const sourceArtifact=original.get(module.relative_path)??fail('missing Rust module artifact:'+module.relative_path);let content=sourceArtifact.content;
    for(const [from,to] of references)content=content.replaceAll(from,to);
    projected.push(artifact(paths.get(module.relative_path)!,content));
  }
  for(const name of ['Cargo.toml','Cargo.lock']){
    const sourceArtifact=original.get(root+'/'+name)??fail('missing Rust '+name);projected.push(artifact(name,sourceArtifact.content));
  }
  const roleModules=new Map<string,string[]>(),layers=new Map<string,Set<string>>(),features=new Set<string>();
  for(const relative of paths.values()){
    const parts=relative.split('/'),feature=parts[2]!,layer=parts[3]!,role=parts[4]!,node=parts[5]!.slice(0,-3),rolePath=parts.slice(0,5).join('/');
    features.add(feature);const featureLayers=layers.get(feature)??new Set<string>();featureLayers.add(layer);layers.set(feature,featureLayers);
    const names=roleModules.get(rolePath)??[];names.push(node);roleModules.set(rolePath,names);
  }
  for(const [role,names] of roleModules)projected.push(artifact(role+'/mod.rs',[...new Set(names)].sort().map(name=>`pub mod ${name};`).join('\n')+'\n'));
  for(const [feature,featureLayers] of layers){
    for(const layer of featureLayers){
      const prefix=`src/features/${feature}/${layer}/`,roles=[...roleModules.keys()].filter(item=>item.startsWith(prefix)).map(item=>item.slice(prefix.length)).sort();
      projected.push(artifact(prefix+'mod.rs',roles.map(role=>`pub mod ${role};`).join('\n')+'\n'));
    }
    projected.push(artifact(`src/features/${feature}/mod.rs`,[...featureLayers].sort().map(layer=>`pub mod ${layer};`).join('\n')+'\n'));
  }
  projected.push(artifact('src/features/mod.rs',[...features].sort().map(feature=>`pub mod ${feature};`).join('\n')+'\n'));
  projected.push(artifact('src/lib.rs','pub mod features;\n'));
  projected.sort(compare);checkedPaths(new Map(projected.map(row=>[row.relative_path,row.relative_path])));
  const byPath=new Map(projected.map(row=>[row.relative_path,row]));
  return {artifacts:projected,modules:modules.map(module=>{
    const relative_path=paths.get(module.relative_path)??fail('unmapped Rust module:'+module.relative_path);
    return {...module,relative_path,sha256:byPath.get(relative_path)!.sha256};
  }).sort(compare)};
}

/** Project checked native output; never reinterpret source or revive a serialized plan. */
export function selectReconciledProjectArtifacts(plan:SelectedReconciledProject){
  const original=selectSelectedReconciledArtifacts(plan),{view_sha256:source_view_sha256,...source}=original;
  const projected=isReconciledPythonProject(plan)?projectPython(plan,original):isReconciledRustProject(plan)?projectRust(plan,original):projectTypeScript(plan,original);
  const body={...source,output_layout:PROJECT_LAYOUT.id,layout_definition_sha256:RECONCILED_PROJECT_LAYOUT_DEFINITION_SHA256,source_view_sha256,artifacts:projected.artifacts,modules:projected.modules};
  return Object.freeze({...body,view_sha256:sha256(canonicalJson(body))});
}

/** Explicit composed profile projection; legacy dispatch remains closed. */
export function selectComposedReconciledProjectArtifacts(plan:ComposedReconciledProjectPlan){
  assertReconciledProjectPlan(plan);
  if(plan.selection.schema_version!==COMPOSED_RECONCILED_COMPILATION_VERSION)fail('explicit composed v2 plan required');
  const original=selectReconciledArtifacts(plan),{view_sha256:source_view_sha256,...source}=original;
  const projected=projectTypeScript(plan,original);
  const body={...source,output_layout:PROJECT_LAYOUT.id,layout_definition_sha256:RECONCILED_PROJECT_LAYOUT_DEFINITION_SHA256,source_view_sha256,artifacts:projected.artifacts,modules:projected.modules};
  return Object.freeze({...body,view_sha256:sha256(canonicalJson(body))});
}
