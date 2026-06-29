# Video Downloader Pro

A sleek **black & yellow themed** Android video/playlist downloader built with **Kivy** and **yt-dlp**.

**Author:** Mahmoud Yasser

---

## Features

- 🎥 Download single videos or entire playlists
- 🎵 Choose between **MP4 (Video)** or **MP3 (Audio)** formats
- 📊 Quality selection: Best, 1080p, 720p, 480p, 360p, 240p, 144p
- 📝 Optional subtitle download (English)
- ⏯ Pause / Resume / Stop controls during download
- ✅ Skip already-downloaded items (archive file)
- 📂 Open downloads folder button
- 🎨 Dark UI with yellow accent (Mahmoud Yasser branding)
- 🤖 Android 10+ (API 30+) compatible — saves to app directory without storage permission issues

---

## Project Structure

```
VideoDownloaderAndroid/
├── main.py                          # Main Kivy application
├── buildozer.spec                   # Buildozer configuration
├── Mahmoud Yasser_Logo.png          # App logo (PNG, required for Android)
├── Mahmoud Yasser_Logo.jpeg         # Original logo (backup)
├── app_icon.ico                     # Desktop icon (optional)
├── .github/
│   └── workflows/
│       └── build.yml                # GitHub Actions CI — builds APK automatically
└── README.md                        # This file
```

---

## 🚀 Quick Start: Get the APK (GitHub Actions — FREE)

You don't need to install anything on your computer. GitHub builds the APK for you in the cloud.

### Step 1: Push to GitHub

1. Create a new repository on GitHub (e.g., `VideoDownloaderPro`).
2. Push this project folder to it:

```bash
cd "VideoDownloaderAndroid"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/VideoDownloaderPro.git
git push -u origin main
```

> **Tip:** If you don't have Git installed, download the project as a ZIP, upload files to GitHub directly, or use [GitHub Desktop](https://desktop.github.com/).

### Step 2: Trigger the Build

- **Automatic:** Push any change to the `main` or `master` branch and the build starts automatically.
- **Manual:** Go to **Actions** → **Build Android APK** → **Run workflow**.

### Step 3: Download the APK

1. Go to the **Actions** tab in your GitHub repository.
2. Click the latest successful workflow run.
3. Scroll down to the **Artifacts** section.
4. Download **`VideoDownloaderPro-APK`**.
5. Extract the ZIP — the `.apk` file is inside.
6. Transfer it to your Android phone and install it.

> **First build warning:** The initial GitHub Actions run may take **30–60 minutes** because it downloads the Android SDK, NDK, and builds Python-for-Android from scratch. Subsequent builds are much faster thanks to caching.

---

## 📦 Release Builds (Auto-Upload)

If you create a Git tag (e.g., `v1.0.0`), the APK is automatically uploaded to a **GitHub Release**:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Go to **Releases** in your repo to download the signed APK.

---

## 🛠️ Local Development (Desktop Testing)

If you want to test the UI on your computer before building the APK:

```bash
# 1. Install Python dependencies
pip install kivy yt-dlp

# 2. Run the app
python main.py
```

> Note: Downloads on desktop will save to `~/Downloads/VideoDownloaderPro/`.

---

## 🔧 Build Locally (Advanced — Linux/WSL2 Required)

If you prefer building the APK on your own machine instead of GitHub Actions:

```bash
# Install buildozer on Ubuntu / WSL2
sudo apt update
sudo apt install python3-pip build-essential git ffmpeg \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    zlib1g-dev libgles2-mesa-dev autoconf automake libtool pkg-config \
    libncurses5-dev libffi-dev libssl-dev libsqlite3-dev zip unzip \
    openjdk-17-jdk

pip install buildozer cython

# Build APK
buildozer android debug

# Output: ./bin/*.apk
```

---

## ⚠️ Android Installation Notes

- **Android 8+:** You may need to enable **Install unknown apps** for your file manager/browser.
- **Android 10+:** The app saves downloads to its private directory (`Android/data/com.mahmoudyasser.videodownloaderpro/...`) to comply with Scoped Storage. Use the **Open Downloads Folder** button inside the app to browse them.

---

## 📋 Requirements (for buildozer.spec)

- `python3`
- `kivy`
- `yt-dlp`
- `requests`, `urllib3`, `certifi`

---

## 📝 License

Personal project by **Mahmoud Yasser**. All rights reserved.

---

## 🆘 Troubleshooting

| Issue | Solution |
|---|---|
| GitHub Actions build fails | Check the **Actions** log — usually caused by missing `buildozer.spec` or logo file issues. Ensure `Mahmoud Yasser_Logo.png` is committed. |
| App crashes on Android | Make sure the APK is built with the same `buildozer.spec` architecture (`arm64-v8a` / `armeabi-v7a`). |
| Download fails / 403 error | yt-dlp updates frequently. Rebuild the APK with the latest `yt-dlp` version by pushing a new commit to trigger GitHub Actions again. |
| Can't find downloads on phone | Tap the **Open Downloads Folder** button in the app, or use a file manager to navigate to the app's private directory. |

---

## 💡 Tips

- **Update yt-dlp regularly:** Video sites change frequently. Rebuild the APK periodically via GitHub Actions to get the latest `yt-dlp` fixes.
- **Quality tip:** For fastest downloads on mobile data, choose `360p` or `480p`.
- **Playlist tip:** Paste a playlist URL, wait for it to load, then uncheck videos you don't want before downloading.

---

Made with ❤️ by **Mahmoud Yasser**.
