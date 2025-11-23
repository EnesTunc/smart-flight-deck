import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../services/audio_service.dart';
import '../services/bridge_service.dart';
import '../theme/app_theme.dart';

/// Push-to-Talk button for voice commands.
class PTTButton extends StatefulWidget {
  const PTTButton({super.key});

  @override
  State<PTTButton> createState() => _PTTButtonState();
}

class _PTTButtonState extends State<PTTButton> with SingleTickerProviderStateMixin {
  final AudioService _audioService = AudioService();
  final BridgeService _bridgeService = BridgeService();

  bool _isRecording = false;
  bool _isProcessing = false;
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Status text
        Text(
          _isRecording
              ? 'Listening...'
              : _isProcessing
                  ? 'Processing...'
                  : 'Hold to speak',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        const SizedBox(height: 16),

        // PTT Button
        GestureDetector(
          onLongPressStart: (_) => _startRecording(),
          onLongPressEnd: (_) => _stopRecording(),
          onLongPressCancel: () => _cancelRecording(),
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
                    color: _isRecording
                        ? AppTheme.errorColor
                        : _isProcessing
                            ? AppTheme.warningColor
                            : AppTheme.primaryColor,
                    boxShadow: [
                      BoxShadow(
                        color: (_isRecording
                                ? AppTheme.errorColor
                                : AppTheme.primaryColor)
                            .withOpacity(0.5),
                        blurRadius: _isRecording ? 20 : 10,
                        spreadRadius: _isRecording ? 5 : 2,
                      ),
                    ],
                  ),
                  child: Icon(
                    _isRecording
                        ? Icons.mic
                        : _isProcessing
                            ? Icons.hourglass_top
                            : Icons.mic_none,
                    size: 48,
                    color: AppTheme.backgroundColor,
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Future<void> _startRecording() async {
    // Haptic feedback
    HapticFeedback.mediumImpact();

    try {
      await _audioService.startRecording();
      setState(() {
        _isRecording = true;
      });
    } catch (e) {
      _showError('Failed to start recording: $e');
    }
  }

  Future<void> _stopRecording() async {
    if (!_isRecording) return;

    // Haptic feedback
    HapticFeedback.lightImpact();

    setState(() {
      _isRecording = false;
      _isProcessing = true;
    });

    try {
      final audioData = await _audioService.stopRecording();

      if (audioData != null && audioData.isNotEmpty) {
        // Send to bridge for processing
        final result = await _bridgeService.sendAudioCommand(audioData);

        if (!result.success) {
          _showError(result.message);
        }
      }
    } catch (e) {
      _showError('Failed to process command: $e');
    } finally {
      setState(() {
        _isProcessing = false;
      });
    }
  }

  Future<void> _cancelRecording() async {
    if (!_isRecording) return;

    await _audioService.cancelRecording();
    setState(() {
      _isRecording = false;
    });
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppTheme.errorColor,
      ),
    );
  }
}
