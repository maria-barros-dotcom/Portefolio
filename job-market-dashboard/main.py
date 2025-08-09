import requests
import sqlite3
import json
import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from datetime import date
from datetime import timedelta
import altair as alt
import plotly.express as px
from urllib.parse import urlencode
from wordcloud import WordCloud
from nltk.corpus import stopwords
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
#from functions import country_dic, category_dict, fetch_jobs_from_api, create_curr_salary_dist, create_historical_salary_dist, clean_text
from functions.helper import country_dic, clean_df, clean_text, color_theme_list, color_map
from functions.cached_calls import (
    get_cached_jobs,
    get_cached_historical,
    get_cached_current_dist,
    get_cached_top_companies,
    get_cached_df,
    get_cached_job_categories
)
from config.id_vals import APP_ID, APP_KEY

app_id, app_key= APP_ID, APP_KEY

#available categories
category_dict= get_cached_job_categories(app_id, app_key)

st.set_page_config(
    page_title="Job Market Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded")

alt.theme.enable("dark")

with st.sidebar:
    with st.form(key="job_search_form"):
        st.title('💼 Job Market Dashboard')
        
        today= date.today()
        max_date= today - timedelta(days= 30*6)
        
        selected_country = st.selectbox('Select a country', country_dic.keys())
        selected_category= st.selectbox('Select a category', category_dict.keys())
        results_per_page= str(st.text_input('How many results do you want to see?:'))
        what= str(st.text_input('Which keywords are you looking for?:'))
        what_exclude=str(st.text_input('Which keywords would you like to exclude?:'))
        where= str(st.text_input('What location would you like to work on?:'))
        max_days_old_=st.slider("How old can the offers be?",min_value=max_date,max_value= today,format="DD/MM/YY",)
        max_days_old = (today-max_days_old_).days
        salary_min=str(st.slider("Minimum salary?:",min_value=500,max_value= 10000))
        salary_max=str(st.slider("Maximum salary?:",min_value=10000,max_value= 1000000))
        work_time = st.selectbox('Part time or full time hours?', ['both','part_time', 'full_time'])
        work_time_dic= {}
        if work_time == 'part_time':
            work_time_dic={'part_time':'1'}
        elif work_time == 'full_time':
            work_time_dic={'full_time':'1'}
            


        selected_color_theme = st.selectbox('Select a color theme', color_theme_list)  

        submit_button = st.form_submit_button(label='Search Jobs')

if submit_button:
    if not results_per_page.isdigit() or not (1 <= int(results_per_page) <= 50):
        st.warning("Please enter a valid positive number for results per page.")
        st.stop()

    if not str(salary_min).isdigit() or not str(salary_max).isdigit():
        st.warning("Salary values must be numbers.")
        st.stop()

    if int(salary_min) < 0 or int(salary_max) < 0:
        st.warning("Salary values cannot be negative.")
        st.stop()
    
    if len(what.strip()) > 100:
        st.warning("Keyword search is too long. Please limit to 100 characters.")
        st.stop()

    if int(salary_min) > int(salary_max):
        st.warning("Minimum salary cannot be higher than maximum salary.")
        st.stop()
    
    if len(where.strip()) > 100:
        st.warning("Location input is too long. Please limit to 100 characters.")
        st.stop()

    curr_search_id= get_cached_jobs(app_id, app_key,
    category=category_dict[selected_category],
    country=selected_country,
    results_per_page=results_per_page,
    what=what,
    what_exclude=what_exclude,
    where=where,
    max_days_old=max_days_old,
    salary_min=salary_min,
    salary_max=salary_max,
    **work_time_dic
    )


    historical_salary_data = get_cached_historical(app_id, app_key, selected_country, curr_search_id)
    current_salary_distribution = get_cached_current_dist(app_id, app_key, selected_country, what, curr_search_id)
    df_companies = get_cached_top_companies(app_id, app_key, selected_country, what)

    try:
        df = clean_df(get_cached_df(curr_search_id))
        num_res= df.shape[0]
        if num_res==0:
            st.markdown("Sorry, there's no recent results that match your demands... try to search older offers or change the keyword names!" )
            
        else:
            st.markdown("#### Job Offers Found")
            st.markdown(f'There are currently {df.shape[0]} available offers!! ')

            st.dataframe(
                df,
                column_config={
                    "url": st.column_config.LinkColumn("Job URL"),
                    "search_id": None,
                    "id": None,

                }
            )

            wc_colormap, plotly_colorscale = color_map[selected_color_theme]

            col1, col2 = st.columns([2, 2])
            
            with col1:

                salary_stats = df[['salary_min', 'salary_max']].replace(0, pd.NA).dropna()
                if not salary_stats.empty:
                    st.metric("Median Salary", f"£{salary_stats.median().mean():,.0f}")
                    st.metric("Average Salary", f"£{salary_stats.mean().mean():,.0f}")

            with col2:
                if not df['description'].dropna().empty:

                    st.markdown("#### ☁️ Word Cloud of Job Descriptions")

                    text = " ".join([clean_text(desc) for desc in df['description'].dropna()])
                    wordcloud = WordCloud(
                        width=500,
                        height=300,
                        background_color='black',
                        colormap=wc_colormap
                    ).generate(text)

                    fig, ax = plt.subplots()
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis("off")
                    st.pyplot(fig) 

        tab1, tab2 = st.tabs(["📊 Salary Analysis", "🏢 Top Companies"])
        with tab1:

            st.markdown(f'#### Salary range in {country_dic[selected_country]}')

            fig= px.bar(
                current_salary_distribution,
                x='salary',
                y='counts',
                color='counts',
                color_continuous_scale=selected_color_theme,
                title=f"Salary Distribution in {country_dic[selected_country]}",
                labels={'salary': 'Salary ', 'counts': 'Number of Offers'},
                template='plotly_dark'
            )
            st.plotly_chart(fig, use_container_width=True)


            st.markdown(f'#### Salary evolution in {country_dic[selected_country]}')

            fig = px.line(
                historical_salary_data,
                x='date',
                y='salary',
                title=f"Average Salary Trend in {country_dic[selected_country]}",
                labels={'date': 'Date', 'salary': 'Average Salary '},
                template='plotly_dark'
            )

            fig.update_traces(
            line=dict(
                color=plotly_colorscale,  # Use the color string directly
                width=3
            )
        )
            st.plotly_chart(fig, use_container_width=True)


        with tab2:

            fig = px.bar(
                df_companies.head(10),
                x='count',
                y='canonical_name',
                orientation='h',
                title='Top Hiring Companies',
                labels={'count': 'Job Count', 'company': 'Company'},
                color='count',
                color_continuous_scale=selected_color_theme,
                template='plotly_dark'
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)


    except sqlite3.OperationalError as e:
        print("Error:", e)


    
