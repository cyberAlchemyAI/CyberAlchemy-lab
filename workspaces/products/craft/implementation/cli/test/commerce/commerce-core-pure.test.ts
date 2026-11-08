/** Source-to-typed-AST controls; no evaluator/native/installed runtime claims.
 * Open Questions: docs/COMMERCE-CONTRACTS.md#open-questions. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {checkCoreCommercePureSources,checkCoreCommercePureProposal,type CorePureSemantics} from '../../src/commerce/commerce-core-pure.js';
import {CoreCommerceSourceError} from '../../src/commerce/commerce-core-syntax.js';
import {matchesCoreRefinementPattern} from '../../src/commerce/commerce-core-types.js';
const base=`module Demo version 1
value-object Label:
  carrier String
  utf8-bytes 1..8
  unicode-scalars 1..8
  pattern "^[a-z]{1,8}$"
value-object Item:
  id UInt64
  verified Bool
  label Label
  count UInt64
  invariant count <= 100
value-object Holder:
  item optional<Item>
enum Status:
  value Open
  value Closed
enum Signal:
  value Go
  value Wait
enum Outcome:
  variant Found value Item
  variant Missing key UInt64
  variant Rejected reason Label
interface Application:
  kind application-composition
  formal-claims optional
`;
const source=(extra:string)=>[{path:'application.alch',text:base+extra}];
const check=(extra:string)=>checkCoreCommercePureSources(source(extra));
const decl=(r:CorePureSemantics,name='Eval')=>r.declarations.find(d=>d.name==='Demo.'+name)!;
const calc=(expression:string,result='UInt64',parameters='  input items List<Item,10>\n')=>`\ncalculation Eval:\n  pure\n${parameters}  result ${result}\n  expression ${expression}\n`;
const rule=(expression:string,parameters='  input holder Holder\n')=>`\nrule Eval:\n${parameters}  expression ${expression}\n`;
const failure=(run:()=>unknown,code?:string)=>assert.throws(run,(e:unknown)=>e instanceof CoreCommerceSourceError&&(!code||e.diagnostics[0]!.code===code));
test('all 32 actual commerce pure declarations, 95 value definitions and explicit collection predicates independently typecheck',()=>{
 const root=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)),sources=readdirSync(root,{recursive:true}).filter((f):f is string=>typeof f==='string'&&f.endsWith('.alch')).map(path=>({path,text:readFileSync(root+path,'utf8')})),r=checkCoreCommercePureSources(sources);
 assert.equal(r.declarations.length,32);assert.equal(r.value_declarations.length,95);assert.equal(r.record_invariants.length,57);assert.equal(r.source_refinements.length,4);assert.equal(r.collection_predicates.length,2);assert.equal(r.qualification,'independent-pure-component-data-only');assert.equal(r.authority_effect,'none');
 assert.equal(checkCoreCommercePureSources([...sources].reverse()).pure_subject_sha256,r.pure_subject_sha256);
});
test('pure normalized subject excludes optional assurance and source whitespace',()=>{const a=check(calc('1')),b=check(calc(' 1  ')+'\nformal-claim Claim:\n  language smtlib2\n  source claims/model.smt2\n  targets Eval\n');assert.equal(a.pure_subject_sha256,b.pure_subject_sha256);});
test('value declarations retain fields, enum wire labels and source constraints in normalized subject',()=>{const s=source(calc('1'));const a=checkCoreCommercePureSources(s),b=checkCoreCommercePureSources([{...s[0]!,text:s[0]!.text.replace('value Open','value Open wire "open"')}]);assert.notEqual(a.pure_subject_sha256,b.pure_subject_sha256);assert.equal(a.source_refinements[0]!.min_bytes,1);assert.equal(a.source_refinements[0]!.min_scalars,1);});
test('multiplication precedence survives independent parsing',()=>{const b=decl(check(calc('1 + 2 * 3'))).body;assert.equal(b.op,'binary');if(b.op==='binary'){assert.equal(b.operator,'add');assert.equal(b.right.op,'binary');if(b.right.op==='binary')assert.equal(b.right.operator,'multiply');}});
test('explicit parentheses change the normalized arithmetic AST',()=>{assert.notEqual(check(calc('(1 + 2) * 3')).pure_subject_sha256,check(calc('1 + 2 * 3')).pure_subject_sha256);});
test('division rounding and evaluation error metadata remain source owned',()=>{const r=check(calc('4 / 3').replace('  expression','  rounding floor\n  expression').replace('  expression 4 / 3','  expression 4 / 3\n  on-evaluation-error fail invalid-total'));assert.equal(decl(r).rounding,'floor');assert.deepEqual(decl(r).on_evaluation_error,{kind:'fail',code:'invalid-total'});});
test('a parameter named rounding cannot override Calculation metadata',()=>{const r=check(calc('rounding','UInt64','  input rounding UInt64\n'));assert.equal(decl(r).rounding,'reject');});
test('record Mapping call remains an actual pure call, not a constructor',()=>{const extra='\nmapping Copy:\n  input original Item\n  target Item\n  total true\n  preserve id, verified, label\n  field count <- original.count\n'+calc('Copy(item)','Item','  input item Item\n');const b=decl(check(extra)).body;assert.equal(b.op,'call');if(b.op==='call')assert.equal(b.declaration,'Demo.Copy');});
test('named pure-call arguments retain source evaluation order through hygienic lets',()=>{const extra='\ncalculation Difference:\n  pure\n  input first UInt64\n  input second UInt64\n  result UInt64\n  expression first - second\n'+calc('Difference(second=2,first=3)');const b=decl(check(extra)).body;assert.equal(b.op,'let');if(b.op==='let'){assert.equal(b.value.op,'literal');if(b.value.op==='literal')assert.equal(b.value.value,'2');assert.equal(b.body.op,'let');}});
test('named constructors evaluate in source order and retain declared field layout',()=>{let b=decl(check(calc('Item(count=3,label="abc",verified=true,id=1)','Item'))).body;const order:unknown[]=[];while(b.op==='let'){assert.equal(b.value.op,'literal');if(b.value.op==='literal')order.push(b.value.value);b=b.body;}assert.deepEqual(order,['3','abc',true,'1']);assert.equal(b.op,'record');if(b.op==='record')assert.deepEqual(Object.keys(b.fields),['id','verified','label','count']);});
test('named enum payload constructors retain authored error evaluation order',()=>{const fixture='\nenum PairResult:\n  variant Pair first UInt64 second UInt64\n'+calc('PairResult.Pair(second=4 / 0,first=1 - 2)','PairResult');let b=decl(check(fixture)).body;assert.equal(b.op,'let');if(b.op==='let'){assert.equal(b.value.op,'binary');if(b.value.op==='binary')assert.equal(b.value.operator,'divide');b=b.body;}assert.equal(b.op,'let');if(b.op==='let'){assert.equal(b.value.op,'binary');if(b.value.op==='binary')assert.equal(b.value.operator,'subtract');assert.equal(b.body.op,'enum_value');}});
test('static refinement constructor validates literal domain',()=>{const b=decl(check(calc('Label("abc")','Label'))).body;assert.equal(b.op,'literal');if(b.op==='literal')assert.deepEqual(b.type,{kind:'refinement',name:'Demo.Label'});});
test('explicit dynamic refinement construction retains a checked validation node',()=>{const b=decl(check(calc('Label(raw)','Label','  input raw literal "abc"\n'))).body;assert.equal(b.op,'validate_refinement');if(b.op==='validate_refinement'){assert.equal(b.refinement,'Demo.Label');assert.equal(b.on_invalid,'InputType');assert.deepEqual(b.value,{op:'var',name:'raw'});}});
test('named Policy actions retain their calculation and hygienic source-order expression',()=>{const b=decl(check(baseCalculation+policy.replaceAll('Base(item)','Base(item=item)'))).body;assert.equal(b.op,'policy');if(b.op==='policy'){assert.equal(b.cases[0]!.action.calculation,'Demo.Base');assert.equal(b.cases[0]!.action.expression.op,'let');assert.equal(b.otherwise.expression.op,'let');}});
test('literal-valued fields retain exact value constraints',()=>{const s='\nvalue-object Receipt:\n  kind literal "accepted"\n\nmapping Accept:\n  target Receipt\n  total true\n  field kind <- "accepted"\n';const r=check(s);assert.deepEqual(r.value_declarations.find(d=>d.name==='Demo.Receipt')!.fields[0]!.type,{kind:'literal',value:'accepted'});failure(()=>check(s.replace('field kind <- "accepted"','field kind <- "rejected"')),'TypeMismatch');});
test('Mapping preconditions lower to a typed InputType failure path',()=>{const b=decl(check('\nmapping Eval:\n  input item Item\n  target Item\n  total true\n  requires item.verified\n  preserve id, verified, label\n  field count <- item.count\n')).body;assert.equal(b.op,'require_some');if(b.op==='require_some')assert.equal(b.value.op,'if');});
test('ordered Mapping cases retain authored priority and final fallback',()=>{const b=decl(check('\nmapping Eval:\n  input item Item\n  target UInt64\n  total true\n  ordered-cases:\n    first when item.verified -> 1\n    second when item.count > 1 -> 2\n    fallback otherwise -> 3\n')).body;assert.equal(b.op,'if');if(b.op==='if'){assert.equal(b.then.op,'literal');assert.equal(b.else.op,'if');}});
test('map/fold and nested checked arithmetic produce typed existing pure ASTs',()=>{const b=decl(check(calc('fold(map(items,item:Item => item.count),0,total:UInt64,amount:UInt64 => checked-add(total,amount))'))).body;assert.equal(b.op,'fold');if(b.op==='fold')assert.equal(b.source.op,'map');});
test('indexed fold adds a checked UInt64 index',()=>assert.equal(decl(check(calc('indexed-fold(items,0,total:UInt64,item:Item,index:UInt64 => total + item.count + index)'))).body.op,'indexed_fold'));
test('bounded repeat carries count, maximum and stable state/index types',()=>{const b=decl(check(calc('repeat(3,max 10,0,total:UInt64,index:UInt64 => total + index)'))).body;assert.equal(b.op,'repeat');if(b.op==='repeat')assert.equal(b.max_iterations,10);});
for(const loop of ['while-bounded','until-bounded'])test(loop+' retains a Bool guard and typed state',()=>assert.equal(decl(check(calc(`${loop}(max 10,0,total:UInt64,total < 3 => total + 1)`))).body.op,loop.replace('-','_')));
test('range remains finite and end-exclusive data for the successor engine',()=>{const b=decl(check(calc('range(0,10,1,max 10)','List<UInt64,10>'))).body;assert.equal(b.op,'range');if(b.op==='range')assert.equal(b.max_iterations,10);});
test('filter requires Bool predicate and preserves source list bound',()=>{const r=decl(check(calc('filter(items,item:Item => item.verified)','List<Item,10>')));assert.deepEqual(r.result,{kind:'List',value:{kind:'record',name:'Demo.Item'},maximum:10});assert.equal(r.body.op,'filter');});
test('simple numeric sorting resolves declared field and stable mode',()=>{const b=decl(check(calc('sort(items,count descending numeric)','List<Item,10>'))).body;assert.equal(b.op,'sort');if(b.op==='sort')assert.deepEqual(b.keys.map(k=>[k.direction,k.mode]),[['desc','numeric']]);});
test('multi-key sorting retains key order and normalizes binary-utf8',()=>{const b=decl(check(calc('sort(items,item:Item => [item.label ascending binary-utf8,item.count descending numeric])','List<Item,10>'))).body;assert.equal(b.op,'sort');if(b.op==='sort')assert.deepEqual(b.keys.map(k=>k.mode),['lexical','numeric']);});
test('inferred literal-string lists remain bounded without equating different literals',()=>assert.equal(decl(check(calc('length(["a","bb"])'))).body.op,'length'));
test('different literal strings may be compared as bounded scalar values',()=>assert.equal(decl(check(rule('"one" != "two"'))).body.op,'unary'));
test('some/none use declared optional expected types',()=>{assert.equal(decl(check(calc('some(1)','optional<UInt64>'))).body.op,'some');assert.equal(decl(check(calc('none','optional<UInt64>'))).body.op,'none');});
test('optional match lowers a single capture and narrowed payload path',()=>{const b=decl(check(calc('match holder.item some(found) => found.count else 0','UInt64','  input holder Holder\n'))).body;assert.equal(b.op,'let');if(b.op==='let')assert.equal(b.body.op,'if');});
for(const expression of ['present(holder.item) and holder.item.count > 0','absent(holder.item) or holder.item.count > 0','not absent(holder.item) and holder.item.count > 0','present(holder.item) and present(holder.item) and holder.item.count > 0'])test('checked short-circuit narrowing: '+expression,()=>assert.equal(decl(check(rule(expression))).result.kind,'Bool'));
test('optional fields require explicit unwrap on an unguarded path',()=>{assert.equal(decl(check(calc('require-some(holder.item).count','UInt64','  input holder Holder\n'))).body.op,'field');failure(()=>check(calc('holder.item.count','UInt64','  input holder Holder\n')),'TypeMismatch');});
const matchRule='\nrule Eval:\n  input outcome Outcome\n  expression match outcome:\n    Found(value) => value.verified\n    Missing(key) => key == 0\n    Rejected(reason) => length-scalars(reason) > 0\n';
test('exhaustive variant branches are typed against their actual payloads',()=>assert.equal(decl(check(matchRule)).body.op,'match_variant'));
test('grouped variant branches with unused incompatible payloads remain valid',()=>{const b=decl(check('\nrule Eval:\n  input outcome Outcome\n  expression match outcome:\n    Found(value), Missing(value), Rejected(value) => true\n')).body;assert.equal(b.op,'match_variant');if(b.op==='match_variant')assert.equal(b.cases.length,3);});
test('inline enum matching binds only the actual variant payload',()=>assert.equal(decl(check(calc('match outcome Found(value) => value.count else 0','UInt64','  input outcome Outcome\n'))).body.op,'match_variant'));
test('match else consumes its own operators and fields',()=>{const b=decl(check(calc('match holder.item some(item) => item.count else 1 + 2','UInt64','  input holder Holder\n'))).body;assert.equal(b.op,'let');if(b.op==='let'&&b.body.op==='if')assert.equal(b.body.else.op,'binary');});
test('Boolean match alternatives do not become enum constructors',()=>assert.equal(decl(check(rule('match flag true => false else true','  input flag Bool\n'))).body.op,'if'));
test('qualified variant requirement retains exact enum and payload field type',()=>assert.equal(decl(check(calc('require-variant(outcome,Outcome.Found).value.count','UInt64','  input outcome Outcome\n'))).body.op,'field'));
const machine='\nstate-machine Lifecycle:\n  state Status\n  input Signal\n  initial Open\n  terminal Closed\n  transition Open Go -> Closed\n  transition Closed Wait -> Closed\n  otherwise reject invalid-transition\n';
test('StateMachine remains a pure named proposal with source initial/terminal/reason',()=>{const d=decl(check(machine),'Lifecycle');assert.equal(d.body.op,'state_machine');assert.equal(d.initial!.op,'enum_value');assert.equal(d.terminal.length,1);assert.equal(d.otherwise_reason,'invalid-transition');});
test('named StateMachine .propose has explicit outcome type and no effects',()=>{const d=decl(check(machine+calc('Lifecycle.propose(state,event)','outcome<Status,Bool,0>','  input state Status\n  input event Signal\n')));assert.equal(d.body.op,'call');assert.equal(d.result.kind,'outcome');});
const baseCalculation='\ncalculation Base:\n  pure\n  input item Item\n  result UInt64\n  expression item.count\n';
const policy='\npolicy Eval:\n  input item Item\n  result UInt64\n  ordered-cases:\n    verified when item.verified -> Base(item)\n    otherwise -> Base(item)\n';
test('Policy selects only declared same-result Calculations and retains otherwise',()=>{const b=decl(check(baseCalculation+policy)).body;assert.equal(b.op,'policy');if(b.op==='policy'){assert.equal(b.cases[0]!.action.calculation,'Demo.Base');assert.equal(b.otherwise.calculation,'Demo.Base');}});
for(const [name,extra,code] of [
 ['Rule numeric result',rule('1'),'TypeMismatch'],
 ['UInt64 overflow',calc('18446744073709551616'),'TypeMismatch'],
 ['unknown pure variable',calc('missing'),'UnknownReference'],
 ['unknown field',calc('item.missing','UInt64','  input item Item\n'),'UnknownReference'],
 ['arithmetic Bool',calc('checked-add(true,1)'),'TypeMismatch'],
 ['comparison incompatible values',rule('1 == true'),'TypeMismatch'],
 ['text length without explicit unit',calc('length("abc")'),'TypeMismatch'],
 ['list uniqueness on scalar',rule('all-unique-exact(1)'),'TypeMismatch'],
 ['untyped empty list',calc('length([])'),'MissingMapping'],
 ['none without optional type',calc('none'),'MissingMapping'],
 ['present on scalar',rule('present(1)'),'TypeMismatch'],
 ['unsafe optional OR',rule('present(holder.item) or holder.item.count > 0'),'TypeMismatch'],
 ['field access before presence',rule('holder.item.count > 0 and present(holder.item)'),'TypeMismatch'],
 ['record constructor missing field',calc('Item(1,true,"abc")','Item'),'MissingMapping'],
 ['record constructor unknown field',calc('Item(id=1,verified=true,label="abc",unknown=3)','Item'),'UnknownReference'],
 ['record constructor duplicate argument',calc('Item(id=1,verified=true,label="abc",id=3)','Item'),'MissingMapping'],
 ['record constructor mixed arguments',calc('Item(1,verified=true,label="abc",count=3)','Item'),'Syntax'],
 ['record constructor wrong type',calc('Item(1,3,"abc",0)','Item'),'TypeMismatch'],
 ['refinement literal wrong pattern',calc('Label("ABC")','Label'),'TypeMismatch'],
 ['literal violates scalar minimum',calc('Label("")','Label'),'TypeMismatch'],
 ['refinement constructor rejects non-text input',calc('Label(raw)','Label','  input raw UInt64\n'),'TypeMismatch'],
 ['map wrong binder type',calc('map(items,item:UInt64 => item)','List<UInt64,10>'),'TypeMismatch'],
 ['map wrong output bound',calc('map(items,item:Item => item.count)','List<UInt64,5>'),'TypeMismatch'],
 ['filter numeric predicate',calc('filter(items,item:Item => item.count)','List<Item,10>'),'TypeMismatch'],
 ['fold wrong state type',calc('fold(items,false,total:UInt64,item:Item => total)'),'TypeMismatch'],
 ['fold index Bool',calc('indexed-fold(items,0,total:UInt64,item:Item,index:Bool => total)'),'TypeMismatch'],
 ['loop binder shadows input',calc('map(items,items:Item => items.count)','List<UInt64,10>'),'DuplicateSymbol'],
 ['repeat zero maximum',calc('repeat(1,max 0,0,total:UInt64,index:UInt64 => total)'),'ResourceLimit'],
 ['while numeric guard',calc('while-bounded(max 10,0,total:UInt64,total => total + 1)'),'TypeMismatch'],
 ['natural sort on numeric',calc('sort(items,count ascending natural)','List<Item,10>'),'TypeMismatch'],
 ['numeric sort on string',calc('sort(items,label ascending numeric)','List<Item,10>'),'TypeMismatch'],
 ['missing sort field',calc('sort(items,missing ascending numeric)','List<Item,10>'),'UnknownReference'],
 ['nonexhaustive enum match',matchRule.replace('    Missing(key) => key == 0\n',''),'NonExhaustive'],
 ['wrong grouped payload field','\nrule Eval:\n  input outcome Outcome\n  expression match outcome:\n    Found(value), Missing(value), Rejected(value) => value.count > 0\n','TypeMismatch'],
 ['duplicate enum case',matchRule.replace('    Missing(key) => key == 0','    Found(value) => value.verified\n    Missing(key) => key == 0'),'DuplicateSymbol'],
 ['match binder leaks',calc('(match holder.item some(found) => found.count else 0) + found.count','UInt64','  input holder Holder\n'),'UnknownReference'],
 ['nullary enum payload binding',rule('match status Open(value) => true else false','  input status Status\n'),'TypeMismatch'],
 ['wrong enum selector',rule('match status Signal.Go => true else false','  input status Status\n'),'TypeMismatch'],
 ['otherwise before case',matchRule.replace('    Found(value) => value.verified','    otherwise => true\n    Found(value) => value.verified'),'InvalidContract'],
 ['StateMachine wrong initial',machine.replace('initial Open','initial Missing'),'UnknownReference'],
 ['StateMachine wrong next',machine.replace('Go -> Closed','Go -> Signal.Go'),'TypeMismatch'],
 ['StateMachine call without propose',machine+calc('Lifecycle(state,event)','outcome<Status,Bool,0>','  input state Status\n  input event Signal\n'),'TypeMismatch'],
 ['Policy selects Rule',rule('true','  input item Item\n').replace('rule Eval','rule Base')+policy,'TypeMismatch'],
 ['Policy result mismatch',baseCalculation.replace('result UInt64','result Bool').replace('expression item.count','expression true')+policy,'TypeMismatch'],
 ['Mapping missing field','\nmapping Eval:\n  input item Item\n  target Item\n  total true\n  preserve id, verified\n  field count <- item.count\n','MissingMapping'],
 ['Mapping preserve/assignment overlap','\nmapping Eval:\n  input item Item\n  target Item\n  total true\n  preserve id, verified, label, count\n  field count <- 1\n','InvalidContract'],
 ['Mapping two candidate preserve inputs','\nmapping Eval:\n  input a Item\n  input b Item\n  target Item\n  total true\n  preserve id, verified, label\n  field count <- a.count\n','InvalidContract'],
 ['ordered Mapping missing fallback','\nmapping Eval:\n  target UInt64\n  total true\n  ordered-cases:\n    first when true -> 1\n','NonExhaustive'],
 ['unknown pure callback',calc('arbitrary(items)'),'UnknownReference'],
 ['effectful operation called from pure source','\noperation Run:\n  output UInt64\n  return 1\n'+calc('Run()'),'UnsupportedCapability'],
 ['unbounded source String','\nvalue-object Unbounded:\n  data String\n'+calc('1'),'MissingMapping'],
]as const)test('rejects '+name,()=>failure(()=>check(extra),code));
test('acyclic pure function dependency is required even when signatures match',()=>failure(()=>check('\ncalculation First:\n  pure\n  result UInt64\n  expression Second()\n\ncalculation Second:\n  pure\n  result UInt64\n  expression First()\n'),'InvalidContract'));
test('refinement unbounded regex operators reject before any RegExp evaluation',()=>failure(()=>checkCoreCommercePureSources([{path:'application.alch',text:base.replace('^[a-z]{1,8}$','^(a+)+$')+calc('1')}]),'UnsupportedCapability'));
test('field/enum/domain changes affect the independent normalized pure subject',()=>{const s=source(calc('1'));const baseline=checkCoreCommercePureSources(s).pure_subject_sha256;for(const [from,to]of [['count <= 100','count <= 99'],['count UInt64','count Bool'],['utf8-bytes 1..8','utf8-bytes 2..8'],['value Open','value Open wire "open"']]as const)assert.notEqual(checkCoreCommercePureSources([{path:'application.alch',text:s[0]!.text.replace(from,to).replace('invariant count <= 100',from==='count UInt64'?'invariant count == true':'invariant count <= 100')}]).pure_subject_sha256,baseline);});
test('typed data is deeply frozen and cannot be used as an original custody handle',()=>{const r=check(calc('1'));assert.ok(Object.isFrozen(r));assert.ok(Object.isFrozen(r.declarations[0]!.body));assert.equal(Object.hasOwn(r,'accepted'),false);assert.equal(Object.hasOwn(r,'selection'),false);});
test('inert transferred pure data is compared with newly reconstructed source rather than adopted',()=>{const s=source(calc('1')),proposed=JSON.parse(JSON.stringify(checkCoreCommercePureSources(s))),checked=checkCoreCommercePureProposal(s,proposed);assert.notEqual(checked,proposed);assert.equal(checked.pure_subject_sha256,proposed.pure_subject_sha256);assert.equal(checked.qualification,'independent-pure-component-data-only');});
for(const field of ['body','kind','parameters','result','preconditions','rounding','on_evaluation_error','initial','terminal','otherwise_reason'])test('proposal forgery rejects '+field+' even with unchanged subject hash',()=>{const s=source(calc('1')),proposed=JSON.parse(JSON.stringify(checkCoreCommercePureSources(s)));proposed.declarations[0][field]={forged:true};failure(()=>checkCoreCommercePureProposal(s,proposed),'InvalidContract');});
test('proposal cannot suppress field, enum or refinement constraints',()=>{const s=source(calc('1'));for(const field of ['value_declarations','record_invariants','source_refinements']){const proposed=JSON.parse(JSON.stringify(checkCoreCommercePureSources(s)));proposed[field]=[];failure(()=>checkCoreCommercePureProposal(s,proposed),'InvalidContract');}});
test('source edit invalidates a previous pure proposal',()=>{const s=source(calc('1')),proposed=checkCoreCommercePureSources(s);failure(()=>checkCoreCommercePureProposal(source(calc('2')),proposed),'InvalidContract');});
test('extra claimed native/selection/acceptance fields cannot enter a pure proposal',()=>{const s=source(calc('1')),proposed={...checkCoreCommercePureSources(s),native_basis:'forged',accepted:true};failure(()=>checkCoreCommercePureProposal(s,proposed),'InvalidContract');});
test('accessor proposal is rejected without invoking its getter',()=>{let invoked=false;const proposal={get body(){invoked=true;return 'forged';}};failure(()=>checkCoreCommercePureProposal(source(calc('1')),proposal),'InvalidContract');assert.equal(invoked,false);});
test('bounded refinement membership agrees with independent fixed regex vectors',()=>{const where={path:'application.alch',start:0,end:0};for(const pattern of ['^$','^abc$','^[a-z]{1,8}$','^evt_[a-f0-9]{4}$','^[a-z]{0,3}[a-z]{1,4}$','^[a-z_ -]{0,3}$'])for(const value of ['', 'abc','abcd','a','abcdefghi','evt_a10f','evt_A10f','  -','a_b','é'])assert.equal(matchesCoreRefinementPattern(pattern,value,where),new RegExp(pattern,'u').test(value),pattern+' '+value);});
test('overlapping bounded repetitions use the finite matcher rather than host backtracking',()=>{const p='^'+'[a-z]{0,20}'.repeat(12)+'$',where={path:'application.alch',start:0,end:0};assert.equal(matchesCoreRefinementPattern(p,'a'.repeat(80)+'!',where),false);});
