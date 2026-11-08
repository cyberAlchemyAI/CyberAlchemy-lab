import {closeSync,constants,fstatSync,lstatSync,openSync,readSync,type BigIntStats} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJson,dataDigest,ProfileRejected,reject,sha256} from './contracts.js';
import {validateBusinessAuthoringContract} from './business-authoring-contracts.js';
import {assertBusinessAuthoringSnapshotCurrent,withBusinessAuthoringSnapshotValidation,type BusinessAuthoringSnapshot} from './loader-v3.js';
import {assertBusinessRecipeSelectionCurrent,businessAuthoringRecipeSnapshot,type BusinessRecipeSelection} from './business-authoring-recipes.js';
import {assertBusinessAuthoringApplicationCurrent,type BusinessAuthoringApplication} from './business-authoring-application.js';
import {createCompiledSemanticGraph} from '../compilation/certificate.js';
import type {BusinessDerivationOrigin,BusinessLoweringLedger,BusinessObligation,BusinessSpecData} from './business-authoring-protocol.js';
import type {ProfilePackageV3} from './contracts-v3.js';
import {BUSINESS_RECIPE_GUARANTEES} from './business-authoring-normalization-protocol.js';

/** Independent source/profile denominator. These registered views preserve links;
 * native observation, proof and admission have separate owners. Open questions:
 * docs/BUSINESS-AUTHORING-CONTRACTS.md and construction task B08.2. */
