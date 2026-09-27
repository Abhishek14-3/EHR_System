def get_recommendations(prediction):
    """
    Return medical recommendations list based on prediction condition.
    """
    # Normalize input
    cond = str(prediction).strip().capitalize()
    
    recommendations_map = {
        "Healthy": [
            "Maintain a balanced diet rich in whole grains, fiber, fruits, and vegetables.",
            "Continue regular physical activity (minimum of 150 minutes of moderate exercise per week).",
            "Ensure 7-9 hours of quality sleep nightly to aid biological recovery.",
            "Schedule annual routine checkups to track overall wellness trends."
        ],
        "Hypertension": [
            "Reduce daily sodium intake to under 1,500 - 2,000 mg.",
            "Follow the DASH (Dietary Approaches to Stop Hypertension) eating plan.",
            "Engage in daily cardiovascular exercise (e.g., brisk walking, jogging, cycling).",
            "Monitor Blood Pressure weekly at home and log all readings.",
            "Consult a cardiologist to evaluate cardiovascular risk and potential medication."
        ],
        "Diabetes": [
            "Monitor blood glucose levels regularly as recommended by your physician.",
            "Limit intake of refined sugars, sweetened beverages, and simple carbohydrates.",
            "Focus on high-fiber, low-glycemic index foods (legumes, leafy greens, non-starchy vegetables).",
            "Participate in daily physical exercise to improve insulin sensitivity.",
            "Schedule regular visits with an endocrinologist and check HbA1c every 3 months."
        ],
        "Arthritis": [
            "Engage in low-impact physical activities (e.g., swimming, water aerobics, cycling, or yoga).",
            "Maintain a healthy weight to minimize joint load and structural stress.",
            "Incorporate anti-inflammatory foods (omega-3 fatty acids, walnuts, olive oil, turmeric).",
            "Utilize warm baths or cold packs to alleviate joint stiffness and pain.",
            "Consult a rheumatologist to develop a comprehensive joint-care strategy."
        ],
        "Asthma": [
            "Identify and avoid environmental triggers (dust, pollen, tobacco smoke, cold air, pet dander).",
            "Ensure a quick-relief rescue inhaler is accessible at all times.",
            "Log peak flow measurements periodically as advised by your pulmonologist.",
            "Practice diaphragmatic breathing exercises to strengthen lung capacity.",
            "Review your Asthma Action Plan annually with a medical specialist."
        ],
        "Obesity": [
            "Adopt a caloric-deficit diet plan focusing on nutrient-dense whole foods and lean proteins.",
            "Gradually increase physical activity, aiming for 150 to 300 minutes of moderate-intensity exercise weekly.",
            "Limit consumption of processed foods, high-calorie snacks, and sugar-sweetened beverages.",
            "Keep a daily food and exercise journal to track habits and identify behavior triggers.",
            "Consult a registered dietitian or healthcare provider for structured weight management."
        ],
        "Cancer": [
            "Schedule an immediate, comprehensive clinical evaluation with an oncologist.",
            "Discuss clinical staging, pathology findings, and personalized treatment options (surgery, chemo, etc.).",
            "Work with an oncology dietitian to maintain nutritional support and weight during treatment.",
            "Seek out support groups or counseling to manage mental well-being and stress.",
            "Avoid exposure to known carcinogens, tobacco, and high alcohol intake."
        ]
    }
    
    # Return matched list, or a default general advisory list
    return recommendations_map.get(cond, [
        "Consult your primary care physician for a complete clinical evaluation.",
        "Maintain a healthy diet consisting of whole foods, vegetables, and lean proteins.",
        "Engage in moderate physical activity at least 3 times per week.",
        "Monitor vital signs and notify a doctor of any sudden changes."
    ])
