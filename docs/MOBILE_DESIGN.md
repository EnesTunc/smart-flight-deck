# Smart Flight Deck Companion - Mobile App Design

> **Durum:** TASARIM TAMAMLANDI
> **Platform:** Flutter (Android + iOS - Paralel)
> **Konsept:** Profesyonel EFB + Sesli Asistan
> **Hedef Cihaz:** Telefon + Tablet (Responsive)
> **MVP Kapsami:** Faz 1-2-3 (Baglanti + Data + Checklist)

---

## 0. Alinan Kararlar

| Konu | Karar | Notlar |
|------|-------|--------|
| **Havacilik Verisi** | OurAirports + Manuel | Basari sonrasi OpenAIP |
| **VATSIM Trafik** | MVP Sonrasi | Opsiyonel ozellik |
| **SimBrief** | MVP Sonrasi (Faz 4-5) | Ticari icin onay gerekebilir |
| **Hedef Cihaz** | Telefon + Tablet | Responsive tasarim |
| **Platform** | Android + iOS Paralel | Flutter tek codebase |
| **MVP Kapsami** | Faz 1-2-3 | Satilabilir minimum urun |
| **MSFS Verisi** | Kullanilmayacak | Lisans riski |

---

## 1. Vizyon

Sadece bir "uzaktan kumanda" degil, **tam donanimli bir Electronic Flight Bag (EFB)** uygulamasi.

### Rakip Analizi

| Uygulama | Ozellikler | Fiyat | Eksikler |
|----------|------------|-------|----------|
| **FS2Crew** | Sesli komut, checklist | $40+ | Mobil yok |
| **BeyondATC** | ATC simulasyonu | $35+ | EFB yok |
| **Navigraph Charts** | Haritalar, chartlar | $10/ay | Sesli komut yok |
| **SimToolkitPro** | EFB, fuel, weight | $15 | Sesli asistan yok |
| **Volanta** | Tracking, harita | Freemium | Kontrol yok |

### Bizim Farkimiz
- Sesli asistan + EFB + Harita **tek uygulamada**
- **Offline** calisabilir (harita cache)
- **Tek seferlik odeme**, abonelik yok
- Profesyonel pilot arayuzu

---

## 2. Uygulama Modulleri

### 2.1 Ana Moduller

```
+------------------------------------------------------------------+
|                    SMART FLIGHT DECK COMPANION                     |
+------------------------------------------------------------------+
|                                                                    |
|  +------------------+  +------------------+  +------------------+  |
|  |                  |  |                  |  |                  |  |
|  |   VOICE ASSIST   |  |    LIVE MAP      |  |    FLIGHT DATA   |  |
|  |                  |  |                  |  |                  |  |
|  |  - PTT Button    |  |  - Moving Map    |  |  - PFD Tape      |  |
|  |  - Voice Status  |  |  - Flight Plan   |  |  - Engine Data   |  |
|  |  - Command Log   |  |  - Traffic       |  |  - Fuel/Weight   |  |
|  |                  |  |  - Airports      |  |  - Nav Info      |  |
|  +------------------+  +------------------+  +------------------+  |
|                                                                    |
|  +------------------+  +------------------+  +------------------+  |
|  |                  |  |                  |  |                  |  |
|  |   CHECKLISTS     |  |    AIRPORT       |  |    SETTINGS      |  |
|  |                  |  |    INFO          |  |                  |  |
|  |  - Interactive   |  |  - Charts        |  |  - Connection    |  |
|  |  - Voice Control |  |  - Weather       |  |  - Voice Config  |  |
|  |  - Auto-verify   |  |  - Frequencies   |  |  - Display       |  |
|  |                  |  |  - Runways       |  |  - Units         |  |
|  +------------------+  +------------------+  +------------------+  |
|                                                                    |
+------------------------------------------------------------------+
```

---

## 3. Ekran Tasarimlari

### 3.1 Ana Ekran (Dashboard)

