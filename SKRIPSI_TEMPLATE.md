# TEMPLATE BAGIAN SKRIPSI

## 1. ABSTRAK (Versi Lengkap)

---

**Sistem Deteksi Konten Malicious pada Domain Pendidikan Berbasis Machine Learning dengan Arsitektur REST API untuk Klien Multi-Platform**

Oleh: [Nama Anda]

Konten malicious pada domain pendidikan merupakan ancaman cyber security yang semakin meningkat di Indonesia. Berdasarkan data dari berbagai sumber, sebagian besar serangan konten malicious terjadi pada domain pendidikan (.ac.id), dimana domain-domain kampus sering menjadi target karena memiliki otoritas tinggi dan aksesibilitas yang luas. Banyak domain pendidikan yang terindikasi memiliki konten ilegal seperti judi online, pornografi, narkoba, dan phishing yang dapat muncul dalam hasil pencarian mesin pencari dan merugikan pengguna. Penelitian ini bertujuan untuk mengembangkan sistem deteksi konten malicious pada domain pendidikan berbasis machine learning dengan arsitektur REST API untuk klien multi-platform yang dapat membantu pengguna mengidentifikasi domain-domain pendidikan yang terindikasi konten malicious. Meskipun fokus penelitian pada domain pendidikan, sistem tetap dapat melakukan scanning pada domain lain untuk keperluan perbandingan dan validasi.

Sistem yang dikembangkan terdiri dari tiga komponen utama. Pertama, backend API menggunakan Django REST Framework yang menyediakan endpoint untuk melakukan scanning domain, manajemen user, dan integrasi dengan model machine learning. Kedua, model machine learning yang menggunakan algoritma klasifikasi untuk mengidentifikasi konten malicious, dimana dilakukan evaluasi terhadap tiga algoritma yaitu Support Vector Machine (SVM), Naive Bayes, dan Random Forest. Ketiga, aplikasi mobile client menggunakan Flutter untuk platform Android yang memungkinkan pengguna melakukan scanning domain secara real-time melalui antarmuka yang user-friendly.

Metodologi pengembangan sistem menggunakan pendekatan waterfall dengan tahapan analisis kebutuhan, perancangan sistem, implementasi, dan pengujian. Dataset yang digunakan untuk training model machine learning terdiri dari [X] sample domain aman dan [Y] sample domain yang terindikasi konten malicious. Preprocessing data dilakukan dengan ekstraksi fitur menggunakan TF-IDF (Term Frequency-Inverse Document Frequency) dan stemming bahasa Indonesia menggunakan library Sastrawi. Model dilatih menggunakan stratified train-test split dengan rasio 80:20.

Hasil evaluasi model menunjukkan bahwa Random Forest mencapai performa terbaik dengan akurasi sebesar [XX]%, precision [XX]%, recall [XX]%, dan F1-Score [XX]%. SVM menunjukkan akurasi [XX]% dengan F1-Score [XX]%, sedangkan Naive Bayes mencapai akurasi [XX]% dengan F1-Score [XX]%. Berdasarkan hasil evaluasi, Random Forest dipilih sebagai model final untuk sistem.

Sistem telah berhasil mengintegrasikan fitur-fitur deteksi komprehensif termasuk real-time verification menggunakan Selenium untuk validasi konten, graph analysis untuk menemukan orphan pages dan isolated clusters, deep content detection untuk konten tersembunyi dan halaman yang tidak terindex, serta subdomain enumeration menggunakan DNS-based discovery. Backend API diimplementasikan dengan menggunakan Django REST Framework dan terintegrasi dengan MySQL untuk penyimpanan data serta Redis untuk caching yang dapat mengurangi 95% penggunaan quota SerpAPI.

Pengujian fungsional menunjukkan semua fitur berjalan dengan baik. Pengujian API endpoints menghasilkan response time rata-rata [X]ms untuk endpoint authentication dan [Y]ms untuk endpoint scanning. Pengujian integrasi antara mobile application dan backend API menunjukkan aplikasi dapat terhubung dengan baik melalui protokol HTTPS dan semua fitur berfungsi sesuai dengan yang diharapkan. Pengujian User Acceptance Testing (UAT) dengan [N] responden menunjukkan tingkat kepuasan sebesar [X]% dengan kategori "Sangat Puas" dan "Puas".

