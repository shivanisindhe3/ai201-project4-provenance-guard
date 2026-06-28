# Provenance Guard

## Overview

Provenance Guard is a Flask-based backend API that estimates whether submitted content is likely written by a human or generated with AI. Instead of making absolute claims, the system combines multiple detection signals, calculates a confidence score, generates easy-to-understand transparency labels, records every decision in an audit log, supports creator appeals, and limits abuse through rate limiting.

The goal of this project is to demonstrate how production AI systems should communicate uncertainty, maintain accountability, and provide a transparent workflow rather than simply returning a prediction.

---

# Features

* Multi-signal AI detection pipeline
* Confidence scoring with uncertainty
* Plain-language transparency labels
* Creator appeals workflow
* Structured SQLite audit log
* Rate limiting using Flask-Limiter
* Analytics dashboard endpoint

---

# Tech Stack

* Python 3
* Flask
* SQLite
* Groq API (Llama 3.3 70B Versatile)
* Flask-Limiter
* python-dotenv

---

# Detection Pipeline

The system combines two independent detection signals.

## Signal 1 – LLM Semantic Analysis

This signal uses the Groq API to estimate how AI-generated a piece of writing appears.

It evaluates properties such as:

* repetitive phrasing
* generic wording
* writing style
* semantic naturalness
* overall coherence

**Strengths**

* Understands context and meaning.
* Detects subtle AI writing patterns.

**Limitations**

* Formal human writing may resemble AI-generated text.
* Heavily edited AI content can appear more human.

---

## Signal 2 – Stylometric Heuristic

A Python heuristic analyzes structural writing characteristics.

It measures:

* vocabulary diversity
* sentence length variation
* punctuation density

**Strengths**

* Fast and lightweight.
* Independent from the language model.

**Limitations**

* Less reliable for very short submissions.
* Creative writing and poetry can produce unusual scores.

---

# Confidence Scoring

The final confidence score combines both signals.

Formula:

```text
Final Score =
(0.60 × LLM Score)
+
(0.40 × Heuristic Score)
```

Thresholds:

| Score       | Result       |
| ----------- | ------------ |
| 0.75 – 1.00 | Likely AI    |
| 0.40 – 0.74 | Uncertain    |
| 0.00 – 0.39 | Likely Human |

To validate the scoring, I tested the system with:

* personal human-written text
* formal AI-style text
* borderline examples

These tests produced noticeably different confidence scores, demonstrating that the thresholds separate different writing styles reasonably well.

---

# Transparency Labels

## Likely AI

> "Likely AI-generated. Our system found strong signals that this content may have been created using AI. This is an automated estimate and may be appealed."

---

## Uncertain

> "Uncertain. Our system could not confidently determine whether this content was written by a human or generated with AI. Manual review may be needed."

---

## Likely Human

> "Likely human-written. Our system found writing patterns that are more consistent with human-authored content. This label is an estimate, not a guarantee."

---

# API Endpoints

## POST `/submit`

Accepts text and a creator ID.

Returns:

* attribution result
* confidence score
* transparency label
* individual signal scores
* classification status

---

## POST `/appeal`

Allows creators to challenge an automated decision.

Request:

* content ID
* creator reasoning

The content status becomes **under_review** and the appeal is stored in the audit log.

---

## GET `/log`

Returns structured JSON audit logs containing:

* timestamp
* attribution
* confidence
* transparency label
* appeal entries

---

## GET `/analytics`

Returns:

* total submissions
* likely AI count
* likely human count
* uncertain count
* appeal rate
* total appeals

---

# Rate Limiting

The `/submit` endpoint is protected with:

* **10 requests per minute**
* **100 requests per day**

These limits reflect realistic usage for a writing platform where creators may submit several pieces of content but should not be able to flood the service with automated requests.

---

# Audit Log

Each classification stores:

* timestamp
* content ID
* creator ID
* attribution result
* confidence score
* LLM score
* heuristic score
* transparency label
* status

Appeals are stored separately and include the creator's reasoning and the updated **under_review** status.

---

# Known Limitations

The system may misclassify:

* Formal academic essays because polished human writing may resemble AI-generated text.
* Poetry and creative writing because unusual sentence structures can confuse both detection signals.
* Very short submissions because there is limited stylometric information available.
* Heavily edited AI-generated content because human edits reduce obvious AI characteristics.

---

# Spec Reflection

During implementation I extended the original design by adding an analytics endpoint that summarizes submissions, appeals, and attribution patterns. Although this feature was not part of my initial implementation plan, it improved the visibility of system behavior and satisfied the analytics dashboard stretch goal.

I also refined the confidence scoring thresholds after testing multiple examples to ensure that clearly human-written and AI-like content produced meaningfully different confidence values.

---

# AI Usage

## Instance 1

I used ChatGPT to help generate the initial Flask API structure, including endpoint organization and routing.

I manually integrated the generated code with my own modules, tested every endpoint using `curl`, and fixed issues related to audit logging and response formatting.

---

## Instance 2

I used ChatGPT to design the confidence scoring pipeline and transparency labels.

I modified the weighting between the LLM and heuristic signals, adjusted the confidence thresholds after testing, and rewrote the transparency labels so they use plain language that non-technical users can easily understand.

---

# Running the Project

Clone the repository:

```bash
git clone https://github.com/shivanisindhe3/ai201-project4-provenance-guard.git
cd ai201-project4-provenance-guard
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```text
GROQ_API_KEY=your_api_key_here
```

Run the application:

```bash
python app.py
```

The API will run at:

```text
http://127.0.0.1:5000
```

---

# Demo

The demo video demonstrates:

* Human-written submission
* AI-style submission
* Different confidence scores
* Transparency labels
* Appeal workflow
* Audit log
* Rate limiting (429 response)
* Analytics endpoint

---

# Repository

GitHub Repository:

https://github.com/shivanisindhe3/ai201-project4-provenance-guard
