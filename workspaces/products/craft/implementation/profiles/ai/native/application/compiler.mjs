/** Reusable implementation-profile recipe over the existing generic source path.
 * Original business bytes remain the prefix; generated technical entities and
 * protected Entries bind the original Workflow/SQLite/Auth owners.
 * Open Questions: README.md#open-questions. */
import {inspectGenericNativeProfileArtifact,genericNativeCapabilityIdentity} from '@domainspec-v2/cli/generic';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';import path from 'node:path';
import {assert,canonical,capture,closed,freeze,sha256,text} from '../shared.mjs';
import {validateApplicationErrorPresentation,applicationErrorProjectionSource,composeApplicationErrorPresentations} from './error-presentation.mjs';
import {validateExecutionAdmission,executionAdmissionSource,executionAdmissionKernelIdentity,executionAdmissionErrorTable} from './execution-admission.mjs';
export const serviceBusinessInputContracts=Object.freeze(['customer-support/domain-v1','invoice-draft/domain-v1','marketing-campaign/domain-v1']);
export const isServiceApplication=profile=>serviceBusinessInputContracts.includes(profile.businessInputContract);
const hasPrivateAdmission=p=>Boolean(p.executionAdmission)||isServiceApplication(p);
const symbol=value=>{assert(typeof value==='string'&&/^[A-Za-z_][A-Za-z0-9_]*$/.test(value),'InvalidContract','source symbol');return value;};
const txHandlers=`    on-unique-conflict reject duplicate-profile-record\n    on-proven-rollback fail storage-rolled-back\n    on-unknown-commit fail outcome-unknown`;
function validateKnowledgeBusinessSource(family,raw){
 const source=closed(raw,['roles','factsRole','approvalRole','policyId','target','projections','timeUnit']);assert(source.factsRole==='facts'&&source.approvalRole==='approval'&&source.timeUnit==='unix-milliseconds','UnsupportedCapability','finite knowledge source owners/clock');
 const expected=new Map([['facts',{format:'json',disclose:true}],['approval',{format:'json',disclose:false}],['documentA',{format:'binary',disclose:true}],['documentB',{format:'binary',disclose:true}]]),prefixes=new Set();assert(Array.isArray(source.roles)&&source.roles.length===4,'InvalidContract','four original knowledge document roles');for(const rawRole of source.roles){const role=closed(rawRole,['role','prefix','format','disclose','minimumOrdinal'],['role','prefix','format','disclose']),contract=expected.get(role.role);assert(contract&&role.format===contract.format&&role.disclose===contract.disclose&&(role.minimumOrdinal===undefined||role.minimumOrdinal===1)&&typeof role.prefix==='string'&&/^[a-z][a-z0-9-]{0,63}-$/.test(role.prefix)&&!prefixes.has(role.prefix),'InvalidContract','original knowledge source role/prefix');expected.delete(role.role);prefixes.add(role.prefix);}
 const projection=closed(source.projections,['modelInput','review']),samePaths=(value,paths)=>{const fields=closed(value,Object.keys(paths));for(const [key,from] of Object.entries(paths)){const item=closed(fields[key],['from']);assert((Array.isArray(from)?from:[from]).includes(item.from),'InvalidContract','original knowledge producer for '+key);}};
 samePaths(projection.modelInput,{subjectId:'id',sourceVersion:'sources.facts.revision',prompt:'technical.prompt'});samePaths(projection.review,family==='permissioned-rag/domain-v1'?{evidenceContext:'technical.evidenceContext',answerSupported:'technical.answerSupported',injectionDetected:'technical.injectionDetected',retrievalAvailable:'technical.retrievalAvailable'}:{state:'technical.state',format:'technical.format',chunks:'technical.chunks',generation:['technical.generation','facts.generation'],deletionRequested:'facts.deletionRequested',parsed:'technical.parsed'});assert(source.target.sink===(family==='permissioned-rag/domain-v1'?'app:answer':'local:index'),'InvalidContract','selected knowledge target sink');
}
export function validateApplicationProfile(raw){const p=closed(raw,['schema','id','module','service','scope','operation','types','stages','entryAccess','sourceSelection','effectOperation','reviewOperation','additionalSources','errorPresentation','executionAdmission','businessInputContract'],['schema','id','module','service','scope','operation','types','stages','entryAccess']);assert(p.schema==='craft.ai-application-profile/v1','UnsupportedCapability','selected application profile');for(const k of ['id','scope']){text(p[k],k,128);assert(/^[A-Za-z][A-Za-z0-9_.-]*$/.test(p[k]),'InvalidContract','finite access token');}const sourceEntry=closed(p.entryAccess,['sourcePath','entry']);assert(path.isAbsolute(sourceEntry.sourcePath)&&/^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$/.test(sourceEntry.entry),'InvalidContract','actual authored Entry selection');for(const k of ['module','service','operation'])symbol(p[k]);if(p.effectOperation!==undefined)symbol(p.effectOperation);if(p.reviewOperation!==undefined)symbol(p.reviewOperation);if(p.additionalSources){assert(Array.isArray(p.additionalSources)&&p.additionalSources.length<=8,'InvalidContract','bounded authored source components');for(const c of p.additionalSources){closed(c,['sourcePath','sha256']);assert(path.isAbsolute(c.sourcePath)&&/^[a-f0-9]{64}$/.test(c.sha256),'InvalidContract','actual authored component identity');}}if(p.businessInputContract!==undefined){assert(['knowledge-ingestion/domain-v1','permissioned-rag/domain-v1',...serviceBusinessInputContracts].includes(p.businessInputContract)&&p.executionAdmission===undefined,'UnsupportedCapability','selected finite knowledge business input contract');}if(p.executionAdmission!==undefined){p.executionAdmission=validateExecutionAdmission(p.executionAdmission);assert(p.errorPresentation!==undefined,'InvalidContract','domain execution admission requires typed error presentation');}if(p.errorPresentation!==undefined){p.errorPresentation=validateApplicationErrorPresentation(p.errorPresentation);if(p.executionAdmission){const technical=executionAdmissionErrorTable(p.module);if(p.errorPresentation.schema_version==='craft.error-presentation-set/v1'){const matches=p.errorPresentation.tables.filter(table=>table.producer===technical.producer);assert(matches.length===1&&canonical(matches[0])===canonical(technical),'InvalidContract','mandatory exact technical admission presentation');}else p.errorPresentation=composeApplicationErrorPresentations(p.errorPresentation,technical,{kernelIdentity:executionAdmissionKernelIdentity()});}}const types=closed(p.types,['request','modelInput','proposal','decision']);for(const value of Object.values(types))symbol(value);assert(Array.isArray(p.stages)&&p.stages.length>0&&p.stages.length<=16,'ResourceLimit','bounded application stages');const seen=new Set();for(const raw of p.stages){const s=closed(raw,['name','kind','capability_binding','capability_sha256','deadline_ms','decision_acceptance_rule','businessOperation','observationOperation'],['name','kind','capability_binding','capability_sha256','deadline_ms']);if(s.decision_acceptance_rule!==undefined)symbol(s.decision_acceptance_rule);for(const k of ["businessOperation","observationOperation"])if(s[k]!==undefined)symbol(s[k]);symbol(s.name);assert(!seen.has(s.name)&&['model','document','index','provider','agent-run'].includes(s.kind),'InvalidContract','unique selected native stages');seen.add(s.name);text(s.capability_binding);assert(/^[a-f0-9]{64}$/.test(s.capability_sha256)&&Number.isSafeInteger(s.deadline_ms)&&s.deadline_ms>0&&s.deadline_ms<=300000,'InvalidContract','actual stage descriptor/duration');}if(p.sourceSelection)p.sourceSelection=selectApplicationSourceDescriptor(p.sourceSelection,{maximumStages:p.stages.length});if(p.businessInputContract){assert(p.sourceSelection,'InvalidContract','knowledge business inputs require checked source formation');if(!isServiceApplication(p))validateKnowledgeBusinessSource(p.businessInputContract,p.sourceSelection);}return freeze(p);}
export function applicationSelectors(raw){const p=validateApplicationProfile(raw),q=name=>p.module+'.'+name;return freeze({service:p.service,start:q('ProfileStartEntry'),principal:q('ProfilePrincipalEntry'),job:q('ProfileReadJobEntry'),stage:q('ProfileReadStageEntry'),status:q('ProfileStatusEntry'),evaluate:q('ProfileWorkerEvaluateEntry'),publicEvaluate:q('ProfileEvaluateEntry'),executionAdmission:hasPrivateAdmission(p)?q('ProfileExecutionAdmissionEntry'):null,review:p.reviewOperation?q('ProfileWorkerReviewEntry'):null,effectEvaluate:p.effectOperation?q('ProfileWorkerEffectEvaluateEntry'):q('ProfileWorkerEvaluateEntry'),capture:q('ProfileCaptureInputEntry'),workflow:q('ProfileWorkflow'),stages:p.stages.map((s,index)=>({name:s.name,binding:s.capability_binding,ordinal:index+1,entry:q('ProfileStage'+index+'Entry'),continuation:q('ProfileContinue'+index+'Entry'),evaluate:s.businessOperation?q('ProfileBusiness'+index+'Entry'):null,observation:s.observationOperation?q('ProfileObservation'+index+'Entry'):null}))});}
function readEntryAccess(p){const bytes=readFileSync(p.entryAccess.sourcePath),source=new TextDecoder('utf8',{fatal:true}).decode(bytes),lines=source.split('\n'),start=lines.indexOf('entry '+p.entryAccess.entry+':');assert(start>=0,'InvalidContract','selected authored Entry exists');const block=[];for(let i=start+1;i<lines.length&&/^  /.test(lines[i]);i++)block.push(lines[i]);assert(block[0]==='  invokes '+p.module+'.'+p.operation&&block[1]==='  interaction request-response'&&block[2]==='  access:'&&block.length===8,'InvalidContract','finite original request-response Entry');const access=block.slice(3).join('\n')+'\n';assert(/^    authenticated customer\n    permission [A-Za-z0-9_.-]+\n    auth-resource [A-Za-z0-9_.-]+\n    auth-action [A-Za-z0-9_.-]+\n    auth-scope [A-Za-z0-9_.-]+\n$/.test(access),'InvalidContract','exact authored business access');assert(block[7]==='    auth-scope '+p.scope&&block[4].slice(15)===block[5].slice(18)+'.'+block[6].slice(16),'InvalidContract','authored Entry scope/resource permission');return {bytes,access,sha256:sha256(bytes)};}
function mirror(p,authored){const entry=(name,target,principal='operator',business=false)=>`entry ${p.module}.${name}:\n  invokes ${p.module}.${target}\n  interaction request-response\n  access:\n${business?authored.access.replace('authenticated customer','authenticated '+principal):`    authenticated ${principal}\n    permission ${p.id}.${name}\n    auth-resource ${p.id}\n    auth-action ${name}\n    auth-scope ${p.scope}\n`}`;
 const header=`\n${hasPrivateAdmission(p)?executionAdmissionSource()+'\n':''}${p.errorPresentation?applicationErrorProjectionSource(p.errorPresentation,{providerBindings:p.stages.filter(s=>s.kind==='provider')}):''}value-object ProfileWire:
  carrier String
  utf8-bytes 0..32768
  unicode-scalars 0..32768

value-object ProfileMetrics:
  emailsSent optional<UInt64>
  opensTotal optional<UInt64>
  uniqueOpens optional<UInt64>
  clicksTotal optional<UInt64>
  uniqueClicks optional<UInt64>
  hardBounces optional<UInt64>
  softBounces optional<UInt64>
  unsubscribed optional<UInt64>
  observedAt String
  partial Bool

value-object ProfileReceipt:
  status String
  providerId String
  contextManifest optional<String>
  amountMinor optional<UInt64>
  metrics optional<ProfileMetrics>

value-object ProfileStageOutput:
  id UInt64
  run UInt64
  accepted Bool
  reason String
  proposal optional<${p.types.proposal}>
  proposalWire optional<ProfileWire>
${hasPrivateAdmission(p)||p.businessInputContract==='permissioned-rag/domain-v1'?'  candidateOrigin optional<ProfileWire>\n':''}  decision optional<${p.types.decision}>
  receipt optional<ProfileReceipt>
${p.errorPresentation?'  diagnostic optional<ProfileDiagnostic>\n':''}
entity ProfileJob:
  run UInt64
  id UInt64
  owner Craft.Generated.Auth.ReadySubjectId
  configurationDigest String
  identity run

entity ProfileStageInput:
  run UInt64
  ordinal UInt64
  attempt UInt64
  sourceDigest String
  identity run, ordinal, attempt

operation ProfileCaptureInput:
  input run UInt64
  input ordinal UInt64
  input attempt UInt64
  input sourceDigest String
  output ProfileStageInput
  transaction ProfileCaptureInput:
    atomic-participants ProfileStageInput
    create captured ProfileStageInput:
      run <- run
      ordinal <- ordinal
      attempt <- attempt
      sourceDigest <- sourceDigest
${txHandlers}
  return captured

entity ProfileStageWork:
  run UInt64
  id UInt64
  ordinal UInt64
  attempt UInt64
  identity run, ordinal, attempt

entity ProfileStageResult:
  run UInt64
  ordinal UInt64
  attempt UInt64
  owner Craft.Generated.Auth.ReadySubjectId
  value ProfileStageOutput
  identity run, ordinal, attempt

entity ProfileContinuation:
  run UInt64
  ordinal UInt64
  stageRevision UInt64
  kind String
  code String
  identity run, ordinal, stageRevision

${p.errorPresentation?`value-object ProfilePublicStatus:
  id UInt64
  run UInt64
  accepted Bool
  error optional<ProfilePublicError>

mapping ProfilePublicProjection:
  input result ProfileStageOutput
  target ProfilePublicStatus
  total true
  field id <- result.id
  field run <- result.run
  field accepted <- result.accepted
  field error <- ProfileSelectPublicError(result=result)

`:`value-object ProfilePublicStatus:
  id UInt64
  run UInt64
  accepted Bool
  reason String
  receipt optional<ProfileReceipt>

mapping ProfilePublicProjection:
  input result ProfileStageOutput
  target ProfilePublicStatus
  total true
  field id <- result.id
  field run <- result.run
  field accepted <- result.accepted
  field reason <- result.reason
  field receipt <- result.receipt

`}operation ProfilePrincipal:
  input run UInt64
  context actor Craft.Generated.Auth.CustomerContext
  output Craft.Generated.Auth.ReadySubjectId
  return actor.customerId

query ProfileReadJob:
  input run UInt64
  source stored ProfileJob
  output optional<ProfileJob>
  where stored.run == run
  project stored
  on-missing return none
  on-unavailable fail read-unavailable

query ProfileReadStage:
  input run UInt64
  input ordinal UInt64
  input attempt UInt64
  source stored ProfileStageResult
  output optional<ProfileStageOutput>
  where stored.run == run and stored.ordinal == ordinal and stored.attempt == attempt
  project stored.value
  on-missing return none
  on-unavailable fail read-unavailable

query ProfileStatus:
  input run UInt64
  input ordinal UInt64
  input attempt UInt64
  context actor Craft.Generated.Auth.CustomerContext
  source stored ProfileStageResult
  output optional<ProfilePublicStatus>
  where stored.run == run and stored.ordinal == ordinal and stored.attempt == attempt and stored.owner == actor.customerId
  project ProfilePublicProjection(stored.value)
  on-missing return none
  on-unavailable fail read-unavailable

operation ProfileStart:
  input id UInt64
  input run UInt64
  context actor Craft.Generated.Auth.CustomerContext
  output ProfileJob
  transaction ProfileStart:
    atomic-participants ProfileJob
    create job ProfileJob:
      run <- run
      id <- id
      owner <- actor.customerId
      configurationDigest <- "${sha256(canonical(p))}"
${txHandlers}
  return job

${entry('ProfileStartEntry','ProfileStart','customer',true)}
${entry('ProfilePrincipalEntry','ProfilePrincipal')}
${entry('ProfileReadJobEntry','ProfileReadJob')}
${entry('ProfileReadStageEntry','ProfileReadStage')}
${entry('ProfileStatusEntry','ProfileStatus','customer',true)}
${entry('ProfileEvaluateEntry',p.operation,'customer',true)}
${entry('ProfileWorkerEvaluateEntry',p.operation,'operator',true)}
${entry('ProfileCaptureInputEntry','ProfileCaptureInput')}
${hasPrivateAdmission(p)?entry('ProfileExecutionAdmissionEntry','ProfileAdmitExecution','operator',true):''}
${p.effectOperation?entry('ProfileWorkerEffectEvaluateEntry',p.effectOperation,'operator',true):''}
${p.reviewOperation?entry('ProfileWorkerReviewEntry',p.reviewOperation,'operator',true):''}
`;
 const stages=p.stages.map((s,i)=>`
calculation ProfileSuccess${i}:
  pure
  input result ProfileStageOutput
  result String
  expression "${i===p.stages.length-1?'complete':'advance'}"

calculation ProfileRejected${i}:
  pure
  input result ProfileStageOutput
  result String
  expression "business-rejection"

policy ProfileDisposition${i}:
  input result ProfileStageOutput
  result String
  ordered-cases:
    accepted when result.accepted${s.decision_acceptance_rule?` and present(result.decision) and ${s.decision_acceptance_rule}(require-some(result.decision))`:""} -> ProfileSuccess${i}(result=result)
    otherwise -> ProfileRejected${i}(result=result)

operation ProfileStage${i}:
  input id UInt64
  input run UInt64
  input stageAttempt UInt64
  output ProfileStageWork
  transaction ProfileStage${i}:
    atomic-participants ProfileStageWork
    create work ProfileStageWork:
      run <- run
      id <- id
      ordinal <- ${i+1}
      attempt <- stageAttempt
${txHandlers}
  return work

operation ProfileContinue${i}:
  input id UInt64
  input run UInt64
  input stageResult ProfileStageOutput
  input stageAttempt UInt64
  input stageRevision UInt64
  output ProfileContinuation
  read job from ${p.module}.ProfileReadJobEntry(run=run)
    on-missing reject profile-job-missing
    on-unavailable fail profile-job-unavailable
  requires job.id == id and stageResult.id == id and stageResult.run == run on-false reject profile-result-identity
  transaction ProfileContinue${i}:
    atomic-participants ProfileStageResult, ProfileContinuation
    create stored ProfileStageResult:
      run <- run
      ordinal <- ${i+1}
      attempt <- stageAttempt
      owner <- job.owner
      value <- stageResult
    create disposition ProfileContinuation:
      run <- run
      ordinal <- ${i+1}
      stageRevision <- stageRevision
      kind <- ProfileDisposition${i}(stageResult)
      code <- stageResult.reason
${txHandlers}
  return disposition

${entry('ProfileStage'+i+'Entry','ProfileStage'+i)}
${entry('ProfileContinue'+i+'Entry','ProfileContinue'+i)}
${s.businessOperation?entry('ProfileBusiness'+i+'Entry',s.businessOperation,'operator',true):''}
${s.observationOperation?entry('ProfileObservation'+i+'Entry',s.observationOperation,'operator',true):''}
`).join('');return header+stages+`\nworkflow ProfileWorkflow:\n  owner ${p.service}\n  scope generated-recoverable\n  profile contracts/workflow-profile.json\n  input id UInt64\n  input run UInt64\n  correlation run\n  durable-state ${p.module}.ProfileJob\n  start ${p.module}.ProfileStartEntry\n`+p.stages.map((s,i)=>`  step ${s.name} invokes ${p.module}.ProfileStage${i}Entry\n`).join('')+'  recovery needed-compensations-only reverse-completion\n';}
export function compileApplicationProfile({businessSourcePath,profile:raw,baseProfile:rawBase,capabilitySelection,kernel,nativeSelections=[],outputDirectory}){
 const p=validateApplicationProfile(raw);assert(path.isAbsolute(businessSourcePath)&&path.isAbsolute(outputDirectory),'InvalidContract','absolute source/output paths');const bytes=readFileSync(businessSourcePath),source=new TextDecoder('utf8',{fatal:true}).decode(bytes);assert(new RegExp('^module '+p.module+' version 1(?:\\r?\\n)').test(source),'InvalidContract','profile selects actual source module');
 const base=capture(rawBase);assert(['craft.generic-transaction-profile/v1-candidate','craft.generic-event-profile/v1-candidate'].includes(base.schema_version),'UnsupportedCapability','existing transaction/event profile required');const event={...base,schema_version:'craft.generic-event-profile/v1-candidate',storage:'sqlite-fenced-event-handoff/v1-candidate',capabilities:base.capabilities.includes('Event')?base.capabilities:[...base.capabilities.filter(c=>c!=='operation-policy-enforcement'),'Event','event-handoff',...(base.capabilities.includes('operation-policy-enforcement')?['operation-policy-enforcement']:[])],services:[{id:p.service,module:p.module}],application_namespace:p.module+(p.errorPresentation?'.GeneratedProfileErrorsV1':'.GeneratedProfile'),string_policy:{max_utf8_bytes:256,max_scalars:256},event_handoff:{transport:'process-local-checked-envelope/v1-candidate',delivery:'durable-at-least-once/v1-candidate'}};
 const components=(p.additionalSources??[]).map(c=>{const original=readFileSync(c.sourcePath);assert(sha256(original)===c.sha256,'StaleOwner','authored business component changed');const decoded=new TextDecoder('utf8',{fatal:true}).decode(original),header=decoded.match(new RegExp('^module '+p.module+' version 1(?:\\r?\\n)'));assert(header,'InvalidContract','same explicit authored module component');return {...c,bytes:original.length,headerBytes:Buffer.byteLength(header[0]),body:decoded.slice(header[0].length)};});let assembled=source;const componentOrigins=[];for(const c of components){assembled+='\n';const start=Buffer.byteLength(assembled);assembled+=c.body;componentOrigins.push({path:c.sourcePath,sha256:c.sha256,bytes:c.bytes,original_header_bytes:c.headerBytes,combined_start_byte:start,combined_end_byte:Buffer.byteLength(assembled),classification:'authored-business-component'});}const authored=readEntryAccess(p),technical=mirror(p,authored),combined=assembled+technical,profileText=canonical(event),selectors=applicationSelectors(p);mkdirSync(outputDirectory);mkdirSync(path.join(outputDirectory,'contracts'));const write=(name,value)=>writeFileSync(path.join(outputDirectory,name),typeof value==='string'?value:canonical(value)+'\n',{flag:'wx'});
 write('business.alch',combined);write('contracts/authored-entry.alch',new TextDecoder().decode(authored.bytes));write('contracts/selected-profile.json',profileText);write('contracts/bounds.json',{schema_version:'craft.generic-compute-bounds/v1-candidate',computation:{required_schema_version:'craft.generic-computation/v1-candidate',required_semantics_revision:'ordered-metered-generic-v1-candidate',limits:event.limits}});write('contracts/transactions.json',event.transaction_bounds);
 const workflow={schema_version:'craft.generic-workflow-profile/v2',workflow:selectors.workflow,base_event_profile_sha256:sha256(canonical(event)),capabilities:[...event.capabilities,'Workflow','recoverable-workflow'],recovery:'needed-compensations-only/reverse-completion-v1',storage:'service-owned-fenced-workflow-journal/v1-candidate',stages:p.stages.map(({decision_acceptance_rule,businessOperation,observationOperation,...s},i)=>({...s,continuation_entry:selectors.stages[i].continuation,maximum_attempts:1,stage_result_type:p.module+'.ProfileStageOutput'}))};write('contracts/workflow-profile.json',workflow);
 if(capabilitySelection){const s=capture(capabilitySelection);s.source_sha256=sha256(combined);s.profile_sha256=sha256(profileText);assert(kernel,'InvalidContract','selected kernel required');s.kernel={path:'kernel.json',sha256:sha256(canonical(kernel))};write('selection.json',s);write('kernel.json',kernel);}
 const origins={schema:'craft.application-profile-origins/v1',profile:p,...(hasPrivateAdmission(p)?{executionAdmissionKernel:{path:new URL('./execution-admission-v1.alch',import.meta.url).pathname,sha256:executionAdmissionKernelIdentity()}}:{}),source:{path:businessSourcePath,sha256:sha256(bytes),bytes:bytes.length},additionalSources:componentOrigins,entrySource:{path:p.entryAccess.sourcePath,entry:p.entryAccess.entry,sha256:authored.sha256,captured:'contracts/authored-entry.alch'},mirror:{path:'business.alch',sha256:sha256(combined),original_prefix_bytes:bytes.length,technical_suffix_sha256:sha256(technical),technical_start_byte:Buffer.byteLength(assembled),...(hasPrivateAdmission(p)?{execution_admission_kernel:{path:new URL('./execution-admission-v1.alch',import.meta.url).pathname,sha256:executionAdmissionKernelIdentity()}}:{})},selectors,authority_effect:'none'};write('origins.json',origins);const bindingManifest={schema:'craft.application-artifact-bindings/v1',source:{combined_sha256:sha256(combined),authored_prefix:origins.source,additional_authored:componentOrigins,original_prefix_bytes:bytes.length,generated_suffix:{classification:'generated-technical-recipe',combined_start_byte:Buffer.byteLength(assembled),recipe_path:new URL(import.meta.url).pathname,recipe_sha256:sha256(readFileSync(new URL(import.meta.url))),suffix_sha256:sha256(technical)}},authored_entry:origins.entrySource,selectors,workflow:{selector:selectors.workflow,stages:p.stages},native_capability_selection:capabilitySelection?{bindings:capabilitySelection.bindings,realizations:capabilitySelection.realizations,kernel}:null,native_selections:capture(nativeSelections),graph_join:'extend-original-generated-graph-by-hash;never-rewrite-bundle',authority_effect:'none'};write('application-bindings.json',bindingManifest);assert(sha256(readFileSync(businessSourcePath))===origins.source.sha256,'StaleOwner','authored source changed during projection');assert(sha256(readFileSync(p.entryAccess.sourcePath))===authored.sha256,'StaleOwner','authored Entry source changed during projection');return freeze({directory:outputDirectory,bindingManifestPath:path.join(outputDirectory,'application-bindings.json'),sourcePath:path.join(outputDirectory,'business.alch'),profilePath:path.join(outputDirectory,'contracts/selected-profile.json'),...(capabilitySelection?{capabilitySelectionPath:path.join(outputDirectory,'selection.json')}:{}),origins,selectors,profile:p});
}

