"""Run the selected current-family non-Session API units with retained evidence.

The seven Session operations belong to the separate T03 learning sequence.
This runner covers the other 27 operations from the exact selection plan.
"""

import argparse
import hashlib
import json
import os
import signal
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PLAN = ROOT / "docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/common-all34-selection-0278/selection-plan.json"
ORDER = (
    "base:all",
    "fixture:challenge.submit",
    "fixture:classification.prepare",
    "fixture:failure.assess",
    "fixture:installation.execute",
    "fixture:package.export",
    "fixture:proposal.review",
    "fixture:release.prepare",
    "member:action-governance",
    "member:ontology",
    "member:resolution",
    "member:workflow",
    "transfer:files",
    "transfer:import",
    "transfer:typed",
)
API76 = "product/lab/release-candidates/v1/interface/api-integration-v76-current-repairs-0001"


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path, value):
    raw = (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def stop_group(pid):
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run(args):
    installed = Path(args.installed_repository).absolute()
    output = Path(args.output).absolute()
    need(installed.is_dir() and not installed.is_symlink(), "installed repository required")
    need(not output.exists() and not output.is_symlink(), "fresh output directory required")
    need(output.parent.is_dir() and not any(p.is_symlink() for p in output.parents), "unlinked output parent required")
    need(not output.is_relative_to(ROOT) and not output.is_relative_to(installed.parent.parent),
         "private evidence must be outside the repository and installation")
    need(all(len(pin) == 64 and all(c in "0123456789abcdef" for c in pin)
             for pin in (args.package_sha256, args.source_sha256, args.profile_sha256)),
         "exact lowercase package/source/profile digests required")
    package = installed / ".cal-package-manifest.json"
    need(package.is_file() and not package.is_symlink() and digest(package) == args.package_sha256,
         "selected installed package manifest differs")
    manifest = json.loads(package.read_bytes())
    need(manifest["entrypoint"]["api_directory"] == API76
         and manifest["binding_paths"]["api.source"] == API76 + "/source-manifest.json"
         and manifest["binding_paths"]["api.profile"] == API76 + "/contract-profile.json",
         "installed API76 entrypoint/source/profile selection differs")
    launcher = installed / "implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python"
    caller = installed / "implementation/lab-runtime/local-host/t17-current-common-caller-0001/caller.py"
    api = installed / manifest["entrypoint"]["api_directory"]
    deps = installed.parent / ".cal-runtime/native/deps"
    plan = installed / PLAN.relative_to(ROOT)
    profile = api / "contract-profile.json"
    source = api / "source-manifest.json"
    need(all(p.is_file() and not p.is_symlink() for p in (launcher, caller, plan, profile, source)),
         "selected installed inputs required")
    need(deps.is_dir() and not deps.is_symlink(), "installed native dependencies required")
    need(digest(profile) == args.profile_sha256, "installed profile digest differs")
    need(digest(source) == args.source_sha256, "installed source digest differs")
    selected = json.loads(plan.read_bytes())
    base = [key for key in selected["units"] if key.startswith("base:")]
    other = [key for key in selected["units"] if not key.startswith("base:") and key != "member:Source8-lifecycle"]
    need(len(base) == 8 and set(other) == set(ORDER[1:]), "selected non-Session unit set differs")
    expected = set()
    for key in base + other:
        expected.update(selected["units"][key]["operations"])
    need(len(expected) == 27, "selected non-Session operation set differs")
    output.mkdir(mode=0o700)
    originals = output / "originals"
    originals.mkdir(mode=0o700)
    write_once(output / "SELECTION.json", {
        "schema_version": "lab-current-non-session-api-selection/v1",
        "installed_repository": str(installed),
        "selection_plan_sha256": digest(plan),
        "caller_sha256": digest(caller),
        "package_sha256": args.package_sha256,
        "source_sha256": args.source_sha256,
        "profile_sha256": args.profile_sha256,
        "units": list(ORDER),
        "expected_operations": sorted(expected),
        "session_operations_excluded": selected["units"]["member:Source8-lifecycle"]["operations"],
        "authority_effect": "none",
    })
    observed = set()
    completed = []
    for index, unit in enumerate(ORDER, 1):
        label = f"{index:02d}-{unit.replace(':', '-')}"
        result_file = output / f"{label}.json"
        command = [str(launcher), "-I", "-B", "-S", str(caller),
                   "--api", str(api), "--source-sha256", args.source_sha256,
                   "--profile-sha256", args.profile_sha256, "--unit", unit,
                   "--output", str(result_file), "--deps", str(deps),
                   "--retention-root", str(originals)]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        with (output / f"{label}.stdout.log").open("xb") as stdout, (output / f"{label}.stderr.log").open("xb") as stderr:
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                       env=env, start_new_session=True)
            try:
                return_code = process.wait(timeout=args.timeout_seconds)
            except subprocess.TimeoutExpired as error:
                stop_group(process.pid)
                process.wait(timeout=30)
                write_once(output / "FAILED-RETAINED.json", {"unit": unit, "failure": "timeout",
                            "timeout_seconds": args.timeout_seconds, "completed_units": completed,
                            "authority_effect": "none"})
                raise RuntimeError(f"{unit} exceeded timeout") from error
            except BaseException:
                stop_group(process.pid)
                process.wait(timeout=30)
                if not (output / "FAILED-RETAINED.json").exists():
                    write_once(output / "FAILED-RETAINED.json", {"unit": unit, "failure": "interrupted",
                                "completed_units": completed, "authority_effect": "none"})
                raise
            if return_code != 0:
                stop_group(process.pid)
        if not result_file.is_file() or result_file.is_symlink():
            write_once(output / "FAILED-RETAINED.json", {"unit": unit, "failure": "no-result",
                        "exit_code": return_code, "completed_units": completed, "authority_effect": "none"})
            raise RuntimeError(f"{unit} produced no result")
        result = json.loads(result_file.read_bytes())
        current = set(result.get("coverage", {}))
        required = (set().union(*(set(selected["units"][name]["operations"]) for name in base))
                    if unit == "base:all" else set(selected["units"][unit]["operations"]))
        pinned = (all(p.is_file() and not p.is_symlink() for p in (package, source, profile))
                  and digest(package) == args.package_sha256
                  and digest(source) == args.source_sha256
                  and digest(profile) == args.profile_sha256)
        valid = (pinned and return_code == 0 and result.get("result") == "PASS" and result.get("unit") == unit
                 and result.get("source_sha256") == args.source_sha256
                 and result.get("profile_sha256") == args.profile_sha256 and current == required
                 and all(row.get("positive", 0) >= 1 and row.get("negative", 0) >= 1
                         for row in result["coverage"].values()))
        if not valid:
            write_once(output / "FAILED-RETAINED.json", {"unit": unit, "failure": "terminal-check",
                        "exit_code": return_code, "result_sha256": digest(result_file),
                        "completed_units": completed, "authority_effect": "none"})
            raise RuntimeError(f"{unit} terminal result differed")
        observed.update(current)
        completed.append({"unit": unit, "result_sha256": digest(result_file),
                          "coverage": result["coverage"], "exit_code": return_code})
        write_once(output / f"{label}.PASS.json", completed[-1])
    need(observed == expected, "final non-Session coverage differs")
    final = {"schema_version": "lab-current-non-session-api-result/v1", "result": "PASS",
             "source_sha256": args.source_sha256, "profile_sha256": args.profile_sha256,
             "selection_sha256": digest(output / "SELECTION.json"),
             "operations": sorted(observed), "operation_count": 27,
             "units": completed, "all34_qualified": False, "authority_effect": "none"}
    write_once(output / "RESULT.json", final)
    return final


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("installed-repository", "package-sha256", "source-sha256", "profile-sha256", "output"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    values = parser.parse_args()
    need(60 <= values.timeout_seconds <= 14400, "bounded unit timeout required")
    print(json.dumps(run(values), sort_keys=True), flush=True)
