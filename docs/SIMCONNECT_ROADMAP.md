# SimConnect & Third-Party Aircraft Support Roadmap

## Current Status

### What Works Now (SimConnect Events)

| Category | Status | Notes |
|----------|--------|-------|
| Landing Gear | ✅ Works | Universal across all aircraft |
| Flaps | ✅ Works | Universal |
| Basic Lights | ✅ Works | Universal |
| Parking Brake | ✅ Works | Universal |
| Basic Autopilot | ⚠️ Partial | On/Off works, values may not |
| Trim | ✅ Works | Universal |
| Engine Start/Stop | ⚠️ Partial | AUTO_START works, realistic startup no |
| Transponder | ⚠️ Partial | Basic mode switching only |

### Aircraft Compatibility Matrix

| Aircraft | Gear | Flaps | Lights | AP Basic | AP Advanced | FCU/MCP |
|----------|------|-------|--------|----------|-------------|---------|
| **Default MSFS** | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| **Asobo A320neo** | ✅ | ✅ | ✅ | ✅ | ⚠️ | ❌ |
| **Fenix A320** | ✅ | ✅ | ⚠️ | ❌ | ❌ | ❌ LVAR |
| **PMDG 737** | ✅ | ✅ | ⚠️ | ❌ | ❌ | ❌ LVAR |
| **Leonardo MD-82** | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ❌ |
| **iniBuilds A310** | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ❌ LVAR |
| **FBW A32NX** | ✅ | ✅ | ✅ | ⚠️ | ❌ | ❌ LVAR |

**Legend:**
- ✅ Full support via SimConnect
- ⚠️ Partial - some functions work
- ❌ Requires LVAR/Custom API

---

## The LVAR Problem

### What are LVARs?
**L:VARs (Local Variables)** are custom variables defined by aircraft developers. Unlike standard SimConnect SimVars, they are not accessible through the regular SimConnect API.

```
Standard SimVar:  AUTOPILOT HEADING LOCK DIR  → Works everywhere
Fenix LVAR:       L:S_FCU_HEADING             → Only accessible via WASM
```

### Why Third-Party Aircraft Use LVARs
1. **Complex Systems** - FMC/MCDU logic needs custom variables
2. **Realistic Behavior** - Standard events don't support all states
3. **Protection** - Some developers intentionally block standard events
4. **Flexibility** - Can create any variable they need

### What Needs LVARs (Examples)

| System | Standard SimConnect | Needs LVAR |
|--------|---------------------|------------|
| FCU Heading | ❌ | ✅ L:A32NX_FCU_HDG_SET |
| FCU Altitude | ❌ | ✅ L:A32NX_FCU_ALT_SET |
| FCU Speed | ❌ | ✅ L:A32NX_FCU_SPD_SET |
| MCDU Input | ❌ | ✅ Custom API |
| Overhead Switches | ⚠️ Some | ✅ Most |
| EFB Controls | ❌ | ✅ |

---

## Solution Options

### Option 1: MobiFlight WASM Module (Recommended)

**What is it?**
Free, open-source WASM module that exposes LVARs to external applications.

**Pros:**
- ✅ Free and open-source
- ✅ Large community support
- ✅ Works with most add-ons
- ✅ Can read AND write LVARs
- ✅ Already has Python examples

**Cons:**
- ⚠️ Requires user to install WASM module
- ⚠️ Slightly more complex setup

**Integration Plan:**
```
bridge/
├── sim/
│   ├── simconnect.py      # Current - standard events
│   ├── mobiflight.py      # NEW - LVAR access via MobiFlight
│   └── aircraft_profiles/ # NEW - per-aircraft LVAR mappings
│       ├── fenix_a320.json
│       ├── pmdg_737.json
│       └── fbw_a32nx.json
```

**GitHub:** https://github.com/MobiFlight/MobiFlight-WASM-Module

---

### Option 2: FSUIPC

**What is it?**
Paid software ($35 registration) that provides extensive sim access.

**Pros:**
- ✅ Very stable and mature
- ✅ Excellent LVAR support
- ✅ Works with almost everything
- ✅ Good Python library (pyuipc)

**Cons:**
- ❌ Paid software (users need license)
- ❌ Additional dependency
- ⚠️ Not all users want to pay

**When to use:**
- Professional users who already have FSUIPC
- Fallback for problematic aircraft

---

### Option 3: Direct Aircraft APIs

Some aircraft have their own APIs:

| Aircraft | API | Notes |
|----------|-----|-------|
| **Fenix A320** | Fenix API | HTTP-based, good documentation |
| **PMDG** | PMDG SDK | Complex but powerful |
| **FBW A32NX** | SimBridge | WebSocket-based |

**Pros:**
- ✅ Full access to all features
- ✅ Designed for that aircraft

**Cons:**
- ❌ Need separate integration for each
- ❌ Maintenance burden
- ❌ Some require licensing

---

## Implementation Roadmap

### Phase 1: MobiFlight Integration (Priority: High)

