# BAB I PENDAHULUAN

## 1.1 Latar Belakang Masalah

Di era transformasi digital saat ini, internet telah menjadi bagian integral dalam kehidupan masyarakat Indonesia. Berdasarkan data dari Asosiasi Penyelenggara Jasa Internet Indonesia (APJII) tahun 2023, penetrasi internet di Indonesia mencapai 78,19% dari total populasi, dengan lebih dari 215 juta pengguna aktif yang mengakses berbagai layanan digital setiap harinya. Mesin pencari seperti Google menjadi gerbang utama bagi pengguna untuk menemukan informasi, dengan lebih dari 95% pengguna internet di Indonesia menggunakan Google sebagai mesin pencari utama mereka.

Namun, di balik kemudahan dan aksesibilitas informasi yang ditawarkan oleh internet, muncul ancaman cyber security yang semakin kompleks dan mengkhawatirkan. Salah satu ancaman yang berkembang pesat adalah munculnya konten malicious pada domain-domain yang seharusnya dapat dipercaya, terutama pada domain pendidikan (.ac.id). Konten malicious ini meliputi berbagai jenis konten ilegal seperti judi online, pornografi, perdagangan narkoba, phishing, dan malware distribution yang sengaja disematkan pada domain-domain tertentu.

Fenomena konten malicious pada domain pendidikan telah menjadi masalah serius di Indonesia. Berdasarkan data dari berbagai sumber dan observasi, sebagian besar serangan konten malicious terjadi pada domain pendidikan (.ac.id), dimana domain-domain kampus sering menjadi target utama karena memiliki otoritas tinggi di mesin pencari, aksesibilitas yang luas, dan kepercayaan tinggi dari pengguna internet. Data dari Kementerian Komunikasi dan Informatika (Kominfo) menunjukkan bahwa pada tahun 2023, terdapat lebih dari 1,2 juta website yang diblokir karena mengandung konten ilegal, dengan peningkatan sebesar 34% dari tahun sebelumnya. Dari jumlah tersebut, diperkirakan lebih dari 60% terjadi pada domain pendidikan, baik yang disematkan secara sengaja oleh pihak yang tidak bertanggung jawab maupun akibat peretasan (hacking) yang mengubah konten website resmi menjadi portal untuk konten ilegal.

Masalah ini menjadi semakin kompleks karena konten malicious seringkali tidak langsung terlihat pada halaman utama website. Penyerang menggunakan teknik-teknik canggih seperti hidden content (konten tersembunyi), orphan pages (halaman yang tidak terhubung dari halaman utama), subdomain terpisah, dan injeksi konten untuk menyembunyikan aktivitas ilegal mereka. Konten-konten ini dapat muncul dalam hasil pencarian mesin pencari ketika pengguna mencari informasi tertentu, membuat pengguna tidak sadar mengakses konten ilegal yang dapat merugikan mereka secara finansial maupun moral.

Dampak dari konten malicious pada domain pendidikan sangat luas dan merugikan berbagai pihak. Dari perspektif institusi pendidikan, keberadaan konten malicious pada domain kampus dapat merusak reputasi dan kredibilitas institusi secara signifikan, mengganggu proses pembelajaran, serta melanggar peraturan yang melarang konten ilegal. Hal ini dapat menyebabkan penurunan kepercayaan masyarakat terhadap institusi pendidikan dan berpotensi merugikan proses akademik. Pengguna internet yang tidak sengaja mengakses konten malicious dapat terpapar risiko keamanan seperti phishing, malware, dan penipuan online. Selain itu, konten ilegal seperti judi online dan narkoba yang muncul pada domain pendidikan dapat memberikan dampak sosial yang negatif, terutama bagi generasi muda yang merupakan mayoritas pengguna internet di Indonesia dan sering mengakses domain pendidikan untuk keperluan akademik.

Deteksi manual terhadap konten malicious pada domain memerlukan waktu yang lama, sumber daya manusia yang besar, dan kurang efisien. Seorang administrator website perlu melakukan scanning secara manual terhadap seluruh halaman website, subdomain, dan konten yang ada, yang dapat memakan waktu berhari-hari bahkan berminggu-minggu untuk domain dengan struktur yang kompleks. Selain itu, deteksi manual rentan terhadap human error dan mungkin melewatkan konten yang tersembunyi dengan baik.

