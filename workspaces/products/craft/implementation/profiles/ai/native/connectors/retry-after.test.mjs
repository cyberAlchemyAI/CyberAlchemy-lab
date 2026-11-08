import test from 'node:test';
import assert from 'node:assert/strict';
import {parseRetryAfter,providerError} from './shared.mjs';
const at=Date.parse('Wed, 21 Oct 2015 07:28:00 GMT');
test('provider seconds are preserved beyond a minute and are not silently capped',()=>{for(const [raw,ms] of [['0',0],['120',120000],['86400',86400000],[' 180 ',180000]])assert.equal(parseRetryAfter(raw,at),ms);});
test('HTTP-date uses captured receipt time and conservatively accounts for server clock',()=>{assert.equal(parseRetryAfter('Wed, 21 Oct 2015 07:30:00 GMT',at),120000);assert.equal(parseRetryAfter('Wed, 21 Oct 2015 07:30:00 GMT',at+180000,'Wed, 21 Oct 2015 07:28:00 GMT'),120000);assert.equal(parseRetryAfter('Wed, 21 Oct 2015 07:20:00 GMT',at),0);});
test('invalid and unrepresentable delays never become permission to retry immediately',()=>{for(const raw of ['-1','1.5','tomorrow','Wed, 99 Oct 2015 07:30:00 GMT','9007199254740991','9'.repeat(129)]){assert.equal(parseRetryAfter(raw,at),null);assert.deepEqual(providerError({status:429,headers:{'retry-after':raw},receivedAtMs:at}),{kind:'unknown',reason:'retry-delay-unavailable',status:429});}});
test('rate-limit observation carries exact minimum delay and no hidden scheduling',()=>{assert.deepEqual(providerError({status:429,headers:{'retry-after':'Wed, 21 Oct 2015 07:30:00 GMT'},receivedAtMs:at}),{kind:'no-effect',reason:'rate-limited',retryAfterMs:120000,retryable:true});assert.equal(providerError({status:429,headers:{},receivedAtMs:at}).retryAfterMs,0);});

test('obsolete HTTP-date forms preserve the same provider minimum',()=>{const clock=Date.parse('Sun, 06 Nov 1994 08:47:37 GMT');for(const value of ['Sun, 06 Nov 1994 08:49:37 GMT','Sunday, 06-Nov-94 08:49:37 GMT','Sun Nov  6 08:49:37 1994'])assert.equal(parseRetryAfter(value,clock),120000);});

test('permanent provider rejections do not advertise automatic repeatability',()=>{for(const status of [400,401,403,404,409,422])assert.equal(providerError({status,headers:{},receivedAtMs:at}).retryable,false);});
