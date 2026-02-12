import sqlite3
import pandas as pd
import os

# 1. Define File Paths
# We use os.path.join to make sure the Mac finds the file in the current folder
base_path = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(base_path, 'sales_data.csv')
db_file = os.path.join(base_path, 'revenue_intelligence.db')

def init_database():
    print("--- 🏁 Script Started ---")
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} not found!")
        print("Please ensure 'sales_data.csv' is in the SAME folder as this script.")
        return

    print("🚀 Initializing Database...")

    try:
        # 2. Connect to SQLite
        conn = sqlite3.connect(db_file)

        # 3. Load CSV into a Pandas Dataframe
        df = pd.read_csv(csv_file, encoding='latin1')

        # 4. Clean column names
        df.columns = [c.replace(' ', '_').replace('/', '_').upper() for c in df.columns]

        # 5. Push Dataframe to SQL
        df.to_sql('SALES_RECORDS', conn, if_exists='replace', index=False)

        print(f"✅ Success! Database created with {len(df)} rows.")
        
        conn.close()
    except Exception as e:
        print(f"❌ An error occurred: {e}")

    print("--- 🏁 Script Finished ---")

if __name__ == "__main__":
    init_database()