export interface BusinessAuthoringCoverageTarget {readonly artifact:string;readonly pointer:string}
export interface BusinessAuthoringCoverageObligation {
 readonly id:string;readonly family:'authored'|'derived';readonly class:string;readonly model_id:string;
 readonly selector:string;readonly scope:string;readonly clause:string;readonly source_pointer:string;
 readonly origins:readonly BusinessDerivationOrigin[];readonly obligation_kind?:BusinessObligation['kind'];
 readonly subject:string;readonly detail:string;
}
export interface BusinessAuthoringObligationData {
 readonly schema_version:'craft.business-authoring-obligations/v1-candidate';readonly model_id:string;
 readonly source_sha256:string;readonly business_sha256:string;readonly lock_sha256:string;
 readonly authored:readonly BusinessAuthoringCoverageObligation[];readonly derived:readonly BusinessAuthoringCoverageObligation[];
 readonly authority_effect:'none';
}
export interface BusinessAuthoringObligationInventory {
 readonly kind:'business-authoring-obligation-inventory';readonly snapshot:BusinessAuthoringSnapshot;readonly spec:BusinessSpecData;
 readonly model_id:string;readonly data:BusinessAuthoringObligationData;readonly inventory_sha256:string;
}
export interface PreparedBusinessAuthoringCoverage {
 readonly kind:'prepared-business-authoring-coverage';readonly selection:BusinessRecipeSelection;
 readonly inventory:BusinessAuthoringObligationInventory;readonly model_id:string;
}
export interface BusinessAuthoringCoverageLink {
 readonly obligation_id:string;readonly origins:readonly BusinessDerivationOrigin[];
 readonly targets:readonly BusinessAuthoringCoverageTarget[];
}
export interface BusinessAuthoringCoverageItem extends BusinessAuthoringCoverageLink {
 readonly family:'authored'|'derived';readonly class:string;readonly state:'retained'|'unsupported-required'|'claim-residue';
 readonly evidence_states:readonly ('linked'|'generated')[];
}
export interface BusinessAuthoringCoverageReport {
 readonly kind:'business-authoring-coverage-report';readonly prepared:PreparedBusinessAuthoringCoverage;readonly application:BusinessAuthoringApplication;
 readonly model_id:string;readonly items:readonly BusinessAuthoringCoverageItem[];readonly missing:readonly string[];readonly complete:boolean;
 readonly ledger:BusinessLoweringLedger;readonly artifacts:Readonly<Record<string,unknown>>;readonly artifact_text:Readonly<Record<string,string>>;
 readonly coverage_sha256:string;readonly authority_effect:'none';
}
type InventoryOwner={snapshot:BusinessAuthoringSnapshot;fingerprint:string};
const inventories=new WeakMap<object,InventoryOwner>(),preparations=new WeakMap<object,{selection:BusinessRecipeSelection;inventory:BusinessAuthoringObligationInventory}>(),reports=new WeakMap<object,{prepared:PreparedBusinessAuthoringCoverage;application:BusinessAuthoringApplication;fingerprint:string}>();
const compare=(a:string,b:string)=>a<b?-1:a>b?1:0;
const esc=(key:string)=>key.replaceAll('~','~0').replaceAll('/','~1');
const symbol=(value:string)=>value.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replace(/[^A-Za-z0-9]+/g,'-').toLowerCase();
const same=(a:unknown,b:unknown)=>dataDigest(a)===dataDigest(b);
function fail(code:string,pointer:string,message:string):never{return reject('BUSINESS_COVERAGE_'+code,pointer,message);}
function closed(value:unknown,keys:readonly string[],at:string):asserts value is Record<string,unknown>{if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).length!==keys.length||keys.some(key=>!Object.hasOwn(value,key)))fail('EVIDENCE',at,'closed required fields only');}
function portable(value:string):string {if(!value||value.length>4096||path.posix.isAbsolute(value)||value.includes('\\')||value.split('/').some(part=>!part||part==='.'||part==='..')||/[\x00-\x1f\x7f]/.test(value))fail('PATH',value,'portable artifact/source key required');return value;}
/** Strict own-property JSON pointer; inherited keys and invalid escapes never resolve. */
export function resolveBusinessAuthoringCoveragePointer(value:unknown,pointer:string):unknown {
 if(pointer==='')return value;if(!pointer.startsWith('/')||pointer.length>4096)fail('POINTER',pointer,'bounded JSON pointer required');let at=value;
 for(const token of pointer.slice(1).split('/')){
  if(/~(?:[^01]|$)/.test(token))fail('POINTER',pointer,'invalid JSON pointer escape');const key=token.replaceAll('~1','/').replaceAll('~0','~');
  if(!at||typeof at!=='object'||!Object.hasOwn(at,key)||Array.isArray(at)&&(!/^(?:0|[1-9][0-9]*)$/.test(key)||Number(key)>=at.length))fail('POINTER',pointer,'target must resolve to an actual own field');at=(at as Record<string,unknown>)[key];
 }
 return at;
}
function regularBytes(file:string,budget:number):Buffer {
 const before=lstatSync(file,{bigint:true});if(!before.isFile()||before.isSymbolicLink()||before.size>BigInt(budget))fail('FILE',file,'bounded regular file required');
 const physical=(s:BigIntStats)=>s.isFile()&&s.dev===before.dev&&s.ino===before.ino&&s.mode===before.mode&&s.size===before.size&&s.mtimeNs===before.mtimeNs&&s.ctimeNs===before.ctimeNs;
 const fd=openSync(file,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK),buffers:Buffer[]=[];let bytes=0;
 try{if(!physical(fstatSync(fd,{bigint:true})))fail('FILE',file,'file changed while opening');for(;;){const buffer=Buffer.alloc(65536),count=readSync(fd,buffer,0,buffer.length,null);if(!count)break;bytes+=count;if(bytes>budget)fail('FILE',file,'file byte budget exceeded');buffers.push(buffer.subarray(0,count));}if(!physical(fstatSync(fd,{bigint:true})))fail('FILE',file,'file changed during capture');}finally{closeSync(fd);}
 if(BigInt(bytes)!==before.size||!physical(lstatSync(file,{bigint:true})))fail('FILE',file,'file path changed');return Buffer.concat(buffers);
}
const ownPath=fileURLToPath(import.meta.url);
function moduleIdentity():string {
 try{const ancestry=()=>{let cursor=path.parse(ownPath).root;const result:string[]=[];for(const part of ['',...ownPath.slice(cursor.length).split(path.sep).filter(Boolean)]){if(part)cursor=path.join(cursor,part);const s=lstatSync(cursor,{bigint:true});if(s.isSymbolicLink())fail('MODULE',ownPath,'implementation symlinks forbidden');result.push(`${s.dev}:${s.ino}:${s.mode}`);}return result;};
  const before=ancestry(),stat=lstatSync(ownPath,{bigint:true}),bytes=regularBytes(ownPath,16777216);if(!same(before,ancestry()))fail('MODULE',ownPath,'implementation ancestor changed');return dataDigest({ancestors:before,sha256:sha256(bytes),mtime:String(stat.mtimeNs),ctime:String(stat.ctimeNs)});
 }catch(error){if(error instanceof ProfileRejected)throw error;return fail('MODULE','/','owning implementation unavailable');}
}
const executingModule=moduleIdentity();
function assertModule():void{if(moduleIdentity()!==executingModule)fail('MODULE','/','reload current coverage implementation');}
const derivationContract=Object.freeze({schema_version:'craft.business-authoring-coverage-derivation/v1-candidate',denominator:'original-noncomment-source-lines-and-source-profile-obligations',targets:'registered-business-authoring-application-only',claims:'unproved-residue',authority_effect:'none'});
const adapter:BusinessDerivationOrigin={kind:'semantic-adapter',source:'craft.business-authoring-coverage/1-candidate',selector:'/derivation-contract',sha256:dataDigest(derivationContract)};
function rawClass(scope:string,text:string,depth:number):string {
 if(scope==='model')return 'identity';if(depth===0)return scope==='capability'?'exposure':'declaration';
 if(scope==='entity'&&/^[A-Za-z_][A-Za-z0-9_-]* (UInt64|String|Bool) meaning /.test(text))return 'field';
 if(scope==='formal-claim'&&/^(sort|predicate|constant) /.test(text))return 'formal-symbol';
 if(scope==='operation')return 'behavior';if(scope==='capability')return text.startsWith('audience ')?'audience':'exposure';
 if(depth===2||/^(example|counterexample) /.test(text))return 'scenario';
 if(/^(requirement|input|claim|boolean-field|bind|identity) /.test(text))return 'reference';return 'clause';
}
function sourceRows(snapshot:BusinessAuthoringSnapshot,modelId:string,spec:BusinessSpecData):BusinessAuthoringCoverageObligation[] {
 const model=snapshot.project.models.find(value=>value.id===modelId),file=model?snapshot.sources[model.source]:undefined;if(!model||!file?.text)fail('SOURCE',modelId,'original selected business source required');
 portable(model.source);if(file.bytes>1048576||sha256(file.text)!==file.sha256||Buffer.byteLength(file.text)!==file.bytes)fail('SOURCE',modelId,'exact bounded captured source required');
 if(spec.identity.namespace!==modelId||spec.identity.stable_id!==modelId)fail('SOURCE',modelId,'exact original model identity required');
 const sourceLines=file.text.split('\n'),facts=sourceLines.flatMap((line,index)=>{const raw=index<sourceLines.length-1?line.replace(/\r$/,''):line;return raw.trim()&&!raw.trimStart().startsWith('#')?[{raw,line:index+1,column:raw.length-raw.trimStart().length+1}]:[];});
 if(facts.length!==spec.source_spans.length||facts.length!==spec.obligations.length)fail('DENOMINATOR',modelId,'original noncomment source denominator cannot omit or invent facts');
 let scope='model',subject=modelId;const ids=new Set<string>();
 return facts.map((fact,index)=>{
  const span=spec.source_spans[index]!,obligation=spec.obligations[index]!,text=fact.raw.trimStart(),depth=(fact.column-1)/2;
  if(span.source!==model.source||span.source_sha256!==file.sha256||span.line!==fact.line||span.column!==fact.column||span.text!==fact.raw||!span.selector.endsWith('/line:'+fact.line)||ids.has(span.selector)||obligation.selector!==span.selector||obligation.span_selector!==span.selector)fail('DENOMINATOR',modelId,'every original source fact needs its own exact span and obligation');ids.add(span.selector);
  if(depth===0){const header=/^(requirement|entity|definition|formal-claim|rule|operation|capability) ([A-Za-z_][A-Za-z0-9_-]*)(?: version [^ ]+)?:$/.exec(text);scope=header?.[1]??'model';subject=header?.[2]??modelId;}
  const clause=depth===0?'declaration':text.split(' ')[0]!,kind=rawClass(scope,text,depth);
  return {id:`authored:${modelId}:line:${fact.line}`,family:'authored',class:kind,model_id:modelId,selector:span.selector,scope,clause,source_pointer:'/spec/source_spans/'+index,origins:[{kind:'business',source:span.source,selector:span.selector,sha256:span.source_sha256}],obligation_kind:obligation.kind,subject,detail:span.text};
 });
}
function derivedRows(snapshot:BusinessAuthoringSnapshot,modelId:string,spec:BusinessSpecData,authored:readonly BusinessAuthoringCoverageObligation[]):BusinessAuthoringCoverageObligation[] {
 const runtime=snapshot.packages.filter(value=>value.data.schema_version==='craft.profile-package/v3-candidate');if(runtime.length!==1)fail('PROFILE',modelId,'one original authoring runtime required');const pkg=runtime[0]!,profile=pkg.data as ProfilePackageV3;
 const profileOrigin=(selector:string):BusinessDerivationOrigin=>({kind:'profile',source:'profile:'+pkg.id,selector,sha256:pkg.manifest_sha256});
 const rows:BusinessAuthoringCoverageObligation[]=[];
 const add=(kind:string,subject:string,scope:string,pointer:string,detail:string,clause='declaration',technical?:string):void=>{
  const source=authored.find(row=>row.scope===scope&&row.subject===subject&&(clause==='declaration'?row.clause==='declaration':row.clause===clause))??authored.find(row=>row.scope===scope&&row.subject===subject);
  rows.push({id:`derived:${modelId}:${kind}:${subject}:${pointer}`,family:'derived',class:kind,model_id:modelId,selector:technical??source?.selector??'/authoring/recipe_ref',scope,clause,source_pointer:pointer,origins:[...(source?.origins??[]),...(technical?[profileOrigin(technical)]:[]),adapter],subject,detail});
 };
 for(const [index,entity] of spec.entities.entries()){
  add('semantic-declaration',entity.id,'entity','/spec/entities/'+index,'Entity metadata and checked typed identity');
  for(const [fieldIndex,field] of entity.fields.entries())add('semantic-field',entity.id,'entity','/spec/entities/'+index+'/fields/'+fieldIndex,'Preserve '+field.name+' type and exact authored meaning',field.name);
 }
 for(const [index,definition] of spec.definitions.entries())add('formal-definition',definition.id,'definition','/spec/definitions/'+index,'The same explicit Bool primitive supplies formal metadata and runtime interpretation','boolean-field');
 for(const [index,claim] of spec.claims.entries()){
  add('formal-claim',claim.id,'formal-claim','/spec/claims/'+index,'Exact explicit formal signature, proposition and ceiling remain unproved');
  add('legacy-meaning',claim.id,'formal-claim','/spec/claims/'+index,'Exact prospective legacy meaning and explicit recorded decision subject');
 }
 for(const [index,rule] of spec.rules.entries()){
  add('semantic-declaration',rule.id,'rule','/spec/rules/'+index,'Rule metadata and checked typed condition');
  add('rule-interpretation',rule.id,'rule','/spec/rules/'+index,'Explicit sort, constant and predicate associations','claim');
 }
 for(const [index,operation] of spec.operations.entries()){
  add('semantic-declaration',operation.id,'operation','/spec/operations/'+index,'Operation metadata and checked typed action');
  for(const [kind,clause] of [['guard','requires'],['result','returns'],['failure','on-rejection'],['effects','effects']] as const)add(kind,operation.id,'operation','/spec/operations/'+index,'Exact authored '+clause+' correspondence',clause);
 }
 for(const [index,capability] of spec.capabilities.entries()){
  const operation=spec.operations.find(value=>value.id===capability.operation_ref),entity=spec.entities.find(value=>value.id===operation?.input.type_ref);if(!operation||!entity)fail('REFERENCE',capability.id,'explicit input/exposure reference required');
  const source='/spec/capabilities/'+index;
  add('public-intent',capability.id,'capability',source,'Public access derives only from explicit authored audience','audience');
  add('request-mapping',capability.id,'capability',source,'Actual reserved identity Mapping and request binding','invokes','/authoring/wire/body');
  for(const [fieldIndex,field] of entity.fields.entries())add('request-field',capability.id,'capability',source+'/fields/'+fieldIndex,'Copy exact unchanged field '+field.name,'invokes','/authoring/wire/body');
  for(const [kind,selector] of [['request-contract','/authoring/wire/schema_version'],['request-method','/authoring/wire/method'],['route','/authoring/wire/route_prefix'],['request-body','/authoring/wire/body'],['request-limits','/authoring/wire/request_bytes'],['timeout','/authoring/wire/timeout_ms'],['transport','/application_runtime/transport']] as const)add(kind,capability.id,'capability',source,'Explicit selected '+kind+' convention','public-name',selector);
 }
 add('owner-decision',modelId,'model','/identity','Exact aggregate, legacy and complete selected-definition decision subjects');
 for(const selector of ['/authoring/contract','/authoring/input_schema','/authoring/recipe_ref','/authoring/logic_profile','/authoring/target','/authoring/effects'])add('recipe-profile',selector,'model','/identity','Captured finite core-owned recipe/profile selection','declaration',selector);
 for(const guarantee of BUSINESS_RECIPE_GUARANTEES)add('runtime-guarantee',guarantee,'model','/identity','Required finite recipe guarantee remains explicit','declaration','/authoring/recipe_ref');
 for(const [index,rule] of profile.rules.entries())if(rule.op==='emit')add('profile-role',rule.id,'profile','/rules/'+index,'Every selected emitted role has its real generated component and file owner','declaration','/rules/'+index);
 return rows;
}
export function inventoryBusinessAuthoringObligations(snapshot:BusinessAuthoringSnapshot,modelId:string,input:BusinessSpecData):BusinessAuthoringObligationInventory {
 assertBusinessAuthoringSnapshotCurrent(snapshot);assertModule();const spec=validateBusinessAuthoringContract('spec',input) as BusinessSpecData;
 const authored=sourceRows(snapshot,modelId,spec),derived=derivedRows(snapshot,modelId,spec,authored);if(authored.length+derived.length>10000)fail('BUDGET',modelId,'closed ledger denominator exceeds 10000 entries');
 const {source_spans:_spans,obligations:_obligations,...semantic}=spec;
 const byId=<T extends {id:string}>(rows:readonly T[])=>[...rows].sort((a,b)=>compare(a.id,b.id)),byName=<T extends {name:string}>(rows:readonly T[])=>[...rows].sort((a,b)=>compare(a.name,b.name));
 const business=dataDigest({...semantic,requirements:byId(spec.requirements),entities:byId(spec.entities).map(entity=>({...entity,fields:byName(entity.fields)})),definitions:byId(spec.definitions),claims:byId(spec.claims).map(claim=>({...claim,sorts:byName(claim.sorts),predicates:byName(claim.predicates),constants:byName(claim.constants)})),rules:byId(spec.rules),operations:byId(spec.operations),capabilities:byId(spec.capabilities)});
 const data=captureJson({schema_version:'craft.business-authoring-obligations/v1-candidate',model_id:modelId,source_sha256:snapshot.sources[snapshot.project.models.find(model=>model.id===modelId)!.source]!.sha256,business_sha256:business,lock_sha256:snapshot.lock.lock_sha256,authored,derived,authority_effect:'none'}) as unknown as BusinessAuthoringObligationData;
 const result=Object.freeze({kind:'business-authoring-obligation-inventory' as const,snapshot,spec,model_id:modelId,data,inventory_sha256:dataDigest(data)});inventories.set(result,{snapshot,fingerprint:dataDigest({spec,data,inventory_sha256:result.inventory_sha256})});assertBusinessAuthoringObligationInventoryCurrent(result);return result;
}
export function assertBusinessAuthoringObligationInventoryCurrent(value:BusinessAuthoringObligationInventory):void {
 const state=value&&typeof value==='object'?inventories.get(value):undefined;if(!state)fail('HANDLE','/','original registered source inventory required');assertModule();assertBusinessAuthoringSnapshotCurrent(state.snapshot);
 if(value.snapshot!==state.snapshot||dataDigest({spec:value.spec,data:value.data,inventory_sha256:value.inventory_sha256})!==state.fingerprint)fail('STALE','/','original source inventory changed');
}
export function prepareBusinessAuthoringCoverage(selection:BusinessRecipeSelection,modelId:string,inventory?:BusinessAuthoringObligationInventory):PreparedBusinessAuthoringCoverage {
 assertBusinessRecipeSelectionCurrent(selection);const snapshot=businessAuthoringRecipeSnapshot(selection),model=selection.models.find(value=>value.model_id===modelId);if(!model)fail('MODEL',modelId,'original selected model required');
 const original=inventory??inventoryBusinessAuthoringObligations(snapshot,modelId,model.spec);assertBusinessAuthoringObligationInventoryCurrent(original);
 if(original.snapshot!==snapshot||original.model_id!==modelId||!same(original.spec,model.spec))fail('CORRESPONDENCE',modelId,'original independently captured source inventory and selection must match');
 const result=Object.freeze({kind:'prepared-business-authoring-coverage' as const,selection,inventory:original,model_id:modelId});preparations.set(result,{selection,inventory:original});return result;
}
export function assertPreparedBusinessAuthoringCoverageCurrent(value:PreparedBusinessAuthoringCoverage):void {const state=value&&typeof value==='object'?preparations.get(value):undefined;if(!state)fail('HANDLE','/','original registered coverage preparation required');assertBusinessRecipeSelectionCurrent(state.selection);assertBusinessAuthoringObligationInventoryCurrent(state.inventory);if(value.selection!==state.selection||value.inventory!==state.inventory||value.model_id!==state.inventory.model_id)fail('STALE','/','coverage preparation changed');}

