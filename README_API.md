# API Documentation - Sistem Deteksi Malicious Domain

## Overview

Sistem ini menyediakan API REST lengkap untuk integrasi dengan aplikasi mobile atau sistem eksternal. API menggunakan Django REST Framework dengan autentikasi berbasis session atau token.

## Base URL

```
http://your-domain.com/api/
```

## Authentication

### Session-based (Web Interface)
- Login via web interface
- Session cookie otomatis digunakan

### Token-based (Mobile/External)
```bash
POST /api/auth/login/
{
  "username": "admin",
  "password": "password123"
}

Response:
{
  "token": "abc123...",
  "user": {...}
}
```

## Endpoints

### 1. System Configuration (`/api/config/`)

Manajemen konfigurasi sistem (admin only).

#### Get Active Configuration
```http
GET /api/config/active/
Authorization: Token <your-token>

Response 200 OK:
{
  "id": 1,
  "enable_api_cache": true,
  "api_cache_ttl_days": 7,
  "use_comprehensive_query": true,
  "max_search_results": 100,
  "enable_bing_search": false,
  "enable_duckduckgo_search": true,
  "enable_subdomain_dns_lookup": true,
  "enable_subdomain_search": false,
  "enable_subdomain_content_scan": false,
  "max_subdomains_to_scan": 10,
  "enable_deep_crawling": true,
  "enable_sitemap_analysis": true,
  "enable_path_discovery": true,
  "enable_graph_analysis": true,
  "max_crawl_pages": 50,
  "enable_realtime_verification": true,
  "use_tiered_verification": true,
  "enable_illegal_content_detection": true,
  "enable_hidden_content_detection": true,
  "enable_injection_detection": true,
  "enable_unindexed_discovery": true,
  "enable_backlink_analysis": false,
  "updated_by": 1,
  "updated_by_username": "admin",
  "updated_at": "2024-01-15T10:30:00Z",
  "notes": ""
}
```

#### Update Configuration
```http
PATCH /api/config/1/
Authorization: Token <your-token>

Request Body:
{
  "enable_api_cache": true,
  "max_search_results": 150,
  "max_crawl_pages": 100
}

Response 200 OK:
{...}  // Updated config
```

#### Reset to Default
```http
POST /api/config/reset_to_default/
Authorization: Token <your-token>

Response 200 OK:
{...}  // Default configuration
```

### 2. Scan Management (`/api/scans/`)

#### Create New Scan
```http
POST /api/scans/
Authorization: Token <your-token>

Request Body:
{
  "domain": "example.com",
  "scan_type": "Cepat (Google Only)",  // or "Komprehensif (Google + Crawling)"
  "enable_verification": true,
  "show_all_results": false
}

Response 201 Created:
{
  "id": 123,
  "scan_id": "scan_abc123",
  "domain": "example.com",
  "status": "PENDING",
  "status_display": "Pending",
  "scan_type": "Cepat (Google Only)",
  "ran_with_verification": true,
  "showed_all_results": false,
  "scan_date": "2024-01-15T10:00:00Z",
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": null,
  "error_message": null
}
```

#### Get Scan History
```http
GET /api/scans/
Authorization: Token <your-token>

Response 200 OK:
[
  {
    "id": 123,
    "scan_id": "scan_abc123",
    "domain": "example.com",
    "status": "COMPLETED",
    ...
  },
  ...
]
```

#### Get Scan Details
```http
GET /api/scans/123/
Authorization: Token <your-token>

Response 200 OK:
{
  "id": 123,
  "scan_id": "scan_abc123",
  ...
}
```

#### Get Scan Results
```http
GET /api/scans/123/results/
Authorization: Token <your-token>

Response 200 OK:
{
  "categories": {
    "1": {
      "name": "Judi Online",
      "items": [...]
    },
    "2": {
      "name": "Pornografi",
      "items": [...]
    }
  },
  "domain_info": {...},
  "total_pages": 50,
  "verified_scan": true,
  "final_conclusion": {
    "status": "MERAH",
    "message": "Domain terindikasi konten berbahaya",
    ...
  }
}
```

#### Get Scan Progress
```http
GET /api/scans/123/progress/
Authorization: Token <your-token>

Response 200 OK:
{
  "status": "PROCESSING",
  "phase": "Verification",
  "current": 25,
  "total": 100,
  "message": "Memverifikasi URL 25 dari 100..."
}
```

