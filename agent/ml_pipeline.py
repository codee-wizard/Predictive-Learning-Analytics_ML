import joblib
import pandas as pd
import os

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
_BASE = os.path.join(os.path.dirname(__file__), "..", "models")

def _load(name):
    return joblib.load(os.path.join(_BASE, name))

# Lazy-load models once at import time
try:
    reg_model     = _load("linear_model.pkl")
    clf_model     = _load("logistic_model.pkl")
    cluster_model = _load("kmeans_model.pkl")
    scaler_reg    = _load("scaler_reg.pkl")
    scaler_clf    = _load("scaler_clf.pkl")
    scaler_cluster= _load("scaler_cluster.pkl")
    MODELS_LOADED = True
except Exception as e:
    print(f"[ml_pipeline] WARNING – Could not load models: {e}")
    MODELS_LOADED = False


# ─────────────────────────────────────────────
# CLUSTER → CATEGORY MAPPING
# ─────────────────────────────────────────────
CATEGORY_MAP = {0: "At-Risk", 1: "Average", 2: "High-Performer"}


# ─────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────
def run_ml_pipeline(user_data: dict) -> dict:
    """
    Accepts a dict of student features (any subset) and returns:
      { predicted_score, status, category }
    Missing fields are filled with sensible defaults.
    """
    if not MODELS_LOADED:
        return {
            "predicted_score": "N/A",
            "status": "Unknown",
            "category": "Unknown",
        }

    # ── 1. Merge supplied data with defaults ──────────────────────────────────
    data = {
        "MathScore":                user_data.get("math", 67.0),
        "ReadingScore":             user_data.get("reading", 70.0),
        "WklyStudyHours":           user_data.get("study_hours", 7.5),
        "NrSiblings":               user_data.get("siblings", 2.0),
        "ParentEduc":               user_data.get("parent_educ", 2),
        "PracticeSport":            user_data.get("sport", 1),
        "TestPrep_none":            1 if user_data.get("test_prep", "none") == "none" else 0,
        "LunchType_standard":       1 if user_data.get("lunch", "standard") == "standard" else 0,
        "Gender_male":              1 if user_data.get("gender", "female") == "male" else 0,
        "IsFirstChild_yes":         1 if user_data.get("is_first_child", "yes") == "yes" else 0,
        "TransportMeans_school_bus":1 if user_data.get("transport", "school_bus") == "school_bus" else 0,
    }

    # ── 2. Feature vector for regression / classification (11 features) ───────
    feat_cols = [
        "MathScore", "ReadingScore", "WklyStudyHours", "ParentEduc",
        "TestPrep_none", "LunchType_standard", "PracticeSport",
        "NrSiblings", "Gender_male", "IsFirstChild_yes", "TransportMeans_school_bus",
    ]
    X_input = pd.DataFrame([data])[feat_cols]

    # ── 3. Regression ─────────────────────────────────────────────────────────
    X_reg_scaled     = scaler_reg.transform(X_input)
    pred_exam_score  = reg_model.predict(X_reg_scaled)[0]

    # ── 4. Classification ─────────────────────────────────────────────────────
    X_clf_scaled = scaler_clf.transform(X_input)
    pass_fail    = clf_model.predict(X_clf_scaled)[0]

    # ── 5. Clustering (6 features) ────────────────────────────────────────────
    cluster_data = {
        "ExamScore":          pred_exam_score,
        "WklyStudyHours":     data["WklyStudyHours"],
        "ParentEduc":         data["ParentEduc"],
        "LunchType_standard": data["LunchType_standard"],
        "TestPrep_none":      data["TestPrep_none"],
        "PracticeSport":      data["PracticeSport"],
    }
    cluster_cols   = ["ExamScore", "WklyStudyHours", "ParentEduc",
                      "LunchType_standard", "TestPrep_none", "PracticeSport"]
    X_cluster      = pd.DataFrame([cluster_data])[cluster_cols]
    X_cluster_scaled = scaler_cluster.transform(X_cluster)
    cluster_id     = cluster_model.predict(X_cluster_scaled)[0]

    return {
        "predicted_score": round(float(pred_exam_score), 2),
        "status":          str(pass_fail),
        "category":        CATEGORY_MAP.get(int(cluster_id), "Unknown"),
    }