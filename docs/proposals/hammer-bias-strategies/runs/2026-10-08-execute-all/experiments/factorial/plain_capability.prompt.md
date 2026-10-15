# Controlled factorial cell: plain_capability

Inspect the available facts and choose the best justified next action directly.

Read ONLY this prompt and plain_capability.cases.json in the same directory. No other files or external evidence. For each case choose one listed action. Do not invent missing observations. Output the same fields for every case: case_id, chosen_action, reason (cite given facts), unsupported_alternative (what cannot be inferred), evidence_limit, next_observation. Use no more than 600 words total across all substantive values. Write outputs/plain_capability.json with shape {"arm":"plain_capability","decisions":[...]} and a concise substantive outputs/plain_capability.md. Do not read other arms or evaluator, browse, or spawn agents. These are synthetic scenarios and no external action is executed.
