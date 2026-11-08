import path from 'node:path';
import {sha256} from '../input/source-manifest.js';
import type {PlannedArtifact} from '../generation/contracts.js';

export interface ProfileTargetExpectation {
  readonly path: string;
  readonly kind: 'Entity'|'Rule'|'Query';
  readonly callable: string;
  readonly imports: readonly Readonly<{path:string;symbol:string;type_only:boolean}>[];
  readonly bound_rule?: string;
}
/** Independent bounded form checks. Native compilation/execution is additionally required.
 * Not an arbitrary TypeScript AST verifier and never a substitute for semantic tests.
 */
export function observeProfiledProject(artifacts:readonly PlannedArtifact[], expected:readonly ProfileTargetExpectation[]): Readonly<{result:'pass'|'fail';failures:readonly string[]}> {
  const failures:string[]=[];
  if(artifacts.length!==expected.length || new Set(artifacts.map(a=>a.relative_path)).size!==expected.length) failures.push('artifact-set');
  for(const e of expected){
    const artifact=artifacts.find(a=>a.relative_path===e.path);
    if(!artifact){failures.push('path:'+e.path);continue;}
    if(sha256(artifact.content)!==artifact.sha256 || Buffer.byteLength(artifact.content)!==artifact.size_bytes) failures.push('artifact-digest:'+e.path);
    const code=artifact.content.replace(/("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(\/\/[^\n]*|\/\*[\s\S]*?\*\/)/g,(match,literal:string|undefined)=>literal??' '.repeat(match.length));
    const tokens=code.replace(/"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g,'""');
    const exported=[...tokens.matchAll(/\bexport\s+const\s+(\w+)\s*=/g)].map(m=>m[1]);
    if(exported.length!==1 || exported[0]!==e.callable || /\bexport\s+(?:default|function|class|let|var)\b|\bexport\s*\{/.test(tokens)) failures.push('export-form:'+e.path);
    if(/\bclass\s+\w+|\bconstructor\s*\(/.test(tokens)) failures.push('class-construction:'+e.path);
    const imports=[...code.matchAll(/\bimport\s+(type\s+)?\{\s*(\w+)\s*\}\s+from\s+"([^"]+)"\s*;/g)].map(m=>({type_only:!!m[1],symbol:m[2]!,path:m[3]!}));
    if((tokens.match(/\bimport\b/g)??[]).length!==imports.length || imports.length!==e.imports.length || imports.some((i,n)=>i.path!==e.imports[n]?.path || i.symbol!==e.imports[n]?.symbol || i.type_only!==e.imports[n]?.type_only)) failures.push('import-binding:'+e.path);
    for(const i of imports){
      const target=path.posix.normalize(path.posix.join(path.posix.dirname(e.path),i.path)).replace(/\.js$/,'.ts');
      if(!artifacts.some(a=>a.relative_path===target)) failures.push('import-target:'+e.path);
    }
    if(/\b(?:fetch|require|eval)\s*\(|\bDate\b|\bMath\.random\b|\bprocess\b/.test(tokens)) failures.push('ambient-effect:'+e.path);
    if(e.kind==='Entity'){
      const validation=`if (!${e.bound_rule}(fields)) return failure(`;
      const validateAt=code.indexOf(validation), snapshotAt=code.indexOf('const value:');
      if(validateAt<0 || snapshotAt<0 || validateAt>snapshotAt) failures.push('validation-before-construction:'+e.path);
      if(!/create:\(input:unknown\):Result=>construct\(input\)/.test(code) || !/reconstruct:\(input:unknown\):Result=>construct\(input\)/.test(code) || !code.includes('construct(input,previous)')) failures.push('construction-routes:'+e.path);
      if(!code.includes('value:null') || !code.includes('Object.freeze({') || !code.includes('snapshots.add(value)')) failures.push('snapshot-contract:'+e.path);
    }
    if(e.kind==='Rule' && !new RegExp(`export const ${e.callable} = \\(fields:\\w+Fields\\):boolean =>`).test(code)) failures.push('boolean-arrow:'+e.path);
    if(e.kind==='Query' && (!code.includes('snapshots:readonly') || !code.includes('Object.freeze(selected.map'))) failures.push('readonly-query:'+e.path);
  }
  return Object.freeze({result:failures.length?'fail':'pass',failures:Object.freeze(failures)});
}
