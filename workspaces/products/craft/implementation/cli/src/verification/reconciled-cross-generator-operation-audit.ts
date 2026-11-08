import {createFactoryAuditRunner} from './reconciled-cross-generator-factory-audit.js';
import {CROSS_GENERATOR_OPERATION_DEFINITION_SHA256} from './reconciled-cross-generator-operation-surface.js';
const replace = (source: string, from: string, to: string) => {
 if(source.split(from).length!==2)throw Error('OPERATION_INTEROP_AUDIT:hook drift');return source.replace(from,to);
};
/** Explicit Operation profile: former factory/owned/Enum audit output is unchanged. */
function createOperationAuditRunner() {
 let runner=createFactoryAuditRunner(CROSS_GENERATOR_OPERATION_DEFINITION_SHA256);
 runner=replace(runner,"if(statement.kind===K.ExportDeclaration)problem('export-form','reexports and export lists excluded',statement);",String.raw`
   if(statement.kind===K.ExportDeclaration){
    const items=statement.exportClause?.elements,spec=literal(statement.moduleSpecifier);
    if(native||!['operation-wrapper','event-wrapper'].includes(expected.role)||!statement.isTypeOnly||!items?.length||!spec||statement.attributes||statement.assertClause||items.some(e=>e.propertyName||e.name?.kind!==K.Identifier))
     problem('export-form','only exact type-only provider reexports permitted',statement);
    else {const ns=items.map(e=>identifier(e.name)).sort();imports.push({specifier:spec,names:ns,type_only:true,reexport:true});exports.push(...ns);typeExports.push(...ns);}
   }`);
 runner=replace(runner,"const enumCall=expected.role",String.raw`
    const assigned=frozen?null:rhs?.kind===K.CallExpression&&member(rhs.expression,'Object','freeze')&&rhs.arguments.length===1?rhs.arguments[0]:null;
    const original=assigned?.arguments?.[0],descriptor=assigned?.arguments?.[1],providerName=expected.role==='operation-wrapper'?'execute':'make';
    const wrapper=['operation-wrapper','event-wrapper'].includes(expected.role)&&name===expected.callable&&assigned?.kind===K.CallExpression&&member(assigned.expression,'Object','assign')&&assigned.arguments.length===2&&original?.kind===K.PropertyAccessExpression&&original.expression.kind===K.Identifier&&bindings.has(identifier(original.expression))&&id(original.name,providerName)&&descriptor?.kind===K.ObjectLiteralExpression&&descriptor.properties.length===1&&descriptor.properties[0].kind===K.PropertyAssignment&&id(descriptor.properties[0].name,'descriptor');
    const enumCall=expected.role`);
 runner=replace(runner,"if(id(rhs,name)||frozen||enumCall)","if(id(rhs,name)||frozen||enumCall||wrapper)");
 runner=replace(runner,"...(!native&&i.type_only?{type_only:true}:{})","...(!native&&i.type_only?{type_only:true}:{}),...(!native&&i.reexport?{reexport:true}:{})");
 runner=replace(runner,"const violations=[];let visits=0;",String.raw`
  const support=(selected.support_modules??[]).find(m=>m.relative_path.replace(/\.ts$/,selected.phase==='native'?'.js':'.ts')===relative_path);
  const trustedSupport=!!support&&support.source_sha256===definition.trusted_enum_provider_sha256;
  if(support&&(!trustedSupport||selected.phase==='source'&&hash(fs.readFileSync(file))!==support.source_sha256))throw Error('OPERATION_INTEROP_AUDIT:support source drift');
  const violations=[];let visits=0;`);
 runner=replace(runner,"const visit=(n,depth=0)=>{","const visit=(n,depth=0,inType=false,inMaterialize=false)=>{");
 runner=replace(runner,"const form=forms.get(n.kind);if(form&&violations.length<64)",String.raw`
   const supportError=trustedSupport&&n.kind===K.ClassDeclaration&&n.name&&identifier(n.name)==='EnumContractError'&&n.heritageClauses?.length===1&&n.heritageClauses[0].types?.length===1&&identifier(n.heritageClauses[0].types[0].expression)==='TypeError';
   const form=forms.get(n.kind);if(form&&!supportError&&violations.length<64)`);
 runner=replace(runner,"if(identifiers.has(name)&&violations.length<64)","if(!inType&&identifiers.has(name)&&violations.length<64)");
 runner=replace(runner,"n.forEachChild(child=>visit(child,depth+1));",String.raw`
   const property=e=>e?.kind===K.PropertyAccessExpression?identifier(e.name):e?.kind===K.ElementAccessExpression&&[K.StringLiteral,K.NoSubstitutionTemplateLiteral].includes(e.argumentExpression?.kind)?identifier(e.argumentExpression).slice(1,-1):null;
   if(n.kind===K.CallExpression){
    const expression=n.expression,object=expression.expression,method=property(expression),callee=object?.kind===K.Identifier&&identifier(object)==='Object'?'Object.'+method:'';
    const marker=n.arguments?.[0]&&allowed.has(n.arguments[0])&&id(n.arguments[0],'exports');
    if(['defineProperty','defineProperties','setPrototypeOf','preventExtensions','seal'].includes(method)&&callee&&!(native&&marker)&&!(trustedSupport&&inMaterialize&&method==='defineProperty'))problem('object-mutation',callee,n);
    if(callee==='Object.freeze'&&n.arguments?.some(a=>property(a)==='prototype'))problem('prototype-freeze',callee,n);
   }
   n.forEachChild(child=>visit(child,depth+1,inType||n.kind===K.TypeReference||n.kind===K.TypeQuery,inMaterialize||trustedSupport&&n.kind===K.VariableDeclaration&&n.name&&identifier(n.name)==='materialize'));`);
 return runner;
}
export const CROSS_GENERATOR_OPERATION_AUDIT_RUNNER = createOperationAuditRunner();

