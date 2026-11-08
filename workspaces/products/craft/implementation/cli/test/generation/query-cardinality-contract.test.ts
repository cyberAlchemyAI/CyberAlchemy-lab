import assert from 'node:assert/strict';
import test from 'node:test';
import {decodeTypedQueryContract, queryReturnsOptional} from '../../src/typed-backend/contracts.ts';
import {QUERY_CARDINALITY_EXTENSION, queryCardinalityExtension} from '../../src/generation/query-cardinality-extension.ts';
import {canonicalJson, sha256} from '../../src/input/source-manifest.ts';
import {renderImplementation} from '../../src/generation/generators.ts';
import {validateSelectedNodeRelationships} from '../../src/input/project-model.ts';

const legacy = {schema_version:'domainspec.typed-query/v1',ontology_query:'FIXTURE-FIND-ORDER',source:'commerce:order',inputs:[],filter:null,projection:['id'],order_by:null,limit:null};
test('Query cardinality is closed, explicit and cannot hide extra matches behind a limit', () => {
  const v1 = decodeTypedQueryContract(legacy);
  assert.deepEqual(v1, legacy); assert.equal(queryReturnsOptional(v1), false);
  assert.deepEqual(queryCardinalityExtension(v1, 'typescript'), {});
  for (const result_cardinality of ['list','optional']) {
    const input = {...legacy,schema_version:'domainspec.typed-query/v2',result_cardinality};
    const decoded = decodeTypedQueryContract(input);
    assert.deepEqual(decoded,input); assert.ok(Object.isFrozen(decoded));
    assert.equal(queryReturnsOptional(decoded), result_cardinality === 'optional');
    for (const language of ['typescript','python','rust'] as const) {
      const extension = queryCardinalityExtension(decoded, language);
      assert.equal(extension.protocol_id, `${language}.bound-query/v2-candidate`);
      assert.equal(extension.cardinality_extension!.sha256, sha256(canonicalJson(QUERY_CARDINALITY_EXTENSION)));
    }
  }
  for(const patch of [{schema_version:'domainspec.typed-query/v2'},
    {result_cardinality:'optional'},
    {schema_version:'domainspec.typed-query/v2',result_cardinality:'first'},
    {schema_version:'domainspec.typed-query/v2',result_cardinality:'optional',limit:1},
    {schema_version:'domainspec.typed-query/v2',result_cardinality:'optional',limit:2},
    {schema_version:'domainspec.typed-query/v2',result_cardinality:'optional',hidden:true}]) {
    assert.throws(() => decodeTypedQueryContract({...legacy,...patch}));
  }
});

test('legacy realization cannot silently render optional Query as a list or unchecked stub', () => {
  for(const language of ['typescript','python','rust']) {
    assert.throws(() => renderImplementation({kind:'Query',body:{typed_contract:{...legacy,schema_version:'domainspec.typed-query/v2',result_cardinality:'optional'}},realization:{language}} as any), /MTCLI_QUERY_PROFILE_REQUIRED/);
  }
});

test('optional Query retains the exact canonical reads relationship', () => {
  const contract=decodeTypedQueryContract({...legacy,schema_version:'domainspec.typed-query/v2',result_cardinality:'optional'});
  const edge={relationship:'reads',source:{feature_id:'commerce',node_id:'find-order'},target:{feature_id:'commerce',node_id:'order'}};
  const node={kind:'Query',feature_id:'commerce',node_id:'find-order',body:{typed_contract:contract},relationships:[edge]};
  assert.doesNotThrow(()=>validateSelectedNodeRelationships(node as any));
  for(const relationships of [[],[edge,edge],[{...edge,target:{feature_id:'commerce',node_id:'other'}}]]) {
    assert.throws(()=>validateSelectedNodeRelationships({...node,relationships} as any), /exactly one reads edge/);
  }
});
