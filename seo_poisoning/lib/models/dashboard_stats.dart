class DashboardStats {
  final int totalDomains;
  final int totalCases;
  final int infectedDomains;
  final int maxCases;

  DashboardStats({
    required this.totalDomains,
    required this.totalCases,
    required this.infectedDomains,
    required this.maxCases,
  });

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      totalDomains: json['total_domains'] ?? 0,
      totalCases: json['total_cases'] ?? 0,
      infectedDomains: json['infected_domains'] ?? 0,
      maxCases: json['max_cases'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_domains': totalDomains,
      'total_cases': totalCases,
      'infected_domains': infectedDomains,
      'max_cases': maxCases,
    };
  }
}

class DomainRanking {
  final String domain;
  final int totalCases;
  final int hackJudol;
  final int pornografi;
  final int hacked;
  final String lastScan;

  DomainRanking({
    required this.domain,
    required this.totalCases,
    required this.hackJudol,
    required this.pornografi,
    required this.hacked,
    required this.lastScan,
  });

  factory DomainRanking.fromJson(Map<String, dynamic> json) {
    return DomainRanking(
      domain: json['domain'] ?? '',
      totalCases: json['total_cases'] ?? 0,
      hackJudol: json['hack_judol'] ?? 0,
      pornografi: json['pornografi'] ?? 0,
      hacked: json['hacked'] ?? 0,
      lastScan: json['last_scan'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'domain': domain,
      'total_cases': totalCases,
      'hack_judol': hackJudol,
      'pornografi': pornografi,
      'hacked': hacked,
      'last_scan': lastScan,
    };
  }
}
