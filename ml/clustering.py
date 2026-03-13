"""
Clustering utility module for player performance prediction
Uses the trained KMeans model to cluster players based on their overall rating
"""

import joblib
import numpy as np
from pathlib import Path

# Get the path to the models
MODEL_DIR = Path(__file__).parent

def load_models():
    """Load the trained KMeans model and scaler"""
    try:
        model_path = MODEL_DIR / "kmeans_model.joblib"
        scaler_path = MODEL_DIR / "scaler.joblib"
        
        kmeans_model = joblib.load(str(model_path))
        scaler = joblib.load(str(scaler_path))
        
        return kmeans_model, scaler
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return None, None


def get_performance_label(overall_rating):
    """
    Determine performance label based on overall rating
    - Top Performer: 81-100
    - Average Performer: 51-80
    - Low Performer: 0-50
    
    Args:
        overall_rating: float, the player's overall rating
    
    Returns:
        str: performance label
    """
    rating = float(overall_rating)
    
    if rating >= 81:
        return "Top Performer"
    elif rating >= 51:
        return "Average Performer"
    else:
        return "Low Performer"


def predict_cluster_and_performance(overall_rating):
    """
    Predict cluster and performance label for a player based on overall rating
    
    Args:
        overall_rating: float, the player's overall rating (0-100)
    
    Returns:
        dict: {
            'cluster': int (0, 1, or 2),
            'performance_label': str
        }
    """
    try:
        rating = float(overall_rating)
        
        # Get performance label based on rating
        performance_label = get_performance_label(rating)
        
        # Assign cluster based on performance label (rating-based)
        if performance_label == "Top Performer":
            cluster = 0
        elif performance_label == "Average Performer":
            cluster = 1
        else:
            cluster = 2
        
        return {
            'cluster': cluster,
            'performance_label': performance_label
        }
    
    except Exception as e:
        print(f"❌ Error in predict_cluster_and_performance: {e}")
        # Default fallback
        performance_label = get_performance_label(overall_rating)
        if performance_label == "Top Performer":
            cluster = 0
        elif performance_label == "Average Performer":
            cluster = 1
        else:
            cluster = 2
        
        return {
            'cluster': cluster,
            'performance_label': performance_label
        }
