/** Checked technical graph -> finite family requirements. No absent native asset
 * is implemented by metadata. Open Questions: docs/COMMERCE-PROFILE-FAMILY-V5.md. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {captureJson,dataDigest} from './contracts.js';
import {PROFILE_V5,ENGINE_V5,closedV5,parametersV5,scopeV5,primitiveV5,nativeRequirementV5,type NativeRequirementV5} from './contracts-v5.js';
import {assertTechnicalModelOwnerV5,type CommerceTechnicalModelOwnerV5} from './technical-model-v5.js';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {pinCoreImplementation} from '../commerce/commerce-core-physical.js';
import type {CommerceFamilyOwner,CommerceTechnicalModelHandle,CommerceDerivedFamilyHandle} from '../commerce/commerce-stages-v1.js';
import type {NativeObligationV1,ProfilePackageV1,RealizationScopeV1} from '../commerce/commerce-data-v1.js';
const ext=path.extname(fileURLToPath(import.meta.url)),pin=pinCoreImplementation(import.meta.url,['technical-model-v5'+ext,'contracts-v5'+ext]),where={path:'profile-family-v5',start:0,end:0};
export type ProfileDescriptorHeaderV5=Omit<ProfilePackageV1,'resolved_dependencies'>;
export interface DerivedFamilyInspectionV5 {readonly kind:'original-derived-profile-requirements/v5-candidate';readonly graph_sha256:string;readonly source_capture_sha256:string;readonly family_sha256:string;readonly mapping_result:Readonly<Record<string,unknown>>;readonly descriptor:ProfileDescriptorHeaderV5;readonly native_requirements:readonly NativeRequirementV5[];readonly qualification:'source-derived-requirements-only;actual-produced-assets-required-before-load';readonly authority_effect:'none'}
export interface CommerceFamilyOwnerV5 extends CommerceFamilyOwner {inspect(family:CommerceDerivedFamilyHandle):DerivedFamilyInspectionV5;dispose(family:CommerceDerivedFamilyHandle):void;modelOwner():CommerceTechnicalModelOwnerV5}
const owners=new WeakSet<object>();
export function assertFamilyOwnerV5(owner:CommerceFamilyOwnerV5){if(!owner||typeof owner!=='object'||!owners.has(owner))fail('ForeignOwner',where,'original v5 family factory required');}
export function createCommerceFamilyOwnerV5(models:CommerceTechnicalModelOwnerV5):CommerceFamilyOwnerV5 {
 assertTechnicalModelOwnerV5(models);pin.assertCurrent();const owned=new WeakMap<object,{model:CommerceTechnicalModelHandle;inspection:DerivedFamilyInspectionV5;disposed:boolean}>();
 const current=(family:CommerceDerivedFamilyHandle)=>{const s=family&&typeof family==='object'?owned.get(family):undefined;if(!s)fail('ForeignOwner',where,'original family from this exact model/family owner required');if(s.disposed)fail('DisposedOwner',where,'derived family disposed');pin.assertCurrent();models.assertCurrent(s.model);return s;};
 const owner:CommerceFamilyOwnerV5=Object.freeze({checkTechnicalSource:models.checkTechnicalSource,derive(model:CommerceTechnicalModelHandle,parameters:ProfilePackageV1['parameters'],scope:RealizationScopeV1){
  pin.assertCurrent();const m=models.inspect(model),p=parametersV5(parameters),s=scopeV5(scope),doc=m.family_contract,native=m.native_contract;
  closedV5(doc,['schema_version','technical_source','qualification','required_successor','families','derivation_chain','extension_contract','currentness','authority_effect','product_approval','open_questions_ref']);if(doc.schema_version!=='craft.commerce-profile-family/v1-candidate'||doc.technical_source!==m.source.artifact.path||doc.required_successor?.schema_version!==PROFILE_V5||doc.required_successor?.engine!==ENGINE_V5||doc.authority_effect!=='none'||!doc.families||typeof doc.families!=='object'||Array.isArray(doc.families))fail('InvalidContract',where,'captured exact technical family contract required');
  for(const [name,value]of Object.entries(doc.families)){
   if(!/^[A-Za-z_][A-Za-z0-9_.]*$/.test(name))fail('InvalidContract',where,'source family names required');
   closedV5(value,name==='EventInboxOutbox'?['primitive','inputs','emits','publication']:['primitive','inputs','emits']);
   const f=value as any;primitiveV5(f.primitive);
   if(typeof f.inputs!=='string'||typeof f.emits!=='string')
    fail('InvalidContract',where,'family inputs/emissions are descriptions,not executable hooks');
   if(name==='EventInboxOutbox'&&f.publication!==undefined){
    closedV5(f.publication,['machine','signal']);
    if(f.primitive!=='event-inbox-outbox'||
     typeof f.publication.machine!=='string'||
     !/^[A-Za-z_][A-Za-z0-9_.]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$/.test(f.publication.machine)||
     typeof f.publication.signal!=='string'||
     !/^[A-Za-z_][A-Za-z0-9_]*$/.test(f.publication.signal))
     fail('InvalidContract',where,'finite EventInboxOutbox publication machine and signal required');
   }
  }
  closedV5(native,['schema_version','qualification','obligations','resolution_stages','stages_are_distinct','on_missing_primitive','on_unproduced_artifact','on_ambiguous_version_or_producer','source_fallback','application_callback','raw_sql_or_js_templates','actual_resolution_owners','authority_effect','product_approval','open_questions_ref','context_facets']);if(native.schema_version!=='craft.commerce-native-obligations/v1-candidate'||native.authority_effect!=='none'||!Array.isArray(native.obligations)||native.obligations.length>32||native.stages_are_distinct!==true||native.source_fallback!==false||native.application_callback!==false||native.raw_sql_or_js_templates!==false)fail('InvalidContract',where,'closed captured native obligation source and no-hook/no-fallback boundary required');
  const requirementRows=new Map<string,NativeRequirementV5>();for(const o of native.obligations){closedV5(o,['primitive_id','abi','required_exports','producer_tasks','status','supplying_runtime','effect_class','binding_mode']);const {status,binding_mode,...r}=o;if(status!=='implementation-pending'||typeof binding_mode!=='string')fail('InvalidContract',where,'requirements do not advertise resolved availability');const req=nativeRequirementV5({...r,kind:'native-requirement',authority_effect:'none'});if(requirementRows.has(req.primitive_id))fail('DuplicateSymbol',where,'one primitive requirement source required');requirementRows.set(req.primitive_id,req);}
  for(const target of s.targets){const original=m.module_contracts.find(module=>module.source.module===target.module)?.declarations.find(d=>dataDigest(d.selector)===dataDigest(target));if(!original)fail('UnknownReference',where,'scope targets must be actual checked source declarations');if(s.kind==='pure-pricing'&&!['Rule','Calculation','Mapping','StateMachine'].includes(target.role))fail('UnsupportedCapability',where,'pure scope cannot silently run an effectful role');}
  const result=models.evaluateSelection(model,p),mapping=m.graph.nodes.find(n=>n.id===m.mapping)!.definition,record=m.values.records.find(r=>mapping.result.kind==='record'&&r.name===mapping.result.name)!;
  const rule=m.policy.scope_rules.find(r=>r.kind===s.kind)!,families:string[]=[],primitives:string[]=[];
  for(const slotName of rule.slots){const slot=m.policy.slots.find(slot=>slot.name===slotName)!,type=record.fields[slot.source_field];if(type?.kind!=='enum')fail('TypeMismatch',where,'family slots must select actual source enum fields');const definition=m.values.enums.find(e=>e.name===type.name)!,variant=definition.variants.find(v=>v.wire===result[slot.source_field]);if(!variant||Object.keys(variant.fields).length)fail('TypeMismatch',where,'source Mapping must return a declared nullary family variant');const selected=doc.families[variant.name];if(!selected||selected.primitive!==slot.primitive)fail('UnsupportedCapability',where,'selected source family is absent or incompatible with its native slot');if(!families.includes(variant.name))families.push(variant.name);if(!primitives.includes(selected.primitive))primitives.push(selected.primitive);}
  for(const id of rule.additional_primitives)if(!primitives.includes(id))primitives.push(id);const requirements=primitives.map(id=>requirementRows.get(id)??fail('MissingMapping',where,'selected primitive has no native requirement source'));
  if(s.kind==='pure-pricing'&&requirements.some(r=>r.effect_class!=='pure'))fail('UnsupportedCapability',where,'pure realization scope cannot acquire an effectful native primitive through policy');
  // Mapping parameters are observed output,not a second hand-written policy.
  if(result.tablePrefix!==p.tablePrefix||result.requestBytes!==String(p.requestBytes)||result.responseBytes!==String(p.responseBytes)||result.bodyTimeoutMs!==String(p.bodyTimeoutMs))fail('InvalidContract',where,'source Mapping changed the requested compatible wire/config domain');
  const obligations:NativeObligationV1[]=requirements.map(({primitive_id,abi,required_exports,producer_tasks})=>({primitive_id,abi,required_exports,producer_tasks})),descriptor:ProfileDescriptorHeaderV5={schema_version:PROFILE_V5,engine:ENGINE_V5,id:m.policy.package_id,version:m.policy.package_version,technical_source:m.source,family_mapping:m.mapping,scope:s,families,parameters:p,obligations,authority_effect:'none'};
  const subject={kind:'original-derived-profile-requirements/v5-candidate' as const,graph_sha256:m.graph_sha256,source_capture_sha256:m.source_capture_sha256,mapping_result:result,descriptor,native_requirements:requirements,qualification:'source-derived-requirements-only;actual-produced-assets-required-before-load' as const,authority_effect:'none' as const},inspection:DerivedFamilyInspectionV5=coreFreeze({...subject,family_sha256:dataDigest(subject)}),family=Object.freeze({kind:'derived-family'}) as unknown as CommerceDerivedFamilyHandle;owned.set(family,{model,inspection,disposed:false});current(family);return family;
 },obligations(family:CommerceDerivedFamilyHandle){return current(family).inspection.descriptor.obligations;},inspect(family:CommerceDerivedFamilyHandle){return current(family).inspection;},assertCurrent(family:CommerceDerivedFamilyHandle){current(family);},dispose(family:CommerceDerivedFamilyHandle){current(family).disposed=true;},modelOwner(){return models;}});owners.add(owner);return owner;
}
