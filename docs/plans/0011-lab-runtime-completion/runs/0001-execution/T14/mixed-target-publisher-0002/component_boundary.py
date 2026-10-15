"""Explicit accepted component seams. Verification is not publication authority."""
from pathlib import Path
from .typed_targets import need,sha,OriginalSchemas,adapt

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
T08_PATH=ROOT/'product/lab/release-candidates/v1/interface/release-proof-inputs-v2-completion-0001/protected_inputs.py'
T08_SHA='7a51fed6ecf0842bc3b6711e02a0b480ca9eed666405643c4e6577f938da703f'
T33_PATH=ROOT/'product/lab/release-candidates/v1/interface/owner-response-ingress-v1-completion-0001/owner_ingress.py'
T33_SHA='7f2623791fdf985c32be0e0a91cc04e65d14601c81244e2c084329fc92076fe4'

def verify_actual_owner_response(module,response,review,selection,trust):
    """Trusted bootstrap supplies original module/anchors; never API payloads.

    No key-adapter signature conversion or replay reservation is made here.
    Actual publish integration must additionally anchor persistent replay state,
    verify live native/core/source/scope and reserve under the same commit lock.
    """
    need(module is not None and Path(module.__file__)==T33_PATH
         and sha(T33_PATH.read_bytes())==T33_SHA,'independently selected owner ingress absent')
    need(Path(module.verify.__code__.co_filename)==T33_PATH
         and Path(module.verify_for_publication.__code__.co_filename)==T33_PATH,
         'owner verifier code origin differs')
    result=module.verify_for_publication(response,review,selection,trust)
    need(result['usage']=='actual-owner' and result['authority_effect']=='none','actual owner evidence absent')
    return result

def prepare_from_protected(module,reader,schema_rows,schema_bindings,target_rows,*,carrier_rows=None,carrier_bindings=None):
    """Keep T08 read purpose, original class and entry/exit boundary unchanged.

    No release/installation read grant is relabeled as admission authority.
    schema_rows are explicit original {path,file_id}; target rows bind file IDs
    and exact adapter specs. No producer bodies are inferred from proof tables.
    """
    need(module is not None and Path(module.__file__)==T08_PATH
         and sha(T08_PATH.read_bytes())==T08_SHA,'independently selected protected reader absent')
    need(type(reader) is module.ProtectedReader
         and Path(reader.read.__code__.co_filename)==T08_PATH,
         'actual selected protected reader required')
    need(reader.anchor.operation in ('release.prepare','installation.execute'),
         'unsupported original protected-reader operation')
    documents={}
    with reader.boundary():
        for row in schema_rows:
            need(set(row)=={'path','file_id'} and row['path'] not in documents,'closed schema file selection required')
            documents[row['path']]=reader.read(row['file_id'],'governed-schema')
        need(type(carrier_rows) is list and type(carrier_bindings) is list,'independent original registered carrier selections required')
        carriers={}
        for row in carrier_rows:
            need(set(row)=={'path','file_id'} and row['path'] not in carriers,'closed carrier file selection required')
            carriers[row['path']]=reader.read(row['file_id'],'governed-descriptor')
        schemas=OriginalSchemas(schema_bindings,documents,carrier_bindings=carrier_bindings,raw_carriers=carriers)
        prepared=[]
        for row in target_rows:
            need(set(row)=={'file_id','output_path','spec'},'closed protected target selection required')
            kind='governed-descriptor' if row['spec']['family']=='registry-descriptor' else 'governed-record'
            raw=reader.read(row['file_id'],kind)
            prepared.append({'output_path':row['output_path'],'adapted':adapt(raw,row['spec'],schemas)})
    return prepared
