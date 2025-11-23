# Context Engine - Tasarım Dokümanı

## 1. Genel Bakış

Context Engine, sesli komutları yürütmeden önce uçuş güvenliğini kontrol eden akıllı sistemdir.
Amacı: **Tehlikeli komutları engellemek veya kullanıcıyı uyarmak.**

### Temel Prensipler

1. **Güvenlik Öncelikli** - Şüphe durumunda komutu engelle
2. **Bilgilendirici** - Neden engellendiğini açıkla
3. **Override İmkanı** - Kritik durumlarda pilot override edebilmeli
4. **Uçak Bağımsız** - Generic kurallar + uçağa özel override

---

## 2. Veri Kaynakları

### 2.1 MSFS'den Alınan Gerçek Zamanlı Veriler

| SimVar | Birim | Açıklama | Kullanım |
|--------|-------|----------|----------|
| `AIRSPEED_INDICATED` | Knots | Gösterge hızı (IAS) | V-speed kontrolleri |
| `AIRSPEED_TRUE` | Knots | Gerçek hız (TAS) | Cruise hesaplamaları |
| `GROUND_VELOCITY` | Knots | Yer hızı | Taxi/takeoff tespiti |
| `PLANE_ALTITUDE` | Feet | MSL yükseklik | Cruise/descent tespiti |
| `PLANE_ALT_ABOVE_GROUND` | Feet | AGL yükseklik | Landing tespiti |
| `VERTICAL_SPEED` | FPM | Dikey hız | Climb/descent tespiti |
| `GEAR_HANDLE_POSITION` | Bool | Gear kolu pozisyonu | Konfigürasyon |
| `FLAPS_HANDLE_INDEX` | Number | Flap pozisyonu (0-4) | Konfigürasyon |
| `SIM_ON_GROUND` | Bool | Yerde mi? | Faz tespiti |
| `ENG_COMBUSTION:1` | Bool | Motor 1 çalışıyor mu? | Faz tespiti |
| `ENG_COMBUSTION:2` | Bool | Motor 2 çalışıyor mu? | Faz tespiti |
| `BRAKE_PARKING_INDICATOR` | Bool | Park freni | Taxi kontrolü |
| `SPOILERS_ARMED` | Bool | Spoiler armed | Landing konfigürasyonu |

### 2.2 LVAR'lardan Alınan Veriler (Uçağa Özel)

| LVAR Örneği | Uçak | Açıklama |
|-------------|------|----------|
| `A32NX_FWC_FLIGHT_PHASE` | FBW A32NX | Dahili flight phase (1-10) |
| `A32NX_SPEEDS_VMAX` | FBW A32NX | Hesaplanmış Vmo |
| `A32NX_SPEEDS_VLS` | FBW A32NX | Lowest selectable speed |

### 2.3 Aircraft Profile'dan Limitler

```json
{
    "limits": {
        "vlo": 250,           // Gear operating speed
        "vle": 280,           // Gear extended speed
        "vmo": 350,           // Max operating speed
        "mmo": 0.82,          // Max Mach
        "vfe": {              // Flap extended speeds
            "1": 230,
            "2": 200,
            "3": 185,
            "full": 177
        },
        "max_altitude": 39000,
        "max_bank_autopilot": 25
    }
}
```

---

## 3. Flight Phase Detection (Uçuş Fazı Tespiti)

### 3.1 Faz Tanımları

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FLIGHT PHASES                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PREFLIGHT ──► ENGINE_START ──► TAXI ──► TAKEOFF ──► CLIMB          │
│       │                                                │             │
│       │                                                ▼             │
│       │                                            CRUISE            │
│       │                                                │             │
│       │                                                ▼             │
│       │            SHUTDOWN ◄── TAXI ◄── LANDING ◄── DESCENT        │
│       │                                     │          │             │
│       │                                     │          ▼             │
│       └─────────────────────────────────────┘      APPROACH         │
│                                                        │             │
│                                              GO_AROUND─┘             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Faz Tespit Kuralları

