import {workflowVerificationDefinitions} from './reconciled-workflow-controls.js';
import {createWorkflowEffectAudit, WORKFLOW_EFFECT_AUDIT_RUNNER} from './reconciled-workflow-effect-audit.js';
import {createWorkflowOrchestrationAudit, WORKFLOW_ORCHESTRATION_AUDIT_RUNNER} from './reconciled-workflow-orchestration-audit.js';
import {createOperationEffectAudit} from './reconciled-operation-controls.js';
import {OPERATION_EFFECT_AUDIT_RUNNER} from './reconciled-operation-effect-audit.js';
import {createInterfaceEffectAudit} from './reconciled-interface-controls.js';
import {INTERFACE_EFFECT_AUDIT_RUNNER} from './reconciled-interface-effect-audit.js';
import {createQueryEffectAudit} from './reconciled-query-controls.js';
import {QUERY_EFFECT_AUDIT_RUNNER} from './reconciled-query-effect-audit.js';
import {createMappingEffectAudit} from './reconciled-mapping-controls.js';
import {MAPPING_EFFECT_AUDIT_RUNNER} from './reconciled-mapping-effect-audit.js';
import {createEventEffectAudit,EVENT_EFFECT_AUDIT_RUNNER} from './reconciled-event-controls.js';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {loadCompiledProjectGraph,type CompiledProjectGraph} from '../input/project-model.js';
import {MAX_SOURCE_FILE_BYTES,SUBPROCESS_TIMEOUT_MS} from '../input/limits.js';
import {canonicalJson,sha256} from '../input/source-manifest.js';
import {planCompiledReconciledProject,type ReconciledProjectPlan} from '../generation/reconciled-project.js';
import {verifyReconciledProject} from '../generation/reconciled-output.js';
import {createReconciledVerificationProjection} from './reconciled-projection.js';
import {createReconciledFormalization} from '../formalization/reconciled.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {createReconciledArtifactCoverage} from './reconciled-artifacts.js';
import {validateResolvedCompositionBindings} from '../generation/resolved-composition-bindings.js';
import {assertReconciledOutputLayout} from '../generation/reconciled-output-layout.js';
import type {OutputLayout} from '../generation/output-layout.js';
import {createReconciledSemanticControls,semanticModulePaths,renderSemanticCases,checkSemanticObservations,SEMANTIC_RUNNER} from './reconciled-semantic-controls.js';
import {createStateMachineEffectAudit,STATE_MACHINE_EFFECT_AUDIT_RUNNER} from './reconciled-state-machine-effect-audit.js';
import {getReconciledSource} from '../generation/reconciled-sources.js';
import {createPublicCompositionControls, COMPOSITION_PUBLIC_DEFINITION_SHA256} from './reconciled-composition-public.js';
import {executeCompositionControls, assertCompositionExecutionCurrent, CompositionExecutionError, type CompositionExecution} from './reconciled-composition-execution.js';
import {prepareCrossGeneratorVerification} from './reconciled-cross-generator-public.js';
import {executePreparedCrossGeneratorVerification, assertCrossGeneratorAggregateCurrent, type CrossGeneratorAggregateExecution} from './reconciled-cross-generator-public-execution.js';
import {bindRetainedWorkflowPublicEvidence, assertWorkflowPublicEvidenceCurrent, type WorkflowPublicEvidence} from './reconciled-workflow-public-evidence.js';

export const RECONCILED_VERIFICATION_EXECUTION_DEFINITION_SHA256='fa1a0f5e5706f0406893fcbbef514caec5436e7d8738cb49d353753edc335dba';
export interface ReconciledVerificationTools {
 readonly typescript_root:string;
 readonly node_type_root:string;
 readonly lean_executable:string;
 readonly target_root?:string;
 readonly output_layout?:OutputLayout;
}
export interface ReconciledExecutedCheck {
 readonly id:string; readonly required:true; readonly executed:boolean;
 readonly result:'pass'|'fail'|'not_evaluable'; readonly reason:string;
 readonly blocked_by:readonly string[]; readonly evidence:Readonly<Record<string,unknown>>;
}
export class ReconciledVerificationExecutionError extends Error {
 readonly exitCode=22;readonly code='DS_RECONCILED_VERIFICATION_EXECUTION';
 constructor(message:string){super('DS_RECONCILED_VERIFICATION_EXECUTION:'+message);this.name='ReconciledVerificationExecutionError';}
}
const registered=new WeakSet<object>();
function freeze<T>(v:T):T{if(v&&typeof v==='object'&&!Object.isFrozen(v)){Object.values(v).forEach(freeze);Object.freeze(v);}return v;}
function fail(message:string):never{throw new ReconciledVerificationExecutionError(message);}
function absolute(v:unknown):string{if(typeof v!=='string'||!path.isAbsolute(v)||path.resolve(v)!==v)fail('normalized absolute path required');return v;}
export function validateReconciledVerificationTools(value:unknown):ReconciledVerificationTools{
 assertInterfaceData(value);
 if(!value||typeof value!=='object'||Array.isArray(value))fail('closed tool options required');
 const row=value as Record<string,unknown>,names=['typescript_root','node_type_root','lean_executable'];
 if(names.some(n=>!Object.hasOwn(row,n))||Object.keys(row).some(n=>![...names,'target_root','output_layout'].includes(n)))fail('closed tool options required');
 for(const [name,v] of Object.entries(row))if(name!=='output_layout')absolute(v);
 assertReconciledOutputLayout(row.output_layout);
 return Object.freeze({...row}) as unknown as ReconciledVerificationTools;
}
function readRegular(file:string,limit=MAX_SOURCE_FILE_BYTES):Buffer{
 if(fs.realpathSync(file)!==file)fail('symbolic source or artifact path');
 const fd=fs.openSync(file,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW|fs.constants.O_NONBLOCK);
 try{
  const st=fs.fstatSync(fd);if(!st.isFile()||st.size>limit)fail('bounded regular file required');
  const data=Buffer.alloc(st.size+1);let offset=0;
  while(offset<data.length){const n=fs.readSync(fd,data,offset,data.length-offset,null);if(!n)break;offset+=n;}
  if(offset!==st.size)fail('file changed during read');return data.subarray(0,offset);
 }finally{fs.closeSync(fd);}
}
function write(root:string,relative:string,content:string|Buffer):string{
 if(path.posix.normalize(relative)!==relative||path.posix.isAbsolute(relative)||relative.includes('\\')||relative.split('/').some(x=>!x||x==='.'||x==='..'))fail('unsafe run artifact path');
 const file=path.join(root,relative);fs.mkdirSync(path.dirname(file),{recursive:true,mode:0o700});fs.writeFileSync(file,content,{flag:'wx',mode:0o600});return file;
}
function cleanEnvironment():NodeJS.ProcessEnv{
 const env={...process.env};delete env.NODE_OPTIONS;delete env.NODE_PATH;delete env.LEAN_SYSROOT;delete env.LEAN_SRC_PATH;env.LEAN_PATH='';return env;
}
function run(command:string,args:readonly string[],cwd:string):string{
 const result=spawnSync(command,[...args],{cwd,env:cleanEnvironment(),encoding:'utf8',timeout:SUBPROCESS_TIMEOUT_MS,maxBuffer:32*1024*1024});
 if(result.error||result.status!==0)fail('validator rejected: '+(result.error?.message||result.stderr||result.stdout||'exit '+result.status).slice(0,4096));
 return result.stdout;
}

