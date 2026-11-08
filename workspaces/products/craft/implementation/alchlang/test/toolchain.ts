import {existsSync} from "node:fs";
import path from "node:path";
import { defaultDomainSpecPackageRoot } from "../src/domainspec-cli.js";

const packageRoot = path.resolve(import.meta.dirname, "..");

function tool(name: "tsx" | "tsc", explicit?: string): string {
  if (explicit) return path.resolve(explicit);
  const local = path.resolve(packageRoot, `node_modules/.bin/${name}`);
  return existsSync(local) ? local : path.resolve(defaultDomainSpecPackageRoot(), `../node_modules/.bin/${name}`);
}

export function testTsx(): string {
  return tool("tsx", process.env.ALCHLANG_TEST_TSX);
}

export function testTypeScript(): string {
  return tool("tsc", process.env.ALCHLANG_TEST_TYPESCRIPT);
}
