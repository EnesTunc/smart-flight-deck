import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../theme/app_theme.dart';
import '../widgets/connection_status.dart';
import '../widgets/ptt_button.dart';
import '../widgets/quick_commands.dart';
import '../widgets/sim_data_panel.dart';
import 'qr_scanner_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  bool _isConnected = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Smart Flight Deck'),
        actions: [
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
        child: _isConnected ? _buildConnectedView() : _buildDisconnectedView(),
      ),
    );
  }

  Widget _buildDisconnectedView() {
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
              'Not Connected',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 12),
            Text(
              'Scan the QR code displayed on your PC to connect',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
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

  Widget _buildConnectedView() {
    return Column(
      children: [
        // Connection status bar
        const ConnectionStatus(),

        // Sim data panel
        const Padding(
          padding: EdgeInsets.all(16.0),
          child: SimDataPanel(),
        ),

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
        builder: (context) => QRScannerScreen(
          onConnected: () {
            setState(() {
              _isConnected = true;
            });
            Navigator.of(context).pop();
          },
        ),
      ),
    );
  }

  void _openSettings() {
    // TODO: Implement settings screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Settings coming soon')),
    );
  }
}
