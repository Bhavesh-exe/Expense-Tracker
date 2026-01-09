# Data Processing - Data loading and feature engineering

import pandas as pd
import os
from datetime import datetime
from typing import Optional
import json

DATA_DIR = "data"
EXPENSE_FILE = os.path.join(DATA_DIR, "expenses.csv")
GOALS_FILE = os.path.join(DATA_DIR, "savings_goals.json")
SURVEY_FILE = os.path.join(DATA_DIR, "survey_responses.json")


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_expenses() -> pd.DataFrame:
    ensure_data_dir()
    
    if os.path.exists(EXPENSE_FILE):
        try:
            df = pd.read_csv(EXPENSE_FILE)
            df['Date'] = pd.to_datetime(df['Date'])
            return df
        except Exception:
            pass
    
    return pd.DataFrame(columns=['ID', 'Date', 'Amount', 'Category', 'Description'])


def save_expenses(df: pd.DataFrame):
    ensure_data_dir()
    df.to_csv(EXPENSE_FILE, index=False)


def add_expense(amount: float, category: str, description: str, date: Optional[datetime] = None) -> bool:
    try:
        df = load_expenses()
        new_id = 1 if df.empty else df['ID'].max() + 1
        
        if date is None:
            date = datetime.now()
        
        new_row = pd.DataFrame([{
            'ID': new_id,
            'Date': date.strftime('%Y-%m-%d'),
            'Amount': amount,
            'Category': category,
            'Description': description
        }])
        
        df = pd.concat([df, new_row], ignore_index=True)
        save_expenses(df)
        return True
    except Exception:
        return False


def delete_expense(expense_id: int) -> bool:
    try:
        df = load_expenses()
        df = df[df['ID'] != expense_id]
        save_expenses(df)
        return True
    except Exception:
        return False


def get_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    
    df['Month'] = df['Date'].dt.to_period('M')
    summary = df.groupby('Month')['Amount'].sum().reset_index()
    summary.columns = ['Month', 'Total']
    return summary


def get_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    
    summary = df.groupby('Category')['Amount'].agg(['sum', 'count', 'mean']).reset_index()
    summary.columns = ['Category', 'Total', 'Count', 'Average']
    summary = summary.sort_values('Total', ascending=False)
    return summary


def get_daily_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    
    daily = df.groupby(df['Date'].dt.date).agg({
        'Amount': 'sum',
        'ID': 'count'
    }).reset_index()
    
    daily.columns = ['Date', 'Total', 'Transactions']
    daily['Date'] = pd.to_datetime(daily['Date'])
    daily['DayOfWeek'] = daily['Date'].dt.dayofweek
    daily['IsWeekend'] = daily['DayOfWeek'] >= 5
    
    for cat in ['Food', 'Entertainment', 'Shopping']:
        cat_daily = df[df['Category'] == cat].groupby(df['Date'].dt.date)['Amount'].sum()
        daily[cat] = daily['Date'].dt.date.map(cat_daily).fillna(0)
    
    return daily


def prepare_prediction_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    
    monthly = get_monthly_summary(df)
    monthly['MonthNum'] = range(len(monthly))
    monthly['Month_of_year'] = monthly['Month'].dt.month
    return monthly


def load_survey_responses() -> dict:
    ensure_data_dir()
    
    if os.path.exists(SURVEY_FILE):
        try:
            with open(SURVEY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    
    return {'responses': {}, 'risk_score': 0}


def save_survey_responses(data: dict):
    ensure_data_dir()
    with open(SURVEY_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def reset_survey():
    if os.path.exists(SURVEY_FILE):
        os.remove(SURVEY_FILE)


def load_goals() -> list:
    ensure_data_dir()
    
    if os.path.exists(GOALS_FILE):
        try:
            with open(GOALS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    
    return []


def save_goals(goals: list):
    ensure_data_dir()
    with open(GOALS_FILE, 'w') as f:
        json.dump(goals, f, indent=2)


def add_goal(name: str, target: float, days: int = 30) -> dict:
    goals = load_goals()
    
    goal = {
        'id': len(goals) + 1,
        'name': name,
        'target': target,
        'saved': 0,
        'days': days,
        'created': datetime.now().isoformat(),
        'status': 'active'
    }
    
    goals.append(goal)
    save_goals(goals)
    return goal


def update_goal_progress(goal_id: int, amount: float):
    goals = load_goals()
    
    for goal in goals:
        if goal['id'] == goal_id:
            goal['saved'] += amount
            if goal['saved'] >= goal['target']:
                goal['status'] = 'completed'
            break
    
    save_goals(goals)


def delete_goal(goal_id: int):
    goals = load_goals()
    goals = [g for g in goals if g['id'] != goal_id]
    save_goals(goals)
