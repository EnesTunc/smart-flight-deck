import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'theme/app_theme.dart';
import 'core/constants/app_constants.dart';
import 'screens/home_screen.dart';
import 'providers/settings_provider.dart';

/// Main application widget
class SmartFlightDeckApp extends ConsumerWidget {
  const SmartFlightDeckApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch theme mode from settings
    final settings = ref.watch(settingsProvider);

    return MaterialApp(
      title: AppConstants.appName,
      debugShowCheckedModeBanner: false,

      // Theme - now dynamic based on user settings
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: settings.themeMode,

      // Home
      home: const HomeScreen(),

      // Routes (to be implemented)
      // routes: {
      //   AppConstants.routeConnection: (context) => const ConnectionScreen(),
      //   AppConstants.routeQrScanner: (context) => const QrScannerScreen(),
      //   AppConstants.routeMap: (context) => const MapScreen(),
      //   AppConstants.routeFlightData: (context) => const FlightDataScreen(),
      //   AppConstants.routeChecklist: (context) => const ChecklistScreen(),
      //   AppConstants.routeAirport: (context) => const AirportScreen(),
      //   AppConstants.routeSettings: (context) => const SettingsScreen(),
      // },
    );
  }
}
