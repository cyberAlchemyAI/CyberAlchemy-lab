import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync, spawnSync} from 'node:child_process';
import {loadCompiledProjectGraph} from '../../src/input/project-model.ts';
import {createCompiledProjectCertificate} from '../../src/compilation/certificate.ts';
import {compileCompositionBoundary, COMPOSITION_BOUNDARY_CONTRACT_SHA256, COMPOSITION_BOUNDARY_VERSION} from '../../src/input/composition-boundary.ts';
import {getReconciledSource} from '../../src/generation/reconciled-sources.ts';
import {planConfiguredRustEvents, RUST_EVENT_CONTRACT_SHA256, RUST_EVENT_PROTOCOL, RUST_EVENT_SELECTION_VERSION} from '../../src/generation/configured-rust-events.ts';
import {rustSelectorModule} from '../../src/generation/configured-rust-values.ts';
import {pythonAllTypesFixture} from './reconciled-python-fixture.ts';

const cargo = process.env.CARGO ?? 'cargo';
const contractPath = path.resolve(import.meta.dirname, '../../../../development/reconciliation-v1/profile-compiler-reconciliation/rust-event-generation-contract.json');
const primitive = (name: string) => ({kind: 'primitive', name});

function fixture(t: any) {
  const source = pythonAllTypesFixture(t), featurePath = path.join(source.source, 'specs/alpha/feature.json'), feature = JSON.parse(fs.readFileSync(featurePath, 'utf8'));
  feature.nodes.push('generated');
  source.write('specs/alpha/nodes/generated.json', {schema_version: 'domainspec.node/v1', feature_id: 'alpha', node_id: 'generated', kind: 'Event', body: {description: 'generated', event_type: 'generated', version: '2', occurrence_id: {field_id: 'event-id', type_ref: primitive('uuid'), required: true}, occurred_at_policy: 'generated', payload: [{field_id: 'active', type_ref: primitive('boolean'), required: true}, {field_id: 'count', type_ref: primitive('integer'), required: true}, {field_id: 'note', type_ref: primitive('string'), required: false}, {field_id: 'order-ref', type_ref: {kind: 'reference', selector: 'alpha:order'}, required: true}, {field_id: 'ratio', type_ref: primitive('decimal'), required: true}, {field_id: 'source-at', type_ref: primitive('timestamp'), required: false}]}});
  fs.writeFileSync(featurePath, JSON.stringify(feature, null, 2) + '\n');
  const graph = loadCompiledProjectGraph(source.source), certificate = createCompiledProjectCertificate(graph);
  const boundary = compileCompositionBoundary(graph, {schema_version: COMPOSITION_BOUNDARY_VERSION, contract_sha256: COMPOSITION_BOUNDARY_CONTRACT_SHA256, graph_sha256: certificate.graph_sha256}, getReconciledSource('composition'));
  const selection = {schema_version: RUST_EVENT_SELECTION_VERSION, language: 'rust' as const, module_root: 'relocated/domain', roots: ['alpha:posted', 'alpha:generated'], boundary_sha256: boundary.boundary_sha256};
  const contract = fs.readFileSync(contractPath, 'utf8');
  return {...source, graph, boundary, selection, contract, plan: planConfiguredRustEvents(graph, boundary, selection, contract)};
}

function crate(root: string, plan: ReturnType<typeof planConfiguredRustEvents>, main: string) {
  fs.mkdirSync(path.join(root, 'src/domain/events'), {recursive: true});
  fs.writeFileSync(path.join(root, 'Cargo.toml'), '[package]\nname="rust-event-check"\nversion="0.0.0"\nedition="2024"\npublish=false\n');
  for (const module of plan.modules) fs.writeFileSync(path.join(root, `src/domain/events/${rustSelectorModule(module.selector)}.rs`), plan.artifacts.find(row => row.relative_path === module.relative_path)!.content);
  const modules = plan.modules.map(module => `pub mod ${rustSelectorModule(module.selector)};`).join('');
  fs.writeFileSync(path.join(root, 'src/main.rs'), `mod domain{pub mod events{${modules}}}\nfn main(){${main}}\n`);
}

