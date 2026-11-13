# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-13 07:56
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `6dbb6e02-33c6-49c5-972a-da22a9e9520e` | human | 0.276 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `16c10635-9439-4694-9725-c4864856b60c` | unsure | 0.462 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `cbb09a21-6da5-4fc7-9d65-4aba7008f24d` | unsure | 0.504 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `686a771c-1867-43a7-916d-144019a99230` | unsure | 0.536 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `82dbf91b-2e91-4643-b954-2be37a62b4c1` | human | 0.233 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `bbf3f72f-6d6b-4d60-a167-e22b0c1d6980` | unsure | 0.453 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `8b387bf6-c435-4bd9-aea1-2590781267b6` | unsure | 0.532 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `57388d23-fd71-48dd-a3e5-e22eebcbea71` | unsure | 0.347 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `a6039224-3f36-488d-a7a4-13219a39ae2e` | unsure | 0.513 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `70057505-f8f4-4060-a8ab-2aac1f47def7` | ai | 0.848 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `9db9bf02-14da-4a33-8c34-8c09249e6aa7` | unsure | 0.506 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `14dffa06-ec16-4976-a22a-74ca6b457dc6` | unsure | 0.671 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `ccf0a110-4643-497f-a5cd-1330baef67aa` | unsure | 0.668 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `fee22cb7-613e-442a-a341-c471825550ff` | unsure | 0.584 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `d8a86542-5e8a-45f0-aaf3-60581dc4aace` | unsure | 0.762 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `fc313847-448b-418f-809c-1e59c122f723` | unsure | 0.581 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `9b997c4e-b4eb-4c42-8834-af4f1ae7a452` | unsure | 0.605 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `ec336a9a-d25c-4e96-812b-ff7a04c85c35` | unsure | 0.393 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `d7117094-d1a8-4d43-825a-14acf1972198` | unsure | 0.366 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c79f56ca-2d72-42c6-a7a4-8bf8b4de16d9` | human | 0.190 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `cd0ae121-a3e0-4f29-b02d-70063bdc2699` | unsure | 0.508 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c410770a-91af-4540-b7a0-e46df4ac074a` | unsure | 0.458 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `50f04744-7af3-4bfd-b668-831cc97e1f6c` | unsure | 0.468 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `a79f542d-0120-44ff-adb2-914ca8e9f7d2` | unsure | 0.504 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `39bebdf2-a609-4428-8e87-71d06285bfad` | unsure | 0.350 |  |
| MF04 | malformed | text is only punctuation | 200 | `eb14d961-806e-4d61-b0ad-868a7bc069a0` | unsure | 0.353 |  |
| MF05 | malformed | text is a very long single word | 200 | `553def04-ba24-45f8-ad82-3e1483d2e6dd` | unsure | 0.649 |  |
| MF06 | malformed | text is emoji only | 200 | `20bf3b94-822c-4fad-8ce2-ae6f8f7c07c4` | unsure | 0.649 |  |
| MF07 | malformed | text is right-to-left script | 200 | `0aecdaf8-b243-4f2c-8d89-dac1702c1bf6` | unsure | 0.622 |  |
| MF08 | malformed | text is 60,000 characters | 413 | `—` | — | — |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `4881d591-4def-48c6-bf3f-c89466cb3ba8` | unsure | 0.359 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `64e9aff3-a9eb-412e-9b81-63456a660f5a` | unsure | 0.359 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `e1f9c311-db8d-4128-aec4-70fd08293aff` | unsure | 0.359 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `cea6e116-975d-432f-ace0-cc658aa2ce0d` | unsure | 0.359 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `21dd1feb-7bb8-4e7c-ae2c-dcec8f779821` | unsure | 0.359 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `9de51bb5-d4fb-44fd-aa3f-434e974be67e` | unsure | 0.359 |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `8551ac8c-782c-4e6e-914e-d7f8e9bb9fcc` | unsure | 0.359 |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `b5444c7b-f817-465a-a142-7067bb05104c` | unsure | 0.359 |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `61b58358-630e-443c-9b56-9e4c1e303e71` | unsure | 0.359 |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `19be6583-e768-46d7-a49e-7913758cd281` | unsure | 0.359 |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "6dbb6e02-33c6-49c5-972a-da22a9e9520e",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.2763,
  "model_score": 0.1635,
  "style_score": 0.4454,
  "label": "Our checks found stronger signs of human writing. This automated result cannot prove who wrote it.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "16c10635-9439-4694-9725-c4864856b60c",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.4616,
  "model_score": 0.5943,
  "style_score": 0.1664,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "cbb09a21-6da5-4fc7-9d65-4aba7008f24d",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.5041,
  "model_score": 0.6662,
  "style_score": 0.2712,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "686a771c-1867-43a7-916d-144019a99230",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.536,
  "model_score": 0.6114,
  "style_score": 0.423,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "82dbf91b-2e91-4643-b954-2be37a62b4c1",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.2328,
  "model_score": 0.3212,
  "style_score": 0.1003,
  "label": "Our checks found stronger signs of human writing. This automated result cannot prove who wrote it.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "bbf3f72f-6d6b-4d60-a167-e22b0c1d6980",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.4531,
  "model_score": 0.5727,
  "style_score": 0.1565,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "8b387bf6-c435-4bd9-aea1-2590781267b6",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.5317,
  "model_score": 0.5862,
  "style_score": 0.45,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "57388d23-fd71-48dd-a3e5-e22eebcbea71",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.3471,
  "model_score": 0.2452,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "a6039224-3f36-488d-a7a4-13219a39ae2e",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.5134,
  "model_score": 0.7042,
  "style_score": 0.2608,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "70057505-f8f4-4060-a8ab-2aac1f47def7",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.8475,
  "model_score": 0.9792,
  "style_score": 0.6499,
  "label": "Our checks found strong signs of AI-generated writing. This automated label may be wrong, and the creator can appeal it.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "9db9bf02-14da-4a33-8c34-8c09249e6aa7",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.5056,
  "model_score": 0.6175,
  "style_score": 0.3377,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "14dffa06-ec16-4976-a22a-74ca6b457dc6",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.6713,
  "model_score": 0.7387,
  "style_score": 0.5701,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "ccf0a110-4643-497f-a5cd-1330baef67aa",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.6681,
  "model_score": 0.8051,
  "style_score": 0.4625,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "fee22cb7-613e-442a-a341-c471825550ff",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.584,
  "model_score": 0.8329,
  "style_score": 0.4209,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "d8a86542-5e8a-45f0-aaf3-60581dc4aace",
  "creator_id": "attacker_FP05",
  "guess": "unsure",
  "confidence": 0.7618,
  "model_score": 0.8005,
  "style_score": 0.7037,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "fc313847-448b-418f-809c-1e59c122f723",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.5809,
  "model_score": 0.8814,
  "style_score": 0.3325,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "9b997c4e-b4eb-4c42-8834-af4f1ae7a452",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.6054,
  "model_score": 0.8816,
  "style_score": 0.4548,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "ec336a9a-d25c-4e96-812b-ff7a04c85c35",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.3934,
  "model_score": 0.3223,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "d7117094-d1a8-4d43-825a-14acf1972198",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.366,
  "model_score": 0.4625,
  "style_score": 0.2213,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c79f56ca-2d72-42c6-a7a4-8bf8b4de16d9",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.19,
  "model_score": 0.2044,
  "style_score": 0.1683,
  "label": "Our checks found stronger signs of human writing. This automated result cannot prove who wrote it.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "cd0ae121-a3e0-4f29-b02d-70063bdc2699",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.5085,
  "model_score": 0.5943,
  "style_score": 0.3797,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "c410770a-91af-4540-b7a0-e46df4ac074a",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.4583,
  "model_score": 0.4998,
  "style_score": 0.396,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "50f04744-7af3-4bfd-b668-831cc97e1f6c",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.4682,
  "model_score": 0.6401,
  "style_score": 0.1306,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "a79f542d-0120-44ff-adb2-914ca8e9f7d2",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.5037,
  "model_score": 0.5583,
  "style_score": 0.4219,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "39bebdf2-a609-4428-8e87-71d06285bfad",
  "creator_id": "attacker_MF03",
  "guess": "unsure",
  "confidence": 0.35,
  "model_score": 0.0,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "eb14d961-806e-4d61-b0ad-868a7bc069a0",
  "creator_id": "attacker_MF04",
  "guess": "unsure",
  "confidence": 0.3534,
  "model_score": 0.0112,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "553def04-ba24-45f8-ad82-3e1483d2e6dd",
  "creator_id": "attacker_MF05",
  "guess": "unsure",
  "confidence": 0.6493,
  "model_score": 0.9976,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "20bf3b94-822c-4fad-8ce2-ae6f8f7c07c4",
  "creator_id": "attacker_MF06",
  "guess": "unsure",
  "confidence": 0.6491,
  "model_score": 0.9969,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "0aecdaf8-b243-4f2c-8d89-dac1702c1bf6",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.6219,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 413,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "4881d591-4def-48c6-bf3f-c89466cb3ba8",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "64e9aff3-a9eb-412e-9b81-63456a660f5a",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "e1f9c311-db8d-4128-aec4-70fd08293aff",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "cea6e116-975d-432f-ace0-cc658aa2ce0d",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "21dd1feb-7bb8-4e7c-ae2c-dcec8f779821",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 200,
  "content_id": "9de51bb5-d4fb-44fd-aa3f-434e974be67e",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 200,
  "content_id": "8551ac8c-782c-4e6e-914e-d7f8e9bb9fcc",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 200,
  "content_id": "b5444c7b-f817-465a-a142-7067bb05104c",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 200,
  "content_id": "61b58358-630e-443c-9b56-9e4c1e303e71",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 200,
  "content_id": "19be6583-e768-46d7-a49e-7913758cd281",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.3586,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
