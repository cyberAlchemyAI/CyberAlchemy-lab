import {createEffectAuditRunner} from './reconciled-effect-audit.js';
import {CROSS_GENERATOR_STATE_MACHINE_DEFINITION_SHA256} from './reconciled-cross-generator-state-machine.js';

export const CROSS_GENERATOR_EXECUTION_DEFINITION_SHA256 = 'c27570b2ea98e71b6ee1765b7fb1509bfee8fce5e71063ed3188fb6e7b53dbd7';
const replace = (source: string, from: string, to: string) => {
  if (source.split(from).length !== 2) throw Error('CROSS_GENERATOR_AUDIT:hook drift');
  return source.replace(from, to);
};
let runner = createEffectAuditRunner('CROSS_GENERATOR_AUDIT', 'domainspec.cross-generator-module-observation/v1-candidate');
runner = replace(runner, 'try{\n const snapshot=', String.raw`try{
 const canonical=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canonical).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';
 if(hash(selected.definition)!=='${CROSS_GENERATOR_EXECUTION_DEFINITION_SHA256}'||!['source','native'].includes(selected.phase))throw Error('CROSS_GENERATOR_AUDIT:definition/phase');
 const native=selected.phase==='native',phasePath=p=>native?p.replace(/\.ts$/,'.js'):p;
 const expectedModules=new Map(selected.modules.map(m=>[phasePath(m.relative_path),m]));
 if(expectedModules.size!==selected.modules.length||canonical([...expectedModules.keys()])!==canonical(selected.module_paths))throw Error('CROSS_GENERATOR_AUDIT:module set');
 const snapshot=`);
runner = replace(runner, 'const violations=[];let visits=0;', String.raw`
  const violations=[];let visits=0;
  const problem=(code,name,n)=>{if(violations.length<64)violations.push({code,name,offset:n?.pos??0});};
  const expected=expectedModules.get(relative_path),imports=[],exports=[],allowed=new Set(),bindings=new Map(),exportInitializers=new Map();
  const id=(n,name)=>n?.kind===K.Identifier&&identifier(n)===name;
  const literal=n=>n?.kind===K.StringLiteral?n.text:null;
  const member=(n,owner,name)=>n?.kind===K.PropertyAccessExpression&&id(n.expression,owner)&&id(n.name,name)&&!n.questionDotToken;
  const actualNames=new Map(),importReferences=new Set();let esModuleMarkers=0;
  for(const statement of source.statements){
   if(statement.kind===K.ImportDeclaration){
    const c=statement.importClause,items=c?.namedBindings?.elements,spec=literal(statement.moduleSpecifier);
    if(native||!spec||c?.isTypeOnly||c?.name||!items?.length||statement.attributes||statement.assertClause||items.some(e=>e.isTypeOnly||e.name?.kind!==K.Identifier))problem('import-form','static named source import required',statement);
    else imports.push({specifier:spec,names:items.map(e=>identifier(e.propertyName??e.name)).sort()});
   }
   if(statement.kind===K.ExportDeclaration)problem('export-form','reexports and export lists excluded',statement);
   if(statement.modifiers?.some(m=>m.kind===K.ExportKeyword)){
    if(native||statement.modifiers.some(m=>m.kind===K.DefaultKeyword))problem('export-form','unexpected export form',statement);
    else if(statement.kind===K.FunctionDeclaration&&statement.name)exports.push(identifier(statement.name));
    else if(statement.kind===K.VariableStatement)for(const d of statement.declarationList.declarations){if(d.name.kind===K.Identifier)exports.push(identifier(d.name));else problem('export-form','destructured export',d);}
    else if(![K.TypeAliasDeclaration,K.InterfaceDeclaration].includes(statement.kind))problem('export-form','unexpected declaration',statement);
   }
   if(!native)continue;
   if(statement.kind===K.VariableStatement)for(const d of statement.declarationList.declarations){
    const call=d.initializer;
    if(call?.kind===K.CallExpression&&id(call.expression,'require')&&call.arguments?.length===1&&literal(call.arguments[0])!==null&&d.name.kind===K.Identifier&&statement.declarationList.declarations.length===1&&/^const\b/.test(statement.declarationList.getText())){
     allowed.add(call.expression);const name=identifier(d.name),specifier=literal(call.arguments[0]);
     if(bindings.has(name))problem('import-binding','duplicate binding',d);
     bindings.set(name,specifier);actualNames.set(name,new Set());
    }
   }
   const e=statement.kind===K.ExpressionStatement?statement.expression:null;
   if(e?.kind===K.CallExpression&&member(e.expression,'Object','defineProperty')&&e.arguments?.length===3&&id(e.arguments[0],'exports')&&literal(e.arguments[1])==='__esModule'&&e.arguments[2]?.kind===K.ObjectLiteralExpression&&e.arguments[2].properties.length===1){
    const p=e.arguments[2].properties[0];if(p.kind===K.PropertyAssignment&&id(p.name,'value')&&p.initializer.kind===K.TrueKeyword){allowed.add(e.arguments[0]);esModuleMarkers++;}
   }
   if(e?.kind===K.BinaryExpression&&e.operatorToken.kind===K.EqualsToken&&e.left.kind===K.PropertyAccessExpression&&id(e.left.expression,'exports')&&!e.left.questionDotToken){
    const name=identifier(e.left.name),zero=e.right.kind===K.VoidExpression&&e.right.expression.kind===K.NumericLiteral&&e.right.expression.getText()==='0';
    if(zero){exportInitializers.set(name,(exportInitializers.get(name)??0)+1);allowed.add(e.left.expression);}
    else {
     const outer=e.right,inner=outer?.arguments?.[0],provider=inner?.arguments?.[0];
     const wrapper=outer?.kind===K.CallExpression&&member(outer.expression,'Object','freeze')&&outer.arguments.length===1&&inner?.kind===K.CallExpression&&member(inner.expression,'Object','assign')&&inner.arguments.length===2&&provider?.kind===K.PropertyAccessExpression&&provider.expression.kind===K.Identifier&&id(provider.name,'select')&&inner.arguments[1]?.kind===K.ObjectLiteralExpression;
     if(id(e.right,name)||wrapper){exports.push(name);allowed.add(e.left.expression);}
    }
   }
  }
`);
runner = replace(runner, 'const form=forms.get(n.kind);', String.raw`
   if(n.kind===K.VariableDeclaration&&n.name?.kind===K.Identifier&&bindings.has(identifier(n.name)))importReferences.add(n.name);
   if(n.kind===K.PropertyAccessExpression&&n.expression?.kind===K.Identifier&&bindings.has(identifier(n.expression))&&!n.questionDotToken){importReferences.add(n.expression);actualNames.get(identifier(n.expression)).add(identifier(n.name));}
   if(n.kind===K.Identifier){
    const name=identifier(n);
    if(['require','exports'].includes(name)&&!allowed.has(n))problem('commonjs-binding','unapproved '+name,n);
    if(native&&bindings.has(name)){
     // Import identifiers may occur only at their declaration or as a static member receiver.
     if(!importReferences.has(n))problem('import-binding','nonstatic namespace use',n);
    }
   }
   const form=forms.get(n.kind);`);
