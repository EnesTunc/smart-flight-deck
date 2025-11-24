import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/bridge_provider.dart';
import '../providers/checklist_provider.dart';
import 'checklist_detail_screen.dart';

/// Checklist List Screen - Shows available checklists in a booklet/brochure style
class ChecklistScreen extends ConsumerStatefulWidget {
  const ChecklistScreen({super.key});

  @override
  ConsumerState<ChecklistScreen> createState() => _ChecklistScreenState();
}

class _ChecklistScreenState extends ConsumerState<ChecklistScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    // Load checklists when screen opens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(checklistProvider.notifier).loadChecklists();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final checklistState = ref.watch(checklistProvider);
    final isConnected = ref.watch(isConnectedProvider);

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.grey.shade900,
        title: const Text(
          'CHECKLISTS',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.2,
          ),
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: isConnected
                ? () => ref.read(checklistProvider.notifier).loadChecklists()
                : null,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: Column(
        children: [
          // Aircraft info bar
          _buildAircraftBar(checklistState.currentAircraft),

          // Search bar
          _buildSearchBar(),

          // Checklists list
          Expanded(
            child: _buildBody(checklistState, isConnected),
          ),
        ],
      ),
    );
  }

  Widget _buildAircraftBar(String? aircraft) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.grey.shade900,
        border: Border(
          bottom: BorderSide(color: Colors.grey.shade700, width: 1),
        ),
      ),
      child: Row(
        children: [
          Icon(Icons.flight, color: Colors.greenAccent, size: 18),
          const SizedBox(width: 8),
          Text(
            'Aircraft: ',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 13,
            ),
          ),
          Expanded(
            child: Text(
              aircraft ?? 'Default',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 13,
                fontWeight: FontWeight.bold,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      padding: const EdgeInsets.all(12),
      child: TextField(
        controller: _searchController,
        onChanged: (value) => setState(() => _searchQuery = value.toLowerCase()),
        style: const TextStyle(color: Colors.white),
        decoration: InputDecoration(
          hintText: 'Search checklists...',
          hintStyle: TextStyle(color: Colors.grey.shade500),
          prefixIcon: Icon(Icons.search, color: Colors.grey.shade500),
          suffixIcon: _searchQuery.isNotEmpty
              ? IconButton(
                  icon: Icon(Icons.clear, color: Colors.grey.shade500),
                  onPressed: () {
                    _searchController.clear();
                    setState(() => _searchQuery = '');
                  },
                )
              : null,
          filled: true,
          fillColor: Colors.grey.shade900,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: BorderSide(color: Colors.grey.shade700),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: BorderSide(color: Colors.grey.shade700),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: const BorderSide(color: Colors.greenAccent),
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        ),
      ),
    );
  }

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

    // Filter checklists by search query
    final filteredChecklists = state.checklists.where((c) {
      if (_searchQuery.isEmpty) return true;
      return c.name.toLowerCase().contains(_searchQuery) ||
          c.phase.toLowerCase().contains(_searchQuery);
    }).toList();

    if (filteredChecklists.isEmpty) {
      return _buildNoResultsView();
    }

    return _buildChecklistGrid(filteredChecklists);
  }

  Widget _buildChecklistGrid(List<ChecklistInfo> checklists) {
    // Group checklists by phase
    final Map<String, List<ChecklistInfo>> grouped = {};
    for (final checklist in checklists) {
      final phase = checklist.phase.isNotEmpty ? checklist.phase : 'General';
      grouped.putIfAbsent(phase, () => []);
      grouped[phase]!.add(checklist);
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: grouped.length,
      itemBuilder: (context, index) {
        final phase = grouped.keys.elementAt(index);
        final items = grouped[phase]!;

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Phase header
            Padding(
              padding: const EdgeInsets.only(left: 4, top: 8, bottom: 8),
              child: Text(
                phase.toUpperCase(),
                style: TextStyle(
                  color: Colors.grey.shade500,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.5,
                ),
              ),
            ),
            // Checklist cards
            ...items.map((checklist) => _buildChecklistCard(checklist)),
            const SizedBox(height: 8),
          ],
        );
      },
    );
  }

  Widget _buildChecklistCard(ChecklistInfo checklist) {
    final isCompleted = checklist.isCompleted;

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: Colors.grey.shade900,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          onTap: () => _openChecklist(checklist),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isCompleted ? Colors.greenAccent.withOpacity(0.5) : Colors.grey.shade700,
                width: 1,
              ),
            ),
            child: Row(
              children: [
                // Checklist icon
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: isCompleted
                        ? Colors.greenAccent.withOpacity(0.2)
                        : Colors.grey.shade800,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    isCompleted ? Icons.check_circle : Icons.checklist,
                    color: isCompleted ? Colors.greenAccent : Colors.grey.shade400,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                // Checklist info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        checklist.name,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Text(
                            '${checklist.itemsCount} items',
                            style: TextStyle(
                              color: Colors.grey.shade500,
                              fontSize: 12,
                            ),
                          ),
                          if (isCompleted) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.greenAccent.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: const Text(
                                'COMPLETED',
                                style: TextStyle(
                                  color: Colors.greenAccent,
                                  fontSize: 9,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),
                // Arrow
                Icon(
                  Icons.chevron_right,
                  color: Colors.grey.shade500,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _openChecklist(ChecklistInfo checklist) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => ChecklistDetailScreen(checklist: checklist),
      ),
    );
  }

  Widget _buildDisconnectedView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.wifi_off,
            color: Colors.grey.shade600,
            size: 64,
          ),
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
            style: TextStyle(
              color: Colors.grey.shade600,
              fontSize: 14,
            ),
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
          CircularProgressIndicator(color: Colors.greenAccent),
          SizedBox(height: 16),
          Text(
            'Loading checklists...',
            style: TextStyle(color: Colors.grey),
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
            size: 64,
          ),
          const SizedBox(height: 16),
          Text(
            error,
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 16,
            ),
          ),
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
          Icon(
            Icons.checklist,
            color: Colors.grey.shade600,
            size: 64,
          ),
          const SizedBox(height: 16),
          Text(
            'No checklists available',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNoResultsView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.search_off,
            color: Colors.grey.shade600,
            size: 64,
          ),
          const SizedBox(height: 16),
          Text(
            'No checklists match "$_searchQuery"',
            style: TextStyle(
              color: Colors.grey.shade400,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
}
