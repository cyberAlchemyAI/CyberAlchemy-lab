"""Cold d95 diagnostic margin selection; invoke through launch.py."""
from __future__ import annotations

import importlib
import importlib.util
import json
import copy
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t03_d95_margin_preflight', HERE / 'margin.py')
margin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(margin)
package = importlib.import_module('api-integration-v33-t03-one-lesson-native-v4-margin-0006')
diagnostic = margin.DiagnosticMargin(package.__name__)
try:
    selected = diagnostic.modules['observed_margin']
    software = selected.software(diagnostic.config, diagnostic.modules)
    dependency = selected.dependency(diagnostic.config)
    selected.instrumentation(diagnostic.config['instrumentation_binding'])
    schemas = diagnostic.modules['protocol'].Schemas(margin.PROFILE_SHA)
    if schemas.profile_binding == diagnostic.config['profile_binding']:
        raise ValueError('old direct profile binding comparison unexpectedly passed')
    if selected.profile_correspondence(schemas.profile_binding, diagnostic.config['profile_binding']) is not True:
        raise ValueError('live profile correspondence did not pass')
    profile_negatives = 0
    for mutation in ('foreign-ref', 'foreign-sha', 'shape-only'):
        original = copy.deepcopy(schemas.profile_binding)
        configured = copy.deepcopy(diagnostic.config['profile_binding'])
        if mutation == 'foreign-ref':
            original['ref'] = 'foreign/profile.json'
        elif mutation == 'foreign-sha':
            original['sha256'] = '0' * 64
        else:
            configured = {'ref': configured['path'], 'sha256': configured['sha256']}
        try:
            selected.profile_correspondence(original, configured)
        except selected.MarginBeforeClaim as error:
            if error.code != 'integrity-failed':
                raise ValueError('wrong live profile refusal') from error
            profile_negatives += 1
        else:
            raise ValueError('false live profile correspondence accepted: ' + mutation)
    import jsonschema
    result = {**diagnostic.public_receipt(),
              'schema_guard': 'PASS', 'source_code_guard': 'PASS',
              'source_code_selected_files': len(software),
              'installed_dependency_guard': 'PASS',
              'installed_dependency_selection_sha256': dependency,
              'instrumentation_guard': 'PASS',
              'live_profile_correspondence': 'PASS',
              'old_direct_profile_comparison': False,
              'live_profile_causal_negatives': profile_negatives,
              'jsonschema_origin': str(Path(jsonschema.__file__).resolve().relative_to(margin.ROOT)),
              'selected_interpreter': str(Path(sys.executable).relative_to(margin.ROOT)),
              'runtime_executed': False, 'lesson_applied': False, 'lesson_assessed': False}
finally:
    diagnostic.close()
result['private_configuration_removed'] = not diagnostic.root.exists()
print(json.dumps(result, sort_keys=True))