Sistem yang dikembangkan telah berhasil memenuhi tujuan penelitian dan dapat digunakan sebagai tools untuk membantu mengidentifikasi domain-domain yang terindikasi konten malicious. Sistem ini juga dapat dikembangkan lebih lanjut dengan penambahan algoritma deep learning, peningkatan dataset training, serta pengembangan versi iOS untuk memperluas jangkauan pengguna.

**Kata Kunci:** Konten Malicious, Machine Learning, REST API, Django REST Framework, Flutter, Multi-Platform Application, Cyber Security, Domain Scanning

---

## 2. BAB I - PENDAHULUAN

### 1.1 Latar Belakang Masalah

Di era digital yang semakin berkembang, penggunaan internet dan domain website telah menjadi bagian penting dalam kehidupan sehari-hari. Namun, berkembangnya teknologi juga membawa ancaman baru dalam bentuk konten malicious pada domain. Banyak domain yang terindikasi memiliki konten ilegal seperti judi online, pornografi, narkoba, dan phishing yang dapat muncul dalam hasil pencarian mesin pencari dan merugikan pengguna.

Konten malicious pada domain merupakan ancaman cyber security yang semakin meningkat. Konten ini dapat berupa situs phishing, malware distribution, atau konten ilegal seperti narkoba dan perjudian yang sengaja disematkan pada domain-domain tertentu. Masalah ini menjadi semakin serius karena pengguna cenderung mempercayai hasil pencarian dan mengklik link tanpa verifikasi lebih lanjut. Institusi pendidikan, organisasi pemerintah, dan perusahaan swasta sering menjadi target karena memiliki domain dengan otoritas tinggi yang dapat dimanfaatkan untuk menyembunyikan konten malicious.

Berdasarkan data dari [sumber penelitian], jumlah domain yang terindikasi konten malicious meningkat [X]% dalam [periode], dengan dampak kerugian ekonomi mencapai [angka]. Deteksi manual terhadap konten malicious pada domain memerlukan waktu yang lama dan kurang efisien. Oleh karena itu, diperlukan sistem otomatis yang dapat mendeteksi domain-domain yang terindikasi konten malicious secara real-time dengan akurasi tinggi. Machine learning telah terbukti efektif dalam klasifikasi teks dan deteksi konten malicious. Dengan kombinasi REST API architecture untuk skalabilitas dan aplikasi mobile untuk aksesibilitas, sistem dapat memberikan solusi yang komprehensif.

### 1.2 Rumusan Masalah

Berdasarkan latar belakang yang telah diuraikan, rumusan masalah dalam penelitian ini adalah:

1. Bagaimana mengembangkan sistem deteksi konten malicious pada domain berbasis machine learning yang dapat mengidentifikasi domain-domain yang terindikasi konten malicious dengan akurasi tinggi?
2. Bagaimana merancang arsitektur REST API yang dapat mendukung aplikasi mobile multi-platform dengan performa optimal?
3. Bagaimana mengintegrasikan model machine learning ke dalam sistem backend API untuk deteksi real-time?
4. Bagaimana mengembangkan aplikasi mobile yang user-friendly dan dapat terhubung dengan backend API melalui protokol HTTPS?
5. Bagaimana mengevaluasi performa sistem secara keseluruhan termasuk akurasi model machine learning dan kepuasan pengguna?

### 1.3 Batasan Masalah

Untuk menjaga fokus penelitian, penelitian ini dibatasi pada:

1. **Domain Target**: Sistem fokus pada deteksi konten malicious untuk domain-domain yang menggunakan bahasa Indonesia, khususnya domain edukasi (.ac.id) dan organisasi (.org, .or.id).

2. **Platform**: Aplikasi mobile dikembangkan untuk platform Android saja (iOS dapat dikembangkan di masa depan).

3. **Algoritma Machine Learning**: Evaluasi dibatasi pada tiga algoritma klasifikasi yaitu Support Vector Machine (SVM), Naive Bayes, dan Random Forest.

4. **Search Engine**: Sistem menggunakan Google Search sebagai primary source untuk scanning (dapat dikembangkan dengan Bing dan DuckDuckGo di masa depan).

