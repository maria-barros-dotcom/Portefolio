
import re
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

country_dic= {'gb': 'Great Britain', 
              'us': 'United States', 
              'at': 'Austria', 
              'au': 'Australia', 
              'be': 'Belgium', 
              'br': 'Brazil',
              'ca': 'Canada',
              'ch': 'Switzerland',
              'de': 'Germany',
              'es': 'Spain',
              'fr': 'France',
              'in': 'India',
              'it': 'Italy',
              'mx': 'Mexico',
              'nl': 'Netherlands',
              'nz': 'New Zealand',
              'pl': 'Poland',
              'sg': 'Singapore',
              'za': 'South Africa' }

color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
        

color_map = {
    'blues': ('Blues', '#1f77b4'),
    'cividis': ('cividis', '#636EFA'),
    'greens': ('Greens', '#2ca02c'),
    'inferno': ('inferno', '#FF7F0E'),
    'magma': ('magma', '#D62728'),
    'plasma': ('plasma', '#9467BD'),
    'reds': ('Reds', '#D62728'),
    'rainbow': ('rainbow', '#FF0000'),
    'turbo': ('turbo', '#7F7F7F'),
    'viridis': ('viridis', '#8C564B')
}

def clean_text(text): 
    
    text = text.lower()
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    
    tokens = word_tokenize(text)
    
    stop_words = set(stopwords.words('english'))
    filtered = [word for word in tokens if word not in stop_words and len(word) > 2]

    return " ".join(filtered)

def clean_df(df):
    
    df = df.drop_duplicates(subset='id', keep='last')
    
    df = df.dropna(subset=['title', 'description', 'salary_min', 'salary_max'])
    
    return df
