/** Bounded strict source lexer. No value codec or authorization owner.
 * Open Questions: EC06/CONTEXT.md. */
import {sourceFail,type CommerceToken} from './commerce-source-model.js';
export const COMMERCE_SOURCE_LIMITS=Object.freeze({source_bytes:1048576,total_bytes:4194304,modules:32,declarations:256,entries:64,tokens:100000,indent_depth:32,parenthesis_depth:64,chart_states:2000000,parser_work:10000000});
export function commerceRelativePath(value:string):string {
 if(typeof value!=='string'||value.length>4096||!value||value.startsWith('/')||/^[A-Za-z]:/.test(value)||/[\\\x00-\x1f\x7f]/.test(value)||value.split('/').some(p=>!p||p==='.'||p==='..'))sourceFail('InvalidContract',{path:String(value).slice(0,4096),start:0,end:0},'normalized relative source path required');
 return value;
}
const lexical=/"(?:[^"\\]|\\.)*"|[A-Za-z_][A-Za-z0-9_.-]*(?:#?\/[^\s(),;<>]+|:[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z0-9_.-]+)|[A-Za-z_][A-Za-z0-9_-]*|[0-9]+|=>|<-|->|==|!=|<=|>=|\.\.|[.,:()\[\]<>=+*/;\-]/y;
export function lexCommerceSource(text:string,path:string):readonly CommerceToken[]{
 commerceRelativePath(path);const root={path,start:0,end:0};
 if(typeof text!=='string')sourceFail('Syntax',root,'source text required');
 if(Buffer.byteLength(text)>COMMERCE_SOURCE_LIMITS.source_bytes)sourceFail('ResourceLimit',root,'source exceeds byte bound');
 if(Buffer.from(text,'utf8').toString('utf8')!==text)sourceFail('Syntax',root,'source must contain well-formed Unicode scalars');
 const output:CommerceToken[]=[],indents=[0],lines=text.split('\n');let base=0,depth=0;
 const emit=(value:string,line:number,column:number,start:number,end:number,layout:CommerceToken['layout']=null)=>{if(output.length>=COMMERCE_SOURCE_LIMITS.tokens)sourceFail('ResourceLimit',{path,start,end},'source token bound exceeded');output.push(Object.freeze({text:value,line,column,path,start,end,layout}));};
 for(let line=0;line<lines.length;line++){
  const raw=lines[line]!,body=line<lines.length-1&&raw.endsWith('\r')?raw.slice(0,-1):raw;
  if(/[\t\r\0]/.test(body))sourceFail('Syntax',{path,start:base,end:base+Buffer.byteLength(body)},'tabs, bare CR and NUL are forbidden');
  const leading=/^ */.exec(body)![0].length;
  if(!body.slice(leading)||body[leading]==='#'){base+=Buffer.byteLength(raw)+1;continue;}
  if(leading%2)sourceFail('Syntax',{path,start:base,end:base+leading},'two-space indentation required');
  if(leading>indents[indents.length-1]!){if(leading!==indents[indents.length-1]!+2)sourceFail('Syntax',{path,start:base,end:base+leading},'skipped indentation level');if(indents.length>=COMMERCE_SOURCE_LIMITS.indent_depth)sourceFail('ResourceLimit',{path,start:base,end:base+leading},'indentation depth exceeded');indents.push(leading);emit('INDENT',line+1,leading+1,base+leading,base+leading,'INDENT');}
  while(leading<indents[indents.length-1]!){indents.pop();emit('DEDENT',line+1,leading+1,base+leading,base+leading,'DEDENT');}
  if(leading!==indents[indents.length-1])sourceFail('Syntax',{path,start:base,end:base+leading},'inconsistent dedent');
  const offsets:number[]=[0];let units=0,bytes=0;for(const scalar of body){for(let j=0;j<scalar.length;j++)offsets[units+j]=bytes;units+=scalar.length;bytes+=Buffer.byteLength(scalar);offsets[units]=bytes;}
  let at=leading;
  while(at<body.length){
   if(body[at]===' '){at++;continue;}
   if(body[at]==='#'&&(at===0||/\s/.test(body[at-1]!)))break;
   lexical.lastIndex=at;const match=lexical.exec(body);
   if(!match)sourceFail('Syntax',{path,start:base+offsets[at]!,end:base+offsets[at+1]!},'invalid source token');
   const word=match[0],end=at+word.length;
   if(word.startsWith('"')){try{const value:unknown=JSON.parse(word);if(typeof value!=='string'||Buffer.from(value).toString('utf8')!==value)throw Error('scalar');}catch{sourceFail('Syntax',{path,start:base+offsets[at]!,end:base+offsets[end]!},'invalid JSON scalar string');}}
   if(word==='('||word==='['){if(++depth>COMMERCE_SOURCE_LIMITS.parenthesis_depth)sourceFail('ResourceLimit',{path,start:base+offsets[at]!,end:base+offsets[end]!},'parenthesis depth exceeded');}else if(word===')'||word===']')depth--;
   emit(word,line+1,at+1,base+offsets[at]!,base+offsets[end]!);at=end;
  }
  emit('NEWLINE',line+1,body.length+1,base+Buffer.byteLength(body),base+Buffer.byteLength(body),'NEWLINE');base+=Buffer.byteLength(raw)+1;
 }
 const end=Buffer.byteLength(text);while(indents.length>1){indents.pop();emit('DEDENT',lines.length,1,end,end,'DEDENT');}
 return Object.freeze(output);
}
