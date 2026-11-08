/** Reconstruct C12 Event/receiver bindings from authored source, never from a
 * caller-supplied envelope. This is source meaning only; runtime owners decide
 * authorization, occurrence identity, and effects.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {dataDigest} from '../profile-engine/contracts.js';
import {coreFreeze,coreSourceFail as fail,coreSourceChildren as children,coreSourceChild as child,coreSourceTokens as tokens,coreSourceText as text,type CoreSourceNode} from '../commerce/commerce-core-syntax.js';
import {createCoreValueTypes} from '../commerce/commerce-core-types.js';
import {parseCoreExpression} from '../commerce/commerce-core-expression.js';
import {coreValueAstType} from '../commerce/commerce-core-pure.js';
import type {CoreCommerceSourceInspection} from '../commerce/commerce-core-source-owner.js';
import {parseCoreCommerceJson} from '../commerce/commerce-core-source-owner.js';
import type {CoreCommerceDeclaration} from '../commerce/commerce-core-reconstruction.js';
import type {GenericEventBindingV1} from './event-data-v1.js';

const words=(n:CoreSourceNode)=>tokens(n).filter(t=>!t.layout).map(t=>t.token);
const site=(d:CoreCommerceDeclaration)=>`${d.syntax.path}:${d.syntax.start}:${d.syntax.end}`;
export function checkGenericEventHandoffSources(capture:CoreCommerceSourceInspection):readonly GenericEventBindingV1[]{
 const model=capture.reconstruction,types=createCoreValueTypes(model),declarations=types.declarations;
 const owner=(d:CoreCommerceDeclaration)=>model.ownership.find(o=>o.declaration===d.id)?.service;
 const one=(d:CoreCommerceDeclaration,key:string)=>{const rows=d.access.filter(c=>words(c)[0]===key);if(rows.length!==1)fail('MissingMapping',d.syntax,'Event receiver requires exactly one '+key);return rows[0]!;};
 const output:GenericEventBindingV1[]=[];
 for(const event of declarations.values())if(event.surface==='Event'&&event.event_handoff){
  const source=event.event_handoff,producer=declarations.get(source.from),target=declarations.get(source.delivered_to);
  if(!producer||producer.surface!=='Operation'||producer.module!==event.module||!target||target.surface!=='Entry'||target.module===event.module)fail('InvalidContract',event.syntax,'Event must bind an actual producer Operation and cross-service receiver Entry');
  const producerService=owner(producer),targetService=owner(target);
  if(!producerService||!targetService||producerService===targetService)fail('InvalidContract',event.syntax,'Event producer and receiver need distinct declared service owners');
  if(source.payload.kind!=='named')fail('TypeMismatch',event.syntax,'Event payload requires an authored producer ValueObject');
  const payload=types.resolve(event.module,source.payload.name,event.syntax);
  if(payload.surface!=='ValueObject'||payload.module!==event.module)fail('TypeMismatch',event.syntax,'Event payload requires an authored producer ValueObject');
  const interaction=words(target.syntax),ix=interaction.indexOf('interaction'),selectors=children(target.syntax,'qualified-name');
  if(interaction[ix+1]!=='event'||text(selectors[2]!)!==event.id)fail('InvalidContract',target.syntax,'receiver Entry must name the exact producer Event selector');
  const consumer=declarations.get(target.invokes??'');if(!consumer||consumer.surface!=='Operation'||owner(consumer)!==targetService)fail('InvalidContract',target.syntax,'receiver Entry must invoke an owned Operation');
  const bindings=children(target.syntax,'expression'),bind=words(target.syntax).indexOf('bind');
  if(bind<0||bindings.length!==1||interaction[bind+2]!=='<-'||consumer.parameters.length!==1||consumer.parameters[0]!.name!==interaction[bind+1])fail('MissingMapping',target.syntax,'receiver Entry requires one authored payload Mapping into the Operation parameter');
  const expression=parseCoreExpression(bindings[0]!);
  if(expression.kind!=='invoke'||expression.args.length!==1||expression.args[0]!.value.kind!=='name'||expression.args[0]!.value.name!=='payload')fail('TypeMismatch',target.syntax,'receiver Mapping must consume the checked Event payload');
  const mapping=types.resolve(target.module,expression.name,target.syntax);
  const consumerInput=consumer.parameters[0]!.type;
  if(!mapping||mapping.surface!=='Mapping'||mapping.parameters.length!==1||mapping.parameters[0]!.type.kind!=='named'||mapping.parameters[0]!.type.name!==payload.id||mapping.result?.kind!=='named'||consumerInput.kind!=='named'||mapping.result.name!==consumerInput.name)fail('TypeMismatch',target.syntax,'receiver Mapping must convert the exact nominal producer payload into the consumer argument');
  const authenticated=words(one(target,'authenticated'))[1];if(authenticated!=='relay')fail('InvalidContract',target.syntax,'Event receiver requires profile-owned relay principal');
  const permission=text(child(one(target,'permission'),'permission-name')),resource=words(one(target,'auth-resource'))[1]!,action=text(child(one(target,'auth-action'),'permission-name')),scope=words(one(target,'auth-scope'))[1]!;
  if(permission!==resource+'.'+action)fail('InvalidContract',target.syntax,'inline receiver permission must bind resource/action');
  const payloadType=coreValueAstType(types.type(event.module,source.payload,event.syntax));
  output.push(coreFreeze({id:event.id+'->'+target.id,event_selector:event.id,event_version:1,producer_service:producerService,producer_operation:producer.id,payload_type:payloadType,payload_schema_sha256:dataDigest(payloadType),target_service:targetService,target_entry:target.id,target_route:'commerce:'+target.id,target_permission:{permission,resource,action,scope},consumer_operation:consumer.id,consumer_mapping:mapping.id,event_source_site:site(event)}));
 }
 if(!output.length){
  // Finite V2 Workflows reuse this transaction admission without inventing an
  // unrelated Event/provider requirement. Ordinary C12 applications retain it.
  const workflows=[...declarations.values()].filter(d=>d.surface==='Workflow'&&d.syntax.rule==='generic-workflow-declaration');
  const file=capture.files.find(f=>f.path==='contracts/workflow-profile.json');
  let finite=false;
  if(workflows.length===1&&file&&![...declarations.values()].some(d=>d.surface==='Event')&&!words(workflows[0]!.syntax).includes('awaits')){const selected=parseCoreCommerceJson(file.text,file.path) as {schema_version?:string;workflow?:string;stages?:unknown};finite=selected.schema_version==='craft.generic-workflow-profile/v2'&&selected.workflow===workflows[0]!.id&&Array.isArray(selected.stages)&&selected.stages.length>0&&selected.stages.length<=64;}
  if(!finite)fail('MissingMapping',{path:capture.application_path,start:0,end:0},'C12 Event handoff requires a declared Event/receiver pair');
 }
 if(new Set(output.map(b=>b.event_selector)).size!==output.length||new Set(output.map(b=>b.target_entry)).size!==output.length)fail('DuplicateSymbol',{path:capture.application_path,start:0,end:0},'Event selector or receiver Entry reused');
 return coreFreeze(output);
}
