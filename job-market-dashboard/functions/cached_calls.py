import streamlit as st
from functions.api_calls import fetch_jobs_from_api, create_historical_salary_dist, create_curr_salary_dist, top_companies, get_job_categories
from functions.db_utils import fetch_jobs_by_search_id

@st.cache_data(ttl=3600)
def get_cached_jobs(app_id, app_key, **kwargs):
    return fetch_jobs_from_api(app_id, app_key, **kwargs)

@st.cache_data(ttl=3600)
def get_cached_historical(app_id, app_key, country, search_id):
    return create_historical_salary_dist(app_id, app_key, country, search_id)

@st.cache_data(ttl=3600)
def get_cached_current_dist(app_id, app_key, country, what, search_id):
    return create_curr_salary_dist(app_id, app_key, country, what, search_id)

@st.cache_data(ttl=3600)
def get_cached_top_companies(app_id, app_key, country, what):
    return top_companies(app_id, app_key, country, what)

@st.cache_data(ttl=3600)
def get_cached_df(search_id):
    return fetch_jobs_by_search_id(search_id)

@st.cache_data(ttl=86400)
def get_cached_job_categories(app_id, app_key):
    return get_job_categories(app_id, app_key)