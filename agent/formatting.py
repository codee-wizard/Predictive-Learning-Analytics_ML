"""
Light post-processing so assistant replies read well in Markdown / Streamlit.
"""

from __future__ import annotations

import re


def polish_assistant_markdown(text: str, max_sentence_run: int = 3) -> str:
    """
    If the model returns one long paragraph with no line breaks, split on
    sentence boundaries so the UI shows readable blocks.
    """
    if not text or not text.strip():
        return text
    s = text.strip()
    if "\n" in s:
        return s
    if len(s) < 320:
        return s

    sentences = re.split(r"(?<=[.!?])\s+", s)
    if len(sentences) < max_sentence_run:
        return s

    blocks: list[str] = []
    buf: list[str] = []
    for sent in sentences:
        if not sent:
            continue
        buf.append(sent)
        if len(buf) >= max_sentence_run:
            blocks.append(" ".join(buf))
            buf = []
    if buf:
        blocks.append(" ".join(buf))
    return "\n\n".join(blocks)
