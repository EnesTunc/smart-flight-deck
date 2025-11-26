import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:dio/dio.dart';
import '../models/app_settings.dart';
import 'bridge_provider.dart';

/// Settings state notifier
/// Manages app settings with local storage and Bridge sync
class SettingsNotifier extends StateNotifier<AppSettings> {
  final SharedPreferences _prefs;
  final Dio? _dio;

  SettingsNotifier(this._prefs, [this._dio])
      : super(AppSettings.fromJson(_loadFromPrefs(_prefs)));

  static Map<String, dynamic> _loadFromPrefs(SharedPreferences prefs) {
    return {
      'mic_sensitivity': prefs.getDouble('mic_sensitivity'),
      'tts_voice': prefs.getString('tts_voice'),
      'tts_volume': prefs.getDouble('tts_volume'),
      'haptic_feedback': prefs.getBool('haptic_feedback'),
      'auto_verification': prefs.getBool('auto_verification'),
      'voice_announcements': prefs.getBool('voice_announcements'),
      'theme_mode': prefs.getString('theme_mode'),
    };
  }

  /// Save current state to SharedPreferences
  Future<void> _saveToPrefs() async {
    final json = state.toJson();
    await _prefs.setDouble('mic_sensitivity', json['mic_sensitivity']);
    await _prefs.setString('tts_voice', json['tts_voice']);
    await _prefs.setDouble('tts_volume', json['tts_volume']);
    await _prefs.setBool('haptic_feedback', json['haptic_feedback']);
    await _prefs.setBool('auto_verification', json['auto_verification']);
    await _prefs.setBool('voice_announcements', json['voice_announcements']);
    await _prefs.setString('theme_mode', json['theme_mode']);
  }

  /// Sync TTS settings to Bridge
  Future<bool> _syncToBridge() async {
    if (_dio == null) return false;

    try {
      await _dio!.put(
        '/api/settings',
        data: {
          'tts_enabled': state.voiceAnnouncements,
          'tts_voice': state.ttsVoice,
        },
      );
      return true;
    } catch (e) {
      debugPrint('Failed to sync settings to Bridge: $e');
      return false;
    }
  }

  /// Update microphone sensitivity
  Future<void> setMicSensitivity(double value) async {
    state = state.copyWith(micSensitivity: value.clamp(0.0, 1.0));
    await _saveToPrefs();
  }

  /// Update TTS voice
  Future<void> setTtsVoice(String voiceId) async {
    state = state.copyWith(ttsVoice: voiceId);
    await _saveToPrefs();
    await _syncToBridge();
  }

  /// Update TTS volume
  Future<void> setTtsVolume(double value) async {
    state = state.copyWith(ttsVolume: value.clamp(0.0, 1.0));
    await _saveToPrefs();
  }

  /// Update haptic feedback
  Future<void> setHapticFeedback(bool enabled) async {
    state = state.copyWith(hapticFeedback: enabled);
    await _saveToPrefs();
  }

  /// Update auto verification
  Future<void> setAutoVerification(bool enabled) async {
    state = state.copyWith(autoVerification: enabled);
    await _saveToPrefs();
    await _syncToBridge();
  }

  /// Update voice announcements
  Future<void> setVoiceAnnouncements(bool enabled) async {
    state = state.copyWith(voiceAnnouncements: enabled);
    await _saveToPrefs();
    await _syncToBridge();
  }

  /// Update theme mode
  Future<void> setThemeMode(ThemeMode mode) async {
    state = state.copyWith(themeMode: mode);
    await _saveToPrefs();
  }

  /// Load settings from Bridge API
  Future<void> loadFromBridge() async {
    if (_dio == null) return;

    try {
      final response = await _dio!.get('/api/settings');
      if (response.statusCode == 200) {
        final data = response.data;
        state = state.copyWith(
          ttsVoice: data['tts_voice'] ?? state.ttsVoice,
          voiceAnnouncements: data['tts_enabled'] ?? state.voiceAnnouncements,
          autoVerification: data['verification_enabled'] ?? state.autoVerification,
        );
        await _saveToPrefs();
      }
    } catch (e) {
      debugPrint('Failed to load settings from Bridge: $e');
    }
  }
}

/// Settings provider
final settingsProvider =
    StateNotifierProvider<SettingsNotifier, AppSettings>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  final bridgeState = ref.watch(bridgeProvider);

  // Create Dio instance if connected
  Dio? dio;
  if (bridgeState.status == ConnectionStatus.connected &&
      bridgeState.bridgeIp != null &&
      bridgeState.bridgePort != null) {
    dio = Dio(BaseOptions(
      baseUrl: 'http://${bridgeState.bridgeIp}:${bridgeState.bridgePort}',
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 10),
    ));
  }

  return SettingsNotifier(prefs, dio);
});

/// SharedPreferences provider
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('SharedPreferences must be overridden');
});

/// Available TTS voices provider
final availableVoicesProvider = FutureProvider<List<TtsVoice>>((ref) async {
  final bridgeState = ref.watch(bridgeProvider);
  if (bridgeState.status != ConnectionStatus.connected ||
      bridgeState.bridgeIp == null ||
      bridgeState.bridgePort == null) {
    return [];
  }

  final dio = Dio(BaseOptions(
    baseUrl: 'http://${bridgeState.bridgeIp}:${bridgeState.bridgePort}',
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 10),
  ));

  try {
    final response = await dio.get('/api/tts/voices');
    if (response.statusCode == 200) {
      final List voices = response.data['voices'] ?? [];
      return voices.map((v) => TtsVoice.fromJson(v)).toList();
    }
  } catch (e) {
    debugPrint('Failed to load TTS voices: $e');
  }
  return [];
});

/// Download TTS voice
final downloadVoiceProvider =
    FutureProvider.family<bool, String>((ref, voiceId) async {
  final bridgeState = ref.watch(bridgeProvider);
  if (bridgeState.status != ConnectionStatus.connected ||
      bridgeState.bridgeIp == null ||
      bridgeState.bridgePort == null) {
    return false;
  }

  final dio = Dio(BaseOptions(
    baseUrl: 'http://${bridgeState.bridgeIp}:${bridgeState.bridgePort}',
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 30),
  ));

  try {
    final response = await dio.post('/api/tts/download?voice_id=$voiceId');
    return response.statusCode == 200 && response.data['success'] == true;
  } catch (e) {
    debugPrint('Failed to download voice: $e');
    return false;
  }
});
