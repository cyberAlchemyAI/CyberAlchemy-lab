import {mkdtempSync,cpSync,readFileSync,writeFileSync,mkdirSync,rmSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {loadProfileProjectV2,prepareBusinessInputV2,dataDigest,captureJson,assertBusinessInputV2Current} from '../../src/profile-engine/index.ts';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {planCompiledSelectedReconciledProject} from '../../src/generation/selected-reconciled-project.ts';
import {compileFormalConditionBindings} from '../../src/formalization/condition-binding.ts';
import {deriveBusinessApplicationBindings} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/business-application-bindings.ts';
import {deriveBusinessApplicationActions} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/business-application-actions.ts';
import {loadDomainSpecCompiler} from '../../../../../../../language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/domainspec-cli.ts';
// Open questions: complete installed public workflow BA18. Source tests use source-owned registries.
export async function businessApplicationFixture(t:{after(callback:()=>void):void}) {
 const cli=path.resolve(import.meta.dirname,'../..'),root=mkdtempSync(path.join(os.tmpdir(),'request-application-'));
 t.after(()=>rmSync(root,{recursive:true,force:true}));cpSync(path.join(cli,'test/profile-engine/fixtures/business-notice'),root,{recursive:true});
 const file=path.join(root,'project.json'),project=JSON.parse(readFileSync(file,'utf8'));project.profiles[0].path=path.join(cli,'profiles/node-http-entry-local-v2');writeFileSync(file,JSON.stringify(project));
 const snapshot=loadProfileProjectV2(file,{engine:[{key:'graph',path:path.join(cli,'src/system-integration/application-graph-v1.ts')}],tools:[{key:'node',path:process.execPath}]}),input=prepareBusinessInputV2(snapshot),engine={dataDigest,captureJson,assertBusinessInputV2Current};
 const compiler=await loadDomainSpecCompiler(),derived=deriveBusinessApplicationBindings(input,'commerce',engine),actions=deriveBusinessApplicationActions(input,derived,compiler),sourceRoot=path.join(root,'derived');
 for(const [relative,body]of Object.entries(actions.prepared.projectFiles)){const target=path.join(sourceRoot,relative);mkdirSync(path.dirname(target),{recursive:true});writeFileSync(target,body);}
 const graph=loadCompiledProjectGraph(sourceRoot);compileFormalConditionBindings(graph,derived.formation.conditions,new Map(Object.entries(derived.formation.files).map(([p,v])=>[p,Buffer.from(v)])));
 const plan=planCompiledSelectedReconciledProject(graph,actions.prepared.selection);
 const source={schema_version:'domainspec.request-application-source/v1-candidate' as const,source_id:'commerce',entries:[{id:'receiveNotice',operation_ref:'commerce:receive-notice',mapping_ref:'commerce:message-to-order',mapping_arguments:[{parameter:'payload',path:['payload']}],request_parameter:'request',route:{method:'POST' as const,path:'/receiveNotice'},access:{kind:'public' as const}}]};
 return {cli,root,sourceRoot,input,derived,actions,graph,plan,source};
}
