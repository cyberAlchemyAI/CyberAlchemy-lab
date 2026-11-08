import assert from 'node:assert/strict';
import {mkdtempSync,rmSync,statSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {test} from 'node:test';
import {DatabaseSync} from 'node:sqlite';
import {build} from './C11-source-fixture.mjs';
import {loadOriginalGenericAuthAsset} from '../../src/generic/auth-asset.ts';
import {createCommerceAuthNativeOwnerFromSelectedAsset} from '../../src/commerce/commerce-auth-ready-bridge-v1.ts';
import {createGenericSqliteRepository} from '../../src/generic/sqlite-repository.ts';
import {openOriginalV3PreAuthStoreIdentity,inspectOriginalV3PreAuthEpoch,
  assertOriginalV3PreAuthMetadataCurrentOnce,assertOriginalV3PreAuthPhysicalCurrent,
  assertOriginalV3PreAuthDistinctFile,closeOriginalV3PreAuthStoreIdentity}
  from '../../src/generic/v3-preauth-store-identity.ts';

test('V3 pre-Auth accessor reads only the original created store metadata and agrees on epoch',async()=>{
  const model=build('ReviewDesk');
  const directory=mkdtempSync(path.join(tmpdir(),'craft-c11-preauth-'));
  let native,store,preAuth;
  try{
    native=createCommerceAuthNativeOwnerFromSelectedAsset(
      loadOriginalGenericAuthAsset(path.join(directory,'native')));
    const storePath=path.join(directory,'store.sqlite');
    store=createGenericSqliteRepository(model.plans,model.application,
      {service:'ReviewDeskService',storePath,mode:'create',nativeAuth:native});
    const originalEpoch=store.inspect().store_epoch_sha256;
    preAuth=openOriginalV3PreAuthStoreIdentity(model.plans,model.application,storePath);
    assert.deepEqual(inspectOriginalV3PreAuthEpoch(preAuth),
      {store_epoch_sha256:originalEpoch});
    assertOriginalV3PreAuthPhysicalCurrent(preAuth);
    assert.throws(()=>assertOriginalV3PreAuthDistinctFile(preAuth,storePath),
      error=>error?.code==='StoreUnavailable');
    const peerPath=path.join(directory,'peer.sqlite');
    writeFileSync(peerPath,'distinct file',{mode:0o600});
    assertOriginalV3PreAuthDistinctFile(preAuth,peerPath);
    assertOriginalV3PreAuthMetadataCurrentOnce(preAuth);
    assert.throws(()=>assertOriginalV3PreAuthMetadataCurrentOnce(preAuth),
      error=>error?.code==='StoreUnavailable');
    closeOriginalV3PreAuthStoreIdentity(preAuth);
    assert.throws(()=>inspectOriginalV3PreAuthEpoch(preAuth),
      error=>error?.code==='StoreUnavailable');
    preAuth=undefined;

    preAuth=openOriginalV3PreAuthStoreIdentity(model.plans,model.application,storePath);
    const sizeBefore=statSync(storePath).size;
    const peer=new DatabaseSync(storePath);
    try{
      const row=peer.prepare('SELECT compatibility FROM "_craft_generic_metadata" WHERE id=1').get();
      assert.equal(typeof row?.compatibility,'string');
      const changed=row.compatibility.replace(/("profile_sha256":")([0-9a-f])/,(_,head,digit)=>
        head+(digit==='a'?'b':'a'));
      assert.notEqual(changed,row.compatibility);
      assert.equal(changed.length,row.compatibility.length);
      peer.prepare('UPDATE "_craft_generic_metadata" SET compatibility=? WHERE id=1').run(changed);
    }finally{peer.close();}
    assert.equal(statSync(storePath).size,sizeBefore);
    assert.throws(()=>assertOriginalV3PreAuthMetadataCurrentOnce(preAuth),
      error=>error?.code==='StoreUnavailable');
    closeOriginalV3PreAuthStoreIdentity(preAuth);
    preAuth=undefined;
  }finally{
    if(preAuth)closeOriginalV3PreAuthStoreIdentity(preAuth);
    store?.close();
    await native?.dispose();
    rmSync(model.root,{recursive:true,force:true});
    rmSync(directory,{recursive:true,force:true});
  }
});
