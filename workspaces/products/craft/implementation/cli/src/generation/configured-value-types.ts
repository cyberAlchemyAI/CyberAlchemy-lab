import type {TypedType} from '../typed-operation/contracts.js';
import type {FieldReferenceModel} from '../input/field-reference-model.js';
import {canonicalJson} from '../input/source-manifest.js';
import {renderStructuredRuleSupport,type StructuredRuleCapability} from './configured-rule-value-support.js';

// Shared static value specialization. Historical Rule names/bytes are preserved.
// Does not emit a runtime type-schema interpreter, factory or reference resolver.
const q=JSON.stringify;
export function createStructuredValueRenderer(model:FieldReferenceModel|null,fail:(message:string)=>never,lazyInputTypes=false){
  const declarations=new Map(model?.declarations.map(d=>[d.selector,d])??[]);
  const rows:string[]=[], types=new Map<string,{native:string;input:string;protocol:string}>(),capabilities=new Set<StructuredRuleCapability>();
  const requestedInputs=new Set<string>(),inputDefinitions=new Map<string,()=>string>();
  const declareInput=(name:string,render:()=>string):string=>{
    if(!lazyInputTypes)return "type "+name+"Input = "+render()+";\n";
    inputDefinitions.set(name,render);return "";
  };
  const inputSource=()=>{
    const emitted=new Map<string,string>();
    for(const name of requestedInputs){const render=inputDefinitions.get(name);if(render)emitted.set(name,"type "+name+"Input = "+render()+";\n");}
    return [...emitted.values()].join("");
  };
  const use=(capability:StructuredRuleCapability)=>{capabilities.add(capability);};
  const get=(s:string)=>declarations.get(s)??fail('missing checked declaration:'+s);
  const ensure=(type:TypedType):{native:string;input:string;protocol:string}=>{
    const id=canonicalJson(type),cached=types.get(id);if(cached)return cached;
    if(type.kind==='scalar'){
      const protocol='rule'+type.name;
      const row:{native:string;input:string;readonly protocol:string}={native:type.name==='UInt64'?'bigint':type.name==='Bool'?'boolean':'string',input:type.name==='UInt64'?'bigint|number|string':type.name==='Bool'?'boolean':'string',get protocol(){use(type.name);return protocol;}};
      types.set(id,row);return row;
    }
    if(type.kind==='reference'){
      const d=get(type.selector);if(d.kind!=='Entity')return fail('reference target must be an Entity:'+type.selector);
      const field=d.contract.properties.find(f=>f.name===type.projection[0]);
      if(!field?.identity)return fail('reference projection must select the Entity identity:'+type.selector+'#'+type.projection[0]);
      const child=ensure(field.type),row={native:child.native,input:child.input,protocol:child.protocol};types.set(id,row);return row;
    }
    // The checked field model rejects embedding cycles before source emission.
    if(type.kind==='named'){
      const d=get(type.selector);
      if(d.kind==='Enum'){
        const payload=ensure({kind:'sum',variants:d.contract.variants}),name='R'+types.size;
        const row={native:name,get input(){requestedInputs.add(name);return name+'Input';},protocol:name+'Value'};types.set(id,row);
        rows.push('type '+name+' = '+payload.native+';\n'+declareInput(name,()=>payload.input)+'const '+row.protocol+':RuleProtocol<'+name+'> = Object.freeze({normalize:'+payload.protocol+'.normalize,key:(value:'+name+'):string=>rulePart('+q(d.selector)+')+rulePart('+payload.protocol+'.key(value))});\n');return row;
      }
      const fields=[...d.contract.properties].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0),children=fields.map(f=>ensure(f.type)),name='R'+types.size;
      const row={native:name,get input(){requestedInputs.add(name);return name+'Input';},protocol:name+'Value'};types.set(id,row);
      const fieldTypes=(input:boolean)=>fields.map((f,i)=>'readonly '+q(f.name)+(input&&f.type.kind==='optional'?'?':'')+':'+(input?children[i]!.input:children[i]!.native)).join(';');
      const keys=d.kind==='Entity'?fields.filter(f=>f.identity):fields;
      rows.push('type '+name+' = Readonly<{'+fieldTypes(false)+'}>;\n'+declareInput(name,()=>'Readonly<{'+fieldTypes(true)+'}>')+'const '+row.protocol+':RuleProtocol<'+name+'> = Object.freeze({\n  normalize:(input:unknown):'+name+'=>{\n    const d=ruleData(input,'+q(fields.map(f=>f.name))+');\n    return Object.freeze({'+fields.map((f,i)=>'['+q(f.name)+']:'+children[i]!.protocol+'.normalize(Object.hasOwn(d,'+q(f.name)+')?d['+q(f.name)+']!.value:'+(f.type.kind==='optional'?'null':'undefined')+')').join(',')+'});\n  },key:(value:'+name+'):string=>rulePart('+q(d.kind)+')+rulePart('+q(d.selector)+')'+keys.map(f=>'+rulePart('+q(f.name)+')+rulePart('+ensure(f.type).protocol+'.key(value['+q(f.name)+']))').join('')+',\n});\n');return row;
    }
    if(type.kind==='sum'){
      use('sum');
      const variants=[...type.variants].sort((a,b)=>a.name<b.name?-1:a.name>b.name?1:0),children=variants.map(v=>v.payload?ensure(v.payload):null),name='R'+types.size;
      const row={native:name,get input(){requestedInputs.add(name);return name+'Input';},protocol:name+'Value'};types.set(id,row);
      const forms=(input:boolean)=>variants.map((v,i)=>'Readonly<{variant:'+q(v.name)+(children[i]?';payload:'+(input?children[i]!.input:children[i]!.native):'')+'}>').join('|');
      rows.push('type '+name+' = ('+forms(false)+');\n'+declareInput(name,()=>'('+forms(true)+')')+'const '+row.protocol+':RuleProtocol<'+name+'> = ruleSum(Object.freeze({'+variants.map((v,i)=>'['+q(v.name)+']:'+(children[i]?.protocol??'null')).join(',')+'}));\n');return row;
    }
    use(type.kind==='optional'?'optional':'sequence');
    const child=ensure(type.element),name='R'+types.size;
    const row={native:name,get input(){requestedInputs.add(name);return name+'Input';},protocol:name+'Value'};types.set(id,row);
    const form=(s:string)=>type.kind==='optional'?'('+s+')|null':'ReadonlyArray<'+s+'>';
    rows.push('type '+name+' = '+form(child.native)+';\n'+declareInput(name,()=>form(child.input))+'const '+row.protocol+':RuleProtocol<'+name+'> = '+(type.kind==='optional'?'ruleOptional('+child.protocol+')':'ruleSequence('+child.protocol+','+(type.kind==='set')+')')+';\n');return row;
  };
  // Pass the generated body to source(body) so JavaScript evaluates every
  // lazy protocol reference before the capability-derived support is emitted.
  return {ensure,get,use,source:(body='')=>renderStructuredRuleSupport(capabilities)+(lazyInputTypes?inputSource():'')+rows.join('')+body};
}
