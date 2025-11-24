import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/bridge_provider.dart';
import '../theme/app_theme.dart';

/// Quick command buttons for common actions.
class QuickCommands extends ConsumerWidget {
  const QuickCommands({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Commands',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: const [
            _CommandButton(
              label: 'GEAR',
              command: 'gear_toggle',
              icon: Icons.flight_land,
            ),
            _CommandButton(
              label: 'FLAPS +',
              command: 'flaps_down',
              icon: Icons.expand_more,
            ),
            _CommandButton(
              label: 'FLAPS -',
              command: 'flaps_up',
              icon: Icons.expand_less,
            ),
            _CommandButton(
              label: 'LIGHTS',
              command: 'landing_lights',
              icon: Icons.lightbulb,
            ),
            _CommandButton(
              label: 'P.BRAKE',
              command: 'parking_brake',
              icon: Icons.do_not_disturb,
            ),
            _CommandButton(
              label: 'SPOILERS',
              command: 'spoilers_arm',
              icon: Icons.vertical_align_top,
            ),
          ],
        ),
      ],
    );
  }
}

class _CommandButton extends ConsumerStatefulWidget {
  final String label;
  final String command;
  final IconData icon;

  const _CommandButton({
    required this.label,
    required this.command,
    required this.icon,
  });

  @override
  ConsumerState<_CommandButton> createState() => _CommandButtonState();
}

class _CommandButtonState extends ConsumerState<_CommandButton> {
  bool _isPressed = false;
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    final isConnected = ref.watch(isConnectedProvider);

    return GestureDetector(
      onTapDown: isConnected ? (_) => setState(() => _isPressed = true) : null,
      onTapUp: isConnected
          ? (_) {
              setState(() => _isPressed = false);
              _sendCommand();
            }
          : null,
      onTapCancel: () => setState(() => _isPressed = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 100),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: _isPressed
              ? AppTheme.primaryColor.withOpacity(0.3)
              : isConnected
                  ? AppTheme.cardColor
                  : AppTheme.cardColor.withOpacity(0.5),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: _isPressed
                ? AppTheme.primaryColor
                : AppTheme.textMuted.withOpacity(0.2),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (_isLoading)
              SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: AppTheme.primaryColor,
                ),
              )
            else
              Icon(
                widget.icon,
                size: 18,
                color: _isPressed
                    ? AppTheme.primaryColor
                    : isConnected
                        ? AppTheme.textSecondary
                        : AppTheme.textMuted,
              ),
            const SizedBox(width: 8),
            Text(
              widget.label,
              style: TextStyle(
                color: _isPressed
                    ? AppTheme.primaryColor
                    : isConnected
                        ? AppTheme.textPrimary
                        : AppTheme.textMuted,
                fontWeight: FontWeight.w600,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _sendCommand() async {
    HapticFeedback.lightImpact();

    setState(() => _isLoading = true);

    try {
      final result = await ref
          .read(bridgeProvider.notifier)
          .sendCommand(widget.command);

      if (!result.success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result.message),
            backgroundColor: AppTheme.errorColor,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        // Parse error to show user-friendly message
        String message = 'Command failed';
        final errorStr = e.toString().toLowerCase();

        if (errorStr.contains('503') || errorStr.contains('not connected') || errorStr.contains('msfs')) {
          message = 'MSFS is not connected';
        } else if (errorStr.contains('timeout') || errorStr.contains('connection')) {
          message = 'Connection error - check Bridge';
        } else if (errorStr.contains('401') || errorStr.contains('session')) {
          message = 'Session expired - reconnect';
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.warning_amber, color: Colors.white, size: 20),
                const SizedBox(width: 8),
                Text(message),
              ],
            ),
            backgroundColor: AppTheme.errorColor,
            behavior: SnackBarBehavior.floating,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }
}
