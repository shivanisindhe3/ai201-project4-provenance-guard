import json
import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def llm_ai_score(text):
    """
    Uses Groq to estimate how AI-like the text is.
    Returns a float from 0.0 to 1.0.
    """
    prompt = f"""
You are an AI content attribution assistant.

Analyze the writing below and estimate how likely it is to be AI-generated.

Return ONLY valid JSON in this exact format:
{{"score": 0.0}}

Rules:
- score must be between 0.0 and 1.0
- 0.0 means very likely human-written
- 1.0 means very likely AI-generated
- Do not include explanations

Text:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        score = float(data.get("score", 0.5))
        return max(0.0, min(1.0, round(score, 2)))

    except Exception:
        return 0.5


def heuristic_ai_score(text):
    """
    Pure Python stylometric heuristic score.
    Returns a float from 0.0 to 1.0.
    """
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    words = re.findall(r"\b\w+\b", text.lower())
    word_count = len(words)

    if word_count == 0:
        return 0.5

    unique_words = len(set(words))
    type_token_ratio = unique_words / word_count

    sentence_lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]

    if len(sentence_lengths) > 1:
        avg_len = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((x - avg_len) ** 2 for x in sentence_lengths) / len(sentence_lengths)
    else:
        variance = 0

    punctuation_count = len(re.findall(r"[,:;—-]", text))
    punctuation_density = punctuation_count / max(word_count, 1)

    score = 0.5

    # Lower vocabulary diversity can look more AI-like
    if type_token_ratio < 0.55:
        score += 0.2
    elif type_token_ratio > 0.75:
        score -= 0.15

    # Very uniform sentence length can look more AI-like
    if variance < 8:
        score += 0.2
    elif variance > 40:
        score -= 0.15

    # Too little punctuation variation can look more AI-like
    if punctuation_density < 0.03:
        score += 0.1
    elif punctuation_density > 0.08:
        score -= 0.05

    return max(0.0, min(1.0, round(score, 2)))