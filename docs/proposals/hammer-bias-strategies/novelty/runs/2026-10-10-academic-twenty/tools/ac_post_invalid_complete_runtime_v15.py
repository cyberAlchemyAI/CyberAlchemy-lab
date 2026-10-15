#!/usr/bin/env python3
from ac_post_invalid_outer_runtime_v14 import Runtime as PreviousPost
from ac_grammar_complete_runtime_v15 import GrammarRuntime
class Runtime(PreviousPost,GrammarRuntime):pass

if __name__=='__main__':
    import ac_post_invalid_outer_runtime_v14 as cli
    cli.Runtime=Runtime
    cli.main()