```
+------------------------------------------------------------------+
|  [=]  SMART FLIGHT DECK              [Wifi: Connected]  [12:45]  |
+------------------------------------------------------------------+
|                                                                    |
|  +------------------------+  +----------------------------------+  |
|  |                        |  |                                  |  |
|  |      MINI MAP          |  |         FLIGHT INFO              |  |
|  |                        |  |                                  |  |
|  |    [Aircraft Icon]     |  |   Aircraft: A320neo              |  |
|  |         *              |  |   Phase:    CRUISE               |  |
|  |        /|\             |  |   Flight:   THY123               |  |
|  |    ----+----           |  |   Route:    LTFM -> LTBA         |  |
|  |                        |  |                                  |  |
|  +------------------------+  +----------------------------------+  |
|                                                                    |
|  +------------------------+  +----------------------------------+  |
|  |   SPEED     ALTITUDE   |  |   HEADING       VS               |  |
|  |                        |  |                                  |  |
|  |   280       FL350      |  |   270deg       +0                |  |
|  |   KTS       35,000ft   |  |   HDG          FPM               |  |
|  +------------------------+  +----------------------------------+  |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |                                                              |  |
|  |  [  CHECKLIST  ]  [  AIRPORT  ]  [  FUEL  ]  [  SETTINGS  ] |  |
|  |                                                              |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|                    +------------------------+                      |
|                    |                        |                      |
|                    |     [  PTT BUTTON  ]   |                      |
|                    |     Hold to Speak      |                      |
|                    |                        |                      |
|                    +------------------------+                      |
|                                                                    |
+------------------------------------------------------------------+
```

### 3.2 Harita Ekrani (Moving Map)

```
+------------------------------------------------------------------+
|  [<]  MOVING MAP                     [Layers]  [Center]  [Zoom]  |
+------------------------------------------------------------------+
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |                                                              |  |
|  |                        LTFM *                                |  |
|  |                            \                                 |  |
|  |                             \  [FIR Boundary]                |  |
|  |                              \                               |  |
|  |                               * ELIKA                        |  |
|  |                                \                             |  |
|  |                                 \                            |  |
|  |                            [*]   * DIVIT                     |  |
|  |                         Aircraft                             |  |
|  |                          FL350                               |  |
|  |                          280kt    \                          |  |
|  |                                    \                         |  |
|  |                                     * LTBA                   |  |
|  |                                                              |  |
|  |  [N]                                                         |  |
|  |   |                                                          |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |  Range: 100nm  |  Track: 180  |  ETE: 0:45  |  Dist: 120nm  |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |  [ VOR ]  [ NDB ]  [ APT ]  [ WPT ]  [ TRAFFIC ]  [ WEATHER ]|  |
|  +--------------------------------------------------------------+  |
|                                                                    |
+------------------------------------------------------------------+
```

### 3.3 Flight Data Ekrani (PFD/Engine)

```
+------------------------------------------------------------------+
|  [<]  FLIGHT DATA                              [PFD]  [ENGINE]   |
+------------------------------------------------------------------+
|                                                                    |
|  +------------------------+  +----------------------------------+  |
|  |                        |  |                                  |  |
|  |     SPEED TAPE         |  |        ALTITUDE TAPE             |  |
|  |                        |  |                                  |  |
|  |        300 -           |  |           - 36000                |  |
|  |        290 -           |  |           - 35500                |  |
|  |   Vmo>  280 ====       |  |      ==== 35000  <-- FL350       |  |
|  |        270 -           |  |           - 34500                |  |
|  |        260 -           |  |           - 34000                |  |
|  |                        |  |                                  |  |
|  |     GS: 450kt          |  |     VS: +0 fpm                   |  |
|  |     TAS: 480kt         |  |     QNH: 1013                    |  |
|  |     Mach: 0.78         |  |                                  |  |
|  +------------------------+  +----------------------------------+  |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |                      NAVIGATION                              |  |
|  |                                                              |  |
|  |   HDG: 270    TRK: 268    WIND: 290/25    OAT: -45C         |  |
|  |                                                              |  |
|  |   NAV1: 110.50 ILS 06    DME: 45.2nm                        |  |
|  |   NAV2: 114.30 VOR IST   DME: 120.5nm                       |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |                       FUEL & WEIGHT                          |  |
|  |                                                              |  |
|  |   FUEL: 12,450 kg  (45%)     ZFW:  58,000 kg                |  |
|  |   FLOW: 2,400 kg/h           GW:   70,450 kg                |  |
|  |   ENDUR: 5:11                CG:   28.5%                     |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
+------------------------------------------------------------------+
```

### 3.4 Checklist Ekrani ✅ YENİ (PDF/Brochure Style)

