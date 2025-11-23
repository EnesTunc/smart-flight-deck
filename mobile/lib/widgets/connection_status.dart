import 'package:flutter/material.dart';

import '../services/bridge_service.dart';
import '../theme/app_theme.dart';

/// Connection status indicator bar.
class ConnectionStatus extends StatelessWidget {
  const ConnectionStatus({super.key});

  @override
  Widget build(BuildContext context) {
    final bridgeService = BridgeService();

    return StreamBuilder<ConnectionState>(
      stream: bridgeService.connectionStateStream,
      initialData: ConnectionState.disconnected,
      builder: (context, snapshot) {
        final state = snapshot.data ?? ConnectionState.disconnected;

        Color backgroundColor;
        Color textColor;
        String text;
        IconData icon;

        switch (state) {
          case ConnectionState.connected:
            backgroundColor = AppTheme.secondaryColor.withOpacity(0.2);
            textColor = AppTheme.secondaryColor;
            text = 'Connected';
            icon = Icons.check_circle;
            break;
          case ConnectionState.connecting:
            backgroundColor = AppTheme.warningColor.withOpacity(0.2);
            textColor = AppTheme.warningColor;
            text = 'Connecting...';
            icon = Icons.sync;
            break;
          case ConnectionState.error:
            backgroundColor = AppTheme.errorColor.withOpacity(0.2);
            textColor = AppTheme.errorColor;
            text = 'Connection Error';
            icon = Icons.error;
            break;
          case ConnectionState.disconnected:
            backgroundColor = AppTheme.surfaceColor;
            textColor = AppTheme.textMuted;
            text = 'Disconnected';
            icon = Icons.cloud_off;
            break;
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
