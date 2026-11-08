import { createHash } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import type { Server } from "node:http";
import { initialGatewayState } from "./body-war-canary-gateway-state.js";
import { createGatewayServers, type Upstream } from "./body-war-canary-gateway-server.js";
import { createOperationalEventPublisher } from "./body-war-canary-operational-event.js";

export interface GatewayStartupConfig {
  readonly stable_target: string;
  readonly data_host: "0.0.0.0";
  readonly data_port: 18080;
  readonly control_host: "0.0.0.0";
  readonly control_port: 18081;
  readonly metrics_host: "0.0.0.0";
  readonly metrics_port: 9464;
  readonly upstream_timeout_ms: number;
  readonly control_token: string;
  readonly started_at: string;
  readonly run_id: string;
  readonly otlp_logs_endpoint: "http://alloy:4318/v1/logs";
}

const exactPort = <T extends number>(value: string | undefined, expected: T, code: string): T => {
  const parsed = Number(value ?? String(expected));
  if (parsed !== expected) throw new Error(code);
  return expected;
};

export function gatewayStartupConfigFromEnvironment(env: NodeJS.ProcessEnv, controlToken: string, startedAt = new Date().toISOString()): GatewayStartupConfig {
  const timeout = Number(env.ORODI_UPSTREAM_TIMEOUT_MS ?? "1000");
  if (!Number.isSafeInteger(timeout) || timeout < 1 || timeout > 1000) throw new Error("GATEWAY_UPSTREAM_TIMEOUT_INVALID");
  if (controlToken.length < 32) throw new Error("GATEWAY_CONTROL_TOKEN_TOO_SHORT");
  return Object.freeze({
    stable_target: env.ORODI_STABLE_TARGET ?? "http://stable:5174",
    data_host: "0.0.0.0",
    data_port: exactPort(env.ORODI_DATA_PORT, 18080, "GATEWAY_DATA_PORT_INVALID"),
    control_host: "0.0.0.0",
    control_port: exactPort(env.ORODI_CONTROL_PORT, 18081, "GATEWAY_CONTROL_PORT_INVALID"),
    metrics_host: "0.0.0.0",
    metrics_port: exactPort(env.ORODI_METRICS_PORT, 9464, "GATEWAY_METRICS_PORT_INVALID"),
    upstream_timeout_ms: timeout,
    control_token: controlToken,
    started_at: startedAt,
    run_id: env.ORODI_RUN_ID ?? "orodi-local",
    otlp_logs_endpoint: (env.ORODI_OTLP_LOGS_ENDPOINT ?? "http://alloy:4318/v1/logs") as "http://alloy:4318/v1/logs",
  });
}

export function createBoundedUpstream(timeoutMs: number, fetchImpl: typeof fetch = fetch): Upstream {
  if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1 || timeoutMs > 1000) throw new Error("GATEWAY_UPSTREAM_TIMEOUT_INVALID");
  return async (target, path) => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    const started = performance.now();
    try {
      const response = await fetchImpl(new URL(path, `${target}/`), { signal: controller.signal, redirect: "error" });
      const body = (await response.text()).slice(0, 1_048_576);
      return { status: response.status, body, duration_seconds: Math.min((performance.now() - started) / 1000, 60) };
    } finally {
      clearTimeout(timeout);
    }
  };
}

export function prepareGateway(config: GatewayStartupConfig, upstream: Upstream) {
  if (Number(config.data_port) === Number(config.control_port)) throw new Error("GATEWAY_PORT_COLLISION");
  const tokenSha256 = createHash("sha256").update(config.control_token, "utf8").digest("hex");
  const state = initialGatewayState(config.stable_target, config.started_at);
  const events = createOperationalEventPublisher(config.otlp_logs_endpoint, config.run_id);
  const servers = createGatewayServers(state, tokenSha256, upstream, events);
  return Object.freeze({ ...servers, events, tokenSha256, initialization_order: ["metrics", "data-listener", "control-listener"] as const, authority_effect: "none" as const });
}

const listen = (server: Server, port: number, host: string): Promise<void> => new Promise((resolve, reject) => {
  const onError = (error: Error): void => reject(error);
  server.once("error", onError);
  server.listen(port, host, () => {
    server.off("error", onError);
    resolve();
  });
});

const close = (server: Server): Promise<void> => new Promise((resolve) => {
  if (!server.listening) return resolve();
  server.close(() => resolve());
});

export async function startGateway(config: GatewayStartupConfig) {
  const prepared = prepareGateway(config, createBoundedUpstream(config.upstream_timeout_ms));
  try {
    await listen(prepared.metricsServer, config.metrics_port, config.metrics_host);
    await listen(prepared.data, config.data_port, config.data_host);
    await listen(prepared.control, config.control_port, config.control_host);
    await prepared.events.publish({ event_type: "gateway_started", phase: "readiness", generation: 0, outcome: "started", fault_state: "inactive", at: config.started_at });
  } catch (error) {
    await Promise.all([close(prepared.control), close(prepared.data), close(prepared.metricsServer)]);
    throw error;
  }
  return Object.freeze({
    ...prepared,
    close: () => Promise.all([close(prepared.control), close(prepared.data), close(prepared.metricsServer)]).then(() => undefined),
  });
}

export async function main(): Promise<void> {
  const tokenPath = process.env.ORODI_CONTROL_TOKEN_FILE ?? "/run/orodi/control-token";
  const metadata = await stat(tokenPath);
  if (!metadata.isFile() || (metadata.mode & 0o777) !== 0o600) throw new Error("GATEWAY_CONTROL_TOKEN_MODE_INVALID");
  const controlToken = (await readFile(tokenPath, "utf8")).trim();
  const config = gatewayStartupConfigFromEnvironment(process.env, controlToken);
  const gateway = await startGateway(config);
  console.log(`ORODI_GATEWAY_READY data=${config.data_port} control=${config.control_port} metrics=${config.metrics_port}`);
  const shutdown = (): void => {
    void gateway.close().finally(() => { process.exitCode = 0; });
  };
  process.once("SIGINT", shutdown);
  process.once("SIGTERM", shutdown);
}

if (process.argv[1]?.endsWith("body-war-canary-gateway-entry.js")) {
  void main().catch((error) => {
    console.error(error instanceof Error ? error.message : "GATEWAY_STARTUP_FAILED");
    process.exitCode = 1;
  });
}
