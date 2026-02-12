import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
from faker import Faker

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="RevOps Command Center", layout="wide", page_icon="⚡")
fake = Faker()
Faker.seed(42)  # Ensures data looks the same on reload (reproducibility)

# --- 2. THE "ELITE OPERATOR" DATA GENERATOR ---
# Instead of a static DB, we generate a live SaaS portfolio
@st.cache_data
def generate_enterprise_data(rows=150):
    data = []
    industries = ['FinTech', 'Healthcare', 'E-commerce', 'Manufacturing', 'SaaS', 'Logistics']
    tiers = ['Tier 1: Strategic', 'Tier 2: Growth', 'Tier 3: SMB']
    
    current_date = datetime.now()
    
    for _ in range(rows):
        # Weighted logic: Tier 1 deals are larger but rarer
        tier = np.random.choice(tiers, p=[0.15, 0.35, 0.50])
        
        if "Tier 1" in tier:
            arr = np.random.uniform(150000, 1200000) # $150k - $1.2M deals
            employees = np.random.randint(1000, 50000)
        elif "Tier 2" in tier:
            arr = np.random.uniform(50000, 149000)
            employees = np.random.randint(200, 1000)
        else:
            arr = np.random.uniform(10000, 49000)
            employees = np.random.randint(10, 200)

        # Renewal Date Logic (Spread over next 12 months)
        days_to_renewal = np.random.randint(-30, 365)
        renewal_date = current_date + timedelta(days=days_to_renewal)
        
        # Engagement Logic
        last_login_days = np.random.randint(0, 120)
        last_login = current_date - timedelta(days=last_login_days)
        
        # Health Score (0-100) correlated to login activity
        base_health = 100 - (last_login_days * 0.8)
        health_score = max(min(int(base_health + np.random.randint(-10, 10)), 100), 0)

        data.append({
            "Account Name": fake.company(),
            "Industry": np.random.choice(industries),
            "ARR": round(arr, 2),
            "Employees": employees,
            "Tier": tier,
            "Renewal Date": renewal_date,
            "Days Since Last Touch": last_login_days,
            "Health Score": health_score,
            "CSM Owner": fake.first_name()
        })
        
    df = pd.DataFrame(data)
    
    # Business Logic: Categorize Health
    def categorize_risk(score, renewal_days):
        if renewal_days < 90 and score < 60:
            return "🔴 Churn Imminent"
        elif score < 70:
            return "🟡 At Risk"
        else:
            return "🟢 Healthy"

    df['Risk Status'] = df.apply(lambda x: categorize_risk(x['Health Score'], (x['Renewal Date'] - current_date).days), axis=1)
    return df

# --- 3. UI STYLING (Salesforce/Stripe Aesthetic) ---
st.markdown("""
    <style>
    .main { background-color: #F3F4F6; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #E5E7EB;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    h3 { color: #111827; font-family: 'Inter', sans-serif; }
    .stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid #E5E7EB; }
    </style>
    """, unsafe_allow_html=True)

