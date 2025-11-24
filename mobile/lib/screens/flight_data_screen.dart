import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/bridge_provider.dart';
import '../widgets/pfd_speed_tape.dart';
import '../widgets/pfd_altitude_tape.dart';
import '../widgets/navigation_panel.dart';
import '../widgets/fuel_panel.dart';

/// Flight Data Screen with Tab Navigation
/// Professional EFB-style interface with PFD, NAV, and FUEL tabs.
class FlightDataScreen extends ConsumerStatefulWidget {
  const FlightDataScreen({super.key});

  @override
  ConsumerState<FlightDataScreen> createState() => _FlightDataScreenState();
}

class _FlightDataScreenState extends ConsumerState<FlightDataScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final simDataAsync = ref.watch(simDataStreamProvider);
    final connectionState = ref.watch(bridgeProvider);

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.grey.shade900,
        title: const Text(
          'FLIGHT DATA',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
          ),
        ),
        centerTitle: true,
        actions: [
          // Connection indicator
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: connectionState.isConnected
                      ? Colors.green.withValues(alpha: 0.2)
                      : Colors.red.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      connectionState.isConnected
                          ? Icons.wifi
                          : Icons.wifi_off,
                      size: 14,
                      color: connectionState.isConnected
                          ? Colors.greenAccent
                          : Colors.red,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      connectionState.isConnected ? 'LIVE' : 'OFFLINE',
                      style: TextStyle(
                        color: connectionState.isConnected
                            ? Colors.greenAccent
                            : Colors.red,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.greenAccent,
          indicatorWeight: 3,
          labelColor: Colors.greenAccent,
          unselectedLabelColor: Colors.grey.shade500,
          labelStyle: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 13,
            letterSpacing: 1,
          ),
          tabs: const [
            Tab(
              icon: Icon(Icons.speed, size: 20),
              text: 'PFD',
            ),
            Tab(
              icon: Icon(Icons.navigation, size: 20),
              text: 'NAV',
            ),
            Tab(
              icon: Icon(Icons.local_gas_station, size: 20),
              text: 'FUEL',
            ),
          ],
        ),
      ),
      body: simDataAsync.when(
        data: (simData) => TabBarView(
          controller: _tabController,
          children: [
            _buildPfdTab(simData),
            _buildNavTab(simData),
            _buildFuelTab(simData),
          ],
        ),
        loading: () => _buildLoadingView(),
        error: (error, stack) => _buildErrorView(error.toString()),
      ),
    );
  }

  /// PFD Tab - Speed and Altitude Tapes
  Widget _buildPfdTab(SimData data) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          // PFD Tapes Row
          SizedBox(
            height: 320,
            child: Row(
              children: [
                // Speed Tape
                Expanded(
                  child: PfdSpeedTape(
                    indicatedSpeed: data.indicatedSpeed,
                    groundSpeed: data.groundSpeed,
                    trueAirspeed: data.trueSpeed,
                    mach: data.mach,
                    vmo: 350,
                    vlo: 250,
                    vfe: 230,
                  ),
                ),
                const SizedBox(width: 12),
                // Altitude Tape
                Expanded(
                  child: PfdAltitudeTape(
                    altitude: data.altitude,
                    verticalSpeed: data.verticalSpeed,
                    qnh: data.qnh,
                    isStdBaro: data.altitude > 18000,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          // Aircraft & Phase info card
          _buildInfoCard(data),
        ],
      ),
    );
  }

  /// NAV Tab - Navigation Information
  Widget _buildNavTab(SimData data) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          // Main Navigation Panel
          NavigationPanel(
            heading: data.heading,
            track: data.track,
            windDirection: data.windDirection,
            windSpeed: data.windSpeed,
            oat: data.oat,
            nav1Freq: data.nav1Freq,
            nav1Ident: data.nav1Ident,
            nav1Dme: data.nav1Dme,
            nav2Freq: data.nav2Freq,
            nav2Ident: data.nav2Ident,
            nav2Dme: data.nav2Dme,
          ),
          const SizedBox(height: 16),
          // Position Card
          _buildPositionCard(data),
          const SizedBox(height: 12),
          // Ground Speed & Mach Card
          _buildSpeedInfoCard(data),
        ],
      ),
    );
  }

  /// FUEL Tab - Fuel and Weight Information
  Widget _buildFuelTab(SimData data) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          // Main Fuel Panel
          FuelPanel(
            fuelTotalKg: data.fuelTotalKg,
            fuelFlowKgH: data.fuelFlowKgH,
            fuelEnduranceMin: data.fuelEnduranceMin,
            fuelPercent: data.fuelPercent,
          ),
          const SizedBox(height: 16),
          // Detailed Fuel Info Card
          _buildDetailedFuelCard(data),
          const SizedBox(height: 12),
          // Weight Info Card (placeholder for future)
          _buildWeightCard(data),
        ],
      ),
    );
  }

  Widget _buildInfoCard(SimData data) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade900,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade700, width: 1),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildInfoItem(
            'AIRCRAFT',
            data.aircraft ?? 'Unknown',
            Icons.flight,
          ),
          _buildInfoItem(
            'PHASE',
            data.flightPhase ?? 'N/A',
            Icons.timeline,
          ),
          _buildInfoItem(
            'STATUS',
            data.simConnected ? 'SIM OK' : 'NO SIM',
            data.simConnected ? Icons.check_circle : Icons.error,
            valueColor: data.simConnected ? Colors.greenAccent : Colors.amber,
          ),
        ],
      ),
    );
  }

  Widget _buildPositionCard(SimData data) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade900,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade700, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.location_on, color: Colors.cyan, size: 18),
              const SizedBox(width: 8),
              Text(
                'POSITION',
                style: TextStyle(
                  color: Colors.grey.shade400,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildDataCell('LAT', _formatCoordinate(data.latitude, true)),
              _buildDataCell('LON', _formatCoordinate(data.longitude, false)),
              _buildDataCell('ALT AGL', '${data.altitudeAgl.toStringAsFixed(0)} ft'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSpeedInfoCard(SimData data) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade900,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade700, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.speed, color: Colors.greenAccent, size: 18),
              const SizedBox(width: 8),
              Text(
                'SPEED INFO',
                style: TextStyle(
                  color: Colors.grey.shade400,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildDataCell('GS', '${data.groundSpeed.toStringAsFixed(0)} kt'),
              _buildDataCell('TAS', '${data.trueSpeed.toStringAsFixed(0)} kt'),
              _buildDataCell('MACH', data.mach.toStringAsFixed(2)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDetailedFuelCard(SimData data) {
    final fuelLbs = data.fuelTotalKg * 2.20462;
    final flowLbs = data.fuelFlowKgH * 2.20462;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade900,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade700, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.info_outline, color: Colors.amber, size: 18),
              const SizedBox(width: 8),
              Text(
                'FUEL DETAILS',
                style: TextStyle(
                  color: Colors.grey.shade400,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildDataCell('TOTAL (LBS)', fuelLbs.toStringAsFixed(0)),
              _buildDataCell('FLOW (LBS/H)', flowLbs.toStringAsFixed(0)),
              _buildDataCell('PERCENT', '${data.fuelPercent.toStringAsFixed(1)}%'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildWeightCard(SimData data) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade900,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade700, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.scale, color: Colors.purple.shade300, size: 18),
              const SizedBox(width: 8),
              Text(
                'WEIGHT & BALANCE',
                style: TextStyle(
                  color: Colors.grey.shade400,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Center(
            child: Text(
              'Coming soon...',
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 13,
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDataCell(String label, String value) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            color: Colors.grey.shade500,
            fontSize: 10,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.bold,
            fontFamily: 'monospace',
          ),
        ),
      ],
    );
  }

  String _formatCoordinate(double value, bool isLatitude) {
    final direction = isLatitude
        ? (value >= 0 ? 'N' : 'S')
        : (value >= 0 ? 'E' : 'W');
    final absValue = value.abs();
    final degrees = absValue.floor();
    final minutes = ((absValue - degrees) * 60).toStringAsFixed(2);
    return '$degrees°$minutes\'$direction';
  }

  Widget _buildInfoItem(String label, String value, IconData icon, {Color? valueColor}) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          icon,
          color: Colors.grey.shade500,
          size: 20,
        ),
        const SizedBox(height: 4),
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
            color: valueColor ?? Colors.white,
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }

  Widget _buildLoadingView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(
            color: Colors.greenAccent,
          ),
          const SizedBox(height: 16),
          Text(
            'Waiting for sim data...',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorView(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            color: Colors.red.shade400,
            size: 48,
          ),
          const SizedBox(height: 16),
          Text(
            'No data available',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Text(
              'Connect to PC Bridge and start MSFS to see flight data',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.grey.shade500,
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
