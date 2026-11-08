import assert from 'node:assert/strict';
import {after,before,test} from 'node:test';
import {mkdtemp,readFile,readdir,rm,symlink,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {parseFormalProposition,FORMAL_PROPOSITION_LIMITS,FORMAL_PROPOSITION_LIMITS_VERSION,type FormalSignature} from '../src/formal-claim.js';
import {parseDomainSource} from '../src/parser.js';
// Independent bounded differential corpus; no live source replacement.
// Open Questions: r5/evidence/R_FOL and docs/FORMAL-CLAIMS.md.
const src=fileURLToPath(new URL('../src/',import.meta.url));
const root=path.resolve(src,'../../../../../../..');
const beforeimage=path.join(root,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/R_FOL/before-formal-claim.ts');
let staging:string,previous:typeof parseFormalProposition;
before(async()=>{staging=await mkdtemp(path.join(tmpdir(),'alch-fol-independent-'));await writeFile(path.join(staging,'package.json'),'{"type":"module"}\n');for(const file of await readdir(src))if(file!=='formal-claim.ts')await symlink(path.join(src,file),path.join(staging,file));await writeFile(path.join(staging,'formal-claim.ts'),await readFile(beforeimage));previous=(await import(pathToFileURL(path.join(staging,'formal-claim.ts')).href)).parseFormalProposition;});
after(async()=>{if(staging)await rm(staging,{recursive:true,force:true});});
const sig=(extra:Partial<FormalSignature>={}):FormalSignature=>({sorts:[{name:'A'},{name:'B'}],functions:[],predicates:[],constants:[],...extra});
const p=sig({predicates:['P','Q','R'].map(name=>({name,parameter_sorts:[]}))});
const typed=sig({functions:[{name:'F',parameter_sorts:['A'],result_sort:'B'},{name:'G',parameter_sorts:['B','A'],result_sort:'A'}],predicates:[{name:'PA',parameter_sorts:['A']},{name:'PB',parameter_sorts:['B']}],constants:[{name:'CA',sort:'A'},{name:'CB',sort:'B'}]});
const valid:Array<[string,FormalSignature]>=[
 ['P()',sig({predicates:[{name:'P',parameter_sorts:[]}]})],
 ['P() and Q() or R()',p],['P() or Q() and R()',p],['P() implies Q() implies R()',p],['(P() implies Q()) implies R()',p],
 ['P() iff (Q() iff R())',p],['(P() iff Q()) iff R()',p],['not not P() or Q() and R()',p],
 ['forall x: A: exists x: B: x = x',sig()],['(forall x: A: x = x) and (exists x: B: x = x)',sig()],
 ['forall x: A: (exists x: B: x = x) and x = x',sig()],
 ['forall x: A: PA(G(F(x), CA)) and PB(CB)',typed],['forall x: A: F(x) = CB and PA(G(CB, CA)) and PB(F(x))',typed],
 ['forall x: A: x = x implies exists y: A: y = x',sig()],['forall item.id: A: item.id = item.id',sig()],['forall x: A:\n\t x = x',sig()],
];
for(const[index,[source,signature]]of valid.entries())test(`retained parser parity: valid typed AST ${index+1}`,()=>assert.deepEqual(parseFormalProposition(source,signature,'independent.alch:7'),previous(source,signature,'independent.alch:7')));
const invalid:Array<[string,FormalSignature,string]>=[
 ['forall x: Missing: x = x',sig(),'FOL_UNKNOWN_SORT'],['forall x: A: x = y',sig(),'FOL_UNBOUND_VARIABLE'],
 ['forall x: A: exists y: B: x = y',sig(),'FOL_SORT_MISMATCH'],
 ['forall x: A: P(x, x)',sig({predicates:[{name:'P',parameter_sorts:['A']}]}),'FOL_ARITY'],
 ['forall x: B: P(x)',sig({predicates:[{name:'P',parameter_sorts:['A']}]}),'FOL_SORT_MISMATCH'],
 ['forall x: A: F(x,x) = x',sig({functions:[{name:'F',parameter_sorts:['A'],result_sort:'A'}]}),'FOL_ARITY'],
 ['forall x: A: Missing(x) = x',sig(),'FOL_UNKNOWN_SYMBOL'],['forall A: A: A = A',sig(),'FOL_SIGNATURE'],
 ['forall x: A: x = x',sig({constants:[{name:'C',sort:'A'}]}),'FOL_UNUSED_SYMBOL'],
 ['P() iff Q() iff R()',p,'FOL_SYNTAX'],['P() and Q() or R() rubbish',p,'FOL_SYNTAX'],['P() & Q() or R()',p,'FOL_SYNTAX'],
 ['forall x: A: (x = x',sig(),'FOL_SYNTAX'],['forall x: A: x = x)',sig(),'FOL_SYNTAX'],
 ['',sig({sorts:[{name:'A'},{name:'A'}]}),'FOL_DUPLICATE_SYMBOL'],['',sig({sorts:[]}),'FOL_SIGNATURE'],
];
function diagnostic(parse:typeof parseFormalProposition,source:string,signature:FormalSignature){try{parse(source,signature,'independent.alch:7');assert.fail('expected rejection');}catch(error){const issues=(error as any).issues;assert.ok(Array.isArray(issues),String(error));return issues;}}
for(const[index,[source,signature,code]]of invalid.entries())test(`retained parser parity: semantic diagnostic ${index+1}`,()=>{const before=diagnostic(previous,source,signature),now=diagnostic(parseFormalProposition,source,signature);assert.equal(now[0].code,code);assert.deepEqual(now,before);});
test('exact versioned four budgets contain no parentheses-only budget',()=>{assert.equal(FORMAL_PROPOSITION_LIMITS_VERSION,'fol-core-proposition-limits/v1');assert.deepEqual(FORMAL_PROPOSITION_LIMITS,{source_bytes:262144,tokens:65536,ast_nodes:16384,ast_depth:128});assert.ok(Object.isFrozen(FORMAL_PROPOSITION_LIMITS));});
test('equality term descendants count toward AST depth',()=>{const signature=sig({functions:[{name:'F',parameter_sorts:['A'],result_sort:'A'}],constants:[{name:'C',sort:'A'}]});const source=(count:number)=>`${'F('.repeat(count)}C${')'.repeat(count)} = C`;assert.equal(parseFormalProposition(source(126),signature).kind,'equal');assert.equal(previous(source(127),signature).kind,'equal');const failure=diagnostic(parseFormalProposition,source(127),signature);assert.equal(failure[0].code,'CLAIM_RESOURCE_LIMIT');assert.match(failure[0].message,/kind=ast_depth limit=128/);});
const app=(proposition:string)=>`domain audit "Audit"\nprofile application-v1\nowner audit\nentity Item:\n  itemId UInt64\n  identity itemId\nformal-claim TestClaim:\n  profile fol-core/1-candidate\n  sort Item\n  predicate P()\n  proposition ${proposition}\n  ceiling "Parser only."\nrule Allowed:\n  claim TestClaim\n`;
test('application parser propagates resource rejection without legacy fallback',()=>{assert.throws(()=>parseDomainSource(app('not '.repeat(128)+'P()')),error=>{const issues=(error as any).issues;assert.ok(Array.isArray(issues));assert.equal(issues[0].code,'CLAIM_RESOURCE_LIMIT');assert.match(issues[0].message,/kind=ast_depth limit=128/);assert.match(issues[0].path,/^\$line:11@\d+$/);return true;});});
test('application source accepts deep grouping without deeper formal AST',()=>{const parsed=parseDomainSource(app('('.repeat(10000)+'P()'+')'.repeat(10000)));assert.equal((parsed.carrier.formal_claims as any[])[0].proposition.kind,'predicate');});
