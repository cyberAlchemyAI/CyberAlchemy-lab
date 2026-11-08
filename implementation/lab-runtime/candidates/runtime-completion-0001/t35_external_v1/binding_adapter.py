"""Selection-aware adapter for repo-relative inputs and external stage leaves."""
from __future__ import annotations

import copy
import hashlib
import json

from .constructor_paths import selected_stage_30
from .held_paths import SelectedSnapshot, _read_selected
from .path_contract import check_binding, require
from .role_stage import ProductionLayout, selected_stage_rows


class RootBoundCapture:
    """Read only rows named by the selected input or 30-leaf stage closure.

    Later phase outputs need an independently selected phase receipt and are
    refused by this construction-only adapter. No caller can obtain a writer
    capability from it.
    """

    def __init__(self, selected_inputs: SelectedSnapshot, stage_rows: list[dict]):
        require(type(selected_inputs) is SelectedSnapshot,
                'actual selected read-only snapshot required')
        self.inputs = selected_inputs
        self.layout = ProductionLayout(selected_inputs.intent)
        expected = selected_stage_rows(selected_inputs)
        require(stage_rows == expected,
                'stage rows differ from freshly rendered exact selected snapshot bytes')
        selected, controls = selected_stage_30(selected_inputs, expected)
        self._outputs = copy.deepcopy(selected)
        self._control_bytes = copy.deepcopy(controls)
        self._outputs_digest = hashlib.sha256(json.dumps(self._outputs, sort_keys=True,
                                                         separators=(',', ':')).encode()).hexdigest()

    @property
    def control_bytes(self) -> dict[str, bytes]:
        return copy.deepcopy(self._control_bytes)

    def read(self, row: dict) -> bytes:
        require(type(row) is dict and set(row) == {'path', 'sha256'},
                'exact source or stage output binding required')
        if row['path'].startswith('/'):
            check_binding(row, kind='output', family=self.layout.family)
            require(hashlib.sha256(json.dumps(self._outputs, sort_keys=True,
                                              separators=(',', ':')).encode()).hexdigest() == self._outputs_digest,
                    'selected stage output map mutated')
            require(self._outputs.get(row['path']) == row,
                    'external output absent from exact 30-leaf stage selection')
            return _read_selected(self.inputs.intent, row, kind='output')
        check_binding(row, kind='source_api')
        return self.inputs.read(row)


def activation_capability(*_args, **_kwargs):
    """No local or synthetic input can authorize effects."""
    raise RuntimeError('T02 installed custody, owner slot, Root permit and protected source are unproved')