Perkembangan teknologi machine learning dan artificial intelligence telah membuka peluang baru untuk mengatasi masalah ini. Machine learning telah terbukti efektif dalam berbagai aplikasi klasifikasi teks dan deteksi konten, termasuk deteksi spam email, klasifikasi sentiment, dan identifikasi konten berbahaya. Dengan menggunakan algoritma machine learning seperti Support Vector Machine (SVM), Naive Bayes, dan Random Forest, sistem dapat dilatih untuk mengidentifikasi pola-pola konten malicious secara otomatis dengan akurasi tinggi.

Selain itu, perkembangan teknologi web API dan arsitektur REST telah memungkinkan pengembangan sistem yang scalable dan dapat diakses dari berbagai platform. Dengan menggunakan Django REST Framework, sistem dapat menyediakan endpoint API yang dapat diakses oleh berbagai klien, termasuk aplikasi mobile. Perkembangan teknologi mobile, khususnya Flutter framework yang dapat digunakan untuk membangun aplikasi cross-platform, memungkinkan pengguna untuk mengakses sistem deteksi konten malicious secara mudah dan praktis melalui smartphone mereka.

Berdasarkan analisis kebutuhan dan gap yang ada dalam penelitian sebelumnya, belum banyak sistem yang secara komprehensif mengintegrasikan machine learning untuk deteksi konten malicious pada domain pendidikan dengan arsitektur REST API dan aplikasi mobile. Sistem-sistem yang ada cenderung fokus pada satu aspek saja, seperti deteksi malware atau filtering konten, namun belum secara khusus menangani masalah konten malicious pada domain pendidikan dengan pendekatan yang terintegrasi antara backend API, machine learning, dan mobile application.

Oleh karena itu, penelitian ini mengembangkan sebuah sistem deteksi konten malicious pada domain pendidikan berbasis machine learning dengan arsitektur REST API untuk klien multi-platform. Meskipun fokus penelitian pada domain pendidikan (.ac.id), sistem tetap dirancang dengan fleksibilitas untuk dapat melakukan scanning pada domain lain (seperti .com, .org, .go.id) untuk keperluan perbandingan dan validasi. Sistem ini dirancang untuk membantu berbagai pihak, terutama institusi pendidikan tinggi, dalam mengidentifikasi dan mendeteksi konten malicious pada domain mereka secara otomatis, cepat, dan akurat melalui aplikasi mobile yang user-friendly.

---

## 1.2 Rumusan Masalah

Berdasarkan latar belakang yang telah diuraikan, dapat diidentifikasi beberapa permasalahan yang perlu diselesaikan dalam penelitian ini. Rumusan masalah dalam penelitian ini adalah:

1. **Bagaimana mengembangkan sistem deteksi konten malicious pada domain pendidikan berbasis machine learning yang dapat mengidentifikasi domain-domain pendidikan yang terindikasi konten malicious dengan akurasi tinggi?**
   
   Permasalahan ini mencakup pengembangan model machine learning yang dapat membedakan antara konten aman dan konten malicious pada domain pendidikan, termasuk berbagai jenis konten ilegal seperti judi online, pornografi, narkoba, dan phishing yang sering muncul pada domain pendidikan. Sistem harus mampu menangani berbagai teknik penyembunyian konten seperti hidden content, orphan pages, dan konten dalam subdomain yang sering digunakan pada domain pendidikan. Meskipun fokus pada domain pendidikan, model harus dapat memberikan hasil yang akurat untuk domain lain sebagai perbandingan.

2. **Bagaimana merancang arsitektur REST API yang dapat mendukung aplikasi mobile multi-platform dengan performa optimal?**
   
   Sistem harus dirancang dengan arsitektur yang scalable dan dapat menangani berbagai request secara bersamaan. REST API harus dapat menyediakan endpoint yang efisien untuk scanning domain, manajemen user, dan integrasi dengan model machine learning. Selain itu, sistem harus dapat mengoptimalkan penggunaan resource seperti API quota untuk search engine dan database.

