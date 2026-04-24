# Block Blast! 9.7.2 — Full Decompilation Analysis

This document lists **every feature and detail** found by decompiling the XAPK
`Block Blast!_9.7.2_APKPure.xapk` with BBOverLoad (apktool 2.9.3 + jadx 1.4.7).

---

## Table of Contents

1. [XAPK / Package Overview](#1-xapk--package-overview)
2. [Split APK Structure](#2-split-apk-structure)
3. [Permissions](#3-permissions)
4. [Android Manifest — Activities](#4-android-manifest--activities)
5. [Android Manifest — Services](#5-android-manifest--services)
6. [Android Manifest — Broadcast Receivers](#6-android-manifest--broadcast-receivers)
7. [Android Manifest — Content Providers](#7-android-manifest--content-providers)
8. [Application Attributes](#8-application-attributes)
9. [Game Engine & Technology Stack](#9-game-engine--technology-stack)
10. [Native Libraries (arm64-v8a)](#10-native-libraries-arm64-v8a)
11. [Third-Party SDKs & Libraries](#11-third-party-sdks--libraries)
12. [Monetisation & Advertising SDKs](#12-monetisation--advertising-sdks)
13. [Analytics & Attribution SDKs](#13-analytics--attribution-sdks)
14. [In-App Purchase (Billing)](#14-in-app-purchase-billing)
15. [Networking & Security](#15-networking--security)
16. [Resources Overview](#16-resources-overview)
17. [Internationalisation (i18n)](#17-internationalisation-i18n)
18. [Home-Screen Widget](#18-home-screen-widget)
19. [Push Notifications (FCM)](#19-push-notifications-fcm)
20. [Ad-Related Configuration](#20-ad-related-configuration)
21. [Game-Specific Configuration Files](#21-game-specific-configuration-files)
22. [Smali / DEX Breakdown](#22-smali--dex-breakdown)
23. [Assets Structure](#23-assets-structure)
24. [Key String Resources](#24-key-string-resources)
25. [How to Make Changes and Recompile](#25-how-to-make-changes-and-recompile)

---

## 1. XAPK / Package Overview

| Field | Value |
|---|---|
| App name | **Block Blast!** |
| Package name | `com.block.juggle` |
| Version name | **9.7.2** |
| Version code | **9720** |
| XAPK version | 2 |
| Minimum SDK | **23** (Android 6.0 Marshmallow) |
| Target SDK | **35** (Android 15) |
| Compile SDK | 35 (Android 15) |
| App category | `game` |
| Total XAPK size | ≈ 225 MB |
| Source | APKPure |

---

## 2. Split APK Structure

The XAPK contains **5 APK splits** and a metadata icon:

| File | Size | ID | Purpose |
|---|---|---|---|
| `com.block.juggle.apk` | 171 MB | `base` | Main application code, resources, assets |
| `config.arm64_v8a.apk` | 64 MB | `config.arm64_v8a` | Native `.so` libraries for ARM64 devices |
| `config.en.apk` | 86 KB | `config.en` | English language resources |
| `config.mdpi.apk` | 192 KB | `config.mdpi` | Medium-density (mdpi) drawable resources |
| `gamedatalib.apk` | 17 KB | `gamedatalib` | Play Asset Delivery install-time asset pack |
| `icon.png` | 48 KB | — | Launcher icon (used by APKPure / XAPK installer) |

> **`gamedatalib`** is a Play Asset Delivery **install-time** module
> (`dist:type="asset-pack"`, `dist:install-time`).  It has no Java code
> (`android:hasCode="false"`).

---

## 3. Permissions

### Dangerous / Sensitive

| Permission | Reason |
|---|---|
| `CAMERA` | Photo-picker / profile picture feature |
| `WRITE_EXTERNAL_STORAGE` | Legacy storage write (API < 29) |
| `READ_EXTERNAL_STORAGE` | Legacy storage read (API < 33) |
| `READ_MEDIA_IMAGES` | Scoped media access (API ≥ 33) |
| `READ_MEDIA_VISUAL_USER_SELECTED` | Fine-grained photo access (API ≥ 34) |
| `POST_NOTIFICATIONS` | Push notification opt-in (API ≥ 33) |

### Normal / System

| Permission | Reason |
|---|---|
| `INTERNET` | All network communication |
| `ACCESS_NETWORK_STATE` | Check connectivity before requests |
| `ACCESS_WIFI_STATE` | Wi-Fi info for analytics |
| `WAKE_LOCK` | Keep CPU awake during downloads / video ads |
| `VIBRATE` | Haptic feedback in-game |
| `FOREGROUND_SERVICE` | Background download / data service |
| `REORDER_TASKS` | Bring task to front (ad deep-links) |

### Ad Services (Privacy Sandbox)

| Permission |
|---|
| `ACCESS_ADSERVICES_TOPICS` |
| `ACCESS_ADSERVICES_ATTRIBUTION` |
| `ACCESS_ADSERVICES_CUSTOM_AUDIENCE` |
| `ACCESS_ADSERVICES_AD_ID` |
| `com.google.android.gms.permission.AD_ID` |

### Billing & Play

| Permission |
|---|
| `com.android.vending.BILLING` |
| `com.google.android.finsky.permission.BIND_GET_INSTALL_REFERRER_SERVICE` |

### Ad Network Custom

| Permission |
|---|
| `com.applovin.array.apphub.permission.BIND_APPHUB_SERVICE` |
| `com.google.android.c2dm.permission.RECEIVE` |
| `com.block.juggle.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION` |

---

## 4. Android Manifest — Activities (96 total)

### Game Activities

| Class | Purpose |
|---|---|
| `org.cocos2dx.javascript.AppActivity` | **Main launcher activity** – Cocos2d-x game surface |
| `org.cocos2dx.javascript.JfeedbackActivity` | In-game feedback / rating dialog |
| `org.cocos2dx.javascript.season.SeasonActivity` | Seasonal event screen |
| `org.cocos2dx.javascript.MoreSettingActivity` | Extended settings screen |
| `org.cocos2dx.javascript.fillad.FillAdActivity` | Ad fill / house-ad display |
| `org.cocos2dx.javascript.image.picker.PhotoPickerActivity` | Photo picker (profile/avatar) |
| `org.cocos2dx.javascript.image.crop.BottomCropActivity` | Image cropping |
| `org.cocos2dx.javascript.image.gallery.CustomGalleryActivity` | Custom gallery browser |
| `org.cocos2dx.javascript.h5.HsWebActivity` | In-game HTML5 web view |
| `org.cocos2dx.javascript.h5.TikTokAuthCallbackActivity` | TikTok OAuth callback |
| `com.mikepenz.aboutlibraries.ui.LibsActivity` | Open-source licenses screen |

### Ad Network Activities (85 total from various SDKs)

Includes activities from: Vungle, Moloco, Facebook Audience Network, PubMatic,
IronSource, Unity Ads, AppLovin MAX, InMobi, ByteDance (TikTok/Pangle),
Amazon APS, Fyber/Digital Turbine, Bigo Ads, Ogury, and Google AdMob.

---

## 5. Android Manifest — Services (17 total)

| Class | Purpose |
|---|---|
| `org.cocos2dx.javascript.google.MyFirebaseMessagingService` | Custom FCM handler (push notifications) |
| `com.appsflyer.FirebaseMessagingServiceListener` | AppsFlyer FCM forwarding |
| `com.google.android.gms.measurement.AppMeasurementService` | Firebase Analytics background service |
| `com.google.android.gms.measurement.AppMeasurementJobService` | Firebase Analytics job scheduler |
| `com.google.firebase.components.ComponentDiscoveryService` | Firebase SDK initialisation |
| `com.google.firebase.messaging.FirebaseMessagingService` | Firebase Cloud Messaging |
| `com.google.android.gms.ads.AdService` | Google Mobile Ads background service |
| `com.bytedance.sdk.openadsdk.multipro.aidl.BinderPoolService` | Pangle (ByteDance) multi-process ad service |
| `androidx.work.impl.background.systemalarm.SystemAlarmService` | WorkManager alarm-based scheduler |
| `androidx.work.impl.background.systemjob.SystemJobService` | WorkManager job scheduler |
| `androidx.work.impl.foreground.SystemForegroundService` | WorkManager foreground service |
| `com.applovin.impl.adview.activity.FullscreenAdService` | AppLovin fullscreen ad service |
| `com.google.android.datatransport.runtime.*` (×2) | Firebase data transport |
| `androidx.camera.core.impl.MetadataHolderService` | CameraX metadata holder |
| `androidx.room.MultiInstanceInvalidationService` | Room database multi-process sync |
| `com.google.android.gms.auth.api.signin.RevocationBoundService` | Google Sign-In token revocation |

---

## 6. Android Manifest — Broadcast Receivers (22 total)

| Class | Purpose |
|---|---|
| `com.appsflyer.SingleInstallBroadcastReceiver` | AppsFlyer install referrer |
| `org.cocos2dx.javascript.google.NotificationDeletedReceiver` | FCM notification dismiss handler |
| `org.cocos2dx.javascript.widget.HsSmallWidget` | Home-screen small widget provider |
| `org.cocos2dx.javascript.widget.HsMediumWidget` | Home-screen medium widget provider |
| `org.cocos2dx.javascript.widget.HsWidgetBroadcastReceiver` | Widget click/update events |
| `cn.hsdata.android.TDReceiver` | ThinkingData analytics receiver |
| `cn.thinkingdata.android.TDReceiver` | ThinkingData analytics receiver (alias) |
| `com.google.android.gms.measurement.AppMeasurementReceiver` | Firebase Analytics |
| `com.google.firebase.iid.FirebaseInstanceIdReceiver` | FCM token refresh |
| `com.facebook.CurrentAccessTokenExpirationBroadcastReceiver` | Facebook token expiry |
| `com.facebook.AuthenticationTokenManager$CurrentAuthenticationTokenChangedBroadcastReceiver` | Facebook auth token change |
| `androidx.work.impl.*` (×6) | WorkManager constraint/reschedule receivers |
| `androidx.profileinstaller.ProfileInstallReceiver` | Baseline profile installation |
| `com.google.android.datatransport.runtime.scheduling.jobscheduling.AlarmManagerSchedulerBroadcastReceiver` | Firebase transport scheduler |
| `com.ogury.core.internal.LogEnablerReceiver` | Ogury SDK debug logging |

---

## 7. Android Manifest — Content Providers (15 total)

| Class | Purpose |
|---|---|
| `org.cocos2dx.javascript.cross.CrossPromotionDataProvider` | In-game cross-promotion content |
| `com.hs.adx.helper.CrossPromotionProvider` | Ad network cross-promotion data |
| `androidx.core.content.FileProvider` | Secure file sharing (images/screenshots) |
| `androidx.startup.InitializationProvider` | App Startup library initialiser |
| `com.applovin.sdk.AppLovinInitProvider` | AppLovin MAX auto-initialisation |
| `com.facebook.ads.AudienceNetworkContentProvider` | Facebook Audience Network init |
| `com.facebook.internal.FacebookInitProvider` | Facebook SDK auto-init |
| `com.google.firebase.provider.FirebaseInitProvider` | Firebase auto-init |
| `com.google.android.gms.ads.MobileAdsInitProvider` | Google Mobile Ads auto-init |
| `com.vungle.ads.VungleProvider` | Vungle SDK init |
| `com.ironsource.lifecycle.IronsourceLifecycleProvider` | IronSource lifecycle tracking |
| `com.ironsource.lifecycle.LevelPlayActivityLifecycleProvider` | LevelPlay lifecycle tracking |
| `com.bugsnag.android.internal.BugsnagContentProvider` | Bugsnag crash reporter init |
| `com.squareup.picasso.PicassoProvider` | Picasso image loader init |
| `sg.bigo.ads.controller.provider.BigoAdsProvider` | Bigo Ads SDK init |

---

## 8. Application Attributes

| Attribute | Value | Notes |
|---|---|---|
| `android:name` | `com.netease.nis.wrapper.MyApplication` | Custom Application class (NetEase NIS security wrapper) |
| `android:label` | `@string/app_name` → **"Block Blast!"** | |
| `android:icon` | `@mipmap/ic_launcher` | |
| `android:allowBackup` | `true` | |
| `android:allowNativeHeapPointerTagging` | `false` | ARM MTE disabled (stability) |
| `android:appCategory` | `game` | |
| `android:appComponentFactory` | `androidx.core.app.CoreComponentFactory` | |
| `android:extractNativeLibs` | `false` | Libraries are page-aligned, not extracted |
| `android:fullBackupContent` | `@xml/appsflyer_backup_rules` | AppsFlyer-managed backup exclusions |
| `android:hardwareAccelerated` | `true` | GPU rendering |
| `android:largeHeap` | `true` | Requests expanded heap for game assets |
| `android:networkSecurityConfig` | `@xml/network_security_config` | Cleartext allowed on all domains |
| `android:persistent` | `false` | |
| `android:supportsRtl` | `true` | RTL layout support |
| `android:usesCleartextTraffic` | `true` | Plain HTTP allowed |

---

## 9. Game Engine & Technology Stack

| Component | Detail |
|---|---|
| **Game Engine** | **Cocos2d-x** (JavaScript binding variant — `cocos2d-jsb`) |
| **Scripting** | JavaScript via Cocos2d JSB (`org.cocos2dx.javascript` package) |
| **Rendering** | OpenGL ES 2.0 (`android:glEsVersion="0x00020000"`) |
| **Native Engine Library** | `libcocos2djs.so` |
| **JS Runtime** | Hermes (`libhermes.so`, `libhermestooling.so`) and JSC tooling (`libjsctooling.so`) |
| **React Native** | React Native runtime (`libreactnative.so`, `libjsi.so`) — used for UI/ad overlays |
| **Application wrapper** | `com.netease.nis.wrapper.MyApplication` — NetEase NIS anti-cheat/security |
| **Hot-Update** | `mbh-hotupdate.7ea21.js` — custom MBH hot-update module (JS code updates without store release) |
| **Data serialisation** | ProtoBuf (`HSAnalytics.proto`, `client_analytics.proto`, `messaging_event.proto`) |
| **Image loading** | Glide (`libglide-webp.so`), Picasso, Fresco (`libimagepipeline.so`) |
| **Key-value storage** | MMKV (`libmmkv.so`) |
| **Kotlin coroutines** | `_COROUTINE` package present; Kotlin stdlib |
| **WorkManager** | Background task scheduling |
| **Room** | Local SQLite ORM |
| **CameraX** | `androidx.camera` — for photo-picker feature |

---

## 10. Native Libraries (arm64-v8a)

All 31 `.so` files from `config.arm64_v8a.apk`:

| Library | Origin / Purpose |
|---|---|
| `libcocos2djs.so` | Cocos2d-x JavaScript engine — **core game engine** |
| `libhermes.so` | Facebook Hermes JS engine |
| `libhermestooling.so` | Hermes tooling/profiling |
| `libjsi.so` | React Native JSI bridge |
| `libreactnative.so` | React Native core native library |
| `libjsctooling.so` | JavaScriptCore tooling |
| `libfbjni.so` | Facebook JNI helpers |
| `libmmkv.so` | Tencent MMKV key-value store |
| `libc++_shared.so` | LLVM C++ standard library (shared) |
| `libimagepipeline.so` | Facebook Fresco image pipeline |
| `libnative-filters.so` | Fresco native image filters |
| `libnative-imagetranscoder.so` | Fresco image transcoding |
| `libimage_processing_util_jni.so` | Image processing utilities |
| `libsurface_util_jni.so` | Surface/view utilities |
| `libglide-webp.so` | Glide WebP decoder |
| `libnesec.so` | NetEase NIS security / anti-cheat |
| `libnesec-x86.so` | NetEase NIS (x86 compat shim in arm64 APK) |
| `libnms.so` | NetEase NMS (network/messaging security) |
| `libpglarmor.so` | PGL Armour anti-tampering |
| `libbuffer_pgl.so` | PGL buffer security |
| `libfile_lock_pgl.so` | PGL file lock |
| `libtask.so` | Task / scheduling native helper |
| `libtobEmbedPagEncrypt.so` | ByteDance/TikTok Pangle encryption |
| `libtt_ugen_layout.so` | TikTok/ByteDance native ad layout |
| `libxquic_bridge.so` | XQUIC (Alibaba QUIC implementation) — CDN acceleration |
| `libapplovin-native-crash-reporter.so` | AppLovin crash reporter |
| `libapminsighta.so` | APM Insight monitoring (A) |
| `libapminsightb.so` | APM Insight monitoring (B) |
| `libbugsnag-ndk.so` | Bugsnag NDK crash handler |
| `libbugsnag-plugin-android-anr.so` | Bugsnag ANR detection |
| `libbugsnag-root-detection.so` | Bugsnag root detection |

---

## 11. Third-Party SDKs & Libraries

### UI & Animation
| SDK | Package |
|---|---|
| Lottie | `com.airbnb.lottie` |
| Glide | `com.bumptech.glide` |
| Picasso | `com.squareup.picasso` |
| Coil | `coil` |
| Material Design (MDC) | `com.google.android.material` |
| AppCompat / AndroidX | `androidx.*` |

### Networking
| SDK | Package |
|---|---|
| OkHttp | `okhttp3` |
| Retrofit | `retrofit2` |
| Volley | `com.android.volley` |
| Cronet (Play Services) | `org.chromium.net` |
| XQUIC | `libxquic_bridge.so` |
| Axios (JS) | `assets/src/assets/libs/axios.min.js` |

### Storage
| SDK | Package |
|---|---|
| MMKV | `libmmkv.so` |
| Room | `androidx.room` |
| JSZip (JS) | `assets/src/assets/libs/jszip.min.js` |

### Crash Reporting
| SDK | Package |
|---|---|
| Bugsnag | `com.bugsnag.android` |

### Security / Anti-Cheat
| SDK | Notes |
|---|---|
| NetEase NIS | `libnesec.so`, `libnms.so` — anti-tamper, integrity checks |
| PGL Armour | `libpglarmor.so`, `libbuffer_pgl.so`, `libfile_lock_pgl.so` |
| SafeDK | `com.safedk` — SDK safety/compliance checks |

### Utility
| SDK | Package |
|---|---|
| Kotlin stdlib + coroutines | `kotlin`, `kotlinx` |
| ReactiveX | `io.reactivex` |
| Guava | `com.google.common` |
| AutoValue | `com.google.auto.value` |
| About Libraries | `com.mikepenz.aboutlibraries` |
| Yalantis UCrop | `com.yalantis` |
| dnsjava | `org.xbill.DNS` |
| SLF4J | `org.slf4j` |
| CheckerFramework | `org.checkerframework` |

---

## 12. Monetisation & Advertising SDKs

The game uses **AppLovin MAX** as its mediation layer on top of many demand partners:

| SDK | Package / Library | Format Support |
|---|---|---|
| **AppLovin MAX (mediation)** | `com.applovin` | Banner, Interstitial, Rewarded, MREC |
| **Google AdMob / GAM** | `com.google.android.gms.ads` | Banner, Interstitial, Rewarded, Native |
| **Facebook Audience Network** | `com.facebook.ads` | Banner, Interstitial, Rewarded, Native |
| **Unity Ads** | `com.unity3d.ads`, `com.unity3d.services` | Interstitial, Rewarded |
| **IronSource / LevelPlay** | `com.ironsource` | Interstitial, Rewarded, Banner |
| **Pangle (ByteDance / TikTok)** | `com.bytedance.sdk.openadsdk` | Interstitial, Rewarded, Full-screen video |
| **Vungle / Liftoff Monetize** | `com.vungle.ads` | Interstitial, Rewarded |
| **Amazon Publisher Services (APS)** | `com.amazon.device.ads`, `com.amazon.aps` | Banner, Interstitial |
| **InMobi** | `com.inmobi.ads` | Interstitial, Native |
| **Moloco** | `com.moloco.sdk` | Interstitial, VAST video |
| **PubMatic** | `com.pubmatic.sdk` | Banner, Interstitial |
| **Bigo Ads** | `sg.bigo.ads` | Interstitial, Rewarded, Splash |
| **Fyber / Digital Turbine** | `com.fyber.inneractive`, `com.digitalturbine` | Interstitial, Rewarded |
| **Ogury** | `com.ogury.ad` | Interstitial |
| **ADQ / Hella** | `com.hs.adx`, `com.adq.sdk` | Interstitial, Rewarded (house ad) |
| **Reklamup** | `com.reklamup` | Banner, Interstitial |
| **ADQuality** | `adquality` | Ad quality monitoring |
| **OMSDK** | `assets/ad-viewer/omsdk-v1.js` | Open Measurement viewability |

### ECPM Floor Configuration (per-country)

`assets/ecpmconfig/` contains **23 per-country JSON files** controlling ad floor
prices by ad unit and session-depth tier (interstitial / rewarded).
Countries covered: AU, BE, BR, CA, DE, ES, FR, GB, ID, IN, IT, JP, KR, MX,
NL, PH, PL, RU, TH, TR, TW, US, **others**.

Example structure (US):
```
"bx5722" → is (interstitial): $5.00 floor at 2nd impression, down to $2.00+
           → rv (rewarded):   $10.00 floor at 1st impression, down to $3.50+
```

### Corridor Map (Ad Frequency Caps)

`assets/corridormapconfig/` — **11 JSON files** configure per-user corridor
segments by country and ad-waterfall ID.  Each corridor has time-window floors
(`in_24h`, `24_168h`, `168_744h`, `out_744h`) with eCPM gates.

---

## 13. Analytics & Attribution SDKs

| SDK | Package | Key IDs found in strings.xml |
|---|---|---|
| **AppsFlyer** | `com.appsflyer` | Dev key: `M9jeZtZDFEpp3XpimBKXC6` |
| **Firebase Analytics** | `com.google.firebase` | Project: `blockjuggledevsite` |
| **ThinkingData** | `cn.thinkingdata.android` | App ID: `c34f7c8cc9e54d688b2db32dd3c72284`, mode: NORMAL, timezone: GMT+0 |
| **Google Sign-In** | `com.google.android.gms.auth.api.signin` | OAuth client: `249091862244-56935578l6r72camqr2nv57ck69v1ih8.apps.googleusercontent.com` |
| **Facebook SDK** | `com.facebook` | App ID: `1576913169390778` |
| **TikTok / ByteDance** | `com.tiktok` | TikTok OAuth callback activity present |
| **APM Insight** | `com.apm.insight` | Performance monitoring |

---

## 14. In-App Purchase (Billing)

- **Google Play Billing Library** version **7.0.0**
- Two proxy activities for billing flow:
  - `com.android.billingclient.api.ProxyBillingActivity`
  - `com.android.billingclient.api.ProxyBillingActivityV2`
- The game uses `BILLING` permission and calls the Play Billing client for
  IAP products (cosmetics, boosters, premium passes, etc.)

---

## 15. Networking & Security

### Network Security Config (`res/xml/network_security_config.xml`)

- **Cleartext traffic permitted globally** (`cleartextTrafficPermitted="true"`)
- User-installed CAs trusted in **debug** builds
- System CAs trusted in release
- Unity Ads CDN domains explicitly whitelisted for cleartext:
  - `cdn-creatives-akamai-prd.unityads.unity3d.com`
  - `cdn-creatives-akamaistls-prd.unityads.unity3d.com`
  - `cdn-creatives-geocdn-prd.unityads.unity3d.com`
  - `cdn-creatives-prd.unityads.unity3d.com`
  - `cdn-creatives-tencent-prd.unityads.unitychina.cn`
  - `cdn-store-icons-*.unityads.unity3d.com`
  - `cdn-creatives-akamaistls-prd.acquire.unity3dusercontent.com`

### Hot-Update

- JavaScript game logic is delivered via a **hot-update mechanism** (`mbh-hotupdate.7ea21.js`)
  using JSZip for patching.
- SHA-256 integrity (`sha256.min.js`) and MD5 (`spark-md5.js`) used for patch verification.

### Anti-Cheat / Integrity

- **NetEase NIS** (`libnesec.so`, `libnms.so`) — code integrity and anti-tamper
- **PGL Armour** (`libpglarmor.so`) — file and memory protection
- **SafeDK** (`com.safedk`) — SDK compliance monitoring
- Bugsnag root detection (`libbugsnag-root-detection.so`)

---

## 16. Resources Overview

| Directory | Contents |
|---|---|
| `res/layout/` | 200+ XML layouts (game UI, ad units, settings, widgets, dialogs) |
| `res/drawable-*/` | Drawables for hdpi, mdpi, xhdpi, xxxhdpi, anydpi, nodpi, watch |
| `res/mipmap-*/` | Launcher icons (hdpi, mdpi, xhdpi, xxhdpi, xxxhdpi, anydpi) |
| `res/values/` | strings (779), integers, bools, attrs (2455 lines), colors, styles, themes |
| `res/values-land/` | Landscape-specific values |
| `res/values-night/` | Dark-mode color overrides |
| `res/values-sw360dp/` `values-sw600dp/` | Screen-width adaptive values |
| `res/anim/` `res/animator/` | View and property animations |
| `res/navigation/` | AndroidX Navigation component graphs |
| `res/xml/` | `network_security_config.xml`, `splits0.xml` (81 language splits), widget configs, `ad_services_config.xml` |
| `res/font/` | Custom font assets |
| `res/raw/` | Raw binary resources |
| `res/color/` `res/color-night/` | Color state lists |
| `res/menu/` | Options/contextual menus |

---

## 17. Internationalisation (i18n)

The app supports **81 languages** via language split APKs:

af, am, ar, as, az, be, bg, bn, bs, ca, cs, da, **de**, el,
**en**, **es**, et, eu, fa, fi, **fr**, gl, gu, hi, hr, hu, hy,
in (id), is, **it**, iw (he), **ja**, ka, kk, km, kn, **ko**,
ky, lo, lt, lv, mk, ml, mn, mr, ms, my, nb, ne, **nl**,
or, pa, **pl**, **pt**, **ro**, **ru**, sa, si, sk, sl, sq, sr,
sv, sw, ta, te, **th**, tl, **tr**, uk, ur, uz, **vi**,
**zh**, zu.

(Bold = major markets.)

---

## 18. Home-Screen Widget

Two home-screen widgets are registered:

| Widget | Size | Update Period |
|---|---|---|
| Small (`HsSmallWidget`) | 2 × 2 cells (110 × 110 dp min) | 12 hours |
| Medium (`HsMediumWidget`) | 4 × 2 cells (250 × 110 dp min) | 12 hours |

- Initial layout: `hs_widget_small_topgrade` / `hs_widget_medium_topgrade`
- Widget category: `home_screen`
- Widget click events handled by `HsWidgetBroadcastReceiver`

---

## 19. Push Notifications (FCM)

- Uses **Firebase Cloud Messaging**
- Custom FCM service: `org.cocos2dx.javascript.google.MyFirebaseMessagingService`
- Notification delete events: `org.cocos2dx.javascript.google.NotificationDeletedReceiver`
- AppsFlyer FCM listener also registered for attribution of push campaigns
- Firebase project: `blockjuggledevsite` (Google project ID visible in `strings.xml`)

---

## 20. Ad-Related Configuration

### Global Ad Strings

| Key | Value |
|---|---|
| `admob_appid` | *(empty — AdMob app ID not exposed in strings.xml)* |
| `af_dev_key` | `M9jeZtZDFEpp3XpimBKXC6` |
| `appkey` | `03c77c311921a376dae47015790ad6c6` |
| `app_id` | `2` |
| `game_id` | `10` |
| `ThinkingData_Appid` | `c34f7c8cc9e54d688b2db32dd3c72284` |

### Ad UI Strings

| Key | Value |
|---|---|
| `ad_close` | Close |
| `ad_skip` | Skip |
| `ad_one_of_two` | Ad 1 of 2 |
| `ad_two_of_two` | Ad 2 of 2 |
| `ad_view_more_btn` | View more |
| `hs_countdown_got_reward` | Rewarded! |
| `hs_countdown_reward` | Reward in %ds |

### Internal Debug / QA Strings (Chinese)

| Key | Value |
|---|---|
| `adq_dokit_title_open_max_ad_info` | 打开MaxAd (Open MaxAd) |
| `title_load_reward` | 拉激励 (Load rewarded) |
| `title_show_reward` | 出激励 (Show rewarded) |
| `title_set_game_data` | 改游戏数据 (Modify game data) |
| `title_open_h5_h5game` | H5Game |
| `title_set_rewardadthree` | 设置激励三次ecpm |
| `adq_dokit_title_show_think_uid` | 唯一ID (Unique ID) |

---

## 21. Game-Specific Configuration Files

### Corridor Map (`assets/corridormapconfig/`)

11 JSON files defining per-segment ad-frequency corridors:

| File | Conditions | Purpose |
|---|---|---|
| `corridor_file_74004.json` | US | US-market corridor map |
| `corridor_file_74002.json` | — | Secondary corridor |
| `corridor_file_74006.json` | — | Tertiary corridor |
| `corridor_factor_*_v*.json` | Various country groups | Factor multipliers per segment version |

Each corridor entry defines:
- **Segment ID** (hex key, e.g. `318751cf4db840b4`)
- **Time windows**: `in_24h`, `24_168h`, `168_744h`, `out_744h`
- **Floor prices** for each time window (`floor1`)

### Trait-Based Feature Flags (`assets/assets/`)

Feature trait JS bundles (loaded at runtime):

| Trait | Purpose |
|---|---|
| `LaunchBrandAdSkipTrait` | Controls brand-ad skip button behaviour at launch |
| `IsOpenChangeSkinNotChangeBlockTrait` | Whether changing skin also changes block style |
| `FixLastStageRepeatDisplayTrait` | Bug fix for last-stage repeated display |

Each trait has a `config.json` (parameters) and `index.js` (implementation).

### Game Hall Assets (`assets/assets/gl_hall/`)

Contains thousands of JSON import manifests for the **game lobby / hall** UI assets
(textures, sprite atlases, scene configs loaded by Cocos2d-x).

### MRAID Bridge (`assets/ia_mraid_bridge.txt`)

MRAID JavaScript bridge used by InnerActive / Fyber rich-media ads.

### Open Measurement (`assets/ad-viewer/`)

- `omsdk-v1.js` — IAB Open Measurement SDK (viewability tracking)
- `omid-session-client-v1.js` — OMID session client

### Baseline Profile (`assets/dexopt/`)

- `baseline.prof` / `baseline.profm` — ART baseline profile for faster startup
  (Android 9+).

---

## 22. Smali / DEX Breakdown

The base APK contains **15 DEX files** (including the audience_network DEX):

| DEX | Smali files | Notes |
|---|---|---|
| `classes.dex` (smali) | 45 | Top-level entry stubs |
| `classes.dex` (smali_assets – audience_network) | 3,330 | Facebook Audience Network SDK |
| `classes2.dex` | 5,695 | Core game + UI code |
| `classes3.dex` | 6,133 | Ad SDK code (AppLovin, etc.) |
| `classes4.dex` | 6,489 | Ad SDK + analytics |
| `classes5.dex` | 6,319 | Mixed SDK code |
| `classes6.dex` | 6,655 | Mixed SDK code |
| `classes7.dex` | 6,507 | Mixed SDK code |
| `classes8.dex` | 6,814 | Mixed SDK code |
| `classes9.dex` | 7,230 | Mixed SDK code |
| `classes10.dex` | 7,306 | Mixed SDK code |
| `classes11.dex` | 8,009 | Mixed SDK code |
| `classes12.dex` | 8,172 | Mixed SDK code |
| `classes13.dex` | 1,398 | Tail SDK code |
| `classes14.dex` | 40 | Minimal tail |
| **Total** | **80,142** | |

The heavy use of multiple DEX files is due to the large number of ad SDKs.
Most business-logic code is **obfuscated** (single/two-letter package names:
`a`, `ab`, `b0`, `c1`, …) except for well-known library packages.

---

## 23. Assets Structure

Total asset files: **8,504** inside the base APK.

| Directory | Files | Contents |
|---|---|---|
| `assets/assets/` | 7,956 | **Cocos2d-x game assets** — sprite atlases, textures, scene files, animations, audio, UI configs, trait JS bundles |
| `assets/lotties/` | 449 | **Lottie JSON animations** — endcard and video ad animations |
| `assets/src/` | 11 | Engine scripts (`cocos2d-jsb.js`, `settings.js`) + lib bundles |
| `assets/ecpmconfig/` | 23 | Per-country eCPM floor JSON configs |
| `assets/corridormapconfig/` | 11 | Ad frequency corridor maps |
| `assets/lottie/` | 1 | ANR-related Lottie animation |
| `assets/ad-viewer/` | 2 | OMSDK + OMID JS |
| `assets/audience_network/` | 2 | Facebook Audience Network DEX files |
| `assets/jsb-adapter/` | 2 | Cocos2d JSB adapter scripts |
| `assets/dexopt/` | 2 | ART baseline profile |

> **Note:** The main game scripts (`G_Cfg.js`, `settings.js`, `cocos2d-jsb.js`)
> are **encrypted** with a custom HEK (Hash Encryption Key) scheme and cannot
> be read directly. They are decrypted at runtime by `libcocos2djs.so`.

---

## 24. Key String Resources

Selected strings that reveal game features and IDs:

| Key | Value |
|---|---|
| `app_name` | Block Blast! |
| `app_id` | 2 |
| `game_id` | 10 |
| `project_id` | blockjuggledevsite |
| `auth_client_id` | `249091862244-56935578l6r72camqr2nv57ck69v1ih8.apps.googleusercontent.com` |
| `af_dev_key` | `M9jeZtZDFEpp3XpimBKXC6` |
| `appkey` | `03c77c311921a376dae47015790ad6c6` |
| `ThinkingData_Appid` | `c34f7c8cc9e54d688b2db32dd3c72284` |
| `ThinkingData_mode` | NORMAL |
| `ThinkingData_timeZone` | GMT+0 |
| `fb_login_protocol_scheme` | fb1576913169390778 |
| `applovin_agree_message` | *GDPR consent dialog text* |
| `hs_countdown_got_reward` | Rewarded! |
| `hs_countdown_reward` | Reward in %ds |
| `ia_skip_rewarded_dialog_title` | Close Video? |
| `tt_reward_msg` | Watch the entire video to claim your reward |
| `tt_reward_full_skip` | Skip after %1$ss |

---

## 25. How to Make Changes and Recompile

The decompiled project is ready to edit at:

```
output/
├── com.block.juggle/        # Base APK (apktool smali project)
│   ├── AndroidManifest.xml  ← edit permissions, activities, etc.
│   ├── apktool.yml          ← apktool metadata (do not edit unless necessary)
│   ├── smali/               ← Dalvik bytecode (edit .smali files here)
│   ├── smali_classes2/ … smali_classes14/
│   ├── smali_assets/        ← Facebook Audience Network smali
│   ├── res/                 ← decoded resources (strings, layouts, drawables)
│   └── assets/              ← raw game assets (JS bundles, configs)
├── config.arm64_v8a/        # Native libs split (apktool project)
├── config.en/               # English language split (apktool project)
├── config.mdpi/             # Medium-DPI drawables split (apktool project)
├── gamedatalib/             # Asset-pack split (apktool project)
├── com.block.juggle-java/   # Java source (jadx output — read-only reference)
│   └── sources/             ← decompiled Java (not editable for rebuild)
├── manifest.json            # XAPK metadata
└── icon.png                 # App icon
```

### Editing & Recompiling a Single Split APK

```bash
# 1. Edit files (example: change a string)
nano output/com.block.juggle/res/values/strings.xml

# 2. Recompile that split
bboverload recompile output/com.block.juggle

# 3. The rebuilt APK will be at:
#    output/com.block.juggle/dist/com.block.juggle.apk

# 4. Sign the rebuilt APK
bboverload sign output/com.block.juggle/dist/com.block.juggle.apk
```

### Repackaging All Splits into a New XAPK

```bash
# Rebuild ALL splits and package them into a .xapk
bboverload recompile-xapk output/

# The rebuilt XAPK will be at:
#    output/dist/com.block.juggle_9.7.2.xapk
```

### Editing Smali Bytecode

Smali files live in `output/com.block.juggle/smali*/`.
Each `.smali` file corresponds to one Java class.
Refer to the jadx Java output at `output/com.block.juggle-java/sources/` as a
human-readable reference.

### Resource Changes

- **Strings**: `res/values/strings.xml`
- **Layouts**: `res/layout/*.xml`
- **Drawables**: replace files in `res/drawable-*/` or `res/mipmap-*/`
- **App icon**: replace `res/mipmap-xxxhdpi/ic_launcher.png` (and all densities)

### Important Notes

1. The main game JavaScript files (`assets/src/assets/`) are **encrypted**
   and cannot be modified directly.
2. Native libraries (`config.arm64_v8a/lib/arm64-v8a/*.so`) are pre-compiled
   binaries — they require a C++ toolchain to rebuild.
3. After recompiling, the APK must be re-signed before installation.
4. The `apktool.yml` file is generated by apktool; only edit it if you need
   to change the package name or version.
