import 'package:flutter/material.dart';

/// PFD Speed Tape Widget
/// Displays airspeed with a vertical tape indicator similar to real PFDs.
class PfdSpeedTape extends StatelessWidget {
  final double indicatedSpeed;
  final double groundSpeed;
  final double trueAirspeed;
  final double mach;
  final double? vmo; // Max operating speed (optional)
  final double? vlo; // Gear operating speed (optional)
  final double? vfe; // Flaps extended speed (optional)

  const PfdSpeedTape({
    super.key,
    required this.indicatedSpeed,
    required this.groundSpeed,
    required this.trueAirspeed,
    required this.mach,
    this.vmo,
    this.vlo,
    this.vfe,
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
          // Speed tape header
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
                'SPD',
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          // Speed tape
          Expanded(
            child: LayoutBuilder(
              builder: (context, constraints) {
                return CustomPaint(
                  size: Size(constraints.maxWidth, constraints.maxHeight),
                  painter: _SpeedTapePainter(
                    speed: indicatedSpeed,
                    vmo: vmo,
                    vlo: vlo,
                    vfe: vfe,
                  ),
                );
              },
            ),
          ),
          // Ground speed, TAS, Mach info
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
                _buildInfoRow('GS', groundSpeed.toStringAsFixed(0), 'kt'),
                const SizedBox(height: 2),
                _buildInfoRow('TAS', trueAirspeed.toStringAsFixed(0), 'kt'),
                const SizedBox(height: 2),
                _buildInfoRow('M', mach.toStringAsFixed(2), ''),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value, String unit) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          '$label:',
          style: TextStyle(
            color: Colors.grey.shade400,
            fontSize: 11,
          ),
        ),
        Row(
          children: [
            Text(
              value,
              style: const TextStyle(
                color: Colors.greenAccent,
                fontSize: 12,
                fontFamily: 'monospace',
                fontWeight: FontWeight.bold,
              ),
            ),
            if (unit.isNotEmpty)
              Text(
                unit,
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
}

class _SpeedTapePainter extends CustomPainter {
  final double speed;
  final double? vmo;
  final double? vlo;
  final double? vfe;

  // Tape configuration
  static const double pixelsPerKnot = 2.0;
  static const double majorTickInterval = 20.0;
  static const double minorTickInterval = 10.0;

  _SpeedTapePainter({
    required this.speed,
    this.vmo,
    this.vlo,
    this.vfe,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final centerY = size.height / 2;

    // Calculate the range of speeds to display
    final visibleRange = size.height / pixelsPerKnot;
    final minSpeed = speed - visibleRange / 2;
    final maxSpeed = speed + visibleRange / 2;

    // Paint background gradient (black to dark gray)
    final bgPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.centerLeft,
        end: Alignment.centerRight,
        colors: [Colors.black, Colors.grey.shade900],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), bgPaint);

    // Draw speed limit bands (Vmo, etc)
    if (vmo != null) {
      _drawSpeedBand(canvas, size, vmo!, 500, Colors.red.withValues(alpha: 0.3), minSpeed, maxSpeed);
    }
    if (vlo != null) {
      _drawSpeedBand(canvas, size, vlo!, vmo ?? 400, Colors.amber.withValues(alpha: 0.2), minSpeed, maxSpeed);
    }

    // Draw tick marks and labels
    final tickPaint = Paint()
      ..color = Colors.white
      ..strokeWidth = 1;

    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
    );

    // Find the first major tick
    final firstMajorTick = (minSpeed / majorTickInterval).ceil() * majorTickInterval;

    for (double spd = firstMajorTick; spd <= maxSpeed; spd += minorTickInterval) {
      final y = centerY - (spd - speed) * pixelsPerKnot;

      if (y < 0 || y > size.height) continue;

      final isMajor = (spd % majorTickInterval) == 0;
      final tickLength = isMajor ? 15.0 : 8.0;

      // Draw tick on right side
      canvas.drawLine(
        Offset(size.width - tickLength, y),
        Offset(size.width, y),
        tickPaint,
      );

      // Draw speed label for major ticks
      if (isMajor && spd >= 0) {
        textPainter.text = TextSpan(
          text: spd.toInt().toString(),
          style: const TextStyle(
            color: Colors.white,
            fontSize: 12,
            fontFamily: 'monospace',
          ),
        );
        textPainter.layout();
        textPainter.paint(
          canvas,
          Offset(size.width - tickLength - textPainter.width - 4, y - textPainter.height / 2),
        );
      }
    }

    // Draw speed limit markers
    _drawSpeedMarker(canvas, size, vmo, 'Vmo', Colors.red, minSpeed, maxSpeed);
    _drawSpeedMarker(canvas, size, vlo, 'Vlo', Colors.amber, minSpeed, maxSpeed);
    _drawSpeedMarker(canvas, size, vfe, 'Vfe', Colors.cyan, minSpeed, maxSpeed);

    // Draw current speed indicator (center box)
    _drawSpeedBox(canvas, size, centerY);
  }

  void _drawSpeedBand(Canvas canvas, Size size, double fromSpeed, double toSpeed,
      Color color, double minSpeed, double maxSpeed) {
    final centerY = size.height / 2;

    final y1 = centerY - (toSpeed - speed) * pixelsPerKnot;
    final y2 = centerY - (fromSpeed - speed) * pixelsPerKnot;

    final clampedY1 = y1.clamp(0.0, size.height);
    final clampedY2 = y2.clamp(0.0, size.height);

    if (clampedY1 < clampedY2) {
      final paint = Paint()..color = color;
      canvas.drawRect(
        Rect.fromLTRB(size.width - 20, clampedY1, size.width, clampedY2),
        paint,
      );
    }
  }

  void _drawSpeedMarker(Canvas canvas, Size size, double? limitSpeed, String label,
      Color color, double minSpeed, double maxSpeed) {
    if (limitSpeed == null) return;
    if (limitSpeed < minSpeed || limitSpeed > maxSpeed) return;

    final centerY = size.height / 2;
    final y = centerY - (limitSpeed - speed) * pixelsPerKnot;

    // Draw marker line
    final paint = Paint()
      ..color = color
      ..strokeWidth = 2;
    canvas.drawLine(
      Offset(0, y),
      Offset(25, y),
      paint,
    );

    // Draw label
    final textPainter = TextPainter(
      text: TextSpan(
        text: label,
        style: TextStyle(
          color: color,
          fontSize: 9,
          fontWeight: FontWeight.bold,
        ),
      ),
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(2, y - textPainter.height - 2));
  }

  void _drawSpeedBox(Canvas canvas, Size size, double centerY) {
    // Draw the speed indicator box
    const boxWidth = 55.0;
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

    // Speed value
    final textPainter = TextPainter(
      text: TextSpan(
        text: speed.toInt().toString(),
        style: const TextStyle(
          color: Colors.greenAccent,
          fontSize: 16,
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

    // Draw pointer arrow
    final arrowPath = Path()
      ..moveTo(size.width / 2 + boxWidth / 2, centerY)
      ..lineTo(size.width / 2 + boxWidth / 2 + 10, centerY - 8)
      ..lineTo(size.width / 2 + boxWidth / 2 + 10, centerY + 8)
      ..close();
    canvas.drawPath(arrowPath, Paint()..color = Colors.greenAccent);
  }

  @override
  bool shouldRepaint(covariant _SpeedTapePainter oldDelegate) {
    return speed != oldDelegate.speed ||
        vmo != oldDelegate.vmo ||
        vlo != oldDelegate.vlo ||
        vfe != oldDelegate.vfe;
  }
}
