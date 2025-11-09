class Config {
  // ========================================
  // KONFIGURASI KONEKSI KE DJANGO BACKEND
  // ========================================
  
  // Untuk DEVELOPMENT (Development/Testing)
  static const String devApiBaseUrl = 'http://10.211.55.2:8000';
  
  // Untuk PRODUCTION (Production/Hosted)
  // Ganti dengan URL production Django Anda (misalnya: https://api.example.com)
  static const String prodApiBaseUrl = 'https://your-domain.com';
  
  // Tentukan environment (ubah ke false untuk production build)
  static const bool isDevelopment = true; // Set ke false saat build untuk Play Store
  
  // API Base URL - akan otomatis memilih berdasarkan environment
  static String get apiBaseUrl {
    return isDevelopment ? devApiBaseUrl : prodApiBaseUrl;
  }
  
  // ========================================
  // CATATAN UNTUK PRODUCTION:
  // ========================================
  // 1. Pastikan Django menggunakan HTTPS (SSL/TLS)
  // 2. Update ALLOWED_HOSTS di settings.py Django
  // 3. Konfigurasi CORS untuk mengizinkan request dari Android app
  // 4. Pastikan domain production sudah memiliki SSL certificate
  // 5. Set isDevelopment = false sebelum build release APK/AAB
  // ========================================
  
  // ========================================
  // CATATAN UNTUK DEVELOPMENT:
  // ========================================
  // - Untuk Android Emulator di Windows, gunakan: http://10.0.2.2:8000
  // - Untuk iOS Simulator di macOS, gunakan: http://localhost:8000
  // - Untuk device fisik Android/iOS, gunakan IP Windows VM/Local IP
  // - Pastikan Django server berjalan dengan: python manage.py runserver 0.0.0.0:8000
  // ========================================
  
  // Legacy API key (tidak digunakan lagi, sekarang pakai token auth)
  static const String apiKey = 'your-secret-api-key';
}
