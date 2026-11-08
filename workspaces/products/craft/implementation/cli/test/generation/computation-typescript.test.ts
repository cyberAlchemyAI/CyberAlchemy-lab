import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import { stripTypeScriptTypes } from 'node:module';
import { generateComputationTypeScript } from '../../src/generation/computation-typescript.ts';
import { checkComputationContract } from '../../src/computation/check.ts';
import { evaluateComputation, evaluateComputationJson, evaluateComputationObserved, evaluateComputationJsonObserved } from '../../src/computation/evaluate.ts';
import { DEFAULT_COMPUTATION_LIMITS, UINT64 as U, BOOL as B } from '../../src/computation/types.ts';
import type { Expr, ComputationContract, ValueType } from '../../src/computation/types.ts';
const literal=(n:string|boolean):Expr=>({op:'literal',type:typeof n==='boolean'?B:U,value:n});
const variable=(name:string):Expr=>({op:'var',name});
const binary=(operator:any,left:Expr,right:Expr):Expr=>({op:'binary',operator,left,right});
const binder=(name:string,type:ValueType=U)=>({name,type});
const base=(expression:Expr,result:ValueType=U,inputs:any[]=[]):ComputationContract=>({schema_version:'domainspec.iteration-expression/v1-candidate',semantics_revision:'ordered-metered-v1-candidate',stage:'full-computation',source_node:'example:computation',records:[],inputs,functions:[],result,rounding:'reject',limits:{...DEFAULT_COMPUTATION_LIMITS},expression});
async function native(c:ComputationContract){const checked=checkComputationContract(c),plan=generateComputationTypeScript(checked);assert(!plan.source.includes('evaluateComputation('));assert(!plan.source.includes('"op":'));assert(!/\bimport\b/.test(plan.source));return {checked,plan,module:await import(`data:text/javascript;base64,${Buffer.from(stripTypeScriptTypes(plan.source)).toString('base64')}`)};}
async function parity(c:ComputationContract,input:unknown,expected:unknown){const n=await native(c),actual=n.module.runComputation(input);assert.equal(actual.ok,true);assert.deepEqual(actual.value,expected);assert.deepEqual(actual,evaluateComputation(n.checked,input));return n;}
const list:ValueType={kind:'list',element:U,max_items:100};

test('native phased filter/map/record fold and model edit change actual source/output',async()=>{
 const c=JSON.parse(fs.readFileSync(new URL('../../examples/computation/record-reducer.craft.json',import.meta.url),'utf8')).contract as ComputationContract;
 const input={orders:[{accepted:true,amount:'500'},{accepted:false,amount:'900'},{accepted:true,amount:'750'}]};
 const n=await parity(c,input,{count:'2',total:'1250'});await parity(c,{orders:[]},{count:'0',total:'0'});
 const overflow={orders:[{accepted:true,amount:'18446744073709551615'},{accepted:true,amount:'1'}]};
 const error=n.module.runComputation(overflow);assert.deepEqual(error,evaluateComputation(n.checked,overflow));assert.equal(error.error.code,'ArithmeticOverflow');assert.deepEqual(error.error.index_path,[1]);assert.deepEqual(error.error.call_path,['summary_step']);
 const edited=structuredClone(c);((edited.functions[0]!.body as any).fields.count.right).value='2';const regenerated=await parity(edited,input,{count:'4',total:'1250'});assert.notEqual(n.plan.source,regenerated.plan.source);
});

test('ordered noncommutative fold and indexed fold retain positions',async()=>{
 const step=binary('add',binary('multiply',variable('state'),literal('10')),variable('item'));
 await parity(base({op:'fold',source:variable('xs'),initial:literal('0'),state:binder('state'),item:binder('item'),body:step},U,[binder('xs',list)]),{xs:['1','2','3']},'123');
 await parity(base({op:'indexed_fold',source:variable('xs'),initial:literal('0'),state:binder('state'),item:binder('item'),index:binder('index'),body:binary('add',variable('state'),variable('index'))},U,[binder('xs',list)]),{xs:['9','9','9']},'3');
});

