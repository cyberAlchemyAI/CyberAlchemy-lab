#!/usr/bin/env python3
from ac_grammar_outer_runtime_v14 import GrammarRuntime as PreviousGrammar
from ac_complete_keys_runtime_v15 import CoverageRuntime
class GrammarRuntime(PreviousGrammar,CoverageRuntime):pass

if __name__=='__main__':
    import ac_grammar_outer_runtime_v14 as cli
    cli.GrammarRuntime=GrammarRuntime
    cli.main()
