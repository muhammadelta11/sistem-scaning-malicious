import 'package:flutter/material.dart';
import '../services/api_service.dart';

class DashboardScreen extends StatefulWidget {
  final ApiService apiService;

  DashboardScreen({required this.apiService});

  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _dashboardData;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    try {
      // Load stats and rankings separately as per api-v2.py
      final stats = await widget.apiService.getDashboardStats();
      final rankings = await widget.apiService.getDomainRanking(limit: 10);

      setState(() {
        _dashboardData = {
          'stats': stats,
          'rankings': rankings['rankings'] ?? rankings['data'] ?? []
        };
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Dashboard'),
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : _errorMessage != null
          ? Center(child: Text('Error: $_errorMessage'))
          : _buildDashboard(),
    );
  }

  Widget _buildDashboard() {
    if (_dashboardData == null) {
      return Center(child: Text('No data available'));
    }

    final stats = _dashboardData!['stats'] as Map<String, dynamic>?;
    final rankings = _dashboardData!['rankings'] as List<dynamic>?;

    return SingleChildScrollView(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Statistics',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 16),
          if (stats != null) ...[
            _buildStatCard('Total Domains', stats['total_domains']?.toString() ?? '0'),
            _buildStatCard('Total Cases', stats['total_cases']?.toString() ?? '0'),
            _buildStatCard('Infected Domains', stats['infected_domains']?.toString() ?? '0'),
            _buildStatCard('Max Cases', stats['max_cases']?.toString() ?? '0'),
          ],
          SizedBox(height: 32),
          Text(
            'Domain Rankings',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 16),
          if (rankings != null && rankings.isNotEmpty)
            DataTable(
              columns: [
                DataColumn(label: Text('Domain')),
                DataColumn(label: Text('Total Cases')),
                DataColumn(label: Text('Judi')),
                DataColumn(label: Text('Porn')),
                DataColumn(label: Text('Hacked')),
                DataColumn(label: Text('Last Scan')),
              ],
              rows: rankings.map((ranking) {
                return DataRow(cells: [
                  DataCell(Text(ranking['domain'] ?? '')),
                  DataCell(Text(ranking['jumlah_kasus']?.toString() ?? '0')),
                  DataCell(Text(ranking['hack_judol']?.toString() ?? '0')),
                  DataCell(Text(ranking['pornografi']?.toString() ?? '0')),
                  DataCell(Text(ranking['hacked']?.toString() ?? '0')),
                  DataCell(Text(ranking['last_scan'] ?? '')),
                ]);
              }).toList(),
            )
          else
            Text('No rankings available'),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value) {
    return Card(
      margin: EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(title, style: TextStyle(fontSize: 16)),
            Text(
              value,
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}
