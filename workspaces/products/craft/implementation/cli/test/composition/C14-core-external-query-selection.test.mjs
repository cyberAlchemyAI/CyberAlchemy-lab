import test from 'node:test';
import assert from 'node:assert/strict';
import {selectCoreCommerceExternalQueries} from '../../src/generic/core-commerce-external-query-selection.ts';

const entry={id:'Catalog.ReadQuoteEntry',service:'catalog',invokes:{role:'Query',module:'Catalog',name:'ReadQuote'},
 access:{principal_kind:'service',caller:'orders',auth_permission:{resource:'catalog',action:'quote.read',scope:'commerce-shop'}}};
const call={target:'Catalog.ReadQuote',entry:entry.id,role:'Query',authorization:'fresh-original-entry-decision-required',
 arguments:[],contexts:[]};
const plan={service:'orders',body:[{kind:'read',call}]};

test('C14 derives external Query target, service actor and permission from the same checked source call and Entry',()=>{
 const selected=selectCoreCommerceExternalQueries(plan,[entry],['orders','catalog']);
 assert.deepEqual(selected,[{query:'Catalog.ReadQuote',entry:'Catalog.ReadQuoteEntry',target_service:'catalog',
  caller_service:'orders',permission:{resource:'catalog',action:'quote.read',scope:'commerce-shop'},
  scope:'commerce-shop',source_call_paths:['$.body[0].call']}]);
 assert.ok(Object.isFrozen(selected));
});

test('C14 rejects a foreign service caller, target, Entry or unselected service before opening a Query runtime',()=>{
 assert.throws(()=>selectCoreCommerceExternalQueries(plan,[{...entry,access:{...entry.access,caller:'inventory'}}],['orders','catalog']),/checked source Entry/);
 assert.throws(()=>selectCoreCommerceExternalQueries({...plan,body:[{kind:'read',call:{...call,target:'Catalog.Other'}}]},[entry],['orders','catalog']),/checked source Entry/);
 assert.throws(()=>selectCoreCommerceExternalQueries({...plan,body:[{kind:'read',call:{...call,entry:'Catalog.OtherEntry'}}]},[entry],['orders','catalog']),/checked source Entry/);
 assert.throws(()=>selectCoreCommerceExternalQueries(plan,[entry],['orders']),/checked source Entry/);
});