3. **Bagaimana mengintegrasikan model machine learning ke dalam sistem backend API untuk deteksi real-time?**
   
   Model machine learning yang telah dilatih harus dapat diintegrasikan ke dalam sistem backend dengan cara yang efisien. Sistem harus dapat melakukan prediksi real-time terhadap konten yang di-scan, dengan memperhatikan performa dan akurasi. Selain itu, sistem harus dapat menangani berbagai format input dan memberikan output yang dapat digunakan oleh aplikasi mobile.

4. **Bagaimana mengembangkan aplikasi mobile yang user-friendly dan dapat terhubung dengan backend API melalui protokol HTTPS?**
   
   Aplikasi mobile harus dirancang dengan antarmuka yang intuitif dan mudah digunakan oleh berbagai kalangan pengguna. Sistem harus memastikan keamanan komunikasi antara aplikasi mobile dan backend API menggunakan protokol HTTPS. Aplikasi harus dapat menampilkan hasil scanning dengan jelas dan memberikan feedback yang informatif kepada pengguna.

5. **Bagaimana mengevaluasi performa sistem secara keseluruhan termasuk akurasi model machine learning dan kepuasan pengguna?**
   
   Sistem harus dievaluasi dari berbagai aspek, termasuk akurasi model machine learning dalam mengklasifikasikan konten malicious, performa API dalam menangani request, dan kepuasan pengguna terhadap aplikasi mobile. Evaluasi ini penting untuk memastikan bahwa sistem dapat memenuhi kebutuhan pengguna dan memberikan hasil yang akurat.

---

## 1.3 Batasan Masalah

Untuk menjaga fokus penelitian dan memastikan penelitian dapat diselesaikan dengan baik dalam waktu yang tersedia, penelitian ini dibatasi pada beberapa aspek berikut:

1. **Domain Target**: 
   Sistem fokus pada deteksi konten malicious untuk domain pendidikan (.ac.id) yang menggunakan bahasa Indonesia, karena berdasarkan observasi dan data, sebagian besar serangan konten malicious terjadi pada domain pendidikan. Domain lain seperti .com, .net, .org, .go.id, dan .id dapat di-scan oleh sistem untuk keperluan perbandingan dan validasi, namun tidak menjadi fokus utama penelitian dan evaluasi.

2. **Platform**: 
   Aplikasi mobile dikembangkan untuk platform Android saja. Platform iOS dapat dikembangkan di masa depan namun tidak termasuk dalam scope penelitian ini.

3. **Algoritma Machine Learning**: 
   Evaluasi dibatasi pada tiga algoritma klasifikasi yaitu Support Vector Machine (SVM), Naive Bayes, dan Random Forest. Algoritma lain seperti deep learning (CNN, LSTM) dapat dievaluasi di masa depan namun tidak termasuk dalam penelitian ini.

4. **Search Engine**: 
   Sistem menggunakan Google Search sebagai primary source untuk scanning dengan menggunakan SerpAPI. Search engine lain seperti Bing dan DuckDuckGo dapat diintegrasikan di masa depan namun tidak termasuk dalam penelitian ini.

5. **Konten Target**: 
   Fokus pada deteksi konten ilegal seperti narkoba, perjudian online, pornografi, phishing, dan malware distribution. Konten lain seperti hate speech dan disinformation tidak termasuk dalam scope penelitian ini.

6. **User Interface**: 
   Aplikasi mobile menggunakan bahasa Indonesia sebagai bahasa utama. Dukungan multi-bahasa dapat ditambahkan di masa depan namun tidak termasuk dalam penelitian ini.

7. **Verifikasi Konten**: 
   Sistem menggunakan Selenium untuk verifikasi real-time konten dari website. Verifikasi dilakukan terhadap hasil pencarian Google dan konten yang di-crawl. Verifikasi manual oleh human expert tidak termasuk dalam scope penelitian ini.

8. **Dataset**: 
   Dataset yang digunakan untuk training model machine learning terdiri dari sample domain aman dan domain yang terindikasi konten malicious dalam bahasa Indonesia. Dataset dalam bahasa lain tidak termasuk dalam penelitian ini.

---

## 1.4 Tujuan Penelitian

