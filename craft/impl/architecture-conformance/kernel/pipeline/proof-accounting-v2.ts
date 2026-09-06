import type {
  ProofAccountingDiagnostic,
  ProofAccountingInputV2,
  ProofAccountingV2,
} from "../contracts/proof-accounting-v2.js";

const duplicates = (values: readonly string[]): string[] => {
  const seen = new Set<string>();
  const repeated = new Set<string>();
  for (const value of values) {
    if (seen.has(value)) repeated.add(value);
    seen.add(value);
  }
  return [...repeated].sort();
};

const countBy = <T>(values: readonly T[], predicate: (value: T) => boolean): number =>
  values.filter(predicate).length;

export const evaluateProofAccountingV2 = (
  input: ProofAccountingInputV2,
): ProofAccountingV2 => {
  const diagnostics = new Set<ProofAccountingDiagnostic>();
  const declaredPositive = new Set(input.declared_positive_case_ids);
  const declaredMutations = new Set(input.declared_mutation_ids);
  const positiveResultIds = input.positive_results.map(({ case_id: id }) => id);
  const mutationResultIds = input.mutation_results.map(({ mutation_id: id }) => id);

  if (input.declared_positive_case_ids.length === 0) {
    diagnostics.add("FACTORY_ACCOUNTING_POSITIVE_MISSING");
  }
  if (input.declared_mutation_ids.length === 0) {
    diagnostics.add("FACTORY_ACCOUNTING_MUTATION_MISSING");
  }
  if (duplicates(input.declared_positive_case_ids).length > 0 ||
      duplicates(positiveResultIds).length > 0) {
    diagnostics.add("FACTORY_ACCOUNTING_POSITIVE_DUPLICATE");
  }
  if (duplicates(input.declared_mutation_ids).length > 0 ||
      duplicates(mutationResultIds).length > 0) {
    diagnostics.add("FACTORY_ACCOUNTING_MUTATION_DUPLICATE");
  }
  if (positiveResultIds.some((id) => !declaredPositive.has(id))) {
    diagnostics.add("FACTORY_ACCOUNTING_POSITIVE_UNEXPECTED");
  }
  if (mutationResultIds.some((id) => !declaredMutations.has(id))) {
    diagnostics.add("FACTORY_ACCOUNTING_MUTATION_UNEXPECTED");
  }

  const positiveResultSet = new Set(positiveResultIds);
  const mutationResultSet = new Set(mutationResultIds);
  const positiveUnaccounted = [
    ...input.declared_positive_case_ids.filter((id) => !positiveResultSet.has(id)),
    ...input.positive_results
      .filter(({ status }) => status === "unaccounted")
      .map(({ case_id }) => case_id),
  ];
  const mutationUnaccounted = [
    ...input.declared_mutation_ids.filter((id) => !mutationResultSet.has(id)),
    ...input.mutation_results
      .filter(({ status }) => status === "unaccounted")
      .map(({ mutation_id }) => mutation_id),
  ];
  if (positiveUnaccounted.length > 0) {
    diagnostics.add("FACTORY_ACCOUNTING_POSITIVE_UNACCOUNTED");
  }
  if (mutationUnaccounted.length > 0) {
    diagnostics.add("FACTORY_ACCOUNTING_MUTATION_UNACCOUNTED");
  }
  if (input.positive_results.some(({ status }) => status === "failed")) {
    diagnostics.add("FACTORY_ACCOUNTING_POSITIVE_FAILED");
  }
  if (input.mutation_results.some(({ status }) => status === "survived")) {
    diagnostics.add("FACTORY_ACCOUNTING_MUTATION_SURVIVED");
  }

  const orderedDiagnostics = [...diagnostics].sort();
  return Object.freeze({
    schema_version: "ProofAccounting/v2" as const,
    result: orderedDiagnostics.length === 0 ? "pass" as const : "block" as const,
    positive: Object.freeze({
      declared: declaredPositive.size,
      passed: countBy(input.positive_results, ({ status }) => status === "passed"),
      failed: countBy(input.positive_results, ({ status }) => status === "failed"),
      unaccounted: new Set(positiveUnaccounted).size,
    }),
    mutations: Object.freeze({
      declared: declaredMutations.size,
      killed: countBy(input.mutation_results, ({ status }) => status === "killed"),
      survived: countBy(input.mutation_results, ({ status }) => status === "survived"),
      unaccounted: new Set(mutationUnaccounted).size,
    }),
    diagnostics: Object.freeze(orderedDiagnostics),
    authority_effect: "none" as const,
  });
};
