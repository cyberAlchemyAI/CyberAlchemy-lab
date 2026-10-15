"""Inert join controls; no native store, real translator, grant or Lab API."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

HERE = Path(__file__).absolute().parent

def main():
    name = '_cal_T32_rich_inert_'+uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)
    selected = __import__(name+'.selected_store',fromlist=['rich_metadata_after_append'])
    fd0 = len(os.listdir('/proc/self/fd'))
    checks = []
    view = {'inert_source':'original test bytes only'}
    node = {'node_id':'inert-node','subject':{'identity':'inert-original-subject'}}
    state = {'identity':{'subject_id':'inert-node'},'inert':True}
    event = {'subject_identity':{'subject_id':'inert-node','subject_kind':'node'},
        'event_id':'inert-event','event_digest':'1'*64,'semantic_cursor':1,
        'complete_resulting_semantic_state':state}
    governance = [{'event_id':'inert-governance'}]
    class InertTranslator:
        def node_spec(self, actual):
            assert actual == view
            return copy.deepcopy(node)
        def rich_record(self, actual, reference, refs):
            assert actual == node and refs == ['inert-governance']
            return {'node_id':actual['node_id'],'semantic_ref':reference,'governance_refs':refs}
        def translate_node(self, record, actual):
            assert actual == node
            return copy.deepcopy(state),{'inert':True}
    translator = InertTranslator()
    reference = {'semantic_event_id':'inert-event','semantic_event_digest':'1'*64,'semantic_cursor':1}
    witness = {'source_view':view,'rich_record':translator.rich_record(node,reference,['inert-governance'])}
    actual = selected.rich_metadata_after_append(translator,[event],governance,witness,{})
    assert actual == {'inert-node':node}
    actual['inert-node']['subject']['identity'] = 'changed own return'
    assert node['subject']['identity'] == 'inert-original-subject'
    checks.append('next node metadata derives from selected translator and copies original spec')
    def refuses(label, semantic, proof, base):
        try:
            selected.rich_metadata_after_append(translator,semantic,governance,proof,base)
        except ValueError:
            checks.append(label)
        else:
            raise AssertionError(label)
    changed = copy.deepcopy(event)
    changed['subject_identity']['subject_id'] = 'other-node'
    refuses('sealed native subject must match original derived node',[changed],witness,{})
    changed = copy.deepcopy(witness)
    changed['rich_record']['node_id'] = 'caller-invented-node'
    refuses('entire rich record must match original translator and event reference',[event],changed,{})
    changed = copy.deepcopy(event)
    changed['complete_resulting_semantic_state'] = {'inert':False}
    refuses('translated rich state must match exact selected native state',[changed],witness,{})
    refuses('duplicate mapped node cannot bypass recovered metadata',[event],witness,{'inert-node':node})
    refuses('incomplete original node witness refuses',[event],{'source_view':view},{})
    base = {'previous-node':{'inert':True}}
    assert selected.rich_metadata_after_append(translator,[],[],{'lifecycle':'inert'},base) == base
    checks.append('relation challenge lifecycle and migration append preserve existing specs')
    assert len(os.listdir('/proc/self/fd')) == fd0
    print(json.dumps({'result':'PASS-inert-rich-metadata-joins-only','checks':checks,'FD_delta':0,
        'actual_native_recovery_or_original_translator_qualified':False,'authority_effect':'none'},sort_keys=True))

if __name__ == '__main__':
    main()
