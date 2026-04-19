# # """
# # Main Streamlit application controller.
# # Handles page routing, initialization, and coordination of all modules.
# # """

# # import streamlit as st
# # from modules.styling import apply_global_styles
# # from modules.sidebar import render_sidebar
# # from modules.home import render as render_home
# # from modules.performance import render as render_performance
# # from modules.predict import render as render_predict


# # # ============================================================
# # # PAGE CONFIG
# # # ============================================================
# # st.set_page_config(
# #     page_title="Student Performance Analytics",
# #     page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path fill='%23b07d4e' d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/></svg>",
# #     layout="wide"
# # )


# # # ============================================================
# # # INITIALIZATION
# # # ============================================================
# # def initialize_session_state():
# #     """
# #     Initialize session state variables.
# #     """
# #     if 'prediction_run' not in st.session_state:
# #         st.session_state.prediction_run = False
# #     if 'page' not in st.session_state:
# #         st.session_state.page = "home"


# # # ============================================================
# # # MAIN APPLICATION CONTROLLER
# # # ============================================================
# # def main():
# #     """
# #     Main application controller that coordinates all modules.
# #     """
# #     # Initialize session state
# #     initialize_session_state()
    
# #     # Apply global styles
# #     apply_global_styles()
    
# #     # Render sidebar and get selected page
# #     selected_page = render_sidebar()
    
# #     # Route to appropriate page
# #     if selected_page == "home":
# #         render_home()
# #     elif selected_page == "performance":
# #         render_performance()
# #     elif selected_page == "predict":
# #         render_predict()


# # # ============================================================
# # # RUN APPLICATION
# # # ============================================================
# # if __name__ == "__main__":
# #     main()


# """
# app.py – Predictive Learning Analytics + AI Study Coach
# ========================================================
# CHANGES FROM ORIGINAL:
#   1. Sidebar now has a page selector: "📊 Dashboard" | "🤖 AI Study Coach"
#   2. The "AI Study Coach" page renders a full ChatGPT-style chat interface
#      powered by LangGraph + Groq.
#   3. All original Dashboard code is preserved exactly as-is inside the
#      `show_dashboard()` function.
# """

# import os
# import streamlit as st
# from dotenv import load_dotenv

# # Load .env (GROQ_API_KEY, etc.)
# load_dotenv()

# # ─────────────────────────────────────────────
# # PAGE CONFIG  (must be the very first st call)
# # ─────────────────────────────────────────────
# st.set_page_config(
#     page_title="Predictive Learning Analytics",
#     page_icon="🎓",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # ─────────────────────────────────────────────
# # SIDEBAR NAVIGATION
# # ─────────────────────────────────────────────
# st.sidebar.title("🎓 Learning Analytics")
# page = st.sidebar.selectbox(
#     "Navigate",
#     ["📊 Dashboard", "🤖 AI Study Coach"],
#     index=0,
# )
# st.sidebar.markdown("---")
# st.sidebar.info(
#     "**AI Study Coach** is powered by LangGraph + Groq LLaMA 3.3.\n\n"
#     "It can analyse your performance, explain concepts, generate study plans, and quiz you!"
# )


# # ═══════════════════════════════════════════════════════════════════════════════
# # DASHBOARD  (original project – DO NOT MODIFY)
# # ═══════════════════════════════════════════════════════════════════════════════

# def show_dashboard():
    
#     """
# Main Streamlit application controller.
# Handles page routing, initialization, and coordination of all modules.
# """

#     import streamlit as st
#     from modules.styling import apply_global_styles
#     from modules.sidebar import render_sidebar
#     from modules.home import render as render_home
#     from modules.performance import render as render_performance
#     from modules.predict import render as render_predict


#     # ============================================================
#     # PAGE CONFIG
#     # ============================================================
#     st.set_page_config(
#         page_title="Student Performance Analytics",
#         page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path fill='%23b07d4e' d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/></svg>",
#         layout="wide"
#     )


#     # ============================================================
#     # INITIALIZATION
#     # ============================================================
#     def initialize_session_state():
#         """
#         Initialize session state variables.
#         """
#         if 'prediction_run' not in st.session_state:
#             st.session_state.prediction_run = False
#         if 'page' not in st.session_state:
#             st.session_state.page = "home"


