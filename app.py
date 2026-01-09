"""
Expense Tracker - Streamlit Web App
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils import CATEGORIES, SURVEY_QUESTIONS, format_currency, calculate_spending_profile
from data_processing import (
    load_expenses, add_expense, delete_expense,
    get_monthly_summary, get_category_summary, get_daily_features,
    load_survey_responses, save_survey_responses, reset_survey,
    load_goals, add_goal, update_goal_progress, delete_goal
)
from model import get_classifier, get_predictor, get_cluster_analyzer, get_budget_optimizer


st.set_page_config(
    page_title="TrackIt - Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .metric-card { background-color: #1a1a2e; border-radius: 10px; padding: 20px; margin: 10px 0; }
    .success-text { color: #00D4AA; }
    .warning-text { color: #FFD700; }
    .danger-text { color: #FF4444; }
</style>
""", unsafe_allow_html=True)


st.sidebar.title("TrackIt")
st.sidebar.markdown("---")

nav_options = ["Add Expense", "View Expenses", "Analysis", "Budget", "Survey", "AI Tools"]

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Add Expense"

for option in nav_options:
    if st.sidebar.button(option, key=f"nav_{option}", use_container_width=True):
        st.session_state.current_page = option
        st.rerun()

page = st.session_state.current_page


if page == "Add Expense":
    st.title("Add New Expense")
    
    description = st.text_input("Description", placeholder="e.g., chai, uber, netflix...")
    
    suggested_category = "Food"
    confidence = 0.0
    
    if description:
        classifier = get_classifier()
        suggested_category, confidence = classifier.predict(description)
        
        if confidence > 0.4:
            st.success(f"Suggested: **{suggested_category}** ({confidence*100:.0f}% confident)")
        else:
            st.warning(f"Maybe: **{suggested_category}** ({confidence*100:.0f}% confident)")
    
    category = st.selectbox(
        "Category",
        CATEGORIES,
        index=CATEGORIES.index(suggested_category) if suggested_category in CATEGORIES else 0
    )
    
    amount = st.number_input("Amount (Rs)", min_value=1, max_value=100000, value=50)
    date = st.date_input("Date", value=datetime.now())
    
    if st.button("Add Expense", type="primary", use_container_width=True):
        if amount > 0:
            success = add_expense(amount, category, description, datetime.combine(date, datetime.min.time()))
            if success:
                st.success(f"Added: Rs {amount} for {category}")
                st.balloons()
            else:
                st.error("Failed to add expense")
        else:
            st.error("Please enter a valid amount")


