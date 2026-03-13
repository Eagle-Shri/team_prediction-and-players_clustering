#!/usr/bin/env python3
"""
Test script to verify rating-based clustering logic
"""

def get_performance_label(overall_rating):
    """
    Determine performance label based on overall rating
    - Top Performer: 81-100
    - Average Performer: 51-80
    - Low Performer: 0-50
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


# Test cases
print("Testing Clustering Logic")
print("=" * 60)

test_cases = [
    (95, "Top Performer", 0),      # High rating - Top Performer
    (85, "Top Performer", 0),      # Mid-high rating - Top Performer
    (81, "Top Performer", 0),      # Boundary - Top Performer
    (80, "Average Performer", 1),  # Just below top - Average
    (65, "Average Performer", 1),  # Mid-range - Average
    (51, "Average Performer", 1),  # Boundary - Average
    (50, "Low Performer", 2),      # Just below average - Low
    (30, "Low Performer", 2),      # Low - Low Performer
    (0, "Low Performer", 2),       # Minimum - Low Performer
]

all_passed = True
for rating, expected_label, expected_cluster in test_cases:
    result = predict_cluster_and_performance(rating)
    actual_label = result['performance_label']
    actual_cluster = result['cluster']
    
    passed = (actual_label == expected_label) and (actual_cluster == expected_cluster)
    status = "✅ PASS" if passed else "❌ FAIL"
    
    print(f"{status} | Rating: {rating:5.1f} | Expected: {expected_label:20s} (Cluster {expected_cluster}) | "
          f"Got: {actual_label:20s} (Cluster {actual_cluster})")
    
    if not passed:
        all_passed = False

print("=" * 60)
if all_passed:
    print("✅ All tests passed!")
else:
    print("❌ Some tests failed!")