| Faz | Koşullar | Öncelik |
|-----|----------|---------|
| **PREFLIGHT** | On ground + Engines off + Parking brake on | 1 |
| **ENGINE_START** | On ground + Engine(s) starting (N2 rising) | 2 |
| **TAXI** | On ground + Engine(s) running + GS < 30 kts + Parking brake off | 3 |
| **TAKEOFF** | On ground + GS > 30 kts OR Airborne + AGL < 1000 + Climbing | 4 |
| **CLIMB** | Airborne + VS > 500 fpm + AGL > 1000 | 5 |
| **CRUISE** | Airborne + VS between -500 and +500 fpm + ALT > 10000 | 6 |
| **DESCENT** | Airborne + VS < -500 fpm + ALT > 10000 | 7 |
| **APPROACH** | Airborne + ALT < 10000 + VS < 0 + Gear OR Flaps extended | 8 |
| **LANDING** | On ground + GS > 30 kts + Was airborne | 9 |
| **GO_AROUND** | Was in approach + VS > 1000 fpm + Throttle > 80% | 10 |
| **SHUTDOWN** | On ground + Engines shutting down | 11 |

### 3.3 Faz Tespit Algoritması (Pseudo-code)

```python
def detect_flight_phase(state: AircraftState, prev_phase: FlightPhase) -> FlightPhase:
    """
    Öncelik sırası önemli - daha spesifik koşullar önce kontrol edilmeli.
    """

    on_ground = state.on_ground
    ias = state.indicated_airspeed
    gs = state.ground_speed
    alt_agl = state.altitude_agl
    vs = state.vertical_speed
    engines_running = state.engine1_running or state.engine2_running
    gear_down = state.gear_handle_position == 1
    flaps_extended = state.flaps_handle_index > 0
    parking_brake = state.parking_brake

    # PREFLIGHT: Yerde, motorlar kapalı
    if on_ground and not engines_running and parking_brake:
        return FlightPhase.PREFLIGHT

    # TAXI: Yerde, motorlar çalışıyor, düşük hız
    if on_ground and engines_running and gs < 30 and not parking_brake:
        return FlightPhase.TAXI

    # TAKEOFF: Yerde yüksek hız veya yeni havalanmış
    if on_ground and gs > 30:
        return FlightPhase.TAKEOFF

    if not on_ground and alt_agl < 1000 and vs > 0:
        if prev_phase in [FlightPhase.TAXI, FlightPhase.TAKEOFF]:
            return FlightPhase.TAKEOFF

    # GO_AROUND: Approach'tan ani tırmanış
    if prev_phase == FlightPhase.APPROACH and vs > 1000:
        return FlightPhase.GO_AROUND

    # LANDING: Yere yeni temas
    if on_ground and gs > 30 and prev_phase in [FlightPhase.APPROACH, FlightPhase.GO_AROUND]:
        return FlightPhase.LANDING

    # APPROACH: Alçak irtifa, alçalıyor, konfigüre
    if not on_ground and alt_agl < 3000 and vs < 0 and (gear_down or flaps_extended):
        return FlightPhase.APPROACH

    # DESCENT: Alçalıyor
    if not on_ground and vs < -500:
        return FlightPhase.DESCENT

    # CLIMB: Tırmanıyor
    if not on_ground and vs > 500:
        return FlightPhase.CLIMB

    # CRUISE: Havada, seviye uçuş
    if not on_ground and -500 <= vs <= 500:
        return FlightPhase.CRUISE

    # Varsayılan: Önceki fazı koru
    return prev_phase
```

---

## 4. Güvenlik Kuralları (Safety Rules)

### 4.1 Gear (İniş Takımı) Kuralları

| Kural ID | Koşul | Aksiyon | Mesaj |
|----------|-------|---------|-------|
| GEAR_001 | IAS > Vlo AND Command = "gear_down" | BLOCK | "Speed too high for gear. Current {ias} kts, max {vlo} kts." |
| GEAR_002 | IAS > Vle AND Gear is down | WARN | "Exceeding gear extended speed. Reduce speed or retract gear." |
| GEAR_003 | AGL < 500 AND Command = "gear_up" | WARN | "Low altitude gear retraction. Altitude {agl} feet." |
| GEAR_004 | Phase = APPROACH AND Command = "gear_up" | BLOCK | "Cannot retract gear during approach." |
| GEAR_005 | Phase = LANDING AND Command = "gear_up" | BLOCK | "Cannot retract gear during landing." |

### 4.2 Flap Kuralları

| Kural ID | Koşul | Aksiyon | Mesaj |
|----------|-------|---------|-------|
| FLAP_001 | IAS > Vfe[position] AND Command = flaps_extend | BLOCK | "Speed too high for flaps {pos}. Max {vfe} kts." |
| FLAP_002 | Phase = CRUISE AND IAS > 250 AND Command = flaps_extend | BLOCK | "Retract speed not reached. Slow down first." |
| FLAP_003 | Phase = TAKEOFF AND AGL < 1000 AND Command = flaps_retract | WARN | "Early flap retraction. Check speed and altitude." |

