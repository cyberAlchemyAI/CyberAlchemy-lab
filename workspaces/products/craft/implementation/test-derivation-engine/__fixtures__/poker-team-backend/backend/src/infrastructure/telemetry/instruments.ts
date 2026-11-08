import { metrics } from "@opentelemetry/api";
import type {
  Attributes,
  Meter,
  Counter,
  Histogram,
  UpDownCounter,
} from "@opentelemetry/api";

const METER_SCOPE = "poker-team";

let _meter: Meter | undefined;

export const getMeter = (): Meter => {
  if (!_meter) {
    _meter = metrics.getMeter(METER_SCOPE);
  }
  return _meter;
};

// --- Instrument factories ---

export const createCounter = (
  name: string,
  options?: { unit?: string; description?: string },
): Counter => getMeter().createCounter(name, options);

export const createHistogram = (
  name: string,
  options?: { unit?: string; description?: string },
): Histogram => getMeter().createHistogram(name, options);

export const createUpDownCounter = (
  name: string,
  options?: { unit?: string; description?: string },
): UpDownCounter => getMeter().createUpDownCounter(name, options);

export type GaugeInstrument = {
  record: (value: number, attributes?: Attributes) => void;
  add: (delta: number, attributes?: Attributes) => void;
};

const serializeAttributes = (attributes: Attributes): string => {
  const keys = Object.keys(attributes).sort();
  return JSON.stringify(
    keys.map((key) => [key, attributes[key]]),
  );
};

export const createGauge = (
  name: string,
  options?: { unit?: string; description?: string },
): GaugeInstrument => {
  const gauge = getMeter().createObservableGauge(name, options);
  const latestValues = new Map<string, { value: number; attributes: Attributes }>();

  gauge.addCallback((observableResult) => {
    for (const sample of latestValues.values()) {
      observableResult.observe(sample.value, sample.attributes);
    }
  });

  const upsertValue = (value: number, attributes?: Attributes): void => {
    const safeAttributes = { ...(attributes ?? {}) };
    latestValues.set(serializeAttributes(safeAttributes), {
      value,
      attributes: safeAttributes,
    });
  };

  return {
    record: (value, attributes) => {
      upsertValue(value, attributes);
    },
    add: (delta, attributes) => {
      const safeAttributes = { ...(attributes ?? {}) };
      const key = serializeAttributes(safeAttributes);
      const previous = latestValues.get(key)?.value ?? 0;
      latestValues.set(key, {
        value: previous + delta,
        attributes: safeAttributes,
      });
    },
  };
};

// --- Pre-built shared instruments (O4, O5, O7, O8) ---

export const operationInvocation = createCounter("operation.invocation", {
  unit: "{invocation}",
  description: "Number of operation invocations (O4)",
});

export const operationDuration = createHistogram("operation.duration", {
  unit: "s",
  description: "Operation execution duration in seconds (O4)",
});

export const httpServerRequestDuration = createHistogram(
  "http.server.request.duration",
  {
    unit: "s",
    description: "HTTP server request duration in seconds (O8)",
  },
);

export const ruleViolation = createCounter("rule.violation", {
  unit: "{violation}",
  description: "Business rule violation count (O5)",
});

export const postconditionCheck = createCounter("postcondition.check", {
  unit: "{check}",
  description: "Postcondition verification result (O7)",
});

export const stateTransition = createCounter("state.transition", {
  unit: "{transition}",
  description: "State machine transition count (O1)",
});

export const stateInvalidTransition = createCounter(
  "state.invalid_transition",
  {
    unit: "{attempt}",
    description: "Invalid state transition attempts (O1)",
  },
);

export const statePopulation = createUpDownCounter("state.population", {
  unit: "{entity}",
  description: "Current entity count per state (O2)",
});

export const invariantViolation = createGauge("invariant.violation", {
  unit: "{entity}",
  description: "Domain invariant violation count (O3)",
});

export const calculationDrift = createHistogram("calculation.drift", {
  unit: "1",
  description:
    "Absolute drift between expected and actual calculation result (O6)",
});

export const eventEmit = createCounter("event.emit", {
  unit: "{event}",
  description: "Domain event emission count (O10)",
});

export const eventConsume = createCounter("event.consume", {
  unit: "{event}",
  description: "Domain event consumption count (O10)",
});

