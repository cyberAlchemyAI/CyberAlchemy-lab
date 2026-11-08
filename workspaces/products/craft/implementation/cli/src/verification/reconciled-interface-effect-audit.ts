import {createEffectAuditRunner} from './reconciled-effect-audit.js';
/** Pure Interface closures have no storage, factory or operational provider. */
export const INTERFACE_EFFECT_AUDIT_RUNNER=createEffectAuditRunner('INTERFACE_EFFECT_AUDIT','domainspec.interface-effect-observation/v1-candidate')
 .replace('const visit=(n,depth=0)=>{','const visit=(n,depth=0,inType=false)=>{')
 .replace('if(identifiers.has(name)&&violations.length<64)','if(!inType&&identifiers.has(name)&&violations.length<64)')
 .replace('n.forEachChild(child=>visit(child,depth+1));',String.raw`
   if(n.kind===K.CallExpression){
    const member=e=>e.kind===K.PropertyAccessExpression?identifier(e.name):e.kind===K.ElementAccessExpression&&[K.StringLiteral,K.NoSubstitutionTemplateLiteral].includes(e.argumentExpression?.kind)?identifier(e.argumentExpression).slice(1,-1):null;
    const expression=n.expression,object=expression.expression,method=member(expression),callee=object?.kind===K.Identifier&&identifier(object)==='Object'?'Object.'+method:'';
    if(['defineProperty','defineProperties','setPrototypeOf','preventExtensions','seal'].includes(method)&&callee&&violations.length<64)violations.push({code:'object-mutation',name:callee,offset:n.pos});
    if(callee==='Object.freeze'&&n.arguments?.some(a=>member(a)==='prototype')&&violations.length<64)violations.push({code:'prototype-freeze',name:callee,offset:n.pos});
   }
   n.forEachChild(child=>visit(child,depth+1,inType||n.kind===K.TypeReference||n.kind===K.TypeInterface));
 `);
