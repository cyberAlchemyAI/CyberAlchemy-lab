"""An actual new process reconstructs a private read-only source and exits."""
import base64,time
from .base import *
from . import reader,model
def main(source_pin,package_pin):
    require(package_pin is not None,'independent package pin required');verify_source(source_pin)
    start=time.monotonic()
    with reader.open_signed(source_pin,package_pin) as selected:
        report=selected.closure_report();product,body=selected.sources.resolve('product:cyberalchemy-lab')
        targets=[]
        for tx in selected.view.data['transactions'][1:]:
            for t in tx['proposal']['targets']:
                s=selected.view.subjects[t['version_ref']];raw,locator,encoding,enclosing=model.record_bytes(selected.view,s)
                require(raw==selected.view.handle.custody.decode_content(t['content']),'cold target original bytes differ')
                targets.append({'version_ref':t['version_ref'],'byte_sha256':sha(raw),'encoding':encoding,
                    'original_file_sha256':enclosing,'locator':locator})
        require(len(targets)==23,'complete cold target accounting required')
        report.update(schema_version='lab-original-participation-cold-process/v1-candidate',result='PASS',
            source_sha256=source_pin,package_sha256=package_pin,original_targets=targets,
            actual_product_artifact=product.artifact,actual_product_original_base64=base64.b64encode(product.original).decode(),
            product_body_version=body['version'],product_revision_witness_encoding=product.revision_witness.encoding,
            process_id=os.getpid(),active_Agents_created=0,Session_memory_rehydrated=False,private_keys_restored=False,
            canonical_effects_applied=0,task_complete=False,goal_complete=False)
    verify_source(source_pin);report['owned_cold_read_workspace_removed']=True;report['duration_seconds']=time.monotonic()-start
    emit(HERE/'receipts/cold.json',report);print(json.dumps({'result':'PASS','pid':os.getpid(),'targets':23,'receipt_binding':binding(HERE/'receipts/cold.json')}),flush=True)
