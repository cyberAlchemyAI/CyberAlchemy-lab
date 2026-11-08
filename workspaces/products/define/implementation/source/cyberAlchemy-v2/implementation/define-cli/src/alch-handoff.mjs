import {spawnSync} from "node:child_process";
import {lstatSync, mkdirSync, mkdtempSync, readFileSync, renameSync, rmSync, writeFileSync} from "node:fs";
import {dirname, join, resolve} from "node:path";

import {canonicalJson, canonicalize, digest} from "./canonical.mjs";
import {validateDefinitionPack} from "./session-runtime.mjs";
import {execute as executeCompiledHandoffReadiness} from "../generated/define-service/entries/AlchHandoffReadiness/app/function/behavior.mjs";

const REPAIR_MESSAGES = {
  "definition-pack": "the Definition Pack is not handoff-ready",
  "language-quality": "the reviewed language-quality evaluation is missing",
  "semantic-grounding": "semantic grounding must pass",
  "non-collapse": "non-collapse must pass",
  orthogonality: "orthogonality must pass",
  "output-target": "the output directory already exists",
};

export class DefineAlchHandoffError extends Error {
  constructor(focus, reasonCodes = []) {
    super(`Define compile blocked: ${REPAIR_MESSAGES[focus] ?? focus}.`);
    this.name = "DefineAlchHandoffError";
    this.code = `define-alch-handoff.${focus}`;
    this.repair_focus = focus;
    this.reason_codes = reasonCodes;
  }
}

function exists(path) {
  try {
    lstatSync(path);
    return true;
  } catch (error) {
    if (error?.code === "ENOENT") return false;
    throw error;
  }
}

function quoted(value) {
  return JSON.stringify(String(value).normalize("NFC"));
}

function conceptStatement(disposition) {
  if (disposition.disposition === "propose") return disposition.candidate_definition.normative_voice;
  if (disposition.disposition === "reuse") return `Reuse the reviewed definition reference ${disposition.definition_ref}.`;
  if (disposition.disposition === "specialize") return `Specialize ${disposition.base_definition_ref} within ${disposition.scope}.`;
  throw new DefineAlchHandoffError("definition-pack", [`pack.unrepresentable-disposition:${disposition.concept_id}`]);
}

function conceptMeaning(disposition) {
  if (disposition.disposition === "propose") return `${disposition.term}: ${disposition.candidate_definition.plain_language_voice}`;
  if (disposition.disposition === "reuse") return `${disposition.term}: reuse ${disposition.definition_ref}`;
  if (disposition.disposition === "specialize") return `${disposition.term}: specialize ${disposition.base_definition_ref} for ${disposition.scope}`;
  return disposition.term;
}

export function evaluateDefinitionPackAlchHandoff(pack, {output_target_new = true} = {}) {
  let validation = validateDefinitionPack(pack);
  if (pack && typeof pack === "object") {
    const {pack_id: packId, ...packMaterial} = pack;
    if (packId !== `definition-pack:${digest(packMaterial)}`) {
      validation = canonicalize({
        ...validation,
        valid: false,
        handoff_ready: false,
        session_state: "validation-blocked",
        reason_codes: [...new Set([...validation.reason_codes, "pack.identity-digest-mismatch"])].sort(),
      });
    }
  }
  const quality = pack?.language_quality_evaluation;
  const checks = quality?.checks ?? {};
  const structuralReasons = validation.reason_codes.filter((reason) => ![
    "pack.language-quality-must-pass",
    "pack.language-quality-evidence-required",
  ].includes(reason));
  const decision = executeCompiledHandoffReadiness({input: {
    pack_handoff_ready: structuralReasons.length === 0 && validation.open_question_count === 0,
    language_quality_present: Boolean(quality && pack?.language_scope && pack?.language_quality_evidence),
    semantic_grounding_pass: checks.semantic_grounding === "pass",
    non_collapse_pass: checks.non_collapse === "pass",
    orthogonality_pass: checks.orthogonality === "pass",
    output_target_new,
  }}, {});
  return canonicalize({...decision, pack_validation: validation});
}

