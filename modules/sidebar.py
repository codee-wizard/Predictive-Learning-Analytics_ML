"""
Sidebar navigation and information display.
"""

import streamlit as st
from .icons import icon


def render_sidebar():
    """
    Render the sidebar with navigation and system information.
    
    Returns:
        str: Selected page name ("home", "performance", or "predict")
    """
    with st.sidebar:
        # Header
        st.markdown(f"""
        <div style='padding: 2rem 1rem 1.5rem 1rem; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem;'>
            <div style='display:flex; align-items:center; gap:0.6rem; margin-bottom:0.4rem;'>
                {icon("layers", "#b07d4e")}
                <div style='font-family: Playfair Display, serif; font-size: 1.05rem; font-weight: 700;
                            color: var(--text); line-height: 1.3;'>Student Performance<br>Analytics</div>
            </div>
            <div style='font-size: 0.7rem; color: var(--text-dim); margin-top: 0.4rem;
                        text-transform: uppercase; letter-spacing: 0.06em;'>ML Analytics &middot; Milestone 1</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation buttons
        if st.button("  HOME", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.prediction_run = False
        if st.button("  PERFORMANCE", use_container_width=True):
            st.session_state.page = "performance"
        if st.button("  PREDICT", use_container_width=True):
            st.session_state.page = "predict"

        # Model Performance Info
        st.markdown(f"""
        <div style='margin-top: 1.5rem; padding: 1.2rem; background: var(--bg-card);
                    border-radius: 12px; border: 1px solid var(--border); box-shadow: var(--shadow);'>
            <div style='font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
                        letter-spacing: 0.12em; color: var(--accent); margin-bottom: 0.8rem;
                        border-bottom: 1px solid var(--border); padding-bottom: 0.4rem;'>Model Performance</div>
            <div style='font-size: 0.82rem; color: var(--text); font-weight: 600; margin-bottom: 0.5rem;
                        display:flex; justify-content:space-between;'><span>Accuracy</span><span>91.76%</span></div>
            <div style='font-size: 0.82rem; color: var(--text); font-weight: 600; margin-bottom: 0.5rem;
                        display:flex; justify-content:space-between;'><span>R&#178; Score</span><span>0.9397</span></div>
            <div style='font-size: 0.82rem; color: var(--text); font-weight: 600; margin-bottom: 0.5rem;
                        display:flex; justify-content:space-between;'><span>F1 Score</span><span>0.9176</span></div>
            <div style='font-size: 0.82rem; color: var(--text); font-weight: 600;
                        display:flex; justify-content:space-between;'><span>MAE</span><span>3.04 marks</span></div>
        </div>

        <div style='margin-top: 1rem; padding: 1.2rem; background: var(--bg-card);
                    border-radius: 12px; border: 1px solid var(--border); box-shadow: var(--shadow);'>
            <div style='font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
                        letter-spacing: 0.12em; color: var(--accent); margin-bottom: 0.8rem;
                        border-bottom: 1px solid var(--border); padding-bottom: 0.4rem;'>System Info</div>
            <div style='font-size: 0.82rem; color: var(--text); font-weight: 500; margin-bottom: 0.5rem;
                        display:flex; align-items:center; gap:0.5rem;'>
                {icon("database", "#b07d4e")} 30,640 records loaded
            </div>
            <div style='font-size: 0.82rem; color: var(--text); font-weight: 500; margin-bottom: 0.5rem;
                        display:flex; align-items:center; gap:0.5rem;'>
                {icon("cpu", "#b07d4e")} 3 models active
            </div>
            <div style='font-size: 0.82rem; color: var(--text); font-weight: 500;
                        display:flex; align-items:center; gap:0.5rem;'>
                {icon("settings", "#b07d4e")} 11 features enabled
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Return current page from session state
    return st.session_state.get("page", "home")
