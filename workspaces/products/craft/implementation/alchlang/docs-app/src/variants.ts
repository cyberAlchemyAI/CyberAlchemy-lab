export const experimentVariants = [
  "baseline",
  "compact-spacing",
  "progressive-reference",
  "task-first",
] as const;

export type ExperimentVariant = typeof experimentVariants[number];

export function variantFromSearch(search: string): ExperimentVariant {
  const requested = new URLSearchParams(search).get("variant");
  return experimentVariants.includes(requested as ExperimentVariant)
    ? requested as ExperimentVariant
    : "baseline";
}

export function variantClassName(variant: ExperimentVariant): string {
  return `experiment-${variant}`;
}
