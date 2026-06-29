[app]
# Title of the application
title = Video Downloader Pro

# Package name (must be unique, no spaces, all lowercase)
package.name = videodownloaderpro

# Package domain (org.test -> org.test.videodownloaderpro)
package.domain = com.mahmoudyasser

# Source code directory
source.dir = .

# Version of the application
version = 1.0.0

# Requirements: Kivy + yt-dlp + dependencies
# Note: ffmpeg is required for MP3 audio extraction. On Android you may need
# to include a prebuilt ffmpeg binary or use a python-for-android ffmpeg recipe.
requirements = python3,kivy,yt-dlp,requests,urllib3,certifi,charset-normalizer,idna

# Orientation (portrait, landscape, or all)
orientation = portrait

# Icon
# Ensure the icon path is correct. For Android, PNG is recommended.
icon.filename = %(source.dir)s/Mahmoud Yasser_Logo.png

# Presplash (loading screen) image
# presplash.filename = %(source.dir)s/presplash.png

# Windowing mode
fullscreen = 0

# Android API versions
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.arch = armeabi-v7a arm64-v8a

# Permissions
# INTERNET is required for yt-dlp.
# For Android 10+ (API 29+), standard WRITE_EXTERNAL_STORAGE is limited.
# We save to the app-private directory by default, so storage permissions are optional.
# MANAGE_EXTERNAL_STORAGE is only needed if you want to write to shared Downloads.
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# If you need MANAGE_EXTERNAL_STORAGE on Android 11+ (for shared Downloads), uncomment:
# android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# Application extras
android.gradle_dependencies = com.android.support:support-compat:28.0.0
android.add_src = 
android.add_aars = 

# App theme
android.apptheme = @android:style/Theme.NoTitleBar

# Presplash background color
android.presplash_color = #0a0a0a

# Window background color
android.window_background = #0a0a0a

# Enable Python 3 support
android.allow_backup = True

# Services (if any)
# services =

# Buildozer specific settings
[buildozer]
# Build directory
build_dir = ./.buildozer

# Application binary output directory
bin_dir = ./bin

# Log level
log_level = 2

# Warn if source code is not in version control
warn_on_root = 1

# iOS (not used for Android builds)
[app:ios]
# ios.kivy_ios = 
# ios.codesign.allowed = 
# ios.codesign.identity = 
# ios.codesign.developer_team = 
# ios.orientation = portrait

# Android specific settings
[app:android]
# android.release_artifact = apk
# android.allow_backup = True
# android.archs = armeabi-v7a arm64-v8a
# android.add_jars = 
# android.add_aars = 
# android.add_libs_armeabi-v7a = 
# android.add_libs_arm64-v8a = 
# android.add_libs_x86 = 
# android.add_libs_mips = 
# android.manifest.placeholders = 
# android.gradle_dependencies = 
# android.add_activities = 
# android.add_services = 
# android.add_providers = 
# android.add_receivers = 
# android.add_assets = 
# android.add_resources = 
# android.add_src = 
# android.add_aars = 
# android.whitelist = 
# android.blacklist = 
# android.add_aars = 
# android.add_jars = 
# android.add_libs = 
# android.add_activities = 
# android.add_services = 
# android.add_providers = 
# android.add_receivers = 
# android.add_assets = 
# android.add_resources = 
# android.add_src = 
# android.gradle_dependencies = 
# android.manifest.placeholders = 
# android.api = 
# android.minapi = 
# android.sdk = 
# android.ndk = 
# android.private_storage = 
# android.skip_update = 
# android.ndk_path = 
# android.sdk_path = 
# android.p4a_dir = 
# android.entrypoint = 
# android.apptheme = 
# android.arch = 

# Packaging mode
# android.release_artifact = apk
# android.copy_libs = 1
# android.add_resources = 
# android.add_assets = 
# android.add_jars = 
# android.add_aars = 
# android.add_src = 
# android.gradle_dependencies = 
# android.manifest.placeholders = 
# android.add_activities = 
# android.add_services = 
# android.add_providers = 
# android.add_receivers = 
# android.private_storage = 
# android.whitelist = 
# android.blacklist = 
# android.copy_libs = 
# android.no-byte-compile-python = 
# android.release_artifact = apk
