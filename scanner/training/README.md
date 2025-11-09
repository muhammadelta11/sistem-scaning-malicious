# Dokumentasi Teknis Pelatihan Model Machine Learning

## 📋 Daftar Isi

1. [Overview](#overview)
2. [Dataset dan Variabel](#dataset-dan-variabel)
3. [Preprocessing Data](#preprocessing-data)
4. [Feature Extraction (TF-IDF)](#feature-extraction-tf-idf)
5. [Algoritma Machine Learning](#algoritma-machine-learning)
6. [Pembagian Data Training dan Testing](#pembagian-data-training-dan-testing)
7. [Evaluasi Model](#evaluasi-model)
8. [Alur Kerja Training](#alur-kerja-training)
9. [Rumus Matematika](#rumus-matematika)

---

## Overview

Sistem ini menggunakan **Supervised Learning** untuk klasifikasi teks Bahasa Indonesia dalam mendeteksi konten berbahaya pada domain. Model dilatih menggunakan kombinasi **TF-IDF Vectorization** dan tiga algoritma klasifikasi: **SVM (Support Vector Machine)**, **Naive Bayes**, dan **Random Forest**.

**Tujuan**: Mengklasifikasikan konten domain menjadi 4 kategori:
- **Aman** (0): Konten normal/bersih
- **Hack Judol** (1): Konten perjudian ilegal
- **Pornografi** (2): Konten pornografi
- **Hacked** (3): Domain yang di-hack/deface

---

## Dataset dan Variabel

### Format Dataset

Dataset disimpan dalam format **CSV** dengan struktur sebagai berikut:

| Kolom | Tipe Data | Deskripsi | Contoh |
|-------|-----------|-----------|--------|
| `url` | String | URL lengkap dari halaman web | `https://example.com/page` |
| `title` | String | Judul halaman web | `"DEPOSIT PULSA BONUS 100"` |
| `description` | String | Deskripsi/konten halaman | `"Meberikan akses ke seluruh user..."` |
| `timestamp` | String | Waktu pengambilan data | `"5/5/2025"` |
| `label_status` | String | Label klasifikasi | `"hack judol"`, `"aman"`, `"pornografi"`, `"hacked"` |

### Variabel yang Digunakan

#### Variabel Input (Features)
- **X**: Teks gabungan dari `title` + `description` setelah preprocessing
- **X_train**: Data training (80% dari total data)
- **X_test**: Data testing (20% dari total data)

#### Variabel Output (Target)
- **y**: Label numerik yang di-mapping dari `label_status`
- **y_train**: Label training
- **y_test**: Label testing

#### Mapping Label
```python
label_mapping = {
    'aman': 0,
    'hack judol': 1,
    'pornografi': 2,
    'hacked': 3
}
```

### Statistik Dataset

- **Total Data**: ~812 baris (dari `labeling_judol_dan_aman-26.csv`)
- **Distribusi Label**: 
  - Aman: ~X%
  - Hack Judol: ~Y%
  - Pornografi: ~Z%
  - Hacked: ~W%

---

## Preprocessing Data

### 1. Penggabungan Teks

Teks dari kolom `title` dan `description` digabungkan menjadi satu string:

```python
df['text'] = df['title'].fillna('') + ' ' + df['description'].fillna('')
```

**Alasan**: Menggabungkan informasi dari judul dan deskripsi memberikan konteks yang lebih lengkap untuk klasifikasi.

### 2. Filtering Data Kosong

Data dengan teks kosong dihapus:

```python
df = df[df['text'].str.strip() != ''].copy()
```

### 3. Stemming Bahasa Indonesia

Menggunakan library **Sastrawi** untuk melakukan stemming (reduksi kata ke bentuk dasar):

```python
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

factory = StemmerFactory()
stemmer = factory.create_stemmer()

def stem_text(text: str) -> str:
    return stemmer.stem(text)

df['text_stemmed'] = df['text'].apply(stem_text)
```

**Contoh Stemming**:
- `"memberikan"` → `"beri"`
- `"pemain"` → `"main"`
- `"deposit"` → `"deposit"`

**Alasan**: Stemming mengurangi variasi kata dan meningkatkan akurasi klasifikasi dengan mengelompokkan kata-kata yang memiliki akar yang sama.

---

## Feature Extraction (TF-IDF)

### Pengertian TF-IDF

**TF-IDF (Term Frequency-Inverse Document Frequency)** adalah teknik untuk mengubah teks menjadi vektor numerik yang merepresentasikan pentingnya suatu kata dalam dokumen relatif terhadap seluruh koleksi dokumen.

### Rumus TF-IDF

#### 1. Term Frequency (TF)

Frekuensi kemunculan term dalam dokumen:

\[
TF(t, d) = \frac{\text{jumlah kemunculan term } t \text{ dalam dokumen } d}{\text{total jumlah term dalam dokumen } d}
\]

Atau versi yang dinormalisasi:

\[
TF(t, d) = \frac{f_{t,d}}{\sum_{t' \in d} f_{t',d}}
\]

Dimana:
- \( f_{t,d} \) = frekuensi term \( t \) dalam dokumen \( d \)
- \( \sum_{t' \in d} f_{t',d} \) = total frekuensi semua term dalam dokumen \( d \)

#### 2. Inverse Document Frequency (IDF)

Mengukur seberapa jarang atau umum suatu term muncul di seluruh koleksi dokumen:

\[
IDF(t, D) = \log \frac{N}{|d \in D : t \in d|}
\]

Dimana:
- \( N \) = total jumlah dokumen dalam koleksi
- \( |d \in D : t \in d| \) = jumlah dokumen yang mengandung term \( t \)

#### 3. TF-IDF Score

Kombinasi TF dan IDF:

\[
TF\text{-}IDF(t, d, D) = TF(t, d) \times IDF(t, D)
\]

### Implementasi TF-IDF

```python
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(
    max_features=10000,      # Maksimal 10,000 fitur (kata unik)
    ngram_range=(1, 2)        # Unigram (1 kata) dan Bigram (2 kata)
)
```

**Parameter**:
- `max_features=10000`: Membatasi jumlah fitur untuk mengurangi dimensi dan mempercepat training
- `ngram_range=(1, 2)`: Menggunakan unigram dan bigram untuk menangkap konteks frasa

**Contoh N-gram**:
- Unigram: `["deposit", "pulsa", "bonus"]`
- Bigram: `["deposit pulsa", "pulsa bonus"]`

### Transformasi Teks ke Vektor

Setelah TF-IDF, setiap dokumen diubah menjadi vektor numerik dengan dimensi 10,000:

```
Dokumen: "deposit pulsa bonus 100"
↓ TF-IDF Vectorization ↓
Vektor: [0.23, 0.45, 0.12, 0.0, 0.0, ..., 0.67, ...]
         ↑     ↑     ↑     ↑     ↑           ↑
       fitur1 fitur2 fitur3 fitur4 fitur5  fitur10000
```

---

## Algoritma Machine Learning

Sistem ini membandingkan **3 algoritma** dan memilih yang terbaik berdasarkan **F1-Score Macro Average**.

### 1. Support Vector Machine (SVM)

#### Konfigurasi
```python
SVC(kernel='linear', C=1.0, class_weight='balanced')
```

#### Prinsip Kerja

SVM mencari **hyperplane** optimal yang memisahkan kelas-kelas dengan margin maksimal.

**Rumus Hyperplane**:

\[
w \cdot x + b = 0
\]

Dimana:
- \( w \) = vektor bobot (weight vector)
- \( x \) = vektor fitur input
- \( b \) = bias

**Optimasi** (untuk soft-margin SVM):

\[
\min_{w,b,\xi} \frac{1}{2}||w||^2 + C \sum_{i=1}^{n} \xi_i
\]

Subject to:
\[
y_i(w \cdot x_i + b) \geq 1 - \xi_i, \quad \xi_i \geq 0
\]

Dimana:
- \( C = 1.0 \) = parameter regularisasi (trade-off antara margin dan error)
- \( \xi_i \) = slack variable untuk data yang tidak linearly separable
- \( y_i \) = label kelas (-1 atau +1 untuk binary, atau 0-3 untuk multi-class)

**Kernel Linear**: Menggunakan dot product untuk klasifikasi linear:

\[
K(x_i, x_j) = x_i \cdot x_j
\]

**class_weight='balanced'**: Menyeimbangkan bobot kelas untuk menangani imbalanced data.

#### Kelebihan
- Efektif untuk data high-dimensional (seperti TF-IDF dengan 10,000 fitur)
- Robust terhadap overfitting
- Performa baik untuk klasifikasi teks

#### Kekurangan
- Lambat untuk dataset besar
- Sulit diinterpretasikan

---

### 2. Naive Bayes (Multinomial)

#### Konfigurasi
```python
MultinomialNB()
```

#### Prinsip Kerja

Naive Bayes menggunakan **Teorema Bayes** dengan asumsi independensi antar fitur (naive assumption).

**Rumus Teorema Bayes**:

\[
P(y|x) = \frac{P(x|y) \times P(y)}{P(x)}
\]

Dimana:
- \( P(y|x) \) = probabilitas posterior (probabilitas kelas \( y \) diberikan fitur \( x \))
- \( P(x|y) \) = likelihood (probabilitas fitur \( x \) diberikan kelas \( y \))
- \( P(y) \) = prior (probabilitas kelas \( y \))
- \( P(x) \) = evidence (probabilitas fitur \( x \))

**Untuk Multinomial Naive Bayes** (cocok untuk data count seperti TF-IDF):

\[
P(y|x) \propto P(y) \prod_{i=1}^{n} P(x_i|y)
\]

**Likelihood untuk Multinomial**:

\[
P(x_i|y) = \frac{N_{yi} + \alpha}{N_y + \alpha \times |V|}
\]

Dimana:
- \( N_{yi} \) = jumlah kemunculan fitur \( i \) dalam kelas \( y \)
- \( N_y \) = total jumlah fitur dalam kelas \( y \)
- \( \alpha \) = smoothing parameter (Laplace smoothing, default = 1.0)
- \( |V| \) = ukuran vocabulary (jumlah fitur unik)

**Prediksi**:

\[
\hat{y} = \arg\max_{y} P(y) \prod_{i=1}^{n} P(x_i|y)
\]

#### Kelebihan
- Sangat cepat untuk training dan prediksi
- Efektif untuk data teks
- Tidak memerlukan banyak data untuk training

#### Kekurangan
- Asumsi independensi fitur (naive) sering tidak realistis
- Dapat underperform jika ada korelasi antar fitur

---

### 3. Random Forest

#### Konfigurasi
```python
RandomForestClassifier(
    n_estimators=100,           # 100 pohon keputusan
    class_weight='balanced',     # Menyeimbangkan kelas
    random_state=42             # Reproducibility
)
```

#### Prinsip Kerja

Random Forest adalah **ensemble method** yang menggabungkan banyak **Decision Tree** dan mengambil voting dari hasilnya.

**Algoritma**:
1. **Bootstrap Sampling**: Membuat 100 subset data dengan sampling dengan replacement
2. **Random Feature Selection**: Setiap tree hanya menggunakan subset fitur yang dipilih secara random
3. **Tree Construction**: Membangun decision tree untuk setiap subset
4. **Voting**: Prediksi final = majority vote dari semua tree

**Rumus Entropy** (untuk split criteria):

\[
H(S) = -\sum_{i=1}^{c} p_i \log_2(p_i)
\]

Dimana:
- \( S \) = subset data
- \( c \) = jumlah kelas
- \( p_i \) = proporsi sampel kelas \( i \) dalam subset

**Information Gain**:

\[
IG(S, A) = H(S) - \sum_{v \in Values(A)} \frac{|S_v|}{|S|} H(S_v)
\]

Dimana:
- \( A \) = atribut/fitur untuk split
- \( S_v \) = subset data dengan nilai \( v \) untuk atribut \( A \)

**Prediksi**:

\[
\hat{y} = \text{mode}(\{\hat{y}_1, \hat{y}_2, ..., \hat{y}_{100}\})
\]

Dimana \( \hat{y}_i \) adalah prediksi dari tree ke-\( i \).

#### Kelebihan
- Robust terhadap overfitting
- Dapat menangani non-linear relationships
- Feature importance dapat dihitung

#### Kekurangan
- Lebih lambat dari Naive Bayes
- Memerlukan lebih banyak memori
- Kurang interpretable dibanding single tree

---

## Pembagian Data Training dan Testing

### Train-Test Split

Data dibagi menjadi **80% training** dan **20% testing** menggunakan stratified sampling:

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,                      # Features (teks yang sudah di-stem)
    y,                      # Labels (0, 1, 2, 3)
    stratify=y,            # Stratified sampling (mempertahankan proporsi kelas)
    test_size=0.2,         # 20% untuk testing
    random_state=42        # Reproducibility
)
```

### Stratified Sampling

**Stratified sampling** memastikan proporsi setiap kelas di training set dan test set sama dengan proporsi di dataset asli.

**Contoh**:
- Jika dataset memiliki 50% "aman", 30% "hack judol", 15% "pornografi", 5% "hacked"
- Maka training set dan test set juga akan memiliki proporsi yang sama

**Alasan**: Mencegah bias dalam evaluasi model, terutama untuk imbalanced dataset.

### Perbandingan Data

| Set | Proporsi | Jumlah Data (contoh) | Deskripsi |
|-----|----------|---------------------|-----------|
| **Training** | 80% | ~650 sampel | Data untuk melatih model |
| **Testing** | 20% | ~162 sampel | Data untuk evaluasi model |

**Rumus**:
\[
N_{train} = N_{total} \times 0.8
\]
\[
N_{test} = N_{total} \times 0.2
\]

---

## Evaluasi Model

### Metrik Evaluasi

Sistem menggunakan beberapa metrik untuk mengevaluasi performa model:

#### 1. Accuracy (Akurasi)

Proporsi prediksi yang benar:

\[
\text{Accuracy} = \frac{\text{TP + TN}}{\text{TP + TN + FP + FN}} = \frac{\text{Correct Predictions}}{\text{Total Predictions}}
\]

Dimana:
- **TP** (True Positive) = Prediksi positif yang benar
- **TN** (True Negative) = Prediksi negatif yang benar
- **FP** (False Positive) = Prediksi positif yang salah
- **FN** (False Negative) = Prediksi negatif yang salah

**Untuk Multi-class Classification**:
\[
\text{Accuracy} = \frac{1}{n} \sum_{i=1}^{n} \mathbb{1}(\hat{y}_i = y_i)
\]

Dimana \( \mathbb{1} \) adalah indicator function (1 jika benar, 0 jika salah).

#### 2. Precision (Presisi)

Proporsi prediksi positif yang benar:

\[
\text{Precision} = \frac{\text{TP}}{\text{TP + FP}}
\]

**Untuk Multi-class** (per kelas):
\[
\text{Precision}_i = \frac{TP_i}{TP_i + FP_i}
\]

#### 3. Recall (Sensitivitas)

Proporsi kasus positif yang terdeteksi dengan benar:

\[
\text{Recall} = \frac{\text{TP}}{\text{TP + FN}}
\]

**Untuk Multi-class** (per kelas):
\[
\text{Recall}_i = \frac{TP_i}{TP_i + FN_i}
\]

#### 4. F1-Score

Harmonic mean dari Precision dan Recall:

\[
F1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} = \frac{2 \times TP}{2 \times TP + FP + FN}
\]

**Untuk Multi-class** (per kelas):
\[
F1_i = 2 \times \frac{\text{Precision}_i \times \text{Recall}_i}{\text{Precision}_i + \text{Recall}_i}
\]

#### 5. Macro Average F1-Score

Rata-rata F1-Score dari semua kelas (tanpa mempertimbangkan jumlah sampel):

\[
F1_{\text{macro}} = \frac{1}{c} \sum_{i=1}^{c} F1_i
\]

Dimana \( c \) adalah jumlah kelas (4 dalam kasus ini).

**Alasan Menggunakan Macro Average**: Memberikan bobot yang sama untuk setiap kelas, penting untuk imbalanced dataset.

### Pemilihan Model Terbaik

Model terbaik dipilih berdasarkan **F1-Score Macro Average** tertinggi:

```python
best_model = max(results, key=lambda x: x["F1-Score (Macro Avg)"])
```

**Alasan**: F1-Score Macro Average memberikan evaluasi yang lebih adil untuk semua kelas dibandingkan accuracy saja, terutama untuk imbalanced data.

### Confusion Matrix

Confusion matrix menunjukkan distribusi prediksi vs label aktual:

```
                Prediksi
              Aman  Judol  Porn  Hacked
Aktual  Aman   50    2     1      0
        Judol   3    45    2      1
        Porn    1    1    20      0
        Hacked  0    1     0      15
```

Dari confusion matrix dapat dihitung:
- **TP** untuk setiap kelas (diagonal)
- **FP** untuk setiap kelas (kolom - diagonal)
- **FN** untuk setiap kelas (baris - diagonal)

---

## Alur Kerja Training

### Diagram Alur

```
1. Load Dataset (CSV)
   ↓
2. Preprocessing
   - Gabungkan title + description
   - Filter data kosong
   - Stemming Bahasa Indonesia
   ↓
3. Label Mapping
   - Convert label_status ke numerik (0, 1, 2, 3)
   ↓
4. Train-Test Split (80:20)
   - Stratified sampling
   ↓
5. Feature Extraction (TF-IDF)
   - Transform teks ke vektor numerik
   - max_features=10000
   - ngram_range=(1, 2)
   ↓
6. Training 3 Model
   ├─ SVM (Linear)
   ├─ Naive Bayes
   └─ Random Forest
   ↓
7. Evaluasi Model
   - Accuracy
   - Precision, Recall, F1-Score (per kelas)
   - F1-Score Macro Average
   ↓
8. Pilih Model Terbaik
   - Berdasarkan F1-Score Macro Average
   ↓
9. Simpan Model
   - joblib.dump()
   - Include: model, label_mapping, version
```

### Pseudocode

```python
# 1. Load Dataset
df = pd.read_csv('labeling_judol_dan_aman-26.csv')

# 2. Preprocessing
df['text'] = df['title'] + ' ' + df['description']
df = df[df['text'].str.strip() != '']
df['text_stemmed'] = df['text'].apply(stem_text)

# 3. Label Mapping
label_mapping = {'aman': 0, 'hack judol': 1, 'pornografi': 2, 'hacked': 3}
df['label'] = df['label_status'].map(label_mapping)

# 4. Train-Test Split
X = df['text_stemmed']
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, stratify=y, test_size=0.2, random_state=42
)

# 5. Training Models
models = {
    "SVM": SVC(kernel='linear', C=1.0, class_weight='balanced'),
    "Naive Bayes": MultinomialNB(),
    "Random Forest": RandomForestClassifier(n_estimators=100, class_weight='balanced')
}

results = []
for name, clf in models.items():
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
        ('clf', clf)
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    
    # Evaluasi
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    f1_macro = report['macro avg']['f1-score']
    
    results.append({
        'Model': name,
        'Accuracy': acc,
        'F1-Score (Macro)': f1_macro,
        'Pipeline': pipeline
    })

# 6. Pilih Model Terbaik
best_model = max(results, key=lambda x: x['F1-Score (Macro)'])

# 7. Simpan Model
joblib.dump({
    'model': best_model['Pipeline'],
    'label_mapping': label_mapping,
    'version': 'django_best_' + best_model['Model'].lower()
}, 'seo_poisoning_best_model.joblib')
```

---

## Rumus Matematika Lengkap

### 1. TF-IDF Vectorization

\[
\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)
\]

\[
\text{TF}(t, d) = \frac{f_{t,d}}{\sum_{t' \in d} f_{t',d}}
\]

\[
\text{IDF}(t, D) = \log \frac{N}{|d \in D : t \in d|}
\]

### 2. SVM (Linear Kernel)

**Objective Function**:
\[
\min_{w,b,\xi} \frac{1}{2}||w||^2 + C \sum_{i=1}^{n} \xi_i
\]

**Constraint**:
\[
y_i(w \cdot x_i + b) \geq 1 - \xi_i, \quad \xi_i \geq 0
\]

**Decision Function**:
\[
f(x) = \text{sign}(w \cdot x + b)
\]

### 3. Naive Bayes

**Posterior Probability**:
\[
P(y|x) = \frac{P(y) \prod_{i=1}^{n} P(x_i|y)}{P(x)}
\]

**Likelihood (Multinomial)**:
\[
P(x_i|y) = \frac{N_{yi} + \alpha}{N_y + \alpha \times |V|}
\]

**Prediction**:
\[
\hat{y} = \arg\max_{y} P(y) \prod_{i=1}^{n} P(x_i|y)
\]

### 4. Random Forest

**Entropy**:
\[
H(S) = -\sum_{i=1}^{c} p_i \log_2(p_i)
\]

**Information Gain**:
\[
IG(S, A) = H(S) - \sum_{v \in Values(A)} \frac{|S_v|}{|S|} H(S_v)
\]

**Final Prediction**:
\[
\hat{y} = \text{mode}(\{\hat{y}_1, \hat{y}_2, ..., \hat{y}_{100}\})
\]

### 5. Evaluasi Metrik

**Accuracy**:
\[
\text{Accuracy} = \frac{1}{n} \sum_{i=1}^{n} \mathbb{1}(\hat{y}_i = y_i)
\]

**Precision**:
\[
\text{Precision}_i = \frac{TP_i}{TP_i + FP_i}
\]

**Recall**:
\[
\text{Recall}_i = \frac{TP_i}{TP_i + FN_i}
\]

**F1-Score**:
\[
F1_i = 2 \times \frac{\text{Precision}_i \times \text{Recall}_i}{\text{Precision}_i + \text{Recall}_i}
\]

**F1-Score Macro Average**:
\[
F1_{\text{macro}} = \frac{1}{c} \sum_{i=1}^{c} F1_i
\]

---

## Kesimpulan

Sistem pelatihan model menggunakan pendekatan **supervised learning** dengan:

1. **Preprocessing**: Stemming Bahasa Indonesia untuk normalisasi teks
2. **Feature Extraction**: TF-IDF dengan 10,000 fitur dan n-gram (1,2)
3. **Algoritma**: Perbandingan 3 algoritma (SVM, Naive Bayes, Random Forest)
4. **Data Split**: 80% training, 20% testing dengan stratified sampling
5. **Evaluasi**: F1-Score Macro Average sebagai metrik utama
6. **Model Selection**: Model terbaik disimpan untuk digunakan dalam sistem deteksi

**Keunggulan Pendekatan Ini**:
- Robust terhadap imbalanced data (dengan class_weight='balanced')
- Menggunakan n-gram untuk menangkap konteks frasa
- Evaluasi yang adil untuk semua kelas (macro average)
- Reproducible (dengan random_state=42)

---

## Referensi

1. Scikit-learn Documentation: https://scikit-learn.org/
2. TF-IDF: https://en.wikipedia.org/wiki/Tf%E2%80%93idf
3. Support Vector Machine: https://en.wikipedia.org/wiki/Support_vector_machine
4. Naive Bayes: https://en.wikipedia.org/wiki/Naive_Bayes_classifier
5. Random Forest: https://en.wikipedia.org/wiki/Random_forest
6. Sastrawi (Indonesian Stemmer): https://github.com/sastrawi/sastrawi

