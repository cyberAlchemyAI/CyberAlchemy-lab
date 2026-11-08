import { createHash } from "node:crypto";
import { createServer, type IncomingMessage, type Server, type ServerResponse } from "node:http";
import { applyGatewayControl } from "./body-war-canary-gateway-state.js";
import { GatewayMetrics } from "./body-war-canary-gateway-metrics.js";
import { routeGatewayRequest } from "./body-war-canary-gateway-router.js";
import type { GatewayControlAction, GatewayState } from "./body-war-canary-gateway-types.js";
import type { GatewayOperationalEventType, OperationalEventPublisher } from "./body-war-canary-operational-event.js";

export interface UpstreamResult { readonly status: number; readonly body: string; readonly duration_seconds: number }
export type Upstream = (target: string, path: "/" | "/api/status") => Promise<UpstreamResult>;

export interface DataPlaneResult {
  readonly status: number;
  readonly body: string;
  readonly cohort: "stable" | "candidate";
  readonly sequence: number;
}

const statusClass = (status: number): "2xx" | "4xx" | "5xx" => status >= 500 ? "5xx" : status >= 400 ? "4xx" : "2xx";

export async function handleDataPlane(
  state: GatewayState,
  sequence: number,
  path: string,
  metrics: GatewayMetrics,
  upstream: Upstream,
): Promise<DataPlaneResult> {
  if (path !== "/" && path !== "/api/status") return { status: 404, body: "not found", cohort: "stable", sequence };
  const decision = routeGatewayRequest(state, sequence);
  if (decision.action === "inject-503") {
    metrics.recordTerminal({ cohort: "candidate", outcome: "bad", status_class: "5xx" }, 0);
    return { status: 503, body: "candidate fault", cohort: "candidate", sequence };
  }
  try {
    const result = await upstream(decision.target, path);
    metrics.recordTerminal({ cohort: decision.cohort, outcome: result.status >= 200 && result.status < 400 ? "good" : "bad", status_class: statusClass(result.status) }, result.duration_seconds);
    return { status: result.status, body: result.body, cohort: decision.cohort, sequence };
  } catch (error) {
    const timeout = error instanceof Error && error.name === "AbortError";
    metrics.recordTerminal({ cohort: decision.cohort, outcome: "bad", status_class: timeout ? "timeout" : "transport" }, 1);
    return { status: 502, body: timeout ? "upstream timeout" : "upstream transport failure", cohort: decision.cohort, sequence };
  }
}

export interface ControlResult { readonly status: 200 | 401 | 404 | 409; readonly state: GatewayState; readonly code: string }

export function handleControlPlane(
  state: GatewayState,
  suppliedToken: string,
  expectedTokenSha256: string,
  expectedGeneration: number,
  action: GatewayControlAction,
  at: string,
): ControlResult {
  const suppliedHash = createHash("sha256").update(suppliedToken, "utf8").digest("hex");
  if (suppliedHash !== expectedTokenSha256) return { status: 401, state, code: "GATEWAY_CONTROL_UNAUTHORIZED" };
  const result = applyGatewayControl(state, expectedGeneration, action, at);
  return result.status === "applied"
    ? { status: 200, state: result.after, code: "GATEWAY_CONTROL_APPLIED" }
    : { status: 409, state: result.state, code: result.code };
}

interface GatewayControlRequest {
  readonly expected_generation: number;
  readonly action: GatewayControlAction;
  readonly at: string;
}

const sendJson = (response: ServerResponse, status: number, value: unknown): void => {
  response.writeHead(status, { "content-type": "application/json" });
  response.end(JSON.stringify(value));
};

