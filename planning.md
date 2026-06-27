# Provenance Guard – Planning Document

## Project Overview

Provenance Guard is a Flask-based backend API that estimates whether submitted text is likely human-written, likely AI-generated, or uncertain. The system combines multiple detection signals, computes a confidence score, generates a plain-language transparency label, logs every decision, supports creator appeals, and applies rate limiting to prevent abuse.

---

# Detection Signals

## Signal 1 – LLM-Based AI Detection

This signal uses the Groq API (Llama 3.3 70B Versatile) to analyze writing style and estimate how AI-generated the content appears.

It evaluates characteristics such as:

* repetitive phrasing
* generic wording
* overly polished structure
* lack of personal specificity
* overall writing naturalness

Output:

```
0.0 = very human-like
1.0 = very AI-like
```

### Strengths

* Understands meaning and writing style.
* Detects subtle AI writing patterns.

### Weaknesses

* May incorrectly classify formal human writing as AI.
* Can struggle with heavily edited AI-generated text.

---

## Signal 2 – Stylometric Heuristic

A Python-based heuristic measures structural writing characteristics.

It analyzes:

* vocabulary diversity
* sentence length variation
* punctuation density

Output:

```
0.0 = very human-like
1.0 = very AI-like
```

### Strengths

* Fast
* Independent from the LLM
* Captures writing structure

### Weaknesses

* Less reliable on very short text.
* Poems and academic writing may appear unusual.

---

# Confidence Scoring

The final confidence score combines both signals.

Formula:

```
combined_score =
(0.60 × llm_score)
+
(0.40 × heuristic_score)
```

The LLM receives more weight because it captures semantic writing patterns, while the heuristic acts as an independent structural check.

---

# Uncertainty Thresholds

| Combined Score | Result       |
| -------------- | ------------ |
| 0.75 – 1.00    | Likely AI    |
| 0.40 – 0.74    | Uncertain    |
| 0.00 – 0.39    | Likely Human |

Rather than forcing every submission into a binary decision, the system explicitly returns an **Uncertain** result whenever confidence is not high enough.

---

# Transparency Labels

## High Confidence AI

> "Likely AI-generated. Our system found strong signals that this content may have been created using AI. This is an automated estimate and may be appealed."

---

## Uncertain

> "Uncertain. Our system could not confidently determine whether this content was written by a human or generated with AI. Manual review may be needed."

---

## High Confidence Human

> "Likely human-written. Our system found writing patterns that are more consistent with human-authored content. This label is an estimate, not a guarantee."

---

# Appeals Workflow

If a creator believes their content was classified incorrectly, they can submit an appeal.

The appeal includes:

* content ID
* creator reasoning

The system:

1. records the appeal
2. changes the status to **under_review**
3. stores the appeal inside the audit log

No automatic reclassification occurs. Appeals are intended for later human review.

---

# Audit Logging

Every submission stores:

* timestamp
* content ID
* creator ID
* attribution result
* confidence score
* LLM score
* heuristic score
* transparency label
* status

Appeals additionally store:

* appeal reasoning
* under_review status

SQLite is used for structured audit logging.

---

# Rate Limiting

The submission endpoint uses:

```
10 requests per minute
100 requests per day
```

Reasoning:

A normal creator may submit only a few pieces of content in one session. These limits allow regular usage while preventing automated abuse or spam submissions.

---

# Edge Cases

### 1. Academic Writing

Very formal human-written essays may appear AI-generated because of polished language.

### 2. Very Short Text

Short sentences provide little evidence for stylometric analysis.

### 3. Edited AI Content

AI-generated content that has been heavily rewritten by a human may be classified as human or uncertain.

### 4. Poetry

Poetry has unusual vocabulary and sentence structure that may confuse both detection signals.

---

# AI Tool Plan

AI tools will be used during implementation for:

* generating the Flask API structure
* creating the Groq integration
* generating SQLite logging code
* implementing confidence scoring
* generating rate limiting
* refining documentation

Every generated component will be manually reviewed, tested with multiple inputs, and modified where necessary before being accepted into the final project.

---

# Stretch Feature

Analytics Dashboard

The `/analytics` endpoint reports:

* total submissions
* likely AI count
* likely human count
* uncertain count
* total appeals
* appeal rate

This provides administrators with an overview of system usage and detection trends.
