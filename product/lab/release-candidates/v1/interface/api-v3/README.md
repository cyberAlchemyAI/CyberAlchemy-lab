# Lab candidate reader with catalog representations

This successor adds exact catalog metadata representations and ten separately reviewable connection correction candidates. It implements `lab.status`, `catalog.get`, `artifact.inspect` and `artifact.query` over independently selected saved signed candidate archives.

Start `serve.py` with an independently provisioned public reader policy, its expected SHA and `--protocol-profile-sha256` selected from the exact reviewed `contract-profile.json`. The client proves possession of its private reader key over the host's one-use challenge. Private credentials remain in owned fixtures and are not exported with evidence.

Calls use `lab-api-call/v2-candidate`, name the host-created opaque context and select `expected_contract_profile_binding`. Replies use `lab-api-reply/v2-candidate` and disclose their actual contract profile. Read authorization is limited to zero actions and the exact selected archive scope.

`artifact.inspect` exposes original domain instances through the original domain envelope. Captured Artifact Type declarations use `lab-catalog-representation-envelope/v1-candidate`. The exact selected metadata body, parent bytes and instance schema are distinct. Optional sections retain selective disclosure.

See [design](DESIGN.md), [profile](contract-profile.json), [catalog representation map](catalog-representations.json), and [connection correction candidates](connection-corrections/manifest.json).

Validation runs under the already recorded development authorization:

```bash
python3 -m unittest discover -s product/lab/release-candidates/v1/interface/api-v3 -p 'test_*.py' -v
```

This remains an incomplete R03 candidate. A validation result creates no canonical admission, human pilot outcome, store mutation or release authority.
