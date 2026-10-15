"""Own inert signatures. Tests bind these; no producer is invoked."""
def exact(*,run_binding,work_ref,source_cut):
    raise AssertionError('inert signature control must never dispatch')
def raw_input(raw):
    raise AssertionError('inert argument control must never dispatch')
