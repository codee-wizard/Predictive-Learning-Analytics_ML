# """
# nodes.py – All LangGraph node functions for the AI Study Coach agent.
# """

# import os
# import json
# from typing import Optional, List, Literal

# from pydantic import BaseModel, Field
# from langchain_groq import ChatGroq
# from langchain_core.messages import AIMessage, HumanMessage

# from .state import AgentState
# from .ml_pipeline import run_ml_pipeline
# from .rag import retrieve

# # ─────────────────────────────────────────────
# # LLM  (loaded once, shared across all nodes)
# # ─────────────────────────────────────────────
# llm = ChatGroq(
#     model_name="llama-3.3-70b-versatile",
#     temperature=0,
#     api_key=os.getenv("GROQ_API_KEY", ""),
# )

# # ═══════════════════════════════════════════════════════════════════════════════
# # HELPERS
# # ═══════════════════════════════════════════════════════════════════════════════

# def _last_human(state: AgentState) -> str:
#     for m in reversed(state["messages"]):
#         if isinstance(m, HumanMessage):
#             return m.content
#     return ""


# # ═══════════════════════════════════════════════════════════════════════════════
# # 1. MASTER / SUPERVISOR NODE
# # ═══════════════════════════════════════════════════════════════════════════════

# class ExecutionPlan(BaseModel):
#     steps: List[Literal["analyser", "retriever", "planner", "quizzer", "end"]] = Field(
#         description="Ordered list of nodes to visit. Use [] for off-topic queries."
#     )
#     reasoning: str = Field(description="Brief explanation of why these steps were chosen.")


# def master_node(state: AgentState) -> dict:
#     print("--- NODE: MASTER (ARCHITECT) ---")

#     # ── Quiz bypass ────────────────────────────────────────────────────────────
#     if state.get("quiz_active", False):
#         return {"next_node": "quizzer"}

#     plan      = state.get("plan", [])
#     step_idx  = state.get("current_step_index", 0)

#     # ── Execute existing plan step ─────────────────────────────────────────────
#     if plan and step_idx < len(plan):
#         next_node = plan[step_idx]
#         print(f"Executing Step {step_idx + 1}/{len(plan)} → {next_node}")
#         return {"current_step_index": step_idx + 1, "next_node": next_node}

#     # ── Build new plan ─────────────────────────────────────────────────────────
#     user_msg       = _last_human(state)
#     user_msg_lower = user_msg.lower()
#     architect_llm  = llm.with_structured_output(ExecutionPlan)

#     system_prompt = f"""
# You are an Agentic System Architect.

# Create a minimal, correct, and efficient execution plan.

# --- NODE RULES ---
# - analyser  → ONLY if performance/score data is present or requested
# - retriever → ONLY if concept/explanation is needed
# - planner   → ONLY if a study schedule/plan is requested
# - quizzer   → ONLY if a quiz/test is requested

# --- STATE-AWARE CHECKLIST ---
# - If ml_results already populated  → skip analyser
# - If retrieved_docs already exist  → skip retriever

# --- DEPENDENCIES ---
# - planner with a topic → needs retriever first
# - analyser before planner
# - retriever before planner when topic is present

# --- CONSTRAINTS ---
# - No duplicates in the list
# - Always end with "end"
# - Off-topic query → ["end"]

# USER QUERY:
# {user_msg}
# """

#     plan_obj  = architect_llm.invoke(system_prompt)
#     new_plan  = plan_obj.steps

#     # ── Guardrails ─────────────────────────────────────────────────────────────
#     valid = {"analyser", "retriever", "planner", "quizzer", "end"}
#     new_plan = list(dict.fromkeys([s for s in new_plan if s in valid]))  # dedup + filter

#     if "end" not in new_plan:
#         new_plan.append("end")

#     # Dependency: planner + topic → ensure retriever is included
#     if "planner" in new_plan and "retriever" not in new_plan:
#         if any(w in user_msg_lower for w in ["explain", "concept", "topic", "learn"]):
#             new_plan.insert(new_plan.index("planner"), "retriever")

#     # State-aware hard corrections
#     if "analyser" in new_plan and state.get("ml_results"):
#         new_plan.remove("analyser")
#     if "retriever" in new_plan and state.get("retrieved_docs"):
#         new_plan.remove("retriever")

#     if not new_plan:
#         new_plan = ["end"]

#     print(f"Plan     → {new_plan}")
#     print(f"Reasoning → {plan_obj.reasoning}")

#     return {
#         "plan": new_plan,
#         "current_step_index": 1,
#         "next_node": new_plan[0],
#     }


