#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Video Downloader Pro
by Mahmoud Yasser

Enhanced Android video/playlist downloader using Kivy + yt-dlp.
"""
from __future__ import annotations

import os
import sys
import threading
import time
import traceback
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp

# yt-dlp (bundled in Android via buildozer requirements)
try:
    import yt_dlp
except ImportError:
    yt_dlp = None

# ===== Android-specific imports =====
ANDROID = False
API_LEVEL = 0

try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path, app_storage_path
    from jnius import autoclass, cast
    import android
    ANDROID = True
    try:
        # Detect API level for scoped-storage logic
        Build = autoclass('android.os.Build')
        API_LEVEL = int(Build.VERSION.SDK_INT)
    except Exception:
        API_LEVEL = 0
except ImportError:
    autoclass = None
    cast = None
    app_storage_path = None
    primary_external_storage_path = None

# ============================================================
#                 BLACK & YELLOW THEME COLORS
# ============================================================
BG = (0.04, 0.04, 0.04, 1)
SURFACE = (0.08, 0.08, 0.08, 1)
SURFACE_LT = (0.12, 0.12, 0.12, 1)
PRIMARY = (1.00, 0.76, 0.03, 1)
PRIMARY_HV = (1.00, 0.84, 0.31, 1)
TEXT = (0.96, 0.96, 0.96, 1)
TEXT_DIM = (0.74, 0.74, 0.74, 1)
TEXT_BLACK = (0.04, 0.04, 0.04, 1)
DANGER = (0.96, 0.26, 0.21, 1)
SUCCESS = (0.06, 0.72, 0.50, 1)
WARNING = (1.00, 0.60, 0.00, 1)


# ============================================================
#                 STYLED COMPONENTS
# ============================================================
class YellowButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.color = TEXT_BLACK
        self.bold = True
        self.font_size = "16sp"
        with self.canvas.before:
            self._color = Color(*PRIMARY)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def on_press(self):
        self._color.rgba = PRIMARY_HV

    def on_release(self):
        self._color.rgba = PRIMARY


class DarkButton(Button):
    def __init__(self, color=PRIMARY, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.color = color
        self.bold = True
        self.font_size = "15sp"
        with self.canvas.before:
            self._color = Color(*SURFACE_LT)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*SURFACE)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._update, size=self._update)
        self.padding = dp(12)
        self.spacing = dp(8)

    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


class StyledInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = SURFACE_LT
        self.foreground_color = TEXT
        self.cursor_color = PRIMARY
        self.font_size = "15sp"
        self.padding = [dp(12), dp(12), dp(12), dp(12)]
        self.multiline = False


# ============================================================
#                     MAIN APP
# ============================================================
class VideoDownloaderApp(App):
    title = "Video Downloader Pro"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_info = None
        self.is_playlist = False
        self.playlist_entries = []
        self.entry_checks = []
        self.is_downloading = False
        self.stop_requested = False
        self.pause_requested = False

        # Determine best download path
        self.download_path = self._choose_download_path()
        os.makedirs(self.download_path, exist_ok=True)

    def _choose_download_path(self):
        """Pick a writable path that works on Android 10+ and desktop."""
        if ANDROID:
            # On Android 11+ (API 30+), standard shared storage is restricted.
            # Use the app-specific external directory — no permissions needed and it is reliable.
            try:
                from android.storage import app_storage_path
                path = os.path.join(app_storage_path(), "downloads")
                if os.path.isdir(path) or os.path.isdir(os.path.dirname(path)):
                    return path
            except Exception:
                pass

            try:
                from android.storage import primary_external_storage_path
                legacy = os.path.join(primary_external_storage_path(), "Download", "VideoDownloaderPro")
                return legacy
            except Exception:
                pass
            return os.path.join(os.path.expanduser("~"), "downloads")
        else:
            return os.path.join(os.path.expanduser("~"), "Downloads", "VideoDownloaderPro")

    def build(self):
        # Android runtime permissions
        if ANDROID:
            try:
                from android.permissions import request_permissions, Permission
                perms = [Permission.INTERNET]
                if API_LEVEL < 29:
                    perms += [Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE]
                request_permissions(perms)
            except Exception:
                pass

        Window.clearcolor = BG

        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))

        # ===== HEADER =====
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(60), spacing=dp(8))

        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), "Mahmoud Yasser_Logo.png")
        if os.path.exists(logo_path):
            logo = Image(source=logo_path, size_hint_x=None, width=dp(50))
            header.add_widget(logo)
        else:
            # Fallback: draw a yellow circle placeholder
            logo_placeholder = BoxLayout(size_hint_x=None, width=dp(50))
            with logo_placeholder.canvas:
                Color(*PRIMARY)
                RoundedRectangle(pos=logo_placeholder.pos, size=logo_placeholder.size, radius=[dp(25)])
            logo_placeholder.bind(pos=lambda inst, *a: setattr(inst.canvas.get_group('a')[0] if inst.canvas.get_group('a') else None, 'pos', inst.pos) or None)
            header.add_widget(logo_placeholder)

        title_box = BoxLayout(orientation="vertical")
        title_lbl = Label(
            text="[b]Video Downloader Pro[/b]",
            markup=True, color=PRIMARY, font_size="20sp",
            halign="left", valign="middle"
        )
        title_lbl.bind(size=title_lbl.setter("text_size"))
        sub_lbl = Label(
            text="by Mahmoud Yasser",
            color=TEXT_DIM, font_size="11sp", italic=True,
            halign="left", valign="middle"
        )
        sub_lbl.bind(size=sub_lbl.setter("text_size"))
        title_box.add_widget(title_lbl)
        title_box.add_widget(sub_lbl)
        header.add_widget(title_box)
        root.add_widget(header)

        # ===== URL INPUT =====
        url_card = Card(orientation="vertical", size_hint_y=None, height=dp(140))
        url_card.add_widget(Label(
            text="[b]🔗  Source URL[/b]", markup=True, color=PRIMARY,
            size_hint_y=None, height=dp(22), halign="left",
            text_size=(Window.width - dp(40), None)
        ))

        self.url_input = StyledInput(
            hint_text="Paste video or playlist URL here...",
            size_hint_y=None, height=dp(46)
        )
        self.url_input.bind(on_text_validate=lambda *a: self.fetch_info())
        url_card.add_widget(self.url_input)

        fetch_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(6))
        self.fetch_btn = YellowButton(
            text="🔍  Fetch Info", size_hint_x=0.75,
            on_release=lambda x: self.fetch_info()
        )
        self.clear_btn = DarkButton(
            text="✕", size_hint_x=0.25,
            on_release=lambda x: self.clear_url()
        )
        fetch_row.add_widget(self.fetch_btn)
        fetch_row.add_widget(self.clear_btn)
        url_card.add_widget(fetch_row)
        root.add_widget(url_card)

        # ===== TABS =====
        self.tabs = TabbedPanel(do_default_tab=False, tab_pos="top_mid",
                                tab_width=dp(110), background_color=BG)

        # ----- Options Tab -----
        opt_tab = TabbedPanelItem(text="Options", background_color=PRIMARY,
                                  color=TEXT_BLACK)
        opt_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))

        opt_box.add_widget(Label(text="[b]FORMAT[/b]", markup=True,
                                 color=PRIMARY, size_hint_y=None, height=dp(20),
                                 halign="left",
                                 text_size=(Window.width - dp(40), None)))
        self.format_spinner = Spinner(
            text="MP4 (Video)",
            values=("MP4 (Video)", "MP3 (Audio)"),
            size_hint_y=None, height=dp(46),
            background_color=PRIMARY, color=TEXT_BLACK
        )
        self.format_spinner.bind(text=self.on_format_change)
        opt_box.add_widget(self.format_spinner)

        opt_box.add_widget(Label(text="[b]QUALITY[/b]", markup=True,
                                 color=PRIMARY, size_hint_y=None, height=dp(20),
                                 halign="left",
                                 text_size=(Window.width - dp(40), None)))
        self.quality_spinner = Spinner(
            text="Best Quality",
            values=("Best Quality", "1080p", "720p", "480p", "360p", "240p", "144p"),
            size_hint_y=None, height=dp(46),
            background_color=SURFACE_LT, color=TEXT
        )
        opt_box.add_widget(self.quality_spinner)

        opt_box.add_widget(Label(text="[b]OPTIONS[/b]", markup=True,
                                 color=PRIMARY, size_hint_y=None, height=dp(20),
                                 halign="left",
                                 text_size=(Window.width - dp(40), None)))

        # Subtitles checkbox
        sub_row = BoxLayout(orientation="horizontal", size_hint_y=None,
                            height=dp(40), spacing=dp(8))
        self.sub_check = CheckBox(size_hint_x=None, width=dp(40), color=PRIMARY)
        sub_row.add_widget(self.sub_check)
        sub_row.add_widget(Label(text="Download subtitles", color=TEXT,
                                 halign="left",
                                 text_size=(Window.width - dp(80), None)))
        opt_box.add_widget(sub_row)

        # Skip-already check
        sk_row = BoxLayout(orientation="horizontal", size_hint_y=None,
                           height=dp(40), spacing=dp(8))
        self.archive_check = CheckBox(active=True, size_hint_x=None,
                                      width=dp(40), color=PRIMARY)
        sk_row.add_widget(self.archive_check)
        sk_row.add_widget(Label(text="Skip already-downloaded items",
                                color=TEXT, halign="left",
                                text_size=(Window.width - dp(80), None)))
        opt_box.add_widget(sk_row)

        opt_box.add_widget(Label(size_hint_y=1))  # spacer
        opt_tab.add_widget(opt_box)
        self.tabs.add_widget(opt_tab)

        # ----- Playlist Tab -----
        pl_tab = TabbedPanelItem(text="Playlist", background_color=PRIMARY,
                                 color=TEXT_BLACK)
        pl_box = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))

        self.pl_title = Label(text="No playlist loaded", color=PRIMARY,
                              size_hint_y=None, height=dp(30), bold=True,
                              halign="left",
                              text_size=(Window.width - dp(20), None))
        pl_box.add_widget(self.pl_title)

        btn_row = BoxLayout(orientation="horizontal", size_hint_y=None,
                            height=dp(40), spacing=dp(5))
        btn_row.add_widget(DarkButton(text="Select All",
                                      on_release=lambda x: self.toggle_all(True)))
        btn_row.add_widget(DarkButton(text="None",
                                      on_release=lambda x: self.toggle_all(False)))
        btn_row.add_widget(DarkButton(text="Invert",
                                      on_release=lambda x: self.invert_all()))
        pl_box.add_widget(btn_row)

        self.count_lbl = Label(text="0 selected", color=PRIMARY,
                               size_hint_y=None, height=dp(22),
                               halign="left",
                               text_size=(Window.width - dp(20), None))
        pl_box.add_widget(self.count_lbl)

        # Scrollable list
        self.pl_scroll = ScrollView()
        self.pl_grid = GridLayout(cols=1, size_hint_y=None, spacing=dp(2))
        self.pl_grid.bind(minimum_height=self.pl_grid.setter("height"))
        self.pl_scroll.add_widget(self.pl_grid)
        pl_box.add_widget(self.pl_scroll)

        self.empty_lbl = Label(text="📋\n\nNo playlist loaded.\n\n"
                               "Paste a URL and tap Fetch Info.",
                               color=TEXT_DIM, halign="center")
        self.pl_grid.add_widget(self.empty_lbl)

        pl_tab.add_widget(pl_box)
        self.tabs.add_widget(pl_tab)

        root.add_widget(self.tabs)

        # ===== PROGRESS =====
        prog_card = Card(orientation="vertical", size_hint_y=None, height=dp(110))

        self.now_lbl = Label(text="Idle. Awaiting download...",
                             color=TEXT_DIM, size_hint_y=None, height=dp(22),
                             halign="left", bold=True,
                             text_size=(Window.width - dp(40), None))
        prog_card.add_widget(self.now_lbl)

        self.progress = ProgressBar(max=100, size_hint_y=None, height=dp(20))
        prog_card.add_widget(self.progress)

        info_row = BoxLayout(orientation="horizontal", size_hint_y=None,
                             height=dp(22))
        self.pct_lbl = Label(text="0%", color=PRIMARY, bold=True,
                             size_hint_x=0.3, halign="left",
                             text_size=(Window.width / 3, None))
        self.speed_lbl = Label(text="", color=TEXT_DIM,
                               size_hint_x=0.7, halign="right",
                               text_size=(Window.width * 0.7, None))
        info_row.add_widget(self.pct_lbl)
        info_row.add_widget(self.speed_lbl)
        prog_card.add_widget(info_row)
        root.add_widget(prog_card)

        # ===== CONTROL BUTTONS =====
        ctrl_row = BoxLayout(orientation="horizontal", size_hint_y=None,
                             height=dp(54), spacing=dp(6))

        self.dl_btn = YellowButton(text="⬇  Download",
                                   on_release=lambda x: self.start_download())
        self.dl_btn.disabled = True
        ctrl_row.add_widget(self.dl_btn)

        self.pause_btn = DarkButton(text="⏸  Pause", color=WARNING,
                                    on_release=lambda x: self.toggle_pause())
        self.pause_btn.disabled = True
        ctrl_row.add_widget(self.pause_btn)

        self.stop_btn = DarkButton(text="⏹  Stop", color=DANGER,
                                   on_release=lambda x: self.stop_download())
        self.stop_btn.disabled = True
        ctrl_row.add_widget(self.stop_btn)
        root.add_widget(ctrl_row)

        # ===== BROWSE / OPEN FOLDER =====
        browse_row = BoxLayout(orientation="horizontal", size_hint_y=None,
                               height=dp(40), spacing=dp(6))
        self.browse_btn = DarkButton(text="📂  Open Downloads Folder", color=PRIMARY,
                                     on_release=lambda x: self.open_downloads())
        browse_row.add_widget(self.browse_btn)
        root.add_widget(browse_row)

        # ===== STATUS BAR =====
        self.status_lbl = Label(text="🟢 Ready  •  © Mahmoud Yasser",
                                color=TEXT_DIM, size_hint_y=None, height=dp(22),
                                font_size="11sp", italic=True,
                                halign="center",
                                text_size=(Window.width - dp(20), None))
        root.add_widget(self.status_lbl)

        return root

    # ============================================================
    #                     UI ACTIONS
    # ============================================================
    def on_format_change(self, spinner, text):
        if "MP4" in text:
            self.quality_spinner.values = ("Best Quality", "1080p", "720p",
                                           "480p", "360p", "240p", "144p")
            self.quality_spinner.text = "Best Quality"
        else:
            self.quality_spinner.values = ("320 kbps", "256 kbps", "192 kbps",
                                           "128 kbps", "96 kbps")
            self.quality_spinner.text = "320 kbps"

    def clear_url(self):
        self.url_input.text = ""
        self.video_info = None
        self.is_playlist = False
        self.playlist_entries = []
        self.entry_checks.clear()
        self.pl_grid.clear_widgets()
        self.empty_lbl = Label(text="📋\n\nNo playlist loaded.\n\n"
                               "Paste a URL and tap Fetch Info.",
                               color=TEXT_DIM, halign="center")
        self.pl_grid.add_widget(self.empty_lbl)
        self.pl_title.text = "No playlist loaded"
        self.count_lbl.text = "0 selected"
        self.dl_btn.disabled = True
        self.now_lbl.text = "Idle. Awaiting download..."
        self.progress.value = 0
        self.pct_lbl.text = "0%"
        self.speed_lbl.text = ""

    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message, color=TEXT,
                                    text_size=(Window.width * 0.7, None),
                                    halign="center"),
                      size_hint=(0.85, 0.4),
                      background_color=SURFACE,
                      title_color=PRIMARY)
        popup.open()

    @mainthread
    def update_status(self, text, color=TEXT_DIM):
        self.status_lbl.text = text
        self.status_lbl.color = color

    def open_downloads(self):
        """Open the download folder in a file manager."""
        try:
            if ANDROID and autoclass:
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                File = autoclass('java.io.File')
                FileProvider = autoclass('androidx.core.content.FileProvider')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                currentActivity = PythonActivity.mActivity

                # Try to get a content URI via FileProvider for app-specific dir
                file_obj = File(self.download_path)
                if file_obj.exists():
                    try:
                        uri = FileProvider.getUriForFile(
                            currentActivity,
                            currentActivity.getPackageName() + ".fileprovider",
                            file_obj
                        )
                        intent = Intent(Intent.ACTION_VIEW)
                        intent.setDataAndType(uri, "resource/folder")
                        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                        currentActivity.startActivity(intent)
                        return
                    except Exception:
                        pass

                # Fallback: launch a chooser
                intent = Intent(Intent.ACTION_VIEW)
                uri = Uri.parse("content://com.android.externalstorage.documents/document/primary%3ADownload%2FVideoDownloaderPro")
                intent.setData(uri)
                currentActivity.startActivity(intent)
            else:
                import subprocess
                if sys.platform.startswith("win"):
                    os.startfile(self.download_path)
                elif sys.platform.startswith("darwin"):
                    subprocess.call(["open", self.download_path])
                else:
                    subprocess.call(["xdg-open", self.download_path])
        except Exception as e:
            self.show_popup("Info", f"Download path:\n{self.download_path}")

    # ============================================================
    #                     FETCH INFO
    # ============================================================
    def fetch_info(self):
        url = self.url_input.text.strip()
        if not url:
            self.show_popup("⚠️ Warning", "Please enter a valid URL!")
            return
        if not yt_dlp:
            self.show_popup("❌ Error",
                            "yt-dlp not installed!\nRun: pip install yt-dlp")
            return

        self.update_status("⏳ Fetching info...", WARNING)
        self.fetch_btn.text = "Fetching..."
        self.fetch_btn.disabled = True
        threading.Thread(target=self._fetch_thread, args=(url,),
                         daemon=True).start()

    def _fetch_thread(self, url):
        try:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": "in_playlist",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "cookiesfrombrowser": None,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            self.video_info = info
            if info and "entries" in info and info.get("entries"):
                self.is_playlist = True
                # Flatten entries, skip None, handle string entries
                raw = info["entries"]
                self.playlist_entries = [e for e in raw if e is not None]
            else:
                self.is_playlist = False
                self.playlist_entries = []
            Clock.schedule_once(lambda dt: self._populate_after_fetch(), 0)
        except Exception as e:
            err = str(e)
            Clock.schedule_once(lambda dt: self._fetch_error(err), 0)

    def _populate_after_fetch(self):
        self.fetch_btn.text = "🔍  Fetch Info"
        self.fetch_btn.disabled = False
        if self.is_playlist:
            title = self.video_info.get("title", "Playlist") if isinstance(self.video_info, dict) else "Playlist"
            self.pl_title.text = f"📋  {title}  •  {len(self.playlist_entries)} items"
            self.populate_playlist()
            # Switch to playlist tab (last widget added is Playlist)
            self.tabs.switch_to(self.tabs.tab_list[-1])
            self.update_status(
                f"✅ Playlist loaded — {len(self.playlist_entries)} items",
                SUCCESS)
        else:
            title = self.video_info.get("title", "Unknown") if isinstance(self.video_info, dict) else "Unknown"
            self.now_lbl.text = f"🎥  {title[:60]}"
            self.update_status("✅ Video info loaded — choose options", SUCCESS)
        self.dl_btn.disabled = False

    def _fetch_error(self, err):
        self.fetch_btn.text = "🔍  Fetch Info"
        self.fetch_btn.disabled = False
        self.update_status("❌ Error fetching info", DANGER)
        self.show_popup("❌ Error", err[:200])

    # ============================================================
    #                     PLAYLIST
    # ============================================================
    def populate_playlist(self):
        self.pl_grid.clear_widgets()
        self.entry_checks.clear()

        if not self.playlist_entries:
            self.empty_lbl = Label(text="📋\n\nPlaylist is empty.",
                                   color=TEXT_DIM, halign="center")
            self.pl_grid.add_widget(self.empty_lbl)
            self.update_count()
            return

        for i, entry in enumerate(self.playlist_entries):
            row = BoxLayout(orientation="horizontal", size_hint_y=None,
                            height=dp(48), spacing=dp(5), padding=dp(5))
            with row.canvas.before:
                c = SURFACE_LT if i % 2 == 0 else SURFACE
                Color(*c)
                rect = Rectangle(pos=row.pos, size=row.size)

                def update(inst, *a, r=rect):
                    r.pos = inst.pos
                    r.size = inst.size
                row.bind(pos=update, size=update)

            chk = CheckBox(active=True, size_hint_x=None, width=dp(40), color=PRIMARY)
            chk.bind(active=lambda *a: self.update_count())
            self.entry_checks.append(chk)
            row.add_widget(chk)

            idx = Label(text=f"{i+1:03d}", color=PRIMARY, bold=True,
                        size_hint_x=None, width=dp(40))
            row.add_widget(idx)

            if isinstance(entry, dict):
                title = entry.get("title", f"Video {i+1}")
            elif isinstance(entry, str):
                title = entry
            else:
                title = f"Video {i+1}"
            title_short = title if len(title) <= 50 else title[:47] + "..."
            row.add_widget(Label(text=title_short, color=TEXT, halign="left",
                                 valign="middle",
                                 text_size=(Window.width - dp(120), None)))

            self.pl_grid.add_widget(row)
        self.update_count()

    def toggle_all(self, state):
        for c in self.entry_checks:
            c.active = state
        self.update_count()

    def invert_all(self):
        for c in self.entry_checks:
            c.active = not c.active
        self.update_count()

    def update_count(self):
        n = sum(1 for c in self.entry_checks if c.active)
        self.count_lbl.text = f"✓ {n} of {len(self.entry_checks)} selected"

    def get_selected_indices(self):
        return [i + 1 for i, c in enumerate(self.entry_checks) if c.active]

    # ============================================================
    #                     DOWNLOAD
    # ============================================================
    def start_download(self):
        url = self.url_input.text.strip()
        if not url:
            self.show_popup("⚠️ Warning", "Please enter a valid URL!")
            return
        if self.is_playlist and not self.get_selected_indices():
            self.show_popup("⚠️ Warning", "Select at least one playlist item!")
            return

        self.is_downloading = True
        self.stop_requested = False
        self.pause_requested = False

        self.dl_btn.disabled = True
        self.dl_btn.text = "Downloading..."
        self.fetch_btn.disabled = True
        self.pause_btn.disabled = False
        self.stop_btn.disabled = False

        self.progress.value = 0
        self.pct_lbl.text = "0%"
        self.update_status("⬇️ Starting download...", WARNING)

        threading.Thread(target=self._download_worker, args=(url,),
                         daemon=True).start()

    def build_opts(self):
        fmt_choice = self.format_spinner.text
        quality = self.quality_spinner.text
        is_pl = self.is_playlist

        if is_pl:
            outtmpl = os.path.join(self.download_path,
                                   "%(playlist_title)s",
                                   "%(playlist_index)s - %(title)s.%(ext)s")
        else:
            outtmpl = os.path.join(self.download_path, "%(title)s.%(ext)s")

        opts = {
            "outtmpl": outtmpl,
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
            "noplaylist": not is_pl,
            "ignoreerrors": True,
            "continuedl": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "cookiesfrombrowser": None,
        }

        if is_pl:
            opts["playlist_items"] = ",".join(map(str, self.get_selected_indices()))

        if self.archive_check.active:
            opts["download_archive"] = os.path.join(self.download_path, ".archive.txt")

        if self.sub_check.active:
            opts["writesubtitles"] = True
            opts["subtitleslangs"] = ["en"]
            opts["writeautomaticsub"] = True

        if "MP4" in fmt_choice:
            qmap = {
                "Best Quality": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]",
                "720p":  "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
                "480p":  "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
                "360p":  "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]",
                "240p":  "bestvideo[height<=240][ext=mp4]+bestaudio[ext=m4a]/best[height<=240]",
                "144p":  "bestvideo[height<=144][ext=mp4]+bestaudio[ext=m4a]/best[height<=144]",
            }
            opts["format"] = qmap.get(quality, qmap["Best Quality"])
            opts["merge_output_format"] = "mp4"
        else:
            bmap = {"320 kbps": "320", "256 kbps": "256", "192 kbps": "192",
                    "128 kbps": "128", "96 kbps": "96"}
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": bmap.get(quality, "192"),
            }]
        return opts

    def _progress_hook(self, d):
        if self.stop_requested:
            raise yt_dlp.utils.DownloadError("Stopped by user")
        while self.pause_requested and not self.stop_requested:
            time.sleep(0.3)

        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            dl = d.get("downloaded_bytes", 0)
            speed = d.get("speed")
            if total > 0:
                pct = (dl / total) * 100
                speed_str = ""
                if speed:
                    if speed > 1024 ** 2:
                        speed_str = f"⚡ {speed / (1024 ** 2):.1f} MB/s"
                    else:
                        speed_str = f"⚡ {speed / 1024:.0f} KB/s"
                Clock.schedule_once(
                    lambda dt, p=pct, s=speed_str: self._update_prog(p, s), 0)
        elif d["status"] == "finished":
            Clock.schedule_once(
                lambda dt: self._update_prog(100, "Finalizing..."), 0)

    @mainthread
    def _update_prog(self, pct, speed_str):
        self.progress.value = pct
        self.pct_lbl.text = f"{pct:.1f}%"
        self.speed_lbl.text = speed_str
        if pct >= 100:
            self.now_lbl.text = "✅ Finalizing..."

    def _download_worker(self, url):
        try:
            opts = self.build_opts()
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            if not self.stop_requested:
                Clock.schedule_once(lambda dt: self._download_success(), 0)
        except yt_dlp.utils.DownloadError as e:
            if "stopped by user" in str(e).lower():
                Clock.schedule_once(lambda dt: self._download_stopped(), 0)
            else:
                err = str(e)
                Clock.schedule_once(lambda dt: self._download_error(err), 0)
        except Exception as e:
            err = str(e)
            Clock.schedule_once(lambda dt: self._download_error(err), 0)

    def _download_success(self):
        self.is_downloading = False
        self.progress.value = 100
        self.pct_lbl.text = "✅ 100%"
        self.now_lbl.text = "✅ Download completed!"
        self.update_status("✅ Download completed!", SUCCESS)
        self._reset_buttons()
        self.show_popup("✅ Success", f"Saved to:\n{self.download_path}")

    def _download_stopped(self):
        self.is_downloading = False
        self.update_status("⏹ Stopped by user", WARNING)
        self._reset_buttons()

    def _download_error(self, err):
        self.is_downloading = False
        self.update_status("❌ Download failed", DANGER)
        self._reset_buttons()
        self.show_popup("❌ Error", err[:200])

    def _reset_buttons(self):
        self.dl_btn.disabled = False
        self.dl_btn.text = "⬇  Download"
        self.fetch_btn.disabled = False
        self.pause_btn.disabled = True
        self.pause_btn.text = "⏸  Pause"
        self.stop_btn.disabled = True
        self.pause_requested = False

    def toggle_pause(self):
        if not self.is_downloading:
            return
        if self.pause_requested:
            self.pause_requested = False
            self.pause_btn.text = "⏸  Pause"
            self.update_status("▶ Resumed", WARNING)
        else:
            self.pause_requested = True
            self.pause_btn.text = "▶  Resume"
            self.update_status("⏸ Paused", PRIMARY)

    def stop_download(self):
        if self.is_downloading:
            self.stop_requested = True
            self.pause_requested = False
            self.update_status("⏳ Stopping...", WARNING)


if __name__ == "__main__":
    VideoDownloaderApp().run()
