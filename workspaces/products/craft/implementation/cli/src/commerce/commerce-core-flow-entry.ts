/** Independent inline entry/access source facets. Private projection schemas
 * describe requirements; they never authorize a request or construct owners.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail,CoreCommerceSourceError,coreSourceChildren as children,coreSourceChild as child,coreSourceDescendants as descendants,coreSourceTokens as tokens,coreSourceText as text,lexCoreCommerceSource,type CoreSourceNode,type CoreSourceRange} from './commerce-core-syntax.js';
import {reconstructCoreCommerceSources,type CoreCommerceDeclaration} from './commerce-core-reconstruction.js';
import {parseCoreExpression,parseCoreTypeTokens,type CoreExpression} from './commerce-core-expression.js';
import {checkCoreCommercePureSources,coreValueAstType as genericEntryValueType} from './commerce-core-pure.js';
import {checkCoreCommerceQuerySources} from './commerce-core-flow-query.js';
import {createCoreValueTypes,CORE_BOOL,type CoreValueType} from './commerce-core-types.js';
import {createCoreContextCatalog,type CoreCapturedAsset,type CoreContextRequirement} from './commerce-core-context.js';
import {createCoreFlowExpressionChecker,type CoreFlowScope,type CoreFlowExpression} from './commerce-core-flow-expression.js';

export interface CoreEntryResourceBinding {
 readonly binding:string;readonly kind:'data'|'private-projection';readonly source_type:string;
 readonly abi:string;readonly selector:string;readonly fields:readonly {readonly name:string;readonly type:CoreValueType}[];
 readonly required_fields:readonly string[];readonly projection_family:boolean;
 readonly source_document:string|null;
 readonly origin:Readonly<{kind:'current-invocation'|'fresh-effect-intent'|'scoped-query-row'|'parent-customer-delegation'|'workflow-journal'|'worker-observation';declaration:string|null;transaction:string|null;binding:string|null}>;
 readonly custody:'required-from-original-registered-owner';readonly public_constructor:'forbidden';
}
export interface CoreEntrySource {
 readonly id:string;readonly invokes:string;readonly role:'Operation'|'Query'|'Workflow';readonly service:string;
 readonly interaction:'request-response'|'event';readonly parameters:readonly {readonly name:string;readonly type:CoreValueType}[];
 readonly result:CoreValueType|null;readonly event_argument:string|null;
 readonly access:Readonly<{
  principal_kind:'customer'|'service';caller:string;permission:string;
  auth_permission:Readonly<{resource:string;action:string;scope:string}>;auth_route_id:string;
  context:Readonly<{source_type:string;abi:string;custody:string}>;
  decision:Readonly<{source_type:string;abi:string;binding_path:string;admission:string;decision:string;route_template:string}>;
  native_requires:'craft.context.current-owner/v1-candidate';current_action:'before-replay-and-effects';
  resource_bindings:readonly CoreEntryResourceBinding[];resource_condition:CoreFlowExpression|null;
  resource_phase:'fresh-intent-before-effects'|'scoped-read-before-response'|'causal-before-invocation';
  matching_replay_resource_check:'trusted-scope-only'|'same-causal-input'|'not-applicable';
  on_resource_missing_or_false:'forbidden'|'resource-not-found';producer:string|null;
  worker_lifetime:'requires-original-local-worker-owner'|'not-applicable';
  invocation_decision:'fresh-separate-original-entry-decision';
  event_completion:'requires-original-consumer-inbox-and-result-commit'|'not-applicable';
 }>;
 readonly native_requirements:readonly string[];readonly qualification:'typed-entry-source-only';
}
export interface CoreEntryAudit {
 readonly schema_version:'craft.commerce-core-entry-audit/v1-candidate';readonly pure_subject_sha256:string;readonly query_subject_sha256:string;
 readonly entries:readonly CoreEntrySource[];readonly diagnostics:readonly {readonly entry:string;readonly diagnostics:CoreCommerceSourceError['diagnostics']}[];
 readonly complete:boolean;readonly authority_effect:'none';
}
const words=(n:CoreSourceNode)=>tokens(n).filter(t=>!t.layout).map(t=>t.token);
const object=(value:unknown,n:CoreSourceRange):Record<string,unknown>=>{if(!value||typeof value!=='object'||Array.isArray(value))fail('InvalidContract',n,'closed source contract object required');return value as Record<string,unknown>;};
const sourceName=(n:CoreExpression):string|null=>n.kind==='name'?n.name:n.kind==='field'&&sourceName(n.value)?sourceName(n.value)+'.'+n.field:null;
/** Collect source-used top-level projection fields, without exposing absent
 * future-stage fields from a projection family. A whole-value use needs all. */
