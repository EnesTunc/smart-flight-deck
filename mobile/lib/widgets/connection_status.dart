import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/bridge_provider.dart';
import '../theme/app_theme.dart';

/// Connection status indicator bar.
class ConnectionStatusBar extends ConsumerWidget {
  const ConnectionStatusBar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectionState = ref.watch(bridgeProvider);
    final simDataAsync = ref.watch(simDataStreamProvider);

    final Color backgroundColor;
    final Color textColor;
    final String text;
    final IconData icon;

    switch (connectionState.status) {
      case ConnectionStatus.connected:
        // Check if MSFS is also connected
        final simConnected = simDataAsync.whenOrNull(
          data: (data) => data.simConnected,
        ) ?? false;

        if (simConnected) {
          backgroundColor = AppTheme.secondaryColor.withOpacity(0.2);
          textColor = AppTheme.secondaryColor;
          text = 'MSFS Connected';
          icon = Icons.flight_takeoff;
        } else {
          backgroundColor = AppTheme.primaryColor.withOpacity(0.2);
          textColor = AppTheme.primaryColor;
          text = 'Bridge Connected';
          icon = Icons.check_circle;
        }
      case ConnectionStatus.connecting:
        backgroundColor = AppTheme.warningColor.withOpacity(0.2);
        textColor = AppTheme.warningColor;
        text = 'Connecting...';
        icon = Icons.sync;
      case ConnectionStatus.reconnecting:
        backgroundColor = AppTheme.warningColor.withOpacity(0.2);
        textColor = AppTheme.warningColor;
        text = 'Reconnecting...';
        icon = Icons.sync;
      case ConnectionStatus.error:
        backgroundColor = AppTheme.errorColor.withOpacity(0.2);
        textColor = AppTheme.errorColor;
        text = 'Connection Error';
        icon = Icons.error;
      case ConnectionStatus.disconnected:
        backgroundColor = AppTheme.surfaceColor;
        textColor = AppTheme.textMuted;
        text = 'Disconnected';
        icon = Icons.cloud_off;
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: backgroundColor,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 16, color: textColor),
          const SizedBox(width: 8),
          Text(
            text,
            style: TextStyle(
              color: textColor,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
