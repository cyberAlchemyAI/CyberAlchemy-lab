"""Maintain original ontology capture on the selected current-family delivery."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
ORIGINAL=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v73-t15-learning-selector-0001/workflow_ontology_outputs.py'
PIN='f4dad99153553ca3aeccc27a21407eddbab74d1618c9bc88d11e1777e482ee04'
def emit(out):
    raw=ORIGINAL.read_bytes();text=raw.decode()
    if hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('exact immutable capture predecessor required')
    # Preserve the exact predecessor pin in the emitted receipt; never rewrite
    # a selected predecessor or pretend the new family had its old counts.
    old='D=self.module.SOURCE.custody_delivery()'
    if text.count(old)!=1:raise ValueError('one exact capture delivery selector required')
    text=text.replace(old,'D=self.module.SOURCE.current_legacy_delivery()',1)
    text=text.replace('The original fifteen-node/ten-edge calculation and native exact joins remain\nunchanged.',
                      'The maintained selected-family rich calculation and native exact joins remain\nexplicitly selected; original schemas and capture correspondence remain unchanged.')
    ast.parse(text);out.mkdir(parents=True,mode=0o700,exist_ok=False)
    (out/'workflow_ontology_outputs.py').write_text(text)
    result={'predecessor':{'path':ORIGINAL.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(raw).hexdigest()},
      'postimage_sha256':hashlib.sha256(text.encode()).hexdigest(),'changed_delivery_selector_count':1,
      'snapshot_causal_checks_original_schemas_and_stage_writer_unchanged':True,'native_qualification':False,'authority_effect':'none'}
    (out/'PINS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);print(json.dumps(emit(p.parse_args().output),sort_keys=True))
