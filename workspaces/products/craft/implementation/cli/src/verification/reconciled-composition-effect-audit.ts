import {sha256} from '../input/source-manifest.js';
import {assertCompositionBinding, COMPOSITION_BINDING_DEFINITION_SHA256, type CompositionVerificationBinding} from './reconciled-composition-binding.js';
import {createEffectAuditRunner} from './reconciled-effect-audit.js';

export const COMPOSITION_EFFECT_DEFINITION_SHA256 = 'f2b6f2d4068a76605206220626f794c5387bd946e5b2c9014cbd86145380f402';
export function createCompositionEffectAudit(binding: CompositionVerificationBinding, definition: string) {
  assertCompositionBinding(binding);
  if (typeof definition !== 'string' || sha256(definition) !== COMPOSITION_EFFECT_DEFINITION_SHA256) throw new TypeError('COMPOSITION_EFFECT_AUDIT:definition drift');
  return Object.freeze({definition_sha256: COMPOSITION_EFFECT_DEFINITION_SHA256, binding});
}
const replace = (source: string, from: string, to: string) => {
  if (source.split(from).length !== 2) throw new TypeError('COMPOSITION_EFFECT_AUDIT:observer hook drift');
  return source.replace(from, to);
};
let runner = createEffectAuditRunner('COMPOSITION_EFFECT_AUDIT', 'domainspec.composition-effect-observation/v1-candidate');
runner = replace(runner, 'try{\n const snapshot=', String.raw`try{
 const canonical=v=>v===null||typeof v!=='object'?JSON.stringify(v):Array.isArray(v)?'['+v.map(canonical).join(',')+']':'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';
 if(hash(selected.definition)!=='${COMPOSITION_EFFECT_DEFINITION_SHA256}'||selected.definition_sha256!=='${COMPOSITION_EFFECT_DEFINITION_SHA256}')throw Error('COMPOSITION_EFFECT_AUDIT:definition drift');
 const b=selected.binding,{binding_sha256,...body}=b??{};
 if(b?.definition_sha256!=='${COMPOSITION_BINDING_DEFINITION_SHA256}'||hash(canonical(body))!==binding_sha256)throw Error('COMPOSITION_EFFECT_AUDIT:binding integrity');
 if(!['source','native'].includes(selected.phase)||typeof selected.module_root!=='string'||!path.isAbsolute(selected.module_root)||fs.lstatSync(selected.module_root).isSymbolicLink())throw Error('COMPOSITION_EFFECT_AUDIT:phase/root');
 const phasePath=p=>p.replace(/\.ts$/,selected.phase==='native'?'.js':'.ts');
 const safe=p=>typeof p==='string'&&p.length>0&&!p.includes('\0')&&!p.includes('\\')&&!path.posix.isAbsolute(p)&&!p.split('/').some(s=>!s||s==='.'||s==='..');
 if(!Array.isArray(b.modules)||!b.modules.length||b.modules.some(m=>!safe(m.relative_path)||!(/\.(?:ts|mjs)$/).test(m.relative_path)||m.relative_path.endsWith('.d.ts')||!(/^[a-f0-9]{64}$/).test(m.source_sha256)||!Array.isArray(m.exports)||!Array.isArray(m.imports)))throw Error('COMPOSITION_EFFECT_AUDIT:module metadata');
 const expectedPaths=b.modules.map(m=>phasePath(m.relative_path));
 if(new Set(expectedPaths).size!==expectedPaths.length||canonical(expectedPaths)!==canonical(selected.module_paths))throw Error('COMPOSITION_EFFECT_AUDIT:module paths');
 const expectedModules=new Map(b.modules.map(m=>[phasePath(m.relative_path),m]));
 for(const m of b.modules){
  const file=path.resolve(selected.module_root,phasePath(m.relative_path));let current=selected.module_root;
  for(const part of phasePath(m.relative_path).split('/')){current=path.join(current,part);if(fs.lstatSync(current).isSymbolicLink())throw Error('COMPOSITION_EFFECT_AUDIT:symbolic artifact');}
  if(!fs.statSync(file).isFile()||fs.statSync(file).size>8388608)throw Error('COMPOSITION_EFFECT_AUDIT:source capacity');
  if(selected.phase==='source'&&hash(fs.readFileSync(file))!==m.source_sha256)throw Error('COMPOSITION_EFFECT_AUDIT:source drift');
 }
 const snapshot=`);
