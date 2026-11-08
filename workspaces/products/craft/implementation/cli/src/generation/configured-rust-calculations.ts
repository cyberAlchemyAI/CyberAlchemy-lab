import {assertCompiledProjectSnapshot, type CompiledProjectGraph} from '../input/project-model.js';
import {canonicalJson, sha256} from '../input/source-manifest.js';
import {decodeExactCalculation, EXACT_CALCULATION_VERSION, type ExactCalculationContract, type ExactNumericExpression} from '../typed-backend/calculation-exact.js';
import {decodeTypedCalculationContract, type NumericExpression, type TypedCalculationContract} from '../typed-backend/contracts.js';
import {assertInterfaceData} from '../typed-backend/interface.js';
import type {PlannedArtifact} from './contracts.js';
import {rustSelectorModule, rustSnake, rustString} from './configured-rust-values.js';

export const RUST_CALCULATION_SELECTION_VERSION = 'domainspec.configured-rust-calculations-selection/v1-candidate';
export const RUST_CALCULATION_PROTOCOL = 'rust.bound-calculation/v1-candidate';
export const RUST_CALCULATION_CONTRACT_SHA256 = '8656ca4bd68e03716103e1991dcc71016455e1b5be681a713289c00d094e44fc';

export interface RustCalculationSelection {
  readonly schema_version: typeof RUST_CALCULATION_SELECTION_VERSION;
  readonly language: 'rust';
  readonly module_root: string;
  readonly roots: readonly string[];
}

type CalculationContract = TypedCalculationContract | ExactCalculationContract;
type Expression = NumericExpression | ExactNumericExpression;
function fail(reason: string): never {throw new TypeError('DS_RUST_CALCULATION:' + reason);}
function artifact(relative_path: string, content: string): PlannedArtifact {return {relative_path, content, size_bytes: Buffer.byteLength(content), sha256: sha256(content)};}
function freeze<T>(value: T): T {if (value && typeof value === 'object' && !Object.isFrozen(value)) {Object.values(value).forEach(freeze); Object.freeze(value);} return value;}

function renderExpression(expression: Expression, rounding: CalculationContract['division_rounding'], inputs: ReadonlySet<string>): string {
  if (expression.op === 'literal') {
    const value = typeof expression.value === 'number' ? BigInt(expression.value) : BigInt(expression.value);
    if (value < 0n || value > 18446744073709551615n) return fail('UInt64 literal out of range');
    return `Ok(${value}u64)`;
  }
  if (expression.op === 'input') {
    if (!inputs.has(expression.name)) return fail('undeclared input:' + expression.name);
    return `Ok(*${rustSnake(expression.name)})`;
  }
  const left = renderExpression(expression.left, rounding, inputs), right = renderExpression(expression.right, rounding, inputs);
  const operation = expression.op === 'add'
    ? 'left.checked_add(right).ok_or(CalculationError::Overflow)'
    : expression.op === 'subtract'
      ? 'left.checked_sub(right).ok_or(CalculationError::Underflow)'
      : expression.op === 'multiply'
        ? 'left.checked_mul(right).ok_or(CalculationError::Overflow)'
        : rounding === 'reject'
          ? 'if right == 0 { Err(CalculationError::DivideByZero) } else if left % right != 0 { Err(CalculationError::Inexact) } else { Ok(left / right) }'
          : rounding === 'floor'
            ? 'if right == 0 { Err(CalculationError::DivideByZero) } else { Ok(left / right) }'
            : 'if right == 0 { Err(CalculationError::DivideByZero) } else { let quotient = left / right; if left % right == 0 { Ok(quotient) } else { quotient.checked_add(1).ok_or(CalculationError::Overflow) } }';
  return `{ let left = (${left})?; let right = (${right})?; ${operation} }`;
}

export function rustCalculationPath(moduleRoot: string, selector: string): string {
  return `${moduleRoot}/src/domain/calculations/${rustSelectorModule(selector)}.rs`;
}

