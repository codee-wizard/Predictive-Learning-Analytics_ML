"""
rag.py – FAISS-backed retrieval over an internal academic knowledge base.
Build the index once at import; expose `retrieve(query, k)`.
"""

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ─────────────────────────────────────────────
# KNOWLEDGE BASE
# ─────────────────────────────────────────────
KNOWLEDGE_BASE = [
    # ── ALGEBRA ──
    "Algebra - Linear Equations: A linear equation is an equation of the form ax + b = 0. "
    "To solve it, isolate the variable by performing inverse operations (addition, subtraction, "
    "multiplication, division) on both sides equally. Example: 2x + 4 = 0 → 2x = -4 → x = -2. "
    "Key idea: maintain balance on both sides.",

    "Algebra - Quadratic Equations: A quadratic equation has the form ax² + bx + c = 0. "
    "It can be solved using factorization, completing the square, or the quadratic formula: "
    "x = (-b ± √(b² - 4ac)) / (2a). The discriminant (b² - 4ac) determines the nature of roots "
    "(real, equal, or complex).",

    "Algebra - Inequalities: Inequalities are similar to equations but involve signs like >, <, ≥, ≤. "
    "When multiplying or dividing both sides by a negative number, the inequality sign must be reversed.",

    # ── ARITHMETIC ──
    "Arithmetic - Percentages: Percentage represents parts per hundred. "
    "Formula: percentage = (part/whole) × 100. Used in profit-loss, discounts, and data interpretation.",

    "Arithmetic - Ratios & Proportions: A ratio compares two quantities, while a proportion states "
    "equality of two ratios. Example: a/b = c/d. Used in scaling, mixtures, and real-life comparisons.",

    # ── GEOMETRY ──
    "Geometry - Triangles: The sum of interior angles of a triangle is 180°. "
    "In a right triangle, Pythagoras' theorem applies: a² + b² = c². Used to find missing sides.",

    "Geometry - Circles: Key elements include radius, diameter, circumference (2πr), and area (πr²). "
    "Understanding relationships between these is essential for solving problems.",

    # ── TRIGONOMETRY ──
    "Trigonometry - Basics: Trigonometric ratios (sin, cos, tan) relate angles to sides of a right triangle. "
    "sin = opposite/hypotenuse, cos = adjacent/hypotenuse, tan = opposite/adjacent.",

    # ── STATISTICS & PROBABILITY ──
    "Statistics - Central Tendency: Mean is average, median is middle value, mode is most frequent value. "
    "Used to summarise datasets.",

    "Probability: Probability measures the likelihood of an event. "
    "Formula: P = favorable outcomes / total outcomes. Value lies between 0 and 1.",

    # ── FUNCTIONS & CALCULUS ──
    "Functions: A function maps an input to exactly one output. "
    "Graphs help visualise relationships between variables.",

    "Calculus - Derivatives: A derivative represents rate of change (slope of a curve). "
    "Example: speed is the derivative of position with respect to time.",

    "Calculus - Integrals: Integrals represent accumulation or area under a curve. "
    "They are the reverse (antiderivative) of derivatives.",

    # ── READING & COMPREHENSION ──
    "Reading Comprehension: Focus on identifying main ideas, supporting details, tone, and inference. "
    "Always connect ideas across paragraphs.",

    "Inference Skills: Inference means understanding what is implied, not directly stated. "
    "Requires combining clues from the text with prior knowledge.",

    # ── WRITING ──
    "Writing - Structure: Use the PEEL method — Point, Evidence, Explanation, Link — "
    "to construct clear and logical paragraphs.",

    # ── PROBLEM SOLVING ──
    "Problem Solving Strategy: First understand the problem, identify knowns and unknowns, "
    "choose a method, solve step-by-step, and verify the answer.",

    "Error Analysis: Reviewing mistakes helps identify conceptual gaps and prevents repeating errors.",

    # ── STUDY SCIENCE ──
    "Active Recall: Testing yourself without notes strengthens memory more effectively than passive review.",

    "Spaced Repetition: Revisiting topics at increasing intervals improves long-term retention.",

    # ── RESOURCES ──
    "For Mathematics learning, Khan Academy (khanacademy.org) offers structured courses from basics to advanced.",

    "For conceptual understanding, 3Blue1Brown provides visual and intuitive explanations of math topics.",

    "For advanced topics, MIT OpenCourseWare offers free university-level lectures.",

    "For structured courses, Coursera allows auditing many courses for free.",

    # ── META LEARNING ──
    "If you cannot explain a concept simply, you have not fully understood it. "
    "Use the Feynman Technique: explain it as if teaching a child.",

    "Learning builds layer by layer; weak fundamentals lead to difficulty in advanced topics. "
    "Always solidify basics before moving forward.",
]

# ─────────────────────────────────────────────
# BUILD INDEX AT IMPORT TIME
# ─────────────────────────────────────────────
_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
_embeddings      = _embedding_model.encode(KNOWLEDGE_BASE, show_progress_bar=False)
_dimension       = _embeddings.shape[1]

_index = faiss.IndexFlatL2(_dimension)
_index.add(np.array(_embeddings, dtype="float32"))

_doc_store = {i: text for i, text in enumerate(KNOWLEDGE_BASE)}


# ─────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────
def retrieve(query: str, k: int = 3) -> list[str]:
    """Return the top-k most relevant knowledge-base chunks for *query*."""
    query_vec = _embedding_model.encode([query], show_progress_bar=False)
    _, indices = _index.search(np.array(query_vec, dtype="float32"), k)
    return [_doc_store[i] for i in indices[0] if i in _doc_store]