// This independent observer uses the native compiler AST, not the planner tokenizer.
const observer=String.raw`
import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';
const [root,config]=process.argv.slice(2);
const {API}=await import(pathToFileURL(path.join(root,'dist/api/sync/api.js')).href);
const {SyntaxKind:K}=await import(pathToFileURL(path.join(root,'dist/ast/index.js')).href);
const settings=JSON.parse(fs.readFileSync(config,'utf8')),api=new API({cwd:path.dirname(config)});
try{
 const snapshot=api.updateSnapshot({openProjects:[config]}),project=snapshot.getProject(config),result=[];
 if(!project)throw Error('missing native project');
 for(const relative_path of settings.files){
  const file=path.resolve(path.dirname(config),relative_path),source=project.program.getSourceFile(file);
  if(!source||project.program.getSyntacticDiagnostics(file).length)throw Error('native syntax failure');
  const imports=[],exports=[];
  for(const s of source.statements){
   const exported=s.modifiers?.some(m=>m.kind===K.ExportKeyword);
   if(s.kind===K.ImportDeclaration){
    const c=s.importClause,b=c?.namedBindings;if(c?.name)throw Error('unexpected default import');
    imports.push({specifier:s.moduleSpecifier.text,names:(b?.elements??[]).map(x=>(x.propertyName??x.name).getText()).sort(),namespace:b?.kind===K.NamespaceImport,type_only:c?.isTypeOnly===true,reexport:false});
   }else if(s.kind===K.ExportDeclaration){
    const elements=s.exportClause?.elements;if(!elements)throw Error('unsupported export declaration');
    for(const e of elements)exports.push({name:e.name.getText(),kind:s.isTypeOnly||e.isTypeOnly?'type':'value'});
    if(s.moduleSpecifier)imports.push({specifier:s.moduleSpecifier.text,names:elements.map(e=>(e.propertyName??e.name).getText()).sort(),namespace:false,type_only:s.isTypeOnly===true,reexport:true});
   }else if(exported){
    if(s.kind===K.VariableStatement)for(const d of s.declarationList.declarations)exports.push({name:d.name.getText(),kind:'value'});
    else if([K.InterfaceDeclaration,K.TypeAliasDeclaration,K.FunctionDeclaration,K.ClassDeclaration,K.EnumDeclaration].includes(s.kind))exports.push({name:s.name.getText(),kind:[K.InterfaceDeclaration,K.TypeAliasDeclaration].includes(s.kind)?'type':'value'});
    else throw Error('unknown native export');
   }
  }
  exports.sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:a.kind<b.kind?-1:1);result.push({relative_path,imports,exports});
 }
 snapshot.dispose();process.stdout.write(JSON.stringify(result));
}finally{api.close();}
`;

/** Runs trusted validators and bounded semantic controls. Operations use explicit
 * run-local fixture ports only, never a production store or target publisher. */
