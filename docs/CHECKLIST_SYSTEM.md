# Checklist System Design Document

> **Durum:** ✅ TAMAMLANDI (v1.0)
> **Son Guncelleme:** 2025-01-23

## Overview

Smart Flight Deck Companion icin hibrit checklist sistemi. Sistem, gercekci 2 pilotlu prosedur deneyimi sunarken SimConnect/WASM uzerinden otomatik dogrulama yapabilir.

---

## Temel Prensipler

### 1. Hibrit Yaklasim
- **Tetikleme:** Ses komutu VEYA mobil buton
- **Asistan Rolu:** First Officer (challenge okur)
- **Kullanici Rolu:** Captain (response verir veya "check" der)
- **Dogrulama:** SimConnect/WASM ile otomatik kontrol

### 2. Challenge-Response Akisi
```
+-----------------------------------------------------------------+
|  Kullanici: "Before takeoff checklist"                          |
|      |                                                          |
|  Asistan: "Before takeoff checklist. Flight controls?"          |
|      |                                                          |
|  Kullanici: "Checked" / "Check" / sessiz                        |
|      |                                                          |
|  Sistem: [SimConnect dogrulamasi]                               |
|      +-- Dogru -> Asistan: "Checked. Flaps?"                    |
|      +-- Yanlis -> Asistan: "Flight controls not verified.      |
|                           Please check and say 'check' again"   |
|      |                                                          |
|  ... devam ...                                                  |
|      |                                                          |
|  Asistan: "Before takeoff checklist complete"                   |
+-----------------------------------------------------------------+
```

---

## Implementasyon Durumu

### Tamamlanan Ozellikler ✅

| Ozellik | Durum | Dosya |
|---------|-------|-------|
| Checklist Engine | ✅ | `logic/checklist.py` |
| State Machine | ✅ | `logic/checklist.py` |
| JSON Loader | ✅ | `logic/checklist_loader.py` |
| SimConnect/WASM Verifier | ✅ | `logic/checklist_verifier.py` |
| Default Checklistler | ✅ | `checklists/default.json` |
| A320 FBW Checklistler | ✅ | `checklists/a320_fbw.json` |
| API Endpoints (8) | ✅ | `api/routes.py` |
| Sesli Komutlar (28) | ✅ | `logic/parser.py` |
| English TTS Responses | ✅ | `logic/checklist.py` |

---

## Mevcut Checklistler

### Default (Tum Ucaklar) - 8 Checklist, 31 Madde

| Checklist | Faz | Madde Sayisi |
|-----------|-----|--------------|
| Before Start | PREFLIGHT | 4 |
| Before Taxi | TAXI | 4 |
| Before Takeoff | TAXI | 6 |
| After Takeoff | CLIMB | 3 |
| Approach | APPROACH | 3 |
| Before Landing | APPROACH | 3 |
| After Landing | LANDING | 4 |
| Shutdown | SHUTDOWN | 4 |

### FlyByWire A32NX - 9 Checklist, 42 Madde

| Checklist | Faz | Madde Sayisi | LVAR Destegi |
|-----------|-----|--------------|--------------|
| Cockpit Preparation | PREFLIGHT | 5 | ✅ |
| Before Start | PREFLIGHT | 5 | ✅ |
| After Start | ENGINE_START | 5 | ✅ |
| Before Takeoff | TAXI | 7 | ✅ |
| After Takeoff | CLIMB | 3 | ✅ |
| Approach | APPROACH | 5 | ✅ |
| Landing | APPROACH | 3 | ✅ |
| After Landing | LANDING | 4 | ✅ |
| Shutdown | SHUTDOWN | 5 | ✅ |

---

## JSON Semasi

### Checklist Dosya Yapisi

