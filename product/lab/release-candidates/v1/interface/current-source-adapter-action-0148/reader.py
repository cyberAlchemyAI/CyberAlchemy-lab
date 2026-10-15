"""Explicitly pinned host source selection; complete fresh deduplicated boundary."""
from contextlib import contextmanager
from .base import *
from . import adapter
from .boundary import boundary
class SelectedReader:
    def __init__(self,adapter_pin,source_pin,package_pin):
        self.adapter_pin=adapter_pin;self.source_pin=source_pin;self.package_pin=package_pin
        self.HERE=PRODUCER_ROOT;self.adapter=adapter;self.Inspection=parent.Inspection;self.records=records
        self.guard()
    def guard(self):return boundary(self.adapter_pin,self.source_pin,self.package_pin)[3]
    def package(self,source_pin,package_pin):
        source,m,expected,_=boundary(self.adapter_pin,source_pin,package_pin)
        require(source_pin==self.source_pin and package_pin==self.package_pin,'independently selected source/package differs')
        return source,m,expected
    def selection(self,source_pin,package_pin,name):
        require(name=='custody-participation','source adapter nickname is closed')
        _,manifest,expected=self.package(source_pin,package_pin)
        return {'name':name,'archive_binding':manifest['archive_binding'],'expected_replay_binding':manifest['expected_replay_binding'],
            'config_sha256':expected['config_sha256'],'baseline_snapshot_digest':expected['baseline_snapshot_digest'],
            'expected_head':expected['expected_head'],'engine_pins':expected['engine_pins'],
            'review_binding':binding(PRODUCER_ROOT/'packages/0001/review.json'),
            'candidate_selection_basis':{'manifest_sha256':package_pin,'source_manifest_sha256':source_pin,'adapter_source_sha256':self.adapter_pin},
            'authority_effect':'none','actual_owner_outcome':None}
    @contextmanager
    def open_signed(self,source_pin,package_pin):
        selected_row=self.selection(source_pin,package_pin,'custody-participation')
        with C.open_source(source_pin,package_pin) as cold:
            view=self.Inspection(cold.data,selected_row,cold.originals,cold.handle)
            selected=adapter.SignedSources(view,source_pin,selection_reader=lambda name:self.selection(source_pin,package_pin,name))
            view.custody_signed_sources=selected
            try:
                yield selected
                selected.guard();self.guard()
            finally:selected.close()
