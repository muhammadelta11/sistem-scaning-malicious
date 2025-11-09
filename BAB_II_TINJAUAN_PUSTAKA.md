# BAB II TINJAUAN PUSTAKA

Bab ini membahas teori-teori dan konsep-konsep yang mendasari penelitian ini, meliputi konten malicious pada domain pendidikan, machine learning untuk klasifikasi teks, arsitektur REST API, mobile application development, dan penelitian terkait.

---

## 2.1 Konten Malicious pada Domain Pendidikan

### 2.1.1 Pengertian Konten Malicious

Konten malicious adalah konten yang secara sengaja dibuat atau disematkan pada website dengan tujuan merugikan pengguna, melanggar hukum, atau melanggar norma sosial. Konten malicious dapat berupa berbagai jenis konten ilegal seperti judi online, pornografi, narkoba, phishing, malware, dan konten lainnya yang dapat merugikan pengguna internet.

Menurut Kementerian Komunikasi dan Informatika (Kominfo), konten malicious adalah konten yang melanggar Undang-Undang Informasi dan Transaksi Elektronik (UU ITE) dan dapat merugikan pengguna internet. Konten malicious dapat muncul dalam berbagai bentuk, mulai dari konten yang terlihat jelas pada halaman utama website hingga konten yang tersembunyi (hidden content) yang tidak terlihat oleh pengunjung biasa namun dapat diakses melalui mesin pencari atau URL langsung.

Pada konteks domain pendidikan, konten malicious mengacu pada konten ilegal yang sengaja disematkan atau disuntikkan pada domain-domain pendidikan (.ac.id) yang seharusnya berisi informasi akademik dan pendidikan. Konten ini dapat muncul karena berbagai alasan, termasuk peretasan website, kompromi server, atau injeksi konten oleh pihak yang tidak bertanggung jawab.

### 2.1.2 Fenomena Konten Malicious pada Domain Pendidikan di Indonesia

Fenomena konten malicious pada domain pendidikan di Indonesia telah menjadi masalah serius dalam beberapa tahun terakhir. Berdasarkan data dari berbagai sumber, domain pendidikan (.ac.id) menjadi salah satu target utama serangan konten malicious karena beberapa alasan:

**1. Otoritas Tinggi di Mesin Pencari**
Domain pendidikan, terutama domain universitas dan perguruan tinggi terkemuka, memiliki otoritas tinggi (domain authority) di mesin pencari seperti Google. Otoritas tinggi ini membuat halaman-halaman dalam domain pendidikan memiliki ranking yang baik dalam hasil pencarian, sehingga sangat berharga bagi penyerang yang ingin menyembunyikan konten malicious.

**2. Kepercayaan Tinggi dari Pengguna**
Pengguna internet cenderung mempercayai domain pendidikan karena diasosiasikan dengan institusi terpercaya dan berpendidikan. Penyerang memanfaatkan kepercayaan ini untuk membuat pengguna lebih mudah mengklik link yang berisi konten malicious.

**3. Aksesibilitas yang Luas**
Domain pendidikan seringkali memiliki banyak subdomain dan halaman yang dapat diakses publik, memberikan banyak celah bagi penyerang untuk menyematkan konten malicious tanpa terdeteksi dengan mudah.

**4. Keamanan Sistem yang Kurang Optimal**
Banyak institusi pendidikan di Indonesia belum memiliki sistem keamanan yang optimal untuk melindungi website mereka dari serangan. Hal ini membuat domain pendidikan menjadi target yang mudah bagi penyerang.

Berdasarkan observasi dan data dari berbagai sumber, diperkirakan lebih dari 60% serangan konten malicious terjadi pada domain pendidikan. Jenis konten yang paling sering ditemukan pada domain pendidikan meliputi judi online, pornografi, narkoba, dan phishing. Konten-konten ini seringkali disematkan pada subdomain yang terpisah atau halaman yang tidak terhubung dari halaman utama website (orphan pages), sehingga sulit dideteksi oleh administrator website.

### 2.1.3 Jenis-Jenis Konten Malicious

Sistem deteksi konten malicious pada domain pendidikan harus mampu mengidentifikasi berbagai jenis konten ilegal. Berikut adalah jenis-jenis konten malicious yang paling sering ditemukan:

