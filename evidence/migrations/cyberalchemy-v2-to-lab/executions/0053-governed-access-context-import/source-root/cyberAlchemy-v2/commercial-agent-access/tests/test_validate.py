from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
VALIDATOR = PACKAGE_ROOT / "scripts/validate.py"


class CommercialAgentAccessValidationTests(unittest.TestCase):
    def run_validator(self, package_root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(VALIDATOR),
                "--package-root",
                str(package_root),
                "--repo-root",
                str(REPO_ROOT),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def mutate(self, filename: str, transform) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            copy_root = Path(temp_dir) / "commercial-agent-access"
            shutil.copytree(PACKAGE_ROOT, copy_root)
            target = copy_root / filename
            document = json.loads(target.read_text(encoding="utf-8"))
            transform(document)
            target.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
            return self.run_validator(copy_root)

    def test_current_package_passes(self) -> None:
        result = self.run_validator(PACKAGE_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["result"], "pass")

    def test_delivery_technology_cannot_become_capability_identity(self) -> None:
        result = self.mutate(
            "product-capability.json",
            lambda document: document.update(
                {"capability_id": "CA2-CAP-SELL-DOMAINSPEC-CLI"}
            ),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stable capability identity changed", result.stdout)

    def test_entitlement_node_is_required(self) -> None:
        result = self.mutate(
            "nodes.json",
            lambda document: document.update(
                {"nodes": [node for node in document["nodes"] if node["node_id"] != "CAA-ENTITLEMENT-CLI-ACCESS"]}
            ),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required business nodes missing", result.stdout)

    def test_both_first_offer_cli_surfaces_are_required(self) -> None:
        result = self.mutate(
            "nodes.json",
            lambda document: document.update(
                {"nodes": [node for node in document["nodes"] if node["node_id"] != "CAA-REALIZATION-ONTOLOGY-CLI-READ-ONLY"]}
            ),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required business nodes missing", result.stdout)

    def test_self_hosted_service_and_agent_request_are_required(self) -> None:
        result = self.mutate(
            "nodes.json",
            lambda document: document.update(
                {"nodes": [node for node in document["nodes"] if node["node_id"] != "CAA-CONTRACT-AGENT-INSTANTIATION-REQUEST"]}
            ),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required business nodes missing", result.stdout)

    def test_contained_target_obligation_is_required(self) -> None:
        def remove_obligation(document: dict) -> None:
            obligations = document["obligation_registry"]["obligations"]
            document["obligation_registry"]["obligations"] = [
                item for item in obligations
                if item["obligation_id"] != "CAA-OBL-CREATE-ONLY-CONTAINED-TARGET"
            ]

        result = self.mutate("product-capability-support.json", remove_obligation)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required Product Capability obligations are missing", result.stdout)

    def test_kep_adapter_and_prerequisite_are_required(self) -> None:
        result = self.mutate(
            "nodes.json",
            lambda document: document.update(
                {"nodes": [node for node in document["nodes"] if node["node_id"] != "CAA-REALIZATION-KEP-AGENT-API-ADAPTER"]}
            ),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required business nodes missing", result.stdout)

    def test_kep_coownership_cannot_become_service_authority(self) -> None:
        def remove_obligation(document: dict) -> None:
            obligations = document["obligation_registry"]["obligations"]
            document["obligation_registry"]["obligations"] = [
                item for item in obligations
                if item["obligation_id"] != "CAA-OBL-KEP-COOWNERSHIP-NON-COLLAPSE"
            ]

        result = self.mutate("product-capability-support.json", remove_obligation)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required Product Capability obligations are missing", result.stdout)

    def test_ontology_read_only_obligation_is_required(self) -> None:
        def remove_obligation(document: dict) -> None:
            obligations = document["obligation_registry"]["obligations"]
            document["obligation_registry"]["obligations"] = [
                item for item in obligations
                if item["obligation_id"] != "CAA-OBL-ONTOLOGY-READ-ONLY"
            ]

        result = self.mutate("product-capability-support.json", remove_obligation)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required Product Capability obligations are missing", result.stdout)

    def test_realization_cannot_be_selected_by_registration(self) -> None:
        def select_acp(document: dict) -> None:
            document["realization_candidates"][0]["state"] = "selected"

        result = self.mutate("product-capability-support.json", select_acp)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("every delivery realization must remain unselected", result.stdout)

    def test_authority_cannot_be_inflated(self) -> None:
        result = self.mutate(
            "product-capability.json",
            lambda document: document.update({"authority_effect": "grant"}),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("authority_effect", result.stdout)


if __name__ == "__main__":
    unittest.main()
