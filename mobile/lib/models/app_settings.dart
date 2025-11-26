import 'package:flutter/material.dart';

/// Application settings model
/// Stores user preferences and sync with Bridge
class AppSettings {
  // Audio
  final double micSensitivity;
  final String ttsVoice;
  final double ttsVolume;
  final bool hapticFeedback;

  // Checklist
  final bool autoVerification;
  final bool voiceAnnouncements;

  // Appearance
  final ThemeMode themeMode;

  const AppSettings({
    this.micSensitivity = 0.5,
    this.ttsVoice = 'ljspeech',
    this.ttsVolume = 0.8,
    this.hapticFeedback = true,
    this.autoVerification = true,
    this.voiceAnnouncements = true,
    this.themeMode = ThemeMode.dark,
  });

  /// Create from JSON (SharedPreferences)
  factory AppSettings.fromJson(Map<String, dynamic> json) {
    return AppSettings(
      micSensitivity: json['mic_sensitivity'] ?? 0.5,
      ttsVoice: json['tts_voice'] ?? 'ljspeech',
      ttsVolume: json['tts_volume'] ?? 0.8,
      hapticFeedback: json['haptic_feedback'] ?? true,
      autoVerification: json['auto_verification'] ?? true,
      voiceAnnouncements: json['voice_announcements'] ?? true,
      themeMode: _themeModeFromString(json['theme_mode'] ?? 'dark'),
    );
  }

  /// Convert to JSON (SharedPreferences)
  Map<String, dynamic> toJson() {
    return {
      'mic_sensitivity': micSensitivity,
      'tts_voice': ttsVoice,
      'tts_volume': ttsVolume,
      'haptic_feedback': hapticFeedback,
      'auto_verification': autoVerification,
      'voice_announcements': voiceAnnouncements,
      'theme_mode': themeMode.name,
    };
  }

  /// Copy with modifications
  AppSettings copyWith({
    double? micSensitivity,
    String? ttsVoice,
    double? ttsVolume,
    bool? hapticFeedback,
    bool? autoVerification,
    bool? voiceAnnouncements,
    ThemeMode? themeMode,
  }) {
    return AppSettings(
      micSensitivity: micSensitivity ?? this.micSensitivity,
      ttsVoice: ttsVoice ?? this.ttsVoice,
      ttsVolume: ttsVolume ?? this.ttsVolume,
      hapticFeedback: hapticFeedback ?? this.hapticFeedback,
      autoVerification: autoVerification ?? this.autoVerification,
      voiceAnnouncements: voiceAnnouncements ?? this.voiceAnnouncements,
      themeMode: themeMode ?? this.themeMode,
    );
  }

  static ThemeMode _themeModeFromString(String mode) {
    switch (mode) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      default:
        return ThemeMode.dark;
    }
  }
}

/// TTS Voice metadata (from Bridge API)
class TtsVoice {
  final String id;
  final String displayName;
  final String gender;
  final String accent;
  final String quality;
  final String license;
  final String filePrefix;
  final bool installed;
  final double sizeMb;

  const TtsVoice({
    required this.id,
    required this.displayName,
    required this.gender,
    required this.accent,
    required this.quality,
    required this.license,
    required this.filePrefix,
    this.installed = false,
    this.sizeMb = 0,
  });

  factory TtsVoice.fromJson(Map<String, dynamic> json) {
    return TtsVoice(
      id: json['id'] ?? '',
      displayName: json['display_name'] ?? '',
      gender: json['gender'] ?? '',
      accent: json['accent'] ?? '',
      quality: json['quality'] ?? '',
      license: json['license'] ?? '',
      filePrefix: json['file_prefix'] ?? '',
      installed: json['installed'] ?? false,
      sizeMb: (json['size_mb'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'display_name': displayName,
      'gender': gender,
      'accent': accent,
      'quality': quality,
      'license': license,
      'file_prefix': filePrefix,
      'installed': installed,
      'size_mb': sizeMb,
    };
  }
}
