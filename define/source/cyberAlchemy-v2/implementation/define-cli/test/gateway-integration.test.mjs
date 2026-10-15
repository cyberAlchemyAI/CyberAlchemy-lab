import assert from "node:assert/strict";
import {randomUUID} from "node:crypto";
import {EventEmitter} from "node:events";
import {mkdtempSync, rmSync} from "node:fs";
import {resolve} from "node:path";
import {PassThrough} from "node:stream";
import test from "node:test";

import {createAppServerDefineAgent} from "../src/app-server-agent.mjs";
import {connectGatewayRpcTransport, createAppServerRpcClient, createCodexAppServerWrapper, createCodexGatewayBackendAdapter, createPersistentGateway,
  loadRepositoryProfile} from "../../agent-reasoning-engine/packages/codex-app-server-wrapper/index.mjs";

const repositoryRoot = resolve(import.meta.dirname, "../../../..");
const connectionToken = "define-gateway-test-token-32-bytes-minimum";
const turn = {
  schema_version: "cav2.define-conversation-turn/v2",
  phase: "discover",
  message: "Tell me more about the subject.",
  question: "Who will use it?",
  scope_ready: false,
  covered_dimensions: [],
  scope: {language: {user_phrases: [], terms: [], distinctions: [], relationships: [], constraints: [], owners: [], open_questions: []}},
  options: [],
};

function fakeCodexChild(observed) {
  const child = new EventEmitter();
  child.stdin = new PassThrough();
  child.stdout = new PassThrough();
  child.stderr = new PassThrough();
  child.kill = () => { child.emit("exit", 0, "SIGTERM"); return true; };
  let buffer = "";
  child.stdin.on("data", (bytes) => {
    buffer += String(bytes);
    let index;
    while ((index = buffer.indexOf("\n")) >= 0) {
      const request = JSON.parse(buffer.slice(0, index));
      buffer = buffer.slice(index + 1);
      if (!request.method) continue;
      observed.push(request);
      if (request.method === "initialize") {
        child.stdout.write(`${JSON.stringify({id: request.id, result: {}})}\n`);
      } else if (request.method === "thread/start") {
        child.stdout.write(`${JSON.stringify({id: request.id, result: {thread: {id: "thread:define-gateway"}}})}\n`);
      } else if (request.method === "turn/start") {
        child.stdout.write(`${JSON.stringify({id: request.id, result: {turn: {id: "turn:define-gateway"}}})}\n`);
        queueMicrotask(() => child.stdout.write(`${JSON.stringify({method: "turn/completed", params: {
          threadId: "thread:define-gateway", turn: {id: "turn:define-gateway", status: "completed",
            items: [{type: "agentMessage", text: JSON.stringify(turn)}]},
        }})}\n`));
      }
    }
  });
  return child;
}

test("Define's default client completes one read-only turn through the acknowledged Codex gateway", {timeout: 10000}, async () => {
  const directory = mkdtempSync("/tmp/are-define-gateway-");
  const socket = process.platform === "win32" ? `\\\\.\\pipe\\are-define-${randomUUID()}` : resolve(directory, "gateway.sock");
  const observed = [];
  const loaded = loadRepositoryProfile(resolve(repositoryRoot,
    "cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/codex-app-server-wrapper/profiles/repository-v1.json"), repositoryRoot);
  assert.equal(loaded.ok, true, loaded.reason_codes?.join(","));
  const gateway = createPersistentGateway({listen_path: socket, backend: {mode: "direct-stdio"},
    backend_adapter: createCodexGatewayBackendAdapter(), connection_token: connectionToken,
    authorize_client: ({consumer_id, lane}) => ["codex:define-cli", "codex:human-chat"].includes(consumer_id) && lane === "interaction-bound",
    spawn_impl: () => fakeCodexChild(observed),
    wrapper_factory: () => createCodexAppServerWrapper({...loaded, loaded_profile: loaded.value})});
  await gateway.start();
  const agent = createAppServerDefineAgent({repository_root: repositoryRoot, gateway_socket: socket,
    connection_token: connectionToken, define_entrypoint_selected: true});
  let humanClient = null;
  let secondDefineAgent = null;
  try {
    let response;
    try { response = await agent.respond({mode: "discovery", user_input: "I am defining an archive", scope_confirmed: false}); }
    catch (error) { throw new Error(`Define gateway turn failed: ${JSON.stringify(error.details ?? error.message)}`); }
    assert.equal(response.question, "Who will use it?");
    assert.deepEqual(observed.filter((entry) => ["thread/start", "turn/start"].includes(entry.method)).map((entry) => entry.method),
      ["thread/start", "turn/start"]);
    const started = observed.find((entry) => entry.method === "thread/start");
    const submitted = observed.find((entry) => entry.method === "turn/start");
    assert.equal(started.params.sandbox, "read-only");
    assert.equal(started.params.approvalPolicy, "on-request");
    assert.deepEqual(submitted.params.sandboxPolicy, {type: "readOnly", networkAccess: false});
    assert.equal(submitted.params.outputSchema.properties.schema_version.const, "cav2.define-conversation-turn/v2");
    assert.match(submitted.params.input[0].text, /I am defining an archive/);
    const humanTransport = connectGatewayRpcTransport({socket_path: socket, consumer_id: "codex:human-chat",
      lane: "interaction-bound", connection_token: connectionToken, expected_backend_adapter_id: "codex-app-server/v1"});
    humanClient = createAppServerRpcClient({transport: humanTransport});
    await humanClient.initialize({clientInfo: {name: "hosted-client-test", version: "1"}, capabilities: {experimentalApi: true}});
    assert.deepEqual(gateway.inspect().sessions.map(({consumer_id}) => consumer_id), ["codex:define-cli", "codex:human-chat"]);
    await assert.rejects(humanClient.request("thread/read", {threadId: "thread:define-gateway", includeTurns: false}),
      /Gateway backend-thread ownership rejected/);
    secondDefineAgent = createAppServerDefineAgent({repository_root: repositoryRoot, gateway_socket: socket,
      connection_token: connectionToken, define_entrypoint_selected: true});
    await assert.rejects(secondDefineAgent.respond({mode: "discovery", user_input: "A second Define client",
      scope_confirmed: false}), /gateway\.consumer-already-attached/);
  } finally {
    await secondDefineAgent?.close();
    await humanClient?.close();
    await agent.close();
    await gateway.close();
    rmSync(directory, {recursive: true, force: true});
  }
});
