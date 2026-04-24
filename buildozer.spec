[app]

# Application name and package
title = BlockOverload
package.name = blockoverload
package.domain = com.bboverload

# Source directory (relative to this spec file)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.include_patterns = blockoverload/*.py

# Application version
version = 1.0.0

# Entry point
entrypoint = blockoverload.main

# Requirements: kivy + its runtime dependencies
requirements = python3,kivy==2.3.0,kivymd

# Orientation
orientation = portrait

# Android-specific settings
android.api = 34
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a, armeabi-v7a

# Permissions (no special permissions needed)
android.permissions =

# App icon / presplash (leave empty to use kivy defaults)
# icon.filename = %(source.dir)s/assets/icon.png
# presplash.filename = %(source.dir)s/assets/presplash.png

# Allow app to be installed on external storage
android.allow_backup = True

# Fullscreen (hide status bar on Android)
fullscreen = 1

# Log level
log_level = 2

[buildozer]
# (Buildozer internal log level)
log_level = 2
warn_on_root = 1