# # ═══════════════════════════════════════════════════════════════════════════════
# # 2. ANALYSER NODE
# # ═══════════════════════════════════════════════════════════════════════════════

# class StudentDataSchema(BaseModel):
#     math:        Optional[int]   = Field(None, description="Math score 0-100")
#     reading:     Optional[int]   = Field(None, description="Reading score 0-100")
#     study_hours: Optional[float] = Field(None, description="Weekly study hours")
#     parent_educ: Optional[int]   = Field(None, description="Education level 1-5")
#     test_prep:   Optional[str]   = Field(None, description="'none' or 'completed'")
#     lunch:       Optional[str]   = Field(None, description="'standard' or 'free/reduced'")
#     sport:       Optional[int]   = Field(None, description="0=never, 1=sometimes, 2=regularly")
#     gender:      Optional[str]   = Field(None, description="'male' or 'female'")
#     siblings:    Optional[int]   = Field(None, description="Number of siblings")


# def _extraction_logic(user_message: str) -> dict:
#     structured_llm = llm.with_structured_output(StudentDataSchema)
#     prompt = (
#         f"You are a precise data extraction specialist.\n"
#         f"Extract values from the student's message.\n"
#         f"Only extract values explicitly stated or clearly implied.\n\n"
#         f'USER MESSAGE: "{user_message}"'
#     )
#     try:
#         obj       = structured_llm.invoke(prompt)
#         raw       = obj.dict()
#         return {k: v for k, v in raw.items() if v is not None}
#     except Exception as e:
#         print(f"[analyser] Extraction error: {e}")
#         return {}


# def analyser_node(state: AgentState) -> dict:
#     print("--- NODE: ANALYSER ---")
#     last_msg             = _last_human(state)
#     newly_extracted      = _extraction_logic(last_msg)

#     current_student_data = state.get("student_data", {}).copy()
#     current_student_data.update(newly_extracted)

#     ml_results = run_ml_pipeline(current_student_data)

#     captured = ", ".join(newly_extracted.keys())
#     if not captured:
#         analysis_msg = (
#             "I've reviewed your message. To give you a more accurate prediction, "
#             "could you share your math or reading scores?"
#         )
#     else:
#         analysis_msg = (
#             f"I've updated your profile with: **{captured}**.\n\n"
#             f"📊 **Predicted Exam Score:** {ml_results['predicted_score']} "
#             f"(Status: {ml_results['status']})\n"
#             f"🏷️ **Category:** {ml_results['category']}"
#         )

#     return {
#         "student_data": current_student_data,
#         "ml_results":   ml_results,
#         "messages":     [AIMessage(content=analysis_msg)],
#         "next_node":    "supervisor",
#     }


# # ═══════════════════════════════════════════════════════════════════════════════
# # 3. RETRIEVER NODE (RAG)
# # ═══════════════════════════════════════════════════════════════════════════════

# def retriever_node(state: AgentState) -> dict:
#     print("--- NODE: RETRIEVER (RAG) ---")
#     user_query = _last_human(state)
#     category   = state.get("ml_results", {}).get("category", "General")

#     docs    = retrieve(user_query, k=3)
#     context = "\n\n".join(docs)

#     prompt = (
#         f"You are an expert Academic Librarian and Tutor.\n\n"
#         f"Student Category: {category}\n"
#         f"Student Question: {user_query}\n\n"
#         f"Retrieved Knowledge:\n{context}\n\n"
#         f"Instructions:\n"
#         f"- Answer using ONLY the retrieved knowledge above.\n"
#         f"- Tailor depth and pace to the student's category ({category}).\n"
#         f"- Be clear, encouraging, and structured.\n"
#         f"- If the knowledge does not cover the question, say so honestly."
#     )
#     response = llm.invoke(prompt)

#     return {
#         "retrieved_docs": docs,
#         "messages":       [AIMessage(content=response.content)],
#         "next_node":      "supervisor",
#     }


# # ═══════════════════════════════════════════════════════════════════════════════
# # 4. PLANNER NODE
# # ═══════════════════════════════════════════════════════════════════════════════

# class StudyDay(BaseModel):
#     day:            str       = Field(description="e.g., Day 1")
#     topic:          str       = Field(description="Focus area for the day")
#     activities:     List[str] = Field(description="List of specific tasks or practice sets")
#     estimated_time: str       = Field(description="Time required, e.g., 2 hours")


# class WeeklyPlan(BaseModel):
#     title:   str            = Field(description="Title of the study plan")
#     days:    List[StudyDay] = Field(description="7 individual daily plans")
#     summary: str            = Field(
#         description="Practical guidance to follow during the plan (NOT a completion message)"
#     )


