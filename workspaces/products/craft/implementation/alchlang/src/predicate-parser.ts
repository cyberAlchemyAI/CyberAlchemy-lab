import { CompilationRejected, type CompilerIssue, type ScalarType, type SfolFormula } from "./model.js";

type Token = { kind: "word" | "number" | "string" | "operator" | "punctuation"; value: string; offset: number };

function tokenize(source: string): Token[] {
  const tokens: Token[] = [];
  let offset = 0;
  while (offset < source.length) {
    const rest = source.slice(offset);
    const whitespace = /^\s+/.exec(rest);
    if (whitespace) { offset += whitespace[0].length; continue; }
    const string = /^("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/.exec(rest);
    if (string) { tokens.push({ kind: "string", value: string[0], offset }); offset += string[0].length; continue; }
    const operator = /^(<=|>=|==|!=|<|>)/.exec(rest);
    if (operator) { tokens.push({ kind: "operator", value: operator[0], offset }); offset += operator[0].length; continue; }
    const number = /^-?(?:\d+\.\d+|\d+)/.exec(rest);
    if (number) { tokens.push({ kind: "number", value: number[0], offset }); offset += number[0].length; continue; }
    const punctuation = /^[(),]/.exec(rest);
    if (punctuation) { tokens.push({ kind: "punctuation", value: punctuation[0], offset }); offset += 1; continue; }
    const word = /^[A-Za-z_][A-Za-z0-9_.-]*/.exec(rest);
    if (word) { tokens.push({ kind: "word", value: word[0], offset }); offset += word[0].length; continue; }
    throw new CompilationRejected([{ code: "PREDICATE_SYNTAX", path: `$@${offset}`, message: `unexpected token ${JSON.stringify(source[offset])}` }]);
  }
  return tokens;
}

const operatorNames: Record<string, string> = { "==": "eq", "!=": "neq", "<": "lt", "<=": "lte", ">": "gt", ">=": "gte" };

export function parseSfolFormula(source: string, facts: ReadonlyMap<string, ScalarType>): SfolFormula {
  const tokens = tokenize(source.trim().replace(/\.$/, ""));
  let cursor = 0;
  const issues: CompilerIssue[] = [];
  const peek = () => tokens[cursor];
  const take = () => tokens[cursor++];
  const matchWord = (word: string): boolean => peek()?.kind === "word" && peek().value.toLowerCase() === word && Boolean(take());

  function resolveFact(raw: string, token: Token): { node: "fact_ref"; ref: string } {
    const direct = facts.has(raw) ? raw : raw.includes(".") && facts.has(raw.slice(raw.lastIndexOf(".") + 1)) ? raw.slice(raw.lastIndexOf(".") + 1) : null;
    if (!direct) issues.push({ code: "UNRESOLVED_REFERENCE", path: `$@${token.offset}`, message: `${raw} is not a declared fact` });
    return { node: "fact_ref", ref: direct ?? raw };
  }

  function primary(expectFact = false): SfolFormula {
    const token = take();
    if (!token) { issues.push({ code: "PREDICATE_SYNTAX", path: "$", message: "missing operand" }); return { node: "literal", value_type: "boolean", value: false }; }
    if (token.value === "(") { const expression = disjunction(); if (take()?.value !== ")") issues.push({ code: "PREDICATE_SYNTAX", path: `$@${token.offset}`, message: "missing closing parenthesis" }); return expression; }
    if (token.kind === "string") return { node: "literal", value_type: "string", value: JSON.parse(token.value[0] === "'" ? `"${token.value.slice(1, -1).replace(/"/g, '\\"')}"` : token.value) };
    if (token.kind === "number") return { node: "literal", value_type: token.value.includes(".") ? "decimal" : "integer", value: Number(token.value) };
    if (token.kind === "word" && ["true", "false"].includes(token.value.toLowerCase())) return { node: "literal", value_type: "boolean", value: token.value.toLowerCase() === "true" };
    if (token.kind === "word" && expectFact) return resolveFact(token.value, token);
    if (token.kind === "word" && facts.has(token.value)) return resolveFact(token.value, token);
    if (token.kind === "word") return { node: "literal", value_type: "string", value: token.value };
    issues.push({ code: "PREDICATE_SYNTAX", path: `$@${token.offset}`, message: `unexpected operand ${token.value}` });
    return { node: "literal", value_type: "boolean", value: false };
  }

  function unary(): SfolFormula {
    if (matchWord("not")) return { operator: "not", operands: [unary()] };
    for (const operator of ["exists", "absent"] as const) {
      if (matchWord(operator)) {
        const opened = peek()?.value === "(" && Boolean(take());
        const operand = primary(true);
        if (opened && take()?.value !== ")") issues.push({ code: "PREDICATE_SYNTAX", path: "$", message: `missing ) after ${operator}` });
        return { operator, operands: [operand] };
      }
    }
    return primary(true);
  }

  function comparison(): SfolFormula {
    const left = unary();
    const token = peek();
    const keyword = token?.kind === "word" ? token.value.toLowerCase() : "";
    const operator = token?.kind === "operator" ? operatorNames[token.value] : ["in", "contains"].includes(keyword) ? keyword : null;
    if (!operator) return left;
    take();
    return { operator, operands: [left, primary(false)] };
  }

  function conjunction(): SfolFormula {
    let expression = comparison();
    while (matchWord("and")) expression = { operator: "and", operands: [expression, comparison()] };
    return expression;
  }

  function disjunction(): SfolFormula {
    let expression = conjunction();
    while (matchWord("or")) expression = { operator: "or", operands: [expression, conjunction()] };
    return expression;
  }

  const expression = disjunction();
  if (cursor !== tokens.length) issues.push({ code: "PREDICATE_SYNTAX", path: `$@${peek().offset}`, message: `unexpected trailing token ${peek().value}` });
  if (issues.length) throw new CompilationRejected(issues);
  return expression;
}

/** @deprecated Use parseSfolFormula. */
export const parsePredicate = parseSfolFormula;

export type LegacyPredicateRegistry = Readonly<Record<string, SfolFormula>>;

export function translateLegacyPredicate(predicateId: string, registry: LegacyPredicateRegistry): SfolFormula {
  const expression = registry[predicateId];
  if (!expression) throw new CompilationRejected([{ code: "LEGACY_PREDICATE_UNBOUND", path: `$.rules.${predicateId}`, message: "legacy predicate requires an explicit executable AST registry entry" }]);
  return expression;
}
