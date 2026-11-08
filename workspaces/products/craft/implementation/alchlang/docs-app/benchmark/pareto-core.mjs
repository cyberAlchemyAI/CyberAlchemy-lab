export function dominates(left, right, objectives) {
  const noWorse = objectives.every((objective) => objective.direction === "min"
    ? left.values[objective.id] <= right.values[objective.id] + objective.epsilon
    : left.values[objective.id] >= right.values[objective.id] - objective.epsilon);
  const better = objectives.some((objective) => objective.direction === "min"
    ? left.values[objective.id] < right.values[objective.id] - objective.epsilon
    : left.values[objective.id] > right.values[objective.id] + objective.epsilon);
  return noWorse && better;
}

export function paretoLayers(candidates, objectives) {
  const remaining = new Map(candidates.map((candidate) => [candidate.id, candidate]));
  const layers = [];
  while (remaining.size) {
    const population = [...remaining.values()];
    const frontier = population
      .filter((candidate) => !population.some((other) => other.id !== candidate.id && dominates(other, candidate, objectives)))
      .map((candidate) => candidate.id)
      .sort();
    layers.push(frontier);
    for (const id of frontier) remaining.delete(id);
  }
  return layers;
}

export function roundRobin(ids) {
  const sorted = [...ids].sort();
  const pairings = [];
  for (let left = 0; left < sorted.length; left += 1) {
    for (let right = left + 1; right < sorted.length; right += 1) {
      pairings.push({ left: sorted[left], right: sorted[right], randomize_order: true, allow_tie: true });
    }
  }
  return pairings;
}
