import {cpSync,mkdtempSync,mkdirSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {PROFILE_ROLE_CONTRACTS,type ProfilePackage} from '../../src/profile-engine/contracts.js';
import {loadProfileProject} from '../../src/profile-engine/loader.js';
import {selectProfileConfiguration,profileTechnicalSelections,type CompiledFunctionContribution} from '../../src/profile-engine/compose.js';
import {assertProfileBusinessInputCurrent} from '../../src/profile-engine/business-input.js';
import {loadCompiledProjectGraph} from '../../src/input/project-model.js';
import {planCompiledProjectBuild} from '../../src/generation/project-build.js';
import {deriveProfileSources,type ProfileTechnicalSelection} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/profile-project-input.js';
import {prepareServicePlan,planPreparedService,disposePreparedService,assertPreparedServiceCurrent} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/service-builder.js';
import {loadDomainSpecCompiler} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/domainspec-cli.js';

// Shared construction fixtures. Open questions: final native/installed qualification PE08/23.
export function createProfileFixture(t:{after(fn:()=>void):void},change?:(profile:any)=>void){
 const root=mkdtempSync(path.join(os.tmpdir(),'profile-composition-'));t.after(()=>rmSync(root,{recursive:true,force:true}));cpSync(path.join(import.meta.dirname,'fixtures/quote-business'),root,{recursive:true});mkdirSync(path.join(root,'profile'));
 const technical={request_bytes:16384,timeout_ms:2000,read_timeout_ms:500,read_max_bytes:8192,read_credentials:'none',success_status:200,rejection_status:409};
 const roles=['domain-function','http-entry','http-dispatch'] as const;
 const profile:any={schema_version:'craft.profile-package/v1',id:'FixtureArchitecture',version:'1.0.0',engine:'craft.profile-engine/v1',conflict_policy:'reject',dependencies:[],capabilities:roles.map(role=>({role,descriptor_ref:PROFILE_ROLE_CONTRACTS[role].descriptor_ref,recipe_ref:PROFILE_ROLE_CONTRACTS[role].recipe_ref})),budgets:{operations:10000,rows:10000,join_pairs:10000,depth:16,bytes:1048576},assets:[],rules:[
  {id:'functions',op:'emit',from:'intents',role:'domain-function',fields:{id:{field:['id']},source:{field:['source']},output_prefix:{concat:[{literal:'functions/'},{field:['id']}]}}},
  {id:'entries',op:'emit',from:'intents',role:'http-entry',fields:{id:{field:['id']},source:{field:['source']},route:{concat:[{literal:'/'},{field:['id']}]},technical:{literal:technical}}},
  {id:'dispatcherRow',op:'defaults',as:'dispatcher',values:{id:'service',artifact_path:'app/index.mjs'}},
  {id:'dispatcher',op:'emit',from:'dispatcher',role:'http-dispatch',fields:{id:{field:['id']},artifact_path:{field:['artifact_path']}}},
 ]};change?.(profile);writeFileSync(path.join(root,'profile/profile.json'),JSON.stringify(profile));
 const project=JSON.parse(readFileSync(path.join(root,'project.json'),'utf8'));project.profiles=[{id:profile.id,version:profile.version,path:'profile'}];writeFileSync(path.join(root,'project.json'),JSON.stringify(project));
 const identity={engine:[{key:'engine',path:path.join(root,'profile/profile.json')}],tools:[{key:'tool',path:path.join(root,'provider.json')}]};
 return {root,profile,identity,load:()=>loadProfileProject(path.join(root,'project.json'),identity)};
}
export function useShippedProfile(fixture:ReturnType<typeof createProfileFixture>,name='node-http-entry-local-v1'){
 const directory=path.resolve(import.meta.dirname,'../../profiles',name);cpSync(directory,path.join(fixture.root,'profile'),{recursive:true});const profile=JSON.parse(readFileSync(path.join(directory,'profile.json'),'utf8')),projectPath=path.join(fixture.root,'project.json'),project=JSON.parse(readFileSync(projectPath,'utf8'));project.profiles=[{id:profile.id,version:profile.version,path:'profile'}];writeFileSync(projectPath,JSON.stringify(project));return fixture;
}
export async function compiledProfileFixture(t:{after(fn:()=>void):void},change?:(profile:any)=>void){
 const fixture=createProfileFixture(t,change),snapshot=fixture.load(),selection=selectProfileConfiguration(snapshot),compiler=await loadDomainSpecCompiler();
 const lowered=deriveProfileSources(selection.input,{assertProfileBusinessInputCurrent},compiler,profileTechnicalSelections(selection) as unknown as readonly ProfileTechnicalSelection[]);
 const derived=path.join(fixture.root,'derived');mkdirSync(derived);for(const [file,body]of Object.entries(lowered.files)){const target=path.join(derived,file);mkdirSync(path.dirname(target),{recursive:true});writeFileSync(target,body);}
 const prepared=await prepareServicePlan(path.join(derived,'service.alch'));t.after(()=>disposePreparedService(prepared));const plan=planPreparedService(prepared);
 const functions:CompiledFunctionContribution[]=prepared.functions.map((fn,index)=>{
  const graph=loadCompiledProjectGraph(fn.workspace),actual=planCompiledProjectBuild(graph,'typescript','domainspec.typescript-exact-uint64/v1','domainspec.application-layout/v1');
  const artifacts={...plan.functions[index]!.artifacts};for(const a of actual.artifacts)artifacts[a.relative_path]=a.content;
  return {intent_id:selection.input.project.public_intents[index]!.id,source:selection.input.project.public_intents[index]!.source,graph,artifacts,assert_current:()=>assertPreparedServiceCurrent(prepared)};
 });
 return {...fixture,snapshot,selection,lowered,prepared,plan,functions};
}

export function applicationFixture(t:{after(fn:()=>void):void},profile='node-http-entry-local-v1'){
 const f=useShippedProfile(createProfileFixture(t),profile);cpSync(path.resolve(import.meta.dirname,'../../examples/profile-engine/craft-application-source'),path.join(f.root,'application'),{recursive:true});const projectPath=path.join(f.root,'project.json'),project=JSON.parse(readFileSync(projectPath,'utf8'));
 project.application_calls=[{id:'receiveNotice',source:'application/commerce.alch',operation_ref:'commerce:receive-notice',mapping_binding_ref:'message-mapping:consume-order',access:{kind:'public'}}];writeFileSync(projectPath,JSON.stringify(project));return {...f,projectPath};
}
