import 'dart:async';
import 'dart:convert';
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

  // Streaming mode
  bool _isStreaming = false;
  StreamController<Uint8List>? _streamController;

  bool get isRecording => _isRecording;
  bool get isStreaming => _isStreaming;

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
    _currentRecordingPath =
        '${directory.path}/command_${DateTime.now().millisecondsSinceEpoch}.wav';

    // Start recording
    await _recorder.start(
      const RecordConfig(
        encoder: AudioEncoder.wav,
        sampleRate: 16000, // Whisper expects 16kHz
        numChannels: 1, // Mono
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
    try {
      // Remove data URL prefix if present
      String cleanBase64 = base64Audio;

      // Handle different data URL formats
      if (base64Audio.contains('base64,')) {
        cleanBase64 = base64Audio.split('base64,').last;
      }

      // Remove any whitespace
      cleanBase64 = cleanBase64.replaceAll(RegExp(r'\s'), '');

      // Decode base64
      final audioBytes = base64Decode(cleanBase64);

      // Save to temp file and play
      final directory = await getTemporaryDirectory();
      final tempFile = File(
          '${directory.path}/tts_${DateTime.now().millisecondsSinceEpoch}.wav');
      await tempFile.writeAsBytes(audioBytes);

      // Play the file
      await _player.play(DeviceFileSource(tempFile.path));

      // Clean up after playback
      _player.onPlayerComplete.first.then((_) async {
        if (await tempFile.exists()) {
          await tempFile.delete();
        }
      });
    } catch (e) {
      throw Exception('Failed to play audio: $e');
    }
  }

  /// Play audio from URL.
  Future<void> playAudioUrl(String url) async {
    await _player.play(UrlSource(url));
  }

  /// Stop current playback.
  Future<void> stopPlayback() async {
    await _player.stop();
  }

  /// Pause current playback.
  Future<void> pausePlayback() async {
    await _player.pause();
  }

  /// Resume paused playback.
  Future<void> resumePlayback() async {
    await _player.resume();
  }

  /// Set playback volume (0.0 to 1.0).
  Future<void> setVolume(double volume) async {
    await _player.setVolume(volume.clamp(0.0, 1.0));
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

  /// Listen for playback state changes.
  Stream<PlayerState> get onPlayerStateChanged => _player.onPlayerStateChanged;

  /// Listen for playback completion.
  Stream<void> get onPlayerComplete => _player.onPlayerComplete;

  /// Start streaming audio (for VAD on server).
  /// Returns stream of audio chunks (PCM16, 16kHz, mono).
  Future<Stream<Uint8List>?> startStreaming() async {
    if (_isStreaming) return null;

    final hasPermission = await _recorder.hasPermission();
    if (!hasPermission) {
      throw Exception('Microphone permission not granted');
    }

    // Use record package's built-in streaming
    final stream = await _recorder.startStream(
      const RecordConfig(
        encoder: AudioEncoder.pcm16bits,  // Raw PCM16 for streaming
        sampleRate: 16000,
        numChannels: 1,
      ),
    );

    _isStreaming = true;
    return stream;
  }

  /// Stop streaming audio.
  Future<void> stopStreaming() async {
    if (!_isStreaming) return;

    await _recorder.stop();
    _isStreaming = false;
  }

  void dispose() {
    _recorder.dispose();
    _player.dispose();
    _streamController?.close();
  }
}