/** Configure the admitted public inference kernel template. Core independently
 * checks the resulting contract, source DTOs and actual native artifact tuple. */
export function createApplicationInferenceSelection({profile,kernelTemplate,artifact,exportPath='./application',target,bounds,mode='fixture'}){
 const module=symbol(profile.module);for(const k of ['modelInput','proposal'])symbol(profile.types[k]);assert(mode==='fixture'||mode==='provider','InvalidContract','explicit model evidence mode');const inspected=inspectGenericNativeProfileArtifact(artifact),namespace=module+'.Inference',replace=value=>Array.isArray(value)?value.map(replace):value&&typeof value==='object'?Object.fromEntries(Object.entries(value).map(([k,v])=>[k,replace(v)])):typeof value==='string'?(value==='Example.Model'?module+'.Model':value==='Example.Workflow'?module+'.ProfileWorkflow':value.replace(/^Example\./,namespace+'.')):value,kernel=replace(capture(kernelTemplate));assert(kernel.schema_version==='domainspec.integration-kernel/v2-candidate'&&/^[a-f0-9]{64}$/.test(kernel.definition_pack_sha256)&&kernel.integration_bindings.length===1&&kernel.provider_realizations.length===1,'InvalidContract','admitted single inference kernel template');const checkedBounds=closed(bounds,['max_input_bytes','max_output_bytes','max_items','deadline_ms','max_model_attempts','max_tool_calls']);assert(checkedBounds.max_model_attempts===1&&checkedBounds.max_tool_calls===0,'UnsupportedCapability','one original model attempt/no tools');const realization={id:namespace+'.Native',integration_binding_ref:kernel.integration_bindings[0].binding_id,contract:'inference/v1',implementation:{package:inspected.name,version:inspected.version,sha256:inspected.sha256,export:exportPath},operations:['text.structured'],capabilities:['structured-output'],mode,target:capture(target),schema:{dialect:'https://json-schema.org/draft/2020-12/schema',subset:'checked-business-values/v1'},bounds:checkedBounds,lifecycle:{credential_slot_ref:null,compatibility:'exact-contract-and-target',retention_policy_ref:namespace+'.Retention',credential_lifecycle_ref:namespace+'.Credentials',synchronization_ref:namespace+'.Sync',retirement_ref:namespace+'.Retirement',fallback:'none',completion:'validated-proposal-only',unknown_effect:'reconcile-before-retry'}},binding={id:namespace+'.Selection',interface:module+'.Model',contract:{kind:'inference/v1',operation:'text.structured',input_type:module+'.'+profile.types.modelInput,result_type:module+'.'+profile.types.proposal,required_capabilities:['structured-output'],tools:'disabled',embedding:null},realization_ref:realization.id,bounds:checkedBounds},integration=kernel.integration_bindings[0],resource=kernel.provider_realizations[0],provider_lineage={integration_binding_ref:integration.binding_id,provider_realization_ref:resource.realization_id,provider_profile_ref:resource.provider_profile_ref,resource_ref:resource.resource_ref,adapter_ref:resource.adapter_ref},identity=genericNativeCapabilityIdentity({contract_sha256:sha256(canonical(binding.contract)),realization_sha256:sha256(canonical(realization)),provider_lineage,realization}),selection={schema_version:'craft.generic-capability-selection/v1',source_sha256:null,profile_sha256:null,kernel:{path:'kernel.json',sha256:sha256(canonical(kernel))},bindings:[binding],realizations:[realization],authority_effect:'none'};return freeze({selection,kernel,bindingId:binding.id,capability_sha256:identity,implementation:realization.implementation});
}

