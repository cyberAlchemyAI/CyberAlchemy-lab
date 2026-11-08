import test from 'node:test';
import assert from 'node:assert/strict';
import {mayAttestProviderNoEffect,mayCompensateProviderFailure,providerEffectPossibleAfterObservation}
  from '../../src/generic/provider-effect-evidence.ts';

const sha='0'.repeat(64);
const failed={schema_version:'craft.generic-command-result/v1-candidate',ok:true,
  outcome:{kind:'Rejected',code:'provider-declined'},fuel_used:1,
  observation:{kind:'business-rejected',command_tuple_sha256:sha,result_sha256:sha}};
const providerStep={kind:'provider-command',on_definite_failure:'compensate',
  provider_failure_compensation_precondition:'proven-no-provider-effect'};

test('fresh checked decline or pre-dispatch rejection permits no-effect attestation',()=>{
  assert.equal(mayAttestProviderNoEffect(true,failed,false),true);
  assert.equal(providerEffectPossibleAfterObservation(false,'DefinitivelyDeclined'),false);
  assert.equal(mayAttestProviderNoEffect(true,failed,
    providerEffectPossibleAfterObservation(false,'DefinitivelyDeclined')),true);
  assert.equal(mayCompensateProviderFailure(providerStep,true),true);
});

test('capture, unknown result, earlier possible effect, and replay never attest no effect',()=>{
  for(const observation of ['Captured',null])
    assert.equal(mayAttestProviderNoEffect(true,failed,
      providerEffectPossibleAfterObservation(false,observation)),false);
  assert.equal(providerEffectPossibleAfterObservation(true,'DefinitivelyDeclined'),true);
  assert.equal(mayAttestProviderNoEffect(false,failed,false),false);
  assert.equal(mayCompensateProviderFailure(providerStep,false),false);
  assert.equal(mayCompensateProviderFailure({...providerStep,
    provider_failure_compensation_precondition:undefined},true),false);
  const succeeded={...failed,outcome:{kind:'Returned',value:{kind:'unit'}}};
  assert.equal(mayAttestProviderNoEffect(true,succeeded,false),false);
});
