/** Core-owned EBNF expression data. No Alch parser implementation is imported.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=new URL('../../',import.meta.url),args=process.argv.slice(2);
if(args.some(x=>x!=='--write')||args.length>1)throw Error('only --write is supported');
const grammar=readFileSync(new URL('docs/COMMERCE-GRAMMAR-V1.ebnf',root),'utf8');
const contract=JSON.parse(readFileSync(new URL('tools/commerce-contracts/source-contract.json',root),'utf8'));
const raw=grammar.replace(/\(\*[\s\S]*?\*\)/g,''),words=raw.match(/"(?:[^"\\]|\\.)*"|[A-Za-z_][A-Za-z0-9_-]*|[=;,|()[\]{}]/g)??[];
// Reject unrecognized grammar bytes instead of silently dropping them.
if(raw.replace(/"(?:[^"\\]|\\.)*"|[A-Za-z_][A-Za-z0-9_-]*|[=;,|()[\]{}]|\s/g,''))throw Error('unknown EBNF syntax');
let at=0;
const expect=x=>{if(words[at++]!==x)throw Error('expected '+x+' at '+at);};
function alt(){const nodes=[seq()];while(words[at]==='|'){at++;nodes.push(seq());}return nodes.length===1?nodes[0]:{op:'alt',nodes};}
function seq(){const nodes=[atom()];while(words[at]===','){at++;nodes.push(atom());}return nodes.length===1?nodes[0]:{op:'seq',nodes};}
function atom(){const t=words[at++];if(!t)throw Error('unexpected EBNF end');
 if(t==='['||t==='{'||t==='('){const node=alt();expect({'[':']','{':'}','(':')'}[t]);return t==='('?node:{op:t==='['?'maybe':'many',node};}
 return t.startsWith('"')?{op:'literal',value:JSON.parse(t)}:{op:'rule',value:t};
}
const rules={};while(at<words.length){const id=words[at++];expect('=');if(Object.hasOwn(rules,id))throw Error('duplicate EBNF rule');rules[id]=alt();expect(';');}
const terminals=new Set(['NAME','STEP_NAME','PROTOCOL_NAME','NATURAL','JSON_STRING','REFERENCE','REFERENCE_COMPONENT','NEWLINE','INDENT','DEDENT']);
const inspect=n=>{if(n.op==='rule'&&!Object.hasOwn(rules,n.value)&&!terminals.has(n.value))throw Error('undefined '+n.value);if(n.nodes)n.nodes.forEach(inspect);if(n.node)inspect(n.node);};Object.values(rules).forEach(inspect);
const hash=createHash('sha256').update(grammar).digest('hex');
const output='// GENERATED Core EBNF data; tools/commerce-contracts/core-grammar.mjs owns it.\n// Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions.\n'+
 'export type CoreGrammarNode={readonly op:"rule";readonly value:string}|{readonly op:"literal";readonly value:string}|{readonly op:"seq";readonly nodes:readonly CoreGrammarNode[]}|{readonly op:"alt";readonly nodes:readonly CoreGrammarNode[]}|{readonly op:"many";readonly node:CoreGrammarNode}|{readonly op:"maybe";readonly node:CoreGrammarNode};\n'+
 `export const CORE_COMMERCE_GRAMMAR_SHA256=${JSON.stringify(hash)};\n`+
 `export const CORE_COMMERCE_RESERVED:readonly string[]=${JSON.stringify(contract.lexer.reserved_names)};\n`+
 `export const CORE_COMMERCE_GRAMMAR:Readonly<Record<string,CoreGrammarNode>>=${JSON.stringify(rules,null,1)};\n`;
const target=new URL('src/commerce/commerce-core-grammar.ts',root);
if(args.includes('--write'))writeFileSync(target,output);else if(readFileSync(target,'utf8')!==output)throw Error('Core grammar projection differs: '+fileURLToPath(target));
process.stdout.write(JSON.stringify({status:args.length?'materialized':'checked',rules:Object.keys(rules).length,grammar_sha256:hash,authority_effect:'none'})+'\n');