export function resolveApplicationProfile({intent,bindings,sourceDirectory}){const p=capture(intent);assert(p.schema==='craft.ai-application-intent/v1'&&bindings instanceof Map&&path.isAbsolute(sourceDirectory),'InvalidContract','selected profile intent/original native bindings');p.schema='craft.ai-application-profile/v1';if(p.additionalSources)p.additionalSources=p.additionalSources.map(relative=>{const sourcePath=path.resolve(sourceDirectory,relative);return {sourcePath,sha256:sha256(readFileSync(sourcePath))};});if(p.sourceSelectionPath){p.sourceSelection=selectApplicationSourceDescriptor(JSON.parse(readFileSync(path.resolve(sourceDirectory,p.sourceSelectionPath),'utf8')));delete p.sourceSelectionPath;}p.entryAccess.sourcePath=path.resolve(sourceDirectory,p.entryAccess.sourcePath);p.stages=p.stages.map(stage=>{const identity=bindings.get(stage.capability_binding);assert(typeof identity==='string'&&/^[a-f0-9]{64}$/.test(identity),'InvalidContract','actual selected native binding identity');return {...stage,capability_sha256:identity};});return validateApplicationProfile(p);}

/** Provider slots remain original R02 contracts, separate from C03 inference. */
export function applicationProviderSelectionIdentity({artifact,selection}){const {release,...profile}=selection;return sha256(canonical({schema:'craft.original-provider-stage-selection/v1',implementation_sha256:inspectGenericNativeProfileArtifact(artifact).sha256,profile:capture(profile)}));}

export function selectApplicationSourceDescriptor(raw,{maximumStages=16}={}){assert(Array.isArray(raw.roles)&&raw.roles.length>0&&raw.roles.length<=16,'InvalidContract','finite selected source roles');for(const role of raw.roles){assert(Object.keys(role).every(k=>['role','prefix','format','disclose','adapter','minimumOrdinal'].includes(k)),'InvalidContract','closed selected source role');if(role.minimumOrdinal!==undefined)assert(Number.isSafeInteger(role.minimumOrdinal)&&role.minimumOrdinal>=1&&role.minimumOrdinal<=maximumStages&&role.disclose===false,'InvalidContract','only nondisclosed controls maydefer within actual finite workflow');}return capture({roles:raw.roles,factsRole:raw.factsRole??"facts",approvalRole:raw.approvalRole??"approval",policyId:raw.policyId,target:raw.target,projections:raw.projections,timeUnit:raw.timeUnit??"unix-milliseconds",...(raw.document?{document:raw.document}:{}),...(raw.recipientRelease?{recipientRelease:raw.recipientRelease}:{})});}
