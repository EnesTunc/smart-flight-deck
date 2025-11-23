import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../services/bridge_service.dart';
import '../theme/app_theme.dart';

/// Quick command buttons for common actions.
class QuickCommands extends StatelessWidget {
  const QuickCommands({super.key});

  @override
  Widget build(BuildContext context) {
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
              command: 'landing_lights_toggle',
              icon: Icons.lightbulb,
            ),
            _CommandButton(
              label: 'P.BRAKE',
              command: 'parking_brake_toggle',
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

class _CommandButton extends StatefulWidget {
  final String label;
  final String command;
  final IconData icon;

  const _CommandButton({
    required this.label,
    required this.command,
    required this.icon,
  });

  @override
  State<_CommandButton> createState() => _CommandButtonState();
}

class _CommandButtonState extends State<_CommandButton> {
  bool _isPressed = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) => setState(() => _isPressed = true),
      onTapUp: (_) {
        setState(() => _isPressed = false);
        _sendCommand();
      },
      onTapCancel: () => setState(() => _isPressed = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 100),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: _isPressed
              ? AppTheme.primaryColor.withOpacity(0.3)
              : AppTheme.cardColor,
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
            Icon(
              widget.icon,
              size: 18,
              color: _isPressed ? AppTheme.primaryColor : AppTheme.textSecondary,
            ),
            const SizedBox(width: 8),
            Text(
              widget.label,
              style: TextStyle(
                color: _isPressed ? AppTheme.primaryColor : AppTheme.textPrimary,
                fontWeight: FontWeight.w600,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _sendCommand() {
    HapticFeedback.lightImpact();

    try {
      BridgeService().sendDirectCommand(widget.command);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to send command: $e'),
          backgroundColor: AppTheme.errorColor,
        ),
      );
    }
  }
}
