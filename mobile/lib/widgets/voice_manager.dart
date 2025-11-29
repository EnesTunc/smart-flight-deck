import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
// import 'package:just_audio/just_audio.dart' as ja; // TODO: Enable when voice preview is implemented
import 'dart:convert';
import '../models/app_settings.dart';
import '../providers/settings_provider.dart';
import '../providers/bridge_provider.dart';

/// Voice Management Widget
/// Shows all voices with download/delete/select functionality
class VoiceManager extends ConsumerWidget {
  const VoiceManager({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final voicesAsync = ref.watch(availableVoicesProvider);
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return voicesAsync.when(
      data: (voices) {
        if (voices.isEmpty) {
          return Text(
            'No voices available',
            style: TextStyle(
              color: isDark ? Colors.white54 : Colors.black54,
            ),
          );
        }

        // Count installed voices
        final installedCount = voices.where((v) => v.installed).length;

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with installed count
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Available Voices',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: isDark ? Colors.white70 : Colors.black87,
                  ),
                ),
                Text(
                  '$installedCount/${voices.length} installed',
                  style: TextStyle(
                    fontSize: 12,
                    color: isDark ? Colors.white38 : Colors.black38,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Voice list
            ...voices.map((voice) => _buildVoiceCard(
                  context,
                  ref,
                  voice,
                  settings.ttsVoice == voice.id,
                  installedCount,
                  settings.hapticFeedback,
                  isDark,
                )),
          ],
        );
      },
      loading: () => const Center(
        child: CircularProgressIndicator(),
      ),
      error: (err, stack) => Text(
        'Error loading voices',
        style: TextStyle(color: Colors.red[300]),
      ),
    );
  }

  Widget _buildVoiceCard(
    BuildContext context,
    WidgetRef ref,
    TtsVoice voice,
    bool isSelected,
    int installedCount,
    bool hapticEnabled,
    bool isDark,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: isSelected
            ? (isDark ? const Color(0xFF00E676).withOpacity(0.1) : const Color(0xFF0066CC).withOpacity(0.1))
            : (isDark ? const Color(0xFF1A1F3A) : Colors.white),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isSelected
              ? (isDark ? const Color(0xFF00E676) : const Color(0xFF0066CC))
              : (isDark ? const Color(0xFF2A2F4A) : const Color(0xFFE0E0E0)),
          width: isSelected ? 2 : 1,
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: voice.installed
              ? () async {
                  if (hapticEnabled) {
                    HapticFeedback.mediumImpact();
                  }
                  await ref.read(settingsProvider.notifier).setTtsVoice(voice.id);
                }
              : null,
          borderRadius: BorderRadius.circular(8),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                // Icon
                Icon(
                  voice.gender == 'female' ? Icons.record_voice_over : Icons.person,
                  color: isSelected
                      ? (isDark ? const Color(0xFF00E676) : const Color(0xFF0066CC))
                      : (isDark ? Colors.white54 : Colors.black54),
                  size: 24,
                ),
                const SizedBox(width: 12),
                // Voice info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        voice.displayName,
                        style: TextStyle(
                          fontSize: 15,
                          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                          color: isDark ? Colors.white : Colors.black,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Row(
                        children: [
                          _buildInfoChip(voice.gender.toUpperCase(), Colors.purple, isDark),
                          const SizedBox(width: 4),
                          _buildInfoChip(voice.accent, Colors.blue, isDark),
                          const SizedBox(width: 4),
                          _buildInfoChip('${voice.sizeMb.toStringAsFixed(0)}MB', Colors.grey, isDark),
                        ],
                      ),
                    ],
                  ),
                ),
                // Action buttons
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Preview button (only for installed voices)
                    if (voice.installed)
                      IconButton(
                        icon: const Icon(Icons.play_circle_outline),
                        color: isDark ? const Color(0xFF00E676) : const Color(0xFF0066CC),
                        iconSize: 28,
                        onPressed: () => _playPreview(context, ref, voice.id, hapticEnabled),
                        tooltip: 'Preview voice',
                      ),
                    // Download button
                    if (!voice.installed)
                      _buildDownloadButton(context, ref, voice.id, hapticEnabled, isDark)
                    // Delete button (not for selected voice, minimum 1 must remain)
                    else if (installedCount > 1 && !isSelected)
                      _buildDeleteButton(context, ref, voice.id, hapticEnabled, isDark)
                    // Selected checkmark
                    else if (isSelected && installedCount == 1)
                      Icon(
                        Icons.check_circle,
                        color: isDark ? const Color(0xFF00E676) : const Color(0xFF0066CC),
                        size: 24,
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildInfoChip(String label, Color color, bool isDark) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(isDark ? 0.15 : 0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withOpacity(isDark ? 0.5 : 0.3)),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w600,
          color: color,
        ),
      ),
    );
  }

  Widget _buildDownloadButton(BuildContext context, WidgetRef ref, String voiceId, bool hapticEnabled, bool isDark) {
    return IconButton(
      icon: const Icon(Icons.download),
      color: Colors.orange,
      onPressed: () async {
        if (hapticEnabled) {
          HapticFeedback.lightImpact();
        }

        final confirmed = await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            backgroundColor: isDark ? const Color(0xFF1A1F3A) : Colors.white,
            title: Text(
              'Download Voice',
              style: TextStyle(color: isDark ? Colors.white : Colors.black),
            ),
            content: Text(
              'Download this voice model? This may take a few moments.',
              style: TextStyle(color: isDark ? Colors.white70 : Colors.black87),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('CANCEL'),
              ),
              ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                ),
                child: const Text(
                  'DOWNLOAD',
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ],
          ),
        );

        if (confirmed == true && context.mounted) {
          final success = await ref.read(downloadVoiceProvider(voiceId).future);
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(success ? 'Voice downloaded successfully' : 'Failed to download voice'),
                backgroundColor: success ? Colors.green : Colors.red,
              ),
            );

            // Refresh voices list
            ref.invalidate(availableVoicesProvider);
          }
        }
      },
    );
  }

  Widget _buildDeleteButton(BuildContext context, WidgetRef ref, String voiceId, bool hapticEnabled, bool isDark) {
    return IconButton(
      icon: const Icon(Icons.delete_outline),
      color: Colors.red[300],
      onPressed: () async {
        if (hapticEnabled) {
          HapticFeedback.lightImpact();
        }

        final confirmed = await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            backgroundColor: isDark ? const Color(0xFF1A1F3A) : Colors.white,
            title: Text(
              'Delete Voice',
              style: TextStyle(color: isDark ? Colors.white : Colors.black),
            ),
            content: Text(
              'Delete this voice model to free up space? You can download it again later.',
              style: TextStyle(color: isDark ? Colors.white70 : Colors.black87),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('CANCEL'),
              ),
              ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red[300],
                ),
                child: const Text(
                  'DELETE',
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ],
          ),
        );

        if (confirmed == true) {
          // TODO: Implement voice delete API
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Voice delete feature coming soon'),
              backgroundColor: Colors.orange,
            ),
          );
        }
      },
    );
  }

  Future<void> _playPreview(BuildContext context, WidgetRef ref, String voiceId, bool hapticEnabled) async {
    if (hapticEnabled) {
      HapticFeedback.lightImpact();
    }

    // Show loading indicator
    if (!context.mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Row(
          children: [
            SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            ),
            SizedBox(width: 12),
            Text('Loading preview...'),
          ],
        ),
        duration: Duration(seconds: 2),
      ),
    );

    try {
      final bridgeState = ref.read(bridgeProvider);
      if (bridgeState.status != ConnectionStatus.connected ||
          bridgeState.bridgeIp == null ||
          bridgeState.bridgePort == null) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).clearSnackBars();
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Bridge not connected'),
              backgroundColor: Colors.red,
            ),
          );
        }
        return;
      }

      // TODO: Implement voice preview
      // This requires bridge API endpoint implementation
      // For now, just show a message
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Voice preview for $voiceId (Coming soon)'),
            backgroundColor: Colors.orange,
            duration: const Duration(seconds: 2),
          ),
        );
      }

      // Future implementation:
      // final dio = Dio(BaseOptions(baseUrl: 'http://${bridgeState.bridgeIp}:${bridgeState.bridgePort}'));
      // final response = await dio.post('/api/tts/preview', queryParameters: {'voice_id': voiceId});
      // Play audio with ja.AudioPlayer()
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).clearSnackBars();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Preview failed: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}
