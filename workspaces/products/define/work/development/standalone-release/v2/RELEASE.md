# Define Apache-2.0 packaging update

The user selected Apache-2.0 for the standalone CyberAlchemy Define distribution on 15 October 2026.

## Applied changes

- Added the unmodified license text retrieved from the Apache Software Foundation's official source as `implementation/define-cli/standalone/LICENSE`.
- Added `NOTICE` with CyberAlchemy contributor attribution and the provenance location for the adapted project code and bundled schema/generator.
- Declared `license = "Apache-2.0"` and `license-files = ["LICENSE", "NOTICE"]` in `pyproject.toml`.
- Set the setuptools minimum to 77.0.3, which supports the SPDX license metadata format.
- Included both legal files in the wheel and source archive, and updated current documentation/discovery metadata to remove the outstanding license decision.

The license applies to the standalone distribution, including its packaged project material. User-supplied Packs and evidence retain their own terms. Separately distributed dependencies retain their own license files. This update does not change the license of the rest of the Lab repository or modify frozen v1/v2 source bytes.

## Artifact and runtime evidence

This is a packaging update to the unpublished `0.3.0rc2` candidate. The earlier archives and qualification records remain in `standalone-release/v1`; the newly licensed archives are selected here by their new hashes.

`archive-check.json` verifies:

- The wheel metadata declares `License-Expression: Apache-2.0`.
- Both archives contain exact copies of LICENSE and NOTICE.
- All **27 selected runtime/resource files** are identical to the previously qualified runtime.
- The runtime inventory remains `55aa310917e1fb246bb27dd0e9e3ab80649bfe04cadf9fd37c71f7bbeb0f0c33`.

The new wheel was installed into a fresh virtual environment outside the Lab repository. `QUALIFICATION.json` records the installation, metadata checks and standalone suite outcome for these exact licensed bytes. The prior four-interpreter qualification and end-to-end evidence remain applicable to the identical runtime selection; they are not presented as new executions of the licensed archives on every interpreter.

## Remaining release work

The license decision is closed. Remaining work is the stable-version promotion (recommended `0.3.0`), qualification of those final archives, and the chosen tagging/publication action. Nothing was published, deployed, admitted into canonical Lab state or adopted as the default runtime here.

## Sources

- Apache Software Foundation: https://www.apache.org/licenses/LICENSE-2.0.txt
- Python Packaging User Guide: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license-and-license-files
