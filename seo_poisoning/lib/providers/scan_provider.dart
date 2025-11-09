import 'package:flutter/foundation.dart';
import '../models/scan_result.dart';
import '../models/dashboard_stats.dart';
import '../models/scan_history.dart';
import '../services/api_service.dart';

class ScanProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();

  // State variables
  bool _isLoading = false;
  String? _error;
  ScanResult? _lastScanResult;
  DashboardStats? _dashboardStats;
  List<ScanHistory> _scanHistory = [];
  List<DomainRanking> _domainRankings = [];

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  ScanResult? get lastScanResult => _lastScanResult;
  DashboardStats? get dashboardStats => _dashboardStats;
  List<ScanHistory> get scanHistory => _scanHistory;
  List<DomainRanking> get domainRankings => _domainRankings;

  // Create scan using Django REST Framework API
  Future<bool> createScan({
    required String domain,
    String scanType = 'Cepat (Google Only)',
    bool enableVerification = true,
    bool showAllResults = false,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // Create scan
      ScanHistory scanHistory;
      try {
        scanHistory = await _apiService.createScan(
          domain: domain,
          scanType: scanType,
          enableVerification: enableVerification,
          showAllResults: showAllResults,
        );
      } catch (e) {
        print('Error creating scan: $e');
        _error = e.toString();
        _isLoading = false;
        notifyListeners();
        return false;
      }

      // Poll for results until scan is complete
      bool isComplete = false;
      int attempts = 0;
      const maxAttempts = 60; // Max 5 minutes (5 seconds * 60)

      while (!isComplete && attempts < maxAttempts) {
        await Future.delayed(Duration(seconds: 5));
        
        try {
          // Get scan progress
          final progress = await _apiService.getScanProgress(scanHistory.id!);
          final status = progress['status'] ?? 'PROCESSING';
          
          if (status == 'COMPLETED') {
            isComplete = true;
            // Get scan results
            try {
              final results = await _apiService.getScanResults(scanHistory.id!);
              _lastScanResult = ScanResult.fromJson(Map<String, dynamic>.from(results));
            } catch (e) {
              print('Error parsing scan results: $e');
              _error = 'Failed to parse scan results: ${e.toString()}';
              _isLoading = false;
              notifyListeners();
              return false;
            }
            break;
          } else if (status == 'FAILED') {
            _error = progress['error_message'] ?? 'Scan failed';
            _isLoading = false;
            notifyListeners();
            return false;
          }
          
          attempts++;
        } catch (e) {
          // Continue polling
          attempts++;
        }
      }

      if (!isComplete) {
        _error = 'Scan timeout. Please check scan history later.';
        _isLoading = false;
        notifyListeners();
        return false;
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } on QuotaExceededException catch (e) {
      // Handle quota exceeded error specifically
      _error = e.message;
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Load dashboard stats
  Future<bool> loadDashboardStats() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final stats = await _apiService.getDashboardStats();
      _dashboardStats = stats;
      _error = null; // Clear error if successful
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e, stackTrace) {
      print('Error loading dashboard stats: $e');
      print('Stack trace: $stackTrace');
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Load scan history
  Future<bool> loadScanHistory({int limit = 50}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final history = await _apiService.getScanHistory(limit: limit);
      _scanHistory = history;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Load domain rankings
  Future<bool> loadDomainRankings({int limit = 10}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final rankings = await _apiService.getDomainRanking(limit: limit);
      _domainRankings = rankings;
      _error = null; // Clear error if successful
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e, stackTrace) {
      print('Error loading domain rankings: $e');
      print('Stack trace: $stackTrace');
      _error = e.toString();
      _domainRankings = []; // Set empty list on error
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Get scan details
  Future<Map<String, dynamic>?> getScanDetails(int scanId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      print('Getting scan details for scan ID: $scanId');
      final details = await _apiService.getScanResults(scanId);
      print('Scan details received, size: ${details.length} keys');
      _error = null; // Clear error if successful
      _isLoading = false;
      notifyListeners();
      return details;
    } catch (e, stackTrace) {
      print('Error getting scan details: $e');
      print('Stack trace: $stackTrace');
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  // Health check
  Future<bool> healthCheck() async {
    try {
      final health = await _apiService.healthCheck();
      return health['status'] == 'healthy';
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  // Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }

  // Clear last scan result
  void clearLastScanResult() {
    _lastScanResult = null;
    notifyListeners();
  }
}