interface ArtifactSet {readonly values:Readonly<Record<string,unknown>>;readonly text:Readonly<Record<string,string>>}
function artifactSet(application:BusinessAuthoringApplication):ArtifactSet {
 assertBusinessAuthoringApplicationCurrent(application);const values:Record<string,unknown>=Object.create(null),text:Record<string,string>=Object.create(null);
 const put=(file:string,data:unknown,bytes?:string):void=>{portable(file);if(Object.hasOwn(values,file)||Object.hasOwn(application.files,file))fail('ARTIFACT',file,'one exact generated artifact owner required');values[file]=captureJson(data);text[file]=bytes??JSON.stringify(data,null,2)+'\n';};
 for(const model of application.models){
  const id=model.model_id,selected=application.selection.models.find(value=>value.model_id===id)!;
  const captured=model.input.applications.find(value=>value.model.id===id);if(!captured)fail('ARTIFACT',id,'actual captured generated application model required');
  put(captured.model.source,captured.source,captured.source);put(captured.model.semantics,captured.semantics);
  put(`lineage/models/${id}.json`,selected);put(`lineage/reviews/${id}.json`,model.input.accepted.review.review);put(`lineage/semantics/${id}.json`,model.input.compatibility.semantics);
  put(`lineage/domains/${id}.json`,createCompiledSemanticGraph(model.graph));put(`lineage/request-bindings/${id}.json`,model.binding);put(`lineage/request-plans/${id}.json`,model.plan);
  put(`lineage/actions/${id}.json`,{schema_version:'craft.business-authoring-action-view/v1-candidate',source_plan_sha256:model.application_plan.plan_sha256,selection:model.application_plan.selection,authority_effect:'none'});
  const resourceIndex:Record<string,{artifact:string;sha256:string;bytes:number}>=Object.create(null);
  for(const key of Object.keys(model.formal.sources).sort(compare)){
   portable(key);const body=model.formal.sources[key]!,artifact=`lineage/formal/${id}/${key}`;let data:unknown=body;
   if(key.endsWith('.json'))try{data=JSON.parse(body);}catch{fail('FORMAL_RESOURCE',key,'original formed JSON resource must parse');}
   put(artifact,data,body);resourceIndex[key]={artifact,sha256:sha256(body),bytes:Buffer.byteLength(body)};
  }
  put(`lineage/formal-index/${id}.json`,{schema_version:'craft.business-authoring-formal-resource-index/v1-candidate',model_id:id,scope:`lineage/formal/${id}`,sources:resourceIndex,conditions:model.formal.conditions,join:model.formal.join,claim_state:'unproved',authority_effect:'none'});
  const capture=model.input.accepted.capture,bytes=regularBytes(capture.file.path,1048576);if(bytes.length!==capture.file.bytes||sha256(bytes)!==capture.file.sha256)fail('DECISION',id,'exact original captured decision bytes required');
  put(`lineage/decisions/${id}.json`,capture.decision,bytes.toString('utf8'));
 }
 for(const pkg of application.authoring_snapshot.packages)put(`lineage/profiles/${pkg.id}.json`,pkg.data);
 put('lineage/requests.json',{models:application.requests.models,project_intents:application.requests.project_intents,request_source:application.requests.request_source,derivation_sha256:application.requests.derivation_sha256});
 put('lineage/routes.json',application.routes);put('lineage/composition.json',application.composition);put('lineage/evaluations.json',application.evaluations);
 for(const [file,body] of Object.entries(application.files)){portable(file);if(Object.hasOwn(values,file))fail('ARTIFACT',file,'generated path collides with lineage');let data:unknown=body;if(file.endsWith('.json'))try{data=JSON.parse(body);}catch{fail('ARTIFACT',file,'generated JSON must parse');}values[file]=captureJson(data);text[file]=body;}
 assertBusinessAuthoringApplicationCurrent(application);return {values:Object.freeze(values),text:Object.freeze(text)};
}
function targetsFor(obligation:BusinessAuthoringCoverageObligation,prepared:PreparedBusinessAuthoringCoverage,application:BusinessAuthoringApplication,artifacts:ArtifactSet):BusinessAuthoringCoverageTarget[] {
 const id=prepared.model_id,source=application.selection.models.find(value=>value.model_id===id)!,model=application.models.find(value=>value.model_id===id)!,spec=source.spec,requestIndex=application.requests.models.findIndex(value=>value.model_id===id),request=application.requests.models[requestIndex]!,subject=obligation.subject;
 let unresolved=false;
 const out:BusinessAuthoringCoverageTarget[]=[],add=(artifact:string,pointer:string)=>{try{if(!Object.hasOwn(artifacts.values,artifact)){unresolved=true;return;}resolveBusinessAuthoringCoveragePointer(artifacts.values[artifact],pointer);out.push({artifact,pointer});}catch{unresolved=true;}};
 const original=`lineage/models/${id}.json`,semantics=`lineage/semantics/${id}.json`,domain=`lineage/domains/${id}.json`,actions=`lineage/actions/${id}.json`,requests='lineage/requests.json';
 const node=(raw:string)=>model.graph.nodes.findIndex(value=>value.selector===symbol(id)+':'+symbol(raw));
 if(obligation.family==='authored'){add(original,obligation.source_pointer);return out;}
 const entity=spec.entities.find(value=>value.id===subject),operation=spec.operations.find(value=>value.id===subject),capability=spec.capabilities.find(value=>value.id===subject),mapping=capability?request.mappings.find(value=>value.exposure_id===capability.id):undefined,mappingIndex=mapping?request.mappings.indexOf(mapping):-1,routeIndex=capability?application.routes.findIndex(value=>value.model_id===id&&value.id===capability.public_name):-1;
 switch(obligation.class){
  case 'semantic-declaration':add(semantics,'/declarations/'+esc(subject));add(domain,'/nodes/'+node(subject));break;
  case 'semantic-field':{const index=Number(obligation.source_pointer.split('/').at(-1)),field=entity?.fields[index];if(field)add(semantics,'/declarations/'+esc(subject)+'/properties/'+esc(field.name));else unresolved=true;add(domain,'/nodes/'+node(subject)+'/body/typed_contract');break;}
  case 'formal-definition':{const index=source.formal.definitions.findIndex(value=>value.definition_ref===subject);add(original,'/formal/definitions/'+index);break;}
  case 'formal-claim':{const index=source.formal.claims.findIndex(value=>value.claim_ref===subject),key=`formalization/claims/${subject}.json`;add(original,'/formal/claims/'+index);add(`lineage/formal/${id}/${key}`,'/claim');add(`lineage/formal/${id}/${key}`,'/canonical_proposition');add(`lineage/formal-index/${id}.json`,'/sources/'+esc(key));break;}
  case 'legacy-meaning':add(semantics,'/claim_meanings/'+esc(subject));break;
  case 'rule-interpretation':add(semantics,'/rule_meanings/'+esc(subject));add(domain,'/nodes/'+node(subject));break;
  case 'guard':case 'result':case 'effects':case 'failure':{
   if(!operation)break;const index=model.application_plan.selection.operations.findIndex(value=>value.selector===symbol(id)+':'+symbol(subject));if(index<0)unresolved=true;
   if(obligation.class==='failure')add(semantics,'/declarations/'+esc(subject)+'/failure_continuation');
   else if(obligation.class==='effects'){if(index>=0)for(const field of ['reads','writes','events'])add(actions,'/selection/operations/'+index+'/'+field);}
   else{add(semantics,'/operation_behaviors/'+esc(subject)+(obligation.class==='guard'?'/guards':'/result'));if(index>=0)add(actions,'/selection/operations/'+index+(obligation.class==='guard'?'/guards':'/result'));}break;
  }
  case 'owner-decision':add(`lineage/decisions/${id}.json`,'/subject');add(`lineage/decisions/${id}.json`,'/legacy_meaning_subjects');add(`lineage/decisions/${id}.json`,'/definition_closure');break;
  case 'recipe-profile':add('lineage/profiles/'+prepared.selection.technical.profile_id+'.json',obligation.selector);add('lineage/composition.json','/lock_sha256');break;
  case 'runtime-guarantee':{const index=prepared.selection.technical.required_guarantees.indexOf(subject);add(semantics,'/required_guarantees/'+index);break;}
  case 'profile-role':{const index=Number(obligation.source_pointer.split('/').at(-1)),runtime=prepared.inventory.snapshot.packages.find(value=>value.data.schema_version==='craft.profile-package/v3-candidate')!,rule=runtime.data.rules[index];
   if(rule?.op==='emit'){add('lineage/profiles/'+runtime.id+'.json',obligation.source_pointer);let owners=0;for(const [componentIndex,component] of application.composition.components.entries())if(component.role===rule.role&&component.origins.some(origin=>origin.kind==='profile-rule'&&origin.source===runtime.id+'/profile.json'&&origin.selector===rule.id)){owners++;add('lineage/composition.json','/components/'+componentIndex);for(const file of component.artifact_paths)add(file,'');}if(!owners)unresolved=true;}break;}
  default:{
   if(!capability||!mapping||routeIndex<0)break;const base='/models/'+requestIndex,at=base+'/mappings/'+mappingIndex;
   if(obligation.class==='public-intent'){const index=request.project_intents.findIndex(value=>value.id===capability.public_name);add(requests,base+'/project_intents/'+index);add('lineage/routes.json','/'+routeIndex);}
   else if(obligation.class==='request-mapping'){add(requests,at);add(domain,'/nodes/'+node(mapping.mapping_id));add(`lineage/request-bindings/${id}.json`,'/application_graph/runtime_bindings');}
   else if(obligation.class==='request-field'){const inputEntity=spec.entities.find(value=>value.id===mapping.input_entity)!,field=inputEntity.fields[Number(obligation.source_pointer.split('/').at(-1))],index=mapping.fields.findIndex(value=>value.target===field?.name);if(index>=0)add(requests,at+'/fields/'+index);}
   else if(obligation.class==='request-contract')add('lineage/profiles/'+prepared.selection.technical.profile_id+'.json','/authoring/wire/schema_version');
   else if(obligation.class==='request-method')add('lineage/routes.json','/'+routeIndex+'/method');
   else if(obligation.class==='request-body')add(requests,at+'/input_parameter');
   else if(obligation.class==='route'){add('lineage/routes.json','/'+routeIndex+'/route');add('lineage/routes.json','/'+routeIndex+'/method');}
   else if(obligation.class==='request-limits')add('lineage/routes.json','/'+routeIndex+'/request_bytes');
   else if(obligation.class==='timeout')add('lineage/routes.json','/'+routeIndex+'/timeout_ms');
   else if(obligation.class==='transport'){const component=application.composition.components.find(value=>value.id==='application_operation_'+capability.public_name);if(component){const index=application.composition.components.indexOf(component);add('lineage/composition.json','/components/'+index+'/depends_on');for(const file of component.artifact_paths.filter(file=>file.endsWith('/profile-entry.ts')||file.endsWith('/application-http.mts')))add(file,'');for(const dependency of component.depends_on){const owner=application.composition.components.find(value=>value.id===dependency);for(const file of owner?.artifact_paths??[])add(file,'');}}}
  }
 }
 return unresolved?[]:out.sort((a,b)=>compare(a.artifact+'#'+a.pointer,b.artifact+'#'+b.pointer));
}
function expectedLinks(prepared:PreparedBusinessAuthoringCoverage,application:BusinessAuthoringApplication,artifacts:ArtifactSet):BusinessAuthoringCoverageLink[] {
 const model=application.models.find(value=>value.model_id===prepared.model_id)!;return [...prepared.inventory.data.authored,...prepared.inventory.data.derived].map(obligation=>{
  const origins=[...obligation.origins];if(obligation.class==='owner-decision'||obligation.class==='legacy-meaning')origins.push({kind:'owner-decision',source:`lineage/decisions/${prepared.model_id}.json`,selector:obligation.class==='owner-decision'?'/subject':'/legacy_meaning_subjects',sha256:model.input.accepted.capture.file.sha256});
  if(obligation.family==='derived'&&!['recipe-profile','profile-role','runtime-guarantee'].includes(obligation.class)){
   const pointer=obligation.class==='request-field'?obligation.source_pointer.replace(/\/fields\/\d+$/,''):obligation.source_pointer.replace(/^\/identity$/,'/spec/identity');
   origins.push({kind:'semantic-adapter',source:`lineage/models/${prepared.model_id}.json`,selector:pointer,sha256:dataDigest(resolveBusinessAuthoringCoveragePointer(application.selection.models.find(value=>value.model_id===prepared.model_id)!,pointer))});
  }
  return {obligation_id:obligation.id,origins,targets:targetsFor(obligation,prepared,application,artifacts)};
 });
}
export function assessBusinessAuthoringCoverage(prepared:PreparedBusinessAuthoringCoverage,application:BusinessAuthoringApplication,candidate?:unknown):BusinessAuthoringCoverageReport {
 const owner=prepared&&typeof prepared==='object'?preparations.get(prepared):undefined;if(!owner)fail('HANDLE','/','original registered coverage preparation required');
 return withBusinessAuthoringSnapshotValidation(owner.inventory.snapshot,()=>assessCoverage(prepared,application,candidate));
}
function assessCoverage(prepared:PreparedBusinessAuthoringCoverage,application:BusinessAuthoringApplication,candidate?:unknown):BusinessAuthoringCoverageReport {
 assertPreparedBusinessAuthoringCoverageCurrent(prepared);assertBusinessAuthoringApplicationCurrent(application);if(application.selection!==prepared.selection||application.authoring_snapshot!==prepared.inventory.snapshot||!application.models.some(model=>model.model_id===prepared.model_id))fail('CORRESPONDENCE',prepared.model_id,'same original registered application and source selection required');
 const artifacts=artifactSet(application),expected=expectedLinks(prepared,application,artifacts),supplied=(candidate===undefined?expected:captureJson(candidate)) as readonly BusinessAuthoringCoverageLink[];
 if(!Array.isArray(supplied)||supplied.length>10000)fail('EVIDENCE','/','bounded coverage links required');const map=new Map<string,BusinessAuthoringCoverageLink>(),expectedMap=new Map(expected.map(link=>[link.obligation_id,link]));
 for(const [index,link] of supplied.entries()){closed(link,['obligation_id','origins','targets'],'/'+index);if(typeof link.obligation_id!=='string'||!expectedMap.has(link.obligation_id)||map.has(link.obligation_id)||!Array.isArray(link.origins)||!Array.isArray(link.targets))fail('EVIDENCE','/'+index,'unique original denominator IDs required');if(!same(link,expectedMap.get(link.obligation_id)))fail('CORRESPONDENCE',link.obligation_id,'exact independently derived origins and actual owned targets required');map.set(link.obligation_id,expectedMap.get(link.obligation_id)!);}
 const obligations=[...prepared.inventory.data.authored,...prepared.inventory.data.derived],missing:string[]=[],items:BusinessAuthoringCoverageItem[]=[],entries:BusinessLoweringLedger['entries'][number][]=[];
 for(const obligation of obligations){const link=map.get(obligation.id),retained=!!link&&link.targets.length>0;if(!retained)missing.push(obligation.id);const item:BusinessAuthoringCoverageItem={obligation_id:obligation.id,family:obligation.family,class:obligation.class,origins:link?.origins??obligation.origins,targets:link?.targets??[],state:!retained?'unsupported-required':obligation.class==='formal-claim'||obligation.scope==='formal-claim'?'claim-residue':'retained',evidence_states:retained?obligation.family==='derived'?['linked','generated']:['linked']:[]};items.push(item);
  if(retained)for(const target of link!.targets){resolveBusinessAuthoringCoveragePointer(artifacts.values[target.artifact],target.pointer);entries.push({id:obligation.id+'#'+target.artifact+'#'+target.pointer,origins:link!.origins,target});}
 }
 if(entries.length>10000)fail('BUDGET','/ledger','closed lowering ledger exceeds 10000 entries');
 const ledger=validateBusinessAuthoringContract('ledger',{schema_version:'craft.business-lowering/v1-candidate',recipe_ref:prepared.selection.recipe_ref,business_sha256:prepared.selection.models.find(model=>model.model_id===prepared.model_id)!.formal.business_sha256,lock_sha256:prepared.selection.technical.lock_sha256,entries,authority_effect:'none'}) as BusinessLoweringLedger;
 const data=captureJson({model_id:prepared.model_id,items,missing,complete:missing.length===0,ledger,artifact_sha256:Object.fromEntries(Object.entries(artifacts.text).map(([file,text])=>[file,sha256(text)])),authority_effect:'none'}) as unknown as Pick<BusinessAuthoringCoverageReport,'model_id'|'items'|'missing'|'complete'|'ledger'|'authority_effect'>;
 const result=Object.freeze({kind:'business-authoring-coverage-report' as const,prepared,application,...data,artifacts:artifacts.values,artifact_text:artifacts.text,coverage_sha256:dataDigest(data)});reports.set(result,{prepared,application,fingerprint:reportFingerprint(result)});assertBusinessAuthoringCoverageCurrent(result);return result;
}
function reportFingerprint(value:BusinessAuthoringCoverageReport):string{return dataDigest({model_id:value.model_id,items:value.items,missing:value.missing,complete:value.complete,ledger:value.ledger,artifacts:value.artifacts,artifact_text:value.artifact_text,coverage_sha256:value.coverage_sha256});}
export function assertBusinessAuthoringCoverageCurrent(value:BusinessAuthoringCoverageReport):void {const state=value&&typeof value==='object'?reports.get(value):undefined;if(!state)fail('HANDLE','/','original registered coverage report required');withBusinessAuthoringSnapshotValidation(state.prepared.inventory.snapshot,()=>{assertPreparedBusinessAuthoringCoverageCurrent(state.prepared);assertBusinessAuthoringApplicationCurrent(state.application);if(value.prepared!==state.prepared||value.application!==state.application||reportFingerprint(value)!==state.fingerprint)fail('STALE','/','coverage report or original producer custody changed');});}
export function assertBusinessAuthoringCoverageComplete(value:BusinessAuthoringCoverageReport):void {assertBusinessAuthoringCoverageCurrent(value);if(!value.complete||value.missing.length)fail('INCOMPLETE','/missing','required original/derived obligations are unsupported or absent: '+value.missing.join(', '));}

