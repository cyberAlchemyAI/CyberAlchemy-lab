"""Authored inert signature/domain checks, no actual role/producer permission."""
import base64,copy,hashlib,importlib.util,json,sys,types
from pathlib import Path
HERE=Path(__file__).absolute().parent;POST=HERE/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'
def main():
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
    pkg='_T31_v3_OWNED_INERT_response';parent=types.ModuleType(pkg);parent.__path__=[str(HERE/'pure')];sys.modules[pkg]=parent
    def load(leaf,path):
        spec=importlib.util.spec_from_file_location(pkg+'.'+leaf,path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
    P=load('protocol',HERE/'pure/protocol.py');load('workflow_output_contracts',POST/'workflow_output_contracts.py');R=load('workflow_response_contract',POST/'workflow_response_contract.py')
    key=Ed25519PrivateKey.generate();public=base64.b64encode(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)).decode();raw=b'{"OWNED-INERT-actual-input":true}\n'
    fields={'schema_version':'lab-authenticated-challenge-response-input/v1-candidate','policy_binding':{'ref':'OWNED-INERT:policy','sha256':'1'*64},'response_sha256':hashlib.sha256(raw).hexdigest(),'run_binding':{'ref':'OWNED-INERT:run','sha256':'2'*64},'work_ref':'OWNED-INERT:work@1','source_cut':{'OWNED-INERT':True},'eligible_invocation_ref':'OWNED-INERT:eligible'}
    selected={k:fields[k]for k in ('policy_binding','run_binding','work_ref','source_cut','eligible_invocation_ref')};signed=dict(fields,signature_base64=base64.b64encode(key.sign(P.compact(fields))).decode());encoded=P.compact(signed)
    assert R.authenticate_response(raw,encoded,public_key=public,**selected)[0]==json.loads(raw);checks=['owned inert signed response bytes join exact preselected phase input domain']
    for field in selected:
        changed=copy.deepcopy(selected);changed[field]={'OWNED-INERT:other':True}if type(selected[field])is dict else 'OWNED-INERT:other'
        try:R.authenticate_response(raw,encoded,public_key=public,**changed)
        except ValueError:checks.append('authenticated response rejects different '+field)
        else:raise AssertionError(field)
    for body,proof in [(raw+b' ',encoded),(raw,P.compact(dict(signed,signature_base64=base64.b64encode(b'0'*64).decode())))]:
        try:R.authenticate_response(body,proof,public_key=public,**selected)
        except Exception:checks.append('changed exact input/signature refuses before producer')
        else:raise AssertionError('changed response accepted')
    return checks
