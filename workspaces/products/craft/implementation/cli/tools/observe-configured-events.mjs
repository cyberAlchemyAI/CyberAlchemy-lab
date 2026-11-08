import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';

// Independent native AST observation. Expected meaning comes from authored
// node files, not execution of the generated module or import of its renderer.
const compilerRoot='/opt/node-toolchain/node_modules/typescript';
if(JSON.parse(fs.readFileSync(path.join(compilerRoot,'package.json'),'utf8')).version!=='7.0.2')throw Error('unselected compiler');
const {API}=await import(pathToFileURL(path.join(compilerRoot,'dist/api/sync/api.js')).href);
const {SyntaxKind:K}=await import(pathToFileURL(path.join(compilerRoot,'dist/ast/index.js')).href);
const [configPath,expectedPath]=process.argv.slice(2),expected=JSON.parse(fs.readFileSync(expectedPath,'utf8'));
const hash=s=>createHash('sha256').update(s).digest('hex');
const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
const compact=s=>s.replace(/\s+/g,''),text=n=>n?.getText(),q=JSON.stringify;
const eventSupport=source=>{
  const fields=[source.occurrence_id,...source.payload],scalars=new Set(fields.flatMap(field=>field.type_ref.kind==='reference'?[]:[field.type_ref.name]));
  const references=fields.some(field=>field.type_ref.kind==='reference');
  return `const eventFail = ():never => {throw new TypeError("EVENT_INPUT");};
const eventData = (value:unknown,allowed:readonly string[],required:readonly string[]):Record<string,PropertyDescriptor> => {
  if(!value||typeof value!=="object"||Array.isArray(value)||![Object.prototype,null].includes(Object.getPrototypeOf(value)))return eventFail();
  const d=Object.getOwnPropertyDescriptors(value);
  if(Reflect.ownKeys(d).some(k=>typeof k!=="string"||!allowed.includes(k))||Object.values(d).some(p=>!Object.hasOwn(p,"value")||!p.enumerable)||required.some(k=>!Object.hasOwn(d,k)))return eventFail();
  return d;
};
${scalars.has('string')?'const eventString = (v:unknown):string => typeof v==="string"?v:eventFail();\n':''}const eventText = (v:unknown):string => typeof v==="string"&&v.length>0?v:eventFail();
${scalars.has('boolean')?'const eventBoolean = (v:unknown):boolean => typeof v==="boolean"?v:eventFail();\n':''}${scalars.has('decimal')?'const eventDecimal = (v:unknown):number => typeof v==="number"&&Number.isFinite(v)?(Object.is(v,-0)?0:v):eventFail();\n':''}${scalars.has('integer')?`const eventInteger = (v:unknown):bigint => {
  let n:bigint;
  if(typeof v==="bigint")n=v;
  else if(typeof v==="number"&&Number.isSafeInteger(v))n=BigInt(v);
  else if(typeof v==="string"&&v.length<=20&&/^(0|-?[1-9][0-9]*)$/.exec(v)?.[0]===v)n=BigInt(v);
  else return eventFail();
  return n>=-9223372036854775808n&&n<=9223372036854775807n?n:eventFail();
};
`:''}${references?'type EventRef<S extends string> = string & {readonly __domainspecRef?:S};\n':''}`;
};
function frozen(n){
  if(n?.kind===K.StringLiteral)return n.text;
  if(n?.kind===K.NumericLiteral)return Number(n.text);
  if(n?.kind===K.TrueKeyword)return true;if(n?.kind===K.FalseKeyword)return false;if(n?.kind===K.NullKeyword)return null;
  if(n?.kind!==K.CallExpression||text(n.expression)!=='Object.freeze'||n.arguments.length!==1)throw Error('frozen literal');
  const value=n.arguments[0];
  if(value.kind===K.ArrayLiteralExpression)return value.elements.map(frozen);
  if(value.kind!==K.ObjectLiteralExpression)throw Error('literal object');
  const result=Object.create(null);
  for(const p of value.properties){
    if(p.kind!==K.PropertyAssignment||p.name.kind!==K.ComputedPropertyName||p.name.expression.kind!==K.StringLiteral||Object.hasOwn(result,p.name.expression.text))throw Error('literal member');
    result[p.name.expression.text]=frozen(p.initializer);
  }
  return result;
}
const errors=[],observations=[],api=new API({cwd:path.dirname(configPath)});
try{
  const snapshot=api.updateSnapshot({openProjects:[configPath]}),project=snapshot.getProject(configPath);
  if(!project)throw Error('missing project');
  const planned=expected.flatMap(e=>[e.relative_path,e.provider_path]).sort(),actual=JSON.parse(fs.readFileSync(configPath,'utf8')).files.slice().sort();
  if(canonical(planned)!==canonical(actual)||new Set(actual).size!==actual.length)throw Error('artifact set');
  for(const e of expected){try{
    const sourceBytes=fs.readFileSync(e.source_path,'utf8'),source=JSON.parse(sourceBytes).body;
    const providerPath=path.resolve(path.dirname(configPath),e.provider_path),wrapperPath=path.resolve(path.dirname(configPath),e.relative_path);
    const providerBytes=fs.readFileSync(providerPath,'utf8'),provider=project.program.getSourceFile(providerPath),wrapper=project.program.getSourceFile(wrapperPath);
    if(!provider||!wrapper||project.program.getSyntacticDiagnostics(providerPath).length||project.program.getSyntacticDiagnostics(wrapperPath).length)throw Error('syntax');
    const at=providerBytes.indexOf('export type EventInput');
    if(at<0||providerBytes.slice(0,at)!==eventSupport(source))throw Error('support perimeter');
    const own=provider.statements.filter(s=>s.pos>=at-1||s.getStart()>=at);
    if(own.length!==3||own[0].kind!==K.TypeAliasDeclaration||text(own[0].name)!=='EventInput'||own[1].kind!==K.TypeAliasDeclaration||text(own[1].name)!=='EventValue'||own[2].kind!==K.VariableStatement)throw Error('provider surface');
    const declarations=own[2].declarationList.declarations;
    if(declarations.length!==1||text(declarations[0].name)!=='make'||declarations[0].initializer.kind!==K.ArrowFunction)throw Error('constructor arrow');
    const fn=declarations[0].initializer,generated=source.occurred_at_policy==='generated';
    if(fn.parameters.length!==(generated?2:1)||compact(text(fn.parameters[0]))!=='input:EventInput'||generated&&compact(text(fn.parameters[1]))!=='clock:()=>string'||text(fn.type)!=='EventValue'||fn.modifiers?.length)throw Error('signature');
    const fields=[...source.payload].sort((a,b)=>a.field_id<b.field_id?-1:a.field_id>b.field_id?1:0),id=q(source.occurrence_id.field_id);
    const type=(f,input)=>f.type_ref.kind==='reference'?'EventRef<'+q(f.type_ref.selector)+'>':({integer:input?'bigint|number|string':'bigint',decimal:'number',boolean:'boolean',string:'string',timestamp:'string',uuid:'string'})[f.type_ref.name];
    const members=input=>fields.map(f=>'readonly '+q(f.field_id)+(f.required?'':'?')+':'+type(f,input)).join(';');
    const inputType='export type EventInput=Readonly<{occurrence:Readonly<{'+id+':'+type(source.occurrence_id,true)+'}>;'+(generated?'':'occurredAt:string;')+'payload:Readonly<{'+members(true)+'}>}>;';
    const outputType='export type EventValue=Readonly<{type:'+q(source.event_type)+';version:'+q(source.version)+';occurrence:Readonly<{'+id+':'+type(source.occurrence_id,false)+'}>;occurredAt:string;payload:Readonly<{'+members(false)+'}>}>;';
    if(compact(text(own[0]))!==compact(inputType)||compact(text(own[1]))!==compact(outputType))throw Error('native types');
    const normal=(f,root)=>{
      const name=f.type_ref.kind==='reference'?'eventText':({string:'eventString',boolean:'eventBoolean',integer:'eventInteger',decimal:'eventDecimal',uuid:'eventText',timestamp:'eventText'})[f.type_ref.name];
      return name+'('+root+'['+q(f.field_id)+']!.value)';
    };
    const top=generated?['occurrence','payload']:['occurrence','occurredAt','payload'];
    const assignments=fields.map(f=>{
      const member='['+q(f.field_id)+']:'+normal(f,'p');
      return f.required?member:'...(Object.hasOwn(p,'+q(f.field_id)+')?{'+member+'}:{})';
    }).join(',');
    const statements=[
      'const d=eventData(input,'+q(top)+','+q(top)+');',
      'const o=eventData(d["occurrence"]!.value,['+id+'],['+id+']);',
      'const p=eventData(d["payload"]!.value,'+q(fields.map(f=>f.field_id))+','+q(fields.filter(f=>f.required).map(f=>f.field_id))+');',
      'const occurrence=Object.freeze({['+id+']:'+normal(source.occurrence_id,'o')+'});',
      'const payload=Object.freeze({'+assignments+'});',
      ...(generated?['if(typeof clock!=="function")return eventFail();','const occurredAt=eventText(clock());']:['const occurredAt=eventText(d["occurredAt"]!.value);']),
      'return Object.freeze({type:'+q(source.event_type)+',version:'+q(source.version)+',occurrence,occurredAt,payload});',
    ];
    if(canonical(fn.body.statements.map(s=>compact(text(s))))!==canonical(statements.map(compact)))throw Error('construction meaning or effect');
    const ws=wrapper.statements;
    if(ws.length!==3||ws[0].kind!==K.ImportDeclaration||compact(text(ws[0]))!==compact('import {make} from '+q(e.provider_import)+';')||ws[1].kind!==K.ExportDeclaration||compact(text(ws[1]))!==compact('export type {EventInput,EventValue} from '+q(e.provider_import)+';')||ws[2].kind!==K.VariableStatement)throw Error('binding surface');
    const binding=ws[2].declarationList.declarations;
    if(binding.length!==1||text(binding[0].name)!==e.callable)throw Error('bound name');
    const outer=binding[0].initializer;
    if(outer.kind!==K.CallExpression||text(outer.expression)!=='Object.freeze'||outer.arguments.length!==1)throw Error('bound freeze');
    const assign=outer.arguments[0];
    if(assign.kind!==K.CallExpression||text(assign.expression)!=='Object.assign'||assign.arguments.length!==2||text(assign.arguments[0])!=='make')throw Error('bound callable');
    const holder=assign.arguments[1];
    if(holder.kind!==K.ObjectLiteralExpression||holder.properties.length!==1||text(holder.properties[0].name)!=='descriptor')throw Error('descriptor binding');
    const descriptor=frozen(holder.properties[0].initializer),{descriptor_sha256,...body}=descriptor;
    if(hash(canonical(body))!==descriptor_sha256||descriptor.provider.sha256!==hash(providerBytes))throw Error('binding digest');
    if(descriptor.source.sha256!==hash(sourceBytes)||descriptor.contract_sha256!==hash(canonical(source))||descriptor.selector!==e.selector)throw Error('source binding');
    for(const key of ['event_type','version','occurrence_id','occurred_at_policy','payload'])if(canonical(descriptor[key])!==canonical(source[key]))throw Error('source semantics');
    if(descriptor.return_semantics!=='immutable-occurrence-data'||descriptor.effect_contract!==(generated?'explicit-clock-only':'none')||descriptor.publication!==false||descriptor.occurrence_registration!==false||descriptor.distributed_exactly_once_claim!==false||descriptor.primary_callable_count!==1)throw Error('claim boundary');
    const refs=[...new Set([source.occurrence_id,...source.payload].filter(f=>f.type_ref.kind==='reference').map(f=>f.type_ref.selector))].sort();
    if(canonical(descriptor.references.map(r=>r.selector))!==canonical(refs))throw Error('reference set');
    for(const ref of descriptor.references){
      const bytes=fs.readFileSync(e.reference_paths[ref.selector],'utf8'),node=JSON.parse(bytes);
      if(ref.source.sha256!==hash(bytes)||ref.body_sha256!==hash(canonical(node.body))||ref.kind!==node.kind||ref.semantics!=='reference-not-embedding')throw Error('reference binding');
    }
    observations.push({selector:e.selector,result:'pass',source_sha256:hash(providerBytes)});
  }catch(error){errors.push({selector:e.selector,reason:error.message});}}
  snapshot.dispose();
}finally{api.close();}
console.log(JSON.stringify({result:errors.length?'fail':'pass',observations,errors}));
if(errors.length)process.exitCode=1;
