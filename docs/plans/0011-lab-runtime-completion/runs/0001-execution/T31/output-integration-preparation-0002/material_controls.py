"""Authored bounded controls for actual new owned-file custody; Root review first."""
import copy,hashlib,importlib.util,json,os,sys,tempfile,types
from pathlib import Path
HERE=Path(__file__).absolute().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
POST=HERE/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'
def main():
    pkg='_T31_own_inert_material';parent=types.ModuleType(pkg);parent.__path__=[str(HERE/'pure')];sys.modules[pkg]=parent
    def load(leaf,path):
        name=pkg+'.'+leaf;spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
    load('protocol',HERE/'pure/protocol.py')
    load('workflow_output_contracts',POST/'workflow_output_contracts.py');load('workflow_output_validation',POST/'workflow_output_validation.py');load('workflow_output_registry',POST/'workflow_output_registry.py')
    F=load('resolver_fixture',HERE/'pure/resolver_fixture.py');M=load('workflow_output_material',POST/'workflow_output_material.py');checks=[];fd0=len(os.listdir('/proc/self/fd'))
    def refuses(label,fn):
        try:fn()
        except (ValueError,OSError):checks.append(label)
        else:raise AssertionError(label+' accepted')
    with tempfile.TemporaryDirectory(prefix='cal-T31-inert-material-') as tmp:
        root=Path(tmp);root.chmod(0o700);(root/'produced').mkdir(mode=0o700);st=root.stat()
        raw=b'{"OWNED_INERT_OUTPUT":true}\n';pin=hashlib.sha256(raw).hexdigest();h={'scope_ref':'OWNED-INERT','identity_ref':'OWNED-INERT','version_ref':'OWNED-INERT@1','carrier_ref':'cal.artifact-type.work-outcome-assessment/v1','byte_sha256':pin}
        row={'artifact':h,'path':'produced/record.json','original_binding':{'ref':'OWNED-INERT@1','sha256':pin}}
        receipt=b'{"OWNED_INERT_RECEIPT":true}\n';b={'ref':'OWNED-INERT-RECEIPT','sha256':hashlib.sha256(receipt).hexdigest()}
        payload={'schema_version':'lab-private-produced-workflow-material/v1-candidate','slots':{'OWNED-SLOT':[row]},'action_receipts':[{'path':'produced/receipt.json','original_binding':b}],'authority_effect':'none'}
        resolver=F.OwnResolver(payload);path=(HERE/'pure/resolver_fixture.py').relative_to(ROOT).as_posix();source={'path':path,'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()}
        descriptor={'resolver_binding':source,'resolver_entrypoint':'OwnResolver.resolve','output_custody':{'root':tmp,'identity':[st.st_dev,st.st_ino,st.st_uid,0o700],'output_roots':['produced']},'output_slot_ref':'OWNED-SLOT','output_scope_ref':'OWNED-INERT'}
        material=M.PrivateOutputMaterial(object(),descriptor,resolver=resolver.resolve,read_public=lambda b:(ROOT/b['path']).read_bytes(),host_guard=lambda:None,source_rows={(path,source['sha256'])});material.begin()
        (root/row['path']).write_bytes(raw);(root/'produced/receipt.json').write_bytes(receipt)
        capsule=F.OwnCapsule({'header':h,'original_receipt':b});routes={'transition:engineering:assessed':descriptor}
        material.close(capsule,routes,F.OwnCarriers());outputs,receipts=material.selected('OWNED-SLOT');assert outputs[0]['raw']==raw and receipts[0]['raw']==receipt;checks.append('only actual new owned metadata files captured/sealed and reread exactly')
        refuses('one-shot closed material refuses replacement',lambda:material.close(capsule,routes,F.OwnCarriers()))
        refuses('before-snapshot cannot be replaced',material.begin)
        refuses('outside selected output roots refuses with descriptor cleanup',lambda:material.capture({'path':'foreign.json','original_binding':row['original_binding']}))
        refuses('parent traversal refuses',lambda:material.capture({'path':'../foreign.json','original_binding':row['original_binding']}))
        link=root/'produced/link';link.symlink_to(root/'produced/record.json');refuses('symlink output refuses',lambda:material.capture({'path':'produced/link','original_binding':row['original_binding']}))
        wrong=copy.deepcopy(row['original_binding']);wrong['sha256']='0'*64;refuses('wrong exact original digest refuses',lambda:material.capture({'path':row['path'],'original_binding':wrong}))
        (root/'produced/record.json').write_bytes(b'{"OWNED_INERT_CHANGED":true}\n');refuses('changed sealed original refuses before reuse',lambda:material.selected('OWNED-SLOT'))
    assert len(os.listdir('/proc/self/fd'))==fd0;checks.append('all selected inert metadata paths balanced descriptors')
    return checks
