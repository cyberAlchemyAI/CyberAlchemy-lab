import {createCompiledProjectCertificate} from '../compilation/certificate.js';
import {assertCompiledCompositionBoundary, type CompiledCompositionBoundary} from '../input/composition-boundary.js';
import {assertCompiledProjectFields, EXACT_PROJECT_FIELD_SELECTION_VERSION, type CompiledProjectFields} from '../input/compiled-field-model.js';
import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import {assertCheckedOperationAction, type CheckedOperationAction, type OperationActionBindings} from '../typed-operation/action-bindings.js';
import {decodeTypedRuleContract, type TypedType, type ValueExpression} from '../typed-operation/contracts.js';
import type {FactoryBinding} from './configured-factories.js';
import {planConfiguredRustEvents, RUST_EVENT_CONTRACT_SHA256, RUST_EVENT_SELECTION_VERSION} from './configured-rust-events.js';
import {planConfiguredRustFactories, RUST_FACTORY_CONTRACT_SHA256, RUST_FACTORY_SELECTION_VERSION} from './configured-rust-factories.js';
import {planConfiguredRustRules, RUST_RULE_CONTRACT_SHA256, RUST_RULE_SELECTION_VERSION} from './configured-rust-rules.js';
import {rustPascal, rustSelectorModule, rustSelectorType, rustSnake, rustString} from './configured-rust-values.js';
import type {PlannedArtifact} from './contracts.js';

export const RUST_OPERATION_SELECTION_VERSION = 'domainspec.configured-rust-operations-selection/v1-candidate';
export const RUST_OPERATION_PROTOCOL = 'rust.bound-operation/v1-candidate';
export const RUST_OPERATION_CONTRACT_SHA256 = 'cacd45695c4ddf104eece3d49198a7b6c98d6ea19d5393e3841255281b57f56c';
export interface RustOperationSelection {readonly schema_version: typeof RUST_OPERATION_SELECTION_VERSION; readonly language: 'rust'; readonly module_root: string; readonly boundary_sha256: string; readonly field_compilation_sha256: string; readonly actions: readonly CheckedOperationAction[]; readonly factories: readonly FactoryBinding[];}
export interface RustOperationSources {readonly rust_contract: string; readonly rule_contract: string; readonly factory_contract: string; readonly event_contract: string;}
type ScopeValue = {type: TypedType; reference: string; owned: string};
type RustAction = Readonly<{bindings: OperationActionBindings; certificate: Readonly<{graph_sha256: string}>; boundary_sha256: string; field_compilation_sha256: string | null; action_sha256: string;
  reads: readonly (OperationActionBindings['reads'][number] & Readonly<{identity: Readonly<{name: string; type: TypedType}>}>)[];
  guards: OperationActionBindings['guards']; writes: OperationActionBindings['writes'];
  events: readonly (OperationActionBindings['events'][number] & Readonly<{contract: Readonly<{occurred_at_policy: 'required' | 'generated'}>}>)[]}>;
function fail(reason: string): never {throw new TypeError('DS_RUST_OPERATION:' + reason);}
function artifact(relative_path: string, content: string): PlannedArtifact {return {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)};}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}
function rustType(type: TypedType): string {
  if (type.kind === 'scalar') return type.name === 'String' ? 'String' : type.name === 'Bool' ? 'bool' : 'u64';
  if (type.kind === 'named') return rustSelectorType(type.selector);
  if (type.kind === 'optional') return `Option<${rustType(type.element)}>`;
  if (type.kind === 'list') return `Vec<${rustType(type.element)}>`;
  if (type.kind === 'set') return `std::collections::BTreeSet<${rustType(type.element)}>`;
  return fail('anonymous sum Operation inputs require a named declaration');
}
/** Operation slots are semantic identities. Existing portable local slots keep
 * their native spelling; an exact qualified selector receives the same
 * collision-resistant module encoding used elsewhere in the Rust backend. */
function rustSlot(value: string): string {
  try { return rustSnake(value); }
  catch {
    if (value.split(':').length === 2) return rustSelectorModule(value);
    return fail('portable local or qualified slot required:' + value);
  }
}
export function rustOperationPath(moduleRoot: string, selector: string): string {return `${moduleRoot}/src/application/operations/${rustSelectorModule(selector)}.rs`;}

