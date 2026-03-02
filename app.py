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