export function renderDefinitionPackAlch(pack) {
  const decision = evaluateDefinitionPackAlchHandoff(pack);
  if (decision.status !== "ready") throw new DefineAlchHandoffError(decision.repair_focus, decision.pack_validation.reason_codes);
  const packDigest = digest(pack);
  const identity = packDigest.slice(0, 24).toUpperCase();
  const dispositions = [...pack.concept_dispositions].sort((left, right) => left.concept_id.localeCompare(right.concept_id));
  const axioms = dispositions.map((disposition, index) => [
    `axiom ReviewedConcept${String(index + 1).padStart(2, "0")}:`,
    `  ontology "ALCH-DEFINE-PACK-${identity}-CONCEPT-${String(index + 1).padStart(2, "0")}"`,
    `  meaning ${quoted(conceptMeaning(disposition))}`,
    `  statement ${quoted(conceptStatement(disposition))}`,
    "  subject domain",
    "  commitment taken-as-given",
  ].join("\n"));
  const source = [
    `domain definition-pack-${packDigest.slice(0, 16)}`,
    "profile semantic-contract-v1",
    "owner cyberalchemy-define-owner",
    "logic sfol-v1",
    "runtime node>=26.8.1",
    "",
    `# Candidate projection of exact source pack digest ${packDigest}.`,
    ...axioms.flatMap((axiom) => [axiom, ""]),
    "axiom DefinitionPackScope:",
    `  ontology "ALCH-DEFINE-PACK-${identity}-SCOPE"`,
    `  meaning ${quoted(`${pack.goal} for ${pack.consumer}`)}`,
    `  statement ${quoted(`Intent: ${pack.intent} Context: ${pack.context}`)}`,
    "  subject domain",
    "  commitment taken-as-given",
    "",
    "axiom CandidateProjectionHasNoAuthority:",
    `  ontology "ALCH-DEFINE-PACK-${identity}-NO-AUTHORITY"`,
    "  meaning \"This compiled Definition Pack remains candidate evidence.\"",
    "  statement \"Compilation cannot make a definition canonical or authorize implementation, effects, publication, or deployment.\"",
    "  subject domain",
    "  commitment taken-as-given",
    "",
    "intrinsic MatchReviewedLanguage:",
    `  ontology "ALCH-DEFINE-PACK-${identity}-MATCH-REVIEWED-LANGUAGE"`,
    "  meaning \"Match reviewed language as a complete normalized phrase.\"",
    "  operation contains-phrase",
    "  input record",
    "  output boolean",
    "",
    "invariant ReviewedLanguageDoesNotCollapseSubstrings:",
    `  ontology "ALCH-DEFINE-PACK-${identity}-NON-COLLAPSE"`,
    "  meaning \"Reviewed language is matched as complete phrases and never as substrings inside larger tokens.\"",
    "  grounded-by CandidateProjectionHasNoAuthority",
    "  intrinsic MatchReviewedLanguage",
    "  property phrase-non-collapse",
    "  violation \"DEFINE_PACK_LANGUAGE_COLLAPSE_DEFECT\"",
    "",
    "governed-by DefinitionPackCandidateConstitution:",
    `  constitution-ref ${quoted(pack.pack_id)}`,
    "  version \"1-candidate\"",
    "  status candidate",
    `  selector ${quoted(`profile:semantic-contract-v1/domain:definition-pack-${packDigest.slice(0, 16)}`)}`,
    "  adopted false",
    "  authority-effect none",
    "",
    "validation ReviewedLanguageConformance:",
    "  invariant ReviewedLanguageDoesNotCollapseSubstrings",
    "  method fixture",
    "  fixtures \"definition-pack.fixtures.json\"",
    "  claim finite-evidence-only",
    "",
  ].join("\n");
  const fixtures = dispositions.map((disposition, index) => ({
    name: `reviewed-concept-${String(index + 1).padStart(2, "0")}`,
    validation: "ReviewedLanguageConformance",
    operation: "contains-phrase",
    input: {text: conceptMeaning(disposition), phrase: disposition.term},
    expected: true,
  }));
  fixtures.push({
    name: "substring-non-collapse",
    validation: "ReviewedLanguageConformance",
    operation: "contains-phrase",
    input: {text: "A predefined runtime is not a Define request.", phrase: "define"},
    expected: true,
  });
  fixtures.push({
    name: "hostile-substring-does-not-match",
    validation: "ReviewedLanguageConformance",
    operation: "contains-phrase",
    input: {text: "A predefined runtime", phrase: "define"},
    expected: false,
  });
  return canonicalize({source, fixtures, pack_digest: packDigest, source_digest: digest(source)});
}

