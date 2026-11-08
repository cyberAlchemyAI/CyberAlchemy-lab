import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {parseBusinessSource} from '../src/business-authoring-parser.js';
import {resolveBusinessSpec,prepareBusinessSpecFile,disposeResolvedBusinessSpec} from '../src/business-authoring-resolve.js';
import {BusinessSourceRejected} from '../src/business-authoring-model.js';
import {lowerBusinessFormalSemantics,assertBusinessFormalSemanticsCurrent,renderBusinessBoolFormal,type BusinessFormalSemantics} from '../src/business-authoring-semantics.js';
const contracts=new URL('../../../../../../../research/craft-alchlang-user-readiness-2026-10-12/business-authoring-design-2026-10-14/implementation-plan/contracts/',import.meta.url);
const reference=readFileSync(new URL('reference-business.alch',contracts),'utf8');
const lower=(source:string)=>lowerBusinessFormalSemantics(resolveBusinessSpec(parseBusinessSource(source)));
const plain=(value:unknown)=>JSON.parse(JSON.stringify(value));
const rejected=(run:()=>unknown,code:string)=>assert.throws(run,e=>{assert.ok(e instanceof BusinessSourceRejected);assert.ok(e.code.startsWith(code),e.message);return true;});

test('one explicit typed Bool primitive supplies formal metadata and the existing runtime interpretation',()=>{
 const value=lower(reference),definition=value.data.definitions[0]!;
 assertBusinessFormalSemanticsCurrent(value);
 assert.deepEqual(definition.primitive,{kind:'entity-bool-field',entity_ref:'Delivery',parameter:'delivery',field:'verified',field_type:'Bool',comparison:'eq',value:true});
 assert.deepEqual(definition.entity,{kind:'entity',entity_ref:'Delivery',identity:'id',fields:[{name:'id',type:'UInt64'},{name:'label',type:'String'},{name:'verified',type:'Bool'}]});
 assert.deepEqual(definition.predicate_uses,[{claim_ref:'DeliveryReady',predicate_ref:'Permitted',sort_ref:'DeliveryValue'}]);
 assert.equal(definition.formal.definition,'DeliveryEligibility(delivery: Delivery) := (delivery.verified = true)');
 assert.equal(definition.formal.expression,'DeliveryReady::Permitted(delivery: DeliveryValue) iff (delivery.verified = true)');
 assert.deepEqual(definition.formal.notation,[{symbol:'delivery',meaning:'One received delivery acknowledgement.'},{symbol:'delivery.verified',meaning:'Caller supplied eligibility flag.'}]);
 assert.equal(definition.formal.operational_interpretation,'Read delivery.verified: Bool and compare with true.');
 assert.deepEqual(plain(value.data.rule_meanings),{CanConfirm:{sorts:{DeliveryValue:'Delivery'},constants:{current:'delivery'},predicates:{Permitted:'verified'}}});
 assert.equal(value.data.authority_effect,'none');assert.equal(value.data.business_sha256,value.business.business_sha256);
 assert.equal(value.data.claims[0]!.proposition_source,'Permitted(current)');assert.equal(value.data.claims[0]!.ceiling,value.business.data.claims[0]!.ceiling);
 assert.equal(definition.input,value.business.data.definitions[0]!.input);assert.equal(definition.field,value.business.data.entities[0]!.fields[1]);
});
test('formal text renderer sorts explicit associations and fixes notation order without rewriting meanings',()=>{
 const value=lower(reference),definition=value.data.definitions[0]!;
 const uses=[{claim_ref:'Zed',predicate_ref:'Z',sort_ref:'V'},{claim_ref:'Aye',predicate_ref:'B',sort_ref:'V'},{claim_ref:'Aye',predicate_ref:'A',sort_ref:'V'}];
 const result=renderBusinessBoolFormal('Eligibility',definition.primitive,'exact Entity meaning','exact Bool meaning',uses);
 assert.equal(result.expression,'Aye::A(delivery: V) iff (delivery.verified = true); Aye::B(delivery: V) iff (delivery.verified = true); Zed::Z(delivery: V) iff (delivery.verified = true)');
 assert.deepEqual(result.notation,[{symbol:'delivery',meaning:'exact Entity meaning'},{symbol:'delivery.verified',meaning:'exact Bool meaning'}]);
 assert.ok(Object.isFrozen(result)&&Object.isFrozen(result.notation));
});
test('compound authored ground formulas keep their exact AST and source',()=>{
 const source='(Permitted(current) and not Permitted(current)) implies (Permitted(current) iff Permitted(current))';
 const value=lower(reference.replace('proposition Permitted(current)','proposition '+source));
 const atom={kind:'predicate',name:'Permitted',arguments:[{kind:'constant',name:'current',sort:'DeliveryValue'}]};
 assert.deepEqual(value.data.claims[0]!.proposition,{kind:'implies',left:{kind:'and',left:atom,right:{kind:'not',operand:atom}},right:{kind:'iff',left:atom,right:atom}});
 assert.equal(value.data.claims[0]!.proposition_source,source);
});
test('unsupported equality never becomes an identity-reflexivity substitute',()=>{
 const source=reference.replace('proposition Permitted(current)','proposition Permitted(current) and current = current');
 const resolved=resolveBusinessSpec(parseBusinessSource(source));
 rejected(()=>lowerBusinessFormalSemantics(resolved),'BUSINESS_UNSUPPORTED');
 assert.throws(()=>lowerBusinessFormalSemantics(resolved),e=>{assert.ok(e instanceof BusinessSourceRejected);assert.equal(e.line,source.split('\n').findIndex(s=>s.startsWith('  proposition '))+1);assert.equal(e.column,3);return true;});
});
test('quantifiers/functions/nonunary/ValueObject/wrong Bool interpretations reject at the real authoring boundary',()=>{
 for(const [before,after] of [
  ['proposition Permitted(current)','proposition forall x: DeliveryValue: Permitted(x)'],
  ['proposition Permitted(current)','proposition Permitted(transform(current))'],
  ['predicate Permitted(DeliveryValue)','predicate Permitted(DeliveryValue, DeliveryValue)'],
  ['entity Delivery:','value-object Delivery:'],
  ['boolean-field delivery.verified','boolean-field delivery.id'],
  ['defined-by DeliveryEligibility','defined-by Permitted'],
  ['sort DeliveryValue interpreted-as Delivery','sort DeliveryValue']
 ])rejected(()=>lower(reference.replace(before!,after!)),'BUSINESS_');
});
test('finite compound expansion rejects complete oversized formulas rather than lowering a prefix',()=>{
 let expression='Permitted(current)';for(let i=0;i<10;i++)expression='('+expression+') iff Permitted(current)';
 rejected(()=>lower(reference.replace('proposition Permitted(current)','proposition '+expression)),'BUSINESS_SOURCE_BUDGET');
});
test('changing the selected Bool field changes both metadata and runtime mapping',()=>{
 const extra=reference.replace('  verified Bool meaning "Caller supplied eligibility flag."','  verified Bool meaning "Caller supplied eligibility flag."\n  approved Bool meaning "Different authored flag."');
 const original=lower(extra),changed=lower(extra.replace('boolean-field delivery.verified','boolean-field delivery.approved'));
 assert.equal(original.data.rule_meanings.CanConfirm!.predicates.Permitted,'verified');assert.equal(changed.data.rule_meanings.CanConfirm!.predicates.Permitted,'approved');
 assert.equal(changed.data.definitions[0]!.primitive.field,'approved');assert.match(changed.data.definitions[0]!.formal.expression,/delivery\.approved = true/);
 assert.notEqual(original.derivation_sha256,changed.derivation_sha256);
});
test('formal handles are deeply frozen, registered and tied to the exact original resolved object',()=>{
 const business=resolveBusinessSpec(parseBusinessSource(reference)),value=lowerBusinessFormalSemantics(business);
 assert.equal(value.business,business);assertBusinessFormalSemanticsCurrent(value);
 for(const forged of [plain(value),{...value},Object.create(value),new Proxy(value,{})])rejected(()=>assertBusinessFormalSemanticsCurrent(forged as BusinessFormalSemantics),'BUSINESS_HANDLE');
 assert.throws(()=>{(value.data.definitions[0]!.primitive as {field:string}).field='id';},TypeError);
 assert.throws(()=>{(value.data.claims[0]!.signature.predicates as unknown[]).push({});},TypeError);
 disposeResolvedBusinessSpec(business);rejected(()=>assertBusinessFormalSemanticsCurrent(value),'BUSINESS_DISPOSED');
 rejected(()=>lowerBusinessFormalSemantics(business),'BUSINESS_DISPOSED');
});
test('formal handle currentness includes live original file capture',()=>{
 const root=mkdtempSync(path.join(os.tmpdir(),'business-formal-current-'));
 try{const file=path.join(root,'business.alch');writeFileSync(file,reference);const value=lowerBusinessFormalSemantics(prepareBusinessSpecFile(root,'business.alch'));writeFileSync(file,reference.replace('Delivery acknowledgements','Changed title'));rejected(()=>assertBusinessFormalSemanticsCurrent(value),'BUSINESS_SOURCE_DRIFT');}
 finally{rmSync(root,{recursive:true,force:true});}
});
test('both independent domains use their authored field including false/true values',()=>{
 for(const [domain,field] of [['delivery-acknowledgement','verified'],['publication-consent','consented']]){
  const source=readFileSync(new URL('./fixtures/business-authoring/'+domain+'/business.alch',import.meta.url),'utf8'),value=lower(source),definition=value.data.definitions[0]!;
  assert.equal(definition.primitive.field,field);assert.equal(value.data.rule_meanings.CanProcess!.predicates[value.data.claims[0]!.signature.predicates[0]!.name],field);
  // Independent primitive oracle: a false supplied field remains false, and true remains true.
  for(const supplied of [false,true]){const input:Record<string,unknown>={[field!]:supplied,id:'18446744073709551615',label:'retained',recipient_confirmed:!supplied};assert.equal(input[definition.primitive.field]===definition.primitive.value,supplied);}
  assert.ok(definition.formal.expression.includes('('+definition.input.name+'.'+field+' = true)'));
 }
});
test('derivation hash uses independent canonical data bytes; declaration reorder preserves formal data',()=>{
 const value=lower(reference);
 const canonical=(v:unknown):string=>Array.isArray(v)?'['+v.map(canonical).join(',')+']':v!==null&&typeof v==='object'?'{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical((v as Record<string,unknown>)[k])).join(',')+'}':JSON.stringify(v);
 assert.equal(value.derivation_sha256,createHash('sha256').update(canonical(value.data)).digest('hex'));
 const [header,...declarations]=reference.trimEnd().split('\n\n');const reordered=lower([header,...declarations.reverse()].join('\n\n')+'\n');
 assert.equal(value.derivation_sha256,reordered.derivation_sha256);assert.deepEqual(value.data,reordered.data);
});