test('range empty/bounded, repeat and zero-cap guard vectors',async()=>{
 await parity(base({op:'range',start:literal('2'),end:literal('8'),step:literal('2'),max_iterations:3},{kind:'list',element:U,max_items:3}),{},['2','4','6']);
 await parity(base({op:'range',start:literal('8'),end:literal('2'),step:literal('2'),max_iterations:0},{kind:'list',element:U,max_items:0}),{},[]);
 await parity(base({op:'repeat',count:literal('3'),max_iterations:3,initial:literal('0'),state:binder('state'),index:binder('index'),body:binary('add',variable('state'),literal('2'))}),{},'6');
 for(const op of ['while_bounded','until_bounded'] as const){const c=base({op,max_iterations:3,initial:literal('0'),state:binder('state'),guard:binary(op==='while_bounded'?'lt':'gte',variable('state'),literal('3')),body:binary('add',variable('state'),literal('1'))});await parity(c,{},'3');}
 for(const [guard,ok] of [[false,true],[true,false]] as const){const c=base({op:'while_bounded',max_iterations:0,initial:literal('0'),state:binder('state'),guard:literal(guard),body:literal('1')});const n=await native(c),result=n.module.runComputation({});assert.equal(result.fuel_used,3);assert.equal(result.ok,ok);assert.deepEqual(result,evaluateComputation(n.checked,{}));if(!ok)assert.equal(result.error.code,'IterationLimit');}
});

test('exact fuel, first prefix byte checkpoint and first error schedule',async()=>{
 const map=base({op:'map',source:variable('xs'),item:binder('item'),body:variable('item')},list,[binder('xs',list)]);map.limits.fuel=6;const n=await parity(map,{xs:['1','2']},['1','2']);assert.equal(n.module.runComputation({xs:['1','2']}).fuel_used,6);
 map.limits.fuel=5;const short=await native(map),error=short.module.runComputation({xs:['1','2']});assert.deepEqual(error,evaluateComputation(short.checked,{xs:['1','2']}));assert.equal(error.error.code,'ResourceLimit');assert.equal(error.error.expression_path,'$.expression.body');assert.deepEqual(error.error.index_path,[1]);
 map.limits.fuel=100;map.limits.max_value_bytes=4;const bounded=await native(map),result=bounded.module.runComputation({xs:['1','2']});assert.deepEqual(result,evaluateComputation(bounded.checked,{xs:['1','2']}));assert.equal(result.error.code,'OutputBound');
 const late=base({op:'map',source:variable('xs'),item:binder('item'),body:binary('divide',literal('10'),variable('item'))},list,[binder('xs',list)]);const l=await native(late),failure=l.module.runComputation({xs:['2','0','1']});assert.equal(failure.ok,false);assert.equal(failure.error.code,'DivideByZero');assert.deepEqual(failure.error.index_path,[1]);assert.deepEqual(failure,evaluateComputation(l.checked,{xs:['2','0','1']}));
});

test('named Rule/Mapping/Calculation are closed and Policy dispatch skips later failures',async()=>{
 const c=base({op:'policy',declaration:'choose',cases:[{condition:{op:'call',declaration:'yes',arguments:[]},calculation:'first',arguments:[literal('7')]},{condition:binary('eq',binary('divide',literal('1'),literal('0')),literal('0')),calculation:'first',arguments:[literal('9')]}],otherwise:{calculation:'first',arguments:[literal('0')]}} as Expr);
 c.functions=[{name:'yes',kind:'Rule',pure:true,parameters:[],result:B,body:literal(true)},{name:'identity',kind:'Mapping',pure:true,parameters:[binder('value')],result:U,body:variable('value')},{name:'first',kind:'Calculation',pure:true,parameters:[binder('value')],result:U,body:{op:'call',declaration:'identity',arguments:[variable('value')]}}];c.functions.push({name:'choose',kind:'Policy',pure:true,parameters:[],result:U,body:c.expression});c.expression={op:'call',declaration:'choose',arguments:[]};await parity(c,{},'7');
});

test('stable multikey numeric lexical/natural ordering with duplicates',async()=>{
 const str:ValueType={kind:'string',max_bytes:32},row:ValueType={kind:'record',name:'row'},rows:ValueType={kind:'list',element:row,max_items:100};
 const field=(name:string):Expr=>({op:'field',value:variable('row'),field:name});
 for(const mode of ['lexical','natural'] as const){const c=base({op:'sort',source:variable('rows'),item:binder('row',row),keys:[{value:field('group'),direction:'asc',mode:'numeric'},{value:field('label'),direction:'asc',mode}]},rows,[binder('rows',rows)]);c.records=[{name:'row',fields:{group:U,label:str,id:U}}];const input={rows:[{group:'1',label:'file10',id:'0'},{group:'0',label:'file2',id:'1'},{group:'1',label:'file2',id:'2'},{group:'1',label:'file2',id:'3'}]};const order=mode==='natural'?[1,2,3,0]:[1,0,2,3];await parity(c,input,order.map(n=>input.rows[n]));}
});

