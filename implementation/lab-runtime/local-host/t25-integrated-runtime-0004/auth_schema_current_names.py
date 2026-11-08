"""Lexical current-family names; actual authority stays in exact host validation."""
import copy,json
LEGACY={'type':'string','pattern':r'^completion-legacy:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$'}
SOURCE8={'type':'string','pattern':r'^completion-current-participation:[A-Za-z0-9][A-Za-z0-9._-]{0,127}$'}
METADATA={
 'lab-local-metadata-candidate-policy/v1-candidate','lab-local-export-candidate-policy/v1-candidate',
 'lab-local-review-candidate-policy/v1-candidate','lab-local-classification-candidate-policy/v1-candidate',
 'lab-local-failure-candidate-policy/v1-candidate','lab-local-typed-extension-candidate-policy/v1-candidate',
 'lab-local-package-import-policy/v1-candidate','lab-local-package-export-policy/v1-candidate',
 'lab-local-challenge-candidate-policy/v1-candidate','lab-local-challenge-review-policy/v1-candidate',
 'lab-local-reference-closed-review-policy/v1-candidate','lab-local-ontology-projection-policy/v1-candidate',
 'lab-local-installation-release-policy/v1-candidate','lab-local-workflow-transition-policy/v1-candidate'}
def apply(value):
 result=copy.deepcopy(value);changes=[]
 for number,row in enumerate(result['oneOf']):
  properties=row.get('properties',{});source=properties.get('source_name');version=properties.get('schema_version',{}).get('const')
  if source is None:continue
  before=copy.deepcopy(source)
  if source.get('const','').startswith('completion-legacy:'):properties['source_name']=copy.deepcopy(LEGACY)
  elif version in METADATA and source.get('const') in ('custody-participation','workflow-participation'):
   properties['source_name']={'anyOf':[copy.deepcopy(source),copy.deepcopy(LEGACY)]}
  elif 'enum' in source:
   old=[name for name in source['enum'] if not name.startswith(('completion-legacy:','completion-current-participation:'))]
   patterns=[]
   if any(name.startswith('completion-legacy:') for name in source['enum']):patterns.append(copy.deepcopy(LEGACY))
   if any(name.startswith('completion-current-participation:') for name in source['enum']):patterns.append(copy.deepcopy(SOURCE8))
   if patterns:properties['source_name']={'anyOf':([{'enum':old}] if old else [])+patterns}
  if before!=properties['source_name']:changes.append({'variant':number,'schema_version':version,'before':before,'after':properties['source_name']})
 return result,changes
if __name__=='__main__':
 import argparse
 from pathlib import Path
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('destination',type=Path);a=p.parse_args();v,changes=apply(json.loads(a.source.read_bytes()));a.destination.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');print(json.dumps({'source_name_changes':changes,'all_other_schema_constraints_unchanged':True,'authority_effect':'none'},sort_keys=True))
