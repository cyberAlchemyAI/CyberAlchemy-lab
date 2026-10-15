"""Actual original API ontology HEAD/manifest/generation cold consumer.

This protocol is distinct from T32's generation HEAD. No native event/body is
converted into another protocol. Original mapper.call performs the real read.
"""
from datetime import datetime,timezone
import copy,fcntl,os,stat
from pathlib import Path
from .contracts import closed,need,sha,compact,parse,relative,verify_files
from .receipt_store import ReceiptStore,stamp
from .origins import require_original

class OriginalOntologyColdCapture:
    def __init__(self,projection,module,software,selection,*,independent_selection_sha256):
        closed(selection,('schema_version','root_identity','principal_ref','work_ref','source_cut','store_ref','branch_ref','mapping_binding','mapping_original_binding','request_binding','expected_preimage_head_sha256','expected_generation','expires_at','authority_effect'))
        need(selection['schema_version']=='lab-original-ontology-cold-selection/v1-candidate'and selection['authority_effect']=='none'
            and sha(compact(selection))==independent_selection_sha256,'closed independent original ontology selection required')
        require_original(software,module,'ontology-projection')
        need(type(projection)is module.OntologyProjection,'actual original projection object required')
        self.projection=projection;self.module=module;self.software=software;self.selection=copy.deepcopy(selection);self.seal=compact(selection)
        self.store=ReceiptStore(projection.root,tuple(selection['root_identity']),self);self.closed=False
    def guard(self):
        need(not self.closed and compact(self.selection)==self.seal,'original ontology capture closed/selection changed')
        self.software.guard();self.software.function(self.projection.guard)()
        need(self.projection.route['store_ref']==self.selection['store_ref']and self.projection.route['branch_ref']==self.selection['branch_ref']
            and self.projection.route['mapping_binding']==self.selection['mapping_binding']and self.projection.route['expected_lab_cut']==self.selection['source_cut']
            and self.projection.policy['principal_ref']==self.selection['principal_ref'],'actual ontology original route/source/principal differs')
        need(self.selection['expires_at']==self.projection.route['expires_at'],'original ontology period cannot be renewed')
        # Original route validation above uses the original actual UTC guards.
        # Retain a direct real-time check too; no clock or producer replacement.
        expiry=datetime.fromisoformat(self.selection['expires_at'].replace('Z','+00:00'))
        need(expiry.tzinfo is not None and datetime.now(timezone.utc)<expiry,'actual original ontology permission expired')
        self.store.check()
    def public(self,binding):
        closed(binding,('ref','sha256'));path=Path(self.module.ROOT)/relative(binding['ref'])
        raw=self.software.read_public({'path':str(path),'sha256':binding['sha256']});need(sha(raw)==binding['sha256'],'selected original public ontology bytes differ');return raw
    def capture_selected(self):
        self.guard();s=self.selection;lock=os.open('.selection.lock',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=self.store.fd)
        try:
            selected=os.fstat(lock);need(stat.S_ISREG(selected.st_mode)and selected.st_uid==os.getuid()and stat.S_IMODE(selected.st_mode)==0o600 and selected.st_size==0 and selected.st_nlink==1,'original ontology lock differs')
            fcntl.flock(lock,fcntl.LOCK_SH|fcntl.LOCK_NB)
            need(stamp(os.stat('.selection.lock',dir_fd=self.store.fd,follow_symlinks=False))==stamp(selected),'original ontology lock attachment differs')
            head_raw=self.store.read(self.store.fd,'HEAD.json');head=parse(head_raw)
            closed(head,('schema_version','sequence','store_ref','branch_ref','parent_head_sha256','generation','generation_sha256'))
            need(head['schema_version']=='lab-owned-ontology-head/v1-candidate'and type(head['sequence'])is int and head['sequence']>0
                and head['store_ref']==s['store_ref']and head['branch_ref']==s['branch_ref']and head['generation']==s['expected_generation']
                and head['parent_head_sha256']==s['expected_preimage_head_sha256'],'actual completed original ontology operation differs')
            need(type(head['generation'])is str and head['generation'].startswith('generation-')and '/'not in head['generation']and '\\'not in head['generation'],'exact original ontology generation required')
            generation=self.store.directory(self.store.fd,head['generation']);manifest_raw=self.store.read(generation,'manifest.json')
            need(sha(manifest_raw)==head['generation_sha256'],'actual original head/manifest differs');manifest=parse(manifest_raw)
            need(manifest['mapping_binding']==s['mapping_binding']and manifest['lab_source_cut']==s['source_cut']and manifest['request_binding']==s['request_binding'],'original mapping/source/request correspondence differs')
            expected={}
            for row in manifest['files']:
                closed(row,('path','sha256'));name=relative(row['path']);need(name not in expected,'duplicate original ontology member');expected[name]=row['sha256']
            captured=self.store.snapshot(generation,set(expected)|{'manifest.json'});need(captured.pop('manifest.json')==manifest_raw,'original ontology manifest changed');verify_files(captured,expected)
            # Policy and actual row mapping are distinct original files.
            mapping_policy_raw=self.public(s['mapping_binding']);mapping_raw=self.public(s['mapping_original_binding'])
            need(s['mapping_original_binding']['ref']==str((self.module.MAPPER/'packages/0001/mapping.json').relative_to(self.module.ROOT)),'actual original mapping.json origin differs')
            mapping=parse(mapping_raw);need(mapping['source_cut']==s['source_cut'],'actual original mapping source cut differs')
            require_paths={p for p in captured if p.startswith(('semantic/','governance/'))or p=='request.json'}
            need(require_paths and 'request.json'in require_paths,'complete original native event/request closure absent')
            native_files={p:captured[p]for p in require_paths if p!='request.json'}
            self.guard();self.software.function(self.projection.mapper.call)
            fixed=self.projection.root/head['generation']
            # Explicit locator adaptation to this controller's held generation
            # directory. Child access does not depend on inheriting our FDs.
            held_generation=Path('/proc')/str(os.getpid())/'fd'/str(generation)
            native_raw=self.projection.mapper.call([held_generation/'semantic',held_generation/'governance',held_generation/'request.json'])
            need(type(native_raw)is bytes and sha(native_raw)==manifest['native_read_sha256'],'actual original fixed-generation mapper read differs')
            need(self.store.snapshot(generation,set(expected)|{'manifest.json'})=={**captured,'manifest.json':manifest_raw}
                and self.store.read(self.store.fd,'HEAD.json')==head_raw,'actual ontology generation/head changed during cold replay')
            # Reinvoke original head verifier too: no wrapper flags substitute
            # for the original native/manifest/whole-file consumer semantics.
            need(self.software.function(self.projection.head)()==(head,head_raw),'original actual head consumer differs')
            self.guard();need(stamp(os.fstat(lock))==stamp(selected)==stamp(os.stat('.selection.lock',dir_fd=self.store.fd,follow_symlinks=False)),'original ontology lock detached')
            head_binding={'ref':str(self.projection.root/'HEAD.json'),'sha256':sha(head_raw)}
            manifest_binding={'ref':str(fixed/'manifest.json'),'sha256':sha(manifest_raw)}
            native_binding={'ref':'actual-original-mapper-stdout:'+sha(native_raw),'sha256':sha(native_raw)}
            replay={'schema_version':'lab-original-ontology-cold-correspondence/v1-candidate','head_binding':head_binding,
                'manifest_binding':manifest_binding,'native_read_binding':native_binding,'cold_replayed':True,'authority_effect':'none'}
            replay_raw=compact(replay)
            return {'schema_version':'lab-original-cold-ontology-material/v1-candidate','principal_ref':s['principal_ref'],'work_ref':s['work_ref'],
                'source_cut':s['source_cut'],'store_ref':s['store_ref'],'mapping_binding':s['mapping_binding'],'mapping_original_binding':s['mapping_original_binding'],
                'mapping_policy_original':mapping_policy_raw,'mapping_original':mapping_raw,'manifest_binding':manifest_binding,'manifest_original':manifest_raw,'head_binding':head_binding,'head_original':head_raw,
                'native_read_binding':native_binding,'native_read_original':native_raw,'native_files':native_files,
                'cold_replay_binding':{'ref':'actual-original-ontology-cold-observation:'+sha(replay_raw),'sha256':sha(replay_raw)},'cold_replay_original':replay_raw,
                'expires_at':s['expires_at'],'authority_effect':'none'}
        finally:fcntl.flock(lock,fcntl.LOCK_UN);os.close(lock)
    def close(self):
        self.closed=True;self.store.close()
