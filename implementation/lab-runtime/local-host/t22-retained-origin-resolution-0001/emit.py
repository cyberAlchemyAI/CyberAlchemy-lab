"""Add a separately named retained-native-origin local fixture profile."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v75-current-fixtures-0001/fixture_resolution_handler.py'
PIN='1de42402dc1a02860f98b2f784e0cae62f9450adb40f397e1c099fbac67cb3a5'
def once(text,before,after):
    if text.count(before)!=1:raise ValueError('exact retained fixture patch seam required')
    return text.replace(before,after,1)
def transform(raw):
    if hashlib.sha256(raw).hexdigest()!=PIN:raise ValueError('exact strict fixture predecessor required')
    text=raw.decode()
    text=once(text, "SUBMISSION_SHA=", "RETAINED_SOURCE_CUT=R.frame("+repr(b'{"branch_ref":"branch:completion-legacy-local-4636eca980a5d94d","commit_sequence":2,"commit_sha256":"0f4e21b32c23bf87a3ad1a17a98f2d99ac66d7364f45d0fc0038728680bbdedd","source_profile_sha256":"3364b562c0f381ec8397ae9dbd839bbbb12ff58c9991bb97f79d8b8eec4b9c48","store_ref":"completion-legacy-local-4636eca980a5d94d","streams":[{"cursor":9,"head_sha256":"8d8a8548a71bc6fb839a9688a59270087b01d8fd12bb8e23fd74abb0a0567a37","stream_ref":"project-governance-event-history"},{"cursor":9,"head_sha256":"90e4ab4272e9e473b899b319e4ec857c4edc43843ae8cf5757472a525a341f6c","stream_ref":"project-semantic-event-history"}]}')+")\nSUBMISSION_SHA=")
    text=once(text,'        self.capsule=R.frame(self.raw)','''        selected=R.frame(self.raw)
        source.require(type(selected) is dict,'closed fixture source object required')
        self.retained=None
        if selected.get('schema_version')=='lab-local-retained-Agent-resolution/v1-fixture':
            source.require(set(selected)=={'schema_version','original_signed_source','original_source_records',
                'coordinating_source_cut','original_source_posture','authority_effect'}
                and selected['authority_effect']=='none'
                and selected['original_source_posture']=='historical-verified-native-origin',
                'closed retained native origin fixture profile required')
            self.retained=selected
            self.capsule=selected['original_signed_source']
        else:self.capsule=selected''')
    text=once(text,'    def header(self,kind,raw=None,version=None):','''    def retained_original(self,kind):
        source.require(self.retained is not None and kind in ('work','challenge-contract'),
            'exact retained source record kind required')
        originals=self.retained['original_source_records']
        source.require(type(originals) is dict and set(originals)=={'work','challenge-contract'},
            'closed retained original Work/Contract bytes required')
        raw=base64.b64decode(originals[kind],validate=True)
        body=R.frame(raw);R.validate(kind,body)
        header=self.capsule['response']['subject' if kind=='work' else 'challenge_contract']
        source.require(body['kind']==kind and body['node_id']==header['identity_ref']
            and body['scope_ref']==header['scope_ref']==self.capsule['envelope']['payload']['scope_ref']
            and source.sha(raw)==header['byte_sha256'],'retained original source header/body differs')
        return raw
    def header(self,kind,raw=None,version=None):''')
    text=once(text,'                 selected_source_cut=outer,now=now())','''                 selected_source_cut=(RETAINED_SOURCE_CUT if self.retained is not None else outer),now=now())
        if self.retained is not None:
            source.require(R.canon(self.retained)==R.canon(R.frame(self.raw))
                and self.capsule is self.retained['original_signed_source'],
                'captured retained fixture routing changed')
            source.require(self.retained['coordinating_source_cut']==outer,
                'retained fixture coordinating cut differs from current request')''')
    old='''            row=self.host.handlers.resolve_exact(header)
            raw=M.record_bytes(self.host.handlers.view,row)[0]
            body=R.frame(raw)'''
    new='''            if self.retained is None:
                row=self.host.handlers.resolve_exact(header)
                raw=M.record_bytes(self.host.handlers.view,row)[0]
            else:
                # The API71 origin/request/candidate and signature were checked
                # above against independent immutable pins. These are its exact
                # historical inputs, never relabeled as current Source records.
                raw=self.retained_original(kind)
            body=R.frame(raw)'''
    text=once(text,old,new)
    old='''        work_row=self.host.handlers.resolve_exact(self.capsule['response']['subject'])
        work_raw=M.record_bytes(self.host.handlers.view,work_row)[0]'''
    new='''        if self.retained is None:
            work_row=self.host.handlers.resolve_exact(self.capsule['response']['subject'])
            work_raw=M.record_bytes(self.host.handlers.view,work_row)[0]
        else:work_raw=self.retained_original('work')'''
    text=once(text,old,new)
    marker='''        self.preflight(message,request,outer,key)'''
    # The original prepare signature calls preflight(message,outer,key), not
    # a new API request shape. Only candidate evidence gains explicit provenance.
    before='''        self.preflight(message,outer,key)
        original=self.vault.object(base64.b64decode(self.capsule['original_challenge_base64']))'''
    after='''        if self.retained is not None:
            check.update(original_source_posture='historical-verified-native-origin',
                original_source_cut=copy.deepcopy(self.capsule['envelope']['payload']['source_cut']),
                coordinating_source_cut=copy.deepcopy(outer),original_Work_or_Contract_Source_current=False)
        self.preflight(message,outer,key)
        original=self.vault.object(base64.b64decode(self.capsule['original_challenge_base64']))'''
    text=once(text,before,after)
    text=once(text,"'candidate_binding':metadata,'requested_effect':'Prepare deferred local fixture candidate only; retain unresolved residue.',",
        "'candidate_binding':metadata,'requested_effect':('Prepare deferred retained-origin fixture candidate only; historical Work/Contract remain historical and unresolved owner residue remains.' if self.retained is not None else 'Prepare deferred local fixture candidate only; retain unresolved residue.'),")
    start=text.index("        R.verify(self.capsule,selected_public_hex=public")
    end=text.index("        p=self.capsule[",start)
    block=text[start:end]
    method="    def verify_origin(self,public,outer,time):\n"+block.replace("now=now()","now=time")+"        if self.retained is not None:\n            self.retained_original('work');self.retained_original('challenge-contract')\n"
    text=text[:start]+"        self.verify_origin(public,outer,now())\n"+text[end:]
    text=once(text,"    def header(self,kind,raw=None,version=None):",method+"    def header(self,kind,raw=None,version=None):")
    text=text.replace("        # Resolve the original Work and Contract on the actual current signed\n        # native source, independently of the fixture signer's declarations.","        # Select exact original Work/Contract bytes from the same-cut current\n        # Source or the independently pinned historical native origin.").replace("current Challenge Contract does not permit fixture Agent response","selected original Challenge Contract does not permit fixture Agent response")
    ast.parse(text);return text.encode()
def emit(out):
    raw=transform(BASE.read_bytes());out.mkdir(mode=0o700,parents=True,exist_ok=False);(out/'fixture_resolution_handler.py').write_bytes(raw)
    value={'predecessor':{'path':BASE.relative_to(ROOT).as_posix(),'sha256':PIN},'postimage_sha256':hashlib.sha256(raw).hexdigest(),
      'old_strict_same_cut_profile_preserved':True,'new_profile':'lab-local-retained-Agent-resolution/v1-fixture',
      'original_native_inputs_pinned_by_unchanged_fixture_resolution_source':True,'original_request_and_cut_rewritten':False,
      'current_Source_Reader_scope_signature_UTC_and_defer_only_guards_preserved':True,
      'old_Work_Contract_Source_current_claimed':False,'actual_native_API_qualification':False,'authority_effect':'none'}
    (out/'PINS.json').write_text(json.dumps(value,indent=2,sort_keys=True)+'\n');return value
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);print(json.dumps(emit(p.parse_args().output),sort_keys=True))
