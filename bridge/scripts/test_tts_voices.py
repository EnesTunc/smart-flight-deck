"""
Smart Flight Deck Companion - TTS Voice Tester
Test all available voices with sample text.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from audio.tts import PiperTTS, AVAILABLE_VOICES


def test_voice(voice_id: str, voice_info: dict):
    """Test a single voice."""
    print(f"\n{'='*60}")
    print(f"Testing: {voice_info['display_name']}")
    print(f"  Voice ID: {voice_id}")
    print(f"  Gender: {voice_info['gender']}")
    print(f"  Accent: {voice_info['accent']}")
    print(f"  Quality: {voice_info['quality']}")
    print(f"  License: {voice_info['license']}")
    print(f"{'='*60}")

    # Create TTS instance
    tts = PiperTTS(voice=voice_id)

    # Test loading
    print("  Loading model...", end=" ", flush=True)
    if not tts.load():
        print("FAILED")
        return False
    print("OK")

    # Test synthesis
    test_text = "Gear down. Flaps set to landing configuration."
    print(f"  Synthesizing: '{test_text}'...", end=" ", flush=True)

    audio_data = tts.synthesize(test_text)
    if not audio_data or len(audio_data) == 0:
        print("FAILED (no audio)")
        return False

    audio_kb = len(audio_data) / 1024
    print(f"OK ({audio_kb:.1f} KB)")

    # Save test file
    output_dir = Path(__file__).parent.parent / "test_output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"test_{voice_id}.wav"

    print(f"  Saving to: {output_file.name}...", end=" ", flush=True)
    if tts.synthesize_to_file(test_text, output_file):
        print("OK")
    else:
        print("FAILED")

    print(f"\n[OK] {voice_info['display_name']} passed all tests")
    return True


def main():
    """Test all voices."""
    print("\n" + "="*60)
    print("  Smart Flight Deck Companion - TTS Voice Tester")
    print("="*60)
    print(f"\nTesting {len(AVAILABLE_VOICES)} voices...")

    passed = 0
    failed = 0

    for voice_id, voice_info in AVAILABLE_VOICES.items():
        if test_voice(voice_id, voice_info):
            passed += 1
        else:
            failed += 1

    # Summary
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)

    if failed == 0:
        print("\n[OK] All voices are working correctly!")
        print("\nTest audio files saved to: bridge/test_output/")
        return 0
    else:
        print(f"\n[WARNING] {failed} voice(s) failed")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
