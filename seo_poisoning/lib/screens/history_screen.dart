import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/scan_provider.dart';
import '../models/scan_history.dart';
import 'results_screen.dart';
import '../models/scan_result.dart';

class HistoryScreen extends StatefulWidget {
  @override
  _HistoryScreenState createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  @override
  void initState() {
    super.initState();
    // Delay loading sampai setelah build selesai
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadHistory();
    });
  }

  Future<void> _loadHistory() async {
    final scanProvider = Provider.of<ScanProvider>(context, listen: false);
    await scanProvider.loadScanHistory();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Scan History'),
        backgroundColor: Theme.of(context).primaryColor,
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadHistory,
          ),
        ],
      ),
      body: Consumer<ScanProvider>(
        builder: (context, scanProvider, child) {
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
                    onPressed: _loadHistory,
                    child: Text('Retry'),
                  ),
                ],
              ),
            );
          }

          if (scanProvider.scanHistory.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.history, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'No scan history found',
                    style: TextStyle(fontSize: 18, color: Colors.grey),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Perform some scans to see history',
                    style: TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: _loadHistory,
            child: ListView.builder(
              padding: EdgeInsets.all(16),
              itemCount: scanProvider.scanHistory.length,
              itemBuilder: (context, index) {
                final history = scanProvider.scanHistory[index];
                return _buildHistoryCard(context, history, scanProvider);
              },
            ),
          );
        },
      ),
    );
  }

  Widget _buildHistoryCard(BuildContext context, ScanHistory history, ScanProvider scanProvider) {
    Color statusColor;
    IconData statusIcon;
    String statusText;

    switch (history.status.toUpperCase()) {
      case 'COMPLETED':
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        statusText = 'Completed';
        break;
      case 'FAILED':
        statusColor = Colors.red;
        statusIcon = Icons.error;
        statusText = 'Failed';
        break;
      case 'PROCESSING':
        statusColor = Colors.blue;
        statusIcon = Icons.hourglass_top;
        statusText = 'Processing';
        break;
      case 'PENDING':
        statusColor = Colors.orange;
        statusIcon = Icons.pending;
        statusText = 'Pending';
        break;
      default:
        statusColor = Colors.grey;
        statusIcon = Icons.help;
        statusText = history.status;
    }

    return Card(
      elevation: 2,
      margin: EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: history.status.toUpperCase() == 'COMPLETED' 
            ? () => _viewResults(context, history, scanProvider)
            : null,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      history.domain,
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(statusIcon, size: 16, color: statusColor),
                        SizedBox(width: 4),
                        Text(
                          statusText,
                          style: TextStyle(color: statusColor, fontSize: 12, fontWeight: FontWeight.w500),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.category, size: 16, color: Colors.grey),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Type: ${history.scanType}',
                      style: TextStyle(color: Colors.grey, fontSize: 14),
                    ),
                  ),
                ],
              ),
              SizedBox(height: 4),
              Row(
                children: [
                  Icon(Icons.verified_user, size: 16, color: Colors.grey),
                  SizedBox(width: 8),
                  Text(
                    history.ranWithVerification ? 'With Verification' : 'Without Verification',
                    style: TextStyle(color: Colors.grey, fontSize: 14),
                  ),
                ],
              ),
              SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Icon(Icons.access_time, size: 14, color: Colors.grey),
                      SizedBox(width: 4),
                      Text(
                        _formatTimestamp(history.startTime),
                        style: TextStyle(color: Colors.grey, fontSize: 12),
                      ),
                    ],
                  ),
                  if (history.status.toUpperCase() == 'COMPLETED')
                    TextButton.icon(
                      onPressed: () => _viewResults(context, history, scanProvider),
                      icon: Icon(Icons.visibility, size: 16),
                      label: Text('View Results'),
                      style: TextButton.styleFrom(
                        padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      ),
                    ),
                ],
              ),
              if (history.errorMessage != null && history.errorMessage!.isNotEmpty)
                Container(
                  margin: EdgeInsets.only(top: 8),
                  padding: EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.error_outline, size: 16, color: Colors.red),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          history.errorMessage!,
                          style: TextStyle(color: Colors.red, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _viewResults(BuildContext context, ScanHistory history, ScanProvider scanProvider) async {
    // Get NavigatorState before showing dialog to ensure we have a stable reference
    final navigator = Navigator.of(context);
    
    // Show loading dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => Center(child: CircularProgressIndicator()),
    );

    try {
      // Get scan details
      print('Getting scan details for scan ID: ${history.id}');
      final details = await scanProvider.getScanDetails(history.id!);
      print('Scan details received: ${details != null ? 'yes, size: ${details.length} keys' : 'no'}');
      
      if (details != null) {
        print('Processing data...');
        print('Details keys: ${details.keys.toList()}');
        
        try {
          final categories = details['categories'];
          final domainInfo = details['domain_info'];
          
          print('Categories type: ${categories.runtimeType}');
          print('DomainInfo type: ${domainInfo.runtimeType}');
          
          // Ensure categories and domainInfo are Maps
          final categoriesMap = categories is Map && !(categories is List)
              ? Map<String, dynamic>.from(categories) 
              : <String, dynamic>{};
          final domainInfoMap = domainInfo is Map && !(domainInfo is List)
              ? Map<String, dynamic>.from(domainInfo) 
              : <String, dynamic>{};
          
          print('Categories map size: ${categoriesMap.length}');
          
          // Safe parsing for numeric fields
          int totalPages = 0;
          if (details['total_pages'] != null) {
            final tp = details['total_pages'];
            if (tp is int) totalPages = tp;
            else if (tp is num) totalPages = tp.toInt();
            else totalPages = int.tryParse(tp.toString()) ?? 0;
          }
          
          int maliciousPages = 0;
          if (details['malicious_pages'] != null) {
            final mp = details['malicious_pages'];
            if (mp is int) maliciousPages = mp;
            else if (mp is num) maliciousPages = mp.toInt();
            else maliciousPages = int.tryParse(mp.toString()) ?? 0;
          }
          
          int riskScore = 0;
          if (details['risk_score'] != null) {
            final rs = details['risk_score'];
            if (rs is int) riskScore = rs;
            else if (rs is num) riskScore = rs.toInt();
            else riskScore = int.tryParse(rs.toString()) ?? 0;
          }
          
          double scanDuration = 0.0;
          if (details['scan_duration'] != null) {
            final sd = details['scan_duration'];
            if (sd is double) scanDuration = sd;
            else if (sd is num) scanDuration = sd.toDouble();
            else scanDuration = double.tryParse(sd.toString()) ?? 0.0;
          }
          
          // Safe parsing for optional fields
          int? totalItems;
          if (details['total_items'] != null) {
            final ti = details['total_items'];
            if (ti is int) totalItems = ti;
            else if (ti is num) totalItems = ti.toInt();
            else totalItems = int.tryParse(ti.toString());
          }
          
          int? totalSubdomains;
          if (details['total_subdomains'] != null) {
            final ts = details['total_subdomains'];
            if (ts is int) totalSubdomains = ts;
            else if (ts is num) totalSubdomains = ts.toInt();
            else totalSubdomains = int.tryParse(ts.toString());
          }
          
          final scanResult = ScanResult(
            scanId: history.scanId,
            status: history.status,
            domain: history.domain,
            totalPages: totalPages,
            maliciousPages: maliciousPages,
            riskScore: riskScore,
            scanDuration: scanDuration,
            timestamp: history.startTime.toIso8601String(),
            categories: categoriesMap,
            domainInfo: domainInfoMap,
            conclusion: details['final_conclusion']?['summary']?.toString() ?? details['conclusion']?.toString(),
            totalItems: totalItems,
            totalSubdomains: totalSubdomains,
          );
          
          print('ScanResult created successfully');
          print('Categories count: ${scanResult.categories.length}');
          
          // Close dialog first using navigator (works even if context is not mounted)
          if (navigator.canPop()) {
            navigator.pop();
            print('Loading dialog closed');
          }
          
          // Use navigator.push directly (doesn't require context.mounted)
          print('Navigating to ResultsScreen...');
          navigator.push(
            MaterialPageRoute(
              builder: (ctx) => ResultsScreen(scanResult: scanResult),
            ),
          );
          print('Navigation completed');
        } catch (e, stackTrace) {
          print('Error creating ScanResult: $e');
          print('Stack trace: $stackTrace');
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Error processing scan results: $e'),
                backgroundColor: Colors.red,
                duration: Duration(seconds: 5),
              ),
            );
          }
        }
      } else {
        // Details is null
        print('No details received (details is null)');
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to load scan results: No data received'),
              backgroundColor: Colors.red,
              duration: Duration(seconds: 3),
            ),
          );
        }
      }
    } catch (e, stackTrace) {
      print('Error in _viewResults: $e');
      print('Stack trace: $stackTrace');
      // Make sure loading dialog is closed
      if (context.mounted) {
        try {
          Navigator.pop(context); // Close loading if still open
        } catch (_) {
          // Dialog might already be closed
        }
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading results: $e'),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 5),
          ),
        );
      }
    }
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inDays > 0) {
      return '${difference.inDays} ${difference.inDays == 1 ? 'day' : 'days'} ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} ${difference.inHours == 1 ? 'hour' : 'hours'} ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} ${difference.inMinutes == 1 ? 'minute' : 'minutes'} ago';
    } else {
      return 'Just now';
    }
  }
}
