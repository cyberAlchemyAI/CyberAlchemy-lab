import {EventEmitter} from "node:events";
import {createConnection} from "node:net";
import {PassThrough} from "node:stream";

import {
  ACKNOWLEDGED_CONTINUITY_MODE,
  GATEWAY_ACK_SCHEMA,
  GATEWAY_CONNECT_SCHEMA,
  GATEWAY_CONNECTED_SCHEMA,
  GATEWAY_DELIVERY_SCHEMA,
} from "./gateway.mjs";

export function connectGatewayRpcTransport(options = {}) {
  const connectImpl = options.connect_impl ?? createConnection;
  const socket = connectImpl(options.socket_path);
  const input = new PassThrough();
  const output = new PassThrough();
  const failure = new EventEmitter();
  let buffer = "";
  let connected = false;
  let closing = false;
  let failed = false;
  let failureError = null;
  let receipt = null;
  let lastAcknowledgedSequence = options.last_acked_sequence ?? 0;
  let lastReceivedSequence = lastAcknowledgedSequence;
  const acknowledgedContinuity = options.continuity !== false;
  let resolveReady;
  let rejectReady;
  const ready = new Promise((resolveValue, reject) => {
    resolveReady = resolveValue;
    rejectReady = reject;
  });

  function fail(code, detail) {
    if (closing || failed) return;
    failed = true;
    failureError = new Error(`${code}${detail ? `:${detail}` : ""}`);
    failureError.code = code;
    if (!connected) rejectReady(failureError);
    else failure.emit("failure", failureError);
    if (!socket.destroyed) socket.destroy();
  }

  socket.on("connect", () => {
    const continuity = acknowledgedContinuity ? {
      mode: ACKNOWLEDGED_CONTINUITY_MODE,
      ...(options.resume_token ? {resume_token: options.resume_token} : {}),
      last_acked_sequence: lastAcknowledgedSequence,
      request_aliases: options.request_aliases ?? [],
    } : undefined;
    socket.write(`${JSON.stringify({schema_version: GATEWAY_CONNECT_SCHEMA, consumer_id: options.consumer_id, lane: options.lane, ...(continuity ? {continuity} : {})})}\n`);
  });
  input.on("data", (data) => {
    if (!socket.destroyed) socket.write(data);
  });
  input.on("end", () => {
    if (!socket.destroyed) socket.end();
  });

  function consumeServerBytes(data) {
    buffer += data.toString("utf8");
    let index;
    while ((index = buffer.indexOf("\n")) >= 0) {
      const line = buffer.slice(0, index);
      buffer = buffer.slice(index + 1);
      if (!line.trim()) continue;
      let frame;
      try { frame = JSON.parse(line); } catch { return fail("gateway.invalid-delivery-json"); }
      if (!acknowledgedContinuity) {
        output.write(`${line}\n`);
        continue;
      }
      if (frame.schema_version !== GATEWAY_DELIVERY_SCHEMA || !Number.isSafeInteger(frame.sequence) || frame.sequence <= 0 || !Object.hasOwn(frame, "message")) {
        return fail("gateway.invalid-delivery-envelope");
      }
      if (frame.sequence <= lastAcknowledgedSequence) {
        socket.write(`${JSON.stringify({schema_version: GATEWAY_ACK_SCHEMA, through_sequence: lastAcknowledgedSequence})}\n`);
        continue;
      }
      if (frame.sequence !== lastReceivedSequence + 1) return fail("gateway.delivery-sequence-gap", `${lastReceivedSequence}->${frame.sequence}`);
      lastReceivedSequence = frame.sequence;
      output.write(`${JSON.stringify(frame.message)}\n`, () => {
        lastAcknowledgedSequence = Math.max(lastAcknowledgedSequence, frame.sequence);
        if (!socket.destroyed) socket.write(`${JSON.stringify({schema_version: GATEWAY_ACK_SCHEMA, through_sequence: lastAcknowledgedSequence})}\n`);
      });
    }
  }
  const onHandshakeData = (chunk) => {
    buffer += chunk.toString("utf8");
    if (buffer.length > 16384) return fail("gateway.handshake-too-large");
    const index = buffer.indexOf("\n");
    if (index < 0) return;
    socket.off("data", onHandshakeData);
    try { receipt = JSON.parse(buffer.slice(0, index)); } catch { receipt = null; }
    if (!receipt || receipt.schema_version !== GATEWAY_CONNECTED_SCHEMA || receipt.ok !== true) {
      return fail(receipt?.reason ?? "gateway.invalid-connect-receipt", receipt?.detail);
    }
    connected = true;
    const remainder = buffer.slice(index + 1);
    buffer = "";
    if (remainder) consumeServerBytes(remainder);
    socket.on("data", consumeServerBytes);
    resolveReady(receipt);
  };
  socket.on("data", onHandshakeData);
  socket.on("error", (error) => {
    if (!closing) fail("gateway.connection-failed", error.message);
  });
  socket.on("close", () => {
    output.end();
    if (!closing) fail("gateway.connection-closed");
  });

  async function close() {
    if (closing) return;
    closing = true;
    if (!socket.destroyed) socket.end();
  }

  return Object.freeze({
    kind: "persistent-gateway",
    input,
    output,
    failure,
    ready,
    get_failure: () => failureError,
    close,
    inspect: () => ({kind: "persistent-gateway", connected, closing, failed, receipt, continuity_mode: acknowledgedContinuity ? ACKNOWLEDGED_CONTINUITY_MODE : null, resume_token: receipt?.continuity?.resume_token ?? null, resume_token_digest: receipt?.continuity?.resume_token_digest ?? null, last_acked_sequence: lastAcknowledgedSequence, authority_effect: "none"}),
  });
}

export function runGatewayClientProxy(options = {}) {
  const clientInput = options.client_input ?? process.stdin;
  const clientOutput = options.client_output ?? process.stdout;
  const clientError = options.client_error ?? process.stderr;
  const connectImpl = options.connect_impl ?? createConnection;
  const socket = connectImpl(options.socket_path);
  clientInput.pause?.();
  let buffer = "";
  let connected = false;

  socket.on("connect", () => {
    socket.write(`${JSON.stringify({schema_version: GATEWAY_CONNECT_SCHEMA, consumer_id: options.consumer_id, lane: options.lane})}\n`);
  });
  const onData = (chunk) => {
    buffer += chunk.toString("utf8");
    const index = buffer.indexOf("\n");
    if (index < 0) return;
    socket.off("data", onData);
    let receipt;
    try { receipt = JSON.parse(buffer.slice(0, index)); } catch { receipt = null; }
    if (!receipt || receipt.schema_version !== GATEWAY_CONNECTED_SCHEMA || receipt.ok !== true) {
      clientError.write(`${JSON.stringify(receipt ?? {reason: "gateway.invalid-connect-receipt"})}\n`);
      socket.destroy();
      return;
    }
    connected = true;
    const remainder = buffer.slice(index + 1);
    if (remainder) clientOutput.write(remainder);
    socket.on("data", (data) => clientOutput.write(data));
    clientInput.on("data", (data) => socket.write(data));
    clientInput.on("end", () => socket.end());
    clientInput.resume?.();
  };
  socket.on("data", onData);
  socket.on("error", (error) => clientError.write(`ARE gateway connection failed: ${error.message}\n`));
  socket.on("close", () => {
    if (!connected) clientInput.pause?.();
  });
  return socket;
}
