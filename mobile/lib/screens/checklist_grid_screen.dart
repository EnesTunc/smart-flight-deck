import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/checklist_role.dart';
import '../providers/bridge_provider.dart';
import '../providers/checklist_provider.dart';

/// Checklist Grid Screen - PDF/Brochure Style
/// Shows all checklists in a 2-column grid layout
/// User can tap or use voice command to start a checklist
class ChecklistGridScreen extends ConsumerStatefulWidget {
  final ChecklistRole role;

  const ChecklistGridScreen({
    super.key,
    required this.role,
  });

  @override
  ConsumerState<ChecklistGridScreen> createState() => _ChecklistGridScreenState();
}

class _ChecklistGridScreenState extends ConsumerState<ChecklistGridScreen> {
  String? _activeChecklistId;

  // Color palette (from example)
  static const Color kDarkBlue = Color(0xFF2A4B6D);
  static const Color kGreen = Color(0xFF00A651);
  static const Color kBorderGrey = Color(0xFFB0B0B0);
  static const Color kTextBlack = Color(0xFF000000);
  static const Color kAmber = Color(0xFFFF8C00);

  @override
  void initState() {
    super.initState();
    // Load checklists when screen opens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(checklistProvider.notifier).loadChecklists();
    });
  }

  @override
  Widget build(BuildContext context) {
    final checklistState = ref.watch(checklistProvider);
    final simDataStream = ref.watch(simDataStreamProvider);
    final aircraftTitle = simDataStream.when(
      data: (data) => data.aircraft ?? 'Unknown Aircraft',
      loading: () => 'Loading...',
      error: (_, __) => 'Unknown Aircraft',
    );
    final isConnected = ref.watch(isConnectedProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            // Header (Aircraft info + Role)
            _buildHeader(aircraftTitle),

            // Main content
            Expanded(
              child: _buildBody(checklistState, isConnected),
            ),
          ],
        ),
      ),
    );
  }

  // --- Header Design ---
  Widget _buildHeader(String aircraftTitle) {
    return Container(
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: kTextBlack, width: 2)),
      ),
      child: IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Left Logo Area
            Container(
              width: 130,
              color: Colors.grey.shade200,
              padding: const EdgeInsets.all(8),
              child: const Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.flight_takeoff, size: 28, color: kDarkBlue),
                  SizedBox(height: 4),
                  Text(
                    "SMART FLIGHT\nDECK",
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                      height: 1.2,
                    ),
                  ),
                ],
              ),
            ),
            // Center Title
            Expanded(
              child: Center(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8.0),
                  child: FittedBox(
                    fit: BoxFit.scaleDown,
                    child: Text(
                      'CHECKLISTS',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Colors.black.withOpacity(0.9),
                      ),
                    ),
                  ),
                ),
              ),
            ),
            // Right Aircraft + Role Info
            Container(
              width: 130,
              color: Colors.grey.shade100,
              padding: const EdgeInsets.all(8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      const Icon(Icons.airplanemode_active,
                          color: Colors.redAccent, size: 18),
                      const SizedBox(width: 4),
                      Flexible(
                        child: Text(
                          aircraftTitle.toUpperCase(),
                          textAlign: TextAlign.right,
                          style: const TextStyle(
                            fontWeight: FontWeight.w900,
                            fontSize: 10,
                          ),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 2,
                        ),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: widget.role == ChecklistRole.pilotFlying
                          ? kDarkBlue.withOpacity(0.1)
                          : kGreen.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      widget.role.shortName,
                      textAlign: TextAlign.right,
                      style: TextStyle(
                        fontSize: 9,
                        fontWeight: FontWeight.bold,
                        color: widget.role == ChecklistRole.pilotFlying
                            ? kDarkBlue
                            : kGreen,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // --- Body ---
  Widget _buildBody(ChecklistProviderState state, bool isConnected) {
    if (!isConnected) {
      return _buildDisconnectedView();
    }

    if (state.isLoading && state.checklists.isEmpty) {
      return _buildLoadingView();
    }

    if (state.error != null && state.checklists.isEmpty) {
      return _buildErrorView(state.error!);
    }

    if (state.checklists.isEmpty) {
      return _buildEmptyView();
    }

    // Group checklists by phase
    final grouped = _groupChecklistsByPhase(state.checklists);

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: GridView.count(
        crossAxisCount: 2,
        mainAxisSpacing: 16,
        crossAxisSpacing: 16,
        childAspectRatio: 0.75,
        children: grouped.entries.map((entry) {
          final phase = entry.key;
          final checklists = entry.value;
          return _buildPhaseCard(phase, checklists);
        }).toList(),
      ),
    );
  }

  Map<String, List<ChecklistInfo>> _groupChecklistsByPhase(
      List<ChecklistInfo> checklists) {
    final Map<String, List<ChecklistInfo>> grouped = {};
    for (final checklist in checklists) {
      final phase = checklist.phase.isNotEmpty ? checklist.phase : 'General';
      grouped.putIfAbsent(phase, () => []);
      grouped[phase]!.add(checklist);
    }
    return grouped;
  }

  // --- Phase Card (contains multiple checklists) ---
  Widget _buildPhaseCard(String phase, List<ChecklistInfo> checklists) {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: kBorderGrey, width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Blue header bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
            color: kDarkBlue,
            child: Text(
              phase.toUpperCase(),
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
          ),
          // Checklist items
          Expanded(
            child: Container(
              color: Colors.white,
              padding: const EdgeInsets.all(8.0),
              child: ListView.builder(
                itemCount: checklists.length,
                itemBuilder: (context, index) {
                  final checklist = checklists[index];
                  final isActive = _activeChecklistId == checklist.id;
                  return _buildChecklistItem(checklist, isActive);
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  // --- Checklist Item Row ---
  Widget _buildChecklistItem(ChecklistInfo checklist, bool isActive) {
    return GestureDetector(
      onTap: () => _startChecklist(checklist),
      child: Container(
        margin: const EdgeInsets.only(bottom: 4),
        padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 4),
        decoration: BoxDecoration(
          color: isActive ? kGreen.withOpacity(0.1) : Colors.transparent,
          borderRadius: BorderRadius.circular(4),
          border: isActive
              ? Border.all(color: kGreen, width: 2)
              : null,
        ),
        child: Row(
          children: [
            // Status icon
            Icon(
              isActive ? Icons.play_circle : Icons.circle_outlined,
              size: 14,
              color: isActive ? kGreen : Colors.grey.shade400,
            ),
            const SizedBox(width: 6),
            // Checklist name
            Expanded(
              child: Text(
                checklist.name,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                  color: isActive ? kGreen : kTextBlack,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // --- Actions ---
  Future<void> _startChecklist(ChecklistInfo checklist) async {
    HapticFeedback.lightImpact();
    setState(() => _activeChecklistId = checklist.id);
    await ref.read(checklistProvider.notifier).startChecklist(checklist.id);
    // TODO: Start reading items based on role
  }

  // --- Empty/Error Views ---
  Widget _buildDisconnectedView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.wifi_off, color: Colors.grey.shade600, size: 64),
          const SizedBox(height: 16),
          Text(
            'Not Connected',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Connect to Bridge to view checklists',
            style: TextStyle(color: Colors.grey.shade600, fontSize: 14),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingView() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(color: kDarkBlue),
          SizedBox(height: 16),
          Text('Loading checklists...', style: TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }

  Widget _buildErrorView(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, color: Colors.red.shade400, size: 64),
          const SizedBox(height: 16),
          Text(error, style: TextStyle(color: Colors.grey.shade400, fontSize: 16)),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => ref.read(checklistProvider.notifier).loadChecklists(),
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.checklist, color: Colors.grey.shade600, size: 64),
          const SizedBox(height: 16),
          Text(
            'No checklists available',
            style: TextStyle(color: Colors.grey.shade400, fontSize: 16),
          ),
        ],
      ),
    );
  }
}