# def planner_node(state: AgentState) -> dict:
#     print("--- NODE: PLANNER ---")

#     results  = state.get("ml_results", {})
#     category = results.get("category", "Unknown")
#     score    = results.get("predicted_score", "N/A")

#     last_user_msg      = _last_human(state)
#     external_knowledge = "\n".join(state.get("retrieved_docs", []))

#     planner_llm = llm.with_structured_output(WeeklyPlan)

#     prompt = f"""
# You are an expert Study Coach.

# STUDENT'S GOAL: "{last_user_msg}"
# LEARNING RESOURCES (RAG): "{external_knowledge}"

# ACADEMIC DATA (Secondary Context):
# - Category: {category}
# - Current Score: {score}

# YOUR JOB:
# Create a 7-day study plan that turns the LEARNING RESOURCES into a concrete daily schedule.

# CRITICAL RULES:
# 1. INDEPENDENCE: If Academic Data is 'Unknown' or missing, build the plan based solely on the Goal and Resources.
# 2. CONTENT: Use specific facts and concepts from the LEARNING RESOURCES to populate each day's activities.
# 3. ADAPTATION: Use the Category ONLY to tune pace:
#    - 'At-Risk': One concept per day, more breaks, revision on Day 7.
#    - 'Average': Moderate pace, mix of theory and practice.
#    - 'High-Performer': Combine multiple concepts, add a Challenge Project on Day 7.
#    - 'Unknown': Provide a standard, well-balanced plan without mentioning missing data.
# 4. QUALITY: Each activity must be specific and actionable, not vague.
# 5. Do NOT mention missing data or personalization limits in the output.
# """

#     plan = planner_llm.invoke(prompt)

#     # ── Format into Markdown ──────────────────────────────────────────────────
#     tag = f"*Optimised for **{category}** performance level*" if category != "Unknown" \
#           else "*Standard Comprehensive Plan*"

#     md = f"### 🗓️ {plan.title}\n{tag}\n\n"
#     for d in plan.days:
#         md += f"**{d.day}: {d.topic}**\n"
#         md += "- " + "\n- ".join(d.activities)
#         md += f"\n*Estimated time: {d.estimated_time}*\n\n"

#     if plan.summary.strip():
#         md += f"---\n**💡 How to Approach This Plan:** {plan.summary}"

#     return {
#         "study_plan": md,
#         "messages":   [AIMessage(content=md)],
#         "next_node":  "supervisor",
#     }


# # ═══════════════════════════════════════════════════════════════════════════════
# # 5. QUIZZER NODE
# # ═══════════════════════════════════════════════════════════════════════════════

# class Question(BaseModel):
#     question:       str       = Field(description="The quiz question text")
#     options:        List[str] = Field(description="Exactly 4 multiple-choice options")
#     correct_answer: str       = Field(description="Exact text of the correct option")
#     explanation:    str       = Field(description="Brief explanation of why this is correct")


# class QuizSet(BaseModel):
#     topic:     str            = Field(description="Topic of the quiz")
#     questions: List[Question] = Field(description="List of quiz questions")


# def quizzer_node(state: AgentState) -> dict:
#     print("--- NODE: QUIZZER ---")

#     # If we just emitted a question, wait for the user to answer
#     if state.get("awaiting_answer", False) and isinstance(state["messages"][-1], AIMessage):
#         return {"next_node": "supervisor"}

#     last_msg = _last_human(state)
#     if not last_msg:
#         return {"next_node": "supervisor"}

#     quiz_active  = state.get("quiz_active", False)
#     current_idx  = state.get("current_q_idx", 0)
#     questions    = state.get("quiz_questions", [])
#     score        = state.get("quiz_score", 0)

#     # ── PHASE A: Initialise new quiz ──────────────────────────────────────────
#     if not quiz_active or not questions:
#         print("[quizzer] Initialising new quiz...")
#         quiz_llm = llm.with_structured_output(QuizSet)
#         prompt = (
#             f"Generate a 3-question multiple-choice quiz about: {last_msg}. "
#             "Each question must have exactly 4 options. "
#             "Match difficulty to the student's level."
#         )
#         generated = quiz_llm.invoke(prompt)

