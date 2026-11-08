import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {loadDomainSpecCompiler} from './domainspec-cli.js';
import {prepareDirectBusinessAuthoringProjectV2,replayDirectBusinessAuthoringPrefixV2,disposeDirectBusinessAuthoringProjectV2,type PreparedDirectBusinessAuthoringProjectV2} from './business-authoring-project-v2.js';
import {recordDirectBusinessReviewDecisionV2} from './business-authoring-review.js';
import type {BusinessOutputKindV2,BusinessOutputRequestV2,BusinessOutputPlanV2} from './business-authoring-coverage-contract-v2.js';
/** Explicit successor lifecycle; legacy project commands keep their original branch.
 * Open Questions: docs/BUSINESS-AUTHORING.md; installed qualification follows U10.
 * Review/decision commands do not generate code or grant operational approval. */
const contract='alchlang.business-spec/v2-candidate';
const help=`alchlang business direct check|review <business.alch> --profile node-http-entry-u0-v4 --output code
alchlang business direct decision <business.alch> --profile node-http-entry-u0-v4 --output code --owner <owner> --outcome accepted|declined --digest <displayed-decision-scope-sha256> --decision-id <id> --record <new-decision.json>
alchlang business direct generate <business.alch> --profile node-http-entry-u0-v4 --output code --decision <decision.json> --out <new-directory> [--require-output <kind>] [--optional-output <kind>]
Code mode includes API contracts and business/system/bridge views. Formal claims are optional. Required unavailable formal output rejects before staging. Hosting, TDE, EVF and publication are deferred.`;
function fail(message:string):never{throw Object.assign(new Error(message),{code:'BUSINESS_DIRECT_COMMAND'});}
export async function runDirectBusinessAuthoringCommandV2(args:readonly string[],io:{stdout(value:string):void;stderr(value:string):void}):Promise<number>{
 if(args.length===0||args.length===1&&args[0]==='--help'){io.stdout(help);return 0;}
 let prepared:PreparedDirectBusinessAuthoringProjectV2|undefined,scratch:string|undefined;
 try{
  const [command,source,...rest]=args;if(!command||!['check','review','decision','generate'].includes(command)||!source||source.startsWith('--'))fail('explicit supported command and business source required');
  const allowed=new Set(['--profile','--output',...(command==='decision'?['--owner','--outcome','--digest','--decision-id','--record']:command==='generate'?['--decision','--out','--require-output','--optional-output']:[])]),options=new Map<string,string>(),extra:BusinessOutputRequestV2[]=[];
  for(let index=0;index<rest.length;index+=2){const key=rest[index]!,value=rest[index+1];if(!allowed.has(key)||!value||value.startsWith('--'))fail('unsupported option or missing value: '+key);
   if(key==='--require-output'||key==='--optional-output')extra.push({kind:value as BusinessOutputKindV2,requiredness:key==='--require-output'?'required':'optional'});
   else {if(options.has(key))fail('duplicate option: '+key);options.set(key,value);}
  }
  const required=(key:string)=>options.get(key)??fail('required '+key);
  if(required('--profile')!=='node-http-entry-u0-v4'||required('--output')!=='code')fail('explicit supported profile and code output required');
  if(command==='decision'){for(const key of ['--owner','--outcome','--digest','--decision-id','--record'])required(key);if(!['accepted','declined'].includes(required('--outcome')))fail('explicit accepted or declined outcome required');}
  if(command==='generate'){required('--decision');required('--out');}
  const compiler=await loadDomainSpecCompiler(),engine=compiler.profileEngine as unknown as {planBusinessOutputsV2(input:readonly BusinessOutputRequestV2[]):BusinessOutputPlanV2};if(typeof engine.planBusinessOutputsV2!=='function')fail('matching public Core output planner required');
  // Reject unavailable required exporters before creating a project or scratch output.
  const outputs=engine.planBusinessOutputsV2([{kind:'code',requiredness:'required'},{kind:'api-contracts',requiredness:'required'},{kind:'business-graph',requiredness:'required'},{kind:'system-graph',requiredness:'required'},{kind:'business-system-bridge',requiredness:'required'},...extra]);
  const absolute=path.resolve(source);prepared=await prepareDirectBusinessAuthoringProjectV2(path.dirname(absolute),path.basename(absolute),{profile:'node-http-entry-u0-v4',output:'code'});
  const review=prepared.review.review,decision_scope_sha256=compiler.profileEngine.dataDigest({review_sha256:review.review_sha256,capture_sha256:review.source_capture.capture_sha256}),base={decision_scope_sha256,source_contract:contract,profile:'node-http-entry-u0-v4',output:'code',model_id:review.model_id,review_sha256:review.review_sha256,source_capture:review.source_capture,sdk_sha256:prepared.runtime.basis.sdk_sha256,subject:review.subject,authority_effect:'none'};
  let result:unknown;
  if(command==='check'||command==='review')result={...base,status:command==='check'?'checked':'reviewed',acceptance:'not-recorded',generation:'not-performed'};
  else if(command==='decision'){
   if(required('--digest')!==decision_scope_sha256)fail('current displayed review/capture scope digest required');
   const decision=recordDirectBusinessReviewDecisionV2(prepared.review,{owner:required('--owner'),outcome:required('--outcome') as 'accepted'|'declined',reviewed_digest:review.review_sha256,decision_id:required('--decision-id')},path.resolve(required('--record')));
   result={...base,status:'recorded',outcome:decision.decision.decision.outcome,decision_file:decision.decision.file};
  }else{
   scratch=fs.mkdtempSync(path.join(os.tmpdir(),'alchlang-u0-build-'));
   const joined=await replayDirectBusinessAuthoringPrefixV2(prepared,path.resolve(required('--decision')),path.join(scratch,'source'),path.join(scratch,'callable'));
   const artifacts=prepared.runtime.output.prepareArtifacts(outputs,joined.application,joined.bound,joined.views),target=path.resolve(required('--out')),output=prepared.runtime.output.publish({target,plan:outputs,application:joined.application,bound:joined.bound,views:joined.views,artifacts});
   result={...base,status:'generated',output_directory:target,scratch_path:scratch,realized_subject:joined.bound.subject,coverage_sha256:joined.coverage.coverage_sha256,views_sha256:joined.views.views_sha256,outputs:output,execution:'not-observed; generated handler requires independent qualification'};
  }
  io.stdout(JSON.stringify(result,null,2));return 0;
 }catch(error){io.stderr(JSON.stringify({status:'rejected',code:(error as {code?:string}).code??'BUSINESS_DIRECT_ERROR',message:(error as Error).message,...(scratch?{scratch_path:scratch}:{}),authority_effect:'none'}));return 1;
 }finally{if(prepared)disposeDirectBusinessAuthoringProjectV2(prepared);}
}