```json
{
  "aircraft": "FlyByWire A32NX",
  "version": "1.0",
  "author": "Smart Flight Deck",
  "checklists": {
    "before_takeoff": {
      "name": "Before Takeoff",
      "phase": "TAXI",
      "items": [
        {
          "id": "flight_controls",
          "challenge": "Flight controls",
          "expected_response": "Checked",
          "verification": {
            "type": "manual"
          },
          "action": { "type": "none" },
          "critical": true
        },
        {
          "id": "flaps_config",
          "challenge": "Flap lever",
          "expected_response": "Config 1 or 2",
          "verification": {
            "type": "simvar",
            "variable": "FLAPS HANDLE INDEX",
            "condition": "in_range",
            "min": 1,
            "max": 2
          },
          "action": { "type": "none" },
          "critical": true,
          "warning_if_fail": "Flaps not in takeoff configuration!"
        },
        {
          "id": "transponder_mode",
          "challenge": "Transponder",
          "expected_response": "TA/RA",
          "verification": {
            "type": "lvar",
            "variable": "A32NX_TRANSPONDER_MODE",
            "condition": "equals",
            "value": 2
          },
          "action": { "type": "none" },
          "critical": false
        }
      ]
    }
  }
}
```

### Verification Types

| Type | Aciklama | Parametreler |
|------|----------|--------------|
| `simvar` | SimConnect variable kontrolu | variable, condition, value |
| `lvar` | LVAR kontrolu (WASM) | variable, condition, value |
| `manual` | Otomatik dogrulama yok | - |
| `combined` | Birden fazla kosul | conditions[] |

### Condition Types

| Condition | Aciklama | Ornek |
|-----------|----------|-------|
| `equals` | Tam esitlik | value: 1 |
| `not_equals` | Esit degil | value: 0 |
| `greater_than` | Buyuktur | value: 100 |
| `less_than` | Kucuktur | value: 50 |
| `in_range` | Aralikta | min: 1, max: 3 |
| `contains` | Icerir (string) | value: "A320" |

### Action Types

| Type | Aciklama | Kullanim |
|------|----------|----------|
| `none` | Aksiyon yok | Sadece dogrulama |
| `simconnect` | SimConnect event | event: "GEAR_DOWN" |
| `lvar` | LVAR yazma | variable, value |
| `key` | Klavye simulasyonu | key: "G" |

---

## State Machine

### Checklist States

```
+----------+    start()    +----------+   respond()   +----------+
|   IDLE   |-------------->| RUNNING  |-------------->| WAITING  |
+----------+               +----------+               +----------+
     ^                          |                          |
     |                          | complete()               | respond()
     |                          v                          |
     |                    +----------+                     |
     +--------------------| COMPLETE |<--------------------+
        cancel()          +----------+      (last item)
```

### State Descriptions

| State | Aciklama | Enum |
|-------|----------|------|
| `IDLE` | Checklist baslatilmamis | `ChecklistState.IDLE` |
| `RUNNING` | Checklist aktif, madde okunuyor | `ChecklistState.RUNNING` |
| `WAITING` | Kullanici yaniti bekleniyor | `ChecklistState.WAITING` |
| `PAUSED` | Gecici durdurulmus | `ChecklistState.PAUSED` |
| `COMPLETE` | Checklist tamamlandi | `ChecklistState.COMPLETE` |
| `FAILED` | Kritik madde basarisiz | `ChecklistState.FAILED` |

### Checklist Item States

| State | Aciklama | Enum |
|-------|----------|------|
| `PENDING` | Henuz okunmadi | `ItemState.PENDING` |
| `ACTIVE` | Su an aktif madde | `ItemState.ACTIVE` |
| `VERIFIED` | Dogrulandi | `ItemState.VERIFIED` |
| `FAILED` | Dogrulama basarisiz | `ItemState.FAILED` |
| `SKIPPED` | Atlandi | `ItemState.SKIPPED` |
| `OVERRIDE` | Uyariya ragmen gecildi | `ItemState.OVERRIDE` |

---