5. **Konten Target**: Fokus pada deteksi konten ilegal seperti narkoba, perjudian, phishing, dan malware distribution.

6. **User Interface**: Aplikasi mobile menggunakan bahasa Indonesia sebagai bahasa utama.

### 1.4 Tujuan Penelitian

Tujuan penelitian ini adalah:

1. Mengembangkan sistem deteksi konten malicious pada domain berbasis machine learning dengan akurasi minimal [X]%.
2. Merancang dan mengimplementasikan REST API menggunakan Django REST Framework yang dapat mendukung aplikasi mobile multi-platform.
3. Membangun aplikasi mobile menggunakan Flutter yang dapat terhubung dengan backend API dan menyediakan antarmuka yang user-friendly.
4. Mengintegrasikan model machine learning ke dalam sistem untuk deteksi real-time.
5. Mengevaluasi performa sistem secara menyeluruh termasuk akurasi model, response time API, dan kepuasan pengguna.

### 1.5 Manfaat Penelitian

Penelitian ini diharapkan memberikan manfaat:

**1. Manfaat Teoritis:**
- Memberikan kontribusi dalam pengembangan sistem deteksi konten malicious pada domain menggunakan machine learning.
- Menambah literatur tentang integrasi machine learning dengan REST API untuk aplikasi mobile.
- Menyediakan baseline untuk penelitian selanjutnya dalam deteksi konten malicious.

**2. Manfaat Praktis:**
- Menyediakan tools yang dapat membantu institusi pendidikan, organisasi, dan perusahaan untuk mengidentifikasi domain yang terindikasi konten malicious.
- Mengurangi waktu deteksi manual dengan sistem otomatis.
- Memberikan solusi yang accessible melalui aplikasi mobile.

### 1.6 Sistematika Penulisan

Skripsi ini disusun dalam lima bab dengan sistematika sebagai berikut:

**BAB I PENDAHULUAN**
Berisi latar belakang masalah, rumusan masalah, batasan masalah, tujuan penelitian, manfaat penelitian, dan sistematika penulisan.

**BAB II TINJAUAN PUSTAKA**
Berisi teori-teori yang mendasari penelitian meliputi konten malicious pada domain, machine learning, REST API, mobile application development, dan penelitian terkait.

**BAB III METODOLOGI PENELITIAN**
Berisi metodologi pengembangan sistem, analisis kebutuhan, perancangan sistem, perancangan model machine learning, implementasi, dan pengujian.

**BAB IV HASIL DAN PEMBAHASAN**
Berisi hasil analisis kebutuhan, hasil perancangan sistem, hasil implementasi, hasil training dan evaluasi model, hasil pengujian, serta pembahasan hasil.

**BAB V KESIMPULAN DAN SARAN**
Berisi kesimpulan dari penelitian dan saran untuk pengembangan selanjutnya.

---

## 3. CONTOH TABEL PENGUJIAN

### Tabel 4.1: Hasil Pengujian Model Machine Learning

| Algoritma | Accuracy | Precision | Recall | F1-Score | Training Time (detik) |
|-----------|----------|-----------|--------|----------|----------------------|
| SVM | [XX]% | [XX]% | [XX]% | [XX]% | [X] |
| Naive Bayes | [XX]% | [XX]% | [XX]% | [XX]% | [X] |
| **Random Forest** | **[XX]%** | **[XX]%** | **[XX]%** | **[XX]%** | [X] |

**Keterangan:** Model dengan performa terbaik ditandai dengan **bold**

### Tabel 4.2: Classification Report Random Forest

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Aman | [X] | [Y] | [Z] | [N] |
| Malicious | [X] | [Y] | [Z] | [N] |
| Macro Avg | [X] | [Y] | [Z] | [N] |
| Weighted Avg | [X] | [Y] | [Z] | [N] |

### Tabel 4.3: Hasil Pengujian Fungsional Backend API

| No | Endpoint | Method | Test Case | Expected | Actual | Status |
|----|----------|--------|-----------|----------|--------|--------|
| 1 | `/api/auth/login/` | POST | Login valid | 200 OK | 200 OK | ✅ |
| 2 | `/api/auth/login/` | POST | Login invalid | 400 Bad Request | 400 Bad Request | ✅ |
| 3 | `/api/scans/` | POST | Create scan | 201 Created | 201 Created | ✅ |
| 4 | `/api/scans/` | GET | Get scan history | 200 OK | 200 OK | ✅ |
| 5 | `/api/scans/{id}/results/` | GET | Get scan results | 200 OK | 200 OK | ✅ |