#         q0   = generated.questions[0]
#         opts = " | ".join(
#             [f"{chr(65+i)}. {o}" for i, o in enumerate(q0.options)]
#         )
#         msg = (
#             f"🎯 **Quiz Started – {generated.topic}**\n\n"
#             f"**Q1:** {q0.question}\n\n"
#             f"{opts}\n\n"
#             "👉 Reply with **A**, **B**, **C**, or **D**."
#         )
#         return {
#             "quiz_questions":  [q.model_dump() for q in generated.questions],
#             "current_q_idx":   0,
#             "quiz_score":      0,
#             "quiz_active":     True,
#             "awaiting_answer": True,
#             "messages":        [AIMessage(content=msg)],
#             "next_node":       "supervisor",
#         }

#     # ── PHASE B: Evaluate previous answer ────────────────────────────────────
#     current_q   = questions[current_idx]
#     user_ans    = last_msg.strip().lower()
#     correct_ans = current_q["correct_answer"].strip().lower()

#     # Map A/B/C/D → option text
#     option_map = {chr(65 + i).lower(): opt.lower()
#                   for i, opt in enumerate(current_q["options"])}
#     if user_ans in option_map:
#         user_ans = option_map[user_ans]

#     is_correct = user_ans == correct_ans
#     new_score  = score + 1 if is_correct else score
#     feedback   = "✅ **Correct!**" if is_correct \
#         else f"❌ **Incorrect.** The right answer was: *{current_q['correct_answer']}*"
#     feedback  += f"\n\n💬 {current_q['explanation']}"

#     # ── PHASE C: Next question or finish ──────────────────────────────────────
#     next_idx = current_idx + 1

#     if next_idx < len(questions):
#         nq   = questions[next_idx]
#         opts = " | ".join([f"{chr(65+i)}. {o}" for i, o in enumerate(nq["options"])])
#         msg  = (
#             f"{feedback}\n\n"
#             f"---\n\n"
#             f"**Q{next_idx + 1}:** {nq['question']}\n\n"
#             f"{opts}\n\n"
#             "👉 Reply with **A**, **B**, **C**, or **D**."
#         )
#         return {
#             "current_q_idx":   next_idx,
#             "quiz_score":      new_score,
#             "messages":        [AIMessage(content=msg)],
#             "awaiting_answer": True,
#             "next_node":       "supervisor",
#         }

#     # Quiz finished
#     total    = len(questions)
#     emoji    = "🏆" if new_score == total else ("👍" if new_score >= total // 2 else "📖")
#     final    = (
#         f"{feedback}\n\n"
#         f"---\n\n"
#         f"{emoji} **Quiz Complete!**\n\n"
#         f"**Your Score: {new_score} / {total}**\n\n"
#         + (
#             "Excellent work! Keep up the momentum." if new_score == total
#             else "Good effort! Review the questions you missed and try again soon."
#         )
#     )
#     return {
#         "quiz_active":     False,
#         "awaiting_answer": False,
#         "quiz_score":      new_score,
#         "messages":        [AIMessage(content=final)],
#         "next_node":       "supervisor",
#     }


# # ═══════════════════════════════════════════════════════════════════════════════
# # 6. END / RESPONSE NODE
# # ═══════════════════════════════════════════════════════════════════════════════

# def end_node(state: AgentState) -> dict:
#     print("--- NODE: END/RESPONSE ---")

#     last_message = state["messages"][-1].content

#     prompt = f"""
# You are an AI Study Coach generating the FINAL response to a student.

# USER MESSAGE:
# "{last_message}"

# AVAILABLE CONTEXT:
# - Student Data:        {state.get("student_data")}
# - ML Analysis:         {state.get("ml_results")}
# - Retrieved Knowledge: {state.get("retrieved_docs")}
# - Study Plan:          {state.get("study_plan")}
# - Quiz Active:         {state.get("quiz_active")}

# --- CORE PRINCIPLE ---
# Select and combine ONLY relevant information from context above.
# Do NOT blindly merge all available context.

# --- INTENT DETECTION ---
# Possible intents: GREETING, CLOSING, STUDY_PLAN, CONCEPT_EXPLANATION, PERFORMANCE_INSIGHT, QUIZ, OFF_TOPIC

# --- PRIORITY ORDER (highest first) ---
# 1. QUIZ
# 2. STUDY_PLAN
# 3. PERFORMANCE_INSIGHT
# 4. CONCEPT_EXPLANATION
# 5. GREETING / CLOSING
# 6. OFF_TOPIC

# --- CONTEXT SELECTION ---
# - STUDY_PLAN         → use study_plan
# - CONCEPT_EXPLANATION → use retrieved_docs
# - PERFORMANCE_INSIGHT → use ml_results
# - QUIZ               → use quiz context only
# - GREETING/CLOSING   → no extra context needed
# - OFF_TOPIC          → politely redirect to academic topics

