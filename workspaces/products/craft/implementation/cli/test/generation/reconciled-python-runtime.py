"""Native all-type package join: authored expectations, never renderer execution."""
import ast
import asyncio
from dataclasses import FrozenInstanceError
import importlib
import json
import pathlib
import sys

data = json.load(sys.stdin)
sys.path.insert(0, data['root'])
plan = data['plan']
modules = {}
for row in plan['modules']:
    source = pathlib.Path(data['root'], row['relative_path']).read_text()
    tree = ast.parse(source)
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                for name in target.elts if isinstance(target, ast.Tuple) else [target]:
                    assert isinstance(name, ast.Name)
                    names.add(name.id)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            assert isinstance(node.target, ast.Name)
            names.add(node.target.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update(a.asname or a.name.split('.')[0] for a in node.names)
    assert sorted(names) == row['bindings'], row['relative_path']
    module = importlib.import_module(row['relative_path'][:-3].replace('/', '.'))
    for selector in row['qualified_selectors']:
        if '/_providers/' not in row['relative_path']:
            modules[selector] = module

assert len({kind for row in plan['modules'] for kind in row['metatypes']}) == 13
assert modules['alpha:mode'].Mode is not modules['beta:mode'].Mode
assert modules['alpha:allowed'].rule_allowed({'value': True}) is True
assert modules['alpha:allowed'].rule_allowed({'value': False}) is False
assert modules['alpha:total'].calculate_total({}) == 18446744073709551615
assert modules['beta:total'].calculate_total({}) == 7

def reject(call):
    try:
        call()
    except TypeError:
        return
    raise AssertionError('INVALID_VALUE_ACCEPTED')

reject(lambda: modules['alpha:legacy-total'].calculate_legacy_total({'amount': True}))
assert modules['alpha:legacy-total'].calculate_legacy_total({'amount': '9007199254740993'}) == 9007199254740993
money_factory = modules['alpha:money'].create_money_factory()
money = money_factory.create({'amount': '9'}).value
other_money = money_factory.create({'amount': '10'}).value
assert money != other_money
assert money == money_factory.create({'amount': 9}).value
mode = modules['alpha:mode'].parse_mode('On')
order_factory = modules['alpha:order'].create_order_factory()
owned = {'id': 'order-1', 'amount': '9', 'money': money, 'mode': mode}
order = order_factory.create(owned).value
assert order is not None
same_identity = order_factory.create(dict(owned, amount='10', money=other_money)).value
assert order == same_identity and hash(order) == hash(same_identity)
assert order_factory.create(dict(owned, id='')).ok is False
assert order_factory.create(dict(owned, money={'amount': '9'})).ok is False
try:
    order.fields.amount = 1
except FrozenInstanceError:
    pass
else:
    raise AssertionError('MUTABLE_FACTORY_SNAPSHOT')
answer = modules['alpha:answer'].create_answer({'variant': 'Amount', 'payload': '9'})
assert answer.payload == 9
reject(lambda: modules['alpha:answer'].create_answer({'variant': 'Amount', 'payload': True}))

raw = {'id': 'order-1', 'amount': '9', 'money': {'amount': '9'}, 'mode': {'variant': 'On'}}
rows = modules['alpha:find'].query_find([raw, dict(raw, id='order-2')], {})
assert [r['id'] for r in rows] == ['order-1', 'order-2']
assert rows[0]['amount'] == 9
reject(lambda: modules['alpha:find'].query_find([dict(raw, amount=True)], {}))
adjusted = modules['alpha:adjust'].mapping_adjust({'total': '9007199254740993'})
assert adjusted['amount'] == 9007199254740993 and len(adjusted.entries) == 1
assert modules['alpha:choose'].policy_choose({'value': True}) == 'alpha:post'
assert modules['alpha:choose'].policy_choose({'value': False}) == 'alpha:total'
summary = modules['alpha:summary'].mapping_summary({'order': raw, 'total': '18446744073709551615'})
assert summary['id'] == 'order-1' and summary['total'] == 18446744073709551615
api = modules['alpha:api']
assert api.public_contracts['response'].normalize(summary)['total'] == 18446744073709551615
assert api.accepts_consumer_version('1.0.0') and not api.accepts_consumer_version('2.0.0')

event_input = {'occurrence': {'event-id': '12345678-1234-4234-8234-123456789abc'}, 'occurredAt': 'fixed-time', 'payload': {}}
event = modules['alpha:posted'].event_posted(event_input)
assert event.type == 'posted' and event.version == '1' and event.occurredAt == 'fixed-time'
state = modules['alpha:lifecycle']
changed = state.transition_lifecycle(state.initial_state, state.Trigger('alpha:posted'), {'value': True})
assert changed.status == 'transitioned' and changed.state.value == 'posted'
assert state.transition_lifecycle(state.initial_state, state.Trigger('alpha:posted'), {'value': False}).status == 'rejected'

class Transaction:
    def __init__(self, store):
        self.store = store
    async def read(self, request):
        raise AssertionError('UNDECLARED_READ')
    async def rollback(self):
        self.store.trace.append('rollback')
    async def commit(self, batch):
        self.store.trace.append('commit')
        assert batch.writes == () and len(batch.events) == 1
        assert batch.events[0]['target'] == 'alpha:posted'
        assert batch.events[0]['value'].type == 'posted'
        await asyncio.sleep(0)
        return {'status': self.store.status}

class Store:
    def __init__(self, status='committed'):
        self.trace, self.status = [], status
    async def begin(self):
        self.trace.append('begin')
        return Transaction(self)

async def execute():
    run = modules['alpha:post'].operation_post
    store = Store()
    result = await run({'order': raw, 'notice_input': event_input}, {'store': store})
    assert result.status == 'committed', result
    assert result.value['id'] == 'order-1' and store.trace == ['begin', 'commit']
    bad = Store()
    result = await run({'order': dict(raw, amount=True), 'notice_input': event_input}, {'store': bad})
    assert result.status == 'failed' and bad.trace == []
    store = Store()
    workflow = await modules['alpha:flow'].workflow_flow({'order': raw, 'notice': event_input}, {'workflow_execution_id': 'run-1', 'failure_occurrence_id': 'failure-1'}, {'alpha:post': {'store': store}})
    assert workflow.status == 'succeeded', workflow
    assert workflow.value['id'] == 'order-1' and store.trace == ['begin', 'commit']
    assert workflow.recovery_bindings is None

asyncio.run(execute())
print(json.dumps({'native_imports': len(plan['modules']), 'metatypes': 13, 'joined_behavior': True}))