**1. Judi Online**
Konten judi online meliputi berbagai bentuk perjudian seperti togel, slot online, casino, poker, dan taruhan olahraga. Konten ini sering muncul dalam bentuk iklan tersembunyi atau halaman yang disponsori. Keyword yang digunakan untuk deteksi meliputi "slot", "gacor", "judi", "poker", "casino", "togel", "sbobet", "deposit pulsa", "betting", dan "taruhan".

**2. Pornografi**
Konten pornografi meliputi gambar, video, atau teks yang mengandung konten dewasa. Konten ini sering disematkan pada halaman tersembunyi atau subdomain terpisah. Keyword yang digunakan untuk deteksi meliputi "bokep", "porn", "xxx", "nonton film dewasa", "video dewasa", dan sejenisnya.

**3. Narkoba/Obat Terlarang**
Konten narkoba meliputi penjualan, distribusi, atau promosi obat-obatan terlarang. Konten ini sangat berbahaya dan melanggar hukum. Keyword yang digunakan untuk deteksi meliputi "sabu", "ganja", "heroin", "kokain", "ekstasi", "narkoba", "narkotika", "psikotropika", "jual sabu", "beli sabu", "distributor narkoba", dan sejenisnya.

**4. Phishing**
Konten phishing adalah upaya untuk mencuri informasi pribadi pengguna seperti username, password, atau data kartu kredit dengan menyamar sebagai entitas terpercaya. Keyword yang digunakan untuk deteksi meliputi "phishing", "phising", "login bank", "verifikasi rekening", "blokir akun", "aktivasi ulang", "konfirmasi data", dan sejenisnya.

**5. Penipuan/Scam**
Konten penipuan meliputi berbagai bentuk penipuan online seperti penipuan investasi, penipuan pinjaman, atau penipuan identitas. Keyword yang digunakan untuk deteksi meliputi "penipuan", "scam", "fraud", "tricker", "modus penipuan", "binary scam", "ponzi scheme", dan sejenisnya.

**6. Hacking/Malware**
Konten hacking atau malware meliputi halaman yang telah diretas atau mengandung malware yang dapat merusak sistem pengguna. Keyword yang digunakan untuk deteksi meliputi "hacked", "defaced", "deface", "malware", "virus", dan sejenisnya.

**7. Terorisme**
Konten terorisme meliputi promosi atau dukungan terhadap aktivitas terorisme. Keyword yang digunakan untuk deteksi meliputi "teror", "terror", "radikal", "jihad", "bom", "pembunuhan", dan sejenisnya.

**8. Konten Lainnya**
Selain jenis konten di atas, sistem juga dapat mendeteksi konten lain seperti pemalsuan, perdagangan manusia, konten kekerasan, prostitusi, dan pornografi anak.

### 2.1.4 Dampak Konten Malicious pada Domain Pendidikan

Konten malicious pada domain pendidikan memiliki dampak yang sangat luas dan merugikan berbagai pihak:

**1. Dampak pada Institusi Pendidikan**
- **Kerusakan Reputasi**: Keberadaan konten malicious pada domain pendidikan dapat merusak reputasi dan kredibilitas institusi secara signifikan. Hal ini dapat menyebabkan penurunan kepercayaan masyarakat terhadap institusi.
- **Pelanggaran Hukum**: Konten malicious melanggar berbagai peraturan, termasuk UU ITE, sehingga dapat menyebabkan institusi terkena sanksi hukum.
- **Gangguan Proses Akademik**: Konten malicious dapat mengganggu proses pembelajaran dan penelitian jika website institusi harus ditutup atau dibatasi aksesnya.
- **Kerugian Finansial**: Institusi mungkin harus mengeluarkan biaya untuk perbaikan sistem, pemulihan data, atau kompensasi kepada pihak yang dirugikan.