### 4.3 Autopilot Kuralları

| Kural ID | Koşul | Aksiyon | Mesaj |
|----------|-------|---------|-------|
| AP_001 | AGL < 500 AND Command = "ap_engage" | WARN | "Low altitude autopilot engagement." |
| AP_002 | Phase = TAKEOFF AND Command = "ap_engage" | BLOCK | "Cannot engage autopilot during takeoff roll." |
| AP_003 | Bank > 30° AND Command = "ap_engage" | WARN | "High bank angle. Level wings before engaging AP." |

### 4.4 Speed Brake / Spoiler Kuralları

| Kural ID | Koşul | Aksiyon | Mesaj |
|----------|-------|---------|-------|
| SPD_001 | Phase = TAKEOFF AND Command = "spoilers_deploy" | BLOCK | "Cannot deploy spoilers during takeoff." |
| SPD_002 | Flaps > 2 AND Command = "spoilers_deploy" | WARN | "Spoiler deployment with flaps extended." |
| SPD_003 | Phase = APPROACH AND NOT spoilers_armed | WARN | "Spoilers not armed for landing." |

### 4.5 Engine Kuralları

| Kural ID | Koşul | Aksiyon | Mesaj |
|----------|-------|---------|-------|
| ENG_001 | Airborne AND Command = "engine_shutdown" | BLOCK | "Cannot shutdown engines in flight!" |
| ENG_002 | GS > 5 AND Command = "engine_shutdown" | WARN | "Aircraft is moving. Confirm engine shutdown." |

### 4.6 Lights Kuralları

| Kural ID | Koşul | Aksiyon | Mesaj |
|----------|-------|---------|-------|
| LGT_001 | Phase = TAKEOFF AND landing_lights = OFF | REMIND | "Landing lights should be on for takeoff." |
| LGT_002 | Phase = APPROACH AND landing_lights = OFF | REMIND | "Landing lights should be on for approach." |
| LGT_003 | ALT > 10000 AND landing_lights = ON | REMIND | "Consider turning off landing lights above 10,000." |
| LGT_004 | On ground AND beacon = OFF AND engines_running | REMIND | "Beacon should be on when engines are running." |

---

## 5. Aksiyon Tipleri

### 5.1 Aksiyon Seviyeleri

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ACTION SEVERITY LEVELS                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ALLOW    - Komut güvenli, hemen yürüt                              │
│     │                                                                │
│     ▼                                                                │
│  REMIND   - Komut yürüt + hatırlatma mesajı ver                     │
│     │      "Landing lights should be on"                            │
│     ▼                                                                │
│  WARN     - Komut yürüt + uyarı ver                                 │
│     │      "Warning: Low altitude gear retraction"                  │
│     ▼                                                                │
│  CONFIRM  - Kullanıcıdan onay iste, sonra yürüt                     │
│     │      "Speed is high. Say 'confirm' to continue"               │
│     ▼                                                                │
│  BLOCK    - Komutu engelle, yürütme                                 │
│            "Unable. Speed too high for gear extension"              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Override Mekanizması

Bazı durumlarda pilot bilerek kuralı ihlal etmek isteyebilir (emergency vs.):

```
User: "Gear down"
System: "Speed too high. Current 280 knots, maximum 250."

User: "Override gear down" veya "Emergency gear down"
System: "Override accepted. Extending gear." (+ warning tone)
```

**Override Edilemez Kurallar:**
- Engine shutdown while airborne (gerçek emergency durumu hariç)
- Gear up during landing roll

---

## 6. V-Speed Referans Tablosu

### 6.1 Generic Defaults (Profil yoksa)

```json
{
    "generic_jet": {
        "vlo": 250,
        "vle": 280,
        "vmo": 350,
        "vfe": {
            "1": 230,
            "2": 215,
            "3": 200,
            "full": 180
        }
    },
    "generic_prop": {
        "vlo": 150,
        "vle": 165,
        "vmo": 200,
        "vfe": {
            "1": 150,
            "2": 130,
            "full": 110
        }
    }
}
```

### 6.2 Airbus A320 Family