test('Rust Event planner preserves occurrence, time and reference identities deterministically', t => {
  const f = fixture(t), repeat = planConfiguredRustEvents(f.graph, f.boundary, f.selection, f.contract), posted = f.plan.modules.find(row => row.selector === 'alpha:posted')!, generated = f.plan.modules.find(row => row.selector === 'alpha:generated')!;
  assert.deepEqual(repeat, f.plan); assert.equal(f.plan.contract_sha256, RUST_EVENT_CONTRACT_SHA256); assert.equal(f.plan.protocol_id, RUST_EVENT_PROTOCOL); assert.equal(posted.occurred_at_policy, 'required'); assert.equal(generated.occurred_at_policy, 'generated'); assert.deepEqual(generated.references, ['alpha:order']);
  const output = f.plan.artifacts.find(row => row.relative_path === generated.relative_path)!.content; assert.match(output, /EventRefF5AlphaN5Order/); assert.doesNotMatch(output, /publish|persist|registry/i);
});

test('generated Rust Events construct owned data and call an explicit clock once after validation', t => {
  const f = fixture(t), root = path.join(f.temp, 'event-crate'), posted = rustSelectorModule('alpha:posted'), generated = rustSelectorModule('alpha:generated');
  crate(root, f.plan, `use domain::events::${posted} as p;let event=p::create_posted(p::PostedInput{occurrence:p::PostedOccurrenceInput{event_id:"event-1".to_owned()},occurred_at:"2026-09-15T00:00:00Z".to_owned(),payload:p::PostedPayloadInput{}}).unwrap();assert_eq!(event.event_type(),"posted");assert_eq!(event.occurrence().event_id(),"event-1");use domain::events::${generated} as g;let count=std::cell::Cell::new(0);let clock=||{count.set(count.get()+1);"2026-09-15T01:00:00Z".to_owned()};let input=g::GeneratedInput{occurrence:g::GeneratedOccurrenceInput{event_id:"event-2".to_owned()},payload:g::GeneratedPayloadInput{active:true,count:-2,note:None,order_ref:g::EventRefF5AlphaN5Order::new("order-1".to_owned()).unwrap(),ratio:-0.0,source_at:None}};let value=g::create_generated(input,&clock).unwrap();assert_eq!(count.get(),1);assert_eq!(value.payload().ratio().to_bits(),0.0f64.to_bits());assert_eq!(value.payload().order_ref().as_str(),"order-1");let bad=g::GeneratedInput{occurrence:g::GeneratedOccurrenceInput{event_id:"event-3".to_owned()},payload:g::GeneratedPayloadInput{active:true,count:0,note:None,order_ref:g::EventRefF5AlphaN5Order::new("order-2".to_owned()).unwrap(),ratio:f64::NAN,source_at:None}};assert_eq!(g::create_generated(bad,&clock).unwrap_err().code(),"DOMAINSPEC_EVENT_DECIMAL");assert_eq!(count.get(),1);`);
  execFileSync(cargo, ['run', '--quiet', '--offline'], {cwd: root, stdio: 'pipe'});
});

test('generated Rust Event values cannot bypass construction through private fields', t => {
  const f = fixture(t), root = path.join(f.temp, 'event-compile-fail'), posted = rustSelectorModule('alpha:posted');
  crate(root, f.plan, `let _=domain::events::${posted}::PostedEvent{occurrence:todo!(),occurred_at:String::new(),payload:todo!()};`);
  const bad = spawnSync(cargo, ['check', '--quiet', '--offline'], {cwd: root, encoding: 'utf8'}); assert.notEqual(bad.status, 0); assert.match(bad.stderr, /private field/);
});

test('Rust Event planner rejects drift, active data, stale inputs and wrong roots before effects', t => {
  const f = fixture(t); let reads = 0; const active = {...f.selection}; Object.defineProperty(active, 'roots', {enumerable: true, get() {reads++; return f.selection.roots;}});
  for (const selection of [active, {...f.selection, language: 'python'}, {...f.selection, roots: ['alpha:posted', 'alpha:posted']}, {...f.selection, roots: ['alpha:order']}, {...f.selection, module_root: '../escape'}, {...f.selection, boundary_sha256: '0'.repeat(64)}]) assert.throws(() => planConfiguredRustEvents(f.graph, f.boundary, selection as any, f.contract));
  assert.equal(reads, 0); assert.throws(() => planConfiguredRustEvents(f.graph, f.boundary, f.selection, f.contract + '\n'));
});
