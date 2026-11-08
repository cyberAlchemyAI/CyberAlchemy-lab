import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {createRequire} from "node:module";
import {execFileSync} from "node:child_process";
import {createHash} from "node:crypto";
import test from "node:test";
import {acceptsInterfaceVersion, decodeInterfaceVersionPolicy, INTERFACE_VERSION_POLICY_SCHEMA, INTERFACE_VERSION_POLICY_DEFINITION_SHA256} from "../../src/typed-backend/interface-version-policy.ts";
import {renderInterfaceVersionPolicy} from "../../src/generation/interface-version-policy-source.ts";
import {decodeBody} from "../../src/input/project-model.ts";

const root = path.resolve(import.meta.dirname, "../../../..");
const policy = (provider_version = "1.2.0", mode: "exact" | "backward" = "backward") => ({schema_version: INTERFACE_VERSION_POLICY_SCHEMA, mode, direction: "consumer-to-provider" as const, provider_version});
const invalid: unknown[] = [null, undefined, 1, 1n, true, {}, [], "", "1", "1.2", "1.2.3.4", "01.2.3", "1.02.3", "1.2.03", "-1.2.3", "1.2.-3", "+1.2.3", "1.2.3\n", "1.2.3\r\n", " 1.2.3", "1.2.3 ", "１.2.3", "1.2.3-rc.1", "1.2.3+build", "^1.2.3", "1.*.0", "1.1e2.0", "1." + "9".repeat(65) + ".0"];

// Independent integer-tuple oracle: production compares canonical decimal strings.
const oracle = (provider: string, consumer: string, exact = false) => {
  const p = provider.split(".").map(BigInt), c = consumer.split(".").map(BigInt);
  if (exact) return p.every((n, i) => n === c[i]);
  return p[0] === c[0] && (p[1]! > c[1]! || p[1] === c[1] && p[2]! >= c[2]!);
};

function native(t: any, sources: Readonly<Record<string, string>>) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "ds-interface-policy-"));
  t.after(() => fs.rmSync(temp, {recursive: true, force: true}));
  for (const [name, source] of Object.entries(sources)) fs.writeFileSync(path.join(temp, name + ".ts"), source);
  const chain = JSON.parse(fs.readFileSync(path.resolve(root, "../../toolchains/node-typescript/toolchain.json"), "utf8"));
  const image = nativeToolchainImage(chain.container_image);
  execFileSync("docker", ["run", "--rm", "--pull", "never", "--network", "none", "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--user", `${process.getuid!()}:${process.getgid!()}`, "--mount", `type=bind,source=${temp},target=${temp}`, "--workdir", temp, image, "tsc", "--ignoreConfig", "--strict", "--noUncheckedIndexedAccess", "--declaration", "--target", "ES2022", "--module", "commonjs", "--outDir", path.join(temp, "js"), ...Object.keys(sources).map(name => path.join(temp, name + ".ts"))], {stdio: "pipe"});
  const require = createRequire(import.meta.url);
  return (name: string) => require(path.join(temp, "js", name + ".js"));
}

test("selected policy is definition-bound, closed, owned and frozen", () => {
  const bytes = fs.readFileSync(path.join(root, "development/reconciliation-v1/profile-compiler-reconciliation/interface-version-policy-contract.json"));
  assert.equal(createHash("sha256").update(bytes).digest("hex"), INTERFACE_VERSION_POLICY_DEFINITION_SHA256);
  const source = policy(), decoded = decodeInterfaceVersionPolicy(source);
  assert.deepEqual(decoded, source); assert.notEqual(decoded, source); assert.ok(Object.isFrozen(decoded));
  source.provider_version = "9.9.9"; assert.equal(decoded.provider_version, "1.2.0");
  assert.deepEqual(decodeInterfaceVersionPolicy(Object.assign(Object.create(null), policy())), policy());
  for (const mutation of [{schema_version: "future"}, {mode: "same-major"}, {direction: "provider-to-consumer"}, {extra: true}, {provider_version: "1"}]) assert.throws(() => decodeInterfaceVersionPolicy({...policy(), ...mutation}), {code: "MTCLI_INTERFACE_VERSION_POLICY"});
});

test("policy objects and consumer versions never evaluate ordinary getters or coercion", () => {
  let calls = 0;
  const hostile = {toString() {calls++; return "1.2.0";}, [Symbol.toPrimitive]() {calls++; return "1.2.0";}};
  for (const consumer of [...invalid, hostile, new String("1.2.0"), Symbol("1.2.0")]) assert.equal(acceptsInterfaceVersion(policy(), consumer), false);
  const getter = {...policy()}; Object.defineProperty(getter, "provider_version", {get() {calls++; return "1.2.0";}, enumerable: true});
  const hidden = {...policy()}; Object.defineProperty(hidden, "direction", {value: "consumer-to-provider", enumerable: false});
  for (const value of [getter, hidden, {...policy(), [Symbol("extra")]: true}, Object.create(policy()), {...policy(), provider_version: hostile}, [], null]) assert.throws(() => decodeInterfaceVersionPolicy(value), {code: "MTCLI_INTERFACE_VERSION_POLICY"});
  assert.equal(calls, 0);
});