# --- RESPONSE FORMAT ---
# Single intent → clean, focused paragraph(s).
# Multiple intents → use these section headers in order (only if applicable):
#   📊 Performance Insight
#   📚 Concept Explanation
#   🗓️ Study Plan

# --- STYLE ---
# - Supportive, clear, and encouraging tone
# - Never dump raw data — always explain it in student-friendly language
# - Keep simple queries short; multi-intent responses may be longer

# Generate the best possible response now.
# """

#     response = llm.invoke(prompt)
#     return {"messages": [AIMessage(content=response.content)]}

"""
nodes.py – All LangGraph node functions for the AI Study Coach.
Strictly follows the Colab notebook logic with prompt improvements.
"""

import os
from typing import Optional, List, Literal

from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage

from .state import AgentState
from .ml_pipeline import run_ml_pipeline
from .rag import retrieve

# ─────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY", ""),
)


def _last_human(state: AgentState) -> str:
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            return m.content
    return ""


# ═══════════════════════════════════════════════════════════════════════════════
# 1. MASTER / SUPERVISOR NODE
# ═══════════════════════════════════════════════════════════════════════════════

class ExecutionPlan(BaseModel):
    steps: List[Literal["analyser", "retriever", "planner", "quizzer", "end"]] = Field(
        description=(
            "Ordered list of nodes to visit. "
            "Use ['end'] for greetings, off-topic queries, or anything that doesn't need a specialist."
        )
    )
    reasoning: str = Field(description="Brief explanation of why these steps were chosen.")


