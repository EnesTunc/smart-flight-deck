# Smart Flight Deck Companion - Voice Commands Reference

> **Toplam:** 90+ sesli komut (70 kontrol + 20 checklist)

---

## Landing Gear

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "Gear down" | "Gear extend", "Lower the gear", "Drop the gear" | GEAR_DOWN | "Gear down" |
| "Gear up" | "Gear retract", "Raise the gear", "Retract gear" | GEAR_UP | "Gear up" |

---

## Flaps

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "Flaps up" | "Flaps zero", "Flaps 0" | FLAPS_UP | "Flaps up" |
| "Flaps down" | "Extend flaps" | FLAPS_DOWN | "Flaps down" |
| "Flaps 1" | "Flaps one" | FLAPS_SET | "Flaps 1" |
| "Flaps 2" | "Flaps two", "Flaps 10" | FLAPS_SET | "Flaps 2" |
| "Flaps 3" | "Flaps three", "Flaps 15" | FLAPS_SET | "Flaps 3" |
| "Flaps 4" | "Flaps four", "Flaps full", "Flaps 20", "Flaps 25" | FLAPS_SET | "Flaps 4" |

---

## Lights

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "Landing lights on/off" | "Turn on/off landing lights", "Lights on/off" | LANDING_LIGHTS_TOGGLE | "Landing lights" |
| "Beacon on/off" | "Beacon lights on/off" | TOGGLE_BEACON_LIGHTS | "Beacon" |
| "Strobes on/off" | "Strobe lights on/off" | STROBES_TOGGLE | "Strobes" |
| "Nav lights on/off" | "Navigation lights on/off" | TOGGLE_NAV_LIGHTS | "Nav lights" |
| "Taxi lights on/off" | - | TOGGLE_TAXI_LIGHTS | "Taxi lights" |

---

## Spoilers / Speedbrake

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "Spoilers arm" | "Arm spoilers", "Spoilers armed" | SPOILERS_ARM_TOGGLE | "Spoilers armed" |
| "Spoilers on" | "Deploy spoilers", "Speedbrake on", "Extend spoilers" | SPOILERS_ON | "Speedbrake deployed" |
| "Spoilers off" | "Retract spoilers", "Speedbrake off" | SPOILERS_OFF | "Speedbrake retracted" |

---

## Autobrake

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "Autobrake off" | "Autobrake disarm" | AUTO_BRAKE_DISARM | "Autobrake off" |
| "Autobrake low" | "Autobrake lo", "Autobrake 1" | AUTO_BRAKE_LO_SET | "Autobrake low" |
| "Autobrake medium" | "Autobrake med", "Autobrake 2" | AUTO_BRAKE_MED_SET | "Autobrake medium" |
| "Autobrake high" | "Autobrake hi", "Autobrake 3" | AUTO_BRAKE_HI_SET | "Autobrake high" |
| "Autobrake max" | "Autobrake maximum", "Autobrake 4" | AUTO_BRAKE_MAX_SET | "Autobrake maximum" |
| "Autobrake RTO" | "Autobrake rejected" | AUTO_BRAKE_RTO_SET | "Autobrake RTO" |

---

## Parking Brake

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "Parking brake" | "Set parking brake", "Release parking brake" | PARKING_BRAKES | "Parking brake" |

---

## Trim

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "Trim up" | "Trim nose up" | ELEV_TRIM_UP | "Trim up" |
| "Trim down" | "Trim nose down" | ELEV_TRIM_DN | "Trim down" |
| "Trim left" | "Aileron trim left", "Roll trim left" | AILERON_TRIM_LEFT | "Aileron trim left" |
| "Trim right" | "Aileron trim right", "Roll trim right" | AILERON_TRIM_RIGHT | "Aileron trim right" |
| "Rudder trim left" | - | RUDDER_TRIM_LEFT | "Rudder trim left" |
| "Rudder trim right" | - | RUDDER_TRIM_RIGHT | "Rudder trim right" |

---

## APU

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "APU start" | "Start APU", "APU on", "Turn on APU" | APU_STARTER | "APU starting" |
| "APU off" | "APU shutdown", "Stop APU", "Turn off APU" | APU_OFF_SWITCH | "APU shutdown" |

---

## Engines

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "Engine start" | "Start engines", "Engines start", "Ignite engines" | ENGINE_AUTO_START | "Engines starting" |
| "Engines off" | "Shutdown engines", "Stop engines", "Cut engines" | ENGINE_AUTO_SHUTDOWN | "Engines shutdown" |
| "Start engine one" | "Start engine 1", "Ignite engine left" | SET_STARTER1_HELD | "Engine 1 starting" |
| "Start engine two" | "Start engine 2", "Ignite engine right" | SET_STARTER2_HELD | "Engine 2 starting" |

---

## Transponder

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "Transponder standby" | "Transponder stby" | XPNDR_SET | "Transponder standby" |
| "Transponder on" | "Transponder alt", "Transponder altitude" | XPNDR_SET | "Transponder on" |
| "Squawk ident" | "Ident", "Transponder ident" | XPNDR_IDENT_ON | "Squawk ident" |
| "Squawk [code]" | "Squawk 7000" | XPNDR_SET | "Squawk [code]" |

---

