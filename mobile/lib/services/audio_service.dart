import 'dart:async';
import 'dart:io';
import 'dart:typed_data';

import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:audioplayers/audioplayers.dart';

/// Service for audio recording and playback.
class AudioService {
  static final AudioService _instance = AudioService._internal();
  factory AudioService() => _instance;
  AudioService._internal();

  final AudioRecorder _recorder = AudioRecorder();
  final AudioPlayer _player = AudioPlayer();

  bool _isRecording = false;
  String? _currentRecordingPath;

  bool get isRecording => _isRecording;

  /// Check and request microphone permission.
  Future<bool> requestPermission() async {
    return await _recorder.hasPermission();
  }

  /// Start recording audio.
  Future<void> startRecording() async {
    if (_isRecording) return;

    final hasPermission = await _recorder.hasPermission();
    if (!hasPermission) {
      throw Exception('Microphone permission not granted');
    }

    // Get temp directory for recording
    final directory = await getTemporaryDirectory();
    _currentRecordingPath = '${directory.path}/command_${DateTime.now().millisecondsSinceEpoch}.wav';

    // Start recording
    await _recorder.start(
      const RecordConfig(
        encoder: AudioEncoder.wav,
        sampleRate: 16000,  // Whisper expects 16kHz
        numChannels: 1,     // Mono
        bitRate: 256000,
      ),
      path: _currentRecordingPath!,
    );

    _isRecording = true;
  }

  /// Stop recording and return the audio data.
  Future<Uint8List?> stopRecording() async {
    if (!_isRecording) return null;

    final path = await _recorder.stop();
    _isRecording = false;

    if (path == null || _currentRecordingPath == null) {
      return null;
    }

    // Read the recorded file
    final file = File(_currentRecordingPath!);
    if (await file.exists()) {
      final data = await file.readAsBytes();
      // Clean up the file
      await file.delete();
      return data;
    }

    return null;
  }

  /// Cancel recording without saving.
  Future<void> cancelRecording() async {
    if (!_isRecording) return;

    await _recorder.stop();
    _isRecording = false;

    // Clean up the file
    if (_currentRecordingPath != null) {
      final file = File(_currentRecordingPath!);
      if (await file.exists()) {
        await file.delete();
      }
    }
  }

  /// Play audio from bytes (TTS response).
  Future<void> playAudio(Uint8List audioData) async {
    await _player.play(BytesSource(audioData));
  }

  /// Play audio from base64 string.
  Future<void> playAudioBase64(String base64Audio) async {
    // Remove data URL prefix if present
    final cleanBase64 = base64Audio.replaceFirst(
      RegExp(r'data:audio/\w+;base64,'),
      '',
    );

    // Decode and play
    // Note: This is a simplified version. In production,
    // you might need to save to a temp file first.
  }

  /// Get current audio amplitude (for visualization).
  Future<double> getAmplitude() async {
    if (!_isRecording) return 0.0;

    final amplitude = await _recorder.getAmplitude();
    // Normalize to 0-1 range
    // dB typically ranges from -160 to 0
    final normalized = (amplitude.current + 60) / 60;
    return normalized.clamp(0.0, 1.0);
  }

  void dispose() {
    _recorder.dispose();
    _player.dispose();
  }
}