```
+------------------------------------------------------------------+
|  [SMART FLIGHT] | BEFORE TAKEOFF CHECKLIST | [A320neo AIRBUS]   |
|     DECK        |                           | Phase: TAXI        |
+==================================================================+
|                                                                  |
|  PROGRESS: [████████░░░░] 60%  3 remaining                      |
|                                                                  |
|  +============================================================+  |
|  | ▣ BEFORE TAKEOFF CHECKLIST                          60% ◀  |  |
|  +============================================================+  |
|  |                                                            |  |
|  |  ✓ Flight controls ................. CHECKED       [✓]    |  |
|  |  ✓ Flaps .......................... CONFIG 1+F      [✓]    |  |
|  |  ⚠ Spoilers ....................... ARMED    [✓] [⚠]      |  |
|  |     ^^^^^ Current item (highlighted background)            |  |
|  |  [ ] Auto brake ................... MAX                    |  |
|  |  [ ] Takeoff config ............... CHECKED                |  |
|  |  [ ] Transponder .................. TA/RA                  |  |
|  |                                                            |  |
|  +============================================================+  |
|                                                                  |
|  +============================================================+  |
|  | 🎤 CURRENT ITEM                                            |  |
|  |------------------------------------------------------------|  |
|  | "Spoilers"                                                 |  |
|  | Expected: ARMED                                            |  |
|  |                                                            |  |
|  | [⚠ NOT VERIFIED] ← SimConnect/WASM doğrulama durumu       |  |
|  | "Spoilers not armed. Say override to continue"            |  |
|  +============================================================+  |
|                                                                  |
|  +--------------------------------------------------------------+|
|  |  [  ✓ CHECK  ]      [  SKIP  ]      [ ✕ ]                   ||
|  |   (yeşil)          (amber)        (kırmızı)                 ||
|  +--------------------------------------------------------------+|
+------------------------------------------------------------------+

Renk Paleti:
- Beyaz zemin (#FFFFFF)
- Header gri (#E0E0E0 + #F5F5F5)
- Başlık çubuğu (#2A4B6D - kDarkBlue)
- Onay yeşil (#00A651 - kGreen)
- Uyarı amber (#FF8C00 - kAmber)
- Border gri (#B0B0B0 - kBorderGrey)
- Metin siyah (#000000 - kTextBlack)
```

### 3.5 Airport Info Ekrani

```
+------------------------------------------------------------------+
|  [<]  LTBA - Istanbul Ataturk                          [Star]    |
+------------------------------------------------------------------+
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |  GENERAL                                                     |  |
|  |                                                              |  |
|  |  ICAO: LTBA          IATA: IST                              |  |
|  |  Elevation: 163 ft   Transition: 18000 ft                   |  |
|  |  Coordinates: 40.976N / 28.814E                             |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |  RUNWAYS                                                     |  |
|  |                                                              |  |
|  |  [06/24]  3000m x 45m  ILS CAT IIIB  [Active]               |  |
|  |  [18/36]  2850m x 45m  ILS CAT I                            |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |  FREQUENCIES                                                 |  |
|  |                                                              |  |
|  |  ATIS:    128.025      Ground:   121.900                    |  |
|  |  Tower:   118.100      Approach: 120.700                    |  |
|  |  Departure: 119.750    Center:   124.025                    |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |  WEATHER (METAR)                                 [Refresh]   |  |
|  |                                                              |  |
|  |  LTBA 231150Z 06008KT 9999 FEW040 SCT100 18/08 Q1015        |  |
|  |                                                              |  |
|  |  Wind: 060/08kt  Vis: 10km+  Temp: 18C  QNH: 1015           |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
+------------------------------------------------------------------+
```

### 3.6 Settings Ekrani ✅ IMPLEMENTED (2025-11-25)

```
+------------------------------------------------------------------+
|  [<]  SETTINGS                                          [Save]   |
+------------------------------------------------------------------+
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |  CONNECTION                                                  |  |
|  +--------------------------------------------------------------+  |
|  |  Status: Connected to 192.168.1.100:8000                     |  |
|  |                                                              |  |
|  |  [Change Connection]          [Disconnect]                   |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |  AUDIO & HAPTICS                                             |  |
|  +--------------------------------------------------------------+  |
|  |  Microphone Sensitivity:    50%                              |  |
|  |  [Low] ────●────────── [High]                                |  |
|  |                                                              |  |
|  |  TTS Voice:  [Linda (US Female) ▼]   [Preview]              |  |
|  |    License: Public Domain      Size: 109 MB                  |  |
|  |    [Download] (other voices)                                 |  |
|  |                                                              |  |
|  |  TTS Volume:    80%                                          |  |
|  |  [Low] ──────────●──── [High]                                |  |
|  |                                                              |  |
|  |  Haptic Feedback:  [✓ ON]                                    |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |  CHECKLIST                                                   |  |
|  +--------------------------------------------------------------+  |
|  |  Auto Verification:     [✓ ON]                               |  |
|  |    Verify items using MSFS SimConnect/WASM data              |  |
|  |                                                              |  |
|  |  Voice Announcements:   [✓ ON]                               |  |
|  |    Read checklist items aloud via TTS                        |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |  APPEARANCE                                                  |  |
|  +--------------------------------------------------------------+  |
|  |  Theme Mode:   [Dark ▼]                                      |  |
|  |    Options: Dark, Light                                      |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|  +--------------------------------------------------------------+  |
|  |  ABOUT                                                       |  |
|  +--------------------------------------------------------------+  |
|  |  App Version:    1.0.0 (build 20250125)                      |  |
|  |  Bridge Version: 1.0.0                                       |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
+------------------------------------------------------------------+
```