### Tabel 4.4: Hasil Pengujian Fungsional Mobile Application

| No | Fitur | Test Case | Expected | Actual | Status |
|----|-------|-----------|----------|--------|--------|
| 1 | Login | Login dengan kredensial valid | Berhasil masuk | Berhasil masuk | ✅ |
| 2 | Dashboard | Tampil statistik | Data muncul | Data muncul | ✅ |
| 3 | Scan Domain | Scan domain valid | Scanning berhasil | Scanning berhasil | ✅ |
| 4 | History | Lihat history scan | Daftar muncul | Daftar muncul | ✅ |
| 5 | Results | Lihat detail hasil | Detail muncul | Detail muncul | ✅ |

### Tabel 4.5: Response Time API Endpoints

| Endpoint | Method | Min (ms) | Max (ms) | Avg (ms) |
|----------|--------|----------|----------|----------|
| `/api/auth/login/` | POST | [X] | [Y] | [Z] |
| `/api/scans/` | POST | [X] | [Y] | [Z] |
| `/api/scans/` | GET | [X] | [Y] | [Z] |
| `/api/scans/{id}/results/` | GET | [X] | [Y] | [Z] |

### Tabel 4.6: Hasil User Acceptance Testing (UAT)

| No | Aspek Evaluasi | Sangat Puas | Puas | Cukup | Tidak Puas | Rata-rata |
|----|----------------|-------------|------|-------|-----------|-----------|
| 1 | Kemudahan Penggunaan | [N] | [N] | [N] | [N] | [X] |
| 2 | Kecepatan Sistem | [N] | [N] | [N] | [N] | [X] |
| 3 | Keakuratan Hasil | [N] | [N] | [N] | [N] | [X] |
| 4 | Tampilan UI/UX | [N] | [N] | [N] | [N] | [X] |
| 5 | Fitur yang Tersedia | [N] | [N] | [N] | [N] | [X] |

---

## 4. CONTOH PENJELASAN IMPLEMENTASI

### 4.3.1 Setup Django Project dan REST Framework

Implementasi backend dimulai dengan setup Django project. Langkah-langkah yang dilakukan adalah:

1. **Installation Dependencies**
   ```bash
   pip install django djangorestframework django-cors-headers
   ```

2. **Project Structure**
   ```
   sistem_deteksi_malicious/
   ├── manage.py
   ├── sistem_deteksi_malicious/
   │   ├── settings.py
   │   ├── urls.py
   │   └── wsgi.py
   └── scanner/
       ├── models.py
       ├── serializers.py
       ├── views.py
       └── urls.py
   ```

3. **Configuration Settings**
   File `settings.py` dikonfigurasi dengan menambahkan aplikasi yang diperlukan dan mengatur CORS untuk mobile app.

4. **Model Definition**
   Model `ScanHistory` dan `User` didefinisikan untuk menyimpan data scan dan user authentication.

[Lanjutkan dengan penjelasan lebih detail...]

---

## 5. CONTOH DAFTAR PUSTAKA

### Format APA Style:

1. Author, A. A. (Tahun). *Judul Buku*. Penerbit.
   
2. Author, B. B., & Author, C. C. (Tahun). Judul artikel. *Nama Jurnal*, Volume(Nomor), Halaman.

3. Django Software Foundation. (2024). *Django REST Framework Documentation*. https://www.django-rest-framework.org/

4. Flutter Team. (2024). *Flutter Documentation*. https://flutter.dev/docs

5. Scikit-learn Developers. (2024). *scikit-learn User Guide*. https://scikit-learn.org/stable/user_guide.html

[Dan seterusnya...]

---

**Note:** 
- Isi semua placeholder [X], [Y], [N], dll dengan data aktual dari penelitian Anda
- Sesuaikan dengan format yang diminta kampus Anda (APA, Harvard, dll)
- Pastikan semua referensi valid dan dapat diakses
- Lakukan cross-check dengan pembimbing skripsi

