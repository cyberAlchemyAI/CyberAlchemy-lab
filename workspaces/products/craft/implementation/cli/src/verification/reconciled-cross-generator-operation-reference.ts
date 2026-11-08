import type {CompiledProjectGraph} from '../input/project-model.js';
import type {ReconciledProjectPlan} from '../generation/reconciled-project.js';
import type {TypedType} from '../typed-operation/contracts.js';
import type {FactRecipe} from './reconciled-rule-facts.js';
import {canonicalJson} from '../input/source-manifest.js';
import {createOperationBinding} from './reconciled-operation-binding.js';
import {createEffectfulOperationReference,type OperationEffectFixture} from './reconciled-operation-effect-reference.js';
import {captureOperationRecipe,operationReferenceEvent,operationReferenceFields} from './reconciled-operation-values.js';
import {OperationReferenceUnsupported,type OperationFixtureMode} from './reconciled-operation-reference.js';
import {assertCrossGeneratorOperationSurface,type CrossGeneratorOperationSurface} from './reconciled-cross-generator-operation-surface.js';

export interface OperationProtocolCall {
 readonly provider:string;readonly method:string;readonly instance:number|null;readonly arity:number;
 readonly arguments:unknown;readonly result:unknown;readonly input_changed:false;
}
const fail=(message:string):never=>{throw new OperationReferenceUnsupported('OPERATION_PROTOCOL:'+message);};

