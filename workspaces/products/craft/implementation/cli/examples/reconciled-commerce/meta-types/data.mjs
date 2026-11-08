import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';

// Each assertion supplies an expectation independently of generated descriptors.
export async function runData({generatedRoot, exampleRoot}) {
  const load = relative => import(pathToFileURL(path.join(generatedRoot, 'commerce-corpus/features/commerce/src', relative)).href);
  const {createCustomerFactory} = await load('domain/entities/customer.js');
  const {createOrderFactory, OrderFieldBindings} = await load('domain/entities/order.js');
  const {createMoneyFactory, MoneyValueComponent} = await load('domain/value-objects/money.js');
  const {ChoiceValueComponent: Choice} = await load('domain/enums/choice.sum.js');
  const {PriorityValueComponent: Priority} = await load('domain/enums/priority.component.js');
  const {mappingSummary} = await load('application/mappings/summary.js');
  const {mappingIntegrationOutbound} = await load('application/mappings/integration-outbound.js');
  const {mappingPartialMoney} = await load('application/mappings/partial-money.js');
  const {mappingDefaultMoney} = await load('application/mappings/default-money.js');
  const values = JSON.parse(fs.readFileSync(path.join(exampleRoot, 'values.json'), 'utf8'));
  const cases = [];
  const check = (id, metaType, expected, body) => {
    body(); cases.push({id, meta_type:metaType, result:'pass', expected});
  };
  const value = result => {assert.equal(result.ok,true); return result.value;};
  const failure = (result, code) => {assert.equal(result.ok,false); assert.equal(result.value,null); assert.deepEqual(result.failure_codes,[code]);};
  const customers = createCustomerFactory(), money = createMoneyFactory(), orders = createOrderFactory();
  const customer = value(customers.create({id:'9007199254740993',name:'Ada'}));
  check('entity-exact-identity','Entity','decimal string normalizes exactly to bigint',()=>assert.equal(customer.fields.id,9007199254740993n));
  check('entity-identity-equality','Entity','same identity with changed name; different identity differs',()=>{
    assert.equal(customer.sameIdentity(value(customers.create({id:9007199254740993n,name:'Changed'}))),true);
    assert.equal(customer.sameIdentity(value(customers.create({id:'2',name:'Ada'}))),false);
  });
  check('entity-required-field','Entity','missing name rejected before Rule execution',()=>{
    const result=customers.create({id:'1'});failure(result,'INVALID_FIELDS');assert.deepEqual(result.trace.validators,[]);
  });
  check('entity-malformed-identities','Entity','negative, leading-zero, fractional and unsafe Number identities rejected',()=>{
    for(const id of ['-1','01','1.5',9007199254740992])failure(customers.create({id,name:'Ada'}),'INVALID_FIELDS');
  });
  check('entity-invariant','Entity','identity zero rejected by positive Rule',()=>failure(customers.create({id:'0',name:'Ada'}),'RULE_FAIL:commerce:positive'));
  check('entity-transition','Entity','same identity transition succeeds; changed identity is rejected',()=>{
    const transitioned=value(customers.transition(customer,{id:'9007199254740993',name:'Updated'}));assert.equal(transitioned.fields.name,'Updated');
    failure(customers.transition(customer,{id:'3',name:'Updated'}),'IDENTITY_CHANGED');
  });
  const amount=value(money.create({quantity:'3'}));
  check('value-object-construction','Value Object','factory normalizes quantity and missing optional note',()=>{
    assert.equal(amount.fields.quantity,3n);assert.equal(amount.fields.note,null);assert.equal(Object.isFrozen(amount.fields),true);
  });
  check('value-object-invariant','Value Object','zero quantity rejected in both create and reconstruct',()=>{
    failure(money.create({quantity:'0'}),'RULE_FAIL:commerce:positive');failure(money.reconstruct({quantity:'0'}),'RULE_FAIL:commerce:positive');
  });
  check('value-object-input-type','Value Object','missing quantity and wrong note rejected',()=>{
    failure(money.create({}),'INVALID_FIELDS');failure(money.create({quantity:'3',note:7}),'INVALID_FIELDS');
  });
  check('value-object-equality','Value Object','normalized equal fields equal; different optional content differs; raw object is unowned',()=>{
    const equal=value(money.create({quantity:3n,note:null}));assert.equal(amount.equals(equal),true);assert.equal(amount.hash(),equal.hash());
    assert.equal(amount.equals(value(money.create({quantity:'3',note:''}))),false);assert.equal(amount.equals({quantity:3n,note:null}),false);
  });
  const some=Choice.create({variant:'Some',payload:amount}), none=Choice.create({variant:'None'});
  check('enum-finite-alternatives','Enum','Normal and Urgent cases; equal alternative roundtrip',()=>{
    assert.deepEqual(Object.keys(Priority.values),['Normal','Urgent']);
    const serialized=JSON.stringify({variant:Priority.fromVariant('Urgent').variant});
    assert.equal(serialized,'{"variant":"Urgent"}');assert.equal(Priority.equals(Priority.fromVariant(JSON.parse(serialized).variant),Priority.values.Urgent),true);
  });
  check('enum-unknown-alternative','Enum','unknown string and non-string rejected',()=>{
    assert.throws(()=>Priority.fromVariant('Missing'),/INVALID_ENUM_VARIANT/);assert.throws(()=>Priority.fromVariant(1),/INVALID_ENUM_VARIANT/);
  });
  check('enum-payload-alternatives','Enum','None and Some with validated Money are distinct owned cases',()=>{
    assert.equal(Choice.isOwned(none),true);assert.equal(Choice.isOwned(some),true);assert.equal(some.payload,amount);
    assert.equal(Choice.equals(some,Choice.create({variant:'Some',payload:value(money.create({quantity:3}))})),true);
    assert.equal(Choice.equals(some,none),false);
  });
  check('enum-payload-rejections','Enum','unknown variant, absent payload, unwanted payload and unvalidated payload rejected',()=>{
    assert.throws(()=>Choice.create({variant:'Other'}),/INVALID_SUM_VARIANT/);
    assert.throws(()=>Choice.create({variant:'Some'}),/INVALID_SUM_PAYLOAD/);
    assert.throws(()=>Choice.create({variant:'None',payload:amount}),/INVALID_SUM_PAYLOAD/);
    assert.throws(()=>Choice.create({variant:'Some',payload:{quantity:'3'}}),/UNOWNED_COMPONENT/);
  });
  check('enum-payload-serialization','Enum','caller explicitly encodes bigint fields and reconstructs through factory',()=>{
    const wire=JSON.stringify({variant:some.variant,payload:{quantity:String(some.payload.fields.quantity),note:some.payload.fields.note}});
    assert.equal(wire,'{"variant":"Some","payload":{"quantity":"3","note":null}}');
    const decoded=JSON.parse(wire);assert.equal(Choice.equals(some,Choice.create({variant:decoded.variant,payload:value(money.create(decoded.payload))})),true);
  });
  const ownedOrderInput={id:'1',customer:value(customers.create({id:'2',name:'Customer'})),money:amount,choice:some,labels:['a','a','b'],lines:[amount],billing_customer_id:'99',tags:['a','b']};
  check('entity-identity-reference','Entity','unknown billing identity accepted as exact scalar; no object fetch',()=>{
    const order=value(orders.create(ownedOrderInput));assert.equal(order.fields.billing_customer_id,99n);assert.equal(typeof order.fields.billing_customer_id,'bigint');
    assert.deepEqual(OrderFieldBindings[0].projection,['id']);assert.equal(OrderFieldBindings[0].target,'billing:customer');
    assert.equal(Object.hasOwn(order.fields,'billing_customer'),false);
  });
  check('entity-owned-components','Entity','Order requires validated nested Money/Customer/Choice; raw records rejected',()=>failure(orders.create({...ownedOrderInput,money:{quantity:'3'}}),'INVALID_FIELDS'));
  check('mapping-multiple-inputs','Mapping','explicit net and fee remain independent arguments',()=>{
    assert.deepEqual(mappingSummary({order:values.order,net:'93',fee:'5'}),{id:1n,net:93n,fee:5n});
    assert.deepEqual(mappingSummary({order:values.order,net:'5',fee:'93'}),{id:1n,net:5n,fee:93n});
  });
  check('mapping-identity-reference','Mapping','only scalar referenced identity is required; no record fetch',()=>assert.deepEqual(mappingIntegrationOutbound({order:'99'}),{id:99n,name:'integration'}));
  check('mapping-required-and-type-rejections','Mapping','missing argument/required field and malformed UInt64 rejected',()=>{
    assert.throws(()=>mappingSummary({order:values.order,net:'93'}),/MAPPING_INPUT/);
    const {id,...missing}=values.order;assert.throws(()=>mappingSummary({order:missing,net:'93',fee:'5'}),/RULE_INPUT/);
    assert.throws(()=>mappingSummary({order:values.order,net:'bad',fee:'5'}),/RULE_INPUT/);
    assert.throws(()=>mappingIntegrationOutbound({order:{id:'99'}}),/MAPPING_INPUT/);
  });
  check('mapping-partial','Mapping','partial result deliberately contains only quantity',()=>{
    const result=mappingPartialMoney({money:{quantity:'3',note:'discard'}});assert.deepEqual(result,{quantity:3n});assert.equal(Object.hasOwn(result,'note'),false);
  });
  check('mapping-default','Mapping','missing/null note uses fallback; empty and present strings preserved',()=>{
    for(const input of [{quantity:'3'},{quantity:'3',note:null}])assert.deepEqual(mappingDefaultMoney({money:input}),{quantity:3n,note:'unspecified'});
    assert.deepEqual(mappingDefaultMoney({money:{quantity:'3',note:''}}),{quantity:3n,note:''});
    assert.deepEqual(mappingDefaultMoney({money:{quantity:'3',note:'hello'}}),{quantity:3n,note:'hello'});
  });
  check('mapping-is-not-construction','Mapping','zero projection succeeds; explicit factory rejects invariant; result is unowned',()=>{
    const result=mappingDefaultMoney({money:{quantity:'0'}});assert.deepEqual(result,{quantity:0n,note:'unspecified'});
    assert.equal(MoneyValueComponent.isOwned(result),false);failure(money.create(result),'RULE_FAIL:commerce:positive');
  });
  check('mapping-input-record-rejections','Mapping','missing required quantity and wrong optional note reject even for partial projection',()=>{
    assert.throws(()=>mappingPartialMoney({money:{note:'x'}}),/MAPPING_INPUT/);
    assert.throws(()=>mappingDefaultMoney({money:{quantity:'3',note:7}}),/MAPPING_INPUT/);
  });
  return {schema_version:'domainspec.meta-type-data-witness/v1-candidate',result:'pass',profile:'domainspec.reconciled-typescript/v1-candidate',value_profile:'domainspec.typescript-exact-uint64/v1',cases,denominators:{cases:cases.length,passed:cases.length,meta_types:4},authority_effect:'none'};
}

if (process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  if(process.argv.length!==4)throw new Error('Usage: node data.mjs <compiled-generated-root> <example-root>');
  process.stdout.write(JSON.stringify(await runData({generatedRoot:path.resolve(process.argv[2]),exampleRoot:path.resolve(process.argv[3])}),null,2)+'\n');
}