**2. Dampak pada Pengguna Internet**
- **Risiko Keamanan**: Pengguna yang tidak sengaja mengakses konten malicious dapat terpapar risiko keamanan seperti phishing, malware, dan penipuan online.
- **Kerugian Finansial**: Pengguna dapat mengalami kerugian finansial jika terkena phishing atau penipuan online.
- **Dampak Psikologis**: Konten ilegal seperti pornografi atau konten kekerasan dapat memberikan dampak psikologis negatif, terutama bagi generasi muda.
- **Pelanggaran Privasi**: Konten phishing dapat mencuri informasi pribadi pengguna seperti username, password, atau data kartu kredit.

**3. Dampak pada Masyarakat**
- **Dampak Sosial**: Konten ilegal seperti judi online dan narkoba dapat memberikan dampak sosial yang negatif, terutama bagi generasi muda yang merupakan mayoritas pengguna internet.
- **Penurunan Kepercayaan**: Keberadaan konten malicious dapat menurunkan kepercayaan masyarakat terhadap institusi pendidikan dan internet secara umum.
- **Dampak Moral**: Konten ilegal dapat merusak nilai-nilai moral dan etika dalam masyarakat.

### 2.1.5 Metode Deteksi Konten Malicious pada Domain Pendidikan

Deteksi konten malicious pada domain pendidikan dapat dilakukan melalui berbagai metode:

**1. Deteksi Berbasis Keyword**
Metode ini menggunakan pencocokan keyword untuk mengidentifikasi konten malicious. Sistem memindai teks dalam halaman website dan mencari keyword-keyword yang terkait dengan konten ilegal. Metode ini sederhana namun efektif untuk deteksi awal.

**2. Deteksi Berbasis Machine Learning**
Metode ini menggunakan algoritma machine learning untuk mengklasifikasikan konten sebagai malicious atau aman. Sistem dilatih menggunakan dataset yang terdiri dari konten aman dan konten malicious, kemudian dapat mengidentifikasi pola-pola konten malicious secara otomatis.

**3. Deteksi Berbasis Deep Content Analysis**
Metode ini melakukan analisis mendalam terhadap konten website, termasuk konten tersembunyi (hidden content), komentar HTML, meta tags, dan atribut tersembunyi. Metode ini dapat menemukan konten malicious yang disembunyikan dengan baik.

**4. Deteksi Berbasis Graph Analysis**
Metode ini menganalisis struktur website sebagai graph untuk menemukan orphan pages (halaman yang tidak terhubung dari halaman utama) dan isolated clusters yang mungkin mengandung konten malicious.

**5. Deteksi Berbasis Subdomain Enumeration**
Metode ini melakukan enumerasi subdomain untuk menemukan subdomain yang terindikasi mengandung konten malicious. Subdomain yang terpisah sering digunakan untuk menyembunyikan konten ilegal.

**6. Verifikasi Real-Time**
Metode ini menggunakan Selenium atau tools serupa untuk mengakses website secara langsung dan memverifikasi konten yang terlihat oleh pengguna. Metode ini dapat memastikan bahwa konten malicious benar-benar ada dan dapat diakses.

---

## 2.2 Machine Learning untuk Klasifikasi Teks

Machine learning adalah cabang dari artificial intelligence yang memungkinkan komputer untuk belajar dari data tanpa diprogram secara eksplisit. Dalam konteks deteksi konten malicious, machine learning digunakan untuk mengklasifikasikan konten sebagai malicious atau aman berdasarkan pola-pola yang ditemukan dalam data training.

### 2.2.1 Support Vector Machine (SVM)

Support Vector Machine (SVM) adalah algoritma machine learning yang digunakan untuk klasifikasi dan regresi. SVM bekerja dengan mencari hyperplane yang optimal untuk memisahkan data ke dalam kelas-kelas yang berbeda.

**Prinsip Kerja SVM:**
1. SVM mencari hyperplane yang memiliki margin maksimal antara kelas-kelas data
2. Hyperplane yang optimal adalah yang memiliki jarak terbesar ke titik-titik data terdekat dari kedua kelas (support vectors)
3. SVM dapat menangani data yang tidak linear separable dengan menggunakan kernel trick

**Kelebihan SVM:**
- Efektif pada dataset dengan dimensi tinggi
- Memori efisien karena hanya menggunakan support vectors
- Versatil dengan berbagai kernel functions (linear, polynomial, RBF)