#     # ============================================================
#     # MAIN APPLICATION CONTROLLER
#     # ============================================================
#     def main():
#         """
#         Main application controller that coordinates all modules.
#         """
#         # Initialize session state
#         initialize_session_state()
        
#         # Apply global styles
#         apply_global_styles()
        
#         # Render sidebar and get selected page
#         selected_page = render_sidebar()
        
#         # Route to appropriate page
#         if selected_page == "home":
#             render_home()
#         elif selected_page == "performance":
#             render_performance()
#         elif selected_page == "predict":
#             render_predict()


#     # ============================================================
#     # RUN APPLICATION
#     # ============================================================
#     if __name__ == "__main__":
#         main()


# # ═══════════════════════════════════════════════════════════════════════════════
# # AI STUDY COACH PAGE
# # ═══════════════════════════════════════════════════════════════════════════════

# def _build_initial_agent_state() -> dict:
#     """Return a fresh AgentState-compatible dict."""
#     return {
#         "messages":           [],
#         "student_data":       {},
#         "ml_results":         {},
#         "retrieved_docs":     [],
#         "quiz_questions":     [],
#         "current_q_idx":      0,
#         "quiz_score":         0,
#         "quiz_active":        False,
#         "awaiting_answer":    False,
#         "study_plan":         "",
#         "planner_notes":      "",
#         "plan":               [],
#         "current_step_index": 0,
#         "next_node":          "",
#     }


# def _init_session():
#     """Initialise Streamlit session state for the chat page."""
#     if "agent_state" not in st.session_state:
#         st.session_state.agent_state = _build_initial_agent_state()
#     if "chat_history" not in st.session_state:
#         # Each entry: {"role": "user"|"assistant", "content": str}
#         st.session_state.chat_history = []


# def _get_last_ai_content(result_state: dict) -> str:
#     """Extract the latest AIMessage content from the returned state."""
#     from langchain_core.messages import AIMessage
#     ai_msgs = [m for m in result_state["messages"] if isinstance(m, AIMessage)]
#     return ai_msgs[-1].content if ai_msgs else "*(no response)*"


# def show_ai_study_coach():
#     """Render the AI Study Coach chat page."""
#     # ── Imports ───────────────────────────────────────────────────────────────
#     from langchain_core.messages import HumanMessage

#     # ── Guard: API key must be set ────────────────────────────────────────────
#     if not os.getenv("GROQ_API_KEY"):
#         st.error(
#             "⚠️ **GROQ_API_KEY** not found.\n\n"
#             "Set it in a `.env` file or as an environment variable, then restart the app."
#         )
#         return

#     # ── Lazy-import the compiled LangGraph app ────────────────────────────────
#     try:
#         from agent import coach_app
#     except Exception as e:
#         st.error(f"❌ Failed to load agent: {e}")
#         st.exception(e)
#         return

#     _init_session()

#     # ── Header ────────────────────────────────────────────────────────────────
#     st.title("🤖 AI Study Coach")
#     st.caption(
#         "Chat with your personal AI tutor. I can analyse your performance, "
#         "explain concepts, build a 7-day study plan, or quiz you on any topic."
#     )

#     # ── Sidebar controls ──────────────────────────────────────────────────────
#     with st.sidebar:
#         st.markdown("### 🎛️ Session Controls")
#         if st.button("🔄 New Conversation", use_container_width=True):
#             st.session_state.agent_state  = _build_initial_agent_state()
#             st.session_state.chat_history = []
#             st.rerun()

#         # Show live student snapshot if available
#         ml = st.session_state.agent_state.get("ml_results", {})
#         if ml and ml.get("predicted_score") != "N/A":
#             st.markdown("---")
#             st.markdown("#### 📈 Current Snapshot")
#             st.metric("Predicted Score", ml.get("predicted_score", "–"))
#             st.metric("Status",          ml.get("status",          "–"))
#             st.metric("Category",        ml.get("category",        "–"))

