import { readFile } from "node:fs/promises";
import { dirname, isAbsolute, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { decodeFactoryRunRequestV1 } from "../codecs/decode-factory-run-request-v1.js";
import { inspectFactoryKitPackage } from "../kit/inspect-kit-package.js";
import { publishExpectedRedKit } from "../kit/publish-expected-red-kit.js";
import { executeFactoryRun } from "../pipeline/execute-factory-run.js";
import { planFactoryRun } from "../pipeline/plan-factory-run.js";
import { replayFactoryRun } from "../pipeline/replay-factory-run.js";
import { reproduceReferenceSuite } from "../pipeline/reproduce-reference-suite.js";
import { verifyFactoryRun } from "../pipeline/verify-factory-run.js";
import { fail } from "../shared/canonical.js";

const here = dirname(fileURLToPath(import.meta.url));
export const repositoryRoot = resolve(here, "../../../../../..");
const implementationRoot = resolve(repositoryRoot, "projects/domainspec-v2/impl");

const argument = (name: string): string | undefined => {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : undefined;
};
const required = (name: string): string => argument(name) ?? fail("FACTORY_CLI_ARGUMENT_MISSING", name);
const localPath = (value: string): string => isAbsolute(value) ? value : resolve(implementationRoot, value);
const loadRequest = async (value: string) => decodeFactoryRunRequestV1(
  JSON.parse(await readFile(localPath(value), "utf8")),
);
const loadKitPackage = async (value: string) =>
  JSON.parse(await readFile(localPath(value), "utf8"));

export const runFactoryCli = async (): Promise<unknown> => {
  const command = process.argv[2];
  if (command === "inspect") {
    const inspection = await inspectFactoryKitPackage(await loadKitPackage(required("--package")));
    return Object.freeze({
      result: inspection.result,
      readiness: inspection.readiness,
      provider_ref_count: inspection.provider_ref_count,
      authority_effect: "none",
    });
  }
  if (command === "init") {
    const inspection = await inspectFactoryKitPackage(await loadKitPackage(required("--package")));
    return publishExpectedRedKit({
      inspection,
      outputPath: localPath(required("--output")),
    });
  }
  if (command === "plan") {
    return planFactoryRun({ repositoryRoot, request: await loadRequest(required("--request")) });
  }
  if (command === "run") {
    const request = await loadRequest(required("--request"));
    const plan = await planFactoryRun({ repositoryRoot, request });
    return executeFactoryRun({ repositoryRoot, outputParent: localPath(required("--output")), plan });
  }
  if (command === "replay") return replayFactoryRun(localPath(required("--run")));
  if (command === "verify") return verifyFactoryRun(localPath(required("--run")));
  if (command === "reproduce") {
    return reproduceReferenceSuite({
      repositoryRoot,
      request: await loadRequest(required("--request")),
      outputRoot: localPath(required("--output")),
    });
  }
  return fail("FACTORY_CLI_COMMAND_UNKNOWN", command);
};

if (process.argv[1] !== undefined && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  runFactoryCli().then((result) => {
    process.stdout.write(`${JSON.stringify(result)}\n`);
  }).catch((error: unknown) => {
    const typed = error as { code?: string; message?: string };
    process.stderr.write(`${JSON.stringify({
      result: "block",
      code: typed.code ?? "FACTORY_UNEXPECTED_FAILURE",
      detail: typed.message ?? String(error),
      authority_effect: "none",
    })}\n`);
    process.exitCode = 1;
  });
}