## Sesli Komutlar (Parser Patterns)

### Checklist Baslatma (10 pattern)
```
"before start checklist"
"before takeoff checklist"
"after takeoff checklist"
"approach checklist"
"before landing checklist"
"after landing checklist"
"shutdown checklist"
"cockpit preparation checklist"
"checklist [name]"
```

### Checklist Yanit (8 pattern)
```
"check" / "checked"     -> checklist_check
"set"                   -> checklist_check
"confirm" / "confirmed" -> checklist_check
"skip" / "next"         -> checklist_skip
"repeat" / "again"      -> checklist_repeat
"override"              -> checklist_override
```

### Checklist Kontrol (6 pattern)
```
"pause checklist"       -> checklist_pause
"resume checklist"      -> checklist_resume
"cancel checklist"      -> checklist_cancel
"what's the current item" -> checklist_status
"checklist status"      -> checklist_status
"list checklists"       -> checklist_list
```

---

## API Endpoints

### Endpoint Listesi

| Endpoint | Method | Auth | Aciklama |
|----------|--------|------|----------|
| `/api/checklist/list` | GET | ✅ | Mevcut ucak icin checklistleri listele |
| `/api/checklist/start/{id}` | POST | ✅ | Checklist baslat |
| `/api/checklist/status` | GET | ✅ | Aktif checklist durumu |
| `/api/checklist/response` | POST | ✅ | Yanit ver (check, skip, override, repeat) |
| `/api/checklist/pause` | POST | ✅ | Duraklat |
| `/api/checklist/resume` | POST | ✅ | Devam et |
| `/api/checklist/cancel` | POST | ✅ | Iptal et |
| `/api/checklist/set-aircraft` | POST | ✅ | Ucak ayarla |

### Request/Response Ornekleri

**Start Checklist:**
```json
POST /api/checklist/start/before_takeoff
Response: {
  "success": true,
  "state": "WAITING",
  "message": "Current item: Flight controls",
  "tts_text": "Before Takeoff checklist. Flight controls.",
  "current_item": {
    "id": "flight_controls",
    "challenge": "Flight controls",
    "expected": "Checked",
    "critical": true
  },
  "progress": 0.0,
  "items_remaining": 6
}
```

**Send Response (Check):**
```json
POST /api/checklist/response
Body: { "response": "check" }
Response: {
  "success": true,
  "state": "WAITING",
  "message": "Next: Flaps",
  "tts_text": "Checked. Flaps.",
  "current_item": {
    "id": "flaps_config",
    "challenge": "Flaps",
    "expected": "Set for takeoff",
    "critical": true
  },
  "verified": true,
  "progress": 16.67,
  "items_remaining": 5
}
```

**Verification Failed (Critical Item):**
```json
POST /api/checklist/response
Body: { "response": "check" }
Response: {
  "success": true,
  "state": "WAITING",
  "message": "Verification failed: Flaps not in takeoff configuration!",
  "tts_text": "Flaps not verified. Flaps not in takeoff configuration!. Say override to continue or check to retry.",
  "current_item": {
    "id": "flaps_config",
    "challenge": "Flaps",
    "expected": "Set for takeoff",
    "critical": true
  },
  "verified": false,
  "verification_message": "Flaps not in takeoff configuration!",
  "progress": 16.67,
  "items_remaining": 5
}
```

**Checklist Complete:**
```json
{
  "success": true,
  "state": "COMPLETE",
  "message": "Before Takeoff complete",
  "tts_text": "Checked. Before Takeoff checklist complete.",
  "progress": 100.0,
  "items_remaining": 0
}
```

---

## Dosya Yapisi