Berdasarkan rumusan masalah yang telah diuraikan, tujuan penelitian ini adalah:

1. **Mengembangkan sistem deteksi konten malicious pada domain pendidikan berbasis machine learning dengan akurasi minimal 85%** yang dapat mengidentifikasi berbagai jenis konten ilegal seperti judi online, pornografi, narkoba, dan phishing yang sering muncul pada domain pendidikan. Sistem harus dapat menangani berbagai teknik penyembunyian konten dan memberikan hasil yang akurat, dengan tetap mempertahankan fleksibilitas untuk scanning domain lain sebagai perbandingan.

2. **Merancang dan mengimplementasikan REST API menggunakan Django REST Framework** yang dapat mendukung aplikasi mobile multi-platform dengan performa optimal. API harus dapat menangani berbagai request secara efisien, mengoptimalkan penggunaan resource, dan menyediakan endpoint yang diperlukan untuk scanning domain dan manajemen user.

3. **Membangun aplikasi mobile menggunakan Flutter** yang dapat terhubung dengan backend API dan menyediakan antarmuka yang user-friendly. Aplikasi harus dapat menampilkan hasil scanning dengan jelas, memberikan feedback yang informatif, dan memastikan keamanan komunikasi menggunakan protokol HTTPS.

4. **Mengintegrasikan model machine learning ke dalam sistem backend API** untuk deteksi real-time. Model harus dapat melakukan prediksi dengan cepat dan akurat, serta dapat menangani berbagai format input dan memberikan output yang dapat digunakan oleh aplikasi mobile.

5. **Mengevaluasi performa sistem secara menyeluruh** termasuk akurasi model machine learning (menggunakan metrik precision, recall, F1-score, dan confusion matrix), response time API (mengukur waktu respons untuk berbagai endpoint), dan kepuasan pengguna terhadap aplikasi mobile (melalui User Acceptance Testing dengan minimal 20 responden).

---

## 1.5 Manfaat Penelitian

Penelitian ini diharapkan dapat memberikan manfaat baik secara teoritis maupun praktis:

### 1.5.1 Manfaat Teoritis

1. **Kontribusi dalam Pengembangan Sistem Deteksi Konten Malicious pada Domain Pendidikan**: 
   Penelitian ini memberikan kontribusi dalam pengembangan sistem deteksi konten malicious pada domain pendidikan menggunakan machine learning, khususnya untuk domain pendidikan Indonesia (.ac.id). Penelitian ini dapat menjadi referensi untuk penelitian selanjutnya dalam bidang deteksi konten berbahaya pada domain pendidikan dan dapat diterapkan pada konteks serupa.

2. **Pengembangan Arsitektur REST API untuk Aplikasi Mobile**: 
   Penelitian ini menambah literatur tentang integrasi machine learning dengan REST API untuk aplikasi mobile, khususnya dalam konteks deteksi konten malicious. Arsitektur yang dikembangkan dapat menjadi pola untuk pengembangan sistem serupa di masa depan.

3. **Evaluasi Algoritma Machine Learning untuk Klasifikasi Konten**: 
   Penelitian ini menyediakan perbandingan performa berbagai algoritma machine learning (SVM, Naive Bayes, Random Forest) dalam konteks deteksi konten malicious pada domain. Hasil evaluasi ini dapat menjadi baseline untuk penelitian selanjutnya.

4. **Baseline untuk Penelitian Selanjutnya**: 
   Penelitian ini menyediakan baseline dan metodologi yang dapat digunakan untuk penelitian selanjutnya dalam bidang deteksi konten malicious, baik dengan menggunakan algoritma yang lebih advanced seperti deep learning maupun dengan memperluas scope deteksi ke jenis konten lain.

### 1.5.2 Manfaat Praktis

1. **Tools untuk Institusi Pendidikan**: 
   Sistem yang dikembangkan dapat digunakan oleh institusi pendidikan tinggi (universitas, perguruan tinggi, sekolah) untuk mengidentifikasi domain mereka yang terindikasi konten malicious. Sistem ini dapat membantu administrator website kampus dalam melakukan monitoring dan maintenance secara proaktif, sehingga dapat mencegah atau menangani konten malicious sebelum merusak reputasi institusi.