function usedFields(source:CoreExpression|null,binding:string,all:readonly string[]):string[]{
 const names=new Set<string>();const visit=(value:unknown)=>{if(!value||typeof value!=='object')return;
  if('kind'in value&&(value.kind==='name'||value.kind==='field')){const path=sourceName(value as CoreExpression);if(path===binding){all.forEach(f=>names.add(f));return;}if(path?.startsWith(binding+'.')){names.add(path.slice(binding.length+1).split('.')[0]!);return;}}
  Object.values(value).forEach(visit);
 };visit(source);return [...names].sort();
}

export function auditCoreCommerceEntrySources(sources:readonly {readonly path:string;readonly text:string}[],assets:readonly CoreCapturedAsset[]=[]):CoreEntryAudit {
 const pure=checkCoreCommercePureSources(sources),queries=checkCoreCommerceQuerySources(sources,assets),model=reconstructCoreCommerceSources(sources),types=createCoreValueTypes(model),catalog=createCoreContextCatalog(types,assets);
 const entries:CoreEntrySource[]=[],diagnostics:CoreEntryAudit['diagnostics'][number][]=[],routes=new Map<string,string>();
 const owned=(d:CoreCommerceDeclaration)=>model.ownership.find(o=>o.declaration===d.id)?.service;
 const interfaceClause=(d:CoreCommerceDeclaration,head:string,required=true)=>{const found=children(d.syntax,'interface-clause').filter(n=>words(n)[0]===head);if(found.length>1)fail('DuplicateSymbol',d.syntax,'duplicate private Interface '+head);if(required&&!found.length)fail('MissingMapping',d.syntax,'private Interface requires '+head);return found[0]??null;};
 const privateInterface=(d:CoreCommerceDeclaration,custody:string,n:CoreSourceRange)=>{if(d.surface!=='Interface'||d.interface_kind!=='trusted-context')fail('TypeMismatch',n,'entry context requires trusted-context Interface');if(words(interfaceClause(d,'custody')!).slice(1).join(' ')!==custody)fail('InvalidContract',n,'private projection custody kind is incompatible with entry');for(const [head,tail]of [['serializable','false'],['public-constructor','forbidden']]as const)if(words(interfaceClause(d,head)!).slice(1).join(' ')!==tail)fail('InvalidContract',n,'entry private context must forbid serialization and public construction');};
 for(const d of types.declarations.values())if(d.surface==='Entry')try{
  const expression=createCoreFlowExpressionChecker(types,catalog),clauses=new Map<string,CoreSourceNode[]>();for(const n of d.access){const head=words(n)[0]!,rows=clauses.get(head)??[];rows.push(n);clauses.set(head,rows);}
  for(const [head,rows]of clauses)if(head!=='resource-binding'&&rows.length>1)fail('DuplicateSymbol',rows[1]!,'duplicate inline entry '+head);
  const clause=(head:string,required=true)=>{const rows=clauses.get(head)??[];if(rows.length>1)fail('DuplicateSymbol',d.syntax,'duplicate inline entry '+head);if(required&&!rows.length)fail('MissingMapping',d.syntax,'entry requires inline '+head);return rows[0]??null;};
  const value=(head:string)=>words(clause(head)!)[1]!;
  const target=types.resolve(d.module,d.invokes!,d.syntax),service=owned(target);if(!service)fail('InvalidContract',d.syntax,'entry target must belong to a declared service');
  const interaction=words(d.syntax)[words(d.syntax).indexOf('interaction')+1]as'request-response'|'event';
  if(target.surface==='Workflow'&&interaction!=='event'||target.surface==='Query'&&interaction==='event')fail('TypeMismatch',d.syntax,'entry interaction is incompatible with target role');
  const parameters=target.parameters.map(p=>({name:p.name,type:types.type(target.module,p.type,p.span)})),result=target.result?types.type(target.module,target.result,target.syntax):null;
  const principal=value('authenticated')as'customer'|'service',caller=value('caller');if(principal==='customer'&&caller!=='self'||principal==='service'&&!model.services.some(s=>s.service===caller))fail('InvalidContract',clause('caller')!,'customer caller must be self; service caller must name a declared service');
  if(principal==='customer')clause('principal-from');
  const permission=text(child(clause('permission')!,'permission-name')),resource=value('auth-resource'),action=text(child(clause('auth-action')!,'permission-name')),scopeName=value('auth-scope');
  if(permission!==resource+'.'+action)fail('InvalidContract',clause('permission')!,'inline permission must equal auth-resource plus auth-action');
  const route=text(child(clause('auth-route')!,'reference')),contextType=types.resolve(d.module,text(child(clause('context')!,'qualified-name')),d.syntax);if(contextType.surface!=='Interface'||contextType.interface_kind!=='trusted-context')fail('TypeMismatch',d.syntax,'entry context requires a trusted-context Interface');
  const custody=words(interfaceClause(contextType,'custody')!).slice(1).join(' '),isWorker=custody==='private-registered-local-worker-owner';
  const expectedCustody=principal==='customer'?'private-registered-entry-auth-owner':isWorker?'private-registered-local-worker-owner':'private-registered-service-entry-owner';privateInterface(contextType,expectedCustody,d.syntax);
  const context=catalog.require(contextType);
  const targetContexts=target.contexts.flatMap(c=>c.type.kind==='named'?[types.resolve(target.module,c.type.name,c.span)]:[]).filter(c=>c.interface_kind==='trusted-context'&&children(c.syntax,'interface-clause').some(n=>words(n)[0]==='custody'&&['private-registered-entry-auth-owner','private-registered-local-worker-owner','private-registered-service-entry-owner'].includes(words(n)[1]!)));
  if(targetContexts.length&&!targetContexts.some(c=>c.id===contextType.id))fail('TypeMismatch',d.syntax,'entry context differs from the original target invocation context');
  if(isWorker){clause('worker-from');clause('invocation-decision');}else if(clause('worker-from',false)||clause('invocation-decision',false))fail('InvalidContract',d.syntax,'worker lifetime clauses require a private local worker context');
  const native=text(child(clause('native-requires')!,'reference'));if(native!=='craft.context.current-owner/v1-candidate')fail('UnsupportedCapability',d.syntax,'unregistered current-entry context ABI');clause('current-action');
  const authOwners=[...types.declarations.values()].filter(c=>c.interface_kind==='native-auth-owner');if(authOwners.length!==1)fail('MissingMapping',d.syntax,'entry requires one explicit native Auth decision Interface');const authOwner=authOwners[0]!,authBinding=catalog.asset(authOwner,['binding']);if(!authBinding)fail('MissingMapping',authOwner.syntax,'Auth decision requires its captured binding');
  const authAbi=text(child(interfaceClause(authOwner,'abi')!,'reference'));if(authBinding.doc.abi!==authAbi)fail('InvalidContract',authOwner.syntax,'Auth binding ABI differs from source decision Interface');
  const admission=words(interfaceClause(authOwner,'admission')!).slice(1).join(''),decision=words(interfaceClause(authOwner,'decision')!).slice(1).join(''),template=object(authBinding.doc.policy_template_mapping,d.syntax).entry_route;
  if(typeof template!=='string'||!/^[-A-Za-z0-9_.]+:logicalEntryId$/.test(template))fail('UnsupportedCapability',authOwner.syntax,'Auth route requires the registered literal-prefix logicalEntryId template');
  if(route!==template.slice(0,-'logicalEntryId'.length)+d.id)fail('InvalidContract',clause('auth-route')!,'Auth route must select this exact logical entry identity');
  const priorRoute=routes.get(route);if(priorRoute&&priorRoute!==d.id)fail('DuplicateSymbol',d.syntax,'Auth route reused by another logical entry');routes.set(route,d.id);
  let eventArgument:string|null=null,producer:string|null=null;
  if(interaction==='event'){
   if(principal!=='service')fail('InvalidContract',d.syntax,'event ingress requires authenticated service producer');producer=value('producer');if(producer!==caller||!model.services.some(s=>s.service===producer))fail('InvalidContract',d.syntax,'event producer must equal its declared service caller');clause('occurrence-from');clause('acknowledge');
   if(parameters.length!==1||parameters[0]!.type.kind!=='record'||types.declarations.get(parameters[0]!.type.name)?.surface!=='Event')fail('TypeMismatch',d.syntax,'event entry requires exactly one declared Event payload');eventArgument=parameters[0]!.name;
  }else if(clause('producer',false)||clause('occurrence-from',false)||clause('acknowledge',false))fail('InvalidContract',d.syntax,'event provenance/ack clauses require an event interaction');
  const guardNode=clause('resource-condition',false),guardSource=guardNode?parseCoreExpression(child(guardNode,'expression')):null;
  const forbidden=clause('on-resource-false',false),notFound=clause('on-resource-missing-or-false',false);if(forbidden&&notFound)fail('DuplicateSymbol',d.syntax,'entry has conflicting resource failure outcomes');if(guardSource&&!forbidden&&!notFound)fail('MissingMapping',d.syntax,'resource condition requires its explicit false/missing outcome');if(!guardSource&&(forbidden||notFound))fail('InvalidContract',d.syntax,'resource failure outcome has no condition');
  const input=expression.registerRecord(d.id+'.CoreEntryInput',parameters,d.syntax),env=new Map<string,CoreValueType>([['input',input]]),contexts=new Map<string,CoreContextRequirement>(),bindings:CoreEntryResourceBinding[]=[];
  const declaredBindings=clauses.get('resource-binding')??[];if(declaredBindings.length>16)fail('ResourceLimit',d.syntax,'entry resource binding bound');
  for(const n of declaredBindings){const binding=words(n)[1]!,sourceType=text(child(n,'qualified-name')),raw=text(child(n,'reference')),parts=raw.split('#');if(parts.length!==2||!parts[0]||!parts[1])fail('InvalidContract',n,'resource owner requires exact ABI and selector');const [abi,selector]=parts as[string,string];if(env.has(binding)||contexts.has(binding))fail('DuplicateSymbol',n,'entry resource binding shadows input/another binding');
   let kind:CoreEntryResourceBinding['kind']='private-projection',fields:CoreEntryResourceBinding['fields']=[],sourceDocument:string|null=null,family=false,resolvedType=sourceType,origin:CoreEntryResourceBinding['origin'];
   if(abi==='craft.commerce-causal-call/v1-candidate'){
    const candidates=[...types.declarations.values()].filter(c=>c.interface_kind==='trusted-context'&&children(c.syntax,'interface-clause').some(n=>words(n)[0]==='abi'&&text(child(n,'reference'))===abi));if(candidates.length!==1)fail('MissingMapping',n,'causal binding requires one exact source Interface');const owner=candidates[0]!;privateInterface(owner,'private-registered-parent-call-store-worker-or-event-owner',n);const asset=catalog.asset(owner,['variants']);if(!asset)fail('MissingMapping',n,'causal Interface requires captured variant schemas');const schemas=object(asset.value,n),projection=object(schemas[sourceType],n);if(projection.kind!=='opaque-private-projection'||typeof projection.projection_family!=='boolean')fail('InvalidContract',n,'causal schema must explicitly declare its private projection kind and family status');
    const namespace=/^([A-Za-z_][A-Za-z0-9_.]*)@1$/.exec(String(asset.doc.source_module));if(!namespace||!types.modules.has(namespace[1]!))fail('UnknownReference',n,'causal projection contract requires exact captured source_module@1');
    const declared=object(projection.fields,n),names=Object.keys(declared);if(!names.length||names.length>64||names.some(name=>!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)))fail('ResourceLimit',n,'causal projection requires bounded named fields');const required=usedFields(guardSource,binding,names);family=projection.projection_family;
    const schemaFields=names.map(name=>{const annotation=declared[name];if(typeof annotation!=='string')fail('InvalidContract',n,'causal projection field needs an explicit type annotation');return {name,type:types.type(namespace[1]!,parseCoreTypeTokens(lexCoreCommerceSource(annotation,'causal-field-annotation.alch'),n),n)};});if(required.some(name=>!names.includes(name)))fail('UnknownReference',n,'required causal projection field is absent');fields=family?schemaFields.filter(field=>required.includes(field.name)):schemaFields;resolvedType=owner.id+'.'+sourceType;sourceDocument=asset.path;
    if(selector==='parent-customer-delegation')origin={kind:'parent-customer-delegation',declaration:null,transaction:null,binding:null};else{const split=selector.split('/');if(split.length!==2)fail('UnsupportedCapability',n,'unknown registered causal selector');const [base,slot]=split as[string,string];if(slot==='original-step-journal'){const workflows=[...types.declarations.values()].filter(w=>w.surface==='Workflow'&&(w.id===base||w.module===base));if(workflows.length!==1)fail('UnknownReference',n,'causal journal selector must name one source Workflow');origin={kind:'workflow-journal',declaration:workflows[0]!.id,transaction:null,binding:null};}else if(slot==='original-worker-observation'){const row=types.resolve(d.module,base,n);if(row.surface!=='Entity'||owned(row)!==service||!isWorker)fail('InvalidContract',n,'worker observation requires service-owned Entity and original worker');origin={kind:'worker-observation',declaration:row.id,transaction:null,binding:null};}else fail('UnsupportedCapability',n,'unregistered causal selector slot');}
    env.set(binding,expression.registerRecord(d.id+'.CorePrivateResource.'+binding,fields,n));
   }else if(abi==='craft.effect-intent/v1-candidate'||abi==='craft.scoped-query-row/v1-candidate'){
    kind='data';const record=types.resolve(d.module,sourceType,n);if(record.surface!=='Entity'||owned(record)!==service)fail('InvalidContract',n,'resource row/intent must select its target service Entity');resolvedType=record.id;fields=expression.fields({kind:'record',name:record.id},n);
    const selectors=selector.split('/');if(abi==='craft.effect-intent/v1-candidate'){
     if(selectors.length!==3||target.surface!=='Operation'||types.resolve(d.module,selectors[0]!,n).id!==target.id)fail('InvalidContract',n,'effect intent must select the exact entry Operation transaction and alias');const transactions=descendants(target.syntax,'transaction').filter(t=>words(t)[1]===selectors[1]);if(transactions.length!==1)fail('UnknownReference',n,'effect intent transaction is absent/ambiguous');const mutations=descendants(transactions[0]!,'mutation').filter(m=>words(m)[0]==='create'&&words(m)[1]===selectors[2]&&types.resolve(target.module,text(child(m,'qualified-name')),m).id===record.id);if(mutations.length!==1)fail('UnknownReference',n,'effect intent must select one exact created Entity alias');origin={kind:'fresh-effect-intent',declaration:target.id,transaction:selectors[1]!,binding:selectors[2]!};
    }else{
     if(selectors.length!==2||target.surface!=='Query'||types.resolve(d.module,selectors[0]!,n).id!==target.id)fail('InvalidContract',n,'scoped row must select this exact entry Query');const query=queries.queries.find(q=>q.name===target.id);if(query?.kind!=='local'||!query.sources.some(s=>s.binding===selectors[1]&&s.entity===record.id))fail('UnknownReference',n,'scoped row must name one independently checked local Query source');origin={kind:'scoped-query-row',declaration:target.id,transaction:null,binding:selectors[1]!};
    }env.set(binding,{kind:'record',name:record.id});
   }else{
    const owner=types.resolve(d.module,sourceType,n);privateInterface(owner,'private-registered-entry-auth-owner',n);const ctx=catalog.require(owner);if(abi!==ctx.abi||selector!=='current-invocation'||owner.id!==contextType.id)fail('InvalidContract',n,'current invocation resource must bind the exact original entry context and ABI');fields=ctx.properties;resolvedType=owner.id;contexts.set(binding,ctx);sourceDocument=catalog.asset(owner,['fields'])?.path??null;origin={kind:'current-invocation',declaration:owner.id,transaction:null,binding:null};
   }
   const required=usedFields(guardSource,binding,fields.map(f=>f.name));if(required.some(name=>!fields.some(f=>f.name===name)))fail('UnknownReference',n,'resource guard selects an undeclared projection field');bindings.push({binding,kind,source_type:resolvedType,abi,selector,fields,required_fields:required,projection_family:family,source_document:sourceDocument,origin,custody:'required-from-original-registered-owner',public_constructor:'forbidden'});
  }
  const guard=guardSource?expression.check(guardSource,{module:d.module,env,contexts}as CoreFlowScope,CORE_BOOL):null;if(guard?.native_calls.length)fail('InvalidContract',guardSource!,'entry resource conditions must be pure over original bounded projections');
  if(bindings.some(binding=>!binding.required_fields.length))fail('InvalidContract',d.syntax,'resource binding is unused by its source condition');
  const intent=bindings.some(b=>b.origin.kind==='fresh-effect-intent'),row=bindings.some(b=>b.origin.kind==='scoped-query-row');if(intent&&row)fail('UnsupportedCapability',d.syntax,'one entry resource phase cannot mix fresh intent with scoped read response');if(row&&!notFound)fail('InvalidContract',d.syntax,'scoped own-resource queries require missing/foreign resource-not-found before projection');
  entries.push(coreFreeze({id:d.id,invokes:target.id,role:target.surface as CoreEntrySource['role'],service,interaction,parameters,result,event_argument:eventArgument,access:{principal_kind:principal,caller,permission,auth_permission:{resource,action,scope:scopeName},auth_route_id:route,context:{source_type:contextType.id,abi:context.abi,custody},decision:{source_type:authOwner.id,abi:authAbi,binding_path:authBinding.path,admission,decision,route_template:template},native_requires:'craft.context.current-owner/v1-candidate',current_action:'before-replay-and-effects',resource_bindings:bindings,resource_condition:guard,resource_phase:intent?'fresh-intent-before-effects':row?'scoped-read-before-response':'causal-before-invocation',matching_replay_resource_check:intent?'trusted-scope-only':interaction==='event'?'not-applicable':'same-causal-input',on_resource_missing_or_false:notFound?'resource-not-found':'forbidden',producer,worker_lifetime:isWorker?'requires-original-local-worker-owner':'not-applicable',invocation_decision:'fresh-separate-original-entry-decision',event_completion:interaction==='event'?'requires-original-consumer-inbox-and-result-commit':'not-applicable'},native_requirements:['original-current-Auth-admission-ready-decision-and-invocation-bound-context','current-action-before-replay-inspection-and-effects','exact-source-entry-permission-route-input-profile-native-scope','resource-projections-only-from-recognized-original-owner-at-declared-phase','missing-required-causal-field-rejects-never-fabricates-future-stage-value','matching-replay-never-runs-fresh-intent-id-clock-or-quote-work','worker-lifetime-never-substitutes-for-fresh-entry-decision','event-producer-schema-occurrence-fingerprint-and-original-local-commit-before-ack'],qualification:'typed-entry-source-only'}));
 }catch(error){if(!(error instanceof CoreCommerceSourceError))throw error;diagnostics.push({entry:d.id,diagnostics:error.diagnostics});}
 entries.sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
 return coreFreeze({schema_version:'craft.commerce-core-entry-audit/v1-candidate',pure_subject_sha256:pure.pure_subject_sha256,query_subject_sha256:queries.query_subject_sha256,entries,diagnostics,complete:diagnostics.length===0,authority_effect:'none'});
}
export function checkCoreCommerceEntrySources(sources:readonly {readonly path:string;readonly text:string}[],assets:readonly CoreCapturedAsset[]=[]):CoreEntryAudit {
 const result=auditCoreCommerceEntrySources(sources,assets);if(!result.complete){const first=result.diagnostics[0]!.diagnostics[0]!;fail(first.code,first,first.message);}return result;
}
export function checkCoreCommerceEntryProposal(sources:readonly {readonly path:string;readonly text:string}[],assets:readonly CoreCapturedAsset[],proposal:unknown):CoreEntryAudit {
 const actual=checkCoreCommerceEntrySources(sources,assets);let hash:string;try{hash=dataDigest(proposal);}catch{return fail('InvalidContract',{path:sources[0]?.path??'application.alch',start:0,end:0},'inert bounded entry proposal required');}if(hash!==dataDigest(actual))fail('InvalidContract',{path:sources[0]?.path??'application.alch',start:0,end:0},'entry proposal differs from independent source reconstruction');return actual;
}

