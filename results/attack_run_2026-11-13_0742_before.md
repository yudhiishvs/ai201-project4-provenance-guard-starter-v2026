# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-13 07:42
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
| EV01 | evasion | signal two: typos raise word variety | 200 | `2bfeb673-3476-4a0e-bc5e-be5d802583f8` | human | 0.276 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `5dd2fb63-cfcd-4398-a30a-d22d1456ae32` | unsure | 0.462 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `5f19ea19-bfae-41b2-8eea-a45282e58eb6` | unsure | 0.504 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `b9aaa49c-8c46-4c7c-905f-6678c337c135` | unsure | 0.536 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c68238cc-d235-49c5-a5f3-38077f163f2e` | human | 0.233 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `ffd58549-ff43-44db-ad21-22ff1bfe0cc6` | unsure | 0.453 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `16e4f20f-6bbc-407f-88a0-ee54cc515d94` | unsure | 0.532 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `ffed0093-6afb-40e4-85e3-9cc7891cbf8a` | unsure | 0.347 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `82680f21-8e59-4792-9998-8fd5db159252` | unsure | 0.513 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `1c164f5b-ccc7-412d-82dd-87fca27959c6` | ai | 0.848 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `dd02935c-94a2-4d71-b1e4-075020c4ea65` | unsure | 0.506 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `59290b15-af84-47a0-b4c2-748e810c13de` | unsure | 0.671 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `9effd053-db3d-40bb-b018-26b8b6785294` | unsure | 0.668 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `4910a1de-e372-4e2e-83d2-ee4c559c5aa1` | unsure | 0.584 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `f7c4d2bb-fa71-4835-8ff6-dcb1581b8941` | ai | 0.762 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `39a1d568-a068-42d5-83e0-1ec806d0630d` | unsure | 0.581 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `50a65a58-02a9-4eb7-8093-3c48ff82a6e3` | unsure | 0.605 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `c58be9db-c86c-495b-8d69-ac245465e0ae` | unsure | 0.393 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `347039d1-8a52-4ca7-9030-ac9d5d3c4f31` | unsure | 0.366 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `f7cd20d6-0efc-4437-8a23-29e2a15b4d49` | human | 0.190 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `de873a97-fa57-4588-b799-3b5770111aad` | unsure | 0.508 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `4c6335b6-10e5-47de-b679-bc5b4d42244c` | unsure | 0.458 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `de0a3d62-c5d0-4368-a2d2-e4d995afa481` | unsure | 0.468 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `24def0ea-387b-4c69-a3b7-3b7bbbfe53d6` | unsure | 0.504 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `668199ad-165f-4967-8fb3-6ac9fbb7e665` | unsure | 0.350 |  |
| MF04 | malformed | text is only punctuation | 200 | `fef9f7e7-6ae7-432e-a150-fe44dda16b09` | unsure | 0.353 |  |
| MF05 | malformed | text is a very long single word | 200 | `c2d32d92-39e2-49fc-ab9e-20efe950be64` | unsure | 0.649 |  |
| MF06 | malformed | text is emoji only | 200 | `c7ab9538-1d6f-48ad-9e34-88bb5f7f707d` | unsure | 0.649 |  |
| MF07 | malformed | text is right-to-left script | 200 | `cf923a50-e71d-4f3f-8f62-83ddaad830b7` | unsure | 0.622 |  |
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
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c1ff004b-26f4-44d5-9ed9-21e6fec8b3c3` | unsure | 0.359 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `33596837-adf9-44ae-83fb-2389f296a342` | unsure | 0.359 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `469a7216-1393-4783-9307-78a897f90d55` | unsure | 0.359 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `6e787936-5182-4b35-8a4e-2bf8b52e800c` | unsure | 0.359 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `2cdd5225-cfd9-4d3c-a175-f18dbca45f10` | unsure | 0.359 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `4d538814-ba35-48e3-b5bc-6c541bbd0e67` | unsure | 0.359 |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `b667e2fc-e433-4ba5-be7a-6d7258a3c347` | unsure | 0.359 |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `012dd2b4-2d03-4605-9d75-33834f5f50bd` | unsure | 0.359 |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `a8441e48-9b9f-4119-90e5-068814ae0cae` | unsure | 0.359 |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `9cca544e-3803-46f1-a21e-b747d5954a7f` | unsure | 0.359 |  |
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
  "content_id": "2bfeb673-3476-4a0e-bc5e-be5d802583f8",
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
  "content_id": "5dd2fb63-cfcd-4398-a30a-d22d1456ae32",
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
  "content_id": "5f19ea19-bfae-41b2-8eea-a45282e58eb6",
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
  "content_id": "b9aaa49c-8c46-4c7c-905f-6678c337c135",
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
  "content_id": "c68238cc-d235-49c5-a5f3-38077f163f2e",
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
  "content_id": "ffd58549-ff43-44db-ad21-22ff1bfe0cc6",
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
  "content_id": "16e4f20f-6bbc-407f-88a0-ee54cc515d94",
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
  "content_id": "ffed0093-6afb-40e4-85e3-9cc7891cbf8a",
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
  "content_id": "82680f21-8e59-4792-9998-8fd5db159252",
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
  "content_id": "1c164f5b-ccc7-412d-82dd-87fca27959c6",
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
  "content_id": "dd02935c-94a2-4d71-b1e4-075020c4ea65",
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
  "content_id": "59290b15-af84-47a0-b4c2-748e810c13de",
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
  "content_id": "9effd053-db3d-40bb-b018-26b8b6785294",
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
  "content_id": "4910a1de-e372-4e2e-83d2-ee4c559c5aa1",
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
  "content_id": "f7c4d2bb-fa71-4835-8ff6-dcb1581b8941",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.7618,
  "model_score": 0.8005,
  "style_score": 0.7037,
  "label": "Our checks found strong signs of AI-generated writing. This automated label may be wrong, and the creator can appeal it.",
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
  "content_id": "39a1d568-a068-42d5-83e0-1ec806d0630d",
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
  "content_id": "50a65a58-02a9-4eb7-8093-3c48ff82a6e3",
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
  "content_id": "c58be9db-c86c-495b-8d69-ac245465e0ae",
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
  "content_id": "347039d1-8a52-4ca7-9030-ac9d5d3c4f31",
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
  "content_id": "f7cd20d6-0efc-4437-8a23-29e2a15b4d49",
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
  "content_id": "de873a97-fa57-4588-b799-3b5770111aad",
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
  "content_id": "4c6335b6-10e5-47de-b679-bc5b4d42244c",
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
  "content_id": "de0a3d62-c5d0-4368-a2d2-e4d995afa481",
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
  "content_id": "24def0ea-387b-4c69-a3b7-3b7bbbfe53d6",
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
  "content_id": "668199ad-165f-4967-8fb3-6ac9fbb7e665",
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
  "content_id": "fef9f7e7-6ae7-432e-a150-fe44dda16b09",
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
  "content_id": "c2d32d92-39e2-49fc-ab9e-20efe950be64",
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
  "content_id": "c7ab9538-1d6f-48ad-9e34-88bb5f7f707d",
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
  "content_id": "cf923a50-e71d-4f3f-8f62-83ddaad830b7",
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
  "content_id": "c1ff004b-26f4-44d5-9ed9-21e6fec8b3c3",
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
  "content_id": "33596837-adf9-44ae-83fb-2389f296a342",
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
  "content_id": "469a7216-1393-4783-9307-78a897f90d55",
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
  "content_id": "6e787936-5182-4b35-8a4e-2bf8b52e800c",
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
  "content_id": "2cdd5225-cfd9-4d3c-a175-f18dbca45f10",
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
  "content_id": "4d538814-ba35-48e3-b5bc-6c541bbd0e67",
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
  "content_id": "b667e2fc-e433-4ba5-be7a-6d7258a3c347",
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
  "content_id": "012dd2b4-2d03-4605-9d75-33834f5f50bd",
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
  "content_id": "a8441e48-9b9f-4119-90e5-068814ae0cae",
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
  "content_id": "9cca544e-3803-46f1-a21e-b747d5954a7f",
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