test('match selected branch and pure StateMachine outcomes/intents',async()=>{
 await parity(base({op:'match',value:literal('5'),binding:binder('candidate'),cases:[{when:binary('eq',variable('candidate'),literal('5')),then:literal('9')}],otherwise:binary('divide',literal('1'),literal('0'))}),{},'9');
 const expression:Expr={op:'state_machine',declaration:'progress',state:variable('start'),event:literal(true),state_binding:binder('state'),event_binding:binder('event',B),transitions:[{guard:variable('event'),next:binary('add',variable('state'),literal('1')),intents:[literal('4')]}],otherwise:'stay',intent_type:U,max_intents:1} as Expr;
 const outcome:ValueType={kind:'outcome',state:U,intent:U,max_intents:1};const c=base({op:'call',declaration:'progress',arguments:[variable('start')]},outcome,[binder('start')]);c.functions=[{name:'progress',kind:'StateMachine',pure:true,parameters:[binder('start')],result:outcome,body:expression}];await parity(c,{start:'6'},{tag:'transition',state:'7',intents:['4'],machine:'progress',branch:'transition:0',reason:'matched'});
 (c.functions[0]!.body as any).transitions=[];await parity(c,{start:'6'},{tag:'stayed',state:'6',intents:[],machine:'progress',branch:'otherwise',reason:'no-match-stay'});(c.functions[0]!.body as any).otherwise='reject';await parity(c,{start:'6'},{tag:'rejected',state:'6',intents:[],machine:'progress',branch:'otherwise',reason:'no-match-reject'});
});

test('JSON and inert boundary malformed input, duplicate keys, Unicode, byte caps',async()=>{
 const c=base(variable('x'),U,[binder('x')]),n=await native(c);
 for(const input of [{x:1},{x:'01'},{x:'18446744073709551616'},{x:'0',extra:true},{}])assert.deepEqual(n.module.runComputation(input),evaluateComputation(n.checked,input));
 for(const input of ['{"x":"1","x":"2"}','{"x":"1"} trailing','{"x":"\\ud800"}','{"x":"2"}'])assert.deepEqual(n.module.runComputationJson(input),evaluateComputationJson(n.checked,input));
 let invoked=0;const getter={get x(){invoked++;return '1';}};assert.equal(n.module.runComputation(getter).ok,false);assert.equal(invoked,0);
 const sparse:any[]=[];sparse.length=1;const lists=await native(base({op:'fold',source:variable('xs'),initial:literal('0'),state:binder('state'),item:binder('item'),body:variable('state')},U,[binder('xs',list)]));assert.equal(lists.module.runComputation({xs:sparse}).ok,false);
});

test('sort comparison resource paths and natural leading zeros/Unicode are exact',async()=>{
 const str:ValueType={kind:'string',max_bytes:32},strings:ValueType={kind:'list',element:str,max_items:100};
 const c=base({op:'sort',source:variable('xs'),item:binder('item',str),keys:[{value:variable('item'),direction:'asc',mode:'natural'}]},strings,[binder('xs',strings)]);c.limits.fuel=10;
 const n=await native(c),failure=n.module.runComputation({xs:['3','2','1']});assert.deepEqual(failure,evaluateComputation(n.checked,{xs:['3','2','1']}));assert.equal(failure.error.code,'ResourceLimit');assert.deepEqual(failure.error.index_path,[2,1,0]);
 c.limits.fuel=1000;await parity(c,{xs:['x002','x2','x02','😀','\ue000']},['x2','x02','x002','\ue000','😀']);
});

test('bounds precede unused seed failures and all filtered predicates finish before mapping',async()=>{
 const c=base({op:'repeat',count:literal('2'),max_iterations:1,initial:binary('divide',literal('1'),literal('0')),state:binder('state'),index:binder('index'),body:literal('0')});const n=await native(c),failure=n.module.runComputation({});assert.deepEqual(failure,evaluateComputation(n.checked,{}));assert.equal(failure.error.code,'IterationBound');assert.equal(failure.error.expression_path,'$.expression.count');assert.equal(failure.fuel_used,2);
 const filter:Expr={op:'filter',source:variable('xs'),item:binder('candidate'),predicate:binary('eq',binary('divide',literal('1'),variable('candidate')),literal('1'))};
 const phased=base({op:'map',source:filter,item:binder('item'),body:binary('divide',literal('1'),literal('0'))},list,[binder('xs',list)]);const p=await native(phased),result=p.module.runComputation({xs:['1','0']});assert.deepEqual(result,evaluateComputation(p.checked,{xs:['1','0']}));assert.equal(result.error.expression_path,'$.expression.source.predicate.left');assert.deepEqual(result.error.index_path,[1]);
});

