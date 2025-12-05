import 'dart:async';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/bridge_provider.dart';
import '../providers/settings_provider.dart';
import '../services/audio_service.dart';
import '../theme/app_theme.dart';
import '../models/app_settings.dart';

/// Microphone Toggle button for voice commands.
/// Tap to activate/deactivate recording.
class PTTButton extends ConsumerStatefulWidget {
  const PTTButton({super.key});

  @override
  ConsumerState<PTTButton> createState() => _PTTButtonState();
}

class _PTTButtonState extends ConsumerState<PTTButton>
    with SingleTickerProviderStateMixin {
  final AudioService _audioService = AudioService();

  bool _isRecording = false;
  bool _isProcessing = false;
  String? _lastResult;
  late AnimationController _pulseController;
  StreamSubscription<Uint8List>? _audioStreamSubscription;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);

    // Listen for command results from WebSocket (VAD detections)
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.listen<Map<String, dynamic>?>(
        lastCommandResultProvider,
        (previous, next) {
          if (next != null && mounted) {
            _handleCommandResult(next);
          }
        },
      );
    });
  }

  @override
  void dispose() {
    _audioStreamSubscription?.cancel();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isConnected = ref.watch(isConnectedProvider);

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Status text
        Text(
          _getStatusText(isConnected),
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: _isRecording
                    ? AppTheme.errorColor
                    : _isProcessing
                        ? AppTheme.warningColor
                        : isConnected
                            ? AppTheme.textSecondary
                            : AppTheme.textMuted,
              ),
        ),
        const SizedBox(height: 8),

        // Last result
        if (_lastResult != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              _lastResult!,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.primaryColor,
                  ),
            ),
          ),

        // Mic Toggle Button
        GestureDetector(
          onTap: isConnected ? _toggleRecording : null,
          child: AnimatedBuilder(
            animation: _pulseController,
            builder: (context, child) {
              final scale = _isRecording
                  ? 1.0 + (_pulseController.value * 0.1)
                  : 1.0;

              return Transform.scale(
                scale: scale,
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: _getButtonColor(isConnected),
                    boxShadow: [
                      BoxShadow(
                        color: (_isRecording
                                ? AppTheme.errorColor
                                : isConnected
                                    ? AppTheme.primaryColor
                                    : AppTheme.textMuted)
                            .withOpacity(0.5),
                        blurRadius: _isRecording ? 20 : 10,
                        spreadRadius: _isRecording ? 5 : 2,
                      ),
                    ],
                  ),
                  child: Icon(
                    _getButtonIcon(),
                    size: 48,
                    color: isConnected
                        ? AppTheme.backgroundColor
                        : AppTheme.textMuted,
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  String _getStatusText(bool isConnected) {
    if (!isConnected) return 'Connect to use voice';
    if (_isRecording) return 'Listening... (Tap to stop)';
    if (_isProcessing) return 'Processing...';
    return 'Tap to activate mic';
  }

  Color _getButtonColor(bool isConnected) {
    if (!isConnected) return AppTheme.surfaceColor;
    if (_isRecording) return AppTheme.errorColor;
    if (_isProcessing) return AppTheme.warningColor;
    return AppTheme.primaryColor;
  }

  IconData _getButtonIcon() {
    if (_isRecording) return Icons.mic;
    if (_isProcessing) return Icons.hourglass_top;
    return Icons.mic_none;
  }

  /// Toggle recording on/off
  Future<void> _toggleRecording() async {
    if (_isRecording) {
      await _stopRecording();
    } else {
      await _startRecording();
    }
  }

  Future<void> _startRecording() async {
    final settings = ref.read(settingsProvider);

    // Haptic feedback
    if (settings.hapticFeedback) {
      HapticFeedback.mediumImpact();
    }

    setState(() {
      _lastResult = null;
    });

    try {
      // Check audio source
      if (settings.audioSource == AudioSource.phone) {
        // Phone microphone - start streaming mode with VAD
        ref.read(bridgeProvider.notifier).startAudioStreaming();

        final audioStream = await _audioService.startStreaming();
        if (audioStream != null) {
          _audioStreamSubscription = audioStream.listen(
            (audioChunk) {
              // Send each chunk to bridge for VAD processing
              ref.read(bridgeProvider.notifier).sendAudioChunk(audioChunk);
            },
            onError: (error) {
              _showError('Streaming error: $error');
              _stopRecording();
            },
            cancelOnError: true,
          );
        }
      } else {
        // PC microphone - start PC streaming with VAD
        final success = await ref
            .read(bridgeProvider.notifier)
            .startPcStreaming();

        if (!success) {
          _showError('Failed to start PC microphone');
          return;
        }
      }

      setState(() {
        _isRecording = true;
      });
    } catch (e) {
      _showError('Failed to start recording: $e');
    }
  }

  Future<void> _stopRecording() async {
    if (!_isRecording) return;

    final settings = ref.read(settingsProvider);

    // Haptic feedback
    if (settings.hapticFeedback) {
      HapticFeedback.lightImpact();
    }

    setState(() {
      _isRecording = false;
    });

    try {
      if (settings.audioSource == AudioSource.phone) {
        // Phone microphone - stop streaming
        await _audioStreamSubscription?.cancel();
        _audioStreamSubscription = null;

        await _audioService.stopStreaming();
        ref.read(bridgeProvider.notifier).stopAudioStreaming();
      } else {
        // PC microphone - stop PC streaming
        await ref.read(bridgeProvider.notifier).stopPcStreaming();
      }
    } catch (e) {
      _showError('Failed to stop recording: $e');
    }
  }

  Future<void> _cancelRecording() async {
    if (!_isRecording) return;

    await _audioStreamSubscription?.cancel();
    _audioStreamSubscription = null;

    await _audioService.stopStreaming();
    ref.read(bridgeProvider.notifier).stopAudioStreaming();

    setState(() {
      _isRecording = false;
    });
  }

  void _handleCommandResult(Map<String, dynamic> result) {
    final success = result['success'] as bool? ?? false;
    final command = result['command'] as String? ?? '';
    final message = result['message'] as String? ?? '';
    final ttsAudio = result['tts_audio'] as String?;

    print('📱 [PTT] Command result received: success=$success, command="$command"');
    print('📱 [PTT] TTS audio present: ${ttsAudio != null}, length: ${ttsAudio?.length ?? 0}');

    setState(() {
      _lastResult = success
          ? '"$command" → $message'
          : message;
    });

    // Play TTS response if available
    if (ttsAudio != null && ttsAudio.isNotEmpty) {
      print('📱 [PTT] Calling playAudioBase64...');
      _audioService.playAudioBase64(ttsAudio).catchError((e) {
        print('❌ [PTT] Failed to play TTS: $e');
        debugPrint('Failed to play TTS: $e');
      });
    } else {
      print('⚠️ [PTT] No TTS audio to play');
    }

    // Show error if command failed
    if (!success) {
      _showError(message);
    }
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppTheme.errorColor,
      ),
    );
  }
}
