import 'package:flutter/material.dart';

/// Fuel & Weight Panel Widget
/// Displays fuel quantity, flow rate, endurance, and weight information.
class FuelPanel extends StatelessWidget {
  final double fuelTotalKg;
  final double fuelFlowKgH;
  final int fuelEnduranceMin;
  final double fuelPercent;
  final double? zfwKg; // Zero fuel weight (optional)
  final double? gwKg; // Gross weight (optional)
  final double? cgPercent; // Center of gravity (optional)

  const FuelPanel({
    super.key,
    required this.fuelTotalKg,
    required this.fuelFlowKgH,
    required this.fuelEnduranceMin,
    required this.fuelPercent,
    this.zfwKg,
    this.gwKg,
    this.cgPercent,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade700, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
            decoration: BoxDecoration(
              color: Colors.grey.shade900,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(8),
                topRight: Radius.circular(8),
              ),
            ),
            child: const Text(
              'FUEL & WEIGHT',
              style: TextStyle(
                color: Colors.white70,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          // Fuel info section
          Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                // Fuel bar and quantity
                _buildFuelBar(),
                const SizedBox(height: 12),
                // Fuel details row
                Row(
                  children: [
                    Expanded(child: _buildFuelItem('FUEL', _formatWeight(fuelTotalKg), '(${fuelPercent.toInt()}%)')),
                    Expanded(child: _buildFuelItem('FLOW', _formatWeight(fuelFlowKgH), '/h')),
                    Expanded(child: _buildFuelItem('ENDUR', _formatEndurance(fuelEnduranceMin), '')),
                  ],
                ),
                // Weight section (if available)
                if (zfwKg != null || gwKg != null) ...[
                  const SizedBox(height: 8),
                  Divider(color: Colors.grey.shade700, height: 1),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      if (zfwKg != null)
                        Expanded(child: _buildWeightItem('ZFW', _formatWeight(zfwKg!))),
                      if (gwKg != null)
                        Expanded(child: _buildWeightItem('GW', _formatWeight(gwKg!))),
                      if (cgPercent != null)
                        Expanded(child: _buildWeightItem('CG', '${cgPercent!.toStringAsFixed(1)}%')),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFuelBar() {
    final percent = fuelPercent.clamp(0, 100);
    Color barColor;
    if (percent < 10) {
      barColor = Colors.red;
    } else if (percent < 25) {
      barColor = Colors.amber;
    } else {
      barColor = Colors.greenAccent;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Progress bar
        Container(
          height: 16,
          decoration: BoxDecoration(
            color: Colors.grey.shade800,
            borderRadius: BorderRadius.circular(4),
            border: Border.all(color: Colors.grey.shade600, width: 1),
          ),
          child: Stack(
            children: [
              // Filled portion
              FractionallySizedBox(
                widthFactor: percent / 100,
                child: Container(
                  decoration: BoxDecoration(
                    color: barColor.withValues(alpha: 0.8),
                    borderRadius: BorderRadius.circular(3),
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        barColor.withValues(alpha: 0.9),
                        barColor.withValues(alpha: 0.6),
                      ],
                    ),
                  ),
                ),
              ),
              // Percentage text
              Center(
                child: Text(
                  '${percent.toInt()}%',
                  style: TextStyle(
                    color: percent > 40 ? Colors.black : Colors.white,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),
        // Warning messages
        if (percent < 10)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Row(
              children: [
                Icon(Icons.warning_amber, color: Colors.red, size: 14),
                const SizedBox(width: 4),
                Text(
                  'LOW FUEL',
                  style: TextStyle(
                    color: Colors.red,
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildFuelItem(String label, String value, String suffix) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            color: Colors.grey.shade500,
            fontSize: 10,
          ),
        ),
        Row(
          crossAxisAlignment: CrossAxisAlignment.baseline,
          textBaseline: TextBaseline.alphabetic,
          children: [
            Text(
              value,
              style: const TextStyle(
                color: Colors.greenAccent,
                fontSize: 14,
                fontFamily: 'monospace',
                fontWeight: FontWeight.bold,
              ),
            ),
            if (suffix.isNotEmpty)
              Text(
                suffix,
                style: TextStyle(
                  color: Colors.grey.shade400,
                  fontSize: 10,
                ),
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildWeightItem(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            color: Colors.grey.shade500,
            fontSize: 10,
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            color: Colors.cyan,
            fontSize: 13,
            fontFamily: 'monospace',
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  String _formatWeight(double kg) {
    if (kg >= 1000) {
      return '${(kg / 1000).toStringAsFixed(1)}t';
    }
    return '${kg.toInt()}kg';
  }

  String _formatEndurance(int minutes) {
    if (minutes <= 0) return '--:--';
    final hours = minutes ~/ 60;
    final mins = minutes % 60;
    return '$hours:${mins.toString().padLeft(2, '0')}';
  }
}
