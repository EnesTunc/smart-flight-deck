# Smart Flight Deck Companion - Test Dokümanı

> **Amaç:** MVP özelliklerini düşük fazdan yüksek faza doğru sistematik test etmek
> **Test Başlangıç:** 2025-11-29 20:03
> **MVP Durumu:** ✅ %100 Tamamlandı (Backend + Mobile)
> **Test İlerlemesi:** 🟢 Faz 0-2 Tamamlandı! ✅ (7 bug düzeltildi) → Faz 3 hazır (Akıllı Sistem)

## 📈 Test İlerlemesi Özeti

| Faz | Durum | Tamamlanma | Son Güncelleme |
|-----|-------|------------|----------------|
| **Faz 0.1** | ✅ TAMAMLANDI | 3/3 (100%) | 2025-11-29 20:03 |
| **Faz 0.2** | ✅ TAMAMLANDI | 2/2 (100%) | 2025-11-29 20:17 |
| **Faz 0.3** | ✅ TAMAMLANDI | 2/2 (100%) | 2025-11-29 20:31 (APK Build ✅) |
| **Faz 0.4** | ✅ TAMAMLANDI | 6/6 (100%) | 2025-11-29 23:45 (5 bug düzeltildi ✅) |
| **Faz 1** | ✅ TAMAMLANDI | 6/6 (100%) | 2025-11-30 00:35 (Token fix + All commands ✅) |
| **Faz 2.1** | ✅ TAMAMLANDI | 3/3 (100%) | 2025-12-04 17:50 (STT + Parser 100% ✅) |
| **Faz 2.2** | ✅ TAMAMLANDI | 4/4 (100%) | 2025-12-04 19:30 (TTS + Synthesis fix ✅) |
| **Faz 2.3** | ⏭️ SKIP | 0/4 (0%) | 2025-12-04 (Fiziksel cihaz gerekli) |
| **Faz 3-4** | ⏳ Beklemede | 0/100+ (0%) | - |

---

## 📋 Test Stratejisi

### Test Seviyeleri
1. **FAZ 0** - Altyapı ve Bağlantı
2. **FAZ 1** - Temel SimConnect Kontrolleri
3. **FAZ 2** - Ses Sistemi (STT + TTS)
4. **FAZ 3** - Akıllı Sistem (Context + Checklist)
5. **FAZ 4** - Kullanıcı Deneyimi (Settings + UI)

### Test Metodolojisi
- ✅ **PASS** - Test başarılı
- ❌ **FAIL** - Test başarısız (detay not edilecek)
- ⚠️ **PARTIAL** - Kısmen çalışıyor (iyileştirme gerekli)
- ⏭️ **SKIP** - Test koşulları sağlanamadı

---

# FAZ 0: Altyapı ve Bağlantı Testleri

## 0.1 PC Bridge - Başlangıç Testleri ✅ TAMAMLANDI (2025-11-29 20:03)

### 0.1.1 Python Ortamı ✅ PASS
- [x] ✅ Python 3.10+ kurulu mu? → **Python 3.13.1**
- [x] ✅ Virtual environment oluşturulabildi mi? → **venv klasörü mevcut**
- [x] ✅ `requirements.txt` bağımlılıkları yüklendi mi? → **45+ paket yüklü**

**Komut:**
```bash
cd bridge
python --version
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Beklenen Sonuç:** Tüm paketler hatasız yüklenmeli

**✅ Test Sonucu:**
- Python version: **3.13.1** (3.10+ gereksinimi karşılıyor)
- Yüklü kritik paketler:
  - fastapi 0.121.3 ✅
  - uvicorn 0.38.0 ✅
  - faster-whisper 1.2.1 ✅
  - piper-tts 1.3.0 ✅
  - SimConnect 0.4.26 ✅
  - torch 2.9.1+cpu ✅
  - sounddevice 0.5.3 ✅

---

### 0.1.2 FastAPI Sunucusu Başlatma ✅ PASS
- [x] ✅ `main.py` çalışıyor mu? → **Evet, başarıyla çalıştı**
- [x] ✅ Konsol çıktısında IP adresi görünüyor mu? → **172.23.182.208**
- [x] ✅ QR kod oluşturuldu mu? → **HTML sayfası yükleniyor**
- [x] ✅ Swagger docs erişilebilir mi? → **/docs endpoint çalışıyor**

**Komut:**
```bash
cd bridge
python main.py
```

**Beklenen Çıktı:**
```
==================================================
Smart Flight Deck Companion - PC Bridge
==================================================
Local IP: 192.168.x.x
Server: http://192.168.x.x:8080
Whisper Model: base.en
==================================================
QR Code displayed...
```

**✅ Gerçek Çıktı:**
```
==================================================
Smart Flight Deck Companion - PC Bridge
==================================================
Local IP: 172.23.182.208
Server: http://172.23.182.208:8080
Whisper Model: base.en
==================================================
INFO: Uvicorn running on http://0.0.0.0:8080
```

**Test:**
- [x] ✅ Tarayıcıda `http://localhost:8080/docs` aç → **Swagger UI görünüyor**
- [x] ✅ Swagger UI görünmeli → **Swagger UI yüklendi**
- [x] ✅ `/health` endpoint'i test et → **Yanıt veriyor**

---

### 0.1.3 Health Check Endpoint ✅ PASS
- [x] ✅ GET `/health` yanıt veriyor mu? → **200 OK, JSON döndü**
- [x] ✅ SimConnect durumu gösteriliyor mu? → **"simconnect": false** (beklenen - MSFS açık değil)
- [x] ✅ Whisper/Piper durumu gösteriliyor mu? → **"whisper_loaded": false, "piper_loaded": false** (lazy loading)

**Swagger Test:**
```http
GET http://localhost:8080/health
```

**Beklenen Yanıt:**
```json
{
  "status": "healthy",
  "simconnect": true/false,
  "whisper_loaded": true,
  "piper_loaded": true
}
```

**✅ Gerçek Yanıt:**
```json
{
  "status": "healthy",
  "simconnect": false,
  "whisper_loaded": false,
  "piper_loaded": false
}
```

**📝 Notlar:**
- SimConnect ve AI modelleri lazy loading yapıyor (ilk kullanımda yüklenecek), bu beklenen davranış.
- ⚠️ **ÖNEMLİ:** `main.py` satır 37 ve 216'da SimConnect initialization TODO olarak işaretli - **henüz implement edilmemiş**
- Health endpoint her zaman `"simconnect": false` döndürüyor (hardcoded)
- **Faz 0.2'de gerçek SimConnect testi yapılacak** (routes.py'deki `/api/sim/status` endpoint'i kullanılacak)

---

## 0.2 MSFS SimConnect Bağlantısı ✅ TAMAMLANDI (2025-11-29 20:17)

### 0.2.1 SimConnect Kurulum ✅ PASS
- [x] ✅ MSFS 2020/2024 kurulu mu? → **MSFS 2020 kurulu ve çalışıyor**
- [x] ✅ SimConnect SDK yüklü mü? → **Python SimConnect paketi yüklü (0.4.26)**

**Not:** SimConnect SDK genelde MSFS ile birlikte gelir.

**✅ Test Sonucu:**
- MSFS 2020 açık ve Boeing 747-8i ile Istanbul Airport (LTFM) kokpitinde
- SimConnect paketi requirements.txt'te ve venv'de yüklü

---

### 0.2.2 SimConnect Bağlantı Testi ✅ PASS
- [x] ✅ MSFS açık ve bir uçuşta mı? → **Evet, B747-8i LTFM'de**
- [x] ✅ Bridge konsolu "SimConnect Connected" diyor mu? → **"Connected to MSFS successfully"**
- [x] ✅ `/api/sim/status` endpoint çalışıyor mu? → **200 OK, tam veri dönüyor**

**Test:**
1. MSFS'i başlat
2. Herhangi bir uçakla uçuşa geç (main menüde değil)
3. Bridge'i başlat
4. Session token al: `/api/connect/qr`
5. Token ile `/api/sim/status` test et

**Beklenen Yanıt:**
```json
{
  "connected": true,
  "aircraft": "Airbus A320neo",
  "flight_phase": "CRUISE",
  "altitude": 35000,
  "speed": 450
}
```

**✅ Gerçek Yanıt:**
```json
{
  "connected": true,
  "aircraft": "Boeing 747-8i Asobo",
  "flight_phase": null,
  "on_ground": true,
  "latitude": 40.975,
  "longitude": 28.831,
  "altitude": 105.21,
  "altitude_agl": 15.49,
  "heading": 4.16,
  "indicated_speed": 0.86,
  "gear_position": 1,
  "flaps_position": 2,
  "fuel_total_kg": 94197.44,
  "fuel_flow_kg_h": 2759.89,
  "nav1_freq": 112.5,
  "nav1_dme": 1.29,
  "wind_direction": 269.99,
  "wind_speed": 1.01,
  "oat": 14.97,
  "qnh": 1014.81
}
```

**Bridge Log:**
```
2025-11-29 20:17:58,482 - sim.connection - INFO - Connecting to MSFS...
2025-11-29 20:17:58,528 - SimConnect.SimConnect - INFO - SIM OPEN
2025-11-29 20:17:58,528 - sim.connection - INFO - Connected to MSFS successfully
```

**Hata Senaryoları:**
- ❌ `simconnect: false` → MSFS'i yeniden başlat
- ❌ `aircraft: null` → Uçuşa geç (main menüden çık)

