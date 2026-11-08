# T35 native-v4 phase observer

This is the explicit callback observer for the fresh d95 Source8 fixture and the frozen `api-integration-v33-t03-one-lesson-native-v4-0004` API. `selected-boundaries.json` binds 15 callback or pure-scope definitions to that API's source manifest and exact file hashes. `observe.py` rejects a changed selection, a substituted callback, or changed source bytes before counting an event. Only callbacks explicitly routed through it are measured.

The source period, Reader lease, Context delivery lease, and Session lease are separate UTC deadlines. The paired T35 runner records monotonic durations and an expired opening refusal in an owned temporary workspace. This observer has no authority effect and does not infer nested callback counts.