```json
{
    "a320": {
        "vlo": 250,
        "vle": 280,
        "vmo": 350,
        "mmo": 0.82,
        "vfe": {
            "1": 230,
            "1+f": 215,
            "2": 200,
            "3": 185,
            "full": 177
        },
        "vref_base": 130,
        "green_dot": 220
    }
}
```

### 6.3 Boeing 737 Family

```json
{
    "b737": {
        "vlo": 270,
        "vle": 320,
        "vmo": 340,
        "mmo": 0.82,
        "vfe": {
            "1": 250,
            "5": 250,
            "10": 210,
            "15": 200,
            "25": 190,
            "30": 175,
            "40": 162
        },
        "vref_base": 130
    }
}
```

---

## 7. Hesaplama Formülleri

### 7.1 Vref Hesaplama (Basitleştirilmiş)

```python
def calculate_vref(aircraft_type: str, landing_weight_kg: float, flap_setting: int) -> float:
    """
    Vref = Vref_base + weight_correction

    Bu basitleştirilmiş bir formül. Gerçek uçaklarda
    daha karmaşık tablolar kullanılır.
    """
    base_vref = AIRCRAFT_LIMITS[aircraft_type]["vref_base"]

    # Weight correction: Her 1000 kg için ~1 knot
    reference_weight = 60000  # kg (tipik landing weight)
    weight_diff = (landing_weight_kg - reference_weight) / 1000
    weight_correction = weight_diff * 1.0  # 1 kt per 1000 kg

    # Flap correction
    flap_correction = {
        "full": 0,
        "3": 5,
        "2": 15,
        "1": 25
    }

    vref = base_vref + weight_correction + flap_correction.get(str(flap_setting), 0)

    return round(vref)
```

### 7.2 Stall Speed Estimation

```python
def estimate_stall_speed(
    weight_kg: float,
    wing_area_sqm: float,
    cl_max: float,
    altitude_ft: float,
    flap_config: int
) -> float:
    """
    Vs = sqrt((2 * W) / (rho * S * Cl_max))

    Basitleştirilmiş - gerçek değerler için FMS gerekir.
    """
    # Air density at altitude (simplified)
    rho_sl = 1.225  # kg/m³ at sea level
    rho = rho_sl * (1 - altitude_ft / 145000) ** 4

    # Weight in Newtons
    W = weight_kg * 9.81

    # Cl_max varies with flap setting
    cl_max_adjusted = cl_max * (1 + flap_config * 0.15)

    # Calculate stall speed in m/s
    vs_ms = math.sqrt((2 * W) / (rho * wing_area_sqm * cl_max_adjusted))

    # Convert to knots
    vs_kts = vs_ms * 1.944

    return round(vs_kts)
```

### 7.3 Flight Phase Scoring (Belirsizlik durumunda)

```python
def score_flight_phase(state: AircraftState) -> Dict[FlightPhase, float]:
    """
    Her faz için 0-1 arası güven skoru hesapla.
    En yüksek skora sahip fazı seç.
    """
    scores = {}

    # TAXI score
    taxi_score = 0.0
    if state.on_ground:
        taxi_score += 0.4
    if state.ground_speed < 30:
        taxi_score += 0.3
    if state.engine1_running or state.engine2_running:
        taxi_score += 0.2
    if not state.parking_brake:
        taxi_score += 0.1
    scores[FlightPhase.TAXI] = taxi_score

    # CRUISE score
    cruise_score = 0.0
    if not state.on_ground:
        cruise_score += 0.3
    if state.altitude > 10000:
        cruise_score += 0.3
    if -500 <= state.vertical_speed <= 500:
        cruise_score += 0.3
    if state.flaps_handle_index == 0:
        cruise_score += 0.1
    scores[FlightPhase.CRUISE] = cruise_score

    # ... diğer fazlar için benzer

    return scores
```

---

## 8. Response Templates

### 8.1 Blocking Responses

```yaml
gear_speed_too_high:
  en: "Unable. Speed {ias} knots exceeds gear limit of {vlo} knots. Reduce speed first."
  tr: "Yapılamıyor. Hız {ias} knot, gear limiti {vlo} knot. Önce hızı azaltın."

flap_speed_too_high:
  en: "Unable. Speed {ias} knots exceeds flap {position} limit of {vfe} knots."
  tr: "Yapılamıyor. Hız {ias} knot, flap {position} limiti {vfe} knot."

engine_shutdown_airborne:
  en: "Unable. Cannot shutdown engines while airborne."
  tr: "Yapılamıyor. Havadayken motorlar kapatılamaz."
```

