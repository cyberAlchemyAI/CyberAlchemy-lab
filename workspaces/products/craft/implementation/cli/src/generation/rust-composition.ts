import {APPLICATION_PATHS, applicationArtifactPath, outputImport} from './output-layout.js';
import {mappingInputs} from '../typed-backend/declarative-function.js';
import type {DeclarativeFunctionContract,DeclarativeExpression as E} from '../typed-backend/declarative-function.js';
import {rustRuntime,rustMain,rustCargo} from './rust-function-runtime.js';
// The shared declarative compiler validates types and dependency cycles before this renderer runs.
const q=(s:string)=>'"'+[...s].map(c=>{if(c.codePointAt(0)!>=0xd800&&c.codePointAt(0)!<=0xdfff)throw Error('DS_RUST_COMPOSITION: unpaired surrogate');return c==='"'?'\\"':c==='\\'?'\\\\':c==='\n'?'\\n':c==='\r'?'\\r':c==='\t'?'\\t':c.codePointAt(0)!<32?`\\u{${c.codePointAt(0)!.toString(16)}}`:c;}).join('')+'"';
export function renderRustComposition(c:DeclarativeFunctionContract,bindings:any,model:any={},applicationId?:string):Record<string,string>{
 const lib=applicationId?applicationArtifactPath(`compositions/${applicationId}/src/lib.rs`):'';
 const nodes=new Map(c.nodes.map(n=>[n.id,n]));
 function expr(e:E,locals=new Set<string>()):string{
  // Validated Int literals span JavaScript's safe-integer range, which fits i64.
  if(e.op==='literal')return `json!(${typeof e.value==='string'?q(e.value):typeof e.value==='number'?`${e.value}i64`:e.value===null?'null':e.value})`;
  if(e.op==='path'){const h=e.path[0]!;const base=locals.has(h)?`v_${h}.clone()`:Object.hasOwn(c.roots,h)?`self.roots[${q(h)}].clone()`:`self.n_${h}()?`;return e.path.slice(1).reduce((s,k)=>`field(${s},${q(k)})`,base);}
  if(e.op!=='call'){
   const rows=expr(e.collection,locals),pred=expr(e.where,new Set([...locals,e.binding]));
   if(e.op==='exactly_one')return `{let rows=list(${rows})?;let mut count=0;for v_${e.binding} in rows {if boolean(${pred})? {count+=1;}}json!(count==1)}`;
   const stop=e.op==='exists'?'true':'false';return `{let rows=list(${rows})?;let mut answer=${e.op==='forall'};for v_${e.binding} in rows {if boolean(${pred})? == ${stop} {answer=${stop};break;}}json!(answer)}`;
  }
  const a=e.args.map(a=>expr(a,locals)),n=e.name;
  if(nodes.has(n)||Object.hasOwn(c.calculations,n))return `{${a.map((v,i)=>`let arg${i}=${v};`).join('')}self.${nodes.has(n)?'n':'c'}_${n}(${a.map((_,i)=>`arg${i}`).join(',')})?}`;
  if(n==='and'||n==='or')return `json!(boolean(${a[0]})? ${n==='and'?'&&':'||'} boolean(${a[1]})?)`;
  if(n==='not')return `json!(!boolean(${a[0]})?)`;
  if(n==='present')return `json!(!nullish(&(${a[0]})))`;
  if(n==='coalesce')return `{let v=${a[0]};if nullish(&v){${a[1]}}else{v}}`;
  if(n==='eq'||n==='ne')return `json!((${a[0]}) ${n==='eq'?'==':'!='} (${a[1]}))`;
  if(['lt','lte','gt','gte'].includes(n))return `json!(compare(${a[0]},${a[1]})? ${({lt:'<',lte:'<=',gt:'>',gte:'>='} as any)[n]} 0)`;
  if(n==='lower')return `json!(string(${a[0]})?.${c.portability?'to_ascii_lowercase':'to_lowercase'}())`;
  if(n==='uint64')return `json!(uint64(${a[0]})?)`;
  if(n==='optional_uint64')return `{let v=${a[0]};if nullish(&v){Value::Null}else{json!(uint64(v)?)}}`;
  if(n==='decimal')return `json!(decimal(string(${a[0]})?,${(e.args[1] as any).value})?)`;
  if(n==='format')return `json!(money(uint64(${a[0]})?,${(e.args[1] as any).value}))`;
  if(n==='text')return `json!(uint64(${a[0]})?.to_string())`;
  if(n==='count')return `json!(list(${a[0]})?.len())`;
  if(n==='one')return `one(${a[0]})?`;
  if(n==='column')return `Value::Array(list(${a[0]})?.into_iter().map(|v|field(v,${q((e.args[1] as any).value)})).collect())`;
  if(n==='distinct')return `distinct(${a[0]})?`;
  if(n==='sort')return `sorted(${a[0]})?`;
  throw Error('DS_RUST_COMPOSITION: unsupported operator '+n);
 }
 let methods='';
 for(const n of c.nodes){let body:string;const inputs=mappingInputs(n);
  if(n.kind==='Mapping')body=`let mut fields=serde_json::Map::new();${Object.entries(n.fields!).map(([k,v])=>`let value=${expr(v,new Set(inputs.map(p=>p.name)))};if !missing(&value){fields.insert(${q(k)}.into(),value);}`).join('\n')}Ok(Value::Object(fields))`;
  else if(n.kind==='Rule')body=`Ok(${expr(n.expression!)})`;
  else body=`let rows=list(${expr(n.source!)})?;self.emit(json!({"kind":"query-start","declaration":${q(n.id)},"total":rows.len()}));let mut selected=Vec::new();for (index,v_${n.binding}) in rows.into_iter().enumerate(){let accepted=boolean(${expr(n.where!,new Set([n.binding!]))})?;self.emit(json!({"kind":"query-row","declaration":${q(n.id)},"index":index,"accepted":accepted,"row":v_${n.binding}}));if accepted{selected.push(v_${n.binding});}}let mut out=Vec::new();for v_${n.binding} in selected{out.push(${expr(n.select!,new Set([n.binding!]))});}Ok(Value::Array(out))`;
  methods+=`fn n_${n.id}(&mut self${inputs.map(p=>`,v_${p.name}:Value`).join('')})->R {${inputs.length?'':`if let Some(v)=self.memo.get(${q(n.id)}){return Ok(v.clone());}`}self.emit(json!({"kind":"node-start","declaration":${q(n.id)},"node_kind":${q(n.kind)}}));let result=(||->R{${body}})();self.observed(${q(n.id)},${q(n.kind)},&result);${inputs.length?'':`if let Ok(v)=&result{self.memo.insert(${q(n.id)}.into(),v.clone());}`}result}\n`;
 }
 let modules=Object.keys(model.modules??{}).map(alias=>`#[path=${q(applicationId?outputImport(lib,`modules/${alias}/${APPLICATION_PATHS.rustLibrary}`):`../../../../modules/${alias}/rust/compositions/function/src/lib.rs`)}] mod import_${alias};\n`).join('');
 modules+=`async fn invoke_import(alias:&str,input:Value,env:&BTreeMap<String,String>,responses:Option<Vec<Value>>,local:bool,tracing:bool)->R {match alias {${Object.keys(model.modules??{}).map(alias=>`${q(alias)}=>Ok(import_${alias}::module_call(input,env,responses,local,tracing).await),`).join('')}_=>Err("FUNCTION_MODULE_REQUIRED".into())}}\n`;

 for(const [name,inputs]of Object.entries(c.calculations)){
  const b=bindings[name],[feature,id]=b.selector.split(':');
  modules+=`#[path=${q(applicationId?outputImport(lib,applicationArtifactPath(`src/domainspec/rust/${feature}/${id}.rs`)):`../../../src/domainspec/rust/${feature}/${id}.rs`)}] mod core_${name};\n`;
  methods+=`fn c_${name}(&mut self,${inputs.map((_,i)=>`a${i}:Value`).join(',')})->R {self.emit(json!({"kind":"node-start","declaration":${q(name)},"node_kind":"Calculation"}));let result=(||->R{let mut inputs=std::collections::BTreeMap::new();${inputs.map((v,i)=>`inputs.insert(${q(b.fields[v])}.into(),uint64(a${i})?);`).join('')}core_${name}::${id.replaceAll('-','_')}(&inputs).map(|n|json!(n)).map_err(calculation_error)})();self.observed(${q(name)},"Calculation",&result);result}\n`;
 }
 methods+=`fn binding_guard(&mut self,binding:&str)->Result<bool,String>{let result=(||->Result<bool,String>{match binding {${(c.bindings??[]).filter(b=>b.condition).map(b=>`${q(b.name)}=>boolean(${expr(b.condition!)}),`).join('')}_=>Err("FUNCTION_BINDING_REQUIRED".into())}})();self.memo.clear();result}\n`;
 methods+=`fn binding_input(&mut self,binding:&str)->R {let result=(||->R{match binding {${(c.bindings??[]).filter(b=>b.input).map(b=>`${q(b.name)}=>Ok(${expr({op:'path',path:[b.input!.mapping]})}),`).join('')}_=>Err("FUNCTION_BINDING_INPUT_REQUIRED".into())}})();self.memo.clear();result}\n`;
 const assertion=(a:any,i:number,phase:string)=>`let passed=boolean(${expr(a.condition)})?;self.emit(json!({"kind":"assertion","index":${i},"phase":${q(phase)},"code":${q(a.code)},"passed":passed}));if !passed{return Err(${q(a.code)}.into());}`;
 const inputOnly=(e:E):boolean=>e.op==='literal'||e.op==='path'&&e.path[0]==='input'||e.op==='call'&&!nodes.has(e.name)&&!Object.hasOwn(c.calculations,e.name)&&e.args.every(inputOnly);
 methods+=`fn precheck(&mut self)->Result<(),String>{${c.assertions.map((a,i)=>inputOnly(a.condition)?assertion(a,i,'input'):'').join('\n')}Ok(())}\n`;
 methods+=`fn execute(&mut self)->R {${c.assertions.map((a,i)=>assertion(a,i,'behavior')).join('\n')}let mut matches=Vec::new();${c.results.map((r,i)=>`let passed=boolean(${expr(r.condition)})?;self.emit(json!({"kind":"result-case","index":${i},"passed":passed}));if passed{matches.push(${i});}`).join('\n')}if matches.len()!=1{return Err("DS_RESULT_CARDINALITY".into());}self.emit(json!({"kind":"selected-case","index":matches[0]}));match matches[0]{${c.results.map((r,i)=>`${i}=>Ok(${expr(r.value)}),`).join('\n')}_=>unreachable!()}}`;
 if(applicationId){
  const runtime=applicationArtifactPath(`compositions/${applicationId}/runtime.rs`);
  let support=rustRuntime;
  for(const name of ['function.json','ontology.json','bindings.json','source.alch','composition.json'])support=support.replaceAll(`"../${name}"`,q(outputImport(runtime,applicationArtifactPath(`compositions/${applicationId}/${name}`))));
  support=support.replaceAll('include_bytes!("lib.rs")',`include_bytes!(${q(outputImport(runtime,lib))})`);
  return {'Cargo.toml':rustCargo,'src/lib.rs':`#![allow(non_snake_case,dead_code,unused_parens)]\n${modules}\ninclude!(${q(outputImport(lib,runtime))});\nimpl Context {${methods}}\n`,'runtime.rs':support,'src/main.rs':rustMain.replace('.join("manifest.json")','.join("../manifest.json")')};
 }
 return {'Cargo.toml':rustCargo,'src/lib.rs':`#![allow(non_snake_case,dead_code,unused_parens)]\n${modules}\n${rustRuntime}\nimpl Context {${methods}}\n`,'src/main.rs':rustMain};
}