#         quiz_active = st.session_state.agent_state.get("quiz_active", False)
#         if quiz_active:
#             st.markdown("---")
#             q_idx = st.session_state.agent_state.get("current_q_idx", 0)
#             q_tot = len(st.session_state.agent_state.get("quiz_questions", []))
#             score = st.session_state.agent_state.get("quiz_score", 0)
#             st.markdown("#### 🎯 Quiz in Progress")
#             st.progress((q_idx) / max(q_tot, 1))
#             st.caption(f"Question {q_idx + 1} of {q_tot}  |  Score: {score}")

#     # ── Render existing chat history ──────────────────────────────────────────
#     for entry in st.session_state.chat_history:
#         with st.chat_message(entry["role"]):
#             st.markdown(entry["content"])

#     # ── Handle new user input ──────────────────────────────────────────────────
#     user_input = st.chat_input("Ask me anything — scores, concepts, study plans, quizzes…")

#     if user_input:
#         # Display user message immediately
#         with st.chat_message("user"):
#             st.markdown(user_input)
#         st.session_state.chat_history.append({"role": "user", "content": user_input})

#         # Build updated messages list for the agent
#         current_state = st.session_state.agent_state.copy()
#         current_state["messages"] = current_state["messages"] + [
#             HumanMessage(content=user_input)
#         ]

#         # Run the LangGraph agent
#         with st.chat_message("assistant"):
#             with st.spinner("Thinking…"):
#                 try:
#                     result_state = coach_app.invoke(current_state)
#                     ai_response  = _get_last_ai_content(result_state)

#                     # Persist updated agent state (preserves memory across turns)
#                     st.session_state.agent_state = result_state

#                     st.markdown(ai_response)
#                     st.session_state.chat_history.append(
#                         {"role": "assistant", "content": ai_response}
#                     )
#                 except Exception as e:
#                     err_msg = f"⚠️ An error occurred: {e}"
#                     st.error(err_msg)
#                     st.session_state.chat_history.append(
#                         {"role": "assistant", "content": err_msg}
#                     )

#         st.rerun()

#     # ── Starter prompts (shown when conversation is empty) ────────────────────
#     if not st.session_state.chat_history:
#         st.markdown("---")
#         st.markdown("#### 💡 Try asking…")
#         cols = st.columns(2)
#         starters = [
#             ("📊 Analyse my scores",
#              "I scored 68 in math and 75 in reading. How am I performing?"),
#             ("📚 Explain a concept",
#              "Can you explain quadratic equations in simple terms?"),
#             ("🗓️ Get a study plan",
#              "Create a 7-day study plan to improve my algebra skills."),
#             ("🎯 Take a quiz",
#              "Give me a quiz on trigonometry basics."),
#         ]
#         for i, (label, prompt_text) in enumerate(starters):
#             col = cols[i % 2]
#             if col.button(label, use_container_width=True, key=f"starter_{i}"):
#                 # Inject the starter as if the user typed it
#                 with st.chat_message("user"):
#                     st.markdown(prompt_text)
#                 st.session_state.chat_history.append(
#                     {"role": "user", "content": prompt_text}
#                 )

#                 from langchain_core.messages import HumanMessage
#                 current_state = st.session_state.agent_state.copy()
#                 current_state["messages"] = current_state["messages"] + [
#                     HumanMessage(content=prompt_text)
#                 ]

#                 with st.chat_message("assistant"):
#                     with st.spinner("Thinking…"):
#                         try:
#                             result_state = coach_app.invoke(current_state)
#                             ai_response  = _get_last_ai_content(result_state)
#                             st.session_state.agent_state = result_state
#                             st.markdown(ai_response)
#                             st.session_state.chat_history.append(
#                                 {"role": "assistant", "content": ai_response}
#                             )
#                         except Exception as e:
#                             st.error(str(e))
#                 st.rerun()


# # ═══════════════════════════════════════════════════════════════════════════════
# # ROUTER
# # ═══════════════════════════════════════════════════════════════════════════════

# if page == "📊 Dashboard":
#     show_dashboard()
# else:
#     show_ai_study_coach()



