import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {assertReconciledProjectPlan,type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {assertCrossGeneratorWorkflowControls,crossGeneratorWorkflowBatchProbes,checkCrossGeneratorWorkflowObservations,type CrossGeneratorWorkflowControls} from './reconciled-cross-generator-workflow.js';
import {assertCrossGeneratorWorkflowAudit,type CrossGeneratorWorkflowAudit,CROSS_GENERATOR_WORKFLOW_MODULE_AUDIT_RUNNER,WORKFLOW_EFFECT_AUDIT_RUNNER,WORKFLOW_ORCHESTRATION_AUDIT_RUNNER} from './reconciled-cross-generator-workflow-audit.js';
import {CROSS_GENERATOR_WORKFLOW_RUNNER,CROSS_GENERATOR_WORKFLOW_OBSERVER_SHA256} from './reconciled-cross-generator-workflow-runner.js';
import {CROSS_GENERATOR_WORKFLOW_DEFINITION_SHA256} from './reconciled-cross-generator-workflow-surface.js';

export const CROSS_GENERATOR_WORKFLOW_EXECUTION_SHA256='66e993c2cfdaf6ea3d309264c3a6881f3e9885ad3d474103597d4d8b54573f6a';
export interface WorkflowExecutionOptions {workspace_parent:string;typescript_root:string;node_types_root:string;}
export class WorkflowRetainedExecutionError extends Error {
 constructor(readonly phase:string,reason:string,readonly workspace?:string){super('WORKFLOW_RETAINED_EXECUTION:'+phase+':'+reason);this.name='WorkflowRetainedExecutionError';}
}
const receipts=new WeakMap<object,()=>void>();
const same=(a:unknown,b:unknown,reason:string)=>{if(canonicalJson(a)!==canonicalJson(b))throw Error(reason);};
function absolute(p:string){
 if(typeof p!=='string'||!path.isAbsolute(p)||path.resolve(p)!==p||fs.realpathSync(p)!==p)throw Error('normalized nonsymbolic absolute path required');return p;
}
function read(file:string,maximum=268435456){
 absolute(file);const fd=fs.openSync(file,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW|fs.constants.O_NONBLOCK);
 try{const st=fs.fstatSync(fd);if(!st.isFile()||st.size>maximum)throw Error('bounded regular file required');
  const bytes=Buffer.alloc(st.size+1);let count=0;while(count<bytes.length){const n=fs.readSync(fd,bytes,count,bytes.length-count,null);if(!n)break;count+=n;}
  if(count!==st.size)throw Error('file changed during read');return bytes.subarray(0,count);
 }finally{fs.closeSync(fd);}
}
function tree(root:string){
 absolute(root);const result:Record<string,string>={};let total=0,entries=0;
 const walk=(dir:string)=>{for(const e of fs.readdirSync(dir,{withFileTypes:true}).sort((a,b)=>a.name<b.name?-1:1)){
  if(++entries>16384)throw Error('tree capacity');const file=path.join(dir,e.name);absolute(file);
  if(e.isDirectory()){result[file]='directory';walk(file);}else if(e.isFile()){const b=read(file);total+=b.length;if(total>536870912)throw Error('tree byte capacity');result[file]=sha256(b);}else throw Error('nonregular tree entry');
 }};walk(root);return result;
}
function freeze<T>(v:T):T{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
// Inspect package search paths afresh: Node may cache an earlier symlink resolution.
function packageLocation(origin:string,name:string){
 let dir=origin;
 for(let depth=0;depth<64;depth++){
  if(path.basename(dir)!=='node_modules'){
   const candidate=path.join(dir,'node_modules',name,'package.json');let present=false;
   try{fs.lstatSync(candidate);present=true;}catch(e){if((e as NodeJS.ErrnoException).code!=='ENOENT')throw e;}
   if(present){const file=fs.realpathSync(candidate);read(file);return {selection_path:candidate,root:absolute(path.dirname(file))};}
  }
  const parent=path.dirname(dir);if(parent===dir)break;dir=parent;
 }
 throw Error('missing package dependency: '+name);
}
/** Separate original ESM lane. Old CommonJS executor, profiles and generated source remain unchanged. */
export function executeCrossGeneratorWorkflow(plan:ReconciledProjectPlan,controls:CrossGeneratorWorkflowControls,auditProfile:CrossGeneratorWorkflowAudit,definition:string,surfaceDefinition:string,options:WorkflowExecutionOptions){
 let phase='preflight',workspace:string|undefined;
 try{
  const assertInputs=()=>{assertReconciledProjectPlan(plan);assertCrossGeneratorWorkflowControls(controls);assertCrossGeneratorWorkflowAudit(auditProfile);};
  assertInputs();
  if(typeof definition!=='string'||sha256(definition)!==CROSS_GENERATOR_WORKFLOW_EXECUTION_SHA256||typeof surfaceDefinition!=='string'||sha256(surfaceDefinition)!==CROSS_GENERATOR_WORKFLOW_DEFINITION_SHA256)throw Error('definition drift');
  same([plan.plan_sha256,controls.surface_sha256],[controls.project_plan_sha256,auditProfile.surface_sha256],'foreign plan or audit');
  same(plan.plan_sha256,auditProfile.project_plan_sha256,'foreign audit plan');
  if(!options||![Object.prototype,null].includes(Object.getPrototypeOf(options))||Reflect.ownKeys(options).length!==3||['workspace_parent','typescript_root','node_types_root'].some(k=>{const d=Object.getOwnPropertyDescriptor(options,k);return !d?.enumerable||!Object.hasOwn(d,'value')||typeof d.value!=='string';}))throw Error('closed data tool options');
  const selected={...options};Object.values(selected).forEach(absolute);
  const rows=controls.rows.filter(r=>r.state==='ready');if(!rows.length)throw Error('no ready Workflow families');
  const all=rows.flatMap(r=>r.modules),modules=[...new Map(all.map(m=>[m.relative_path,m])).values()].sort((a,b)=>a.relative_path<b.relative_path?-1:1);
  if(!modules.length||modules.length>8192)throw Error('module capacity');for(const m of all)same(m,modules.find(n=>n.relative_path===m.relative_path),'inconsistent shared module');
  const sources=modules.map(m=>{const a=plan.resolved.artifacts.find(a=>a.relative_path===m.relative_path);if(!a||sha256(a.content)!==m.sha256)throw Error('source artifact identity');return {relative_path:m.relative_path,content:a.content};});
  if(process.version!=='v26.8.1')throw Error('Node 26.8.1 required');
  const packagePath=path.join(selected.typescript_root,'package.json'),pkg=JSON.parse(read(packagePath).toString());
  if(pkg.name!=='typescript'||pkg.version!=='7.0.2')throw Error('TypeScript 7.0.2 required');
  const platformName='@typescript/typescript-'+process.platform+'-'+process.arch;
  const platform=()=>packageLocation(selected.typescript_root,platformName);
  const platformRoot=platform().root,platformPkg=JSON.parse(read(path.join(platformRoot,'package.json')).toString());
  same(platformRoot,path.dirname(createRequire(packagePath).resolve(platformName+'/package.json')),'platform resolution mismatch');
  if(platformPkg.name!==platformName||platformPkg.version!=='7.0.2')throw Error('platform package identity');
  const nodePackage=path.join(selected.node_types_root,'package.json'),nodePkg=JSON.parse(read(nodePackage).toString());
  if(nodePkg.name!=='@types/node'||nodePkg.version!=='26.4.0')throw Error('Node declarations 26.4.0 required');
  same(nodePkg.dependencies,{ 'undici-types':'~8.3.0'},'Node declaration dependency contract');
  const undici=()=>packageLocation(selected.node_types_root,'undici-types');
  const undiciRoot=undici().root,undiciPkg=JSON.parse(read(path.join(undiciRoot,'package.json')).toString());
  same(undiciRoot,path.dirname(createRequire(nodePackage).resolve('undici-types/package.json')),'declaration resolution mismatch');
  if(undiciPkg.name!=='undici-types'||undiciPkg.version!=='8.3.0'||Object.keys(undiciPkg.dependencies??{}).length)throw Error('Undici declaration dependency contract');
  const fingerprint=()=>({node:sha256(read(process.execPath)),typescript:tree(selected.typescript_root),platform_resolution:platform(),platform:tree(platformRoot),node_types:tree(selected.node_types_root),undici_resolution:undici(),undici:tree(undiciRoot)});
  const tools=fingerprint(),probes=crossGeneratorWorkflowBatchProbes(controls);
  workspace=fs.mkdtempSync(path.join(selected.workspace_parent,'ds-workflow-retained-'));absolute(workspace);
  const root=workspace,sourceRoot=path.join(root,'source'),nativeRoot=path.join(root,'native');fs.mkdirSync(sourceRoot);fs.mkdirSync(nativeRoot);
  const expected=new Map<string,string>([[sourceRoot,'directory'],[nativeRoot,'directory']]);
  const add=(relative:string,content:string|Buffer)=>{
   if(relative.includes('\\')||relative.includes('\0')||path.posix.isAbsolute(relative)||relative.split('/').some(p=>!p||p==='.'||p==='..'))throw Error('unsafe run path');
   const file=path.join(root,relative);fs.mkdirSync(path.dirname(file),{recursive:true,mode:0o700});
   let p=path.dirname(file);while(p!==root){expected.set(p,'directory');p=path.dirname(p);}
   fs.writeFileSync(file,content,{flag:'wx',mode:0o600});expected.set(file,sha256(content));return file;
  };
  const current=()=>{same(tree(root),Object.fromEntries(expected),'run artifact changed or unexpected');same(fingerprint(),tools,'toolchain or declaration dependency changed');assertInputs();};
  const run=(args:string[],maximum=16777216)=>{
   const r=spawnSync(process.execPath,args,{cwd:root,env:{LANG:'C',TZ:'UTC'},encoding:'utf8',timeout:60000,maxBuffer:maximum});
   if(r.error||r.status!==0)throw Error((r.error?.message||r.stderr||r.stdout||'exit '+r.status).slice(0,4096));return r.stdout;
  };
  phase='source-materialization';sources.forEach(s=>add('source/'+s.relative_path,s.content));add('package.json','{"type":"module"}\n');
  // Compile against captured declarations, not ambient package lookup. Original trees remain in custody.
  for(const [origin,files,destination] of [[selected.node_types_root,tools.node_types,'declarations/node_modules/@types/node'],[undiciRoot,tools.undici,'declarations/node_modules/undici-types']] as const){
   for(const [file,h] of Object.entries(files))if(h!=='directory'){const bytes=read(file);if(sha256(bytes)!==h)throw Error('declaration changed during capture');add(destination+'/'+path.relative(origin,file).split(path.sep).join('/'),bytes);}
  }
  const compilerOptions={strict:true,skipLibCheck:false,types:['node'],typeRoots:[path.join(root,'declarations/node_modules/@types')],target:'ES2022',module:'NodeNext',moduleResolution:'NodeNext',rootDir:sourceRoot,outDir:nativeRoot};
  const config=add('compiler.json',canonicalJson({compilerOptions,files:sources.map(s=>path.join(sourceRoot,s.relative_path))}));
  const scripts={module:add('module-audit.mjs',CROSS_GENERATOR_WORKFLOW_MODULE_AUDIT_RUNNER),effects:add('effects-audit.mjs',WORKFLOW_EFFECT_AUDIT_RUNNER),orchestration:add('orchestration-audit.mjs',WORKFLOW_ORCHESTRATION_AUDIT_RUNNER)};
  const runner=add('observer.mjs',CROSS_GENERATOR_WORKFLOW_RUNNER),auditHashes:Record<string,string>={};
  const audit=(stage:'source'|'native')=>{
   const moduleRoot=stage==='source'?sourceRoot:nativeRoot,phasePath=(p:string)=>stage==='source'?p:p.replace(/\.ts$/,'.js');
   const auditConfig=add(stage+'-audit-config.json',canonicalJson({compilerOptions:{...compilerOptions,rootDir:moduleRoot,allowJs:true,checkJs:false,noEmit:true},files:modules.map(m=>path.join(moduleRoot,phasePath(m.relative_path)))}));
   for(const facet of ['module','effects','orchestration'] as const){
    phase=stage+'-'+facet+'-audit';
    const sourceProfile=facet==='module'?{module_paths:modules.map(m=>m.relative_path),modules,support_modules:modules.filter(m=>m.role==='enum-runtime').map(m=>({relative_path:m.relative_path,source_sha256:m.sha256}))}:auditProfile[facet];
    // Non-ready rows are not observed; retain the exact applicable profile members, never fabricate them.
    const paths=sourceProfile.module_paths.filter(p=>modules.some(m=>m.relative_path===p));
    const selectedProfile={...sourceProfile,...('workflow_modules' in sourceProfile?{workflow_modules:sourceProfile.workflow_modules.filter(m=>paths.includes(m.relative_path))}:{}),...('support_modules' in sourceProfile?{support_modules:sourceProfile.support_modules.filter(m=>paths.includes(m.relative_path))}:{})};
    const auditDefinition=facet==='module'?surfaceDefinition:auditProfile.definitions[facet];
    const input=add(stage+'-'+facet+'-audit-input.json',canonicalJson({...selectedProfile,definition:auditDefinition,phase:stage,module_root:moduleRoot,module_paths:paths.map(phasePath)}));
    current();const output=run([scripts[facet],selected.typescript_root,auditConfig,input]);current();
    const wanted={schema_version:facet==='module'?'domainspec.cross-generator-module-observation/v1-candidate':facet==='effects'?'domainspec.workflow-effect-observation/v1-candidate':'domainspec.workflow-orchestration-observation/v1-candidate',phase:stage,definition_sha256:sha256(auditDefinition),
     modules:paths.map(p=>{
      const m=modules.find(m=>m.relative_path===p)!;
      return {relative_path:phasePath(p),source_sha256:expected.get(path.join(moduleRoot,phasePath(p))),...(facet==='module'?{imports:m.imports.filter(i=>stage==='source'||!i.type_only).map(i=>({specifier:i.specifier,names:i.names,...(i.namespace?{namespace:true}:{}),...(stage==='source'&&i.type_only?{type_only:true}:{}),...(stage==='source'&&i.reexport?{reexport:true}:{})})).sort((a,b)=>a.specifier<b.specifier?-1:a.specifier>b.specifier?1:0),exports:[...m.value_exports,...(stage==='source'?m.type_exports:[])].sort()}:{}),violations:[]};
     })};
    same(JSON.parse(output),wanted,'independent '+facet+' audit mismatch');add(stage+'-'+facet+'-audit-observation.json',output);auditHashes[stage+':'+facet]=sha256(output);
   }
  };
  audit('source');phase='strict-native-compilation';current();run([path.join(selected.typescript_root,'bin/tsc'),'--project',config,'--pretty','false']);
  let nativeBytes=0;
  const nativeModules=modules.map(m=>{
   const relative_path=m.relative_path.replace(/\.ts$/,'.js'),file=path.join(nativeRoot,relative_path),bytes=read(file);nativeBytes+=bytes.length;if(nativeBytes>67108864)throw Error('native byte capacity');
   let p=path.dirname(file);while(p!==root){expected.set(p,'directory');p=path.dirname(p);}
   const hash=sha256(bytes);expected.set(file,hash);return {relative_path,sha256:hash};
  });current();audit('native');
  phase='native-behavior';const observedRows:any[]=[],batchRecords:{selector:string;inputs:string[];outputs:string[]}[]=[];
  for(const [rowIndex,row] of rows.entries()){
   const selectedProbes=probes.filter(p=>p.rows[0]!.selector===row.selector);same(selectedProbes.map(p=>p.batch),row.batches,'incomplete batch plan');
   const files=selectedProbes.map((p,i)=>{const value=canonicalJson(p);if(Buffer.byteLength(value)>8388608)throw Error('input batch capacity');return add('families/'+rowIndex+'/batch-'+i+'.json',value);});
   const manifest=add('families/'+rowIndex+'/manifest.json',canonicalJson(files));current();
   const output=run(['--experimental-vm-modules','--permission','--allow-fs-read='+root,'--disable-proto=throw','--max-old-space-size=256',runner,manifest,nativeRoot],33554432);current();
   if(Buffer.byteLength(output)>33554432||!output.endsWith('\n'))throw Error('output family capacity or framing');
   const lines=output.slice(0,-1).split('\n');if(lines.length!==files.length)throw Error('incomplete batch observations');
   const batches=lines.map((line,i)=>{
    if(Buffer.byteLength(line)>8388608)throw Error('output batch capacity');const b=JSON.parse(line);
    same(Object.keys(b).sort(),['controls_sha256','selector','identity','descriptor','material_descriptor','batch','cases'].sort(),'batch observation envelope');
    same([b.controls_sha256,b.selector,b.batch,b.identity,b.descriptor,b.material_descriptor],[controls.controls_sha256,row.selector,row.batches[i],row.identity,row.descriptor,row.material_descriptor],'batch observation identity');
    add('families/'+rowIndex+'/observation-'+i+'.json',line+'\n');return b;
   });
   batchRecords.push({selector:row.selector,inputs:files.map(file=>expected.get(file)!),outputs:lines.map(line=>sha256(line+'\n'))});
   observedRows.push({selector:row.selector,identity:batches[0].identity,descriptor:batches[0].descriptor,material_descriptor:batches[0].material_descriptor,batches:batches.map(b=>b.batch),cases:batches.flatMap(b=>b.cases)});
  }
  const observations={controls_sha256:controls.controls_sha256,rows:observedRows},outcome=checkCrossGeneratorWorkflowObservations(controls,observations);
  const observationHash=sha256(canonicalJson(observations));add('observation-index.json',canonicalJson({observation_sha256:observationHash,families:batchRecords}));
  phase='final-currentness';current();
  const result=freeze({schema_version:'domainspec.cross-generator-workflow-execution/v1-candidate' as const,result:'pass' as const,definition_sha256:CROSS_GENERATOR_WORKFLOW_EXECUTION_SHA256,observer_sha256:CROSS_GENERATOR_WORKFLOW_OBSERVER_SHA256,project_plan_sha256:plan.plan_sha256,controls_sha256:controls.controls_sha256,surface_sha256:controls.surface_sha256,protocol_sha256:controls.protocol_sha256,cases_definition_sha256:controls.cases_definition_sha256,audit_sha256:auditProfile.audit_sha256,workspace:root,outcome,native_modules:nativeModules,audits:auditHashes,families:batchRecords,observation_sha256:observationHash,files:Object.fromEntries(expected),tool_files:tools,authority_effect:'none' as const,claim_scope:'finite-private-retained-original-workflow-esm-not-whole-project' as const});
  receipts.set(result,current);return result;
 }catch(e){throw new WorkflowRetainedExecutionError(phase,e instanceof Error?e.message:String(e),workspace);}
}
export type CrossGeneratorWorkflowExecution=ReturnType<typeof executeCrossGeneratorWorkflow>;
export function assertCrossGeneratorWorkflowExecutionCurrent(value:unknown):asserts value is CrossGeneratorWorkflowExecution{
 if(!value||typeof value!=='object'||!receipts.has(value))throw new WorkflowRetainedExecutionError('receipt','registered execution required');
 try{receipts.get(value)!();}catch(e){throw new WorkflowRetainedExecutionError('currentness',e instanceof Error?e.message:String(e));}
}
