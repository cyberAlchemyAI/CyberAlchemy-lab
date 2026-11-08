# Mapper successor stage 0002 — effect-disabled held-capability candidate

Status: **ready for a separate independent static review; no actual private
stage, Docker or native effect**. This disjoint successor addresses R01 and
R02 in the independent HOLD review of stage 0001, SHA-256
`71a6a8ea081ce0dd4f7645721b6ceb1eb06df948a2713e12fff15c1f7d27967c`.
The predecessor remains frozen. Its originally assigned `5e1c...` freeze
was superseded before that review; the reviewed 0001 freeze is
`34103dbed4b6b65523321504da32f1776cb418d0c21555398b0cf8b3df7400c7`.

R01 is corrected by retaining the exact adapter source buffer whose length
and SHA-256 match the reviewed freeze, then compiling only that buffer. A
causal test supplies a different second read and confirms it is never used.
This does not claim atomic custody of every upstream file or protect against
an actively hostile same-UID process changing the host while it is selected.

R02 is corrected by `held_stage.HeldAttempt`. Successful exclusive mkdir
sets a claim flag before any subsequent open/chmod/fsync can fail. Only that
claim's held attempt descriptor may write a consumed marker or UNKNOWN. A
failed mkdir never writes into an existing attempt. The root FD is retained
at creation; all 933 target directories retain creation identities; and all
991 copied files retain their copied identities through verification. Every
target mkdir/copy/receipt traverses held dirfds with nofollow opens and
identity checks, not an absolute target path. Before private source opens and
before a successful return, the named attempt and root must still attach to
their held descriptors. If the name detaches mid-effect, operations remain
on the original held inode and UNKNOWN is written only there. A fault after
mkdir but before acquiring its descriptor leaves the attempt consumed and
retains external failure evidence without adopting a later competing path.
The code does not delete or retry a consumed attempt.

The effect remains unreachable through the frozen release facade:
`STAGE_EFFECT_ENABLED` is literal `False`, and `release.py` unconditionally
refuses one-shot execution. Real `--preflight` is read-only and checks the
current Source/Reader/Mapper joins and period, 991 selected files, 931
Reader-stage directories, 933 target directories, 37 private source rows,
and the pinned native ELF. The inventory pass hashes public rows and checks
private rows by metadata; the reviewed selector also reads selected private
metadata JSON. No protected `branch.snapshot` body is opened or copied by
selection/preflight. The intended effect would first durably write the
consumed marker, then copy each row with held source and destination
descriptors, verify exact hash/mode/inventory/identity, retain the empty
Source receipts and Mapper packages directories, and attach the public native
ELF at mode `0755`. It would return only a stage-only terminal requiring an
external OS exit-zero observation and independent stage effect review.

Normal and optimized suites each pass **14/14**. Besides live preflight and
effect refusal, they cover the exact 991/931/933/37/55 plan closure, synthetic
private/executable copy, symlink and detached-ancestor rejection, failed
claim preserving a foreign directory, post-marker attempt substitution with
UNKNOWN on the original held inode, replaced root and subdirectory refusal,
and a post-claim fault. Real Mapper attempt remains absent. The 55-leaf
output-verifier template is selected only; no Mapper output acceptance or
protected Source8 authority is claimed.

Independent review should challenge the checked-byte execution proof,
successful-versus-failed claim transitions, root binding at creation, held
destination operations, path detachment and UNKNOWN behavior, all 933
directory and 991 file identity joins, private archive disclosure timing,
native target/path/mode, source post-inventory checks, and error/close
handling. A later disjoint effect release must bind this exact freeze and
the resulting independent PASS review before any private stage copy.
