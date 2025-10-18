import random

HEALTH_TIPS = [
    {"category": "HYDRATION", "text": "Drink a glass of water before meals to help manage appetite."},
    {"category": "NUTRITION", "text": "Aim for a colorful plate—variety boosts micronutrient intake."},
    {"category": "PROTEIN", "text": "Include a protein source at each meal to support satiety and muscle repair."},
    {"category": "FIBER", "text": "Add leafy greens or legumes for extra fiber to support digestion."},
    {"category": "MOVEMENT", "text": "A 10-minute walk after meals can help stabilize blood sugar."},
    {"category": "SLEEP", "text": "Avoid heavy meals 2–3 hours before bedtime for better sleep quality."},
    {"category": "MINDFUL", "text": "Eat slowly and without distractions—notice taste, texture, and fullness."},
    {"category": "HEART", "text": "Swap saturated fats for olive oil or avocado to support heart health."},
    {"category": "OMEGA-3", "text": "Include fatty fish like salmon 1–2x per week for omega-3s."},
    {"category": "STRESS", "text": "Take 5 deep breaths before eating to engage rest-and-digest."},
    {"category": "MICROS", "text": "Rotate ingredients weekly to broaden vitamin and mineral coverage."},
    {"category": "SODIUM", "text": "Flavor with herbs/spices instead of salt to reduce sodium intake."},
    {"category": "SUGAR", "text": "Pair sweets with protein or fat to blunt blood sugar spikes."},
]


def get_random_tip():
    return random.choice(HEALTH_TIPS)


