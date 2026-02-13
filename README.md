# Enterprise Revenue Dashboard (2026)

## Strategic Context
This dashboard is an elite RevOps tool designed to bridge the gap between high-level financial metrics and boots-on-the-ground account strategy. Leveraging SQL-powered analytics and a weighted health-scoring algorithm, it provides Enterprise Account Managers and RevOps leaders with a "single pane of glass" view of portfolio health and churn risk.

## Key Features & Business Logic
* **Weighted Health Scoring Engine:** Calculates account health based on three pillars: Product Engagement (40%), Sentiment/NPS (30%), and Support Volume (30%).
* **Capital at Risk Treemap:** A horizontal, interactive visualization that groups accounts by "Recommended Playbook," allowing leaders to zoom from global strategy down to individual account details.
* **SQL Analytics Layer:** Uses an in-memory SQLite engine to perform real-time aggregations of ARR, growth metrics, and renewal timelines.
* **Risk Composition Analysis:** A 100% stacked bar chart comparing the risk profile (Healthy vs. Critical) across different market industries.

## Strategic Playbooks (The "Why")
The dashboard automatically assigns one of four intervention strategies based on data-driven triggers:
1.  **Executive Sponsor Call (CEO):** High-value accounts ($250k+) with critical health scores.
2.  **Risk Mitigation Plan:** Mid-market accounts with critical health scores requiring immediate CSM intervention.
3.  **Strategy Session / QBR:** Accounts that are "At Risk" or have had zero contact for over 90 days (preventing "silent churn").
4.  **Value Realization Report:** Healthy accounts requiring a low-touch, data-driven touchpoint to reinforce ROI.

## Technical Stack
* **Language:** Python 3.9+
* **Framework:** Streamlit
* **Visualization:** Plotly Express
* **Data Engine:** SQLite & Pandas
* **Synthetics:** Faker (for generating realistic enterprise datasets)

## Deployment
This app is optimized for Streamlit Cloud and includes a `requirements.txt` for seamless dependency management.