# ML Models for Expense Tracker

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from utils import CATEGORIES


TRAINING_DATA = [
    ("chai", "Food"), ("tea", "Food"), ("coffee", "Food"),
    ("breakfast", "Food"), ("lunch", "Food"), ("dinner", "Food"),
    ("samosa", "Food"), ("maggi", "Food"), ("momos", "Food"),
    ("pizza", "Food"), ("burger", "Food"), ("biryani", "Food"),
    ("paratha", "Food"), ("thali", "Food"), ("dosa", "Food"),
    ("pani puri", "Food"), ("golgappa", "Food"), ("chowmein", "Food"),
    ("shawarma", "Food"), ("noodles", "Food"), ("rice", "Food"),
    ("canteen", "Food"), ("mess", "Food"), ("tiffin", "Food"),
    ("zomato", "Food"), ("swiggy", "Food"), ("food delivery", "Food"),
    ("restaurant", "Food"), ("dhaba", "Food"), ("cafe", "Food"),
    ("snacks", "Food"), ("chips", "Food"), ("biscuit", "Food"),
    ("ice cream", "Food"), ("juice", "Food"), ("lassi", "Food"),
    ("cold drink", "Food"), ("coke", "Food"), ("pepsi", "Food"),
    
    ("uber", "Transport"), ("ola", "Transport"), ("cab", "Transport"),
    ("auto", "Transport"), ("rickshaw", "Transport"), ("taxi", "Transport"),
    ("bus", "Transport"), ("metro", "Transport"), ("train", "Transport"),
    ("petrol", "Transport"), ("fuel", "Transport"), ("parking", "Transport"),
    ("rapido", "Transport"), ("bike taxi", "Transport"),
    
    ("recharge", "Bills"), ("mobile", "Bills"), ("phone", "Bills"),
    ("electricity", "Bills"), ("wifi", "Bills"), ("internet", "Bills"),
    ("water bill", "Bills"), ("gas bill", "Bills"),
    
    ("movie", "Entertainment"), ("cinema", "Entertainment"), ("pvr", "Entertainment"),
    ("netflix", "Entertainment"), ("prime", "Entertainment"), ("hotstar", "Entertainment"),
    ("spotify", "Entertainment"), ("gaming", "Entertainment"), ("concert", "Entertainment"),
    ("party", "Entertainment"), ("outing", "Entertainment"), ("trip", "Entertainment"),
    ("fest", "Entertainment"), ("event", "Entertainment"),
    
    ("amazon", "Shopping"), ("flipkart", "Shopping"), ("myntra", "Shopping"),
    ("clothes", "Shopping"), ("shoes", "Shopping"), ("shirt", "Shopping"),
    ("jeans", "Shopping"), ("shopping", "Shopping"), ("gift", "Shopping"),
    ("stationery", "Shopping"), ("notebook", "Shopping"), ("pen", "Shopping"),
    ("headphones", "Shopping"), ("earphones", "Shopping"),
    
    ("medicine", "Health"), ("doctor", "Health"), ("pharmacy", "Health"),
    ("hospital", "Health"), ("clinic", "Health"), ("medical", "Health"),
    ("tablets", "Health"), ("syrup", "Health"),
]


class ExpenseClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=500)
        self.model = LogisticRegression(max_iter=1000)
        self.is_trained = False
    
    def train(self):
        texts = [t[0] for t in TRAINING_DATA]
        labels = [t[1] for t in TRAINING_DATA]
        
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)
        self.is_trained = True
    
    def predict(self, text: str) -> tuple:
        if not self.is_trained:
            self.train()
        
        text = text.lower().strip()
        if not text:
            return "Other", 0.0
        
        try:
            X = self.vectorizer.transform([text])
            proba = self.model.predict_proba(X)[0]
            pred_idx = proba.argmax()
            category = self.model.classes_[pred_idx]
            confidence = proba[pred_idx]
            return category, confidence
        except Exception:
            return "Other", 0.0


class SpendingPredictor:
    def __init__(self):
        self.daily_avg = 0
        self.days_tracked = 0
        self.current_month_total = 0
        self.is_trained = False
    
    def train(self, df):
        if df.empty:
            return False
        
        from datetime import datetime
        current_month = datetime.now().strftime("%Y-%m")
        
        df['Month'] = df['Date'].dt.strftime("%Y-%m")
        current_month_df = df[df['Month'] == current_month]
        
        if current_month_df.empty:
            all_months = df['Month'].unique()
            if len(all_months) > 0:
                last_month = sorted(all_months)[-1]
                current_month_df = df[df['Month'] == last_month]
        
        if current_month_df.empty:
            return False
        
        self.current_month_total = current_month_df['Amount'].sum()
        unique_days = current_month_df['Date'].dt.date.nunique()
        self.days_tracked = unique_days
        self.daily_avg = self.current_month_total / max(unique_days, 1)
        self.is_trained = True
        return True
    
    def predict_next_month(self) -> float:
        if not self.is_trained:
            return 0.0
        return round(self.daily_avg * 30, 0)
    
    def get_trend(self) -> str:
        if not self.is_trained:
            return "unknown"
        
        if self.daily_avg > 150:
            return "High"
        elif self.daily_avg > 80:
            return "Moderate"
        else:
            return "Low"
    
    def get_daily_avg(self) -> float:
        return round(self.daily_avg, 0)


class ClusterAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = None
    
    def analyze(self, daily_features, n_clusters: int = 3) -> dict:
        if len(daily_features) < n_clusters:
            return {'error': 'Not enough data (need at least 3 days)'}
        
        features = daily_features[['Total', 'Food', 'Entertainment', 'IsWeekend']].values
        features_scaled = self.scaler.fit_transform(features)
        
        n_clusters = min(n_clusters, len(features))
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = self.kmeans.fit_predict(features_scaled)
        
        clusters = []
        overall_mean = features[:, 0].mean()
        
        for i in range(n_clusters):
            mask = labels == i
            cluster_data = features[mask]
            
            if len(cluster_data) == 0:
                continue
            
            avg_spending = cluster_data[:, 0].mean()
            
            if avg_spending > overall_mean * 1.3:
                name = "High Spending"
                color = "#FF4444"
            elif avg_spending < overall_mean * 0.7:
                name = "Frugal Days"
                color = "#00D4AA"
            else:
                name = "Normal Days"
                color = "#FFD700"
            
            clusters.append({
                'name': name,
                'color': color,
                'count': int(mask.sum()),
                'avg_spending': round(avg_spending, 0),
                'avg_food': round(cluster_data[:, 1].mean(), 0),
                'weekend_pct': round(cluster_data[:, 3].mean() * 100, 0)
            })
        
        clusters.sort(key=lambda x: x['avg_spending'], reverse=True)
        
        return {
            'clusters': clusters,
            'total_days': len(daily_features),
            'insight': self._generate_insight(clusters)
        }
    
    def _generate_insight(self, clusters: list) -> str:
        high = [c for c in clusters if "High" in c['name']]
        if high and high[0]['weekend_pct'] > 60:
            return f"Most high-spending happens on weekends ({high[0]['weekend_pct']:.0f}%)"
        return "Keep tracking to see your spending patterns!"


class BudgetOptimizer:
    def analyze(self, category_summary, total_budget: float = None) -> dict:
        if category_summary.empty:
            return {'error': 'No expense data'}
        
        total_spent = category_summary['Total'].sum()
        
        if total_budget is None:
            total_budget = total_spent
        
        needs_cats = ['Food', 'Transport', 'Bills', 'Health']
        wants_cats = ['Entertainment', 'Shopping', 'Other']
        
        needs_spent = category_summary[category_summary['Category'].isin(needs_cats)]['Total'].sum()
        wants_spent = category_summary[category_summary['Category'].isin(wants_cats)]['Total'].sum()
        
        needs_ratio = needs_spent / total_spent * 100 if total_spent > 0 else 50
        wants_ratio = wants_spent / total_spent * 100 if total_spent > 0 else 30
        
        recommendations = []
        for _, row in category_summary.iterrows():
            pct = row['Total'] / total_spent * 100 if total_spent > 0 else 0
            
            if pct > 30:
                status = "High"
                color = "#FF4444"
            elif pct > 20:
                status = "Moderate"
                color = "#FFD700"
            else:
                status = "Good"
                color = "#00D4AA"
            
            recommendations.append({
                'category': row['Category'],
                'spent': row['Total'],
                'percent': round(pct, 1),
                'status': status,
                'color': color
            })
        
        return {
            'total_budget': round(total_budget, 0),
            'needs_ratio': round(needs_ratio, 1),
            'wants_ratio': round(wants_ratio, 1),
            'savings_potential': round(total_budget * 0.2, 0),
            'recommendations': recommendations
        }


_classifier = None
_predictor = None
_cluster_analyzer = None
_budget_optimizer = None


def get_classifier() -> ExpenseClassifier:
    global _classifier
    if _classifier is None:
        _classifier = ExpenseClassifier()
        _classifier.train()
    return _classifier


def get_predictor() -> SpendingPredictor:
    global _predictor
    if _predictor is None:
        _predictor = SpendingPredictor()
    return _predictor


def get_cluster_analyzer() -> ClusterAnalyzer:
    global _cluster_analyzer
    if _cluster_analyzer is None:
        _cluster_analyzer = ClusterAnalyzer()
    return _cluster_analyzer


def get_budget_optimizer() -> BudgetOptimizer:
    global _budget_optimizer
    if _budget_optimizer is None:
        _budget_optimizer = BudgetOptimizer()
    return _budget_optimizer
