import test from 'node:test';
import assert from 'node:assert/strict';
import {selectCoreCommerceHttpGetSuccessProjection,projectCoreCommerceHttpGetSuccessValue}
 from '../../src/generic/core-commerce-http-success-projection.ts';

test('C14 checked optional Query projects the concrete HTTP value while preserving missing rejection',()=>{
 const query={kind:'local',query:{module:'Orders',role:'Query',name:'GetOrder'},output:{kind:'optional',element:{kind:'record',name:'Orders.OrderView'}},
  on_missing:{kind:'reject',code:'resource-not-found'}};
 const projection=selectCoreCommerceHttpGetSuccessProjection(query,'Orders.OrderView@1');
 assert.equal(projection.query,'Orders.GetOrder');
 assert.equal(projection.kind,'unwrap-some');
 const order={id:'order-one'};
 assert.equal(projectCoreCommerceHttpGetSuccessValue(projection,{kind:'some',value:order}),order);
 assert.throws(()=>projectCoreCommerceHttpGetSuccessValue(projection,{kind:'none'}),/no concrete HTTP success value/);
 assert.throws(()=>selectCoreCommerceHttpGetSuccessProjection(query,'Orders.OtherView@1'),/differs/);
 assert.throws(()=>selectCoreCommerceHttpGetSuccessProjection({...query,on_missing:{kind:'return'}},'Orders.OrderView@1'),/differs/);
});

test('C14 direct Query output is not unwrapped or changed',()=>{
 const query={kind:'local',query:{module:'Catalog',role:'Query',name:'ReadQuote'},output:{kind:'record',name:'Catalog.QuoteView'},on_missing:{kind:'reject'}};
 const projection=selectCoreCommerceHttpGetSuccessProjection(query,'Catalog.QuoteView@1');
 const quote={id:'quote-one'};
 assert.equal(projection.kind,'direct');
 assert.equal(projectCoreCommerceHttpGetSuccessValue(projection,quote),quote);
});
