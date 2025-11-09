import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/scan_provider.dart';
import '../providers/auth_provider.dart';
import 'results_screen.dart';

class ScanFormScreen extends StatefulWidget {
  @override
  _ScanFormScreenState createState() => _ScanFormScreenState();
}

class _ScanFormScreenState extends State<ScanFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _domainController = TextEditingController();

  String _scanType = 'Cepat (Google Only)';
  bool _enableVerification = true;
  bool _showAllResults = false;

  @override
  void initState() {
    super.initState();
    // Load quota status when screen opens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      authProvider.loadQuotaStatus();
    });
  }

  @override
  void dispose() {
    _domainController.dispose();
    super.dispose();
  }

  Future<void> _handleScan() async {
    if (_formKey.currentState!.validate()) {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      final scanProvider = Provider.of<ScanProvider>(context, listen: false);

      // Check quota before scanning
      if (authProvider.quotaStatus != null && !authProvider.quotaStatus!.canScan) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Kuota scan habis! Sisa: ${authProvider.quotaStatus!.remainingQuota}'),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 3),
          ),
        );
        return;
      }

      final success = await scanProvider.createScan(
        domain: _domainController.text.trim(),
        scanType: _scanType,
        enableVerification: _enableVerification,
        showAllResults: _showAllResults,
      );

      if (success) {
        // Refresh quota status
        await authProvider.loadQuotaStatus();
        
        if (scanProvider.lastScanResult != null) {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ResultsScreen(
                scanResult: scanProvider.lastScanResult!,
              ),
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Scan berhasil dimulai. Hasil akan muncul saat selesai.'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        final errorMsg = scanProvider.error ?? 'Gagal memulai scan';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMsg),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 5),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Scan Domain'),
        backgroundColor: Theme.of(context).primaryColor,
      ),
      body: Consumer2<ScanProvider, AuthProvider>(
        builder: (context, scanProvider, authProvider, child) {
          return SingleChildScrollView(
            padding: EdgeInsets.all(16),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Quota Status
                  if (authProvider.quotaStatus != null)
                    _buildQuotaCard(authProvider.quotaStatus!),
                  SizedBox(height: 16),
                  // Domain Input
                  Card(
                    elevation: 4,
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Domain Information',
                            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                          ),
                          SizedBox(height: 16),
                          TextFormField(
                            controller: _domainController,
                            decoration: InputDecoration(
                              labelText: 'Domain Name',
                              hintText: 'example.com',
                              prefixIcon: Icon(Icons.domain),
                            ),
                            validator: (value) {
                              if (value == null || value.isEmpty) {
                                return 'Please enter a domain name';
                              }
                              if (!RegExp(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$').hasMatch(value)) {
                                return 'Please enter a valid domain name';
                              }
                              return null;
                            },
                          ),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  // Scan Options
                  Card(
                    elevation: 4,
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Scan Options',
                            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                          ),
                          SizedBox(height: 16),
                          DropdownButtonFormField<String>(
                            value: _scanType,
                            decoration: InputDecoration(
                              labelText: 'Scan Type',
                            ),
                            items: [
                              DropdownMenuItem(
                                value: 'Cepat (Google Only)',
                                child: Text('Fast Scan'),
                              ),
                              DropdownMenuItem(
                                value: 'Komprehensif (Google + Crawling)',
                                child: Text('Comprehensive Scan'),
                              ),
                            ],
                            onChanged: (value) {
                              setState(() {
                                _scanType = value!;
                              });
                            },
                          ),
                          SizedBox(height: 16),
                          SwitchListTile(
                            title: Text('Enable Real-time Verification'),
                            subtitle: Text('Verify content with live website checks'),
                            value: _enableVerification,
                            onChanged: (value) {
                              setState(() {
                                _enableVerification = value;
                              });
                            },
                          ),
                          SwitchListTile(
                            title: Text('Show All Results'),
                            subtitle: Text('Show all detected items without verification filter'),
                            value: _showAllResults,
                            onChanged: (value) {
                              setState(() {
                                _showAllResults = value;
                              });
                            },
                          ),
                        ],
                      ),
                    ),
                  ),
                  SizedBox(height: 24),
                  if (scanProvider.error != null)
                    Card(
                      color: Colors.red.shade50,
                      child: Padding(
                        padding: EdgeInsets.all(16),
                        child: Row(
                          children: [
                            Icon(Icons.error, color: Colors.red),
                            SizedBox(width: 16),
                            Expanded(
                              child: Text(
                                scanProvider.error!,
                                style: TextStyle(color: Colors.red),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: (scanProvider.isLoading || 
                                 (authProvider.quotaStatus != null && 
                                  !authProvider.quotaStatus!.canScan))
                          ? null
                          : _handleScan,
                      style: ElevatedButton.styleFrom(
                        padding: EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: scanProvider.isLoading
                          ? CircularProgressIndicator(color: Colors.white)
                          : Text(
                              'Start Scan',
                              style: TextStyle(fontSize: 18),
                            ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildQuotaCard(quotaStatus) {
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
                  canScan ? Icons.check_circle : Icons.error,
                  color: canScan ? Colors.green : Colors.red,
                ),
                SizedBox(width: 8),
                Text(
                  'Kuota Scan',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            SizedBox(height: 12),
            if (isUnlimited)
              Text(
                'Unlimited - Anda dapat melakukan scan tanpa batas',
                style: TextStyle(fontWeight: FontWeight.w500),
              )
            else
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Terpakai: $used/$limit • Sisa: $remaining',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: canScan ? Colors.green : Colors.red,
                    ),
                  ),
                  SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: limit > 0 ? used / limit : 0,
                    backgroundColor: Colors.grey.shade300,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      canScan ? Colors.green : Colors.red,
                    ),
                  ),
                  if (!canScan)
                    Padding(
                      padding: EdgeInsets.only(top: 8),
                      child: Text(
                        'Kuota habis! Hubungi admin untuk meningkatkan kuota.',
                        style: TextStyle(color: Colors.red, fontSize: 12),
                      ),
                    ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
