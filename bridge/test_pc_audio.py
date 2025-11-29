"""
Test script for PC microphone recording
Run this to verify PC audio recording works correctly
"""

import time
from audio.pc_recorder import PcRecorder


def test_pc_recording():
    """Test PC microphone recording."""
    print("=" * 60)
    print("PC Microphone Recording Test")
    print("=" * 60)

    # Create recorder
    recorder = PcRecorder(sample_rate=16000, channels=1)

    # List available devices
    print("\nAvailable input devices:")
    devices = recorder.get_available_devices()
    for dev in devices:
        print(f"  [{dev['index']}] {dev['name']}")
        print(f"       Channels: {dev['channels']}, Sample Rate: {dev['sample_rate']}Hz")

    if not devices:
        print("ERROR: No input devices found!")
        return

    # Use default device
    print(f"\nUsing default input device")
    print("-" * 60)

    # Start recording
    print("\nStarting recording...")
    success = recorder.start_recording()

    if not success:
        print("ERROR: Failed to start recording!")
        return

    print("✓ Recording started successfully")
    print("Recording for 5 seconds... Speak now!")

    # Record for 5 seconds
    time.sleep(5)

    # Stop recording
    print("\nStopping recording...")
    wav_bytes = recorder.stop_recording()

    if wav_bytes:
        print(f"✓ Recording stopped successfully")
        print(f"  Audio data: {len(wav_bytes)} bytes")
        print(f"  Duration: ~5 seconds")

        # Save to file for verification
        output_file = "test_recording.wav"
        with open(output_file, "wb") as f:
            f.write(wav_bytes)
        print(f"  Saved to: {output_file}")
        print("\nYou can play this file to verify the recording!")
    else:
        print("ERROR: Failed to get audio data!")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_pc_recording()
