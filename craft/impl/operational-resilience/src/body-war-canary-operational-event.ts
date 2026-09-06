export const ORODI_EVENT_TYPES = [
  "gateway_started",
  "install_candidate",
  "candidate_fault_activated",
  "rollback",
] as const;

export type GatewayOperationalEventType = typeof ORODI_EVENT_TYPES[number];
export type OperationalEventOutcome = "started" | "applied" | "pass" | "fail";
export type OperationalFaultState = "inactive" | "active" | "not_applicable";

export interface GatewayOperationalEvent {
  readonly event_type: GatewayOperationalEventType;
  readonly phase: "readiness" | "control_transition";
  readonly generation: number;
  readonly outcome: OperationalEventOutcome;
  readonly fault_state: OperationalFaultState;
  readonly at: string;
}

export interface OperationalEventPublisher {
  publish(event: GatewayOperationalEvent): Promise<void>;
}

interface OtlpAttribute {
  readonly key: string;
  readonly value: { readonly stringValue?: string; readonly intValue?: string };
}

const runIdPattern = /^[a-z0-9][a-z0-9-]{0,63}$/;
const utcPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/;
const allowedEvents = new Set<string>(ORODI_EVENT_TYPES);
const allowedOutcomes = new Set<string>(["started", "applied", "pass", "fail"]);
const allowedFaultStates = new Set<string>(["inactive", "active", "not_applicable"]);

const stringAttribute = (key: string, value: string): OtlpAttribute => ({ key, value: { stringValue: value } });
const intAttribute = (key: string, value: number): OtlpAttribute => ({ key, value: { intValue: String(value) } });

function validateEndpoint(endpoint: string): void {
  const parsed = new URL(endpoint);
  if (parsed.protocol !== "http:" || parsed.hostname !== "alloy" || parsed.port !== "4318" || parsed.pathname !== "/v1/logs" || parsed.search || parsed.hash) {
    throw new Error("ORODI_OTLP_LOGS_ENDPOINT_INVALID");
  }
}

function validateEvent(runId: string, event: GatewayOperationalEvent): void {
  if (!runIdPattern.test(runId)) throw new Error("ORODI_RUN_ID_INVALID");
  if (!allowedEvents.has(event.event_type)) throw new Error("ORODI_EVENT_TYPE_INVALID");
  if (event.phase !== "readiness" && event.phase !== "control_transition") throw new Error("ORODI_EVENT_PHASE_INVALID");
  if (!Number.isSafeInteger(event.generation) || event.generation < 0 || event.generation > 1_000_000) throw new Error("ORODI_EVENT_GENERATION_INVALID");
  if (!allowedOutcomes.has(event.outcome)) throw new Error("ORODI_EVENT_OUTCOME_INVALID");
  if (!allowedFaultStates.has(event.fault_state)) throw new Error("ORODI_EVENT_FAULT_STATE_INVALID");
  if (!utcPattern.test(event.at) || !Number.isFinite(Date.parse(event.at))) throw new Error("ORODI_EVENT_TIME_INVALID");
}

export function buildOtlpLogPayload(runId: string, event: GatewayOperationalEvent): object {
  validateEvent(runId, event);
  const timeUnixNano = (BigInt(Date.parse(event.at)) * 1_000_000n).toString();
  const body = `event_type=${event.event_type} phase=${event.phase} generation=${event.generation} outcome=${event.outcome} fault_state=${event.fault_state}`;
  return {
    resourceLogs: [{
      resource: {
        attributes: [
          stringAttribute("service.name", "orodi-gateway"),
          stringAttribute("service.namespace", "orodi"),
          stringAttribute("deployment.environment.name", "local"),
        ],
      },
      scopeLogs: [{
        scope: { name: "domainspec.orodi.operator-interface", version: "1" },
        logRecords: [{
          timeUnixNano,
          observedTimeUnixNano: timeUnixNano,
          severityNumber: 9,
          severityText: "INFO",
          body: { stringValue: body },
          attributes: [
            stringAttribute("run.id", runId),
            stringAttribute("event.type", event.event_type),
            stringAttribute("orodi.phase", event.phase),
            intAttribute("orodi.generation", event.generation),
            stringAttribute("orodi.outcome", event.outcome),
            stringAttribute("orodi.fault_state", event.fault_state),
          ],
        }],
      }],
    }],
  };
}

export function createOperationalEventPublisher(
  endpoint: string,
  runId: string,
  fetchImpl: typeof fetch = fetch,
): OperationalEventPublisher {
  validateEndpoint(endpoint);
  if (!runIdPattern.test(runId)) throw new Error("ORODI_RUN_ID_INVALID");
  return Object.freeze({
    async publish(event: GatewayOperationalEvent): Promise<void> {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 1000);
      try {
        const response = await fetchImpl(endpoint, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify(buildOtlpLogPayload(runId, event)),
          redirect: "error",
          signal: controller.signal,
        });
        if (!response.ok) throw new Error("ORODI_OPERATIONAL_EVENT_REJECTED");
      } catch (error) {
        if (error instanceof Error && error.message === "ORODI_OPERATIONAL_EVENT_REJECTED") throw error;
        throw new Error("ORODI_OPERATIONAL_EVENT_UNAVAILABLE");
      } finally {
        clearTimeout(timeout);
      }
    },
  });
}