**Available TTS Voices (All Public Domain):**
- **Linda (US Female)** - ljspeech - 109 MB - High quality - ✅ Pre-installed
- **Cori (UK Female)** - cori-high - 109 MB - High quality - ⬇️ Download on-demand
- **John (US Male)** - john - 61 MB - Medium quality - ⬇️ Download on-demand
- **Bryce (US Male)** - bryce - 61 MB - Medium quality - ⬇️ Download on-demand

**Settings Features:**
- ✅ Immediate save (no save button needed)
- ✅ Haptic feedback on all interactions
- ✅ Voice preview with sample text
- ✅ On-demand voice download with progress indicator
- ✅ Sync with Bridge API (SharedPreferences + API)
- ✅ Offline support (local changes saved, synced when reconnected)
- ✅ Aviation-themed dark UI (#00E676 green accent)

---

## 4. Harita Sistemi

### 4.1 Teknoloji Secimi

| Secenek | Lisans | Maliyet | Offline | Oneri |
|---------|--------|---------|---------|-------|
| **OpenStreetMap + flutter_map** | ODbL | Ucretsiz* | Evet | **ONERILEN** |
| Mapbox | Proprietary | Freemium | Evet | Alternatif |
| Google Maps | Proprietary | Ucretli | Sinirli | Hayir |

*Tile server icin: Kendi host veya ucretsiz tier (Thunderforest, Stadia)

### 4.2 Harita Katmanlari

```
+------------------------------------------------------------------+
|                        HARITA KATMANLARI                          |
+------------------------------------------------------------------+
|                                                                    |
|  BASE LAYERS (Sadece biri aktif)                                  |
|  +--------------------------------------------------------------+  |
|  |  [ ] Street Map (OSM Standard)                               |  |
|  |  [x] Aviation (OpenAIP style)                                |  |
|  |  [ ] Satellite (Bing/Esri)                                   |  |
|  |  [ ] Dark Mode                                               |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
|  OVERLAY LAYERS (Birden fazla aktif olabilir)                     |
|  +--------------------------------------------------------------+  |
|  |  [x] Airports (ICAO)                                         |  |
|  |  [x] Navaids (VOR, NDB, FIX)                                 |  |
|  |  [x] Airways (High/Low)                                      |  |
|  |  [ ] Airspace (FIR, TMA, CTR)                                |  |
|  |  [x] Flight Plan Route                                       |  |
|  |  [x] Own Aircraft                                            |  |
|  |  [ ] AI Traffic                                              |  |
|  |  [ ] VATSIM Traffic (Online required)                        |  |
|  |  [ ] Weather Radar (Online required)                         |  |
|  +--------------------------------------------------------------+  |
|                                                                    |
+------------------------------------------------------------------+
```

### 4.3 Veri Kaynaklari (KARAR VERILDI)

| Veri | Kaynak | Lisans | Ticari | Guncelleme |
|------|--------|--------|--------|------------|
| Base Map | OpenStreetMap | ODbL | OK (attribution) | Cache |
| **Airports** | **OurAirports** | **Public Domain** | **OK** | Aylik |
| **Runways** | **OurAirports** | **Public Domain** | **OK** | Aylik |
| **Frequencies** | **OurAirports** | **Public Domain** | **OK** | Aylik |
| Navaids | Manuel derleme | Public | OK | Manuel |
| Weather | NOAA/AWC | Public | OK | Canli |
| VATSIM | VATSIM API | Free | OK | MVP sonrasi |

### 4.4 OurAirports Detaylari

**Neden OurAirports?**
- %100 Public Domain (ticari kullanima tamamen acik)
- 74,000+ havaalani
- Detayli runway bilgisi
- Frekanslar dahil
- CSV/JSON formati

**Icerik:**
```
airports.csv      → ICAO, isim, koordinat, yukseklik, tip
runways.csv       → Runway bilgileri, boyut, kaplama
frequencies.csv   → Tower, Ground, ATIS, Approach
countries.csv     → Ulke bilgileri
regions.csv       → Bolge bilgileri
```

**Indirme:** https://ourairports.com/data/

### 4.5 MSFS Verisi Neden Kullanilmiyor?

```
MSFS SimConnect ile havaalani verisi cekilebilir AMA:

Sorunlar:
+-- Sadece yakin havaalanlari listelenebilir (tum DB yok)
+-- MSFS verileri Microsoft'a ait
+-- Ticari urun icin lisans belirsiz
+-- SDK License eklenti yapmaya izin verir, veri cekmeye degil
+-- Hukuki risk yuksek

Sonuc: MSFS verilerini KULLANMIYORUZ
```

### 4.6 Navaid Verileri (Manuel Derleme)

MVP'de navaid olmayacak. Ileride eklenecek:
- FAA NASR data (ABD - Public)
- Eurocontrol AIS (Avrupa - Basvuru gerekli)
- Community katki sistemi

---

## 5. Veri Akisi

### 5.1 PC Bridge <-> Mobile

```
+------------------+                      +------------------+
|                  |                      |                  |
|   PC BRIDGE      |                      |   MOBILE APP     |
|                  |                      |                  |
+--------+---------+                      +--------+---------+
         |                                         |
         |  HTTP REST                              |
         |  - Audio upload (POST)                  |
         |  - Command execute (POST)               |
         |  - Settings (GET/PUT)                   |
         |                                         |
         |  WebSocket (Real-time)                  |
         |  <=====================================>|
         |  - Sim data stream (2Hz)                |
         |  - Position updates                     |
         |  - Phase changes                        |
         |  - Command results                      |
         |  - TTS audio stream                     |
         |                                         |
+--------+---------+                      +--------+---------+
|                  |                      |                  |
|   MSFS           |                      |   LOCAL DB       |
|   SimConnect     |                      |   (SQLite)       |
|                  |                      |                  |
|  - Aircraft pos  |                      |  - Airports      |
|  - Flight data   |                      |  - Navaids       |
|  - Gear/Flaps    |                      |  - Map tiles     |
|  - Fuel/Weight   |                      |  - Settings      |
|                  |                      |                  |
+------------------+                      +------------------+
```

### 5.2 WebSocket Veri Formati

```json
{
  "type": "sim_data",
  "timestamp": "2025-01-23T10:30:00Z",
  "data": {
    "position": {
      "latitude": 40.976,
      "longitude": 28.814,
      "altitude_msl": 35000,
      "altitude_agl": 35000,
      "heading": 270,
      "track": 268
    },
    "speed": {
      "indicated": 280,
      "true": 480,
      "ground": 450,
      "mach": 0.78,
      "vertical": 0
    },
    "aircraft": {
      "title": "Fenix A320",
      "type": "A320",
      "gear_position": 0,
      "flaps_index": 0,
      "spoilers_armed": true
    },
    "fuel": {
      "total_kg": 12450,
      "flow_kg_h": 2400,
      "endurance_min": 311
    },
    "navigation": {
      "nav1_freq": 110.50,
      "nav1_ident": "ILS 06",
      "nav1_dme": 45.2
    },
    "environment": {
      "wind_direction": 290,
      "wind_speed": 25,
      "oat": -45,
      "qnh": 1013
    },
    "flight_phase": "CRUISE"
  }
}
```

---

## 6. Offline Yetenek

### 6.1 Offline Calisanlar
- [x] PTT ve ses kaydi
- [x] Yerel harita (cached tiles)
- [x] Havaalani veritabani
- [x] Checklist'ler
- [x] Ayarlar

### 6.2 Online Gerekenler
- [ ] PC Bridge baglantisi (ana ozellik)
- [ ] Canli METAR/TAF
- [ ] VATSIM trafik
- [ ] Harita tile indirme (ilk seferde)

### 6.3 Tile Cache Stratejisi

```
Kullanici ucus plani yuklediginde:
1. Rota boyunca 50nm buffer
2. Kalkis/varis havaalani 100nm
3. Zoom 5-12 arasi tile'lar
4. Tahmini boyut: 50-200 MB/ucus
```

---

## 7. UI/UX Prensipleri

### 7.1 Tasarim Dili

- **Dark Theme**: Gece ucuslari icin (kokpit uyumlu)
- **Aviation Colors**: Standart renk kodlari
  - Yesil: Aktif/OK
  - Amber: Dikkat/Warning
  - Kirmizi: Tehlike/Error
  - Cyan: Bilgi/Navigation
  - Magenta: Flight plan/Active waypoint

### 7.2 Font

- **Mono/Digital**: Sayi gosterimleri icin (DSEG, LCD style)
- **Sans-serif**: Genel metin (Roboto, SF Pro)
- Buyuk, okunabilir font boyutlari (tablet kullanimi)

### 7.3 Touch Hedefleri

- Minimum 48x48 dp touch target
- PTT butonu: Ekranin 1/4'u (kolay erisilebilir)
- Gesture desteği: Swipe (sayfalar arasi), Pinch (zoom)

---

## 8. Flutter Proje Yapisi

```
mobile/
+-- lib/
|   +-- main.dart                 # Entry point
|   +-- app.dart                  # App configuration
|   |
|   +-- core/                     # Cekirdek
|   |   +-- constants/            # Sabitler, renkler
|   |   +-- theme/                # Dark theme
|   |   +-- utils/                # Yardimci fonksiyonlar
|   |   +-- extensions/           # Dart extensions
|   |
|   +-- data/                     # Veri katmani
|   |   +-- models/               # Data models
|   |   +-- repositories/         # Veri erisim
|   |   +-- datasources/          # API, Local DB
|   |   +-- database/             # SQLite schemas
|   |
|   +-- services/                 # Servisler
|   |   +-- bridge_service.dart   # PC Bridge iletisimi
|   |   +-- websocket_service.dart# WebSocket yonetimi
|   |   +-- audio_service.dart    # Ses kayit/oynatma
|   |   +-- location_service.dart # GPS (opsiyonel)
|   |
|   +-- features/                 # Ozellik modulleri
|   |   +-- home/                 # Ana ekran
|   |   +-- voice/                # PTT, komut
|   |   +-- map/                  # Harita
|   |   +-- flight_data/          # PFD, engine
|   |   +-- checklist/            # Checklist UI
|   |   +-- airport/              # Havaalani bilgi
|   |   +-- settings/             # Ayarlar
|   |   +-- connection/           # QR, baglanti
|   |
|   +-- widgets/                  # Paylasilan widget'lar
|       +-- pfd_tape.dart         # Speed/Alt tape
|       +-- compass_rose.dart     # Heading indicator
|       +-- fuel_gauge.dart       # Yakit gostergesi
|       +-- status_bar.dart       # Ust bilgi cubugu
|
+-- assets/
|   +-- icons/                    # Ucak, navaid ikonlari
|   +-- data/                     # airports.json, navaids.json
|   +-- fonts/                    # LCD font
|
+-- test/                         # Unit & widget testleri
|
+-- pubspec.yaml                  # Bagimliliklar
```

---

## 9. Bagimliliklar (pubspec.yaml)

```yaml
dependencies:
  flutter:
    sdk: flutter

  # State Management
  flutter_riverpod: ^2.4.0       # State management

  # Network
  dio: ^5.3.0                    # HTTP client
  web_socket_channel: ^2.4.0     # WebSocket

  # Map
  flutter_map: ^6.0.0            # OpenStreetMap
  latlong2: ^0.9.0               # Coordinates

  # Audio
  record: ^5.0.0                 # Ses kayit
  just_audio: ^0.9.35            # Ses oynatma

  # QR
  mobile_scanner: ^3.5.0         # QR kod okuma

  # Storage
  sqflite: ^2.3.0                # SQLite
  shared_preferences: ^2.2.0     # Key-value
  path_provider: ^2.1.0          # File paths

  # UI
  flutter_svg: ^2.0.7            # SVG icons
  shimmer: ^3.0.0                # Loading effect

  # Utils
  intl: ^0.18.0                  # Formatting
  geolocator: ^10.0.0            # GPS (opsiyonel)
```

---

## 10. Faz Plani

### Faz 1: Temel Baglanti (MVP) ✅ TAMAMLANDI
- [x] ✅ QR kod ile PC baglantisi
- [x] ✅ PTT butonu + ses kaydi
- [x] ✅ Temel sim verisi gosterimi
- [x] ✅ TTS yanit oynatma
- [x] ✅ Basit dark theme
- [x] ✅ Riverpod state management
- [x] ✅ Auto-reconnection & saved connections

### Faz 2: Flight Data ✅ TAMAMLANDI
- [x] ✅ PFD tape'leri (speed, altitude) - CustomPaint ile gercek PFD gorunumu
- [x] ✅ Navigation bilgileri (HDG, TRK, WIND, NAV1/NAV2, DME)
- [x] ✅ Fuel/weight gosterimi (progress bar, endurance, flow)
- [x] ✅ Flight Data Screen (portrait + landscape layout)
- [ ] Engine data (N1, N2, EGT - MVP sonrasi)

> **Not:** Bridge tarafinda AircraftState ve WebSocket genisletildi,
> tum veriler nested JSON formatinda mobile'a gonderiliyor (2Hz).

### Faz 3: Checklist UI ✅ TAMAMLANDI
- [x] ✅ Interaktif checklist ekrani (checklist_detail_screen.dart)
- [x] ✅ Checklist secimi (brosur tarzı UI, faz bazlı gruplama)
- [x] ✅ Arama fonksiyonu (checklist_screen.dart)
- [x] ✅ Dogrulama durumu gosterimi (verified/not verified badges)
- [x] ✅ Progress tracking (progress bar, yuzde gosterimi)
- [x] ✅ CHECK/SKIP/CANCEL butonlari
- [x] ✅ Haptic feedback
- [ ] Sesli kontrol entegrasyonu (PTT ile checklist kontrolu - MVP sonrasi)

> **Not:** Backend checklist sistemi hazir (8 API endpoint).
> Mobil UI tamamlandi - checklist_provider.dart, checklist_screen.dart, checklist_detail_screen.dart

### Faz 4: Harita
- [ ] OpenStreetMap entegrasyonu
- [ ] Ucak pozisyonu (moving map)
- [ ] Flight plan rotasi
- [ ] Temel havaalani ikonlari

### Faz 5: Airport Info
- [ ] Havaalani arama
- [ ] Runway/frequency bilgisi
- [ ] METAR/TAF (online)
- [ ] Favoriler

### Faz 6: Gelismis Harita
- [ ] Navaid katmani
- [ ] Airspace katmani
- [ ] Tile caching (offline)
- [ ] VATSIM trafik (opsiyonel)

### Faz 7: Polish
- [ ] Animasyonlar
- [ ] Haptic feedback
- [ ] Widget shortcuts
- [ ] Tablet optimizasyonu

---

## 11. Ek Bilgiler

### 11.1 VATSIM Nedir?

**VATSIM** (Virtual Air Traffic Simulation Network) - Gercek insanlarin online olarak
hava trafik kontroloru (ATC) oynamasini saglayan bir ag.

```
Ornek Senaryo:
+-- Sen MSFS'te Istanbul'dan kalkiyorsun
+-- Gercek bir kisi "Istanbul Tower" rolunde sana kalkis izni veriyor
+-- Diger gercek pilotlar da ayni hava sahasinda ucuyor

Haritada Gosterim (MVP Sonrasi):
+-- VATSIM API'sinden tum online pilotlarin pozisyonunu cekebiliriz
+-- Radar ekrani gibi: "Su an Istanbul cevresinde 15 pilot var"
+-- ATC pozisyonlari da gosterilebilir
```

**Karar:** MVP sonrasi degerlendirilecek (opsiyonel ozellik)

### 11.2 SimBrief Nedir?

**SimBrief** - Ucretsiz online ucus planlama servisi. Sim pilotlarinin ~%90'i kullaniyor.

```
SimBrief'te Yapilanlar:
+-- Rota planlama: LTFM -> LTBA
+-- Yakit hesaplama
+-- Hava durumu kontrolu
+-- OFP (Operational Flight Plan) olusturma

Entegrasyon Ne Saglar:
+-- Kullanici SimBrief'te plan yapar
+-- "Import from SimBrief" butonu ile plani cekilir
+-- Haritada rota otomatik cizilir
+-- Waypoint'ler yuklenir
```

**SimBrief API Sinirlari:**
- Sadece kullanicinin KENDI planini cekebilirsin
- Havaalani/navaid veritabani API ile ACIK DEGIL
- Ticari kullanim icin Navigraph ile iletisim onerilir

**Karar:** MVP sonrasi (Faz 4-5), lansman oncesi Navigraph'a onay emaili atilacak

### 11.3 Karar Verilmis Konular

| Soru | Karar | Tarih |
|------|-------|-------|
| Harita veri kaynagi | OurAirports + Manuel | 2025-01 |
| VATSIM entegrasyonu | MVP sonrasi opsiyonel | 2025-01 |
| SimBrief entegrasyonu | MVP sonrasi (Faz 4-5) | 2025-01 |
| Tablet vs Telefon | Her ikisi (responsive) | 2025-01 |
| Platform onceligi | Paralel (Flutter) | 2025-01 |
| MVP kapsami | Faz 1-2-3 | 2025-01 |
| MSFS verisi | Kullanilmayacak (risk) | 2025-01 |

### 11.4 Acik Konular (Gelecekte Karar Verilecek)

1. **OpenAIP lisansi:** Basari sonrasi ~$500/yil deger mi?
2. **Navigraph onay:** SimBrief ticari kullanim icin email atilacak
3. **Airspace verileri:** Hangi kaynak kullanilacak?
4. **Community katki:** Kullanicilar navaid ekleyebilir mi?

---

## 12. MVP Tanimi

### 12.1 MVP Nedir?

**MVP = Minimum Viable Product** (Satilabilir Minimum Urun)

```
+---------------------------------------------------------------+
|                        MVP KAPSAMI                            |
+---------------------------------------------------------------+
|                                                               |
|  Faz 1: Temel Baglanti           <- Urun calisiyor           |
|  +-- QR ile PC baglantisi                                     |
|  +-- PTT butonu + ses kaydi                                   |
|  +-- TTS yanit oynatma                                        |
|  +-- Baglanti durumu                                          |
|                                                               |
|  Faz 2: Flight Data              <- Urun KULLANISLI oluyor   |
|  +-- Hiz/Yukseklik gosterimi                                  |
|  +-- Heading, VS                                              |
|  +-- Ucus fazi                                                |
|                                                               |
|  Faz 3: Checklist UI             <- Urun SATILABILIR oluyor  |
|  +-- Interaktif checklist                                     |
|  +-- Sesli kontrol                                            |
|  +-- Dogrulama durumu                                         |
|                                                               |
+---------------------------------------------------------------+
|                      MVP SONRASI                              |
+---------------------------------------------------------------+
|                                                               |
|  Faz 4: Harita                   <- Premium ozellik          |
|  Faz 5: Airport Info             <- Premium ozellik          |
|  Faz 6: Gelismis Harita          <- Premium ozellik          |
|  Faz 7: Polish                   <- Kalite artisi            |
|                                                               |
+---------------------------------------------------------------+
```

### 12.2 MVP Basari Kriterleri

- [x] ✅ PC Bridge'e baglanabiliyor
- [x] ✅ Ses kaydedip gonderebiliyor
- [x] ✅ Komut yaniti alabiliyor (TTS)
- [x] ✅ Ucak verilerini gorebiliyor
- [x] ✅ Checklist kullanabiliyor
- [ ] Telefon VE tablette calisiyor (test edilecek)
- [ ] Android VE iOS'ta calisiyor (iOS test edilecek)

---

## 13. Referanslar

### Ilham Kaynaklari
- Garmin G1000/G3000 EFB
- Airbus EFB (flyPad)
- ForeFlight
- Navigraph Charts

### Teknik Kaynaklar
- [flutter_map docs](https://docs.fleaflet.dev/)
- [OpenStreetMap wiki](https://wiki.openstreetmap.org/)
- [OurAirports data](https://ourairports.com/data/)
- [VATSIM API](https://api.vatsim.net/)
- [SimBrief API](https://www.simbrief.com/api/)
- [NOAA Aviation Weather](https://aviationweather.gov/)

### Veri Kaynaklari
- **OurAirports:** https://ourairports.com/data/ (Public Domain)
- **OpenStreetMap:** https://www.openstreetmap.org/ (ODbL)
- **NOAA/AWC:** https://aviationweather.gov/data/ (Public)

---

## Degisiklik Gecmisi

| Tarih | Degisiklik |
|-------|------------|
| 2025-01-23 | Ilk tasarim dokumani olusturuldu |
| 2025-01-23 | Kararlar eklendi: OurAirports, MVP kapsami, responsive tasarim |
| 2025-01-23 | VATSIM ve SimBrief aciklamalari eklendi |
| 2025-01-23 | MSFS veri kullanim riski dokumante edildi |
| 2025-11-24 | Faz 1 ve Faz 2 tamamlandi olarak isaretlendi |
| 2025-11-24 | PFD Tape, Navigation, Fuel widget'lari eklendi |
| 2025-11-24 | Faz 3 (Checklist UI) tamamlandi |
| 2025-11-24 | Flight Data 3-tab sistemi eklendi (PFD, NAV, FUEL) |
| 2025-11-24 | Kullanici dostu hata mesajlari eklendi |
| 2025-11-24 | QR kod HTML sayfasi eklendi |
| 2025-11-25 | ✅ Settings UI tamamlandi (Settings screen + Riverpod provider) |
| 2025-11-25 | ✅ TTS multi-voice sistem (4 Public Domain voices) |
| 2025-11-25 | ✅ On-demand voice download sistemi eklendi |
| 2025-11-25 | ✅ Mic sensitivity, TTS volume slider eklendi |
| 2025-11-25 | ✅ Theme mode toggle (Dark/Light) eklendi |
| 2025-12-05 | ✅ **Checklist UI tamamen yenilendi - PDF/Brochure tarzı** |
| 2025-12-05 | ✅ Beyaz zemin + noktalı çizgi satırlar + aviation renk paleti |
| 2025-12-05 | ✅ Header: Bridge'den uçak bilgisi + Smart Flight Deck branding |
| 2025-12-05 | ✅ Current item highlight panel (verification badge ile) |
| 2025-12-05 | ✅ Professional aviation format (kDarkBlue, kGreen, kAmber) |

---

*Son guncelleme: 2025-12-05*
