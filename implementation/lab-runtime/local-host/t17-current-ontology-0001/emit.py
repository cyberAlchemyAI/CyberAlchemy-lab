"""Emit a current-family ontology projector without changing the predecessor."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
ORIGINAL=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v73-t15-learning-selector-0001/ontology_projection.py'
ORIGINAL_SHA='e9f52281e2f4cebb82cc95ad91ea0bad4d2f46ed88ba0c175d088b51cfb984af'
HEADER_HELPER='''def selected_mapping_headers(mapping):
    """The selected fixture mapper contract is exactly eighteen nodes/twelve edges."""
    rows=mapping['rows']
    require(type(rows) is list and len(rows)==30,'mapped exact source closure differs')
    kinds=[row['subject_identity']['subject_kind'] for row in rows]
    require(kinds.count('node')==18 and kinds.count('edge')==12
        and set(kinds)=={'node','edge'},'selected current mapper node/edge contract differs')
    selected=[row['artifact'] for row in rows]
    require(len({row['version_ref'] for row in selected})==30,'mapped exact source closure differs')
    return selected

'''
ORIGIN_HELPER='''def selected_mapper(mapper):
    from types import ModuleType
    require(type(mapper) is ModuleType and mapper is SOURCE.current_legacy_delivery().MAPPED
        and Path(mapper.__file__).resolve()==MAPPER_EXECUTION/'build.py'
        and mapper.HERE==MAPPER,'selected current native mapping executable/package root differs')
    return mapper

'''


def once(text,before,after):
    if text.count(before)!=1:
        raise ValueError('exact current ontology patch seam required')
    return text.replace(before,after)


def transform(raw):
    if hashlib.sha256(raw).hexdigest()!=ORIGINAL_SHA:
        raise ValueError('immutable predecessor ontology projector differs')
    text=raw.decode()
    start=text.index("MAPPER=HERE.parent/'current-mapped-context-v4'")
    end=text.index('CLAIM=',start)
    text=text[:start]+'''from . import runtime_selection as PORTABLE
MAPPER=ROOT/Path(PORTABLE.binding('family.mapper_source')['path']).parent
MAPPER_PIN=PORTABLE.binding('family.mapper_source')['sha256']
MAPPER_EXECUTION=MAPPER
MAPPER_EXECUTION_PIN=MAPPER_PIN
PACKAGE_PIN=PORTABLE.binding('family.mapper_package')['sha256']
'''+text[end:]
    if text.count('SOURCE.custody_delivery()')!=3:
        raise ValueError('three exact current ontology producer selection seams required')
    text=text.replace('SOURCE.custody_delivery()','SOURCE.current_legacy_delivery()')
    text=once(text,"require(len(node_ids)==15 and len(edge_ids)==10,'actual carrier node/edge closure differs')",
              "require(len(node_ids)==18 and len(edge_ids)==12,'actual carrier node/edge closure differs')")
    text=once(text,'def validate_control(policy,schemas):',HEADER_HELPER+ORIGIN_HELPER+'def validate_control(policy,schemas):')
    text=once(text,"        require(Path(self.mapper.__file__).resolve()==MAPPER_EXECUTION/'build.py'\n            and self.mapper.SELECTOR_ROOT==MAPPER_EXECUTION and self.mapper.HERE==MAPPER,\n            'selected native mapping executable or original semantic/package root differs')",'        selected_mapper(self.mapper)')
    text=once(text,'        self.mapper.guard(MAPPER_EXECUTION_PIN)','        selected_mapper(self.mapper)\n        self.mapper.guard(MAPPER_EXECUTION_PIN)')
    text=once(text,"        selected=[r['artifact'] for r in mapping['rows']]\n        require(len(selected)==25 and len({r['version_ref'] for r in selected})==25,'mapped exact source closure differs')",'        selected=selected_mapping_headers(mapping)')
    compile(text,str(ORIGINAL),'exec')
    return text.encode()


def emit(output):
    output=Path(output)
    if output.exists():raise ValueError('fresh ontology postimage directory required')
    raw=transform(ORIGINAL.read_bytes());output.mkdir(parents=True,mode=0o700)
    path=output/'ontology_projection.py';path.write_bytes(raw)
    value={'status':'POSTIMAGE-UNQUALIFIED','predecessor_sha256':ORIGINAL_SHA,
        'postimage_sha256':hashlib.sha256(raw).hexdigest(),'native_mapper_contract':{'nodes':18,'edges':12,'total':30},
        'native_calls_and_owned_commit_semantics_changed':False,'authority_effect':'none'}
    (output/'PINS.json').write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
    return value


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path)
    print(json.dumps(emit(parser.parse_args().output),sort_keys=True))
