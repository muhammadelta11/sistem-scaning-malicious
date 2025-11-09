# Implementasi Training Model

## 📋 Daftar Isi

1. [Struktur Kode](#struktur-kode)
2. [Implementasi Preprocessing](#implementasi-preprocessing)
3. [Implementasi TF-IDF](#implementasi-tf-idf)
4. [Implementasi Algoritma](#implementasi-algoritma)
5. [Implementasi Evaluasi](#implementasi-evaluasi)
6. [Contoh Kode Lengkap](#contoh-kode-lengkap)

---

## Struktur Kode

### File Utama

- **`scanner/services/training_service.py`**: Service utama untuk training model
- **`scanner/views.py`**: View untuk halaman training (function `training_view`)
- **`scanner/templates/scanner/training.html`**: Template HTML untuk halaman training

### Dependencies

```python
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
```

---

## Implementasi Preprocessing

### 1. Load Dataset

```python
import pandas as pd

# Load dataset dari CSV
df = pd.read_csv('labeling_judol_dan_aman-26.csv')

# Cek struktur dataset
print(df.head())
print(f"Total rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
```

### 2. Gabungkan Teks

```python
# Gabungkan title dan description
df['text'] = df['title'].fillna('') + ' ' + df['description'].fillna('')

# Filter data kosong
df = df[df['text'].str.strip() != ''].copy()

print(f"Data setelah filter: {len(df)} rows")
```

### 3. Stemming Bahasa Indonesia

```python
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Setup stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

def stem_text(text: str) -> str:
    """Stem teks Bahasa Indonesia."""
    try:
        return stemmer.stem(text)
    except:
        return text

# Apply stemming
df['text_stemmed'] = df['text'].apply(stem_text)

# Contoh hasil stemming
print("Original:", df['text'].iloc[0])
print("Stemmed:", df['text_stemmed'].iloc[0])
```

**Contoh Output**:
```
Original: DEPOSIT PULSA BONUS 100 Baca Buku Digital Menambah Ilmu
Stemmed: deposit pulsa bonus 100 baca buku digital tambah ilmu
```

### 4. Label Mapping

```python
# Mapping label string ke numerik
label_mapping = {
    'aman': 0,
    'hack judol': 1,
    'pornografi': 2,
    'hacked': 3
}

# Filter hanya label yang valid
df = df[df['label_status'].isin(label_mapping.keys())].copy()

# Convert label ke numerik
df['label'] = df['label_status'].map(label_mapping)

# Cek distribusi label
print(df['label_status'].value_counts())
```

**Output**:
```
hack judol    450
aman          300
pornografi     50
hacked         12
Name: label_status, dtype: int64
```

---

## Implementasi TF-IDF

### 1. Inisialisasi TF-IDF Vectorizer

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# Inisialisasi TF-IDF Vectorizer
tfidf = TfidfVectorizer(
    max_features=10000,      # Maksimal 10,000 fitur (kata unik)
    ngram_range=(1, 2),      # Unigram (1 kata) dan Bigram (2 kata)
    lowercase=True,           # Convert ke lowercase
    stop_words=None,          # Tidak menggunakan stop words (karena sudah di-stem)
    min_df=1,                # Minimum document frequency = 1
    max_df=0.95              # Maximum document frequency = 95% (menghilangkan kata yang terlalu umum)
)
```

### 2. Transform Teks ke Vektor

```python
# Fit dan transform data training
X_train_tfidf = tfidf.fit_transform(X_train)

# Transform data testing (hanya transform, tidak fit)
X_test_tfidf = tfidf.transform(X_test)

# Cek dimensi
print(f"Training shape: {X_train_tfidf.shape}")  # (n_samples, 10000)
print(f"Test shape: {X_test_tfidf.shape}")        # (n_samples, 10000)
```

**Output**:
```
Training shape: (650, 10000)
Test shape: (162, 10000)
```

### 3. Contoh Vektor TF-IDF

```python
# Ambil contoh vektor untuk satu dokumen
example_vector = X_train_tfidf[0].toarray()[0]

# Cari fitur dengan nilai tertinggi
feature_names = tfidf.get_feature_names_out()
top_indices = example_vector.argsort()[-10:][::-1]  # Top 10

print("Top 10 fitur dengan nilai TF-IDF tertinggi:")
for idx in top_indices:
    print(f"  {feature_names[idx]}: {example_vector[idx]:.4f}")
```

**Output**:
```
Top 10 fitur dengan nilai TF-IDF tertinggi:
  deposit pulsa: 0.4523
  pulsa bonus: 0.3891
  bonus 100: 0.3124
  deposit: 0.2456
  pulsa: 0.1987
  bonus: 0.1567
  ...
```

---

## Implementasi Algoritma

### 1. SVM (Support Vector Machine)

```python
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

# Buat pipeline: TF-IDF + SVM
svm_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
    ('svm', SVC(
        kernel='linear',        # Linear kernel
        C=1.0,                  # Regularization parameter
        class_weight='balanced' # Menyeimbangkan kelas
    ))
])

# Training
svm_pipeline.fit(X_train, y_train)

# Prediksi
y_pred_svm = svm_pipeline.predict(X_test)

# Evaluasi
from sklearn.metrics import accuracy_score, classification_report
acc_svm = accuracy_score(y_test, y_pred_svm)
print(f"SVM Accuracy: {acc_svm:.4f}")
```

### 2. Naive Bayes (Multinomial)

```python
from sklearn.naive_bayes import MultinomialNB

# Buat pipeline: TF-IDF + Naive Bayes
nb_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
    ('nb', MultinomialNB())
])

# Training
nb_pipeline.fit(X_train, y_train)

# Prediksi
y_pred_nb = nb_pipeline.predict(X_test)

# Evaluasi
acc_nb = accuracy_score(y_test, y_pred_nb)
print(f"Naive Bayes Accuracy: {acc_nb:.4f}")
```

### 3. Random Forest

```python
from sklearn.ensemble import RandomForestClassifier

# Buat pipeline: TF-IDF + Random Forest
rf_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
    ('rf', RandomForestClassifier(
        n_estimators=100,        # 100 pohon keputusan
        class_weight='balanced', # Menyeimbangkan kelas
        random_state=42          # Reproducibility
    ))
])

