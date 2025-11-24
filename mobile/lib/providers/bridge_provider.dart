import 'dart:async';
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../core/constants/app_constants.dart';

// =============================================================================
// Connection State
// =============================================================================

enum ConnectionStatus {
  disconnected,
  connecting,
  connected,
  error,
  reconnecting,
}

class BridgeConnectionState {
  final ConnectionStatus status;
  final String? bridgeIp;
  final int? bridgePort;
  final String? sessionToken;
  final String? errorMessage;
  final DateTime? connectedAt;

  const BridgeConnectionState({
    this.status = ConnectionStatus.disconnected,
    this.bridgeIp,
    this.bridgePort,
    this.sessionToken,
    this.errorMessage,
    this.connectedAt,
  });

  bool get isConnected => status == ConnectionStatus.connected;

  BridgeConnectionState copyWith({
    ConnectionStatus? status,
    String? bridgeIp,
    int? bridgePort,
    String? sessionToken,
    String? errorMessage,
    DateTime? connectedAt,
  }) {
    return BridgeConnectionState(
      status: status ?? this.status,
      bridgeIp: bridgeIp ?? this.bridgeIp,
      bridgePort: bridgePort ?? this.bridgePort,
      sessionToken: sessionToken ?? this.sessionToken,
      errorMessage: errorMessage ?? this.errorMessage,
      connectedAt: connectedAt ?? this.connectedAt,
    );
  }
}

// =============================================================================
// Sim Data State
// =============================================================================

class SimData {
  // Connection
  final bool simConnected;

  // Position
  final double latitude;
  final double longitude;
  final double altitude;
  final double altitudeAgl;
  final double heading;
  final double track;

  // Speed
  final double indicatedSpeed;
  final double trueSpeed;
  final double groundSpeed;
  final double mach;
  final double verticalSpeed;

  // Aircraft state
  final int gearPosition;
  final int flapsPosition;
  final bool spoilersArmed;
  final bool onGround;
  final String? aircraft;
  final String? flightPhase;

  // Fuel
  final double fuelTotalKg;
  final double fuelFlowKgH;
  final int fuelEnduranceMin;
  final double fuelPercent;

  // Navigation
  final double nav1Freq;
  final String? nav1Ident;
  final double nav1Dme;
  final double nav2Freq;
  final String? nav2Ident;
  final double nav2Dme;

  // Environment
  final double windDirection;
  final double windSpeed;
  final double oat;
  final double qnh;

  const SimData({
    this.simConnected = false,
    this.latitude = 0,
    this.longitude = 0,
    this.altitude = 0,
    this.altitudeAgl = 0,
    this.heading = 0,
    this.track = 0,
    this.indicatedSpeed = 0,
    this.trueSpeed = 0,
    this.groundSpeed = 0,
    this.mach = 0,
    this.verticalSpeed = 0,
    this.gearPosition = 0,
    this.flapsPosition = 0,
    this.spoilersArmed = false,
    this.onGround = true,
    this.aircraft,
    this.flightPhase,
    this.fuelTotalKg = 0,
    this.fuelFlowKgH = 0,
    this.fuelEnduranceMin = 0,
    this.fuelPercent = 0,
    this.nav1Freq = 0,
    this.nav1Ident,
    this.nav1Dme = 0,
    this.nav2Freq = 0,
    this.nav2Ident,
    this.nav2Dme = 0,
    this.windDirection = 0,
    this.windSpeed = 0,
    this.oat = 0,
    this.qnh = 1013,
  });

  // Convenience getters
  double get speed => indicatedSpeed; // Alias for compatibility