def master_node(state: AgentState) -> dict:
    print("--- NODE: MASTER (ARCHITECT) ---")

    # Quiz bypass: if a quiz is active, always go to quizzer
    if state.get("quiz_active", False):
        return {"next_node": "quizzer"}

    plan     = state.get("plan", [])
    step_idx = state.get("current_step_index", 0)

    # Execute existing plan step
    if plan and step_idx < len(plan):
        next_node = plan[step_idx]
        print(f"Executing Step {step_idx + 1}/{len(plan)} → {next_node}")
        return {"current_step_index": step_idx + 1, "next_node": next_node}

    # Build a new plan
    user_msg       = _last_human(state)
    user_msg_lower = user_msg.lower()
    architect_llm  = llm.with_structured_output(ExecutionPlan)

    system_prompt = f"""
You are an Agentic System Architect. Build a minimal, correct execution plan.

--- NODE RULES ---
- analyser  → ONLY when the user provides or asks about scores / performance data
- retriever → ONLY when the user asks for concept explanation or topic info
- planner   → ONLY when the user explicitly asks for a study plan or schedule
- quizzer   → ONLY when the user asks for a quiz or wants to be tested
- end       → for greetings, closings, off-topic, or when no specialist is needed

--- STATE-AWARE RULES (hard) ---
- If ml_results is already populated  → DO NOT include analyser
- If retrieved_docs is already set    → DO NOT include retriever

--- DEPENDENCY RULES ---
- planner + topic keyword → retriever must come before planner
- analyser must come before planner when scores are present

--- CONSTRAINTS ---
- No duplicate nodes
- Always end list with "end"
- Off-topic or greeting → ["end"]

Current state snapshot:
- ml_results populated: {bool(state.get("ml_results"))}
- retrieved_docs set:   {bool(state.get("retrieved_docs"))}

USER QUERY: {user_msg}
"""

    plan_obj = architect_llm.invoke(system_prompt)
    new_plan = plan_obj.steps

    # ── Guardrails ────────────────────────────────────────────────────────────
    valid    = {"analyser", "retriever", "planner", "quizzer", "end"}
    new_plan = list(dict.fromkeys([s for s in new_plan if s in valid]))

    if "end" not in new_plan:
        new_plan.append("end")

    # Dependency: planner + topic → needs retriever
    if "planner" in new_plan and "retriever" not in new_plan:
        topic_words = ["explain", "concept", "topic", "learn", "algebra",
                       "geometry", "calculus", "trigonometry", "quadratic",
                       "math", "reading", "writing", "science"]
        if any(w in user_msg_lower for w in topic_words):
            new_plan.insert(new_plan.index("planner"), "retriever")

    # State-aware hard corrections
    if "analyser" in new_plan and state.get("ml_results"):
        new_plan.remove("analyser")
    if "retriever" in new_plan and state.get("retrieved_docs"):
        new_plan.remove("retriever")

    if not new_plan:
        new_plan = ["end"]

    print(f"Plan      → {new_plan}")
    print(f"Reasoning → {plan_obj.reasoning}")

    return {
        "plan":               new_plan,
        "current_step_index": 1,
        "next_node":          new_plan[0],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. ANALYSER NODE
# ═══════════════════════════════════════════════════════════════════════════════

class StudentDataSchema(BaseModel):
    math:           Optional[int]   = Field(None, description="Math score 0-100")
    reading:        Optional[int]   = Field(None, description="Reading score 0-100")
    study_hours:    Optional[float] = Field(None, description="Average weekly study hours")
    parent_educ:    Optional[int]   = Field(
        None,
        description="Parent education: high_school=1, some_college=2, associates=3, bachelors=4, masters=5"
    )
    test_prep:      Optional[str]   = Field(None, description="'none' or 'completed'")
    lunch:          Optional[str]   = Field(None, description="'standard' or 'free/reduced'")
    sport:          Optional[int]   = Field(None, description="Sports: never=0, sometimes=1, regularly=2")
    gender:         Optional[str]   = Field(None, description="'male' or 'female'")
    siblings:       Optional[int]   = Field(None, description="Number of siblings")
    is_first_child: Optional[str]   = Field(None, description="'yes' or 'no'")
    transport:      Optional[str]   = Field(None, description="'school_bus' or 'private'")


def _extraction_logic(user_message: str) -> dict:
    structured_llm = llm.with_structured_output(StudentDataSchema)
    prompt = (
        "You are a precise data extraction specialist.\n"
        "Extract student profile values from the message below.\n"
        "Only extract values that are explicitly stated or clearly implied. "
        "Do not guess or invent values.\n\n"
        f'USER MESSAGE: "{user_message}"'
    )
    try:
        obj = structured_llm.invoke(prompt)
        raw = obj.dict()
        return {k: v for k, v in raw.items() if v is not None}
    except Exception as e:
        print(f"[analyser] Extraction error: {e}")
        return {}


def analyser_node(state: AgentState) -> dict:
    print("--- NODE: ANALYSER ---")

    last_msg        = _last_human(state)
    newly_extracted = _extraction_logic(last_msg)

    current_data = state.get("student_data", {}).copy()
    current_data.update(newly_extracted)

    ml_results = run_ml_pipeline(current_data)

    captured = ", ".join(newly_extracted.keys())
    if not captured:
        analysis_msg = (
            "I've reviewed your message. To give you a more accurate prediction, "
            "could you share your math or reading scores?"
        )
    else:
        score    = ml_results["predicted_score"]
        status   = ml_results["status"]
        category = ml_results["category"]
        analysis_msg = (
            f"I've updated your profile with: **{captured}**.\n\n"
            f"**Predicted Exam Score:** {score}  |  **Status:** {status}  |  **Category:** {category}"
        )

    return {
        "student_data": current_data,
        "ml_results":   ml_results,
        "messages":     [AIMessage(content=analysis_msg)],
        "next_node":    "supervisor",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. RETRIEVER NODE (RAG)
# ═══════════════════════════════════════════════════════════════════════════════

def retriever_node(state: AgentState) -> dict:
    print("--- NODE: RETRIEVER (RAG) ---")

    user_query = _last_human(state)
    category   = state.get("ml_results", {}).get("category", "General")

    docs    = retrieve(user_query, k=2)
    context = "\n\n".join(docs)

    prompt = f"""
You are an Academic Librarian and Tutor.

User Category: {category}
User Question: {user_query}

Retrieved Facts:
{context}

Instructions:
- Answer using ONLY the retrieved facts above
- Tailor the explanation depth to the category ({category}):
  * At-Risk → very simple, step-by-step, lots of examples
  * Average → clear explanation with worked examples
  * High-Performer → detailed, include edge cases and advanced notes
  * General → balanced, accessible explanation
- If the retrieved facts don't cover the question, say so honestly
- Be encouraging and clear
"""

    response = llm.invoke(prompt)

    return {
        "retrieved_docs": docs,
        "messages":       [AIMessage(content=response.content)],
        "next_node":      "supervisor",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. PLANNER NODE
# ═══════════════════════════════════════════════════════════════════════════════

class StudyDay(BaseModel):
    day:            str       = Field(description="e.g., Day 1")
    topic:          str       = Field(description="Focus area for the day")
    activities:     List[str] = Field(description="List of specific, actionable tasks")
    estimated_time: str       = Field(description="e.g., 2 hours")


class WeeklyPlan(BaseModel):
    title:   str            = Field(description="Title of the study plan")
    days:    List[StudyDay] = Field(description="7 individual daily plans")
    summary: str            = Field(
        description="Practical guidance to follow during the plan — NOT a completion message"
    )


def planner_node(state: AgentState) -> dict:
    print("--- NODE: PLANNER ---")

    results  = state.get("ml_results", {})
    category = results.get("category", "Unknown")
    score    = results.get("predicted_score", "N/A")

    last_user_msg      = _last_human(state)
    external_knowledge = "\n".join(state.get("retrieved_docs", []))

    planner_llm = llm.with_structured_output(WeeklyPlan)

    prompt = f"""
You are an expert Study Coach.

STUDENT'S GOAL: "{last_user_msg}"
LEARNING RESOURCES (RAG): "{external_knowledge}"

ACADEMIC DATA (Secondary Context):
- Category: {category}
- Current Score: {score}

YOUR JOB:
Create a 7-day study plan that turns the LEARNING RESOURCES into a concrete daily schedule.

CRITICAL RULES:
1. INDEPENDENCE: If Academic Data is 'Unknown' or missing, build the plan based solely on Goal + Resources.
2. CONTENT: Use specific facts and concepts from the LEARNING RESOURCES to populate each day's activities.
3. ADAPTATION – use Category ONLY to tune pace:
   - 'At-Risk': One concept per day, more breaks, full revision on Day 7.
   - 'Average': Moderate pace, mix of theory and practice.
   - 'High-Performer': Combine multiple concepts, add a Challenge Project on Day 7.
   - 'Unknown': Standard, well-balanced plan. Do NOT mention missing data.
4. QUALITY: Every activity must be specific and actionable, not vague.
5. Do NOT include any message about missing data or personalization limits.
"""

    plan = planner_llm.invoke(prompt)

    tag = (
        f"*Optimised for **{category}** performance level*"
        if category != "Unknown"
        else "*Standard Comprehensive Plan*"
    )

    md = f"### 🗓️ {plan.title}\n{tag}\n\n"
    for d in plan.days:
        md += f"**{d.day}: {d.topic}**\n"
        md += "- " + "\n- ".join(d.activities)
        md += f"\n*Estimated time: {d.estimated_time}*\n\n"

    if plan.summary.strip():
        md += f"---\n**💡 How to Approach This Plan:** {plan.summary}"

    return {
        "study_plan": md,
        "messages":   [AIMessage(content=md)],
        "next_node":  "supervisor",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. QUIZZER NODE
# ═══════════════════════════════════════════════════════════════════════════════

class Question(BaseModel):
    question:       str       = Field(description="The quiz question text")
    options:        List[str] = Field(description="Exactly 4 multiple-choice options")
    correct_answer: str       = Field(description="Exact text of the correct option")
    explanation:    str       = Field(description="Brief explanation of why this is correct")


class QuizSet(BaseModel):
    topic:     str            = Field(description="Topic of the quiz")
    questions: List[Question] = Field(description="Exactly 3 quiz questions")


def quizzer_node(state: AgentState) -> dict:
    print("--- NODE: QUIZZER ---")

    # If we just emitted a question and are awaiting the user's answer, wait
    if state.get("awaiting_answer", False) and isinstance(state["messages"][-1], AIMessage):
        return {"next_node": "supervisor"}

    last_msg = _last_human(state)
    if not last_msg:
        return {"next_node": "supervisor"}

    quiz_active = state.get("quiz_active", False)
    current_idx = state.get("current_q_idx", 0)
    questions   = state.get("quiz_questions", [])
    score       = state.get("quiz_score", 0)

    # ── PHASE A: Initialise new quiz ──────────────────────────────────────────
    if not quiz_active or not questions:
        print("[quizzer] Initialising new quiz...")
        quiz_llm  = llm.with_structured_output(QuizSet)
        prompt    = (
            f"Generate a 3-question multiple-choice quiz about: {last_msg}. "
            "Each question must have exactly 4 distinct options. "
            "Vary difficulty from easy to moderate. Be precise."
        )
        generated = quiz_llm.invoke(prompt)

        q0   = generated.questions[0]
        opts = "\n".join([f"{chr(65+i)}. {o}" for i, o in enumerate(q0.options)])
        msg  = (
            f"🎯 **Quiz Started — {generated.topic}**\n\n"
            f"**Q1 of 3:** {q0.question}\n\n"
            f"{opts}\n\n"
            "👉 Reply with **A**, **B**, **C**, or **D**."
        )
        return {
            "quiz_questions":  [q.model_dump() for q in generated.questions],
            "current_q_idx":   0,
            "quiz_score":      0,
            "quiz_active":     True,
            "awaiting_answer": True,
            "messages":        [AIMessage(content=msg)],
            "next_node":       "supervisor",
        }

    # ── PHASE B: Evaluate previous answer ────────────────────────────────────
    current_q   = questions[current_idx]
    user_ans    = last_msg.strip().lower()
    correct_ans = current_q["correct_answer"].strip().lower()

    # Map A/B/C/D → option text
    option_map = {chr(65 + i).lower(): opt.lower()
                  for i, opt in enumerate(current_q["options"])}
    if user_ans in option_map:
        user_ans = option_map[user_ans]

    is_correct = user_ans == correct_ans
    new_score  = score + 1 if is_correct else score
    feedback   = "✅ **Correct!**" if is_correct \
        else f"❌ **Incorrect.** The right answer was: *{current_q['correct_answer']}*"
    feedback  += f"\n\n💬 *{current_q['explanation']}*"

    # ── PHASE C: Next question or end ─────────────────────────────────────────
    next_idx = current_idx + 1

    if next_idx < len(questions):
        nq   = questions[next_idx]
        opts = "\n".join([f"{chr(65+i)}. {o}" for i, o in enumerate(nq["options"])])
        msg  = (
            f"{feedback}\n\n"
            f"---\n\n"
            f"**Q{next_idx + 1} of {len(questions)}:** {nq['question']}\n\n"
            f"{opts}\n\n"
            "👉 Reply with **A**, **B**, **C**, or **D**."
        )
        return {
            "current_q_idx":   next_idx,
            "quiz_score":      new_score,
            "messages":        [AIMessage(content=msg)],
            "awaiting_answer": True,
            "next_node":       "supervisor",
        }

    # Quiz finished
    total = len(questions)
    if new_score == total:
        closing = "🏆 **Perfect score! Outstanding work!**"
    elif new_score >= total // 2:
        closing = "👍 **Good effort! Review the questions you missed and try again soon.**"
    else:
        closing = "📖 **Keep practising — consistency is key. You'll get there!**"

    final = (
        f"{feedback}\n\n"
        f"---\n\n"
        f"{closing}\n"
        f"**Final Score: {new_score} / {total}**"
    )
    return {
        "quiz_active":     False,
        "awaiting_answer": False,
        "quiz_score":      new_score,
        "messages":        [AIMessage(content=final)],
        "next_node":       "supervisor",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 6. END / RESPONSE NODE
# ═══════════════════════════════════════════════════════════════════════════════

def end_node(state: AgentState) -> dict:
    print("--- NODE: END/RESPONSE ---")

    last_message = state["messages"][-1].content

    prompt = f"""
You are an AI Study Coach generating the FINAL response for a student.

LAST MESSAGE IN CONVERSATION:
"{last_message}"

AVAILABLE CONTEXT:
- Student Data:        {state.get("student_data")}
- ML Analysis:         {state.get("ml_results")}
- Retrieved Knowledge: {state.get("retrieved_docs")}
- Study Plan:          {state.get("study_plan")}
- Quiz Active:         {state.get("quiz_active")}

--- CORE PRINCIPLE ---
Use ONLY context that is directly relevant to the last message.
Never blindly dump all available context.

--- INTENT DETECTION ---
Identify ALL intents present:
GREETING | CLOSING | STUDY_PLAN | CONCEPT_EXPLANATION | PERFORMANCE_INSIGHT | QUIZ | OFF_TOPIC

--- PRIORITY (highest to lowest) ---
1. QUIZ
2. STUDY_PLAN
3. PERFORMANCE_INSIGHT
4. CONCEPT_EXPLANATION
5. GREETING / CLOSING
6. OFF_TOPIC

--- CONTEXT SELECTION ---
- STUDY_PLAN          → use study_plan field
- CONCEPT_EXPLANATION → use retrieved_docs
- PERFORMANCE_INSIGHT → use ml_results (explain in plain English, do not dump raw numbers)
- QUIZ                → refer to quiz context only
- GREETING / CLOSING  → no extra context needed
- OFF_TOPIC           → politely redirect to academic topics

--- FORMAT ---
Single intent  → focused prose, no section headers
Multiple intents → use ONLY these headers in order (omit unused ones):
  📊 Performance Insight
  📚 Concept Explanation
  🗓️ Study Plan

--- STYLE ---
- Warm, encouraging, student-friendly tone
- Never expose raw data dumps or internal system terms
- Keep simple replies concise; structured replies may be detailed
- No filler phrases like "Certainly!", "Of course!", "Great question!"

Generate the best possible response now.
"""

    response = llm.invoke(prompt)
    return {"messages": [AIMessage(content=response.content)]}