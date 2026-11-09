/** Compile one exact zero-effect role from an original checked service source.
 * No business rules, source rewriting, runtime AST interpretation or auth grants.
 */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {stripTypeScriptTypes} from 'node:module';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
const sha=raw=>createHash('sha256').update(raw).digest('hex');
export async function createSourceOperationCompiler(coreRoot){
 const load=relative=>import(pathToFileURL(path.join(coreRoot,'dist',relative)).href);
 const [sourceApi,semanticApi,projectionApi,domainApi,emitterApi]=await Promise.all([
  load('commerce/commerce-core-source-owner.js'),load('generic/semantic-reconstruction.js'),
  load('generic/pure-source-stage.js'),load('generic/computation-domain.js'),load('commerce/commerce-computation-native.js')]);
 return Object.freeze({compile({modelRoot,applicationPath='application.alch',selector,outputDirectory}){
  if(!path.isAbsolute(modelRoot)||path.normalize(modelRoot)!==modelRoot||!path.isAbsolute(outputDirectory)||path.normalize(outputDirectory)!==outputDirectory)throw Error('normalized-source-projection-path-required');
  const sources=sourceApi.createCoreCommerceSourceOwner('atomic-state-entry');
  let source,semantics,semantic,domain,handle;
  try {
   source=sources.prepare(modelRoot,applicationPath);
   semantics=semanticApi.createGenericSemanticOwner(sources,'atomic-state-entry');semantic=semantics.check(source);
   const original=sources.inspect(source),declaration=original.reconstruction.modules.flatMap(m=>m.declarations).find(d=>d.id===selector);
   if(!declaration)throw Error('source-selector-missing');
   const role=declaration.meta_type??declaration.surface;
   const projected=projectionApi.createGenericKeyedPureComputation(original,selector);
   domain=domainApi.createGenericComputationDomainOwner(sources,source,semantics,semantic);
   handle=domain.check(projected.contract);
   const compiled=emitterApi.compileGenericComputationTypeScript(domain,handle);
   const code=stripTypeScriptTypes(compiled.source,{mode:'strip'});
   domain.assertCurrent(handle);sources.assertCurrent(source);
   mkdirSync(outputDirectory);
   writeFileSync(path.join(outputDirectory,'operation.mjs'),code,{flag:'wx'});
   writeFileSync(path.join(outputDirectory,'projection.json'),JSON.stringify({schema_version:'generic-original-source-operation-projection/v1',selector,source_capture_sha256:original.capture_sha256,files:original.files.map(({path,sha256,bytes})=>({path,sha256,bytes})),native:compiled.manifest,qualification:'local-zero-effect-component-only; no service permission or owner admission'},null,2)+'\n',{flag:'wx'});
   domain.assertCurrent(handle);sources.assertCurrent(source);
   const files=['operation.mjs','projection.json'].map(name=>{const raw=readFileSync(path.join(outputDirectory,name));return {path:name,sha256:sha(raw),bytes:raw.length};});
   const manifest={schema_version:'generic-original-source-operation-artifact/v1',selector,role,source_capture_sha256:original.capture_sha256,files,authority_effect:'none'};
   writeFileSync(path.join(outputDirectory,'manifest.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
   return manifest;
  } finally {
   if(handle)domain.dispose(handle);
   if(semantic)semantics.dispose(semantic);
   if(source)sources.dispose(source);
  }
 }});
}