```
bridge/
+-- logic/
|   +-- checklist.py           # Ana checklist engine (500+ satir)
|   |                          # - ChecklistState, ItemState enums
|   |                          # - ChecklistItem, Checklist dataclasses
|   |                          # - ChecklistEngine (state machine)
|   |                          # - parse_user_response()
|   |
|   +-- checklist_loader.py    # JSON yukleme (200+ satir)
|   |                          # - ChecklistLoader
|   |                          # - ChecklistManager
|   |                          # - Aircraft matching
|   |
|   +-- checklist_verifier.py  # SimConnect/WASM dogrulama (250+ satir)
|                              # - ChecklistVerifier
|                              # - SIMVAR_MAPPINGS
|                              # - create_verifier_from_sim_manager()
|
+-- checklists/                # Checklist JSON dosyalari
|   +-- default.json           # 8 checklist, 31 madde
|   +-- a320_fbw.json          # 9 checklist, 42 madde (LVAR)
|
+-- api/
    +-- routes.py              # 8 checklist endpoint eklendi
```

---

## Kullanim Ornekleri

### Python API

```python
from logic import ChecklistManager, UserResponse

# Manager olustur
manager = ChecklistManager()
manager.set_aircraft("FlyByWire A32NX")

# Mevcut checklistleri listele
checklists = manager.list_available()
# [{"id": "before_takeoff", "name": "Before Takeoff", ...}, ...]

# Checklist baslat
result = manager.start_checklist("before_takeoff")
print(result.tts_text)
# "Before Takeoff checklist. Flight controls."

# Kullanici "check" dedi
result = manager.engine.respond(UserResponse.CHECK)
print(result.tts_text)
# "Checked. Flaps."

# Kullanici "skip" dedi
result = manager.engine.respond(UserResponse.SKIP)
print(result.tts_text)
# "Flaps skipped. Spoilers."

# Checklist duraklat
result = manager.engine.pause()
print(result.tts_text)
# "Before Takeoff checklist paused."

# Devam et
result = manager.engine.resume()
print(result.tts_text)
# "Spoilers."

# Iptal et
result = manager.engine.cancel()
print(result.tts_text)
# "Before Takeoff checklist cancelled."
```

### Voice Command Flow

```
Kullanici: "Before takeoff checklist"
Asistan:   "Before takeoff checklist. Flight controls."

Kullanici: "Check"
Asistan:   "Checked. Flaps."

Kullanici: "Check"
Asistan:   "Flaps not verified. Flaps not in takeoff configuration.
            Say override to continue or check to retry."

Kullanici: "Override"
Asistan:   "Flaps override accepted. Spoilers."

Kullanici: "Check"
Asistan:   "Armed. Auto brake."

... (devam) ...

Asistan:   "Checked. Before takeoff checklist complete."
```

---

## Gelecek Gelistirmeler

- [ ] Checklist editor (mobil/web UI)
- [ ] Checklist paylasimi (community)
- [ ] Ses kayitli checklistler (gercek ses)
- [ ] Checklist istatistikleri (basari orani, sure)
- [ ] Emergency checklist quick access
- [ ] Flow prosedurleri (checklist degil, akis)
- [ ] Context Engine entegrasyonu (faz uyumu)
- [ ] Otomatik checklist onerisi (faz degisiminde)
- [ ] Timeout ve otomatik ilerleme
- [ ] Daha fazla ucak profili (Fenix, PMDG, Cessna)

---

## Notlar

### Performans
- JSON dosyalari baslangicta yuklenir ve cache'lenir
- Regex pattern'lar compile edilmis halde tutulur
- Verification sadece kullanici yanit verdiginde yapilir

### Guvenlik
- Kritik maddeler (critical: true) basarisiz olursa override gerektirir
- Manual verification her zaman basarili sayilir (kullanici sorumlulugu)
- LVAR dogrulamasi icin WASM baglantisi gerekir

### Genisletilebilirlik
- Yeni ucak profili eklemek icin sadece JSON dosyasi olusturmak yeterli
- `_match_aircraft()` fonksiyonuna pattern eklenebilir
- Verification turleri genisletilebilir