test('owned policy action and named nested failures retain branch and full call path',async()=>{
 const c=base({op:'call',declaration:'choose',arguments:[]});c.functions=[{name:'bad',kind:'Calculation',pure:true,parameters:[],result:U,body:binary('divide',literal('1'),literal('0'))},{name:'choose',kind:'Policy',pure:true,parameters:[],result:U,body:{op:'policy',declaration:'choose',cases:[{condition:literal(true),calculation:'bad',arguments:[]}],otherwise:{calculation:'bad',arguments:[]}}}];const n=await native(c),result=n.module.runComputation({});assert.deepEqual(result,evaluateComputation(n.checked,{}));assert.equal(result.error.expression_path,'$.functions[0].body');assert.deepEqual(result.error.call_path,['choose','bad']);
 c.limits.fuel=4;const b=await native(c),limited=b.module.runComputation({});assert.deepEqual(limited,evaluateComputation(b.checked,{}));assert.equal(limited.error.expression_path,'$.functions[1].body.cases[0]');assert.deepEqual(limited.error.call_path,['choose','bad']);
});

test('outcome field elimination supports tagged matching',async()=>{
 const tag:ValueType={kind:'string',max_bytes:10},outcome:ValueType={kind:'outcome',state:U,intent:U,max_intents:1};
 const field=(key:string):Expr=>({op:'field',value:variable('candidate'),field:key});
 const c=base({op:'match',value:variable('result'),binding:binder('candidate',outcome),cases:[{when:binary('eq',field('tag'),{op:'literal',type:tag,value:'transition'}),then:field('state')}],otherwise:literal('0')},U,[binder('result',outcome)]);
 await parity(c,{result:{tag:'transition',state:'9',intents:['4'],machine:'progress',branch:'transition:0',reason:'matched'}},'9');await parity(c,{result:{tag:'stayed',state:'9',intents:[],machine:'progress',branch:'otherwise',reason:'no-match-stay'}},'0');const n=await native(c);for(const tag of [{},null,1,true,[]]){const input={result:{tag,state:'9',intents:[],machine:'progress',branch:'otherwise',reason:'no-match-stay'}};assert.deepEqual(n.module.runComputation(input),evaluateComputation(n.checked,input));}
});

test('lexical let/conditional Boolean branches and arithmetic rounding remain explicit',async()=>{
 const bad= binary('divide',literal('1'),literal('0'));
 const c=base({op:'let',binding:binder('flag',B),value:literal(true),body:{op:'if',condition:binary('and',variable('flag'),{op:'unary',operator:'not',value:literal(false)}),then:literal('9'),else:bad}});
 const n=await parity(c,{},'9');assert.equal(n.module.runComputation({}).fuel_used,8);
 await parity(base(binary('or',literal(true),binary('eq',bad,literal('0'))),B),{},true);
 for(const [rounding,expected] of [['floor','2'],['ceil','3']] as const){const arithmetic=base(binary('divide',literal('5'),literal('2')));arithmetic.rounding=rounding;await parity(arithmetic,{},expected);}
 const reject=await native(base(binary('divide',literal('5'),literal('2')))),failure=reject.module.runComputation({});assert.equal(failure.error.code,'InexactDivision');assert.deepEqual(failure,evaluateComputation(reject.checked,{}));
});

