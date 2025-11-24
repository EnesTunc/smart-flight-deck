import 'package:flutter/material.dart';

/// PFD Altitude Tape Widget
/// Displays altitude with a vertical tape indicator similar to real PFDs.
class PfdAltitudeTape extends StatelessWidget {
  final double altitude;
  final double verticalSpeed;
  final double qnh;
  final bool isStdBaro;

  const PfdAltitudeTape({
    super.key,
    required this.altitude,
    required this.verticalSpeed,
    required this.qnh,
    this.isStdBaro = false,
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
        children: [
          // Altitude tape header
          Container(
            padding: const EdgeInsets.symmetric(vertical: 4),
            decoration: BoxDecoration(
              color: Colors.grey.shade900,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(8),
                topRight: Radius.circular(8),
              ),
            ),
            child: const Center(
              child: Text(
                'ALT',
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          // Altitude tape
          Expanded(
            child: LayoutBuilder(
              builder: (context, constraints) {
                return CustomPaint(
                  size: Size(constraints.maxWidth, constraints.maxHeight),
                  painter: _AltitudeTapePainter(
                    altitude: altitude,
                    verticalSpeed: verticalSpeed,
                  ),
                );
              },
            ),
          ),
          // V/S and QNH info
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.grey.shade900,
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(8),
                bottomRight: Radius.circular(8),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildVsRow(),
                const SizedBox(height: 4),
                _buildQnhRow(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVsRow() {
    final vsSign = verticalSpeed >= 0 ? '+' : '';
    final vsColor = verticalSpeed.abs() > 2000
        ? Colors.amber
        : verticalSpeed.abs() > 500
            ? Colors.white
            : Colors.grey.shade400;

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          'V/S:',
          style: TextStyle(
            color: Colors.grey.shade400,
            fontSize: 11,
          ),
        ),
        Row(
          children: [
            Text(
              '$vsSign${verticalSpeed.toInt()}',
              style: TextStyle(
                color: vsColor,
                fontSize: 12,
                fontFamily: 'monospace',
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              'fpm',
              style: TextStyle(
                color: Colors.grey.shade500,
                fontSize: 10,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQnhRow() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          'QNH:',
          style: TextStyle(
            color: Colors.grey.shade400,
            fontSize: 11,
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
          decoration: BoxDecoration(
            color: isStdBaro ? Colors.cyan.withValues(alpha: 0.2) : Colors.transparent,
            borderRadius: BorderRadius.circular(2),
          ),
          child: Text(
            isStdBaro ? 'STD' : qnh.toStringAsFixed(0),
            style: TextStyle(
              color: isStdBaro ? Colors.cyan : Colors.greenAccent,
              fontSize: 12,
              fontFamily: 'monospace',
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ],
    );
  }
}

class _AltitudeTapePainter extends CustomPainter {
  final double altitude;
  final double verticalSpeed;

  // Tape configuration
  static const double pixelsPerFoot = 0.03;
  static const double majorTickInterval = 1000.0;
  static const double minorTickInterval = 500.0;

  _AltitudeTapePainter({
    required this.altitude,
    required this.verticalSpeed,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final centerY = size.height / 2;

    // Calculate the range of altitudes to display
    final visibleRange = size.height / pixelsPerFoot;
    final minAlt = altitude - visibleRange / 2;
    final maxAlt = altitude + visibleRange / 2;

    // Paint background gradient
    final bgPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.centerLeft,
        end: Alignment.centerRight,
        colors: [Colors.grey.shade900, Colors.black],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), bgPaint);

    // Draw tick marks and labels
    final tickPaint = Paint()
      ..color = Colors.white
      ..strokeWidth = 1;

    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
    );

    // Find the first major tick
    final firstMajorTick = (minAlt / majorTickInterval).ceil() * majorTickInterval;

    for (double alt = firstMajorTick; alt <= maxAlt; alt += minorTickInterval) {
      final y = centerY - (alt - altitude) * pixelsPerFoot;

      if (y < 0 || y > size.height) continue;

      final isMajor = (alt % majorTickInterval) == 0;
      final tickLength = isMajor ? 15.0 : 8.0;

      // Draw tick on left side
      canvas.drawLine(
        Offset(0, y),
        Offset(tickLength, y),
        tickPaint,
      );

      // Draw altitude label for major ticks
      if (isMajor && alt >= 0) {
        final displayAlt = _formatAltitude(alt);
        textPainter.text = TextSpan(
          text: displayAlt,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 12,
            fontFamily: 'monospace',
          ),
        );
        textPainter.layout();
        textPainter.paint(
          canvas,
          Offset(tickLength + 4, y - textPainter.height / 2),
        );
      }
    }

    // Draw trend vector (vertical speed indicator)
    if (verticalSpeed.abs() > 100) {
      _drawTrendVector(canvas, size, centerY);
    }

    // Draw current altitude indicator (center box)
    _drawAltitudeBox(canvas, size, centerY);
  }

  String _formatAltitude(double alt) {
    if (alt >= 10000) {
      // Show as FL for high altitudes
      return (alt / 100).toInt().toString();
    }
    return alt.toInt().toString();
  }

  void _drawTrendVector(Canvas canvas, Size size, double centerY) {
    // Draw a trend vector showing where altitude will be in 10 seconds
    final trendFeet = verticalSpeed / 6; // V/S per 10 seconds
    final trendPixels = trendFeet * pixelsPerFoot;
    final maxTrend = size.height * 0.3;
    final clampedTrend = trendPixels.clamp(-maxTrend, maxTrend);

    final paint = Paint()
      ..color = Colors.cyan.withValues(alpha: 0.7)
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke;

    canvas.drawLine(
      Offset(size.width / 2, centerY),
      Offset(size.width / 2, centerY - clampedTrend),
      paint,
    );

    // Arrow head
    if (clampedTrend.abs() > 10) {
      final direction = clampedTrend > 0 ? -1 : 1;
      final arrowY = centerY - clampedTrend;
      final arrowPath = Path()
        ..moveTo(size.width / 2, arrowY)
        ..lineTo(size.width / 2 - 5, arrowY + 8 * direction)
        ..lineTo(size.width / 2 + 5, arrowY + 8 * direction)
        ..close();
      canvas.drawPath(arrowPath, Paint()..color = Colors.cyan.withValues(alpha: 0.7));
    }
  }

  void _drawAltitudeBox(Canvas canvas, Size size, double centerY) {
    // Draw the altitude indicator box
    const boxWidth = 65.0;
    const boxHeight = 28.0;
    final boxRect = RRect.fromRectAndRadius(
      Rect.fromCenter(
        center: Offset(size.width / 2, centerY),
        width: boxWidth,
        height: boxHeight,
      ),
      const Radius.circular(4),
    );

    // Box background
    final boxBgPaint = Paint()..color = Colors.black;
    canvas.drawRRect(boxRect, boxBgPaint);

    // Box border
    final boxBorderPaint = Paint()
      ..color = Colors.greenAccent
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    canvas.drawRRect(boxRect, boxBorderPaint);

    // Altitude value
    final displayAlt = altitude >= 18000
        ? 'FL${(altitude / 100).toInt()}'
        : altitude.toInt().toString();

    final textPainter = TextPainter(
      text: TextSpan(
        text: displayAlt,
        style: const TextStyle(
          color: Colors.greenAccent,
          fontSize: 14,
          fontFamily: 'monospace',
          fontWeight: FontWeight.bold,
        ),
      ),
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(
        size.width / 2 - textPainter.width / 2,
        centerY - textPainter.height / 2,
      ),
    );

    // Draw pointer arrow (on left side)
    final arrowPath = Path()
      ..moveTo(size.width / 2 - boxWidth / 2, centerY)
      ..lineTo(size.width / 2 - boxWidth / 2 - 10, centerY - 8)
      ..lineTo(size.width / 2 - boxWidth / 2 - 10, centerY + 8)
      ..close();
    canvas.drawPath(arrowPath, Paint()..color = Colors.greenAccent);
  }

  @override
  bool shouldRepaint(covariant _AltitudeTapePainter oldDelegate) {
    return altitude != oldDelegate.altitude ||
        verticalSpeed != oldDelegate.verticalSpeed;
  }
}