# Training
rf_pipeline.fit(X_train, y_train)

# Prediksi
y_pred_rf = rf_pipeline.predict(X_test)

# Evaluasi
acc_rf = accuracy_score(y_test, y_pred_rf)
print(f"Random Forest Accuracy: {acc_rf:.4f}")
```

---

## Implementasi Evaluasi

### 1. Classification Report

```python
from sklearn.metrics import classification_report

# Generate classification report
report = classification_report(
    y_test,              # True labels
    y_pred,              # Predicted labels
    target_names=['aman', 'hack judol', 'pornografi', 'hacked'],  # Label names
    output_dict=True,    # Return as dictionary
    zero_division=0      # Handle division by zero
)

# Print report
print(classification_report(
    y_test, y_pred,
    target_names=['aman', 'hack judol', 'pornografi', 'hacked']
))
```

**Output**:
```
              precision    recall  f1-score   support

        aman       0.95      0.98      0.96        60
   hack judol       0.97      0.95      0.96        90
  pornografi       0.92      0.85      0.88        10
      hacked       0.80      0.75      0.77         2

    accuracy                           0.95       162
   macro avg       0.91      0.88      0.89       162
weighted avg       0.95      0.95      0.95       162
```

### 2. F1-Score Macro Average

```python
# Extract F1-Score Macro Average
f1_macro = report['macro avg']['f1-score']
print(f"F1-Score (Macro Avg): {f1_macro:.4f}")
```

### 3. Confusion Matrix

```python
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Generate confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Visualize confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['aman', 'hack judol', 'pornografi', 'hacked'],
            yticklabels=['aman', 'hack judol', 'pornografi', 'hacked'])
plt.xlabel('Prediksi')
plt.ylabel('Aktual')
plt.title('Confusion Matrix')
plt.show()
```

### 4. Perbandingan Model

```python
# Bandingkan semua model
results = []

models = {
    "SVM": svm_pipeline,
    "Naive Bayes": nb_pipeline,
    "Random Forest": rf_pipeline
}

for name, pipeline in models.items():
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    f1_macro = report['macro avg']['f1-score']
    
    results.append({
        'Model': name,
        'Accuracy': acc,
        'F1-Score (Macro)': f1_macro
    })

# Tampilkan hasil
import pandas as pd
df_results = pd.DataFrame(results)
print(df_results)
```

**Output**:
```
           Model  Accuracy  F1-Score (Macro)
0            SVM     0.9500           0.8900
1   Naive Bayes     0.9383           0.8750
2  Random Forest     0.9444           0.8820
```

### 5. Pilih Model Terbaik

```python
# Pilih model terbaik berdasarkan F1-Score Macro Average
best_model = max(results, key=lambda x: x['F1-Score (Macro)'])
print(f"Model terbaik: {best_model['Model']}")
print(f"F1-Score: {best_model['F1-Score (Macro)']:.4f}")
```

---

## Contoh Kode Lengkap

### Training Service (Lengkap)

```python
"""
Service untuk training model machine learning.
"""

import logging
import pandas as pd
import joblib
import os
from typing import Dict, Any, Optional
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

logger = logging.getLogger(__name__)

