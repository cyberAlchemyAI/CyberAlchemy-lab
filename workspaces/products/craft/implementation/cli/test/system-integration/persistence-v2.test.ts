import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { compilePersistenceCompositionV2, PersistenceCompositionError, validatePersistenceCompositionV2 } from "../../src/system-integration/persistence-v2.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixturePath = path.resolve(here, "../../../system-integration/fixtures/persistence-composition-v2/commerce-postgresql.json");
const schemaPath = path.resolve(here, "../../../system-integration/contracts/persistence-composition-v2.schema.json");
const fixture = JSON.parse(fs.readFileSync(fixturePath, "utf8"));
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T;

test("R3 persistence composition is deterministic and preserves all logical shapes", () => {
  const left = compilePersistenceCompositionV2(fixture);
  const right = compilePersistenceCompositionV2(clone(fixture));
  assert.deepEqual(left, right);
  assert.match(left.composition_digest, /^[a-f0-9]{64}$/);
  assert.match(left.integration_kernel.kernel_digest, /^[a-f0-9]{64}$/);
  assert.deepEqual([...new Set(left.persistence_mappings[0]!.field_mappings.map(item => item.logical_shape))].sort(), ["entity-reference", "enum", "list", "optional", "scalar", "set", "sum", "value-object"]);
  assert.equal(left.runtime_guarantees_observed, false);
  assert.equal(left.authority_effect, "none");
});

test("R3 schema closes every persistence and migration record", () => {
  const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
  assert.equal(schema.additionalProperties, false);
  for (const name of ["persistenceBinding", "physicalModel", "identityMapping", "fieldMapping", "relationMapping", "indexMapping", "conversionRule", "persistenceMapping", "transactionGuarantee", "migrationStep", "migration"]) {
    assert.equal(schema.$defs[name].additionalProperties, false, name);
  }
});

test("D46 specialization must agree exactly with the shared integration kernel", () => {
  const changed = clone(fixture);
  changed.persistence_bindings[0].resource_ref = "resource:other-database";
  assert.throws(() => validatePersistenceCompositionV2(changed), (error) => error instanceof PersistenceCompositionError && error.code === "PERSISTENCE_BINDING_DRIFT");
});

test("logical-to-physical mapping references and identities fail closed", () => {
  const missingConversion = clone(fixture);
  missingConversion.persistence_mappings[0].field_mappings.find((item: { logical_shape: string }) => item.logical_shape === "value-object").conversion_ref = "conversion:missing";
  assert.throws(() => validatePersistenceCompositionV2(missingConversion), (error) => error instanceof PersistenceCompositionError && error.code === "PERSISTENCE_REFERENCE_UNRESOLVED");
  const changedIdentity = clone(fixture);
  changedIdentity.persistence_mappings[0].identity_mappings[0].physical_field_ref = "physical:customers/other-id";
  assert.throws(() => validatePersistenceCompositionV2(changedIdentity), (error) => error instanceof PersistenceCompositionError && error.code === "PERSISTENCE_IDENTITY_DRIFT");
});

test("logical property references preserve snake-case field identities", () => {
  const changed = clone(fixture);
  const field = changed.persistence_mappings[0].field_mappings[0];
  field.logical_property_ref = "commerce:order#billing_customer_id";
  changed.persistence_mappings[0].identity_mappings[0].logical_property_ref = field.logical_property_ref;
  assert.equal(validatePersistenceCompositionV2(changed).persistence_mappings[0]!.field_mappings.some(item => item.logical_property_ref === "commerce:order#billing_customer_id"), true);
});

test("relation fields must belong to their declared source and target physical models", () => {
  const changed = clone(fixture);
  changed.persistence_mappings[0].relation_mappings[0].target_field_ref = "physical:other/id";
  assert.throws(() => validatePersistenceCompositionV2(changed), (error) => error instanceof PersistenceCompositionError && error.code === "PERSISTENCE_RELATION_FIELD");
});

test("optional, list, and set cardinalities cannot collapse", () => {
  const listAsSet = clone(fixture);
  listAsSet.persistence_mappings[0].field_mappings.find((item: { logical_shape: string }) => item.logical_shape === "list").collection_semantics = "unique-unordered";
  assert.throws(() => validatePersistenceCompositionV2(listAsSet), (error) => error instanceof PersistenceCompositionError && error.code === "PERSISTENCE_CARDINALITY_COLLAPSE");
  const optionalAsScalar = clone(fixture);
  optionalAsScalar.persistence_mappings[0].field_mappings.find((item: { logical_shape: string }) => item.logical_shape === "optional").storage_shape = "scalar";
  assert.throws(() => validatePersistenceCompositionV2(optionalAsScalar), (error) => error instanceof PersistenceCompositionError && error.code === "PERSISTENCE_SHAPE_COLLAPSE");
});

test("D47 exposes exactly one local commit boundary without claiming runtime proof", () => {
  const compiled = validatePersistenceCompositionV2(fixture);
  assert.equal(compiled.transaction_guarantees[0]!.atomicity_scope, "single-resource-local");
  assert.equal(compiled.transaction_guarantees[0]!.local_commit_boundary_ref, "commit-boundary:orders-database-transaction");
  assert.equal(compiled.transaction_guarantees[0]!.runtime_guarantees_observed, false);
  const secondBoundary = clone(fixture);
  secondBoundary.transaction_guarantees[0].local_commit_boundary_refs = ["commit-boundary:first", "commit-boundary:second"];
  assert.throws(() => validatePersistenceCompositionV2(secondBoundary), (error) => error instanceof PersistenceCompositionError && error.code === "PERSISTENCE_SCHEMA");
});