// S01 direct successor. Legacy mandatory-claim coverage above is unchanged.
import {inventoryBusinessSourceContractV2,type BusinessCoverageInventoryV2,type BusinessCoverageObligationV2} from './business-authoring-coverage-contract-v2.js';
import {assertDirectBusinessSourceGraphV2Current,type CheckedDirectBusinessSourceGraphV2} from '../formalization/direct-condition-binding.js';
import type {BusinessInputOwnerV2,AuthoringBusinessInputV2} from './business-authoring-identity-protocol-v2.js';
import type {BusinessDirectApplicationImplementationV2} from './business-authoring-application.js';
import type {BusinessCheckedCoverageV2,CheckedDirectApplicationV2,BoundU0EntryV2,BusinessRequestStagesOwnerV2,BusinessPureGenerationOwnerV2,GeneratedU0CallableSourceV2} from './business-authoring-stages-v2.js';
import {checkCoreDirectBusinessRecipeV2} from './business-authoring-recipes.js';
import {projectDirectExecutableV2,projectOptionalAssuranceV2} from './business-authoring-identity-v2.js';

type DirectCoverageLinkV2=BusinessCheckedCoverageV2['owners'][number];
export interface DirectSourceCoverageV2 {
 readonly kind:'checked-direct-source-coverage-v2';readonly source:CheckedDirectBusinessSourceGraphV2;
 readonly inventory:BusinessCoverageInventoryV2;readonly owners:readonly DirectCoverageLinkV2[];
 readonly unresolved_native_obligations:readonly string[];readonly coverage_sha256:string;readonly authority_effect:'none';
}
const directCoverageRegistryV2=new WeakMap<object,{source:CheckedDirectBusinessSourceGraphV2;fingerprint:string}>();
const directNativeObligationsV2=['decoder','values','encoder','handler','generated-callable','request-graph','injected-handler'] as const;
function directInventoryV2(spec:Parameters<typeof inventoryBusinessSourceContractV2>[0],source:Parameters<typeof inventoryBusinessSourceContractV2>[1]):BusinessCoverageInventoryV2 {
 const base=inventoryBusinessSourceContractV2(spec,source),entry=base.obligations.find(row=>row.id==='executable:entry')!;
 const extra:BusinessCoverageObligationV2[]=[...['input','output'].map(side=>({id:'derived:'+side+'-mapping',kind:'entry' as const,owner_required:'entry-intent' as const,origins:entry.origins,state:'producer-required' as const})),...directNativeObligationsV2.map(role=>({id:'native:'+role,kind:'entry' as const,owner_required:'native-realization' as const,origins:entry.origins,state:'producer-required' as const}))];
 const {inventory_sha256:_old,...body}=base,data={...body,obligations:[...base.obligations,...extra]};
 return captureJson({...data,inventory_sha256:dataDigest(data)}) as unknown as BusinessCoverageInventoryV2;
}
/** Source-only component, registered against real compiled/typed owners. It is
 * deliberately not BusinessCheckedCoverageV2 and supplies no native acceptance. */
