import {CROSS_GENERATOR_VALUE_PRODUCER_DEFINITION_SHA256} from './reconciled-cross-generator-value-producer.js';
import {createEffectAuditRunner} from './reconciled-effect-audit.js';
import {CROSS_GENERATOR_FACTORY_EXECUTION_DEFINITION_SHA256, CROSS_GENERATOR_OWNED_VALUES_EXECUTION_DEFINITION_SHA256} from './reconciled-cross-generator-factory-surface.js';
const replace = (source: string, from: string, to: string) => {if(source.split(from).length!==2)throw Error('FACTORY_AUDIT:hook drift');return source.replace(from,to);};
export function createFactoryAuditRunner(definitionHash: string) {
let runner = createEffectAuditRunner('FACTORY_AUDIT','domainspec.cross-generator-module-observation/v1-candidate');
runner=replace(runner,'try{\n const snapshot=',String.raw`try{
 const canonical=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canonical).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';
 if(hash(selected.definition)!=='${definitionHash}'||!['source','native'].includes(selected.phase))throw Error('FACTORY_AUDIT:definition/phase');
 const native=selected.phase==='native',phasePath=p=>native?p.replace(/\.ts$/,'.js'):p;
 const expectedModules=new Map(selected.modules.map(m=>[phasePath(m.relative_path),m]));
 if(expectedModules.size!==selected.modules.length||canonical([...expectedModules.keys()])!==canonical(selected.module_paths))throw Error('FACTORY_AUDIT:module set');
 const snapshot=`);
runner=replace(runner,'const violations=[];let visits=0;',String.raw`
  const violations=[];let visits=0;
  const problem=(code,name,n)=>{if(violations.length<64)violations.push({code,name,offset:n?.pos??0});};
  const expected=expectedModules.get(relative_path),imports=[],exports=[],typeExports=[],valueExports=[],allowed=new Set(),bindings=new Map(),initializers=new Map();
  const id=(n,name)=>n?.kind===K.Identifier&&identifier(n)===name;
  const literal=n=>n?.kind===K.StringLiteral?n.text:null;
  const member=(n,owner,name)=>n?.kind===K.PropertyAccessExpression&&id(n.expression,owner)&&id(n.name,name)&&!n.questionDotToken;
  const names=new Map(),importReferences=new Set();let markers=0;
  for(const statement of source.statements){
   if(statement.kind===K.ImportDeclaration){
    const c=statement.importClause,items=c?.namedBindings?.elements,spec=literal(statement.moduleSpecifier);
    if(native||!spec||c?.name||!items?.length||statement.attributes||statement.assertClause||items.some(e=>e.isTypeOnly||e.name?.kind!==K.Identifier))problem('import-form','static named import required',statement);
    else imports.push({specifier:spec,names:items.map(e=>identifier(e.propertyName??e.name)).sort(),...(c.isTypeOnly?{type_only:true}:{})});
   }
   if(statement.kind===K.ExportDeclaration)problem('export-form','reexports and export lists excluded',statement);
   if(statement.modifiers?.some(m=>m.kind===K.ExportKeyword)){
    if(native||statement.modifiers.some(m=>m.kind===K.DefaultKeyword))problem('export-form','unexpected export form',statement);
    else if([K.FunctionDeclaration,K.TypeAliasDeclaration,K.InterfaceDeclaration].includes(statement.kind)&&statement.name?.kind===K.Identifier){const name=identifier(statement.name);exports.push(name);(statement.kind===K.FunctionDeclaration?valueExports:typeExports).push(name);}
    else if(statement.kind===K.VariableStatement)for(const d of statement.declarationList.declarations){if(d.name.kind===K.Identifier){exports.push(identifier(d.name));valueExports.push(identifier(d.name));}else problem('export-form','destructured export',d);}
    else problem('export-form','unexpected declaration',statement);
   }
   if(!native)continue;
   if(statement.kind===K.VariableStatement)for(const d of statement.declarationList.declarations){
    const call=d.initializer;
    if(call?.kind===K.CallExpression&&id(call.expression,'require')&&call.arguments?.length===1&&literal(call.arguments[0])!==null&&d.name.kind===K.Identifier&&statement.declarationList.declarations.length===1&&/^const\b/.test(statement.declarationList.getText())){
     allowed.add(call.expression);const name=identifier(d.name),specifier=literal(call.arguments[0]);
     if(bindings.has(name))problem('import-binding','duplicate binding',d);
     bindings.set(name,specifier);names.set(name,new Set());
    }
   }
   const e=statement.kind===K.ExpressionStatement?statement.expression:null;
   if(e?.kind===K.CallExpression&&member(e.expression,'Object','defineProperty')&&e.arguments?.length===3&&id(e.arguments[0],'exports')&&literal(e.arguments[1])==='__esModule'&&e.arguments[2]?.kind===K.ObjectLiteralExpression&&e.arguments[2].properties.length===1){
    const p=e.arguments[2].properties[0];if(p.kind===K.PropertyAssignment&&id(p.name,'value')&&p.initializer.kind===K.TrueKeyword){allowed.add(e.arguments[0]);markers++;}
   }
   if(e?.kind===K.BinaryExpression&&e.operatorToken.kind===K.EqualsToken&&e.left.kind===K.PropertyAccessExpression&&id(e.left.expression,'exports')&&!e.left.questionDotToken){
    let chain=e;const init=[];
    while(chain?.kind===K.BinaryExpression&&chain.operatorToken.kind===K.EqualsToken&&chain.left.kind===K.PropertyAccessExpression&&id(chain.left.expression,'exports')&&!chain.left.questionDotToken){init.push(chain.left);chain=chain.right;}
    if(chain?.kind===K.VoidExpression&&chain.expression.kind===K.NumericLiteral&&chain.expression.getText()==='0'){for(const lhs of init){const name=identifier(lhs.name);initializers.set(name,(initializers.get(name)??0)+1);allowed.add(lhs.expression);}continue;}
    const name=identifier(e.left.name),rhs=e.right;
    const frozen=rhs?.kind===K.CallExpression&&member(rhs.expression,'Object','freeze')&&rhs.arguments.length===1&&[K.ObjectLiteralExpression,K.ArrayLiteralExpression].includes(rhs.arguments[0].kind);
    const callee=rhs?.expression?.kind===K.ParenthesizedExpression?rhs.expression.expression:null;
    const enumCall=expected.role==='enum-definition'&&rhs?.kind===K.CallExpression&&callee?.kind===K.BinaryExpression&&callee.operatorToken.kind===K.CommaToken&&callee.left.kind===K.NumericLiteral&&callee.left.getText()==='0'&&callee.right.kind===K.PropertyAccessExpression&&callee.right.expression.kind===K.Identifier&&id(callee.right.name,'defineEnum')&&rhs.arguments.length===1&&rhs.arguments[0].kind===K.ObjectLiteralExpression;
    if(id(rhs,name)||frozen||enumCall){exports.push(name);allowed.add(e.left.expression);}
   }
  }
`);
runner=replace(runner,'const form=forms.get(n.kind);',String.raw`
   if(n.kind===K.VariableDeclaration&&n.name?.kind===K.Identifier&&bindings.has(identifier(n.name)))importReferences.add(n.name);
   if(n.kind===K.PropertyAccessExpression&&n.expression?.kind===K.Identifier&&bindings.has(identifier(n.expression))&&!n.questionDotToken){importReferences.add(n.expression);names.get(identifier(n.expression)).add(identifier(n.name));}
   if(n.kind===K.Identifier){
    const name=identifier(n);
    if(['require','exports'].includes(name)&&!allowed.has(n))problem('commonjs-binding','unapproved '+name,n);
    if(native&&bindings.has(name)&&!importReferences.has(n))problem('import-binding','nonstatic namespace use',n);
   }
   const form=forms.get(n.kind);`);
runner=replace(runner,'modules.push({relative_path,source_sha256:hash(fs.readFileSync(file)),violations});',String.raw`
  if(native){
   if(markers!==1)problem('export-marker','exactly one CommonJS marker required',source);
   for(const [name,specifier]of bindings)imports.push({specifier,names:[...names.get(name)].sort()});
   if(canonical([...initializers].sort())!==canonical(expected.value_exports.map(name=>[name,1]).sort()))problem('export-initialization','unexpected CommonJS initialization',source);
  }
  imports.sort((a,b)=>a.specifier<b.specifier?-1:a.specifier>b.specifier?1:0);exports.sort();
  if(!native&&(canonical(typeExports.sort())!==canonical([...expected.type_exports].sort())||canonical(valueExports.sort())!==canonical([...expected.value_exports].sort())))problem('export-kind','source-derived type/value export distinction',source);
  const wanted=expected.imports.filter(i=>!native||!i.type_only).map(i=>({specifier:i.specifier,names:i.names,...(!native&&i.type_only?{type_only:true}:{})})).sort((a,b)=>a.specifier<b.specifier?-1:a.specifier>b.specifier?1:0);
  if(canonical(imports)!==canonical(wanted))problem('import-surface','source-derived imports differ',source);
  if(canonical(exports)!==canonical([...expected.value_exports,...(native?[]:expected.type_exports)].sort()))problem('export-surface','source-derived exports differ',source);
  for(const i of imports){const target=path.posix.normalize(path.posix.join(path.posix.dirname(relative_path),i.specifier));if(!i.specifier.startsWith('.')||!expectedModules.has(native?target:target.replace(/\.js$/,'.ts')))problem('external-import',i.specifier,source);}
  modules.push({relative_path,source_sha256:hash(fs.readFileSync(file)),imports,exports,violations});`);
return runner;
}
export const CROSS_GENERATOR_FACTORY_AUDIT_RUNNER = createFactoryAuditRunner(CROSS_GENERATOR_FACTORY_EXECUTION_DEFINITION_SHA256);
export const CROSS_GENERATOR_OWNED_VALUES_AUDIT_RUNNER = createFactoryAuditRunner(CROSS_GENERATOR_OWNED_VALUES_EXECUTION_DEFINITION_SHA256);
export const CROSS_GENERATOR_VALUE_PRODUCER_AUDIT_RUNNER = createFactoryAuditRunner(CROSS_GENERATOR_VALUE_PRODUCER_DEFINITION_SHA256);
