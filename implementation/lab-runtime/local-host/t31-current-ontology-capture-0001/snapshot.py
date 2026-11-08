"""Fresh native replay of exact retained public-projection generation bytes.

The private host supplies a protected archive control and a current metadata
grant. Retained projection evidence never reactivates its old channel/grant.
"""
import copy
import importlib
import json
from pathlib import Path

def need(ok,reason):
    if not ok:raise ValueError(reason)
def closed(value,fields,reason):need(type(value) is dict and set(value)==set(fields),reason)

class OntologySnapshot:
    def __init__(self,host,*,control_binding,work_ref,live_guard):
        self.host=host;self.control_binding=copy.deepcopy(control_binding);self.work_ref=work_ref;self.live_guard=live_guard
        pkg=type(host).__module__.rsplit('.',1)[0]
        self.P,self.A,self.H,self.SS=(importlib.import_module(pkg+'.'+name) for name in ('protocol','auth','handlers','session_source_freshness'))
        service=importlib.import_module(pkg+'.service');auth=importlib.import_module(pkg+'.auth')
        need(type(host) is service.Service and type(host.channel) is auth.ReaderChannel,'actual selected independent Service/Reader required')
        self.original=host.vault.material(self.control_binding);self.control=self.P.frame_parse(self.original)
        closed(self.control,('schema_version','generation_root','head_binding','manifest_binding','native_read_binding','projection_receipt_binding',
          'mapping_binding','mapping_original_binding','work_ref','source_cut','store_ref','authority_effect'),'closed private original ontology archive selection required')
        c=self.control
        need(c['schema_version']=='lab-private-original-ontology-archive/v1' and c['authority_effect']=='none' and c['work_ref']==work_ref
             and c['source_cut']==self.H.cut(host.handlers.view),'archive control Work/current cut differs')
        self.mapper=self.P.source.current_legacy_delivery().MAPPED
        self.source=host.handlers.view.custody_signed_sources;self.source.guard()
        self.family=self.SS.fresh_selected_source(self.source);self.basis=copy.deepcopy(self.SS.captured_source_basis(self.source))
        self.guard()
    def guard(self):
        self.live_guard();self.host.channel.termination_guard();self.host.schemas.guard()
        need(self.host.vault.material(self.control_binding)==self.original and self.P.compact(self.control)==self.P.compact(self.P.frame_parse(self.original)),
             'independent ontology archive control changed')
        need(self.H.cut(self.host.handlers.view)==self.control['source_cut'] and self.SS.captured_source_basis(self.source)==self.basis,
             'ontology archive selected current Source facts changed')
        self.SS.fresh_selected_source(self.source,self.family)
        need(self.mapper is self.P.source.current_legacy_delivery().MAPPED,'actual current mapper object changed')
    def capture(self):
        self.guard();c=self.control;P=self.P
        head_raw=self.host.vault.material(c['head_binding']);manifest_raw=self.host.vault.material(c['manifest_binding'])
        expected=self.host.vault.material(c['native_read_binding']);reply_raw=self.host.vault.material(c['projection_receipt_binding'])
        head,manifest,reply=(P.frame_parse(raw) for raw in (head_raw,manifest_raw,reply_raw))
        need(reply['schema_version']=='lab-ontology-projection-receipt/v1-candidate' and reply['posture']=='applied'
             and reply['lab_source_cut']==c['source_cut'] and reply['mapping_binding']==c['mapping_binding']
             and reply['ontology_applied_cut']['store_ref']==c['store_ref'] and reply['ontology_applied_cut']['commit_sha256']==P.source.sha(head_raw)
             and head['generation_sha256']==P.source.sha(manifest_raw) and head['store_ref']==c['store_ref']
             and manifest['lab_source_cut']==c['source_cut'] and manifest['mapping_binding']==c['mapping_binding']
             and manifest['native_read_sha256']==P.source.sha(expected),'actual public projection/head/manifest/native correspondence differs')
        root=Path(c['generation_root']);need(root.is_absolute() and root.resolve()==root and not root.is_relative_to(P.ROOT)
            and not root.is_symlink() and not any(p.is_symlink() for p in root.parents),'independently selected external generation root required')
        workspace=importlib.import_module(type(self.host).__module__.rsplit('.',1)[0]+'.workspace')
        files={};all_paths=set()
        for row in manifest['files']:
            closed(row,('path','sha256'),'closed exact native generation member required');relative=Path(row['path'])
            need(not relative.is_absolute() and relative.as_posix()==row['path'] and '..' not in relative.parts
                 and row['path'] not in all_paths,'unsafe or duplicate generation member')
            all_paths.add(row['path']);raw=workspace.read_private(root/relative)
            need(P.source.sha(raw)==row['sha256'],'retained original native generation member changed')
            if row['path'].startswith(('semantic/','governance/')):files[row['path']]=raw
        actual_paths={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        need(not any(p.is_symlink() for p in root.rglob('*')) and actual_paths==all_paths|{'manifest.json'}
             and workspace.read_private(root/'manifest.json')==manifest_raw,'retained original generation closure differs')
        package=self.mapper.HERE/'packages/0001';policy_raw=(self.mapper.HERE/'policy.json').read_bytes();mapping_raw=(package/'mapping.json').read_bytes()
        need(c['mapping_binding']==P.binding(str((self.mapper.HERE/'policy.json').relative_to(P.ROOT)),policy_raw)
             and c['mapping_original_binding']==P.binding(str((package/'mapping.json').relative_to(P.ROOT)),mapping_raw)
             and P.frame_parse(mapping_raw)['source_cut']==c['source_cut'],'actual selected original mapper policy/map differs')
        self.guard();observed=self.mapper.call([root/'semantic',root/'governance',root/'request.json']);self.guard()
        need(observed==expected,'fresh actual native replay of retained generation differs')
        replay={'schema_version':'lab-original-ontology-cold-correspondence/v1-candidate','head_binding':c['head_binding'],
          'manifest_binding':c['manifest_binding'],'native_read_binding':c['native_read_binding'],'cold_replayed':True,'authority_effect':'none'}
        replay_raw=P.compact(replay)
        return {'schema_version':'lab-original-cold-ontology-material/v1-candidate','principal_ref':self.host.channel.guard()['principal_ref'],
          'work_ref':self.work_ref,'source_cut':copy.deepcopy(c['source_cut']),'store_ref':c['store_ref'],'mapping_binding':c['mapping_binding'],
          'mapping_policy_original':policy_raw,'mapping_original_binding':c['mapping_original_binding'],'mapping_original':mapping_raw,
          'manifest_binding':c['manifest_binding'],'manifest_original':manifest_raw,'head_binding':c['head_binding'],'head_original':head_raw,
          'native_read_binding':c['native_read_binding'],'native_read_original':observed,'native_files':files,
          'cold_replay_binding':P.binding('actual-fresh-ontology-cold:'+P.source.sha(replay_raw),replay_raw),'cold_replay_original':replay_raw,
          'expires_at':self.host.channel.policy['expires_at'],'authority_effect':'none'}
