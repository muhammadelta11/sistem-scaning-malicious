# data_manager.py
"""
Mengelola semua operasi baca dan tulis file (dataset, dashboard).
"""

import os
import pandas as pd
import joblib
import csv
from datetime import datetime
import streamlit as st # Diperlukan untuk st.success/warning

# Import konstanta dari config.py
from config import DATA_FILE, DATASET_FILE, MODEL_FILE

def load_or_create_dataset():
    """Memuat atau membuat dataset untuk training"""
    if os.path.exists(DATASET_FILE):
        try:
            df = pd.read_csv(DATASET_FILE, quoting=csv.QUOTE_ALL)
            required_cols = ["url", "title", "description", "timestamp", "label_status"]
            for col in required_cols:
                if col not in df.columns:
                    df[col] = ""
            return df
        except:
            return pd.DataFrame(columns=["url", "title", "description", "timestamp", "label_status"])
    else:
        return pd.DataFrame(columns=["url", "title", "description", "timestamp", "label_status"])

def add_to_dataset(url, title, description, label_status):
    """Menambahkan data baru ke dataset dengan format yang benar"""
    try:
        if os.path.exists(DATASET_FILE):
            try:
                existing_df = pd.read_csv(DATASET_FILE, engine='python')
                if url in existing_df['url'].values:
                    st.warning(f"URL sudah ada dalam dataset: {url}")
                    return False
            except:
                pass
        
        new_data = {
            "url": url,
            "title": title[:500] if len(title) > 500 else title,
            "description": description[:1000] if len(description) > 1000 else description,
            "timestamp": datetime.now().strftime("%Y-%m-%d"),
            "label_status": label_status
        }
        
        new_df = pd.DataFrame([new_data])
        
        if os.path.exists(DATASET_FILE):
            existing_df = pd.read_csv(DATASET_FILE, engine='python')
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df.to_csv(DATASET_FILE, index=False, quoting=csv.QUOTE_ALL)
        else:
            new_df.to_csv(DATASET_FILE, index=False, quoting=csv.QUOTE_ALL)
        
        st.success(f"Data berhasil ditambahkan ke dataset dengan label: {label_status}")
        return True
        
    except Exception as e:
        st.error(f"Gagal menambahkan data ke dataset: {str(e)}")
        return False

def ensure_dataframe_columns(df):
    """Memastikan semua kolom yang diperlukan ada dalam dataframe"""
    required_columns = ['domain', 'jumlah_kasus', 'hack_judol', 'pornografi', 'hacked', 'last_scan']
    
    for col in required_columns:
        if col not in df.columns:
            if col == 'domain':
                df[col] = ''
            elif col == 'last_scan':
                df[col] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                df[col] = 0
    
    return df

def load_or_create_dataframe():
    """Memuat atau membuat dataframe dengan kolom yang benar"""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = ensure_dataframe_columns(df)
    else:
        df = pd.DataFrame(columns=['domain', 'jumlah_kasus', 'hack_judol', 'pornografi', 'hacked', 'last_scan'])
    
    return df

@st.cache_resource
def load_resources():
    """Memuat model ML, mapping label, dan data dashboard."""
    try:
        model_data = joblib.load(MODEL_FILE)
    except:
        st.error(f"Model ML tidak ditemukan. Pastikan file '{MODEL_FILE}' ada.")
        model_data = {'model': None, 'label_mapping': {}}
    
    ranking_data = load_or_create_dataframe()
    
    return model_data['model'], model_data['label_mapping'], ranking_data