import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {validStructuredRuleSupport} from '/structured-rule-support-observer.mjs';
// Independent native observer. Expectations are authored from test contracts.
const compilerRoot='/opt/node-toolchain/node_modules/typescript';
const version=JSON.parse(fs.readFileSync(path.join(compilerRoot,'package.json'),'utf8')).version;
if(version!=='7.0.2')throw Error('unselected native compiler');
const {API}=await import(pathToFileURL(path.join(compilerRoot,'dist/api/sync/api.js')).href);
const {SyntaxKind:K}=await import(pathToFileURL(path.join(compilerRoot,'dist/ast/index.js')).href);
const [configPath,expectedPath]=process.argv.slice(2),expected=JSON.parse(fs.readFileSync(expectedPath,'utf8')),files=JSON.parse(fs.readFileSync(configPath,'utf8')).files,errors=[],observations=[];
const text=n=>n?.getText(),compact=s=>s?.replace(/\s+/g,''),exported=n=>n.modifiers?.some(m=>m.kind===K.ExportKeyword),hash=s=>createHash('sha256').update(s).digest('hex');
if(JSON.stringify([...files].sort())!==JSON.stringify(expected.map(e=>e.path).sort())||new Set(files).size!==files.length)errors.push('artifact-set');
const supportNames=new Set(['rulePart','ruleData','ruleString','ruleBool','ruleUInt64','ruleOptional','ruleSequence','ruleToSet','ruleSum']);
const api=new API({cwd:path.dirname(configPath)});
try{
 const snapshot=api.updateSnapshot({openProjects:[configPath]}),project=snapshot.getProject(configPath);if(!project)throw Error('missing native project');
 for(const e of expected){
  const file=path.resolve(path.dirname(configPath),e.path),source=project.program.getSourceFile(file);if(!source){errors.push('missing-source');continue;}
  const raw=fs.readFileSync(file,'utf8');
  if(!validStructuredRuleSupport(raw))errors.push('support-drift:'+e.path);
  for(const d of project.program.getSyntacticDiagnostics(file))errors.push('syntax:'+d.code);
  const exports=[];let arrow;
  for(const s of source.statements){
   if(s.kind===K.VariableStatement&&exported(s)){for(const d of s.declarationList.declarations){exports.push(text(d.name));arrow=d.initializer;}}
   else if(s.kind===K.VariableStatement){for(const d of s.declarationList.declarations)if(!supportNames.has(text(d.name))&&!/^R[0-9]+Value$/.test(text(d.name)))errors.push('unplanned-top-level');}
   else if(s.kind!==K.TypeAliasDeclaration)errors.push('top-level');
  }
  if(JSON.stringify(exports)!=='["map"]'||arrow?.kind!==K.ArrowFunction||arrow.parameters?.length!==1||!text(arrow.type)?.startsWith('Readonly<{'))errors.push('mapping-arrow');
  const statements=arrow?.body?.statements??[],locals=new Map(statements.filter(s=>s.kind===K.VariableStatement).flatMap(s=>s.declarationList.declarations).map(d=>[text(d.name),d]));
  if(statements.length!==3+e.inputs.length+e.fields.length+(e.source_fields?1:0)+(e.required?.length??0))errors.push('statement-perimeter');
  if(compact(text(locals.get('d')?.initializer))!==compact('ruleData(parameters,'+JSON.stringify(e.inputs)+')'))errors.push('input-perimeter');
  if(compact(text(statements[1]))!==compact('if(Object.keys(d).length!=='+e.inputs.length+')throw new TypeError("MAPPING_INPUT");'))errors.push('required-inputs');
  for(const [i,name]of e.inputs.entries()){
   const normalized=compact(text(locals.get('p'+i)?.initializer));
   const protocol=e.protocols[i];
   if(!new RegExp('^'+protocol+'\\.normalize\\(d\\['+JSON.stringify(name)+'\\]!\\.value\\)$').test(normalized))errors.push('parameter-binding');
  }
  if(e.source_fields&&compact(text(locals.get('s')?.initializer))!==compact('ruleData(d["source"]!.value,'+JSON.stringify(e.source_fields)+')'))errors.push('presence-perimeter');
  for(const [i,f]of e.fields.entries()){
   const expression=compact(text(locals.get('v'+i)?.initializer));
   if(f.expression!==undefined&&expression!==compact(f.expression)||f.pattern!==undefined&&!new RegExp(f.pattern).test(expression))errors.push('field-binding:'+f.name);
  }
  const projection='Object.freeze({'+e.fields.map((f,i)=>f.present?'...('+f.present+'?{['+JSON.stringify(f.name)+']:v'+i+'}:{})':'['+JSON.stringify(f.name)+']:v'+i).join(',')+'})';
  const last=statements.at(-1);if(last?.kind!==K.ReturnStatement||compact(text(last.expression))!==compact(projection))errors.push('target-projection');
  const guards=statements.filter(s=>s.kind===K.IfStatement).slice(1).map(s=>compact(text(s)));
  if(JSON.stringify(guards)!==JSON.stringify((e.required??[]).map(name=>compact('if(!Object.hasOwn(s,'+JSON.stringify(name)+'))throw new TypeError("MAPPING_REQUIRED_VALUE");'))))errors.push('missing-source-guard');
  const visit=n=>{
   if([K.ClassDeclaration,K.ClassExpression,K.FunctionDeclaration,K.FunctionExpression,K.ImportDeclaration,K.ImportKeyword,K.AwaitExpression,K.AnyKeyword].includes(n.kind))errors.push('executable-form');
   if(n.kind===K.Identifier&&['globalThis','process','Date','Math','Promise','fetch','require','eval','Function','setTimeout','setInterval','queueMicrotask','WebSocket'].includes(text(n)))errors.push('ambient-or-dynamic');
   n.forEachChild(visit);
  };visit(source);
  const closed=n=>{
   if(n.kind===K.CallExpression){
    const callee=text(n.expression),arrayMap=n.expression.kind===K.PropertyAccessExpression&&text(n.expression.name)==='map';
    if(!arrayMap&&!/^(?:rule(?:Part|Data|Optional|Sequence|Sum|ToSet)|(?:R[0-9]+Value|ruleString|ruleBool|ruleUInt64)\.(?:normalize|key)|Object\.(?:freeze|hasOwn|keys))$/.test(callee))errors.push('call-perimeter');
    if(callee==='Object.freeze'&&![K.ObjectLiteralExpression,K.ArrayLiteralExpression,K.CallExpression].includes(n.arguments?.[0]?.kind))errors.push('freeze-alias');
   }
   if(n.kind===K.BinaryExpression&&n.operatorToken?.kind===K.EqualsToken)errors.push('write-perimeter');
   if(n.kind===K.NewExpression&&text(n.expression)!=='TypeError')errors.push('allocation-perimeter');
   n.forEachChild(closed);
  };
  for(const s of source.statements)if(s.kind===K.VariableStatement&&!s.declarationList.declarations.some(d=>supportNames.has(text(d.name))))closed(s);
  observations.push({path:e.path,inputs:e.inputs,fields:e.fields.map(f=>f.name),return_semantics:'field-projection-not-construction'});
 }
 snapshot.dispose();
}finally{api.close();}
console.log(JSON.stringify({schema_version:'domainspec.mapping-observation/v1-candidate',result:errors.length?'fail':'pass',errors,observations,typescript:version,authority_effect:'none'}));
if(errors.length)process.exitCode=1;
