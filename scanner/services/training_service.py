"""
Service untuk training model machine learning.
"""

import logging
import pandas as pd
import joblib
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import traceback
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from django.conf import settings

logger = logging.getLogger(__name__)

# Stemming setup
factory = StemmerFactory()
stemmer = factory.create_stemmer()

def stem_text(text: str) -> str:
    """Stem Bahasa Indonesia."""
    try:
        return stemmer.stem(text)
    except:
        return text


class TrainingService:
    """Service untuk training ML model."""
    
    @staticmethod
    def get_dataset_path() -> Optional[str]:
        """Get path to dataset file."""
        try:
            # Try to get from scanner.config
            from scanner import config
            dataset_path = config.DATASET_FILE
            
            if os.path.exists(dataset_path):
                return dataset_path
            
            # Fallback to BASE_DIR
            base_dir = str(settings.BASE_DIR) if hasattr(settings.BASE_DIR, '__str__') else settings.BASE_DIR
            fallback_path = os.path.join(base_dir, 'labeling_judol_dan_aman-26.csv')
            
            if os.path.exists(fallback_path):
                return fallback_path
                
            return None
        except Exception as e:
            logger.error(f"Error getting dataset path: {e}")
            return None
    
    @staticmethod
    def get_model_path() -> str:
        """Get path to save trained model."""
        try:
            from scanner import config
            return config.MODEL_FILE
        except:
            base_dir = str(settings.BASE_DIR) if hasattr(settings.BASE_DIR, '__str__') else settings.BASE_DIR
            return os.path.join(base_dir, 'seo_poisoning_best_model.joblib')
    
    @staticmethod
    def check_dataset() -> Tuple[bool, str, Optional[int]]:
        """Check if dataset exists and get info."""
        dataset_path = TrainingService.get_dataset_path()
        
        if not dataset_path or not os.path.exists(dataset_path):
            return False, "Dataset tidak ditemukan", None
        
        try:
            df = pd.read_csv(dataset_path)
            row_count = len(df)
            return True, dataset_path, row_count
        except Exception as e:
            return False, f"Error membaca dataset: {e}", None
    
    @staticmethod
    def check_model() -> Tuple[bool, str, Optional[Dict]]:
        """Check if trained model exists."""
        model_path = TrainingService.get_model_path()
        
        if not os.path.exists(model_path):
            return False, "Model belum dilatih", None
        
        try:
            model_data = joblib.load(model_path)
            version = model_data.get('version', 'unknown')
            label_mapping = model_data.get('label_mapping', {})
            training_info = model_data.get('training_info', None)
            
            model_info_dict = {
                'path': model_path,
                'version': version,
                'labels': list(label_mapping.keys())
            }
            
            # Add training information if available
            if training_info:
                model_info_dict['training_info'] = training_info
            
            return True, f"Model version: {version}", model_info_dict
        except Exception as e:
            return False, f"Error membaca model: {e}", None
    
    @staticmethod
    def train_model(dataset_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Train model from dataset.
        
        Returns:
            Dictionary dengan keys: success, message, metrics, model_info
        """
        try:
            # Get dataset path
            if not dataset_path:
                dataset_path = TrainingService.get_dataset_path()
            
            if not dataset_path or not os.path.exists(dataset_path):
                return {
                    'success': False,
                    'message': 'Dataset tidak ditemukan',
                    'error': 'File dataset tidak ada'
                }
            
            # Load data
            logger.info(f"Loading dataset from: {dataset_path}")
            df = pd.read_csv(dataset_path)
            
            # Combine text columns
            df['text'] = df['title'].fillna('') + ' ' + df['description'].fillna('')
            df = df[df['text'].str.strip() != ''].copy()
            
            if len(df) == 0:
                return {
                    'success': False,
                    'message': 'Dataset kosong setelah preprocessing',
                    'error': 'No valid data'
                }
            
            logger.info(f"Dataset size: {len(df)} rows")
            
            # Apply stemming
            logger.info("Applying Indonesian stemming...")
            df['text_stemmed'] = df['text'].apply(stem_text)
            
            # Mapping label
            label_mapping = {'aman': 0, 'hack judol': 1, 'pornografi': 2, 'hacked': 3}
            df = df[df['label_status'].isin(label_mapping.keys())].copy()
            df['label'] = df['label_status'].map(label_mapping)
            
            # Count distribution
            label_counts = df['label_status'].value_counts().to_dict()
            
            # Split data
            X = df['text_stemmed']
            y = df['label']
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, stratify=y, test_size=0.2, random_state=42
            )
            
            # Train models
            models = {
                "SVM (Linear)": SVC(kernel='linear', C=1.0, class_weight='balanced'),
                "Naive Bayes": MultinomialNB(),
                "Random Forest": RandomForestClassifier(
                    n_estimators=100, class_weight='balanced', random_state=42
                )
            }
            
            logger.info(f"Training {len(models)} models...")
            results = []
            
            for name, clf in models.items():
                logger.info(f"Training {name}...")
                pipeline = Pipeline([
                    ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
                    ('clf', clf)
                ])
                pipeline.fit(X_train, y_train)
                y_pred = pipeline.predict(X_test)
                
                acc = accuracy_score(y_test, y_pred)
                report = classification_report(
                    y_test, y_pred, 
                    target_names=list(label_mapping.keys()), 
                    output_dict=True,
                    zero_division=0
                )
                
                # Pastikan semua kelas ada di report, bahkan jika tidak ada di test set
                for label_name, label_num in label_mapping.items():
                    if label_name not in report:
                        report[label_name] = {
                            'precision': 0.0,
                            'recall': 0.0,
                            'f1-score': 0.0,
                            'support': 0
                        }
                
                f1_macro = report.get("macro avg", {}).get("f1-score", 0)
                
                results.append({
                    "Model": name,
                    "Akurasi": acc,
                    "F1-Score (Macro Avg)": f1_macro,
                    "Pipeline": pipeline,
                    "Report": report
                })
            
            # Find best model
            best_model = max(results, key=lambda x: x["F1-Score (Macro Avg)"])
            
            # Save model with training information
            model_filename = TrainingService.get_model_path()
            model_data = {
                'model': best_model["Pipeline"],
                'label_mapping': label_mapping,
                'version': f"django_best_{best_model['Model'].lower().replace(' ', '_')}",
                # Save training information for display
                'training_info': {
                    'best_model': best_model['Model'],
                    'accuracy': best_model['Akurasi'],
                    'f1_score': best_model['F1-Score (Macro Avg)'],
                    'all_results': [
                        {
                            'model': r['Model'],
                            'accuracy': r['Akurasi'],
                            'f1_score': r['F1-Score (Macro Avg)']
                        }
                        for r in results
                    ],
                    'training_size': len(X_train),
                    'test_size': len(X_test),
                    'label_counts': label_counts,
                    'trained_at': datetime.now().isoformat()
                }
            }
            joblib.dump(model_data, model_filename)
            
            logger.info(f"Model saved to: {model_filename}")
            
            return {
                'success': True,
                'message': 'Model berhasil dilatih dan disimpan',
                'metrics': {
                    'best_model': best_model['Model'],
                    'accuracy': best_model['Akurasi'],
                    'f1_score': best_model['F1-Score (Macro Avg)'],
                    'all_results': [
                        {
                            'model': r['Model'],
                            'accuracy': r['Akurasi'],
                            'f1_score': r['F1-Score (Macro Avg)']
                        }
                        for r in results
                    ],
                    'class_report': best_model['Report'],
                    'label_distribution': label_mapping,
                    'label_counts': label_counts
                },
                'model_info': {
                    'path': model_filename,
                    'version': model_data['version']
                },
                'training_size': len(X_train),
                'test_size': len(X_test)
            }
            
        except Exception as e:
            error_msg = str(e)
            error_trace = traceback.format_exc()
            logger.error(f"Training error: {error_msg}\n{error_trace}")
            
            return {
                'success': False,
                'message': f'Error saat training: {error_msg}',
                'error': error_trace
            }

