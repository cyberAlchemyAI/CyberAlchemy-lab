/** Finite error renderer checks; actual application binding tested at integration.
 * Open Questions: docs/ERROR-PRESENTATION.md#open-questions. */
import test from 'node:test';import assert from 'node:assert/strict';
import {renderGenericPlatformError,renderGenericErrorPresentation,createGenericErrorPresentationBinding,assertGenericErrorPresentationRuntime} from '../../src/generic/error-presentation.js';
test('fixed platform errors retain authentication vs provider/unknown distinction',async()=>{
 for(const [code,status]of [['AuthenticationRequired',401],['PermissionDenied',403],['ExternalOutcomeUnknown',503],['MalformedRequest',400],['RouteNotFound',404]]as const){const r=renderGenericPlatformError(code,status),body=await r.json();assert.equal(r.status,status);assert.equal(body.kind,'error');assert.equal(body.error.code,code);assert.match(body.error.correlationId,/^[a-f0-9]{32}$/);assert.equal(r.headers.get('cache-control'),'no-store');}
});
test('unknown platform strings and status spoofing are fixed safe500',async()=>{
 for(const [code,status]of [['secret-token@example.com',400],['AuthenticationRequired',200],['provider-authorization-denied',401]]as const){const r=renderGenericPlatformError(code,status);assert.equal(r.status,500);const raw=await r.text();assert.equal(raw.includes(code),false);assert.ok(Buffer.byteLength(raw)<=4096);}
});
test('fixed fallback is nonrecursive and never echoes forged business result content',async()=>{const result=renderGenericErrorPresentation({kind:'original-error-presentation-binding/v1'},{entry:'Private.X',outcomeKind:'Rejected',code:'secret\r\nheader'});assert.equal(result.status,500);assert.equal((await result.text()).includes('secret'),false);});
test('public correlation tokens are fresh and never command identity',async()=>{const a=await renderGenericPlatformError('PermissionDenied',403).json(),b=await renderGenericPlatformError('PermissionDenied',403).json();assert.notEqual(a.error.correlationId,b.error.correlationId);assert.deepEqual(Object.keys(a.error).sort(),['category','code','correlationId','message','presentationVersion']);});
test('foreign technical/application bindings fail before any response authority is installed',()=>{assert.throws(()=>createGenericErrorPresentationBinding({sourceOwner:{} as any,sourceHandle:{} as any,businessOwner:{},businessHandle:{} as any}));assert.throws(()=>assertGenericErrorPresentationRuntime({kind:'original-error-presentation-binding/v1'},{} as any),/FOREIGN_BINDING/);});
