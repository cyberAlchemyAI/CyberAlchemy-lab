import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {validStructuredRuleSupport} from '/structured-rule-support-observer.mjs';
const compilerRoot='/opt/node-toolchain/node_modules/typescript';
const version=JSON.parse(fs.readFileSync(path.join(compilerRoot,'package.json'),'utf8')).version;
if(version!=='7.0.2')throw Error('unselected native compiler');
const {API}=await import(pathToFileURL(path.join(compilerRoot,'dist/api/sync/api.js')).href);
const {SyntaxKind:K}=await import(pathToFileURL(path.join(compilerRoot,'dist/ast/index.js')).href);
const [configPath,expectedPath]=process.argv.slice(2),expected=JSON.parse(fs.readFileSync(expectedPath,'utf8')),files=JSON.parse(fs.readFileSync(configPath,'utf8')).files,errors=[],observations=[];
const text=n=>n?.getText(),compact=s=>s?.replace(/\s+/g,''),exported=n=>n.modifiers?.some(m=>m.kind===K.ExportKeyword),hash=s=>createHash('sha256').update(s).digest('hex');
const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a<b?-1:a>b?1:0)):x);
if(JSON.stringify([...files].sort())!==JSON.stringify(expected.map(e=>e.path).sort())||new Set(files).size!==files.length)errors.push('artifact-set');
const supportNames=new Set(['rulePart','ruleData','ruleString','ruleBool','ruleUInt64','ruleOptional','ruleSequence','ruleToSet','ruleSum']);
function literal(n){
 if(n?.kind===K.StringLiteral)return n.text;
 if(n?.kind===K.NumericLiteral)return Number(n.text);
 if(n?.kind===K.TrueKeyword)return true;if(n?.kind===K.FalseKeyword)return false;if(n?.kind===K.NullKeyword)return null;
 if(n?.kind!==K.CallExpression||text(n.expression)!=='Object.freeze'||n.arguments?.length!==1)throw Error('binding-literal');
 const arg=n.arguments[0];
 if(arg.kind===K.ArrayLiteralExpression)return arg.elements.map(literal);
 if(arg.kind!==K.ObjectLiteralExpression)throw Error('binding-object');
 const object=Object.create(null);
 for(const p of arg.properties){
  if(p.kind!==K.PropertyAssignment||p.name.kind!==K.ComputedPropertyName||p.name.expression.kind!==K.StringLiteral||Object.hasOwn(object,p.name.expression.text))throw Error('binding-property');
  object[p.name.expression.text]=literal(p.initializer);
 }
 return object;
}
const api=new API({cwd:path.dirname(configPath)});
try{
 const snapshot=api.updateSnapshot({openProjects:[configPath]}),project=snapshot.getProject(configPath);if(!project)throw Error('missing project');
 for(const e of expected){
  const file=path.resolve(path.dirname(configPath),e.path),source=project.program.getSourceFile(file);if(!source){errors.push('missing-source');continue;}
  for(const d of project.program.getSyntacticDiagnostics(file))errors.push('syntax:'+d.code);
  const imports=[],exports=[];let arrow,exportVariable;
  for(const s of source.statements){
   if(s.kind===K.ImportDeclaration){
    const clause=s.importClause;if(!clause?.namedBindings?.elements||clause.name||clause.isTypeOnly)errors.push('import-form');
    for(const b of clause?.namedBindings?.elements??[])imports.push({path:s.moduleSpecifier.text,symbol:text(b.propertyName??b.name),local:text(b.name)});
   }else if(s.kind===K.VariableStatement&&exported(s)){
    for(const d of s.declarationList.declarations){exports.push(text(d.name));arrow=d.initializer;exportVariable=d;}
   }else if(s.kind===K.VariableStatement){for(const d of s.declarationList.declarations)if(!supportNames.has(text(d.name))&&!/^R[0-9]+Value$/.test(text(d.name)))errors.push('unplanned-top-level');}
   else if(s.kind!==K.TypeAliasDeclaration)errors.push('top-level');
  }
  if(JSON.stringify(imports)!==JSON.stringify(e.imports)||JSON.stringify(exports)!==JSON.stringify([e.callable]))errors.push('imports-or-exports');
  if(e.kind==='binding'){
   try{
    if(source.statements.length!==2||arrow.kind!==K.CallExpression||text(arrow.expression)!=='Object.freeze'||arrow.arguments.length!==1)throw Error('bound-form');
    const assign=arrow.arguments[0];
    if(assign.kind!==K.CallExpression||text(assign.expression)!=='Object.assign'||assign.arguments.length!==2||text(assign.arguments[0])!=='select')throw Error('bound-callable');
    const wrapper=assign.arguments[1];
    if(wrapper.kind!==K.ObjectLiteralExpression||wrapper.properties.length!==1||text(wrapper.properties[0].name)!=='descriptor')throw Error('descriptor-form');
    const descriptor=literal(wrapper.properties[0].initializer),{descriptor_sha256,...body}=descriptor;
    if(descriptor_sha256!==hash(canonical(body)))throw Error('descriptor-digest');
    const providerFile=path.resolve(path.dirname(file),e.imports[0].path.replace(/\.js$/,'.ts'));
    if(descriptor.provider.sha256!==hash(fs.readFileSync(providerFile,'utf8')))throw Error('provider-digest');
    if(descriptor.return_semantics!=='strategy'||descriptor.effect_contract!=='none'||descriptor.dependency_contract!=='explicit-inputs-only')throw Error('descriptor-semantics');
    if(descriptor.strategy_set_sha256!==hash(canonical(descriptor.catalogue)))throw Error('catalogue-digest');
    if(canonical(descriptor.catalogue.map(c=>({selector:c.selector,kind:c.kind,sha256:c.source.sha256,body_sha256:c.body_sha256})))!==canonical(e.catalogue))throw Error('current-catalogue');
    if(descriptor.contract_sha256!==e.contract_sha256)throw Error('source-contract');
    for(const d of descriptor.rule_dependencies)if(hash(fs.readFileSync(path.resolve(path.dirname(configPath),d.path),'utf8'))!==d.sha256)throw Error('Rule-provider-digest');
   }catch(error){errors.push(error.message);}
   observations.push({path:e.path,kind:e.kind});continue;
  }
  const raw=fs.readFileSync(file,'utf8');
  if(!validStructuredRuleSupport(raw))errors.push('support-drift');
  if(arrow?.kind!==K.ArrowFunction||arrow.parameters?.length!==1)errors.push('arrow-form');
  if(e.kind==='policy'&&compact(text(arrow.type))!==e.targets.map(JSON.stringify).join('|'))errors.push('strategy-return-type');
  if(e.kind==='rule'&&arrow.type?.kind!==K.BooleanKeyword)errors.push('Rule-return-type');
  const statements=arrow?.body?.statements??[],locals=new Map(statements.filter(s=>s.kind===K.VariableStatement).flatMap(s=>s.declarationList.declarations).map(d=>[text(d.name),d]));
  if(compact(text(locals.get('d')?.initializer))!==compact('ruleData(parameters,'+JSON.stringify(e.inputs)+')'))errors.push('input-perimeter');
  if(compact(text(statements[1]))!==compact('if(Object.keys(d).length!=='+e.inputs.length+')throw new TypeError('+JSON.stringify(e.kind==='policy'?'POLICY_INPUT':'RULE_INPUT')+');')&&compact(text(statements[1]))!==compact("if(Object.keys(d).length!=="+e.inputs.length+")throw new TypeError('RULE_INPUT');"))errors.push('required-inputs');
  for(const[i,name]of e.inputs.entries())if(!new RegExp('^(?:R[0-9]+Value|ruleString|ruleBool|ruleUInt64)\\.normalize\\(d\\['+JSON.stringify(name)+'\\]!\\.value\\)$').test(compact(text(locals.get('p'+i)?.initializer))))errors.push('parameter-binding');
  if(e.kind==='policy'){
   if(statements.length!==3+e.inputs.length+e.cases.length)errors.push('statement-perimeter');
   for(const[i,c]of e.cases.entries())if(compact(text(statements[2+e.inputs.length+i]))!==compact('if('+c.expression+')return '+JSON.stringify(c.target)+';'))errors.push('ordered-Rule-binding');
   if(compact(text(statements.at(-1)))!==compact('return '+JSON.stringify(e.default_target)+';'))errors.push('default-target');
  }else if(e.return_expression!==undefined&&compact(text(statements.at(-1)?.expression))!==compact(e.return_expression))errors.push('Rule-expression');
  const visit=n=>{
   if([K.ClassDeclaration,K.ClassExpression,K.FunctionDeclaration,K.FunctionExpression,K.ImportKeyword,K.AwaitExpression,K.AnyKeyword].includes(n.kind))errors.push('executable-form');
   if(n.kind===K.Identifier&&['globalThis','process','Date','Math','Promise','fetch','require','eval','Function','setTimeout','setInterval','queueMicrotask','WebSocket'].includes(text(n)))errors.push('ambient-or-dynamic');
   n.forEachChild(visit);
  };visit(source);
  const closed=(n,dependencies)=>{
   if(n.kind===K.CallExpression){
    const callee=text(n.expression),arrayMethod=n.expression.kind===K.PropertyAccessExpression&&['map','some','filter'].includes(text(n.expression.name));
    if(!arrayMethod&&!dependencies.includes(callee)&&!/^(?:rule(?:Part|Data|Optional|Sequence|Sum|ToSet)|(?:R[0-9]+Value|ruleString|ruleBool|ruleUInt64)\.(?:normalize|key)|Object\.(?:freeze|hasOwn|keys))$/.test(callee))errors.push('call-perimeter');
    if(callee==='Object.freeze'&&![K.ObjectLiteralExpression,K.ArrayLiteralExpression,K.CallExpression].includes(n.arguments?.[0]?.kind))errors.push('freeze-alias');
   }
   if(n.kind===K.BinaryExpression&&n.operatorToken?.kind===K.EqualsToken)errors.push('write-perimeter');
   if(n.kind===K.NewExpression&&text(n.expression)!=='TypeError')errors.push('allocation-perimeter');
   n.forEachChild(c=>closed(c,dependencies));
  };
  for(const s of source.statements)if(s.kind===K.VariableStatement&&!s.declarationList.declarations.some(d=>supportNames.has(text(d.name))))closed(s,exported(s)?e.imports.map(i=>i.local):[]);
  observations.push({path:e.path,kind:e.kind,inputs:e.inputs});
 }
 snapshot.dispose();
}finally{api.close();}
console.log(JSON.stringify({schema_version:'domainspec.policy-observation/v1-candidate',result:errors.length?'fail':'pass',errors,observations,typescript:version,authority_effect:'none'}));
if(errors.length)process.exitCode=1;
