"""Exact-name parser probes. No Docker/Source dispatch."""
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from unittest import mock

C = Path(__file__).resolve().parent.parent / "source-only-docker-0006"
raw = (C / "controller.py").read_bytes()
if hashlib.sha256(raw).hexdigest() != "5a409b3833225881ed4d3c7c803251f4b5284004fafddc12c2a392aa919bfa01":
    raise RuntimeError("selected source drift")
spec = importlib.util.spec_from_file_location("reviewed_controller", C / "controller.py")
c = importlib.util.module_from_spec(spec)
exec(compile(raw, str(C / "controller.py"), "exec"), c.__dict__)
n = c.NAME.encode()
cases = [
    ("lower_prefix_exact_name", 1, b"[]\n", b"error: no such object: " + n, True),
    ("upper_prefix_exact_name", 1, b"[]\n", b"ERROR: NO SUCH OBJECT: " + n, True),
    ("container_prefix_exact_name", 1, b"", b"Error: No Such Container: " + n, True),
    ("whitespace_exact_name", 1, b" [] \n", b"  error:\t no  such object: " + n + b"\n", True),
    ("different_object_suffix", 1, b"[]", b"error: no such object: " + n + b"-other", False),
    ("different_object_case", 1, b"[]", b"error: no such object: " + n.upper(), False),
    ("transport_prefix", 1, b"[]", b"daemon unavailable; error: no such object: " + n, False),
    ("wrong_exit", 2, b"[]", b"error: no such object: " + n, False),
    ("partial_stdout", 1, b"partial", b"error: no such object: " + n, False),
    ("extra_error_line", 1, b"[]", b"error: no such object: " + n + b"\npermission denied", False),
]
observations = []
for label, code, stdout, stderr, expected in cases:
    with mock.patch.object(c, "cli", return_value=subprocess.CompletedProcess([], code, stdout, stderr)):
        try:
            value = c.inspected(c.NAME)
            accepted = value is None
        except ValueError:
            accepted = False
    observations.append({"case": label, "accepted_absence": accepted,
                         "expected_absence": expected,
                         "matches_exact_name_contract": accepted == expected})
    if accepted != expected:
        raise RuntimeError("unexpected parser behavior")
if observations[5]["accepted_absence"] is not False:
    raise RuntimeError("wrong-case counterexample was not refused")
print(json.dumps({"schema": "independent-exact-name-parser-probes/v1",
                  "source_effect": "NOT_RUN",
                  "prior_defect_refused": True,
                  "observations": observations}, indent=2))
