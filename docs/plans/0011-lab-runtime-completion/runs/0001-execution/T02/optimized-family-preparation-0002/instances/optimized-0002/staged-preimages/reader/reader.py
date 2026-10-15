"""Host selects exact adapter code, source and package independently."""
from contextlib import contextmanager
from .base import *
from . import adapter
from .inspection import Inspection

class CurrentFixtureReader:
    def __init__(self, adapter_pin, source_pin, package_pin):
        self.adapter_pin=adapter_pin
        self.source_pin=source_pin;self.package_pin=package_pin
        self.HERE=PRODUCER_ROOT
        self.adapter=adapter
        self.Inspection=Inspection
        self.records=records
        self.guard()
    def guard(self):
        path=ADAPTER_ROOT/'source-manifest.json'
        require(sha(path.read_bytes())==self.adapter_pin,'independent current source adapter pin differs')
        manifest=load(path)
        require(manifest['authority_effect']=='none' and manifest['actual_owner_outcome'] is None,'source adapter grants no authority')
        for row in manifest['files']:original(row)
        require(manifest['producer_source_binding']==binding(PRODUCER_ROOT/'source-manifest.json') and manifest['producer_package_binding']==binding(PRODUCER_ROOT/'packages/0001/manifest.json'),'new source adapter selects another producer')
        require(manifest['producer_source_binding']['sha256']==self.source_pin and manifest['producer_package_binding']['sha256']==self.package_pin,'independent producer pins differ')
        verify_source(self.source_pin)
        return manifest
    def package(self, source_pin, package_pin):
        self.guard()
        require(source_pin==self.source_pin and package_pin==self.package_pin,'independently selected new source/package differs')
        manifest,expected,_=C.package(source_pin,package_pin)
        return verify_source(source_pin),manifest,expected
    def selection(self, source_pin, package_pin, name):
        require(name=='custody-participation','source adapter nickname is closed')
        _,manifest,expected=self.package(source_pin,package_pin)
        return {'name':name,'archive_binding':manifest['archive_binding'],'expected_replay_binding':manifest['expected_replay_binding'],
                'config_sha256':expected['config_sha256'],'baseline_snapshot_digest':expected['baseline_snapshot_digest'],
                'expected_head':expected['expected_head'],'engine_pins':expected['engine_pins'],
                'review_binding':binding(PRODUCER_ROOT/'packages/0001/review.json'),
                'candidate_selection_basis':{'manifest_sha256':package_pin,'source_manifest_sha256':source_pin,'adapter_source_sha256':self.adapter_pin},
                'authority_effect':'none','actual_owner_outcome':None}
    @contextmanager
    def open_signed(self, source_pin, package_pin):
        self.package(source_pin,package_pin)
        selected_row=self.selection(source_pin,package_pin,'custody-participation')
        with C.open_source(source_pin,package_pin) as cold:
            view=Inspection(cold.data,selected_row,cold.originals,cold.handle)
            selected=adapter.SignedSources(view,source_pin,selection_reader=lambda name:self.selection(source_pin,package_pin,name))
            view.custody_signed_sources=selected
            try:
                yield selected
                selected.guard()
                self.guard()
            finally:selected.close()
