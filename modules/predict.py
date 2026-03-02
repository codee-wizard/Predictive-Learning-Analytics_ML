"""
Predict page rendering with student input form and prediction results.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from .icons import icon, ICONS
from .components import page_title, page_subtitle, section_title, recommendation_card
from .model_loader import load_models


def render():
    """
    Render the predict page with input form and prediction results.
    """
    models = load_models()
    
    linear_model = models['linear_model']
    logistic_model = models['logistic_model']
    kmeans_model = models['kmeans_model']
    scaler_reg = models['scaler_reg']
    scaler_clf = models['scaler_clf']
    scaler_cluster = models['scaler_cluster']

    if None in [linear_model, logistic_model, scaler_reg, scaler_clf]:
        st.warning("Prediction Engine unavailable. Please verify model files in /models/")
        return

    st.markdown(page_title("Student Success Predictor"), unsafe_allow_html=True)
    st.markdown(page_subtitle("Enter the student's academic and behavioural profile to generate ML-powered predictions."), unsafe_allow_html=True)

    col_input, col_result = st.columns([1, 1.2], gap="large")

    # ── INPUT PANEL ──
    with col_input:
        st.markdown("""
        <div style='font-family: Playfair Display, serif; font-size: 1.05rem; font-weight: 600;
                    color: var(--text); margin-bottom: 1rem;'>Student Profile</div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(f"<div class='input-group-header'>{icon('academic','#b07d4e')} &nbsp; Academic Baseline</div>", unsafe_allow_html=True)
            math_score    = st.slider("Math Score", 0, 100, 65)
            reading_score = st.slider("Reading Score", 0, 100, 68)
            test_prep_label = st.selectbox(
                "Test Preparation",
                ["Completed", "Not Completed"],
                help="Students who complete test prep are significantly more likely to be High-Performers"
            )
            test_prep = 0 if test_prep_label == "Completed" else 1

        st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(f"<div class='input-group-header'>{icon('clock','#b07d4e')} &nbsp; Weekly Habits</div>", unsafe_allow_html=True)
            study_label = st.selectbox(
                "Weekly Study Time",
                ["Low — less than 5 hrs (2.5 hrs avg)",
                 "Moderate — 5 to 10 hrs (7.5 hrs avg)",
                 "High — more than 10 hrs (12.0 hrs avg)"],
                index=1
            )
            study_hours_map = {
                "Low — less than 5 hrs (2.5 hrs avg)":    2.5,
                "Moderate — 5 to 10 hrs (7.5 hrs avg)":   7.5,
                "High — more than 10 hrs (12.0 hrs avg)":  12.0,
            }
            study_hours = study_hours_map[study_label]

            sport_label    = st.select_slider("Sport Participation", options=["Never", "Sometimes", "Regularly"], value="Sometimes")
            practice_sport = {"Never": 0, "Sometimes": 1, "Regularly": 2}[sport_label]

        st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(f"<div class='input-group-header'>{icon('user','#b07d4e')} &nbsp; Demographics &amp; Background</div>", unsafe_allow_html=True)
            educ_map = {
                "High School":        1,
                "Some College":       2,
                "Associate's Degree": 3,
                "Bachelor's Degree":  4,
                "Master's Degree":    5,
            }
            educ_label  = st.selectbox("Parent Education Level", list(educ_map.keys()))
            parent_educ = educ_map[educ_label]

            c1, c2 = st.columns(2)
            with c1:
                lunch_label = st.radio("Lunch Type", ["Standard", "Reduced/Free"], horizontal=True)
                lunch_type  = 1 if lunch_label == "Standard" else 0
            with c2:
                gender_label = st.radio("Gender", ["Female", "Male"], horizontal=True)
                gender_male  = 1 if gender_label == "Male" else 0

            c3, c4 = st.columns(2)
            with c3:
                first_child_label = st.radio("First Child?", ["Yes", "No"], horizontal=True)
                is_first_child    = 1 if first_child_label == "Yes" else 0
            with c4:
                transport_label = st.radio("Transport", ["School Bus", "Public"], horizontal=True)
                transport_bus   = 1 if transport_label == "School Bus" else 0

            nr_siblings = st.number_input("Number of Siblings", min_value=0, max_value=6, value=1)

        st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
        if st.button("UPDATE INSIGHTS", type="primary", use_container_width=True):
            st.session_state.prediction_run = True

    # ── RESULTS PANEL ──
    with col_result:
        if not st.session_state.prediction_run:
            st.markdown("""
            <div style='background: var(--bg-card); border: 1.5px dashed var(--border);
                        border-radius: var(--radius); height: 880px; display: flex;
                        flex-direction: column; align-items: center; justify-content: center;
                        text-align: center; padding: 4rem;'>
                <div style='width:48px; height:48px; border-radius:50%; background:rgba(176,125,78,0.08);
                            display:flex; align-items:center; justify-content:center; margin: 0 auto 1.2rem auto;'>
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                         fill="none" stroke="#b07d4e" stroke-width="1.5" opacity="0.4"
                         stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
                    </svg>
                </div>
                <div style='font-family: Playfair Display, serif; font-size: 1.2rem;
                            font-weight: 600; color: var(--text-dim);'>Ready for Input</div>
                <div style='font-size: 0.88rem; color: var(--text-dim); margin-top: 0.8rem;
                            max-width: 260px; line-height: 1.6; opacity: 0.7;'>
                    Fill in the student profile on the left and click
                    <strong>Update Insights</strong> to generate predictions.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Feature order: MathScore, ReadingScore, WklyStudyHours, ParentEduc,
            # TestPrep_none, LunchType_standard, PracticeSport, NrSiblings,
            # Gender_male, IsFirstChild_yes, TransportMeans_school_bus
            input_data = np.array([[
                math_score, reading_score, study_hours, parent_educ,
                test_prep,  lunch_type,    practice_sport, nr_siblings,
                gender_male, is_first_child, transport_bus
            ]])

            input_reg = scaler_reg.transform(input_data)
            input_clf = scaler_clf.transform(input_data)

            predicted_score  = float(np.clip(linear_model.predict(input_reg)[0], 0, 100))
            predicted_result = logistic_model.predict(input_clf)[0]
            proba            = logistic_model.predict_proba(input_clf)[0]
            fail_prob = proba[0] * 100
            pass_prob = proba[1] * 100
            conf_val  = pass_prob if predicted_result == "Pass" else fail_prob

            # Clustering: ExamScore, WklyStudyHours, ParentEduc, LunchType_standard, TestPrep_none, PracticeSport
            cluster_input = np.array([[
                predicted_score, study_hours, parent_educ,
                lunch_type, test_prep, practice_sport
            ]])
            if scaler_cluster and kmeans_model:
                cluster_scaled = scaler_cluster.transform(cluster_input)
                raw_label      = kmeans_model.predict(cluster_scaled)[0]
                centers        = kmeans_model.cluster_centers_
                order          = np.argsort(centers[:, 0])
                name_map       = {order[0]: "At-Risk", order[1]: "Average", order[2]: "High-Performer"}
                learner_seg    = name_map[raw_label]
            else:
                learner_seg = "At-Risk" if predicted_score < 63.6 else ("Average" if predicted_score < 72.5 else "High-Performer")

            # Score-based alignment overrides
            if predicted_score < 60:
                learner_seg = "At-Risk"
            elif predicted_score > 82:
                learner_seg = "High-Performer"
            else:
                if learner_seg == "High-Performer" and predicted_score < 76:
                    learner_seg = "Average"
                if learner_seg == "At-Risk" and predicted_score > 65:
                    learner_seg = "Average"

            is_pass      = predicted_result == "Pass"
            result_color = "#5a8a45" if is_pass else "#c05840"
            seg_colors   = {"At-Risk": "#c05840", "Average": "#7a6a55", "High-Performer": "#5a8a45"}
            seg_icons_svg = {
                "At-Risk":        ICONS["alert_sm"],
                "Average":        ICONS["minus_circle"],
                "High-Performer": ICONS["star"],
            }
            seg_color = seg_colors.get(learner_seg, "#7a6a55")
            seg_icon  = seg_icons_svg.get(learner_seg, "")

            # Executive Summary
            st.markdown("<div class='section-title' style='margin-top:0;'>Executive Summary</div>", unsafe_allow_html=True)
            e1, e2, e3 = st.columns(3)
            card_style = "background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.4rem 1rem; box-shadow: var(--shadow); text-align: center; height: 145px; box-sizing: border-box; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.2rem;"
            with e1:
                st.markdown(f"""
                <div style='{card_style} border-top: 3px solid var(--accent);'>
                    <div class='card-label'>Predicted Score</div>
                    <div style='font-family:Playfair Display,serif; font-size:2.3rem; font-weight:700; color:var(--accent);'>{predicted_score:.1f}%</div>
                    <div style='font-size:0.72rem; color:var(--text-dim);'>Threshold: 69.0</div>
                </div>
                """, unsafe_allow_html=True)
            with e2:
                st.markdown(f"""
                <div style='{card_style} border-top: 3px solid {result_color};'>
                    <div class='card-label'>Outcome</div>
                    <div style='font-family:Playfair Display,serif; font-size:2.3rem; font-weight:700; color:{result_color};'>{predicted_result.upper()}</div>
                    <div style='font-size:0.72rem; color:var(--text-dim);'>Confidence: {conf_val:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
            with e3:
                st.markdown(f"""
                <div style='{card_style} border-top: 3px solid {seg_color};'>
                    <div class='card-label'>Learner Segment</div>
                    <div style='margin:0.2rem 0; display:flex; justify-content:center;'>{seg_icon}</div>
                    <div style='font-family:Playfair Display,serif; font-size:1.1rem; font-weight:700; color:{seg_color};'>{learner_seg}</div>
                </div>
                """, unsafe_allow_html=True)

            # Performance Analytics
            st.markdown(section_title("Performance Analytics"), unsafe_allow_html=True)
            chart_col, gauge_col = st.columns([1.2, 1])

            with chart_col:
                fig_bar = go.Figure(go.Bar(
                    x=["Math", "Reading", "Predicted Exam"],
                    y=[math_score, reading_score, predicted_score],
                    marker=dict(
                        color=["#d4c4b0", "#c4b8a0", "#b07d4e"],
                        line=dict(color="white", width=1.5)
                    ),
                    width=0.45,
                    text=[f"{math_score}", f"{reading_score}", f"{predicted_score:.1f}"],
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(color="white", size=13, family="DM Sans", weight=700)
                ))
                fig_bar.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=20, b=5, l=5, r=5),
                    height=230,
                    yaxis=dict(range=[0, 110], gridcolor="rgba(100,80,50,0.07)",
                               tickfont=dict(color="#7a6a55", size=10)),
                    xaxis=dict(tickfont=dict(color="#7a6a55", size=11)),
                    showlegend=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with gauge_col:
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=pass_prob,
                    title=dict(text="Pass Confidence %",
                               font=dict(color="#7a6a55", size=11, family="DM Sans")),
                    number=dict(font=dict(color="#2c2416", size=30, family="Playfair Display"),
                                suffix="%"),
                    gauge=dict(
                        axis=dict(range=[0, 100], tickfont=dict(color="#7a6a55", size=8)),
                        bar=dict(color="#b07d4e", thickness=0.25),
                        bgcolor="rgba(0,0,0,0)",
                        borderwidth=0,
                        steps=[
                            dict(range=[0,  50], color="rgba(192,88,64,0.10)"),
                            dict(range=[50, 75], color="rgba(176,125,78,0.10)"),
                            dict(range=[75,100], color="rgba(90,138,69,0.10)"),
                        ],
                        threshold=dict(line=dict(color="#b07d4e", width=2),
                                       thickness=0.75, value=50)
                    )
                ))
                fig_gauge.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=30, b=5, l=15, r=15),
                    height=230,
                    font=dict(family="DM Sans")
                )
                st.plotly_chart(fig_gauge, use_container_width=True)

            # Strategic Recommendations
            st.markdown(section_title("Strategic Recommendations"), unsafe_allow_html=True)
            recs = []

            if test_prep == 1:
                recs.append((icon("clipboard", "#b07d4e"), "Enrol in Test Preparation",
                    "Student has not completed test prep. Clustering shows 100% of High-Performers "
                    "completed it vs 0% of Average students &#8212; this is the single most actionable improvement available."))
            else:
                recs.append((icon("award", "#5a8a45"), "Sustain and Advance",
                    "Student has completed test preparation &#8212; the strongest differentiator in the dataset. "
                    "Maintain consistency and explore advanced peer mentoring or enrichment programmes."))

            if study_hours < 7.5:
                recs.append((icon("arrow_up", "#b07d4e"), "Increase Weekly Study Hours",
                    "Student is in the Low study category (less than 5 hrs/wk). Moving to Moderate "
                    "(5&#8211;10 hrs/wk) is consistently associated with better outcomes across all learner segments."))
            else:
                recs.append((icon("check_circle", "#5a8a45"), "Study Commitment On Track",
                    "Study time is well-positioned. Focus on quality of preparation rather than adding more hours."))

            if predicted_score < 69.0:
                recs.append((icon("warning", "#c05840"), "Early Intervention Required",
                    f"Predicted score ({predicted_score:.1f}) is below the Pass threshold (69.0). "
                    "Targeted academic support before the exam is recommended."))

            if learner_seg == "At-Risk":
                recs.append((icon("book_open", "#c05840"), "At-Risk Study Plan",
                    "Revise fundamentals daily, identify and address weak subject areas, and prioritise "
                    "consistent daily practice over long infrequent sessions."))
            elif learner_seg == "Average":
                recs.append((icon("target", "#b07d4e"), "Move Toward High-Performer",
                    "Practice moderate-to-advanced problems and attempt weekly mock tests. "
                    "Completing test preparation is the clearest path to the High-Performer cluster."))

            for ic_svg, title, body in recs:
                st.markdown(recommendation_card(ic_svg, title, body), unsafe_allow_html=True)

            st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
            if st.button("Reset Predictor", key="reset"):
                st.session_state.prediction_run = False
                st.rerun()
