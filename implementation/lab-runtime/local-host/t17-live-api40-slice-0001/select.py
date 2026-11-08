"""Select causal API40 coverage from one observed composite run."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[4]
LIVE = Path("implementation/lab-runtime/local-host/t06-api40-rebind-0001/RUN-LIVE-EFFECTS-0002.json")
DRIVER = Path("implementation/lab-runtime/local-host/t06-api40-rebind-0001/drive_effects_0002.py")
REVIEW = Path("implementation/lab-runtime/local-host/working/t06-api40-live-seven-call-independent-review-0001/REVIEW.md")
PINS = {
    LIVE: "7bac9d32cad2aa5081ede012ac3d70b0f139b7c166482638954c9a83902f7d5b",
    DRIVER: "ced8b82be6a6ca77562b1d900b7dca122e3e1ecefbd06e428a5e4c0bd50b7cec",
    REVIEW: "b99eb1ee7b2f79121c62f4d5dc50ecc10b98a983e8730644d0466d43a30bb830",
}
SOURCE = "45412c382dc0cc9c807dd2bf4ec67037c7ae58854fcbb42cb15a96f0f7f3a219"
PROFILE = "cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614"
SDK = "f123c4e02828c1c3f88dfc4b74adc3bdf1cc2919bc53df8ccf68e00ff677da1e"


def exact(path: Path, digest: str) -> bytes:
    path = path.absolute()
    for ancestor in (path, *path.parents):
        mode = ancestor.lstat().st_mode
        if stat.S_ISLNK(mode) or (ancestor == path and not stat.S_ISREG(mode)):
            raise ValueError("linked or nonregular evidence")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError("selected evidence differs")
    return raw


def classify(live: dict) -> dict:
    result = live["result"]
    observations = result["observations"]
    if not (live["status"] == result["status"] == "PASS" and
            live["process_exit_code"] == result["process_exit_code"] == 0 and
            live["source_manifest_sha256"] == SOURCE and live["profile_sha256"] == PROFILE and
            live["sdk_manifest_sha256"] == SDK and live["driver_sha256"] == PINS[DRIVER] and
            result["dispatch_operations_executed"] == len(observations) == 7 and
            result["events"][1]["catalog_operation_count"] == 34 and
            result["whole_API_qualified"] is False):
        raise ValueError("live composite origin or terminal differs")
    positive, inspection, negative = observations[2:5]
    if not ([(row["branch"], row["operation"]) for row in observations] ==
            [("base", "lab.status"), ("base", "catalog.get"),
             ("actions", "action.dispatch"), ("actions", "operation.inspect"),
             ("actions", "action.dispatch"), ("governance", "capability.adoption.prepare"),
             ("governance", "operation.inspect")] and
            positive["case"] == "positive-owned-counter" and positive["reply_kind"] == "result" and
            positive["posture"] == inspection["posture"] == "completed" and
            negative["case"] == "wrong-scope-refusal" and negative["reply_kind"] == "error" and
            negative["code"] == "unauthorized" and
            positive["counter_after"] == inspection["counter_after"] == negative["counter_after"] == 1 and
            len({positive["request_sha256"], negative["request_sha256"]}) == 2):
        raise ValueError("Action causal sequence differs")
    return {
        "schema_version": "lab-T17-api40-live-coverage-slice/v1",
        "api_source_sha256": SOURCE, "api_profile_sha256": PROFILE,
        "sdk_manifest_sha256": SDK,
        "live_receipt_sha256": PINS[LIVE], "driver_sha256": PINS[DRIVER],
        "common_dispatcher_operation_count": 34,
        "actual_dispatches": 7,
        "qualified_operation_slice": ["action.dispatch"],
        "positive_and_causal_negative_same_lifetime": True,
        "unchanged_owned_effect_counter": 1,
        "other_six_calls_are_partial_coverage_only": True,
        "T17_complete": False,
        "claim_ceiling": "One Action dispatch positive and wrong-scope causal negative on one API40 composite lifetime; the other 33 operations remain unqualified."
    }


def build() -> dict:
    for path, digest in PINS.items():
        exact(ROOT / path, digest)
    review = exact(ROOT / REVIEW, PINS[REVIEW])
    if PINS[LIVE].encode() not in review or b"physical counter value is 1" not in review:
        raise ValueError("independent physical counter review missing")
    live = json.loads(exact(ROOT / LIVE, PINS[LIVE]))
    return classify(live)


if __name__ == "__main__":
    print(json.dumps(build(), sort_keys=True, indent=2))