## Autopilot

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "Autopilot on" | "Engage autopilot" | AP_MASTER | "Autopilot" |
| "Autopilot off" | "Disengage autopilot" | AP_MASTER | "Autopilot" |
| "Heading hold" | "Heading mode" | AP_PANEL_HEADING_HOLD | "Heading hold" |
| "Altitude hold" | "Altitude mode" | AP_PANEL_ALTITUDE_HOLD | "Altitude hold" |
| "Nav hold" | "Nav mode" | AP_NAV1_HOLD | "Nav hold" |
| "Approach mode" | "Approach" | AP_APR_HOLD | "Approach mode" |
| "Vertical speed" | "Vertical speed mode", "VS mode" | AP_VS_HOLD | "Vertical speed" |
| "Flight level change" | - | FLIGHT_LEVEL_CHANGE | "Flight level change" |
| "Speed hold" | "Speed mode" | AP_PANEL_SPEED_HOLD | "Speed hold" |

---

## Radio / Comms

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "Swap COM1" | "Flip COM1", "Switch COM1", "Swap COM" | COM_STBY_RADIO_SWAP | "COM 1 swapped" |
| "Swap COM2" | "Flip COM2", "Switch COM2" | COM2_RADIO_SWAP | "COM 2 swapped" |
| "Swap NAV1" | "Flip NAV1", "Switch NAV1", "Swap NAV" | NAV1_RADIO_SWAP | "NAV 1 swapped" |
| "Swap NAV2" | "Flip NAV2", "Switch NAV2" | NAV2_RADIO_SWAP | "NAV 2 swapped" |

---

## Cabin / Doors

| Komut | Alternatifler | SimConnect Event | Yanit |
|-------|---------------|------------------|-------|
| "Open door" | "Close door", "Open main door" | TOGGLE_AIRCRAFT_EXIT | "Door toggled" |
| "Door one" | "Exit one", "Door left" | TOGGLE_AIRCRAFT_EXIT_FAST | "Door 1 toggled" |
| "Door two" | "Exit two", "Door right" | TOGGLE_AIRCRAFT_EXIT_FAST | "Door 2 toggled" |
| "Seatbelt sign" | "Fasten seatbelts on/off" | CABIN_SEATBELTS_ALERT_SWITCH_TOGGLE | "Seatbelt sign" |
| "No smoking sign" | "No smoking on/off" | CABIN_NO_SMOKING_ALERT_SWITCH_TOGGLE | "No smoking sign" |

---

## Status Queries

| Komut | Alternatifler | Yanit |
|-------|---------------|-------|
| "What's the speed?" | "Current speed" | "Current speed is X knots" |
| "What's the altitude?" | "Current altitude" | "Altitude is X feet" |
| "What's the heading?" | "Current heading" | "Heading is X degrees" |
| "Fuel remaining" | "How much fuel?" | "Fuel remaining X percent" |

---

## Checklist Commands ✅

### Checklist Başlatma

| Komut | Alternatifler | Yanit |
|-------|---------------|-------|
| "Before start checklist" | "Start before start checklist" | "Before Start checklist. Parking brake." |
| "Before taxi checklist" | "Run before taxi checklist" | "Before Taxi checklist. Flight controls." |
| "Before takeoff checklist" | "Takeoff checklist" | "Before Takeoff checklist. Flight controls." |
| "After takeoff checklist" | - | "After Takeoff checklist. Landing gear." |
| "Approach checklist" | - | "Approach checklist. Approach briefing." |
| "Before landing checklist" | "Landing checklist" | "Before Landing checklist. Landing gear." |
| "After landing checklist" | - | "After Landing checklist. Spoilers." |
| "Shutdown checklist" | - | "Shutdown checklist. Parking brake." |
| "Cockpit preparation checklist" | "Cockpit prep checklist" | "Cockpit Preparation checklist. Battery 1." |

### Checklist Yanıtları

| Komut | Alternatifler | Aksiyon |
|-------|---------------|---------|
| "Check" | "Checked", "Set", "Confirm", "Confirmed" | Maddeyi onayla |
| "Skip" | "Next", "Next item" | Maddeyi atla |
| "Repeat" | "Again", "Say again" | Maddeyi tekrarla |
| "Override" | - | Başarısız doğrulamayı geç |

### Checklist Kontrol

| Komut | Alternatifler | Aksiyon |
|-------|---------------|---------|
| "Pause checklist" | "Hold checklist" | Checklist'i duraklat |
| "Resume checklist" | "Continue checklist" | Checklist'e devam et |
| "Cancel checklist" | "Stop checklist", "Abort checklist" | Checklist'i iptal et |
| "Checklist status" | "What's the current item?" | Mevcut maddeyi söyle |
| "List checklists" | - | Mevcut checklistleri listele |

---

## Best Practices

### Clear Commands
- Speak clearly and at a normal pace
- Use standard aviation phraseology
- Wait for the PTT beep before speaking

### Environment
- Reduce background noise when possible
- Use a headset for better recognition
- Keep microphone at consistent distance

### Command Structure
```
[Action] [Target] [Parameter]

Examples:
- "Gear down"
- "Flaps 2"
- "Autobrake max"
- "Start engine one"
```

---

## Adding Custom Commands

Edit `bridge/logic/parser.py` to add patterns:

```python
# Add to PATTERNS list
(r"your pattern here", "your_intent", {}),
```

Edit `bridge/logic/commands.py` to register:

```python
CommandRegistry.register(
    Command(
        id="your_intent",
        name="Your Command",
        type=CommandType.ACTION,
        description="What it does",
        sim_event="SIMCONNECT_EVENT",
        response_template="TTS response",
    )
)
```

---

*Last updated: 2025-01*
