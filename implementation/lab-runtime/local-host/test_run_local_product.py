"""Check fresh image selection, concurrent isolation and failure cleanup."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "run-local-product.sh"
COMPOSE = HERE / "compose.yaml"
BUILD = "build --no-cache lab-fixture"
CHAIN = "run --rm --no-deps --pull never chain-fixture"
LAB = "run --rm --no-deps --pull never lab-fixture"


def fake_docker(root):
    docker = root / "docker"
    docker.write_text(
        "#!/bin/sh\n"
        "printf '%s|%s\\n' \"$LAB_LOCAL_IMAGE\" \"$*\" >> \"$DOCKER_CALLS\"\n"
        "case \"$*\" in *'build --no-cache lab-fixture'*)\n"
        "  if [ -n \"$BUILD_BARRIER_DIR\" ]; then\n"
        "    : > \"$BUILD_BARRIER_DIR/${LAB_LOCAL_IMAGE##*:}\"\n"
        "    tries=0\n"
        "    while [ \"$(find \"$BUILD_BARRIER_DIR\" -type f | wc -l)\" -lt 2 ]; do\n"
        "      tries=$((tries + 1))\n"
        "      if [ \"$tries\" -ge 200 ]; then exit 20; fi\n"
        "      sleep 0.05\n"
        "    done\n"
        "  fi;;\n"
        "esac\n"
        "if [ -n \"$DOCKER_FAIL_ON\" ]; then\n"
        "  case \"$*\" in *\"$DOCKER_FAIL_ON\"*) exit 19;; esac\n"
        "fi\n"
    )
    docker.chmod(0o700)


def environment(root, calls, failure="", barrier=""):
    result = os.environ.copy()
    result.update(PATH=str(root) + os.pathsep + result["PATH"],
                  DOCKER_CALLS=str(calls), DOCKER_FAIL_ON=failure,
                  BUILD_BARRIER_DIR=str(barrier))
    return result


def rows(path):
    return [line.split("|", 1) for line in path.read_text().splitlines()]


class LocalProductLauncherTests(unittest.TestCase):
    def run_with_fake_docker(self, failure=""):
        with tempfile.TemporaryDirectory(prefix="cal-local-launcher-test-") as directory:
            root = Path(directory)
            fake_docker(root)
            calls = root / "calls"
            result = subprocess.run(["bash", str(SCRIPT)],
                                    env=environment(root, calls, failure),
                                    capture_output=True, text=True, check=False)
            return result, rows(calls)

    def assert_one_image(self, calls):
        images = {image for image, _ in calls}
        self.assertEqual(len(images), 1, calls)
        image = images.pop()
        self.assertRegex(image, r"^cyberalchemy-lab-local-host:local-[0-9a-f]{32}$")
        self.assertEqual(calls[-1], [image, "image rm -- " + image])
        return image

    def test_rebuilds_before_both_fixture_runs_and_removes_exact_image(self):
        self.assertEqual(COMPOSE.read_text().count("image: ${LAB_LOCAL_IMAGE:-"), 2)
        result, calls = self.run_with_fake_docker()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(calls), 4)
        self.assert_one_image(calls)
        self.assertTrue(calls[0][1].endswith(BUILD), calls)
        self.assertTrue(calls[1][1].endswith(CHAIN), calls)
        self.assertTrue(calls[2][1].endswith(LAB), calls)
        compose_args = [call[1].split(" build --no-cache", 1)[0]
                        if " build --no-cache" in call[1] else
                        call[1].split(" run --rm", 1)[0]
                        for call in calls[:3]]
        self.assertEqual(len(set(compose_args)), 1, calls)
        self.assertRegex(compose_args[0],
                         r"^compose -f /tmp/cal-local-product-context-[^ ]+/compose\.yaml$")
        self.assertNotIn(str(COMPOSE), str(calls[:3]))
        self.assertNotIn("image inspect", str(calls))

    def test_build_failure_prevents_fixture_runs_and_cleans_tag(self):
        result, calls = self.run_with_fake_docker(BUILD)
        self.assertEqual(result.returncode, 19)
        self.assertEqual(len(calls), 2)
        self.assert_one_image(calls)

    def test_chain_failure_prevents_work_journey_and_cleans_tag(self):
        result, calls = self.run_with_fake_docker(CHAIN)
        self.assertEqual(result.returncode, 19)
        self.assertEqual(len(calls), 3)
        self.assert_one_image(calls)

    def test_work_journey_failure_cleans_tag(self):
        result, calls = self.run_with_fake_docker(LAB)
        self.assertEqual(result.returncode, 19)
        self.assertEqual(len(calls), 4)
        self.assert_one_image(calls)

    def test_overlapping_launchers_use_distinct_tags(self):
        with tempfile.TemporaryDirectory(prefix="cal-local-launcher-overlap-") as directory:
            root = Path(directory)
            fake_docker(root)
            barrier = root / "barrier"
            barrier.mkdir()
            outputs = [root / "calls-1", root / "calls-2"]
            processes = [subprocess.Popen(["bash", str(SCRIPT)],
                                          env=environment(root, path, barrier=barrier),
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          text=True) for path in outputs]
            for process in processes:
                stdout, stderr = process.communicate(timeout=20)
                self.assertEqual(process.returncode, 0, stderr + stdout)
            traces = [rows(path) for path in outputs]
            images = [self.assert_one_image(trace) for trace in traces]
            self.assertNotEqual(images[0], images[1])
            for trace in traces:
                self.assertEqual(len(trace), 4)
                self.assertTrue(trace[0][1].endswith(BUILD))
                self.assertTrue(trace[1][1].endswith(CHAIN))
                self.assertTrue(trace[2][1].endswith(LAB))


if __name__ == "__main__":
    unittest.main()
