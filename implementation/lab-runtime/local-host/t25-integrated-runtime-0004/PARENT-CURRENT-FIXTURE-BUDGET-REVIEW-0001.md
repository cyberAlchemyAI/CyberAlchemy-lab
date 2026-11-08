# Independent review of a new bounded fixture session budget

Reviewed auth_schema_current_budget_0001.py and independently reran all six full Draft2020-12 cases in normal and optimized Python; both passed. The new current-Legacy base variant is split from the old source-name variant, so the historical selectors retain their 900-second maximum. Only the explicitly current-Legacy base and dedicated Lesson read/application session-control branches admit a maximum of 3600. Source8 and history stay unchanged; zero, boolean and overlong values refuse, and a complete current policy matches exactly one variant.

This changes schema syntax for a separately constructed bounded local fixture. It does not extend an existing grant, source period, View, Session or caller deadline. Actual runtime and fixture caps must be declared coherently before signing and must continue enforcing the minimum of every current authority/lease boundary. A current 900-second family does not become a 3600-second family merely because schema validation succeeds.

No blocking finding in the narrow schema successor. Actual new family construction and the complete real-clock lifecycle remain required. No expired application or earlier indeterminate result is upgraded by this review.

Helper SHA: 4e53b772ce4cd35d8e27bd52fd6b12f6a247dcf2c89bb5c36bea78465e15f77c