test("direction, numeric ordering, exact mode and precision remain separate", () => {
  const versions: string[] = [];
  for (let major = 0; major < 4; major++) for (let minor = 0; minor < 4; minor++) for (let patch = 0; patch < 4; patch++) versions.push(`${major}.${minor}.${patch}`);
  versions.push("1.10.0", "1.2.10", "1.9007199254740992.0", "1.9007199254740993.0", "1.0." + "9".repeat(64));
  for (const provider of versions) for (const consumer of versions) for (const mode of ["exact", "backward"] as const) assert.equal(acceptsInterfaceVersion(policy(provider, mode), consumer), oracle(provider, consumer, mode === "exact"), `${mode}:${provider}:${consumer}`);
  assert.equal(acceptsInterfaceVersion(policy(), "1.3.0"), false);
  assert.equal(acceptsInterfaceVersion(policy("1.3.0"), "1.2.0"), true);
  const max = "9".repeat(64); assert.equal(acceptsInterfaceVersion(policy(`${max}.${max}.${max}`), `${max}.${max}.${max}`), true);
});

test("standalone generated policy compiles and matches independent native outcomes", t => {
  const providers = ["1.2.0", "1.10.0", "1.2.9007199254740993", "0.0.0"];
  const sources = Object.fromEntries(providers.flatMap((v, i) => ["backward", "exact"].map(mode => [`p${i}${mode}`, renderInterfaceVersionPolicy(policy(v, mode as "exact" | "backward"))])));
  assert.equal(sources.p0backward, renderInterfaceVersionPolicy(policy()));
  const load = native(t, sources);
  for (const [i, provider] of providers.entries()) for (const mode of ["backward", "exact"] as const) {
    const module = load(`p${i}${mode}`); assert.ok(Object.isFrozen(module.versionPolicy));
    assert.equal(module.versionPolicy.definition_sha256, INTERFACE_VERSION_POLICY_DEFINITION_SHA256);
    for (const consumer of [...providers, "1.0.0", "1.2.1", "1.3.0", "1.2.9007199254740992", "2.0.0"]) assert.equal(module.acceptsVersion(consumer), oracle(provider, consumer, mode === "exact"));
    for (const consumer of invalid) assert.equal(module.acceptsVersion(consumer), false);
    let calls = 0; assert.equal(module.acceptsVersion({toString() {calls++; return provider;}}), false); assert.equal(calls, 0);
  }
});

test("native-compiling mutants expose direction, major, patch, ordering and grammar changes", t => {
  const original = renderInterfaceVersionPolicy(policy("1.10.2"));
  const mutations: Record<string, string> = {
    reversed: original.replace("return order > 0", "return order < 0"),
    major: original.replace("if (consumer[0] !== provider[0]) return false;", ""),
    patch: original.replace("index < 3", "index < 2"),
    lexical: original.replace("left.length === right.length", "true"),
    equality: original.replace("  return true;", "  return false;"),
    whitespace: original.replace(".exec(consumerVersion)", ".exec(consumerVersion.trim())").replace("!match || match[0] !== consumerVersion", "!match"),
    leadingZero: original.replaceAll("0|[1-9][0-9]{0,63}", "[0-9]{1,64}"),
  };
  for (const source of Object.values(mutations)) assert.notEqual(source, original);
  const load = native(t, {original, ...mutations});
  const witnesses: Record<string, [string, boolean]> = {reversed: ["1.9.0", true], major: ["2.9.0", false], patch: ["1.10.3", false], lexical: ["1.9.0", true], equality: ["1.10.2", true], whitespace: ["1.10.2\n", false], leadingZero: ["1.01.0", false]};
  for (const [name, [consumer, expected]] of Object.entries(witnesses)) {assert.equal(load("original").acceptsVersion(consumer), expected); assert.notEqual(load(name).acceptsVersion(consumer), expected, name);}
});

test("generated declarations preserve literal policy identity and readonly data", t => {
  native(t, {policy: renderInterfaceVersionPolicy(policy()), consumer: `import {versionPolicy, acceptsVersion} from './policy';
const direction: 'consumer-to-provider' = versionPolicy.direction;
const mode: 'backward' = versionPolicy.mode;
const version: '1.2.0' = versionPolicy.provider_version;
const result: boolean = acceptsVersion('1.0.0');
// @ts-expect-error descriptor is readonly
versionPolicy.mode = 'exact';
// @ts-expect-error direction cannot be reversed
const wrong: 'provider-to-consumer' = versionPolicy.direction;
void [direction, mode, version, result, wrong];
`});
});

test("legacy CLI grammar and factory same-major fixture are not reinterpreted", async () => {
  const body = {description: "legacy", boundary_kind: "internal", version: "1", compatibility: "backward", operations: [{operation_id: "find", operation_ref: "commerce:find", request: [], result: []}]};
  assert.equal(decodeBody("Interface", body).version, "1");
  assert.throws(() => decodeBody("Interface", {...body, version: "1.2.0"}), {code: "MTCLI_INTERFACE_VERSION"});
  const {evaluateVersionedInterface} = await import("../../../architecture-conformance/families/versioned-interface-boundary/evaluator/evaluate-interface.ts");
  const {settlementInterfaceDescriptor, settlementInterfaceObservation} = await import("../../../architecture-conformance/families/versioned-interface-boundary/fixtures/settlement-interface.ts");
  const observed = settlementInterfaceObservation();
  assert.equal(observed.compatibility_checks.find(c => c.consumer_version === "1.3.0")?.accepted, true);
  assert.equal(evaluateVersionedInterface(settlementInterfaceDescriptor, observed).verdict, "pass");
  assert.equal(acceptsInterfaceVersion(policy(), "1.3.0"), false);
});

import {nativeToolchainImage} from '../helpers/native-toolchain-image.ts';
