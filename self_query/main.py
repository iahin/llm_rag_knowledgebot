# from pathlib import Path
# import pandas as pd
# import sqlite3
# from langchain_community.utilities import SQLDatabase

# # --- Paths that work regardless of the working directory ---
# BASE_DIR = Path(__file__).resolve().parent
# CSV_PATH = BASE_DIR / "data" / "realistic_restaurant_reviews.csv"
# DB_NAME = "my_database.db"
# DB_DIR = BASE_DIR / DB_NAME

# csv_file = CSV_PATH
# df = pd.read_csv(csv_file)
# conn = sqlite3.connect(DB_DIR)
# table_name = "my_table"

# df.to_sql(table_name, conn, if_exists="replace", index=False)

# db = SQLDatabase.from_uri("sqlite:///"+DB_NAME)

# result = db.run("SELECT * FROM my_table LIMIT 10;")

# print(result)
