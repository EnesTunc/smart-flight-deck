import 'package:flutter/material.dart';

/// Aviation-standard color palette for the EFB interface.
/// Based on standard cockpit display colors.
class AppColors {
  AppColors._();

  // ===========================================
  // Base Colors (Dark Theme)
  // ===========================================

  /// Primary background - deep dark blue/black
  static const Color background = Color(0xFF0A0E14);

  /// Secondary background - slightly lighter
  static const Color surface = Color(0xFF141A22);

  /// Card/Panel background
  static const Color card = Color(0xFF1A2230);

  /// Border color
  static const Color border = Color(0xFF2A3444);

  // ===========================================
  // Aviation Standard Colors
  // ===========================================

  /// Green - Active/OK/Confirmed
  static const Color green = Color(0xFF00FF00);
  static const Color greenDim = Color(0xFF00AA00);

  /// Amber/Yellow - Caution/Warning
  static const Color amber = Color(0xFFFFAA00);
  static const Color amberDim = Color(0xFFCC8800);

  /// Red - Danger/Error/Critical
  static const Color red = Color(0xFFFF0000);
  static const Color redDim = Color(0xFFCC0000);

  /// Cyan - Navigation/Information
  static const Color cyan = Color(0xFF00FFFF);
  static const Color cyanDim = Color(0xFF00AAAA);

  /// Magenta - Flight plan/Active waypoint
  static const Color magenta = Color(0xFFFF00FF);
  static const Color magentaDim = Color(0xFFAA00AA);

  /// White - Primary text
  static const Color white = Color(0xFFFFFFFF);
  static const Color whiteDim = Color(0xFFAAAAAA);

  /// Blue - Selected/Highlighted
  static const Color blue = Color(0xFF4488FF);
  static const Color blueDim = Color(0xFF2255AA);

  // ===========================================
  // Semantic Colors
  // ===========================================

  /// Primary action color
  static const Color primary = cyan;

  /// Secondary action color
  static const Color secondary = blue;

  /// Success state
  static const Color success = green;

  /// Warning state
  static const Color warning = amber;

  /// Error state
  static const Color error = red;

  /// Info state
  static const Color info = cyan;

  // ===========================================
  // Text Colors
  // ===========================================

  static const Color textPrimary = white;
  static const Color textSecondary = whiteDim;
  static const Color textDisabled = Color(0xFF666666);

  // ===========================================
  // Component Colors
  // ===========================================

  /// PTT Button colors
  static const Color pttIdle = Color(0xFF2A3444);
  static const Color pttRecording = red;
  static const Color pttProcessing = amber;

  /// Connection status
  static const Color connected = green;
  static const Color disconnected = red;
  static const Color connecting = amber;

  // ===========================================
  // PFD Tape Colors
  // ===========================================

  static const Color speedTape = green;
  static const Color altitudeTape = green;
  static const Color headingTape = green;
  static const Color vsTape = green;

  /// Speed limits
  static const Color vmo = red;
  static const Color vfe = amber;
}
