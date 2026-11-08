import {execFileSync} from 'node:child_process';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,rmSync,realpathSync,readdirSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {captureJson,dataDigest,reject,type Json} from './contracts.js';
import {assertProfileSnapshotCurrent,profileSnapshotFiles,type ProfileSnapshot,type ProfileSnapshotV2} from './loader.js';
import {assertBusinessAuthoringSnapshotCurrent,businessAuthoringSnapshotFiles,type BusinessAuthoringSnapshot} from './loader-v3.js';


type NativeSnapshot=ProfileSnapshot|ProfileSnapshotV2|BusinessAuthoringSnapshot;
function isAuthoring(snapshot:NativeSnapshot):snapshot is BusinessAuthoringSnapshot{return 'kind' in snapshot&&snapshot.kind==='business-authoring-snapshot';}
function assertNativeSnapshot(snapshot:NativeSnapshot):void {if(isAuthoring(snapshot))assertBusinessAuthoringSnapshotCurrent(snapshot);else assertProfileSnapshotCurrent(snapshot);}
function nativeSnapshotFiles(snapshot:NativeSnapshot){return isAuthoring(snapshot)?businessAuthoringSnapshotFiles(snapshot):profileSnapshotFiles(snapshot);}

/** Actual native-check receipt, registered only after successful compiler exit.
 * Open questions: PE08 final renderer checker coverage and package qualification. */
