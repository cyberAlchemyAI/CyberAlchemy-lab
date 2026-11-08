"""Load the exact Root-selected bridge bytes for one inactive read scope."""
from __future__ import annotations

from contextlib import contextmanager
import sys
import types

from .binding_adapter import RootBoundCapture
from .path_contract import require

MODULE_NAME = '_t35_external_runtime_capture'
BRIDGE_KEY = 'runtime_bridge'


@contextmanager
def selected_read_scope(capture: RootBoundCapture):
    """Bind generated reads to selected snapshot code, never ambient sys.path."""
    require(type(capture) is RootBoundCapture and MODULE_NAME not in sys.modules,
            'exact unoccupied selected runtime bridge required')
    intent = capture.inputs.intent
    row = intent['code_bindings'].get(BRIDGE_KEY)
    require(row is not None and capture.inputs.rows.get(row['path']) == row,
            'Root-selected runtime bridge absent')
    raw = capture.inputs.read(row, maximum=256 * 1024)
    module = types.ModuleType(MODULE_NAME)
    module.__file__ = str(capture.layout.snapshot / row['path'])
    sys.modules[MODULE_NAME] = module
    try:
        exec(compile(raw, module.__file__, 'exec', dont_inherit=True), module.__dict__)
        require(callable(module.selected_read_scope) and callable(module.read) and
                callable(module.verify_inputs) and callable(module.run_native),
                'selected runtime bridge shape differs')
        with module.selected_read_scope(capture):
            yield
    finally:
        if sys.modules.get(MODULE_NAME) is module:
            del sys.modules[MODULE_NAME]
