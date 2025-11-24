import 'package:flutter/material.dart';

/// Navigation Panel Widget
/// Displays heading, track, wind, OAT, and NAV radio information.
class NavigationPanel extends StatelessWidget {
  final double heading;
  final double track;
  final double windDirection;
  final double windSpeed;
  final double oat;
  final double nav1Freq;
  final String? nav1Ident;
  final double nav1Dme;
  final double nav2Freq;
  final String? nav2Ident;
  final double nav2Dme;

  const NavigationPanel({
    super.key,
    required this.heading,
    required this.track,
    required this.windDirection,
    required this.windSpeed,
    required this.oat,
    required this.nav1Freq,
    this.nav1Ident,
    required this.nav1Dme,
    required this.nav2Freq,
    this.nav2Ident,
    required this.nav2Dme,
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
              'NAVIGATION',
              style: TextStyle(
                color: Colors.white70,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          // Top row: HDG, TRK, WIND, OAT
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildDataItem('HDG', '${heading.toInt()}°', Colors.greenAccent),
                _buildDataItem('TRK', '${track.toInt()}°', Colors.greenAccent),
                _buildWindItem(),
                _buildDataItem('OAT', '${oat.toInt()}°C', Colors.cyan),
              ],
            ),
          ),
          // Divider
          Divider(color: Colors.grey.shade700, height: 1),
          // NAV1 row
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: _buildNavRow(
              'NAV1',
              nav1Freq,
              nav1Ident,
              nav1Dme,
              Colors.greenAccent,
            ),
          ),
          // NAV2 row
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: _buildNavRow(
              'NAV2',
              nav2Freq,
              nav2Ident,
              nav2Dme,
              Colors.cyan,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDataItem(String label, String value, Color valueColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      mainAxisSize: MainAxisSize.min,
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
          style: TextStyle(
            color: valueColor,
            fontSize: 14,
            fontFamily: 'monospace',
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildWindItem() {
    final windArrowRotation = (windDirection + 180) % 360; // Arrow points TO wind direction

    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          'WIND',
          style: TextStyle(
            color: Colors.grey.shade500,
            fontSize: 10,
          ),
        ),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Transform.rotate(
              angle: windArrowRotation * 3.14159 / 180,
              child: const Icon(
                Icons.arrow_upward,
                color: Colors.amber,
                size: 14,
              ),
            ),
            const SizedBox(width: 2),
            Text(
              '${windDirection.toInt()}/${windSpeed.toInt()}',
              style: const TextStyle(
                color: Colors.amber,
                fontSize: 14,
                fontFamily: 'monospace',
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildNavRow(
    String label,
    double freq,
    String? ident,
    double dme,
    Color color,
  ) {
    final hasSignal = freq > 0 && ident != null && ident.isNotEmpty;

    return Row(
      children: [
        // Label
        SizedBox(
          width: 40,
          child: Text(
            label,
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 11,
            ),
          ),
        ),
        // Frequency
        SizedBox(
          width: 65,
          child: Text(
            freq > 0 ? freq.toStringAsFixed(2) : '---.-',
            style: TextStyle(
              color: hasSignal ? color : Colors.grey.shade600,
              fontSize: 13,
              fontFamily: 'monospace',
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        // Ident
        Expanded(
          child: Text(
            ident ?? '---',
            style: TextStyle(
              color: hasSignal ? color : Colors.grey.shade600,
              fontSize: 13,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        // DME
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'DME',
              style: TextStyle(
                color: Colors.grey.shade500,
                fontSize: 10,
              ),
            ),
            const SizedBox(width: 4),
            Text(
              dme > 0 ? '${dme.toStringAsFixed(1)}nm' : '--.-nm',
              style: TextStyle(
                color: hasSignal ? Colors.white : Colors.grey.shade600,
                fontSize: 12,
                fontFamily: 'monospace',
              ),
            ),
          ],
        ),
      ],
    );
  }
}
