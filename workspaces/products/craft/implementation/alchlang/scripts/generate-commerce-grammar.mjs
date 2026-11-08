/** Maintainer-only deterministic Core grammar projection. Runtime uses local data.
 * Open Questions: private EC06/CONTEXT.md. */
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const options=new Map();const args=process.argv.slice(2);let write=false;
for(let i=0;i<args.length;i++){if(args[i]==='--write'){write=true;continue;}if(!['--grammar','--contract','--output'].includes(args[i])||!args[i+1]||options.has(args[i]))throw Error('explicit unique --grammar --contract --output required');options.set(args[i],args[++i]);}
for(const key of ['--grammar','--contract','--output'])if(!options.has(key))throw Error('missing '+key);
const raw=readFileSync(options.get('--grammar'),'utf8'),contract=JSON.parse(readFileSync(options.get('--contract'),'utf8'));
const text=raw.replace(/\(\*[\s\S]*?\*\)/g,''),scan=/"(?:[^"\\]|\\.)*"|[A-Za-z_][A-Za-z0-9_-]*|[=;,|()\[\]{}]/y,stream=[];
for(let at=0;at<text.length;){if(/\s/.test(text[at])){at++;continue;}scan.lastIndex=at;const m=scan.exec(text);if(!m)throw Error('invalid grammar at '+at);stream.push(m[0]);at=scan.lastIndex;}
const literalScan=/"(?:[^"\\]|\\.)*"|[A-Za-z_][A-Za-z0-9_.-]*(?:#?\/[^\s(),;<>]+|:[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z0-9_.-]+)|[A-Za-z_][A-Za-z0-9_-]*|[0-9]+|=>|<-|->|==|!=|<=|>=|\.\.|[.,:()\[\]<>=+*/;\-]/y;
const literalTokens=value=>{const out=[];for(let at=0;at<value.length;){if(/\s/.test(value[at])){at++;continue;}literalScan.lastIndex=at;const m=literalScan.exec(value);if(!m)throw Error('unsupported grammar literal '+value);out.push({literal:m[0]});at=literalScan.lastIndex;}return out;};
let position=0,synthetic=0;const rules=new Map(),references=new Set();
const pop=()=>stream[position++],expect=x=>{if(pop()!==x)throw Error('expected '+x+' at grammar token '+position);};
function choice(){const nodes=[sequence()];while(stream[position]==='|'){position++;nodes.push(sequence());}return {kind:'choice',nodes};}
function sequence(){const nodes=[atom()];while(stream[position]===','){position++;nodes.push(atom());}return {kind:'sequence',nodes};}
function atom(){const token=pop();if(['[','{','('].includes(token)){const node=choice();expect({'[':']','{':'}','(':')'}[token]);return {kind:{'[':'optional','{':'repeat','(':'group'}[token],node};}if(token.startsWith('"'))return {kind:'literal',value:JSON.parse(token)};references.add(token);return {kind:'name',value:token};}
function symbol(node){if(node.kind==='name')return node.value;const name='$'+(++synthetic);rules.set(name,expand(node,name));return name;}
function expand(node,self){switch(node.kind){case'name':return [[node.value]];case'literal':return [literalTokens(node.value)];case'sequence':return [node.nodes.map(symbol)];case'choice':return node.nodes.flatMap(n=>expand(n,self));case'group':return expand(node.node,self);case'optional':return [[],[symbol(node.node)]];case'repeat':if(!self)throw Error('repeat needs own production');return [[],[symbol(node.node),self]];default:throw Error('unknown grammar form');}}
while(position<stream.length){const name=pop();expect('=');const node=choice();expect(';');if(rules.has(name))throw Error('duplicate rule '+name);rules.set(name,expand(node,name));}
const terminals=new Set(['NAME','STEP_NAME','PROTOCOL_NAME','NATURAL','JSON_STRING','REFERENCE','REFERENCE_COMPONENT','NEWLINE','INDENT','DEDENT']);for(const name of references)if(!rules.has(name)&&!terminals.has(name))throw Error('undefined grammar symbol '+name);
const rows=[...rules].flatMap(([lhs,bodies])=>bodies.map(rhs=>({lhs,rhs})));const hash=createHash('sha256').update(raw).digest('hex');
const output=`// GENERATED from Core COMMERCE-GRAMMAR-V1.ebnf; do not edit.\n// Open Questions: private EC06/CONTEXT.md. Syntax only; no executable authority.\nexport const COMMERCE_GRAMMAR_SHA256=${JSON.stringify(hash)};\nexport const COMMERCE_RESERVED_NAMES=Object.freeze(${JSON.stringify(contract.lexer.reserved_names)} as const);\nexport interface CommerceGrammarProduction {readonly lhs:string;readonly rhs:readonly (string|{readonly literal:string})[]}\nexport const COMMERCE_GRAMMAR_PRODUCTIONS:readonly CommerceGrammarProduction[]=${JSON.stringify(rows,null,1)};\n`;
if(write)writeFileSync(options.get('--output'),output);else if(readFileSync(options.get('--output'),'utf8')!==output)throw Error('local commerce grammar data differs from Core');
process.stdout.write(JSON.stringify({status:write?'materialized':'checked',productions:rows.length,named_rules:[...rules.keys()].filter(n=>!n.startsWith('$')).length,grammar_sha256:hash,scope:'syntax data projection only'})+'\n');