export function compileDefinitionPackToAlch(input, outputPath, options = {}) {
  const pack = input?.definition_pack ?? input;
  const output = resolve(outputPath);
  const decision = evaluateDefinitionPackAlchHandoff(pack, {output_target_new: !exists(output)});
  if (decision.status !== "ready") throw new DefineAlchHandoffError(decision.repair_focus, decision.pack_validation.reason_codes);
  const rendered = renderDefinitionPackAlch(pack);
  const parent = dirname(output);
  mkdirSync(parent, {recursive: true});
  const stage = mkdtempSync(join(parent, ".define-alch-handoff-"));
  const sourcePath = join(stage, "definition-pack.alch");
  const fixturePath = join(stage, "definition-pack.fixtures.json");
  const compiledPath = join(stage, "compiled");
  const localRepositoryRoot = resolve(import.meta.dirname, "../../..");
  const compilerPath = resolve(options.compiler_path ?? join(localRepositoryRoot, "language/capabilities/alchlang/plans/general-compiler-v1/implementation/dist/cli.js"));
  try {
    writeFileSync(sourcePath, rendered.source, {encoding: "utf8", flag: "wx", mode: 0o600});
    writeFileSync(fixturePath, `${canonicalJson(rendered.fixtures)}\n`, {encoding: "utf8", flag: "wx", mode: 0o600});
    const compilation = spawnSync(process.execPath, [compilerPath, "build", sourcePath, "--out", compiledPath], {
      cwd: localRepositoryRoot,
      encoding: "utf8",
      env: process.env,
    });
    if (compilation.status !== 0) throw new Error(`define-alch-handoff.compiler:${(compilation.stderr || compilation.stdout).trim()}`);
    const compilerResult = JSON.parse(compilation.stdout);
    const compilerManifestBytes = readFileSync(join(compiledPath, "manifest.json"));
    const receiptMaterial = canonicalize({
      schema_version: "cav2.definition-pack-alch-handoff/v1",
      pack_id: pack.pack_id,
      pack_digest: rendered.pack_digest,
      source_path: "definition-pack.alch",
      source_digest: rendered.source_digest,
      fixture_path: "definition-pack.fixtures.json",
      fixture_digest: digest(`${canonicalJson(rendered.fixtures)}\n`),
      compiled_root: "compiled",
      compiler_manifest_digest: digest(compilerManifestBytes),
      pipeline: ["definition-pack", "alch-source", "semantic-contract-ontology", "craft-project", "domainspec-compile", "runtime-projection", "fixture-validation"],
      language_quality: {semantic_grounding: "pass", non_collapse: "pass", orthogonality: "pass"},
      ontology_admitted: false,
      constitution_adopted: false,
      authority_effect: "none",
    });
    const receipt = canonicalize({...receiptMaterial, receipt_digest: digest(receiptMaterial)});
    writeFileSync(join(stage, "handoff-receipt.json"), `${canonicalJson(receipt)}\n`, {encoding: "utf8", flag: "wx", mode: 0o600});
    renameSync(stage, output);
    return canonicalize({ok: true, output, compiler: compilerResult, receipt, authority_effect: "none"});
  } catch (error) {
    rmSync(stage, {recursive: true, force: true});
    throw error;
  }
}
