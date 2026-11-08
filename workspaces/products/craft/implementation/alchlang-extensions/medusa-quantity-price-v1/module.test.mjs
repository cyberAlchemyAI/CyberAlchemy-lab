import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync, mkdtempSync, rmSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {buildApplication, root} from './build.mjs';
import {quotePrice, prepareQuote, usdToMinor, minorToUsd, UINT64_MAX} from './adapter.mjs';
const fixtures = JSON.parse(readFileSync(path.join(root,'fixtures.json'),'utf8'));
test('generated DomainSpec application quotes every quantity-price fixture', async t => {
  const temp = mkdtempSync(path.join(os.tmpdir(),'alch-price-test-'));
  t.after(() => rmSync(temp,{recursive:true,force:true}));
  writeFileSync(path.join(temp,'package.json'), JSON.stringify({type:'module'}));
  const api = await buildApplication(temp);
  for (const fixture of fixtures) await t.test(fixture.name, () => {
    const before = structuredClone(fixture);
    const actual = quotePrice(api,fixture.snapshot,fixture.request);
    for (const [key,value] of Object.entries(fixture.expected)) assert.deepEqual(actual[key],value,key);
    // Input order cannot choose an identity when cheapest prices tie.
    assert.deepEqual(quotePrice(api,{...fixture.snapshot,prices:[...fixture.snapshot.prices].reverse()},fixture.request),actual);
    assert.deepEqual(fixture,before);
    assert.equal(Object.isFrozen(actual),true);
  });
  const max = structuredClone(fixtures.find(f => f.name === 'uint64_max'));
  max.request.quantity = 2;
  assert.throws(() => quotePrice(api,max.snapshot,max.request),/CALCULATION_OVERFLOW/);
});
test('USD conversion is exact, bounded and refuses rounding or binary float input', () => {
  for (const [input,expected] of [['0',0n],['0.01',1n],['1.2',120n],['10.99',1099n],['90071992547409.93',9007199254740993n],['184467440737095516.15',UINT64_MAX]]) {
    assert.equal(usdToMinor(input),expected);
    assert.equal(usdToMinor(minorToUsd(expected)),expected);
  }
  for (const input of [10.99,NaN,Infinity,'-1','01','1e2','1.001','1.000',' 1','1.','+1','']) assert.throws(() => usdToMinor(input),/QUOTE_USD_DECIMAL/);
  assert.throws(() => usdToMinor('184467440737095516.16'),/QUOTE_MONEY_RANGE/);
  for (const value of [-1n,UINT64_MAX+1n,100]) assert.throws(() => minorToUsd(value),/QUOTE_MONEY_RANGE/);
});
test('adapter rejects unsupported or malformed requests and price snapshots', () => {
  const base = fixtures[0];
  const reject = (mutate, code) => {const f=structuredClone(base);mutate(f);assert.throws(()=>prepareQuote(f.snapshot,f.request),new RegExp(code));};
  for (const value of [undefined,null,0,-1,1.5,'15',2147483648,NaN]) reject(f=>f.request.quantity=value,'QUOTE_QUANTITY');
  for (const value of [undefined,null,'',123,' usd ']) reject(f=>f.request.currency_code=value,'QUOTE_CURRENCY_REQUIRED');
  reject(f=>f.request.currency_code='eur','QUOTE_UNSUPPORTED_CURRENCY');
  reject(f=>f.request.region_id='region','QUOTE_FIELD');
  reject(f=>f.request.variant_id='other','QUOTE_VARIANT_MISMATCH');
  reject(f=>f.snapshot.prices[0].price_set_id='other','QUOTE_PRICE_SET_MISMATCH');
  reject(f=>f.snapshot.prices.push(f.snapshot.prices[0]),'QUOTE_DUPLICATE_PRICE');
  reject(f=>f.snapshot.prices[0].price_list_id='sale','QUOTE_UNSUPPORTED_RULES');
  reject(f=>f.snapshot.prices[0].rules_count=1,'QUOTE_UNSUPPORTED_RULES');
  reject(f=>f.snapshot.prices[0].currency_code='USD','QUOTE_STORED_CURRENCY');
  reject(f=>f.snapshot.prices[0].deleted_at=false,'QUOTE_DELETED_AT');
  reject(f=>f.snapshot.prices[0].raw_amount.value='1.001','QUOTE_USD_DECIMAL');
  reject(f=>f.snapshot.prices[0].raw_amount.precision=10,'QUOTE_RAW_PRECISION');
  reject(f=>{f.snapshot.prices[0].min_quantity=20;f.snapshot.prices[0].max_quantity=10;},'QUOTE_TIER_RANGE');
  reject(f=>f.snapshot.prices[0].min_quantity=0,'QUOTE_QUANTITY');
  reject(f=>{Object.defineProperty(f.request,'quantity',{get(){throw Error('must not run');}});},'QUOTE_FIELD');
  const upper=structuredClone(base);upper.request.currency_code='USD';assert.equal(prepareQuote(upper.snapshot,upper.request).parameters.requestedCurrency,'usd');
});
