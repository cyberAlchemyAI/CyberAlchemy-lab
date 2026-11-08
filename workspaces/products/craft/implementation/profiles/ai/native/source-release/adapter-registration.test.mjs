/** Original adapter registration lifetime; no caller-owned unregister authority.
 * Open Questions: README.md. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {createSourceReleaseService} from './index.mjs';
function fixture(t){const root=mkdtempSync(path.join(tmpdir(),'craft-source-registration-')),release=createSourceReleaseService({path:path.join(root,'release.sqlite'),now:()=>1000});t.after(()=>{release.close();rmSync(root,{recursive:true,force:true});});const source=({id})=>({id,tenant:'t',revision:'1',aclRevision:'1',readers:['u'],classifications:['internal'],bytes:Buffer.from('record')});return {release,adapter:{readCurrent:source}};}
test('original registration retires idempotently and cannot remove its successor',t=>{
 const {release,adapter}=fixture(t),old=release.authority.registerAdapter('query',adapter);assert.ok(Object.isFrozen(old));old.assertCurrent();assert.throws(()=>release.authority.registerAdapter('query',adapter),/SOURCE_ADAPTER_CONFLICT/);old.retire();assert.throws(()=>old.assertCurrent(),/SOURCE_ADAPTER_UNAVAILABLE/);const next=release.authority.registerAdapter('query',adapter);old.retire();next.assertCurrent();next.retire();assert.throws(()=>next.assertCurrent(),/SOURCE_ADAPTER_UNAVAILABLE/);
});
test('retiring an adapter invalidates existing manifest/ticket currentness',t=>{
 const {release,adapter}=fixture(t),registration=release.authority.registerAdapter('query',adapter);release.authority.defineContext({id:'c',tenant:'t',principal:'u',inputs:[{adapter:'query',id:'p1'}]});release.authority.setPolicy({id:'p',revision:'1',tenants:['t'],actions:['update'],sinks:['crm'],recipients:['acct'],classifications:['internal'],requireRecipientRead:false});const manifest=release.port.captureContext({contextId:'c',tenant:'t',principal:'u'}),binding={attemptId:'a',fence:1,resourceId:'r',action:'update',sink:'crm',recipient:'acct',payload:Buffer.from('update'),tenant:'t',principal:'u'},ticket=release.port.issueRelease({manifest,policyId:'p',expiresAt:2000,...binding});registration.retire();assert.throws(()=>release.port.consumeRelease(ticket,binding),/SOURCE_ADAPTER_UNAVAILABLE/);assert.throws(()=>release.port.captureContext({contextId:'c',tenant:'t',principal:'u'}),/SOURCE_ADAPTER_UNAVAILABLE/);
});
test('registration token is scoped to its service; a foreign retirement does not affect another owner',t=>{
 const a=fixture(t),b=fixture(t),first=a.release.authority.registerAdapter('query',a.adapter),second=b.release.authority.registerAdapter('query',b.adapter);first.retire();second.assertCurrent();assert.throws(()=>a.release.authority.registerAdapter('inline',a.adapter),/SOURCE_ADAPTER_CONFLICT/);assert.throws(()=>a.release.authority.registerAdapter('invalid',{}),/SOURCE_ADAPTER_CONFLICT/);assert.equal('unregisterAdapter' in a.release.authority,false);second.retire();
});
test('service close invalidates outstanding registration and rejects late registration',t=>{
 const {release,adapter}=fixture(t),registration=release.authority.registerAdapter('query',adapter);release.close();assert.throws(()=>registration.assertCurrent(),/SOURCE_ADAPTER_UNAVAILABLE/);assert.throws(()=>release.authority.registerAdapter('query2',adapter),/SOURCE_ADAPTER_UNAVAILABLE/);registration.retire();release.close();
});