test('an unused explicitly resolved Entity sort rejects at formal lowering without narrowing',()=>{
 const source=reference.replace('  sort DeliveryValue interpreted-as Delivery','  sort DeliveryValue interpreted-as Delivery\n  sort UnusedValue interpreted-as Delivery');
 const business=resolveBusinessSpec(parseBusinessSource(source));
 assert.equal(business.data.claims[0]!.sorts.length,2);
 assert.throws(()=>lowerBusinessFormalSemantics(business),error=>{
  assert.ok(error instanceof BusinessSourceRejected);assert.equal(error.code,'BUSINESS_UNSUPPORTED');
  assert.equal(error.line,source.split('\n').findIndex(line=>line==='  sort UnusedValue interpreted-as Delivery')+1);assert.equal(error.column,3);return true;
 });
});
test('redundant source grouping and a shallow implication AST keep independent finite budgets',()=>{
 const atom='Permitted(current)',proposition='('.repeat(63)+atom+' implies '+atom+' implies '+atom+')'.repeat(63);
 const value=lower(reference.replace('proposition '+atom,'proposition '+proposition));
 const expectedAtom={kind:'predicate',name:'Permitted',arguments:[{kind:'constant',name:'current',sort:'DeliveryValue'}]};
 assert.equal(value.data.claims[0]!.proposition_source,proposition);
 assert.deepEqual(value.data.claims[0]!.proposition,{kind:'implies',left:expectedAtom,right:{kind:'implies',left:expectedAtom,right:expectedAtom}});
});