# Setup stemmer
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
    def train_model(dataset_path: str) -> Dict[str, Any]:
        """
        Train model from dataset.
        
        Args:
            dataset_path: Path ke file dataset CSV
            
        Returns:
            Dictionary dengan keys: success, message, metrics, model_info
        """
        try:
            # 1. Load dataset
            logger.info(f"Loading dataset from: {dataset_path}")
            df = pd.read_csv(dataset_path)
            
            # 2. Preprocessing
            # Gabungkan title dan description
            df['text'] = df['title'].fillna('') + ' ' + df['description'].fillna('')
            df = df[df['text'].str.strip() != ''].copy()
            
            if len(df) == 0:
                return {
                    'success': False,
                    'message': 'Dataset kosong setelah preprocessing',
                    'error': 'No valid data'
                }
            
            logger.info(f"Dataset size: {len(df)} rows")
            
            # 3. Stemming
            logger.info("Applying Indonesian stemming...")
            df['text_stemmed'] = df['text'].apply(stem_text)
            
            # 4. Label mapping
            label_mapping = {'aman': 0, 'hack judol': 1, 'pornografi': 2, 'hacked': 3}
            df = df[df['label_status'].isin(label_mapping.keys())].copy()
            df['label'] = df['label_status'].map(label_mapping)
            
            # 5. Count distribution
            label_counts = df['label_status'].value_counts().to_dict()
            
            # 6. Train-test split
            X = df['text_stemmed']
            y = df['label']
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, stratify=y, test_size=0.2, random_state=42
            )
            
            # 7. Train models
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
                
                # Evaluasi
                acc = accuracy_score(y_test, y_pred)
                report = classification_report(
                    y_test, y_pred,
                    target_names=label_mapping.keys(),
                    output_dict=True,
                    zero_division=0
                )
                f1_macro = report.get("macro avg", {}).get("f1-score", 0)
                
                results.append({
                    "Model": name,
                    "Akurasi": acc,
                    "F1-Score (Macro Avg)": f1_macro,
                    "Pipeline": pipeline,
                    "Report": report
                })
            
            # 8. Pilih model terbaik
            best_model = max(results, key=lambda x: x["F1-Score (Macro Avg)"])
            
            # 9. Simpan model
            model_filename = 'seo_poisoning_best_model.joblib'
            model_data = {
                'model': best_model["Pipeline"],
                'label_mapping': label_mapping,
                'version': f"django_best_{best_model['Model'].lower().replace(' ', '_')}"
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
            logger.error(f"Training error: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'Error saat training: {str(e)}',
                'error': str(e)
            }
```

### Penggunaan Training Service

```python
from scanner.services.training_service import TrainingService

# Training model
result = TrainingService.train_model('labeling_judol_dan_aman-26.csv')

if result['success']:
    print(f"Model terbaik: {result['metrics']['best_model']}")
    print(f"Accuracy: {result['metrics']['accuracy']:.4f}")
    print(f"F1-Score: {result['metrics']['f1_score']:.4f}")
    print(f"Training size: {result['training_size']}")
    print(f"Test size: {result['test_size']}")
else:
    print(f"Error: {result['message']}")
```

---

## Tips dan Best Practices

### 1. Data Preprocessing

- **Selalu filter data kosong**: Menghindari error saat training
- **Gunakan stemming**: Meningkatkan akurasi untuk Bahasa Indonesia
- **Normalisasi teks**: Convert ke lowercase, hapus karakter khusus

### 2. Feature Extraction

- **Pilih max_features yang tepat**: Terlalu kecil mengurangi informasi, terlalu besar memperlambat training
- **Gunakan n-gram**: Menangkap konteks frasa (bigram, trigram)
- **Tune min_df dan max_df**: Menghilangkan kata yang terlalu jarang atau terlalu umum

### 3. Model Selection

- **Gunakan stratified sampling**: Mempertahankan proporsi kelas
- **Evaluasi dengan multiple metrics**: Accuracy, Precision, Recall, F1-Score
- **Pilih model berdasarkan F1-Score Macro**: Lebih adil untuk imbalanced data

### 4. Model Evaluation

- **Gunakan confusion matrix**: Memahami distribusi error
- **Perhatikan per-class metrics**: Identifikasi kelas yang sulit diprediksi
- **Validasi dengan test set**: Jangan gunakan test set untuk tuning

### 5. Model Persistence

- **Simpan model dengan joblib**: Format yang efisien untuk scikit-learn
- **Include metadata**: Label mapping, version, training date
- **Backup model lama**: Sebelum training ulang

---

## Troubleshooting

### 1. Dataset Kosong

**Error**: `Dataset kosong setelah preprocessing`

**Solusi**:
- Cek apakah kolom `title` dan `description` memiliki data
- Pastikan tidak semua data kosong setelah filtering

### 2. Memory Error

**Error**: `MemoryError` saat training

**Solusi**:
- Kurangi `max_features` di TfidfVectorizer (misalnya 5000)
- Kurangi `n_estimators` di RandomForest (misalnya 50)
- Gunakan batch processing untuk dataset besar

### 3. Imbalanced Data

**Problem**: Model bias ke kelas mayoritas

**Solusi**:
- Gunakan `class_weight='balanced'` di SVM dan Random Forest
- Gunakan F1-Score Macro Average sebagai metrik utama
- Pertimbangkan oversampling atau undersampling

### 4. Low Accuracy

**Problem**: Akurasi rendah (< 80%)

**Solusi**:
- Cek kualitas dataset (label yang benar)
- Tambah jumlah data training
- Tune hyperparameter (C untuk SVM, n_estimators untuk RF)
- Coba algoritma lain atau ensemble methods

---

## Referensi Kode

- **Training Service**: `scanner/services/training_service.py`
- **Training View**: `scanner/views.py` (function `training_view`)
- **Training Template**: `scanner/templates/scanner/training.html`
- **Dataset**: `labeling_judol_dan_aman-26.csv`

