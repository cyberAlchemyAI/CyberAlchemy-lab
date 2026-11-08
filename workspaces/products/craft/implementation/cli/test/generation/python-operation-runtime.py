"""Independent native behavior oracle for the checked commerce Operation.

The reference store models all-or-none state/outbox updates and uncertain
acknowledgements. It is not a production durability implementation.
"""
import asyncio
import copy
import dataclasses
import importlib
import inspect
import sys
import typing
from types import MappingProxyType

sys.path.insert(0, sys.argv[1])
module = importlib.import_module(sys.argv[2])
run = getattr(module, sys.argv[3])


def account(balance="100"):
    return dict(id="account-a", balance=balance, detail=dict(amount="2"),
                labels=["b", "a"], status=dict(variant="Ready"),
                choice=dict(variant="Some", payload=dict(amount="3")))


def inputs():
    return dict(account_id="account-a", amount="10", replacement=account("90"),
                receipt=dict(id="receipt-a", amount="10"), response="accepted",
                posted_input=dict(occurrence={"occurrence-id": "one"}, payload={"account-id": "account-a", "amount": "10"}),
                audit_input=dict(occurrence={"occurrence-id": "two"}, payload={"account-id": "account-a", "amount": "10"}))


def immutable(value):
    if type(value) in (str, int, bool, float, type(None)):
        return
    if type(value) is tuple:
        for item in value:
            immutable(item)
        return
    if type(value) is MappingProxyType:
        try:
            value["__probe"] = True
        except TypeError:
            pass
        else:
            raise AssertionError("MUTABLE_MAPPING")
        for item in value.values():
            immutable(item)
        return
    assert dataclasses.is_dataclass(value), type(value)
    assert value.__dataclass_params__.frozen, "MUTABLE_DATACLASS"
    assert not hasattr(value, "__dict__"), "MUTABLE_DICT"
    for field in dataclasses.fields(value):
        immutable(getattr(value, field.name))


class Store:
    def __init__(self, **options):
        self.options = options
        self.records = {"commerce:account/account-a": account()}
        self.outbox = []
        self.trace = []
        self.batches = []
        self.revision = 0
        self.begun = asyncio.Event()
        self.committing = asyncio.Event()

    async def begin(self):
        self.trace.append("begin")
        if self.options.get("begin"):
            raise RuntimeError("begin")
        self.begun.set()
        if callback := self.options.get("on_begin"):
            callback()
        if gate := self.options.get("begin_gate"):
            await gate.wait()
        return Transaction(self)


class Transaction:
    def __init__(self, store):
        self.store = store
        self.snapshot = dict(store.records)
        self.revision = store.revision
        self.terminal = False

    async def read(self, request):
        s = self.store
        s.trace.append("read:" + request["slot"])
        assert not self.terminal
        immutable(request)
        assert request["target"] == "commerce:account"
        assert request["key"] == "account-a"
        if s.options.get("read"):
            raise RuntimeError("read")
        if s.options.get("cancel_read"):
            raise asyncio.CancelledError()
        if s.options.get("missing"):
            return None
        if s.options.get("wrong_identity"):
            return dict(account(), id="different")
        if s.options.get("bad_read"):
            return dict(account(), balance=True)
        return self.snapshot.get(request["target"] + "/" + request["key"])

    async def rollback(self):
        self.store.trace.append("rollback")
        assert not self.terminal, "ROLLBACK_AFTER_COMMIT"
        self.terminal = True
        if self.store.options.get("rollback"):
            raise RuntimeError("cleanup")

    async def commit(self, batch):
        s = self.store
        s.trace.append("commit")
        assert not self.terminal, "DUPLICATE_COMMIT"
        self.terminal = True
        immutable(batch)
        s.batches.append(batch)
        s.committing.set()
        assert [w["slot"] for w in batch.writes] == ["account-state", "receipt-state"], "WRITE_ORDER"
        assert [e["slot"] for e in batch.events] == ["posted-fact", "audit-fact"], "EVENT_ORDER"
        assert [w["mode"] for w in batch.writes] == ["replace", "create"], "WRITE_MODE"
        if self.revision != s.revision or s.options.get("commit") == "reject":
            return {"status": "rejected"}
        if s.options.get("commit") == "throw-before":
            raise RuntimeError("unknown")
        draft = dict(s.records)
        for write in batch.writes:
            key = write["target"] + "/" + write["value"]["id"]
            if (write["mode"] == "create") == (key in draft):
                return {"status": "rejected"}
            if write["mode"] == "delete":
                del draft[key]
            else:
                draft[key] = write["value"]
        s.records, s.outbox = draft, s.outbox + list(batch.events)
        s.revision += 1
        if gate := s.options.get("commit_gate"):
            await gate.wait()
        if s.options.get("commit") == "throw-after":
            raise RuntimeError("lost acknowledgement")
        if s.options.get("commit") == "cancel":
            raise asyncio.CancelledError()
        if s.options.get("commit") == "indeterminate":
            return {"status": "indeterminate"}
        if "receipt" in s.options:
            return s.options["receipt"]
        return {"status": "committed"}


