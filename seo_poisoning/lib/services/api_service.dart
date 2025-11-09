import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/scan_result.dart';
import '../models/dashboard_stats.dart';
import '../models/scan_history.dart';
import '../config.dart';

// Custom exception for quota exceeded errors
class QuotaExceededException implements Exception {
  final String message;
  QuotaExceededException(this.message);
  
  @override
  String toString() => message;
}

class ApiService {
  static const String baseUrl = Config.apiBaseUrl;
  static const String apiPrefix = '/api'; // Django REST Framework prefix
  
  // Helper method untuk mendapatkan auth token dari SharedPreferences
  Future<String?> _getAuthToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('auth_token');
  }
  
  // Helper method untuk menyimpan auth token
  Future<void> _saveAuthToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }
  
  // Helper method untuk menghapus auth token
  Future<void> _removeAuthToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }
  
  // Helper method untuk headers dengan authentication
  Future<Map<String, String>> _getHeaders({bool includeAuth = true}) async {
    final headers = {
      'Content-Type': 'application/json',
    };
    
    if (includeAuth) {
      final token = await _getAuthToken();
      if (token != null) {
        headers['Authorization'] = 'Token $token'; // Django REST Framework token auth
      }
    }
    
    return headers;
  }
  
  // Authentication: Login
  Future<Map<String, dynamic>> login(String username, String password) async {
    final url = Uri.parse('$baseUrl$apiPrefix/auth/login/');
    
    try {
      final response = await http.post(
        url,
        headers: await _getHeaders(includeAuth: false),
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );
      
      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);
        final token = data['token'];
        
        if (token != null && token.toString().isNotEmpty) {
          await _saveAuthToken(token.toString());
          return {
            'success': true, 
            'token': token.toString(), 
            'user': data['user'] ?? {}
          };
        } else {
          return {'success': false, 'error': 'Token tidak ditemukan dalam response'};
        }
      } else {
        try {
          final errorData = jsonDecode(response.body);
          final errorMsg = errorData['error'] ?? errorData['detail'] ?? 'Login failed';
          return {'success': false, 'error': errorMsg.toString()};
        } catch (e) {
          return {'success': false, 'error': 'Login failed: ${response.statusCode}'};
        }
      }
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }
  
  // Authentication: Logout
  Future<void> logout() async {
    await _removeAuthToken();
  }
  
  // Get user profile with quota and premium status
  Future<Map<String, dynamic>?> getUserProfile() async {
    final url = Uri.parse('$baseUrl$apiPrefix/users/profile/');
    
    final response = await http.get(
      url,
      headers: await _getHeaders(),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get user profile: ${response.statusCode} - ${response.body}');
    }
  }
  
  // Get quota status
  Future<Map<String, dynamic>?> getQuotaStatus() async {
    final url = Uri.parse('$baseUrl$apiPrefix/users/quota_status/');
    
    final response = await http.get(
      url,
      headers: await _getHeaders(),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get quota status: ${response.statusCode} - ${response.body}');
    }
  }
  
  // Create scan using Django REST Framework API
  Future<ScanHistory> createScan({
    required String domain,
    String scanType = 'Cepat (Google Only)',
    bool enableVerification = true,
    bool showAllResults = false,
  }) async {
    final url = Uri.parse('$baseUrl$apiPrefix/scans/');
    
    final response = await http.post(
      url,
      headers: await _getHeaders(),
      body: jsonEncode({
        'domain': domain,
        'scan_type': scanType,
        'enable_verification': enableVerification,
        'show_all_results': showAllResults,
      }),
    );
    
    if (response.statusCode == 201) {
      try {
        final data = jsonDecode(response.body);
        return ScanHistory.fromJson(Map<String, dynamic>.from(data));
      } catch (e) {
        print('Error parsing scan history from create scan: $e');
        print('Response body: ${response.body}');
        throw Exception('Failed to parse scan response: $e');
      }
    } else {
      final error = jsonDecode(response.body);
      final errorMsg = error['error'] ?? error['detail'] ?? 'Failed to create scan';
      
      // Handle quota exceeded errors
      if (response.statusCode == 403) {
        final quotaExceeded = error['quota_exceeded'];
        if (quotaExceeded == true || quotaExceeded == 'true' || quotaExceeded == 1) {
          throw QuotaExceededException(errorMsg.toString());
        }
      }
      
      throw Exception('$errorMsg (${response.statusCode})');
    }
  }
  
  // Get scan history
  Future<List<ScanHistory>> getScanHistory({int limit = 50}) async {
    final url = Uri.parse('$baseUrl$apiPrefix/scans/');
    
    final response = await http.get(
      url,
      headers: await _getHeaders(),
    );
    
    if (response.statusCode == 200) {
      try {
        final data = jsonDecode(response.body);
        // Django REST Framework returns results in 'results' field for pagination
        final results = data['results'] ?? (data is List ? data : []);
        
        if (results is! List) {
          print('Warning: results is not a List, got ${results.runtimeType}');
          return [];
        }
        
        return (results as List).map((item) {
          try {
            // Ensure item is a Map before parsing
            if (item is! Map) {
              print('Warning: ScanHistory item is not a Map, got ${item.runtimeType}');
              print('Item data: $item');
              throw Exception('ScanHistory item is not a Map: ${item.runtimeType}');
            }
            
            // Convert to Map<String, dynamic>
            final itemMap = Map<String, dynamic>.from(item);
            return ScanHistory.fromJson(itemMap);
          } catch (e, stackTrace) {
            print('Error parsing ScanHistory item: $e');
            print('Stack trace: $stackTrace');
            print('Item data: $item');
            print('Item type: ${item.runtimeType}');
            rethrow;
          }
        }).toList();
      } catch (e, stackTrace) {
        print('Error parsing scan history: $e');
        print('Stack trace: $stackTrace');
        print('Response body: ${response.body}');
        throw Exception('Failed to parse scan history: $e');
      }
    } else {
      throw Exception('Failed to get scan history: ${response.statusCode} - ${response.body}');
    }
  }
  
  // Get scan results
  Future<Map<String, dynamic>> getScanResults(int scanId) async {
    final url = Uri.parse('$baseUrl$apiPrefix/scans/$scanId/results/');
    
    try {
      final response = await http.get(
        url,
        headers: await _getHeaders(),
      ).timeout(
        Duration(seconds: 30), // Timeout 30 detik
        onTimeout: () {
          throw Exception('Request timeout: Scan results mengambil waktu terlalu lama');
        },
      );
      
      if (response.statusCode == 200) {
        try {
          final data = jsonDecode(response.body);
          return Map<String, dynamic>.from(data);
        } catch (e) {
          print('Error parsing scan results: $e');
          print('Response body length: ${response.body.length}');
          throw Exception('Failed to parse scan results: $e');
        }
      } else {
        final errorBody = response.body.length > 500 
            ? '${response.body.substring(0, 500)}...' 
            : response.body;
        throw Exception('Failed to get scan results: ${response.statusCode} - $errorBody');
      }
    } catch (e) {
      if (e.toString().contains('timeout')) {
        rethrow;
      }
      print('Error getting scan results: $e');
      rethrow;
    }
  }
  
  // Get scan progress
  Future<Map<String, dynamic>> getScanProgress(int scanId) async {
    final url = Uri.parse('$baseUrl$apiPrefix/scans/$scanId/progress/');
    
    final response = await http.get(
      url,
      headers: await _getHeaders(),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to get scan progress: ${response.statusCode} - ${response.body}');
    }
  }
  
  // Get dashboard stats (using domain summaries)
  Future<DashboardStats> getDashboardStats() async {
    final url = Uri.parse('$baseUrl$apiPrefix/domain-summaries/');
    
    try {
      final response = await http.get(
        url, 
        headers: await _getHeaders(),
      ).timeout(
        Duration(seconds: 10), // Timeout 10 detik
        onTimeout: () {
          throw Exception('Request timeout: Dashboard stats mengambil waktu terlalu lama');
        },
      );
      
      if (response.statusCode == 200) {
        try {
          final data = jsonDecode(response.body);
          final results = data['results'] ?? (data is List ? data : []);
          
          if (results is! List) {
            print('Warning: Dashboard results is not a List, got ${results.runtimeType}');
            // Return empty stats if results is not a List
            return DashboardStats(
              totalDomains: 0,
              totalCases: 0,
              infectedDomains: 0,
              maxCases: 0,
            );
          }
          
          // Calculate stats from domain summaries
          int totalDomains = 0;
          int totalCases = 0;
          int infectedDomains = 0;
          int maxCases = 0;
          
          for (var item in results) {
            try {
              if (item is Map) {
                totalDomains++;
                // Safe int parsing
                int cases;
                final totalCasesValue = item['total_cases'] ?? 0;
                if (totalCasesValue is int) {
                  cases = totalCasesValue;
                } else if (totalCasesValue is double) {
                  cases = totalCasesValue.toInt();
                } else if (totalCasesValue is num) {
                  cases = totalCasesValue.toInt();
                } else if (totalCasesValue is String) {
                  cases = int.tryParse(totalCasesValue) ?? 0;
                } else {
                  cases = int.tryParse(totalCasesValue?.toString() ?? '0') ?? 0;
                }
                
                totalCases += cases;
                if (cases > 0) infectedDomains++;
                if (cases > maxCases) maxCases = cases;
              }
            } catch (e) {
              print('Error parsing dashboard item: $e');
              continue; // Skip this item and continue
            }
          }
          
          return DashboardStats(
            totalDomains: totalDomains,
            totalCases: totalCases,
            infectedDomains: infectedDomains,
            maxCases: maxCases,
          );
        } catch (e) {
          print('Error parsing dashboard stats: $e');
          print('Response body: ${response.body.length > 500 ? response.body.substring(0, 500) : response.body}');
          throw Exception('Failed to parse dashboard stats: $e');
        }
      } else {
        throw Exception('Failed to get dashboard stats: ${response.statusCode} - ${response.body.length > 500 ? response.body.substring(0, 500) : response.body}');
      }
    } catch (e) {
      print('Error getting dashboard stats: $e');
      rethrow;
    }
  }
  
  // Get domain ranking
  Future<List<DomainRanking>> getDomainRanking({int limit = 10}) async {
    final url = Uri.parse('$baseUrl$apiPrefix/domain-summaries/?ordering=-total_cases&limit=$limit');
    
    try {
      final response = await http.get(
        url, 
        headers: await _getHeaders(),
      ).timeout(
        Duration(seconds: 10), // Timeout 10 detik
        onTimeout: () {
          throw Exception('Request timeout: Domain ranking mengambil waktu terlalu lama');
        },
      );
      
      if (response.statusCode == 200) {
        try {
          final data = jsonDecode(response.body);
          final results = data['results'] ?? (data is List ? data : []);
          
          if (results is! List) {
            print('Warning: Domain ranking results is not a List, got ${results.runtimeType}');
            return [];
          }
          
          return (results as List).map<DomainRanking>((item) {
            try {
              // Ensure item is a Map
              if (item is! Map) {
                print('Warning: Domain ranking item is not a Map, got ${item.runtimeType}');
                throw Exception('Domain ranking item is not a Map');
              }
              
              final itemMap = Map<String, dynamic>.from(item);
              
              // Parse date if it's a DateTime string
              String lastScanStr = '';
              if (itemMap['last_scan'] != null) {
                if (itemMap['last_scan'] is String) {
                  lastScanStr = itemMap['last_scan'];
                } else if (itemMap['last_scan'] is Map) {
                  // Handle serialized DateTime
                  final lastScanMap = Map<String, dynamic>.from(itemMap['last_scan']);
                  lastScanStr = lastScanMap['date']?.toString() ?? lastScanMap.toString();
                } else if (itemMap['last_scan'] is DateTime) {
                  lastScanStr = itemMap['last_scan'].toString();
                }
              }
              
              // Safe int parsing
              int _parseInt(dynamic value, int defaultValue) {
                if (value == null) return defaultValue;
                if (value is int) return value;
                if (value is String) return int.tryParse(value) ?? defaultValue;
                if (value is double) return value.toInt();
                return defaultValue;
              }
              
              return DomainRanking(
                domain: itemMap['domain']?.toString() ?? '',
                totalCases: _parseInt(itemMap['total_cases'], 0),
                hackJudol: _parseInt(itemMap['hack_judol'] ?? itemMap['hack judol'], 0),
                pornografi: _parseInt(itemMap['pornografi'], 0),
                hacked: _parseInt(itemMap['hacked'], 0),
                lastScan: lastScanStr,
              );
            } catch (e) {
              print('Error parsing domain ranking item: $e');
              print('Item data: $item');
              // Return empty DomainRanking if parsing fails
              return DomainRanking(
                domain: '',
                totalCases: 0,
                hackJudol: 0,
                pornografi: 0,
                hacked: 0,
                lastScan: '',
              );
            }
          }).where((ranking) => ranking.domain.isNotEmpty).toList(); // Filter out empty domains
        } catch (e) {
          print('Error parsing domain ranking: $e');
          print('Response body: ${response.body.length > 500 ? response.body.substring(0, 500) : response.body}');
          throw Exception('Failed to parse domain ranking: $e');
        }
      } else {
        throw Exception('Failed to get domain ranking: ${response.statusCode} - ${response.body.length > 500 ? response.body.substring(0, 500) : response.body}');
      }
    } catch (e) {
      print('Error getting domain ranking: $e');
      rethrow;
    }
  }
  
  // Health check
  Future<Map<String, dynamic>> healthCheck() async {
    // Use dedicated health check endpoint that doesn't require authentication
    final url = Uri.parse('$baseUrl$apiPrefix/health/');
    
    try {
      final response = await http.get(url, headers: await _getHeaders(includeAuth: false));
      
      if (response.statusCode == 200) {
        try {
          final data = jsonDecode(response.body);
          return {'status': data['status'] ?? 'healthy', 'message': data['message']};
        } catch (e) {
          return {'status': 'healthy'};
        }
      } else {
        return {'status': 'unhealthy', 'code': response.statusCode};
      }
    } catch (e) {
      return {'status': 'error', 'error': e.toString()};
    }
  }
}
