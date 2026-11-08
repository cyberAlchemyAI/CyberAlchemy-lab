/** Finite application resource joins; original owners alone mint runtime ports.
 * Open Questions: craft/projects/domainspec-v2/impl/cli/docs/APPLICATION-INPUT-PROFILES.md. */
import {types} from 'node:util';
import {assert,closed,freeze,text,u64} from '../shared.mjs';
export const APPLICATION_SYSTEM_BINDINGS=freeze([
 {consumer:'permissioned-rag/domain-v1',sourcePort:'ingestion',producer:'knowledge-ingestion/domain-v1',targetPort:'active',contract:'craft.generated-ingestion-reference/v1',effect:'read',input_codec:'craft.application-run/v1',result_codec:'craft.generated-ingestion-reference/v1',slot:'knowledge.ingestion'},
 {consumer:'customer-support/domain-v1',sourcePort:'rag',producer:'permissioned-rag/domain-v1',targetPort:'answer',contract:'craft.rag-answer-binding/v1',effect:'read',input_codec:'craft.application-run/v1',result_codec:'craft.rag-answer-binding/v1',slot:'rag',source_roles:['ragFacts','documentA','documentB']},
 {consumer:'marketing-campaign/domain-v1',sourcePort:'preferences',producer:'crm-contact-enrichment/domain-v1',targetPort:'preferences',contract:'craft.generated-query-source/v1',effect:'read',input_codec:'craft.grouped-preference-inputs/v1',result_codec:'craft.generated-query-source/v1',slot:'query'}
]);
export function selectApplicationSystemBinding(edge,children){
 const consumer=children.get(edge.source),producer=children.get(edge.target);assert(consumer&&producer,'InvalidContract','actual application join children');const matches=APPLICATION_SYSTEM_BINDINGS.filter(row=>row.consumer===consumer.family&&row.producer===producer.family&&['sourcePort','targetPort','contract','effect','input_codec','result_codec'].every(key=>row[key]===edge[key]));assert(matches.length===1,'UnsupportedCapability','finite original application resource join');return matches[0];
}
export function validateApplicationSystemJoin(raw,binding){
 const preference=binding.slot==='query';let value;
 // Grouped inputs are a genuine host Map, not serialized authority JSON. Check
 // its container without sending the Map through the inert JSON copier.
 if(preference){assert(raw&&typeof raw==='object'&&!types.isProxy(raw)&&Object.getPrototypeOf(raw)===Object.prototype,'InvalidContract','plain grouped preference join');const descriptors=Object.getOwnPropertyDescriptors(raw),keys=Reflect.ownKeys(descriptors);assert(keys.every(key=>typeof key==='string'&&['inputs','workerSubject'].includes(key)&&descriptors[key].enumerable&&Object.hasOwn(descriptors[key],'value'))&&Object.hasOwn(descriptors,'inputs'),'InvalidContract','closed grouped preference join fields');value=Object.fromEntries(keys.map(key=>[key,descriptors[key].value]));}
 else value=closed(raw,['run','workerSubject','publicSubject'],['run']);for(const key of ['workerSubject','publicSubject'])if(value[key]!==undefined)text(value[key],key,128);
 if(preference){assert(value.inputs instanceof Map&&!types.isProxy(value.inputs)&&Object.getPrototypeOf(value.inputs)===Map.prototype&&value.inputs.size>0&&value.inputs.size<=100,'InvalidContract','bounded original grouped preference Query inputs');const inputs=new Map([...value.inputs].map(([id,rows])=>{text(id,'preference source id',256);assert(Array.isArray(rows)&&rows.length>0&&rows.length<=16,'ResourceLimit','bounded original preference group');return [id,freeze(rows.map(row=>{const input=closed(row,['contactId']);u64(input.contactId);return {contactId:input.contactId};}))];}));return {...value,inputs};}
 const run=closed(value.run,['id','run']);u64(run.id);u64(run.run);return {...value,run:{...run}};
}
export function applicationSystemRoleSubjects(binding,configuration){
 assert(APPLICATION_SYSTEM_BINDINGS.includes(binding),'ForeignOwner','original finite application resource binding');if(!binding.source_roles)return Object.freeze({});const run=closed(configuration.run,['id','run']);u64(run.id);u64(run.run);return freeze(Object.fromEntries(binding.source_roles.map(role=>[role,run.id])));
}
export function assertApplicationSystemSlotFree(resources,binding){
 if(binding.slot==='knowledge.ingestion')assert(resources.knowledge&&!Object.hasOwn(resources.knowledge,'ingestion'),'InvalidContract','declared ingestion join cannot be shadowed');
 if(binding.slot==='rag')assert(!Object.hasOwn(resources,'rag'),'InvalidContract','declared RAG join cannot be shadowed');
 if(binding.slot==='query')assert(!Object.hasOwn(resources,'query')&&!Object.hasOwn(resources,'preference'),'InvalidContract','declared protected Query join cannot be shadowed');
}
export async function bindApplicationSystemResource({binding,configuration,producer,producerResources,consumerResources}){
 assertApplicationSystemSlotFree(consumerResources,binding);producer.assertCurrent();const selectors=producer.access.selectors,workerSubject=configuration.workerSubject??producerResources.workerSubject,publicSubject=configuration.publicSubject??producerResources.customerSubject;
 if(binding.slot==='knowledge.ingestion'){assert(typeof producer.createReference==='function'&&producer.referencePort,'ForeignOwner','original generated ingestion reference owner');const reference=await producer.createReference({actor:producer.actor(publicSubject,selectors.status),...configuration.run});producer.assertCurrent();return {...consumerResources,knowledge:{...consumerResources.knowledge,ingestion:{port:producer.referencePort,reference}}};}
 if(binding.slot==='rag'){assert(typeof producer.readAnswer==='function','ForeignOwner','original generated RAG answer owner');const workerActor=producer.actor(workerSubject,selectors.stage),publicActor=producer.actor(publicSubject,selectors.status),selection=freeze({...configuration.run}),application=Object.freeze({readAnswer(request){producer.assertCurrent();return producer.readAnswer({...request,actor:publicActor,workerActor,access:producer.access,...selection});}}),rag={application,access:producer.access,workerActor,publicActor,run:selection.run,producerRun:selection};await application.readAnswer({});producer.assertCurrent();return {...consumerResources,rag};}
 assert(typeof producer.createPreferenceSource==='function'&&consumerResources.release?.authority,'ForeignOwner','original generated CRM Query factory and consumer release authority');const query=await producer.createPreferenceSource({inputs:configuration.inputs,releaseAuthority:consumerResources.release.authority,adapterId:'crm-preferences',subject:workerSubject});producer.assertCurrent();return {...consumerResources,query};
}
