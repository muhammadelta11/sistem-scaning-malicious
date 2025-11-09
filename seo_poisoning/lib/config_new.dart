class Config {
  // For Android emulator: use 10.0.2.2
  // For iOS simulator: use localhost
  // For physical device: use your computer's IP address
  // For macOS Flutter app connecting to Parallels Desktop (Windows VM):
  // Use the Parallels Desktop IP address (check with ipconfig in Windows VM)
  // Example: http://10.211.55.2:8000 or http://10.37.129.2:8000
  static const String apiBaseUrl = 'http://10.211.55.3:8000'; // Adjust this IP

  // Change this to your actual API key
  static const String apiKey = 'your-secret-api-key';
}
