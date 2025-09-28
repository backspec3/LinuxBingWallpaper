#!/usr/bin/env python3
"""
Linux Bing Wallpaper - Modern PyQt6 Version
美しく現代的なBing壁紙自動設定アプリ（8枚版）
"""

import sys
import os
import requests
import json
import subprocess
import threading
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget, QPushButton, QLabel, QFrame, QProgressBar, QListWidget,
    QListWidgetItem, QScrollArea, QMessageBox, QSystemTrayIcon,
    QMenu, QFileDialog, QSplitter, QGroupBox, QTextEdit, QSlider,
    QCheckBox, QComboBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, 
    QEasingCurve, QRect, QSize, QSettings, QStandardPaths
)
from PyQt6.QtGui import (
    QPixmap, QIcon, QFont, QPalette, QColor, QAction,
    QPainter, QBrush, QLinearGradient, QMovie
)

from PIL import Image

class WallpaperFetcher(QThread):
    """壁紙取得用ワーカースレッド"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, wallpaper_dir):
        super().__init__()
        self.wallpaper_dir = wallpaper_dir
        
    def run(self):
        try:
            self.progress.emit("Bing APIに接続中...")
            
            # Bing公式API（8枚取得）
            api_url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8&mkt=ja-JP"
            
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('images'):
                raise Exception("壁紙データが見つかりません")
            
            wallpapers = []
            for i, image_data in enumerate(data['images']):
                self.progress.emit(f"壁紙 {i+1}/8 をダウンロード中...")
                
                image_url = "https://www.bing.com" + image_data['url']
                title = image_data.get('title', '不明')
                copyright_info = image_data.get('copyright', '')
                date = image_data.get('startdate', 'unknown')
                
                # 画像をダウンロード
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                
                # ファイル名を生成
                filename = f"bing_wallpaper_{date}.jpg"
                file_path = self.wallpaper_dir / filename
                
                # 画像を保存
                with open(file_path, 'wb') as f:
                    f.write(img_response.content)
                
                wallpapers.append({
                    'path': str(file_path),
                    'title': title,
                    'copyright': copyright_info,
                    'date': date,
                    'url': image_url
                })
            
            self.finished.emit({'wallpapers': wallpapers})
            
        except Exception as e:
            self.error.emit(str(e))

class WallpaperWidget(QWidget):
    """壁紙プレビューウィジェット"""
    clicked = pyqtSignal(str)
    
    def __init__(self, wallpaper_info):
        super().__init__()
        self.wallpaper_info = wallpaper_info
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 画像プレビュー
        self.image_label = QLabel()
        self.image_label.setFixedSize(200, 110)  # 4列に収まるようサイズ調整
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #2d2d2d;
            }
            QLabel:hover {
                border-color: #2196F3;
                background-color: #1565C0;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.mousePressEvent = self.on_click
        
        # 壁紙を読み込み
        self.load_image()
        
        # タイトル
        title_label = QLabel(self.wallpaper_info['title'][:30] + "...")
        title_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFixedSize(200, 30)  # 画像プレビューと同じ幅、高さ30px
        
        # 日付
        date_label = QLabel(self.wallpaper_info['date'])
        date_label.setFont(QFont("Arial", 8))
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_label.setStyleSheet("color: #666;")
        date_label.setFixedSize(200, 20)  # 画像プレビューと同じ幅、高さ20px
        
        layout.addWidget(self.image_label)
        layout.addWidget(title_label)
        layout.addWidget(date_label)
        
        self.setLayout(layout)
        
    def load_image(self):
        """画像を読み込んでプレビュー表示"""
        try:
            pixmap = QPixmap(self.wallpaper_info['path'])
            if not pixmap.isNull():
                # アスペクト比を保持してリサイズ
                scaled_pixmap = pixmap.scaled(
                    200, 110, 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("プレビュー\n読み込み失敗")
        except Exception as e:
            self.image_label.setText("プレビュー\nエラー")
            
    def on_click(self, event):
        """クリック時の処理"""
        self.clicked.emit(self.wallpaper_info['path'])

class BingWallpaperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.wallpaper_dir = Path.home() / "Pictures" / "BingWallpapers"
        self.wallpaper_dir.mkdir(parents=True, exist_ok=True)
        
        self.wallpapers = []
        self.current_wallpaper = None
        
        # 設定
        self.settings = QSettings("BingWallpaper", "Settings")
        
        self.setup_ui()
        self.setup_style()
        self.setup_system_tray()
        
        # 自動更新タイマーを初期化（標準でオン）
        self.setup_auto_update()
        
        # 起動時に壁紙を取得
        QTimer.singleShot(1000, self.fetch_wallpapers)
        
    def setup_ui(self):
        """UIの設定"""
        self.setWindowTitle("Linux Bing Wallpaper")
        self.setGeometry(200, 200, 1300, 800)  # 幅を1300に拡大
        self.setMinimumSize(1300, 700)  # 最小サイズを設定
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # メインレイアウト
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        # 左側：コントロールパネル
        left_panel = self.create_control_panel()
        
        # 右側：壁紙ギャラリー
        right_panel = self.create_gallery_panel()
        
        # スプリッター
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([320, 980])  # 右側を大幅に拡大
        
        main_layout.addWidget(splitter)
        
    def create_control_panel(self):
        """コントロールパネルの作成"""
        panel = QFrame()
        panel.setFixedWidth(320)  # 幅を320に拡大
        layout = QVBoxLayout()
        
        # タイトル
        title_label = QLabel(" Bing Wallpaper")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 現在の壁紙情報
        current_group = QGroupBox("現在の壁紙")
        current_layout = QVBoxLayout()
        
        self.current_preview = QLabel()
        self.current_preview.setFixedSize(280, 160)  # サイズを拡大
        self.current_preview.setStyleSheet("""
            QLabel {
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #2d2d2d;
                color: #ffffff;
            }
        """)
        self.current_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_preview.setText("壁紙を選択してください")
        
        self.current_title = QLabel("タイトル: 未選択")
        self.current_title.setWordWrap(True)
        
        current_layout.addWidget(self.current_preview)
        current_layout.addWidget(self.current_title)
        current_group.setLayout(current_layout)
        
        # ボタン群
        button_group = QGroupBox("操作")
        button_layout = QVBoxLayout()
        
        self.fetch_btn = QPushButton("🔄 壁紙を更新")
        self.fetch_btn.clicked.connect(self.fetch_wallpapers)
        
        self.set_btn = QPushButton("🖥️ 壁紙を設定")
        self.set_btn.clicked.connect(self.set_wallpaper)
        self.set_btn.setEnabled(False)
        
        self.folder_btn = QPushButton("📁 フォルダを開く")
        self.folder_btn.clicked.connect(self.open_folder)
        
        self.auto_checkbox = QCheckBox("自動更新 (毎日)")
        self.auto_checkbox.setChecked(True)  # 標準でオン
        self.auto_checkbox.toggled.connect(self.toggle_auto_update)
        
        button_layout.addWidget(self.fetch_btn)
        button_layout.addWidget(self.set_btn)
        button_layout.addWidget(self.folder_btn)
        button_layout.addWidget(self.auto_checkbox)
        button_group.setLayout(button_layout)
        
        # デスクトップ環境設定
        desktop_group = QGroupBox("デスクトップ環境")
        desktop_layout = QVBoxLayout()
        
        self.desktop_combo = QComboBox()
        self.desktop_combo.addItems(["自動検出", "GNOME", "KDE", "XFCE", "その他 (feh)"])
        
        desktop_layout.addWidget(QLabel("デスクトップ環境:"))
        desktop_layout.addWidget(self.desktop_combo)
        desktop_group.setLayout(desktop_layout)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # ステータス
        self.status_label = QLabel("準備完了")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                border: 1px solid #404040;
                border-radius: 6px;
                background-color: #2d2d2d;
                color: #64B5F6;
                font-weight: bold;
            }
        """)
        
        # レイアウトに追加
        layout.addWidget(title_label)
        layout.addSpacing(10)
        layout.addWidget(current_group)
        layout.addSpacing(10)
        layout.addWidget(button_group)
        layout.addSpacing(10)
        layout.addWidget(desktop_group)
        layout.addStretch()
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        panel.setLayout(layout)
        return panel
        
    def create_gallery_panel(self):
        """ギャラリーパネルの作成"""
        panel = QFrame()
        layout = QVBoxLayout()
        
        # ギャラリータイトル
        gallery_title = QLabel("壁紙ギャラリー")
        gallery_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        # スクロールエリア
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout()
        self.gallery_layout.setSpacing(10)  # 4列に収まるよう間隔を調整
        self.gallery_widget.setLayout(self.gallery_layout)
        
        scroll_area.setWidget(self.gallery_widget)
        
        layout.addWidget(gallery_title)
        layout.addWidget(scroll_area)
        
        panel.setLayout(layout)
        return panel
        
    def setup_style(self):
        """ダークテーマスタイルの設定"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #2d2d2d;
                color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #2d2d2d;
                color: #64B5F6;
            }
            
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 18px;
                border-radius: 8px;
                font-weight: bold;
                min-height: 32px;
                font-size: 11px;
            }
            
            QPushButton:hover {
                background-color: #1976D2;
            }
            
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
            
            QComboBox {
                padding: 8px;
                border: 2px solid #404040;
                border-radius: 6px;
                background-color: #2d2d2d;
                color: #ffffff;
                min-height: 20px;
            }
            
            QComboBox:hover {
                border-color: #2196F3;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            
            QCheckBox {
                spacing: 8px;
                color: #ffffff;
            }
            
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            
            QCheckBox::indicator:unchecked {
                border: 2px solid #404040;
                border-radius: 4px;
                background-color: #2d2d2d;
            }
            
            QCheckBox::indicator:unchecked:hover {
                border-color: #2196F3;
            }
            
            QCheckBox::indicator:checked {
                border: 2px solid #2196F3;
                border-radius: 4px;
                background-color: #2196F3;
            }
            
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            
            QScrollArea {
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #1e1e1e;
            }
            
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #2196F3;
            }
            
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 6px;
                background-color: #2d2d2d;
                text-align: center;
                color: #ffffff;
            }
            
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 4px;
            }
        """)
        
    def setup_system_tray(self):
        """システムトレイの設定"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setToolTip("Bing Wallpaper")
            
            # アイコンを設定
            icon = QIcon.fromTheme("applications-graphics")
            if icon.isNull():
                # フォールバックアイコンを作成
                pixmap = QPixmap(16, 16)
                pixmap.fill(QColor("#2196F3"))
                icon = QIcon(pixmap)
            self.tray_icon.setIcon(icon)
            
            # システムトレイメニュー
            tray_menu = QMenu()
            
            show_action = QAction("表示", self)
            show_action.triggered.connect(self.show)
            
            fetch_action = QAction("壁紙を更新", self)
            fetch_action.triggered.connect(self.fetch_wallpapers)
            
            quit_action = QAction("終了", self)
            quit_action.triggered.connect(QApplication.instance().quit)
            
            tray_menu.addAction(show_action)
            tray_menu.addSeparator()
            tray_menu.addAction(fetch_action)
            tray_menu.addSeparator()
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def setup_auto_update(self):
        """自動更新の初期設定"""
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.fetch_wallpapers)
        self.auto_timer.start(24 * 60 * 60 * 1000)  # 24時間
        
    def tray_icon_activated(self, reason):
        """トレイアイコンクリック時の処理"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
        
    def fetch_wallpapers(self):
        """壁紙を更新して取得"""
        self.fetch_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("壁紙を取得中...")
        
        # 既存の壁紙をクリア
        self.clear_gallery()
        
        # ワーカースレッドで取得
        self.fetcher = WallpaperFetcher(self.wallpaper_dir)
        self.fetcher.finished.connect(self.on_wallpapers_fetched)
        self.fetcher.error.connect(self.on_fetch_error)
        self.fetcher.progress.connect(self.on_fetch_progress)
        self.fetcher.start()
        
    def on_wallpapers_fetched(self, result):
        """壁紙取得完了時の処理"""
        self.wallpapers = result['wallpapers']
        self.populate_gallery()
        
        self.fetch_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"✅ {len(self.wallpapers)}枚の壁紙を取得しました")
        
    def on_fetch_error(self, error_msg):
        """壁紙取得エラー時の処理"""
        self.fetch_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"❌ エラー: {error_msg}")
        
        QMessageBox.critical(self, "エラー", f"壁紙の取得に失敗しました:\n{error_msg}")
        
    def on_fetch_progress(self, message):
        """進捗更新"""
        self.status_label.setText(message)
        
    def clear_gallery(self):
        """ギャラリーをクリア"""
        while self.gallery_layout.count():
            child = self.gallery_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def populate_gallery(self):
        """ギャラリーに壁紙を表示（8枚を4x2配置）"""
        row, col = 0, 0
        max_cols = 4  # 4列で8枚を2行に配置
        
        for wallpaper in self.wallpapers:
            widget = WallpaperWidget(wallpaper)
            widget.clicked.connect(self.on_wallpaper_selected)
            
            self.gallery_layout.addWidget(widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
    def on_wallpaper_selected(self, wallpaper_path):
        """壁紙選択時の処理"""
        self.current_wallpaper = wallpaper_path
        
        # 選択された壁紙の情報を取得
        selected_info = None
        for wallpaper in self.wallpapers:
            if wallpaper['path'] == wallpaper_path:
                selected_info = wallpaper
                break
                
        if selected_info:
            # プレビューを更新
            pixmap = QPixmap(wallpaper_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    276, 156,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.current_preview.setPixmap(scaled_pixmap)
                
            # タイトルを更新
            self.current_title.setText(f"タイトル: {selected_info['title']}")
            
            # 設定ボタンを有効化
            self.set_btn.setEnabled(True)
            
            self.status_label.setText(f"壁紙を選択: {selected_info['title'][:30]}...")
            
    def set_wallpaper(self):
        """デスクトップ壁紙を設定"""
        if not self.current_wallpaper:
            QMessageBox.warning(self, "警告", "設定する壁紙を選択してください")
            return
            
        try:
            self.status_label.setText("壁紙を設定中...")
            
            # デスクトップ環境を取得
            desktop_env = self.get_desktop_environment()
            
            if desktop_env == "gnome":
                cmd = ["gsettings", "set", "org.gnome.desktop.background", 
                      "picture-uri", f"file://{self.current_wallpaper}"]
            elif desktop_env == "kde":
                # KDE Plasma用のコマンド（複数の方法を試す）
                kde_commands = [
                    ["plasma-apply-wallpaperimage", self.current_wallpaper],
                    ["qdbus", "org.kde.plasmashell", "/PlasmaShell", 
                     "setWallpaper", self.current_wallpaper],
                    ["qdbus-qt5", "org.kde.plasmashell", "/PlasmaShell", 
                     "setWallpaper", self.current_wallpaper]
                ]
                
                cmd = None
                for test_cmd in kde_commands:
                    try:
                        # コマンドが存在するかチェック
                        subprocess.run(["which", test_cmd[0]], check=True, 
                                     capture_output=True)
                        cmd = test_cmd
                        break
                    except subprocess.CalledProcessError:
                        continue
                        
                if not cmd:
                    raise Exception("KDE用の壁紙設定コマンドが見つかりません。\n"
                                  "plasma-apply-wallpaperimage または qdbus をインストールしてください。")
                    
            elif desktop_env == "xfce":
                cmd = ["xfconf-query", "-c", "xfce4-desktop", 
                      "-p", "/backdrop/screen0/monitor0/workspace0/last-image", 
                      "-s", self.current_wallpaper]
            else:
                # フォールバック：複数の選択肢を試す
                fallback_commands = [
                    ["feh", "--bg-scale", self.current_wallpaper],
                    ["nitrogen", "--set-scaled", self.current_wallpaper],
                    ["gsettings", "set", "org.gnome.desktop.background", 
                     "picture-uri", f"file://{self.current_wallpaper}"]
                ]
                
                cmd = None
                for test_cmd in fallback_commands:
                    try:
                        subprocess.run(["which", test_cmd[0]], check=True, 
                                     capture_output=True)
                        cmd = test_cmd
                        break
                    except subprocess.CalledProcessError:
                        continue
                        
                if not cmd:
                    raise Exception("壁紙設定用のコマンドが見つかりません。\n"
                                  "feh、nitrogen、またはgsettingsをインストールしてください。")
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.status_label.setText("✅ 壁紙を設定しました")
                
                # システムトレイに通知（ダイアログなし）
                if hasattr(self, 'tray_icon'):
                    self.tray_icon.showMessage(
                        "壁紙設定完了",
                        "Bing壁紙を設定しました",
                        QSystemTrayIcon.MessageIcon.Information,
                        3000
                    )
            else:
                raise Exception(f"コマンド実行エラー: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.status_label.setText("❌ タイムアウト")
            QMessageBox.critical(self, "エラー", "壁紙設定がタイムアウトしました")
        except FileNotFoundError:
            self.status_label.setText("❌ コマンドが見つかりません")
            QMessageBox.critical(self, "エラー", f"必要なコマンドが見つかりません\n"
                               f"デスクトップ環境: {desktop_env}")
        except Exception as e:
            self.status_label.setText("❌ 設定失敗")
            QMessageBox.critical(self, "エラー", f"壁紙の設定に失敗しました:\n{str(e)}")
            
    def get_desktop_environment(self):
        """デスクトップ環境を検出"""
        # コンボボックスの設定を確認
        selection = self.desktop_combo.currentText()
        if selection != "自動検出":
            return selection.lower()
            
        # 自動検出
        desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
        xdg_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        
        if 'gnome' in desktop_session or 'gnome' in xdg_desktop:
            return 'gnome'
        elif 'kde' in desktop_session or 'kde' in xdg_desktop or 'plasma' in desktop_session:
            return 'kde'
        elif 'xfce' in desktop_session or 'xfce' in xdg_desktop:
            return 'xfce'
        else:
            return 'other'
            
    def open_folder(self):
        """壁紙フォルダを開く"""
        try:
            subprocess.run(['xdg-open', str(self.wallpaper_dir)], check=True)
            self.status_label.setText("📁 フォルダを開きました")
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "エラー", "フォルダを開けませんでした")
            
    def toggle_auto_update(self, checked):
        """自動更新の切り替え"""
        if checked:
            # タイマーを再開
            if hasattr(self, 'auto_timer'):
                self.auto_timer.start(24 * 60 * 60 * 1000)  # 24時間
            else:
                self.setup_auto_update()
            self.status_label.setText("⏰ 自動更新を有効にしました")
        else:
            if hasattr(self, 'auto_timer'):
                self.auto_timer.stop()
            self.status_label.setText("自動更新を無効にしました")
            
    def closeEvent(self, event):
        """ウィンドウ閉じる時の処理"""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    app.setApplicationName("Bing Wallpaper")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("LinuxWallpaper")
    
    # アプリケーションアイコン設定
    app.setWindowIcon(QIcon.fromTheme("applications-graphics"))
    
    # メインウィンドウ作成
    window = BingWallpaperApp()
    window.show()
    
    # システムトレイアイコン表示
    if hasattr(window, 'tray_icon'):
        window.tray_icon.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