"""
app.py – Predictive Learning Analytics + AI Study Coach
========================================================
Changes from v1:
  1. Sidebar uses styled buttons (not dropdown) to switch pages
  2. AI Study Coach page: fully redesigned chat UI matching M1 theme
  3. Chat history persisted in SQLite (public / shared sessions)
  4. Removed "Current Snapshot" sidebar panel from coach page
  5. nodes.py strictly follows Colab logic
"""

import os
import uuid
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# PAGE CONFIG (must be FIRST st call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Predictive Learning Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL STYLES (from styles.py)
# ─────────────────────────────────────────────
from styles import apply_global_styles
apply_global_styles()

# ─────────────────────────────────────────────
# DB INIT
# ─────────────────────────────────────────────
from agent.chat_history import (
    init_db, create_session, session_exists, save_message,
    load_messages, list_sessions, update_session_title, delete_session,
)
init_db()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════

def _sidebar_nav():
    with st.sidebar:
        st.markdown(
            '<div class="page-title" style="font-size:1.35rem; margin-bottom:0.1rem;">🎓 Learning Analytics</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="page-subtitle" style="font-size:0.78rem; margin-bottom:1.4rem;">Predictive · Adaptive · Intelligent</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<hr style="border-color:var(--border); margin:0 0 1rem 0;">', unsafe_allow_html=True)

        # ── Page buttons ──────────────────────────────────────────────────────
        current = st.session_state.get("current_page", "dashboard")

        dash_style = "nav-btn-active" if current == "dashboard" else ""
        coach_style = "nav-btn-active" if current == "coach" else ""

        st.markdown(f'<div class="{dash_style}">', unsafe_allow_html=True)
        if st.button("📊  Dashboard", use_container_width=True, key="nav_dash"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f'<div class="{coach_style}">', unsafe_allow_html=True)
        if st.button("🤖  AI Study Coach", use_container_width=True, key="nav_coach"):
            st.session_state.current_page = "coach"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Coach-specific sidebar content ────────────────────────────────────
        if current == "coach":
            st.markdown('<hr style="border-color:var(--border); margin:1.2rem 0 0.8rem 0;">', unsafe_allow_html=True)

            # New conversation button
            if st.button("✏️  New Conversation", use_container_width=True, key="new_conv"):
                _start_new_session()
                st.rerun()

            # Quiz progress (only when quiz is active)
            agent_state = st.session_state.get("agent_state", {})
            if agent_state.get("quiz_active", False):
                q_idx = agent_state.get("current_q_idx", 0)
                q_tot = len(agent_state.get("quiz_questions", []))
                q_score = agent_state.get("quiz_score", 0)
                pct = int((q_idx / max(q_tot, 1)) * 100)

                st.markdown(
                    f"""
                    <div style="margin-top:0.8rem;">
                      <div class="sidebar-section-label">🎯 Quiz in Progress</div>
                      <div class="quiz-progress-bar">
                        <div class="quiz-progress-fill" style="width:{pct}%"></div>
                      </div>
                      <div style="font-size:0.78rem; color:var(--text-dim); margin-top:0.4rem;">
                        Question {q_idx + 1} of {q_tot} &nbsp;·&nbsp; Score: {q_score}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Past sessions
            st.markdown('<div class="sidebar-section-label">🕒 Past Conversations</div>', unsafe_allow_html=True)
            sessions = list_sessions(limit=20)
            if sessions:
                current_sid = st.session_state.get("session_id", "")
                for s in sessions:
                    sid   = s["session_id"]
                    title = s["title"] or "Untitled"
                    count = s["message_count"]
                    dt    = s["started_at"][:10] if s["started_at"] else ""
                    active_style = "border-color:var(--accent);" if sid == current_sid else ""

                    st.markdown(
                        f"""
                        <div class="session-item" style="{active_style}">
                          <div class="session-title">{title}</div>
                          <div class="session-meta">{dt} · {count} messages</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button("Load", key=f"load_{sid}", use_container_width=True):
                            _load_session(sid)
                            st.rerun()
                    with col2:
                        if st.button("🗑", key=f"del_{sid}", use_container_width=True):
                            delete_session(sid)
                            if sid == current_sid:
                                _start_new_session()
                            st.rerun()
            else:
                st.markdown(
                    '<div style="font-size:0.8rem; color:var(--text-dim);">No conversations yet.</div>',
                    unsafe_allow_html=True,
                )


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _build_fresh_agent_state() -> dict:
    return {
        "messages":           [],
        "student_data":       {},
        "ml_results":         {},
        "retrieved_docs":     [],
        "quiz_questions":     [],
        "current_q_idx":      0,
        "quiz_score":         0,
        "quiz_active":        False,
        "awaiting_answer":    False,
        "study_plan":         "",
        "planner_notes":      "",
        "plan":               [],
        "current_step_index": 0,
        "next_node":          "",
    }


def _start_new_session():
    new_sid = str(uuid.uuid4())
    create_session(new_sid)
    st.session_state.session_id    = new_sid
    st.session_state.chat_display  = []        # display history (role/content dicts)
    st.session_state.agent_state   = _build_fresh_agent_state()


def _load_session(session_id: str):
    """Load an existing session from SQLite into st.session_state."""
    from langchain_core.messages import HumanMessage, AIMessage as AI

    msgs_db = load_messages(session_id)
    display = [{"role": m["role"], "content": m["content"]} for m in msgs_db]

    # Rebuild agent messages list
    lc_msgs = []
    for m in msgs_db:
        if m["role"] == "user":
            lc_msgs.append(HumanMessage(content=m["content"]))
        else:
            lc_msgs.append(AI(content=m["content"]))

    new_state = _build_fresh_agent_state()
    new_state["messages"] = lc_msgs

    st.session_state.session_id   = session_id
    st.session_state.chat_display = display
    st.session_state.agent_state  = new_state


def _init_coach_session():
    """Ensure a valid session exists in st.session_state."""
    if "session_id" not in st.session_state:
        _start_new_session()
    elif not session_exists(st.session_state.session_id):
        create_session(st.session_state.session_id)

    if "chat_display" not in st.session_state:
        st.session_state.chat_display = []

    if "agent_state" not in st.session_state:
        st.session_state.agent_state = _build_fresh_agent_state()


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD (original project — paste your real code inside here)
# ═══════════════════════════════════════════════════════════════════════════════

def show_dashboard():
 
    """
Main Streamlit application controller.
Handles page routing, initialization, and coordination of all modules.
"""

    import streamlit as st
    from modules.styling import apply_global_styles
    from modules.sidebar import render_sidebar
    from modules.home import render as render_home
    from modules.performance import render as render_performance
    from modules.predict import render as render_predict


    # ============================================================
    # PAGE CONFIG
    # ============================================================
    st.set_page_config(
        page_title="Student Performance Analytics",
        page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path fill='%23b07d4e' d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/></svg>",
        layout="wide"
    )


    # ============================================================
    # INITIALIZATION
    # ============================================================
    def initialize_session_state():
        """
        Initialize session state variables.
        """
        if 'prediction_run' not in st.session_state:
            st.session_state.prediction_run = False
        if 'page' not in st.session_state:
            st.session_state.page = "home"


    # ============================================================
    # MAIN APPLICATION CONTROLLER
    # ============================================================
    def main():
        """
        Main application controller that coordinates all modules.
        """
        # Initialize session state
        initialize_session_state()
        
        # Apply global styles
        apply_global_styles()
        
        # Render sidebar and get selected page
        selected_page = render_sidebar()
        
        # Route to appropriate page
        if selected_page == "home":
            render_home()
        elif selected_page == "performance":
            render_performance()
        elif selected_page == "predict":
            render_predict()


    # ============================================================
    # RUN APPLICATION
    # ============================================================
    if __name__ == "__main__":
        main()



# ═══════════════════════════════════════════════════════════════════════════════
# AI STUDY COACH PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def _get_last_ai_content(result_state: dict) -> str:
    from langchain_core.messages import AIMessage
    ai_msgs = [m for m in result_state["messages"] if isinstance(m, AIMessage)]
    return ai_msgs[-1].content if ai_msgs else "*(no response)*"


def _handle_user_message(user_input: str, coach_app):
    """Run the agent with user_input, persist to DB, update session state."""
    from langchain_core.messages import HumanMessage

    sid = st.session_state.session_id

    # Save user message to DB and display list
    save_message(sid, "user", user_input)
    st.session_state.chat_display.append({"role": "user", "content": user_input})

    # Auto-title the session from first user message
    sessions = list_sessions()
    current  = next((s for s in sessions if s["session_id"] == sid), None)
    if current and (current["title"] in ("New Conversation", "") or current["message_count"] <= 1):
        update_session_title(sid, user_input[:55] + ("…" if len(user_input) > 55 else ""))

    # Build updated agent state
    current_state = dict(st.session_state.agent_state)
    current_state["messages"] = current_state["messages"] + [
        HumanMessage(content=user_input)
    ]

    # Invoke the LangGraph agent
    result_state = coach_app.invoke(current_state)
    ai_response  = _get_last_ai_content(result_state)

    # Persist
    save_message(sid, "assistant", ai_response)
    st.session_state.chat_display.append({"role": "assistant", "content": ai_response})
    st.session_state.agent_state = result_state

    return ai_response


def show_ai_study_coach():
    # ── Guard: API key ────────────────────────────────────────────────────────
    if not os.getenv("GROQ_API_KEY"):
        st.markdown(
            '<div class="chat-page-header">'
            '<div class="chat-page-title">🤖 AI Study Coach</div>'
            '<div class="chat-page-sub">Configuration required</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.error(
            "**GROQ_API_KEY not found.**\n\n"
            "Add `GROQ_API_KEY=your_key` to a `.env` file in the project root, then restart."
        )
        return

    # ── Lazy-load LangGraph app ───────────────────────────────────────────────
    try:
        from agent import coach_app
    except Exception as e:
        st.error(f"Failed to load agent: {e}")
        st.exception(e)
        return

    _init_coach_session()

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="chat-page-header">
            <div class="chat-page-title">🤖 AI Study Coach</div>
            <div class="chat-page-sub">
                Ask me anything — performance analysis, concept explanations,
                7-day study plans, or a quick quiz.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Starter prompts (only when chat is empty) ─────────────────────────────
    if not st.session_state.chat_display:
        st.markdown(
            '<div style="font-size:0.82rem; font-weight:700; letter-spacing:0.1em; '
            'text-transform:uppercase; color:var(--text-dim); margin-bottom:0.8rem;">'
            'Try asking…</div>',
            unsafe_allow_html=True,
        )
        starters = [
            ("📊 Analyse my performance",
             "I scored 68 in math and 75 in reading. Am I performing well?"),
            ("📚 Explain a concept",
             "Can you explain quadratic equations in simple terms?"),
            ("🗓️ Build a study plan",
             "Give me a 7-day plan to improve my algebra skills."),
            ("🎯 Take a quiz",
             "Give me a quiz on trigonometry basics."),
        ]
        cols = st.columns(4)
        for i, (label, prompt_text) in enumerate(starters):
            with cols[i]:
                st.markdown('<div class="starter-chip">', unsafe_allow_html=True)
                if st.button(label, key=f"starter_{i}", use_container_width=True):
                    with st.spinner("Thinking…"):
                        try:
                            _handle_user_message(prompt_text, coach_app)
                        except Exception as e:
                            st.error(str(e))
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Chat history ──────────────────────────────────────────────────────────
    for entry in st.session_state.chat_display:
        with st.chat_message(entry["role"]):
            st.markdown(entry["content"])

    # ── Chat input ────────────────────────────────────────────────────────────
    user_input = st.chat_input("Message your AI Study Coach…")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    ai_response = _handle_user_message(user_input, coach_app)
                    st.markdown(ai_response)
                    # Remove the duplicate we just manually displayed
                    st.session_state.chat_display.pop()   # remove assistant entry
                    st.session_state.chat_display.pop()   # remove user entry
                except Exception as e:
                    err = f"⚠️ Error: {e}"
                    st.error(err)

        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════

if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

_sidebar_nav()

if st.session_state.current_page == "dashboard":
    show_dashboard()
else:
    show_ai_study_coach()