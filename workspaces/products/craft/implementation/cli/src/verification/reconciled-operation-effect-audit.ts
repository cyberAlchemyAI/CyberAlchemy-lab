import {createEffectAuditRunner} from './reconciled-effect-audit.js';
/** Async ports are explicit; the selected Enum support exceptions are not domain classes. */
export const OPERATION_EFFECT_AUDIT_RUNNER=createEffectAuditRunner('OPERATION_EFFECT_AUDIT','domainspec.operation-effect-observation/v1-candidate')
 .replace('const violations=[];let visits=0;',String.raw`
  const support=(selected.support_modules??[]).find(m=>m.relative_path.replace(/\.ts$/,selected.phase==='native'?'.js':'.ts')===relative_path);
  const trustedSupport=!!support&&support.source_sha256===definition.trusted_enum_provider_sha256;
  if(support&&(!trustedSupport||selected.phase==='source'&&hash(fs.readFileSync(file))!==support.source_sha256))throw Error('OPERATION_EFFECT_AUDIT:support source drift');
  const violations=[];let visits=0;
 `)
 .replace('const visit=(n,depth=0)=>{','const visit=(n,depth=0,inType=false,inMaterialize=false)=>{')
 .replace("const form=forms.get(n.kind);if(form&&violations.length<64)",String.raw`
   const supportError=trustedSupport&&n.kind===K.ClassDeclaration&&n.name&&identifier(n.name)==='EnumContractError'&&n.heritageClauses?.length===1&&n.heritageClauses[0].types?.length===1&&identifier(n.heritageClauses[0].types[0].expression)==='TypeError';
   const form=forms.get(n.kind);if(form&&!supportError&&violations.length<64)`)
 .replace('if(identifiers.has(name)&&violations.length<64)','if(!inType&&identifiers.has(name)&&violations.length<64)')
 .replace('n.forEachChild(child=>visit(child,depth+1));',String.raw`
   const member=e=>e?.kind===K.PropertyAccessExpression?identifier(e.name):e?.kind===K.ElementAccessExpression&&[K.StringLiteral,K.NoSubstitutionTemplateLiteral].includes(e.argumentExpression?.kind)?identifier(e.argumentExpression).slice(1,-1):null;
   if(n.kind===K.CallExpression){
    const expression=n.expression,object=expression.expression,method=member(expression),callee=object?.kind===K.Identifier&&identifier(object)==='Object'?'Object.'+method:'';
    if(['defineProperty','defineProperties','setPrototypeOf','preventExtensions','seal'].includes(method)&&callee&&!(trustedSupport&&inMaterialize&&method==='defineProperty')&&violations.length<64)violations.push({code:'object-mutation',name:callee,offset:n.pos});
    if(callee==='Object.freeze'&&n.arguments?.some(a=>member(a)==='prototype')&&violations.length<64)violations.push({code:'prototype-freeze',name:callee,offset:n.pos});
   }
   n.forEachChild(child=>visit(child,depth+1,inType||n.kind===K.TypeReference||n.kind===K.TypeQuery,inMaterialize||trustedSupport&&n.kind===K.VariableDeclaration&&n.name&&identifier(n.name)==='materialize'));
 `);
