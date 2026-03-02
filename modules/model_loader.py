"""
Model loading utilities for ML models and scalers.
"""

import streamlit as st
import joblib


@st.cache_resource
def load_models():
    """
    Load all ML models and scalers from disk.
    
    Returns:
        dict: Dictionary containing all models and scalers with keys:
            - 'linear_model': Linear regression model
            - 'logistic_model': Logistic regression model
            - 'kmeans_model': K-Means clustering model
            - 'scaler_reg': Scaler for regression
            - 'scaler_clf': Scaler for classification
            - 'scaler_cluster': Scaler for clustering
            
        Returns None values if loading fails.
    """
    try:
        models = {
            'linear_model': joblib.load("models/linear_model.pkl"),
            'logistic_model': joblib.load("models/logistic_model.pkl"),
            'kmeans_model': joblib.load("models/kmeans_model.pkl"),
            'scaler_reg': joblib.load("models/scaler_reg.pkl"),
            'scaler_clf': joblib.load("models/scaler_clf.pkl"),
            'scaler_cluster': joblib.load("models/scaler_cluster.pkl"),
        }
        return models
    except Exception as e:
        st.error(f"Model Load Error: {str(e)}")
        return {
            'linear_model': None,
            'logistic_model': None,
            'kmeans_model': None,
            'scaler_reg': None,
            'scaler_clf': None,
            'scaler_cluster': None,
        }
