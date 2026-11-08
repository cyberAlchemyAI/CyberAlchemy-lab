"""Versioned actual-clock Session expiry test for the selected API33 runtime.

The original test's 70-second opening budget expired during guarded native
verification before a Session/timer existed. This changes only that test's
budget and wait; the selected API33 implementation remains unchanged.
"""
from __future__ import annotations

import time
from datetime import timedelta

OPEN_DEADLINE_SECONDS = 360
TIMER_COMPLETION_GRACE_SECONDS = 120


def successor_class(base, module):
    now = module.now

    class Sessions(base):
        def test_27_actual_expiry_timer_disposes(self):
            call = self.opening()
            call["message"]["budget"]["deadline"] = (
                now() + timedelta(seconds=OPEN_DEADLINE_SECONDS)
            ).isoformat()
            opened = self.success(call)
            self.assertEqual(opened["posture"], "active")
            resource = self.service.sessions.live[opened["session_ref"]]
            self.opened_result = opened
            self.resource = resource
            resource.note(b"private-note-expiring-in-real-time")
            held = resource.memory[0]

            # The selected implementation may shorten the requested deadline.
            # Observe its actual issued expiry and wait for its real timer.
            remaining = max(0.0, (resource.expires - now()).total_seconds())
            self.assertGreater(remaining, 0.0, "opened Session already expired")
            cutoff = time.monotonic() + remaining + TIMER_COMPLETION_GRACE_SECONDS
            while not resource.closed and time.monotonic() < cutoff:
                time.sleep(0.2)
            self.assertTrue(resource.closed, "real deadline disposal timer did not finish")
            self.assertEqual(held, bytearray(len(held)))
            self.assertEqual(self.success(self.inspection(opened["session_ref"]))["posture"],
                             "expired")

    # Keep the inherited class's distinct source-module identity in case
    # receipts; both selected Session modules contain an identical test27.
    Sessions.__module__ = module.__name__
    Sessions.__qualname__ = base.__qualname__
    return Sessions