/** Closed C07 inline permission facet. It reuses the original declaration graph;
 * private Auth producers, not these inert descriptors, issue READY custody. */
export function checkCoreGenericKeyedEntrySources(sources:readonly {path:string;text:string}[],mode:'keyed-query-entry'|'atomic-state-entry'|'external-read-entry'|'external-write-entry'|'event-handoff-entry'='keyed-query-entry'):readonly import('../generic/query-data-v1.js').GenericLogicalEntryV1[]{
 if(mode!=='keyed-query-entry'&&(mode!=='atomic-state-entry'&&mode!=='external-read-entry'&&mode!=='external-write-entry'&&mode!=='event-handoff-entry'))fail('InvalidContract',{path:'entry-mode',start:0,end:0},'exact entry source mode required');
 const model=reconstructCoreCommerceSources(sources,mode),types=createCoreValueTypes(model),out:import('../generic/query-data-v1.js').GenericLogicalEntryV1[]=[];
 for(const d of types.declarations.values())if(d.surface==='Entry'){
  if(mode==='event-handoff-entry'&&words(d.syntax)[words(d.syntax).indexOf('interaction')+1]==='event')continue;
  const clauses=new Map<string,CoreSourceNode>();for(const n of d.access){const head=words(n)[0]!;if(clauses.has(head))fail('DuplicateSymbol',n,'duplicate inline access clause');if(!['authenticated','caller','permission','auth-resource','auth-action','auth-scope'].includes(head))fail('UnsupportedCapability',n,'entry access clause requires a later profile');clauses.set(head,n);}
  const value=(head:string,optional=false)=>{const n=clauses.get(head);if(!n){if(optional)return null;return fail('MissingMapping',d.syntax,'entry requires inline '+head);}const v=words(n).slice(1).join('');if(!v)fail('InvalidContract',n,'entry access value missing');return v;};
  if(value('authenticated')!=='customer'&&!(mode==='event-handoff-entry'&&value('authenticated')==='operator'))fail('UnsupportedCapability',d.syntax,'selected entry principal required');if((value('caller',true)??'self')!=='self')fail('InvalidContract',d.syntax,'original caller must be self');
  const target=types.resolve(d.module,d.invokes!,d.syntax),service=model.ownership.find(o=>o.declaration===target.id)?.service;if(!service)fail('InvalidContract',d.syntax,'entry target needs original profile service ownership');
  if(target.surface!=='Query'&&target.surface!=='Operation')fail('UnsupportedCapability',d.syntax,'entry target requires Query or Operation');
  if(words(d.syntax)[words(d.syntax).indexOf('interaction')+1]!=='request-response')fail('UnsupportedCapability',d.syntax,'keyed profile requires request-response logical entry');
  const permission=value('permission')!,resource=value('auth-resource')!,action=value('auth-action')!,scope=value('auth-scope')!;
  if(permission!==resource+'.'+action||[permission,resource,action,scope].some(v=>v.length>256))fail('InvalidContract',d.syntax,'permission must match exact bounded resource.action and scope');
  if(!target.result)fail('MissingMapping',d.syntax,'entry target result missing');
  out.push({schema_version:'craft.generic-logical-entry/v1-candidate',entry:d.id,target:target.id,target_role:target.surface,service,interaction:'request-response',parameters:target.parameters.map(p=>({name:p.name,type:genericEntryValueType(types.type(target.module,p.type,p.span))})),result:genericEntryValueType(types.type(target.module,target.result,target.syntax)),access:{principal_kind:'customer',caller:'self',permission,resource,action,scope,route:'commerce:'+d.id,context_type:'Craft.Generated.Auth.CustomerContext',context_abi:'craft.generic-auth-customer-context/v1-candidate',native_abi:'craft.commerce-auth-ready-bridge/v1-candidate',native_asset:'auth-foundation-ready',current_action:'final-ready-before-protected-read'}});
 }
 if(out.length>64)fail('ResourceLimit',{path:sources[0]?.path??'source',start:0,end:0},'at most 64 logical entries');return coreFreeze(out);
}