export function checkDirectSourceCoverageV2(source:CheckedDirectBusinessSourceGraphV2,candidate?:unknown):DirectSourceCoverageV2 {
 assertModule();assertDirectBusinessSourceGraphV2Current(source);
 const inventory=directInventoryV2(source.checked.transfer.spec,source.checked.transfer.source),selectors=source.checked.roles.selectors;
 const closure=(selector:string)=>{const rows=source.closures.filter(row=>row.selector===selector);if(rows.length!==1)fail('DIRECT_SELECTOR',selector,'one original typed owner required');return rows[0]!;};
 const owners:DirectCoverageLinkV2[]=inventory.obligations.filter(row=>row.owner_required!=='native-realization').map(row=>{
  if(row.kind==='authored-fact')return {obligation_id:row.id,owner_selector:row.origins[0]!.source+'#'+row.origins[0]!.selector,owner_sha256:source.checked.transfer.source.sha256};
  const selector=row.id==='derived:input-mapping'?selectors.input_mapping:row.id==='derived:output-mapping'?selectors.output_mapping:row.kind==='entity-shape'?selectors.entity:row.kind==='condition'?selectors.rule:['guard','result','rejection','effects'].includes(row.kind)?selectors.operation:selectors.entry;
  const actual=closure(selector);return {obligation_id:row.id,owner_selector:actual.selector,owner_sha256:actual.typed_closure_sha256};
 });
 const unresolved=inventory.obligations.filter(row=>row.owner_required==='native-realization').map(row=>row.id);
 const data={kind:'checked-direct-source-coverage-v2' as const,source,inventory,owners:captureJson(owners) as unknown as readonly DirectCoverageLinkV2[],unresolved_native_obligations:Object.freeze(unresolved),authority_effect:'none' as const};
 const value:DirectSourceCoverageV2=Object.freeze({...data,coverage_sha256:dataDigest({inventory,owners,unresolved,source:source.check_sha256})});
 if(candidate!==undefined&&dataDigest(captureJson(candidate))!==dataDigest({inventory:value.inventory,owners:value.owners,unresolved_native_obligations:value.unresolved_native_obligations}))fail('DIRECT_COVERAGE','/candidate','all original obligations and exact owner links required; invented formal or native coverage forbidden');
 directCoverageRegistryV2.set(value,{source,fingerprint:dataDigest(value)});assertDirectSourceCoverageV2Current(value);return value;
}
export function assertDirectSourceCoverageV2Current(value:DirectSourceCoverageV2):void {
 const state=value&&typeof value==='object'?directCoverageRegistryV2.get(value):undefined;if(!state)fail('DIRECT_HANDLE','/coverage','original checked direct source coverage required');
 assertModule();assertDirectBusinessSourceGraphV2Current(state.source);
 if(value.source!==state.source||dataDigest(value)!==state.fingerprint)fail('DIRECT_STALE','/coverage','original source/coverage correspondence changed');
}
export function lookupDirectSourceCoverageOwnerV2(value:DirectSourceCoverageV2,id:string):Readonly<{state:'checked-owner';owner:DirectCoverageLinkV2}|{state:'pending-producer';owner:null}> {
 assertDirectSourceCoverageV2Current(value);const obligations=value.inventory.obligations.filter(row=>row.id===id);if(obligations.length!==1)fail('DIRECT_SELECTOR',id,'exact original obligation required');
 const links=value.owners.filter(row=>row.obligation_id===id);
 if(obligations[0]!.owner_required==='native-realization'){if(links.length)fail('DIRECT_COVERAGE',id,'source coverage cannot mint native owners');return Object.freeze({state:'pending-producer',owner:null});}
 if(links.length!==1)fail('DIRECT_COVERAGE',id,'exactly one actual checked owner required');return Object.freeze({state:'checked-owner',owner:links[0]!});
}
export interface BusinessDirectCoverageImplementationV2 {
 inventory(input:AuthoringBusinessInputV2):BusinessCoverageInventoryV2;
 check(application:CheckedDirectApplicationV2,bound?:BoundU0EntryV2):BusinessCheckedCoverageV2;
 assertCurrent(coverage:BusinessCheckedCoverageV2):void;
 source(coverage:BusinessCheckedCoverageV2):DirectSourceCoverageV2;
 generated(coverage:BusinessCheckedCoverageV2):GeneratedU0CallableSourceV2;
}
/** Production join: original selected acceptance/early/application/generation and
 * optional actual native late binding. No data flag can satisfy these owners. */
