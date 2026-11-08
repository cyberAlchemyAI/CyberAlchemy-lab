import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,lstatSync,realpathSync,readdirSync,rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {deriveBusinessApplicationBindings,assertDerivedBusinessApplicationCurrent} from './business-application-bindings.js';
import {deriveBusinessApplicationActions} from './business-application-actions.js';
import {compileApplicationExecutable} from './application-executable.js';
import type {BusinessApplicationInput} from './business-application-protocol.js';
import type {DomainSpecCompiler} from './domainspec-cli.js';
import {digest,json,symbol} from './domainspec-profile.js';
// Open questions: minimal request graph/artifact joins BA05/06 and installed qualification BA18.
const prepared=new WeakMap<object,{compiler:DomainSpecCompiler;workspace:string;fingerprint:string}>();
const fingerprint=(value:{actions:any;graph:unknown;executable:unknown})=>digest(json({actions:value.actions.execution,graph:value.graph,executable:value.executable}));
export function prepareBusinessApplication(input:BusinessApplicationInput,id:string,compiler:DomainSpecCompiler){
 const engine=compiler.profileEngine;if(!engine?.assertBusinessInputV2Current)throw Error('BUSINESS_APPLICATION_PEER_REQUIRED');
 const derived=deriveBusinessApplicationBindings(input,id,engine),actions=deriveBusinessApplicationActions(input,derived,compiler);
 const workspace=mkdtempSync(path.join(os.tmpdir(),'alch-business-application-'));
 try{
  for(const [relative,body]of Object.entries(actions.prepared.projectFiles)){
   if(!relative||path.isAbsolute(relative)||relative.includes('\\')||relative.split('/').some(part=>!part||part==='.'||part==='..'))throw Error('BUSINESS_APPLICATION_DERIVED_PATH');
   const target=path.join(workspace,relative);mkdirSync(path.dirname(target),{recursive:true});writeFileSync(target,body,{flag:'wx'});
  }
  const graph=compiler.compileProject(workspace).graph,executable=compileApplicationExecutable(actions.prepared,graph,compiler);assertDerivedBusinessApplicationCurrent(derived);
  const result=Object.freeze({input,id,derived,actions,workspace,graph,executable});prepared.set(result,{compiler,workspace,fingerprint:fingerprint(result)});assertPreparedBusinessApplicationCurrent(result);return result;
 }catch(error){rmSync(workspace,{recursive:true,force:true});throw error;}
}
export function assertPreparedBusinessApplicationCurrent(value:ReturnType<typeof prepareBusinessApplication>):void {
 const state=prepared.get(value);if(!state)throw Error('BUSINESS_APPLICATION_UNREGISTERED');assertDerivedBusinessApplicationCurrent(value.derived);
 if(fingerprint(value)!==state.fingerprint)throw Error('BUSINESS_APPLICATION_PREPARATION_CHANGED');
 if(!lstatSync(state.workspace).isDirectory()||realpathSync(state.workspace)!==state.workspace)throw Error('BUSINESS_APPLICATION_SCRATCH_OWNERSHIP');
 const files=value.actions.prepared.projectFiles,actual:string[]=[];
 const visit=(directory:string,depth:number):void=>{if(depth>16)throw Error('BUSINESS_APPLICATION_SCRATCH_BUDGET');for(const entry of readdirSync(path.join(state.workspace,directory),{withFileTypes:true})){const relative=directory?directory+'/'+entry.name:entry.name;if(entry.isSymbolicLink())throw Error('BUSINESS_APPLICATION_SCRATCH_SYMLINK');if(entry.isDirectory())visit(relative,depth+1);else if(entry.isFile()){actual.push(relative);if(actual.length>10000)throw Error('BUSINESS_APPLICATION_SCRATCH_BUDGET');}else throw Error('BUSINESS_APPLICATION_SCRATCH_KIND');}};
 visit('',0);if(json(actual.sort())!==json(Object.keys(files).sort()))throw Error('BUSINESS_APPLICATION_SCRATCH_INVENTORY');
 for(const relative of Object.keys(files)){
  if(path.isAbsolute(relative)||relative.split('/').some(p=>p==='..'))throw Error('BUSINESS_APPLICATION_DERIVED_PATH');
  let target=state.workspace;for(const part of relative.split('/')){target=path.join(target,part);if(lstatSync(target).isSymbolicLink())throw Error('BUSINESS_APPLICATION_SCRATCH_SYMLINK');}
  if(!lstatSync(target).isFile()||readFileSync(target,'utf8')!==files[relative])throw Error('BUSINESS_APPLICATION_SCRATCH_CHANGED');
 }
 // Source/action/graph/artifact fingerprints and scratch inventory were checked above.
 // Reuse the owning registries; do not regenerate the same immutable native plan.
 state.compiler.profileEngine.assertBusinessApplicationPlanCurrent(value.graph,value.executable.plan);
}
export function disposePreparedBusinessApplication(value:ReturnType<typeof prepareBusinessApplication>):void {
 const state=prepared.get(value);if(!state)throw Error('BUSINESS_APPLICATION_UNREGISTERED');prepared.delete(value);rmSync(state.workspace,{recursive:true,force:true});
}
/** Public profile join through the exact owning Core constructors. */
export function prepareBusinessApplicationCallables(value:ReturnType<typeof prepareBusinessApplication>,choices:readonly {intent_id:string;route:string}[],compiler:DomainSpecCompiler){
 assertPreparedBusinessApplicationCurrent(value);const engine=compiler.profileEngine,intents=value.input.snapshot.project.application_intents.filter(i=>i.application_id===value.id),formation=value.derived.formation;
 const entries=intents.map(intent=>{
  const selected=choices.find(c=>c.intent_id===intent.id);if(!selected)throw Error('BUSINESS_APPLICATION_PROFILE_CHOICE_REQUIRED');
  const operation_ref=formation.feature+':'+formation.symbols[intent.operation_ref],mapping_ref=formation.feature+':'+formation.symbols[intent.mapping_ref],operation=value.actions.prepared.selection.operations.find((o:any)=>o.selector===operation_ref);
  if(!operation||operation.inputs.length!==1)throw Error('BUSINESS_APPLICATION_REQUEST_SHAPE');
  return {id:intent.id,operation_ref,mapping_ref,mapping_arguments:Object.entries(intent.mapping_arguments).map(([parameter,path])=>({parameter:symbol(parameter,'_'),path:path.path})),request_parameter:operation.inputs[0].name,route:{method:'POST',path:selected.route},access:intent.access};
 });
 const source={schema_version:'domainspec.request-application-source/v1-candidate',source_id:value.id,entries},binding=engine.compileRequestApplicationBindingV1(value.graph,source,value.executable.plan),plan=engine.composeRequestApplicationPlanV1(value.executable.plan,binding),original=value.input.applications.find(a=>a.model.id===value.id)!;
 const lineage={application_id:value.id,original_source:original.model.source,original_source_sha256:value.derived.original_source_sha256,original_semantics_sha256:value.derived.original_semantics_sha256,derived_source_sha256:value.derived.source_sha256,derivation_sha256:value.derived.derivation_sha256,line_map:value.derived.line_map};
 return intents.map(intent=>engine.prepareRequestApplicationCallable(value.graph,plan,binding,intent,lineage,()=>assertPreparedBusinessApplicationCurrent(value)));
}