  factory SimData.fromJson(Map<String, dynamic> json) {
    // Handle nested data structure from MOBILE_DESIGN.md
    final position = json['position'] as Map<String, dynamic>? ?? {};
    final speed = json['speed'] as Map<String, dynamic>? ?? {};
    final aircraft = json['aircraft'] as Map<String, dynamic>? ?? {};
    final fuel = json['fuel'] as Map<String, dynamic>? ?? {};
    final navigation = json['navigation'] as Map<String, dynamic>? ?? {};
    final environment = json['environment'] as Map<String, dynamic>? ?? {};

    return SimData(
      simConnected: json['connected'] ?? json['sim_connected'] ?? false,
      // Position - try nested first, then flat
      latitude: (position['latitude'] ?? json['latitude'] ?? 0).toDouble(),
      longitude: (position['longitude'] ?? json['longitude'] ?? 0).toDouble(),
      altitude: (position['altitude_msl'] ?? json['altitude'] ?? 0).toDouble(),
      altitudeAgl: (position['altitude_agl'] ?? json['altitude_agl'] ?? 0).toDouble(),
      heading: (position['heading'] ?? json['heading'] ?? 0).toDouble(),
      track: (position['track'] ?? json['track'] ?? 0).toDouble(),
      // Speed
      indicatedSpeed: (speed['indicated'] ?? json['speed'] ?? json['indicated_speed'] ?? 0).toDouble(),
      trueSpeed: (speed['true'] ?? json['true_speed'] ?? 0).toDouble(),
      groundSpeed: (speed['ground'] ?? json['ground_speed'] ?? 0).toDouble(),
      mach: (speed['mach'] ?? json['mach'] ?? 0).toDouble(),
      verticalSpeed: (speed['vertical'] ?? json['vertical_speed'] ?? 0).toDouble(),
      // Aircraft
      gearPosition: aircraft['gear_position'] ?? json['gear_position'] ?? 0,
      flapsPosition: aircraft['flaps_index'] ?? json['flaps_position'] ?? 0,
      spoilersArmed: aircraft['spoilers_armed'] ?? json['spoilers_armed'] ?? false,
      onGround: json['on_ground'] ?? true,
      aircraft: aircraft['title'] ?? json['aircraft'],
      flightPhase: json['flight_phase'],
      // Fuel
      fuelTotalKg: (fuel['total_kg'] ?? json['fuel_total_kg'] ?? 0).toDouble(),
      fuelFlowKgH: (fuel['flow_kg_h'] ?? json['fuel_flow'] ?? 0).toDouble(),
      fuelEnduranceMin: fuel['endurance_min'] ?? json['fuel_endurance'] ?? 0,
      fuelPercent: (json['fuel_percent'] ?? 0).toDouble(),
      // Navigation
      nav1Freq: (navigation['nav1_freq'] ?? json['nav1_freq'] ?? 0).toDouble(),
      nav1Ident: navigation['nav1_ident'] ?? json['nav1_ident'],
      nav1Dme: (navigation['nav1_dme'] ?? json['nav1_dme'] ?? 0).toDouble(),
      nav2Freq: (navigation['nav2_freq'] ?? json['nav2_freq'] ?? 0).toDouble(),
      nav2Ident: navigation['nav2_ident'] ?? json['nav2_ident'],
      nav2Dme: (navigation['nav2_dme'] ?? json['nav2_dme'] ?? 0).toDouble(),
      // Environment
      windDirection: (environment['wind_direction'] ?? json['wind_direction'] ?? 0).toDouble(),
      windSpeed: (environment['wind_speed'] ?? json['wind_speed'] ?? 0).toDouble(),
      oat: (environment['oat'] ?? json['oat'] ?? 0).toDouble(),
      qnh: (environment['qnh'] ?? json['qnh'] ?? 1013).toDouble(),
    );
  }
}

// =============================================================================
// Command Result
// =============================================================================

class CommandResult {
  final bool success;
  final String command;
  final String? action;
  final String message;
  final String? ttsAudio;

  const CommandResult({
    required this.success,
    required this.command,
    this.action,
    required this.message,
    this.ttsAudio,
  });

  factory CommandResult.fromJson(Map<String, dynamic> json) {
    return CommandResult(
      success: json['success'] ?? false,
      command: json['command'] ?? '',
      action: json['action'],
      message: json['message'] ?? '',
      ttsAudio: json['tts_audio'],
    );
  }
}

// =============================================================================
// Bridge Notifier
// =============================================================================