**Kekurangan SVM:**
- Tidak perform dengan baik pada dataset yang sangat besar
- Sensitif terhadap noise dan outliers
- Sulit untuk interpretasi hasil

**Aplikasi dalam Deteksi Konten Malicious:**
SVM dapat digunakan untuk mengklasifikasikan teks sebagai malicious atau aman dengan menggunakan TF-IDF sebagai feature extraction. SVM cocok untuk dataset dengan dimensi tinggi seperti teks yang telah di-vectorize.

### 2.2.2 Naive Bayes

Naive Bayes adalah algoritma klasifikasi probabilistik yang didasarkan pada teorema Bayes dengan asumsi independensi bersyarat (naive assumption) bahwa setiap fitur independen terhadap fitur lainnya.

**Prinsip Kerja Naive Bayes:**
1. Menghitung probabilitas posterior berdasarkan probabilitas prior dan likelihood
2. Mengasumsikan bahwa setiap fitur independen terhadap fitur lainnya (naive assumption)
3. Mengklasifikasikan berdasarkan probabilitas posterior tertinggi

**Formula Naive Bayes:**
```
P(class|features) = P(class) * ∏ P(feature|class) / P(features)
```

**Kelebihan Naive Bayes:**
- Sederhana dan mudah diimplementasikan
- Cepat dalam training dan prediction
- Tidak memerlukan banyak data training
- Efektif untuk klasifikasi teks

**Kekurangan Naive Bayes:**
- Asumsi independensi seringkali tidak realistis
- Sensitif terhadap feature selection
- Dapat menghasilkan probabilitas yang tidak akurat

**Aplikasi dalam Deteksi Konten Malicious:**
Naive Bayes sangat populer untuk klasifikasi teks karena kemampuannya menangani data dengan dimensi tinggi dan performa yang baik pada dataset teks. Algoritma ini cocok untuk deteksi spam email dan klasifikasi konten.

### 2.2.3 Random Forest

Random Forest adalah algoritma ensemble learning yang menggunakan multiple decision trees untuk membuat prediksi. Setiap tree dilatih pada subset data yang berbeda, dan hasil akhir adalah voting dari semua trees.

**Prinsip Kerja Random Forest:**
1. Membuat multiple decision trees dengan menggunakan bootstrap sampling
2. Setiap tree dilatih pada subset fitur yang berbeda (random feature selection)
3. Hasil prediksi adalah voting dari semua trees (majority voting untuk klasifikasi)

**Kelebihan Random Forest:**
- Tahan terhadap overfitting
- Dapat menangani data dengan banyak fitur
- Tidak memerlukan preprocessing yang kompleks
- Dapat memberikan feature importance

**Kekurangan Random Forest:**
- Memerlukan banyak memori
- Sulit untuk interpretasi hasil
- Tidak perform dengan baik pada dataset yang sangat kecil

**Aplikasi dalam Deteksi Konten Malicious:**
Random Forest efektif untuk klasifikasi teks karena kemampuannya menangani overfitting dan dapat memberikan insight tentang fitur-fitur penting dalam deteksi konten malicious.

### 2.2.4 TF-IDF (Term Frequency-Inverse Document Frequency)

TF-IDF adalah teknik feature extraction yang digunakan untuk mengukur pentingnya suatu kata dalam dokumen relatif terhadap koleksi dokumen. TF-IDF menggabungkan dua komponen:

**1. Term Frequency (TF)**
Mengukur seberapa sering suatu kata muncul dalam dokumen. Formula TF:
```
TF(t,d) = (Jumlah kemunculan term t dalam dokumen d) / (Total jumlah term dalam dokumen d)
```

**2. Inverse Document Frequency (IDF)**
Mengukur seberapa jarang suatu kata muncul dalam koleksi dokumen. Formula IDF:
```
IDF(t,D) = log(Total jumlah dokumen / Jumlah dokumen yang mengandung term t)
```

**3. TF-IDF Score**
```
TF-IDF(t,d,D) = TF(t,d) * IDF(t,D)
```

**Kelebihan TF-IDF:**
- Mengurangi bobot kata-kata yang umum (seperti "yang", "dan", dll)
- Meningkatkan bobot kata-kata yang penting dan jarang
- Efektif untuk klasifikasi teks dan information retrieval

