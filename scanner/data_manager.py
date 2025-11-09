# data_manager.py
"""
Mengelola semua operasi baca dan tulis file (dataset, dashboard).
"""

import os
import pandas as pd
import joblib
import csv
from datetime import datetime
import logging

# Import konstanta dari config.py
from .config import DATA_FILE, DATASET_FILE, MODEL_FILE

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
    """Menambahkan data baru ke dataset dengan format yang benar.
    Memastikan kolom yang digunakan sama dengan struktur file CSV yang sudah ada.
    """
    try:
        # Pastikan directory ada
        dataset_dir = os.path.dirname(DATASET_FILE)
        if dataset_dir and not os.path.exists(dataset_dir):
            os.makedirs(dataset_dir, exist_ok=True)
        
        # Sanitize input
        if not url:
            raise ValueError("URL tidak boleh kosong")
        
        url = str(url).strip()
        title = str(title).strip()[:500] if title else ""
        description = str(description).strip()[:1000] if description else ""
        label_status = str(label_status).strip() if label_status else "malicious"
        
        # Get existing columns structure from CSV file
        existing_columns = None
        existing_df_full = None
        
        if os.path.exists(DATASET_FILE):
            try:
                # Read existing CSV to get column structure and data
                # Use same quoting as original file
                existing_df_full = pd.read_csv(
                    DATASET_FILE, 
                    engine='python', 
                    encoding='utf-8', 
                    quoting=csv.QUOTE_ALL,
                    on_bad_lines='skip'  # Skip bad lines if any
                )
                existing_columns = list(existing_df_full.columns)
                
                logging.info(f"Dataset existing columns: {existing_columns}")
                logging.info(f"Total existing rows: {len(existing_df_full)}")
                
                # Check if URL already exists (case-insensitive)
                if 'url' in existing_df_full.columns:
                    # Normalize URLs for comparison (lowercase, strip whitespace, remove trailing slash)
                    def normalize_url(u):
                        if pd.isna(u):
                            return ""
                        u_str = str(u).strip().lower()
                        # Remove trailing slash for comparison
                        if u_str.endswith('/'):
                            u_str = u_str[:-1]
                        return u_str
                    
                    # Normalize existing URLs
                    existing_urls = existing_df_full['url'].apply(normalize_url)
                    
                    # Normalize input URL
                    normalized_input_url = url.strip().lower()
                    if normalized_input_url.endswith('/'):
                        normalized_input_url = normalized_input_url[:-1]
                    
                    # Check for exact match
                    if normalized_input_url in existing_urls.values:
                        logging.warning(f"URL sudah ada dalam dataset (exact match): {url}")
                        return False
                    
                    # Also check for URL variations (with/without trailing slash, http/https)
                    url_variations = [
                        normalized_input_url,
                        normalized_input_url + '/',
                        normalized_input_url.replace('https://', 'http://'),
                        normalized_input_url.replace('http://', 'https://'),
                        normalized_input_url.replace('https://', 'http://') + '/',
                        normalized_input_url.replace('http://', 'https://') + '/',
                    ]
                    
                    for var_url in url_variations:
                        if var_url in existing_urls.values:
                            logging.warning(f"URL sudah ada dalam dataset (variation match): {url}")
                            return False
            except Exception as e:
                logging.error(f"Error reading existing dataset: {e}", exc_info=True)
                existing_columns = None
                existing_df_full = None
        
        # Prepare new data - start with required columns
        # Check timestamp format from existing data if available
        timestamp_format = "%d/%m/%Y"  # Default format (matching existing file)
        timestamp_value = None
        
        if existing_df_full is not None and 'timestamp' in existing_df_full.columns:
            # Get first non-empty timestamp to check format
            sample_timestamps = existing_df_full['timestamp'].dropna()
            if len(sample_timestamps) > 0:
                sample_timestamp = sample_timestamps.iloc[0]
                # Try to detect format (could be "5/5/2025" or "2025-05-05" or "2025-5-5")
                timestamp_str = str(sample_timestamp).strip()
                if '/' in timestamp_str:
                    timestamp_format = "%d/%m/%Y"  # Format like "5/5/2025"
                elif '-' in timestamp_str:
                    parts = timestamp_str.split('-')
                    if len(parts[0]) == 4:
                        timestamp_format = "%Y-%m-%d"  # Format like "2025-05-05"
                    else:
                        timestamp_format = "%d-%m-%Y"  # Format like "5-5-2025"
        
        # Format timestamp according to existing format
        now = datetime.now()
        if timestamp_format == "%d/%m/%Y":
            # Format: day/month/year (no leading zeros for day/month if < 10)
            timestamp_value = f"{now.day}/{now.month}/{now.year}"
        elif timestamp_format == "%d-%m-%Y":
            timestamp_value = now.strftime("%d-%m-%Y")
        elif timestamp_format == "%Y-%m-%d":
            timestamp_value = now.strftime("%Y-%m-%d")
        else:
            # Default fallback
            timestamp_value = f"{now.day}/{now.month}/{now.year}"
        
        new_data = {
            "url": url,
            "title": title,
            "description": description,
            "timestamp": timestamp_value,
            "label_status": label_status
        }
        
        # If existing columns exist, preserve all columns and fill missing ones
        if existing_columns:
            # Add any missing columns from existing structure with default values
            for col in existing_columns:
                if col not in new_data:
                    # Fill with appropriate default value based on column name
                    col_lower = col.lower()
                    if col_lower in ['id', 'index']:
                        # Skip ID/index columns - pandas will handle them
                        continue
                    elif col_lower.startswith('date') or col_lower.startswith('time'):
                        # Use same timestamp format as detected
                        new_data[col] = timestamp_value
                    elif col_lower in ['created_at', 'updated_at', 'created', 'updated']:
                        # Use same timestamp format as detected
                        new_data[col] = timestamp_value
                    else:
                        new_data[col] = ""  # Empty string for other unknown columns
            
            # Ensure all existing columns are in the same order as original file
            # Only include columns that exist in original structure
            ordered_data = {}
            for col in existing_columns:
                if col in new_data:
                    ordered_data[col] = new_data[col]
                else:
                    # Fill missing columns with empty string
                    ordered_data[col] = ""
            new_data = ordered_data
        
        # Create new dataframe with new data
        # Ensure columns are in correct order from the start
        if existing_columns:
            # Create dataframe with columns in same order as existing
            new_df = pd.DataFrame([new_data], columns=existing_columns)
        else:
            # No existing file, use standard order
            new_df = pd.DataFrame([new_data])

        if existing_df_full is not None and len(existing_df_full) > 0:
            try:
                # Ensure both dataframes have same columns in same order
                if existing_columns:
                    # Ensure existing_df has all columns in correct order
                    for col in existing_columns:
                        if col not in existing_df_full.columns:
                            existing_df_full[col] = ""
                    existing_df_full = existing_df_full[existing_columns]
                
                # Combine dataframes
                combined_df = pd.concat([existing_df_full, new_df], ignore_index=True)
                
                # Save with same column order and format as original
                combined_df.to_csv(DATASET_FILE, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')
                logging.info(f"Data berhasil ditambahkan. Total rows: {len(combined_df)}")
            except Exception as e:
                logging.error(f"Error combining dataframes: {e}", exc_info=True)
                raise
        else:
            # Create new file, preserve column order if known
            if existing_columns:
                new_df = new_df[existing_columns]
            new_df.to_csv(DATASET_FILE, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')
            logging.info(f"Dataset baru dibuat dengan {len(new_df)} row")

        logging.info(f"Data berhasil ditambahkan ke dataset dengan label: {label_status}")
        return True

    except Exception as e:
        logging.error(f"Gagal menambahkan data ke dataset: {str(e)}", exc_info=True)
        raise  # Re-raise untuk ditangani di service layer

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

def load_resources():
    """Memuat model ML, mapping label, dan data dashboard."""
    try:
        model_data = joblib.load(MODEL_FILE)
    except:
        logging.error(f"Model ML tidak ditemukan. Pastikan file '{MODEL_FILE}' ada.")
        model_data = {'model': None, 'label_mapping': {}}

    ranking_data = load_or_create_dataframe()

    return model_data['model'], model_data['label_mapping'], ranking_data
