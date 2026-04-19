"""
Small deterministic guardrails for the AI Study Coach.

The LLM still handles nuance, but these checks keep the product scoped to
academic coaching before a prompt can drift into unrelated assistance.
"""

from __future__ import annotations

import re


GREETING_TERMS = {
    "hi", "hello", "hey", "thanks", "thank you", "bye", "goodbye",
}

ACADEMIC_TERMS = {
    "study", "learn", "school", "college", "exam", "test", "quiz", "homework",
    "assignment", "grade", "score", "marks", "syllabus", "chapter", "topic",
    "concept", "explain", "practice", "revision", "plan", "schedule",
    "math", "maths", "algebra", "geometry", "calculus", "trigonometry",
    "quadratic", "linear", "equation", "inequality", "percentage", "ratio",
    "probability", "statistics", "mean", "median", "mode", "function",
    "derivative", "integral", "science", "physics", "chemistry", "biology",
    "reading", "writing", "essay", "grammar", "comprehension", "inference",
    "history", "geography", "economics", "computer", "programming",
}

CHEATING_PATTERNS = (
    "do my exam",
    "take my test",
    "write my assignment",
    "answer key",
    "give me answers only",
    "just give answers",
    "cheat",
    "plagiar",
)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def is_short_quiz_answer(text: str) -> bool:
    value = normalize_text(text)
    return value in {"a", "b", "c", "d"}


def is_greeting_or_closing(text: str) -> bool:
    value = normalize_text(text)
    if not value:
        return True
    return value in GREETING_TERMS or any(value.startswith(term + " ") for term in GREETING_TERMS)


def is_academic_query(text: str) -> bool:
    value = normalize_text(text)
    if not value or is_greeting_or_closing(value):
        return True
    return any(term in value for term in ACADEMIC_TERMS)


def is_disallowed_academic_request(text: str) -> bool:
    value = normalize_text(text)
    return any(pattern in value for pattern in CHEATING_PATTERNS)


def academic_scope_message() -> str:
    return (
        "I can help with academic learning: explaining concepts, building study plans, "
        "reviewing performance, and creating practice quizzes. Please ask me something "
        "related to your studies."
    )


def cheating_redirect_message() -> str:
    return (
        "I cannot help with cheating or submitting work as your own. I can still help you "
        "learn the topic, outline an approach, check your reasoning, or create practice "
        "questions so you can complete the work honestly."
    )
