import { GATEWAY_INSTRUMENTS, validateMetricAttributes, type Cohort, type Outcome, type RequestMetricAttributes, type StatusClass } from "./body-war-canary-gateway-instruments.js";
import type { GatewayState } from "./body-war-canary-gateway-types.js";

const keyOf = (attributes: RequestMetricAttributes): string => `${attributes.cohort}\0${attributes.outcome}\0${attributes.status_class}`;
const COHORTS: readonly Cohort[] = ["stable", "candidate"];
const OUTCOMES: readonly Outcome[] = ["good", "bad"];
const STATUS_CLASSES: readonly StatusClass[] = ["2xx", "4xx", "5xx", "timeout", "transport"];

export class GatewayMetrics {
  readonly #requests = new Map<string, { attributes: RequestMetricAttributes; count: number }>();
  readonly #durations = new Map<Cohort, number[]>();

  recordTerminal(attributes: RequestMetricAttributes, durationSeconds: number): void {
    validateMetricAttributes(attributes);
    if (!Number.isFinite(durationSeconds) || durationSeconds < 0 || durationSeconds > 60) throw new Error("GATEWAY_DURATION_INVALID");
    const key = keyOf(attributes);
    const existing = this.#requests.get(key);
    this.#requests.set(key, { attributes: { ...attributes }, count: (existing?.count ?? 0) + 1 });
    const durations = this.#durations.get(attributes.cohort) ?? [];
    durations.push(durationSeconds);
    this.#durations.set(attributes.cohort, durations);
  }

  accountedRequests(): number {
    return [...this.#requests.values()].reduce((sum, row) => sum + row.count, 0);
  }

  renderPrometheus(state: GatewayState): string {
    const lines: string[] = [
      `# TYPE ${GATEWAY_INSTRUMENTS.requests}_total counter`,
    ];
    for (const cohort of COHORTS) {
      for (const outcome of OUTCOMES) {
        for (const status_class of STATUS_CLASSES) {
          const attributes = { cohort, outcome, status_class };
          const count = this.#requests.get(keyOf(attributes))?.count ?? 0;
          lines.push(`${GATEWAY_INSTRUMENTS.requests}_total{cohort="${cohort}",outcome="${outcome}",status_class="${status_class}"} ${count}`);
        }
      }
    }
    lines.push(`# TYPE ${GATEWAY_INSTRUMENTS.duration}_seconds summary`);
    for (const cohort of ["stable", "candidate"] as const) {
      const values = this.#durations.get(cohort) ?? [];
      const sum = values.reduce((total, value) => total + value, 0);
      lines.push(`${GATEWAY_INSTRUMENTS.duration}_seconds_count{cohort="${cohort}"} ${values.length}`);
      lines.push(`${GATEWAY_INSTRUMENTS.duration}_seconds_sum{cohort="${cohort}"} ${sum}`);
    }
    lines.push(`# TYPE ${GATEWAY_INSTRUMENTS.candidateWeight} gauge`);
    lines.push(`${GATEWAY_INSTRUMENTS.candidateWeight} ${state.candidate_weight / 100}`);
    lines.push(`${GATEWAY_INSTRUMENTS.candidateFaultActive} ${state.candidate_fault_active ? 1 : 0}`);
    lines.push(`${GATEWAY_INSTRUMENTS.candidateReferencePresent} ${state.candidate_target === null ? 0 : 1}`);
    lines.push(`${GATEWAY_INSTRUMENTS.configGeneration} ${state.generation}`);
    return `${lines.join("\n")}\n`;
  }
}