runner = replace(runner, 'modules.push({relative_path,source_sha256:hash(fs.readFileSync(file)),violations});', String.raw`
  if(native){
   if(esModuleMarkers!==1)problem('export-marker','exactly one CommonJS marker required',source);
   for(const [name,specifier]of bindings)imports.push({specifier,names:[...actualNames.get(name)].sort()});
   if(canonical([...exportInitializers].sort())!==canonical([[expected.callable,1]]))problem('export-initialization','unexpected CommonJS export initialization',source);
  }
  imports.sort((a,b)=>a.specifier<b.specifier?-1:a.specifier>b.specifier?1:0);exports.sort();
  const wanted=expected.imports.map(i=>({specifier:i.specifier,names:i.names})).sort((a,b)=>a.specifier<b.specifier?-1:a.specifier>b.specifier?1:0);
  if(canonical(imports)!==canonical(wanted))problem('import-surface','source-derived imports differ',source);
  if(canonical(exports)!==canonical([expected.callable]))problem('export-surface','source-derived callable differs',source);
  for(const i of imports){const target=path.posix.normalize(path.posix.join(path.posix.dirname(relative_path),i.specifier));if(!i.specifier.startsWith('.')||!expectedModules.has(native?target:target.replace(/\.js$/,'.ts')))problem('external-import',i.specifier,source);}
  modules.push({relative_path,source_sha256:hash(fs.readFileSync(file)),imports,exports,violations});`);
export const CROSS_GENERATOR_AUDIT_RUNNER = runner;

