import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/services.dart';
import '../providers/settings_provider.dart';
import '../models/app_settings.dart';

/// Settings Screen
/// Aviation-themed settings with dark UI and green accents
class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  String? _selectedVoiceForPreview;

  @override
  Widget build(BuildContext context) {
    final settings = ref.watch(settingsProvider);
    final voicesAsync = ref.watch(availableVoicesProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF0A0E27),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1F3A),
        elevation: 0,
        title: const Text(
          'SETTINGS',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            letterSpacing: 1.2,
            color: Color(0xFF00E676),
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white70),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // AUDIO & HAPTICS Section
          _buildSectionHeader('AUDIO & HAPTICS'),
          const SizedBox(height: 12),
          _buildSettingsCard([
            _buildMicSensitivitySlider(settings),
            const Divider(color: Color(0xFF2A2F4A), height: 24),
            _buildTtsVoiceDropdown(settings, voicesAsync),
            const Divider(color: Color(0xFF2A2F4A), height: 24),
            _buildTtsVolumeSlider(settings),
            const Divider(color: Color(0xFF2A2F4A), height: 24),
            _buildHapticToggle(settings),
          ]),

          const SizedBox(height: 24),

          // CHECKLIST Section
          _buildSectionHeader('CHECKLIST'),
          const SizedBox(height: 12),
          _buildSettingsCard([
            _buildAutoVerificationToggle(settings),
            const Divider(color: Color(0xFF2A2F4A), height: 24),
            _buildVoiceAnnouncementsToggle(settings),
          ]),

          const SizedBox(height: 24),

          // APPEARANCE Section
          _buildSectionHeader('APPEARANCE'),
          const SizedBox(height: 12),
          _buildSettingsCard([
            _buildThemeSelector(settings),
          ]),

          const SizedBox(height: 24),

          // Footer info
          _buildFooter(),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 4),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w700,
          letterSpacing: 1.5,
          color: Color(0xFF00E676),
        ),
      ),
    );
  }

  Widget _buildSettingsCard(List<Widget> children) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF1A1F3A),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF2A2F4A),
          width: 1,
        ),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: children,
      ),
    );
  }

  Widget _buildMicSensitivitySlider(AppSettings settings) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Microphone Sensitivity',
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w500,
                color: Colors.white,
              ),
            ),
            Text(
              '${(settings.micSensitivity * 100).round()}%',
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: Color(0xFF00E676),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SliderTheme(
          data: SliderThemeData(
            activeTrackColor: const Color(0xFF00E676),
            inactiveTrackColor: const Color(0xFF2A2F4A),
            thumbColor: const Color(0xFF00E676),
            overlayColor: const Color(0xFF00E676).withOpacity(0.2),
            trackHeight: 3,
          ),
          child: Slider(
            value: settings.micSensitivity,
            min: 0.0,
            max: 1.0,
            divisions: 20,
            onChanged: (value) {
              ref.read(settingsProvider.notifier).setMicSensitivity(value);
              HapticFeedback.selectionClick();
            },
          ),
        ),
      ],
    );
  }

  Widget _buildTtsVoiceDropdown(AppSettings settings, AsyncValue<List<TtsVoice>> voicesAsync) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'TTS Voice',
          style: TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w500,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 8),
        voicesAsync.when(
          data: (voices) {
            if (voices.isEmpty) {
              return const Text(
                'No voices available',
                style: TextStyle(color: Colors.white54),
              );
            }

            final selectedVoice = voices.firstWhere(
              (v) => v.id == settings.ttsVoice,
              orElse: () => voices.first,
            );

            return Column(
              children: [
                // Voice dropdown
                Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFF0A0E27),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFF2A2F4A)),
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: settings.ttsVoice,
                      isExpanded: true,
                      dropdownColor: const Color(0xFF1A1F3A),
                      style: const TextStyle(color: Colors.white),
                      items: voices.map((voice) {
                        return DropdownMenuItem<String>(
                          value: voice.id,
                          child: Row(
                            children: [
                              Icon(
                                voice.gender == 'female'
                                    ? Icons.record_voice_over
                                    : Icons.person,
                                color: const Color(0xFF00E676),
                                size: 18,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(voice.displayName),
                              ),
                              if (!voice.installed)
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 6,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: Colors.orange.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(4),
                                    border: Border.all(
                                      color: Colors.orange,
                                      width: 1,
                                    ),
                                  ),
                                  child: const Text(
                                    'DOWNLOAD',
                                    style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.w600,
                                      color: Colors.orange,
                                    ),
                                  ),
                                ),
                              if (voice.installed)
                                const Icon(
                                  Icons.check_circle,
                                  color: Color(0xFF00E676),
                                  size: 16,
                                ),
                            ],
                          ),
                        );
                      }).toList(),
                      onChanged: (voiceId) async {
                        if (voiceId == null) return;

                        final voice = voices.firstWhere((v) => v.id == voiceId);

                        // If not installed, download first
                        if (!voice.installed) {
                          final confirmed = await _showDownloadDialog(voice);
                          if (confirmed != true) return;

                          final success = await ref.read(
                            downloadVoiceProvider(voiceId).future,
                          );

                          if (!success && mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Failed to download voice'),
                                backgroundColor: Colors.red,
                              ),
                            );
                            return;
                          }
                        }

                        await ref.read(settingsProvider.notifier).setTtsVoice(voiceId);
                        if (mounted) {
                          HapticFeedback.mediumImpact();
                        }
                      },
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                // Voice info row
                Row(
                  children: [
                    _buildVoiceInfoChip(
                      selectedVoice.gender.toUpperCase(),
                      Colors.purple,
                    ),
                    const SizedBox(width: 8),
                    _buildVoiceInfoChip(
                      selectedVoice.accent,
                      Colors.blue,
                    ),
                    const SizedBox(width: 8),
                    _buildVoiceInfoChip(
                      selectedVoice.quality.toUpperCase(),
                      const Color(0xFF00E676),
                    ),
                    const Spacer(),
                    // Preview button
                    TextButton.icon(
                      onPressed: () => _previewVoice(settings.ttsVoice),
                      icon: const Icon(
                        Icons.play_arrow,
                        size: 18,
                        color: Color(0xFF00E676),
                      ),
                      label: const Text(
                        'PREVIEW',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF00E676),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            );
          },
          loading: () => const Center(
            child: CircularProgressIndicator(
              color: Color(0xFF00E676),
            ),
          ),
          error: (err, stack) => Text(
            'Error loading voices',
            style: TextStyle(color: Colors.red[300]),
          ),
        ),
      ],
    );
  }

  Widget _buildVoiceInfoChip(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withOpacity(0.5)),
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

  Future<bool?> _showDownloadDialog(TtsVoice voice) {
    return showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1F3A),
        title: const Text(
          'Download Voice',
          style: TextStyle(color: Colors.white),
        ),
        content: Text(
          'Download ${voice.displayName}?\n\nSize: ${voice.sizeMb.toStringAsFixed(1)} MB',
          style: const TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('CANCEL'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF00E676),
            ),
            child: const Text(
              'DOWNLOAD',
              style: TextStyle(color: Colors.black),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _previewVoice(String voiceId) async {
    // TODO: Implement TTS preview playback
    // This will call the Bridge API /api/tts/preview endpoint
    if (mounted) {
      HapticFeedback.lightImpact();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Playing preview for $voiceId'),
          backgroundColor: const Color(0xFF00E676),
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }

  Widget _buildTtsVolumeSlider(AppSettings settings) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'TTS Volume',
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w500,
                color: Colors.white,
              ),
            ),
            Text(
              '${(settings.ttsVolume * 100).round()}%',
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: Color(0xFF00E676),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SliderTheme(
          data: SliderThemeData(
            activeTrackColor: const Color(0xFF00E676),
            inactiveTrackColor: const Color(0xFF2A2F4A),
            thumbColor: const Color(0xFF00E676),
            overlayColor: const Color(0xFF00E676).withOpacity(0.2),
            trackHeight: 3,
          ),
          child: Slider(
            value: settings.ttsVolume,
            min: 0.0,
            max: 1.0,
            divisions: 20,
            onChanged: (value) {
              ref.read(settingsProvider.notifier).setTtsVolume(value);
              HapticFeedback.selectionClick();
            },
          ),
        ),
      ],
    );
  }

  Widget _buildHapticToggle(AppSettings settings) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        const Text(
          'Haptic Feedback',
          style: TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w500,
            color: Colors.white,
          ),
        ),
        Switch(
          value: settings.hapticFeedback,
          activeColor: const Color(0xFF00E676),
          onChanged: (value) {
            ref.read(settingsProvider.notifier).setHapticFeedback(value);
            if (value) {
              HapticFeedback.mediumImpact();
            }
          },
        ),
      ],
    );
  }

  Widget _buildAutoVerificationToggle(AppSettings settings) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Auto Verification',
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w500,
                color: Colors.white,
              ),
            ),
            SizedBox(height: 4),
            Text(
              'Verify checklist items via SimConnect',
              style: TextStyle(
                fontSize: 12,
                color: Colors.white54,
              ),
            ),
          ],
        ),
        Switch(
          value: settings.autoVerification,
          activeColor: const Color(0xFF00E676),
          onChanged: (value) {
            ref.read(settingsProvider.notifier).setAutoVerification(value);
            HapticFeedback.selectionClick();
          },
        ),
      ],
    );
  }

  Widget _buildVoiceAnnouncementsToggle(AppSettings settings) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Voice Announcements',
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w500,
                color: Colors.white,
              ),
            ),
            SizedBox(height: 4),
            Text(
              'Enable TTS responses',
              style: TextStyle(
                fontSize: 12,
                color: Colors.white54,
              ),
            ),
          ],
        ),
        Switch(
          value: settings.voiceAnnouncements,
          activeColor: const Color(0xFF00E676),
          onChanged: (value) {
            ref.read(settingsProvider.notifier).setVoiceAnnouncements(value);
            HapticFeedback.selectionClick();
          },
        ),
      ],
    );
  }

  Widget _buildThemeSelector(AppSettings settings) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Theme',
          style: TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w500,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            color: const Color(0xFF0A0E27),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0xFF2A2F4A)),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<ThemeMode>(
              value: settings.themeMode,
              isExpanded: true,
              dropdownColor: const Color(0xFF1A1F3A),
              style: const TextStyle(color: Colors.white),
              items: const [
                DropdownMenuItem(
                  value: ThemeMode.dark,
                  child: Row(
                    children: [
                      Icon(Icons.dark_mode, color: Color(0xFF00E676), size: 18),
                      SizedBox(width: 8),
                      Text('Dark'),
                    ],
                  ),
                ),
                DropdownMenuItem(
                  value: ThemeMode.light,
                  child: Row(
                    children: [
                      Icon(Icons.light_mode, color: Color(0xFF00E676), size: 18),
                      SizedBox(width: 8),
                      Text('Light'),
                    ],
                  ),
                ),
              ],
              onChanged: (mode) {
                if (mode != null) {
                  ref.read(settingsProvider.notifier).setThemeMode(mode);
                  HapticFeedback.mediumImpact();
                }
              },
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildFooter() {
    return const Padding(
      padding: EdgeInsets.all(16),
      child: Column(
        children: [
          Text(
            'Smart Flight Deck Companion',
            style: TextStyle(
              fontSize: 12,
              color: Colors.white38,
            ),
          ),
          SizedBox(height: 4),
          Text(
            'v1.0.0 (MVP)',
            style: TextStyle(
              fontSize: 11,
              color: Colors.white24,
            ),
          ),
        ],
      ),
    );
  }
}