class BridgeNotifier extends StateNotifier<BridgeConnectionState> {
  // ignore: unused_field - kept for future use with other providers
  BridgeNotifier(Ref ref) : super(const BridgeConnectionState());
  Dio? _dio;
  WebSocketChannel? _wsChannel;
  StreamSubscription? _wsSubscription;
  Timer? _reconnectTimer;
  Timer? _pingTimer;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 5;

  final _simDataController = StreamController<SimData>.broadcast();
  Stream<SimData> get simDataStream => _simDataController.stream;

  @override
  void dispose() {
    _cleanup();
    _simDataController.close();
    super.dispose();
  }

  void _cleanup() {
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();
    _wsSubscription?.cancel();
    _wsChannel?.sink.close();
    _wsChannel = null;
    _dio = null;
  }

  /// Load saved connection and try to reconnect
  /// Silently fails if connection cannot be established
  Future<void> loadSavedConnection() async {
    final prefs = await SharedPreferences.getInstance();
    final ip = prefs.getString(AppConstants.keyBridgeIp);
    final port = prefs.getInt(AppConstants.keyBridgePort);
    final token = prefs.getString(AppConstants.keySessionToken);

    if (ip != null && port != null && token != null) {
      // Try to reconnect with saved credentials - silently fail
      final success = await connect(ip, port, token, saveConnection: false);
      if (!success) {
        // Reset to clean disconnected state (no error shown)
        state = const BridgeConnectionState(status: ConnectionStatus.disconnected);
      }
    }
  }

