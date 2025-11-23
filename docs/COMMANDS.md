# Smart Flight Deck Companion - Voice Commands Reference

## Command Categories

### Gear Commands

| Voice Command | Variations | Action |
|---------------|------------|--------|
| "Gear down" | "Lower the gear", "Gear extend", "Drop the gear" | Extend landing gear |
| "Gear up" | "Raise the gear", "Gear retract", "Retract gear" | Retract landing gear |

**Safety Check:** Gear extension is blocked if:
- Speed > 250 knots

---

### Flaps Commands

| Voice Command | Variations | Action |
|---------------|------------|--------|
| "Flaps up" | "Flaps zero", "Flaps 0" | Retract flaps fully |
| "Flaps down" | "Extend flaps" | Extend flaps one notch |
| "Flaps 1" | "Flaps one" | Set flaps to position 1 |
| "Flaps 2" | "Flaps two", "Flaps 10" | Set flaps to position 2 |
| "Flaps 3" | "Flaps three", "Flaps 15" | Set flaps to position 3 |
| "Flaps full" | "Flaps 4", "Flaps four", "Flaps 20" | Set flaps to full |

**Safety Checks:**
| Position | Max Speed |
|----------|-----------|
| Flaps 1 | 250 kts |
| Flaps 2 | 200 kts |
| Flaps 3 | 180 kts |
| Flaps Full | 160 kts |

---

### Lights Commands

| Voice Command | Variations | Action |
|---------------|------------|--------|
| "Landing lights on" | "Turn on landing lights", "Lights on" | Turn on landing lights |
| "Landing lights off" | "Turn off landing lights", "Lights off" | Turn off landing lights |
| "Strobes on" | "Strobe lights on" | Turn on strobe lights |
| "Strobes off" | "Strobe lights off" | Turn off strobe lights |
| "Beacon on" | "Beacon lights on" | Turn on beacon |
| "Beacon off" | "Beacon lights off" | Turn off beacon |
| "Nav lights on" | "Navigation lights on" | Turn on nav lights |
| "Taxi lights on" | - | Turn on taxi lights |

---

### Brake Commands

| Voice Command | Variations | Action |
|---------------|------------|--------|
| "Parking brake" | "Set parking brake", "Release parking brake" | Toggle parking brake |

---

### Spoiler Commands

| Voice Command | Variations | Action |
|---------------|------------|--------|
| "Arm spoilers" | "Spoilers arm", "Arm the spoilers" | Arm ground spoilers |
| "Spoilers on" | "Deploy spoilers", "Extend spoilers" | Deploy spoilers |
| "Spoilers off" | "Retract spoilers" | Retract spoilers |

---

### Autopilot Commands

| Voice Command | Variations | Action |
|---------------|------------|--------|
| "Autopilot on" | "Engage autopilot" | Enable autopilot master |
| "Autopilot off" | "Disengage autopilot" | Disable autopilot master |
| "Heading hold" | "Heading mode" | Toggle heading hold |
| "Altitude hold" | "Altitude mode" | Toggle altitude hold |
| "Nav hold" | "Nav mode" | Toggle NAV hold |
| "Approach mode" | "Approach" | Toggle approach mode |

---

### Status Queries

| Voice Command | Variations | Response |
|---------------|------------|----------|
| "What's the speed?" | "Current speed" | "Current speed is X knots" |
| "What's the altitude?" | "Current altitude" | "Altitude is X feet" |
| "What's the heading?" | "Current heading" | "Heading is X degrees" |
| "Fuel remaining" | "How much fuel?" | "Fuel remaining X percent" |

---

## Tips for Best Recognition

1. **Speak clearly** - Articulate commands, especially "up" vs "down"
2. **Use standard phraseology** - Aviation standard terms work best
3. **Wait for the beep** - Make sure recording has started
4. **Avoid background noise** - Cockpit sounds can interfere
5. **Short commands** - Keep commands concise

---

## Adding Custom Commands

Commands can be extended by editing `bridge/logic/parser.py`:

```python
# Add pattern
(r"custom pattern", "custom_intent", {}),

# Add to CommandRegistry in bridge/logic/commands.py
CommandRegistry.register(
    Command(
        id="custom_intent",
        name="Custom Command",
        type=CommandType.ACTION,
        description="My custom command",
        sim_event="SIMCONNECT_EVENT_NAME",
        response_template="Custom response",
    )
)
```
