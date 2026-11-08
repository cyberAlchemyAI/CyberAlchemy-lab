# Fresh local Source8-shaped fixture

Create a disposable, locally signed 24-hour Source, 30-minute Reader, 20-minute Context, and 900-second Session family under a new private directory. The constructor uses the existing synthetic eight-record builder and never modifies or renews the historical periods. Its self-issued keys are test inputs, not enrolled Lab authority.

```bash
mkdir -m 700 /tmp/cal-source8-local-fixtures
python3.14 -I -B implementation/lab-runtime/local-host/source8-current-fixture/fresh_family.py /tmp/cal-source8-local-fixtures --create
python3.14 -I -B implementation/lab-runtime/local-host/source8-current-fixture/fresh_family.py /tmp/cal-source8-local-fixtures --select RUN_ID_FROM_CREATE
python3.14 -I -B implementation/lab-runtime/local-host/source8-current-fixture/test_fresh_family.py
```

Each run ID and output directory is single use. Selection cold-verifies the signed archive, public policy chain, deadlines, original period hash, and exact constructor identity. The output contains private fixture keys; keep the directory private and remove it when no longer needed.

This proves a fresh synthetic fixture path only.

The separate native successor runner has also completed a current locally signed Source → two cold replays → Reader → Mapper → Context family. Its exact public phase and period bindings are in [NATIVE-CHAIN-RECEIPT-0001.json](NATIVE-CHAIN-RECEIPT-0001.json). The selected protected archive remains in an owner-only external `/tmp` directory; no key or snapshot belongs in this checkout. The native family uses a clean external copy of the 1,010 pinned installed runtime files, because the historical installation accumulated unselected Python caches and the current host liblzma source bytes changed. Both older failed attempts remain intact for diagnosis.

API30 still pins expired reader, store, and Context origins. A disjoint API successor must bind this native family and pass both whole fixture classes before T02 can be called complete. This local family does not enroll protected Source8 issuers or grants.
