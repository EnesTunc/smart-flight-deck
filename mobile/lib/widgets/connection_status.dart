import 'package:flutter/material.dart';

import '../services/bridge_service.dart';
import '../theme/app_theme.dart';

/// Connection status indicator bar.
class ConnectionStatus extends StatelessWidget {
  const ConnectionStatus({super.key});

  @override
  Widget build(BuildContext context) {
    final bridgeService = BridgeService();

    return StreamBuilder<BridgeConnectionState>(
      stream: bridgeService.connectionStateStream,
      initialData: BridgeConnectionState.disconnected,
      builder: (context, snapshot) {
        final state = snapshot.data ?? BridgeConnectionState.disconnected;

        final Color backgroundColor;
        final Color textColor;
        final String text;
        final IconData icon;

        switch (state) {
          case BridgeConnectionState.connected:
            backgroundColor = AppTheme.secondaryColor.withValues(alpha: 0.2);
            textColor = AppTheme.secondaryColor;
            text = 'Connected';
            icon = Icons.check_circle;
          case BridgeConnectionState.connecting:
            backgroundColor = AppTheme.warningColor.withValues(alpha: 0.2);
            textColor = AppTheme.warningColor;
            text = 'Connecting...';
            icon = Icons.sync;
          case BridgeConnectionState.error:
            backgroundColor = AppTheme.errorColor.withValues(alpha: 0.2);
            textColor = AppTheme.errorColor;
            text = 'Connection Error';
            icon = Icons.error;
          case BridgeConnectionState.disconnected:
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
      },
    );
  }
}
