import {spawn} from "node:child_process";
import {EventEmitter} from "node:events";
import {PassThrough} from "node:stream";

import {freezeResult, isRecord, nonEmptyString} from "./canonical.mjs";

const MODES = new Set(["direct-stdio", "daemon-proxy", "websocket"]);

export function resolveBackendCommand(configuration = {}) {
  const mode = configuration.mode ?? "direct-stdio";
  if (!MODES.has(mode)) throw new TypeError(`Unsupported Codex backend mode: ${mode}`);
  const command = nonEmptyString(configuration.command) ? configuration.command : "codex";
  const prefix = Array.isArray(configuration.command_prefix_args)
    ? configuration.command_prefix_args.filter(nonEmptyString)
    : [];
  if (mode === "websocket") {
    if (!nonEmptyString(configuration.url) || !configuration.url.startsWith("ws://")) throw new TypeError("A loopback ws:// URL is required for the WebSocket backend.");
    return freezeResult({mode, url: configuration.url, authority_effect: "none"});
  }
  const args = mode === "daemon-proxy"
    ? [...prefix, "app-server", "proxy", ...(nonEmptyString(configuration.socket_path) ? ["--sock", configuration.socket_path] : [])]
    : [...prefix, "app-server", "--stdio"];
  return freezeResult({mode, command, args, authority_effect: "none"});
}

function createWebSocketBackend(configuration, WebSocketImpl) {
  if (typeof WebSocketImpl !== "function") throw new TypeError("This Node runtime does not provide WebSocket support.");
  const child = new EventEmitter();
  child.stdin = new PassThrough();
  child.stdout = new PassThrough();
  child.stderr = new PassThrough();
  const socket = new WebSocketImpl(configuration.url);
  const queued = [];
  let inputBuffer = "";
  let opened = false;
  let closed = false;
  function transmit(line) {
    if (opened) socket.send(line);
    else queued.push(line);
  }
  child.stdin.on("data", (chunk) => {
    inputBuffer += chunk.toString("utf8");
    let index;
    while ((index = inputBuffer.indexOf("\n")) >= 0) {
      const line = inputBuffer.slice(0, index);
      inputBuffer = inputBuffer.slice(index + 1);
      if (line.trim()) transmit(line);
    }
  });
  socket.addEventListener("open", () => {
    opened = true;
    for (const line of queued.splice(0)) socket.send(line);
  });
  socket.addEventListener("message", async (event) => {
    const data = typeof event.data === "string" ? event.data : Buffer.from(await event.data.arrayBuffer()).toString("utf8");
    child.stdout.write(data.endsWith("\n") ? data : `${data}\n`);
  });
  socket.addEventListener("error", () => {
    if (!closed) child.emit("error", new Error("Codex app-server WebSocket backend failed."));
  });
  socket.addEventListener("close", (event) => {
    if (closed) return;
    closed = true;
    child.stdout.end();
    child.stderr.end();
    child.emit("exit", event.code === 1000 ? 0 : 1, null);
  });
  child.kill = () => {
    if (closed) return;
    closed = true;
    socket.close(1000, "ARE gateway shutdown");
    child.stdout.end();
    child.stderr.end();
    child.emit("exit", 0, "SIGTERM");
  };
  child.socket = socket;
  return child;
}

export function spawnCodexBackend(configuration = {}, spawnImpl = spawn, WebSocketImpl = globalThis.WebSocket) {
  if (!isRecord(configuration)) throw new TypeError("Codex backend configuration must be an object.");
  const resolved = resolveBackendCommand(configuration);
  if (resolved.mode === "websocket") return createWebSocketBackend(resolved, WebSocketImpl);
  return spawnImpl(resolved.command, resolved.args, {stdio: ["pipe", "pipe", "pipe"]});
}