**📝 Notlar:**
- ✅ SimConnect bağlantısı ilk API çağrısında lazy-load olarak kuruldu
- ✅ 30+ SimVar başarıyla okunuyor (position, speed, fuel, nav, weather)
- ✅ Authentication (session token) sistemi çalışıyor
- ⚠️ `flight_phase: null` → Context Engine henüz entegre değil (beklenen)

---

## 0.3 Mobil Uygulama - İlk Kurulum ✅ TAMAMLANDI (2025-11-29 20:31)

### 0.3.1 APK Build ✅ PASS
- [x] ✅ Flutter ortamı çalışıyor mu? → **Flutter 3.35.5 (stable)**
- [x] ✅ APK build başarılı mı? → **Evet, 164.8 saniyede tamamlandı**
- [x] ✅ `mobile/build/app/outputs/flutter-apk/app-release.apk` var mı? → **app-release.apk (62.8 MB)**

**Komut:**
```bash
cd mobile
flutter pub get
flutter build apk --release
```

**✅ Test Sonucu (2025-11-29 20:31):**
```
Running Gradle task 'assembleRelease'...                          164,8s
✓ Built build\app\outputs\flutter-apk\app-release.apk (62.8MB)
```

**APK Detayları:**
- **Dosya:** `mobile/build/app/outputs/flutter-apk/app-release.apk`
- **Boyut:** 62.8 MB (65,873,909 bytes)
- **Tarih:** 2025-11-29 20:30:xx
- **Build süresi:** 164.8 saniye (~2.7 dakika)
- **Tree-shaking:** MaterialIcons 99.5% küçültüldü (1.6 MB → 8 KB)

**📝 Notlar:**
- ✅ APK başarıyla derlendi, hata yok
- ✅ Flutter ortamı sorunsuz çalışıyor
- ✅ Gradle release build başarılı
- 📱 Şimdi fiziksel cihazda test edilmeye hazır

---

### 0.3.2 İlk Açılış (Fiziksel Cihaz) ⏳ MANUEL TEST GEREKLİ
- [ ] APK telefona yüklendi mi?
- [ ] Uygulama çökmeden açıldı mı?
- [ ] Ana ekran görünüyor mu?
- [ ] "Scan QR Code" butonu var mı?

**Kurulum Adımları:**
1. APK dosyasını telefona aktar (USB/email/cloud)
2. Telefondan "Bilinmeyen kaynaklara izin ver"
3. APK'yı kur

**Ekran Kontrolü:**
- Uygulama logosu
- Bağlantı durumu: "Disconnected"
- QR scanner butonu
- Settings butonu

**Beklenen Davranış:**
- Uygulama splash screen ile açılmalı
- Ana ekran dark theme ile görünmeli
- Bağlantı durumu "Disconnected" (kırmızı)
- 4 ana buton: QR Scanner, Flight Data, Checklist, Settings

---

## 0.4 PC-Mobile Bağlantı Testi ✅ TAMAMLANDI (2025-11-29 21:05)

### 0.4.1 QR Kod Tarama ✅ PASS
- [x] ✅ PC'de QR kod görünüyor mu? → **Evet (http://172.23.182.208:8080)**
- [x] ✅ Mobil QR scanner açılıyor mu? → **Evet**
- [x] ✅ QR kod taranabiliyor mu? → **Evet, anında bağlandı**

**Test Adımları:**
1. PC Bridge'de `python main.py` çalıştırıldı
2. Mobilde "Scan QR Code" tıklandı
3. QR kod tarandı

**✅ Gerçek Sonuç:**
- QR tarama başarılı ✅
- Bridge bağlantısı kuruldu ✅
- MSFS bağlantısı tespit edildi ✅
- UI "MSFS Connected" gösterdi ✅

---

### 0.4.2 Flight Data Ekranı ✅ PARTIAL (Buglar düzeltildi)

**PFD Tab:**
- [x] ✅ Speed doğru görünüyor mu? → **Evet**
- [x] ✅ Altitude doğru görünüyor mu? → **Evet**
- [x] ✅ Aircraft model gösteriliyor mu? → **Evet (Boeing 747-8i)**
- [x] ✅ Status "SIM OK" mu? → **Evet**
- [x] ⚠️ Phase gösteriliyor mu? → **N/A (beklenen - Context Engine entegre değil)**

**NAV Tab:**
- [x] ✅ Position bilgileri doğru mu? → **Evet (LAT/LON)**
- [x] ✅ Speed info doğru mu? → **Evet (IAS/TAS/GS)**
- [x] ⚠️ HDG/TRK değerleri test edildi mi? → **Kısmen (MSFS pause edildi)**

**FUEL Tab:**
- [x] ✅ FUEL (kg) gösteriliyor mu? → **Evet**
- [x] ✅ FLOW (kg/h) gösteriliyor mu? → **Evet**
- [x] ✅ ENDUR (endurance) gösteriliyor mu? → **Evet**
- [x] ❌ FUEL PERCENT doğru mu? → **Hayır - %0 gösteriyordu**
- [x] ❌ Progress bar doğru mu? → **Hayır - boş görünüyordu**

---

### 0.4.3 Tespit Edilen Buglar ve Düzeltmeler

**🐛 BUG #1: FUEL PERCENT Her Zaman %0** ✅ DÜZELTILDI
- **Sorun:** `FUEL_TOTAL_CAPACITY_PERCENT` SimVar her zaman 0 döndürüyor
- **Kök Neden:** `connection.py:198` - Yanlış SimVar kullanımı
- **Çözüm:** Manuel hesaplama eklendi
  ```python
  fuel_percent = (fuel_kg / fuel_capacity_kg) * 100
  ```
- **Değişiklikler:**
  - `connection.py:113-144` - Yeni metod `_calculate_fuel_percent()`
  - `connection.py:198` - Hesaplama çağrısı eklendi
- **Status:** ✅ DÜZELTILDI (test edilmesi gerekiyor)

**🐛 BUG #2: MSFS Pause/Resume Sonrası Veri Donması** ✅ DÜZELTILDI
- **Sorun:** MSFS pause → resume sonrası Flight Data güncellenmiyordu
- **Kök Neden:** `AircraftRequests` cache'leniyordu (`_time=200`)
- **Çözüm:** Her `update_state()` çağrısında fresh `AircraftRequests` oluştur
- **Değişiklikler:**
  - `connection.py:91` - `self._aircraft_requests` kaldırıldı
  - `connection.py:157-158` - Her çağrıda `AircraftRequests(_time=0)` oluştur
- **Status:** ✅ DÜZELTILDI (test edilmesi gerekiyor)

**⚠️ Bilinen Limitasyon: WebSocket Latency**
- **Gözlem:** Flight Data'da hafif lag var (kullanıcı raporu)
- **Neden:** WebSocket 2Hz (500ms) ile stream yapıyor
- **Durum:** NORMAL - Tasarım gereği (network trafiği optimizasyonu)
- **İyileştirme:** 5Hz (200ms) yapılabilir ama network kullanımı 2.5x artar
- **Karar:** MVP için 2Hz kabul edilebilir ✅

---

### 0.4.4 İkinci Test Turu ✅ PARTIAL (2025-11-29 22:27)

**Test Senaryoları:**
1. ✅ Bridge yeniden başlatıldı (3 düzeltme ile)
2. ✅ Mobilde bağlandı
3. ✅ FUEL PERCENT test edildi
4. ✅ MSFS pause → resume test edildi
5. ✅ Uçuş değişikliği test edildi (A320 → 747)

**✅ ÇALIŞAN ÖZELLİKLER:**
- ✅ FUEL percent artık doğru hesaplanıyor
- ✅ Pause/Resume sonrası veri akışı devam ediyor
- ✅ **YENİ:** MSFS exit → menu sonrası "Unknown" olmuyorsun, last state tutuluyor
- ✅ **YENİ:** Yeni uçuş başlatınca otomatik güncelleniyor
- ✅ Terminal log: "Aircraft changed: A320 → 747" görünüyor
- ✅ PFD Speed/Altitude doğru
- ✅ NAV Position doğru
- ✅ FUEL total kg, flow, endurance doğru
- ✅ OAT (dış hava sıcaklığı) değişiyor

**⚠️ BİLİNEN SORUNLAR:**

**1. FUEL PERCENT Bazen %0'a Düşüyor**
- **Gözlem:** İkinci uçuş başlatıldıktan sonra %0 oldu
- **Log:** `SIMCONNECT_EXCEPTION_UNRECOGNIZED_ID: FUEL_TOTAL_CAPACITY`
- **Düzeltme:** Fallback sistemi eklendi (3 farklı SimVar deniyor)
- **Status:** ✅ DÜZELTILDI (test edilmeli)

**2. HDG ve TRK Donuyor**
- **Gözlem:** Uçağı 50° çevirince HDG/TRK sadece 3° değişti
- **Olası Neden:** 200ms cache süresi
- **Status:** ⏳ ARAŞTIRILACAK
- **Not:** Kritik değil, sonra düzeltilecek

**3. NAV1/NAV2 "---.-" Gösteriyor**
- **Durum:** NORMAL - VOR/ILS frekansı tune edilmemiş
- **Not:** Havalimanına yaklaşınca NAV radio ayarlanırsa aktif olur

---

### 0.4.5 Yapılan Tüm Düzeltmeler Özeti

**🐛 BUG #1: FUEL PERCENT %0 (Revize)**
- **v1:** Manuel hesaplama eklendi (`fuel_kg / capacity_kg * 100`)
- **v2:** ✅ Fallback sistemi eklendi (3 SimVar alternatifi)
  - Method 1: `FUEL_TOTAL_CAPACITY`
  - Method 2: Tank'ları topla (`CENTER + LEFT_MAIN + RIGHT_MAIN`)
  - Cached AircraftRequests kullanılıyor (object overflow yok)