elif page == "View Expenses":
    st.title("Your Expenses")
    
    df = load_expenses()
    
    if df.empty:
        st.info("No expenses yet. Add your first expense!")
    else:
        col1, col2 = st.columns(2)
        with col1:
            filter_category = st.multiselect("Filter by Category", CATEGORIES)
        with col2:
            date_range = st.date_input(
                "Date Range",
                value=(df['Date'].min(), df['Date'].max()),
                key="date_filter"
            )
        
        filtered_df = df.copy()
        if filter_category:
            filtered_df = filtered_df[filtered_df['Category'].isin(filter_category)]
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['Date'] >= pd.to_datetime(date_range[0])) &
                (filtered_df['Date'] <= pd.to_datetime(date_range[1]))
            ]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Spent", format_currency(filtered_df['Amount'].sum()))
        with col2:
            st.metric("Transactions", len(filtered_df))
        with col3:
            st.metric("Avg per Transaction", format_currency(filtered_df['Amount'].mean()) if not filtered_df.empty else "Rs 0")
        
        st.markdown("### All Expenses")
        
        display_df = filtered_df[['Date', 'Amount', 'Category', 'Description']].copy()
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        display_df['Amount'] = display_df['Amount'].apply(lambda x: f"Rs {x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)


elif page == "Analysis":
    st.title("Spending Analysis")
    
    df = load_expenses()
    
    if df.empty:
        st.info("Add some expenses to see analysis!")
    else:
        st.markdown("### Category Breakdown")
        category_summary = get_category_summary(df)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            chart_data = category_summary.set_index('Category')['Total']
            st.bar_chart(chart_data)
        
        with col2:
            for _, row in category_summary.iterrows():
                st.markdown(f"**{row['Category']}**: Rs {row['Total']:,.0f} ({row['Count']} txn)")
        
        st.markdown("---")
        
        st.markdown("### Monthly Trend")
        monthly = get_monthly_summary(df)
        
        if not monthly.empty:
            monthly['Month_str'] = monthly['Month'].astype(str)
            chart_data = monthly.set_index('Month_str')['Total']
            st.line_chart(chart_data)
            
            st.markdown("### Next Month Prediction")
            
            predictor = get_predictor()
            
            if predictor.train(df):
                prediction = predictor.predict_next_month()
                daily_avg = predictor.get_daily_avg()
                trend = predictor.get_trend()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Daily Average", format_currency(daily_avg))
                with col2:
                    st.metric("Next Month (30 days)", format_currency(prediction))
                with col3:
                    st.metric("Spending Level", trend)
                
                st.caption(f"Based on {predictor.days_tracked} days of tracking this month")
            else:
                st.info("Add more expenses to see prediction")


elif page == "Budget":
    st.title("Budget Management")
    
    df = load_expenses()
    
    if df.empty:
        st.info("Add expenses to get budget insights")
    else:
        st.markdown("### Set Monthly Budget")
        
        col1, col2 = st.columns(2)
        with col1:
            monthly_budget = st.number_input("Your Monthly Budget (Rs)", min_value=1000, value=3000, step=500)
        with col2:
            current_month = datetime.now().strftime("%Y-%m")
            st.text_input("Current Month", value=current_month, disabled=True)
        
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        current_spending = df[df['Month'] == current_month]['Amount'].sum()
        
        st.markdown("### Budget Status")
        
        remaining = monthly_budget - current_spending
        progress = min(current_spending / monthly_budget, 1.0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Spent This Month", format_currency(current_spending))
        with col2:
            st.metric("Remaining", format_currency(max(remaining, 0)))
        with col3:
            st.metric("Budget Used", f"{progress * 100:.0f}%")
        
        st.progress(progress)
        
        if remaining < 0:
            st.error(f"Over budget by Rs {abs(remaining):,.0f}!")
        elif remaining < monthly_budget * 0.2:
            st.warning("Low budget remaining. Consider reducing spending.")
        else:
            st.success("You're on track with your budget!")
        
        st.markdown("### Category-wise Spending")
        category_summary = get_category_summary(df[df['Month'] == current_month])
        
        for _, row in category_summary.iterrows():
            pct = (row['Total'] / monthly_budget * 100) if monthly_budget > 0 else 0
            st.markdown(f"**{row['Category']}**: Rs {row['Total']:,.0f} ({pct:.1f}% of budget)")


elif page == "Survey":
    st.title("Spending Habits Survey")
    st.caption("Answer 10 questions to get personalized savings advice")
    
    survey_data = load_survey_responses()
    
    if len(survey_data.get('responses', {})) >= 10:
        st.markdown("### Your Results")
        
        profile = calculate_spending_profile(survey_data.get('risk_score', 0))
        
        st.markdown(f"""
        <div style="background-color: #1a1a2e; padding: 20px; border-radius: 10px; text-align: center;">
            <h2 style="color: {profile['color']};">{profile['name']}</h2>
            <p>{profile['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Tips for You")
        for tip in profile['tips']:
            st.markdown(f"- {tip}")
        
        if st.button("Retake Survey"):
            reset_survey()
            st.rerun()
    
    else:
        current_q = len(survey_data.get('responses', {})) + 1
        
        if current_q <= 10:
            st.progress(current_q / 10, text=f"Question {current_q} of 10")
            
            q_data = SURVEY_QUESTIONS[current_q]
            st.markdown(f"### {q_data['question']}")
            
            for key, (text, risk) in q_data['options'].items():
                if st.button(f"{key}. {text}", use_container_width=True, key=f"q{current_q}_{key}"):
                    survey_data['responses'][str(current_q)] = key
                    survey_data['risk_score'] = survey_data.get('risk_score', 0) + risk
                    save_survey_responses(survey_data)
                    st.rerun()
        
        if st.button("Reset Survey"):
            reset_survey()
            st.rerun()


elif page == "AI Tools":
    st.title("AI Tools")
    
    df = load_expenses()
    
    if 'ai_tab' not in st.session_state:
        st.session_state.ai_tab = "Spending Patterns"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Spending Patterns", use_container_width=True, 
                     type="primary" if st.session_state.ai_tab == "Spending Patterns" else "secondary"):
            st.session_state.ai_tab = "Spending Patterns"
            st.rerun()
    with col2:
        if st.button("Budget Tips", use_container_width=True,
                     type="primary" if st.session_state.ai_tab == "Budget Tips" else "secondary"):
            st.session_state.ai_tab = "Budget Tips"
            st.rerun()
    with col3:
        if st.button("Savings Goals", use_container_width=True,
                     type="primary" if st.session_state.ai_tab == "Savings Goals" else "secondary"):
            st.session_state.ai_tab = "Savings Goals"
            st.rerun()
    
    st.markdown("---")
    
    ai_tab = st.session_state.ai_tab
    
    if ai_tab == "Spending Patterns":
        st.markdown("### K-Means Clustering Analysis")
        
        if df.empty:
            st.info("Add expenses to see spending patterns")
        else:
            daily = get_daily_features(df)
            
            if len(daily) < 3:
                st.warning("Need at least 3 days of data for clustering")
            else:
                analyzer = get_cluster_analyzer()
                result = analyzer.analyze(daily)
                
                if 'error' in result:
                    st.warning(result['error'])
                else:
                    st.caption(f"Analyzed {result['total_days']} days of spending")
                    
                    for cluster in result['clusters']:
                        st.markdown(f"""
                        <div style="background-color: #1a1a2e; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid {cluster['color']};">
                            <h4 style="color: {cluster['color']}; margin: 0;">{cluster['name']}</h4>
                            <p style="margin: 5px 0;">
                                {cluster['count']} days - Avg: Rs {cluster['avg_spending']}/day<br>
                                Food: Rs {cluster['avg_food']} - Weekend: {cluster['weekend_pct']}%
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.info(result['insight'])
    
    elif ai_tab == "Budget Tips":
        st.markdown("### 50-30-20 Budget Analysis")
        
        if df.empty:
            st.info("Add expenses to get budget recommendations")
        else:
            category_summary = get_category_summary(df)
            optimizer = get_budget_optimizer()
            result = optimizer.analyze(category_summary)
            
            if 'error' in result:
                st.warning(result['error'])
            else:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Needs", f"{result['needs_ratio']}%", delta="Target: 50%")
                with col2:
                    st.metric("Wants", f"{result['wants_ratio']}%", delta="Target: 30%")
                with col3:
                    st.metric("Potential Savings", format_currency(result['savings_potential']))
                
                st.markdown("### Category Analysis")
                for rec in result['recommendations']:
                    st.markdown(f"**{rec['category']}** - {rec['status']}: Rs {rec['spent']:,.0f} ({rec['percent']}% of total)")
    
    elif ai_tab == "Savings Goals":
        st.markdown("### Your Savings Goals")
        
        with st.expander("Add New Goal"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_name = st.text_input("Goal Name", placeholder="e.g., New Headphones")
            with col2:
                new_target = st.number_input("Target Amount (Rs)", min_value=100, value=1000)
            with col3:
                new_days = st.number_input("Days to achieve", min_value=7, value=30)
            
            if st.button("Add Goal"):
                if new_name:
                    add_goal(new_name, new_target, new_days)
                    st.success(f"Goal '{new_name}' added!")
                    st.rerun()
        
        goals = load_goals()
        
        if not goals:
            st.info("No savings goals yet. Add one above!")
        else:
            for goal in goals:
                progress = (goal['saved'] / goal['target'] * 100) if goal['target'] > 0 else 0
                remaining = goal['target'] - goal['saved']
                
                try:
                    created = datetime.fromisoformat(goal['created'])
                    deadline = created + timedelta(days=goal['days'])
                    days_left = (deadline - datetime.now()).days
                except:
                    days_left = goal['days']
                
                daily_needed = remaining / max(days_left, 1)
                
                st.markdown(f"""
                <div style="background-color: #1a1a2e; padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <h4>{goal['name']}</h4>
                    <p>Rs {goal['saved']:,.0f} / Rs {goal['target']:,.0f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.progress(min(progress / 100, 1.0))
                st.caption(f"{days_left} days left - Need Rs {daily_needed:,.0f}/day")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"+Rs 100", key=f"add100_{goal['id']}"):
                        update_goal_progress(goal['id'], 100)
                        st.rerun()
                with col2:
                    if st.button(f"+Rs 500", key=f"add500_{goal['id']}"):
                        update_goal_progress(goal['id'], 500)
                        st.rerun()
                with col3:
                    if st.button("Delete", key=f"del_{goal['id']}"):
                        delete_goal(goal['id'])
                        st.rerun()
                
                st.markdown("---")
