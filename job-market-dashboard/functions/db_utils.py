import sqlite3
import pandas as pd

def fetch_jobs_by_search_id(search_id):
    with sqlite3.connect('data/jobs.db') as conn:
        query = "SELECT * FROM jobs WHERE search_id = ?"
        df = pd.read_sql(query, conn, params=[str(search_id)])
        return df
