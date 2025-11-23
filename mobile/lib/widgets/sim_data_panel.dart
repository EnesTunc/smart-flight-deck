import 'package:flutter/material.dart';

import '../services/bridge_service.dart';
import '../theme/app_theme.dart';

/// Panel displaying real-time simulator data.
class SimDataPanel extends StatelessWidget {
  const SimDataPanel({super.key});

  @override
  Widget build(BuildContext context) {
    final bridgeService = BridgeService();

    return StreamBuilder<SimData>(
      stream: bridgeService.simDataStream,
      initialData: SimData(
        connected: false,
        altitude: 0,
        speed: 0,
        heading: 0,
        gearPosition: 0,
        flapsPosition: 0,
        onGround: true,
      ),
      builder: (context, snapshot) {
        final data = snapshot.data!;

        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Row(
                  children: [
                    Icon(
                      data.connected ? Icons.flight_takeoff : Icons.flight_land,
                      color: data.connected
                          ? AppTheme.secondaryColor
                          : AppTheme.textMuted,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      data.connected ? 'MSFS Connected' : 'MSFS Not Connected',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                  ],
                ),

                if (data.connected) ...[
                  const SizedBox(height: 16),
                  const Divider(),
                  const SizedBox(height: 16),

                  // Data grid
                  Row(
                    children: [
                      Expanded(
                        child: _DataItem(
                          label: 'ALT',
                          value: '${data.altitude.toStringAsFixed(0)}',
                          unit: 'ft',
                        ),
                      ),
                      Expanded(
                        child: _DataItem(
                          label: 'SPD',
                          value: '${data.speed.toStringAsFixed(0)}',
                          unit: 'kts',
                        ),
                      ),
                      Expanded(
                        child: _DataItem(
                          label: 'HDG',
                          value: '${data.heading.toStringAsFixed(0)}',
                          unit: '°',
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 16),

                  // Status indicators
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _StatusIndicator(
                        label: 'GEAR',
                        isActive: data.gearPosition == 1,
                        activeColor: AppTheme.secondaryColor,
                      ),
                      _StatusIndicator(
                        label: 'FLAPS ${data.flapsPosition}',
                        isActive: data.flapsPosition > 0,
                        activeColor: AppTheme.primaryColor,
                      ),
                      _StatusIndicator(
                        label: 'GND',
                        isActive: data.onGround,
                        activeColor: AppTheme.warningColor,
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }
}

class _DataItem extends StatelessWidget {
  final String label;
  final String value;
  final String unit;

  const _DataItem({
    required this.label,
    required this.value,
    required this.unit,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            color: AppTheme.textMuted,
            fontSize: 12,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 4),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.baseline,
          textBaseline: TextBaseline.alphabetic,
          children: [
            Text(
              value,
              style: const TextStyle(
                color: AppTheme.textPrimary,
                fontSize: 24,
                fontWeight: FontWeight.bold,
                fontFamily: 'JetBrainsMono',
              ),
            ),
            const SizedBox(width: 2),
            Text(
              unit,
              style: TextStyle(
                color: AppTheme.textSecondary,
                fontSize: 12,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _StatusIndicator extends StatelessWidget {
  final String label;
  final bool isActive;
  final Color activeColor;

  const _StatusIndicator({
    required this.label,
    required this.isActive,
    required this.activeColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: isActive ? activeColor.withOpacity(0.2) : AppTheme.surfaceColor,
        borderRadius: BorderRadius.circular(4),
        border: Border.all(
          color: isActive ? activeColor : AppTheme.textMuted.withOpacity(0.3),
        ),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: isActive ? activeColor : AppTheme.textMuted,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
