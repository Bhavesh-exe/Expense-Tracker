# TrackIt - ML-Powered Expense Tracker

A personal finance web app built with **Streamlit** and **Machine Learning** for students to track expenses, predict spending, and save money.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange)

[Live Demo](https://expense-tracker-ml.streamlit.app/)

## Features

### Smart Expense Tracking
- Add expenses with **auto-categorization** using ML
- View and filter expense history
- Category-wise breakdown

### AI-Powered Analysis
- **Spending Prediction** based on daily average
- **K-Means Clustering** to identify spending patterns
- **50-30-20 Budget Recommendations**

### Spending Habits Survey
- 10-question quiz to analyze your habits
- Personalized spending profile
- Tailored savings tips

### Savings Goals
- Set and track savings goals
- Progress visualization
- Daily savings calculator

## Quick Start

```bash
# Clone the repo
git clone https://github.com/bhavesh-exe/expense-tracker.git
cd expense-tracker

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Project Structure

```
expense-tracker/
├── app.py                 # Streamlit UI
├── model.py               # ML models (Classifier, Predictor, Clustering)
├── data_processing.py     # Data loading & feature engineering
├── utils.py               # Constants & helpers
├── requirements.txt       # Dependencies
└── data/
    ├── expenses.csv       # Expense data
    └── savings_goals.json # User goals
```

## ML Models

| Model | Algorithm | Purpose |
|-------|-----------|---------|
| Expense Classifier | TF-IDF + Logistic Regression | Auto-categorize expenses |
| Spending Predictor | Daily Average Extrapolation | Predict next month's spending |
| Pattern Analyzer | K-Means Clustering | Identify spending patterns |
| Budget Optimizer | 50-30-20 Rule | Recommend budget allocation |

## Tech Stack

- **Frontend**: Streamlit
- **ML**: scikit-learn
- **Data**: pandas, numpy
