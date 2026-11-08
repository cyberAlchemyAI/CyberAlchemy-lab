import type {FieldReferenceModel} from '../input/field-reference-model.js';
import type {TypedType} from '../typed-operation/contracts.js';

// Converts already normalized, owned factory fields to pure Rule input views.
// Static source only; never reads raw caller snapshots or executes invariants.
// Scope/open questions: STRUCTURED-RULE-VALUES.md.
export function ruleFactView(type:TypedType,source:string,model:FieldReferenceModel):string {
  const declarations=new Map(model.declarations.map(d=>[d.selector,d]));
  let next=0,visits=0;
  const view=(type:TypedType,code:string):string=>{
    if(++visits>10000)throw new Error('DS_CONFIGURED_FACTORY:fact view source limit');
    if(type.kind==='scalar')return code;
    if(type.kind==='reference')return code;
    if(type.kind==='optional')return '('+code+' === null ? null : '+view(type.element,code)+')';
    if(type.kind==='list'||type.kind==='set'){const item='fact'+next++;return 'Object.freeze('+code+'.map('+item+'=>'+view(type.element,item)+'))';}
    if(type.kind==='named'){
      const d=declarations.get(type.selector);if(!d)throw new Error('DS_CONFIGURED_FACTORY:missing fact declaration');
      if(d.kind==='Enum')return view({kind:'sum',variants:d.contract.variants},code);
      return 'Object.freeze({'+d.contract.properties.map(p=>'['+JSON.stringify(p.name)+']:'+view(p.type,code+'.fields['+JSON.stringify(p.name)+']')).join(',')+'})';
    }
    return '('+type.variants.map(v=>code+'.variant === '+JSON.stringify(v.name)+' ? Object.freeze({variant:'+JSON.stringify(v.name)+(v.payload?',payload:'+view(v.payload,code+'.payload'):'')+'}) : ').join('')+"(()=>{throw new TypeError('INVALID_RULE_FACT');})())";
  };
  return view(type,source);
}
