/** Resource limits are admission, not proof/solver execution. Open Questions: docs/FORMAL-CLAIMS.md. */
import assert from 'node:assert/strict';
import test from 'node:test';
import {FORMAL_PROPOSITION_LIMITS as L,parseFormalProposition,type FormalSignature} from '../src/formal-claim.js';
const signature:FormalSignature={sorts:[{name:'S'}],functions:[],predicates:[{name:'P',parameter_sorts:[]}],constants:[]};
const parse=(source:string,s=signature)=>parseFormalProposition(source,s,'limits.alch:7');
const limited=(source:string,kind:keyof typeof L,s=signature)=>assert.throws(()=>parse(source,s),(e:any)=>{assert.equal(e.issues?.[0]?.code,'CLAIM_RESOURCE_LIMIT');assert.match(e.issues[0].message,new RegExp(`kind=${kind} limit=${L[kind]}`));assert.match(e.issues[0].path,/^limits\.alch:7@/);assert.equal(e instanceof RangeError,false);return true;});
test('fixed fol-core limits are versioned and immutable',()=>{assert.deepEqual(L,{source_bytes:262144,tokens:65536,ast_nodes:16384,ast_depth:128});assert.equal(Object.isFrozen(L),true);});
test('UTF8 byte admission checks N-1,N,N+1 before lexical/AST work',()=>{
 for(const size of [L.source_bytes-1,L.source_bytes])assert.equal(parse('P()'+' '.repeat(size-3)).kind,'predicate');
 limited('P()'+' '.repeat(L.source_bytes-2),'source_bytes');
 // Unicode whitespace is measured by UTF8 bytes rather than JS character length.
 const source='P()'+'\u2003'.repeat(87380);assert.equal(Buffer.byteLength(source),262143);assert.equal(parse(source).kind,'predicate');limited(source+'  ','source_bytes');
});
test('token admission checks N-1,N,N+1 with AST depth independent of parentheses',()=>{
 const grouped='('.repeat(32766)+'P()'+')'.repeat(32766);
 assert.equal(parse(grouped).kind,'predicate');assert.equal(parse('not '+grouped).kind,'not');
 limited('('.repeat(32767)+'P()'+')'.repeat(32767),'tokens');
});
test('2000 and 10000 enclosing parentheses add no AST depth and never use host recursion',()=>{
 for(const n of [2000,10000])assert.deepEqual(parse('('.repeat(n)+'P()'+')'.repeat(n)),{kind:'predicate',name:'P',arguments:[]});
});
test('AST depth checks N-1,N,N+1 and 10000-not attack',()=>{
 for(const count of [126,127])assert.equal(parse('not '.repeat(count)+'P()').kind,'not');
 limited('not '.repeat(128)+'P()','ast_depth');limited('not '.repeat(10000)+'P()','ast_depth');
});
test('flat left-associative chains are bounded even without parser recursion',()=>{
 assert.equal(parse(Array(128).fill('P()').join(' and ')).kind,'and');limited(Array(129).fill('P()').join(' and '),'ast_depth');
 limited(Array(129).fill('P()').join(' implies '),'ast_depth');
});
test('AST node admission checks N-1,N,N+1 on balanced trees',()=>{
 let expression='P()';for(let n=0;n<13;n++)expression='('+expression+' and '+expression+')';
 assert.equal(parse(expression).kind,'and');assert.equal(parse('not '+expression).kind,'not');limited('not not '+expression,'ast_nodes');
});
test('term function depth is included under predicate nodes',()=>{
 const s:FormalSignature={sorts:[{name:'S'}],functions:[{name:'F',parameter_sorts:['S'],result_sort:'S'}],predicates:[{name:'P',parameter_sorts:['S']}],constants:[{name:'C',sort:'S'}]};
 assert.equal(parse('P('+'F('.repeat(126)+'C'+')'.repeat(127),s).kind,'predicate');limited('P('+'F('.repeat(127)+'C'+')'.repeat(128),'ast_depth',s);
});
test('mixed grouping, function arguments and quantifiers retain typed semantics',()=>{
 const s:FormalSignature={sorts:[{name:'S'}],functions:[{name:'F',parameter_sorts:['S'],result_sort:'S'}],predicates:[{name:'P',parameter_sorts:['S']}],constants:[]};
 const plain='forall x: S: (P(F(x)) implies exists y: S: P(y))';assert.deepEqual(parse('('.repeat(2000)+plain+')'.repeat(2000),s),parse(plain,s));
});
test('quantifier and function attacks terminate with resource diagnostics, malformed grouping stays syntax error',()=>{
 limited('forall x: S: '.repeat(1000)+'P()','ast_depth');
 assert.throws(()=>parse('('.repeat(10000)+'P()'+')'.repeat(9999)),/FOL_SYNTAX/);
 assert.throws(()=>parse('P() iff P() iff P()'),/FOL_SYNTAX/);
 assert.throws(()=>parse('P('),/FOL_SYNTAX/);
});