  /// Save connection info for later
  Future<void> _saveConnection(String ip, int port, String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConstants.keyBridgeIp, ip);
    await prefs.setInt(AppConstants.keyBridgePort, port);
    await prefs.setString(AppConstants.keySessionToken, token);
    await prefs.setString(
      AppConstants.keyLastConnected,
      DateTime.now().toIso8601String(),
    );
  }

  /// Clear saved connection
  Future<void> clearSavedConnection() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(AppConstants.keyBridgeIp);
    await prefs.remove(AppConstants.keyBridgePort);
    await prefs.remove(AppConstants.keySessionToken);
  }

  /// Connect to PC Bridge
  Future<bool> connect(
    String ip,
    int port,
    String sessionToken, {
    bool saveConnection = true,
  }) async {
    state = state.copyWith(
      status: ConnectionStatus.connecting,
      bridgeIp: ip,
      bridgePort: port,
      sessionToken: sessionToken,
      errorMessage: null,
    );

    final baseUrl = 'http://$ip:$port';

    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 10),
      headers: {
        AppConstants.sessionTokenHeader: sessionToken,
      },
    ));

    // Verify connection
    try {
      final response = await _dio!.post('/api/connect/verify');
      if (response.data['status'] != 'connected') {
        throw Exception('Verification failed');
      }
    } catch (e) {
      state = state.copyWith(
        status: ConnectionStatus.error,
        errorMessage: 'Failed to verify connection: $e',
      );
      return false;
    }

    // Establish WebSocket
    try {
      final wsUrl = 'ws://$ip:$port/ws/stream/$sessionToken';
      _wsChannel = WebSocketChannel.connect(Uri.parse(wsUrl));

      _wsSubscription = _wsChannel!.stream.listen(
        _handleWebSocketMessage,
        onError: _handleWebSocketError,
        onDone: _handleWebSocketClosed,
      );

      // Start ping timer
      _startPingTimer();

      state = state.copyWith(
        status: ConnectionStatus.connected,
        connectedAt: DateTime.now(),
      );

      _reconnectAttempts = 0;

      if (saveConnection) {
        await _saveConnection(ip, port, sessionToken);
      }

      return true;
    } catch (e) {
      state = state.copyWith(
        status: ConnectionStatus.error,
        errorMessage: 'Failed to establish WebSocket: $e',
      );
      return false;
    }
  }

  /// Disconnect from PC Bridge
  void disconnect() {
    _cleanup();
    state = const BridgeConnectionState(status: ConnectionStatus.disconnected);
  }

  /// Send direct command via HTTP API
  Future<CommandResult> sendCommand(String command) async {
    if (_dio == null || !state.isConnected) {
      return const CommandResult(
        success: false,
        command: '',
        message: 'Not connected',
      );
    }

    try {
      final response = await _dio!.post('/api/sim/command/$command');
      return CommandResult(
        success: response.data['success'] ?? false,
        command: command,
        action: response.data['event'],
        message: response.data['message'] ?? 'Command executed',
      );
    } catch (e) {
      return CommandResult(
        success: false,
        command: command,
        message: 'Failed: $e',
      );
    }
  }

  /// Send audio command
  Future<CommandResult> sendAudioCommand(List<int> audioData) async {
    if (_dio == null || !state.isConnected) {
      return const CommandResult(
        success: false,
        command: '',
        message: 'Not connected',
      );
    }

    try {
      final formData = FormData.fromMap({
        'audio': MultipartFile.fromBytes(
          audioData,
          filename: 'command.wav',
          contentType: DioMediaType('audio', 'wav'),
        ),
      });

      final response = await _dio!.post(
        '/api/audio/command',
        data: formData,
      );

      return CommandResult.fromJson(response.data);
    } catch (e) {
      return CommandResult(
        success: false,
        command: '',
        message: 'Failed to send audio: $e',
      );
    }
  }

  /// Get sim status via HTTP
  Future<SimData?> getSimStatus() async {
    if (_dio == null || !state.isConnected) return null;

    try {
      final response = await _dio!.get('/api/sim/status');
      return SimData.fromJson(response.data);
    } catch (e) {
      return null;
    }
  }

  void _handleWebSocketMessage(dynamic message) {
    try {
      final data = jsonDecode(message as String);
      final type = data['type'] as String?;

      switch (type) {
        case 'sim_data':
          final simData = SimData.fromJson(data['data'] ?? data);
          _simDataController.add(simData);
          break;
        case 'command_result':
          // Could emit to a separate stream if needed
          break;
        case 'pong':
          // Connection alive
          break;
      }
    } catch (e) {
      // Ignore parse errors
    }
  }

  void _handleWebSocketError(Object error) {
    state = state.copyWith(
      status: ConnectionStatus.error,
      errorMessage: 'WebSocket error: $error',
    );
    _scheduleReconnect();
  }

  void _handleWebSocketClosed() {
    if (state.status == ConnectionStatus.connected ||
        state.status == ConnectionStatus.reconnecting) {
      state = state.copyWith(status: ConnectionStatus.disconnected);
      _scheduleReconnect();
    }
  }

  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (_wsChannel != null && state.isConnected) {
        _wsChannel!.sink.add(jsonEncode({'type': 'ping'}));
      }
    });
  }

  void _scheduleReconnect() {
    if (_reconnectAttempts >= _maxReconnectAttempts) {
      state = state.copyWith(
        status: ConnectionStatus.error,
        errorMessage: 'Max reconnection attempts reached',
      );
      return;
    }

    if (state.bridgeIp == null ||
        state.bridgePort == null ||
        state.sessionToken == null) {
      return;
    }

    _reconnectAttempts++;
    state = state.copyWith(status: ConnectionStatus.reconnecting);

    final delay = Duration(seconds: _reconnectAttempts * 2);
    _reconnectTimer = Timer(delay, () {
      if (state.status == ConnectionStatus.reconnecting) {
        connect(
          state.bridgeIp!,
          state.bridgePort!,
          state.sessionToken!,
          saveConnection: false,
        );
      }
    });
  }
}

// =============================================================================
// Providers
// =============================================================================

final bridgeProvider = StateNotifierProvider<BridgeNotifier, BridgeConnectionState>(
  (ref) => BridgeNotifier(ref),
);

final simDataStreamProvider = StreamProvider<SimData>((ref) {
  final bridge = ref.watch(bridgeProvider.notifier);
  return bridge.simDataStream;
});

final isConnectedProvider = Provider<bool>((ref) {
  return ref.watch(bridgeProvider).isConnected;
});

final connectionStatusProvider = Provider<ConnectionStatus>((ref) {
  return ref.watch(bridgeProvider).status;
});
