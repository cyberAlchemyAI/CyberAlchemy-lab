#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'registry.json').read_text())
a=json.loads((ROOT/'artifact-type-candidate.json').read_text())
artifact_lines=['<!-- GENERATED FILE: canonical data is artifact-type-candidate.json. -->','','# Artifact Type Effective-State Registry v2','',f"- Type: `{a['artifact_type_ref']}`",f"- Version: `{a['version']}`",f"- Status: `{a['status']}`",f"- Authority effect: `{a['authority_effect']}`",'', '## Distinct validation purpose','',a['distinct_validation_purpose'],'','## Orthogonality rules','']
artifact_lines += [f"- **{x['rule_id']}**: {x['statement']}" for x in a['orthogonality_rules']]
artifact_lines += ['','## Claim ceiling','',a['claim_ceiling']]
(ROOT/'ARTIFACT-TYPE.md').write_text('\n'.join(artifact_lines).rstrip()+'\n')
lines=['<!-- GENERATED FILE: canonical data is registry.json. -->','','# Artifact Type effective-state registry','',f"- Registry: `{r['registry_id']}`",f"- Status: `{r['status']}`",f"- Authority effect: `{r['authority_effect']}`",'','## Inventory','']
for k,v in r['inventory'].items(): lines.append(f"- {k.replace('_',' ').title()}: `{v}`")
lines += ['','## Descriptor effective state','','| Artifact Type ref | Descriptor version | Effective state | Semantic binding | Descriptor |','| --- | --- | --- | --- | --- |']
for x in r['descriptors']: lines.append(f"| `{x['artifact_type_ref']}` | `{x['descriptor_version']}` | `{x['effective_state']}` | `{x['semantic_binding_posture']}` | `{x['descriptor_path']}` |")
lines += ['','## Duplicate resolutions','','| Source | Effective target | Decision |','| --- | --- | --- |']
for x in r['duplicate_resolutions']: lines.append(f"| `{x['source_artifact_type_ref']}` | `{x['effective_current_target_ref']}` | `{x['decision_ref']}` |")
lines += ['','## Claim ceiling','',r['claim_ceiling']]
(ROOT/'REGISTRY.md').write_text('\n'.join(lines).rstrip()+'\n')
