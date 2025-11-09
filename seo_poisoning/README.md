# SEO Poisoning Detector Mobile App

A Flutter mobile application that consumes the SEO Poisoning Detection API to scan domains for malicious content.

## Features

- **Domain Scanning**: Scan domains for SEO poisoning with Google search and crawling
- **Dashboard**: View statistics and rankings of infected domains
- **Scan History**: Browse previous scan results with filtering
- **Real-time Results**: Get instant feedback on scan progress and results

## Prerequisites

- Flutter SDK (version 2.19.0 or higher)
- Android Studio or VS Code with Flutter extensions
- Running SEO Poisoning Detection API server (see main project README)

## Setup

1. **Install Dependencies**
   ```bash
   flutter pub get
   ```

2. **Configure API Connection**

   Edit the API configuration in `lib/main_full.dart`:
   ```dart
   final ApiService apiService = ApiService(
     baseUrl: 'http://your-api-server:8000', // Change to your API URL
     apiKey: 'your-secret-api-key', // Change to your API key
   );
   ```

3. **Run the App**
   ```bash
   flutter run
   ```

## API Configuration

The app connects to the FastAPI backend. Make sure:

1. The API server is running on the specified URL
2. The API key matches the one configured in the backend
3. CORS is properly configured for mobile access

## App Structure

```
lib/
├── main_full.dart          # Main app with navigation
├── services/
│   └── api_service.dart    # API communication service
└── screens/
    ├── dashboard_screen.dart  # Dashboard with statistics
    └── history_screen.dart    # Scan history browser
```

## Usage

### Domain Scanning
1. Enter the target domain (e.g., `uns.ac.id`)
2. Enter your SerpApi API key
3. Select scan type (Fast or Comprehensive)
4. Toggle backlink analysis if needed
5. Tap "Mulai Pemindaian" to start scanning

### Dashboard
- View overall statistics (total domains, cases, infected domains)
- Browse domain rankings in a table format

### Scan History
- View all previous scan results
- Filter by domain using the search field
- Expand items to see detailed information

## API Endpoints Used

- `POST /scan/domain` - Domain scanning
- `GET /dashboard` - Dashboard statistics
- `GET /scan/history` - Scan history retrieval
- `GET /domain/{domain}/info` - Domain intelligence

## Troubleshooting

### Connection Issues
- Ensure the API server is running and accessible
- Check the API URL and port configuration
- Verify API key authentication

### Build Issues
- Run `flutter clean` and `flutter pub get`
- Check Flutter SDK version compatibility
- Ensure Android/iOS development environment is set up

### API Errors
- Check API server logs for error details
- Verify request parameters match API expectations
- Ensure CORS is properly configured

## Development

To modify the app:

1. **Add New Features**: Create new screens in `lib/screens/`
2. **API Integration**: Add methods to `ApiService` class
3. **UI Components**: Modify existing screens or create new ones

## License

This project is part of the SEO Poisoning Detection system.
