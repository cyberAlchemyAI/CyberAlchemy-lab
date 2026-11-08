"""Select the exact independent complete T08 checkpoint before T09 imports."""
import bootstrap
from bootstrap import R,E,checked
import json

CHECKPOINT_SHA='c8dfb70b169227a88a6b327c0beef36ac435dcf434dc69c45a6cc42a1ebbc863'
REVIEW_SHA='842e64fcb9a0818bc4e779adb20f296bca967b9f236f27d55219892490e12814'
CHECKPOINT=json.loads(checked(E/'semantic-checkpoint-0001.json',CHECKPOINT_SHA))
REVIEW=json.loads(checked(E/'reviewer-semantic-checkpoint-0001-review.json',REVIEW_SHA))

def guard():
    checked(E/'semantic-checkpoint-0001.json',CHECKPOINT_SHA)
    checked(E/'reviewer-semantic-checkpoint-0001-review.json',REVIEW_SHA)
    for key in ('source_bindings','original_contract_bindings','accepted_import_bindings','original_selected_inputs'):
        for b in CHECKPOINT[key]:
            raw=checked(R/b['relative_path'],b['sha256'])
            if len(raw)!=b['size_bytes']:raise ValueError('accepted T08 size drift')

guard()
