/** Commerce source syntax/data, not Core-checked semantics or native custody.
 * Open Questions: private EC06/CONTEXT.md and Core COMMERCE-LOWERING-V1.md. */
import type {CommerceDiagnostic} from './commerce-stages-v1.js';
export interface CommerceSourceSpan {readonly path:string;readonly start:number;readonly end:number}
export interface CommerceToken extends CommerceSourceSpan {readonly text:string;readonly line:number;readonly column:number;readonly layout:'NEWLINE'|'INDENT'|'DEDENT'|null}
export interface CommerceSyntax extends CommerceSourceSpan {readonly kind:string;readonly children:readonly (CommerceSyntax|CommerceToken)[]}
export class CommerceSourceError extends Error {
 readonly diagnostics:readonly CommerceDiagnostic[];
 constructor(code:CommerceDiagnostic['code'],span:CommerceSourceSpan,message:string){
  super(`${code}: ${span.path}:${span.start}: ${message}`);this.name='CommerceSourceError';
  this.diagnostics=Object.freeze([Object.freeze({code,path:span.path,start:span.start,end:span.end,message:Buffer.from(message).subarray(0,4096).toString('utf8')})]);
 }
}
export const commerceSourceHashAlgorithm='sha256' as const;
export type CommerceSourceType =
 {readonly kind:'scalar';readonly name:'UInt64'|'Bool'}|
 {readonly kind:'string'}|{readonly kind:'named';readonly name:string}|
 {readonly kind:'optional';readonly element:CommerceSourceType}|
 {readonly kind:'list';readonly element:CommerceSourceType;readonly max_items:number}|
 {readonly kind:'literal';readonly value:string}|
 {readonly kind:'outcome';readonly state:CommerceSourceType;readonly intent:CommerceSourceType;readonly max_intents:number};
export interface CommerceSourceField {readonly name:string;readonly type:CommerceSourceType;readonly span:CommerceSourceSpan}
export interface CommerceSourceImport {readonly module:string;readonly name:string;readonly alias:string;readonly span:CommerceSourceSpan}
export type CommerceSourceRole='Entity'|'ValueObject'|'Enum'|'Rule'|'Calculation'|'Mapping'|'Query'|'Policy'|'StateMachine'|'Operation'|'Workflow'|'Interface'|'Event';
interface DeclarationBase {readonly id:string;readonly local_name:string;readonly module:string;readonly syntax:CommerceSyntax;readonly span:CommerceSourceSpan}
export interface CommerceRecordSource extends DeclarationBase {readonly kind:'Entity'|'ValueObject'|'Event';readonly fields:readonly CommerceSourceField[];readonly refinement:boolean;readonly identity:readonly string[];readonly unique:readonly (readonly string[])[];readonly immutable:readonly string[]|'all';readonly invariants:readonly CommerceSyntax[]}
export interface CommerceEnumSource extends DeclarationBase {readonly kind:'Enum';readonly variants:readonly {readonly name:string;readonly wire:string|null;readonly fields:readonly CommerceSourceField[];readonly span:CommerceSourceSpan}[]}
export interface CommerceCallableSource extends DeclarationBase {readonly kind:'Rule'|'Calculation'|'Mapping'|'Query'|'Policy'|'StateMachine'|'Operation'|'Workflow';readonly inputs:readonly CommerceSourceField[];readonly contexts:readonly CommerceSourceField[];readonly result:CommerceSourceType|null;readonly body:CommerceSyntax}
export interface CommerceInterfaceSource extends DeclarationBase {readonly kind:'Interface';readonly interface_kind:string;readonly exposes:readonly string[];readonly clauses:readonly CommerceSyntax[]}
export interface CommerceEntrySource extends DeclarationBase {readonly kind:'Entry';readonly invokes:string;readonly interaction:'request-response'|'event';readonly access:CommerceSyntax}
export interface CommerceClaimSource extends DeclarationBase {readonly kind:'FormalClaim';readonly language:'lean4'|'smtlib2'|'alloy'|'tla-plus'|'souffle';readonly reference:string;readonly targets:readonly string[]}
export type CommerceDeclarationSource=CommerceRecordSource|CommerceEnumSource|CommerceCallableSource|CommerceInterfaceSource|CommerceEntrySource|CommerceClaimSource;
export interface CommerceParsedModule {readonly schema_version:'alchlang.commerce-source-syntax/v1-candidate';readonly module:string;readonly version:1;readonly path:string;readonly text:string;readonly sha256:string;readonly bytes:number;readonly imports:readonly CommerceSourceImport[];readonly declarations:readonly CommerceDeclarationSource[];readonly syntax:CommerceSyntax;readonly authority_effect:'none'}
export function sourceFail(code:CommerceDiagnostic['code'],span:CommerceSourceSpan,message:string):never {throw new CommerceSourceError(code,span,message);}
export function commerceSyntaxChildren(node:CommerceSyntax,kind:string):CommerceSyntax[]{return node.children.filter((x):x is CommerceSyntax=>'kind'in x&&x.kind===kind);}
export function commerceSyntaxChild(node:CommerceSyntax,kind:string):CommerceSyntax {return commerceSyntaxChildren(node,kind)[0]??sourceFail('InvalidContract',node,`missing parsed ${kind}`);}
export function commerceSyntaxTokens(node:CommerceSyntax):CommerceToken[]{
 const result:CommerceToken[]=[],stack:(CommerceSyntax|CommerceToken)[]=[node];
 while(stack.length){const item=stack.pop()!;if('text'in item)result.push(item);else for(let i=item.children.length-1;i>=0;i--)stack.push(item.children[i]!);}
 return result;
}
export function commerceSyntaxText(node:CommerceSyntax):string{return commerceSyntaxTokens(node).map(t=>t.text).join('');}
export function commerceSyntaxDescendants(node:CommerceSyntax,kind:string):CommerceSyntax[]{
 const found:CommerceSyntax[]=[],stack=[node];while(stack.length){const item=stack.pop()!;if(item.kind===kind)found.push(item);for(let i=item.children.length-1;i>=0;i--){const child=item.children[i]!;if('kind'in child)stack.push(child);}}return found;
}