test("migration rollback posture cannot contradict its declared steps", () => {
  const forwardOnly = clone(fixture);
  forwardOnly.migrations[0].rollback_posture = "forward-only";
  assert.throws(() => validatePersistenceCompositionV2(forwardOnly), (error) => error instanceof PersistenceCompositionError && error.code === "PERSISTENCE_ROLLBACK");
  const noVerification = clone(fixture);
  noVerification.migrations[0].verification_refs = [];
  assert.throws(() => validatePersistenceCompositionV2(noVerification), (error) => error instanceof PersistenceCompositionError && error.code === "PERSISTENCE_SCHEMA");
});

test('ordered index keys preserve sequence; unordered keys preserve set identity',()=>{
 const input=clone(fixture),mapping=input.persistence_mappings[0];
 const index=mapping.index_mappings.find((i:any)=>i.index_id==='index:orders-customer');
 index.field_refs=['physical:orders/id','physical:orders/customer-id'];
 const forward=compilePersistenceCompositionV2(input);
 index.field_refs.reverse();const reverse=compilePersistenceCompositionV2(input);
 assert.notEqual(forward.composition_digest,reverse.composition_digest);
 assert.deepEqual(forward.persistence_mappings[0]!.index_mappings.find(i=>i.index_id===index.index_id)!.field_refs,['physical:orders/id','physical:orders/customer-id']);
 index.order='unordered';const left=compilePersistenceCompositionV2(input);index.field_refs.reverse();
 assert.deepEqual(compilePersistenceCompositionV2(input),left);
});

test('index fields require exact mapped membership and exactly their declared model',()=>{
 for(const field of ['physical:orders/missing','physical:customers/id','physical:absent/id']){
  const input=clone(fixture);input.persistence_mappings[0].index_mappings.find((i:any)=>i.index_id==='index:orders-customer').field_refs=[field];
  assert.throws(()=>validatePersistenceCompositionV2(input),{code:'PERSISTENCE_INDEX_FIELD'});
 }
 const input=clone(fixture),m=input.persistence_mappings[0];
 m.physical_models.push({model_id:'physical-model:orders/nested',model_kind:'relational-table',physical_name:'nested_orders',version:'v2'});
 m.field_mappings.push({...m.field_mappings[0],logical_property_ref:'commerce:order#nested-id',physical_field_ref:'physical:orders/nested/id'});
 m.index_mappings.find((i:any)=>i.index_id==='index:orders-customer').field_refs=['physical:orders/nested/id'];
 assert.throws(()=>validatePersistenceCompositionV2(input),{code:'PERSISTENCE_INDEX_FIELD'});
 // Even exact membership cannot grant ownership to a field in no model namespace.
 m.field_mappings.at(-1).physical_field_ref='physical:absent/id';m.index_mappings.find((i:any)=>i.index_id==='index:orders-customer').field_refs=['physical:absent/id'];
 assert.throws(()=>validatePersistenceCompositionV2(input),{code:'PERSISTENCE_INDEX_FIELD'});
});

test('both ordered and unordered index keys reject empty and duplicate fields',()=>{
 for(const order of ['ordered','unordered'])for(const fields of [[],['physical:orders/id','physical:orders/id']]){
  const input=clone(fixture),index=input.persistence_mappings[0].index_mappings.find((i:any)=>i.index_id==='index:orders-customer');index.order=order;index.field_refs=fields;
  assert.throws(()=>validatePersistenceCompositionV2(input),{code:fields.length?'PERSISTENCE_DUPLICATE':'PERSISTENCE_SCHEMA'});
 }
});

test('an ambiguous mapped index field rejects even when selecting its narrower declared namespace',()=>{
 const input=clone(fixture),m=input.persistence_mappings[0];
 m.physical_models.push({model_id:'physical-model:orders/nested',model_kind:'relational-table',physical_name:'nested_orders',version:'v2'});
 m.field_mappings.push({...m.field_mappings[0],logical_property_ref:'commerce:order#nested-id',physical_field_ref:'physical:orders/nested/id'});
 const index=m.index_mappings.find((i:any)=>i.index_id==='index:orders-customer');
 index.model_ref='physical-model:orders/nested';index.field_refs=['physical:orders/nested/id'];
 assert.throws(()=>validatePersistenceCompositionV2(input),{code:'PERSISTENCE_INDEX_FIELD'});
});

test('ordered normalization preserves input and ordinary arbitrary mapped model identities',()=>{
 const input=clone(fixture),m=input.persistence_mappings[0];
 m.physical_models.push({model_id:'physical-model:research-samples',model_kind:'relational-table',physical_name:'research_samples',version:'v2'});
 for(const key of ['released','sample-id'])m.field_mappings.push({...m.field_mappings[0],logical_property_ref:'commerce:order#sample-'+key,physical_field_ref:'physical:research-samples/'+key});
 m.index_mappings.push({index_id:'index:sample-release',model_ref:'physical-model:research-samples',physical_name:'sample_release_idx',field_refs:['physical:research-samples/sample-id','physical:research-samples/released'],unique:false,order:'ordered'});
 const before=clone(input),result=compilePersistenceCompositionV2(input);
 assert.deepEqual(input,before);
 assert.deepEqual(result.persistence_mappings[0]!.index_mappings.find(i=>i.index_id==='index:sample-release')!.field_refs,m.index_mappings.at(-1).field_refs);
 assert.ok(Object.isFrozen(result.persistence_mappings[0]!.index_mappings.find(i=>i.index_id==='index:sample-release')!.field_refs));
});
