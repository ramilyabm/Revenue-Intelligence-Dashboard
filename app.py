import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import sqlite3
from datetime import datetime, timedelta
from faker import Faker

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="RevOps Command Center", layout="wide")
fake = Faker()
Faker.seed(42)

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    
    div[data-testid="stMetric"], div[data-testid="metric-container"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        padding: 15px 25px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s ease;
    }
    
    span[data-baseweb="tag"] {
        background-color: #E2E8F0 !important;
        color: #1E293B !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA GENERATOR ---
@st.cache_data
def generate_enterprise_data(rows=200):
    data = []
    industries = ['FinTech', 'Healthcare', 'E-commerce', 'Manufacturing', 'SaaS', 'Logistics']
    tiers = ['Tier 1: Strategic', 'Tier 2: Growth', 'Tier 3: SMB']
    
    current_date = datetime.now()
    
    for _ in range(rows):
        tier = np.random.choice(tiers, p=[0.15, 0.35, 0.50])
        
        if "Tier 1" in tier:
            arr = np.random.uniform(200000, 1500000)
            employees = np.random.randint(1000, 50000)
        elif "Tier 2" in tier:
            arr = np.random.uniform(50000, 199000)
            employees = np.random.randint(200, 1000)
        else:
            arr = np.random.uniform(10000, 49000)
            employees = np.random.randint(10, 200)

        growth_rate = np.random.uniform(-0.10, 0.30)
        previous_arr = arr / (1 + growth_rate)

        last_login_days = np.random.randint(0, 150)
        nps_score = np.random.randint(0, 11)
        open_tickets = np.random.randint(0, 15)
        
        score_engagement = max(100 - (last_login_days * 0.5), 0)
        score_nps = nps_score * 10 
        score_support = max(100 - (open_tickets * 5), 0)
        health_score = int((score_engagement * 0.4) + (score_nps * 0.3) + (score_support * 0.3))
        
        days_to_renewal = np.random.randint(-15, 365)
        renewal_date = current_date + timedelta(days=days_to_renewal)

        risk_status = "Healthy"
        if days_to_renewal < 90 and health_score < 50:
            risk_status = "Critical"
        elif health_score < 70:
            risk_status = "At Risk"

        data.append({
            "Account_Name": fake.company(),
            "Industry": np.random.choice(industries),
            "ARR": round(arr, 2),
            "Previous_ARR": round(previous_arr, 2),
            "Tier": tier,
            "Renewal_Date": renewal_date,
            "Days_Since_Last_Touch": last_login_days,
            "Health_Score": health_score,
            "NPS": nps_score,
            "Open_Tickets": open_tickets,
            "Risk_Status": risk_status
        })
        
    return pd.DataFrame(data)

# --- 3. SQL ENGINE ---
def run_sql_analysis(df):
    conn = sqlite3.connect(':memory:')
    df.to_sql('portfolio', conn, index=False, if_exists='replace')
    
    kpi_query = """
    SELECT 
        SUM(ARR) as Total_ARR,
        SUM(Previous_ARR) as Total_Prev_ARR,
        SUM(CASE WHEN Risk_Status = 'Critical' THEN ARR ELSE 0 END) as Critical_Risk_ARR,
        AVG(Health_Score) as Avg_Health,
        COUNT(CASE WHEN Renewal_Date BETWEEN datetime('now') AND datetime('now', '+90 days') THEN 1 END) as Q1_Renewals
    FROM portfolio
    """
    kpis = pd.read_sql_query(kpi_query, conn)
    conn.close()
    return kpis

# --- 4. MAIN APP ---
def main():
    # HEADER
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("Enterprise Revenue Dashboard")
        st.caption(f"Live SQL Analytics | Data Refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    with c2:
        st.write("")
        if st.button("Sync Warehouse", use_container_width=True):
             st.cache_data.clear()
             st.rerun()

    # DATA
    df = generate_enterprise_data(200)
    kpi_data = run_sql_analysis(df)
    
    total_arr = kpi_data['Total_ARR'][0]
    critical_risk = kpi_data['Critical_Risk_ARR'][0]
    avg_health = kpi_data['Avg_Health'][0]
    renewals_due = kpi_data['Q1_Renewals'][0]

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        with st.container(border=True):
            st.metric("Total ARR", f"${total_arr/1_000_000:.2f}M", "YoY +12%")
    with k2:
        with st.container(border=True):
            st.metric("Critical Risk", f"${critical_risk/1_000_000:.2f}M", "Requires Action", delta_color="inverse")
    with k3:
        with st.container(border=True):
            st.metric("Avg Health", f"{int(avg_health)}/100", "Weighted Score")
    with k4:
        with st.container(border=True):
            st.metric("Q1 Renewals", int(renewals_due), "Urgent")

    # FILTERS
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader("Portfolio Controls")
        f1, f2, f3 = st.columns(3)
        with f1:
            tier_filter = st.multiselect("Filter by Tier", options=df['Tier'].unique(), default=df['Tier'].unique())
        with f2:
            risk_filter = st.multiselect("Filter by Risk Status", options=df['Risk_Status'].unique(), default=["Critical", "At Risk"])
        with f3:
            search = st.text_input("Find Specific Account", placeholder="e.g. Acme Corp...")

    mask = (df['Tier'].isin(tier_filter)) & (df['Risk_Status'].isin(risk_filter))
    if search:
        mask = mask & (df['Account_Name'].str.contains(search, case=False))
    filtered_df = df[mask]

    # VISUALS
    tab1, tab2 = st.tabs(["Retention Analysis", "Territory Overview"])
    
    with tab1:
        with st.container(border=True):
            st.markdown("#### Risk Detection Engine")
            c_left, c_right = st.columns([2, 1])
            with c_left:
                fig = px.scatter(
                    filtered_df, x="Health_Score", y="ARR", size="ARR", color="Risk_Status",
                    hover_name="Account_Name",
                    custom_data=["Tier", "NPS", "Risk_Status"], 
                    color_discrete_map={"Healthy": "#10B981", "At Risk": "#F59E0B", "Critical": "#EF4444"},
                    range_x=[0, 105], template="plotly_white", height=500
                )
                fig.update_traces(
                    marker=dict(line=dict(width=1, color='white')),
                    hovertemplate=(
                        "<b>%{hovertext}</b><br>" + 
                        "<span style='color:gray'>%{customdata[0]}</span><br><br>" + 
                        "<b>ARR:</b> %{y:$,.0f}<br>" +
                        "<b>Health:</b> %{x}%<br>" +
                        "<b>NPS:</b> %{customdata[1]}/10<br>" +
                        "<extra></extra>"
                    )
                )
                fig.update_layout(
                    hoverlabel=dict(bgcolor="white", font_size=14, font_family="Inter, sans-serif", bordercolor="#e2e8f0"),
                    xaxis_title="Health Score (Engagement + NPS)",
                    yaxis_title="Annual Recurring Revenue (ARR)",
                    legend_title_text=None
                )
                fig.add_vline(x=50, line_width=1, line_dash="dash", line_color="#EF4444", annotation_text="Critical Threshold")
                st.plotly_chart(fig, use_container_width=True)
                
            with c_right:
                risk_chart = px.bar(
                    filtered_df, x="Tier", y="ARR", color="Risk_Status", 
                    color_discrete_map={"Healthy": "#10B981", "At Risk": "#F59E0B", "Critical": "#EF4444"},
                )
                risk_chart.update_layout(showlegend=False, xaxis_title=None)
                st.plotly_chart(risk_chart, use_container_width=True)

    with tab2:
        with st.container(border=True):
            st.markdown("#### Market Segment Performance")
            t_left, t_right = st.columns([1, 1])
            with t_left:
                st.caption("Revenue Concentration by Industry")
                industry_stats = filtered_df.groupby("Industry").agg({
                    "ARR": "sum", "Account_Name": "count", "Health_Score": "mean"
                }).reset_index()
                
                fig_bar = px.bar(
                    industry_stats, x="Industry", y="ARR", text_auto='.2s',
                    color="ARR", color_continuous_scale="Tealgrn", 
                    custom_data=["Account_Name", "Health_Score"] 
                )
                fig_bar.update_traces(
                    marker_line_color='white', marker_line_width=1,
                    hovertemplate=(
                        "<b>%{x}</b><br>" +
                        "<span style='color:gray'>Market Segment</span><br><br>" +
                        "<b>Total ARR:</b> %{y:$,.0f}<br>" +
                        "<b>Accounts:</b> %{customdata[0]}<br>" +
                        "<b>Avg Health:</b> %{customdata[1]:.0f}/100<extra></extra>"
                    )
                )
                fig_bar.update_layout(
                    hoverlabel=dict(bgcolor="white", font_size=14, font_family="Inter", bordercolor="#e2e8f0"),
                    coloraxis_showscale=False, xaxis_title=None, yaxis_title=None, plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
            with t_right:
                st.caption("Risk Distribution by Industry")
                
                # 1. Prepare Data: Count accounts per Industry & Risk Status
                risk_distribution = filtered_df.groupby(["Industry", "Risk_Status"]).size().reset_index(name='Account_Count')
                
                # 2. Stacked Bar Chart
                fig_risk = px.bar(
                    risk_distribution, 
                    x="Industry", 
                    y="Account_Count", 
                    color="Risk_Status",
                    # Stack them to show composition (100% view)
                    barmode="stack",
                    color_discrete_map={"Healthy": "#10B981", "At Risk": "#F59E0B", "Critical": "#EF4444"},
                )
                
                # 3. Clean UI & Tooltip
                fig_risk.update_traces(
                    marker_line_color='white', 
                    marker_line_width=1,
                    hovertemplate=(
                        "<b>%{x}</b><br>" + # Industry
                        "Status: <b>%{fullData.name}</b><br>" + # The Color Group Name
                        "Count: <b>%{y} Accounts</b><extra></extra>"
                    )
                )
                
                fig_risk.update_layout(
                    hoverlabel=dict(bgcolor="white", font_size=14, font_family="Inter", bordercolor="#e2e8f0"),
                    xaxis_title=None,
                    yaxis_title="Number of Accounts",
                    legend_title_text=None,
                    plot_bgcolor="rgba(0,0,0,0)",
                    # Move legend to the top for cleaner look
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig_risk, use_container_width=True)

    # --- STRATEGIC INTERVENTION PLAN (HORIZONTAL TREEMAP + RATIONALE) ---
    st.markdown("### Strategic Intervention Plan")
    st.info("Prioritized list of accounts requiring immediate executive or strategic action.")
    
    # Logic: Critical/At Risk OR Healthy but Ignored (>90 Days)
    action_df = filtered_df[
        (filtered_df['Risk_Status'] != "Healthy") | 
        (filtered_df['Days_Since_Last_Touch'] > 90)
    ].copy()
    
    # Definition 1: The Playbook
    def get_strategic_playbook(row):
        if row['Risk_Status'] == 'Critical' and row['ARR'] > 250000:
            return "1. Executive Sponsor Call (CEO)"
        elif row['Risk_Status'] == 'Critical':
            return "2. Risk Mitigation Plan"
        elif row['Risk_Status'] == 'At Risk':
             return "3. Strategy Session / QBR"
        else:
            return "4. Value Realization Report"

    # Definition 2: The Rationale (THE WHY)
    def get_rationale(row):
        if row['Risk_Status'] == 'Critical' and row['ARR'] > 250000:
            return f"High Value (${row['ARR']/1000:.0f}k) + Critical Health"
        elif row['Risk_Status'] == 'Critical':
            return "Health Score Critical (<50)"
        elif row['Risk_Status'] == 'At Risk':
             return "Health Score Warning (<70)"
        else:
            return f"Drifting: No Contact for {row['Days_Since_Last_Touch']} Days"

    if not action_df.empty:
        action_df['Recommended_Playbook'] = action_df.apply(get_strategic_playbook, axis=1)
        action_df['Rationale'] = action_df.apply(get_rationale, axis=1) # Apply the Rationale
        
        # 1. Full Width Treemap
        st.markdown("#### Capital at Risk Map (Click to Zoom)")
        fig_tree = px.treemap(
            action_df, 
            path=['Recommended_Playbook', 'Risk_Status', 'Account_Name'], 
            values='ARR',
            color='Risk_Status',
            color_discrete_map={"Healthy": "#10B981", "At Risk": "#F59E0B", "Critical": "#EF4444"},
        )
        fig_tree.update_traces(
            root_color="#F1F5F9",
            textinfo="label+value+percent parent",
            hovertemplate="<b>%{label}</b><br>Value: %{value:$,.0f}<extra></extra>"
        )
        fig_tree.update_layout(
            margin=dict(t=0, l=0, r=0, b=0), 
            hoverlabel=dict(bgcolor="white", font_size=14, font_family="Inter")
        )
        st.plotly_chart(fig_tree, use_container_width=True)

        # 2. Action Queue Below
        st.markdown("#### Action Queue")
        display_df = action_df.sort_values(by=['Recommended_Playbook', 'ARR'], ascending=[True, False])
        
        st.dataframe(
            display_df[['Account_Name', 'ARR', 'Risk_Status', 'Recommended_Playbook', 'Rationale']], 
            use_container_width=True, 
            hide_index=True, 
            height=400,
            column_config={
                "ARR": st.column_config.NumberColumn("Revenue", format="$%d"),
                "Recommended_Playbook": st.column_config.TextColumn("Action Required", width="medium"),
                "Risk_Status": st.column_config.TextColumn("Status"),
                "Rationale": st.column_config.TextColumn("Logic / Reason", width="large"),
            }
        )
    else:
        st.success("Great job! No accounts currently require intervention.")

if __name__ == "__main__":
    main()