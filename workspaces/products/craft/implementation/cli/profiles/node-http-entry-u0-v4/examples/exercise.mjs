import assert from 'node:assert/strict';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
// Consumer example only. Business behavior is imported from generated code.
// Open Questions: ../docs/SUPPORTED-CELL.md#open-questions.
if(process.argv.length!==3)throw Error('Usage: node exercise.mjs ABSOLUTE_OR_RELATIVE_GENERATED_DIRECTORY');
const directory=path.resolve(process.argv[2]),entry=await import(pathToFileURL(path.join(directory,'entry.mjs')).href);
for(const [verified,status,expected]of [
 [true,200,'{"kind":"completed","value":{"id":"9007199254740993","verified":true}}'],
 [false,422,'{"kind":"rejected","code":"delivery-verification-required"}']
]){
 const response=await entry.handler(new Request('https://example.invalid/confirm-delivery',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:'9007199254740993',verified})}));
 const body=await response.text();assert.equal(response.status,status);assert.equal(body,expected);console.log(JSON.stringify({status:response.status,body:JSON.parse(body)}));
}
