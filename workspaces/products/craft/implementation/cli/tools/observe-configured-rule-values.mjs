import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {validStructuredRuleSupport} from '/structured-rule-support-observer.mjs';

// Independent native AST observer. Expectations come from tests, never a plan.
// Structure and pinned support are checked here; behavior is tested separately.
const compilerRoot='/opt/node-toolchain/node_modules/typescript';
const version=JSON.parse(fs.readFileSync(path.join(compilerRoot,'package.json'),'utf8')).version;
if(version!=='7.0.2')throw new Error('unselected native compiler');
const {API}=await import(pathToFileURL(path.join(compilerRoot,'dist/api/sync/api.js')).href);
const {SyntaxKind:K}=await import(pathToFileURL(path.join(compilerRoot,'dist/ast/index.js')).href);
const [configPath,expectedPath]=process.argv.slice(2),expected=JSON.parse(fs.readFileSync(expectedPath,'utf8'));
const files=JSON.parse(fs.readFileSync(configPath,'utf8')).files,errors=[],observations=[];
const text=n=>n?.getText(),exported=n=>n.modifiers?.some(m=>m.kind===K.ExportKeyword);
if(JSON.stringify([...files].sort())!==JSON.stringify(expected.map(e=>e.path).sort()))errors.push('artifact-set');
const api=new API({cwd:path.dirname(configPath)});
try{
  const snapshot=api.updateSnapshot({openProjects:[configPath]}),project=snapshot.getProject(configPath);
  if(!project)throw new Error('native project missing');
  for(const e of expected){
    const file=path.resolve(path.dirname(configPath),e.path),source=project.program.getSourceFile(file);
    if(!source){errors.push('missing-source:'+e.path);continue;}
    const raw=fs.readFileSync(file,'utf8');
if(!validStructuredRuleSupport(raw))errors.push('support-drift:'+e.path);
    const imports=[],exports=[];let arrow;
    for(const d of project.program.getSyntacticDiagnostics(file))errors.push('syntax:'+d.code);
    for(const statement of source.statements){
      if(statement.kind===K.ImportDeclaration){
        const clause=statement.importClause;
        if(!clause?.namedBindings?.elements||clause.name||clause.isTypeOnly)errors.push('import-form:'+e.path);
        for(const b of clause?.namedBindings?.elements??[])imports.push({path:statement.moduleSpecifier.text,symbol:text(b.propertyName??b.name),local:text(b.name)});
      }else if(statement.kind===K.VariableStatement&&exported(statement)){
        for(const d of statement.declarationList.declarations){exports.push(text(d.name));arrow=d.initializer;}
      }else if(![K.TypeAliasDeclaration,K.VariableStatement].includes(statement.kind))errors.push('top-level:'+e.path);
    }
    if(JSON.stringify(exports)!==JSON.stringify([e.callable]))errors.push('exports:'+e.path);
    if(JSON.stringify(imports)!==JSON.stringify(e.imports))errors.push('imports:'+e.path);
    if(arrow?.kind!==K.ArrowFunction||arrow.type?.kind!==K.BooleanKeyword)errors.push('boolean-arrow:'+e.path);
    const statements=arrow?.body?.statements??[],last=statements.at(-1);
    if(last?.kind!==K.ReturnStatement)errors.push('return:'+e.path);
    if(e.return_expression!==undefined&&text(last?.expression)!==e.return_expression)errors.push('expression:'+e.path);
    const normalized=statements.filter(s=>s.kind===K.VariableStatement).flatMap(s=>s.declarationList.declarations).filter(d=>/^p[0-9]+$/.test(text(d.name)));
    if(normalized.length!==e.parameters.length)errors.push('normalizer-count:'+e.path);
    for(const [i,p] of e.parameters.entries()){
      if(!text(normalized[i]?.initializer)?.endsWith('.normalize(d['+JSON.stringify(p)+']!.value)'))errors.push('argument-binding:'+e.path);
    }
    const visit=n=>{
      if([K.ClassDeclaration,K.ClassExpression,K.FunctionDeclaration,K.FunctionExpression,K.ImportKeyword,K.AwaitExpression].includes(n.kind))errors.push('executable-form:'+e.path);
      if(n.kind===K.CallExpression&&/^(?:eval|require|fetch|JSON\.(?:parse|stringify)|Reflect\.apply)$/.test(text(n.expression)))errors.push('dynamic-call:'+e.path);
      n.forEachChild(visit);
    };
    visit(source);observations.push({path:e.path,exports,imports,parameters:e.parameters,return_expression:text(last?.expression)});
  }
  snapshot.dispose();
}finally{api.close();}
console.log(JSON.stringify({schema_version:'domainspec.structured-rule-observation/v1-candidate',result:errors.length?'fail':'pass',errors,observations,typescript:version,authority_effect:'none'}));
if(errors.length)process.exitCode=1;
