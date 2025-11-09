class UserProfile {
  final int id;
  final String username;
  final String email;
  final String? firstName;
  final String? lastName;
  final String? organizationName;
  final String role;
  final bool isActive;
  final bool isPremium;
  final QuotaStatus? quotaStatus;
  final DateTime dateJoined;

  UserProfile({
    required this.id,
    required this.username,
    required this.email,
    this.firstName,
    this.lastName,
    this.organizationName,
    required this.role,
    required this.isActive,
    required this.isPremium,
    this.quotaStatus,
    required this.dateJoined,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    // Helper function untuk safe bool parsing
    bool _parseBool(dynamic value, bool defaultValue) {
      if (value == null) return defaultValue;
      if (value is bool) return value;
      if (value is String) {
        final lower = value.toLowerCase().trim();
        return lower == 'true' || lower == '1' || lower == 'yes';
      }
      if (value is int) return value == 1;
      if (value is double) return value == 1.0;
      if (value is List) {
        // Handle List case - return false (not empty doesn't mean true)
        print('Warning: Expected bool but got List: $value');
        return defaultValue;
      }
      print('Warning: Unexpected type for bool: ${value.runtimeType} ($value)');
      return defaultValue;
    }
    
    try {
      return UserProfile(
        id: json['id'] is int ? json['id'] : (int.tryParse(json['id']?.toString() ?? '0') ?? 0),
        username: json['username']?.toString() ?? '',
        email: json['email']?.toString() ?? '',
        firstName: json['first_name']?.toString(),
        lastName: json['last_name']?.toString(),
        organizationName: json['organization_name']?.toString(),
        role: json['role']?.toString() ?? 'user',
        isActive: _parseBool(json['is_active'], false),
        isPremium: _parseBool(json['is_premium'], false),
        quotaStatus: json['quota_status'] != null && 
                    !(json['quota_status'] is List) &&
                    (json['quota_status'] is Map || json['quota_status'] is Map<String, dynamic>)
            ? QuotaStatus.fromJson(Map<String, dynamic>.from(json['quota_status']))
            : null,
        dateJoined: json['date_joined'] != null 
            ? (json['date_joined'] is DateTime 
                ? json['date_joined'] 
                : DateTime.parse(json['date_joined'].toString()))
            : DateTime.now(),
      );
    } catch (e) {
      print('Error in UserProfile.fromJson: $e');
      print('JSON data: $json');
      rethrow;
    }
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'first_name': firstName,
      'last_name': lastName,
      'organization_name': organizationName,
      'role': role,
      'is_active': isActive,
      'is_premium': isPremium,
      'quota_status': quotaStatus?.toJson(),
      'date_joined': dateJoined.toIso8601String(),
    };
  }
}

class QuotaStatus {
  final int quotaLimit;
  final int usedQuota;
  final int remainingQuota;
  final bool isUnlimited;
  final bool canScan;
  final String resetPeriod;
  final DateTime? nextReset;
  final DateTime lastReset;

  QuotaStatus({
    required this.quotaLimit,
    required this.usedQuota,
    required this.remainingQuota,
    required this.isUnlimited,
    required this.canScan,
    required this.resetPeriod,
    this.nextReset,
    required this.lastReset,
  });

  factory QuotaStatus.fromJson(Map<String, dynamic> json) {
    // Helper function untuk safe bool parsing
    bool _parseBool(dynamic value, bool defaultValue) {
      if (value == null) return defaultValue;
      if (value is bool) return value;
      if (value is String) {
        final lower = value.toLowerCase().trim();
        return lower == 'true' || lower == '1' || lower == 'yes';
      }
      if (value is int) return value == 1;
      if (value is double) return value == 1.0;
      if (value is List) {
        // Handle List case - return false (not empty doesn't mean true)
        print('Warning: Expected bool but got List for QuotaStatus: $value');
        return defaultValue;
      }
      print('Warning: Unexpected type for bool in QuotaStatus: ${value.runtimeType} ($value)');
      return defaultValue;
    }
    
    // Helper function untuk safe int parsing
    int _parseInt(dynamic value, int defaultValue) {
      if (value == null) return defaultValue;
      if (value is int) return value;
      if (value is String) return int.tryParse(value) ?? defaultValue;
      if (value is double) return value.toInt();
      if (value is List) {
        print('Warning: Expected int but got List: $value');
        return defaultValue;
      }
      print('Warning: Unexpected type for int: ${value.runtimeType} ($value)');
      return defaultValue;
    }
    
    // Helper function untuk safe DateTime parsing
    DateTime? _parseDateTime(dynamic value) {
      if (value == null) return null;
      if (value is DateTime) return value;
      if (value is String) {
        try {
          return DateTime.parse(value);
        } catch (e) {
          print('Warning: Failed to parse DateTime: $value');
          return null;
        }
      }
      print('Warning: Unexpected type for DateTime: ${value.runtimeType} ($value)');
      return null;
    }
    
    try {
      return QuotaStatus(
        quotaLimit: _parseInt(json['quota_limit'], 0),
        usedQuota: _parseInt(json['used_quota'], 0),
        remainingQuota: _parseInt(json['remaining_quota'], 0),
        isUnlimited: _parseBool(json['is_unlimited'], false),
        canScan: _parseBool(json['can_scan'], true),
        resetPeriod: json['reset_period']?.toString() ?? 'monthly',
        nextReset: _parseDateTime(json['next_reset']),
        lastReset: _parseDateTime(json['last_reset']) ?? DateTime.now(),
      );
    } catch (e) {
      print('Error in QuotaStatus.fromJson: $e');
      print('JSON data: $json');
      rethrow;
    }
  }

  Map<String, dynamic> toJson() {
    return {
      'quota_limit': quotaLimit,
      'used_quota': usedQuota,
      'remaining_quota': remainingQuota,
      'is_unlimited': isUnlimited,
      'can_scan': canScan,
      'reset_period': resetPeriod,
      'next_reset': nextReset?.toIso8601String(),
      'last_reset': lastReset.toIso8601String(),
    };
  }
}