### 3. Malicious Keywords (`/api/keywords/`)

#### List Keywords
```http
GET /api/keywords/
Authorization: Token <your-token>

Response 200 OK:
[
  {
    "id": 1,
    "keyword": "slot gacor",
    "category": "judi",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z",
    "created_by": 1,
    "created_by_username": "admin"
  },
  ...
]
```

#### Create Keyword
```http
POST /api/keywords/
Authorization: Token <your-token>

Request Body:
{
  "keyword": "new_keyword",
  "category": "phishing",
  "is_active": true
}

Response 201 Created:
{...}
```

#### Update Keyword
```http
PATCH /api/keywords/1/
Authorization: Token <your-token>

Request Body:
{
  "is_active": false
}

Response 200 OK:
{...}
```

#### Toggle Keyword Status
```http
POST /api/keywords/1/toggle/
Authorization: Token <your-token>

Response 200 OK:
{...}  // Toggled keyword
```

### 4. Activity Logs (`/api/activity-logs/`)

#### List Activity Logs
```http
GET /api/activity-logs/
Authorization: Token <your-token>

Response 200 OK:
[
  {
    "id": 1,
    "user": 1,
    "user_username": "admin",
    "timestamp": "2024-01-15T10:00:00Z",
    "organization_name": "Organization",
    "action": "CREATE_SCAN",
    "details": "Created scan for example.com"
  },
  ...
]
```

### 5. Users Management (`/api/users/`)

#### List Users
```http
GET /api/users/
Authorization: Token <your-token>  // Admin only

Response 200 OK:
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "",
    "last_name": "",
    "organization_name": "Main Organization",
    "role": "admin",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z"
  },
  ...
]
```

#### Create User
```http
POST /api/users/
Authorization: Token <your-token>  // Admin only

Request Body:
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "organization_name": "Organization",
  "role": "user"
}

Response 201 Created:
{...}
```

#### Reset User Password
```http
POST /api/users/1/reset_password/
Authorization: Token <your-token>  // Admin only

Request Body:
{
  "password": "NewSecurePass123!"
}

Response 200 OK:
{...}
```

### 6. Domain Summaries (`/api/domain-summaries/`)

#### List Domain Summaries
```http
GET /api/domain-summaries/
Authorization: Token <your-token>

Response 200 OK:
[
  {
    "id": 1,
    "domain": "example.com",
    "total_cases": 15,
    "hack_judol": 10,
    "pornografi": 3,
    "hacked": 2,
    "last_scan": "2024-01-15T10:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  },
  ...
]
```

## Configuration Parameters Explained

### API & Cache Settings
- **enable_api_cache**: Aktifkan caching hasil search (hemat 95% quota API)
- **api_cache_ttl_days**: Lama penyimpanan cache (1-90 hari)

### Search Engine Settings
- **use_comprehensive_query**: Gunakan 1 query comprehensive vs 4 query terpisah
- **max_search_results**: Maksimal hasil per query (10-200)
- **enable_bing_search**: Aktifkan Bing search (menggunakan API)
- **enable_duckduckgo_search**: Aktifkan DuckDuckGo (GRATIS)

### Subdomain Discovery
- **enable_subdomain_dns_lookup**: DNS lookup (GRATIS)
- **enable_subdomain_search**: Search via Google (menggunakan API)
- **enable_subdomain_content_scan**: Scan konten subdomain (10+ API calls)
- **max_subdomains_to_scan**: Maksimal subdomain (default: 10)

### Crawling Settings
- **enable_deep_crawling**: Deep crawling untuk halaman tersembunyi
- **enable_sitemap_analysis**: Analisis sitemap.xml (GRATIS)
- **enable_path_discovery**: Path brute force (GRATIS)
- **enable_graph_analysis**: Graph analysis untuk orphan pages
- **max_crawl_pages**: Maksimal halaman di-crawl (default: 50)

### Verification Settings
- **enable_realtime_verification**: Verifikasi real-time dengan Selenium
- **use_tiered_verification**: Requests first, lalu Selenium

### Illegal Content Detection
- **enable_illegal_content_detection**: Deteksi konten ilegal komprehensif
- **enable_hidden_content_detection**: Deteksi CSS hidden, dll
- **enable_injection_detection**: Deteksi JavaScript/iframe injection
- **enable_unindexed_discovery**: Discovery halaman tidak terindex