export const eventConsumerLag = createHistogram("event.consumer.lag", {
  unit: "s",
  description: "Lag between event emission and consumption (O10)",
});

export const queryDuration = createHistogram("query.duration", {
  unit: "s",
  description: "Query execution duration in seconds (O11)",
});

export const queryResultSize = createHistogram("query.result_size", {
  unit: "{row}",
  description: "Query result size in rows/items (O11)",
});

export const queryCacheHitRatio = createHistogram("query.cache.hit_ratio", {
  unit: "1",
  description: "Observed query cache hit ratio samples (O11)",
});

export const queryCacheLookup = createCounter("query.cache.lookup", {
  unit: "{lookup}",
  description: "Query cache lookup attempts (O11)",
});

export const queryCacheHit = createCounter("query.cache.hit", {
  unit: "{hit}",
  description: "Query cache hits (O11)",
});

export const idempotencyViolation = createGauge("idempotency.violation", {
  unit: "{violation}",
  description: "Idempotency constraint violation count (O9)",
});

export const exposureAmount = createGauge("exposure.amount", {
  unit: "{currency_minor}",
  description: "Estimated monetary exposure caused by duplicate transactions (O9/O15)",
});

export const idempotencyDedup = createCounter("idempotency.dedup", {
  unit: "{dedup}",
  description: "Idempotent request deduplication count (O9)",
});

export const reconciliationMismatch = createGauge(
  "reconciliation.mismatch",
  {
    unit: "{currency_minor}",
    description: "Reconciliation mismatch amount (O15)",
  },
);

export const transactionDuplicate = createCounter("transaction.duplicate", {
  unit: "{duplicate}",
  description: "Detected duplicate financial transactions (O15)",
});

export const workflowInvocation = createCounter("workflow.invocation", {
  unit: "{invocation}",
  description: "Workflow invocation count (O12)",
});

export const workflowDuration = createHistogram("workflow.duration", {
  unit: "s",
  description: "Workflow total duration (O12)",
});

export const workflowFailed = createCounter("workflow.failed", {
  unit: "{failure}",
  description: "Workflow failure count by step (O12)",
});

export const workflowStepDuration = createHistogram("workflow.step.duration", {
  unit: "s",
  description: "Workflow step duration in seconds (O12)",
});

export const businessStatsRecorded = createCounter("business.stats_recorded", {
  unit: "{snapshot}",
  description: "Number of stats records ingested (O13)",
});

export const businessCorrectionRate = createHistogram(
  "business.correction_rate",
  {
    unit: "1",
    description: "Rolling ratio of corrected stats records (O13)",
  },
);

export const businessIngestionLatency = createHistogram(
  "business.ingestion_latency",
  {
    unit: "s",
    description: "Latency from stat date to ingestion observation (O13)",
  },
);

export const businessActivePlayersWithStats = createHistogram(
  "business.active_players_with_stats",
  {
    unit: "{player}",
    description: "Observed active players with ingested stats (O13)",
  },
);

export const businessSettlementsExecuted = createCounter(
  "business.settlements_executed",
  {
    unit: "{settlement}",
    description: "Number of settlements executed (O13)",
  },
);

export const businessPayoutAmount = createCounter("business.payout_amount", {
  unit: "{currency_minor}",
  description: "Total payout amount in minor currency units (O13)",
});

export const businessMakeupRecovered = createCounter(
  "business.makeup_recovered",
  {
    unit: "{currency_minor}",
    description: "Total recovered makeup amount in minor units (O13)",
  },
);

export const businessAvgSettlementValue = createHistogram(
  "business.avg_settlement_value",
  {
    unit: "{currency_minor}",
    description: "Observed settlement value samples in minor units (O13)",
  },
);

export const businessPreviewBeforeSettlement = createHistogram(
  "business.preview_before_settlement",
  {
    unit: "1",
    description: "Observed preview-to-settlement ratio samples (O13)",
  },
);

export const funnelStep = createCounter("funnel.step", {
  unit: "{step}",
  description: "Funnel step completion (O14)",
});

export const funnelConversionRate = createHistogram("funnel.conversion_rate", {
  unit: "1",
  description: "Funnel conversion rate (O14)",
});
