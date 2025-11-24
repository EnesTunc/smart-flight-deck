/// Application-wide constants
class AppConstants {
  AppConstants._();

  // ===========================================
  // App Info
  // ===========================================

  static const String appName = 'Smart Flight Deck';
  static const String appVersion = '0.1.0';
  static const String appDescription = 'Professional EFB + Voice Assistant for MSFS';

  // ===========================================
  // Network
  // ===========================================

  /// Default PC Bridge port
  static const int defaultPort = 8000;

  /// WebSocket reconnect delay (ms)
  static const int wsReconnectDelay = 3000;

  /// HTTP request timeout (ms)
  static const int httpTimeout = 10000;

  /// Session token header
  static const String sessionTokenHeader = 'X-Session-Token';

  // ===========================================
  // Audio
  // ===========================================

  /// Audio sample rate for recording
  static const int audioSampleRate = 16000;

  /// Audio channels (mono)
  static const int audioChannels = 1;

  /// Max recording duration (seconds)
  static const int maxRecordingDuration = 30;

  /// PTT hold delay before recording starts (ms)
  static const int pttHoldDelay = 100;

  // ===========================================
  // UI
  // ===========================================

  /// Animation duration (ms)
  static const int animationDuration = 200;

  /// Minimum touch target size (dp)
  static const double minTouchTarget = 48.0;

  /// PTT button size ratio (of screen width)
  static const double pttButtonRatio = 0.35;

  /// Border radius
  static const double borderRadiusSmall = 4.0;
  static const double borderRadiusMedium = 8.0;
  static const double borderRadiusLarge = 16.0;

  /// Padding
  static const double paddingSmall = 8.0;
  static const double paddingMedium = 16.0;
  static const double paddingLarge = 24.0;

  // ===========================================
  // Data Refresh Rates
  // ===========================================

  /// Sim data update rate (Hz)
  static const int simDataUpdateRate = 2;

  /// Position update rate for map (Hz)
  static const int mapUpdateRate = 1;

  // ===========================================
  // Storage Keys
  // ===========================================

  static const String keySessionToken = 'session_token';
  static const String keyBridgeIp = 'bridge_ip';
  static const String keyBridgePort = 'bridge_port';
  static const String keyLastConnected = 'last_connected';
  static const String keyThemeMode = 'theme_mode';
  static const String keyUnits = 'units';

  // ===========================================
  // Routes
  // ===========================================

  static const String routeHome = '/';
  static const String routeConnection = '/connection';
  static const String routeQrScanner = '/qr-scanner';
  static const String routeMap = '/map';
  static const String routeFlightData = '/flight-data';
  static const String routeChecklist = '/checklist';
  static const String routeAirport = '/airport';
  static const String routeSettings = '/settings';
}
