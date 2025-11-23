import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'theme/app_theme.dart';
import 'core/constants/app_constants.dart';
import 'screens/home_screen.dart';

/// Main application widget
class SmartFlightDeckApp extends ConsumerWidget {
  const SmartFlightDeckApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp(
      title: AppConstants.appName,
      debugShowCheckedModeBanner: false,

      // Theme
      theme: AppTheme.darkTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.dark, // Always dark for cockpit use

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
