import type {ExactCalculationContract, ExactNumericExpression} from '../typed-backend/calculation-exact.js';
import type {TypedCalculationContract, NumericExpression} from '../typed-backend/contracts.js';
import {pythonStringLiteral as q} from './configured-python-enums.js';

export type PythonCalculationContract = ExactCalculationContract | TypedCalculationContract;

/** Small shared arithmetic perimeter, not an expression interpreter. */
export function renderPythonCalculationSupport(): string {
  return `def _normalize(value: object) -> int:
    if type(value) is int:
        result = value
    elif type(value) is str and 1 <= len(value) <= 20 and all("0" <= c <= "9" for c in value) and (value == "0" or value[0] != "0"):
        result = int(value)
    else:
        raise TypeError("CALCULATION_INPUT")
    if result < 0 or result > 18446744073709551615:
        raise TypeError("CALCULATION_INPUT")
    return result


def _inputs(value: object, names: tuple[str, ...]) -> dict[str, object]:
    if type(value) is not dict or len(value) != len(names):
        raise TypeError("CALCULATION_INPUT")
    if any(type(key) is not str for key in value):
        raise TypeError("CALCULATION_INPUT")
    if any(key not in names for key in value):
        raise TypeError("CALCULATION_INPUT")
    return value


def _checked(value: int) -> int:
    if value < 0:
        raise ValueError("CALCULATION_UNDERFLOW")
    if value > 18446744073709551615:
        raise ValueError("CALCULATION_OVERFLOW")
    return value


def _divide(left: int, right: int, rounding: str) -> int:
    if right == 0:
        raise ValueError("CALCULATION_DIVIDE_BY_ZERO")
    quotient, remainder = divmod(left, right)
    if remainder != 0 and rounding == "reject":
        raise ValueError("CALCULATION_INEXACT")
    return _checked(quotient + (1 if rounding == "ceil" and remainder != 0 else 0))
`;
}

export function renderPythonCalculationProvider(contract: PythonCalculationContract, runtimeImport: string): string {
  const names = contract.inputs.map(p => p.name), lines: string[] = [];
  const expression = (e: ExactNumericExpression | NumericExpression): string => {
    if (e.op === 'input') return `p${names.indexOf(e.name)}`;
    if (e.op === 'literal') return String(e.value);
    const left = expression(e.left), right = expression(e.right), name = `v${lines.length}`;
    const source = e.op === 'divide' ? `_divide(${left}, ${right}, ${q(contract.division_rounding)})` :
      `_checked(${left} ${e.op === 'add' ? '+' : e.op === 'subtract' ? '-' : '*'} ${right})`;
    lines.push(`    ${name} = ${source}\n`); return name;
  };
  const result = expression(contract.expression);
  return `from __future__ import annotations\nfrom typing import TypedDict as _TypedDict\nfrom ${runtimeImport} import _normalize, _inputs, _checked, _divide\n\n` +
    `_Inputs = _TypedDict("_Inputs", {${names.map(n => `${q(n)}: int | str`).join(', ')}})\n\n` +
    `def calculate(input: _Inputs) -> int:\n    d = _inputs(input, (${names.map(n => q(n) + ',').join(' ')}))\n` +
    names.map((n, i) => `    p${i} = _normalize(d[${q(n)}])\n`).join('') + lines.join('') + `    return ${result}\n`;
}

/** Nested descriptor collections are immutable; no external mutable backing. */
export function pythonFrozenLiteral(value: unknown): string {
  if (value === null) return 'None';
  if (typeof value === 'boolean') return value ? 'True' : 'False';
  if (typeof value === 'string') return q(value);
  if (typeof value === 'number') return String(value);
  if (Array.isArray(value)) return '(' + value.map(v => pythonFrozenLiteral(v) + ',').join(' ') + ')';
  if (value && typeof value === 'object') return '_MappingProxyType({' + Object.entries(value).map(([k, v]) => q(k) + ': ' + pythonFrozenLiteral(v)).join(', ') + '})';
  throw new TypeError('DS_PYTHON_CALCULATION:invalid descriptor literal');
}

export function renderPythonCalculationBinding(providerImport: string, callable: string, descriptor: unknown): string {
  return `from __future__ import annotations
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from ${providerImport} import calculate as _calculate, _Inputs

_DESCRIPTOR = ${pythonFrozenLiteral(descriptor)}

@_dataclass(frozen=True, slots=True)
class _BoundCalculation:
    @property
    def descriptor(self):
        return _DESCRIPTOR

    def __call__(self, input: _Inputs) -> int:
        return _calculate(input)

${callable} = _BoundCalculation()
__all__ = [${q(callable)}]
`;
}