export interface NativeQualification {readonly schema_version:'craft.profile-native-qualification/v1';readonly files_sha256:string;readonly lock_sha256:string;readonly covered_files:readonly string[];readonly checked_files:readonly string[];readonly typed_emissions:readonly string[];readonly compiler_sha256:string;readonly module_mode:'NodeNext';readonly receipt_sha256:string}
const qualified=new WeakMap<object,{snapshot:ProfileSnapshot|ProfileSnapshotV2|BusinessAuthoringSnapshot;files:Readonly<Record<string,string>>}>();
const emissions=new WeakMap<object,{snapshot:ProfileSnapshot|ProfileSnapshotV2|BusinessAuthoringSnapshot;sha256:string;emitted:readonly string[]}>();
/** Static module closure; this does not execute generated code or certify a sandbox. */
export function assertNativeImportClosure(snapshot:ProfileSnapshot|ProfileSnapshotV2|BusinessAuthoringSnapshot,files:Readonly<Record<string,string>>,compilerPath:string):void {
 const parserFile=path.join(path.dirname(path.dirname(realpathSync(compilerPath))),'lib/typescript.js');
 if(!nativeSnapshotFiles(snapshot).some(f=>f.key.startsWith('tool:')&&f.path===parserFile))reject('PROFILE_NATIVE_TOOL_UNPINNED','/','TypeScript parser must belong to the captured tool closure');
 const ts=createRequire(parserFile)(parserFile);let nodes=0;
 const reference=(file:string,specifier:string)=>{
  if(specifier==='node:crypto')return; // existing generated whole-plan hash primitive
  if(!specifier.startsWith('./')&&!specifier.startsWith('../'))reject('PROFILE_NATIVE_IMPORT_UNSUPPORTED',file,'external packages/builtins need a separately supported captured adapter');
  const target=path.posix.normalize(path.posix.join(path.posix.dirname(file),specifier));if(target.startsWith('../')||path.posix.isAbsolute(target))reject('PROFILE_NATIVE_IMPORT_ESCAPE',file,'imports must stay within owned output closure');
  const candidates=[target,target.replace(/\.js$/,'.ts'),target.replace(/\.mjs$/,'.mts'),target+'.ts',target+'.js',target+'/index.ts',target+'/index.js'];
  if(!candidates.some(candidate=>Object.hasOwn(files,candidate)))reject('PROFILE_NATIVE_IMPORT_MISSING',file,'referenced owned module is absent: '+specifier);
 };
 for(const [file,body]of Object.entries(files))if(/\.(?:ts|mts|cts|js|mjs|cjs)$/.test(file)){
  const source=ts.createSourceFile(file,body,ts.ScriptTarget.Latest,true);const visit=(node:any)=>{
   if(++nodes>1000000)reject('PROFILE_NATIVE_IMPORT_BUDGET',file,'bounded syntax inventory exceeded');
   if((ts.isImportDeclaration(node)||ts.isExportDeclaration(node))&&node.moduleSpecifier){if(!ts.isStringLiteral(node.moduleSpecifier))reject('PROFILE_NATIVE_IMPORT_DYNAMIC',file,'literal module required');reference(file,node.moduleSpecifier.text);}
   if(ts.isCallExpression(node)&&(node.expression.kind===ts.SyntaxKind.ImportKeyword||ts.isIdentifier(node.expression)&&node.expression.text==='require')){const argument=node.arguments[0];if(node.arguments.length!==1||!argument||!ts.isStringLiteral(argument))reject('PROFILE_NATIVE_IMPORT_DYNAMIC',file,'computed imports are outside supported output closure');reference(file,argument.text);}
   ts.forEachChild(node,visit);
  };visit(source);
 }
}
/** Owned scratch emission of the already captured domain TypeScript plan. */
export function compileProfileDomainFiles(snapshot:ProfileSnapshot|ProfileSnapshotV2|BusinessAuthoringSnapshot,files:Readonly<Record<string,string>>,compilerPath:string):Readonly<Record<string,string>> {
 assertNativeSnapshot(snapshot);const executable=realpathSync(compilerPath),captured=nativeSnapshotFiles(snapshot).find(f=>f.key.startsWith('tool:')&&f.path===executable);
 if(!captured)reject('PROFILE_NATIVE_TOOL_UNPINNED','/','compiler entry must belong to selected tool manifest');
 const compilerManifest=JSON.parse(readFileSync(path.join(path.dirname(path.dirname(executable)),'package.json'),'utf8'));
 if(compilerManifest.name!=='typescript'||compilerManifest.version!=='6.0.3'||path.resolve(path.dirname(path.dirname(executable)),compilerManifest.bin?.tsc)!==executable)reject('PROFILE_NATIVE_COMPILER','/','declared TypeScript6.0.3 entry required');
 const data=captureJson(files) as Readonly<Record<string,string>>,stage=mkdtempSync(path.join(os.tmpdir(),'profile-domain-emit-')),out:Record<string,string>={...data},emitted:string[]=[];
 try{
  for(const [relative,body]of Object.entries(data)){if(path.isAbsolute(relative)||relative.includes('\\')||relative.split('/').some(p=>!p||p==='.'||p==='..'))reject('PROFILE_NATIVE_PATH',relative,'owned relative source path required');const file=path.join(stage,relative);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,body,{flag:'wx'});}
  const roots=Object.keys(data).filter(p=>p.endsWith('/domain/typescript/src/index.ts')).map(p=>p.slice(0,-'/index.ts'.length));
  const applications=Object.keys(data).filter(p=>/^applications\/[^/]+\/src\/profile-entry\.ts$/.test(p));
  if(!roots.length&&(!applications.length||!['craft.profile-project/v2-candidate','craft.business-authoring-project/v1-candidate'].includes(snapshot.project.schema_version)))reject('PROFILE_DOMAIN_PLAN_MISSING','/','captured domain or v2 application TypeScript entry required');
  for(const root of roots){const library=root.replace(/\/src$/,'/lib'),sources=Object.keys(data).filter(p=>p.startsWith(root+'/')&&p.endsWith('.ts')).sort();
   try{execFileSync(process.execPath,[executable,'--strict','--skipLibCheck','--target','ES2022','--module','commonjs','--declaration','--rootDir',path.join(stage,root),'--outDir',path.join(stage,library),...sources.map(p=>path.join(stage,p))],{cwd:stage,encoding:'utf8',stdio:['ignore','pipe','pipe']});}catch(error){reject('PROFILE_DOMAIN_COMPILE_FAILED',root,String((error as {stdout?:string}).stdout??error));}
   const collect=(folder:string)=>{for(const item of readdirSync(path.join(stage,folder),{withFileTypes:true})){const relative=folder+'/'+item.name;if(item.isDirectory())collect(relative);else{if(Object.hasOwn(out,relative))reject('PROFILE_RENDER_COLLISION',relative,'native output overlaps an existing owner');out[relative]=readFileSync(path.join(stage,relative),'utf8');if(relative.endsWith('.js'))emitted.push(relative);}}};collect(library);out[library+'/package.json']='{"type":"commonjs"}\n';
   const prefix=root.slice(0,-'domain/typescript/src'.length),runtimeSource=prefix+'runtime/boundary-source.ts',runtime=prefix+'runtime/boundary.mjs';
   if(!Object.hasOwn(data,runtimeSource))reject('PROFILE_RUNTIME_SOURCE_REQUIRED',runtime,'typed runtime source lineage required');
   const scratch=path.join(stage,'.runtime-emission');mkdirSync(scratch,{recursive:true});
   try{execFileSync(process.execPath,[executable,'--strict','--skipLibCheck','--target','ES2022','--module','ESNext','--moduleResolution','bundler','--declaration','--outDir',scratch,path.join(stage,runtimeSource)],{cwd:stage,encoding:'utf8',stdio:['ignore','pipe','pipe']});}catch(error){reject('PROFILE_RUNTIME_COMPILE_FAILED',runtimeSource,String((error as {stdout?:string}).stdout??error));}
   const emittedRuntime=readFileSync(path.join(scratch,'boundary-source.js'),'utf8');if(data[runtime]!==emittedRuntime)reject('PROFILE_RUNTIME_EMISSION_MISMATCH',runtime,'runtime must equal pinned native emission of captured typed source');
   out[runtime.replace(/\.mjs$/,'.d.mts')]=readFileSync(path.join(scratch,'boundary-source.d.ts'),'utf8');emitted.push(runtime);
  }
  // Emit the actual shared typed module once before checking its consumers.
  const sharedSources=Object.keys(data).filter(p=>/^runtime\/[^/]+\.mts$/.test(p));
  if(sharedSources.length){
   try{execFileSync(process.execPath,[executable,'--strict','--skipLibCheck','--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--declaration','--rootDir',path.join(stage,'runtime'),'--outDir',path.join(stage,'runtime/lib'),...sharedSources.map(p=>path.join(stage,p))],{cwd:stage,encoding:'utf8',stdio:['ignore','pipe','pipe']});}catch(error){reject('PROFILE_APPLICATION_TRANSPORT_COMPILE_FAILED','/runtime',String((error as {stdout?:string}).stdout??error));}
   for(const name of readdirSync(path.join(stage,'runtime/lib'))){const relative='runtime/lib/'+name;if(Object.hasOwn(out,relative))reject('PROFILE_RENDER_COLLISION',relative,'shared emission overlaps owned file');out[relative]=readFileSync(path.join(stage,relative),'utf8');if(relative.endsWith('.mjs'))emitted.push(relative);}
  }
  for(const entry of applications){const source=entry.slice(0,-'/profile-entry.ts'.length),library=source.replace(/\/src$/,'/lib'),sources=Object.keys(data).filter(p=>p.startsWith(source+'/')&&/\.(?:ts|mts)$/.test(p)).sort();
   try{execFileSync(process.execPath,[executable,'--strict','--skipLibCheck','--target','ES2022','--module','NodeNext','--moduleResolution','NodeNext','--declaration','--rootDir',path.join(stage,source),'--outDir',path.join(stage,library),...sources.map(p=>path.join(stage,p))],{cwd:stage,encoding:'utf8',stdio:['ignore','pipe','pipe']});}catch(error){reject('PROFILE_APPLICATION_COMPILE_FAILED',source,String((error as {stdout?:string}).stdout??error));}
   const collect=(folder:string)=>{for(const item of readdirSync(path.join(stage,folder),{withFileTypes:true})){const relative=folder+'/'+item.name;if(item.isDirectory())collect(relative);else{if(Object.hasOwn(out,relative))reject('PROFILE_RENDER_COLLISION',relative,'application native output overlaps another owner');out[relative]=readFileSync(path.join(stage,relative),'utf8');if(/\.(?:js|mjs)$/.test(relative))emitted.push(relative);}}};collect(library);out[library+'/package.json']='{"type":"module"}\n';
  }
  assertNativeSnapshot(snapshot);const result=Object.freeze(out);emissions.set(result,{snapshot,sha256:dataDigest(result),emitted:Object.freeze(emitted)});return result;
 }catch(error){if(isAuthoring(snapshot)&&error&&typeof error==='object'&&Object.isExtensible(error))Object.defineProperty(error,'scratch_path',{value:stage,enumerable:true});throw error;}finally{if(!isAuthoring(snapshot))rmSync(stage,{recursive:true,force:true});}
}
export function qualifyNativeFiles(snapshot:ProfileSnapshot|ProfileSnapshotV2|BusinessAuthoringSnapshot,files:Readonly<Record<string,string>>,compilerPath:string):NativeQualification {
 assertNativeSnapshot(snapshot);const data=captureJson(files) as Readonly<Record<string,string>>;
 if(Object.hasOwn(data,'native-config.json'))reject('PROFILE_NATIVE_RESERVED','/','checker configuration is core-owned');
 if(Object.values(data).some(v=>typeof v!=='string'))reject('PROFILE_NATIVE_FILES','/','UTF-8 file content required');
 const executable=realpathSync(compilerPath),root=path.dirname(path.dirname(executable)),manifest=JSON.parse(readFileSync(path.join(root,'package.json'),'utf8'));
 if(manifest.name!=='typescript'||manifest.version!=='6.0.3'||path.resolve(root,manifest.bin?.tsc)!==executable)reject('PROFILE_NATIVE_COMPILER','/','declared TypeScript6.0.3 entry required');
 const captured=nativeSnapshotFiles(snapshot).find(f=>f.key.startsWith('tool:')&&f.path===executable);if(!captured)reject('PROFILE_NATIVE_TOOL_UNPINNED','/','compiler entry must belong to selected tool manifest');
 assertNativeImportClosure(snapshot,data,compilerPath);
 const covered=Object.keys(data).filter(p=>/\.(?:ts|mts|cts|js|mjs|cjs)$/.test(p)&&!(/\.d\.(?:ts|mts|cts)$/.test(p))).sort();if(!covered.length)reject('PROFILE_NATIVE_COVERAGE','/','executable source files required');
 const emission=emissions.get(files);if(emission&&(emission.snapshot!==snapshot||emission.sha256!==dataDigest(data)))reject('PROFILE_NATIVE_EMISSION_STALE','/','exact registered native emissions required');const compilerOutputs=new Set(emission?.emitted??[]);
 const stage=mkdtempSync(path.join(os.tmpdir(),'profile-native-'));
 try{
  for(const [relative,body]of Object.entries(data)){if(path.isAbsolute(relative)||relative.includes('\\')||relative.split('/').some(p=>!p||p==='.'||p==='..'))reject('PROFILE_NATIVE_PATH',relative,'owned relative source path required');const file=path.join(stage,relative);mkdirSync(path.dirname(file),{recursive:true});writeFileSync(file,body,{flag:'wx'});}
  const configuration={compilerOptions:{noEmit:true,strict:true,noImplicitAny:false,useUnknownInCatchVariables:false,skipLibCheck:true,allowJs:true,checkJs:true,target:'ES2022',module:'NodeNext',moduleResolution:'NodeNext',resolveJsonModule:true,types:[],lib:['ES2022','DOM']},files:[...covered.filter(p=>!compilerOutputs.has(p)),...Object.keys(data).filter(p=>p.endsWith('.d.ts'))]};
  writeFileSync(path.join(stage,'native-config.json'),JSON.stringify(configuration));
  try{execFileSync(process.execPath,[executable,'-p',path.join(stage,'native-config.json')],{cwd:stage,encoding:'utf8',stdio:['ignore','pipe','pipe']});}catch(error){reject('PROFILE_NATIVE_CHECK_FAILED','/',String((error as {stdout?:string}).stdout??(error as Error).message));}
  assertNativeSnapshot(snapshot);const body={schema_version:'craft.profile-native-qualification/v1' as const,files_sha256:dataDigest(data),lock_sha256:snapshot.lock.lock_sha256,covered_files:Object.freeze(covered),checked_files:Object.freeze(configuration.files),typed_emissions:Object.freeze([...compilerOutputs].sort()),compiler_sha256:captured.sha256,module_mode:'NodeNext' as const};const result=Object.freeze({...body,receipt_sha256:dataDigest(body)});qualified.set(result,{snapshot,files:data});return result;
 }catch(error){if(isAuthoring(snapshot)&&error&&typeof error==='object'&&Object.isExtensible(error))Object.defineProperty(error,'scratch_path',{value:stage,enumerable:true});throw error;}finally{if(!isAuthoring(snapshot))rmSync(stage,{recursive:true,force:true});}
}
export function assertNativeQualificationCurrent(receipt:NativeQualification,files:Readonly<Record<string,string>>,snapshot:ProfileSnapshot|ProfileSnapshotV2|BusinessAuthoringSnapshot):void {
 const state=qualified.get(receipt);if(!state||state.snapshot!==snapshot||receipt.files_sha256!==dataDigest(files)||receipt.lock_sha256!==snapshot.lock.lock_sha256)reject('PROFILE_NATIVE_QUALIFICATION_UNREGISTERED_OR_STALE','/','use exact current in-process successful qualification');assertNativeSnapshot(snapshot);
}
