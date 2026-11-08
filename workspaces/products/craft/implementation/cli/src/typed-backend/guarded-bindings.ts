import {mappingInputs} from './declarative-function.js';
import type {DeclarativeFunctionContract as Contract,DeclarativeExpression as E} from './declarative-function.js';

/** Conservative availability proof over the already type-checked expression graph. */
export function validateGuardAvailability(c:Contract):void {
 if(!c.bindings)return;
 const nodes=new Map(c.nodes.map(n=>[n.id,n])),guards=new Map(c.bindings.filter(b=>b.condition).map(b=>[b.name,b.condition!]));
 const fail=(s:string):never=>{throw Error('DS_DECLARATIVE: '+s);};
 let budget=100000;
 const tick=()=>{if(--budget<0)fail('guard analysis limit');};
 const rule=(e:E):E=>{tick();if(e.op==='path'&&e.path.length===1&&nodes.get(e.path[0]!)?.kind==='Rule')return rule(nodes.get(e.path[0]!)!.expression!);return e;};
 const canonical=(v:any):string=>JSON.stringify(v,(_k,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.keys(x).sort().map(k=>[k,x[k]])):x);
 const key=(e:E,v:boolean)=>`${v}:${canonical(rule(e))}`;
 function facts(e:E,v:boolean):Set<string>{
  e=rule(e);const out=new Set([key(e,v)]);
  if(e.op==='call'&&e.name==='not')for(const x of facts(e.args[0]!,!v))out.add(x);
  if(e.op==='call'&&['and','or'].includes(e.name)){
   const a=facts(e.args[0]!,v),b=facts(e.args[1]!,v),union=e.name==='and'?v:!v;
   for(const x of a)if(union||b.has(x))out.add(x);if(union)for(const x of b)out.add(x);
  }
  return out;
 }
 function proven(e:E,v:boolean,known:Set<string>):boolean {
  e=rule(e);if(known.has(key(e,v)))return true;
  if(e.op==='literal')return e.value===v;
  if(e.op==='call'&&e.name==='not')return proven(e.args[0]!,!v,known);
  if(e.op==='call'&&['and','or'].includes(e.name)){
   const a=()=>proven(e.args[0]!,v,known),b=()=>proven(e.args[1]!,v,known);
   return (e.name==='and'?v:!v)?a()&&b():a()||b();
  }
  return false;
 }
 const assume=(known:Set<string>,e:E,v:boolean)=>new Set([...known,...facts(e,v)]);
 function walk(e:E,known:Set<string>,available:Set<string>,locals=new Set<string>()):void {
  tick();
  function declaration(id:string){
   const n=nodes.get(id);if(!n)return;
   if(n.kind==='Rule')walk(n.expression!,known,available);
   else if(n.kind==='Mapping')for(const field of Object.values(n.fields!))walk(field,known,available,new Set(mappingInputs(n).map(p=>p.name)));
   else {walk(n.source!,known,available);const inner=new Set([n.binding!]);walk(n.where!,known,available,inner);walk(n.select!,assume(known,n.where!,true),available,inner);}
  }
  if(e.op==='path'){
   const head=e.path[0]!;if(locals.has(head))return;
   if(Object.hasOwn(c.roots,head)){
    if(!available.has(head))fail('guard forward/cyclic binding dependency: '+head);
    const guard=guards.get(head);if(guard&&!proven(guard,true,known))fail('unguarded binding output: '+head);
   }else declaration(head);
  }else if(e.op==='call'){
   if(e.name==='and'||e.name==='or'){
    walk(e.args[0]!,known,available,locals);walk(e.args[1]!,assume(known,e.args[0]!,e.name==='and'),available,locals);
   }else {for(const a of e.args)walk(a,known,available,locals);declaration(e.name);}
  }else if(e.op!=='literal'){
   walk(e.collection,known,available,locals);walk(e.where,known,available,new Set([...locals,e.binding]));
  }
 }
 const available=new Set(['input']);
 for(const b of c.bindings){if(b.condition)walk(b.condition,new Set(),available);if(b.input)walk({op:"path",path:[b.input.mapping]},b.condition?assume(new Set(),b.condition,true):new Set(),available);available.add(b.name);}
 for(const a of c.assertions)walk(a.condition,new Set(),available);
 for(const r of c.results){walk(r.condition,new Set(),available);walk(r.value,assume(new Set(),r.condition,true),available);}
}
