import type * as W from './external-write-data-v1.js';
import type * as E from './event-data-v1.js';
import {checkGenericEventHandoffSources} from './event-handoff-source.js';
import {deriveCheckedExternalBindings,externalApplicationExecutableMeaning} from './external-read-source.js';
import type * as X from './external-read-data-v1.js';
/** Original physical source -> distinct inert atomic application contract.
 * No supplied plan, row value or inspection grants transaction authority.
 * Open Questions: C08 runtime/installed qualification remains separate. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail,coreSourceChild as child,coreSourceChildren as children,coreSourceTokens as tokens,type CoreSourceNode} from '../commerce/commerce-core-syntax.js';
import {coreValueAstType,type GenericExpressionData} from '../commerce/commerce-core-pure.js';
import {createCoreValueTypes} from '../commerce/commerce-core-types.js';
import {createCoreContextCatalog} from '../commerce/commerce-core-context.js';
import type {CoreCommerceSourceInspection} from '../commerce/commerce-core-source-owner.js';
import type {CoreOperationSource,CoreOperationStep,CoreOperationAction,CoreOperationCall,CoreTransactionStep} from '../commerce/commerce-core-flow-operation.js';
import {createGenericApplicationSourceParts,projectGenericKeyedRole} from './readonly-control.js';
import {inspectGenericOpaqueAssurance} from './assurance-source.js';
import {genericTransactionSourceSite} from './identity.js';
import type {ComputationLimitsV1} from '../commerce/commerce-data-v1.js';
import type * as Q from './query-data-v1.js';
import type * as T from './transaction-data-v1.js';
type Op=GenericExpressionData<CoreOperationSource>;type Step=GenericExpressionData<CoreOperationStep>;type Tx=GenericExpressionData<CoreTransactionStep>;type Action=GenericExpressionData<CoreOperationAction>;type Call=GenericExpressionData<CoreOperationCall>;type Site=readonly (readonly [string,string|number])[];
const words=(n:CoreSourceNode)=>tokens(n).filter(t=>!t.layout).map(t=>t.token);
const bodyNodes=(n:CoreSourceNode,rule:string)=>children(n,rule).map(w=>w.children.find((x):x is CoreSourceNode=>'rule'in x)!);
function readOnlyPreflight(rows:readonly W.GenericExternalWritePreflightStepV1[]):X.GenericExternalPreflightStepV1[]{return rows.map(s=>{if(s.kind==='write-external')return fail('UnsupportedCapability',{path:'transaction-source',start:0,end:0},'V3 write cell cannot enter V1/V2');return s.kind==='conditional'?{...s,then:readOnlyPreflight(s.then),otherwise:readOnlyPreflight(s.otherwise)}:s;});}
function createTransactionSourceContract(capture:CoreCommerceSourceInspection){
 const at={path:capture.application_path,start:0,end:0};if(capture.capture_mode!=='atomic-state-entry'&&capture.capture_mode!=='external-read-entry'&&capture.capture_mode!=='external-write-entry'&&capture.capture_mode!=='event-handoff-entry')fail('InvalidContract',at,'original atomic source capture required');
 const types=createCoreValueTypes(capture.reconstruction),root=[...types.declarations.values()].find(d=>d.interface_kind==='application-composition');if(!root)fail('MissingMapping',at,'actual application root required');
 const bounds=createCoreContextCatalog(types,capture.files.filter(f=>f.path.endsWith('.json'))).asset(root,['computation-bounds'])?.value as any;
 if(bounds?.schema_version!=='craft.generic-compute-bounds/v1-candidate'||bounds.computation?.required_schema_version!=='craft.generic-computation/v1-candidate'||bounds.computation?.required_semantics_revision!=='ordered-metered-generic-v1-candidate')fail('InvalidContract',root.syntax,'exact actual computation bounds required');
 const limits=bounds.computation.limits as ComputationLimitsV1,parts=createGenericApplicationSourceParts(capture,limits,capture.capture_mode),profile=parts.profile;
 if(profile.schema_version!==(capture.capture_mode==='event-handoff-entry'?'craft.generic-event-profile/v1-candidate':'craft.generic-transaction-profile/v1-candidate'))fail('InvalidContract',at,'actual selected atomic profile required');
 const txBounds=profile.transaction_bounds,service=(id:string)=>parts.model.ownership.find(o=>o.declaration===id)?.service??fail('InvalidContract',at,'original service ownership absent');
 const provenance:{operation:string;site:string;span:{path:string;start:number;end:number}}[]=[],sites=new Set<string>();
 const site=(operation:string,segments:Site,node:CoreSourceNode)=>{let value:string;try{value=genericTransactionSourceSite(operation,segments);}catch{return fail('ResourceLimit',node,'bounded exact source site required');}if(sites.has(value))fail('DuplicateSymbol',node,'duplicate original transaction source site');sites.add(value);provenance.push({operation,site:value,span:{path:node.path,start:node.start,end:node.end}});return value;};
 const external=(capture.capture_mode==='external-read-entry'||capture.capture_mode==='external-write-entry'||capture.capture_mode==='event-handoff-entry'&&capture.files.some(f=>f.path==='contracts/external-generation.json'))?deriveCheckedExternalBindings(capture,parts.common.functions,parts.common.values):undefined;
 const writes=parts.external_write,usedWriteBindings=new Set<string>();
 const eventBindings=capture.capture_mode==='event-handoff-entry'?checkGenericEventHandoffSources(capture):[],usedEvents=new Set<string>();
 if(writes&&!external)fail('InvalidContract',at,'selected external write requires captured external read composition');
 const controls:(T.GenericStatefulControlV1|X.GenericExternalStatefulControlV1|W.GenericExternalWriteStatefulControlV1|E.GenericEventStatefulControlV1)[]=parts.stateful.map((o:Op)=>{
  const d=parts.types.declarations.get(o.name)!,nodes=bodyNodes(child(d.syntax,'operation-statements'),'operation-statement'),indexes=o.body.flatMap((s,i)=>s.kind==='transaction'?[i]:[]);
  if(o.protocol||indexes.length!==1||indexes[0]!==o.body.length-2||o.body.at(-1)?.kind!=='action')fail('UnsupportedCapability',d.syntax,'one top-level transaction followed by exactly one terminal result expression required');
  const index=indexes[0]!,txStep=o.body[index]!,last=o.body.at(-1)!;
  if(txStep.kind!=='transaction'||last.kind!=='action'||last.action.kind!=='return')fail('UnsupportedCapability',d.syntax,'transaction result continuation must be a typed pure return');
  const transaction=txStep.transaction,txnNode=nodes[index]!;
  if(transaction.participants.length>txBounds.max_participants||!transaction.participants.length||transaction.participants.some(id=>service(id)!==service(o.name)))fail('UnsupportedCapability',txnNode,'bounded same-service participants required');
  const slots:Q.GenericContextSlotV1[]=[],role=(v:Extract<Action,{kind:'return'}>['value'],p:string)=>projectGenericKeyedRole(v,p,slots);
  const failure=(a:Action,n:CoreSourceNode):T.GenericTransactionSourceFailureV1=>{if(a.kind!=='reject'&&a.kind!=='fail')fail('UnsupportedCapability',n,'explicit failure action required');return a;};
  const terminal=(a:Action,n:CoreSourceNode,p:string):Q.GenericTerminalActionV1=>a.kind==='return'?{kind:'return',value:role(a.value,p+'.value')}:failure(a,n);
  const args=(call:Call,p:string)=>call.arguments.map((a,i)=>({parameter:a.parameter,value:role(a.value,p+'.arguments['+i+'].value')}));
  const originalPure=(call:Call,n:CoreSourceNode)=>{const target=parts.common.pure_operations.find(p=>p.operation.module+'.'+p.operation.name===call.target);if(!target||call.entry||call.role!=='Operation'||call.contexts.length||service(call.target)!==service(o.name))fail('UnsupportedCapability',n,'nonterminal call requires actual same-service zero-effect Operation');return target;};
  const sameType=(a:unknown,b:unknown)=>dataDigest(a)===dataDigest(b),bindingNames=new Map<string,number>();
  const countName=(name:string)=>bindingNames.set(name,(bindingNames.get(name)??0)+1);
  const collectTransactionNames=(rows:readonly Tx[])=>{for(const row of rows){if('name'in row)countName(row.name);if('binding'in row)countName(row.binding);if(row.kind==='for'){countName(row.item);collectTransactionNames(row.body);}if(row.kind==='conditional'){collectTransactionNames(row.then);collectTransactionNames(row.otherwise);}}};
  const collectNames=(rows:readonly Step[])=>{for(const row of rows){if('name'in row)countName(row.name);if(row.kind==='conditional'){collectNames(row.then);collectNames(row.otherwise);}if(row.kind==='read-set'){countName(row.item);collectNames(row.body);}if(row.kind==='transaction')collectTransactionNames(row.transaction.body);}};o.parameters.forEach(p=>countName(p.name));o.contexts.forEach(c=>countName(c.binding));collectNames(o.body);
  let work=0;const budget=(depth:number,n:CoreSourceNode)=>{if(++work>Math.min(limits.max_ast_nodes,4096)||depth>Math.min(limits.max_ast_depth,txBounds.max_control_depth))fail('ResourceLimit',n,'atomic control construction bound');};
  const preflight=(rows:readonly Step[],source:readonly CoreSourceNode[],prefix:Site,origins:Map<string,T.GenericReadOriginV1>,depth=1):W.GenericExternalWritePreflightStepV1[]=>rows.map((s,i)=>{
   const n=source[i]??fail('InvalidContract',d.syntax,'checked/source preflight mismatch'),p='$.preflight'+JSON.stringify([...prefix,i]);budget(depth,n);
   if(s.kind==='action'){
    const arm=prefix.at(-1);if(!external&&capture.capture_mode!=='event-handoff-entry'||!arm||!['then','else'].includes(arm[0])||arm[1]!==0||i!==rows.length-1||n.rule!=='action')fail('UnsupportedCapability',n,'source failure requires final actual action in an external V2 branch');
    const action=failure(s.action,n),physical=words(n),actions=children(n,'failure-action');
    if(actions.length!==1||physical.length!==2||physical[0]!==action.kind||physical[1]!==action.code)fail('InvalidContract',n,'checked failure differs from actual original action');
    return {kind:'source-failure',action,source_site:site(o.name,prefix,n)};
   }
   if(s.kind==='enforce-policy'){
    if(n.rule!=='enforce-statement'||s.source_site.path!==n.path||s.source_site.start!==n.start||s.source_site.end!==n.end)fail('InvalidContract',n,'checked enforcement requires its exact original source statement');
    return {kind:'enforce-policy',semantics_revision:s.semantics_revision,policy:s.policy,value:role(s.value,p+'.value'),result_enum:s.result_enum,reason_enum:s.reason_enum,rejections:s.rejections,source_site:site(o.name,[...prefix,['enforce',i]],n),source_span:s.source_site};
   }
   if(s.kind==='guard'){site(o.name,[...prefix,['guard',i]],n);return {kind:'guard',condition:role(s.condition,p+'.condition'),on_false:failure(s.on_false,n)};}
   if(s.kind==='call'){
    const binding=writes?.bindings.find(b=>b.write_operation_ref===s.call.target);
    if(binding){
     if(s.call.entry||s.call.role!=='Operation'||s.call.contexts.length||bindingNames.get(s.name)!==1||!sameType(binding.result_type,coreValueAstType(s.call.result)))fail('UnsupportedCapability',n,'native source call requires exact unique authored binding and declared logical result type; no hidden response retyping');
     const required=['on-transport-error','on-invalid-response','on-error'];if(s.handlers.length!==3||required.some(c=>!s.handlers.some(h=>h.channel===c))||s.handlers.some(h=>h.action.kind!=='reject'&&h.action.kind!=='fail'))fail('MissingMapping',n,'native source call requires exactly three explicit failure handlers');
     const checkContinuation=(offset:number,ref:string,negative:boolean,kind:'reject'|'fail')=>{
      const row=rows[i+offset],node=source[i+offset];if(!row||row.kind!=='conditional'||!node||row.then.length!==1||row.then[0]!.kind!=='action'||row.then[0]!.action.kind!==kind||row.otherwise.length)fail('MissingMapping',n,'native call requires actual ordered matches/conflict and unresolved/fail continuations');
      const ast=row.condition.source,inv=negative?(ast.kind==='not'?ast.value:null):ast;if(!inv||inv.kind!=='invoke'||parts.types.resolve(d.module,inv.name,inv).id!==ref)fail('InvalidContract',node,'actual continuation Rule/polarity differs from selected binding');
      const selected=parts.common.functions.find(f=>f.name===ref)!;const ix=selected.parameters.length-1,argument=inv.args.some(a=>a.name!==null)?inv.args.find(a=>a.name===selected.parameters[ix]!.name):inv.args[ix];if(!argument||argument.value.kind!=='name'||argument.value.name!==s.name)fail('InvalidContract',node,'actual native result must be the continuation Rule result argument');
      return genericTransactionSourceSite(o.name,[...prefix,['conditional',i+offset]]);
     };
     const matches_source_site=checkContinuation(1,binding.matches_rule_ref,true,'reject'),unresolved_source_site=checkContinuation(2,binding.unresolved_rule_ref,false,'fail');usedWriteBindings.add(binding.id);
     return {kind:'write-external',binding:s.name,type:coreValueAstType(s.call.result),call:{binding_ref:binding.id,binding_sha256:dataDigest(binding),interface_ref:binding.interface_ref,contract_operation_ref:binding.write_operation_ref,arguments:args(s.call,p),source_callsite:site(o.name,[...prefix,['call',s.name]],n),authored_site:{operation:o.name,binding:s.name}},handlers:s.handlers.map(h=>({channel:h.channel as 'on-transport-error'|'on-invalid-response'|'on-error',action:failure(h.action,n)})),continuations:{matches_rule_ref:binding.matches_rule_ref,unresolved_rule_ref:binding.unresolved_rule_ref,matches_source_site,unresolved_source_site}};
    }
    if(s.handlers.length)fail('UnsupportedCapability',n,'pure call propagates business outcome without handlers');const target=originalPure(s.call,n);return {kind:'call-pure-local',binding:s.name,target:s.call.target,target_contract_sha256:dataDigest(target),arguments:args(s.call,p),result:coreValueAstType(s.call.result),source_callsite:site(o.name,[...prefix,['call',s.name]],n),authorization:'original-local-context-forwarding-required'};
   }
   if(s.kind==='read-external'){
    if(!external)fail('UnsupportedCapability',n,'external read requires explicit new source admission');const source_callsite=site(o.name,[...prefix,['read',s.name]],n),call=external.calls.find(c=>c.operation===o.name&&c.site===source_callsite),binding=call&&external.bindings.find(b=>b.id===call.binding);
    if(!binding||binding.interface_ref!==s.call.interface_ref||dataDigest(binding.request_type)!==dataDigest(coreValueAstType(s.call.request_type))||dataDigest(binding.result_type)!==dataDigest(coreValueAstType(s.type))||binding.service!==service(o.name))fail('InvalidContract',n,'actual original Interface/profile/callsite/type binding required');
    return {kind:'read-external',binding:s.name,type:coreValueAstType(s.type),call:{binding_ref:binding.id,binding_sha256:dataDigest(binding),binding_semantics_sha256:binding.binding_semantics_sha256,interface_ref:binding.interface_ref,contract_operation_ref:binding.contract_operation_ref,arguments:s.call.arguments.map(a=>({parameter:a.parameter,value:role(a.value,p+'.arguments['+s.call.arguments.indexOf(a)+'].value')})),source_callsite},on_unavailable:terminal(s.on_unavailable,n,p+'.on_unavailable'),on_malformed:terminal(s.on_malformed,n,p+'.on_malformed')};
   }
   if(s.kind==='read'){
    const call=s.call,entry=call?.entry&&parts.common.entries.find(e=>e.entry===call.entry),query=call&&parts.common.queries.find(q=>q.query===call.target);
    if(!call||!entry||!query||call.role!=='Query'||entry.target_role!=='Query'||entry.target!==call.target||entry.service!==service(o.name)||query.service!==service(o.name)||s.entity||s.key||s.do_not_ack.length||!s.on_missing)fail('UnsupportedCapability',n,'preflight read requires actual same-service protected Query with explicit handlers');
    const e=query.projection.expression,inner=e.op==='some'?e.value:e,rowOrigin=s.type.kind==='record'&&s.type.name===query.source.entity&&inner.op==='var'&&inner.name===query.source.binding?{binding:s.name,entry:entry.entry,query:query.query,entity:query.source.entity,projection:(e.op==='some'?'canonical-some-identity-row':'identity-row') as T.GenericReadOriginV1['projection'],result_type:coreValueAstType(s.type)}:null;
    if(rowOrigin)origins.set(s.name,rowOrigin);
    return {kind:'read-entry',binding:s.name,type:coreValueAstType(s.type),call:{entry:entry.entry,query:query.query,arguments:args(call,p),source_callsite:site(o.name,[...prefix,['read',s.name]],n),authorization:'fresh-original-entry-decision-required'},on_missing:terminal(s.on_missing,n,p+'.on_missing'),on_unavailable:terminal(s.on_unavailable,n,p+'.on_unavailable'),row_origin:rowOrigin};
   }
   if(s.kind==='conditional'){
    site(o.name,[...prefix,['conditional',i]],n);const bodies=children(n,'operation-statements');let thenSource:readonly CoreSourceNode[],otherwiseSource:readonly CoreSourceNode[];
    if(n.rule==='condition-statement'){
     const actions=children(n,'action');if(!external&&capture.capture_mode!=='event-handoff-entry'||bodies.length||actions.length!==1||s.then.length!==1||s.then[0]!.kind!=='action'||s.otherwise.length)fail('UnsupportedCapability',n,'inline external conditional requires its exact checked single action and empty otherwise');
     thenSource=actions;otherwiseSource=[];
    }else{
     if(n.rule!=='when-statement'||!bodies[0]||bodies.length>2)fail('UnsupportedCapability',n,'stateful preflight conditional requires actual inline or structured branches');
     thenSource=bodyNodes(bodies[0]!,'operation-statement');otherwiseSource=bodies[1]?bodyNodes(bodies[1],'operation-statement'):[];
    }
    if(s.then.length!==thenSource.length||s.otherwise.length!==otherwiseSource.length)fail('InvalidContract',n,'checked/source conditional branch sequence mismatch');
    const yes=new Map(origins),no=new Map(origins),then=preflight(s.then,thenSource,[...prefix,['conditional',i],['then',0]],yes,depth+1),otherwise=preflight(s.otherwise,otherwiseSource,[...prefix,['conditional',i],['else',0]],no,depth+1);for(const [key,value]of yes)if(no.has(key)&&dataDigest(no.get(key))===dataDigest(value))origins.set(key,value);return {kind:'conditional',condition:role(s.condition,p+'.condition'),then,otherwise};
   }
   return fail('UnsupportedCapability',n,'stateful preflight is closed to reads, pure calls, checked Policy enforcement, guards, conditionals and external V2 source failures');
  });
  const origins=new Map<string,T.GenericReadOriginV1>(),prepared=preflight(o.body.slice(0,index),nodes.slice(0,index),[],origins);
  const txPath:Site=[['transaction',transaction.name]];site(o.name,txPath,txnNode);
  let emissionOrdinal=0;
  const transactionSteps=(rows:readonly Tx[],source:readonly CoreSourceNode[],prefix:Site,depth=1):(T.GenericTransactionStepV1|E.GenericEventEmitStepV1)[]=>{
   const statements=source.filter(n=>n.rule!=='transaction-handler');if(rows.length!==statements.length)fail('InvalidContract',txnNode,'checked/source transaction sequence mismatch');
   return rows.map((s,i)=>{const n=statements[i]!,p='$.transaction'+JSON.stringify([...prefix,i]);budget(depth,n);
    if(s.kind==='emit-event'){
     if(capture.capture_mode!=='event-handoff-entry'||depth!==1)fail('UnsupportedCapability',n,'only top-level source-ordered Event emission admitted');
     const binding=eventBindings.find(b=>b.event_selector===s.event&&b.producer_operation===o.name);
     if(!binding||dataDigest(coreValueAstType(s.payload.type))!==dataDigest(binding.payload_type)||usedEvents.has(binding.id))fail('InvalidContract',n,'emit must match one authored Event payload and producer');
     usedEvents.add(binding.id);return {kind:'emit-event',binding_ref:binding.id,binding_sha256:dataDigest(binding),event_selector:binding.event_selector,event_version:binding.event_version,payload_type:binding.payload_type,payload:role(s.payload,p+'.payload'),source_site:site(o.name,[...prefix,['emit',i]],n),emission_ordinal:emissionOrdinal++};
    }
    if(s.kind==='mutation'){
     if(s.operation!=='create'&&s.operation!=='update')fail('UnsupportedCapability',n,'only create/update admitted');
     const ordered_fields=s.fields.map((f,j)=>({name:f.name,value:role(f.value,p+'.fields['+j+'].value')})),source_site=site(o.name,[...prefix,[s.operation,s.binding]],n);
     if(s.operation==='create')return {kind:'create',binding:s.binding,entity:s.target,ordered_fields,source_site};
     const origin=s.origin_read_binding&&origins.get(s.origin_read_binding);if(!origin||origin.entity!==s.target||s.key||s.expected_version)fail('InvalidContract',n,'update requires independently reconstructed direct original read');
     return {kind:'update-observed',binding:s.binding,entity:s.target,origin_read_binding:origin.binding,ordered_fields,source_site};
    }
    if(s.kind==='guard')return {kind:'guard',condition:role(s.condition,p+'.condition'),on_false:failure(s.on_false,n),source_site:site(o.name,[...prefix,['guard',i]],n)};
    if(s.kind==='let'){if(s.on_error)fail('UnsupportedCapability',n,'atomic typed errors remain outer faults');return {kind:'let',binding:s.name,type:coreValueAstType(s.value.type),value:role(s.value,p+'.value'),source_site:site(o.name,[...prefix,['call',s.name]],n)};}
    if(s.kind==='for')return {kind:'for',item:s.item,source:role(s.source,p+'.source'),body:transactionSteps(s.body,bodyNodes(n,'transaction-statement'),[...prefix,['loop',i]],depth+1) as T.GenericTransactionStepV1[],source_site:site(o.name,[...prefix,['loop',i]],n)};
    if(s.kind==='conditional'){
     const yes:CoreSourceNode[]=[],no:CoreSourceNode[]=[];let other=false;for(const c of n.children){if('token'in c&&c.token==='otherwise')other=true;if('rule'in c&&c.rule==='transaction-statement')(other?no:yes).push(c.children.find((x):x is CoreSourceNode=>'rule'in x)!);}
     return {kind:'conditional',condition:role(s.condition,p+'.condition'),then:transactionSteps(s.then,yes,[...prefix,['conditional',i],['then',0]],depth+1) as T.GenericTransactionStepV1[],otherwise:transactionSteps(s.otherwise,no,[...prefix,['conditional',i],['else',0]],depth+1) as T.GenericTransactionStepV1[],source_site:site(o.name,[...prefix,['conditional',i]],n)};
    }
    return fail('UnsupportedCapability',n,'transaction step outside closed atomic scope');
   });
  };
  const required=['on-version-conflict','on-unique-conflict','on-proven-rollback','on-unknown-commit'] as const;
  const applicable=capture.capture_mode==='event-handoff-entry'?transaction.body.some(s=>s.kind==='mutation'&&s.operation==='update')?'on-unique-conflict':'on-version-conflict':null;
  if(transaction.defaults.length||transaction.handlers.length<2||transaction.handlers.length>4||new Set(transaction.handlers.map(h=>h.channel)).size!==transaction.handlers.length||transaction.handlers.some(h=>!required.includes(h.channel as typeof required[number]))||required.some(k=>!transaction.handlers.some(h=>h.channel===k)&&k!==applicable&&k!=='on-version-conflict'))fail('MissingMapping',txnNode,'exact applicable transaction failure handlers required');
  const handlers=Object.fromEntries(required.map(k=>{const h=transaction.handlers.find(h=>h.channel===k);if(!h)return [k,k==='on-version-conflict'?null:{kind:'reject',code:'unique-conflict-not-applicable'}];if(!h.action||h.recovery||h.do_not_ack)fail('UnsupportedCapability',txnNode,'transaction recovery requires explicit reject/fail only');return [k,failure(h.action,txnNode)];})) as T.GenericTransactionPlanV1['handlers'];
  site(o.name,[['return',0]],nodes.at(-1)!);
  const control={operation:o.name,service:service(o.name),parameters:o.parameters.map(p=>({name:p.name,type:coreValueAstType(p.type)})),contexts:o.contexts.map(c=>{if(c.source_type!=='Craft.Generated.Auth.CustomerContext'||c.abi!=='craft.generic-auth-customer-context/v1-candidate')fail('UnsupportedCapability',d.syntax,'selected Auth context required');return {...c,source_type:'Craft.Generated.Auth.CustomerContext' as const,abi:'craft.generic-auth-customer-context/v1-candidate' as const};}),context_slots:slots,result:coreValueAstType(o.result),transaction:{name:transaction.name,participants:transaction.participants.filter(id=>parts.types.declarations.get(id)?.surface==='Entity'),body:transactionSteps(transaction.body,bodyNodes(txnNode,'transaction-statement'),txPath),result_expression:role(last.action.value,'$.transaction.result_expression'),handlers,limits,transaction_bounds:txBounds,defaults:[] as readonly []},protocol:null};
  if(capture.capture_mode==='event-handoff-entry')return {schema_version:'craft.generic-stateful-control/v4-candidate',semantics_revision:'atomic-event-handoff/v1-candidate',...control,preflight:prepared} as E.GenericEventStatefulControlV1;
  const ordinary={...control,transaction:{...control.transaction,body:control.transaction.body as T.GenericTransactionStepV1[]}};
  if(writes)return {schema_version:'craft.generic-stateful-control/v3-candidate',semantics_revision:'atomic-external-write-entry/v1-candidate',...ordinary,preflight:prepared};
  if(external)return {schema_version:'craft.generic-stateful-control/v2-candidate',semantics_revision:'atomic-external-read-entry/v1-candidate',...ordinary,preflight:readOnlyPreflight(prepared)};
  const legacy=(rows:readonly X.GenericExternalPreflightStepV1[]):T.GenericStatefulPreflightStepV1[]=>rows.map(s=>{if(s.kind==='read-external'||s.kind==='source-failure')return fail('UnsupportedCapability',d.syntax,'external discriminant cannot enter legacy v1 control');if(s.kind==='conditional')return {...s,then:legacy(s.then),otherwise:legacy(s.otherwise)};return s;});
  return {schema_version:'craft.generic-stateful-control/v1-candidate',semantics_revision:'atomic-state-entry/v1-candidate',...ordinary,preflight:legacy(readOnlyPreflight(prepared))};
 });
 if(!controls.length)fail('MissingMapping',at,'atomic source needs actual stateful Operation');
 if(capture.capture_mode==='event-handoff-entry'&&(usedEvents.size!==eventBindings.length||eventBindings.some(b=>!controls.some(o=>o.operation===b.consumer_operation))))fail('MissingMapping',at,'each Event requires exactly one producer emit and a checked consumer Operation');
 const entries:(Q.GenericLogicalEntryV1|T.GenericTransactionEntryV1|E.GenericEventEntryV1|E.GenericEventOperatorEntryV1|E.GenericEventOperatorQueryEntryV1)[]=parts.common.entries.map(e=>{
  const source=parts.types.declarations.get(e.entry)!,operator=capture.capture_mode==='event-handoff-entry'&&source.access.some(a=>words(a)[0]==='authenticated'&&words(a)[1]==='operator');
  const command=controls.some(o=>o.operation===e.target);
  if(operator&&command)return {...e,schema_version:'craft.generic-operator-entry/v1-candidate',target_role:'Operation',access:{...e.access,principal_kind:'operator' as const,current_action:'final-ready-before-command-replay-and-commit' as const}};
  if(operator)return {...e,schema_version:'craft.generic-operator-query-entry/v1-candidate',access:{...e.access,principal_kind:'operator' as const}};
  return command?{...e,schema_version:'craft.generic-transaction-entry/v1-candidate',target_role:'Operation',access:{...e.access,current_action:'final-ready-before-command-replay-and-commit'}}:e;
 });
 if(capture.capture_mode==='event-handoff-entry')for(const binding of eventBindings){const target=parts.types.declarations.get(binding.consumer_operation)!,result=target.result&&parts.types.type(target.module,target.result,target.syntax);if(!result||target.parameters.length!==1)fail('TypeMismatch',target.syntax,'receiver Operation requires one mapped argument');entries.push({schema_version:'craft.generic-event-entry/v1-candidate',entry:binding.target_entry,target:binding.consumer_operation,target_role:'Operation',service:binding.target_service,interaction:'event',event_selector:binding.event_selector,event_version:binding.event_version,payload_type:binding.payload_type,mapping:binding.consumer_mapping,parameters:[{name:target.parameters[0]!.name,type:coreValueAstType(parts.types.type(target.module,target.parameters[0]!.type,target.parameters[0]!.span))}],result:coreValueAstType(result),access:{principal_kind:'service',caller:binding.producer_service,permission:binding.target_permission.permission,resource:binding.target_permission.resource,action:binding.target_permission.action,scope:binding.target_permission.scope,route:binding.target_route,context_type:'Craft.Generated.Auth.ServiceContext',context_abi:'craft.generic-auth-service-context/v1-candidate',native_abi:'craft.commerce-auth-ready-bridge/v1-candidate',native_asset:'auth-foundation-ready',current_action:'fresh-ready-before-inbox-replay-and-commit'}});}
 const common={...parts.common,entries:entries as (Q.GenericLogicalEntryV1|T.GenericTransactionEntryV1)[],application_namespace:profile.application_namespace,transaction_bounds:txBounds};
 if(writes&&usedWriteBindings.size!==writes.bindings.length)fail('InvalidContract',at,'every selected write pair requires an actual uniquely bound call with continuations');
 const contract:T.GenericTransactionApplicationContractV1|X.GenericExternalTransactionApplicationV1|W.GenericExternalWriteTransactionApplicationV1|E.GenericEventTransactionApplicationV1=capture.capture_mode==='event-handoff-entry'?{...common,entries,schema_version:'craft.generic-transaction-application/v4-candidate',semantics_revision:'atomic-event-handoff/v1-candidate',admission_mode:'event-handoff-entry',stateful_operations:controls.map(c=>c.schema_version==='craft.generic-stateful-control/v4-candidate'?c:fail('InvalidContract',at,'Event mode requires every source control V4')),external_bindings:external?.bindings??[],write_bindings:writes?.bindings??[],...(writes?{identity_limits:writes.selection.identity_limits}:{}),event_bindings:eventBindings,execution_policy:'original-durable-event-handoff'}:writes?{...common,schema_version:'craft.generic-transaction-application/v3-candidate',semantics_revision:'atomic-external-write-entry/v1-candidate',admission_mode:'external-write-entry',stateful_operations:controls.map(c=>c.schema_version==='craft.generic-stateful-control/v3-candidate'?c:fail('InvalidContract',at,'write mode requires every source control V3')),external_bindings:external!.bindings,write_bindings:writes.bindings,identity_limits:writes.selection.identity_limits,execution_policy:'refused-until-original-durable-external-owner'}:external?{...common,schema_version:'craft.generic-transaction-application/v2-candidate',semantics_revision:'atomic-external-read-entry/v1-candidate',admission_mode:'external-read-entry',stateful_operations:controls.map(c=>c.schema_version==='craft.generic-stateful-control/v2-candidate'?c:fail('InvalidContract',at,'new mode requires every control V2')),external_bindings:external.bindings}:{...common,schema_version:'craft.generic-transaction-application/v1-candidate',semantics_revision:'atomic-state-entry/v1-candidate',admission_mode:'atomic-state-entry',stateful_operations:controls.map(c=>c.schema_version==='craft.generic-stateful-control/v1-candidate'?c:fail('InvalidContract',at,'old mode requires v1 controls'))};
 const executableSubject=dataDigest(contract.admission_mode==='external-read-entry'?externalApplicationExecutableMeaning(contract):contract);
 const assurance=inspectGenericOpaqueAssurance(capture,executableSubject);
 return coreFreeze({contract,assurance,derivation:{...parts.derivation,executable_semantics_sha256:executableSubject,profile_sha256:dataDigest(profile),source_capture_sha256:capture.capture_sha256,source_sites:provenance,assurance_sha256:assurance.assurance_sha256}});
}

/** Existing callers retain their original closed V1/V2 return algebra. */
export function createGenericTransactionSourceContract(capture:CoreCommerceSourceInspection){
 const actual=createTransactionSourceContract(capture);if(actual.contract.admission_mode==='external-write-entry'||actual.contract.admission_mode==='event-handoff-entry')return fail('UnsupportedCapability',{path:capture.application_path,start:0,end:0},'V3/V4 source requires its distinct checked source entrypoint');return coreFreeze({...actual,contract:actual.contract});
}
/** Source-only V3 remains original source composition; this grants no dispatch. */
export function createGenericExternalWriteTransactionSourceContract(capture:CoreCommerceSourceInspection){
 if(capture.capture_mode!=='external-write-entry')return fail('InvalidContract',{path:capture.application_path,start:0,end:0},'exact write capture mode required');const actual=createTransactionSourceContract(capture);if(actual.contract.admission_mode!=='external-write-entry')return fail('InvalidContract',{path:capture.application_path,start:0,end:0},'actual V3 contract required');return coreFreeze({...actual,contract:actual.contract});
}
/** C12 exact Event source admission; this result is inert until original runtime owners check it. */
export function createGenericEventTransactionSourceContract(capture:CoreCommerceSourceInspection){
 if(capture.capture_mode!=='event-handoff-entry')return fail('InvalidContract',{path:capture.application_path,start:0,end:0},'exact Event capture mode required');const actual=createTransactionSourceContract(capture);if(actual.contract.admission_mode!=='event-handoff-entry')return fail('InvalidContract',{path:capture.application_path,start:0,end:0},'actual V4 contract required');return coreFreeze({...actual,contract:actual.contract});
}
