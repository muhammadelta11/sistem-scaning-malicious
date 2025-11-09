import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/scan_result.dart';

class ResultsScreen extends StatefulWidget {
  final ScanResult scanResult;

  const ResultsScreen({Key? key, required this.scanResult}) : super(key: key);

  @override
  _ResultsScreenState createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen> {
  ScanResult get scanResult => widget.scanResult;

  @override
  Widget build(BuildContext context) {
    try {
      print('Building ResultsScreen for domain: ${scanResult.domain}');
      print('Categories count: ${scanResult.categories.length}');
      
      return Scaffold(
        appBar: AppBar(
          title: Text('Scan Results'),
          backgroundColor: Theme.of(context).primaryColor,
          actions: [
            IconButton(
              icon: Icon(Icons.share),
              onPressed: () {
                // TODO: Implement share functionality
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Share functionality coming soon')),
                );
              },
            ),
          ],
        ),
        body: SingleChildScrollView(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildSummaryCard(context),
              SizedBox(height: 16),
              _buildStatusCard(),
              SizedBox(height: 16),
              _buildDetailsCard(),
              if (scanResult.categories.isNotEmpty) ...[
                SizedBox(height: 16),
                _buildCategoriesCard(),
              ],
              if (scanResult.conclusion != null) ...[
                SizedBox(height: 16),
                _buildConclusionCard(),
              ],
              SizedBox(height: 16),
              _buildRiskAssessmentCard(),
            ],
          ),
        ),
      );
    } catch (e, stackTrace) {
      print('Error building ResultsScreen: $e');
      print('Stack trace: $stackTrace');
      // Return error screen if build fails
      return Scaffold(
        appBar: AppBar(
          title: Text('Scan Results'),
          backgroundColor: Theme.of(context).primaryColor,
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error, size: 64, color: Colors.red),
              SizedBox(height: 16),
              Text('Error displaying results: $e'),
              SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: Text('Go Back'),
              ),
            ],
          ),
        ),
      );
    }
  }

  Widget _buildSummaryCard(BuildContext context) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Scan Summary',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            Row(
              children: [
                Icon(Icons.domain, color: Theme.of(context).primaryColor),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    scanResult.domain,
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
                  ),
                ),
              ],
            ),
            SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.access_time, color: Colors.grey),
                SizedBox(width: 8),
                Text(
                  'Duration: ${scanResult.scanDuration.toStringAsFixed(2)}s',
                  style: TextStyle(color: Colors.grey),
                ),
              ],
            ),
            SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.schedule, color: Colors.grey),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _formatTimestamp(scanResult.timestamp),
                    style: TextStyle(color: Colors.grey),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusCard() {
    Color statusColor;
    IconData statusIcon;
    String statusText;

    switch (scanResult.status.toUpperCase()) {
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
      default:
        statusColor = Colors.orange;
        statusIcon = Icons.pending;
        statusText = scanResult.status;
    }

    return Card(
      elevation: 4,
      color: statusColor.withOpacity(0.1),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(statusIcon, color: statusColor, size: 32),
            SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Status',
                    style: TextStyle(fontSize: 14, color: Colors.grey),
                  ),
                  Text(
                    statusText,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: statusColor,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailsCard() {
    return Card(
      elevation: 4,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Scan Details',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            _buildDetailRow('Scan ID', scanResult.scanId),
            _buildDetailRow('Total Pages', scanResult.totalPages.toString()),
            _buildDetailRow('Malicious Pages', scanResult.maliciousPages.toString()),
            if (scanResult.totalItems != null)
              _buildDetailRow('Total Items', scanResult.totalItems.toString()),
            if (scanResult.totalSubdomains != null)
              _buildDetailRow('Subdomains Found', scanResult.totalSubdomains.toString()),
          ],
        ),
      ),
    );
  }

  Widget _buildCategoriesCard() {
    try {
      // Count total items first
      int totalItems = 0;
      List<Map<String, dynamic>> allItems = [];
      
      scanResult.categories.forEach((categoryKey, categoryData) {
        try {
          if (categoryData is Map<String, dynamic>) {
            final items = categoryData['items'];
            List<dynamic> itemsList = [];
            
            if (items is List) {
              itemsList = items;
            } else if (items != null) {
              print('Warning: items is not a List, got ${items.runtimeType}');
            }
            
            for (var item in itemsList) {
              try {
                if (item is Map<String, dynamic>) {
                  allItems.add({
                    'category': categoryData['name']?.toString() ?? categoryKey?.toString() ?? 'Unknown',
                    'categoryKey': categoryKey?.toString() ?? '',
                    'item': item,
                  });
                  totalItems++;
                }
              } catch (e) {
                print('Error processing category item: $e');
                continue; // Continue to next item in the loop
              }
            }
          }
        } catch (e) {
          print('Error processing category $categoryKey: $e');
          // Return from forEach callback to skip this category and continue to next
          return;
        }
      });
    
    if (totalItems == 0) {
      return Card(
        elevation: 4,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('No malicious content detected', style: TextStyle(color: Colors.grey)),
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
            Row(
              children: [
                Icon(Icons.warning, color: Colors.red, size: 24),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Detected Malicious Content ($totalItems items)',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.red,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            // Use ListView.builder for lazy loading - more efficient for large lists
            ConstrainedBox(
              constraints: BoxConstraints(maxHeight: 400), // Limit height to prevent overflow
              child: ListView.builder(
                shrinkWrap: true,
                physics: ClampingScrollPhysics(),
                itemCount: allItems.length,
                itemBuilder: (context, index) {
                  final itemData = allItems[index];
                  final categoryName = itemData['category'] as String;
                  final item = itemData['item'] as Map<String, dynamic>;
                  
                  // Show category name only if it's the first item of this category
                  final showCategory = index == 0 || 
                      (allItems[index - 1]['categoryKey'] != itemData['categoryKey']);
                  
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (showCategory)
                        Padding(
                          padding: EdgeInsets.only(bottom: 8, top: index > 0 ? 12 : 0),
                          child: Text(
                            categoryName,
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                              color: Colors.red.shade700,
                            ),
                          ),
                        ),
                      Container(
                        margin: EdgeInsets.only(bottom: 12, left: 8),
                        padding: EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.red.shade50,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.red.shade200),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    item['title']?.toString() ?? 'No Title',
                                    style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                IconButton(
                                  icon: Icon(Icons.copy, size: 18, color: Colors.grey),
                                  onPressed: () {
                                    final url = item['url']?.toString() ?? '';
                                    if (url.isNotEmpty) {
                                      Clipboard.setData(ClipboardData(text: url));
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        SnackBar(
                                          content: Text('URL berhasil disalin'),
                                          duration: Duration(seconds: 2),
                                        ),
                                      );
                                    }
                                  },
                                  padding: EdgeInsets.zero,
                                  constraints: BoxConstraints(),
                                ),
                              ],
                            ),
                            SizedBox(height: 4),
                            Text(
                              item['url']?.toString() ?? '',
                              style: TextStyle(color: Colors.blue, fontSize: 12),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            if (item['snippet'] != null && item['snippet'].toString().isNotEmpty) ...[
                              SizedBox(height: 4),
                              Text(
                                item['snippet'].toString(),
                                style: TextStyle(fontSize: 12, color: Colors.grey.shade700),
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                            SizedBox(height: 4),
                            Row(
                              children: [
                                if (item['confidence'] != null) ...[
                                  Icon(Icons.warning, size: 14, color: Colors.orange),
                                  SizedBox(width: 4),
                                  Flexible(
                                    child: Text(
                                      'Confidence: ${(item['confidence'] is num ? (item['confidence'] as num).toStringAsFixed(2) : '0.00')}',
                                      style: TextStyle(fontSize: 12, color: Colors.orange.shade700),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                                if (item['verification_status'] != null) ...[
                                  SizedBox(width: 12),
                                  Icon(Icons.verified_user, size: 14, color: Colors.green),
                                  SizedBox(width: 4),
                                  Flexible(
                                    child: Text(
                                      item['verification_status'].toString().toUpperCase(),
                                      style: TextStyle(fontSize: 12, color: Colors.green.shade700),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
    } catch (e, stackTrace) {
      print('Error building categories card: $e');
      print('Stack trace: $stackTrace');
      // Return error card if build fails
      return Card(
        elevation: 4,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.error, color: Colors.red),
              SizedBox(height: 8),
              Text(
                'Error loading categories: $e',
                style: TextStyle(color: Colors.red),
              ),
            ],
          ),
        ),
      );
    }
  }

  Widget _buildConclusionCard() {
    return Card(
      elevation: 4,
      color: Colors.blue.shade50,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.info, color: Colors.blue, size: 24),
                SizedBox(width: 8),
                Text(
                  'Kesimpulan',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade900,
                  ),
                ),
              ],
            ),
            SizedBox(height: 8),
            Text(
              scanResult.conclusion!,
              style: TextStyle(fontSize: 14, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }

  // Removed _buildMaliciousContentList - now handled directly in _buildCategoriesCard with ListView.builder

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 2,
            child: Text(
              label,
              style: TextStyle(fontWeight: FontWeight.w500),
              overflow: TextOverflow.ellipsis,
              maxLines: 2,
            ),
          ),
          SizedBox(width: 8),
          Expanded(
            flex: 3,
            child: Text(
              value,
              style: TextStyle(color: Colors.grey.shade700),
              textAlign: TextAlign.right,
              overflow: TextOverflow.ellipsis,
              maxLines: 2,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRiskAssessmentCard() {
    Color riskColor;
    String riskLevel;
    IconData riskIcon;

    if (scanResult.riskScore >= 70) {
      riskColor = Colors.red;
      riskLevel = 'High Risk';
      riskIcon = Icons.warning;
    } else if (scanResult.riskScore >= 40) {
      riskColor = Colors.orange;
      riskLevel = 'Medium Risk';
      riskIcon = Icons.warning_amber;
    } else {
      riskColor = Colors.green;
      riskLevel = 'Low Risk';
      riskIcon = Icons.check_circle;
    }

    return Card(
      elevation: 4,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Risk Assessment',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            Center(
              child: Column(
                children: [
                  Icon(
                    riskIcon,
                    size: 64,
                    color: riskColor,
                  ),
                  SizedBox(height: 16),
                  Text(
                    riskLevel,
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: riskColor,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Risk Score: ${scanResult.riskScore}/100',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
            ),
            SizedBox(height: 16),
            _buildRiskExplanation(riskLevel),
          ],
        ),
      ),
    );
  }

  Widget _buildRiskExplanation(String riskLevel) {
    String explanation;
    switch (riskLevel) {
      case 'High Risk':
        explanation = 'Domain ini menunjukkan tanda-tanda signifikan SEO poisoning. Tindakan segera disarankan untuk menyelidiki dan mengurangi ancaman keamanan potensial.';
        break;
      case 'Medium Risk':
        explanation = 'Domain ini menunjukkan beberapa aktivitas mencurigakan. Pemantauan rutin dan penyelidikan lebih lanjut mungkin diperlukan.';
        break;
      case 'Low Risk':
        explanation = 'Domain ini tampaknya relatif aman berdasarkan scan saat ini. Lanjutkan pemantauan rutin untuk setiap perubahan.';
        break;
      default:
        explanation = 'Tidak dapat menentukan tingkat risiko.';
    }

    return Container(
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        explanation,
        style: TextStyle(fontSize: 14, height: 1.4),
      ),
    );
  }

  String _formatTimestamp(String timestamp) {
    try {
      final dateTime = DateTime.parse(timestamp);
      final now = DateTime.now();
      final difference = now.difference(dateTime);

      if (difference.inDays > 0) {
        return '${difference.inDays} ${difference.inDays == 1 ? 'day' : 'days'} ago';
      } else if (difference.inHours > 0) {
        return '${difference.inHours} ${difference.inHours == 1 ? 'hour' : 'hours'} ago';
      } else if (difference.inMinutes > 0) {
        return '${difference.inMinutes} ${difference.inMinutes == 1 ? 'minute' : 'minutes'} ago';
      } else {
        return 'Just now';
      }
    } catch (e) {
      return timestamp;
    }
  }
}
