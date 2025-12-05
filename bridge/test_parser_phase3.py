"""
Faz 3.1 - Command Parser Detaylı Testler
"""
from logic.parser import CommandParser

def test_basic_commands():
    """3.1.1 - Temel komut tanıma"""
    parser = CommandParser()

    tests = [
        ("gear down", "gear_down", {}),
        ("flaps two", "flaps_set", {"position": 2}),  # Parser returns int
        ("landing lights on", "landing_lights_toggle", {}),
    ]

    print("=" * 60)
    print("TEST 3.1.1: Temel Komut Tanıma")
    print("=" * 60)

    passed = 0
    for text, expected_intent, expected_params in tests:
        result = parser.parse(text)

        if result and result.intent == expected_intent:
            # Check parameters if expected
            params_match = True
            for key, value in expected_params.items():
                if result.parameters.get(key) != value:
                    params_match = False
                    break

            if params_match:
                print(f"[PASS] '{text}' -> {result.intent}")
                passed += 1
            else:
                print(f"[FAIL] '{text}' -> {result.intent} (params mismatch)")
                print(f"       Expected: {expected_params}")
                print(f"       Got: {result.parameters}")
        else:
            actual = result.intent if result else "None"
            print(f"[FAIL] '{text}' -> {actual} (expected: {expected_intent})")

    print()
    print(f"Result: {passed}/{len(tests)} passed")
    print()
    return passed == len(tests)


def test_aliases():
    """3.1.2 - Alias ve varyasyonlar"""
    parser = CommandParser()

    tests = [
        ("lower the gear", "gear_down"),
        ("raise the gear", "gear_up"),
        ("set flaps one", "flaps_set"),
        ("lower the landing gear", "gear_down"),  # Faz 2'de eklendi
    ]

    print("=" * 60)
    print("TEST 3.1.2: Alias ve Varyasyonlar")
    print("=" * 60)

    passed = 0
    for text, expected_intent in tests:
        result = parser.parse(text)

        if result and result.intent == expected_intent:
            print(f"[PASS] '{text}' -> {result.intent}")
            passed += 1
        else:
            actual = result.intent if result else "None"
            print(f"[FAIL] '{text}' -> {actual} (expected: {expected_intent})")

    print()
    print(f"Result: {passed}/{len(tests)} passed")
    print()
    return passed == len(tests)


def test_unknown_commands():
    """3.1.3 - Tanınmayan komutlar"""
    parser = CommandParser()

    tests = [
        "blabla nonsense",
        "xyz unknown command",
        "asdfasdf",
    ]

    print("=" * 60)
    print("TEST 3.1.3: Unknown Command Handling")
    print("=" * 60)

    passed = 0
    for text in tests:
        result = parser.parse(text)

        if result is None:
            print(f"[PASS] '{text}' -> None (correctly not matched)")
            passed += 1
        else:
            print(f"[FAIL] '{text}' -> {result.intent} (should be None)")

    print()
    print(f"Result: {passed}/{len(tests)} passed")
    print()
    return passed == len(tests)


def test_confidence_scores():
    """Bonus - Confidence değerleri"""
    parser = CommandParser()

    tests = [
        ("gear down", 0.9),  # Pattern match = high
        ("girda", 0.7),      # Fuzzy match = lower
    ]

    print("=" * 60)
    print("BONUS TEST: Confidence Scores")
    print("=" * 60)

    for text, expected_min_confidence in tests:
        result = parser.parse(text)

        if result:
            status = "[PASS]" if result.confidence >= expected_min_confidence else "[WARN]"
            print(f"{status} '{text}' -> confidence={result.confidence:.2f} (min={expected_min_confidence})")
        else:
            print(f"[FAIL] '{text}' -> No match")

    print()


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("         FAZ 3.1 - COMMAND PARSER TESTS")
    print("=" * 60)
    print()

    results = {
        "3.1.1 Basic Commands": test_basic_commands(),
        "3.1.2 Aliases": test_aliases(),
        "3.1.3 Unknown Commands": test_unknown_commands(),
    }

    test_confidence_scores()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")

    total_passed = sum(1 for r in results.values() if r)
    print()
    print(f"Total: {total_passed}/{len(results)} test groups passed")
    print()
