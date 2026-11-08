import test from 'node:test';
import assert from 'node:assert/strict';
import {selectCommerceGeneratedLocalReadKeyIndexV1}
 from '../../src/commerce/commerce-generated-local-read-key-v1.ts';

const shipment={name:'Fulfillment.Shipment',role:'Entity',entity:{
 identity:['shipmentId'],unique:[['orderId']]}};
const values={records:[shipment]};
const read=fields=>({kind:'read',entity:shipment.name,call:null,key:{key:fields}});

test('generated local read selects the checked unique Shipment orderId key',()=>{
 assert.equal(selectCommerceGeneratedLocalReadKeyIndexV1(values,read(['orderId']),
  Object.freeze({orderId:'order-one'})),1);
 assert.equal(selectCommerceGeneratedLocalReadKeyIndexV1(values,read(['shipmentId']),
  Object.freeze({shipmentId:'shipment-one'})),0);
});

test('generated local read rejects wrong, forged, and ambiguous keys before storage',()=>{
 assert.throws(()=>selectCommerceGeneratedLocalReadKeyIndexV1(values,read(['orderId']),
  {shipmentId:'shipment-one'}),/exactly one declared Entity identity or unique key/);
 assert.throws(()=>selectCommerceGeneratedLocalReadKeyIndexV1(values,read(['unknown']),
  {unknown:'value'}),/exactly one declared Entity identity or unique key/);
 assert.throws(()=>selectCommerceGeneratedLocalReadKeyIndexV1({records:[shipment,
  {...shipment}]},read(['orderId']),{orderId:'order-one'}),/one checked local read Entity/);
 assert.throws(()=>selectCommerceGeneratedLocalReadKeyIndexV1({records:[{
  ...shipment,entity:{identity:['shipmentId'],unique:[['orderId'],['orderId']]}}]},
  read(['orderId']),{orderId:'order-one'}),/exactly one declared Entity identity or unique key/);
});