**Aplikasi dalam Deteksi Konten Malicious:**
TF-IDF digunakan untuk mengubah teks menjadi vektor numerik yang dapat diproses oleh algoritma machine learning. Kata-kata yang sering muncul dalam konten malicious (seperti "judi", "narkoba", dll) akan memiliki bobot TF-IDF yang tinggi.

### 2.2.5 Stemming dan Preprocessing

Preprocessing adalah tahap penting dalam klasifikasi teks yang bertujuan untuk membersihkan dan menstandarisasi data sebelum diproses oleh algoritma machine learning.

**1. Tokenization**
Proses memecah teks menjadi token-token (kata-kata) individual. Tokenization dapat dilakukan berdasarkan spasi, tanda baca, atau aturan tertentu.

**2. Case Normalization**
Mengubah semua huruf menjadi huruf kecil (lowercase) untuk menghindari perbedaan antara "Judi" dan "judi".

**3. Stop Words Removal**
Menghapus kata-kata yang sangat umum (stop words) seperti "yang", "dan", "atau", "di", "dari", dll yang tidak memberikan informasi penting untuk klasifikasi.

**4. Stemming**
Proses mengurangi kata ke bentuk dasar (root word) dengan menghapus suffix dan prefix. Contoh: "berjudi", "judi", "perjudian" → "judi".

**Stemming untuk Bahasa Indonesia:**
Untuk bahasa Indonesia, dapat digunakan library Sastrawi yang merupakan Indonesian Stemmer. Sastrawi dapat melakukan stemming untuk berbagai bentuk kata dalam bahasa Indonesia.

**Contoh Stemming dengan Sastrawi:**
```python
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

factory = StemmerFactory()
stemmer = factory.create_stemmer()

# Input
text = "saya sedang berjudi online"

# Output
stemmed = stemmer.stem(text)  # "saya sedang judi"
```

**5. Lemmatization**
Mirip dengan stemming, namun lemmatization menghasilkan bentuk dasar yang valid secara linguistik. Lemmatization lebih akurat namun lebih lambat daripada stemming.

**6. Punctuation Removal**
Menghapus tanda baca yang tidak diperlukan untuk klasifikasi.

**Aplikasi dalam Deteksi Konten Malicious:**
Preprocessing sangat penting untuk memastikan bahwa algoritma machine learning dapat mengenali pola-pola yang sama dalam berbagai bentuk kata. Misalnya, "berjudi", "judi", "perjudian" harus dikenali sebagai kata yang sama terkait dengan judi online.

---

## 2.3 Arsitektur REST API

### 2.3.1 Konsep REST (Representational State Transfer)

REST (Representational State Transfer) adalah arsitektur software untuk sistem terdistribusi yang diperkenalkan oleh Roy Fielding pada tahun 2000. REST adalah gaya arsitektur, bukan protokol, yang mendefinisikan bagaimana sistem harus berkomunikasi melalui HTTP.

**Prinsip-Prinsip REST:**
1. **Stateless**: Setiap request harus mengandung semua informasi yang diperlukan. Server tidak menyimpan state client antara request.
2. **Client-Server**: Pemisahan yang jelas antara client dan server, memungkinkan mereka untuk berkembang secara independen.
3. **Cacheable**: Response harus dapat di-cache untuk meningkatkan performa.
4. **Uniform Interface**: Interface yang konsisten dan seragam untuk semua resource.
5. **Layered System**: Sistem dapat terdiri dari beberapa layer (proxy, gateway, dll) tanpa mempengaruhi komunikasi.
6. **Code on Demand** (optional): Server dapat mengirim executable code ke client.

**Resource dan HTTP Methods:**
REST menggunakan HTTP methods untuk operasi CRUD (Create, Read, Update, Delete):
- **GET**: Mengambil resource (read)
- **POST**: Membuat resource baru (create)
- **PUT**: Mengupdate resource (update)
- **DELETE**: Menghapus resource (delete)
- **PATCH**: Partial update

