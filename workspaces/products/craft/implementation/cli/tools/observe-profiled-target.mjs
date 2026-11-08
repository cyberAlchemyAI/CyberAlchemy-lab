import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

// Run inside the selected shared toolchain image; never install a private compiler.
const compilerRoot='/opt/node-toolchain/node_modules/typescript';
const version=JSON.parse(fs.readFileSync(path.join(compilerRoot,'package.json'),'utf8')).version;
if(version!=='7.0.2') throw new Error('unselected native AST compiler:'+version);
const {API}=await import(pathToFileURL(path.join(compilerRoot,'dist/api/sync/api.js')).href);
const {SyntaxKind:K}=await import(pathToFileURL(path.join(compilerRoot,'dist/ast/index.js')).href);
const [configPath,expectationsPath]=process.argv.slice(2);
const expected=JSON.parse(fs.readFileSync(expectationsPath,'utf8'));
const api=new API({cwd:path.dirname(configPath)});
const errors=[];
const observations=[];
const name=n=>n?.getText();
const exported=n=>n.modifiers?.some(m=>m.kind===K.ExportKeyword);
try{
  const snapshot=api.updateSnapshot({openProjects:[configPath]});
  const project=snapshot.getProject(configPath);
  if(!project) throw new Error('native project missing');
  for(const e of expected){
    const file=path.resolve(path.dirname(configPath),e.path);
    const source=project.program.getSourceFile(file);
    if(!source){errors.push('path:'+e.path);continue;}
    for(const diagnostic of project.program.getSyntacticDiagnostics(file)) errors.push('syntax:'+e.path+':'+diagnostic.code);
    const exports=[],imports=[];let classCount=0;let construct;
    const visit=node=>{
      if(node.kind===K.ClassDeclaration || node.kind===K.ClassExpression) classCount++;
      if(node.kind===K.VariableDeclaration && name(node.name)==='construct') construct=node.initializer;
      if(e.kind==='Query' && node.kind===K.BinaryExpression && node.operatorToken.kind===K.EqualsToken && [K.PropertyAccessExpression,K.ElementAccessExpression].includes(node.left.kind)) errors.push('query-mutation:'+e.path);
      node.forEachChild(visit);
    };
    visit(source);
    for(const statement of source.statements){
      if(statement.kind===K.ImportDeclaration){
        const clause=statement.importClause;
        for(const item of clause?.namedBindings?.elements??[]) imports.push({path:statement.moduleSpecifier.text,symbol:name(item.name),type_only:!!clause.isTypeOnly});
        if(clause?.name || !clause?.namedBindings?.elements) errors.push('unsupported-import:'+e.path);
      }
      if(exported(statement)){
        if(statement.kind===K.VariableStatement){
          for(const d of statement.declarationList.declarations){exports.push(name(d.name));if(d.initializer?.kind!==K.ArrowFunction) errors.push('non-arrow:'+e.path);}
        }else if(![K.InterfaceDeclaration,K.TypeAliasDeclaration].includes(statement.kind)) errors.push('runtime-export:'+e.path);
      }
    }
    if(classCount) errors.push('class-construction:'+e.path);
    if(exports.length!==1 || exports[0]!==e.callable) errors.push('export-set:'+e.path);
    if(JSON.stringify(imports)!==JSON.stringify(e.imports.map(i=>({path:i.path,symbol:i.symbol,type_only:i.type_only})))) errors.push('import-binding:'+e.path);
    if(e.kind==='Entity'){
      // Require a direct early-return guard in the same construction block, not
      // a token hidden under an unreachable branch, string, comment or helper.
      const statements=construct?.body?.statements??[];
      const guard=statements.findIndex(s=>s.kind===K.IfStatement && s.expression.kind===K.PrefixUnaryExpression && s.expression.operator===K.ExclamationToken && s.expression.operand.kind===K.CallExpression && name(s.expression.operand.expression)===e.bound_rule && s.thenStatement.kind===K.ReturnStatement && s.thenStatement.expression?.kind===K.CallExpression && name(s.thenStatement.expression.expression)==='failure');
      const construction=statements.findIndex(s=>s.kind===K.VariableStatement && s.declarationList.declarations.some(d=>name(d.name)==='value'));
      if(guard<0 || construction<0 || guard>=construction) errors.push('validation-before-construction:'+e.path);
      for(const statement of statements.slice(0,Math.max(guard,0))) if(statement.kind===K.ReturnStatement) errors.push('early-construction-bypass:'+e.path);
    }
    if(e.kind==='Rule'){
      const variable=source.statements.find(s=>s.kind===K.VariableStatement && exported(s));
      const arrow=variable?.declarationList.declarations[0]?.initializer;
      if(arrow?.type?.kind!==K.BooleanKeyword) errors.push('boolean-rule:'+e.path);
      let calls=0;arrow?.body?.forEachChild(function scan(n){if(n.kind===K.CallExpression)calls++;n.forEachChild(scan);});
      if(arrow?.body?.kind===K.CallExpression || calls) errors.push('hidden-rule-call:'+e.path);
    }
    observations.push({path:e.path,exports,imports,class_count:classCount});
  }
  snapshot.dispose();
}finally{api.close();}
process.stdout.write(JSON.stringify({schema_version:'domainspec.profile-native-observation/v1-candidate',typescript:version,result:errors.length?'fail':'pass',errors,observations,authority_effect:'none'})+'\n');
if(errors.length)process.exitCode=1;
