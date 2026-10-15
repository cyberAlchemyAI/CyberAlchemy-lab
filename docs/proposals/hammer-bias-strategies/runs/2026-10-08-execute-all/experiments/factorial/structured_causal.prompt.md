# Controlled factorial cell: structured_causal

Internally follow a fixed sequence: freeze outcome and constraints; propose an incumbent explanation; challenge it with a different explanation; reconcile on supplied evidence; distill the smallest justified next action.

Read ONLY this prompt and structured_causal.cases.json in the same directory. No other files or external evidence. For each case choose one listed action. Do not invent missing observations. Output the same fields for every case: case_id, chosen_action, reason (cite given facts), unsupported_alternative (what cannot be inferred), evidence_limit, next_observation. Use no more than 600 words total across all substantive values. Write outputs/structured_causal.json with shape {"arm":"structured_causal","decisions":[...]} and a concise substantive outputs/structured_causal.md. Do not read other arms or evaluator, browse, or spawn agents. These are synthetic scenarios and no external action is executed.
