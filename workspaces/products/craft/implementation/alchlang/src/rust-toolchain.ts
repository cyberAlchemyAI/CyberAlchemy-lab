import {cpSync, existsSync} from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";

const runtimeTemplate = fileURLToPath(new URL("./event-templates/rust-runtime/", import.meta.url));

export function installLockedRustRuntime(crateRoot: string): void {
  cpSync(path.join(runtimeTemplate, "Cargo.toml"), path.join(crateRoot, "Cargo.toml"));
  cpSync(path.join(runtimeTemplate, "Cargo.lock"), path.join(crateRoot, "Cargo.lock"));
}

export function rustToolchainLauncher(): string {
  let current = path.dirname(fileURLToPath(import.meta.url));
  while (!existsSync(path.join(current, "tools/toolchain/run"))) {
    const parent = path.dirname(current);
    if (parent === current) throw Error("ALCH_RUST_TOOLCHAIN_MISSING");
    current = parent;
  }
  return path.join(current, "tools/toolchain/run");
}