export function planConfiguredRustOperations(graph: CompiledProjectGraph, boundary: CompiledCompositionBoundary, fields: CompiledProjectFields, selection: RustOperationSelection, sources: RustOperationSources) {
  assertCompiledProjectSnapshot(graph); assertCompiledCompositionBoundary(boundary); assertCompiledProjectFields(fields); assertInterfaceData(selection); assertInterfaceData(sources);
  if (Object.keys(sources).sort().join('|') !== 'event_contract|factory_contract|rule_contract|rust_contract' || sha256(sources.rust_contract) !== RUST_OPERATION_CONTRACT_SHA256 || sha256(sources.rule_contract) !== RUST_RULE_CONTRACT_SHA256 || sha256(sources.factory_contract) !== RUST_FACTORY_CONTRACT_SHA256 || sha256(sources.event_contract) !== RUST_EVENT_CONTRACT_SHA256) fail('contract drift');
  const certificate = createCompiledProjectCertificate(graph);
  if (selection.schema_version !== RUST_OPERATION_SELECTION_VERSION || selection.language !== 'rust' || selection.boundary_sha256 !== boundary.boundary_sha256 || selection.field_compilation_sha256 !== fields.compilation_sha256 || boundary.certificate.graph_sha256 !== certificate.graph_sha256 || fields.certificate.graph_sha256 !== certificate.graph_sha256 || fields.selection.schema_version !== EXACT_PROJECT_FIELD_SELECTION_VERSION) fail('unsupported or stale selection');
  if (selection.module_root.split('/').some(part => {try {rustSnake(part); return false;} catch {return true;}})) fail('portable module root required');
  if (!Array.isArray(selection.actions) || !selection.actions.length || selection.actions.length > 256) fail('bounded actions required');
  for (const action of selection.actions) assertCheckedOperationAction(action);
  const selectedActions = selection.actions as unknown as readonly RustAction[];
  if (new Set(selectedActions.map(action => action.bindings.selector)).size !== selectedActions.length) fail('unique actions required');
  for (const action of selectedActions) if (action.certificate.graph_sha256 !== certificate.graph_sha256 || action.boundary_sha256 !== boundary.boundary_sha256 || action.field_compilation_sha256 !== fields.compilation_sha256) fail('stale action');
  const factoryRules = selection.factories.flatMap(binding => [...binding.base_validators, ...binding.extensions.flatMap(extension => extension.validators)]).map(validator => validator.rule);
  const ruleRoots = [...new Set([...selectedActions.flatMap(action => action.guards.map(guard => guard.selector)), ...factoryRules])].sort();
  const rules = planConfiguredRustRules(graph, fields, {schema_version: RUST_RULE_SELECTION_VERSION, language: 'rust', module_root: selection.module_root, roots: ruleRoots, field_compilation_sha256: fields.compilation_sha256}, sources.rule_contract);
  const factories = planConfiguredRustFactories(graph, fields, rules, {schema_version: RUST_FACTORY_SELECTION_VERSION, language: 'rust', module_root: selection.module_root, field_compilation_sha256: fields.compilation_sha256, factories: selection.factories}, sources.factory_contract);
  const eventRoots = [...new Set(selectedActions.flatMap(action => action.events.map(event => event.target)))].sort();
  const events = eventRoots.length ? planConfiguredRustEvents(graph, boundary, {schema_version: RUST_EVENT_SELECTION_VERSION, language: 'rust', module_root: selection.module_root, roots: eventRoots, boundary_sha256: boundary.boundary_sha256}, sources.event_contract) : null;
  const declarations = new Map(fields.model.declarations.map(row => [row.selector, row])), properties = new Map([...declarations.values()].flatMap(row => row.kind === 'Enum' ? [] : row.contract.properties.map(property => [property.ontology_property, {owner: row.selector, property}] as const)));
  const ruleContracts = new Map(graph.nodes.filter(node => node.kind === 'Rule').map(node => [node.selector, decodeTypedRuleContract(node.body.typed_contract)]));
  const eventModules = new Map(events?.modules.map(module => [module.selector, module]) ?? []), factoryModules = new Map(factories.modules.map(module => [module.selector, module]));
  const modules = [...selectedActions].sort((left, right) => left.bindings.selector < right.bindings.selector ? -1 : 1).map(action => {
    const selector = action.bindings.selector, name = rustPascal(selector.split(':')[1]!), symbol = rustSnake(selector.split(':')[1]!), transaction = `${name}Transaction`, store = `${name}Store`, batch = `${name}Batch`, outcome = `${name}Outcome`, request = `${name}Request`, requestSymbol = `${symbol}_request`;
    const scope = new Map<string, ScopeValue>(action.bindings.inputs.map(input => [input.name, {type: input.type, reference: rustSnake(input.name), owned: `Clone::clone(${rustSnake(input.name)})`} ]));
    for (const read of action.reads) scope.set(read.parameter, {type: {kind: 'named', selector: read.target}, reference: `&${rustSnake(read.parameter)}`, owned: `${rustSnake(read.parameter)}.clone()`});
    const expression = (value: ValueExpression, activeScope: ReadonlyMap<string, ScopeValue>): ScopeValue => {
      if (value.op === 'literal') {
        const type: TypedType = {kind: 'scalar', name: value.type};
        if (value.type === 'String') {const owned = `String::from(${rustString(String(value.value))})`; return {type, owned, reference: `&${owned}`};}
        if (value.type === 'Bool') {const owned = value.value ? 'true' : 'false'; return {type, owned, reference: `&${owned}`};}
        const integer = BigInt(value.value); if (integer < 0n || integer > 18446744073709551615n) return fail('UInt64 literal out of range'); const owned = `${integer}u64`; return {type, owned, reference: `&${owned}`};
      }
      if (value.op === 'variant') {
        const owner = [...declarations.values()].find(row => row.kind === 'Enum' && row.contract.variants.some(variant => variant.ontology_variant === value.selector)); if (!owner || owner.kind !== 'Enum') return fail('unknown Enum variant');
        const variant = owner.contract.variants.find(row => row.ontology_variant === value.selector)!; if (variant.payload !== null) return fail('payload variant expression unsupported'); const owned = `${rustSelectorType(owner.selector)}::${rustPascal(variant.name)}`;
        return {type: {kind: 'named', selector: owner.selector}, owned, reference: `&${owned}`};
      }
      if (value.op === 'to_set') {const inner = expression(value.value, activeScope); if (inner.type.kind !== 'list') return fail('to_set requires list'); const owned = `${inner.reference}.iter().cloned().collect::<std::collections::BTreeSet<_>>()`; return {type: {kind: 'set', element: inner.type.element}, owned, reference: `&(${owned})`};}
      let current = activeScope.get(value.root) ?? fail('unknown Operation value root:' + value.root), type = current.type, reference = current.reference;
      for (const ontology of value.properties) {const found = properties.get(ontology); if (!found || type.kind !== 'named' || type.selector !== found.owner) return fail('property owner mismatch:' + ontology); reference += `.${rustSnake(found.property.name)}()`; type = found.property.type;}
      return {type, reference, owned: `Clone::clone(${reference})`};
    };
    const rollback = (status: 'Rejected' | 'Failed', stage: string, code: string) => `{ let cleanup_failed = transaction.rollback().await.is_err(); return ${outcome}::${status} { stage: ${rustString(stage)}, code: ${rustString(code)}, cleanup_failed }; }`;
    const reads = action.reads.map((read, index) => {
      const key = expression(read.key, new Map(action.bindings.inputs.map(input => [input.name, scope.get(input.name)!]))), variable = rustSnake(read.parameter), method = `read_${rustSlot(read.slot)}`;
      return `    let key${index}: ${rustType(read.identity.type)} = ${key.owned};\n    let ${variable} = match transaction.${method}(&key${index}).await {\n        Ok(Some(value)) => value,\n        Ok(None) => ${rollback('Failed', 'read', 'READ_NOT_FOUND')},\n        Err(_) => ${rollback('Failed', 'read', 'READ_FAILED')},\n    };\n    if ${variable}.${rustSnake(read.identity.name)}() != &key${index} ${rollback('Failed', 'read', 'READ_IDENTITY_MISMATCH')}\n`;
    }).join('');
    const guards = action.guards.map(guard => {
      const contract = ruleContracts.get(guard.selector) ?? fail('missing guard Rule'), supplied = new Map(guard.arguments.map(argument => [argument.parameter, argument.value]));
      const args = contract.parameters.map(parameter => expression(supplied.get(parameter.name) ?? fail('missing guard argument'), scope).reference).join(', ');
      return `    if !crate::domain::rules::${rustSelectorModule(guard.selector)}::${rustSnake(guard.selector.split(':')[1]!)}(${args}) ${rollback('Rejected', 'guard', 'RULE_REJECTED:' + guard.selector)}\n`;
    }).join('');
    const validate = (type: TypedType, variable: string, stage: string): string => {
      if (type.kind !== 'named') return '';
      const declaration = declarations.get(type.selector); if (!declaration || declaration.kind === 'Enum') return '';
      const module = factoryModules.get(type.selector) ?? fail('missing factory:' + type.selector);
      return `    if crate::domain::types::${rustSelectorModule(type.selector)}::${module.callable}().validate(&${variable}).is_err() ${rollback('Failed', stage, 'OWNED_VALUE_INVALID:' + type.selector)}\n`;
    };
    const writes = action.writes.map((write, index) => {const variable = `write${index}`, type: TypedType = {kind: 'named', selector: write.target}; return `    let ${variable}: ${rustType(type)} = ${expression(write.value, scope).owned};\n${validate(type, variable, 'write-validation')}`;}).join('');
    const eventValues = action.events.map((event, index) => {
      const module = eventModules.get(event.target) ?? fail('missing Event:' + event.target), clock = module.occurred_at_policy === 'generated' ? `, clock_${rustSnake(event.slot)}` : '';
      return `    let event${index} = match crate::domain::events::${rustSelectorModule(event.target)}::${module.symbol}(${rustSnake(event.parameter)}${clock}) { Ok(value) => value, Err(_) => ${rollback('Failed', 'event', 'EVENT_INPUT:' + event.target)} };\n`;
    }).join('');
    const resultValue = expression(action.bindings.result.value, scope), resultType = action.bindings.result.type;
    const result = `    let result: ${rustType(resultType)} = ${resultValue.owned};\n${validate(resultType, 'result', 'result')} `;
    const writeFields = action.writes.map((write, index) => `    pub ${rustSlot(write.slot)}: WriteIntent<${rustSelectorType(write.target)}>,`).join('\n');
    const eventFields = action.events.map(event => {const module = eventModules.get(event.target)!; return `    pub ${rustSlot(event.slot)}: EventIntent<crate::domain::events::${rustSelectorModule(event.target)}::${module.value}>,`;}).join('\n');
    const batchValues = [...action.writes.map((write, index) => `        ${rustSlot(write.slot)}: WriteIntent { target: ${rustString(write.target)}, mode: WriteMode::${rustPascal(write.mode)}, value: write${index} },`), ...action.events.map((event, index) => `        ${rustSlot(event.slot)}: EventIntent { target: ${rustString(event.target)}, value: event${index} },`)].join('\n');
    const readMethods = action.reads.map(read => `    async fn read_${rustSlot(read.slot)}(&mut self, key: &${rustType(read.identity.type)}) -> Result<Option<${rustSelectorType(read.target)}>, OperationPortError>;`).join('\n');
    const functionInputs = action.bindings.inputs.map(input => `${rustSnake(input.name)}: &${rustType(input.type)}`), eventInputs = action.events.map(event => {const module = eventModules.get(event.target)!; return `${rustSnake(event.parameter)}: crate::domain::events::${rustSelectorModule(event.target)}::${module.input}`;}), clocks = action.events.filter(event => eventModules.get(event.target)!.occurred_at_policy === 'generated').map(event => `clock_${rustSlot(event.slot)}: &impl Fn() -> String`);
    const requestFields = [...action.bindings.inputs.map(input => `    pub ${rustSnake(input.name)}: ${rustType(input.type)},`), ...action.events.map(event => {const module = eventModules.get(event.target)!; return `    pub ${rustSnake(event.parameter)}: crate::domain::events::${rustSelectorModule(event.target)}::${module.input},`;})];
    const requestNames = [...action.bindings.inputs.map(input => rustSnake(input.name)), ...action.events.map(event => rustSnake(event.parameter))];
    const requestArguments = [...action.bindings.inputs.map(input => `&${rustSnake(input.name)}`), ...action.events.map(event => rustSnake(event.parameter)), ...clocks.map(clock => clock.split(':')[0]!.trim()), 'store'];
    const content = `// Generated DomainSpec Rust Operation.\npub const DOMAINSPEC_SELECTOR: &str = ${rustString(selector)};\npub const DOMAINSPEC_ACTION_SHA256: &str = ${rustString(action.action_sha256)};\npub const DOMAINSPEC_PROTOCOL_ID: &str = ${rustString(RUST_OPERATION_PROTOCOL)};\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq)]\npub struct OperationPortError;\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq)]\npub enum CommitReceipt { Committed, Rejected, Indeterminate }\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq)]\npub enum WriteMode { Create, Replace, Delete }\n\n#[derive(Clone, Debug)]\npub struct WriteIntent<T> { pub target: &'static str, pub mode: WriteMode, pub value: T }\n\n#[derive(Clone, Debug)]\npub struct EventIntent<T> { pub target: &'static str, pub value: T }\n\n#[derive(Clone, Debug)]\npub struct ${request} {\n${requestFields.join('\n')}\n}\n\n#[derive(Clone, Debug)]\npub struct ${batch} {\n${writeFields}${writeFields && eventFields ? '\n' : ''}${eventFields}\n}\n\n#[derive(Clone, Debug)]\npub enum ${outcome} {\n    Committed(${rustType(resultType)}),\n    Rejected { stage: &'static str, code: &'static str, cleanup_failed: bool },\n    Failed { stage: &'static str, code: &'static str, cleanup_failed: bool },\n    Indeterminate { stage: &'static str, code: &'static str },\n}\n\n#[allow(async_fn_in_trait)]\npub trait ${transaction} {\n${readMethods}${readMethods ? '\n' : ''}    async fn rollback(&mut self) -> Result<(), OperationPortError>;\n    async fn commit(&mut self, batch: ${batch}) -> Result<CommitReceipt, OperationPortError>;\n}\n\n#[allow(async_fn_in_trait)]\npub trait ${store} {\n    type Transaction: ${transaction};\n    async fn begin(&self) -> Result<Self::Transaction, OperationPortError>;\n}\n\npub async fn ${requestSymbol}<S: ${store}>(request: ${request}${clocks.length ? `, ${clocks.join(', ')}` : ''}, store: &S) -> ${outcome} {\n    let ${request} { ${requestNames.join(', ')} } = request;\n    ${symbol}(${requestArguments.join(', ')}).await\n}\n\npub async fn ${symbol}<S: ${store}>(${[...functionInputs, ...eventInputs, ...clocks, 'store: &S'].join(', ')}) -> ${outcome} {\n    let mut transaction = match store.begin().await { Ok(value) => value, Err(_) => return ${outcome}::Failed { stage: \"begin\", code: \"BEGIN_FAILED\", cleanup_failed: false } };\n${reads}${guards}${writes}${eventValues}${result}    let batch = ${batch} {\n${batchValues}\n    };\n    match transaction.commit(batch).await {\n        Ok(CommitReceipt::Committed) => ${outcome}::Committed(result),\n        Ok(CommitReceipt::Rejected) => ${outcome}::Rejected { stage: \"commit\", code: \"COMMIT_REJECTED\", cleanup_failed: false },\n        Ok(CommitReceipt::Indeterminate) => ${outcome}::Indeterminate { stage: \"commit\", code: \"COMMIT_INDETERMINATE\" },\n        Err(_) => ${outcome}::Indeterminate { stage: \"commit\", code: \"COMMIT_UNCERTAIN\" },\n    }\n}\n`;
    const relative_path = rustOperationPath(selection.module_root, selector);
    return {selector, symbol, request, request_symbol: requestSymbol, transaction, store, batch, outcome, relative_path, action_sha256: action.action_sha256, rule_dependencies: action.guards.map(guard => guard.selector), factory_dependencies: [...new Set([...action.writes.map(write => write.target), ...(resultType.kind === 'named' ? [resultType.selector] : [])])].sort(), event_dependencies: action.events.map(event => event.target), artifact: artifact(relative_path, content)};
  });
  const files = new Map<string, PlannedArtifact>();
  for (const row of [...rules.artifacts, ...factories.artifacts, ...(events?.artifacts ?? []), ...modules.map(module => module.artifact)]) {const existing = files.get(row.relative_path); if (existing && existing.content !== row.content) fail('artifact collision:' + row.relative_path); files.set(row.relative_path, row);}
  const body = {schema_version: 'domainspec.configured-rust-operations-plan/v1-candidate' as const, selection: {...selection, actions: selection.actions.map(action => action.action_sha256), factories: structuredClone(selection.factories)}, certificate, boundary_sha256: boundary.boundary_sha256, field_compilation_sha256: fields.compilation_sha256, contract_sha256: RUST_OPERATION_CONTRACT_SHA256, protocol_id: RUST_OPERATION_PROTOCOL, rule_plan_sha256: rules.plan_sha256, factory_plan_sha256: factories.plan_sha256, event_plan_sha256: events?.plan_sha256 ?? null, modules: modules.map(({artifact: _artifact, ...module}) => module), artifacts: [...files.values()].sort((left, right) => left.relative_path < right.relative_path ? -1 : 1), authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
