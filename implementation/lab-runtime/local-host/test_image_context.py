"""Exercise the real Docker context boundary with harmless synthetic files."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


HERE = Path(__file__).resolve().parent


@unittest.skipUnless(shutil.which("docker"), "Docker CLI is unavailable")
class ImageContextTests(unittest.TestCase):
    def setUp(self):
        daemon = subprocess.run(["docker", "info", "--format", "{{.ServerVersion}}"],
                                capture_output=True, text=True, check=False)
        if daemon.returncode != 0:
            self.skipTest("Docker daemon is unavailable")

    def test_build_context_allows_lock_but_refuses_other_files(self):
        with tempfile.TemporaryDirectory(prefix="cal-image-context-test-") as directory:
            context = Path(directory)
            shutil.copyfile(HERE / ".dockerignore", context / ".dockerignore")
            shutil.copyfile(HERE / "requirements.lock", context / "requirements.lock")
            (context / "protected.bin").write_bytes(b"synthetic test sentinel\n")

            dockerfile = context / "Dockerfile"
            dockerfile.write_text("FROM scratch\nCOPY requirements.lock /requirements.lock\n")
            destination = context / "output"
            allowed = subprocess.run(
                ["docker", "build", "--no-cache", "--progress", "plain",
                 "--output", f"type=local,dest={destination}", str(context)],
                capture_output=True, text=True, check=False)
            self.assertEqual(allowed.returncode, 0, allowed.stdout + allowed.stderr)
            self.assertEqual((destination / "requirements.lock").read_bytes(),
                             (HERE / "requirements.lock").read_bytes())

            dockerfile.write_text("FROM scratch\nCOPY protected.bin /protected.bin\n")
            refused = subprocess.run(
                ["docker", "build", "--no-cache", "--progress", "plain", str(context)],
                capture_output=True, text=True, check=False)
            self.assertNotEqual(refused.returncode, 0,
                                "Docker unexpectedly received an excluded file")


if __name__ == "__main__":
    unittest.main()
