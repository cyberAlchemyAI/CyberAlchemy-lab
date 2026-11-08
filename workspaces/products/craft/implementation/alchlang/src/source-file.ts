import { readFileSync } from "node:fs";
import path from "node:path";
import { CompilationRejected } from "./model.js";
import { parseDomainSource, type ParsedDomainSource } from "./parser.js";

export type AlchLangFileFormat = "canonical-alch" | "legacy-markdown";
export interface LoadedAlchLangSource extends ParsedDomainSource {
  source_path: string;
  file_format: AlchLangFileFormat;
}

function reject(code: string, sourcePath: string, message: string): never {
  throw new CompilationRejected([{ code, path: sourcePath, message }]);
}

export function loadAlchLangSource(sourcePath: string): LoadedAlchLangSource {
  const absolute = path.resolve(sourcePath);
  const rawExtension = path.extname(absolute);
  const extension = rawExtension.toLowerCase();
  if (rawExtension !== extension) reject("SOURCE_EXTENSION", absolute, "AlchLang file extensions are lowercase: .alch or legacy .md");
  if (extension !== ".alch" && extension !== ".md") {
    reject("SOURCE_EXTENSION", absolute, "AlchLang source must use .alch; .md is accepted only as a legacy fenced container");
  }
  const bytes = readFileSync(absolute, "utf8");
  if (bytes.startsWith("\uFEFF")) reject("SOURCE_ENCODING", absolute, "canonical UTF-8 source must not contain a byte-order mark");
  if (extension === ".alch" && bytes.includes("```")) reject("SOURCE_CONTAINER", absolute, ".alch files contain plain AlchLang and must not use Markdown fences");
  const parsed = parseDomainSource(bytes);
  if (extension === ".md" && parsed.source_kind !== "markdown-alchlang") reject("SOURCE_CONTAINER", absolute, "legacy .md input must contain exactly one fenced alchlang block");
  if (extension === ".alch" && parsed.source_kind !== "plain-alchlang") reject("SOURCE_CONTAINER", absolute, ".alch source did not parse as plain AlchLang");
  return { ...parsed, source_path: absolute, file_format: extension === ".alch" ? "canonical-alch" : "legacy-markdown" };
}
