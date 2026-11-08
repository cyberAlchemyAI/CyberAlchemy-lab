import assert from 'node:assert/strict';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const {evaluate}=await import(pathToFileURL(path.join(path.resolve(process.argv[2]??'generated'),'rule.mjs')).href);
const encode=value=>new TextEncoder().encode(JSON.stringify(value));
for(const [verified,flagged,expected] of [[true,false,true],[false,true,false],[true,true,true]]){
 const result=await evaluate(encode({request:{verified,flagged}}));
 assert.equal(result.ok,true);
 const actual=JSON.parse(new TextDecoder().decode(result.wire));
 assert.equal(actual,expected);
 console.log(JSON.stringify({verified,flagged,result:actual}));
}
const invalid=await evaluate(encode({request:{verified:'true',flagged:false}}));
assert.equal(invalid.ok,false);
console.log('Wrong input types reject; no formal claim is required.');