test('native execution preserves every retained formal fuel/error/encoding vector',async()=>{
 const vectors=JSON.parse(fs.readFileSync(new URL('../../../../../../../research/craft-alchlang-formal-iteration-2026-10-13/design-examples/encoding-budget.cases.json',import.meta.url),'utf8'));
 for(const row of vectors.budget_cases){const c=base(row.expression,row.expression.op==='map'?list:U,Object.hasOwn(row.inputs,'xs')?[binder('xs',list)]:[]);c.stage=row.stage;c.limits.fuel=row.fuel;if(row.max_value_bytes)c.limits.max_value_bytes=row.max_value_bytes;if(row.rounding)c.rounding=row.rounding;const n=await native(c),actual=n.module.runComputation(row.inputs);assert.deepEqual(actual,evaluateComputation(n.checked,row.inputs),row.id);if(row.expected.kind==='value'){assert.equal(actual.ok,true,row.id);assert.deepEqual(actual.value,row.expected.value,row.id);}else {assert.equal(actual.ok,false,row.id);assert.equal(actual.error.code,row.expected.code,row.id);assert.equal(actual.error.expression_path,'$.expression'+row.expected.expression_path.map((key:string)=>'.'+key).join(''),row.id);assert.deepEqual(actual.error.index_path,row.expected.index_path,row.id);assert.deepEqual(actual.error.call_path,row.expected.call_path,row.id);}}
 const n=await native(base(literal('0')));for(const vector of vectors.encoding_vectors){const encoded=Buffer.from(n.module.canonicalComputationJson(vector.value));assert.equal(encoded.toString('hex'),vector.expected_hex);assert.equal(encoded.length,vector.expected_bytes);}
});

test('outcome provenance fields have qualified types and reject inconsistent wire metadata',async()=>{
 const outcome:ValueType={kind:'outcome',state:U,intent:U,max_intents:1};
 const valid={tag:'transition',state:'9',intents:['4'],machine:'progress',branch:'transition:0',reason:'matched'};
 for(const [field,type,expected] of [['machine',{kind:'string',max_bytes:128},'progress'],['branch',{kind:'string',max_bytes:32},'transition:0'],['reason',{kind:'string',max_bytes:32},'matched']] as const){const c=base({op:'field',value:variable('result'),field},type as ValueType,[binder('result',outcome)]);await parity(c,{result:valid},expected);}
 const n=await native(base(variable('result'),outcome,[binder('result',outcome)]));
 for(const changed of [{machine:'BadMachine'},{branch:'transition:64'},{branch:'transition:00'},{reason:'no-match-stay'},{tag:'stayed'},{machine:null},{reason:4}]){const input={result:{...valid,...changed}},actual=n.module.runComputation(input);assert.deepEqual(actual,evaluateComputation(n.checked,input));assert.equal(actual.ok,false);}
});

test('observed Policy proves equal-value targets selected and invoked without changing normal fuel/result',async()=>{
 const c=base({op:'call',declaration:'select',arguments:[variable('choice')]},U,[binder('choice',B)]);
 c.functions=[{name:'first',kind:'Calculation',pure:true,parameters:[binder('value')],result:U,body:variable('value')},{name:'second',kind:'Calculation',pure:true,parameters:[binder('value')],result:U,body:variable('value')},{name:'select',kind:'Policy',pure:true,parameters:[binder('flag',B)],result:U,body:{op:'policy',declaration:'select',cases:[{condition:variable('flag'),calculation:'first',arguments:[literal('7')]}],otherwise:{calculation:'second',arguments:[literal('7')]}}}];
 for(const choice of [true,false]){const n=await native(c),input={choice},observed=n.module.runComputationObserved(input);assert.deepEqual(observed,evaluateComputationObserved(n.checked,input));assert.deepEqual(observed.result,n.module.runComputation(input));assert.deepEqual(observed.result.value,'7');assert.equal(observed.observation_status,'complete');assert.deepEqual(observed.policy_decisions,[{policy:'select',branch:choice?'case:0':'otherwise',calculation:choice?'first':'second',expression_path:'$.functions[2].body',index_path:[],call_path:['select'],invocation_entered:true}]);assert.deepEqual(n.module.runComputationJsonObserved(JSON.stringify(input)),evaluateComputationJsonObserved(n.checked,JSON.stringify(input)));}
 const failures=structuredClone(c);((failures.functions[2]!.body as any).cases[0].arguments)[0]=binary('divide',literal('1'),literal('0'));const failed=await native(failures),argumentFailure=failed.module.runComputationObserved({choice:true});assert.deepEqual(argumentFailure,evaluateComputationObserved(failed.checked,{choice:true}));assert.equal(argumentFailure.result.error.code,'DivideByZero');assert.equal(argumentFailure.policy_decisions[0].invocation_entered,false);
 for(const [fuel,entered] of [[6,false],[7,true]] as const){const limited=structuredClone(c);limited.limits.fuel=fuel;const n=await native(limited),observed=n.module.runComputationObserved({choice:true});assert.deepEqual(observed,evaluateComputationObserved(n.checked,{choice:true}));assert.equal(observed.result.error.code,'ResourceLimit');assert.equal(observed.policy_decisions[0].invocation_entered,entered);assert.deepEqual(observed.result,n.module.runComputation({choice:true}));}
});