```python
# bridge/sim/mobiflight.py

class MobiFlightClient:
    """Access LVARs via MobiFlight WASM module."""

    def __init__(self, simconnect):
        self.sc = simconnect
        self.client_data_area = None

    async def read_lvar(self, lvar_name: str) -> float:
        """Read an LVAR value."""
        # Use SimConnect ClientData to communicate with WASM
        pass

    async def write_lvar(self, lvar_name: str, value: float):
        """Write an LVAR value."""
        pass

    async def execute_html_event(self, event_name: str):
        """Execute an HTML event (H: events)."""
        pass
```

### Phase 2: Aircraft Profiles

Create JSON profiles for each supported aircraft:

```json
// bridge/sim/aircraft_profiles/fenix_a320.json
{
    "name": "Fenix A320",
    "detection": {
        "title_contains": "Fenix"
    },
    "commands": {
        "fcu_heading_set": {
            "type": "lvar",
            "lvar": "S_FCU_HEADING",
            "action": "set"
        },
        "fcu_heading_push": {
            "type": "lvar",
            "lvar": "S_FCU_HEADING_PUSH",
            "action": "set",
            "value": 1
        },
        "fcu_heading_pull": {
            "type": "lvar",
            "lvar": "S_FCU_HEADING_PULL",
            "action": "set",
            "value": 1
        },
        "ap1_push": {
            "type": "lvar",
            "lvar": "S_FCU_AP1",
            "action": "toggle"
        }
    }
}
```

### Phase 3: Smart Aircraft Detection

```python
# bridge/sim/aircraft_detector.py

class AircraftDetector:
    """Detect current aircraft and load appropriate profile."""

    async def detect(self) -> str:
        """Return aircraft profile name."""
        title = await self.simconnect.get_aircraft_title()

        if "Fenix" in title:
            return "fenix_a320"
        elif "PMDG" in title and "737" in title:
            return "pmdg_737"
        elif "FlyByWire" in title or "A32NX" in title:
            return "fbw_a32nx"
        else:
            return "default"
```

### Phase 4: Extended Voice Commands

Add new commands for LVAR-based controls:

```python
# New parser patterns for FCU
(r"set heading (\\d+)", "fcu_heading_set", {"value": "group1"}),
(r"heading (select|sel)", "fcu_heading_pull", {}),
(r"heading (managed|man)", "fcu_heading_push", {}),
(r"set altitude (\\d+)", "fcu_altitude_set", {"value": "group1"}),
(r"set speed (\\d+)", "fcu_speed_set", {"value": "group1"}),
```

---

## AVARs (Animation Variables)

### What are AVARs?
**A:VARs (Animation Variables)** control visual animations in the cockpit. They're different from LVARs:

| Type | Purpose | Read | Write |
|------|---------|------|-------|
| LVAR | System state | ✅ | ✅ |
| AVAR | Animations | ✅ | ⚠️ Limited |

### When Needed
- Reading switch positions
- Checking visual states
- Some aircraft use AVARs for logic

### Access Method
AVARs are typically accessed through the same WASM module as LVARs.

---

## H:Events (HTML Events)

### What are H:Events?
Custom events defined in aircraft's JavaScript code. Used to trigger specific actions.

```
Standard: TOGGLE_BEACON_LIGHTS
H:Event:  H:A320_Neo_MFD_BTN_LS_1
```

### Access Method
MobiFlight WASM module can execute H:Events.

---

## Testing Strategy

### Phase 1: Default Aircraft
```bash
# Test with Asobo A320neo
python test_commands.py --aircraft="Asobo A320"
```

### Phase 2: FlyByWire A32NX (Free)
Best test case for LVAR integration - free, well-documented.

### Phase 3: Fenix A320 (Paid)
Complex but popular. Good real-world test.

### Phase 4: PMDG 737 (Paid)
Different ecosystem, different challenges.

---

## User Experience

### Installation Steps (Future)
1. Download MobiFlight WASM Module
2. Copy to Community folder
3. Start Smart Flight Deck
4. Automatic aircraft detection

### Fallback Behavior
```
if aircraft_profile_exists:
    use_lvar_commands()
else:
    use_standard_simconnect()
    warn_user("Some features may not work with this aircraft")
```

---

## Resources

### MobiFlight
- GitHub: https://github.com/MobiFlight/MobiFlight-WASM-Module
- Docs: https://www.mobiflight.com/en/documentation.html
- Python Example: https://github.com/odwdinern/Python-SimConnect/issues/

### FlyByWire
- LVAR List: https://docs.flybywiresim.com/
- SimBridge: https://docs.flybywiresim.com/tools/simbridge/

### Fenix
- API Docs: Available with purchase
- Community: Fenix Discord

### PMDG
- SDK: Included with aircraft
- Forum: PMDG Support Forum

---

## Timeline Estimate

| Phase | Description | Status |
|-------|-------------|--------|
| Current | Standard SimConnect | ✅ Done |
| Next | MobiFlight Integration | Planned |
| Future | Aircraft Profiles | Planned |
| Future | FCU/MCP Voice Control | Planned |
| Future | MCDU Integration | Research |

---

*This document will be updated as development progresses.*