**Contoh REST API:**
```
GET    /api/scans/          # Mendapatkan daftar semua scan
GET    /api/scans/1/        # Mendapatkan detail scan dengan ID 1
POST   /api/scans/          # Membuat scan baru
PUT    /api/scans/1/        # Mengupdate scan dengan ID 1
DELETE /api/scans/1/        # Menghapus scan dengan ID 1
```

### 2.3.2 Django REST Framework

Django REST Framework (DRF) adalah toolkit yang powerful untuk membangun REST API menggunakan Django. DRF menyediakan berbagai fitur untuk mempermudah pengembangan API:

**Fitur-Fitur DRF:**
1. **Serializers**: Mengkonversi model Django ke JSON dan sebaliknya
2. **ViewSets**: Menggabungkan logika untuk multiple views terkait
3. **Routers**: Auto-generate URL patterns untuk ViewSets
4. **Authentication**: Berbagai metode authentication (Token, Session, OAuth, dll)
5. **Permissions**: Control akses berdasarkan user roles
6. **Pagination**: Built-in pagination untuk list views
7. **Filtering & Search**: Built-in filtering dan search capabilities
8. **Throttling**: Rate limiting untuk mencegah abuse

**Contoh Penggunaan DRF:**

```python
# serializers.py
from rest_framework import serializers
from .models import ScanHistory

class ScanHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanHistory
        fields = ['id', 'domain', 'status', 'scan_date']

# views.py
from rest_framework import viewsets
from .models import ScanHistory
from .serializers import ScanHistorySerializer

class ScanHistoryViewSet(viewsets.ModelViewSet):
    queryset = ScanHistory.objects.all()
    serializer_class = ScanHistorySerializer
    permission_classes = [IsAuthenticated]
```

### 2.3.3 Token Authentication

Token authentication adalah metode autentikasi yang menggunakan token untuk mengidentifikasi user. Token adalah string yang unik yang dikirim oleh server kepada client setelah login berhasil, dan client harus menyertakan token ini dalam setiap request selanjutnya.

**Cara Kerja Token Authentication:**
1. User melakukan login dengan username dan password
2. Server memvalidasi kredensial dan mengirim token jika valid
3. Client menyimpan token dan menyertakannya dalam header setiap request
4. Server memvalidasi token pada setiap request

**Token Authentication dengan DRF:**
DRF menyediakan TokenAuthentication yang dapat digunakan dengan mudah:

```python
# settings.py
INSTALLED_APPS = [
    ...
    'rest_framework.authtoken',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}

# views.py
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class ScanHistoryViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    ...
```

**Penggunaan Token di Client:**
```http
GET /api/scans/ HTTP/1.1
Host: api.example.com
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### 2.3.4 API Documentation dengan Swagger

Swagger (sekarang OpenAPI) adalah framework untuk mendeskripsikan, memproduksi, mengonsumsi, dan memvisualisasikan REST API. Swagger UI menyediakan interface interaktif untuk testing dan dokumentasi API.

**DRF dengan Swagger:**
DRF dapat diintegrasikan dengan drf-yasg atau drf-spectacular untuk menghasilkan dokumentasi Swagger:

```python
# urls.py
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Domain Scanner API",
      default_version='v1',
      description="API untuk deteksi konten malicious pada domain pendidikan",
   ),
   public=True,
)

urlpatterns = [
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
]
```

---

## 2.4 Mobile Application Development

### 2.4.1 Flutter Framework

Flutter adalah framework open-source yang dikembangkan oleh Google untuk membangun aplikasi mobile, web, dan desktop dari satu codebase. Flutter menggunakan bahasa Dart dan menyediakan rendering engine yang cepat.

**Kelebihan Flutter:**
1. **Cross-Platform**: Satu codebase untuk iOS dan Android
2. **Hot Reload**: Perubahan kode langsung terlihat tanpa restart aplikasi
3. **Performance**: Mendekati native performance dengan rendering engine sendiri
4. **Rich Widgets**: Library widget yang lengkap dan customizable
5. **Growing Ecosystem**: Komunitas dan package yang berkembang pesat

**Arsitektur Flutter:**
Flutter menggunakan arsitektur widget tree dimana semua UI adalah widget:
- Widget adalah immutable
- Widget tree di-rebuild ketika state berubah
- Flutter engine merender widget tree secara efisien

**Contoh Flutter App:**
```dart
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Domain Scanner',
      home: HomeScreen(),
    );
  }
}
```

### 2.4.2 State Management dengan Provider

State management adalah cara untuk mengelola state aplikasi secara efisien. Provider adalah salah satu state management yang populer di Flutter yang berdasarkan pada konsep InheritedWidget.

**Konsep Provider:**
1. **Provider**: Menyediakan data/state ke widget tree
2. **Consumer**: Widget yang mengonsumsi data dari Provider
3. **ChangeNotifier**: Class yang dapat memberitahu listener ketika state berubah

**Contoh Provider:**
```dart
// provider
class ScanProvider extends ChangeNotifier {
  List<ScanHistory> _scans = [];
  
