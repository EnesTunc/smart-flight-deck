// Smart Flight Deck basic widget test.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:smart_flight_deck/app.dart';

void main() {
  testWidgets('App launches and shows title', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      const ProviderScope(
        child: SmartFlightDeckApp(),
      ),
    );

    // Verify that the app title is displayed.
    expect(find.text('Smart Flight Deck'), findsOneWidget);
  });
}
