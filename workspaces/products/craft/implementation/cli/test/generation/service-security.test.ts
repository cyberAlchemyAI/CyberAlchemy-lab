import test from 'node:test';
import assert from 'node:assert/strict';
import {compileServiceSecurity} from '../../src/typed-backend/service-security.js';
const secure={authentication:'auth-foundation',authorization:'tenant-permissions',scope:'tenant-principal'};
test('explicit public and protected route contract admits only the selected complete profile',()=>{
 assert.deepEqual(compileServiceSecurity(secure,[{access:'public'},{access:'protected'}]),secure);
 assert.doesNotThrow(()=>compileServiceSecurity({authentication:'deferred',authorization:'deferred',scope:'shared-public'},[{}]));
 for(const x of [null,[],{...secure,scope:'shared-public'},{...secure,authentication:'deferred'},{...secure,extra:true}])assert.throws(()=>compileServiceSecurity(x,[{access:'protected'}]),/SERVICE_SECURITY_CONTRACT/);
});
test('missing and invalid route access cannot silently make protected routes public',()=>{
 for(const routes of [[{}],[{access:'anonymous'}],[],Array(33).fill({access:'protected'})])assert.throws(()=>compileServiceSecurity(secure,routes),/SERVICE_SECURITY_CONTRACT/);
});
