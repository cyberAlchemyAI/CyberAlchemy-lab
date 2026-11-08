"""New current-Legacy-only bounded fixture budget; historical caps remain900."""
import copy,json
from auth_schema_current_names import LEGACY

def cap(value):
 if isinstance(value,dict):
  return {k:3600 if k=='maximum' and v==900 else cap(v) for k,v in value.items()}
 if isinstance(value,list):return [cap(x) for x in value]
 return value

def apply(value):
 result=copy.deepcopy(value);rows=result['oneOf'];base=rows[0];p=base['properties']
 if p['schema_version']!={'const':'lab-local-candidate-policy/v4-candidate'}:raise ValueError('exact base participation variant required')
 original=copy.deepcopy(base);parts=p['source_name']['anyOf']
 if len(parts)!=2 or parts[1]!=LEGACY or set(parts[0])!={'enum'}:raise ValueError('exact current/name split seam required')
 p['source_name']=copy.deepcopy(parts[0])
 current=copy.deepcopy(original);current['properties']['source_name']=copy.deepcopy(LEGACY);current['properties']['session_control']=cap(current['properties']['session_control']);rows.append(current)
 changed=[len(rows)-1]
 for i,row in enumerate(rows[:-1]):
  properties=row.get('properties',{})
  if properties.get('source_name')==LEGACY and properties.get('schema_version',{}).get('const') in ('lab-local-lesson-read-policy/v1-candidate','lab-local-lesson-application-policy/v2-candidate'):
   before=properties['session_control'];after=cap(before)
   if after!=before:properties['session_control']=after;changed.append(i)
 return result,changed
if __name__=='__main__':
 import argparse
 from pathlib import Path
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('destination',type=Path);a=p.parse_args();v,changed=apply(json.loads(a.source.read_bytes()));a.destination.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');print(json.dumps({'changed_current_legacy_rows':changed,'new_maximum_session_seconds':3600,'historical_and_source8_maximum_seconds':900,'active_leases_changed':False,'authority_effect':'none'},sort_keys=True))
