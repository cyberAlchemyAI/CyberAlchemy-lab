import assert from 'node:assert/strict';
import test from 'node:test';
import {fileURLToPath} from 'node:url';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.js';
import {createCoreCommerceSemanticOwner} from '../../src/commerce/commerce-core-semantic-owner.js';
import {projectCoreServiceTopologyV1} from '../../src/generic/core-topology-bridge.js';

const candidate=fileURLToPath(new URL('../../../../../../../examples/ecommerce-target-candidate/',import.meta.url)).replace(/\/$/,'');

test('unchanged Commerce source projects checked multi-service topology without executable admission',()=>{
 const sources=createCoreCommerceSourceOwner(),source=sources.prepare(candidate);
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(source);
 const topology=projectCoreServiceTopologyV1(sources,source,semantics,semantic);
 assert.equal(topology.schema_version,'craft.core-service-topology/v1-candidate');
 assert.equal(topology.services.length,5);
 assert.equal(topology.entries.length,22);
 assert.equal(topology.events.length,10);
 assert.equal(topology.workflows.length,1);
 assert.equal(topology.entries.filter(e=>e.principal_kind==='customer').length,2);
 assert.equal(topology.entries.filter(e=>e.principal_kind==='service').length,20);
 assert.deepEqual(new Set(topology.services.map(s=>s.id)),new Set(['catalog','orders','inventory','payments','fulfillment']));
 assert.equal(topology.entries.filter(e=>e.interaction==='event').length,2);
 assert.equal(topology.qualification,'checked-core-topology-only;generic-profile-native-and-application-admission-not-established');
 assert.equal(topology.authority_effect,'none');
 assert.equal(Object.isFrozen(topology),true);
 assert.equal(Object.isFrozen(topology.entries[0]),true);
 semantics.dispose(semantic);
 sources.dispose(source);
});

test('topology projection requires semantic and source handles from the same capture',()=>{
 const sources=createCoreCommerceSourceOwner(),source=sources.prepare(candidate);
 const semantics=createCoreCommerceSemanticOwner(sources),semantic=semantics.check(source);
 const other=sources.prepare(candidate);
 assert.throws(()=>projectCoreServiceTopologyV1(sources,other,semantics,semantic),/ForeignOwner/);
 semantics.dispose(semantic);
 sources.dispose(source);
 sources.dispose(other);
});
