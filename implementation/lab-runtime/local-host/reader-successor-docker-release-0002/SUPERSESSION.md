# Reader Docker release 0002 supersession

Release 0001 remains frozen at SHA-256
`ebb844e41ea9fc1910beb1a619bd95528e603ea6f08c18c6e90a38af50582051`.
Its independent static review SHA-256 is
`352ebce7f6e100b6e41a78c496657543fc2d629391c4db34409b6775013c4cbd`
and its verdict is HOLD. No Reader Docker effect was dispatched from 0001.

The HOLD finding was a signal arriving during `prepare_attempt()` after the
exclusive attempt root was created. The controller could then refuse before
its consumed marker, leaving no explicit UNKNOWN receipt. Release 0002 adds
a stop check after preparation and a no-replace UNKNOWN receipt for any
post-claim exception through `run()`. It also refuses to write a receipt into
a competing process's exclusive attempt root. Causal tests cover both signal
windows and the competing-claim case. The controller 0003 freeze and static
review remain unchanged.

Release 0002 has no dispatch authority until its own exact-byte independent
static PASS review. The sole selected attempt and Docker name remain unused.
