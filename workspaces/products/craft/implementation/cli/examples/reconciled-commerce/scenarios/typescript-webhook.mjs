import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const target = path.resolve(process.argv[2] ?? "");
const route = process.argv[3] ?? "/webhook";
assert.match(route, /^\/[A-Za-z0-9/_-]+$/);
const dist = path.join(target, "dist");
const inboundCandidates = fs.readdirSync(dist, { recursive: true })
  .map(entry => String(entry).split(path.sep).join("/"))
  .filter(entry => entry.endsWith("/providers/reference/inbound-http.js") || entry === "providers/reference/inbound-http.js");
assert.equal(inboundCandidates.length, 1, `expected one emitted inbound provider, observed:${inboundCandidates.join(",")}`);
const { createWebhookServer } = await import(pathToFileURL(path.join(dist, inboundCandidates[0])));
const body = "domainspec-installed-webhook";
const secret = "installed-reference-secret";
let invocations = 0;
const server = createWebhookServer("127.0.0.1:0", secret, async observed => {
  assert.equal(observed, body);
  invocations += 1;
});

await new Promise((resolve, reject) => {
  server.once("error", reject);
  server.listen(0, "127.0.0.1", resolve);
});
try {
  const address = server.address();
  assert.notEqual(address, null);
  assert.equal(typeof address, "object");
  const url = `http://127.0.0.1:${address.port}${route}`;
  const invalid = await fetch(url, { method: "POST", headers: { "x-domainspec-signature": "0".repeat(64) }, body });
  assert.equal(invalid.status, 401);
  assert.equal(invocations, 0);
  const signature = createHmac("sha256", secret).update(body).digest("hex");
  const valid = await fetch(url, { method: "POST", headers: { "x-domainspec-signature": signature }, body });
  assert.equal(valid.status, 202);
  assert.equal(invocations, 1);
  process.stdout.write(`${JSON.stringify({ language: "typescript", startup: "http-listener", invalid_status: invalid.status, valid_status: valid.status, handler_invocations: invocations, result: "pass" })}\n`);
} finally {
  await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
}