export function executeReconciledVerification(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,toolOptions:ReconciledVerificationTools){
 const input=createReconciledVerificationProjection(graph,plan),selected=validateReconciledVerificationTools(toolOptions);
 const coverage=createReconciledArtifactCoverage(plan);
 const semantic=createReconciledSemanticControls(graph,plan),semanticPaths=semanticModulePaths(semantic);
 const crossGeneratorPreparation=prepareCrossGeneratorVerification(graph,plan);
 let crossGeneratorExecution:CrossGeneratorAggregateExecution|undefined;
 let workflowEvidence:WorkflowPublicEvidence|undefined;
 let publicEpochCurrent:(()=>void)|undefined;
 const workflowCount=graph.nodes.filter(n=>n.kind==='Workflow').length;
 const workflowDefinitions=workflowVerificationDefinitions();
 const effectProfiles=[
  {...createWorkflowEffectAudit(graph,plan,workflowDefinitions.binding,workflowDefinitions.effects),key:'workflow',kind:'Workflow',definition_source:'workflow_effect_audit' as const,observer:WORKFLOW_EFFECT_AUDIT_RUNNER,diagnostic:'WORKFLOW_EFFECT_AUDIT'},
  {...createWorkflowOrchestrationAudit(graph,plan,workflowDefinitions),key:'workflow-orchestration',kind:'Workflow',definition_source:'workflow_orchestration_audit' as const,observer:WORKFLOW_ORCHESTRATION_AUDIT_RUNNER,diagnostic:'WORKFLOW_ORCHESTRATION',schema:'domainspec.workflow-orchestration-observation/v1-candidate',claim_scope:'source-bound-orchestration-structure-not-universal-behavior'},
  {...createOperationEffectAudit(graph,plan),key:'operation',kind:'Operation',definition_source:'semantic_operation_controls' as const,observer:OPERATION_EFFECT_AUDIT_RUNNER,diagnostic:'OPERATION_EFFECT_AUDIT'},
  {...createInterfaceEffectAudit(graph,plan),key:'interface',kind:'Interface',definition_source:'semantic_interface_controls' as const,observer:INTERFACE_EFFECT_AUDIT_RUNNER,diagnostic:'INTERFACE_EFFECT_AUDIT'},
  {...createQueryEffectAudit(graph,plan),key:'query',kind:'Query',definition_source:'semantic_query_controls' as const,observer:QUERY_EFFECT_AUDIT_RUNNER,diagnostic:'QUERY_EFFECT_AUDIT'},
  {...createMappingEffectAudit(graph,plan),key:'mapping',kind:'Mapping',definition_source:'semantic_mapping_controls' as const,observer:MAPPING_EFFECT_AUDIT_RUNNER,diagnostic:'MAPPING_EFFECT_AUDIT'},
  {...createStateMachineEffectAudit(graph,plan),key:'state-machine',kind:'State Machine',definition_source:'state_machine_effect_audit' as const,observer:STATE_MACHINE_EFFECT_AUDIT_RUNNER,diagnostic:'STATE_MACHINE_EFFECT_AUDIT'},
  {...createEventEffectAudit(graph,plan),key:'event',kind:'Event',definition_source:'semantic_event_controls' as const,observer:EVENT_EFFECT_AUDIT_RUNNER,diagnostic:'EVENT_EFFECT_AUDIT'},
 ].map(a=>{const rows=semantic.rows.filter(r=>r.state==='ready'&&r.kind===a.kind),structural=a.key==='workflow-orchestration';return {...a,rows,
  native_paths:[...new Set(rows.flatMap(r=>r.state==='ready'?[...r.module_paths]:[]))].filter(p=>a.module_paths.includes(p)).sort(),
  schema:'schema' in a?a.schema:'domainspec.'+a.key+'-effect-observation/v1-candidate',claim_scope:'claim_scope' in a?a.claim_scope:'selected-syntactic-effect-restrictions-not-universal-purity',
  source_id:structural?'workflow-source-orchestration-audit':a.key+'-source-effect-audit',native_id:structural?'workflow-native-orchestration-audit':a.key+'-native-effect-audit',current_id:structural?'workflow-orchestration-audit-currentness':a.key+'-effect-audit-currentness'};}).filter(a=>a.roots.length);
 type EffectProfile=typeof effectProfiles[number];
 const crossGeneratorDependencies=['source-currentness','isolated-exact-source-replay','strict-native-compilation','independent-module-surface-observation','toolchain-currentness',...effectProfiles.flatMap(a=>[a.source_id,...(a.native_paths.length?[a.native_id]:[])])];
 const extra=['lean-structural-kernel','verification-workspace-currentness','toolchain-currentness','verification-workspace-cleanup','cross-generator-currentness'];
 if(workflowCount)extra.push('workflow-public-evidence-binding','workflow-public-evidence-currentness');
 if(semantic.ready_count)extra.push('semantic-workspace-currentness');
 if(plan.composition)extra.push('composition-behavior-currentness');
 for(const a of effectProfiles)extra.push(a.source_id,a.native_id,a.current_id);
 const checks=new Map<string,ReconciledExecutedCheck>([...input.evidence_requirements.map(r=>r.id),...extra].map(id=>[id,{id,required:true,executed:false,result:'not_evaluable',reason:'check not executed',blocked_by:[],evidence:{}}]));
 const put=(id:string,result:ReconciledExecutedCheck['result'],reason:string,evidence:Record<string,unknown>={},executed=true,blocked_by:string[]=[])=>checks.set(id,{id,required:true,executed,result,reason,evidence,blocked_by});
 const attempt=(id:string,action:()=>Record<string,unknown>,dependencies:string[]=[]):boolean=>{
  // A verification run cannot recover authority from a transient observed
  // failure by reading restored bytes later in the same run.
  if(checks.get(id)?.result==='fail')return false;
  const blocked=dependencies.filter(id=>checks.get(id)?.result!=='pass');
  if(blocked.length){put(id,'not_evaluable','prerequisite did not pass',{},false,blocked);return false;}
  try{put(id,'pass','observed check passed',action());return true;}
  catch(error){put(id,'fail',error instanceof Error?error.message:String(error));return false;}
 };
 const finish=()=>{
  const prerequisites:Record<string,string[]>={
   'cross-generator-behavior':[...crossGeneratorDependencies,'verification-workspace-currentness','cross-generator-currentness','verification-workspace-cleanup',...(selected.target_root?['exact-output-currentness']:[])],
   'strict-native-compilation':['source-currentness','isolated-exact-source-replay','toolchain-currentness','verification-workspace-currentness'],
   'independent-module-surface-observation':['strict-native-compilation'],
   'lean-structural-kernel':['source-currentness','isolated-exact-source-replay','toolchain-currentness','successor-formalization-currentness'],
   'source-and-selection-preservation':['lean-structural-kernel'],
   'successor-formalization-currentness':['lean-structural-kernel','source-and-selection-preservation'],
   'exact-output-currentness':['source-currentness'],
   ...Object.fromEntries(effectProfiles.flatMap(a=>[[a.source_id,['source-currentness','isolated-exact-source-replay','strict-native-compilation','independent-module-surface-observation','toolchain-currentness','verification-workspace-currentness',a.current_id]],[a.native_id,[a.source_id,'semantic-workspace-currentness',a.current_id]]])),
   ...(semantic.ready_count?{'selected-generator-semantic-controls':['source-currentness','isolated-exact-source-replay','strict-native-compilation','independent-module-surface-observation','toolchain-currentness','verification-workspace-currentness','semantic-workspace-currentness',...effectProfiles.flatMap(a=>a.native_paths.length?[a.native_id]:[])]}:{}),
   ...(coverage.javascript_paths.length?{'generated-javascript-syntax':['source-currentness','isolated-exact-source-replay','toolchain-currentness','verification-workspace-currentness']}:{}),
   ...(plan.composition?{'composition-source-preservation':['source-currentness','isolated-exact-source-replay','source-and-selection-preservation','verification-workspace-currentness'],'selected-calculation-bindings':['composition-source-preservation','strict-native-compilation','independent-module-surface-observation','generated-javascript-syntax'],
    'composition-behavior-controls':['source-currentness','isolated-exact-source-replay','selected-calculation-bindings','toolchain-currentness','verification-workspace-currentness','composition-behavior-currentness','verification-workspace-cleanup',...(selected.target_root?['exact-output-currentness']:[])]}:{}),
  };
  // Revisit dependencies after final currentness checks; earlier observations are
  // not passing evidence when a dependency changed later in the same run.
  let changed=true;
  while(changed){changed=false;for(const [id,deps] of Object.entries(prerequisites)){
   const check=checks.get(id)!,blocked=deps.filter(dep=>checks.get(dep)?.result!=='pass');
   if(blocked.length&&(check.result==='pass'||['selected-generator-semantic-controls','cross-generator-behavior'].includes(id)&&check.executed&&check.result==='not_evaluable'&&canonicalJson(check.blocked_by)!==canonicalJson(blocked))){put(id,'not_evaluable','final prerequisite did not pass',check.evidence as Record<string,unknown>,check.executed,blocked);changed=true;}
  }}
  // Close original artifact prerequisites first. Cross-generator execution used
  // these original checks, not the alternate fulfillment it can later supply.
  const baseline=new Map(checks),originalSemantic=baseline.get('selected-generator-semantic-controls')!;
  const workflowProfiles=effectProfiles.filter(a=>a.kind==='Workflow');
  const standaloneChecks=[originalSemantic,...workflowProfiles.flatMap(a=>[baseline.get(a.source_id)!,baseline.get(a.native_id)!,baseline.get(a.current_id)!])];
  const retainedPrerequisites=['source-currentness','isolated-exact-source-replay','strict-native-compilation','independent-module-surface-observation','toolchain-currentness','verification-workspace-currentness',
   'workflow-public-evidence-binding','workflow-public-evidence-currentness','cross-generator-currentness','verification-workspace-cleanup',
   ...(semantic.ready_count?['semantic-workspace-currentness']:[]),...(selected.target_root?['exact-output-currentness']:[]),...workflowProfiles.flatMap(a=>[a.source_id,a.current_id])];
  const retainedBlocked=workflowCount?retainedPrerequisites.filter(id=>baseline.get(id)?.result!=='pass'):[];
  const retainedUsable=!!workflowEvidence&&!retainedBlocked.length;
  const standaloneObserved=originalSemantic.executed&&originalSemantic.result!=='fail'&&!originalSemantic.blocked_by.length&&Array.isArray(originalSemantic.evidence.tested);
  const tested=standaloneObserved?originalSemantic.evidence.tested as {selector:string;kind:string;contract_sha256:string;case_count:number}[]:[];
  const standaloneRow=(selector:string)=>{
   const row=semantic.rows.find(r=>r.selector===selector);
   return !!row&&row.state==='ready'&&tested.some(t=>t.selector===row.selector&&t.kind===row.kind&&t.contract_sha256===row.contract_sha256&&t.case_count===row.cases.length);
  };
  const retainedRow=(selector:string)=>{
   const row=workflowEvidence?.rows.find(r=>r.selector===selector);
   return retainedUsable&&row?.retained_status==='observed'&&row.required_source_paths.length>0&&workflowEvidence!.facets.every(f=>
    f.required_source_paths.filter(p=>row.required_source_paths.includes(p)).every(p=>f.observed.some(o=>o.source_path===p)));
  };
  const auditFulfillment=workflowProfiles.map(a=>{
   const original=baseline.get(a.native_id)!,facet=workflowEvidence?.facets.find(f=>f.facet===(a.key==='workflow-orchestration'?'native:orchestration':'native:effects'));
   const standalone=original.result==='pass'?(original.evidence.modules as {relative_path:string;source_sha256:string}[]).map(m=>{
    const source_path=m.relative_path.replace(/\.js$/,'.ts'),artifact=plan.resolved.artifacts.find(p=>p.relative_path===source_path)!;
    return {source_path,source_sha256:sha256(artifact.content),artifact_path:path.join(original.evidence.module_root as string,m.relative_path),artifact_sha256:m.source_sha256,origin:'original-standalone-native'};
   }):[];
   const retained=retainedUsable?facet?.observed??[]:[];
   const origins=[...standalone,...retained];
   const missingPaths=a.module_paths.filter(p=>!origins.some(o=>o.source_path===p));
   // A shared dependency is not evidence that an unavailable Workflow ran.
   const missingRoots=a.roots.filter(selector=>!(original.result==='pass'&&a.rows.some(r=>r.selector===selector))&&!retainedRow(selector));
   const result=original.result==='fail'?'fail' as const:!missingPaths.length&&!missingRoots.length?'pass' as const:'not_evaluable' as const;
   const evidence={...original.evidence,scope:'complete-source-workflow-audit-path-and-root-union',definition_sha256:a.definition_sha256,
    required_source_paths:a.module_paths,required_workflow_selectors:a.roots,origins,missing_source_paths:missingPaths,missing_workflow_selectors:missingRoots,
    original_standalone_result:original.result,retained_binding_sha256:workflowEvidence?.binding_sha256??null};
   if(original.result!=='fail')put(a.native_id,result,result==='pass'?'complete Workflow audit obligations observed across explicit artifact origins':'Workflow audit paths or source roots remain unavailable',
    evidence,original.executed||retained.length>0,result==='pass'?[]:[...new Set([...original.blocked_by,...retainedBlocked])]);
   return {id:a.native_id,result,evidence};
  });
  const fulfillmentRows=semantic.rows.map(row=>{
   const standalone=standaloneRow(row.selector),retained=row.kind==='Workflow'&&retainedRow(row.selector);
   return {selector:row.selector,kind:row.kind,result:standalone||retained?'pass' as const:'not_evaluable' as const,
    origins:[...(standalone?['original-standalone-native']:[]),...(retained?['original-retained-workflow']:[])],
    standalone_adapter_status:row.state,retained_workflow_status:row.kind==='Workflow'?workflowEvidence?.rows.find(r=>r.selector===row.selector)?.retained_status??'not_evaluable': 'inapplicable',
    reason:standalone||retained?null:row.state==='not_evaluable'?row.reason:'original standalone observation or prerequisites unavailable'};
  });
  if(workflowCount&&originalSemantic.result!=='fail'){
   const missing=fulfillmentRows.filter(r=>r.result!=='pass'),auditBlocked=workflowProfiles.map(a=>a.native_id).filter(id=>checks.get(id)?.result!=='pass');
   const result=!missing.length&&!auditBlocked.length?'pass':'not_evaluable';
   put('selected-generator-semantic-controls',result,result==='pass'?'every source node has complete applicable semantic evidence':'source semantic or Workflow audit obligations remain unavailable',
    {...originalSemantic.evidence,evidence_scope:'original-standalone-fields-plus-source-obligation-fulfillment',fulfilled_node_count:fulfillmentRows.length-missing.length,
     fulfillment:fulfillmentRows,original_standalone_result:originalSemantic.result,retained_binding_sha256:workflowEvidence?.binding_sha256??null},
    originalSemantic.executed||fulfillmentRows.some(r=>r.origins.includes('original-retained-workflow')),result==='pass'?[]:[...new Set([...originalSemantic.blocked_by,...auditBlocked,...(missing.some(r=>r.kind==='Workflow')?retainedBlocked:[])])]);
  }
  const workflow_public_coverage={workflow_count:workflowCount,binding:workflowEvidence??null,standalone_checks:standaloneChecks,audit_fulfillment:auditFulfillment,
   semantic_fulfillment:fulfillmentRows,retained_prerequisites:workflowCount?retainedPrerequisites:[],retained_blocked_by:retainedBlocked,
   retained_status:workflowCount?workflowEvidence?.retained_status??'not_evaluable':'inapplicable',
   evidence_scope:'sealed-historical-report-not-a-live-retained-receipt',prerequisite_order:'original-artifact-checks-then-retained-binding-then-public-fulfillment'};
  const rows=[...checks.values()],failed=rows.some(c=>c.result==='fail'),missing=rows.some(c=>c.result==='not_evaluable');
  const body={schema_version:'domainspec.reconciled-verification-execution/v1-candidate' as const,definition_sha256:RECONCILED_VERIFICATION_EXECUTION_DEFINITION_SHA256,projection_sha256:input.projection_sha256,project_plan_sha256:plan.plan_sha256,source_identity:input.source_identity,denominators:input.denominators,checks:rows,result:failed?'fail' as const:missing?'incomplete' as const:'pass' as const,executed_check_count:rows.filter(c=>c.executed).length,not_evaluable_count:rows.filter(c=>c.result==='not_evaluable').length,claim_scope:'executed-checks-only' as const,runtime_conformance:'not_evaluable' as const,target_effect:'none' as const,authority_effect:'none' as const};
  const semantic_coverage={controls_sha256:semantic.controls_sha256,node_count:semantic.node_count,ready_count:semantic.ready_count,not_evaluable_count:semantic.not_evaluable_count,case_count:semantic.case_count,rows:semantic.rows.map(r=>r.state==='ready'?{selector:r.selector,kind:r.kind,adapter_status:'ready' as const,contract_sha256:r.contract_sha256,case_count:r.cases.length}:{selector:r.selector,kind:r.kind,adapter_status:'not_evaluable' as const,reason:r.reason})};
  const crossCheck=checks.get('cross-generator-behavior')!;
  const cross_generator_coverage={preparation:crossGeneratorPreparation,execution:crossGeneratorExecution??null,
   public_result:crossCheck.result,blocked_by:crossCheck.blocked_by,
   retained_workspace_state:!crossGeneratorExecution?.workspace?'not_created' as const:checks.get('verification-workspace-cleanup')?.result==='pass'?'removed' as const:'cleanup_not_confirmed' as const,
   evidence_scope:'sealed-historical-report-not-a-live-retained-receipt' as const};
  const selectedBody={...body,semantic_coverage,cross_generator_coverage,workflow_public_coverage,...(selected.output_layout===undefined?{}:{output_layout:selected.output_layout})};
  const report=freeze({...selectedBody,report_sha256:sha256(canonicalJson(selectedBody))});registered.add(report);return report;
 };
 put('compiled-graph-obligations','pass','registered graph and complete plan certificates match',{certificate:input.compiled_certificate,denominators:input.denominators});
 put('cross-generator-behavior','not_evaluable','cross-generator native families have not executed',{preparation_sha256:crossGeneratorPreparation.preparation_sha256},false);
 put('selected-generator-semantic-controls','not_evaluable','semantic controls have not executed for all source nodes',{controls_sha256:semantic.controls_sha256,node_count:semantic.node_count,ready_node_count:semantic.ready_count,remaining:semantic.rows.filter(r=>r.state==='not_evaluable')},false);
 if(plan.composition)put('composition-behavior-controls','not_evaluable','composition controls have not executed',{},false);
 put('safe-output-separate-from-planning','not_evaluable','target publication and concurrent-writer qualification are not performed',{},false);
 const sourceCurrent=()=>{const current=loadCompiledProjectGraph(graph.project_root);if(canonicalJson(current.source_manifest)!==canonicalJson(graph.source_manifest))fail('source manifest drift');return {source_count:current.source_manifest.source_count,manifest_sha256:current.source_manifest.manifest_sha256};};
 if(!attempt('source-currentness',sourceCurrent)){
  for(const [id,c] of checks)if(id!=='source-currentness'&&c.result!=='fail')put(id,'not_evaluable','current source prerequisite failed',c.evidence as Record<string,unknown>,c.executed,['source-currentness']);
  return finish();
 }
 const targetCurrent=()=>{
  const result=verifyReconciledProject(plan,selected.target_root!,null,selected.output_layout);if(result.result!=='pass')fail('existing target does not match exact whole-project output');
  return {view_sha256:result.view_sha256,receipt_sha256:result.expected_receipt_sha256,...(selected.output_layout===undefined?{}:{output_layout:selected.output_layout})};
 };
 if(selected.target_root&&!attempt('exact-output-currentness',targetCurrent)){
  for(const [id,c] of checks)if(c.result==='not_evaluable')put(id,'not_evaluable','existing output prerequisite failed',{},false,['exact-output-currentness']);
  return finish();
 }
 let runRoot='',owned:fs.Stats;
 const compositionExecutions:CompositionExecution[]=[];
 try{runRoot=fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()),'domainspec-reconciled-verify-'));owned=fs.lstatSync(runRoot);}
 catch(error){
  put('verification-workspace-currentness','fail',error instanceof Error?error.message:String(error));
  if(runRoot)put('verification-workspace-cleanup','fail','run directory identity unavailable; cleanup refused',{run_directory:runRoot},false);
  return finish();
 }
 try{
  const nativeRoot=path.join(runRoot,'native'),replayRoot=path.join(runRoot,'source');
  const semanticRoot=path.join(runRoot,'semantic'),signatureFiles=new Map<string,string>();
  const signaturesCurrent=()=>{for(const [p,content]of signatureFiles)if(readRegular(path.join(semanticRoot,p)).toString('utf8')!==content)fail('INTERFACE_SIGNATURE:control source changed');};
  const effectFiles=new Map(effectProfiles.map(a=>[a.key,new Map<string,string>()]));
  const effectFilesCurrent=(only?:EffectProfile)=>{for(const a of only?[only]:effectProfiles)for(const [file,expected]of effectFiles.get(a.key)!)if(readRegular(file).toString('utf8')!==expected)fail(a.diagnostic+':audit artifact changed');};
  const writeEffect=(a:EffectProfile,relative:string,content:string)=>{const file=write(runRoot,relative,content);effectFiles.get(a.key)!.set(file,content);return file;};
  const effectScripts=new Map<string,string>();
  const auditEffects=(a:EffectProfile,phase:'source'|'native',moduleRoot:string,config:string,paths:readonly string[])=>{
   if(!effectScripts.has(a.key))effectScripts.set(a.key,writeEffect(a,a.key+'-effects.mjs',a.observer));
   const effectScript=effectScripts.get(a.key)!;
   const definition=getReconciledSource(a.definition_source);
   const included=(m:{relative_path:string})=>paths.includes(m.relative_path.replace(/\.ts$/,phase==='native'?'.js':'.ts'));
   const input=writeEffect(a,a.key+'-effects-'+phase+'.json',canonicalJson({phase,definition,module_root:moduleRoot,module_paths:paths,
    ...('support_modules' in a?{support_modules:a.support_modules.filter(included)}:{}),...('workflow_modules' in a?{workflow_modules:a.workflow_modules.filter(included)}:{})})+'\n');
   const expected={schema_version:a.schema,phase,definition_sha256:a.definition_sha256,modules:paths.map(relative_path=>({relative_path,source_sha256:sha256(readRegular(path.join(moduleRoot,relative_path))),violations:[]}))};
   effectFilesCurrent(a);
   const observed=JSON.parse(run(process.execPath,[effectScript,selected.typescript_root,config,input],runRoot));
   effectFilesCurrent(a);
   if(canonicalJson(observed)!==canonicalJson(expected))fail(a.diagnostic+':'+phase+':'+canonicalJson(observed).slice(0,3072));
   for(const m of expected.modules)if(sha256(readRegular(path.join(moduleRoot,m.relative_path)))!==m.source_sha256)fail(a.diagnostic+':module changed during audit');
   return {phase,module_root:moduleRoot,definition_sha256:a.definition_sha256,selectors:phase==='source'?a.roots:a.rows.map(r=>r.selector),module_count:paths.length,modules:expected.modules,observation_sha256:sha256(canonicalJson(observed)),observer_sha256:sha256(a.observer),claim_scope:a.claim_scope};
  };
  let semanticSnapshot:Record<string,string>|null=null;
  const semanticInventory=()=>{
   const files=['package.json','compiler.json','cases.json','runner.mjs',...signatureFiles.keys(),...semanticPaths.map(p=>'modules/'+p.replace(/\.ts$/,'.js'))];
   const expected=new Set(files);for(const file of files){let parent=path.posix.dirname(file);while(parent!=='.'){expected.add(parent);parent=path.posix.dirname(parent);}}
   let count=0;const walk=(folder:string)=>{for(const entry of fs.readdirSync(folder,{withFileTypes:true})){const file=path.join(folder,entry.name),relative=path.relative(semanticRoot,file).split(path.sep).join('/');
    if(++count>expected.size||!expected.has(relative)||entry.isSymbolicLink())fail('unexpected semantic workspace entry');
    if(entry.isDirectory())walk(file);else if(!entry.isFile())fail('nonregular semantic workspace entry');
   }};walk(semanticRoot);if(count!==expected.size)fail('incomplete semantic workspace inventory');
   return Object.fromEntries(files.map(p=>[p,sha256(readRegular(path.join(semanticRoot,p)))]));
  };
  fs.mkdirSync(nativeRoot);fs.mkdirSync(replayRoot);
  attempt('isolated-exact-source-replay',()=>{
   for(const s of graph.source_manifest.sources){const bytes=readRegular(path.join(graph.project_root,s.relative_path));if(bytes.length!==s.size_bytes||sha256(bytes)!==s.sha256)fail('source changed before replay: '+s.relative_path);write(replayRoot,s.relative_path,bytes);}
   const replay=planCompiledReconciledProject(loadCompiledProjectGraph(replayRoot),plan.selection);
   const replayCoverage=createReconciledArtifactCoverage(replay);
   if(replay.plan_sha256!==plan.plan_sha256||canonicalJson(replayCoverage)!==canonicalJson(coverage)||canonicalJson(replay.composition)!==canonicalJson(plan.composition))fail('isolated replay mismatch');
   return {plan_sha256:replay.plan_sha256,source_count:graph.source_manifest.source_count,artifact_count:replayCoverage.artifacts.length};
  });
  for(const artifact of coverage.artifacts)write(nativeRoot,artifact.relative_path,artifact.content);
  const packageText=canonicalJson({type:'module'})+'\n';
  write(nativeRoot,'package.json',packageText);
  const configText=canonicalJson({compilerOptions:{target:'ES2022',module:'NodeNext',moduleResolution:'NodeNext',strict:true,skipLibCheck:true,noEmit:true,...(coverage.javascript_paths.length?{allowJs:true,checkJs:false}:{}),types:['node'],typeRoots:[selected.node_type_root]},files:coverage.modules.map(a=>a.relative_path)})+'\n';
  const config=write(nativeRoot,'tsconfig.json',configText);
  for(const a of effectProfiles)effectFiles.get(a.key)!.set(config,configText);
  const tsc=path.join(selected.typescript_root,'bin/tsc'),typeManifest=path.join(selected.node_type_root,'node/package.json');
  const toolFiles=[path.join(selected.typescript_root,'package.json'),tsc,path.join(selected.typescript_root,'dist/api/sync/api.js'),path.join(selected.typescript_root,'dist/ast/index.js'),typeManifest,selected.lean_executable];
  let initialTools:Record<string,string>|null=null;
  const fingerprint=()=>Object.fromEntries(toolFiles.map(file=>[file,sha256(readRegular(file,256*1024*1024))]));
  attempt('toolchain-currentness',()=>{
   const ts=JSON.parse(readRegular(toolFiles[0]!).toString('utf8')),types=JSON.parse(readRegular(typeManifest).toString('utf8'));
   if(ts.version!=='7.0.2'||types.name!=='@types/node')fail('TypeScript 7.0.2 and Node type declarations required');
   initialTools=fingerprint();return {typescript_version:ts.version,node_types_version:types.version,files:initialTools,node_version:process.version};
  });
  attempt('strict-native-compilation',()=>{
   const version=run(process.execPath,[tsc,'--version'],nativeRoot).trim();if(version!=='Version 7.0.2')fail('native TypeScript version drift');
   run(process.execPath,[tsc,'--project',config],nativeRoot);
   return {version,artifact_count:coverage.typescript_paths.length,javascript_typechecking:'not-claimed',configuration_sha256:sha256(readRegular(config))};
  },['isolated-exact-source-replay','toolchain-currentness']);
  if(coverage.javascript_paths.length)attempt('generated-javascript-syntax',()=>{
   for(const relative of coverage.javascript_paths)run(process.execPath,['--check',path.join(nativeRoot,relative)],nativeRoot);
   return {node_version:process.version,artifact_paths:coverage.javascript_paths,scope:'syntax-only-no-behavior-execution'};
  },['isolated-exact-source-replay','toolchain-currentness']);
  attempt('independent-module-surface-observation',()=>{
   const script=write(runRoot,'observe.mjs',observer),observed=JSON.parse(run(process.execPath,[script,selected.typescript_root,config],nativeRoot));
   const expected=coverage.modules.map(m=>({relative_path:m.relative_path,imports:m.imports.map(({specifier,names,namespace,type_only,reexport})=>({specifier,names,namespace,type_only,reexport})),exports:m.exports}));
   if(canonicalJson(observed)!==canonicalJson(expected))fail('native import/export surface mismatch');
   return {module_count:observed.length,observation_sha256:sha256(canonicalJson(observed)),observer_sha256:sha256(observer)};
  },['strict-native-compilation']);
  for(const a of effectProfiles)attempt(a.source_id,()=>auditEffects(a,'source',nativeRoot,config,a.module_paths),['isolated-exact-source-replay','strict-native-compilation','independent-module-surface-observation','toolchain-currentness']);
  if(semantic.ready_count){
   const passed=attempt('selected-generator-semantic-controls',()=>{
    if(process.version!=='v26.8.1')fail('Node 26.8.1 required for the semantic permission boundary');
    for(const a of coverage.artifacts)if(sha256(readRegular(path.join(nativeRoot,a.relative_path)))!==a.sha256)fail('native source changed before semantic emission');
    const settings=JSON.parse(configText);settings.compilerOptions.noEmit=false;settings.compilerOptions.rootDir=nativeRoot;settings.compilerOptions.outDir=path.join(semanticRoot,'modules');
    settings.files=semanticPaths.map(p=>path.join(nativeRoot,p));delete settings.compilerOptions.allowJs;delete settings.compilerOptions.checkJs;
    const semanticConfig=canonicalJson(settings)+'\n',caseText=renderSemanticCases(semantic);
    const project=write(semanticRoot,'compiler.json',semanticConfig),cases=write(semanticRoot,'cases.json',caseText),runner=write(semanticRoot,'runner.mjs',SEMANTIC_RUNNER);
    write(semanticRoot,'package.json',packageText);
    const signatures=semantic.rows.filter(r=>r.state==='ready'&&'signature_source' in r);
    if(signatures.length){
     for(const [index,row]of signatures.entries())if('signature_source' in row){const p='signatures/'+index+'.ts';signatureFiles.set(p,row.signature_source);write(semanticRoot,p,row.signature_source);}
     const signatureConfig=canonicalJson({...JSON.parse(configText),files:[...signatureFiles.keys()]})+'\n';
     signatureFiles.set('signatures.json',signatureConfig);const file=write(semanticRoot,'signatures.json',signatureConfig);
     run(process.execPath,[tsc,'--project',file],semanticRoot);signaturesCurrent();
    }
    run(process.execPath,[tsc,'--project',project],nativeRoot);
    semanticSnapshot=semanticInventory();
    for(const a of effectProfiles)if(a.native_paths.length){
     const files=a.native_paths.map(p=>p.replace(/\.ts$/,'.js'));
     const auditConfig=writeEffect(a,a.key+'-native-audit.json',canonicalJson({compilerOptions:{target:'ES2022',module:'NodeNext',moduleResolution:'NodeNext',allowJs:true,checkJs:false,noEmit:true,skipLibCheck:true,types:['node'],typeRoots:[selected.node_type_root]},files:files.map(p=>path.join(semanticRoot,'modules',p))})+'\n');
     if(!attempt(a.native_id,()=>auditEffects(a,'native',path.join(semanticRoot,'modules'),auditConfig,files),[a.source_id]))fail(a.diagnostic+':native prerequisite failed');
     if(canonicalJson(semanticInventory())!==canonicalJson(semanticSnapshot))fail(a.diagnostic+':semantic workspace changed during audit');
    }
    if(readRegular(project).toString('utf8')!==semanticConfig||readRegular(cases).toString('utf8')!==caseText||readRegular(runner).toString('utf8')!==SEMANTIC_RUNNER||readRegular(path.join(semanticRoot,'package.json')).toString('utf8')!==packageText)fail('semantic controls changed before execution');
    effectFilesCurrent();signaturesCurrent();
    const result=spawnSync(process.execPath,['--permission','--allow-fs-read='+semanticRoot,'--disable-proto=throw',runner,cases,path.join(semanticRoot,'modules')],{cwd:semanticRoot,env:{LANG:'C',TZ:'UTC'},encoding:'utf8',timeout:SUBPROCESS_TIMEOUT_MS,maxBuffer:32*1024*1024});
    if(result.error||result.status!==0)fail('pure semantic process rejected: '+(result.error?.message||result.stderr||result.stdout||'exit '+result.status).slice(0,4096));
    return {...checkSemanticObservations(semantic,result.stdout),interface_signature_count:signatures.length,node_version:process.version,execution_scope:'permission-restricted-pure-controls',environment:'minimal-no-inherited-credentials'};
   },['isolated-exact-source-replay','strict-native-compilation','independent-module-surface-observation','toolchain-currentness',...effectProfiles.map(a=>a.source_id)]);
   if(passed&&semantic.not_evaluable_count)put('selected-generator-semantic-controls','not_evaluable','bounded controls passed for evaluated source nodes; remaining nodes are not_evaluable',checks.get('selected-generator-semantic-controls')!.evidence as Record<string,unknown>,true);
  }
  if(plan.composition){
   const rows:Record<string,unknown>[]=[];
   const ran=attempt('composition-behavior-controls',()=>{
    for(const composition of plan.composition!.compositions){
     try{
      const row=createPublicCompositionControls(graph,plan,composition.id);
      if(row.state==='not_evaluable'){rows.push(row);continue;}
      const execution=executeCompositionControls(row.control,{workspace_parent:runRoot,typescript_root:selected.typescript_root,node_type_root:selected.node_type_root});
      if(path.dirname(execution.workspace)!==runRoot)fail('composition workspace escaped parent');
      compositionExecutions.push(execution);
      const {workspace,...evidence}=execution;
      rows.push({id:row.id,state:'pass',...evidence,workspace_relative:path.relative(runRoot,workspace),
       coverage:row.control.family.coverage,search:row.control.family.search,case_family_sha256:sha256(canonicalJson(row.control.family))});
     }catch(error){rows.push({id:composition.id,state:'fail',phase:error instanceof CompositionExecutionError?error.phase:'control-construction',reason:error instanceof Error?error.message:String(error)});}
    }
    return {definition_sha256:COMPOSITION_PUBLIC_DEFINITION_SHA256,composition_count:plan.composition!.compositions.length,
     case_count:compositionExecutions.reduce((n,r)=>n+r.cases,0),rows,claim_scope:'finite-source-bound-composition-computation-only'};
   },['source-currentness','isolated-exact-source-replay','strict-native-compilation','independent-module-surface-observation','generated-javascript-syntax','toolchain-currentness']);
   if(ran){
    const result=rows.some(r=>r.state==='fail')?'fail':rows.some(r=>r.state==='not_evaluable')?'not_evaluable':'pass';
    put('composition-behavior-controls',result,result==='pass'?'all selected composition cases passed':result==='fail'?'composition control failed; see causal row':'complete source family unavailable; see missing obligations',checks.get('composition-behavior-controls')!.evidence as Record<string,unknown>);
   }
  }
  const crossRan=attempt('cross-generator-behavior',()=>{
   crossGeneratorExecution=executePreparedCrossGeneratorVerification(crossGeneratorPreparation,graph,plan,{workspace_parent:runRoot,typescript_root:fs.realpathSync(selected.typescript_root),node_types_root:fs.realpathSync(path.join(selected.node_type_root,'node'))});
   return {retained_report_sha256:crossGeneratorExecution.report_sha256,preparation_sha256:crossGeneratorPreparation.preparation_sha256,
    native_result:crossGeneratorExecution.result,executed_family_count:crossGeneratorExecution.executed_family_count,retained_family_count:crossGeneratorExecution.retained_family_count,
    claim_scope:'finite-source-bound-cross-generator-protocols'};
  },crossGeneratorDependencies);
  if(crossRan&&crossGeneratorExecution){
   const result=crossGeneratorExecution.result==='incomplete'?'not_evaluable':crossGeneratorExecution.result==='fail'?'fail':'pass';
   const reason=crossGeneratorExecution.result==='inapplicable'?'no applicable cross-generator protocols; zero native families executed':result==='pass'?'all applicable retained native protocols passed':result==='fail'?'native family or currentness failed; see complete coverage':'required family or edge evidence unavailable; see complete coverage';
   put('cross-generator-behavior',result,reason,checks.get('cross-generator-behavior')!.evidence as Record<string,unknown>);
  }
  if(workflowCount&&crossGeneratorExecution)attempt('workflow-public-evidence-binding',()=>{
   workflowEvidence=bindRetainedWorkflowPublicEvidence(graph,plan,semantic,crossGeneratorPreparation,crossGeneratorExecution);
   return {binding_sha256:workflowEvidence.binding_sha256,workflow_count:workflowEvidence.workflow_count,retained_status:workflowEvidence.retained_status,
    public_fulfillment:'not_evaluable',scope:'registered-retained-binding-before-final-public-prerequisites'};
  },crossGeneratorDependencies);
  const formal=createReconciledFormalization(graph,plan),base=write(runRoot,'Reconciled.lean',formal.artifact.content);
  const audit=write(runRoot,'Audit.lean',formal.artifact.content+'\n#print axioms DomainSpec.Reconciled.currentStructuralReferencesHold\n#eval IO.println (DomainSpec.Reconciled.toJson DomainSpec.Reconciled.sourceData)\n');
  let observedMeaning:unknown;
  attempt('lean-structural-kernel',()=>{
   const version=run(selected.lean_executable,['--version'],runRoot).trim();if(!/^Lean \(version 4\.33\.1,/.test(version))fail('Lean 4.33.1 required');
   const output=run(selected.lean_executable,[audit],runRoot),lines=output.trim().split('\n');
   if(lines.length!==2||lines[0]!=="'DomainSpec.Reconciled.currentStructuralReferencesHold' depends on axioms: [propext, Classical.choice, Quot.sound]")fail('unexpected Lean proof dependency or output');
   observedMeaning=JSON.parse(lines[1]!);
   return {version,proof_sha256:formal.artifact.sha256,audit_sha256:sha256(readRegular(audit)),axioms:['propext','Classical.choice','Quot.sound'],scope:formal.claim_scope,checked_predicates:formal.checked_predicates};
  },['isolated-exact-source-replay','toolchain-currentness']);
  attempt('source-and-selection-preservation',()=>{
   const expected={graph:input.semantic_graph,selection:input.compilation_selection};
   if(canonicalJson(observedMeaning)!==canonicalJson(expected))fail('Lean source/selection round trip mismatch');
   return {observation_sha256:sha256(canonicalJson(observedMeaning))};
  },['lean-structural-kernel']);
  const formalFilesCurrent=()=>{
   if(readRegular(base).toString('utf8')!==formal.artifact.content)fail('formalization bytes changed');
   const expected=formal.artifact.content+'\n#print axioms DomainSpec.Reconciled.currentStructuralReferencesHold\n#eval IO.println (DomainSpec.Reconciled.toJson DomainSpec.Reconciled.sourceData)\n';
   if(readRegular(audit).toString('utf8')!==expected)fail('audit bytes changed');
   return {proof_sha256:formal.artifact.sha256,bundle_sha256:formal.bundle_sha256};
  };
  attempt('successor-formalization-currentness',formalFilesCurrent,['lean-structural-kernel','source-and-selection-preservation']);
  const publicArtifactsCurrent=()=>{
   for(const a of coverage.artifacts){const bytes=readRegular(path.join(nativeRoot,a.relative_path));if(bytes.length!==a.size_bytes||sha256(bytes)!==a.sha256)fail('native artifact changed during verification: '+a.relative_path);}
   const expected=new Set([...coverage.artifacts.map(a=>a.relative_path),'package.json','tsconfig.json']);
   for(const file of [...expected]){let parent=path.posix.dirname(file);while(parent!=='.'){expected.add(parent);parent=path.posix.dirname(parent);}}
   let observed=0;const walk=(folder:string)=>{for(const entry of fs.readdirSync(folder,{withFileTypes:true})){
    const file=path.join(folder,entry.name),relative=path.relative(nativeRoot,file).split(path.sep).join('/');
    if(++observed>expected.size||!expected.has(relative)||entry.isSymbolicLink())fail('unexpected verification workspace entry: '+relative);
    if(entry.isDirectory())walk(file);else if(!entry.isFile())fail('nonregular verification workspace entry: '+relative);
   }};walk(nativeRoot);if(observed!==expected.size)fail('incomplete verification workspace inventory');
   if(readRegular(config).toString('utf8')!==configText||readRegular(path.join(nativeRoot,'package.json')).toString('utf8')!==packageText)fail('native validation configuration changed');
   if(checks.get('independent-module-surface-observation')?.executed&&readRegular(path.join(runRoot,'observe.mjs')).toString('utf8')!==observer)fail('native observer changed');
   return {artifact_count:coverage.artifacts.length};
  };
  attempt('verification-workspace-currentness',publicArtifactsCurrent);
  if(plan.composition){
   attempt('composition-source-preservation',()=>({composition_count:plan.composition!.compositions.length,artifact_count:plan.composition!.artifacts.length,composition_plan_sha256:plan.composition!.plan_sha256,scope:'exact-replay-and-source-retention'}),['isolated-exact-source-replay','source-and-selection-preservation','verification-workspace-currentness']);
   attempt('selected-calculation-bindings',()=>{
    const binding=validateResolvedCompositionBindings(plan.composition,graph,plan.resolved,plan.composition!.definition_source.content);
    return {composition_plan_sha256:binding.plan_sha256,bindings:binding.compositions.flatMap(c=>c.bindings.filter(b=>b.role==='calculation-call')),scope:'checked-binding-and-observed-native-surface-not-behavior'};
   },['composition-source-preservation','strict-native-compilation','independent-module-surface-observation','generated-javascript-syntax']);
  }
  publicEpochCurrent=()=>{
  // A later successful read must not erase an already observed failure.
  const recheck=(id:string,action:()=>Record<string,unknown>)=>{if(checks.get(id)?.result!=='fail')attempt(id,action);};
  recheck('verification-workspace-currentness',publicArtifactsCurrent);
  recheck('successor-formalization-currentness',formalFilesCurrent);
  if(semanticSnapshot)recheck('semantic-workspace-currentness',()=>{
   const current=semanticInventory();if(canonicalJson(current)!==canonicalJson(semanticSnapshot))fail('semantic workspace changed during verification');
   return {inventory_sha256:sha256(canonicalJson(current)),file_count:Object.keys(current).length};
  });
  if(initialTools)recheck('toolchain-currentness',()=>{const final=fingerprint();if(canonicalJson(final)!==canonicalJson(initialTools))fail('toolchain files changed during verification');return {...checks.get('toolchain-currentness')!.evidence,files:final};});
  for(const a of effectProfiles)if(effectFiles.get(a.key)!.size)recheck(a.current_id,()=>{
   effectFilesCurrent(a);const files=effectFiles.get(a.key)!;
   return {file_count:files.size,files:[...files].map(([file,content])=>({relative_path:path.relative(runRoot,file),sha256:sha256(content)}))};
  });
  recheck('source-currentness',sourceCurrent);
  if(selected.target_root)recheck('exact-output-currentness',targetCurrent);
  };
  publicEpochCurrent();
 }catch(error){put('verification-workspace-currentness','fail',error instanceof Error?error.message:String(error));}
 finally{
  if(selected.target_root)attempt('exact-output-currentness',targetCurrent);
  else put('exact-output-currentness','not_evaluable','no existing output target supplied',{},false);
  if(!attempt('source-currentness',sourceCurrent)){
   for(const [id,c] of checks)if(id!=='source-currentness'&&c.result==='pass')put(id,'not_evaluable','source changed after execution; previous observation is stale',c.evidence as Record<string,unknown>,c.executed,['source-currentness']);
  }
  if(plan.composition){
   if(compositionExecutions.length)attempt('composition-behavior-currentness',()=>{
    for(const receipt of compositionExecutions)assertCompositionExecutionCurrent(receipt);
    return {execution_count:compositionExecutions.length,observations:compositionExecutions.map(r=>({binding_sha256:r.binding_sha256,observation_sha256:r.observation_sha256,file_count:Object.keys(r.files).length}))};
   });
   else put('composition-behavior-currentness','not_evaluable','no successful composition execution receipt to revalidate',{},false,['composition-behavior-controls']);
  }
  if(crossGeneratorExecution)attempt('cross-generator-currentness',()=>{
   assertCrossGeneratorAggregateCurrent(crossGeneratorExecution);
   return {retained_report_sha256:crossGeneratorExecution.report_sha256,retained_family_count:crossGeneratorExecution.retained_family_count,checked_before_owned_cleanup:true};
  });
  else put('cross-generator-currentness','not_evaluable','no aggregate receipt to revalidate',{},false,['cross-generator-behavior']);
  if(workflowEvidence)attempt('workflow-public-evidence-currentness',()=>{
   assertWorkflowPublicEvidenceCurrent(workflowEvidence);
   return {binding_sha256:workflowEvidence.binding_sha256,checked_before_owned_cleanup:true};
  });
  else if(workflowCount)put('workflow-public-evidence-currentness','not_evaluable','no original Workflow evidence binding to revalidate',{},false,['workflow-public-evidence-binding']);
  // Retained-receipt inspection can be lengthy. Check original public evidence
  // again at the cleanup boundary, not only before inspecting retained files.
  if(publicEpochCurrent)publicEpochCurrent();
  attempt('verification-workspace-cleanup',()=>{
   const current=fs.lstatSync(runRoot);if(!current.isDirectory()||current.isSymbolicLink()||current.dev!==owned.dev||current.ino!==owned.ino)fail('owned verification directory identity changed; cleanup refused');
   fs.rmSync(runRoot,{recursive:true});return {owned_directory_removed:true};
  });
 }
 return finish();
}
export type ReconciledVerificationExecution=ReturnType<typeof executeReconciledVerification>;
export function renderReconciledVerificationExecution(value:ReconciledVerificationExecution):string{
 if(!value||typeof value!=='object'||!registered.has(value))fail('registered execution report required');return canonicalJson(value)+'\n';
}