async function readControlRequest(request: IncomingMessage): Promise<GatewayControlRequest> {
  const chunks: Buffer[] = [];
  let length = 0;
  for await (const chunk of request) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    length += buffer.length;
    if (length > 4096) throw new Error("GATEWAY_CONTROL_BODY_TOO_LARGE");
    chunks.push(buffer);
  }
  const parsed = JSON.parse(Buffer.concat(chunks).toString("utf8")) as Partial<GatewayControlRequest>;
  if (!Number.isSafeInteger(parsed.expected_generation) || typeof parsed.at !== "string" || typeof parsed.action !== "object" || parsed.action === null) {
    throw new Error("GATEWAY_CONTROL_BODY_INVALID");
  }
  return parsed as GatewayControlRequest;
}

export interface GatewayServers {
  readonly data: Server;
  readonly control: Server;
  readonly metricsServer: Server;
  readonly metrics: GatewayMetrics;
  readonly getState: () => GatewayState;
}

const eventTypeFor = (action: GatewayControlAction): GatewayOperationalEventType =>
  action.kind === "install-candidate" ? "install_candidate" : action.kind === "set-candidate-fault" ? "candidate_fault_activated" : "rollback";

export async function handleConservedControlPlane(
  state: GatewayState,
  suppliedToken: string,
  expectedTokenSha256: string,
  expectedGeneration: number,
  action: GatewayControlAction,
  at: string,
  events: OperationalEventPublisher,
): Promise<ControlResult> {
  const result = handleControlPlane(state, suppliedToken, expectedTokenSha256, expectedGeneration, action, at);
  if (result.status === 200) {
    await events.publish({
      event_type: eventTypeFor(action),
      phase: "control_transition",
      generation: result.state.generation,
      outcome: "applied",
      fault_state: result.state.candidate_fault_active ? "active" : "inactive",
      at,
    });
  }
  return result;
}

export function createGatewayServers(initial: GatewayState, tokenSha256: string, upstream: Upstream, events: OperationalEventPublisher): GatewayServers {
  let state = initial;
  let sequence = 0;
  const metrics = new GatewayMetrics();
  const data = createServer((request, response) => {
    void (async () => {
      sequence += 1;
      const result = await handleDataPlane(state, sequence, request.url ?? "", metrics, upstream);
      response.writeHead(result.status, { "content-type": "text/plain", "x-orodi-cohort": result.cohort, "x-orodi-sequence": String(result.sequence) });
      response.end(result.body);
    })().catch(() => sendJson(response, 500, { code: "GATEWAY_DATA_UNEXPECTED" }));
  });
  const control = createServer((request, response) => {
    void (async () => {
      if (request.method === "GET" && request.url === "/ready") return sendJson(response, 200, { ready: true, generation: state.generation });
      if (request.method === "GET" && request.url === "/control/state") return sendJson(response, 200, state);
      if (request.method !== "POST" || request.url !== "/control/action") return sendJson(response, 404, { code: "GATEWAY_CONTROL_ROUTE_NOT_FOUND" });
      const suppliedToken = request.headers.authorization?.replace(/^Bearer\s+/i, "") ?? "";
      const body = await readControlRequest(request);
      const result = await handleConservedControlPlane(state, suppliedToken, tokenSha256, body.expected_generation, body.action, body.at, events);
      if (result.status === 200) state = result.state;
      return sendJson(response, result.status, { code: result.code, state: result.state });
    })().catch((error) => sendJson(response, error instanceof Error && error.message.startsWith("ORODI_OPERATIONAL_EVENT_") ? 503 : 409, { code: error instanceof Error ? error.message : "GATEWAY_CONTROL_BODY_INVALID", state }));
  });
  const metricsServer = createServer((request, response) => {
    if (request.method === "GET" && request.url === "/-/ready") return sendJson(response, 200, { ready: true });
    if (request.method === "GET" && request.url === "/metrics") {
      response.writeHead(200, { "content-type": "text/plain; version=0.0.4" });
      response.end(metrics.renderPrometheus(state));
      return;
    }
    sendJson(response, 404, { code: "GATEWAY_METRICS_ROUTE_NOT_FOUND" });
  });
  return { data, control, metricsServer, metrics, getState: () => state };
}