### Backlink Analysis
- **enable_backlink_analysis**: Analisis backlink (menggunakan API)

## Error Responses

### 400 Bad Request
```json
{
  "error": "Format domain tidak valid."
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "error": "Resource tidak ditemukan"
}
```

### 500 Internal Server Error
```json
{
  "error": "Gagal memparse hasil scan: ..."
}
```

## Rate Limiting

- **API Calls**: Tidak ada rate limiting (handle by your infrastructure)
- **Scan Concurrency**: Maksimal 3 scan bersamaan per user
- **Cache TTL**: Default 7 hari

## Best Practices

1. **Use Caching**: Enable API cache untuk hemat quota
2. **Comprehensive Query**: Use comprehensive query untuk efisiensi
3. **Monitor Quota**: Check SerpAPI usage regularly
4. **Batch Operations**: Use bulk endpoints when available
5. **Error Handling**: Always handle errors gracefully
6. **Progress Tracking**: Poll progress endpoint for long scans

## Mobile Integration Example

### Flutter/Dart
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ScannerAPI {
  final String baseUrl = 'https://your-domain.com/api';
  String? authToken;

  Future<Map<String, dynamic>> createScan(String domain) async {
    final response = await http.post(
      Uri.parse('$baseUrl/scans/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Token $authToken',
      },
      body: jsonEncode({
        'domain': domain,
        'scan_type': 'Cepat (Google Only)',
        'enable_verification': true,
        'show_all_results': false,
      }),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to create scan');
    }
  }

  Future<Map<String, dynamic>> getScanProgress(int scanId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/scans/$scanId/progress/'),
      headers: {
        'Authorization': 'Token $authToken',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get progress');
    }
  }

  Future<Map<String, dynamic>> getSystemConfig() async {
    final response = await http.get(
      Uri.parse('$baseUrl/config/active/'),
      headers: {
        'Authorization': 'Token $authToken',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get config');
    }
  }
}
```

### React Native
```javascript
import axios from 'axios';

const ScannerAPI = {
  baseURL: 'https://your-domain.com/api',
  token: null,

  async createScan(domain) {
    const response = await axios.post(
      `${this.baseURL}/scans/`,
      {
        domain,
        scan_type: 'Cepat (Google Only)',
        enable_verification: true,
        show_all_results: false,
      },
      {
        headers: {
          Authorization: `Token ${this.token}`,
        },
      }
    );
    return response.data;
  },

  async getScanProgress(scanId) {
    const response = await axios.get(
      `${this.baseURL}/scans/${scanId}/progress/`,
      {
        headers: {
          Authorization: `Token ${this.token}`,
        },
      }
    );
    return response.data;
  },

  async getSystemConfig() {
    const response = await axios.get(
      `${this.baseURL}/config/active/`,
      {
        headers: {
          Authorization: `Token ${this.token}`,
        },
      }
    );
    return response.data;
  },
};

export default ScannerAPI;
```

## Testing API

### Using cURL
```bash
# Get system config
curl -X GET http://localhost:8000/api/config/active/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json"

# Create scan
curl -X POST http://localhost:8000/api/scans/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "scan_type": "Cepat (Google Only)",
    "enable_verification": true
  }'

# Get scan progress
curl -X GET http://localhost:8000/api/scans/123/progress/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json"
```

### Using Python requests
```python
import requests

BASE_URL = "http://localhost:8000/api"
TOKEN = "abc123..."

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Get config
response = requests.get(f"{BASE_URL}/config/active/", headers=headers)
print(response.json())

# Create scan
data = {
    "domain": "example.com",
    "scan_type": "Cepat (Google Only)",
    "enable_verification": True
}
response = requests.post(f"{BASE_URL}/scans/", json=data, headers=headers)
scan = response.json()
print(scan)

# Get progress
response = requests.get(f"{BASE_URL}/scans/{scan['id']}/progress/", headers=headers)
print(response.json())
```

## Summary

API ini menyediakan:
- ✅ Full CRUD untuk scans, keywords, users
- ✅ Real-time progress tracking
- ✅ System configuration management
- ✅ Activity logging
- ✅ Mobile-friendly responses
- ✅ Comprehensive error handling
- ✅ Token-based authentication
- ✅ Well-documented endpoints

Semua konfigurasi yang sebelumnya hardcoded sekarang bisa diubah via UI atau API!