def dependencies(store, clocks=None):
    def clock(label):
        def tick():
            store.trace.append("clock:" + label)
            return "time:" + label
        return tick
    return {"store": store, "clocks": clocks or {"posted-fact": clock("posted"), "audit-fact": clock("audit")}}


async def main():
    for spoof in (False, True):
        effects = []
        class ActiveMeta(type):
            def __eq__(cls, other):
                effects.append("metaclass equality")
                return spoof
        class Hostile(metaclass=ActiveMeta):
            pass
        for raw in (Hostile(), dict(inputs(), amount=Hostile())):
            s = Store()
            outcome = await run(raw, dependencies(s))
            assert outcome.status == "failed" and outcome.stage == "input", "ACTIVE_INPUT_ACCEPTED"
            assert not s.trace, "ACTIVE_INPUT_PROVIDER_EFFECT"
        assert not effects, "ACTIVE_METACLASS_EXECUTED"
    if sys.argv[4] in ("plain-enum", "sum-enum"):
        class EnumStore:
            async def begin(self):
                return self
            async def commit(self, batch):
                assert batch.writes == () and batch.events == ()
                return {"status": "committed"}
            async def rollback(self):
                raise AssertionError("UNEXPECTED_ROLLBACK")
        choices = [{"variant": "Ready"}, {"variant": "Draft"}] if sys.argv[4] == "plain-enum" else [{"variant": "Some", "payload": "18446744073709551615"}, {"variant": "None"}]
        for choice in choices:
            result = await run({"amount": 1, "choice": choice}, {"store": EnumStore()})
            assert result.status == "committed", result
            assert result.value["variant"] == choice["variant"]
            if "payload" in choice:
                assert result.value["payload"] == 18446744073709551615
            immutable(result)
        print("ENUM_OPERATION_OK")
        return
    if sys.argv[4] == "scalar":
        class ScalarTransaction:
            def __init__(self):
                self.trace = []
            async def read(self, request):
                raise AssertionError("UNDECLARED_READ")
            async def rollback(self):
                self.trace.append("rollback")
            async def commit(self, batch):
                immutable(batch)
                assert batch.writes == () and batch.events == ()
                self.trace.append("commit")
                return {"status": "committed"}
        class ScalarStore:
            def __init__(self):
                self.transaction = ScalarTransaction()
            async def begin(self):
                self.transaction.trace.append("begin")
                return self.transaction
        for amount in [1, "18446744073709551615"]:
            s = ScalarStore()
            result = await run({"amount": amount}, {"store": s})
            assert result.status == "committed" and result.value == int(amount)
            assert s.transaction.trace == ["begin", "commit"]
            immutable(result)
        s = ScalarStore()
        result = await run({"amount": 0}, {"store": s})
        assert result.status == "rejected" and result.continuation == "return-accept-error"
        assert s.transaction.trace == ["begin", "rollback"]
        s = ScalarStore()
        assert (await run({"amount": True}, {"store": s})).code == "OPERATION_INPUT"
        assert not s.transaction.trace
        print("SCALAR_OPERATION_OK")
        return
    if sys.argv[4] == "record":
        value, s = inputs(), Store()
        value["result_account"] = account()
        result = await run(value, dependencies(s))
        assert result.status == "committed" and result.value["id"] == "account-a"
        immutable(result)
        value["result_account"]["detail"]["amount"] = "0"
        assert result.value["detail"]["amount"] == 2
        s = Store()
        result = await run(value, dependencies(s))
        assert result.status == "failed" and result.stage == "result", result
        assert s.trace == ["begin", "read:current-account", "clock:posted", "clock:audit", "rollback"]
        assert not s.outbox and len(s.records) == 1
        print("RECORD_OPERATION_OK")
        return
    assert inspect.iscoroutinefunction(type(run).__call__)
    assert len(inspect.signature(run).parameters) == 2
    assert set(typing.get_type_hints(module.OperationInput)) == set(inputs())
    assert typing.get_type_hints(module.OperationBatch)["writes"] == tuple[module.WriteIntent, ...]
    immutable(run.descriptor)
    assert run.descriptor["effect_contract"] == "state-and-outbox"
    assert run.descriptor["primary_callable_count"] == 1
    assert run.descriptor["provider_durability_claim"] is False
    try:
        run.extra = True
    except (AttributeError, TypeError):
        pass
    else:
        raise AssertionError("MUTABLE_OPERATION")

    s, value = Store(), inputs()
    monitored = []
    observing = False
    def audit(event, args):
        if observing and (event in ("open", "import", "exec", "compile") or event.startswith(("os.", "socket.", "subprocess.", "ctypes."))):
            monitored.append(event)
    sys.addaudithook(audit)
    observing = True
    try:
        result = await run(value, dependencies(s))
        immutable(result)
        immutable(s.batches[0])
    finally:
        observing = False
    assert not monitored, ("AMBIENT_EFFECT", monitored)
    assert result.status == "committed", result
    assert result.value == "accepted", "WRONG_RESULT"
    assert s.trace == ["begin", "read:current-account", "clock:posted", "clock:audit", "commit"], s.trace
    assert s.records["commerce:account/account-a"]["balance"] == 90
    assert s.records["commerce:receipt/receipt-a"]["amount"] == 10
    assert len(s.outbox) == 2
    assert [e["value"].occurrence["occurrence-id"] for e in s.outbox] == ["one", "two"]
    assert [e["value"].occurredAt for e in s.outbox] == ["time:posted", "time:audit"]
    assert s.outbox[0]["value"] is not s.outbox[1]["value"]
    immutable(result)
    value["replacement"]["detail"]["amount"] = "999"
    value["posted_input"]["payload"]["amount"] = "999"
    assert s.records["commerce:account/account-a"]["detail"]["amount"] == 2
    assert s.outbox[0]["value"].payload["amount"] == 10

    cases = [
        ({"begin": True}, "failed", "begin", "BEGIN_FAILED", False),
        ({"read": True}, "failed", "read", "OPERATION_FAILED", False),
        ({"cancel_read": True}, "failed", "read", "OPERATION_FAILED", False),
        ({"read": True, "rollback": True}, "failed", "read", "OPERATION_FAILED", False),
        ({"missing": True}, "failed", "read", "READ_NOT_FOUND", False),
        ({"wrong_identity": True}, "failed", "read", "READ_IDENTITY_MISMATCH", False),
        ({"bad_read": True}, "failed", "read", "OPERATION_FAILED", False),
        ({"commit": "reject"}, "rejected", "commit", "COMMIT_REJECTED", False),
        ({"commit": "throw-before"}, "indeterminate", "commit", "COMMIT_UNCERTAIN", False),
        ({"commit": "throw-after"}, "indeterminate", "commit", "COMMIT_UNCERTAIN", True),
        ({"commit": "cancel"}, "indeterminate", "commit", "COMMIT_UNCERTAIN", True),
        ({"commit": "indeterminate"}, "indeterminate", "commit", "COMMIT_INDETERMINATE", True),
    ]
    for options, status, stage, code, committed in cases:
        s = Store(**options)
        result = await run(inputs(), dependencies(s))
        assert (result.status, result.stage, result.code) == (status, stage, code), (options, result)
        assert result.continuation == "return-post-error"
        assert result.cleanupFailed is bool(options.get("rollback"))
        assert len(s.outbox) == (2 if committed else 0)
        assert len(s.records) == (2 if committed else 1)
        assert s.trace.count("commit") == (1 if stage == "commit" else 0)
        assert s.trace.count("rollback") == (1 if stage == "read" else 0)
        immutable(result)

    class Active(dict):
        def __getitem__(self, key):
            raise AssertionError("ACTIVE_RECEIPT")
    for receipt in [None, {}, [], {"status": "bad"}, {"status": True}, {"status": "committed", "extra": True}, Active(status="committed")]:
        s = Store(receipt=receipt)
        result = await run(inputs(), dependencies(s))
        assert result.status == "indeterminate" and result.code == "INVALID_COMMIT_RECEIPT", result
        assert s.trace.count("commit") == 1 and "rollback" not in s.trace

    # Guard order, every declared guard, factory validation before any clock,
    # and Event input validation before commit.
    for field, replacement, stage, status, code in [
        (("amount",), "100", "guard", "rejected", "RULE_REJECTED:commerce:can-post"),
        (("receipt", "amount"), "11", "guard", "rejected", "RULE_REJECTED:commerce:receipt-matches"),
        (("replacement", "balance"), "0", "write-validation", "failed", "OPERATION_FAILED"),
        (("replacement", "detail", "amount"), "0", "write-validation", "failed", "OPERATION_FAILED"),
        (("replacement", "choice", "payload", "amount"), "0", "write-validation", "failed", "OPERATION_FAILED"),
        (("posted_input", "payload", "amount"), "bad", "event", "failed", "OPERATION_FAILED"),
    ]:
        value, s = inputs(), Store()
        owner = value
        for segment in field[:-1]:
            owner = owner[segment]
        owner[field[-1]] = replacement
        result = await run(value, dependencies(s))
        assert (result.status, result.stage, result.code) == (status, stage, code), (field, result)
        assert s.trace == ["begin", "read:current-account", "rollback"], s.trace
        assert len(s.outbox) == 0 and len(s.records) == 1

    for malformed in [True, -1, 1.0, "01", "18446744073709551616", "-0", " 1", "١"]:
        value, s = inputs(), Store()
        value["amount"] = malformed
        result = await run(value, dependencies(s))
        assert result.status == "failed" and result.code == "OPERATION_INPUT", (malformed, result)
        assert not s.trace
    for malformed in [None, [], Active(inputs()), dict(inputs(), extra=True)]:
        s = Store()
        result = await run(malformed, dependencies(s))
        assert result.code == "OPERATION_INPUT" and not s.trace
    value = inputs()
    value["extra"] = value
    s = Store()
    assert (await run(value, dependencies(s))).code == "OPERATION_INPUT" and not s.trace

    # Capture must precede the first provider await, including detached Event
    # inputs and the clock function references.
    value, gate = inputs(), asyncio.Event()
    s = Store(begin_gate=gate)
    deps = dependencies(s)
    pending = asyncio.create_task(run(value, deps))
    await s.begun.wait()
    value["response"] = "wrong"
    value["replacement"]["balance"] = "0"
    value["posted_input"]["occurrence"]["occurrence-id"] = "changed"
    deps["clocks"]["posted-fact"] = lambda: "changed-clock"
    gate.set()
    result = await pending
    assert result.status == "committed" and result.value == "accepted", "LATE_CAPTURE"
    assert s.outbox[0]["value"].occurrence["occurrence-id"] == "one", "LATE_EVENT_CAPTURE"
    assert s.outbox[0]["value"].occurredAt == "time:posted", "LATE_CLOCK_CAPTURE"

    # Completion must await settlement; cancellation after commit is uncertain.
    for cancel in [False, True]:
        gate, s = asyncio.Event(), Store()
        s.options["commit_gate"] = gate
        pending = asyncio.create_task(run(inputs(), dependencies(s)))
        await s.committing.wait()
        assert not pending.done()
        if cancel:
            pending.cancel()
        else:
            gate.set()
        result = await pending
        assert result.status == ("indeterminate" if cancel else "committed"), result
        assert "rollback" not in s.trace and s.trace.count("commit") == 1

    # Explicit clock failure is precommit; no ambient-clock fallback.
    s = Store()
    def broken():
        raise RuntimeError("clock")
    deps = dependencies(s)
    deps["clocks"]["posted-fact"] = broken
    result = await run(inputs(), deps)
    assert result.status == "failed" and result.stage == "event"
    assert s.trace == ["begin", "read:current-account", "rollback"]
    print("OPERATION_RUNTIME_OK")


asyncio.run(main())
