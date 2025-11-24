import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../providers/bridge_provider.dart';
import '../theme/app_theme.dart';

class QRScannerScreen extends ConsumerStatefulWidget {
  const QRScannerScreen({super.key});

  @override
  ConsumerState<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends ConsumerState<QRScannerScreen> {
  final MobileScannerController _controller = MobileScannerController();
  bool _isProcessing = false;
  String? _errorMessage;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Listen for connection state changes
    ref.listen<BridgeConnectionState>(bridgeProvider, (previous, next) {
      if (next.status == ConnectionStatus.connected) {
        // Successfully connected - go back
        Navigator.of(context).pop();
      } else if (next.status == ConnectionStatus.error) {
        setState(() {
          _errorMessage = next.errorMessage ?? 'Connection failed';
          _isProcessing = false;
        });
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan QR Code'),
        actions: [
          IconButton(
            icon: ValueListenableBuilder<TorchState>(
              valueListenable: _controller.torchState,
              builder: (context, state, child) {
                return Icon(
                  state == TorchState.on ? Icons.flash_on : Icons.flash_off,
                );
              },
            ),
            onPressed: () => _controller.toggleTorch(),
          ),
          IconButton(
            icon: ValueListenableBuilder<CameraFacing>(
              valueListenable: _controller.cameraFacingState,
              builder: (context, state, child) {
                return Icon(
                  state == CameraFacing.front
                      ? Icons.camera_front
                      : Icons.camera_rear,
                );
              },
            ),
            onPressed: () => _controller.switchCamera(),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Stack(
              children: [
                MobileScanner(
                  controller: _controller,
                  onDetect: _onDetect,
                ),
                // Scanning overlay
                Center(
                  child: Container(
                    width: 250,
                    height: 250,
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: _isProcessing
                            ? AppTheme.warningColor
                            : AppTheme.primaryColor,
                        width: 2,
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
                // Loading indicator
                if (_isProcessing)
                  Container(
                    color: Colors.black54,
                    child: const Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          CircularProgressIndicator(),
                          SizedBox(height: 16),
                          Text(
                            'Connecting...',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            ),
          ),
          // Instructions
          Container(
            padding: const EdgeInsets.all(24),
            color: AppTheme.surfaceColor,
            child: Column(
              children: [
                if (_errorMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppTheme.errorColor.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error, color: AppTheme.errorColor),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            _errorMessage!,
                            style: const TextStyle(color: AppTheme.errorColor),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.close,
                              color: AppTheme.errorColor),
                          onPressed: () {
                            setState(() {
                              _errorMessage = null;
                            });
                          },
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
                Text(
                  'Point your camera at the QR code on your PC',
                  style: Theme.of(context).textTheme.bodyLarge,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  'Make sure both devices are on the same Wi-Fi network',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppTheme.textMuted,
                      ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                // Manual connection option
                TextButton.icon(
                  onPressed: _showManualConnectionDialog,
                  icon: const Icon(Icons.edit),
                  label: const Text('Enter IP manually'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _onDetect(BarcodeCapture capture) async {
    if (_isProcessing) return;

    final barcode = capture.barcodes.firstOrNull;
    if (barcode?.rawValue == null) return;

    setState(() {
      _isProcessing = true;
      _errorMessage = null;
    });

    try {
      // Parse QR data
      final data = jsonDecode(barcode!.rawValue!);
      final ip = data['ip'] as String;
      final port = data['port'] as int;
      final sessionToken = data['session_token'] as String;

      // Try to connect using provider
      await ref.read(bridgeProvider.notifier).connect(ip, port, sessionToken);
    } catch (e) {
      setState(() {
        _errorMessage = 'Invalid QR code: ${e.toString()}';
        _isProcessing = false;
      });
    }
  }

  void _showManualConnectionDialog() {
    final ipController = TextEditingController();
    final portController = TextEditingController(text: '8000');
    final tokenController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.surfaceColor,
        title: const Text('Manual Connection'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: ipController,
              decoration: const InputDecoration(
                labelText: 'IP Address',
                hintText: '192.168.1.100',
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: portController,
              decoration: const InputDecoration(
                labelText: 'Port',
                hintText: '8080',
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: tokenController,
              decoration: const InputDecoration(
                labelText: 'Session Token',
                hintText: 'From PC Bridge',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              final ip = ipController.text.trim();
              final port = int.tryParse(portController.text.trim()) ?? 8080;
              final token = tokenController.text.trim();

              if (ip.isNotEmpty && token.isNotEmpty) {
                Navigator.pop(context);
                setState(() {
                  _isProcessing = true;
                  _errorMessage = null;
                });

                await ref
                    .read(bridgeProvider.notifier)
                    .connect(ip, port, token);
              }
            },
            child: const Text('Connect'),
          ),
        ],
      ),
    );
  }
}
