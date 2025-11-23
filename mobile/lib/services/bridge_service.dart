import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

/// Service for communicating with the PC Bridge.
class BridgeService {
  static final BridgeService _instance = BridgeService._internal();
  factory BridgeService() => _instance;
  BridgeService._internal();

  Dio? _dio;
  WebSocketChannel? _wsChannel;
  String? _sessionToken;
  String? _baseUrl;

  final _simDataController = StreamController<SimData>.broadcast();
  final _connectionStateController = StreamController<ConnectionState>.broadcast();

  Stream<SimData> get simDataStream => _simDataController.stream;
  Stream<ConnectionState> get connectionStateStream => _connectionStateController.stream;

  bool get isConnected => _wsChannel != null;

  /// Connect to the PC Bridge.
  Future<void> connect(String ip, int port, String sessionToken) async {
    _baseUrl = 'http://$ip:$port';
    _sessionToken = sessionToken;

    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl!,
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 10),
      headers: {
        'X-Session-Token': sessionToken,
      },
    ));

    // Verify connection
    try {
      final response = await _dio!.post('/api/connect/verify');
      if (response.data['status'] != 'connected') {
        throw Exception('Connection verification failed');
      }
    } catch (e) {
      throw Exception('Failed to verify connection: $e');
    }

    // Establish WebSocket
    try {
      final wsUrl = 'ws://$ip:$port/ws/stream/$sessionToken';
      _wsChannel = WebSocketChannel.connect(Uri.parse(wsUrl));

      _wsChannel!.stream.listen(
        _handleWebSocketMessage,
        onError: _handleWebSocketError,
        onDone: _handleWebSocketClosed,
      );

      _connectionStateController.add(ConnectionState.connected);
    } catch (e) {
      throw Exception('Failed to establish WebSocket: $e');
    }
  }

  /// Disconnect from the PC Bridge.
  void disconnect() {
    _wsChannel?.sink.close();
    _wsChannel = null;
    _dio = null;
    _sessionToken = null;
    _connectionStateController.add(ConnectionState.disconnected);
  }

  /// Send audio data for transcription and command execution.
  Future<CommandResult> sendAudioCommand(List<int> audioData) async {
    if (_dio == null) {
      throw Exception('Not connected');
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
      throw Exception('Failed to send audio: $e');
    }
  }

  /// Send a direct command (button press).
  Future<void> sendDirectCommand(String command) async {
    if (_wsChannel == null) {
      throw Exception('Not connected');
    }

    _wsChannel!.sink.add(jsonEncode({
      'type': 'command',
      'command': command,
    }));
  }

  void _handleWebSocketMessage(dynamic message) {
    try {
      final data = jsonDecode(message as String);
      final type = data['type'] as String;

      switch (type) {
        case 'sim_data':
          _simDataController.add(SimData.fromJson(data['data']));
          break;
        case 'command_result':
          // Handle command result
          break;
        case 'pong':
          // Connection alive
          break;
      }
    } catch (e) {
      print('Error parsing WebSocket message: $e');
    }
  }

  void _handleWebSocketError(Object error) {
    print('WebSocket error: $error');
    _connectionStateController.add(ConnectionState.error);
  }

  void _handleWebSocketClosed() {
    print('WebSocket closed');
    _connectionStateController.add(ConnectionState.disconnected);
  }

  void dispose() {
    _simDataController.close();
    _connectionStateController.close();
    disconnect();
  }
}

enum ConnectionState {
  disconnected,
  connecting,
  connected,
  error,
}

class SimData {
  final bool connected;
  final double altitude;
  final double speed;
  final double heading;
  final int gearPosition;
  final int flapsPosition;
  final bool onGround;

  SimData({
    required this.connected,
    required this.altitude,
    required this.speed,
    required this.heading,
    required this.gearPosition,
    required this.flapsPosition,
    required this.onGround,
  });

  factory SimData.fromJson(Map<String, dynamic> json) {
    return SimData(
      connected: json['connected'] ?? false,
      altitude: (json['altitude'] ?? 0).toDouble(),
      speed: (json['speed'] ?? 0).toDouble(),
      heading: (json['heading'] ?? 0).toDouble(),
      gearPosition: json['gear_position'] ?? 0,
      flapsPosition: json['flaps_position'] ?? 0,
      onGround: json['on_ground'] ?? true,
    );
  }
}

class CommandResult {
  final bool success;
  final String command;
  final String? action;
  final String message;
  final String? ttsAudio;

  CommandResult({
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
