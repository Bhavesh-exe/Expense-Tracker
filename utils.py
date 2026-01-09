# Utils - Constants and helpers for Expense Tracker

CATEGORIES = ["Food", "Transport", "Bills", "Entertainment", "Shopping", "Health", "Other"]

COLORS = {
    "primary": "#00D4AA",
    "secondary": "#FFD700",
    "danger": "#FF4444",
    "warning": "#FFA500",
    "success": "#00D4AA",
    "dark": "#1a1a2e",
    "light": "#2d2d44"
}

SPENDING_PROFILES = {
    "saver": {
        "name": "Smart Saver",
        "description": "You're great at managing money!",
        "color": "#00D4AA",
        "tips": [
            "Keep up the good work!",
            "Consider investing your savings.",
            "Share your budgeting tips with friends!"
        ]
    },
    "balanced": {
        "name": "Balanced Spender",
        "description": "Good balance between spending and saving.",
        "color": "#FFD700",
        "tips": [
            "Try the 50-30-20 rule: 50% needs, 30% wants, 20% savings.",
            "Set a weekly food budget.",
            "Consider 1-2 'no spend' days per week."
        ]
    },
    "moderate_risk": {
        "name": "Moderate Spender",
        "description": "You tend to overspend in some areas.",
        "color": "#FFA500",
        "tips": [
            "Reduce food delivery orders.",
            "Unsubscribe from unused services.",
            "Wait 24 hours before impulse purchases."
        ]
    },
    "high_risk": {
        "name": "Overspender",
        "description": "Your spending habits need attention.",
        "color": "#FF4444",
        "tips": [
            "Create a strict weekly budget.",
            "Switch to mess/home food.",
            "Cancel unnecessary subscriptions.",
            "Use cash instead of UPI.",
            "Track EVERY expense for one month."
        ]
    }
}

SURVEY_QUESTIONS = {
    1: {
        "question": "What is your monthly pocket money/allowance?",
        "options": {
            "A": ("Less than Rs 2,000", 0),
            "B": ("Rs 2,000 - Rs 4,000", 0),
            "C": ("Rs 4,000 - Rs 6,000", 0),
            "D": ("Rs 6,000 - Rs 10,000", 0),
        }
    },
    2: {
        "question": "How often do you order food online (Zomato/Swiggy)?",
        "options": {
            "A": ("Rarely (1-2 times/month)", 0),
            "B": ("Sometimes (1-2 times/week)", 1),
            "C": ("Often (3-5 times/week)", 2),
            "D": ("Daily", 3),
        }
    },
    3: {
        "question": "Where do you usually eat?",
        "options": {
            "A": ("Mostly mess/home food", 0),
            "B": ("Mix of mess and canteen", 1),
            "C": ("Mostly outside restaurants", 2),
            "D": ("Premium restaurants/cafes", 3),
        }
    },
    4: {
        "question": "How often do you go out with friends?",
        "options": {
            "A": ("Rarely (once a month)", 0),
            "B": ("Sometimes (2-3 times/month)", 1),
            "C": ("Often (every weekend)", 2),
            "D": ("Very often (multiple times/week)", 3),
        }
    },
    5: {
        "question": "Do you have paid subscriptions (Netflix, Spotify)?",
        "options": {
            "A": ("No subscriptions", 0),
            "B": ("1-2 subscriptions", 1),
            "C": ("3-4 subscriptions", 2),
            "D": ("5+ subscriptions", 3),
        }
    },
    6: {
        "question": "How often do you shop online (Amazon, Flipkart)?",
        "options": {
            "A": ("Only when necessary", 0),
            "B": ("Once a month", 1),
            "C": ("Multiple times a month", 2),
            "D": ("Weekly or more", 3),
        }
    },
    7: {
        "question": "Do you wait for sales before buying?",
        "options": {
            "A": ("Always wait for sales", 0),
            "B": ("Usually wait", 0),
            "C": ("Sometimes", 1),
            "D": ("Buy whenever I want", 2),
        }
    },
    8: {
        "question": "Do you track your expenses?",
        "options": {
            "A": ("Yes, regularly", 0),
            "B": ("Sometimes", 1),
            "C": ("Rarely", 2),
            "D": ("Never", 3),
        }
    },
    9: {
        "question": "Do you save money each month?",
        "options": {
            "A": ("Yes, 20%+ of budget", 0),
            "B": ("Yes, 10-20%", 0),
            "C": ("Sometimes, when possible", 1),
            "D": ("No, spend everything", 2),
        }
    },
    10: {
        "question": "How often do you run out of money before month-end?",
        "options": {
            "A": ("Never", 0),
            "B": ("Rarely", 1),
            "C": ("Sometimes", 2),
            "D": ("Often", 3),
        }
    }
}


def format_currency(amount: float) -> str:
    return f"Rs {amount:,.0f}"


def get_category_emoji(category: str) -> str:
    emojis = {
        "Food": "",
        "Transport": "",
        "Bills": "",
        "Entertainment": "",
        "Shopping": "",
        "Health": "",
        "Other": ""
    }
    return emojis.get(category, "")


def calculate_spending_profile(risk_score: int, total_questions: int = 10) -> dict:
    max_risk = total_questions * 3
    risk_percentage = (risk_score / max_risk) * 100
    
    if risk_percentage < 15:
        return SPENDING_PROFILES["saver"]
    elif risk_percentage < 35:
        return SPENDING_PROFILES["balanced"]
    elif risk_percentage < 60:
        return SPENDING_PROFILES["moderate_risk"]
    else:
        return SPENDING_PROFILES["high_risk"]
