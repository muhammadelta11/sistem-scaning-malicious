# Index Dokumentasi Training Model

## 📚 Daftar Dokumentasi

### 1. [README.md](README.md) - Dokumentasi Teknis Lengkap
**Isi**: Dokumentasi komprehensif tentang pelatihan model machine learning

**Topik yang dibahas**:
- ✅ Overview sistem training
- ✅ Dataset dan variabel yang digunakan
- ✅ Preprocessing data (stemming, filtering)
- ✅ Feature Extraction (TF-IDF) dengan rumus lengkap
- ✅ Algoritma Machine Learning (SVM, Naive Bayes, Random Forest) dengan rumus matematika
- ✅ Pembagian data training dan testing (80:20)
- ✅ Evaluasi model (Accuracy, Precision, Recall, F1-Score)
- ✅ Alur kerja training
- ✅ Rumus matematika lengkap untuk semua komponen

**Untuk**: Dosen, peneliti, developer yang ingin memahami teori dan konsep training

---

### 2. [IMPLEMENTASI.md](IMPLEMENTASI.md) - Implementasi Kode
**Isi**: Implementasi praktis dan contoh kode untuk training model

**Topik yang dibahas**:
- ✅ Struktur kode dan dependencies
- ✅ Implementasi preprocessing (load dataset, gabungkan teks, stemming)
- ✅ Implementasi TF-IDF vectorization
- ✅ Implementasi algoritma (SVM, Naive Bayes, Random Forest)
- ✅ Implementasi evaluasi (classification report, confusion matrix)
- ✅ Contoh kode lengkap untuk training service
- ✅ Tips dan best practices
- ✅ Troubleshooting common issues

**Untuk**: Developer yang ingin mengimplementasikan atau memodifikasi training

---

### 3. [DATASET_DAN_STATISTIK.md](DATASET_DAN_STATISTIK.md) - Dataset dan Statistik
**Isi**: Informasi detail tentang dataset dan statistik training

**Topik yang dibahas**:
- ✅ Informasi dataset (file, format, sumber)
- ✅ Struktur dataset (kolom, contoh data)
- ✅ Distribusi label (imbalanced data analysis)
- ✅ Statistik teks (panjang, jumlah kata)
- ✅ Analisis fitur (TF-IDF features, feature importance)
- ✅ Perbandingan training dan testing set
- ✅ Statistik performa model
- ✅ Rekomendasi untuk peningkatan

**Untuk**: Dosen, peneliti yang ingin memahami karakteristik dataset dan hasil training

---

## 🎯 Panduan Penggunaan

### Untuk Presentasi ke Dosen

1. **Mulai dengan [README.md](README.md)**:
   - Jelaskan overview sistem
   - Tunjukkan rumus matematika (TF-IDF, SVM, Naive Bayes, Random Forest)
   - Jelaskan variabel yang digunakan
   - Tunjukkan perbandingan training dan testing (80:20)

2. **Lanjut dengan [DATASET_DAN_STATISTIK.md](DATASET_DAN_STATISTIK.md)**:
   - Tunjukkan struktur dataset
   - Jelaskan distribusi label (imbalanced data)
   - Tunjukkan statistik performa model
   - Diskusikan rekomendasi untuk peningkatan

3. **Jika ditanya implementasi, lihat [IMPLEMENTASI.md](IMPLEMENTASI.md)**:
   - Tunjukkan contoh kode
   - Jelaskan alur implementasi
   - Diskusikan best practices

### Untuk Development

1. **Baca [README.md](README.md)** untuk memahami konsep
2. **Lihat [IMPLEMENTASI.md](IMPLEMENTASI.md)** untuk implementasi
3. **Cek [DATASET_DAN_STATISTIK.md](DATASET_DAN_STATISTIK.md)** untuk memahami dataset

---

## 📊 Quick Reference

### Rumus Penting

#### TF-IDF
\[
\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)
\]

#### F1-Score
\[
F1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}
\]

#### Train-Test Split
- **Training**: 80% dari total data
- **Testing**: 20% dari total data
- **Stratified**: Mempertahankan proporsi kelas

### Variabel Penting

| Variabel | Deskripsi |
|----------|-----------|
| `X` | Features (teks setelah preprocessing) |
| `y` | Labels (0, 1, 2, 3) |
| `X_train`, `y_train` | Data training (80%) |
| `X_test`, `y_test` | Data testing (20%) |
| `label_mapping` | Mapping label string ke numerik |

### Algoritma yang Dibandingkan

1. **SVM (Linear)**: `SVC(kernel='linear', C=1.0, class_weight='balanced')`
2. **Naive Bayes**: `MultinomialNB()`
3. **Random Forest**: `RandomForestClassifier(n_estimators=100, class_weight='balanced')`

### Metrik Evaluasi

- **Accuracy**: Proporsi prediksi yang benar
- **Precision**: Proporsi prediksi positif yang benar
- **Recall**: Proporsi kasus positif yang terdeteksi
- **F1-Score**: Harmonic mean dari Precision dan Recall
- **F1-Score Macro Average**: Rata-rata F1-Score dari semua kelas

---

## 🔍 Pencarian Cepat

### Cari tentang...

- **Rumus matematika** → [README.md](README.md) bagian "Rumus Matematika"
- **Variabel dataset** → [README.md](README.md) bagian "Dataset dan Variabel"
- **Cara kerja TF-IDF** → [README.md](README.md) bagian "Feature Extraction (TF-IDF)"
- **Algoritma SVM** → [README.md](README.md) bagian "Algoritma Machine Learning" → "1. Support Vector Machine (SVM)"
- **Implementasi kode** → [IMPLEMENTASI.md](IMPLEMENTASI.md)
- **Statistik dataset** → [DATASET_DAN_STATISTIK.md](DATASET_DAN_STATISTIK.md)
- **Perbandingan training/testing** → [README.md](README.md) bagian "Pembagian Data Training dan Testing"
- **Evaluasi model** → [README.md](README.md) bagian "Evaluasi Model"

---

## 📝 Catatan Penting

1. **Dataset**: `labeling_judol_dan_aman-26.csv` (~812 baris)
2. **Preprocessing**: Stemming Bahasa Indonesia menggunakan Sastrawi
3. **Feature Extraction**: TF-IDF dengan 10,000 fitur, n-gram (1,2)
4. **Train-Test Split**: 80% training, 20% testing (stratified)
5. **Model Selection**: Berdasarkan F1-Score Macro Average
6. **Best Model**: SVM (Linear) dengan akurasi ~95%

---

## 🔗 File Terkait

- **Training Service**: `scanner/services/training_service.py`
- **Training View**: `scanner/views.py` (function `training_view`)
- **Training Template**: `scanner/templates/scanner/training.html`
- **Dataset**: `labeling_judol_dan_aman-26.csv`
- **Model File**: `seo_poisoning_best_model.joblib`

---

## 📞 Kontak

Untuk pertanyaan atau saran tentang dokumentasi ini, silakan hubungi developer atau buat issue di repository.

---

**Last Updated**: November 2025