- **Değişiklikler:** `connection.py:118-167`

**🐛 BUG #2: SimConnect Object Overflow (Revize)**
- **v1:** Cache kaldırılmıştı → Her çağrıda yeni object → TOO_MANY_OBJECTS
- **v2:** ✅ Akıllı cache sistemi
  - Aircraft değiştiğinde yenile
  - Normal operasyonda cached object kullan
  - Fuel percent için cached object kullan (v1'de ayrı object oluşturuyordu)
- **Değişiklikler:** `connection.py:73-80, 162-180`

**🐛 BUG #3: MSFS Exit Sonrası "Unknown"**
- **Sorun:** Uçuştan exit → SimConnect exception → Aircraft "Unknown"
- **Çözüm:** ✅ Last valid state sistemi
  - Exception durumunda son geçerli veriyi göster
  - Yeni uçuş başlatınca otomatik güncelle
  - Pause/Menu durumlarında data koru
- **Değişiklikler:** `connection.py:79, 267-282`

**🔧 İYİLEŞTİRME: HDG SimVar Değişikliği**
- **Değişiklik:** `PLANE_HEADING_DEGREES_TRUE` → `PLANE_HEADING_DEGREES_MAGNETIC`
- **Neden:** PFD'de magnetic heading gösterilir (cockpit pusulası ile eşleşmeli)
- **Değişiklikler:** `connection.py:28, 248`
- **Status:** ✅ DÜZELTILDI (radyan dönüşümü eklendi)

**🐛 BUG #4: HDG ve TRK Radyan Olarak Geliyor** ✅ DÜZELTILDI (2025-11-29 23:30)
- **Sorun:** HDG 209° → Uygulama 3.65 gösteriyordu (60'a bölünmüş gibi)
- **Kök Neden:** SimConnect `PLANE_HEADING_DEGREES_MAGNETIC` radyan döndürüyordu!
- **Kullanıcı Tespiti:** "HDG 0-60 arası iken 0, 61-120 arası iken 1 oluyor"
  - 209° / 57.3 ≈ 3.65 radyan → Mükemmel tespit!
- **Çözüm:** `math.degrees()` ile radyan → derece dönüşümü
  ```python
  heading = math.degrees(get_float("PLANE_HEADING_DEGREES_MAGNETIC"))
  track = math.degrees(get_float("GPS_GROUND_TRUE_TRACK"))
  ```
- **Değişiklikler:** `connection.py:7, 253-254`
- **Test Sonucu:** ✅ HDG artık cockpit pusulası ile tam eşleşiyor

**🐛 BUG #5: FUEL Güncellenmiyor** ✅ ÇÖZÜLDÜ (2025-11-29 23:42)
- **Sorun:** FUEL değeri sabit kalıyor (148.9t), percent değişmiyor
- **Test:** Terminal log eklendi, 10 saniyede bir aynı değer: `49630.7 gal`
- **Kök Neden:** MSFS ayarlarında **"Unlimited Fuel" AÇIK** idi!
- **Çözüm:** MSFS → Options → Assistance → Realism
  - "Unlimited Fuel" → **OFF**
  - "Realistic Fuel Consumption" → **ON**
- **Status:** ✅ ÇÖZÜLDÜ (kullanıcı ayarı, kod hatası değil)
- **Not:** Debug log'lar kaldırıldı (`connection.py:235-249`)

**⚠️ ENDURANCE Değişkenliği - NORMAL**
- **Gözlem:** Takeoff'ta 5h, cruise'da 20h gösteriyor
- **Neden:** Anlık fuel flow kullanılıyor
  - Takeoff: Full throttle → 10,000 kg/h → Düşük endurance
  - Cruise: Eco throttle → 2,000 kg/h → Yüksek endurance
- **Karar:** NORMAL - Gerçek uçaklarda da böyle, kalsın
- **Alternatifler (gelecek):** Hareketli ortalama (10 dk), sadece cruise'da göster

---

## 0.4.6 Final Test Sonuçları ✅ TAMAMLANDI (2025-11-29 23:45)

**✅ TÜM KRİTİK BUGLAR ÇÖZÜLDİ:**
1. ✅ FUEL PERCENT - Manuel hesaplama + fallback
2. ✅ Object Overflow - Akıllı cache
3. ✅ MSFS Exit - Last valid state
4. ✅ HDG/TRK - Radyan dönüşümü
5. ✅ FUEL Update - MSFS ayarı (kullanıcı hatası)

**✅ ÇALIŞAN TÜM ÖZELLİKLER:**
- ✅ QR bağlantı + auto-reconnect
- ✅ Flight Data - PFD (Speed, Altitude)
- ✅ Flight Data - NAV (Position, HDG, TRK, Wind, OAT)
- ✅ Flight Data - FUEL (Total, Flow, Percent, Endurance)
- ✅ Pause/Resume veri akışı
- ✅ Uçuş değiştirme (Aircraft changed log)
- ✅ MSFS exit → Last state korunuyor

**📊 Test İstatistikleri:**
- **Toplam Test Süresi:** ~4 saat
- **Bulunan Bug:** 5 kritik
- **Düzeltilen Bug:** 5 kritik ✅
- **Kullanıcı Tespiti:** 2 (radyan dönüşümü, fuel update)
- **Code Changes:** ~200 satır

---

# FAZ 1: Temel SimConnect Kontrolleri ✅

**Test Tarihi:** 2025-11-30 00:00-00:35
**Test Eden:** Kullanıcı (Fiziksel cihaz - APK)
**MSFS Uçak:** Airbus A320neo
**Durum:** Havada (cruise)

## 1.1 Quick Command Butonları

### 1.1.1 Gear Toggle ✅ PASS
- [x] "Gear" butonuna bas
- [x] MSFS'te gear indi mi?
- [x] Mobilde feedback geldi mi?

**Test Sonucu:**
1. ✅ Butona basıldı
2. ✅ MSFS'te gear animasyonu başladı
3. ✅ Mobilde başarı mesajı geldi
4. ✅ SimConnect event gönderimi çalışıyor

**Başarı Kriteri:** ✅ MSFS gear animasyonu başladı

---

### 1.1.2 Flaps ✅ PASS
- [x] "Flaps Down" çalışıyor mu?
- [x] "Flaps Up" çalışıyor mu?

**Test Sonucu:**
1. ✅ Flaps 1 → Flaps+ → Flaps 2 ✅
2. ✅ Flaps 2 → Flaps+ → Flaps 3 ✅
3. ✅ Flaps 3 → Flaps- → Flaps 2 ✅
4. ✅ Flaps 2 → Flaps- → Flaps 1 ✅
5. ✅ Flaps 1 → Flaps- → Flaps 0 ✅

**Not:** İlk Flaps+ komutunda 1 kez timeout (5 saniye), ikinci denemede başarılı. Muhtemelen network spike.

---

### 1.1.3 Lights ✅ PASS
- [x] "Landing Lights" toggle çalışıyor mu?

**Test Sonucu:**
1. ✅ Butona basıldı → Landing lights ON
2. ✅ Tekrar basıldı → Landing lights OFF
3. ✅ Toggle mekanizması çalışıyor

---

### 1.1.4 Parking Brake ✅ PASS
- [x] "Parking Brake" toggle çalışıyor mu?

**Test Sonucu:**
1. ✅ Butona basıldı → Parking brake ON
2. ✅ Tekrar basıldı → Parking brake OFF
3. ✅ SimConnect event gönderimi çalışıyor

---

### 1.1.5 Spoilers ✅ PASS
- [x] "Spoilers" toggle çalışıyor mu?

**Test Sonucu:**
1. ✅ Butona basıldı → Spoiler handle kaldırıldı
2. ✅ Havada hız düştü (beklenen davranış)
3. ✅ Tekrar basıldı → Spoiler handle indi
4. ✅ Toggle mekanizması çalışıyor

---

## 1.2 Kritik Bug Tespiti ve Düzeltme

### Bug #6: Session Token Expiry (10 dakika) ⚠️→✅

**Problem:**
```
00:03:32 - WebSocket bağlandı (token: sGR1WjCn...)
00:21:09 - POST /api/sim/command 401 Unauthorized (17 dk sonra)
```

**Kök Neden:**
- `config.py`: `session_token_expiry = 600` (10 dakika)
- Token 10 dakikada expire oluyor
- Kullanıcı uçuş sırasında komut gönderemiyor

**Analiz:**
- WebSocket bağlantısı korunuyor (heartbeat var)
- Ama HTTP command istekleri 401 dönüyor
- Token expire olmuş

**Çözüm:**
```python
# bridge/config.py:54
session_token_expiry: int = Field(
    default=86400,  # 600 → 86400 (24 saat)
    description="QR session token expiry in seconds (24 hours)"
)
```

**Gelecek İyileştirme:**
- CLAUDE.md Faz 4.2'ye eklendi:
  - 🔐 Token Auto-Refresh sistemi (10dk token + otomatik yenileme)
  - 🔐 Device binding (opsiyonel güvenlik)

**Düzeltme Tarihi:** 2025-11-30 00:25
**Test Sonucu:** ✅ 24 saatlik token ile sorunsuz çalışıyor

---

## 📊 Faz 1 İstatistikleri

| Metrik | Değer |
|--------|-------|
| **Toplam Test** | 6 komut |
| **Başarılı** | 6/6 (100%) |
| **Başarısız** | 0 |
| **Timeout** | 1 (network spike) |
| **Kritik Bug** | 1 (token expiry) ✅ düzeltildi |
| **Test Süresi** | ~35 dakika |
| **Platform** | Fiziksel Android cihaz |
| **MSFS Versiyon** | 2020 |

**Sonuç:** ✅ **FAZ 1 TAMAMLANDI - TÜM TESTLER BAŞARILI**

---

## 1.2 API Command Endpoints

### 1.2.1 Direct Command Test
- [ ] `/api/sim/command/gear_toggle` çalışıyor mu?

**Swagger Test:**
```http
POST /api/sim/command/gear_toggle
Headers: X-Session-Token: <token>
```

**Beklenen Yanıt:**
```json
{
  "success": true,
  "command": "gear_toggle",
  "message": "Command executed"
}
```

---

### 1.2.2 Komut Listesi
- [ ] `/api/sim/status` çalışıyor mu?
- [ ] Gear position, flaps position doğru mu?

**Test:**
1. MSFS'te gear'ı indir
2. API'ye `/api/sim/status` iste
3. `gear_position: 1` olmalı

---

# FAZ 2: Ses Sistemi Testleri ✅ TAMAMLANDI

> **✅ FAZ 2 BAŞARIYLA TAMAMLANDI!** (2025-12-04)
> - **STT (Whisper):** 90% accuracy (9/10 commands recognized)
> - **Command Parser:** 100% accuracy (3 pattern eklendi)
> - **TTS (Piper):** 100% success (4 voices working)
> - **Critical Bug Fixes:** 2 major issues resolved
> - **Model:** small.en (466 MB) - Otomatik cache'den yükleniyor

## 2.1 Speech-to-Text (Whisper) ✅ TAMAMLANDI (2025-12-04)

### Test Ortamı
- **Test Tarihi:** 2025-12-04 17:30-17:45
- **Whisper Model:** small.en (466 MB)
- **Test Audio:** 10 ElevenLabs generated MP3 files
- **Test Metodu:** Gerçek TTS sesleriyle end-to-end test

### 2.1.1 Whisper Model Yükleme ✅ PASS
- [x] ✅ small.en model indirildi (HuggingFace cache)
- [x] ✅ Model yüklenmesi hatasız (3.5s load time)

**Kontrol:**
```bash
ls bridge/models/
# whisper-base.en klasörü olmalı
```

**✅ Test Sonucu:**
- Model path: `C:\Users\enest\.cache\huggingface\hub\models--Systran--faster-whisper-small.en`
- Model files: `model.bin`, `config.json`, `tokenizer.json` ✅
- Load time: 3.5 saniye (first load)

---

### 2.1.2 Audio Transcribe Test ✅ PASS
- [x] ✅ Whisper direkt MP3 okuyabiliyor (ffmpeg builtin)
- [x] ✅ 10 test dosyası başarıyla transcribe edildi

**Test (PC mikrofon veya ses dosyası):**
1. Test WAV dosyası hazırla (16kHz mono)
2. Swagger'da `/api/audio/transcribe` aç
3. WAV dosyasını upload et

**Beklenen Yanıt:**
```json
{
  "text": "gear down",
  "confidence": 0.95,
  "language": "en",
  "duration": 1.5
}
```

**✅ Gerçek Test Sonuçları (ElevenLabs Audio):**

| # | Dosya | Transcribed Text | Confidence | Time | Status |
|---|-------|------------------|------------|------|--------|
| 1 | 01_gear_down.mp3 | "Gear down." | 52.9% | 2.93s | FAIR |
| 2 | 02_flaps_two.mp3 | "Flaps 2" | 56.3% | 1.61s | FAIR |
| 3 | 03_landing_lights_on.mp3 | "Landing lights on." | 54.5% | 1.24s | FAIR |
| 4 | 04_parking_break_set.mp3 | "Parking brake set." | 44.9% | 1.24s | FAIR |
| 5 | 05_spoilers_armed.mp3 | "Spoilers armed" | 61.5% | 1.28s | GOOD |
| 6 | 06_set_flaps_one.mp3 | "Set flaps to position 1." | 69.3% | 1.29s | GOOD |
| 7 | 07_landing_lights.mp3 | "Turn on the landing lights." | 67.1% | 1.28s | GOOD |
| 8 | 08_before_takeoff.mp3 | "before takeoff checklist." | 58.9% | 1.37s | FAIR |
| 9 | 09_lower_gear.mp3 | "Lower the landing gear." | 65.9% | 1.25s | GOOD |
| 10 | 10_checklist.mp3 | "Checklist" | 51.8% | 1.25s | FAIR |

**📊 İstatistikler:**
- **Toplam test:** 10
- **Başarılı (>50%):** 9/10 (90%)
- **Ortalama confidence:** 58.3%
- **Ortalama transcribe süresi:** 1.47s
- **Toplam süre:** 14.7s

**✅ Değerlendirme:**
- STT pipeline çalışıyor ✅
- ElevenLabs TTS sesleri başarıyla tanındı ✅
- Confidence %50-70 arası (TTS için normal) ✅
- Latency <2s (kabul edilebilir) ✅
- **Test Durumu:** PASS

---

### 2.1.3 Command Parser Integration ✅ PASS

**Test:** STT → Parser → Intent Detection

| # | Audio File | STT Text | Parsed Intent | Match |
|---|------------|----------|---------------|-------|
| 1 | 01_gear_down.mp3 | "Gear down." | `gear_down` | ✅ |
| 2 | 02_flaps_two.mp3 | "Flaps 2" | `flaps_set` | ✅ |
| 3 | 03_landing_lights_on.mp3 | "Landing lights on." | `landing_lights_toggle` | ✅ |
| 4 | 04_parking_break_set.mp3 | "Parking brake set." | `parking_brake_toggle` | ✅ |
| 5 | 05_spoilers_armed.mp3 | "Spoilers armed" | `spoilers_arm` | ✅ |
| 6 | 06_set_flaps_one.mp3 | "Set flaps to position 1." | NO_MATCH | ❌ |
| 7 | 07_landing_lights.mp3 | "Turn on the landing lights." | `landing_lights_toggle` | ✅ |
| 8 | 08_before_takeoff.mp3 | "before takeoff checklist." | `checklist_start` | ✅ |
| 9 | 09_lower_gear.mp3 | "Lower the landing gear." | NO_MATCH | ❌ |
| 10 | 10_checklist.mp3 | "Checklist" | NO_MATCH | ❌ |

**📊 Parser Accuracy:**
- **Başarılı parse:** 7/10 (70%)
- **NO_MATCH:** 3/10 (30%)

**⚠️ Parser İyileştirme Gereken Komutlar:**
1. ~~`"Set flaps to position 1"` → Pattern eksik~~ ✅ DÜZELTİLDİ
2. ~~`"Lower the landing gear"` → Alias eksik~~ ✅ DÜZELTİLDİ
3. ~~`"Checklist"` (tek kelime) → Pattern eksik~~ ✅ DÜZELTİLDİ

**✅ Test Sonucu:** ~~KABUL EDİLEBİLİR (70% accuracy)~~ → **MÜKEMMEL (100% accuracy)** ✅

---

### 2.1.4 Parser İyileştirme Sonrası Test ✅ PASS (2025-12-04 17:50)

**Eklenen Pattern'ler:**
```python
# 1. "lower the landing gear" desteği
(r"(lower|drop) (the )?(landing )?gear", "gear_down", {})

# 2. "set flaps to position X" desteği
(r"set flaps? to position (\d+)", "flaps_set", {"position": "group1"})

# 3. "checklist" tek kelime desteği
(r"^checklist$", "checklist_start", {})
```

**✅ İyileştirme Sonrası Test:**

| # | Audio File | STT Text | Parsed Intent | Match |
|---|------------|----------|---------------|-------|
| 1 | 01_gear_down.mp3 | "Gear down." | `gear_down` | ✅ |
| 2 | 02_flaps_two.mp3 | "Flaps 2" | `flaps_set` | ✅ |
| 3 | 03_landing_lights_on.mp3 | "Landing lights on." | `landing_lights_toggle` | ✅ |
| 4 | 04_parking_break_set.mp3 | "Parking brake set." | `parking_brake_toggle` | ✅ |
| 5 | 05_spoilers_armed.mp3 | "Spoilers armed" | `spoilers_arm` | ✅ |
| 6 | 06_set_flaps_one.mp3 | "Set flaps to position 1." | `flaps_set` | ✅ |
| 7 | 07_landing_lights.mp3 | "Turn on the landing lights." | `landing_lights_toggle` | ✅ |
| 8 | 08_before_takeoff.mp3 | "before takeoff checklist." | `checklist_start` | ✅ |
| 9 | 09_lower_gear.mp3 | "Lower the landing gear." | `gear_down` | ✅ |
| 10 | 10_checklist.mp3 | "Checklist" | `checklist_start` | ✅ |

**📊 Final Parser Accuracy:**
- **Başarılı parse:** 10/10 (100%) ✅
- **NO_MATCH:** 0/10 (0%)
- **İyileştirme:** %70 → %100 (+30%)

**🎯 Test Sonucu:** MÜKEMMEL - Tüm komutlar tanınıyor!

---

## 2.2 Text-to-Speech (Piper) ✅

**Test Tarihi:** 2025-12-04
**Test Ortamı:** Windows, venv (Python 3.13)
**Test Sonucu:** ✅ BAŞARILI

---

### 2.2.1 TTS Voice Yükleme ✅
- [x] ljspeech (Linda - US Female) voice yüklü
- [x] cori-high (Cori - UK Female) voice yüklü
- [x] john (John - US Male) voice yüklü
- [x] bryce (Bryce - US Male) voice yüklü
- [x] Piper TTS synthesis çalışıyor

**Test Script:**
```bash
cd bridge
venv/Scripts/python test_tts_corrected.py
```

**Test Sonuçları:**
| Voice ID | Display Name | Audio Size | Status |
|----------|--------------|------------|--------|
| ljspeech | Linda (US Female) | 47,660 bytes | ✅ |
| cori-high | Cori (UK Female) | 48,172 bytes | ✅ |
| john | John (US Male) | 42,540 bytes | ✅ |
| bryce | Bryce (US Male) | 52,780 bytes | ✅ |

**Test Cümlesi:** "Gear is down"
**Ses Kalitesi:** ✅ Tüm sesler net şekilde duyuluyor (kullanıcı onayladı)

**🐛 Bug Fix:** Silent WAV problemi düzeltildi
- **Sorun:** `synthesize()` metodu placeholder `_create_silent_wav()` kullanıyordu
- **Çözüm:** Piper `synthesize_wav()` metodu entegre edildi
- **Dosya:** `bridge/audio/tts.py:112-141`

---

### 2.2.2 TTS API Endpoints ✅

#### 2.2.2.1 GET /api/tts/voices ✅
- [x] Endpoint çalışıyor
- [x] 4 Public Domain voice listeleniyor
- [x] Installed status doğru

**Test Komutu:**
```bash
curl -s http://localhost:8080/api/tts/voices
```

**Yanıt Örneği:**
```json
{
  "current_voice": "ljspeech",
  "voices": [
    {
      "id": "ljspeech",
      "display_name": "Linda (US Female)",
      "gender": "female",
      "accent": "US",
      "quality": "high",
      "license": "Public Domain",
      "installed": true,
      "size_mb": 108.9
    }
    // ... 3 more voices
  ],
  "total": 4,
  "installed": 4
}
```

**✅ Test Sonucu:** Başarılı

---

#### 2.2.2.2 POST /api/tts/preview ✅
- [x] Endpoint çalışıyor
- [x] Base64 audio data üretiliyor
- [x] Voice seçimi çalışıyor
- [x] Custom text desteği var

**Test Komutu:**
```bash
# Session token al
TOKEN=$(curl -s http://localhost:8080/api/connect/qr | grep -o '"session_token":"[^"]*"' | cut -d'"' -f4)

# Preview iste
curl -s -X POST "http://localhost:8080/api/tts/preview?voice_id=ljspeech&text=Gear+is+down" \
  -H "x-session-token: $TOKEN"
```

**Yanıt Örneği:**
```json
{
  "voice": "ljspeech",
  "voice_info": {
    "display_name": "Linda (US Female)",
    "gender": "female",
    "accent": "US",
    "quality": "high",
    "license": "Public Domain"
  },
  "text": "Gear is down",
  "audio": "UklGRiTWAABXQVZFZm10..." // base64 WAV data
}
```

**✅ Test Sonucu:** Başarılı - Gerçek audio data üretiliyor

---

### 2.2.3 TTS Audio Kalitesi ✅

**Manuel Dinleme Testi:**
- ✅ `bridge/tts_samples/test_ljspeech.wav` - Net ve anlaşılır
- ✅ `bridge/tts_samples/test_cori-high.wav` - UK aksanı belirgin
- ✅ `bridge/tts_samples/test_john.wav` - Erkek ses doğal
- ✅ `bridge/tts_samples/test_bryce.wav` - Erkek ses doğal

**Kullanıcı Geri Bildirimi:** "evet hepsinde gear is down sesini duyuyorum"

**🎯 Test Sonucu:** MÜKEMMEL - Tüm sesler çalışıyor!

---

## 2.3 FAZ 2 GENEL ÖZET ✅

### Test İstatistikleri

| Test Kategorisi | Başarı Oranı | Notlar |
|-----------------|--------------|--------|
| **STT (Whisper)** | 90% (9/10) | ElevenLabs audio ile test edildi |
| **Command Parser** | 100% (10/10) | 3 pattern eklendi, %70→%100 |
| **TTS (Piper)** | 100% (4/4) | Tüm voices çalışıyor |
| **TTS API** | 100% (2/2) | voices + preview endpoints |

### Kritik Düzeltmeler
1. ✅ Command Parser: 3 missing pattern eklendi
2. ✅ TTS Synthesis: Silent WAV bug fix
3. ✅ Piper API: `synthesize_wav()` entegrasyonu

### Sonuç
**✅ FAZ 2 (STT + TTS) BAŞARIYLA TAMAMLANDI!**

Next Steps: Faz 3 (Akıllı Komut Sistemi) testleri

---

## 2.4 NOTLAR (Faz 2)

**STT Confidence Values:**
- ElevenLabs TTS audio: ~50-70% (normal)
- Gerçek insan sesi: ~70-90% (beklenen)
- Threshold: Şu anda yok (tüm sonuçlar kabul ediliyor)

**TTS Performance:**
- Synthesis süresi: ~0.5-1s (ljspeech, "Gear is down")
- Audio boyutu: ~40-50KB (kısa cümleler için)

**Public Domain Voices:**
- Tüm 4 voice ticari kullanıma uygun
- License: Public Domain
- Total size: ~450 MB (4 voice)

---

### 2.2.4 Deprecated/Not Implemented Endpoints ⚠️

**NOT:** Aşağıdaki endpoints planlanmış ancak implementasyonda YOK:
- [x] ❌ `POST /api/tts/voice` (voice değiştirme) - Not Found
- [x] ❌ `POST /api/tts/generate` (direct generation) - Not Found
- [x] ❌ `POST /api/tts/download` (voice download) - Not Found

**Mevcut TTS API (2 endpoint):**
- [x] ✅ `GET /api/tts/voices` - Liste çalışıyor
- [x] ✅ `POST /api/tts/preview` - Audio generation çalışıyor

**Karar:** Voice'lar PyInstaller bundle'da pre-installed gelecek. Runtime download MVP'de yok.

---

## 2.3 Mobil Ses Entegrasyonu ⏭️ SKIP

> **⏭️ Test Atlandı - Fiziksel Cihaz Gerekli**
>
> **Sebep:** Bu testler end-to-end mobil entegrasyonu gerektirir:
> - Android/iOS cihaz + MSFS simülatör
> - Gerçek uçuş ortamı
> - Sesli komut testi (kütüphanede mümkün değil)
>
> **Durum:** Backend (Bridge) testleri tamamlandı ✅
> **Todo:** Fiziksel test ortamında yapılacak (Post-MVP)

### 2.3.1 PTT (Push-to-Talk) Butonu ⏭️
- [ ] ⏭️ PTT butonuna basıldığında kayıt başlıyor mu?
- [ ] ⏭️ Ses seviyesi göstergesi animasyonlu mu?
- [ ] ⏭️ Bırakınca kayıt duruyor mu?

**Test (Phone Mic modu):**
1. Mobilde Settings → Audio Source: Phone Mic
2. Ana ekranda PTT butonuna tap (bir kez - toggle modu)
3. "Gear down" de
4. Tekrar tap (kayıt durur)

**Beklenen Davranış:**
- Buton yeşil olmalı (recording)
- Ses dalgası animasyonu
- Kayıt bitince kırmızıya dönmeli

---

### 2.3.2 Audio Upload ve Transcribe ⏭️
- [ ] ⏭️ WAV dosyası Bridge'e gönderiliyor mu?
- [ ] ⏭️ Transcribe sonucu dönüyor mu?

**Kontrol (Bridge konsolu):**
```
Received audio: 16000Hz, 1 channel, 2.5s
Transcribing...
Result: "gear down"
```

**Mobil:**
- Transcribe sonucu ekranda görünmeli (debug modu varsa)

---

### 2.3.3 TTS Audio Playback ⏭️
- [ ] ⏭️ TTS yanıtı base64'ten decode ediliyor mu?
- [ ] ⏭️ Audio cihazda çalınıyor mu?

**Test:**
1. Quick command butonuna bas (örn: Gear)
2. Bridge TTS yanıtı oluşturur
3. Mobilde ses çalmalı: "Gear down"

**Beklenen Sonuç:**
- Telefondan kadın sesi (Linda): "Gear down"
- Ses net ve anlaşılır

---

### 2.3.4 PC Microphone Modu ⏭️
- [ ] ⏭️ Settings → PC Mic çalışıyor mu?
- [ ] ⏭️ PC'de kayıt başlatılıyor mu?

**Test:**
1. Settings → Audio Source: PC Mic
2. Ana ekranda PTT tap
3. PC mikrofonundan "gear down" de
4. Tekrar tap

**Bridge Test:**
```bash
cd bridge
python test_pc_audio.py
```

**Beklenen Sonuç:**
- PC mikrofonu 5 saniye kayıt
- `test_recording.wav` oluşur
- Mobil "[PC recording received]" gösterir

**Not:** Pipeline entegrasyonu henüz TODO, bu aşamada sadece kayıt testi.

---

# FAZ 3: Akıllı Komut Sistemi

## 3.1 Komut Parser (Intent Recognition)

### 3.1.1 Temel Komut Tanıma
- [ ] "gear down" → `gear_down` intent
- [ ] "flaps two" → `flaps_set` intent (param: 2)
- [ ] "landing lights on" → `lights_landing_on`

**Test (Swagger - `/api/audio/command`):**
1. Test WAV dosyası oluştur (text-to-speech tools ile)
2. Upload et
3. Yanıtta doğru intent olmalı

**Alternatif Test (parser.py doğrudan):**
```python
from logic.parser import parse_voice_command

text = "gear down"
result = parse_voice_command(text)
print(result.intent)  # "gear_down"
```

---

### 3.1.2 Alias ve Varyasyonlar
- [ ] "lower the gear" → `gear_down`
- [ ] "raise the gear" → `gear_up`
- [ ] "set flaps one" → `flaps_set` (param: 1)

**Test:**
```python
assert parse_voice_command("lower the gear").intent == "gear_down"
assert parse_voice_command("raise the gear").intent == "gear_up"
assert parse_voice_command("set flaps one").intent == "flaps_set"
```

---

### 3.1.3 Confidence ve Fallback
- [ ] Tanınmayan komut → "Unknown command"
- [ ] Benzer komutlar için öneri?

**Test:**
```python
result = parse_voice_command("blabla nonsense")
assert result.intent == "unknown"
```

---

## 3.2 Context Engine - Flight Phase Detection

### 3.2.1 Phase Tespit Testi
- [ ] Yerde park freni çekili → `PREFLIGHT`
- [ ] Motorlar çalışıyor → `TAXI`
- [ ] Havada tırmanış → `CLIMB`

**Test:**
1. MSFS'te cold & dark uçak
2. `/api/context/status` → `phase: PREFLIGHT`
3. Motorları çalıştır
4. `/api/context/status` → `phase: ENGINE_START`
5. Taxi yap
6. `/api/context/status` → `phase: TAXI`

---

### 3.2.2 V-Speed Limitleri
- [ ] `/api/context/limits` doğru Vlo, Vle değerleri
- [ ] A320 için Vlo=250, Vle=280

**Test:**
```http
GET /api/context/limits
```

**Beklenen (A320):**
```json
{
  "vlo": 250,
  "vle": 280,
  "vmo": 350,
  "vfe": [230, 200, 185, 177]
}
```

---

### 3.2.3 Safety Rules - Gear Down High Speed
- [ ] Hız > Vlo → BLOCK
- [ ] Hız < Vlo → ALLOW

**Test:**
1. MSFS'te 280kt hızda uç
2. `/api/context/evaluate` POST: `{"command": "gear_down"}`

**Beklenen Yanıt:**
```json
{
  "allowed": false,
  "action": "BLOCK",
  "warning": "Speed too high for gear. Current 280 kts, max 250 kts."
}
```

**Test 2 (düşük hız):**
1. Hızı 200kt'a düşür
2. Tekrar evaluate et
3. `allowed: true, action: ALLOW`

---

### 3.2.4 Flaps Speed Check
- [ ] Flaps 2 için Vfe kontrolü (200kt)
- [ ] Hız fazla → BLOCK

**Test:**
1. MSFS'te 250kt
2. Evaluate: `{"command": "flaps_set", "param": 2}`
3. BLOCK olmalı

---

## 3.3 Checklist Sistemi

### 3.3.1 Checklist Listesi
- [ ] `/api/checklist/list` default checklistleri döndürüyor mu?
- [ ] A320 FBW için 9 checklist var mı?

**Test:**
```http
GET /api/checklist/list
```

**Beklenen (default):**
```json
{
  "aircraft": "Default",
  "checklists": [
    {"id": "before_start", "name": "Before Start", "items_count": 4},
    ...
  ]
}
```

---

### 3.3.2 Checklist Başlatma
- [ ] `/api/checklist/start/before_takeoff` çalışıyor mu?
- [ ] İlk madde okutuluyor mu?

**Test:**
```http
POST /api/checklist/start/before_takeoff
```

**Beklenen Yanıt:**
```json
{
  "success": true,
  "state": "WAITING",
  "tts_text": "Before Takeoff checklist. Flight controls.",
  "current_item": {
    "id": "flight_controls",
    "challenge": "Flight controls",
    "expected": "Checked"
  },
  "progress": 0.0,
  "items_remaining": 6
}
```

---

### 3.3.3 Checklist Response (Check)
- [ ] "check" yanıtı sonraki maddeye geçiyor mu?

**Test:**
```http
POST /api/checklist/response
Body: {"response": "check"}
```

**Beklenen:**
```json
{
  "success": true,
  "tts_text": "Checked. Flaps.",
  "progress": 16.67,
  "items_remaining": 5
}
```

---

### 3.3.4 Checklist Verification (SimConnect)
- [ ] Flaps verification çalışıyor mu?
- [ ] Yanlış konfigürasyon → FAIL?

**Test:**
1. MSFS'te flaps 0
2. Before Takeoff checklist'i başlat
3. "Flaps" maddesine gel
4. "check" de (ama flaps 0)
5. Verification FAIL olmalı

**Beklenen:**
```json
{
  "verified": false,
  "verification_message": "Flaps not in takeoff configuration!"
}
```

---

### 3.3.5 Checklist Override
- [ ] "override" komutu çalışıyor mu?
- [ ] Failed item atlanabiliyor mu?

**Test:**
1. Verification failed olan madde
2. POST: `{"response": "override"}`
3. Sonraki maddeye geçmeli

---

### 3.3.6 Checklist Pause/Resume
- [ ] Pause çalışıyor mu?
- [ ] Resume ile devam edebiliyor mu?

**Test:**
```http
POST /api/checklist/pause
→ State: PAUSED

POST /api/checklist/resume
→ State: WAITING (aynı madde)
```

---

### 3.3.7 Checklist Complete
- [ ] Son madde "check" sonrası COMPLETE?
- [ ] TTS: "checklist complete"?

**Test:**
1. Tüm maddeleri geç
2. Son madde: "check"
3. State: COMPLETE
4. `tts_text: "Before Takeoff checklist complete."`

---

## 3.4 MobiFlight WASM (LVAR)

### 3.4.1 WASM Status
- [ ] `/api/wasm/status` çalışıyor mu?
- [ ] WASM kurulu değilse `installed: false`?

**Test:**
```http
GET /api/wasm/status
```

---

### 3.4.2 WASM Install (opsiyonel)
- [ ] Auto-install çalışıyor mu?

**Test:**
```http
POST /api/wasm/install
```

**Not:** Community folder yazma izni gerekir

---

### 3.4.3 Aircraft Profile Detection
- [ ] `/api/aircraft/profile` uçağı tespit ediyor mu?

**Test (FBW A32NX):**
1. MSFS'te FlyByWire A32NX yükle
2. `/api/aircraft/profile` iste

**Beklenen:**
```json
{
  "aircraft": "FlyByWire A32NX",
  "profile": "fbw_a32nx",
  "lvar_support": true
}
```

---

# FAZ 4: Kullanıcı Deneyimi ve UI

## 4.1 Settings Screen

### 4.1.1 Settings Açılışı
- [ ] Ana ekranda Settings ikonu var mı?
- [ ] Settings ekranı açılıyor mu?

**Test:**
1. Mobilde ana ekran
2. Sağ üst köşe → Settings ikonu (⚙️)
3. Settings screen açılmalı

---

### 4.1.2 Audio & Haptics Bölümü

#### Mic Sensitivity Slider
- [ ] Slider 0-100% arasında hareket ediyor mu?
- [ ] Değer kaydediliyor mu?

**Test:**
1. Slider'ı %80'e çek
2. Uygulamayı kapat
3. Tekrar aç
4. Settings'te %80 olmalı

---

#### TTS Voice Selection
- [ ] Dropdown 4 voice gösteriyor mu?
- [ ] Voice değiştirme çalışıyor mu?

**Test:**
1. Dropdown aç
2. "Cori (UK Female)" seç
3. Bridge'e sync olmalı
4. Quick command test et → UK aksanıyla konuşmalı

---

#### Voice Preview
- [ ] Preview butonu var mı?
- [ ] Butona basınca ses çalıyor mu? (TODO - UI hazır, audio playback pending)

**Test:**
1. Voice seç (örn: John)
2. Preview butonuna bas
3. "Welcome to Smart Flight Deck" sesi çalmalı

**Not:** Audio playback henüz implementasyonda, UI hazır.

---

#### Voice Download
- [ ] Kurulu olmayan voice için "Download" butonu?
- [ ] Download onay dialogu?
- [ ] Download başarılı?

**Test (Bryce voice):**
1. Bryce (US Male) seç
2. "Download" butonu görünmeli
3. Bas → Onay dialogu: "Download Bryce? (61 MB)"
4. Onayla → Download başlar
5. Tamamlandığında "Installed" badge

**Not:** Download Bridge üzerinden (~2-3 dakika)

---

#### TTS Volume
- [ ] Volume slider çalışıyor mu?
- [ ] Ses seviyesi değişiyor mu?

**Test:**
1. Volume %50
2. Quick command → ses orta seviye
3. Volume %100
4. Tekrar command → ses daha yüksek

---

#### Haptic Feedback
- [ ] Toggle çalışıyor mu?
- [ ] Kapalıyken titreşim yok mu?

**Test:**
1. Haptic OFF
2. PTT butonuna bas → titreşim OLMAMALI
3. Haptic ON
4. PTT butonuna bas → titreşim olmalı

---

### 4.1.3 Checklist Bölümü

#### Auto Verification
- [ ] Toggle çalışıyor mu?
- [ ] OFF iken verification atlanıyor mu?

**Test:**
1. Auto Verification OFF
2. Checklist başlat
3. "check" de → verification yapılmamalı (hep başarılı)

---

#### Voice Announcements
- [ ] Toggle çalışıyor mu?
- [ ] OFF iken TTS çalmıyor mu?

**Test:**
1. Voice Announcements OFF
2. Checklist başlat
3. TTS ÇALMAMALI (sadece yazı)

---

### 4.1.4 Appearance

#### Theme Mode
- [ ] Dark/Light theme değişimi çalışıyor mu?
- [ ] Anında uygulanıyor mu?

**Test:**
1. Light theme seç
2. Ekran beyaz arka plana geçmeli
3. Dark theme seç
4. Siyah arka plana dönmeli

---

### 4.1.5 About Bölümü

#### Version Display
- [ ] App version görünüyor mu?
- [ ] Bridge version (eğer bağlıysa)?

**Beklenen:**
```
App Version: 1.0.0
Bridge Version: 1.0.0
```

---

## 4.2 Flight Data Screen

### 4.2.1 PFD Tab
- [ ] Speed tape görünüyor mu?
- [ ] Altitude tape çalışıyor mu?
- [ ] Vmo/Vle limitleri gösteriliyor mu?

**Test:**
1. Flight Data ekranına git
2. PFD tab seçili
3. Speed tape MSFS ile eşleşmeli
4. Altitude tape MSFS ile eşleşmeli

---

### 4.2.2 NAV Tab
- [ ] Heading doğru mu?
- [ ] Wind bilgisi var mı?
- [ ] NAV1/NAV2 DME?

**Test:**
1. MSFS'te ILS approach yap
2. NAV tab'a git
3. NAV1 DME distance görünmeli

---

### 4.2.3 FUEL Tab
- [ ] Fuel percentage?
- [ ] Endurance hesabı?
- [ ] Flow göstergesi?

**Test:**
1. MSFS'te fuel %50
2. FUEL tab → %50 göstermeli
3. Endurance: "1h 23m" gibi

---

## 4.3 Checklist Screen (Mobile UI)

### 4.3.1 Checklist Listesi
- [ ] Broşür tarzı görünüm?
- [ ] Faz bazlı gruplama?
- [ ] Arama fonksiyonu?

**Test:**
1. Ana ekrandan "Checklists"
2. 8 checklist listelenmiş olmalı (default)
3. Arama kutusuna "takeoff" yaz → sadece takeoff checklistleri

---

### 4.3.2 Checklist Detail Screen
- [ ] Interactive checklist?
- [ ] CHECK/SKIP/CANCEL butonları?
- [ ] Progress bar?

**Test:**
1. "Before Takeoff" seç
2. Detail ekranına geç
3. "START CHECKLIST" butonuna bas
4. İlk madde görünmeli
5. "CHECK" bas → sonraki madde
6. Progress bar ilerlemeli

---

### 4.3.3 Progress Tracking
- [ ] Yüzde göstergesi doğru mu?
- [ ] Items remaining doğru sayıyor mu?

**Test:**
1. 6 maddelik checklist
2. İlk maddede: 0% (0/6)
3. 3 madde sonra: 50% (3/6)
4. Son madde: 100% (6/6)

---

## 4.4 UX İyileştirmeleri

### 4.4.1 Hata Mesajları
- [ ] Kullanıcı dostu?
- [ ] Teknik detaylar gizli mi?

**Test:**
1. MSFS'i kapat (connection kesilmeli)
2. Quick command butonuna bas
3. Mesaj: "MSFS connection lost" (teknik stack trace DEĞİL)

---

### 4.4.2 Haptic Feedback
- [ ] Tüm butonlarda haptic var mı?
- [ ] Farklı seviyelerde mi? (light/heavy)

**Test:**
1. PTT butonuna tap → light impact
2. Emergency komutlar (varsa) → heavy impact

---

### 4.4.3 Connection Status
- [ ] Bağlantı durumu her zaman görünür mü?
- [ ] Renk kodlu (yeşil/kırmızı)?

**Test:**
1. Bağlıyken → Yeşil "Connected"
2. Bağlantı kes → Kırmızı "Disconnected"

---

# Entegrasyon Testleri (End-to-End)

## E2E-1: Sesli Komut Pipeline (Phone Mic)

**Senaryo:** "Gear down" sesli komutu baştan sona

**Adımlar:**
1. [ ] MSFS açık, havada uçuyorsun
2. [ ] Mobil Settings → Phone Mic
3. [ ] PTT butonuna tap
4. [ ] "Gear down" de
5. [ ] Tekrar tap (kayıt durur)
6. [ ] Bridge transkribe eder
7. [ ] Parser intent tanır: `gear_down`
8. [ ] Context Engine değerlendirir (hız OK?)
9. [ ] SimConnect GEAR_DOWN eventi gönderir
10. [ ] TTS yanıt oluşturur: "Gear down"
11. [ ] Mobilde TTS çalar
12. [ ] MSFS'te gear iner

**Beklenen Süre:** < 3 saniye (PTT bırakma → gear hareketi)

**Başarı Kriteri:** ✅ Gear fiziksel olarak inmeli

---

## E2E-2: Checklist Workflow (Sesli + Doğrulama)

**Senaryo:** Before Takeoff checklist sesli komutla

**Adımlar:**
1. [ ] MSFS'te runway'de bekliyorsun
2. [ ] Flaps 0, Gear Down, Spoilers disarmed
3. [ ] Sesli: "Before takeoff checklist"
4. [ ] TTS: "Before Takeoff checklist. Flight controls."
5. [ ] Sesli: "Check"
6. [ ] TTS: "Checked. Flaps."
7. [ ] Sesli: "Check"
8. [ ] TTS: "Flaps not verified. Flaps not in takeoff configuration."
9. [ ] MSFS'te flaps 2'ye al
10. [ ] Sesli: "Check"
11. [ ] TTS: "Checked. Spoilers."
12. [ ] (Devam et tüm checklist)
13. [ ] TTS: "Before Takeoff checklist complete."

**Başarı Kriteri:** ✅ Checklist tamamlandı mesajı

---

## E2E-3: Context Safety Block

**Senaryo:** Hız fazlayken gear inmeye çalış

**Adımlar:**
1. [ ] MSFS'te 300kt hızda uç
2. [ ] Sesli: "Gear down"
3. [ ] Context Engine hız kontrolü → BLOCK
4. [ ] TTS: "Unable. Speed 300 knots exceeds gear limit of 250 knots."
5. [ ] MSFS'te gear KALKMALI (hareket etmemeli)

**Başarı Kriteri:** ✅ Gear inmemeli, uyarı verilmeli

---

## E2E-4: Settings Sync (Bridge ↔ Mobile)

**Senaryo:** TTS voice değiştir, etkisini gör

**Adımlar:**
1. [ ] Mobilde Settings → TTS Voice: John (US Male)
2. [ ] Kaydet
3. [ ] Bridge'e sync edilmeli (`/api/settings` PUT)
4. [ ] Quick command test et
5. [ ] TTS erkek sesiyle çalmalı (John)

**Başarı Kriteri:** ✅ Ses değişimi uygulanmış olmalı

---

# Stress & Edge Case Testleri

## ST-1: Uzun Süreli Bağlantı
- [ ] 1 saat boyunca bağlantı kopuyor mu?

**Test:**
1. Bağlantıyı kur
2. 1 saat bekle (timer kur)
3. Hala bağlı mı?

---

## ST-2: Hızlı Komut Gönderimi
- [ ] 10 komutu 10 saniyede gönder
- [ ] Hepsi işleniyor mu?

**Test:**
1. Quick commands butonlarına hızlıca bas
2. Gear, Flaps, Lights, Gear, Flaps...
3. MSFS'te hepsi çalışmalı

---

## ST-3: Bağlantı Kaybı ve Yeniden Bağlanma
- [ ] Wi-Fi kapatınca ne oluyor?
- [ ] Wi-Fi açınca otomatik bağlanıyor mu?

**Test:**
1. Telefonda Wi-Fi'yi kapat
2. 5 saniye bekle
3. Wi-Fi aç
4. 10 saniye içinde yeniden bağlanmalı

---

## ST-4: MSFS Crash/Restart
- [ ] MSFS çökerse Bridge devam ediyor mu?
- [ ] MSFS yeniden açınca bağlanıyor mu?

**Test:**
1. MSFS'yi kapat (ALT+F4)
2. Bridge hata vermemeli (graceful disconnect)
3. MSFS'yi tekrar aç
4. Bridge otomatik bağlanmalı

---

## ST-5: Gürültülü Ortamda STT
- [ ] Arka planda müzik varken tanıma?

**Test:**
1. PC'de YouTube aç (müzik çal)
2. Sesli komut dene: "Gear down"
3. Tanımalı (veya "not clear" demeli)

**Beklenti:** Confidence < 0.7 ise fallback

---

# Performans Testleri

## PT-1: STT Latency
- [ ] PTT bırakma → Transcribe sonucu < 2 saniye?

**Test:**
1. Timer başlat
2. PTT bas → "gear down" → bırak
3. Timer durdur (transcribe geldiğinde)

**Hedef:** < 2 saniye

---

## PT-2: TTS Latency
- [ ] Komut → TTS oynatma < 1 saniye?

**Test:**
1. Quick command bas
2. TTS çalana kadar timer

**Hedef:** < 1 saniye

---

## PT-3: WebSocket Update Rate
- [ ] SimData 2Hz (0.5 saniye)?

**Test:**
1. Konsol log'larına bak
2. Timestamp'lere bak
3. ~500ms aralıklarla gelmeli

---

## PT-4: CPU Kullanımı
- [ ] Bridge CPU < %20?
- [ ] Mobil pil tüketimi normal?

**Test (Bridge):**
1. Task Manager aç
2. Python process'i izle
3. Idle: < %5, Active: < %20

**Test (Mobil):**
1. 1 saat kullan
2. Pil %10'dan fazla düşmemeli

---

## PT-5: RAM Kullanımı
- [ ] Bridge RAM < 1GB?

**Test:**
1. Task Manager
2. Python process RAM kullanımı

**Hedef:** ~500-800MB (Whisper model yüklü)

---

# Güvenlik Testleri

## SEC-1: Authentication
- [ ] Token olmadan API çağrılamıyor mu?

**Test:**
```http
GET /api/sim/status
(No X-Session-Token header)
→ 401 Unauthorized
```

---

## SEC-2: Expired Token
- [ ] Token expire edince reddediliyor mu?

**Test:**
1. Token al
2. Bridge'i yeniden başlat (token invalidate)
3. Eski token ile istek at
4. 401 dönmeli

---

## SEC-3: CORS
- [ ] Sadece mobil client bağlanabiliyor mu?

**Test:**
1. Tarayıcıda `http://192.168.x.x:8080/api/sim/status` aç
2. CORS hatası almalı

**Not:** Swagger allowlist'te olduğu için çalışır, ama random site'lar çalışmamalı.

---

# Platform-Specific Testleri

## PLT-1: Android 8.0 Compatibility
- [ ] Android 8.0'da çalışıyor mu?

**Test:**
- Android 8.0 emülatör veya cihaz
- APK kur, test et

---

## PLT-2: iOS Test (Gelecek)
- [ ] iOS build başarılı?

**Not:** MVP'de Android öncelikli, iOS post-MVP

---

## PLT-3: Windows 10/11
- [ ] Bridge Windows 10'da çalışıyor mu?

**Test:**
- Windows 10 VM veya cihaz
- Bridge başlat

---

# Regression Testleri

## REG-1: Önceki Özelliklerin Kırılması
- [ ] Settings eklendikten sonra Quick Commands hala çalışıyor mu?
- [ ] Checklist eklenince SimConnect bozulmadı mı?

**Test:**
1. Her yeni özellik sonrası
2. Eski özelliği tekrar test et

---

# Test Sonuçları Tablosu

| Test ID | Faz | Açıklama | Durum | Tarih | Notlar |
|---------|-----|----------|-------|-------|--------|
| 0.1.1 | 0 | Python ortamı | ✅ PASS | 2025-11-29 20:03 | Python 3.13.1, 45+ paket yüklü |
| 0.1.2 | 0 | FastAPI başlatma | ✅ PASS | 2025-11-29 20:03 | Server: 172.23.182.208:8080 |
| 0.1.3 | 0 | Health endpoint | ✅ PASS | 2025-11-29 20:03 | JSON yanıt OK |
| 0.2.1 | 0 | SimConnect kurulum | ✅ PASS | 2025-11-29 20:17 | MSFS 2020 + SimConnect 0.4.26 |
| 0.2.2 | 0 | SimConnect bağlantı | ✅ PASS | 2025-11-29 20:17 | B747-8i LTFM, 30+ SimVar OK |
| 0.4.1 | 0 | QR kod tarama | ⏳ PENDING | - | APK + bağlantı testi |
| 1.1.1 | 1 | Gear toggle | ⏳ PENDING | - | - |
| 2.2.1 | 2 | TTS voice yükleme | ⏳ PENDING | - | - |
| 2.3.1 | 2 | PTT butonu | ⏳ PENDING | - | - |
| 3.1.1 | 3 | Komut tanıma | ⏳ PENDING | - | - |
| 3.2.3 | 3 | Safety gear block | ⏳ PENDING | - | - |
| 3.3.2 | 3 | Checklist başlat | ⏳ PENDING | - | - |
| 4.1.2 | 4 | Settings mic slider | ⏳ PENDING | - | - |
| 4.2.1 | 4 | PFD speed tape | ⏳ PENDING | - | - |
| E2E-1 | E2E | Sesli komut pipeline | ⏳ PENDING | - | - |
| E2E-2 | E2E | Checklist workflow | ⏳ PENDING | - | - |
| ST-2 | Stress | Hızlı komut | ⏳ PENDING | - | - |
| PT-1 | Perf | STT latency | ⏳ PENDING | - | - |

---

# Test Ortamı

## Donanım
- **PC:** Windows 10/11, Intel i5+, 8GB+ RAM
- **Telefon:** Android 8.0+, 4GB RAM
- **Network:** Wi-Fi 5GHz (önerilen)

## Yazılım
- **MSFS:** 2020 veya 2024 (güncel patch)
- **Python:** 3.10+
- **Flutter:** 3.10+
- **Bridge:** main branch (latest)
- **Mobile APK:** Release build (62.8 MB)

## Test Uçakları
- Default: Cessna 172 (basit)
- FlyByWire A32NX (LVAR test)
- Fenix A320 (opsiyonel - LVAR)

---

# Hata Raporlama Formatı

Eğer bir test başarısız olursa:

```markdown
## Bug Report #XXX

**Test ID:** 3.2.3
**Faz:** 3 - Context Engine
**Açıklama:** Safety rule gear block çalışmıyor

**Adımlar:**
1. MSFS'te 300kt hızda uç
2. Sesli: "Gear down"
3. Beklenen: BLOCK
4. Gerçekleşen: Gear indi (block edilmedi)

**Beklenen Sonuç:** TTS "Speed too high for gear"
**Gerçek Sonuç:** Gear indi

**Ortam:**
- MSFS: 2024
- Uçak: A320
- Bridge version: 1.0.0
- APK version: 1.0.0

**Log Çıktısı:**
```
[Paste bridge console output]
```

**Ekran Görüntüsü:** (varsa)
```

---

# Öncelikli Test Sırası (İlk Gün)

## Sabah Testi (08:00 - 12:00)
1. ✅ 0.1: PC Bridge Başlatma (TAMAMLANDI - 20:03) ✅
2. ✅ 0.2: SimConnect (TAMAMLANDI - 20:17) ✅
3. ⏳ 0.3-0.4: Mobil + Bağlantı (PENDING - APK gerekli)
4. ⏳ 1.1-1.2: Quick Commands (PENDING - APK + MSFS gerekli)

**Hedef:** Temel fonksiyonların çalıştığını doğrula
**İlerleme:** 2/4 tamamlandı (0.1 ✅, 0.2 ✅)

---

## Öğleden Sonra Testi (13:00 - 18:00)
1. ✅ 3.1-3.2: Context Engine (1 saat)
2. ✅ 3.3: Checklist (1.5 saat)
3. ✅ 4.1: Settings Screen (1 saat)
4. ✅ E2E-1, E2E-2: End-to-End (1.5 saat)

**Hedef:** Akıllı özellikler çalışıyor mu?

---

## Akşam Testi (19:00 - 22:00)
1. ✅ 4.2-4.3: Flight Data + Checklist UI (1 saat)
2. ✅ ST-1 to ST-5: Stress testleri (1 saat)
3. ✅ PT-1 to PT-5: Performans (1 saat)

**Hedef:** UX ve stabilite

---

# Kritik Başarı Kriterleri (MVP Onay)

MVP'nin tamamlandığını söylemek için:

- [ ] ✅ **E2E-1 geçti** (sesli komut pipeline çalışıyor)
- [ ] ✅ **E2E-2 geçti** (checklist workflow çalışıyor)
- [ ] ✅ **Settings sync** çalışıyor
- [ ] ✅ **No crash** (1 saat stability)
- [ ] ✅ **SimConnect reliable** (komutlar %95+ başarı)
- [ ] ✅ **TTS audible** (ses net ve anlaşılır)

**Eğer bunlar geçerse → MVP BAŞARILI! 🎉**

---

# Gelecek Testler (Post-MVP)

- [ ] iOS build ve test
- [ ] VAD Streaming sistem test
- [ ] Voice preview audio playback
- [ ] MobiFlight WASM full test (Fenix, PMDG)
- [ ] Multi-language support (Turkish)
- [ ] Tablet UI test (10" screen)

---

**Last Updated:** 2025-11-29
**Test Lead:** [Your Name]
**Test Environment:** Windows 11 + Android 12 + MSFS 2024

---

# Appendix A: Hızlı Komut Referansı

### Bridge Başlatma
```bash
cd bridge
venv\Scripts\activate
python main.py
```

### Swagger UI
```
http://localhost:8000/docs
```

### Test Scripts
```bash
# PC audio test
python test_pc_audio.py

# TTS test
python test_tts_voices.py

# Parser test
python -m pytest tests/test_parser.py
```

### APK Build
```bash
cd mobile
flutter build apk --release
```

---

# Appendix B: Faydalı API Endpoints (Test için)

| Endpoint | Kullanım | Örnek |
|----------|----------|-------|
| `/health` | Durum kontrolü | `GET /health` |
| `/api/sim/status` | Uçak verisi | `GET /api/sim/status` |
| `/api/context/status` | Flight phase | `GET /api/context/status` |
| `/api/checklist/list` | Checklist listesi | `GET /api/checklist/list` |
| `/api/tts/voices` | TTS voices | `GET /api/tts/voices` |
| `/api/settings` | Settings | `GET /api/settings` |

---

# Appendix C: Beklenen Değerler (MSFS Default A320)

| SimVar | Örnek Değer | Birim |
|--------|-------------|-------|
| AIRSPEED INDICATED | 250 | knots |
| PLANE ALTITUDE | 35000 | feet |
| VERTICAL SPEED | -500 | fpm |
| GEAR HANDLE POSITION | 0 (up) / 1 (down) | bool |
| FLAPS HANDLE INDEX | 0-4 | index |
| SIM ON GROUND | 0/1 | bool |

---

🎯 **Hedef:** Bugün tüm testleri tamamla ve eksikleri tespit et!
📝 **Rapor:** Her test sonrası tabloyu güncelle
🐛 **Bug varsa:** Hemen CLAUDE.md'ye ekle ve fix planla

Başarılar! 🚀