/** Direct source semantics only. No renderer or generated body is an expected-answer oracle. */
export function createOperationProtocolReference(graph:CompiledProjectGraph,plan:ReconciledProjectPlan,surface:CrossGeneratorOperationSurface,selector:string){
 assertCrossGeneratorOperationSurface(surface);
 if(surface.project_plan_sha256!==plan.plan_sha256)fail('foreign surface');
 const row=surface.rows.find(r=>r.selector===selector)??fail('missing source Operation');
 const node=graph.nodes.find(n=>n.selector===selector)??fail('missing node');
 const binding=createOperationBinding(node,graph,plan),oracle=createEffectfulOperationReference(graph,plan,binding.action),action=binding.action,b=action.bindings;
 if(binding.action.action_sha256!==row.action_sha256)fail('foreign action');
 const instances=new Map(row.initialization.map((i,index)=>[i.selector,index]));
 const initialization=row.initialization.map((i,index)=>({provider:i.selector,method:'factory',instance:index,arity:0,arguments:['array',[]],result:{instance:index,frozen:true,extensions:[]},input_changed:false}));
 const expected=(id:string,recipe:FactRecipe,fixture:OperationEffectFixture,mode:OperationFixtureMode='committed')=>{
  const semantic=oracle.expected(recipe,fixture,mode),calls:OperationProtocolCall[]=[],owned=new WeakMap<object,string>(),clocks=new WeakMap<object,string>(),plain=new Map<string,object>();
  const wire=(v:any,depth=0):any=>{
   if(depth>64)fail('value depth');
   if(v!==null&&(typeof v==='object'||typeof v==='function')){
    const clock=clocks.get(v);if(clock!==undefined)return ['clock',clock];
    const token=owned.get(v);if(token!==undefined)return ['owned',token];
   }
   if(v===null)return ['null'];
   if(typeof v==='bigint')return ['bigint',String(v)];
   if(typeof v==='string'||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v))return [typeof v,v];
   if(Array.isArray(v))return ['array',v.map(x=>wire(x,depth+1))];
   if(!v||typeof v!=='object')fail('active value');
   return ['record',Object.keys(v).sort().map(k=>[k,wire(v[k],depth+1)])];
  };
  const emit=(provider:string,method:string,args:any[],value:any,instance:number|null=null,error?:{name:string;message:string})=>{
   if(calls.length>=65536)fail('call capacity');
   calls.push({provider,method,instance,arity:args.length,arguments:wire(args),result:error?{kind:'error',...error}:{kind:'value',value:wire(value)},input_changed:false});
  };
  const result=()=>({calls,semantic});
  const own=(type:TypedType,v:any,depth=0):any=>{
   if(depth>64)fail('owned depth');
   if(type.kind==='scalar')return v;
   if(type.kind==='optional')return v===null?null:own(type.element,v,depth+1);
   if(type.kind==='list'||type.kind==='set')return v.map((x:any)=>own(type.element,x,depth+1));
   if(type.kind==='sum'){
    const variant=type.variants.find(x=>x.name===v.variant)??fail('source variant');
    return {variant:v.variant,...(variant.payload?{payload:own(variant.payload,v.payload,depth+1)}:{})};
   }
   const d=oracle.values.get(type),provider=type.selector;
   if(d.kind==='Enum'){
    const sum=d.variants.some((v:any)=>v.payload!==null),input=sum?own({kind:'sum',variants:d.variants},v,depth+1):v.variant;
    const token=sum?'owned:'+id+':'+calls.length:'enum:'+canonicalJson([provider,v.variant]);
    let value=plain.get(token);if(!value){value={};owned.set(value,token);if(!sum)plain.set(token,value);}
    emit(provider,sum?'create':'fromVariant',[input],{value,data:sum?input:{variant:v.variant},owned:true,frozen:true});
    return value;
   }
   const input=Object.fromEntries(d.properties.map(p=>[p.name,own(p.type as TypedType,v[p.name],depth+1)]));
   const factory=plan.selection.factories.find(f=>f.selector===provider)??fail('missing factory');
   const failure:string[]=[];
   for(const validator of factory.base_validators){
    const rule=oracle.facts.reference.rules.get(validator.rule)??fail('missing Rule');
    const args=new Map(validator.arguments.map(a=>{
     let current=v;for(const key of a.path??[a.field!])current=current[key];
     return [a.parameter,{type:rule.parameters.find(p=>p.name===a.parameter)!.type,value:current}] as const;
    }));
    if(!oracle.facts.reference.evaluate(validator.rule,args)){failure.push('RULE_FAIL:'+validator.rule);break;}
   }
   const instance=instances.get(provider)??fail('missing factory instance'),value=failure.length?null:{};
   if(value)owned.set(value,'owned:'+id+':'+calls.length);
   emit(provider,'create',[input],{ok:failure.length===0,value,fields:failure.length?null:input,failure_codes:failure,owned:failure.length===0,frozen:true},instance);
   if(failure.length)throw new TypeError('OPERATION_VALUE:'+failure.join(','));
   return value;
  };
  let captured:any,scope:Map<string,{type:TypedType;value:any}>;
  try{
   captured=captureOperationRecipe(recipe);
   operationReferenceFields(captured,[...b.inputs.map(p=>p.name),...b.events.map(e=>e.parameter)]);
   scope=new Map(b.inputs.map(p=>[p.name,{type:p.type,value:oracle.values.normalize(p.type,captured[p.name])}]));
  }catch(e){if(e instanceof OperationReferenceUnsupported)throw e;return result();}
  if(action.events.some(e=>e.contract.occurred_at_policy==='generated'&&(!fixture.clocks.some(c=>c.slot===e.slot)||fixture.clocks.find(c=>c.slot===e.slot)!.mode==='missing'))||mode==='begin-throw')return result();
  try{
   for(const read of action.reads){
    const key=oracle.values.normalize(read.identity.type,oracle.values.value(read.key,scope).value),row=fixture.reads.find(r=>r.slot===read.slot)??fail('read fixture');
    if(row.throws)return result();const raw=captureOperationRecipe(row.value,'read');if(raw===null)return result();
    const value=oracle.values.normalize({kind:'named',selector:read.target},raw);
    if(oracle.values.key(read.identity.type,key)!==oracle.values.key(read.identity.type,value[read.identity.name]))return result();
    scope.set(read.parameter,{type:{kind:'named',selector:read.target},value});
   }
   for(const guard of b.guards){
    const args=Object.fromEntries(guard.arguments.map(a=>[a.parameter,oracle.values.value(a.value,scope).value]));
    const accepted=oracle.facts.reference.guard(guard,scope);emit(guard.selector,'guard',[args],accepted);
    if(!accepted)return result();
   }
   for(const write of action.writes){
    const type:TypedType={kind:'named',selector:write.target};
    own(type,oracle.values.normalize(type,oracle.values.value(write.value,scope).value));
   }
   for(const event of action.events){
    const generated=event.contract.occurred_at_policy==='generated',clock={},args=[captured[event.parameter],...(generated?[clock]:[])];
    if(generated)clocks.set(clock,event.slot);
    try{
     const value=operationReferenceEvent(event.contract,captured[event.parameter],()=>{
      const c=fixture.clocks.find(c=>c.slot===event.slot)??fail('clock fixture');
      if(c.mode==='throw')throw Error('fixture-clock');return c.value;
     },oracle.eventReferenceScalar);
     emit(event.target,'event',args,{value,frozen:true});
    }catch(e){
     if(e instanceof OperationReferenceUnsupported)throw e;
     emit(event.target,'event',args,null,null,{name:e instanceof TypeError?'TypeError':'Error',message:e instanceof TypeError?'EVENT_INPUT':'fixture-clock'});return result();
    }
   }
   own(b.result.type,oracle.values.normalize(b.result.type,oracle.values.value(b.result.value,scope).value));
  }catch(e){if(e instanceof OperationReferenceUnsupported)throw e;if(!(e instanceof TypeError))throw e;}
  return result();
 };
 return {binding,initialization,expected};
}
