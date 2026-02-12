import sqlite3
import pandas as pd
import os

# 1. Path Management (Ensures the script finds the DB on your Mac)
base_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_path, 'revenue_intelligence.db')

def run_analysis():
    print("--- 🔍 STARTING REVENUE ANALYSIS ---")
    
    # 2. Safety Check: Does the database exist?
    if not os.path.exists(db_path):
        print(f"❌ Error: Could not find '{db_path}'")
        print("Please run 'setup_db.py' first to create the database.")
        return

    # 3. Connect to the database
    conn = sqlite3.connect(db_path)

    # 4. The "Revenue Intelligence" SQL Query
    # This query identifies high-value customers and their most recent activity
    query = """
    SELECT 
        CUSTOMERNAME,
        COUNT(ORDERNUMBER) AS TOTAL_ORDERS,
        ROUND(SUM(SALES), 2) AS LIFETIME_VALUE,
        MAX(ORDERDATE) AS LAST_ORDER_DATE,
        CITY,
        COUNTRY
    FROM SALES_RECORDS
    GROUP BY CUSTOMERNAME
    ORDER BY LIFETIME_VALUE DESC
    LIMIT 10;
    """

    try:
        print("📊 Querying database for Top 10 High-Value Accounts...")
        
        # 5. Execute and load into Pandas
        df = pd.read_sql_query(query, conn)

        # 6. Display the Results
        print("\n--- 🏆 TOP 10 ACCOUNTS BY REVENUE ---")
        # We display the core metrics a Strategic AM would care about
        print(df[['CUSTOMERNAME', 'TOTAL_ORDERS', 'LIFETIME_VALUE', 'LAST_ORDER_DATE']])
        
        print("\n✅ Analysis complete. These are your 'Tier 1' accounts.")
        
    except Exception as e:
        print(f"❌ An error occurred during analysis: {e}")
    finally:
        conn.close()

    print("--- 🏁 SCRIPT FINISHED ---")

if __name__ == "__main__":
    run_analysis()