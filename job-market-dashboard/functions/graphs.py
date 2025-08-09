import plotly.express as px
from wordcloud import WordCloud
import streamlit as st

def plot_salary_trend(df):
    fig = px.line(df, x='date', y='salary')
    fig.update_layout(title='Salary Trend', title_x=0.3)
    st.plotly_chart(fig)

def plot_wordcloud(text_series):
    wordcloud = WordCloud().generate(" ".join(text_series))
    st.image(wordcloud.to_array())
