import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {validStructuredRuleSupport} from '/structured-rule-support-observer.mjs';

// Independent native observer. Expected read/filter/output fields come from
// authored test contracts, never the generator's self-reported conformance.
const compilerRoot='/opt/node-toolchain/node_modules/typescript';
const version=JSON.parse(fs.readFileSync(path.join(compilerRoot,'package.json'),'utf8')).version;
if(version!=='7.0.2')throw new Error('unselected native compiler');
const {API}=await import(pathToFileURL(path.join(compilerRoot,'dist/api/sync/api.js')).href);
const {SyntaxKind:K}=await import(pathToFileURL(path.join(compilerRoot,'dist/ast/index.js')).href);
const [configPath,expectedPath]=process.argv.slice(2),expected=JSON.parse(fs.readFileSync(expectedPath,'utf8'));
const files=JSON.parse(fs.readFileSync(configPath,'utf8')).files,errors=[],observations=[];
const text=n=>n?.getText(),compact=s=>s?.replace(/\s+/g,''),exported=n=>n.modifiers?.some(m=>m.kind===K.ExportKeyword);
const hash=s=>createHash('sha256').update(s).digest('hex');
if(JSON.stringify([...files].sort())!==JSON.stringify(expected.map(e=>e.path).sort())||new Set(files).size!==files.length)errors.push('artifact-set');
const api=new API({cwd:path.dirname(configPath)});
try{
  const snapshot=api.updateSnapshot({openProjects:[configPath]}),project=snapshot.getProject(configPath);
  if(!project)throw new Error('native project missing');
  for(const e of expected){
    const file=path.resolve(path.dirname(configPath),e.path),source=project.program.getSourceFile(file);
    if(!source){errors.push('missing-source:'+e.path);continue;}
    const raw=fs.readFileSync(file,'utf8');
    if(!validStructuredRuleSupport(raw))errors.push('support-drift:'+e.path);
    const exports=[];let arrow;
    const supportNames=new Set(['rulePart','ruleData','ruleString','ruleBool','ruleUInt64','ruleOptional','ruleSequence','ruleToSet','ruleSum']);
    for(const d of project.program.getSyntacticDiagnostics(file))errors.push('syntax:'+d.code);
    for(const s of source.statements){
      if(s.kind===K.VariableStatement&&exported(s)){for(const d of s.declarationList.declarations){exports.push(text(d.name));arrow=d.initializer;}}
      else if(s.kind===K.VariableStatement){for(const d of s.declarationList.declarations)if(!supportNames.has(text(d.name))&&!/^R[0-9]+Value$/.test(text(d.name)))errors.push('unplanned-top-level:'+e.path);}
      else if(s.kind!==K.TypeAliasDeclaration)errors.push('top-level:'+e.path);
    }
    if(JSON.stringify(exports)!=='["query"]'||arrow?.kind!==K.ArrowFunction||arrow.parameters?.length!==2||!text(arrow.type)?.startsWith('ReadonlyArray<Readonly<{'))errors.push('read-model-arrow:'+e.path);
    const statements=arrow?.body?.statements??[];
    const wanted=5+e.inputs.length+(e.order_by?1:0)+(e.limit===null?0:1);
    if(statements.length!==wanted)errors.push('statement-perimeter:'+e.path);
    const declarations=statements.filter(s=>s.kind===K.VariableStatement).flatMap(s=>s.declarationList.declarations);
    const locals=new Map(declarations.map(d=>[text(d.name),d]));
    if(compact(text(locals.get('d')?.initializer))!==compact('ruleData(parameters,'+JSON.stringify(e.inputs)+')'))errors.push('parameter-perimeter:'+e.path);
    for(const [i,name] of e.inputs.entries())if(!text(locals.get('p'+i)?.initializer)?.endsWith('.normalize(d['+JSON.stringify(name)+']!.value)'))errors.push('parameter-binding:'+e.path);
    if(!/^R[0-9]+Value\.normalize\(rows\)$/.test(text(locals.get('snapshots')?.initializer)))errors.push('declared-read:'+e.path);
    const selection=locals.get('selected')?.initializer;
    if(text(selection?.expression)!=='snapshots.filter')errors.push('filter-target:'+e.path);
    const predicate=text(selection?.arguments?.[0]?.body);
    if(e.filter_expression!==undefined&&compact(predicate)!==compact(e.filter_expression))errors.push('filter-meaning:'+e.path);
    if(e.filter_pattern!==undefined&&!new RegExp(e.filter_pattern).test(compact(predicate)))errors.push('filter-meaning:'+e.path);
    const last=statements.at(-1),projection='Object.freeze(selected.map(row=>Object.freeze({'+e.projection.map(f=>'['+JSON.stringify(f)+']:row['+JSON.stringify(f)+']').join(',')+'})))';
    if(last?.kind!==K.ReturnStatement||compact(text(last.expression))!==compact(projection))errors.push('projection:'+e.path);
    const expressions=statements.filter(s=>s.kind===K.ExpressionStatement).map(s=>compact(text(s.expression)));
    const wantedExpressions=[];
    if(e.order_by){const {field,direction}=e.order_by;const atom=n=>e.order_type==='Bool'?'Number('+n+'['+JSON.stringify(field)+'])':n+'['+JSON.stringify(field)+']';const a=atom('a'),b=atom('b');wantedExpressions.push(compact('selected.sort((a,b)=>'+a+' < '+b+' ? '+(direction==='asc'?'-1':'1')+' : '+a+' > '+b+' ? '+(direction==='asc'?'1':'-1')+' : 0)'));}
    if(e.limit!==null)wantedExpressions.push('selected=selected.slice(0,'+e.limit+')');
    if(JSON.stringify(expressions)!==JSON.stringify(wantedExpressions))errors.push('ordering-limit:'+e.path);
    const visit=n=>{
      if([K.ClassDeclaration,K.ClassExpression,K.FunctionDeclaration,K.FunctionExpression,K.ImportDeclaration,K.ImportKeyword,K.AwaitExpression,K.AnyKeyword].includes(n.kind))errors.push('executable-form:'+e.path);
      if(n.kind===K.Identifier&&['globalThis','process','Date','Math','Promise','fetch','require','eval','Function','setTimeout','setInterval','queueMicrotask','WebSocket'].includes(text(n)))errors.push('ambient-or-dynamic:'+e.path);
      n.forEachChild(visit);
    };
    visit(source);
    // Beyond the separately pinned shared support, accept only the emitted
    // pure normalizer and Query call perimeter. A generic Object call or a
    // new top-level variable is not evidence of an allowed dependency.
    const closed=n=>{
      if(n.kind===K.CallExpression){
        const callee=text(n.expression);
        if(!/^(?:rule(?:Part|Data|Optional|Sequence|Sum)|(?:R[0-9]+Value|ruleString|ruleBool|ruleUInt64)\.(?:normalize|key)|Object\.(?:freeze|hasOwn|keys)|Number|snapshots\.filter|selected\.(?:sort|slice|map))$/.test(callee))errors.push('call-perimeter:'+e.path);
        if(callee==='Object.freeze'&&![K.ObjectLiteralExpression,K.ArrayLiteralExpression,K.CallExpression].includes(n.arguments?.[0]?.kind))errors.push('freeze-alias:'+e.path);
      }
      if(n.kind===K.BinaryExpression&&n.operatorToken?.kind===K.EqualsToken&&!wantedExpressions.includes(compact(text(n))))errors.push('write-perimeter:'+e.path);
      if(n.kind===K.NewExpression&&text(n.expression)!=='TypeError')errors.push('allocation-perimeter:'+e.path);
      n.forEachChild(closed);
    };
    for(const s of source.statements){
      if(s.kind!==K.VariableStatement||s.declarationList.declarations.some(d=>supportNames.has(text(d.name))))continue;
      closed(s);
    }
    observations.push({path:e.path,return_semantics:'read-model',parameters:e.inputs,projection:e.projection,predicate});
  }
  snapshot.dispose();
}finally{api.close();}
console.log(JSON.stringify({schema_version:'domainspec.query-observation/v1-candidate',result:errors.length?'fail':'pass',errors,observations,typescript:version,authority_effect:'none'}));
if(errors.length)process.exitCode=1;
