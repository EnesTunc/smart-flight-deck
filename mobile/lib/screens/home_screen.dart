import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/bridge_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/connection_status.dart';
import '../widgets/ptt_button.dart';
import '../widgets/quick_commands.dart';
import '../widgets/sim_data_panel.dart';
import 'checklist_screen.dart';
import 'flight_data_screen.dart';
import 'qr_scanner_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  @override
  void initState() {
    super.initState();
    // Try to load saved connection on startup
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(bridgeProvider.notifier).loadSavedConnection();
    });
  }

  @override
  Widget build(BuildContext context) {
    final connectionState = ref.watch(bridgeProvider);
    final isConnected = connectionState.isConnected;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Smart Flight Deck'),
        actions: [
          if (isConnected)
            IconButton(
              icon: const Icon(Icons.link_off),
              onPressed: _disconnect,
              tooltip: 'Disconnect',
            ),
          IconButton(
            icon: const Icon(Icons.qr_code_scanner),
            onPressed: _openQRScanner,
            tooltip: 'Scan QR to connect',
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: _openSettings,
          ),
        ],
      ),
      body: SafeArea(
        child: isConnected ? _buildConnectedView() : _buildDisconnectedView(),
      ),
    );
  }

  Widget _buildDisconnectedView() {
    final connectionState = ref.watch(bridgeProvider);

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.flight,
              size: 80,
              color: AppTheme.textMuted,
            ),
            const SizedBox(height: 24),
            Text(
              _getStatusText(connectionState.status),
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 12),
            // Only show error if user actively tried to connect (not from auto-reconnect)
            if (connectionState.status == ConnectionStatus.error &&
                connectionState.errorMessage != null &&
                !connectionState.errorMessage!.contains('saved')) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.errorColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.warning_amber, color: AppTheme.errorColor, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      _getSimplifiedError(connectionState.errorMessage!),
                      textAlign: TextAlign.center,
                      style: TextStyle(color: AppTheme.errorColor),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
            ],
            if (connectionState.status == ConnectionStatus.reconnecting) ...[
              const CircularProgressIndicator(),
              const SizedBox(height: 12),
              Text(
                'Attempting to reconnect...',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ] else ...[
              Text(
                'Scan the QR code displayed on your PC to connect',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
            const SizedBox(height: 32),
            ElevatedButton.icon(
              onPressed: _openQRScanner,
              icon: const Icon(Icons.qr_code_scanner),
              label: const Text('Scan QR Code'),
            ),
          ],
        ),
      ),
    );
  }

  /// Convert technical error messages to user-friendly text
  String _getSimplifiedError(String error) {
    final errorLower = error.toLowerCase();

    if (errorLower.contains('timeout') || errorLower.contains('timed out')) {
      return 'Connection timed out';
    } else if (errorLower.contains('refused') || errorLower.contains('unreachable')) {
      return 'Bridge not reachable';
    } else if (errorLower.contains('websocket')) {
      return 'Connection lost';
    } else if (errorLower.contains('verify') || errorLower.contains('401')) {
      return 'Session expired';
    } else if (errorLower.contains('network') || errorLower.contains('socket')) {
      return 'Network error';
    }
    // Default short message
    return 'Connection failed';
  }

  String _getStatusText(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.disconnected:
        return 'Not Connected';
      case ConnectionStatus.connecting:
        return 'Connecting...';
      case ConnectionStatus.connected:
        return 'Connected';
      case ConnectionStatus.error:
        return 'Connection Error';
      case ConnectionStatus.reconnecting:
        return 'Reconnecting...';
    }
  }

  Widget _buildConnectedView() {
    return Column(
      children: [
        // Connection status bar
        const ConnectionStatusBar(),

        // Sim data panel
        const Padding(
          padding: EdgeInsets.all(16.0),
          child: SimDataPanel(),
        ),

        // Navigation buttons row
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          child: Row(
            children: [
              Expanded(
                child: _NavButton(
                  icon: Icons.speed,
                  label: 'FLIGHT DATA',
                  onTap: () => _openFlightData(),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _NavButton(
                  icon: Icons.checklist,
                  label: 'CHECKLIST',
                  onTap: () => _openChecklist(),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _NavButton(
                  icon: Icons.local_airport,
                  label: 'AIRPORT',
                  onTap: () => _openAirport(),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _NavButton(
                  icon: Icons.map,
                  label: 'MAP',
                  onTap: () => _openMap(),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // Quick command buttons
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16.0),
          child: QuickCommands(),
        ),

        const Spacer(),

        // PTT Button
        const Padding(
          padding: EdgeInsets.all(32.0),
          child: PTTButton(),
        ),

        const SizedBox(height: 32),
      ],
    );
  }

  void _openQRScanner() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const QRScannerScreen(),
      ),
    );
  }

  void _disconnect() {
    ref.read(bridgeProvider.notifier).disconnect();
  }

  void _openSettings() {
    // TODO: Implement settings screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Settings coming soon')),
    );
  }

  void _openFlightData() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const FlightDataScreen(),
      ),
    );
  }

  void _openChecklist() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const ChecklistScreen(),
      ),
    );
  }

  void _openAirport() {
    // TODO: Implement airport screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Airport info coming soon')),
    );
  }

  void _openMap() {
    // TODO: Implement map screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Moving map coming soon')),
    );
  }
}

/// Navigation button widget for the home screen
class _NavButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _NavButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.grey.shade900,
      borderRadius: BorderRadius.circular(8),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.shade700, width: 1),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                color: Colors.greenAccent,
                size: 24,
              ),
              const SizedBox(height: 4),
              Text(
                label,
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 9,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