// Separate profile: Policy surface rules above and its definition remain intact.
let stateRunner = replace(runner, CROSS_GENERATOR_EXECUTION_DEFINITION_SHA256, CROSS_GENERATOR_STATE_MACHINE_DEFINITION_SHA256);
stateRunner = replace(stateRunner, "if(statement.kind===K.ExportDeclaration)problem('export-form','reexports and export lists excluded',statement);", String.raw`
   if(statement.kind===K.ExportDeclaration){
    const items=statement.exportClause?.elements,spec=literal(statement.moduleSpecifier);
    if(native||!items?.length||items.some(e=>e.propertyName||e.name?.kind!==K.Identifier))problem('export-form','unsupported export declaration',statement);
    else if(statement.isTypeOnly&&spec){const names=items.map(e=>identifier(e.name)).sort();imports.push({specifier:spec,names,type_only:true});exports.push(...names);}
    else if(!statement.isTypeOnly&&!statement.moduleSpecifier&&items.length===1&&id(items[0].name,'initialState'))exports.push('initialState');
    else problem('export-form','unsupported export declaration',statement);
   }`);
stateRunner = replace(stateRunner, "else if(![K.TypeAliasDeclaration,K.InterfaceDeclaration].includes(statement.kind))problem('export-form','unexpected declaration',statement);", "else if([K.TypeAliasDeclaration,K.InterfaceDeclaration].includes(statement.kind)&&statement.name?.kind===K.Identifier)exports.push(identifier(statement.name));else problem('export-form','unexpected declaration',statement);");
stateRunner = replace(stateRunner, "if(e?.kind===K.BinaryExpression&&e.operatorToken.kind===K.EqualsToken&&e.left.kind===K.PropertyAccessExpression&&id(e.left.expression,'exports')&&!e.left.questionDotToken){", String.raw`
   if(e?.kind===K.CallExpression&&member(e.expression,'Object','defineProperty')&&e.arguments?.length===3&&id(e.arguments[0],'exports')&&literal(e.arguments[1])==='initialState'){
    const object=e.arguments[2],properties=object?.properties,getter=properties?.find(p=>id(p.name,'get')),enumerable=properties?.find(p=>id(p.name,'enumerable')),fn=getter?.initializer,returned=fn?.body?.statements?.[0]?.expression;
    if(object?.kind===K.ObjectLiteralExpression&&properties.length===2&&getter.kind===K.PropertyAssignment&&enumerable?.kind===K.PropertyAssignment&&enumerable.initializer.kind===K.TrueKeyword&&fn.kind===K.FunctionExpression&&!fn.parameters.length&&fn.body.statements.length===1&&fn.body.statements[0].kind===K.ReturnStatement&&returned?.kind===K.PropertyAccessExpression&&returned.expression.kind===K.Identifier&&id(returned.name,'initialState')){allowed.add(e.arguments[0]);exports.push('initialState');}
   }
   if(e?.kind===K.BinaryExpression&&e.operatorToken.kind===K.EqualsToken&&e.left.kind===K.PropertyAccessExpression&&id(e.left.expression,'exports')&&!e.left.questionDotToken){
    let chain=e;const initializers=[];
    while(chain?.kind===K.BinaryExpression&&chain.operatorToken.kind===K.EqualsToken&&chain.left.kind===K.PropertyAccessExpression&&id(chain.left.expression,'exports')&&!chain.left.questionDotToken){initializers.push(chain.left);chain=chain.right;}
    if(chain?.kind===K.VoidExpression&&chain.expression.kind===K.NumericLiteral&&chain.expression.getText()==='0'){for(const lhs of initializers){const name=identifier(lhs.name);exportInitializers.set(name,(exportInitializers.get(name)??0)+1);allowed.add(lhs.expression);}continue;}
    if(id(e.left.name,'initialState')&&literal(e.right)===expected.initial_state){exports.push('initialState');allowed.add(e.left.expression);continue;}
`);
stateRunner = replace(stateRunner, "id(provider.name,'select')", "id(provider.name,'reduce')");
stateRunner = replace(stateRunner, 'canonical([[expected.callable,1]])', 'canonical(expected.value_exports.map(name=>[name,1]))');
stateRunner = replace(stateRunner, 'expected.imports.map(i=>({specifier:i.specifier,names:i.names}))', "expected.imports.filter(i=>!native||!i.type_only).map(i=>({specifier:i.specifier,names:i.names,...(!native&&i.type_only?{type_only:true}:{})}))");
stateRunner = replace(stateRunner, 'canonical([expected.callable])', 'canonical([...expected.value_exports,...(native?[]:expected.type_exports)].sort())');
export const CROSS_GENERATOR_STATE_MACHINE_AUDIT_RUNNER = stateRunner;
