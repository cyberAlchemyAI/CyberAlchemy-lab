import path from 'node:path';
import type {TypedType} from '../typed-operation/contracts.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import type {planConfiguredFactories} from './configured-factories.js';
import type {createStructuredValueRenderer} from './configured-value-types.js';
import {canonicalJson} from '../input/source-manifest.js';

/** Static raw-fact to owned-value adapters. No invariant is synthesized here:
 * the selected generated factories own validation and child ownership.
 */
export interface OperationValueProviders {
  readonly modules:readonly Pick<ReturnType<typeof planConfiguredFactories>['modules'][number],'selector'|'relative_path'|'callable'>[];
  readonly sum_modules?:readonly {selector:string;relative_path:string;name:string}[];
  readonly enum_components?:readonly {selector:string;relative_path:string;name:string}[];
}
export function createOperationOwnedRenderer(values:ReturnType<typeof createStructuredValueRenderer>,model:FieldReferenceModel|null,factories:OperationValueProviders,ownerPath:string){
  const q=JSON.stringify,rows:string[]=[],imports:string[]=[],cache=new Map<string,string>();let next=0;
  const relative=(target:string)=>{const p=path.posix.relative(path.posix.dirname(ownerPath),target).replace(/\.ts$/,'.js');return p.startsWith('.')?p:'./'+p;};
  const ensure=(type:TypedType):string=>{
    const key=canonicalJson(type),prior=cache.get(key);if(prior)return prior;
    const name='own'+next++;cache.set(key,name);const native=values.ensure(type).native;
    let expression:string;
    if(type.kind==='scalar')expression='v';
    else if(type.kind==='optional')expression='v===null?null:'+ensure(type.element)+'(v)';
    else if(type.kind==='list'||type.kind==='set')expression='Object.freeze(v.map(x=>'+ensure(type.element)+'(x)))';
    else if(type.kind==='sum')expression=type.variants.map(v=>'v.variant==='+q(v.name)+'?Object.freeze({variant:'+q(v.name)+' as const'+(v.payload?',payload:'+ensure(v.payload)+'(v.payload)':'')+'}):').join('')+'(()=>{throw new TypeError("OPERATION_VALUE");})()';
    else {
      const declaration=model?.declarations.find(d=>d.selector===type.selector);if(!declaration)throw Error('DS_CONFIGURED_OPERATION:missing owned declaration');
      const local='ownedImport'+next++;
      if(declaration.kind==='Enum'){
        const sum=factories.sum_modules?.find(m=>m.selector===type.selector),plain=factories.enum_components?.find(m=>m.selector===type.selector),module=sum??plain;
        if(!module)throw Error('DS_CONFIGURED_OPERATION:missing Enum component');
        imports.push('import {'+module.name+'ValueComponent as '+local+'} from '+q(relative(module.relative_path))+';\n');
        expression=sum?local+'.create('+ensure({kind:'sum',variants:declaration.contract.variants})+'(v))':local+'.fromVariant(v.variant)';
      }else{
        const module=factories.modules.find(m=>m.selector===type.selector);if(!module)throw Error('DS_CONFIGURED_OPERATION:missing selected factory');
        imports.push('import {'+module.callable+' as '+local+'} from '+q(relative(module.relative_path))+';\n');
        const fields=declaration.contract.properties.map(p=>'['+q(p.name)+']:'+ensure(p.type)+'(v['+q(p.name)+'])').join(',');
        rows.push('const '+name+'Factory='+local+'();\nconst '+name+'=(v:'+native+')=>{const result='+name+'Factory.create({'+fields+'});if(!result.ok)throw new TypeError("OPERATION_VALUE:"+result.failure_codes.join(","));return result.value;};\n');
        return name;
      }
    }
    rows.push('const '+name+'=(v:'+native+')=>('+expression+');\n');return name;
  };
  return {ensure,imports:()=>imports.join(''),source:()=>rows.join('')};
}
