"""Independent synthetic/read-only review; never runs Mapper or private copy."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest

REPO = Path("/home/vlad_/projects/CyberAlchemy-lab")
BASE = REPO / "implementation/lab-runtime/local-host/mapper-only-docker-release-0001"
EVIDENCE = Path(__file__).resolve().parent
FREEZE = "e358a9cc908fb69514a15985b776f0a36306adaf77916c12a85a3069d9feb7cd"

def verify():
    raw = (BASE / "freeze.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != FREEZE:
        raise RuntimeError("FREEZE_DRIFT")
    rows = json.loads(raw)["file_bindings"]
    for row in rows:
        raw = (BASE / row["path"]).read_bytes()
        if len(raw) != row["size"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise RuntimeError("MEMBER_DRIFT")
    return len(rows)

verify()
sys.path.insert(0, str(BASE))
import controller as c
import docker_protocol as p
import test_release_static as t
suite = unittest.defaultTestLoader.loadTestsFromModule(t)
result = unittest.TextTestRunner(verbosity=1).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)

observations = {}
selection = c.trusted_selection()
args = c.docker_create_argv(selection, label=t.LABEL)
with tempfile.TemporaryDirectory(prefix="mapper-review-terminal-") as root:
    evidence = Path(root)
    terminal = p.reconcile_once(t.FakeDocker(), args, image=c.IMAGE, label=t.LABEL,
                                name=t.NAME, evidence_dir=evidence)
    raw = (evidence / "terminal.json").read_bytes()
    calculated = c.sha(c.canonical(terminal))
    if terminal["overall"] != "PASS" or c.sha(raw) == calculated:
        raise RuntimeError("TERMINAL_COUNTEREXAMPLE_NOT_REPRODUCED")
    try:
        c.bounded_nofollow_bytes(evidence / "terminal.json", calculated, 1024 * 1024)
    except ValueError as error:
        observations["R01"] = {
            "genuine_fake_protocol_terminal": "PASS",
            "actual_terminal_sha256": c.sha(raw),
            "controller_calculated_sha256": calculated,
            "controller_gate": str(error),
            "output_validation_reached": False,
        }
    else:
        raise RuntimeError("EXPECTED_TERMINAL_DIGEST_REFUSAL")

# Exactly the selected real CLI read-only absent response is fed back into
# the production parser. No create/start/remove method can execute here.
import subprocess
class CapturedAbsent(p.SubprocessDocker):
    def _run(self, args, *, deadline):
        return subprocess.CompletedProcess(args, 1,
            (EVIDENCE / "absent.stdout").read_bytes(),
            (EVIDENCE / "absent.stderr").read_bytes())
try:
    CapturedAbsent().absent("0" * 64, deadline=time.monotonic() + 10)
except p.DockerCommandError as error:
    observations["R02"] = {
        "selected_cli_absence_rejected": True,
        "returncode": error.returncode,
        "stdout_sha256": c.sha((EVIDENCE / "absent.stdout").read_bytes()),
        "stderr_sha256": c.sha((EVIDENCE / "absent.stderr").read_bytes()),
        "no_mutating_docker_call": True,
    }
else:
    raise RuntimeError("EXPECTED_ABSENCE_COUNTEREXAMPLE")
print(json.dumps({"inherited_tests":result.testsRun,"inherited_pass":True,
                  "observations":observations,"optimized":sys.flags.optimize,
                  "members_pre_post":verify(),"private_archive_read":False,
                  "mapper_effect":False},sort_keys=True))
