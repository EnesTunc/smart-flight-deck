import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';

import '../providers/bridge_provider.dart';
import '../theme/app_theme.dart';

/// Panel displaying real-time simulator data.
class SimDataPanel extends ConsumerWidget {
  const SimDataPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final simDataAsync = ref.watch(simDataStreamProvider);

    return simDataAsync.when(
      data: (data) => _buildPanel(context, data),
      loading: () => _buildPanel(context, const SimData()),
      error: (_, __) => _buildPanel(context, const SimData()),
    );
  }

  Widget _buildPanel(BuildContext context, SimData data) {
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
                  data.simConnected ? Icons.flight_takeoff : Icons.flight_land,
                  color: data.simConnected
                      ? AppTheme.secondaryColor
                      : AppTheme.textMuted,
                ),
                const SizedBox(width: 8),
                Text(
                  data.simConnected ? 'MSFS Connected' : 'MSFS Not Connected',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const Spacer(),
                if (data.aircraft != null)
                  Text(
                    data.aircraft!,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: AppTheme.textMuted,
                        ),
                  ),
              ],
            ),

            if (data.simConnected) ...[
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 16),

              // Data grid
              Row(
                children: [
                  Expanded(
                    child: _DataItem(
                      label: 'ALT',
                      value: data.altitude.toStringAsFixed(0),
                      unit: 'ft',
                    ),
                  ),
                  Expanded(
                    child: _DataItem(
                      label: 'SPD',
                      value: data.speed.toStringAsFixed(0),
                      unit: 'kts',
                    ),
                  ),
                  Expanded(
                    child: _DataItem(
                      label: 'HDG',
                      value: data.heading.toStringAsFixed(0),
                      unit: '°',
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 12),

              // Second row - VS
              Row(
                children: [
                  Expanded(
                    child: _DataItem(
                      label: 'V/S',
                      value: _formatVerticalSpeed(data.verticalSpeed),
                      unit: 'fpm',
                      valueColor: _getVsColor(data.verticalSpeed),
                    ),
                  ),
                  const Expanded(child: SizedBox()),
                  const Expanded(child: SizedBox()),
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

              // Flight phase if available
              if (data.flightPhase != null) ...[
                const SizedBox(height: 12),
                Center(
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      data.flightPhase!.toUpperCase(),
                      style: TextStyle(
                        color: AppTheme.primaryColor,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }

  String _formatVerticalSpeed(double vs) {
    final sign = vs >= 0 ? '+' : '';
    return '$sign${vs.toStringAsFixed(0)}';
  }

  Color _getVsColor(double vs) {
    if (vs > 100) return AppTheme.secondaryColor;
    if (vs < -100) return AppTheme.warningColor;
    return AppTheme.textPrimary;
  }
}

class _DataItem extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final Color? valueColor;

  const _DataItem({
    required this.label,
    required this.value,
    required this.unit,
    this.valueColor,
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
              style: GoogleFonts.jetBrainsMono(
                color: valueColor ?? AppTheme.textPrimary,
                fontSize: 24,
                fontWeight: FontWeight.bold,
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
