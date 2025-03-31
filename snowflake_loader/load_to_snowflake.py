# snowflake_loader/load_to_snowflake.py

import pandas as pd
import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

def load_data():
    df = pd.read_csv("tours_scraped.csv")

    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )

    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO SS_INTELLIGUIDE.TOUR_PRODUCTS (
                TOUR_ID, TOUR_NAME, DURATION, URL, BROCHURE_URL, VALIDATED, SUMMARY
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row["TOUR_ID"], row["TOUR_NAME"], row["DURATION"], row["URL"],
            row["BROCHURE_URL"], row["VALIDATED"], row["SUMMARY"]
        ))
    conn.commit()
    cursor.close()
    conn.close()
    print("Data loaded into Snowflake.")

if __name__ == "__main__":
    load_data()