  List<ScanHistory> get scans => _scans;
  
  Future<void> loadScans() async {
    // Load data from API
    _scans = await apiService.getScans();
    notifyListeners();
  }
}

// usage
class ScanListScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<ScanProvider>(
      builder: (context, scanProvider, child) {
        return ListView.builder(
          itemCount: scanProvider.scans.length,
          itemBuilder: (context, index) {
            return ListTile(
              title: Text(scanProvider.scans[index].domain),
            );
          },
        );
      },
    );
  }
}
```

### 2.4.3 HTTP Client untuk API Integration

Untuk berkomunikasi dengan REST API, Flutter menggunakan package `http` atau `dio` untuk melakukan HTTP requests.

**HTTP Client dengan package http:**
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  final String baseUrl = 'https://api.example.com';
  final String? token;
  
  Future<List<ScanHistory>> getScans() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/scans/'),
      headers: {
        'Authorization': 'Token $token',
        'Content-Type': 'application/json',
      },
    );
    
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => ScanHistory.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load scans');
    }
  }
}
```

**Error Handling:**
```dart
try {
  final scans = await apiService.getScans();
  // Handle success
} catch (e) {
  // Handle error
  print('Error: $e');
}
```

---

## 2.5 Penelitian Terkait

### 2.5.1 Sistem Deteksi Konten Malicious pada Domain Pendidikan

Penelitian tentang deteksi konten malicious pada domain pendidikan masih terbatas, namun ada beberapa penelitian terkait yang relevan:

**1. Deteksi Malicious Content pada Website**
Beberapa penelitian telah mengembangkan sistem untuk mendeteksi konten malicious pada website menggunakan berbagai teknik seperti machine learning, natural language processing, dan web crawling. Namun, penelitian-penelitian ini umumnya tidak fokus pada domain pendidikan.

**2. SEO Poisoning Detection**
Penelitian tentang SEO poisoning telah dilakukan untuk mendeteksi manipulasi hasil pencarian mesin pencari. Namun, penelitian-penelitian ini lebih fokus pada teknik manipulasi SEO daripada deteksi konten malicious pada domain tertentu.

**3. Web Content Classification**
Penelitian tentang klasifikasi konten web menggunakan machine learning telah banyak dilakukan, namun umumnya untuk tujuan lain seperti content filtering atau sentiment analysis, bukan untuk deteksi konten malicious pada domain pendidikan.

**Gap Penelitian:**
Belum ada penelitian yang secara komprehensif mengintegrasikan machine learning, REST API, dan mobile application untuk deteksi konten malicious pada domain pendidikan dengan fokus pada konteks Indonesia.

### 2.5.2 Aplikasi Mobile untuk Cyber Security di Institusi Pendidikan

Aplikasi mobile untuk cyber security telah berkembang dalam beberapa tahun terakhir, namun aplikasi khusus untuk deteksi konten malicious pada domain pendidikan masih terbatas:

**1. Security Monitoring Apps**
Beberapa aplikasi mobile telah dikembangkan untuk monitoring keamanan website, namun umumnya untuk monitoring uptime, SSL certificate, atau malware detection, bukan untuk deteksi konten malicious.

**2. Content Filtering Apps**
Aplikasi content filtering telah dikembangkan untuk memblokir konten tidak pantas, namun umumnya untuk penggunaan personal, bukan untuk monitoring domain institusi.

