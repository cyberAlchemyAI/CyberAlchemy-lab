"""Independent exact packet/source reconstruction; no effect dispatch."""
import sys
from packet import *


def run(packet_sha,code_sha):
    require(binding(HERE/'packet.py')['sha256']==code_sha,'independently selected preparation reader changed')
    path=HERE/'packages/0001/preparation.json';require(binding(path)['sha256']==packet_sha,'independently selected packet changed')
    prerequisite();value=original(binding(path));result=validate(value)
    # Postimages reconstruct from exact original records or parent selections.
    for m in value['members']:
        if m['member_class']=='workflow-transition-protocol':
            parent=original(m['scope']['source_selection']['parent_binding']);index=int(m['scope']['source_selection']['json_pointer'].split('/')[-1])
            require(bound(m['targets'][0])==encoded(parent['workflows'][index]),'cold model reconstruction differs')
    for r in value['selected_carrier_postimages']:require(bound(r['source_binding'])==bound(r['postimage_binding']),'cold original carrier byte parity differs')
    result.update(packet_binding=binding(path),reader_binding=binding(HERE/'packet.py'),model_execution_gaps_retained=56,selected_carrier_postimages=13,
        actual_owner_outcome=None,canonical_effects_applied=0,local_transactions_applied=0,operational_permissions_granted=0,Session_memory_restored=False,
        expired_Lesson_historical_only=True,runtime_activation=False,human_pilot=False,all_workflow_transitions_executed=False)
    print(encoded(result).decode(),end='')


if __name__=='__main__':
    require(len(sys.argv)==3,'usage: cold.py packet-sha reader-sha');run(*sys.argv[1:])
