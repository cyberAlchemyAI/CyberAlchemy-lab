import {createHash} from "node:crypto";
import {closeSync, existsSync, mkdirSync, openSync, rmSync, writeFileSync} from "node:fs";
import {basename, isAbsolute, relative, resolve, sep} from "node:path";
import {spawnSync} from "node:child_process";

function digest(value) {
  return createHash("sha256").update(JSON.stringify(value)).digest("hex");
}

function within(parent, child) {
  const rel = relative(resolve(parent), resolve(child));
  return rel === "" || (!rel.startsWith(`..${sep}`) && rel !== ".." && !isAbsolute(rel));
}

function normalizePath(value) {
  return String(value).replaceAll("\\", "/").replace(/^\.\//, "");
}

function allowed(path, allowlist) {
  const normalized = normalizePath(path);
  return allowlist.some((entry) => normalized === entry || normalized.startsWith(`${entry}/`));
}

function defaultCommandRunner({cwd, args}) {
  const result = spawnSync("git", args, {cwd, encoding: "utf8", shell: false});
  return {status: result.status, stdout: result.stdout ?? "", stderr: result.stderr ?? ""};
}

function requireSuccess(result, operation, {trim = false} = {}) {
  if (!result || result.status !== 0) throw new Error(`${operation} failed: ${result?.stderr?.trim() || "unknown git error"}`);
  const output = String(result.stdout ?? "");
  return trim ? output.trim() : output;
}

export function createVariantWorkspaceFactory({repository_root, workspace_root, command_runner = defaultCommandRunner} = {}) {
  if (!repository_root || !workspace_root) throw new TypeError("repository_root and workspace_root are required");
  const repositoryRoot = resolve(repository_root);
  const workspaceRoot = resolve(workspace_root);
  if (repositoryRoot === workspaceRoot || within(repositoryRoot, workspaceRoot) || within(workspaceRoot, repositoryRoot)) {
    throw new TypeError("workspace_root must be a dedicated directory outside the source repository");
  }
  mkdirSync(workspaceRoot, {recursive: true});
  const lockPath = resolve(workspaceRoot, ".single-writer.lock");
  let active = null;

  function prepare({baseline_ref, target_ref, technique_refs = [], mutation_allowlist = []} = {}) {
    if (!baseline_ref || !target_ref) throw new TypeError("baseline_ref and target_ref are required");
    if (active !== null) return {ok: false, disposition: "busy", reason_codes: ["evolution.variant-writer-active"], authority_effect: "none"};
    let lock;
    try {
      lock = openSync(lockPath, "wx", 0o600);
    } catch (error) {
      if (error?.code === "EEXIST") return {ok: false, disposition: "busy", reason_codes: ["evolution.variant-writer-active"], authority_effect: "none"};
      throw error;
    }
    const allowlist = [...new Set(mutation_allowlist.map(normalizePath).filter(Boolean))].sort();
    if (allowlist.length === 0) {
      closeSync(lock);
      rmSync(lockPath, {force: true});
      throw new TypeError("A non-empty mutation_allowlist is required");
    }
    const workspaceId = `variant-${digest({baseline_ref, target_ref, technique_refs: [...technique_refs].sort(), mutation_allowlist: allowlist}).slice(0, 24)}`;
    const workspacePath = resolve(workspaceRoot, workspaceId);
    if (!within(workspaceRoot, workspacePath) || basename(workspacePath) !== workspaceId || existsSync(workspacePath)) {
      closeSync(lock);
      rmSync(lockPath, {force: true});
      throw new Error("Variant workspace target is unsafe or already exists");
    }
    try {
      requireSuccess(command_runner({cwd: repositoryRoot, args: ["worktree", "add", "--detach", workspacePath, baseline_ref]}), "git worktree add");
      writeFileSync(lock, JSON.stringify({workspace_id: workspaceId, workspace_path: workspacePath, baseline_ref, target_ref}), "utf8");
      active = {lock, workspaceId, workspacePath, baselineRef: baseline_ref, targetRef: target_ref, allowlist};
      return Object.freeze({ok: true, disposition: "prepared", workspace_id: workspaceId, workspace_path: workspacePath, mutation_allowlist: allowlist, authority_effect: "none"});
    } catch (error) {
      closeSync(lock);
      rmSync(lockPath, {force: true});
      throw error;
    }
  }

  function inspect() {
    if (active === null) return {ok: false, disposition: "no-active-workspace", reason_codes: ["evolution.variant-workspace-missing"], authority_effect: "none"};
    const output = requireSuccess(command_runner({cwd: active.workspacePath, args: ["status", "--porcelain=v1", "--untracked-files=all"]}), "git status");
    const changedPaths = output.split("\n").filter(Boolean).map((line) => normalizePath(line.slice(3))).sort();
    const violations = changedPaths.filter((path) => !allowed(path, active.allowlist));
    return Object.freeze({ok: violations.length === 0, disposition: violations.length === 0 ? "within-allowlist" : "blocked", changed_paths: changedPaths, violations, reason_codes: violations.length === 0 ? [] : ["evolution.variant-mutation-outside-allowlist"], authority_effect: "none"});
  }

  function finalize() {
    const assessment = inspect();
    if (!assessment.ok) return assessment;
    const head = requireSuccess(command_runner({cwd: active.workspacePath, args: ["rev-parse", "HEAD"]}), "git rev-parse", {trim: true});
    const diff = requireSuccess(command_runner({cwd: active.workspacePath, args: ["diff", "--binary", "HEAD", "--"]}), "git diff");
    return Object.freeze({ok: true, disposition: "finalized", workspace_id: active.workspaceId, workspace_path: active.workspacePath, baseline_ref: active.baselineRef, target_ref: active.targetRef, changed_paths: assessment.changed_paths, source_tree_digest: digest({head, diff}), authority_effect: "none"});
  }

  function release({remove_worktree = false} = {}) {
    if (active === null) return {ok: true, disposition: "already-released", authority_effect: "none"};
    const released = active;
    try {
      if (remove_worktree) requireSuccess(command_runner({cwd: repositoryRoot, args: ["worktree", "remove", released.workspacePath]}), "git worktree remove");
    } finally {
      closeSync(released.lock);
      rmSync(lockPath, {force: true});
      active = null;
    }
    return Object.freeze({ok: true, disposition: "released", workspace_id: released.workspaceId, removed: remove_worktree, authority_effect: "none"});
  }

  return Object.freeze({prepare, inspect, finalize, release, inspectFactory: () => ({workspace_root: workspaceRoot, active_workspace_id: active?.workspaceId ?? null, lock_present: existsSync(lockPath), authority_effect: "none"})});
}