export function createBusinessDirectCoverageOwnerV2(inputs:BusinessInputOwnerV2,applications:BusinessDirectApplicationImplementationV2,requests:BusinessRequestStagesOwnerV2,generation:BusinessPureGenerationOwnerV2):BusinessDirectCoverageImplementationV2 {
 const original=[inputs.assertCurrent,applications.assertCurrent,applications.assertConditionCurrent,applications.source,requests.assertEarlyCurrent,requests.assertBoundCurrent,generation.generate,generation.assertCurrent];
 const assertOwners=()=>{assertModule();if(original.some((method,i)=>method!==[inputs.assertCurrent,applications.assertCurrent,applications.assertConditionCurrent,applications.source,requests.assertEarlyCurrent,requests.assertBoundCurrent,generation.generate,generation.assertCurrent][i]))fail('DIRECT_OWNER_STALE','/coverage','original input/application/requests/generation methods required');};
 const inventories=new WeakMap<object,BusinessCoverageInventoryV2>();
 const owned=new WeakMap<object,{application:CheckedDirectApplicationV2;bound:BoundU0EntryV2|null;source:DirectSourceCoverageV2;generated:GeneratedU0CallableSourceV2;fingerprint:string}>();
 const inventory=(input:AuthoringBusinessInputV2):BusinessCoverageInventoryV2=>{
  assertOwners();inputs.assertCurrent(input);requests.assertEarlyCurrent(input.early_requests);
  const model=input.selection.models.find(model=>model.model_id===input.model_id);if(!model||model.spec!==input.spec||model.capture!==input.capture)fail('DIRECT_JOIN','/input','exact original selected source/spec/capture required');
  checkCoreDirectBusinessRecipeV2({source:model.source,spec:input.spec,executable:projectDirectExecutableV2(input.spec),assurance:projectOptionalAssuranceV2(input.spec)});
  const next=directInventoryV2(input.spec,model.source),previous=inventories.get(input);if(previous&&dataDigest(previous)!==dataDigest(next))fail('DIRECT_STALE','/inventory','original source denominator changed');if(previous)return previous;inventories.set(input,next);return next;
 };
 const coverageFingerprint=(coverage:BusinessCheckedCoverageV2)=>dataDigest({kind:coverage.kind,inventory:coverage.inventory,application:coverage.application.plan_sha256,bound:coverage.bound?.subject??null,owners:coverage.owners,coverage_sha256:coverage.coverage_sha256,authority_effect:coverage.authority_effect});
 const assertCurrent=(coverage:BusinessCheckedCoverageV2):void=>{
  const state=coverage&&typeof coverage==='object'?owned.get(coverage):undefined;if(!state)fail('DIRECT_HANDLE','/coverage','original application coverage from this owner required');
  assertOwners();applications.assertCurrent(state.application);applications.assertConditionCurrent(state.application.condition);inputs.assertCurrent(state.application.input);requests.assertEarlyCurrent(state.application.input.early_requests);assertDirectSourceCoverageV2Current(state.source);
  const regenerated=generation.generate(state.application);if(regenerated.application!==state.application||regenerated.source_sha256!==state.generated.source_sha256||dataDigest(regenerated.files)!==dataDigest(state.generated.files))fail('DIRECT_STALE','/generated','current original generation owner and exact source artifacts required');
  if(state.bound){requests.assertBoundCurrent(state.bound);generation.assertCurrent(state.bound.callable);}
  if(coverage.application!==state.application||coverage.bound!==state.bound||coverage.inventory!==inventory(state.application.input)||applications.source(state.application)!==state.source.source||coverageFingerprint(coverage)!==state.fingerprint)fail('DIRECT_STALE','/coverage','original checked source/application/bound correspondence changed');
 };
 return Object.freeze({inventory,check(application:CheckedDirectApplicationV2,bound?:BoundU0EntryV2):BusinessCheckedCoverageV2{
  assertOwners();applications.assertCurrent(application);applications.assertConditionCurrent(application.condition);
  const denominator=inventory(application.input),source=checkDirectSourceCoverageV2(applications.source(application)),generated=generation.generate(application);
  if(dataDigest(denominator)!==dataDigest(source.inventory)||generated.application!==application||!generated.files.length)fail('DIRECT_JOIN','/coverage','original source denominator and generated application required');
  const owners:DirectCoverageLinkV2[]=[...source.owners];
  if(bound){
   requests.assertBoundCurrent(bound);generation.assertCurrent(bound.callable);
   if(bound.early!==application.input.early_requests||bound.early.selection!==application.input.selection||bound.callable.source.application!==application||bound.callable.source.source_sha256!==generated.source_sha256||dataDigest(bound.callable.source.files)!==dataDigest(generated.files)||bound.subject.executable_sha256!==source.inventory.executable_sha256||bound.subject.capture_sha256!==application.input.capture.capture_sha256||bound.subject.callable_sha256!==bound.callable.artifact.sha256||bound.subject.handler_sha256!==bound.handler_artifact.sha256||bound.subject.basis_sha256!==bound.basis.basis_sha256)fail('DIRECT_JOIN','/bound','exact original early/application/generated/native realization required');
   for(const [role,required]of [['decoder','decodeU0Json'],['values','formU0Submission'],['encoder','encodeU0Outcome'],['handler','createU0HttpHandler']] as const){const rows=bound.basis.artifacts.filter(row=>row.exports.includes(required)&&row.requirement.required_exports.includes(required));if(rows.length!==1)fail('DIRECT_NATIVE','/bound/'+role,'one actual selected native role required');owners.push({obligation_id:'native:'+role,owner_selector:rows[0]!.requirement.artifact_id,owner_sha256:rows[0]!.sha256});}
   owners.push({obligation_id:'native:generated-callable',owner_selector:bound.callable.artifact.path,owner_sha256:bound.callable.artifact.sha256},{obligation_id:'native:request-graph',owner_selector:'request-graph:'+bound.early.entries[0]!.entry_id,owner_sha256:bound.subject.request_graph_sha256},{obligation_id:'native:injected-handler',owner_selector:bound.handler_artifact.path,owner_sha256:bound.handler_artifact.sha256});
  }
  const ids=new Set(denominator.obligations.map(row=>row.id));if(new Set(owners.map(row=>row.obligation_id)).size!==owners.length||owners.some(row=>!ids.has(row.obligation_id))||owners.length!==denominator.obligations.length-(bound?0:directNativeObligationsV2.length))fail('DIRECT_COVERAGE','/owners','exact obligation/owner closure required');
  const links=captureJson(owners) as unknown as readonly DirectCoverageLinkV2[],data={kind:'checked-business-coverage-v2' as const,inventory:denominator,application,bound:bound??null,owners:links,authority_effect:'none' as const};
  const coverage:BusinessCheckedCoverageV2=Object.freeze({...data,coverage_sha256:dataDigest({inventory:denominator.inventory_sha256,application:application.plan_sha256,generated:generated.source_sha256,bound:bound?.subject.realized_sha256??null,owners:links})});
  owned.set(coverage,{application,bound:bound??null,source,generated,fingerprint:coverageFingerprint(coverage)});assertCurrent(coverage);return coverage;
 },assertCurrent,source(coverage:BusinessCheckedCoverageV2){assertCurrent(coverage);return owned.get(coverage)!.source;},generated(coverage:BusinessCheckedCoverageV2){assertCurrent(coverage);return owned.get(coverage)!.generated;}});
}
