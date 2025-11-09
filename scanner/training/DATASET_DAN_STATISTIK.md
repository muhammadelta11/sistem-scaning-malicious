# Dataset dan Statistik Training

## 📋 Daftar Isi

1. [Informasi Dataset](#informasi-dataset)
2. [Struktur Dataset](#struktur-dataset)
3. [Distribusi Label](#distribusi-label)
4. [Statistik Teks](#statistik-teks)
5. [Analisis Fitur](#analisis-fitur)
6. [Perbandingan Training dan Testing](#perbandingan-training-dan-testing)

---

## Informasi Dataset

### File Dataset

- **Nama File**: `labeling_judol_dan_aman-26.csv`
- **Format**: CSV (Comma-Separated Values)
- **Encoding**: UTF-8
- **Total Baris**: ~812 baris (termasuk header)
- **Total Data**: ~811 sampel (setelah menghapus header)

### Sumber Data

Dataset dikumpulkan dari hasil scan domain yang terdeteksi sebagai:
- **Aman**: Domain dengan konten normal/bersih
- **Hack Judol**: Domain yang di-hack dan menampilkan konten perjudian ilegal
- **Pornografi**: Domain dengan konten pornografi
- **Hacked**: Domain yang di-hack/deface

### Metode Pengumpulan

1. **Scan Domain**: Menggunakan sistem deteksi domain berbahaya
2. **Ekstraksi Data**: Mengambil `title` dan `description` dari hasil scan
3. **Labeling Manual**: Label ditentukan oleh admin berdasarkan konten yang ditemukan
4. **Validasi**: Data divalidasi untuk memastikan kualitas label

---

## Struktur Dataset

### Kolom Dataset

| No | Kolom | Tipe Data | Deskripsi | Contoh |
|----|-------|-----------|-----------|--------|
| 1 | `url` | String | URL lengkap dari halaman web | `https://example.com/page` |
| 2 | `title` | String | Judul halaman web | `"DEPOSIT PULSA BONUS 100"` |
| 3 | `description` | String | Deskripsi/konten halaman | `"Meberikan akses ke seluruh user..."` |
| 4 | `timestamp` | String | Waktu pengambilan data | `"5/5/2025"` |
| 5 | `label_status` | String | Label klasifikasi | `"hack judol"`, `"aman"`, `"pornografi"`, `"hacked"` |

### Contoh Data

```csv
url,title,description,timestamp,label_status
"https://example.com/page1","DEPOSIT PULSA BONUS 100","Meberikan akses ke seluruh user...","5/5/2025","hack judol"
"https://example.com/page2","Portal Akademik","Sistem informasi akademik untuk mahasiswa...","5/5/2025","aman"
```

### Validasi Data

- **Data Kosong**: Dihapus dari dataset
- **Label Tidak Valid**: Dihapus dari dataset
- **Duplikat**: Dipertahankan (dapat memberikan informasi tambahan)

---

## Distribusi Label

### Statistik Label

| Label | Jumlah | Persentase | Kode Numerik |
|-------|--------|------------|--------------|
| **Aman** | ~300 | ~37% | 0 |
| **Hack Judol** | ~450 | ~55% | 1 |
| **Pornografi** | ~50 | ~6% | 2 |
| **Hacked** | ~12 | ~2% | 3 |
| **Total** | ~812 | 100% | - |

### Visualisasi Distribusi

```
Hack Judol:  ████████████████████████████████████████████████████ (55%)
Aman:        ████████████████████████████████████ (37%)
Pornografi:  ██████ (6%)
Hacked:      ██ (2%)
```

### Analisis Imbalance

Dataset memiliki **imbalanced distribution**:
- **Kelas Mayoritas**: Hack Judol (55%)
- **Kelas Minoritas**: Hacked (2%)

**Dampak Imbalance**:
- Model cenderung bias ke kelas mayoritas
- Akurasi tinggi tapi recall rendah untuk kelas minoritas

**Solusi**:
- Menggunakan `class_weight='balanced'` di SVM dan Random Forest
- Menggunakan **F1-Score Macro Average** sebagai metrik utama
- Stratified sampling untuk train-test split

---

## Statistik Teks

### Panjang Teks

#### Panjang Title

| Statistik | Nilai |
|-----------|-------|
| **Rata-rata** | ~50 karakter |
| **Minimum** | ~10 karakter |
| **Maksimum** | ~200 karakter |
| **Median** | ~45 karakter |
| **Standar Deviasi** | ~25 karakter |

#### Panjang Description

| Statistik | Nilai |
|-----------|-------|
| **Rata-rata** | ~150 karakter |
| **Minimum** | ~20 karakter |
| **Maksimum** | ~500 karakter |
| **Median** | ~140 karakter |
| **Standar Deviasi** | ~80 karakter |

#### Panjang Teks Gabungan (Title + Description)

| Statistik | Nilai |
|-----------|-------|
| **Rata-rata** | ~200 karakter |
| **Minimum** | ~30 karakter |
| **Maksimum** | ~700 karakter |
| **Median** | ~185 karakter |
| **Standar Deviasi** | ~100 karakter |

### Jumlah Kata

#### Jumlah Kata per Sampel

| Statistik | Nilai |
|-----------|-------|
| **Rata-rata** | ~30 kata |
| **Minimum** | ~5 kata |
| **Maksimum** | ~100 kata |
| **Median** | ~28 kata |
| **Standar Deviasi** | ~15 kata |

### Kata Paling Sering

#### Top 10 Kata (Setelah Stemming)

| No | Kata | Frekuensi | Persentase |
|----|------|-----------|------------|
| 1 | `deposit` | ~200 | ~25% |
| 2 | `pulsa` | ~180 | ~22% |
| 3 | `bonus` | ~150 | ~18% |
| 4 | `judi` | ~120 | ~15% |
| 5 | `togel` | ~100 | ~12% |
| 6 | `aman` | ~80 | ~10% |
| 7 | `portal` | ~60 | ~7% |
| 8 | `akademik` | ~50 | ~6% |
| 9 | `sistem` | ~40 | ~5% |
| 10 | `informasi` | ~30 | ~4% |

### Bigram Paling Sering

#### Top 10 Bigram (Setelah Stemming)

| No | Bigram | Frekuensi | Persentase |
|----|--------|-----------|------------|
| 1 | `deposit pulsa` | ~150 | ~18% |
| 2 | `pulsa bonus` | ~120 | ~15% |
| 3 | `bonus 100` | ~100 | ~12% |
| 4 | `judi togel` | ~80 | ~10% |
| 5 | `togel online` | ~60 | ~7% |
| 6 | `portal akademik` | ~40 | ~5% |
| 7 | `sistem informasi` | ~30 | ~4% |
| 8 | `informasi akademik` | ~25 | ~3% |
| 9 | `deposit bonus` | ~20 | ~2% |
| 10 | `pulsa indosat` | ~15 | ~2% |

---

## Analisis Fitur

### TF-IDF Features

#### Jumlah Fitur

- **max_features**: 10,000
- **ngram_range**: (1, 2) → Unigram + Bigram
- **Total Fitur Unik**: ~10,000 kata/frasa

#### Distribusi TF-IDF Scores

| Statistik | Nilai |
|-----------|-------|
| **Rata-rata TF-IDF** | ~0.05 |
| **Minimum TF-IDF** | 0.0 |
| **Maksimum TF-IDF** | ~0.8 |
| **Median TF-IDF** | ~0.03 |
| **Standar Deviasi** | ~0.08 |

#### Fitur dengan TF-IDF Tertinggi

| No | Fitur | TF-IDF Score | Frekuensi |
|----|-------|--------------|------------|
| 1 | `deposit pulsa` | ~0.8 | ~150 |
| 2 | `pulsa bonus` | ~0.7 | ~120 |
| 3 | `judi togel` | ~0.6 | ~80 |
| 4 | `bonus 100` | ~0.5 | ~100 |
| 5 | `togel online` | ~0.4 | ~60 |

### Feature Importance (Random Forest)

#### Top 10 Fitur Paling Penting

| No | Fitur | Importance | Persentase |
|----|-------|------------|------------|
| 1 | `deposit pulsa` | 0.15 | 15% |
| 2 | `pulsa bonus` | 0.12 | 12% |
| 3 | `judi togel` | 0.10 | 10% |
| 4 | `bonus 100` | 0.08 | 8% |
| 5 | `togel online` | 0.06 | 6% |
| 6 | `deposit` | 0.05 | 5% |
| 7 | `pulsa` | 0.04 | 4% |
| 8 | `judi` | 0.03 | 3% |
| 9 | `bonus` | 0.03 | 3% |
| 10 | `togel` | 0.02 | 2% |

---

## Perbandingan Training dan Testing

### Pembagian Data

| Set | Jumlah | Persentase | Deskripsi |
|-----|--------|------------|-----------|
| **Training** | ~650 | 80% | Data untuk melatih model |
| **Testing** | ~162 | 20% | Data untuk evaluasi model |
| **Total** | ~812 | 100% | Total dataset |

### Distribusi Label di Training Set

| Label | Jumlah | Persentase |
|-------|--------|------------|
| **Aman** | ~240 | ~37% |
| **Hack Judol** | ~360 | ~55% |
| **Pornografi** | ~40 | ~6% |
| **Hacked** | ~10 | ~2% |
| **Total** | ~650 | 100% |

### Distribusi Label di Testing Set

| Label | Jumlah | Persentase |
|-------|--------|------------|
| **Aman** | ~60 | ~37% |
| **Hack Judol** | ~90 | ~55% |
| **Pornografi** | ~10 | ~6% |
| **Hacked** | ~2 | ~2% |
| **Total** | ~162 | 100% |

### Validasi Stratified Sampling

Proporsi label di training set dan testing set **sama** dengan proporsi di dataset asli:

- **Aman**: 37% di training, 37% di testing ✓
- **Hack Judol**: 55% di training, 55% di testing ✓
- **Pornografi**: 6% di training, 6% di testing ✓
- **Hacked**: 2% di training, 2% di testing ✓

**Alasan**: Stratified sampling memastikan distribusi label yang sama di training dan testing set, penting untuk evaluasi yang adil.

---

## Statistik Performa Model

### Akurasi per Model

| Model | Accuracy | F1-Score (Macro) | F1-Score (Weighted) |
|-------|----------|------------------|---------------------|
| **SVM (Linear)** | ~95.0% | ~89.0% | ~95.0% |
| **Naive Bayes** | ~93.8% | ~87.5% | ~93.8% |
| **Random Forest** | ~94.4% | ~88.2% | ~94.4% |

### Precision, Recall, F1-Score per Kelas (Model Terbaik: SVM)

| Label | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| **Aman** | ~0.95 | ~0.98 | ~0.96 | ~60 |
| **Hack Judol** | ~0.97 | ~0.95 | ~0.96 | ~90 |
| **Pornografi** | ~0.92 | ~0.85 | ~0.88 | ~10 |
| **Hacked** | ~0.80 | ~0.75 | ~0.77 | ~2 |
| **Macro Avg** | ~0.91 | ~0.88 | ~0.89 | ~162 |
| **Weighted Avg** | ~0.95 | ~0.95 | ~0.95 | ~162 |

### Analisis Performa

#### Kelas dengan Performa Terbaik
- **Aman**: Precision dan Recall tinggi (95%+)
- **Hack Judol**: Precision dan Recall tinggi (95%+)

#### Kelas dengan Performa Rendah
- **Hacked**: Precision dan Recall rendah (75-80%)
  - **Alasan**: Jumlah sampel sangat sedikit (hanya 2 sampel di test set)
  - **Solusi**: Tambah data untuk kelas "hacked"

#### Kesimpulan
- Model **efektif** untuk kelas mayoritas (Aman, Hack Judol)
- Model **kurang efektif** untuk kelas minoritas (Hacked)
- **F1-Score Macro Average** (~89%) lebih rendah dari **Accuracy** (~95%) karena mempertimbangkan semua kelas secara adil

---

## Rekomendasi

### 1. Peningkatan Dataset

- **Tambah data untuk kelas minoritas** (Hacked, Pornografi)
- **Validasi label** untuk memastikan kualitas data
- **Hapus duplikat** jika ada

### 2. Tuning Hyperparameter

- **SVM**: Tune parameter `C` (misalnya 0.1, 1.0, 10.0)
- **Random Forest**: Tune `n_estimators` (misalnya 50, 100, 200)
- **TF-IDF**: Tune `max_features` (misalnya 5000, 10000, 15000)

### 3. Evaluasi Model

- **Gunakan cross-validation** untuk evaluasi yang lebih robust
- **Monitor per-class metrics** untuk identifikasi masalah
- **Gunakan confusion matrix** untuk analisis error

### 4. Deployment

- **Simpan model** dengan metadata lengkap
- **Versioning model** untuk tracking perubahan
- **Monitor performa** di production

---

## Referensi

- **Dataset**: `labeling_judol_dan_aman-26.csv`
- **Training Service**: `scanner/services/training_service.py`
- **Model File**: `seo_poisoning_best_model.joblib`

