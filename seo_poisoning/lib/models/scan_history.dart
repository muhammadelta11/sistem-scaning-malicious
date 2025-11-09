class ScanHistory {
  final int? id;
  final String scanId;
  final String domain;
  final String status;
  final String statusDisplay;
  final String scanType;
  final bool ranWithVerification;
  final bool showedAllResults;
  final DateTime scanDate;
  final DateTime startTime;
  final DateTime? endTime;
  final String? errorMessage;

  ScanHistory({
    this.id,
    required this.scanId,
    required this.domain,
    required this.status,
    required this.statusDisplay,
    required this.scanType,
    required this.ranWithVerification,
    required this.showedAllResults,
    required this.scanDate,
    required this.startTime,
    this.endTime,
    this.errorMessage,
  });

  factory ScanHistory.fromJson(Map<String, dynamic> json) {
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
        print('Warning: Expected bool but got List in ScanHistory: $value');
        return defaultValue;
      }
      print('Warning: Unexpected type for bool in ScanHistory: ${value.runtimeType} ($value)');
      return defaultValue;
    }
    
    // Helper function untuk safe int parsing
    int? _parseInt(dynamic value) {
      if (value == null) return null;
      if (value is int) return value;
      if (value is String) return int.tryParse(value);
      if (value is double) return value.toInt();
      if (value is List) {
        print('Warning: Expected int but got List in ScanHistory: $value');
        return null;
      }
      print('Warning: Unexpected type for int in ScanHistory: ${value.runtimeType} ($value)');
      return null;
    }
    
    try {
      return ScanHistory(
        id: _parseInt(json['id']),
        scanId: json['scan_id']?.toString() ?? '',
        domain: json['domain']?.toString() ?? '',
        status: json['status']?.toString() ?? 'PENDING',
        statusDisplay: json['status_display']?.toString() ?? json['status']?.toString() ?? 'Pending',
        scanType: json['scan_type']?.toString() ?? 'Cepat (Google Only)',
        ranWithVerification: _parseBool(json['ran_with_verification'], true),
        showedAllResults: _parseBool(json['showed_all_results'], false),
        scanDate: json['scan_date'] != null 
            ? (json['scan_date'] is DateTime 
                ? json['scan_date'] 
                : DateTime.parse(json['scan_date'].toString()))
            : DateTime.now(),
        startTime: json['start_time'] != null 
            ? (json['start_time'] is DateTime 
                ? json['start_time'] 
                : DateTime.parse(json['start_time'].toString()))
            : DateTime.now(),
        endTime: json['end_time'] != null 
            ? (json['end_time'] is DateTime 
                ? json['end_time'] 
                : DateTime.tryParse(json['end_time'].toString()))
            : null,
        errorMessage: json['error_message']?.toString(),
      );
    } catch (e, stackTrace) {
      print('Error parsing ScanHistory.fromJson: $e');
      print('Stack trace: $stackTrace');
      print('JSON data: $json');
      // Print each field to identify which one is problematic
      print('id: ${json['id']} (${json['id'].runtimeType})');
      print('ran_with_verification: ${json['ran_with_verification']} (${json['ran_with_verification']?.runtimeType})');
      print('showed_all_results: ${json['showed_all_results']} (${json['showed_all_results']?.runtimeType})');
      rethrow;
    }
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'scan_id': scanId,
      'domain': domain,
      'status': status,
      'status_display': statusDisplay,
      'scan_type': scanType,
      'ran_with_verification': ranWithVerification,
      'showed_all_results': showedAllResults,
      'scan_date': scanDate.toIso8601String(),
      'start_time': startTime.toIso8601String(),
      'end_time': endTime?.toIso8601String(),
      'error_message': errorMessage,
    };
  }
}