2. **Pengurangan Waktu Deteksi Manual**: 
   Sistem otomatis dapat mengurangi waktu yang diperlukan untuk mendeteksi konten malicious dari berhari-hari menjadi beberapa menit saja. Hal ini dapat meningkatkan efisiensi dan produktivitas administrator website.

3. **Aksesibilitas melalui Aplikasi Mobile**: 
   Aplikasi mobile memungkinkan pengguna untuk melakukan scanning domain secara mudah dan praktis dari mana saja dan kapan saja menggunakan smartphone mereka. Hal ini meningkatkan aksesibilitas sistem dan memudahkan pengguna dalam menggunakan sistem.

4. **Peningkatan Keamanan Cyber**: 
   Dengan mendeteksi konten malicious secara dini, sistem dapat membantu mengurangi risiko keamanan cyber bagi pengguna internet. Sistem dapat membantu mencegah pengguna mengakses konten ilegal yang dapat merugikan mereka.

5. **Dukungan bagi Penegakan Hukum**: 
   Sistem dapat membantu pihak berwenang dalam mengidentifikasi domain-domain yang terindikasi konten ilegal, sehingga dapat mendukung proses penegakan hukum terhadap konten ilegal di internet.

---

## 1.6 Sistematika Penulisan

Skripsi ini disusun dalam lima bab dengan sistematika sebagai berikut:

**BAB I PENDAHULUAN**
Berisi latar belakang masalah yang menjelaskan kondisi dan konteks penelitian, rumusan masalah yang mengidentifikasi permasalahan yang akan diselesaikan, batasan masalah yang membatasi scope penelitian, tujuan penelitian yang menyatakan tujuan yang ingin dicapai, manfaat penelitian yang menjelaskan kontribusi penelitian, dan sistematika penulisan yang menjelaskan struktur skripsi.

**BAB II TINJAUAN PUSTAKA**
Berisi teori-teori yang mendasari penelitian meliputi konten malicious pada domain pendidikan (pengertian, fenomena di Indonesia, jenis-jenis, dampak, metode deteksi), machine learning untuk klasifikasi teks (SVM, Naive Bayes, Random Forest, TF-IDF, preprocessing), arsitektur REST API (konsep REST, Django REST Framework, authentication), mobile application development (Flutter framework, state management, API integration), dan penelitian terkait yang relevan dengan penelitian ini.

**BAB III METODOLOGI PENELITIAN**
Berisi metodologi pengembangan sistem yang menjelaskan pendekatan dan tahapan pengembangan, analisis kebutuhan yang mengidentifikasi kebutuhan fungsional dan non-fungsional, perancangan sistem yang mencakup arsitektur sistem, diagram UML, dan desain database, perancangan model machine learning yang mencakup dataset preparation, feature extraction, model selection, dan evaluation, implementasi yang menjelaskan langkah-langkah development, dan pengujian sistem yang mencakup unit testing, integration testing, dan user acceptance testing.

**BAB IV HASIL DAN PEMBAHASAN**
Berisi hasil analisis kebutuhan dan perancangan sistem, hasil implementasi backend API dan mobile application, hasil training dan evaluasi model machine learning dengan perbandingan berbagai algoritma, hasil pengujian sistem yang mencakup pengujian fungsional, performa, dan user acceptance testing, serta pembahasan hasil yang menganalisis kelebihan, keterbatasan, dan perbandingan dengan sistem sejenis.

**BAB V KESIMPULAN DAN SARAN**
Berisi kesimpulan yang merangkum pencapaian tujuan penelitian, kontribusi penelitian, dan hasil akhir sistem, serta saran yang memberikan rekomendasi untuk pengembangan selanjutnya, peningkatan model machine learning, fitur tambahan yang dapat dikembangkan, dan optimasi performa sistem.

---

**Catatan:**
- Semua data statistik (angka persentase, jumlah website, dll) harus diganti dengan data aktual dari sumber terpercaya atau dihilangkan jika tidak tersedia
- Sesuaikan dengan format penulisan yang diminta oleh kampus Anda
- Pastikan semua referensi di-cite dengan benar sesuai format yang diminta

