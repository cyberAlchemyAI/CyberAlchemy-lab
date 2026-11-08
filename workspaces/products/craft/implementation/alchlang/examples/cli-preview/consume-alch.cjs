const assert = require('node:assert/strict');
const path = require('node:path');
const root = path.resolve(process.argv[2]);
const expectedFee = process.argv[3] ?? '500';
const api = require(path.join(root, 'domain.js'));
const native = name => require(path.join(root, 'generated/src/domainspec/typescript/delivery-example', name+'.js'));
const mapping = api.evaluateMapping('OrderToMessage', {orderId:'order-42'});
assert.deepEqual(mapping, {messageId:'order-42',currency:'GBP'});
assert.deepEqual(api.evaluateMapping('PartialMessage', {}), {});
assert.deepEqual(api.evaluateMapping('PartialMessage', {orderId:'order-42', extra:'not copied'}), {messageId:'order-42'});
const diagnostics=[];
function reject(label, fn, code) {
  let rejected=false;
  try { fn(); } catch (error) {
    rejected=true;
    assert.match(error.message, new RegExp(`^${code}(?::|$)`));
    diagnostics.push({label,code,message:error.message});
  }
  assert.equal(rejected,true,`${label} must reject`);
}
reject('mapping incompatible identity',()=>api.evaluateMapping('OrderToMessage',{orderId:12}),'ALCH_INPUT_TYPE');
reject('policy missing input',()=>api.selectPolicy('ChooseDeliveryFee',{urgent:true}),'ALCH_MISSING_INPUT');
reject('policy wrong Bool',()=>api.selectPolicy('ChooseDeliveryFee',{urgent:'true',priority:false}),'ALCH_INPUT_TYPE');
assert.equal(native('urgent-required').urgentRequired({urgent:true}), true);
assert.equal(native('urgent-required').urgentRequired({urgent:false}), false);
const inputs=[{urgent:true,priority:true},{urgent:false,priority:true},{urgent:false,priority:false}];
const selected=inputs.map(input=>api.selectPolicy('ChooseDeliveryFee',input));
assert.deepEqual(selected,['ExpressFee','PriorityFee','StandardFee']);
// Consumer wiring is explicit; Policy selection does not invoke these functions.
const targets={ExpressFee:native('express-fee').expressFee,PriorityFee:native('priority-fee').priorityFee,StandardFee:native('standard-fee').standardFee};
const fees=selected.map(name=>String(targets[name]({})));
assert.deepEqual(fees,['1000','750',expectedFee]);
console.log(JSON.stringify({mapping,partial:{},partialSupplied:{messageId:'order-42'},rule:[true,false],selected,fees,diagnostics}));
