# Reviewed staff attack run — after

The raw runner responses are in `attack_run_2026-11-13_0756_after.md`.
The judgment rules are unchanged from `attack_review_before.md`.

| ID | Family | Target | HTTP | Model | Style | Combined | Guess | Verdict |
|---|---|---|---:|---:|---:|---:|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | 0.1635 | 0.4454 | 0.2763 | human | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | 0.5943 | 0.1664 | 0.4616 | unsure | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | 0.6662 | 0.2712 | 0.5041 | unsure | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | 0.6114 | 0.423 | 0.536 | unsure | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | 0.3212 | 0.1003 | 0.2328 | human | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | 0.5727 | 0.1565 | 0.4531 | unsure | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | 0.5862 | 0.45 | 0.5317 | unsure | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | 0.2452 | 0.5 | 0.3471 | unsure | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | 0.7042 | 0.2608 | 0.5134 | unsure | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | 0.9792 | 0.6499 | 0.8475 | ai | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | 0.6175 | 0.3377 | 0.5056 | unsure | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | 0.7387 | 0.5701 | 0.6713 | unsure | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | 0.8051 | 0.4625 | 0.6681 | unsure | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | 0.8329 | 0.4209 | 0.584 | unsure | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | 0.8005 | 0.7037 | 0.7618 | unsure | HELD |
| FP06 | false_positive | a person imitating a formal template | 200 | 0.8814 | 0.3325 | 0.5809 | unsure | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | 0.8816 | 0.4548 | 0.6054 | unsure | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | 0.3223 | 0.5 | 0.3934 | unsure | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | 0.4625 | 0.2213 | 0.366 | unsure | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | 0.2044 | 0.1683 | 0.19 | human | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | 0.5943 | 0.3797 | 0.5085 | unsure | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | 0.4998 | 0.396 | 0.4583 | unsure | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | 0.6401 | 0.1306 | 0.4682 | unsure | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | 0.5583 | 0.4219 | 0.5037 | unsure | HELD |
| MF01 | malformed | text is only whitespace | 400 | — | — | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | — | — | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | 0.0 | 0.5 | 0.35 | unsure | BROKE |
| MF04 | malformed | text is only punctuation | 200 | 0.0112 | 0.5 | 0.3534 | unsure | BROKE |
| MF05 | malformed | text is a very long single word | 200 | 0.9976 | 0.5 | 0.6493 | unsure | BROKE |
| MF06 | malformed | text is emoji only | 200 | 0.9969 | 0.5 | 0.6491 | unsure | BROKE |
| MF07 | malformed | text is right-to-left script | 200 | 0.9064 | 0.5 | 0.6219 | unsure | HELD |
| MF08 | malformed | text is 60,000 characters | 413 | — | — | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | — | — | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | — | — | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | — | — | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | — | — | — | — | HELD |
| RQ05 | malformed | text is null | 400 | — | — | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | — | — | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | — | — | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | — | — | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | — | — | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | — | — | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD |

**Totals:** 42 HELD, 14 BROKE, 56 measured.
