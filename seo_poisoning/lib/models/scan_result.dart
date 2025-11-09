class ScanResult {
  final String scanId;
  final String status;
  final String domain;
  final int totalPages;
  final int maliciousPages;
  final int riskScore;
  final double scanDuration;
  final String timestamp;
  final Map<String, dynamic> categories;
  final Map<String, dynamic> domainInfo;
  final String? conclusion; // Tambahan untuk kesimpulan scan
  final int? totalItems; // Total items ditemukan
  final int? totalSubdomains; // Total subdomains ditemukan

  ScanResult({
    required this.scanId,
    required this.status,
    required this.domain,
    required this.totalPages,
    required this.maliciousPages,
    required this.riskScore,
    required this.scanDuration,
    required this.timestamp,
    required this.categories,
    required this.domainInfo,
    this.conclusion,
    this.totalItems,
    this.totalSubdomains,
  });

  factory ScanResult.fromJson(Map<String, dynamic> json) {
    // Handle both Django API response format and legacy format
    return ScanResult(
      scanId: json['scan_id'] ?? json['scanId'] ?? '',
      status: json['status'] ?? 'unknown',
      domain: json['domain'] ?? '',
      totalPages: json['total_pages'] ?? json['totalPages'] ?? 0,
      maliciousPages: json['malicious_pages'] ?? json['maliciousPages'] ?? 0,
      riskScore: json['risk_score'] ?? json['riskScore'] ?? 0,
      scanDuration: (json['scan_duration'] ?? json['scanDuration'] ?? 0.0).toDouble(),
      timestamp: json['timestamp'] ?? json['scan_date'] ?? DateTime.now().toIso8601String(),
      categories: json['categories'] ?? {},
      domainInfo: json['domain_info'] ?? json['domainInfo'] ?? {},
      conclusion: json['conclusion'] ?? json['summary'],
      totalItems: json['total_items'] ?? json['totalItems'],
      totalSubdomains: json['total_subdomains'] ?? json['totalSubdomains'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'scan_id': scanId,
      'status': status,
      'domain': domain,
      'total_pages': totalPages,
      'malicious_pages': maliciousPages,
      'risk_score': riskScore,
      'scan_duration': scanDuration,
      'timestamp': timestamp,
      'categories': categories,
      'domain_info': domainInfo,
      if (conclusion != null) 'conclusion': conclusion,
      if (totalItems != null) 'total_items': totalItems,
      if (totalSubdomains != null) 'total_subdomains': totalSubdomains,
    };
  }
}

class DetailedScanResult {
  final String url;
  final String title;
  final String snippet;
  final String category;
  final double confidence;
  final String verificationStatus;
  final List<String> keywordsFound;
  final Map<String, dynamic>? deepAnalysis;

  DetailedScanResult({
    required this.url,
    required this.title,
    required this.snippet,
    required this.category,
    required this.confidence,
    required this.verificationStatus,
    required this.keywordsFound,
    this.deepAnalysis,
  });

  factory DetailedScanResult.fromJson(Map<String, dynamic> json) {
    return DetailedScanResult(
      url: json['url'] ?? '',
      title: json['title'] ?? '',
      snippet: json['snippet'] ?? '',
      category: json['category'] ?? '',
      confidence: (json['confidence'] ?? 0.0).toDouble(),
      verificationStatus: json['verification_status'] ?? json['verificationStatus'] ?? 'unknown',
      keywordsFound: List<String>.from(json['keywords_found'] ?? json['keywordsFound'] ?? []),
      deepAnalysis: json['deep_analysis'] ?? json['deepAnalysis'],
    );
  }
}
