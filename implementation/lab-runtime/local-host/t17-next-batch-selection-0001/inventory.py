"""Cold all34 inventory and smallest fresh-family Session operation batch."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TASK = ('docs/plans/0011-lab-runtime-completion/work-pack/tasks/T17.md',
        '4d5d71bb4542ad3f3b36ea0ee9065adce5615abfb899b7dc5532ca2481009d50')
PLAN = ('docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/common-all34-selection-0278/selection-plan.json',
        '1625d9229d855796a7b32661c4a11a084b37a5352138c193de1ec8069aa0891b')
PROTOCOL = ('product/lab/release-candidates/v1/interface/api-integration-v33-t35-session-preflight-0002/protocol.py',
            'f3f24585ac712732c297ef04b4a7f31f6cd70745b60f6dd0bc5df92b40d7bcde')
READS = ('lab.status', 'catalog.get', 'artifact.query', 'artifact.inspect',
         'context.get', 'session.inspect', 'operation.inspect')
NEXT = ('session.open', 'session.close')


def pinned(binding):
    path = ROOT / binding[0]
    if not path.is_file() or path.is_symlink():
        raise ValueError('selected T17 input absent or linked')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding[1]:
        raise ValueError('selected T17 input changed: ' + binding[0])
    return raw


def supported(raw):
    bindings = {}
    def value(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return (node.value,)
        if isinstance(node, ast.Tuple):
            return sum((value(item) for item in node.elts), ())
        if isinstance(node, ast.Name):
            return bindings[node.id]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return value(node.left) + value(node.right)
        raise ValueError('unselected operation expression')
    for statement in ast.parse(raw).body:
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1 and isinstance(statement.targets[0], ast.Name):
            if statement.targets[0].id.endswith('SUPPORTED'):
                bindings[statement.targets[0].id] = value(statement.value)
    return bindings['SUPPORTED']


def build():
    task = pinned(TASK).decode()
    if 'All34 same-family positive/negative aggregate PASS' not in task:
        raise ValueError('T17 task requirement differs')
    plan = json.loads(pinned(PLAN))
    ops = supported(pinned(PROTOCOL))
    selected = plan['operations']
    if (len(selected) != 34 or len(set(selected)) != 34 or set(plan['operation_contracts']) != set(selected)
            or len(ops) != 34 or len(set(ops)) != 34 or set(ops) != set(selected)
            or not set(READS + NEXT) <= set(selected) or set(READS) & set(NEXT)):
        raise ValueError('selected all34/current API operation inventory differs')
    return {'schema_version': 'lab-T17-next-live-batch-selection/v1-candidate',
            'selected_bindings': [{'path': p, 'sha256': h} for p, h in (TASK, PLAN, PROTOCOL)],
            'all34_operations': selected,
            'all34_count': 34,
            'historical_seven_read_operations': list(READS),
            'historical_seven_transferred_to_fresh_family': False,
            'fresh_family_selected': False,
            'next_positive_negative_batch': list(NEXT),
            'same_process_precursor': ['context.get'],
            'required_live_evidence': ['one frozen corrected Source8 source/profile/cut',
                'authenticated Reader and fresh Context delivery',
                'actual session.open positive reply and live resource',
                'schema-valid causal Actor/Agent refusal with unchanged owned effect state',
                'actual session.close positive reply, RAM disposal and no identity reuse',
                'same selected source/profile/cut for each result'],
            'operation_coverage': {op: {'fresh_family_positive': False,
                                        'fresh_family_negative': False} for op in selected},
            'authority_effect': 'none',
            'claim_ceiling': 'Exact 34-operation inventory and next two-operation live driver selection only; no T17 operation qualified.'}


if __name__ == '__main__':
    print(json.dumps(build(), indent=2, sort_keys=True))
