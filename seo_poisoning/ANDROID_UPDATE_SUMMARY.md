# Android App Update Summary

## Overview
Aplikasi Android (Flutter) telah diperbarui secara menyeluruh untuk mengintegrasikan dengan Django REST Framework API, menambahkan fitur authentication, quota system, dan premium features.

## Perubahan Utama

### 1. API Integration
- ✅ Update `ApiService` untuk menggunakan Django REST Framework API
- ✅ Tambah authentication dengan token-based auth
- ✅ Integrasi endpoint baru: `/api/scans/`, `/api/users/profile/`, `/api/users/quota_status/`

### 2. Authentication
- ✅ Tambah `LoginScreen` untuk user login
- ✅ Tambah `AuthProvider` untuk manage authentication state
- ✅ Token disimpan di SharedPreferences
- ✅ Auto-logout jika token tidak valid

### 3. Quota System
- ✅ Tambah `QuotaStatus` model
- ✅ Display quota di HomeScreen dan ScanFormScreen
- ✅ Check quota sebelum scan
- ✅ Auto-refresh quota setelah scan

### 4. Premium Features
- ✅ Tambah `UserProfile` model dengan `isPremium` flag
- ✅ Display premium badge di HomeScreen
- ✅ Profile screen menampilkan premium status

### 5. UI Updates
- ✅ Redesign HomeScreen dengan quota status widget
- ✅ Update ScanFormScreen dengan quota check
- ✅ Tambah ProfileScreen untuk user profile
- ✅ Update navigation dengan bottom navigation bar

## File Changes

### New Files
- `lib/models/user_profile.dart` - User profile dan quota models
- `lib/providers/auth_provider.dart` - Authentication provider
- `lib/screens/login_screen.dart` - Login screen
- `lib/screens/profile_screen.dart` - Profile screen
- `scanner/api/auth_views.py` - Authentication API endpoint

### Updated Files
- `lib/main.dart` - Tambah AuthProvider, update routing
- `lib/services/api_service.dart` - Update untuk Django REST Framework API
- `lib/providers/scan_provider.dart` - Update untuk new API structure
- `lib/screens/home_screen.dart` - Tambah quota widget, premium badge
- `lib/screens/scan_form_screen.dart` - Tambah quota check, update scan flow
- `lib/models/scan_history.dart` - Update model structure
- `pubspec.yaml` - Tambah `shared_preferences` dependency
- `scanner/api/views.py` - Tambah profile dan quota_status endpoints
- `scanner/api/serializers.py` - Tambah QuotaStatusSerializer dan UserProfileSerializer
- `scanner/api/urls.py` - Tambah auth/login endpoint

## API Endpoints yang Digunakan

### Authentication
- `POST /api/auth/login/` - Login dan dapatkan token

### User
- `GET /api/users/profile/` - Get user profile dengan quota dan premium status
- `GET /api/users/quota_status/` - Get quota status saja

### Scan
- `POST /api/scans/` - Create scan baru
- `GET /api/scans/` - Get scan history
- `GET /api/scans/{id}/results/` - Get scan results
- `GET /api/scans/{id}/progress/` - Get scan progress

### Domain Summary
- `GET /api/domain-summaries/` - Get dashboard stats dan rankings

## Setup Instructions

### 1. Django Backend
Pastikan Django REST Framework Token Authentication sudah dikonfigurasi:

```python
# settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
    ...
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    ...
}
```

Install token auth:
```bash
python manage.py migrate
```

### 2. Flutter App
Update dependencies:
```bash
cd seo_poisoning
flutter pub get
```

Update config:
- Edit `lib/config.dart` dan sesuaikan `apiBaseUrl` dengan IP server Django Anda

### 3. Testing
1. Jalankan Django server:
```bash
python manage.py runserver 0.0.0.0:8000
```

2. Build dan jalankan Flutter app:
```bash
flutter run
```

3. Login dengan credentials yang ada di database Django
4. Test scan dengan domain yang valid

## Notes

- Pastikan Django server bisa diakses dari device/emulator (check firewall/network)
- Untuk emulator Android, gunakan `10.0.2.2` sebagai localhost
- Untuk device fisik, gunakan IP komputer Anda di network yang sama
- Token authentication perlu di-setup di Django settings

## Next Steps (Optional)

1. Add refresh token mechanism
2. Add offline support dengan local caching
3. Add push notifications untuk scan completion
4. Add biometric authentication
5. Add dark mode support