**Gap Penelitian:**
Belum ada aplikasi mobile yang secara khusus dirancang untuk membantu institusi pendidikan dalam mendeteksi konten malicious pada domain mereka dengan menggunakan machine learning dan REST API.

### 2.5.3 Machine Learning untuk Klasifikasi Web Content

Penelitian tentang machine learning untuk klasifikasi web content telah banyak dilakukan:

**1. Text Classification dengan Machine Learning**
Beberapa penelitian telah menggunakan algoritma seperti SVM, Naive Bayes, dan Random Forest untuk klasifikasi teks dengan hasil yang baik. Namun, penelitian-penelitian ini umumnya untuk dataset dalam bahasa Inggris.

**2. Indonesian Text Classification**
Penelitian tentang klasifikasi teks bahasa Indonesia masih terbatas, terutama untuk deteksi konten malicious. Beberapa penelitian telah menggunakan stemming bahasa Indonesia (Sastrawi) untuk preprocessing.

**Gap Penelitian:**
Belum ada penelitian yang secara khusus membandingkan performa berbagai algoritma machine learning (SVM, Naive Bayes, Random Forest) untuk deteksi konten malicious pada domain pendidikan dengan dataset bahasa Indonesia.

---

## 2.6 Kerangka Teori

Berdasarkan tinjauan pustaka yang telah diuraikan, kerangka teori untuk penelitian ini dapat digambarkan sebagai berikut:

**1. Konten Malicious pada Domain Pendidikan**
Penelitian ini fokus pada deteksi konten malicious pada domain pendidikan (.ac.id) yang merupakan target utama serangan konten malicious di Indonesia. Konten malicious yang dideteksi meliputi judi online, pornografi, narkoba, phishing, dan konten ilegal lainnya.

**2. Machine Learning untuk Klasifikasi**
Penelitian ini menggunakan tiga algoritma machine learning (SVM, Naive Bayes, Random Forest) untuk mengklasifikasikan konten sebagai malicious atau aman. Feature extraction dilakukan menggunakan TF-IDF, dan preprocessing dilakukan dengan stemming bahasa Indonesia menggunakan Sastrawi.

**3. REST API Architecture**
Sistem backend menggunakan Django REST Framework untuk menyediakan API yang dapat diakses oleh aplikasi mobile. Authentication dilakukan menggunakan Token Authentication, dan dokumentasi API disediakan menggunakan Swagger.

**4. Mobile Application**
Aplikasi mobile dikembangkan menggunakan Flutter untuk platform Android. State management dilakukan menggunakan Provider, dan komunikasi dengan API dilakukan menggunakan HTTP client.

**5. Integrasi Sistem**
Sistem mengintegrasikan machine learning model ke dalam backend API untuk deteksi real-time, dan aplikasi mobile mengakses API untuk melakukan scanning dan menampilkan hasil.

**Kerangka Teori Penelitian:**
```
┌─────────────────────────────────────────────────────────┐
│          Konten Malicious pada Domain Pendidikan         │
│  (Judi, Pornografi, Narkoba, Phishing, dll)            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│          Machine Learning Classification                │
│  (SVM, Naive Bayes, Random Forest)                      │
│  + TF-IDF Feature Extraction                            │
│  + Indonesian Stemming (Sastrawi)                       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│          Django REST Framework Backend API               │
│  + Token Authentication                                 │
│  + Real-time Detection                                  │
│  + Swagger Documentation                                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│          Flutter Mobile Application                      │
│  + Provider State Management                            │
│  + HTTP API Integration                                │
│  + User-friendly UI/UX                                 │
└─────────────────────────────────────────────────────────┘
```

Kerangka teori ini menunjukkan bagaimana berbagai komponen sistem terintegrasi untuk mendeteksi konten malicious pada domain pendidikan, dengan machine learning sebagai core engine, REST API sebagai middleware, dan mobile application sebagai user interface.

---

**Catatan:**
- Semua referensi harus di-cite dengan format yang sesuai (APA/Harvard/IEEE)
- Data statistik harus diganti dengan data aktual dari sumber terpercaya
- Contoh kode dapat disesuaikan dengan implementasi aktual
- Penelitian terkait harus diupdate dengan paper/jurnal yang relevan dan terbaru

