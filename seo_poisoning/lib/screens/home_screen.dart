import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/scan_provider.dart';
import '../providers/auth_provider.dart';
import '../models/dashboard_stats.dart';
import '../models/scan_history.dart';
import 'scan_form_screen.dart';
import 'results_screen.dart';
import 'history_screen.dart';
import 'about_screen.dart';
import 'profile_screen.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadDashboardData();
    });
  }

  Future<void> _loadDashboardData() async {
    try {
      final scanProvider = Provider.of<ScanProvider>(context, listen: false);
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      
      // Load user profile first (may fail if not authenticated)
      try {
        await authProvider.loadUserProfile();
      } catch (e) {
        print('Warning: Failed to load user profile: $e');
        // Continue even if profile load fails
      }
      
      // Load dashboard data
      await scanProvider.loadDashboardStats();
      await scanProvider.loadDomainRankings();
    } catch (e) {
      print('Error loading dashboard data: $e');
      // Error will be displayed in UI via Consumer
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('SEO Poisoning Detector'),
        backgroundColor: Theme.of(context).primaryColor,
        actions: [
          Consumer<AuthProvider>(
            builder: (context, authProvider, child) {
              if (authProvider.userProfile?.isPremium == true) {
                return Padding(
                  padding: EdgeInsets.symmetric(horizontal: 8),
                  child: Chip(
                    avatar: Icon(Icons.star, color: Colors.amber, size: 18),
                    label: Text('Premium', style: TextStyle(fontSize: 12)),
                    backgroundColor: Colors.amber.shade100,
                  ),
                );
              }
              return SizedBox.shrink();
            },
          ),
          IconButton(
            icon: Icon(Icons.person),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => ProfileScreen()),
              );
            },
          ),
        ],
      ),
      body: _buildCurrentScreen(),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.search),
            label: 'Scan',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history),
            label: 'History',
          ),
        ],
      ),
    );
  }

  Widget _buildCurrentScreen() {
    switch (_currentIndex) {
      case 0:
        return _buildHomeTab();
      case 1:
        return ScanFormScreen();
      case 2:
        return HistoryScreen();
      default:
        return _buildHomeTab();
    }
  }

  Widget _buildHomeTab() {
    return Consumer2<ScanProvider, AuthProvider>(
      builder: (context, scanProvider, authProvider, child) {
        if (scanProvider.isLoading) {
          return Center(child: CircularProgressIndicator());
        }

        if (scanProvider.error != null) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.error, size: 64, color: Colors.red),
                SizedBox(height: 16),
                Text('Error: ${scanProvider.error}'),
                SizedBox(height: 16),
                ElevatedButton(
                  onPressed: _loadDashboardData,
                  child: Text('Retry'),
                ),
              ],
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: _loadDashboardData,
          child: SingleChildScrollView(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Quota Status Widget
                if (authProvider.quotaStatus != null)
                  _buildQuotaStatusCard(authProvider.quotaStatus!),
                SizedBox(height: 16),
                // Dashboard Stats
                _buildDashboardStats(scanProvider.dashboardStats),
                SizedBox(height: 24),
                // Quick Actions
                _buildQuickActions(),
                SizedBox(height: 24),
                // Domain Rankings
                _buildDomainRankings(scanProvider.domainRankings),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildQuotaStatusCard(quotaStatus) {
    final isUnlimited = quotaStatus.isUnlimited;
    final canScan = quotaStatus.canScan;
    final used = quotaStatus.usedQuota;
    final limit = quotaStatus.quotaLimit;
    final remaining = quotaStatus.remainingQuota;
    
    return Card(
      elevation: 4,
      color: canScan ? Colors.green.shade50 : Colors.red.shade50,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isUnlimited ? Icons.all_inclusive : Icons.assignment,
                  color: canScan ? Colors.green : Colors.red,
                ),
                SizedBox(width: 8),
                Text(
                  'Status Kuota Scan',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            SizedBox(height: 12),
            if (isUnlimited)
              Row(
                children: [
                  Icon(Icons.check_circle, color: Colors.green),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Unlimited - Anda dapat melakukan scan tanpa batas',
                      style: TextStyle(fontWeight: FontWeight.w500),
                      overflow: TextOverflow.ellipsis,
                      maxLines: 2,
                    ),
                  ),
                ],
              )
            else
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Terpakai: $used/$limit',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: canScan ? Colors.green : Colors.red,
                        ),
                      ),
                      Text(
                        'Sisa: $remaining',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: canScan ? Colors.green : Colors.red,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: limit > 0 ? used / limit : 0,
                    backgroundColor: Colors.grey.shade300,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      canScan ? Colors.green : Colors.red,
                    ),
                  ),
                  if (quotaStatus.nextReset != null)
                    Padding(
                      padding: EdgeInsets.only(top: 8),
                      child: Text(
                        'Reset berikutnya: ${_formatDate(quotaStatus.nextReset!)}',
                        style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                      ),
                    ),
                ],
              ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }

  Widget _buildDashboardStats(DashboardStats? stats) {
    if (stats == null) {
      return Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('No dashboard data available'),
        ),
      );
    }

    return Card(
      elevation: 4,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Dashboard Statistics',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Total Domains',
                    stats.totalDomains.toString(),
                    Icons.domain,
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Total Cases',
                    stats.totalCases.toString(),
                    Icons.warning,
                    Colors.orange,
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Infected Domains',
                    stats.infectedDomains.toString(),
                    Icons.bug_report,
                    Colors.red,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Max Cases',
                    stats.maxCases.toString(),
                    Icons.trending_up,
                    Colors.purple,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, size: 32, color: color),
        SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(fontSize: 12, color: Colors.grey),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildQuickActions() {
    return Card(
      elevation: 4,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Quick Actions',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {
                      setState(() {
                        _currentIndex = 1;
                      });
                    },
                    icon: Icon(Icons.search),
                    label: Text('New Scan'),
                    style: ElevatedButton.styleFrom(
                      padding: EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
                SizedBox(width: 16),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      setState(() {
                        _currentIndex = 2;
                      });
                    },
                    icon: Icon(Icons.history),
                    label: Text('View History'),
                    style: OutlinedButton.styleFrom(
                      padding: EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDomainRankings(List<DomainRanking> rankings) {
    if (rankings.isEmpty) {
      return Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('No domain rankings available'),
        ),
      );
    }

    return Card(
      elevation: 4,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Top Infected Domains',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            ListView.builder(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              itemCount: rankings.length,
              itemBuilder: (context, index) {
                final ranking = rankings[index];
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: _getRiskColor(ranking.totalCases),
                    child: Text('${index + 1}'),
                  ),
                  title: Text(ranking.domain),
                  subtitle: Text('Cases: ${ranking.totalCases}'),
                  trailing: Icon(Icons.arrow_forward_ios, size: 16),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Color _getRiskColor(int cases) {
    if (cases >= 50) return Colors.red;
    if (cases >= 20) return Colors.orange;
    if (cases >= 5) return Colors.yellow;
    return Colors.green;
  }
}