test('Policy observation collector truncates bounded prefix without changing evaluation or logical fuel',async()=>{
 const c=base({op:'map',source:variable('xs'),item:binder('item'),body:binary('add',{op:'call',declaration:'select',arguments:[]},{op:'call',declaration:'select',arguments:[]})},list,[binder('xs',list)]);
 c.functions=[{name:'seven',kind:'Calculation',pure:true,parameters:[],result:U,body:literal('7')},{name:'select',kind:'Policy',pure:true,parameters:[],result:U,body:{op:'policy',declaration:'select',cases:[],otherwise:{calculation:'seven',arguments:[]}}}];
 const input={xs:Array(100).fill('0')},n=await native(c),observed=n.module.runComputationObserved(input);assert.deepEqual(observed,evaluateComputationObserved(n.checked,input));assert.equal(observed.observation_status,'truncated');assert.equal(observed.policy_decisions.length,100);assert.deepEqual(observed.result,n.module.runComputation(input));assert.deepEqual(observed.result.value,Array(100).fill('14'));assert.equal(Buffer.byteLength(JSON.stringify(observed.policy_decisions))<=65536,true);assert.deepEqual(observed.policy_decisions[99].index_path,[49]);assert(observed.policy_decisions.every((row:any)=>row.invocation_entered));
 const one=n.module.runComputationObserved({xs:['0']});assert.equal(one.observation_status,'complete');assert.equal(one.policy_decisions.length,2);
});

test('Policy observation byte ceiling and nested argument selection preserve causal prefix and results',async()=>{
 const long=(n:number)=>'fn'+n+'_'+'x'.repeat(120),policy='policy_'+'p'.repeat(120),target='calc_'+'c'.repeat(120);
 const c=base({op:'map',source:variable('xs'),item:binder('item'),body:{op:'call',declaration:long(0),arguments:[]}},list,[binder('xs',list)]);
 for(let n=0;n<20;n++)c.functions.push({name:long(n),kind:'Calculation',pure:true,parameters:[],result:U,body:{op:'call',declaration:n===19?policy:long(n+1),arguments:[]}});
 c.functions.push({name:policy,kind:'Policy',pure:true,parameters:[],result:U,body:{op:'policy',declaration:policy,cases:[],otherwise:{calculation:target,arguments:[]}}},{name:target,kind:'Calculation',pure:true,parameters:[],result:U,body:literal('1')});
 const input={xs:Array(100).fill('1')},n=await native(c),observed=n.module.runComputationObserved(input);assert.deepEqual(observed,evaluateComputationObserved(n.checked,input));assert.equal(observed.observation_status,'truncated');assert(observed.policy_decisions.length<100);assert(Buffer.byteLength(JSON.stringify(observed.policy_decisions))<=65536);assert.deepEqual(observed.result,n.module.runComputation(input));assert.deepEqual(observed.result.value,Array(100).fill('1'));
 const nested=base({op:'call',declaration:'parent',arguments:[]});nested.functions=[{name:'identity',kind:'Calculation',pure:true,parameters:[binder('n')],result:U,body:variable('n')},{name:'constant',kind:'Calculation',pure:true,parameters:[],result:U,body:literal('9')},{name:'child',kind:'Policy',pure:true,parameters:[],result:U,body:{op:'policy',declaration:'child',cases:[],otherwise:{calculation:'constant',arguments:[]}}},{name:'parent',kind:'Policy',pure:true,parameters:[],result:U,body:{op:'policy',declaration:'parent',cases:[],otherwise:{calculation:'identity',arguments:[{op:'call',declaration:'child',arguments:[]}]}}}];
 const p=await native(nested),trace=p.module.runComputationObserved({});assert.deepEqual(trace,evaluateComputationObserved(p.checked,{}));assert.deepEqual(trace.result.value,'9');assert.deepEqual(trace.policy_decisions.map((row:any)=>({policy:row.policy,calls:row.call_path,entered:row.invocation_entered})),[{policy:'parent',calls:['parent'],entered:true},{policy:'child',calls:['parent','child'],entered:true}]);
 const plain=await native(base(literal('2')));assert.deepEqual(plain.module.runComputationObserved({}),{result:{ok:true,value:'2',fuel_used:1},policy_decisions:[],observation_status:'complete'});assert.deepEqual(plain.module.runComputationJsonObserved('{"x":1,"x":2}'),evaluateComputationJsonObserved(plain.checked,'{"x":1,"x":2}'));
});
