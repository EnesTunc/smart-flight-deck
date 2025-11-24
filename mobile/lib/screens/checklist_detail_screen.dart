import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/checklist_provider.dart';

/// Interactive Checklist Detail Screen
/// Shows checklist items with check/skip functionality
class ChecklistDetailScreen extends ConsumerStatefulWidget {
  final ChecklistInfo checklist;

  const ChecklistDetailScreen({
    super.key,
    required this.checklist,
  });

  @override
  ConsumerState<ChecklistDetailScreen> createState() => _ChecklistDetailScreenState();
}

class _ChecklistDetailScreenState extends ConsumerState<ChecklistDetailScreen> {
  bool _isStarting = false;

  @override
  void initState() {
    super.initState();
    // Start the checklist when screen opens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _startChecklist();
    });
  }

  Future<void> _startChecklist() async {
    setState(() => _isStarting = true);
    await ref.read(checklistProvider.notifier).startChecklist(widget.checklist.id);
    setState(() => _isStarting = false);
  }

  @override
  Widget build(BuildContext context) {
    final checklistState = ref.watch(checklistProvider);
    final status = checklistState.activeStatus;
    final completedItems = checklistState.completedItems;

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.grey.shade900,
        title: Text(
          widget.checklist.name.toUpperCase(),
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            letterSpacing: 1,
          ),
        ),
        centerTitle: true,
        actions: [
          // Progress indicator
          if (status != null && status.active)
            Padding(
              padding: const EdgeInsets.only(right: 12),
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.greenAccent.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${(status.progress * 100).toInt()}%',
                    style: const TextStyle(
                      color: Colors.greenAccent,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
      body: _isStarting
          ? _buildLoadingView()
          : status == null || !status.active
              ? _buildInactiveView(status)
              : _buildActiveChecklist(status, completedItems),
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
            'Starting checklist...',
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildInactiveView(ChecklistStatus? status) {
    final isComplete = status?.state == ChecklistState.complete;

    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            isComplete ? Icons.check_circle : Icons.checklist,
            color: isComplete ? Colors.greenAccent : Colors.grey.shade600,
            size: 80,
          ),
          const SizedBox(height: 24),
          Text(
            isComplete ? 'Checklist Complete!' : 'Checklist not active',
            style: TextStyle(
              color: isComplete ? Colors.greenAccent : Colors.grey.shade400,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 32),
          if (isComplete)
            ElevatedButton.icon(
              onPressed: () => Navigator.of(context).pop(),
              icon: const Icon(Icons.arrow_back),
              label: const Text('Back to Checklists'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.greenAccent,
                foregroundColor: Colors.black,
              ),
            )
          else
            ElevatedButton.icon(
              onPressed: _startChecklist,
              icon: const Icon(Icons.play_arrow),
              label: const Text('Start Checklist'),
            ),
        ],
      ),
    );
  }

  Widget _buildActiveChecklist(ChecklistStatus status, List<String> completedItems) {
    return Column(
      children: [
        // Progress bar
        _buildProgressBar(status.progress),

        // Items list
        Expanded(
          child: _buildItemsList(status, completedItems),
        ),

        // Current item panel
        if (status.currentItem != null) _buildCurrentItemPanel(status),

        // Action buttons
        _buildActionButtons(status),
      ],
    );
  }

  Widget _buildProgressBar(double progress) {
    return Container(
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: progress,
              backgroundColor: Colors.grey.shade800,
              valueColor: const AlwaysStoppedAnimation<Color>(Colors.greenAccent),
              minHeight: 6,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildItemsList(ChecklistStatus status, List<String> completedItems) {
    // Build a mock list of items based on the checklist
    // In a real app, we'd get the full item list from the API
    final currentItemId = status.currentItem?.id;

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      itemCount: widget.checklist.itemsCount,
      itemBuilder: (context, index) {
        // We only know the current item, so we show placeholders for others
        final isCurrentItem = status.currentItem != null && index == _getCurrentItemIndex(status);
        final isCompleted = index < _getCurrentItemIndex(status);
        final isPending = index > _getCurrentItemIndex(status);

        return _buildChecklistItem(
          index: index,
          challenge: isCurrentItem ? status.currentItem!.challenge : 'Item ${index + 1}',
          expected: isCurrentItem ? status.currentItem!.expected : '---',
          isCurrentItem: isCurrentItem,
          isCompleted: isCompleted,
          isPending: isPending,
          isCritical: isCurrentItem ? status.currentItem!.critical : false,
        );
      },
    );
  }

  int _getCurrentItemIndex(ChecklistStatus status) {
    // Calculate current index based on progress
    return ((status.progress) * widget.checklist.itemsCount).floor();
  }

  Widget _buildChecklistItem({
    required int index,
    required String challenge,
    required String expected,
    required bool isCurrentItem,
    required bool isCompleted,
    required bool isPending,
    required bool isCritical,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: isCurrentItem
            ? Colors.greenAccent.withOpacity(0.1)
            : Colors.grey.shade900,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isCurrentItem
              ? Colors.greenAccent
              : isCompleted
                  ? Colors.greenAccent.withOpacity(0.3)
                  : Colors.grey.shade800,
          width: isCurrentItem ? 2 : 1,
        ),
      ),
      child: Row(
        children: [
          // Status icon
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              color: isCompleted
                  ? Colors.greenAccent
                  : isCurrentItem
                      ? Colors.greenAccent.withOpacity(0.3)
                      : Colors.grey.shade800,
              shape: BoxShape.circle,
            ),
            child: Icon(
              isCompleted
                  ? Icons.check
                  : isCurrentItem
                      ? Icons.arrow_forward
                      : Icons.circle_outlined,
              color: isCompleted || isCurrentItem ? Colors.white : Colors.grey.shade600,
              size: 16,
            ),
          ),
          const SizedBox(width: 12),
          // Challenge text
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    if (isCritical && isCurrentItem)
                      Padding(
                        padding: const EdgeInsets.only(right: 6),
                        child: Icon(
                          Icons.warning_amber,
                          color: Colors.amber,
                          size: 14,
                        ),
                      ),
                    Expanded(
                      child: Text(
                        challenge,
                        style: TextStyle(
                          color: isPending ? Colors.grey.shade600 : Colors.white,
                          fontSize: 14,
                          fontWeight: isCurrentItem ? FontWeight.bold : FontWeight.normal,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // Expected response
          Text(
            expected,
            style: TextStyle(
              color: isCompleted
                  ? Colors.greenAccent
                  : isPending
                      ? Colors.grey.shade700
                      : Colors.grey.shade400,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCurrentItemPanel(ChecklistStatus status) {
    final item = status.currentItem!;
    final verified = status.verified;

    return Container(
      margin: const EdgeInsets.all(12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade900,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.greenAccent.withOpacity(0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Challenge
          Row(
            children: [
              Icon(Icons.mic, color: Colors.greenAccent, size: 18),
              const SizedBox(width: 8),
              Text(
                'CURRENT ITEM',
                style: TextStyle(
                  color: Colors.grey.shade500,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            '"${item.challenge}"',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Text(
                'Expected: ',
                style: TextStyle(
                  color: Colors.grey.shade500,
                  fontSize: 13,
                ),
              ),
              Text(
                item.expected,
                style: const TextStyle(
                  color: Colors.greenAccent,
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          // Verification status
          if (verified != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: verified
                    ? Colors.greenAccent.withOpacity(0.2)
                    : Colors.amber.withOpacity(0.2),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    verified ? Icons.check_circle : Icons.warning,
                    color: verified ? Colors.greenAccent : Colors.amber,
                    size: 16,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    verified ? 'VERIFIED' : 'NOT VERIFIED',
                    style: TextStyle(
                      color: verified ? Colors.greenAccent : Colors.amber,
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildActionButtons(ChecklistStatus status) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade900,
        border: Border(
          top: BorderSide(color: Colors.grey.shade700),
        ),
      ),
      child: SafeArea(
        child: Row(
          children: [
            // CHECK button
            Expanded(
              flex: 2,
              child: ElevatedButton.icon(
                onPressed: () => _sendResponse('check'),
                icon: const Icon(Icons.check, size: 20),
                label: const Text('CHECK'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.greenAccent,
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            // SKIP button
            Expanded(
              child: OutlinedButton(
                onPressed: () => _sendResponse('skip'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.amber,
                  side: const BorderSide(color: Colors.amber),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text('SKIP'),
              ),
            ),
            const SizedBox(width: 8),
            // CANCEL button
            IconButton(
              onPressed: _cancelChecklist,
              icon: const Icon(Icons.close, color: Colors.red),
              tooltip: 'Cancel',
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _sendResponse(String response) async {
    HapticFeedback.lightImpact();
    await ref.read(checklistProvider.notifier).sendResponse(response);

    // Check if checklist is complete
    final status = ref.read(checklistProvider).activeStatus;
    if (status?.state == ChecklistState.complete) {
      HapticFeedback.heavyImpact();
    }
  }

  Future<void> _cancelChecklist() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey.shade900,
        title: const Text('Cancel Checklist?', style: TextStyle(color: Colors.white)),
        content: const Text(
          'Are you sure you want to cancel this checklist?',
          style: TextStyle(color: Colors.grey),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('NO'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('YES, CANCEL'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await ref.read(checklistProvider.notifier).cancelChecklist();
      if (mounted) {
        Navigator.of(context).pop();
      }
    }
  }
}
