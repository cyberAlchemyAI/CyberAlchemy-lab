import {assertReconciledProjectPlan,selectReconciledArtifacts,type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {inventoryGeneratedModule} from '../generation/generated-module-surface.js';
import {sha256} from '../input/source-manifest.js';

export const VERIFICATION_ARTIFACT_COVERAGE_DEFINITION_SHA256='c7215a92397f886934b5a0534dd3fc4a6d5176931ccb5ddd32e2034615328bcc';
const fail=(message:string):never=>{throw new TypeError('DS_VERIFICATION_ARTIFACT_COVERAGE:'+message);};
const compare=(a:{relative_path:string},b:{relative_path:string})=>a.relative_path<b.relative_path?-1:a.relative_path>b.relative_path?1:0;
function freeze<T>(value:T):T{if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.values(value).forEach(freeze);Object.freeze(value);}return value;}
/** Complete ownership-based inventory; no file or generated behavior is executed. */
export function createReconciledArtifactCoverage(plan:ReconciledProjectPlan){
 assertReconciledProjectPlan(plan);
 if(sha256(getReconciledSource('verification_artifact_coverage'))!==VERIFICATION_ARTIFACT_COVERAGE_DEFINITION_SHA256)fail('definition drift');
 const view=selectReconciledArtifacts(plan),typed=new Set(view.modules.map(m=>m.relative_path));
 const javascript=new Set(plan.composition?.compositions.map(c=>c.behavior_path)??[]),support=new Set(plan.composition?.artifacts.map(a=>a.relative_path)??[]);
 const typescript_paths:string[]=[],javascript_paths:string[]=[],preserved_paths:string[]=[],seen=new Set<string>();
 for(const a of view.artifacts){
  if(seen.has(a.relative_path))fail('duplicate artifact');seen.add(a.relative_path);
  if(typed.has(a.relative_path)){if(!a.relative_path.endsWith('.ts')||javascript.has(a.relative_path))fail('invalid typed module');typescript_paths.push(a.relative_path);}
  else if(javascript.has(a.relative_path)){if(!a.relative_path.endsWith('.mjs'))fail('invalid JavaScript module');javascript_paths.push(a.relative_path);}
  else if(support.has(a.relative_path))preserved_paths.push(a.relative_path);
  else fail('unaccounted artifact '+a.relative_path);
 }
 for(const name of [...typed,...javascript,...support])if(!seen.has(name))fail('missing owned artifact '+name);
 const behaviorModules=javascript_paths.map(relative_path=>{
  const artifact=view.artifacts.find(a=>a.relative_path===relative_path)!,surface=inventoryGeneratedModule(artifact.content);
  if(surface.imports.length)fail('generated composition behavior must not import modules');
  return {relative_path,sha256:artifact.sha256,qualified_selectors:[] as string[],metatypes:[] as string[],artifact_role:'composition-behavior' as const,request_sha256s:[] as string[],exports:surface.exports,imports:[] as typeof view.modules[number]['imports']};
 });
 return freeze({definition_sha256:VERIFICATION_ARTIFACT_COVERAGE_DEFINITION_SHA256,artifacts:view.artifacts,modules:[...view.modules,...behaviorModules].sort(compare),typescript_paths,javascript_paths,preserved_paths});
}
