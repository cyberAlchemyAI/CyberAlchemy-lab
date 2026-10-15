# Diagnose first, then compare transport candidates

F1/F4, I1/I2, and K1/K2 leave two incompatible finite accounts live. F2/F3 supplies an anomaly: the preferred mat changes signed displacement from 3 to 4 at the reference setting. FRICTION attributes the mat increment to pulse direction and predicts zero yaw everywhere. ROCKING attributes it to payload position times mat orientation and predicts corresponding yaw. With opposite orientation at a=1,p=1,c=0, their predictions oppose: FRICTION gives (x,yaw)=(4,0); ROCKING gives (2,-1). Neither account is established; omitted mechanisms remain unknown.

## Probe card 1: preserve the disagreement

Implement I3, containing K4's three diagnostic settings. Hold p=1,c=0 and preserve tray, beads, payload mass, and transport task. For each a in {-1,1}, run bare, mat o=1, and mat o=-1: six matched trials. Reset bead starting positions between trials and record signed displacement and yaw with the supplied video.

| a | m | o | FRICTION (x,yaw) | ROCKING (x,yaw) |
|---|---|---|---|---|
| 1 | 0 | irrelevant | (3,0) | (3,0) |
| 1 | 1 | 1 | (4,0) | (4,1) |
| 1 | 1 | -1 | (4,0) | (2,-1) |
| -1 | 0 | irrelevant | (-3,0) | (-3,0) |
| -1 | 1 | 1 | (-4,0) | (-2,-1) |
| -1 | 1 | -1 | (-4,0) | (-4,1) |

A resolved disagreement with an account's joint pattern defeats that account. A pattern matching neither defeats the supplied two-account explanation, retaining omitted causes. Inadequate resolution or inconsistent readings leave diagnosis unresolved and block remedy selection. A match supports only the finite account within these settings.

Only after this separating design can I1/I2 and K3 converge provisionally: relinquish the mat as an assumed remedy while retaining it as a diagnostic perturbation. Diagnosis must precede suppression of its effect. No physical conclusion follows from the table.

## Probe card 2: qualify candidates after diagnosis

Combine K5's mat-free candidate with I4's reversible clamp candidate. Run eight trials after interpreting card 1:

- Six bare trials: m=0,c=0, each a in {-1,1} crossed with p in {-1,0,1}.
- Two clamped mat trials: m=1,c=1,p=o=1, one per pulse direction.

Both rivals predict (3a,0) at every setting. Compare displacement magnitudes with the supplied bare reference magnitude 3 and compare clamped trials with bare trials at matching a,p=1. Any resolved magnitude above 3 defeats that candidate at the tested setting; nonzero yaw defeats the rivals' corresponding prediction. Qualification requires resolved readings across all candidate settings. Selection remains provisional and bounded; broader bare coverage does not confer broader clamp coverage. Preserve all diagnostic video before choosing a passing candidate.

## Source disposition and limits

I1-I3 and K1-K4 remain explicit above; I4 and K5 are retained in card 2. I5's eight-trial proposal and K6's nine-trial burden are superseded by fourteen proposed trials to compare both candidates. K6's defeat gates and K7's operation families are retained. O1 is embedded in card 1; O2 remains outside the binary specification; O3 is rejected as unavailable; O4 is rejected as insufficient alone. Clamping before diagnosis is rejected under I2. Neither candidate is yet successful transport.

No new hardware or adhesive is required. Burdens are fourteen trials, bead resets, controlled settings, and joint video interpretation. Repeatability, precision, omitted causes, and real transport performance remain unknown (I5/K6). All arithmetic is synthetic model prediction, never a physical result.
