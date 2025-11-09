import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../models/user_profile.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _error;
  UserProfile? _userProfile;
  QuotaStatus? _quotaStatus;
  
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get error => _error;
  UserProfile? get userProfile => _userProfile;
  QuotaStatus? get quotaStatus => _quotaStatus;
  
  AuthProvider() {
    _checkAuthStatus();
  }
  
  // Check if user is already authenticated
  Future<void> _checkAuthStatus() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('auth_token');
    
    if (token != null) {
      _isAuthenticated = true;
      await loadUserProfile();
    }
  }
  
  // Login
  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final result = await _apiService.login(username, password);
      
      // Check success field dengan type safety
      final success = result['success'];
      if (success is bool && success == true) {
        _isAuthenticated = true;
        await loadUserProfile();
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        // Handle error
        final errorMsg = result['error'];
        _error = errorMsg is String ? errorMsg : (errorMsg?.toString() ?? 'Login failed');
        _isAuthenticated = false;
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      _isAuthenticated = false;
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
  
  // Logout
  Future<void> logout() async {
    await _apiService.logout();
    _isAuthenticated = false;
    _userProfile = null;
    _quotaStatus = null;
    notifyListeners();
  }
  
  // Load user profile
  Future<void> loadUserProfile() async {
    try {
      final profileData = await _apiService.getUserProfile();
      if (profileData != null && profileData is Map && !(profileData is List)) {
        try {
          // Ensure it's a Map<String, dynamic>
          final profileMap = Map<String, dynamic>.from(profileData);
          _userProfile = UserProfile.fromJson(profileMap);
          _quotaStatus = _userProfile?.quotaStatus;
          _error = null; // Clear any previous error
          notifyListeners();
        } catch (e, stackTrace) {
          // Error parsing profile data
          print('Error parsing user profile: $e');
          print('Stack trace: $stackTrace');
          print('Profile data: $profileData');
          _error = 'Failed to parse user profile: ${e.toString()}';
          notifyListeners();
        }
      } else {
        print('Invalid profile data format: ${profileData?.runtimeType ?? 'null'}');
        print('Profile data: $profileData');
        _error = 'Invalid profile data format: ${profileData?.runtimeType ?? 'null'}';
        notifyListeners();
      }
    } catch (e, stackTrace) {
      print('Error loading user profile: $e');
      print('Stack trace: $stackTrace');
      _error = e.toString();
      notifyListeners();
    }
  }
  
  // Load quota status
  Future<void> loadQuotaStatus() async {
    try {
      final quotaData = await _apiService.getQuotaStatus();
      if (quotaData != null && quotaData is Map && !(quotaData is List)) {
        try {
          // Ensure it's a Map<String, dynamic>
          final quotaMap = Map<String, dynamic>.from(quotaData);
          _quotaStatus = QuotaStatus.fromJson(quotaMap);
          _error = null; // Clear error if successful
          notifyListeners();
        } catch (e, stackTrace) {
          print('Error parsing quota status: $e');
          print('Stack trace: $stackTrace');
          print('Quota data: $quotaData');
          _error = 'Failed to parse quota status: ${e.toString()}';
          notifyListeners();
        }
      } else {
        print('Invalid quota data format: ${quotaData?.runtimeType ?? 'null'}');
        print('Quota data: $quotaData');
        _error = 'Invalid quota data format: ${quotaData?.runtimeType ?? 'null'}';
        notifyListeners();
      }
    } catch (e, stackTrace) {
      print('Error loading quota status: $e');
      print('Stack trace: $stackTrace');
      _error = e.toString();
      notifyListeners();
    }
  }
  
  // Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}