### 8.2 Warning Responses

```yaml
low_altitude_gear_up:
  en: "Warning. Retracting gear at {agl} feet. Confirm?"
  tr: "Uyarı. {agl} feet'te gear kaldırılıyor. Onaylıyor musunuz?"

approach_no_spoilers:
  en: "Reminder. Spoilers not armed for landing."
  tr: "Hatırlatma. Spoiler'lar landing için armed değil."
```

### 8.3 Information Responses

```yaml
phase_change:
  en: "Now in {phase} phase."
  tr: "{phase} fazına geçildi."

speed_check:
  en: "Current speed {ias} knots. {limit_name} is {limit_value} knots."
  tr: "Mevcut hız {ias} knot. {limit_name} {limit_value} knot."
```

---

## 9. Edge Cases & Special Handling

### 9.1 Go-Around Durumu

```
Eğer:
  - Önceki faz = APPROACH
  - Throttle > %80
  - VS > +1000 fpm
  - Gear was down
O zaman:
  - Faz = GO_AROUND
  - Gear UP komutuna izin ver (normal şartlarda approach'ta block)
  - Flap retraction'a izin ver (kademeli)
```

### 9.2 Emergency Durumları

```
Override kabul edilecek durumlar:
  - "Emergency gear down" - Hız yüksek olsa bile
  - "Emergency descent" - Normal prosedürler bypass

Override kabul EDİLMEYECEK durumlar:
  - Engine shutdown in flight (simulation'da mantıksız)
  - Gear up on ground (fiziksel olarak imkansız)
```

### 9.3 SimConnect Bağlantı Kaybı

```
Eğer SimConnect verisi 5 saniye gelmezse:
  - Son bilinen state'i kullan
  - Tüm komutları WARN moduna al
  - Kullanıcıyı bilgilendir: "Simulator connection unstable"
```

---

## 10. Implementasyon Notları

### 10.1 Dosya Yapısı

```
bridge/logic/
├── context.py           # Ana Context Engine sınıfı (mevcut)
├── flight_phase.py      # Flight phase detection
├── safety_rules.py      # Güvenlik kuralları
├── v_speeds.py          # V-speed hesaplamaları
└── responses.py         # Response templates
```

### 10.2 Performans

- Flight phase detection: Her 500ms'de bir çalıştır
- V-speed cache: Aircraft değişmediği sürece cache'le
- Rule evaluation: Sadece ilgili komut geldiğinde

### 10.3 Test Senaryoları

```python
# test_context_engine.py

def test_gear_down_speed_check():
    """Hız yüksekken gear inmemeli"""
    state = AircraftState(indicated_airspeed=280, on_ground=False)
    result = engine.evaluate("gear_down", state)
    assert result.action == Action.BLOCK

def test_gear_down_approach():
    """Approach fazında gear inmeli"""
    state = AircraftState(indicated_airspeed=180, on_ground=False, altitude_agl=2000)
    result = engine.evaluate("gear_down", state)
    assert result.action == Action.ALLOW

def test_go_around_gear_up():
    """Go-around'da gear kalkabilmeli"""
    state = AircraftState(vertical_speed=2000, on_ground=False)
    engine.set_phase(FlightPhase.GO_AROUND)
    result = engine.evaluate("gear_up", state)
    assert result.action == Action.ALLOW
```

---

## 11. Gelecek İyileştirmeler

### Faz 2
- [ ] Weight-based Vref calculation (LVAR'dan ağırlık okuma)
- [ ] Wind correction for landing
- [ ] Fuel calculation and warnings

### Faz 3
- [ ] TCAS/Traffic awareness integration
- [ ] Terrain awareness (GPWS benzeri)
- [ ] Weather-based restrictions

### Faz 4
- [ ] Machine learning ile phase detection iyileştirme
- [ ] Kullanıcı davranış öğrenme (pilot style)

---

## 12. Referanslar

- FAA Airplane Flying Handbook (FAA-H-8083-3C)
- EASA Easy Access Rules for Air Operations
- Airbus A320 FCOM (Flight Crew Operating Manual)
- Boeing 737 NG FCOMv2
- ICAO Doc 8168 - Aircraft Operations

---

*Bu doküman, Context Engine geliştirme sürecinde güncellenecektir.*
