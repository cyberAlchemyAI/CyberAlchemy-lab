/** Independent typed Workflow source facets. These describe required original
 * worker/entry/journal/store evidence, never create those owners or execute it.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail,CoreCommerceSourceError,coreSourceChildren as children,coreSourceChild as child,coreSourceTokens as tokens,coreSourceText as text,type CoreSourceNode,type CoreSourceRange} from './commerce-core-syntax.js';
import {reconstructCoreCommerceSources,type CoreCommerceDeclaration} from './commerce-core-reconstruction.js';
import {parseCoreExpression,parseCoreTypeTokens,type CoreExpression} from './commerce-core-expression.js';
import {checkCoreCommercePureSources} from './commerce-core-pure.js';
import {createCoreValueTypes,sameCoreValueType,CORE_BOOL,coreStringDomain,type CoreValueType} from './commerce-core-types.js';
import {createCoreContextCatalog,type CoreCapturedAsset,type CoreContextRequirement} from './commerce-core-context.js';
import {createCoreFlowExpressionChecker,type CoreFlowScope,type CoreFlowExpression} from './commerce-core-flow-expression.js';

export interface CoreWorkflowInvocation {
 readonly entry:string;readonly target:string;readonly role:'Operation'|'Query';
 readonly arguments:readonly {readonly parameter:string;readonly value:CoreFlowExpression}[];
 readonly binding:string|null;readonly result:CoreValueType;
 readonly authorization:'fresh-original-entry-decision-before-invocation';
}
export type CoreWorkflowAction=
 {readonly kind:'step'|'finish';readonly target:string}|
 {readonly kind:'suspend';readonly category:'control'|'persisted-state';readonly target:string}|
 {readonly kind:'resume'|'stop-this-worker'};
export interface CoreWorkflowDriver {
 readonly kind:'snapshot'|'claim'|'observation';readonly call:CoreWorkflowInvocation;
 readonly guard:CoreFlowExpression|null;readonly immutable_inputs:readonly CoreFlowExpression[];
 readonly on_missing:Readonly<{kind:'reject'|'fail';code:string}>|null;
 readonly inspection:CoreWorkflowInvocation|null;
 readonly requirements:readonly string[];
}
export interface CoreWorkflowBranch {
 readonly channel:'variant'|'success'|'call-failure'|'contention'|'unavailable'|'evidence-conflict'|'unknown';
 readonly variant:string|null;readonly binding:Readonly<{name:string;type:CoreValueType}>|null;
 readonly guard:CoreFlowExpression|null;readonly require:CoreFlowExpression|null;
 readonly observe:CoreFlowExpression|null;readonly action:CoreWorkflowAction;
 readonly retaining:'command'|'attempt'|null;
 readonly restriction:'do-not-release'|'do-not-assume-rollback'|null;
 readonly original_journal:'retain';readonly failed_require:'suspend-same-persisted-state';
}
export type CoreWorkflowStep=
 {readonly name:string;readonly kind:'remote';readonly call:CoreWorkflowInvocation;readonly branches:readonly CoreWorkflowBranch[];readonly unhandled_variants:readonly string[];readonly fallback:'suspend-same-persisted-state-retaining-original-journal'}|
 {readonly name:string;readonly kind:'local-observation';readonly observe:CoreFlowExpression;readonly commit_before:string;readonly next:string;readonly requirements:readonly string[]}|
 {readonly name:string;readonly kind:'review';readonly guard:CoreFlowExpression;readonly suspend:CoreWorkflowAction;readonly required_evidence:'original-current-persisted-state'};
export interface CoreWorkflowSource {
 readonly name:string;readonly owner:string;readonly parameters:readonly {readonly name:string;readonly type:CoreValueType}[];
 readonly contexts:readonly {readonly binding:string;readonly source_type:string;readonly abi:string}[];
 readonly correlation:CoreFlowExpression;readonly input_entry:string;readonly input_producer:string;
 readonly inbox_identity:readonly ({readonly kind:'original-entry-identity';readonly entry:string}|{readonly kind:'value';readonly value:CoreFlowExpression})[];
 readonly inbox_fingerprint:CoreFlowExpression;readonly durable_state:string;
 readonly ownership:readonly {readonly field:string;readonly type:CoreValueType}[];
 readonly drivers:readonly CoreWorkflowDriver[];
 readonly resume:readonly {readonly state:string;readonly guard:CoreFlowExpression|null;readonly action:CoreWorkflowAction}[];
 readonly steps:readonly CoreWorkflowStep[];
 readonly terminals:readonly {readonly name:string;readonly guard:CoreFlowExpression;readonly persisted_sources:readonly string[];readonly effects:'none';readonly on_false:'suspend-same-state'}[];
 readonly defaults:Readonly<{unhandled_resume:'suspend-same-persisted-state';max_transitions_per_resume:64;transition_limit:'suspend-retaining-original-journal';unhandled_result:'suspend-same-persisted-state';call_failure:'suspend-same-persisted-state';failed_success_guard:'suspend-same-persisted-state';failed_terminal_guard:'suspend-same-persisted-state'}>;
 readonly native_requirements:readonly string[];readonly qualification:'typed-workflow-source-only';
}
export interface CoreWorkflowAudit {
 readonly schema_version:'craft.commerce-core-workflow-audit/v1-candidate';readonly pure_subject_sha256:string;
 readonly workflows:readonly CoreWorkflowSource[];readonly diagnostics:readonly {readonly workflow:string;readonly diagnostics:CoreCommerceSourceError['diagnostics']}[];
 readonly complete:boolean;readonly authority_effect:'none';
}
const words=(n:CoreSourceNode)=>tokens(n).filter(t=>!t.layout).map(t=>t.token);
const range=(n:CoreSourceRange)=>({path:n.path,start:n.start,end:n.end});
const name=(value:string,n:CoreSourceRange):CoreExpression=>({...range(n),kind:'name',name:value});
const unique=(names:readonly string[],n:CoreSourceRange)=>{if(new Set(names).size!==names.length)fail('DuplicateSymbol',n,'duplicate Workflow binding or selector');};
const sourceMeaning=(value:unknown):unknown=>Array.isArray(value)?value.map(sourceMeaning):value&&typeof value==='object'?Object.fromEntries(Object.entries(value).filter(([key])=>!['path','start','end'].includes(key)).map(([key,value])=>[key,sourceMeaning(value)])):value;

export function auditCoreCommerceWorkflowSources(sources:readonly {readonly path:string;readonly text:string}[],assets:readonly CoreCapturedAsset[]=[]):CoreWorkflowAudit {
 const pure=checkCoreCommercePureSources(sources),model=reconstructCoreCommerceSources(sources),types=createCoreValueTypes(model),catalog=createCoreContextCatalog(types,assets);
 const workflows:CoreWorkflowSource[]=[],diagnostics:CoreWorkflowAudit['diagnostics'][number][]=[];
 for(const d of types.declarations.values())if(d.surface==='Workflow')try{
  const expression=createCoreFlowExpressionChecker(types,catalog),contexts=new Map<string,CoreContextRequirement>();
  for(const c of d.contexts){if(c.type.kind!=='named')fail('TypeMismatch',c.span,'Workflow context requires a private Interface');contexts.set(c.name,catalog.require(types.resolve(d.module,c.type.name,c.span)));}
  const parameters=d.parameters.map(p=>({name:p.name,type:types.type(d.module,p.type,p.span)}));
  let scope:CoreFlowScope={module:d.module,env:new Map(parameters.map(p=>[p.name,p.type])),contexts};
  const bind=(s:CoreFlowScope,binding:string,type:CoreValueType,n:CoreSourceRange):CoreFlowScope=>{if(s.env.has(binding)||s.contexts.has(binding))fail('DuplicateSymbol',n,'Workflow binding shadows original scope '+binding);return {...s,env:new Map([...s.env,[binding,type]])};};
  const checked=(n:CoreSourceNode,s=scope,expected?:CoreValueType)=>expression.check(parseCoreExpression(n),s,expected);
  const sourceName=(n:CoreExpression):string|null=>n.kind==='name'?n.name:n.kind==='field'&&sourceName(n.value)?sourceName(n.value)+'.'+n.field:null;
  const truth=(s:CoreFlowScope,n:CoreExpression,yes:boolean):CoreFlowScope=>{if(n.kind==='not')return truth(s,n.value,!yes);if(n.kind==='binary'&&(n.operator==='and'&&yes||n.operator==='or'&&!yes))return truth(truth(s,n.left,yes),n.right,yes);if(n.kind==='invoke'&&['present','absent'].includes(n.name)&&n.args.length===1){const path=sourceName(n.args[0]!.value);if(path){const narrowed=new Set(s.narrowed);if(n.name==='present'&&yes||n.name==='absent'&&!yes)narrowed.add(path);else narrowed.delete(path);return {...s,narrowed};}}return s;};
  const owned=(target:CoreCommerceDeclaration)=>model.ownership.find(o=>o.declaration===target.id)?.service;
  const ts=words(d.syntax),owner=ts[ts.indexOf('owner')+1]!,producer=ts[ts.indexOf('input-producer')+1]!;
  if(!model.services.some(s=>s.service===owner)||owned(d)!==owner)fail('InvalidContract',d.syntax,'Workflow owner must be its declared service owner');
  if(!model.services.some(s=>s.service===producer))fail('UnknownReference',d.syntax,'Workflow input producer is not a declared service');
  const ns=children(d.syntax,'qualified-name'),inputEntry=types.resolve(d.module,text(ns[0]!),ns[0]!),durable=types.resolve(d.module,text(ns[1]!),ns[1]!);
  if(inputEntry.surface!=='Entry'||types.resolve(inputEntry.module,inputEntry.invokes!,inputEntry.syntax).id!==d.id)fail('TypeMismatch',ns[0]!,'Workflow input-entry must invoke this exact Workflow');
  if(words(inputEntry.syntax)[words(inputEntry.syntax).indexOf('interaction')+1]!=='event')fail('TypeMismatch',inputEntry.syntax,'Workflow ingress requires an event entry');
  const inputProducer=inputEntry.access.find(c=>words(c)[0]==='producer');if(!inputProducer||words(inputProducer)[1]!==producer)fail('InvalidContract',inputEntry.syntax,'Workflow producer differs from its ingress entry');
  if(durable.surface!=='Entity'||owned(durable)!==owner)fail('InvalidContract',ns[1]!,'Workflow durable state requires its service-owned Entity');
  const stateField=durable.fields.find(f=>f.name==='state');if(!stateField)fail('MissingMapping',durable.syntax,'Workflow durable Entity requires state');
  const stateType=types.type(durable.module,stateField.type,stateField.span);if(stateType.kind!=='enum')fail('TypeMismatch',stateField.span,'Workflow persisted state must be a closed Enum');
  const stateEnum=types.declarations.get(stateType.name)!;if(stateEnum.variants.some(v=>v.fields.length))fail('TypeMismatch',stateEnum.syntax,'Workflow persisted states must be nullary Enum values');
  const asState=(raw:string,n:CoreSourceRange)=>{const dot=raw.lastIndexOf('.'),tag=raw.slice(dot+1);if(dot>=0&&types.resolve(d.module,raw.slice(0,dot),n).id!==stateEnum.id)fail('TypeMismatch',n,'Workflow state belongs to another Enum');if(!stateEnum.variants.some(v=>v.name===tag))fail('UnknownReference',n,'unknown Workflow persisted state '+raw);return tag;};
  const nodes=children(d.syntax,'workflow-step'),terminalNodes=children(d.syntax,'workflow-terminal'),stepNames=nodes.map(n=>text(child(n,'step-name'))),terminalNames=terminalNodes.map(n=>text(child(n,'step-name')));
  unique(stepNames,d.syntax);unique(terminalNames,d.syntax);if(stepNames.length>64||terminalNames.length>16)fail('ResourceLimit',d.syntax,'Workflow step/terminal bound');
  if(stepNames.some(n=>terminalNames.includes(n)))fail('DuplicateSymbol',d.syntax,'Workflow step and terminal names overlap');
  const target=(raw:string,n:CoreSourceRange)=>{if(!stepNames.includes(raw))fail('UnknownReference',n,'unknown Workflow step '+raw);return raw;};
  const action=(n:CoreSourceNode):CoreWorkflowAction=>{const ws=words(n);if(ws[0]==='finish'){if(!terminalNames.includes(ws[1]!))fail('UnknownReference',n,'unknown Workflow terminal');return {kind:'finish',target:ws[1]!};}if(ws[0]==='suspend'){const value=ws.slice(1).join('');return ['same-state','ownership-unresolved','needs-review'].includes(value)?{kind:'suspend',category:'control',target:value}:{kind:'suspend',category:'persisted-state',target:asState(value,n)};}if(ws[0]==='resume'||ws[0]==='stop-this-worker')return {kind:ws[0]};return {kind:'step',target:target(ws.join(''),n)};};
  const resolveCall=(q:CoreSourceNode,role:'Operation'|'Query'|null)=>{const entry=types.resolve(d.module,text(q),q);if(entry.surface!=='Entry')fail('TypeMismatch',q,'Workflow must invoke an explicit entry');const callable=types.resolve(entry.module,entry.invokes!,entry.syntax);if(!['Operation','Query'].includes(callable.surface)||role&&callable.surface!==role)fail('TypeMismatch',q,'Workflow driver/step has incompatible entry target role');if(words(entry.syntax)[words(entry.syntax).indexOf('interaction')+1]!=='request-response')fail('TypeMismatch',q,'Workflow calls require request-response entries');return {entry,callable};};
  const mapping=(q:CoreSourceNode,inputs:readonly CoreSourceNode[],s:CoreFlowScope,role:'Operation'|'Query'|null,binding:string|null,annotation:CoreValueType|null):CoreWorkflowInvocation=>{
   const {entry,callable}=resolveCall(q,role),names=inputs.map(i=>words(i)[1]!);unique(names,q);
   if(names.length!==callable.parameters.length||names.some(n=>!callable.parameters.some(p=>p.name===n)))fail('MissingMapping',q,'Workflow input mapping must equal the original entry signature');
   const result=types.type(callable.module,callable.result!,callable.syntax);if(annotation&&!sameCoreValueType(result,annotation))fail('TypeMismatch',q,'Workflow result annotation differs from actual entry result');
   return {entry:entry.id,target:callable.id,role:callable.surface as'Operation'|'Query',arguments:inputs.map(i=>{const parameter=callable.parameters.find(p=>p.name===words(i)[1])!;return {parameter:parameter.name,value:checked(child(i,'expression'),s,types.type(callable.module,parameter.type,parameter.span))};}),binding,result,authorization:'fresh-original-entry-decision-before-invocation'};
  };
  const invoke=(n:CoreSourceNode,s:CoreFlowScope,role:'Operation'|'Query'|null)=>{const resultNode=child(n,'driver-result'),binding=words(resultNode)[1]!,typeNode=child(resultNode,'type'),annotation=types.type(d.module,parseCoreTypeTokens(tokens(typeNode),typeNode),typeNode);return mapping(child(n,'qualified-name'),children(n,'driver-input'),s,role,binding,annotation);};
  const correlations=children(d.syntax,'expression'),correlation=checked(correlations[0]!);if(correlation.type.kind!=='UInt64'&&!coreStringDomain(correlation.type,types))fail('TypeMismatch',correlations[0]!,'Workflow correlation needs a bounded scalar identity');
  const fingerprint=checked(correlations[1]!);if(!coreStringDomain(fingerprint.type,types))fail('TypeMismatch',correlations[1]!,'Workflow inbox fingerprint requires bounded text');
  const lists=children(d.syntax,'name-list'),identityNodes=children(lists[0]!,'qualified-name');unique(identityNodes.map(text),lists[0]!);
  const inboxIdentity=identityNodes.map(n=>text(n)==='logicalEntryId'?{kind:'original-entry-identity' as const,entry:inputEntry.id}:{kind:'value' as const,value:expression.check(name(text(n),n),scope)});
  if(!inboxIdentity.some(v=>v.kind==='original-entry-identity'))fail('MissingMapping',lists[0]!,'Workflow inbox requires original logical entry identity');
  for(const v of inboxIdentity)if(v.kind==='value'&&v.value.type.kind!=='UInt64'&&!coreStringDomain(v.value.type,types))fail('TypeMismatch',lists[0]!,'Workflow inbox identity needs bounded scalar keys');
  const ownership=children(lists[1]!,'qualified-name').map(n=>{const field=text(n),f=durable.fields.find(f=>f.name===field);if(!f)fail('UnknownReference',n,'Workflow ownership field absent');return {field,type:types.type(durable.module,f.type,f.span)};});unique(ownership.map(f=>f.field),lists[1]!);
  if(ownership.length!==3||ownership[0]!.type.kind!=='optional'||!coreStringDomain(ownership[0]!.type.value,types)||ownership.slice(1).some(f=>f.type.kind!=='UInt64'))fail('TypeMismatch',lists[1]!,'Workflow ownership requires optional bounded owner identity, UInt64 epoch and UInt64 version');
  const drivers:CoreWorkflowDriver[]=[];
  const snapshotNode=child(d.syntax,'snapshot-driver'),snapshot=invoke(snapshotNode,scope,'Query');scope=bind(scope,snapshot.binding!,snapshot.result,snapshotNode);
  const snapshotGuard=checked(child(snapshotNode,'expression'),scope,CORE_BOOL),immutableNodes=children(child(snapshotNode,'name-list'),'qualified-name');unique(immutableNodes.map(text),snapshotNode);
  const immutableInputs=immutableNodes.map(n=>{if(!text(n).startsWith(snapshot.binding!+'.'))fail('InvalidContract',n,'immutable Workflow input must come from its actual snapshot result');return expression.check(name(text(n),n),scope);});
  const missing=words(child(snapshotNode,'failure-action'));drivers.push({kind:'snapshot',call:snapshot,guard:snapshotGuard,immutable_inputs:immutableInputs,on_missing:{kind:missing[0]as'reject'|'fail',code:missing[1]!},inspection:null,requirements:['reread-before-each-step-and-after-observation','original-current-row-versions-and-ownership','missing-stops-with-declared-failure','unavailable-suspends-without-dispatch']});
  scope=truth(scope,parseCoreExpression(child(snapshotNode,'expression')),true);
  const claimNode=child(d.syntax,'claim-driver'),claim=invoke(claimNode,scope,'Operation');if(claim.result.kind!=='record'||claim.result.name!==durable.id)fail('TypeMismatch',claimNode,'claim result must be the original durable-state Entity');
  const worker=contexts.get('worker');if(!worker)fail('MissingMapping',claimNode,'native claim protocol requires original worker context binding');const workerSource=types.declarations.get(worker.source_type)!;if(workerSource.interface_kind!=='trusted-context'||!children(workerSource.syntax,'interface-clause').some(c=>words(c).join(' ')==='custody private-registered-local-worker-owner'))fail('InvalidContract',claimNode,'claim worker binding must require the original private local worker owner');scope=bind(scope,claim.binding!,claim.result,claimNode);
  drivers.push({kind:'claim',call:claim,guard:null,immutable_inputs:[],on_missing:null,inspection:null,requirements:['original-private-worker-and-quiescent-predecessor-evidence','compare-and-set-current-version','bind-original-worker-to-committed-claim-before-dispatch','contention-stops-this-worker','unknown-suspends-ownership-unresolved-no-step']});
  const observationNode=child(d.syntax,'observation-driver'),observationTarget=resolveCall(child(observationNode,'qualified-name'),'Operation'),observationParameter=observationTarget.callable.parameters.find(p=>p.name==='observation');if(!observationParameter)fail('MissingMapping',observationNode,'observation Operation requires its declared observation parameter');
  const observationType=types.type(observationTarget.callable.module,observationParameter.type,observationParameter.span);if(observationType.kind!=='enum')fail('TypeMismatch',observationNode,'Workflow observation must be a closed Enum');
  const stepType=expression.registerRecord(d.id+'.CoreStepObservation',[{name:'observation',type:observationType}],observationNode),observationScope=bind(scope,'step',stepType,observationNode),observation=invoke(observationNode,observationScope,'Operation');
  if(sourceName(observation.arguments.find(a=>a.parameter==='observation')!.value.source)!=='step.observation')fail('InvalidContract',observationNode,'observation driver must preserve the original step observation');
  const observationFields=expression.fields(observation.result,observationNode);if(!observationFields.some(f=>f.name==='fresh'&&f.type.kind==='Bool'))fail('MissingMapping',observationNode,'observation commit result requires fresh Bool');
  const inspectionNode=child(observationNode,'invocation'),inspectionAst=parseCoreExpression(inspectionNode);if(inspectionAst.kind!=='invoke')fail('TypeMismatch',inspectionNode,'observation recovery must inspect an explicit entry');
  const inspectionEntry=types.resolve(d.module,inspectionAst.name,inspectionNode);if(inspectionEntry.surface!=='Entry')fail('TypeMismatch',inspectionNode,'observation inspection must target an entry');const inspectionTarget=types.resolve(inspectionEntry.module,inspectionEntry.invokes!,inspectionNode);if(inspectionTarget.surface!=='Query')fail('TypeMismatch',inspectionNode,'unknown observation recovery must be a read-only Query');
  if(words(inspectionEntry.syntax)[words(inspectionEntry.syntax).indexOf('interaction')+1]!=='request-response')fail('TypeMismatch',inspectionNode,'observation inspection requires a request-response entry');
  if(inspectionAst.args.length!==inspectionTarget.parameters.length||inspectionAst.args.some(a=>!a.name)||new Set(inspectionAst.args.map(a=>a.name)).size!==inspectionAst.args.length)fail('MissingMapping',inspectionNode,'observation inspection requires exact named arguments');
  const inspection:CoreWorkflowInvocation={entry:inspectionEntry.id,target:inspectionTarget.id,role:'Query',arguments:inspectionAst.args.map(a=>{const p=inspectionTarget.parameters.find(p=>p.name===a.name);if(!p)fail('UnknownReference',a.value,'unknown observation inspection argument');return {parameter:p.name,value:expression.check(a.value,observationScope,types.type(inspectionTarget.module,p.type,p.span))};}),binding:null,result:types.type(inspectionTarget.module,inspectionTarget.result!,inspectionNode),authorization:'fresh-original-entry-decision-before-invocation'};
  if(!inspection.arguments.some(a=>a.parameter==='observation'))fail('MissingMapping',inspectionNode,'unknown observation inspection must compare the original observation');
  for(const argument of inspection.arguments){const original=observation.arguments.find(a=>a.parameter===argument.parameter);if(!original||dataDigest(sourceMeaning(original.value.source))!==dataDigest(sourceMeaning(argument.value.source)))fail('InvalidContract',inspectionNode,'unknown observation inspection must retain exact original observation and identity arguments');}
  drivers.push({kind:'observation',call:observation,guard:null,immutable_inputs:[],on_missing:null,inspection,requirements:['original-observation-and-current-order-progress-versions','contention-reapply-original-observation-never-redispatch','unknown-retains-original-ticket-no-fresh-continuation-or-rollback-inference','then-target-only-after-fresh-acknowledged-commit-and-matching-reread-state','evidence-conflict-persists-original-step-command']});
  const resume:CoreWorkflowSource['resume'][number][]=[],unconditional=new Set<string>();
  for(const n of children(child(d.syntax,'resume-block'),'resume-case')){const state=asState(text(child(n,'qualified-name')),n);if(unconditional.has(state))fail('InvalidContract',n,'Workflow resume case unreachable after unconditional state case');const guardNode=children(n,'expression')[0],guard=guardNode?checked(guardNode,scope,CORE_BOOL):null;if(!guard)unconditional.add(state);resume.push({state,guard,action:action(child(n,'workflow-action'))});}
  // Persisted Entity projections are available only in persisted guards. They
  // demand actual current service-owned rows; these aliases perform no lookup.
  const persistedEntities=[...types.declarations.values()].filter(e=>e.surface==='Entity'&&owned(e)===owner),tree=new Map<string,unknown>();
  for(const e of persistedEntities){const parts=e.id.split('.');let cursor=tree;for(const part of parts.slice(0,-1)){let next=cursor.get(part) as Map<string,unknown>|undefined;if(!next){next=new Map();cursor.set(part,next);}if(!(next instanceof Map))fail('DuplicateSymbol',e.syntax,'persisted module/Entity namespace collision');cursor=next;}if(cursor.has(parts.at(-1)!))fail('DuplicateSymbol',e.syntax,'persisted Entity namespace collision');cursor.set(parts.at(-1)!,{kind:'record',name:e.id});}
  let serial=0;const namespace=(m:Map<string,unknown>):CoreValueType=>expression.registerRecord(d.id+'.CorePersistedNamespace'+(++serial),[...m].map(([field,value])=>({name:field,type:value instanceof Map?namespace(value):value as CoreValueType})),d.syntax);
  let persistedScope=scope;for(const [field,value]of tree)persistedScope=bind(persistedScope,field,value instanceof Map?namespace(value):value as CoreValueType,d.syntax);
  const steps:CoreWorkflowStep[]=[];
  const restrictions=(n:CoreSourceNode)=>{const ws=words(n);return ws.includes('do-not-release')?'do-not-release' as const:ws.includes('do-not-assume-rollback')?'do-not-assume-rollback' as const:null;};
  const branchAction=(n:CoreSourceNode,s:CoreFlowScope)=>{const ws=words(n),e=children(n,'expression')[0],observe=ws[0]==='observe'&&e?checked(e,s,observationType):null,require=ws[0]==='require'&&e?checked(e,s,CORE_BOOL):null;return {observe,require,action:action(child(n,'workflow-action')),retaining:ws.includes('retaining')?(ws[ws.indexOf('retaining')+2]==='attempt'?'attempt' as const:'command' as const):null,restriction:restrictions(n)};};
  for(const n of nodes){const stepName=text(child(n,'step-name')),remote=children(n,'remote-step')[0],local=children(n,'local-step')[0],review=children(n,'review-step')[0];
   if(local){const targets=children(local,'step-name').map(text);if(targets.length!==2||target(targets[0]!,local)!==target(targets[1]!,local))fail('InvalidContract',local,'local observation commit-before and next must identify the same step');steps.push({name:stepName,kind:'local-observation',observe:checked(child(local,'expression'),scope,observationType),commit_before:targets[0]!,next:targets[1]!,requirements:['unknown-inspects-original-observation-before-provider-dispatch','fresh-acknowledged-local-commit-or-original-never-dispatched-journal-evidence','snapshot-reread-and-state-match-before-next']});continue;}
   if(review){const suspendNode=child(review,'step-name'),raw=text(suspendNode);if(!['same-state','ownership-unresolved','needs-review'].includes(raw))asState(raw,suspendNode);steps.push({name:stepName,kind:'review',guard:checked(child(review,'expression'),persistedScope,CORE_BOOL),suspend:{kind:'suspend',category:['same-state','ownership-unresolved','needs-review'].includes(raw)?'control':'persisted-state',target:raw},required_evidence:'original-current-persisted-state'});continue;}
   if(!remote)fail('UnsupportedCapability',n,'unknown Workflow step form');
   const call=invoke(remote,scope,null),inner=bind(scope,call.binding!,call.result,remote),branches:CoreWorkflowBranch[]=[],closed=new Set<string>(),channels=new Set<string>();
   const resultEnum=call.result.kind==='enum'?types.declarations.get(call.result.name)!:null;
   const append=(channel:CoreWorkflowBranch['channel'],body:ReturnType<typeof branchAction>,variant:string|null=null,binding:CoreWorkflowBranch['binding']=null,guard:CoreFlowExpression|null=null)=>branches.push({channel,variant,binding,guard,...body,original_journal:'retain',failed_require:'suspend-same-persisted-state'});
   for(const b of children(remote,'step-branch')){const ws=words(b),patterns=children(b,'pattern-list')[0],guardNode=children(b,'expression')[0];
    if(patterns){if(!resultEnum)fail('TypeMismatch',patterns,'Workflow variant branch requires Enum result');const group=new Set<string>();
     for(const p of children(patterns,'pattern')){const ps=words(p),raw=text(child(p,'qualified-name')),dot=raw.lastIndexOf('.'),tag=raw.slice(dot+1);if(dot>=0&&types.resolve(d.module,raw.slice(0,dot),p).id!==resultEnum.id)fail('TypeMismatch',p,'Workflow pattern belongs to another Enum');const variant=resultEnum.variants.find(v=>v.name===tag);if(!variant)fail('UnknownReference',p,'Workflow pattern not in actual step result');if(group.has(tag)||closed.has(tag))fail('InvalidContract',p,'duplicate or unreachable Workflow result pattern');group.add(tag);let branchScope=inner,binding:CoreWorkflowBranch['binding']=null;
      if(ps.includes('(')){if(!variant.fields.length)fail('TypeMismatch',p,'nullary Workflow variant cannot bind payload');const type=variant.fields.length===1?types.type(resultEnum.module,variant.fields[0]!.type,variant.fields[0]!.span):{kind:'variant' as const,name:resultEnum.id,variant:tag};binding={name:ps.at(-2)!,type};branchScope=bind(inner,binding.name,type,p);}
      const guard=guardNode?checked(guardNode,branchScope,CORE_BOOL):null;if(!guard)closed.add(tag);append('variant',branchAction(child(b,'branch-action'),guardNode?truth(branchScope,parseCoreExpression(guardNode),true):branchScope),tag,binding,guard);
     }continue;
    }
    const channel=({'on-success':'success','on-call-failure':'call-failure','on-contention':'contention','on-unavailable':'unavailable','on-evidence-conflict':'evidence-conflict','on-unknown':'unknown'}as const)[ws[0]as'on-success'];if(!channel)fail('UnsupportedCapability',b,'unregistered Workflow result channel');if(channels.has(channel))fail('DuplicateSymbol',b,'duplicate Workflow result channel');channels.add(channel);
    if(channel==='success'){append(channel,{observe:null,require:checked(child(b,'expression'),inner,CORE_BOOL),action:action(child(b,'workflow-action')),retaining:null,restriction:null});}
    else if(channel==='contention')append(channel,{observe:null,require:null,action:{kind:'resume'},retaining:null,restriction:null});
    else if(channel==='unavailable')append(channel,{observe:null,require:null,action:action(child(b,'workflow-action')),retaining:null,restriction:null});
    else if(channel==='unknown')append(channel,{observe:null,require:null,action:{kind:'step',target:target(text(child(b,'step-name')),b)},retaining:null,restriction:restrictions(b)});
    else append(channel,branchAction(child(b,'branch-action'),scope));
   }
   steps.push({name:stepName,kind:'remote',call,branches,unhandled_variants:resultEnum?.variants.filter(v=>!closed.has(v.name)).map(v=>v.name)??[],fallback:'suspend-same-persisted-state-retaining-original-journal'});
  }
  for(const step of steps)if(step.kind==='remote')for(const b of step.branches)if(b.channel==='unknown'&&b.action.kind==='step'){const target=b.action.target,next=steps.find(s=>s.name===target);if(next?.kind!=='remote'||next.call.role!=='Query')fail('InvalidContract',d.syntax,'unknown commit continuation must inspect through a read-only entry');}
  const terminals=terminalNodes.map(n=>{const guard=checked(child(n,'expression'),persistedScope,CORE_BOOL),used=new Set<string>(),stack:unknown[]=[guard.source];while(stack.length){const value=stack.pop();if(value&&typeof value==='object'){if('kind'in value&&value.kind==='name'&&'name'in value&&typeof value.name==='string')for(const entity of persistedEntities)if(value.name.startsWith(entity.id+'.'))used.add(entity.id);stack.push(...Object.values(value));}}return {name:text(child(n,'step-name')),guard,persisted_sources:[...used].sort(),effects:'none' as const,on_false:'suspend-same-state' as const};});
  workflows.push(coreFreeze({name:d.id,owner,parameters,contexts:[...contexts].map(([binding,c])=>({binding,source_type:c.source_type,abi:c.abi})),correlation,input_entry:inputEntry.id,input_producer:producer,inbox_identity:inboxIdentity,inbox_fingerprint:fingerprint,durable_state:durable.id,ownership,drivers,resume,steps,terminals,defaults:{unhandled_resume:'suspend-same-persisted-state',max_transitions_per_resume:64,transition_limit:'suspend-retaining-original-journal',unhandled_result:'suspend-same-persisted-state',call_failure:'suspend-same-persisted-state',failed_success_guard:'suspend-same-persisted-state',failed_terminal_guard:'suspend-same-persisted-state'},native_requirements:['original-ingress-producer-occurrence-inbox-and-work-schedule-commit-before-ack','original-private-worker-lifecycle-and-committed-claim','fresh-entry-decisions-independent-of-worker-lifetime','original-current-snapshot-versions-and-state-reread','original-step-journal-and-immutable-inputs','no-lease-steal-without-native-quiescent-predecessor-evidence','original-observation-commit-or-unresolved-ticket-never-fabricated-continuation','no-provider-dispatch-from-absence-timeout-or-unknown-key','terminal-guard-on-current-owned-rows-with-no-domain-effects'],qualification:'typed-workflow-source-only'}));
 }catch(error){if(!(error instanceof CoreCommerceSourceError))throw error;diagnostics.push({workflow:d.id,diagnostics:error.diagnostics});}
 workflows.sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0);
 return coreFreeze({schema_version:'craft.commerce-core-workflow-audit/v1-candidate',pure_subject_sha256:pure.pure_subject_sha256,workflows,diagnostics,complete:diagnostics.length===0,authority_effect:'none'});
}
export function checkCoreCommerceWorkflowSources(sources:readonly {readonly path:string;readonly text:string}[],assets:readonly CoreCapturedAsset[]=[]):CoreWorkflowAudit {
 const result=auditCoreCommerceWorkflowSources(sources,assets);if(!result.complete){const first=result.diagnostics[0]!.diagnostics[0]!;fail(first.code,first,first.message);}return result;
}
export function checkCoreCommerceWorkflowProposal(sources:readonly {readonly path:string;readonly text:string}[],assets:readonly CoreCapturedAsset[],proposal:unknown):CoreWorkflowAudit {
 const result=checkCoreCommerceWorkflowSources(sources,assets);let hash:string;try{hash=dataDigest(proposal);}catch{return fail('InvalidContract',{path:sources[0]?.path??'application.alch',start:0,end:0},'inert bounded Workflow proposal required');}if(hash!==dataDigest(result))fail('InvalidContract',{path:sources[0]?.path??'application.alch',start:0,end:0},'Workflow proposal differs from independent source reconstruction');return result;
}
