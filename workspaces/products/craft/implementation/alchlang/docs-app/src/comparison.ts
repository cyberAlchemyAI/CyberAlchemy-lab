import { experimentVariants, type ExperimentVariant } from "./variants";

export const preferenceDimensions = [
  "readability",
  "navigation",
  "density",
  "task_completion",
  "overall",
] as const;

export type PreferenceDimension = typeof preferenceDimensions[number];
export type PreferenceChoice = "left" | "tie" | "right";

export type ComparisonPair = {
  id: string;
  left: ExperimentVariant;
  right: ExperimentVariant;
};

export type PairObservation = {
  pairId: string;
  choices: Partial<Record<PreferenceDimension, PreferenceChoice>>;
  note: string;
};

export const variantDetails: Record<ExperimentVariant, { label: string; treatment: string }> = {
  baseline: {
    label: "Baseline",
    treatment: "Complete reference with the original spacing and reading order.",
  },
  "compact-spacing": {
    label: "Compact spacing",
    treatment: "The same content with reduced vertical rhythm and component scale.",
  },
  "progressive-reference": {
    label: "Progressive reference",
    treatment: "Long reference sections begin collapsed behind explicit disclosures.",
  },
  "task-first": {
    label: "Task first",
    treatment: "The working source editor appears before explanatory reading.",
  },
};

export const dimensionDetails: Record<PreferenceDimension, { label: string; prompt: string }> = {
  readability: { label: "Readability", prompt: "Which treatment is easier to scan and read?" },
  navigation: { label: "Navigation", prompt: "Which treatment makes the next useful destination clearer?" },
  density: { label: "Information density", prompt: "Which treatment balances completeness and visual load better?" },
  task_completion: { label: "Task completion", prompt: "Which treatment helps you finish the review task faster?" },
  overall: { label: "Overall preference", prompt: "Which treatment would you choose for this documentation?" },
};

export function createComparisonPairs(ids: readonly ExperimentVariant[] = experimentVariants): ComparisonPair[] {
  const pairs: ComparisonPair[] = [];
  for (let left = 0; left < ids.length; left += 1) {
    for (let right = left + 1; right < ids.length; right += 1) {
      const canonicalLeft = ids[left];
      const canonicalRight = ids[right];
      const reverseDisplay = pairs.length % 2 === 1;
      pairs.push({
        id: `${canonicalLeft}--${canonicalRight}`,
        left: reverseDisplay ? canonicalRight : canonicalLeft,
        right: reverseDisplay ? canonicalLeft : canonicalRight,
      });
    }
  }
  return pairs;
}

export const comparisonPairs = createComparisonPairs();

export function observationComplete(observation: PairObservation | undefined): boolean {
  return preferenceDimensions.every((dimension) => observation?.choices[dimension]);
}

export function reviewComplete(observations: Record<string, PairObservation>): boolean {
  return comparisonPairs.every((pair) => observationComplete(observations[pair.id]));
}

export type VariantScores = Record<ExperimentVariant, Record<PreferenceDimension, number>>;

export function scoreObservations(observations: Record<string, PairObservation>): VariantScores {
  const scores = Object.fromEntries(experimentVariants.map((variant) => [
    variant,
    Object.fromEntries(preferenceDimensions.map((dimension) => [dimension, 0])),
  ])) as VariantScores;

  for (const pair of comparisonPairs) {
    const observation = observations[pair.id];
    if (!observation) continue;
    for (const dimension of preferenceDimensions) {
      const choice = observation.choices[dimension];
      if (choice === "left") scores[pair.left][dimension] += 1;
      if (choice === "right") scores[pair.right][dimension] += 1;
      if (choice === "tie") {
        scores[pair.left][dimension] += 0.5;
        scores[pair.right][dimension] += 0.5;
      }
    }
  }
  return scores;
}

function dominates(
  left: Record<PreferenceDimension, number>,
  right: Record<PreferenceDimension, number>,
): boolean {
  const noWorse = preferenceDimensions.every((dimension) => left[dimension] >= right[dimension]);
  const better = preferenceDimensions.some((dimension) => left[dimension] > right[dimension]);
  return noWorse && better;
}

export function comparisonParetoLayers(scores: VariantScores): ExperimentVariant[][] {
  const remaining = new Set<ExperimentVariant>(experimentVariants);
  const layers: ExperimentVariant[][] = [];
  while (remaining.size) {
    const population = [...remaining];
    const frontier = population.filter((candidate) => !population.some(
      (other) => other !== candidate && dominates(scores[other], scores[candidate]),
    ));
    layers.push(frontier);
    frontier.forEach((candidate) => remaining.delete(candidate));
  }
  return layers;
}

function orderedObservation(pair: ComparisonPair, observation: PairObservation) {
  return {
    pair_id: pair.id,
    displayed_left: pair.left,
    displayed_right: pair.right,
    choices: Object.fromEntries(preferenceDimensions.map((dimension) => [dimension, observation.choices[dimension]])),
    note: observation.note.trim(),
  };
}

export function comparisonEvidence(observations: Record<string, PairObservation>) {
  const scores = scoreObservations(observations);
  return {
    schema_version: "alchlang-pareto-human-comparison/v1",
    status: reviewComplete(observations) ? "complete" : "incomplete",
    variant_set: [...experimentVariants],
    dimensions: [...preferenceDimensions],
    observations: comparisonPairs
      .filter((pair) => observations[pair.id])
      .map((pair) => orderedObservation(pair, observations[pair.id])),
    scores,
    pareto_layers: reviewComplete(observations) ? comparisonParetoLayers(scores) : [],
    claim_ceiling: "Human comparison evidence only. A Pareto frontier does not select, approve, merge, publish, or deploy a treatment.",
  };
}

export function canonicalJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.entries(value as Record<string, unknown>)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, item]) => `${JSON.stringify(key)}:${canonicalJson(item)}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

export async function sha256(value: string): Promise<string> {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