runner = replace(runner, 'const violations=[];let visits=0;', String.raw`
  const violations=[];let visits=0;
  const problem=(code,name,n)=>{if(violations.length<64)violations.push({code,name,offset:n?.pos??0});};
  const expected=expectedModules.get(relative_path),actualImports=[],actualExports=[],prototypeReads=new Set(),decimalMath=new Set(),descriptorReflect=new Set();
  const id=(n,name)=>n?.kind===K.Identifier&&identifier(n)===name;
  const literal=n=>n&&[K.StringLiteral,K.NoSubstitutionTemplateLiteral].includes(n.kind)?n.text:n?.kind===K.NumericLiteral?n.getText():null;
  const member=(n,name)=>n?.kind===K.PropertyAccessExpression&&!n.questionDotToken&&id(n.name,name);
  const call=(n,count)=>n?.kind===K.CallExpression&&!n.questionDotToken&&!n.typeArguments?.length&&n.arguments?.length===count&&!n.arguments.some(a=>a.kind===K.SpreadElement);
  for(const statement of source.statements){
   if(statement.kind===K.ImportDeclaration){
    const c=statement.importClause,elements=c?.namedBindings?.elements;
    if(statement.moduleSpecifier?.kind!==K.StringLiteral||!c||c.isTypeOnly||c.name||!elements?.length||statement.attributes||statement.assertClause||elements.some(e=>e.isTypeOnly||e.name?.kind!==K.Identifier||e.propertyName&&e.propertyName.kind!==K.Identifier)){problem('import-surface','literal named import required',statement);continue;}
    const spec=statement.moduleSpecifier.text;
    const target=path.posix.normalize(path.posix.join(path.posix.dirname(relative_path),spec)),mapped=selected.phase==='source'?target.replace(/\.js$/,'.ts'):target;
    if(!spec.startsWith('.')||!expectedModules.has(mapped))problem('external-import',spec,statement);
    for(const e of elements)actualImports.push({specifier:spec,imported:identifier(e.propertyName??e.name),local:identifier(e.name)});
   }
   if(statement.kind===K.ExportDeclaration)problem('export-surface','re-export or export list',statement);
   const exported=statement.modifiers?.some(m=>m.kind===K.ExportKeyword);
   if(!exported)continue;
   if(statement.modifiers.some(m=>m.kind===K.DefaultKeyword)){problem('export-surface','default export',statement);continue;}
   if(statement.kind===K.FunctionDeclaration&&statement.name?.kind===K.Identifier)actualExports.push(identifier(statement.name));
   else if(statement.kind===K.VariableStatement){for(const d of statement.declarationList.declarations){if(d.name?.kind===K.Identifier)actualExports.push(identifier(d.name));else problem('export-surface','destructured export',d);}}
   else if(selected.phase==='source'&&[K.InterfaceDeclaration,K.TypeAliasDeclaration].includes(statement.kind)){}
   else problem('export-surface','unsupported exported declaration',statement);
  }
  actualExports.sort();
  if(canonical(actualImports)!==canonical(expected.imports))problem('import-binding','source-derived imports differ',source);
  if(canonical(actualExports)!==canonical(expected.exports))problem('export-binding','source-derived exports differ',source);
  if(relative_path===phasePath(b.adapter_path)){
   const functions=source.statements.filter(s=>s.kind===K.FunctionDeclaration&&id(s.name,'evaluateCalculation'));
   const fn=functions[0],statement=fn?.body?.statements?.[0],clauses=statement?.caseBlock?.clauses;
   const bridges=b.bridges.filter(r=>r.role==='calculation-call');
   let valid=functions.length===1&&fn.parameters?.length===2&&id(fn.parameters[0].name,'name')&&id(fn.parameters[1].name,'input')&&fn.body?.statements?.length===1&&statement.kind===K.SwitchStatement&&id(statement.expression,'name')&&clauses?.length===bridges.length+1;
   for(let index=0;valid&&index<bridges.length;index++){
    const bridge=bridges[index],clause=clauses[index],block=clause.statements?.[0],rows=block?.statements;
    const variable=rows?.[0],declarations=variable?.declarationList?.declarations,d=declarations?.[0],args=d?.initializer,returned=rows?.[1],target=returned?.expression,record=target?.arguments?.[0],properties=record?.properties;
    valid=clause.kind===K.CaseClause&&literal(clause.expression)===bridge.name&&clause.statements.length===1&&block.kind===K.Block&&rows.length===2&&
     variable.kind===K.VariableStatement&&declarations.length===1&&/^const\b/.test(variable.declarationList.getText())&&id(d.name,'d')&&call(args,2)&&id(args.expression,'argumentsFor')&&id(args.arguments[0],'input')&&args.arguments[1]?.kind===K.ArrayLiteralExpression&&canonical(args.arguments[1].elements.map(literal))===canonical(bridge.arguments.map(a=>a.authored_name))&&
     returned.kind===K.ReturnStatement&&call(target,1)&&id(target.expression,'calculation'+index)&&record.kind===K.ObjectLiteralExpression&&properties.length===bridge.arguments.length;
    for(let i=0;valid&&i<bridge.arguments.length;i++){
     const binding=bridge.arguments[i],property=properties[i],value=property.initializer,lookup=value?.expression?.kind===K.NonNullExpression?value.expression.expression:value?.expression;
     valid=property.kind===K.PropertyAssignment&&literal(property.name)===binding.core_name&&member(value,'value')&&lookup?.kind===K.ElementAccessExpression&&!lookup.questionDotToken&&id(lookup.expression,'d')&&literal(lookup.argumentExpression)===binding.authored_name;
    }
   }
   if(valid){const clause=clauses.at(-1),thrower=clause.statements?.[0],error=thrower?.expression;valid=clause.kind===K.DefaultClause&&clause.statements.length===1&&thrower.kind===K.ThrowStatement&&error?.kind===K.NewExpression&&id(error.expression,'TypeError')&&error.arguments?.length===1&&literal(error.arguments[0])==='COMPOSITION_CALCULATION';}
   if(!valid)problem('adapter-binding','source-derived argument projection differs',source);
  }
  const members=new Set(definition.forbidden_members);
`);
runner = replace(runner, 'const visit=(n,depth=0)=>{', 'const visit=(n,depth=0,inType=false)=>{');
runner = replace(runner, 'const form=forms.get(n.kind);', String.raw`
   // The existing input shape check may read Object.prototype but cannot leak it.
   if(call(n,1)&&member(n.expression,'includes')){
    const array=n.expression.expression,argument=n.arguments[0],items=array?.elements;
    if(array?.kind===K.ArrayLiteralExpression&&items?.length===2&&member(items[0],'prototype')&&id(items[0].expression,'Object')&&items[1].kind===K.NullKeyword&&call(argument,1)&&member(argument.expression,'getPrototypeOf')&&id(argument.expression.expression,'Object')){prototypeReads.add(items[0]);prototypeReads.add(argument.expression);}
   }
   if(call(n,2)&&member(n.expression,'max')&&id(n.expression.expression,'Math')&&n.arguments[0]?.kind===K.NumericLiteral&&n.arguments[0].getText()==='1'&&id(n.arguments[1],'scale'))decimalMath.add(n.expression.expression);
   if(call(n,1)&&member(n.expression,'ownKeys')&&id(n.expression.expression,'Reflect')&&(id(n.arguments[0],'d')||id(n.arguments[0],'descriptors')))descriptorReflect.add(n.expression.expression);
   let property=null;
   if(n.kind===K.PropertyAccessExpression)property=identifier(n.name);
   else if(n.kind===K.ElementAccessExpression){property=literal(n.argumentExpression);if(property===null)problem('computed-member','nonliteral member access',n);}
   else if(n.kind===K.ComputedPropertyName){property=literal(n.expression);if(property===null)problem('computed-member','nonliteral property name',n);}
   else if(n.kind===K.BindingElement){const p=n.propertyName??n.name;if(p?.kind===K.Identifier)property=identifier(p);else if(p?.kind===K.StringLiteral)property=p.text;}
   if(property!==null&&members.has(property)&&!prototypeReads.has(n))problem('forbidden-member',property,n);
   const form=forms.get(n.kind);`);
runner = replace(runner, 'if(identifiers.has(name)&&violations.length<64)', 'if(!inType&&identifiers.has(name)&&!decimalMath.has(n)&&!descriptorReflect.has(n)&&violations.length<64)');
runner = replace(runner, 'n.forEachChild(child=>visit(child,depth+1));', 'n.forEachChild(child=>visit(child,depth+1,inType||n.kind===K.TypeReference||n.kind===K.TypeQuery));');
runner = replace(runner, 'modules.push({relative_path,source_sha256:hash(fs.readFileSync(file)),violations});', 'modules.push({relative_path,source_sha256:hash(fs.readFileSync(file)),imports:actualImports,exports:actualExports,violations});');
export const COMPOSITION_EFFECT_AUDIT_RUNNER = runner;
