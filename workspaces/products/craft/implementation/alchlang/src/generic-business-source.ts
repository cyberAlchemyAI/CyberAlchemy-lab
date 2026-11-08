/** Alch frontend admission using the established parser; Core reconstructs
 * independently before executable ownership. Open Questions: ../docs/GENERIC-APPLICATIONS.md. */
import {parseCommerceModuleSource} from './commerce-source-parser.js';
import {sourceFail} from './commerce-source-model.js';
import type {CommerceParsedModule,CommerceDeclarationSource,CommerceSourceSpan} from './commerce-source-model.js';
import type {GenericCapabilitySelectionV1,GenericCapabilityBindingV1,GenericCapabilityToolV1} from './generic-capability-data-v1.js';
import {GENERIC_NATIVE_VECTOR_TYPE_V1} from './generic-capability-data-v1.js';
export function parseGenericBusinessSource(text:string,relativePath:string,boundedValues=false,stateProposals=false,keyedQueries=false,atomicTransactions=false){
 const module=parseCommerceModuleSource(text,relativePath);
 for(const d of module.declarations)if(!['Rule','ValueObject','Operation','Mapping','Calculation','Policy',...(atomicTransactions?['FormalClaim']:[]),...(boundedValues?['Enum']:[]),...(boundedValues&&stateProposals?['StateMachine']:[]),...(boundedValues&&stateProposals&&keyedQueries?['Entity','Query','Entry']:[])].includes(d.kind)&&!(d.kind==='Interface'&&(d.interface_kind==='application-composition'||boundedValues&&d.interface_kind==='bounded-schema')))sourceFail('UnsupportedCapability',d.span,'declaration is outside the implemented composition capability set');
 return module;
}

/** Preliminary normalized selectors, never checked runtime authority. Core
 * independently reconstructs these relations from the original captured files.
 * The existing source/sidecar paths carry the identities across that handoff. */
export function lowerGenericCapabilitySelectors(modules:readonly CommerceParsedModule[],input:unknown,selectionPath:string){
 const fallback={path:selectionPath,start:0,end:0};
 const selection=input as GenericCapabilitySelectionV1;
 if(!selection||selection.schema_version!=='craft.generic-capability-selection/v1'||!Array.isArray(selection.bindings)||selection.bindings.length<1||selection.bindings.length>128)
  sourceFail('InvalidContract',fallback,'bounded capability-selection/v1 bindings required');
 const declarations=modules.flatMap(m=>m.declarations);
 const resolve=(name:unknown,at:CommerceSourceSpan,owner?:CommerceParsedModule):CommerceDeclarationSource=>{
  if(typeof name!=='string'||!name)sourceFail('UnknownReference',at,'explicit capability selector required');
  const imported=owner?.imports.find(i=>i.alias===name),qualified=String(name).includes('.')?name:imported?imported.module+'.'+imported.name:owner?owner.module+'.'+name:name;
  const matches=declarations.filter(d=>d.id===qualified||!owner&&!String(name).includes('.')&&d.local_name===name);
  if(matches.length!==1)sourceFail(matches.length?'DuplicateSymbol':'UnknownReference',at,`${matches.length?'ambiguous':'missing'} capability selector ${name}`);
  return matches[0]!;
 };
 const seen=new Set<string>();
 return Object.freeze(selection.bindings.map((binding:GenericCapabilityBindingV1)=>{
  if(!binding||!binding.contract)sourceFail('InvalidContract',fallback,'capability binding contract required');
  const declaration=resolve(binding.interface,fallback);
  if(declaration.kind!=='Interface'||declaration.interface_kind!=='bounded-schema')sourceFail('TypeMismatch',declaration.span,`capability selector ${binding.interface} requires an existing bounded-schema Interface`);
  if(binding.interface!==declaration.id)sourceFail('InvalidContract',declaration.span,`fully qualified capability selector required: ${declaration.id}`);
  if(seen.has(declaration.id))sourceFail('DuplicateSymbol',declaration.span,`ambiguous capability bindings for ${declaration.id}`);seen.add(declaration.id);
  const module=modules.find(m=>m.path===declaration.span.path)!;
  const exposed=declaration.exposes.map(name=>resolve(name,declaration.span,module).id);
  const value=(selector:string)=>{
   const d=resolve(selector,declaration.span,module);
   if(selector!==d.id||d.kind!=='ValueObject'||!exposed.includes(d.id))sourceFail('TypeMismatch',declaration.span,`capability value selector ${selector} must be a fully qualified exposed business value of ${declaration.id} (ValueObject signature required)`);
   return d.id;
  };
  if(binding.contract.kind==='agent-run/v1'&&(!Array.isArray(binding.contract.tools)||binding.contract.tools.length>32))sourceFail('InvalidContract',declaration.span,'bounded explicit agent tools required');
  const tools=binding.contract.kind==='agent-run/v1'?binding.contract.tools.map((tool:GenericCapabilityToolV1)=>{
   if(!tool||typeof tool!=='object')sourceFail('InvalidContract',declaration.span,'explicit tool selectors required');
   const entry=resolve(tool.entry,declaration.span),query=resolve(tool.query,declaration.span);
   if(entry.kind!=='Entry'||query.kind!=='Query')sourceFail('TypeMismatch',declaration.span,`tool ${tool.name} requires existing Entry and Query selectors`);
   if(tool.entry!==entry.id||tool.query!==query.id)sourceFail('InvalidContract',declaration.span,`tool ${tool.name} requires fully qualified Entry and Query selectors`);
   return Object.freeze({name:tool.name,entry:entry.id,query:query.id,argument_codec:tool.argument_codec,result_codec:tool.result_codec});
  }):[];
  const nativeVector=binding.contract.kind==='inference/v1'&&binding.contract.operation==='vector.embed'&&binding.contract.result_type===GENERIC_NATIVE_VECTOR_TYPE_V1;
  return Object.freeze({id:binding.id,interface:declaration.id,input_type:value(binding.contract.input_type),result_type:nativeVector?GENERIC_NATIVE_VECTOR_TYPE_V1:value(binding.contract.result_type),contract:binding.contract.kind,operation:binding.contract.operation,realization_ref:binding.realization_ref,tools:Object.freeze(tools),source_span:declaration.span});
 }));
}
