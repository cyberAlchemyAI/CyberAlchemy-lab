import assert from 'node:assert/strict';
import test from 'node:test';
import {projectOperationalExpectations} from '../../src/profile-engine/operational-expectations.js';
// Open questions: live observations/normalizers/sinks remain separately qualified.
const identity={source_sha256:'a'.repeat(64),lock_sha256:'b'.repeat(64)};
const declaration={schema_version:'craft.profile-orodi-declaration/v1',id:'ApiObservations',required:false,mode:'offline-expectations',families:['telemetry','health-failure'],observation_points:['request-start','request-result'],failure_codes:['FUNCTION_INTEGRATION_TIMEOUT'],disclosure:{allowed_attribute_keys:['intent','code'],max_attributes:2,max_string_length:128}};
test('absence and offline declarations cannot manufacture runtime evidence',()=>{
 const absent=projectOperationalExpectations([],identity),present=projectOperationalExpectations([declaration],identity);assert.equal((absent.states as any).declaration,'absent');assert.equal((present.states as any).declaration,'declared');
 assert.equal((present.states as any).offline_validation,'not-run');assert.equal((present.states as any).replay,'not-run');assert.equal((present.states as any).current_observation,'not-run');assert.equal((present.states as any).telemetry_accounting,'not-run');assert.equal((present.states as any).runtime_admission,'denied');assert.deepEqual(present.runtime_admitted_observations,[]);assert.deepEqual(present.eligible_controls,[]);
 assert.deepEqual(projectOperationalExpectations([declaration],identity),present);
});
test('forged live states and unsupported required mechanisms/families reject',()=>{
 for(const extra of [{runtime_admission:'admitted'},{observations:[{status:'passed'}]},{accounted:true},{proved:true}])assert.throws(()=>projectOperationalExpectations([{...declaration,...extra}],identity),/PROFILE_ORODI_DECLARATION/);
 assert.throws(()=>projectOperationalExpectations([{...declaration,required:true,mode:'live'}],identity),/PROFILE_ORODI_MECHANISM_UNSUPPORTED/);
 assert.throws(()=>projectOperationalExpectations([{...declaration,families:['infrastructure-plan']}],identity),/PROFILE_ORODI_FAMILY_UNSUPPORTED/);
 assert.throws(()=>projectOperationalExpectations([{...declaration,disclosure:{...declaration.disclosure,allowed_attribute_keys:['api_token']}}],identity),/PROFILE_ORODI_DISCLOSURE/);
});
