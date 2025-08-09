
import requests
import uuid
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
from functions.helper import country_dic



def fetch_jobs_from_api(app_id, app_key,category, country='gb', **kwargs):
    job_link = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1?app_id={app_id}&app_key={app_key}"

    optional_params = {
        'results_per_page': kwargs.get('results_per_page'),
        'what': kwargs.get('what'),
        'what_exclude': kwargs.get('what_exclude'),
        'where': kwargs.get('where'),
        'max_days_old': kwargs.get('max_days_old'),
        'salary_min': kwargs.get('salary_min'),
        'salary_max': kwargs.get('salary_max'),
        'part_time': kwargs.get('part_time'),
        'full_time': kwargs.get('full_time'),
        'category': category,
    }
    params = {k: v for k, v in optional_params.items() if v not in [None, '']}

    acc_link = f"{job_link}&" + "&".join(f"{k}={v}" for k, v in params.items())
    try:
        response = requests.get(acc_link, timeout=10)
        response.raise_for_status()
        file = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None
    except ValueError:
        st.error("Invalid response format from API.")
        return None

    search_id = str(uuid.uuid4())
    date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect('data/jobs.db') as conn:
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO searches (search_id, country, what, what_exclude, location, salary_min, salary_max, date_created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (search_id, country, kwargs.get('what'), kwargs.get('what_exclude'), kwargs.get('where'),
             kwargs.get('salary_min'), kwargs.get('salary_max'), date_created))

        if 'results' not in file or not file['results']:
            st.error("No results found for this query.")
            return None

        for result in file['results']:
            id_ = int(result.get('id'))
            company = result.get('company', {}).get('display_name', '')
            title = result.get('title', '')
            location = ", ".join(result.get('location', {}).get('area', []))
            description = result.get('description', '')
            salary_min = int(result.get('salary_min', 0) or 0)
            salary_max = int(result.get('salary_max', 0) or 0)
            contract_type = result.get('contract_type', 'unavailable field')
            contract_time = result.get('contract_time', 'unavailable field')
            created_raw = result.get('created')
            created = datetime.fromisoformat(created_raw.replace('Z', '+00:00')).strftime("%d/%m/%Y") if created_raw else ''
            url = result.get('redirect_url', '')

            cur.execute("""
                INSERT INTO jobs (id, country, company, title, location, description, salary_min, salary_max,
                                  contract_type, contract_time, created, url, search_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET search_id=excluded.search_id;""",
                (id_, country_dic.get(country, country), company, title, location, description,
                 salary_min, salary_max, contract_type, contract_time, created, url, search_id))


        conn.commit()

    return search_id


def get_job_categories(app_id, app_key):
    url = f"http://api.adzuna.com/v1/api/jobs/gb/categories?app_id={app_id}&app_key={app_key}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        if 'results' not in data or not isinstance(data['results'], list):
            st.error("Unexpected API response format.")
            return {}
        return {item['label']: item['tag'] for item in data['results']}
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None
    except ValueError:
        st.error("Invalid response format from API.")
        return None

def get_location_history(app_id, app_key, location0="UK", location1="West Midlands"):
    url = f"http://api.adzuna.com/v1/api/jobs/gb/history?app_id={app_id}&app_key={app_key}&location0={location0}&location1={location1}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        df = pd.DataFrame(res.json()['history'])
        df['date'] = pd.to_datetime(df['date'])
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return pd.DataFrame()
    except ValueError:
        st.error("Invalid response format from API.")
        return pd.DataFrame()
    

def create_historical_salary_dist(app_id, app_key, country, search_id):

    link = f'http://api.adzuna.com/v1/api/jobs/{country}/history?app_id={app_id}&app_key={app_key}&&content-type=application/json'
    
    try:
        res = requests.get(link, timeout=10)
        res.raise_for_status()
        file= res.json()
        data = pd.DataFrame(list(file['month'].items()), columns=['salary', 'counts']) 
        data = pd.DataFrame(list(file['month'].items()), columns=['date', 'salary']) 
        data['date']= pd.to_datetime(data['date'])
        data = data.sort_values(by='date', ascending=False)

        return data
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return pd.DataFrame()
    except ValueError:
        st.error("Invalid response format from API.")
        return pd.DataFrame()


def create_curr_salary_dist(app_id, app_key, country, what ,search_id):

    link = f'http://api.adzuna.com/v1/api/jobs/{country}/histogram?app_id={app_id}&app_key={app_key}&what={what}&content-type=application/json'
    
    try:
        res = requests.get(link, timeout=10)
        res.raise_for_status()
        file= res.json()
        data = pd.DataFrame(list(file['histogram'].items()), columns=['salary', 'counts'])
        return data

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return pd.DataFrame()
    except ValueError:
        st.error("Invalid response format from API.")
        return pd.DataFrame()


def top_companies(app_id, app_key, country, what):

    link= f"http://api.adzuna.com/v1/api/jobs/{country}/top_companies?app_id={app_id}&app_key={app_key}&what={what}&content-type=application/json"

    try:
        res = requests.get(link, timeout=10)
        res.raise_for_status()
        file= res.json()
        data= pd.DataFrame(file['leaderboard'])
        return data

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return pd.DataFrame()
    except ValueError:
        st.error("Invalid response format from API.")
        return pd.DataFrame()

   