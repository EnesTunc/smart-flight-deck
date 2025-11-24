import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'bridge_provider.dart';

// =============================================================================
// Checklist Models
// =============================================================================

class ChecklistInfo {
  final String id;
  final String name;
  final String nameTr;
  final String phase;
  final int itemsCount;
  final bool isCompleted;

  const ChecklistInfo({
    required this.id,
    required this.name,
    this.nameTr = '',
    this.phase = '',
    this.itemsCount = 0,
    this.isCompleted = false,
  });

  factory ChecklistInfo.fromJson(Map<String, dynamic> json) {
    return ChecklistInfo(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      nameTr: json['name_tr'] ?? '',
      phase: json['phase'] ?? '',
      itemsCount: json['items_count'] ?? 0,
      isCompleted: json['is_completed'] ?? false,
    );
  }
}

class ChecklistItem {
  final String id;
  final String challenge;
  final String expected;
  final bool critical;
  final String? notes;

  const ChecklistItem({
    required this.id,
    required this.challenge,
    required this.expected,
    this.critical = false,
    this.notes,
  });

  factory ChecklistItem.fromJson(Map<String, dynamic> json) {
    return ChecklistItem(
      id: json['id'] ?? '',
      challenge: json['challenge'] ?? '',
      expected: json['expected'] ?? json['expected_response'] ?? '',
      critical: json['critical'] ?? false,
      notes: json['notes'],
    );
  }
}

enum ChecklistState {
  idle,
  running,
  waiting,
  paused,
  complete,
}

class ChecklistStatus {
  final bool active;
  final ChecklistState state;
  final String? checklistName;
  final ChecklistItem? currentItem;
  final double progress;
  final int itemsRemaining;
  final bool? verified;
  final String? verificationMessage;
  final String? ttsText;

  const ChecklistStatus({
    this.active = false,
    this.state = ChecklistState.idle,
    this.checklistName,
    this.currentItem,
    this.progress = 0.0,
    this.itemsRemaining = 0,
    this.verified,
    this.verificationMessage,
    this.ttsText,
  });

  factory ChecklistStatus.fromJson(Map<String, dynamic> json) {
    ChecklistItem? currentItem;
    if (json['current_item'] != null) {
      currentItem = ChecklistItem.fromJson(json['current_item']);
    }

    // Parse state to determine if active
    final state = _parseState(json['state']);
    // Active if state is RUNNING or WAITING (not IDLE, COMPLETE, or PAUSED)
    final isActive = json['active'] ??
        (state == ChecklistState.running || state == ChecklistState.waiting);

    return ChecklistStatus(
      active: isActive,
      state: state,
      checklistName: json['checklist_name'],
      currentItem: currentItem,
      progress: (json['progress'] ?? 0.0).toDouble(),
      itemsRemaining: json['items_remaining'] ?? 0,
      verified: json['verified'],
      verificationMessage: json['verification_message'],
      ttsText: json['tts_text'],
    );
  }

  static ChecklistState _parseState(String? state) {
    switch (state?.toUpperCase()) {
      case 'RUNNING':
        return ChecklistState.running;
      case 'WAITING':
        return ChecklistState.waiting;
      case 'PAUSED':
        return ChecklistState.paused;
      case 'COMPLETE':
        return ChecklistState.complete;
      default:
        return ChecklistState.idle;
    }
  }
}

// =============================================================================
// Checklist Provider State
// =============================================================================

class ChecklistProviderState {
  final List<ChecklistInfo> checklists;
  final String? currentAircraft;
  final ChecklistStatus? activeStatus;
  final List<String> completedItems; // Track completed item IDs
  final bool isLoading;
  final String? error;

  const ChecklistProviderState({
    this.checklists = const [],
    this.currentAircraft,
    this.activeStatus,
    this.completedItems = const [],
    this.isLoading = false,
    this.error,
  });

  ChecklistProviderState copyWith({
    List<ChecklistInfo>? checklists,
    String? currentAircraft,
    ChecklistStatus? activeStatus,
    List<String>? completedItems,
    bool? isLoading,
    String? error,
  }) {
    return ChecklistProviderState(
      checklists: checklists ?? this.checklists,
      currentAircraft: currentAircraft ?? this.currentAircraft,
      activeStatus: activeStatus ?? this.activeStatus,
      completedItems: completedItems ?? this.completedItems,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

// =============================================================================
// Checklist Notifier
// =============================================================================

class ChecklistNotifier extends StateNotifier<ChecklistProviderState> {
  final Ref _ref;
  Dio? _dio;

  ChecklistNotifier(this._ref) : super(const ChecklistProviderState());

  Dio? get _client {
    final connectionState = _ref.read(bridgeProvider);
    if (!connectionState.isConnected) return null;

    _dio ??= Dio(BaseOptions(
      baseUrl: 'http://${connectionState.bridgeIp}:${connectionState.bridgePort}',
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 10),
      headers: {
        'X-Session-Token': connectionState.sessionToken,
      },
    ));
    return _dio;
  }

  /// Load available checklists from Bridge
  Future<void> loadChecklists() async {
    final dio = _client;
    if (dio == null) {
      state = state.copyWith(error: 'Not connected');
      return;
    }

    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await dio.get('/api/checklist/list');
      final data = response.data;

      final checklists = (data['checklists'] as List?)
              ?.map((c) => ChecklistInfo.fromJson(c))
              .toList() ??
          [];

      state = state.copyWith(
        checklists: checklists,
        currentAircraft: data['aircraft'],
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load checklists',
      );
    }
  }

  /// Start a checklist
  Future<bool> startChecklist(String checklistId) async {
    final dio = _client;
    if (dio == null) return false;

    state = state.copyWith(isLoading: true, error: null, completedItems: []);

    try {
      final response = await dio.post('/api/checklist/start/$checklistId');
      final status = ChecklistStatus.fromJson(response.data);

      state = state.copyWith(
        activeStatus: status,
        isLoading: false,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to start checklist',
      );
      return false;
    }
  }

  /// Send response (check, skip, override)
  Future<bool> sendResponse(String response) async {
    final dio = _client;
    if (dio == null) return false;

    try {
      final result = await dio.post(
        '/api/checklist/response',
        data: {'response': response},
      );
      final status = ChecklistStatus.fromJson(result.data);

      // Track completed items
      List<String> completed = List.from(state.completedItems);
      if (response == 'check' && state.activeStatus?.currentItem != null) {
        completed.add(state.activeStatus!.currentItem!.id);
      }

      state = state.copyWith(
        activeStatus: status,
        completedItems: completed,
      );
      return true;
    } catch (e) {
      return false;
    }
  }

  /// Get current status
  Future<void> refreshStatus() async {
    final dio = _client;
    if (dio == null) return;

    try {
      final response = await dio.get('/api/checklist/status');
      final status = ChecklistStatus.fromJson(response.data);
      state = state.copyWith(activeStatus: status);
    } catch (e) {
      // Ignore errors
    }
  }

  /// Cancel active checklist
  Future<void> cancelChecklist() async {
    final dio = _client;
    if (dio == null) return;

    try {
      await dio.post('/api/checklist/cancel');
      state = state.copyWith(
        activeStatus: const ChecklistStatus(),
        completedItems: [],
      );
    } catch (e) {
      // Ignore errors
    }
  }

  /// Clear state
  void clear() {
    _dio = null;
    state = const ChecklistProviderState();
  }
}

// =============================================================================
// Providers
// =============================================================================

final checklistProvider =
    StateNotifierProvider<ChecklistNotifier, ChecklistProviderState>(
  (ref) => ChecklistNotifier(ref),
);
