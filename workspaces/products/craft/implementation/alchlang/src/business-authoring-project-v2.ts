import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadDomainSpecCompiler,type DomainSpecCompiler} from './domainspec-cli.js';
import {prepareBusinessSpecFileV2,assertResolvedBusinessSpecV2Current,disposeResolvedBusinessSpecV2} from './business-authoring-resolve.js';
import {lowerDirectBusinessV2,assertLoweredDirectBusinessV2Current} from './business-authoring-carriers.js';
import {assertDirectBusinessFormationV2Current} from './application-domain-lowering.js';
import {prepareDirectBusinessAuthoringApplicationV2,assertPreparedDirectBusinessAuthoringApplicationV2Current} from './business-authoring-prepare.js';
import {compileDirectApplicationExecutableV2} from './application-executable.js';
import {prepareDirectBusinessReviewV2,assertPreparedDirectBusinessReviewV2Current,captureDirectBusinessReviewDecisionV2,requireAcceptedDirectBusinessReviewV2} from './business-authoring-review.js';
import type {BusinessRecipeSelectionV2,BusinessEarlyRequestsV2} from './business-authoring-identity-protocol-v2.js';
import type {LoweredDirectBusinessV2} from './business-authoring-stages-v2.js';
import type {PreparedAlchDirectBusinessReviewV2} from './business-authoring-review.js';
import type {U0RuntimeBridgeV4} from './u0-runtime-bridge.js';
/** One public source-to-native prefix for every subsequent build epoch.
 * No recorded acceptance is invented, and no per-feature evaluator is accepted.
 * Open Questions: J02/Q02/K02/U04/G01/U08/U09 and U10/V02 qualification. */
function fail(message:string):never{throw new Error('BUSINESS_PROJECT_V2: '+message);}
export interface PreparedDirectBusinessAuthoringProjectV2 {
 readonly kind:'prepared-direct-business-authoring-project-v2';readonly lowered:LoweredDirectBusinessV2;
 readonly selection:BusinessRecipeSelectionV2;readonly early:BusinessEarlyRequestsV2;
 readonly review:PreparedAlchDirectBusinessReviewV2;readonly runtime:U0RuntimeBridgeV4;readonly authority_effect:'none';
}
type State={compiler:DomainSpecCompiler;runtime:U0RuntimeBridgeV4;factory:NonNullable<DomainSpecCompiler['profileEngine']['createBusinessU0RuntimeV4']>};
const prepared=new WeakMap<object,State>();
function state(value:PreparedDirectBusinessAuthoringProjectV2):State {
 const s=value&&typeof value==='object'?prepared.get(value):undefined;if(!s)fail('original prepared project required');
 if(s.compiler.profileEngine.createBusinessU0RuntimeV4!==s.factory||value.runtime!==s.runtime)fail('original public SDK factory/runtime required');
 assertResolvedBusinessSpecV2Current(value.lowered.business);assertLoweredDirectBusinessV2Current(value.lowered);s.runtime.assertCurrent();s.runtime.recipes.assertCurrent(value.selection);s.runtime.requests.assertEarlyCurrent(value.early);assertPreparedDirectBusinessReviewV2Current(value.review);return s;
}
export interface DirectBusinessProjectSelectionV2 {readonly profile:'node-http-entry-u0-v4';readonly output:'code'}
export async function prepareDirectBusinessAuthoringProjectV2(root:string,relative:string,choice:DirectBusinessProjectSelectionV2):Promise<PreparedDirectBusinessAuthoringProjectV2>{
 const module=fileURLToPath(import.meta.url);if(path.basename(path.dirname(module))!=='dist'||!module.endsWith('.js'))fail('built public AlchLang required; no private source runtime fallback');
 const compiler=await loadDomainSpecCompiler(),factory=compiler.profileEngine.createBusinessU0RuntimeV4;if(typeof factory!=='function')fail('built Core U0 v4 bootstrap export required');
 const selected=compiler.profileEngine.captureJson(choice);if(!selected||Object.keys(selected).sort().join(',')!=='output,profile'||selected.profile!=='node-http-entry-u0-v4'||selected.output!=='code')fail('explicit supported profile and code output selection required');
 const business=prepareBusinessSpecFileV2(path.resolve(root),relative);let runtime:U0RuntimeBridgeV4|undefined;
 try{runtime=await factory({frontend_root:path.dirname(path.dirname(module))});const lowered=lowerDirectBusinessV2(business),modelId=business.data.identity.namespace,captured=runtime.captureSource(modelId,path.resolve(root),relative);
  const selection=runtime.recipes.select([{model_id:modelId,source:captured.source,spec:business.data,executable_sha256:compiler.profileEngine.dataDigest(lowered.executable),assurance_sha256:compiler.profileEngine.dataDigest(lowered.assurance),capture:captured.capture}],runtime.basis);
  const early=runtime.requests.prepareEarly(selection),review=prepareDirectBusinessReviewV2(lowered,selection,runtime.reviews),value:PreparedDirectBusinessAuthoringProjectV2=Object.freeze({kind:'prepared-direct-business-authoring-project-v2',lowered,selection,early,review,runtime,authority_effect:'none'});prepared.set(value,{compiler,runtime,factory});state(value);return value;
 }catch(error){disposeResolvedBusinessSpecV2(business);if(runtime)runtime.dispose();throw error;}
}
export function assertPreparedDirectBusinessAuthoringProjectV2Current(value:PreparedDirectBusinessAuthoringProjectV2):void{state(value);}
/** Read an actual explicit decision, form original input, compile actual source,
 * emit/import actual callable, bind native entry and project genuine graph views.
 * Both output directories must be fresh; failed residue is never deleted. */