/** Source-bound native checked arithmetic. Planning is inert and produces bytes
 * only; Cargo execution belongs to the separate native verification lane. */
export function planConfiguredRustCalculations(graph: CompiledProjectGraph, selection: RustCalculationSelection, contractSource: string) {
  assertCompiledProjectSnapshot(graph); assertInterfaceData(selection); assertInterfaceData(contractSource);
  if (sha256(contractSource) !== RUST_CALCULATION_CONTRACT_SHA256) fail('contract drift');
  if (selection.schema_version !== RUST_CALCULATION_SELECTION_VERSION || selection.language !== 'rust') fail('unsupported selection');
  const rootParts = selection.module_root.split('/'); if (!rootParts.length || rootParts.some(part => {try {rustSnake(part); return false;} catch {return true;}})) fail('portable module root required');
  if (!Array.isArray(selection.roots) || !selection.roots.length || selection.roots.length > 256 || new Set(selection.roots).size !== selection.roots.length) fail('bounded unique roots required');
  const roots = [...selection.roots].sort(), nodes = new Map(graph.nodes.map(node => [node.selector, node]));
  const modules = roots.map(selector => {
    const node = nodes.get(selector); if (node?.kind !== 'Calculation') return fail('selected root is not a Calculation:' + selector);
    const raw = node.body.typed_contract as {schema_version?: string};
    const contract: CalculationContract = raw?.schema_version === EXACT_CALCULATION_VERSION ? decodeExactCalculation(raw) : decodeTypedCalculationContract(raw);
    const symbol = rustSnake(selector.split(':')[1]!), inputs = new Set(contract.inputs.map(input => input.name));
    const parameters = contract.inputs.map(input => `${rustSnake(input.name)}: &u64`).join(', ');
    const expression = renderExpression(contract.expression, contract.division_rounding, inputs);
    const content = `// Generated DomainSpec Rust Calculation.\npub const DOMAINSPEC_SELECTOR: &str = ${rustString(selector)};\npub const DOMAINSPEC_CONTRACT_SHA256: &str = ${rustString(sha256(canonicalJson(contract)))};\npub const DOMAINSPEC_PROTOCOL_ID: &str = ${rustString(RUST_CALCULATION_PROTOCOL)};\n\n#[derive(Copy, Clone, Debug, PartialEq, Eq)]\npub enum CalculationError {\n    Overflow,\n    Underflow,\n    DivideByZero,\n    Inexact,\n}\n\nimpl CalculationError {\n    pub const fn code(self) -> &'static str {\n        match self {\n            Self::Overflow => \"DOMAINSPEC_CALCULATION_OVERFLOW\",\n            Self::Underflow => \"DOMAINSPEC_CALCULATION_UNDERFLOW\",\n            Self::DivideByZero => \"DOMAINSPEC_CALCULATION_DIVIDE_BY_ZERO\",\n            Self::Inexact => \"DOMAINSPEC_CALCULATION_INEXACT\",\n        }\n    }\n}\n\npub fn ${symbol}(${parameters}) -> Result<u64, CalculationError> {\n    ${expression}\n}\n`;
    const relative_path = rustCalculationPath(selection.module_root, selector);
    return {selector, symbol, relative_path, source_schema: contract.schema_version, rounding: contract.division_rounding, inputs: contract.inputs, contract_sha256: sha256(canonicalJson(contract)), artifact: artifact(relative_path, content)};
  });
  const body = {schema_version: 'domainspec.configured-rust-calculations-plan/v1-candidate' as const, selection: {...selection, roots}, contract_sha256: RUST_CALCULATION_CONTRACT_SHA256, protocol_id: RUST_CALCULATION_PROTOCOL, modules: modules.map(({artifact: _artifact, ...module}) => module), artifacts: modules.map(module => module.artifact).sort((a, b) => a.relative_path < b.relative_path ? -1 : 1), authority_effect: 'none' as const};
  return freeze({...body, plan_sha256: sha256(canonicalJson(body))});
}
