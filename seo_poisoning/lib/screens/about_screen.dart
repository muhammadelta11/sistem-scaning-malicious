import 'package:flutter/material.dart';

class AboutScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('About'),
        backgroundColor: Theme.of(context).primaryColor,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Icon(
                  Icons.security,
                  size: 80,
                  color: Theme.of(context).primaryColor,
                ),
              ),
              SizedBox(height: 20),
              Text(
                'SEO Poisoning Detector',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).primaryColor,
                ),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 20),
              Text(
                'Deskripsi Sistem',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 10),
              Text(
                'SEO Poisoning Detector adalah aplikasi mobile yang dirancang untuk mendeteksi konten berbahaya atau tidak diinginkan pada situs web. Aplikasi ini menggunakan teknologi AI dan analisis SERP (Search Engine Results Page) untuk mengidentifikasi domain yang terinfeksi oleh konten seperti judi online, pornografi, atau situs yang telah diretas.',
                style: TextStyle(fontSize: 16, height: 1.5),
              ),
              SizedBox(height: 20),
              Text(
                'Fitur Utama:',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 10),
              _buildFeatureItem('Pemindaian Domain', 'Analisis cepat dan komprehensif terhadap domain target.'),
              _buildFeatureItem('Dashboard Statistik', 'Tampilan data statistik dan peringkat domain.'),
              _buildFeatureItem('Riwayat Pemindaian', 'Pelacakan dan filter riwayat pemindaian sebelumnya.'),
              _buildFeatureItem('Analisis Backlink', 'Opsional analisis backlink untuk deteksi lebih mendalam.'),
              SizedBox(height: 20),
              Text(
                'Teknologi:',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 10),
              Text(
                'Aplikasi ini dibangun menggunakan Flutter untuk cross-platform development, dengan integrasi API SerpApi untuk data pencarian dan layanan backend khusus untuk analisis SEO.',
                style: TextStyle(fontSize: 16, height: 1.5),
              ),
              SizedBox(height: 20),
              Text(
                'Versi: 1.0.0',
                style: TextStyle(
                  fontSize: 16,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFeatureItem(String title, String description) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.check_circle, color: Colors.green, size: 20),
          SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Text(
                  description,
                  style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
