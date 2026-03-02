"""
Home page rendering.
"""

import streamlit as st
from .icons import icon
from .components import capability_card, metric_card, section_title


def render():
    """
    Render the home page with hero section, capabilities, metrics, and insights.
    """
    # Hero Section
    st.markdown("""
    <div class='hero-strip'>
        <div style='font-size: 0.78rem; font-weight: 700; letter-spacing: 0.18em;
                    text-transform: uppercase; color: var(--accent); margin-bottom: 0.7rem;'>
            Gen AI Course &middot; Milestone 1 &middot; February 2026
        </div>
        <div style='font-family: Playfair Display, serif; font-size: 2.6rem; font-weight: 700;
                    color: var(--text); margin-bottom: 0; line-height: 1.15;'>
            Intelligent Learning Analytics<br>&amp; Agentic AI Study Coach
        </div>
        <div style='font-size: 1.05rem; color: var(--text-dim); max-width: 650px;
                    line-height: 1.7; margin-top: 0.7rem;'>
            A complete ML pipeline for student performance analysis &#8212; predicting exam scores,
            classifying Pass/Fail outcomes, and segmenting students into meaningful learner
            categories using 30,640 student records.
        </div>
        <div style='margin-top: 1.8rem; display: flex; gap: 0.8rem; flex-wrap: wrap;'>
            <div style='background: var(--accent); color: white; padding: 0.4rem 1rem;
                        border-radius: 50px; font-size: 0.78rem; font-weight: 600;'>R&#178; = 0.9397</div>
            <div style='background: var(--accent); color: white; padding: 0.4rem 1rem;
                        border-radius: 50px; font-size: 0.78rem; font-weight: 600;'>Accuracy = 91.76%</div>
            <div style='background: var(--accent); color: white; padding: 0.4rem 1rem;
                        border-radius: 50px; font-size: 0.78rem; font-weight: 600;'>3 Learner Segments</div>
            <div style='background: var(--accent); color: white; padding: 0.4rem 1rem;
                        border-radius: 50px; font-size: 0.78rem; font-weight: 600;'>30,640 Records</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Platform Capabilities
    st.markdown(section_title("Platform Capabilities"), unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    caps = [
        (icon("trending_up",    "#b07d4e"), "Score Prediction",
         "Linear Regression predicts ExamScore (R&#178; = 0.94, MAE = 3.0) using 11 academic and behavioural features."),
        (icon("check_circle",   "#b07d4e"), "Pass / Fail Classification",
         "Logistic Regression classifies students with 91.8% accuracy using balanced class weights."),
        (icon("users",          "#b07d4e"), "Learner Segmentation",
         "K-Means (k=3) groups students into At-Risk, Average, and High-Performer clusters based on performance and behaviour."),
        (icon("alert_triangle", "#b07d4e"), "Early Intervention",
         "Flags at-risk students before exams using behavioural and academic features, enabling targeted teacher action."),
    ]
    for col, (ic_svg, title, body) in zip([c1, c2, c3, c4], caps):
        with col:
            st.markdown(f"""
            <div style='background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
                        padding: 2rem 1.8rem; box-shadow: var(--shadow); transition: all 0.2s ease;
                        min-height: 220px; box-sizing: border-box; display: flex; flex-direction: column;'>
                <div style='margin-bottom:0.6rem;'>{ic_svg}</div>
                <div style='font-family: Playfair Display, serif; font-size: 1rem; font-weight: 600;
                            color: var(--text); margin-bottom: 0.5rem;'>{title}</div>
                <div style='font-size: 0.88rem; color: var(--text-dim); line-height: 1.6; margin-top: 0.5rem; flex: 1;'>{body}</div>
            </div>
            """, unsafe_allow_html=True)

    # System Metrics
    st.markdown(section_title("System Metrics"), unsafe_allow_html=True)
    m1, m2, m3, m4, m5 = st.columns(5)
    metrics = [
        ("Total Records",  "30,640"),
        ("Training Set",   "24,512"),
        ("Test Set",       "6,128"),
        ("Input Features", "11"),
        ("ML Models",      "3"),
    ]
    for col, (lbl, val) in zip([m1, m2, m3, m4, m5], metrics):
        with col:
            st.markdown(f"""
            <div style='background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
                        padding: 1.6rem 1rem; box-shadow: var(--shadow); text-align: center;
                        min-height: 110px; box-sizing: border-box; display: flex; flex-direction: column;
                        align-items: center; justify-content: center;'>
                <div class='card-label'>{lbl}</div>
                <div class='card-value' style='font-size: 2rem;'>{val}</div>
            </div>
            """, unsafe_allow_html=True)

    # Key Research Insight
    st.markdown(section_title("Key Research Insight"), unsafe_allow_html=True)
    st.markdown(f"""
    <div class='intel-card' style='background: linear-gradient(135deg, #faf5ee, #f5ede0);
                                   border-left: 4px solid var(--accent);'>
        <div style='display:flex; align-items:center; gap:0.6rem; font-family: Playfair Display, serif;
                    font-size: 1.08rem; font-weight: 600; color: var(--text); margin-bottom: 0.8rem;'>
            {icon("pin", "#b07d4e")}
            Test Preparation is the Single Biggest Academic Differentiator
        </div>
        <div style='font-size: 0.9rem; color: var(--text-dim); line-height: 1.7; margin-bottom: 1.5rem;'>
            All three learner clusters study approximately the same hours per week (~6.91&#8211;6.94 hrs).
            Yet <strong style='color: var(--accent);'>100% of High-Performers completed test prep</strong>
            while 0% of Average students did, and only 8% of At-Risk students did.
            Study time alone does not predict success &#8212; <em>how</em> students prepare matters far more.
        </div>
        <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;'>
            <div style='text-align:center; background: rgba(192,88,64,0.06); border-radius: 10px;
                        padding: 1rem; border: 1px solid rgba(192,88,64,0.2);'>
                <div style='font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.1em; color: #c05840; margin-bottom: 0.3rem;'>At-Risk</div>
                <div style='font-family: Playfair Display, serif; font-size: 1.9rem;
                            font-weight: 700; color: #c05840;'>58.64</div>
                <div style='font-size: 0.75rem; color: var(--text-dim); margin-top: 0.2rem;'>Avg Score &middot; 8% prep</div>
                <div style='font-size: 0.72rem; color: var(--text-dim);'>7,818 students (25.5%)</div>
            </div>
            <div style='text-align:center; background: var(--bg-card); border-radius: 10px;
                        padding: 1rem; border: 1px solid var(--border);'>
                <div style='font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.1em; color: var(--text-dim); margin-bottom: 0.3rem;'>Average</div>
                <div style='font-family: Playfair Display, serif; font-size: 1.9rem;
                            font-weight: 700; color: var(--text);'>68.59</div>
                <div style='font-size: 0.75rem; color: var(--text-dim); margin-top: 0.2rem;'>Avg Score &middot; 0% prep</div>
                <div style='font-size: 0.72rem; color: var(--text-dim);'>13,454 students (43.9%)</div>
            </div>
            <div style='text-align:center; background: rgba(90,138,69,0.07); border-radius: 10px;
                        padding: 1rem; border: 1px solid rgba(90,138,69,0.25);'>
                <div style='font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.1em; color: #5a8a45; margin-bottom: 0.3rem;'>High-Performer</div>
                <div style='font-family: Playfair Display, serif; font-size: 1.9rem;
                            font-weight: 700; color: #5a8a45;'>76.40</div>
                <div style='font-size: 0.75rem; color: var(--text-dim); margin-top: 0.2rem;'>Avg Score &middot; 100% prep</div>
                <div style='font-size: 0.72rem; color: var(--text-dim);'>9,368 students (30.6%)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Team Section
    st.markdown(section_title("Team"), unsafe_allow_html=True)
    st.markdown("""
    <div class='intel-card' style='padding: 1.5rem 2rem;'>
        <div style='display: flex; justify-content: space-between; align-items: center;
                    flex-wrap: wrap; gap: 1rem;'>
            <div>
                <div style='font-size: 0.9rem; color: var(--text); font-weight: 600; margin-bottom: 0.3rem;'>
                    Sathvik Koriginja (2401010231) &nbsp;&middot;&nbsp;
                    Anushka Tyagi (2401010090) &nbsp;&middot;&nbsp;
                    Apoorva Choudhary (2401010092)
                </div>
                <div style='font-size: 0.78rem; color: var(--text-dim);'>
                    Gen AI Course &middot; Milestone 1 &middot; February 2026 &middot;
                    Dataset: Students Exam Scores Extended (Kaggle)
                </div>
            </div>
            <div style='font-size: 0.78rem; color: var(--text-dim);'>
                pandas &middot; numpy &middot; scikit-learn &middot; plotly &middot; streamlit
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
