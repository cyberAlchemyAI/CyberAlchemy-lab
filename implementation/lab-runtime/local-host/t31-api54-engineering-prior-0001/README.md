# T31 engineering prior-output API successor

API54 selects the original public engineering workflow with its current decision-profile header and preserves the public `intent-resolution`, `work`, and `implementation` first-phase inputs. It removes the agent-context Work-substitution shortcut from this engineering route. The disjoint `workflow-transition-v2-t31` kernel accepts a distinct `produced-current` posture only for `transition:engineering:implemented`'s GeneratedOutput input; it continues to require exact signed-Source current posture for Intent, Resolution, Work, Coordination, and every other input.

The new `workflow_prior_input.py` proves that this GeneratedOutput is the sole output of the immediately preceding committed `engineering:designed` event in the same owned WorkflowRun, Source cut, Work, Actor, and journal head. It reopens the selected sealed private original output bytes and checks their header, body, and digest. It does not call this output admitted to signed Source. The original design producer already exists as `DesignStageProducer`; API54 does not call it or append a WorkflowRun.

The [cold receipt](RESULT.json) binds source manifest `030cadf77f52b44d6f83d4004c74d21e7c0cfd8443de33110cdd98c0ad989e44` and profile `a38cd23816cbf8e624fd1b44913c3b84af9f7fb52faa864727c59eab2e3c2dbe`. The selected source guard passes. Eight focused tests pass in normal and optimized Python, including input-substitution, wrong phase, source Work substitution, uncommitted/foreign event, wrong slot, wrong Work/cut and changed original bytes.

This is cold product code only. It awaits a freshly signed W03 Source/Reader/Mapper/Context with exact producer Work and a workflow-local Principal/Assignment, then genuine design producer output, committed WorkflowRun and later consumer. The original observed count remains **4/28**. The ce4/API53 agent-context refusal is preserved.

```bash
python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t31-api54-engineering-prior-0001 -p 'test_*.py' -v
python3 -O -B -m unittest discover -s implementation/lab-runtime/local-host/t31-api54-engineering-prior-0001 -p 'test_*.py' -v
```