export async function replayDirectBusinessAuthoringPrefixV2(value:PreparedDirectBusinessAuthoringProjectV2,decisionFile:string,sourceProject:string,callableRoot:string){
 const s=state(value),publish=s.compiler.profileEngine.publishBusinessAuthoringDirectory;if(typeof publish!=='function')fail('public no-overwrite source writer required');
 const decision=captureDirectBusinessReviewDecisionV2(value.review,path.resolve(decisionFile)),accepted=requireAcceptedDirectBusinessReviewV2(value.review,decision);
 const input=s.runtime.inputs.form(value.selection,value.lowered.business.data.identity.namespace,accepted.accepted,value.early),prepared=prepareDirectBusinessAuthoringApplicationV2(value.lowered.business,input,Object.freeze({input:s.runtime.inputs,application:s.runtime.applications})),formation=prepared.bindings.formation;
 publish(path.resolve(sourceProject),Object.entries(formation.projectFiles).map(([relative_path,content])=>({relative_path,content})),'.domainspec-direct-source-',()=>{state(value);assertPreparedDirectBusinessAuthoringApplicationV2Current(prepared);assertDirectBusinessFormationV2Current(formation);s.runtime.inputs.assertCurrent(input);});
 s.runtime.registerProject(input,path.resolve(sourceProject));const application=compileDirectApplicationExecutableV2(prepared.executable).checked,generated=s.runtime.generation.generate(application);
 publish(path.resolve(callableRoot),generated.files.map(file=>({relative_path:file.path,content:file.content})),'.domainspec-direct-callable-',()=>{state(value);s.runtime.applications.assertCurrent(application);});
 const callable=await s.runtime.generation.importGenerated(generated,path.join(path.resolve(callableRoot),'invoke.mjs'));state(value);
 const bound=await s.runtime.requests.bindLate(value.early,callable,s.runtime.basis);state(value);
 const coverage=s.runtime.views.check(application,bound),views=s.runtime.views.project(coverage);s.runtime.views.assertCurrent(views);
 return Object.freeze({kind:'replayed-direct-business-prefix-v2' as const,prepared:value,decision,accepted,input,frontend:prepared,application,generated,callable,bound,coverage,views,authority_effect:'none' as const});
}
export function disposeDirectBusinessAuthoringProjectV2(value:PreparedDirectBusinessAuthoringProjectV2):void {const s=state(value);s.runtime.recipes.dispose(value.selection);disposeResolvedBusinessSpecV2(value.lowered.business);s.runtime.dispose();prepared.delete(value);}
