import { existsSync, realpathSync } from "node:fs";
import { dirname, join, parse } from "node:path";
import { fileURLToPath } from "node:url";

/** Resolve the checkout's canonical implementation inputs from source or emitted code.
 * Emitted tools remain checkout-local; this does not make them a portable package. */
export function localImplRoot(moduleUrl: string): string {
  let candidate = dirname(fileURLToPath(moduleUrl));
  while (true) {
    if (existsSync(join(candidate, "spec/minted-project/project.schema.json")) &&
        existsSync(join(candidate, "tools/minted-project/compiler.ts")))
      return realpathSync(candidate);
    const parent = dirname(candidate);
    if (parent === candidate || candidate === parse(candidate).root) break;
    candidate = parent;
  }
  throw new Error("canonical local DomainSpec implementation root is unavailable");
}