def main():
    # --- HEADER ---
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("⚡ Enterprise Revenue Command Center")
        st.caption(f"Live Portfolio Snapshot | Data Refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    with c2:
        st.button("🔄 Sync Salesforce Data", type="primary", use_container_width=True)

    # --- DATA LOADING ---
    df = generate_enterprise_data(200) # Generating 200 Mock Enterprise Accounts
    
    # --- KPI ROW ---
    total_arr = df['ARR'].sum()
    at_risk_arr = df[df['Risk Status'] != "🟢 Healthy"]['ARR'].sum()
    avg_health = df['Health Score'].mean()
    renewal_q = df[(df['Renewal Date'] > datetime.now()) & (df['Renewal Date'] < datetime.now() + timedelta(days=90))]
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total ARR (Annual Recurring)", f"${total_arr/1_000_000:.2f}M", "YoY +12%")
    k2.metric("Pipeline Risk (ARR)", f"${at_risk_arr/1_000_000:.2f}M", "-4.2%", delta_color="inverse")
    k3.metric("Avg Portfolio Health", f"{int(avg_health)}/100", "Stable")
    k4.metric("Q1 Renewals Due", len(renewal_q), "High Urgency")

    st.markdown("---")

    # --- FILTERS ---
    with st.container():
        f1, f2, f3 = st.columns(3)
        with f1:
            tier_filter = st.multiselect("Account Tier", options=df['Tier'].unique(), default=df['Tier'].unique())
        with f2:
            risk_filter = st.multiselect("Risk Status", options=df['Risk Status'].unique(), default=["🔴 Churn Imminent", "🟡 At Risk"])
        with f3:
            search = st.text_input("Search Account Name", placeholder="e.g. Acme Corp...")

    # Filter Logic
    mask = (df['Tier'].isin(tier_filter)) & (df['Risk Status'].isin(risk_filter))
    if search:
        mask = mask & (df['Account Name'].str.contains(search, case=False))
    
    filtered_df = df[mask]

    # --- MAIN VISUALS ---
    tab1, tab2 = st.tabs(["📉 Retention Analysis", "📊 Territory Overview"])
    
    with tab1:
        c_left, c_right = st.columns([2, 1])
        
        with c_left:
            st.subheader("Health Score vs. ARR (Whale Watch)")
            st.info("💡 **Strategy:** Focus on large bubbles (High ARR) on the left side (Low Health). These are your highest churn risks.")
            
            fig = px.scatter(
                filtered_df, 
                x="Health Score", 
                y="ARR", 
                size="ARR", 
                color="Risk Status",
                hover_name="Account Name",
                color_discrete_map={"🟢 Healthy": "#10B981", "🟡 At Risk": "#F59E0B", "🔴 Churn Imminent": "#EF4444"},
                range_x=[0, 105],
                template="plotly_white",
                height=500
            )
            # Add a vertical line for the "Danger Zone"
            fig.add_vline(x=60, line_width=1, line_dash="dash", line_color="red", annotation_text="Churn Danger Zone")
            st.plotly_chart(fig, use_container_width=True)
            
        with c_right:
            st.subheader("Risk Distribution by Tier")
            risk_chart = px.bar(
                filtered_df, 
                x="Tier", 
                y="ARR", 
                color="Risk Status", 
                title="Revenue at Risk per Tier",
                color_discrete_map={"🟢 Healthy": "#10B981", "🟡 At Risk": "#F59E0B", "🔴 Churn Imminent": "#EF4444"},
                barmode="stack"
            )
            risk_chart.update_layout(showlegend=False)
            st.plotly_chart(risk_chart, use_container_width=True)

    with tab2:
        st.dataframe(filtered_df)

    # --- ACTIONABLE INTELLIGENCE TABLE ---
    st.markdown("### 🚨 High Priority Intervention List")
    
    # We create a "Next Best Action" logic based on data
    action_df = filtered_df[filtered_df['Risk Status'] != "🟢 Healthy"].copy()
    
    def get_action(row):
        if row['ARR'] > 500000 and row['Health Score'] < 50:
            return "🔥 CEO Intervention Required"
        elif row['Days Since Last Touch'] > 60:
            return "📅 Schedule QBR"
        else:
            return "📧 Send Value Report"

    if not action_df.empty:
        action_df['Recommended Playbook'] = action_df.apply(get_action, axis=1)
        
        display_cols = ['Account Name', 'Tier', 'ARR', 'Health Score', 'Days Since Last Touch', 'Recommended Playbook']
        
        st.dataframe(
            action_df[display_cols].sort_values(by='ARR', ascending=False),
            use_container_width=True,
            column_config={
                "ARR": st.column_config.NumberColumn("ARR", format="$%d"),
                "Health Score": st.column_config.ProgressColumn("Health", format="%d", min_value=0, max_value=100)
            }
        )
    else:
        st.success("No accounts currently fit the risk criteria.")

if __name__ == "__main__":
    main()