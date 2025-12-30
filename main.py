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
    QCheckBox, QComboBox, QSpacerItem, QSizePolicy, QTabWidget
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

# ---------------------------------------------
# アイコン関連ユーティリティ
# ---------------------------------------------
# カスタムアイコンの基底候補ファイル
ICON_BASE_CANDIDATES = [
    ("assets", "bingwall-ico.png"),        
    ("asssets", "bingwall-ico.png"),       
    ("assets", "bingwall-icon.png"),       
    ("assets", "app_icon.png"),            
]

ICON_GENERATED_PATTERN = "app_icon_{size}x{size}.png"
ICON_SIZES = [16, 24, 32, 48, 64, 128, 256]

_generated_icon_cache = {}

def _find_base_icon():
    """利用可能な基底アイコンファイルを探索して最初に見つかったパスを返す"""
    script_dir = Path(__file__).parent
    for folder, filename in ICON_BASE_CANDIDATES:
        candidate = script_dir / folder / filename
        if candidate.exists():
            return candidate
    return None

def _generate_size_variants(base_path: Path):
    """指定された基底PNGから各サイズの派生アイコンを `assets` フォルダ内に生成（存在しなければ）。
    生成後パスをキャッシュしておく。失敗しても例外を伝播させずフォールバック可能。"""
    global _generated_icon_cache
    script_dir = Path(__file__).parent
    assets_dir = script_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    try:
        img = Image.open(base_path).convert("RGBA")
    except Exception as e:
        print(f"基底アイコン読み込み失敗: {e}")
        return

    for size in ICON_SIZES:
        out_path = assets_dir / ICON_GENERATED_PATTERN.format(size=size)
        if not out_path.exists():
            try:
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                resized.save(out_path, format="PNG")
            except Exception as e:
                print(f"アイコンサイズ生成失敗 {size}px: {e}")
                continue
        _generated_icon_cache[size] = out_path

def get_app_icon(size=64):
    """指定サイズのQIconを返す。
    1) 既に生成済みのサイズファイル(app_icon_{size}x{size}.png)があればそれを使用
    2) 基底アイコン (bingwall-ico.png など) から生成（初回のみ）
    3) 失敗時はフォールバック描画"""
    try:
        script_dir = Path(__file__).parent
        target_icon_path = script_dir / "assets" / ICON_GENERATED_PATTERN.format(size=size)
        if target_icon_path.exists():
            return QIcon(str(target_icon_path))

        # まだ生成されてない場合は基底アイコン探索→生成
        base_icon = _find_base_icon()
        if base_icon:
            _generate_size_variants(base_icon)
            if target_icon_path.exists():
                return QIcon(str(target_icon_path))
            # 生成後キャッシュにある別サイズからスケール（サイズ生成失敗時）
            if _generated_icon_cache:
                # 最も近いサイズを探してスケール
                nearest_size = min(_generated_icon_cache.keys(), key=lambda s: abs(s - size))
                pm = QPixmap(str(_generated_icon_cache[nearest_size]))
                if not pm.isNull():
                    scaled = pm.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    return QIcon(scaled)
        else:
            # 基底アイコンが見つからない → 従来フォールバック
            return create_fallback_icon(size)

        # ここまでで取得できなければフォールバック
        return create_fallback_icon(size)
    except Exception as e:
        print(f"アイコン取得エラー: {e}")
        return create_fallback_icon(size)

def create_fallback_icon(size=64):
    """フォールバックアイコンを作成"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # グラデーションを作成
    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor(33, 150, 243))  # Material Blue
    gradient.setColorAt(1, QColor(25, 118, 210))  # Darker Blue
    
    # 円を描画
    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, size-4, size-4)
    
    # 中央のカメラアイコン
    painter.setPen(QColor(255, 255, 255))
    painter.setBrush(QColor(255, 255, 255, 100))
    center = size // 2
    lens_radius = size // 4
    painter.drawEllipse(center-lens_radius, center-lens_radius, 
                       lens_radius*2, lens_radius*2)
    
    painter.end()
    return QIcon(pixmap)

class WallpaperFetcher(QThread):
    """壁紙取得用ワーカースレッド"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, wallpaper_dir, wallpaper_type="new"):
        super().__init__()
        self.wallpaper_dir = wallpaper_dir
        self.wallpaper_type = wallpaper_type  # "new" or "spotlight"
        
    def run(self):
        try:
            self.progress.emit("Bing APIに接続中...")
            
            # 壁紙タイプに応じてAPIエンドポイントを選択
            if self.wallpaper_type == "spotlight":
                # スポットライト壁紙（Bing Wallpaper Archiveからランダム取得）
                wallpapers = self.fetch_random_from_archive()
            else:
                # 新着壁紙API（8枚取得日本語版）
                api_url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8&mkt=ja-JP"
                response = requests.get(api_url, timeout=10)
                response.raise_for_status()
                data = response.json()
                wallpapers = self.fetch_new_wallpapers(data)
            
            self.finished.emit({'wallpapers': wallpapers})
            
        except Exception as e:
            self.error.emit(str(e))
    
    def fetch_random_from_archive(self):
        """Bing Wallpaper Archiveからランダムに8枚取得"""
        import random
        
        self.progress.emit("アーカイブAPIからメタデータを取得中...")
        
        # 日本のアーカイブAPIを取得
        archive_url = "https://bing.npanuhin.me/JP/ja.json"
        
        try:
            response = requests.get(archive_url, timeout=15)
            response.raise_for_status()
            archive_data = response.json()
            
            if not archive_data or len(archive_data) < 8:
                raise Exception("アーカイブデータが不足しています")
            
            self.progress.emit(f"アーカイブから{len(archive_data)}枚の壁紙を発見...")
            
            # ランダムに8枚選択
            selected_images = random.sample(archive_data, min(8, len(archive_data)))
            
            wallpapers = []
            for i, image_data in enumerate(selected_images):
                self.progress.emit(f"スポットライト壁紙 {i+1}/8 をダウンロード中...")
                
                # 画像URLを取得
                image_url = image_data.get('url')
                if not image_url:
                    continue
                
                title = image_data.get('title', '不明')
                copyright_info = image_data.get('copyright', '')
                date = image_data.get('date', 'unknown')
                description = image_data.get('description', '')
                
                # 画像をダウンロード
                try:
                    img_response = requests.get(image_url, timeout=30)
                    img_response.raise_for_status()
                    
                    # ファイル名を生成
                    filename = f"bing_archive_{date.replace('-', '')}.jpg"
                    file_path = self.wallpaper_dir / filename
                    
                    # 画像を保存
                    with open(file_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    wallpapers.append({
                        'path': str(file_path),
                        'title': title if title else description[:50] if description else date,
                        'copyright': copyright_info,
                        'date': date,
                        'url': image_url
                    })
                except Exception as e:
                    print(f"画像ダウンロードエラー ({date}): {e}")
                    continue
            
            return wallpapers
            
        except Exception as e:
            # フォールバック: 通常のBing APIを使用
            self.progress.emit("アーカイブ取得失敗、通常APIを使用...")
            api_url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=8&n=8&mkt=ja-JP"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return self.fetch_new_wallpapers(data)
    
    def fetch_new_wallpapers(self, data):
        """新着壁紙を処理"""
        wallpapers = []
        if not data.get('images'):
            raise Exception("壁紙データが見つかりません")
        
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
        
        return wallpapers

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
        self.spotlight_wallpapers = []
        self.current_wallpaper = None
        
        # ウィンドウアイコンを設定
        self.setWindowIcon(get_app_icon(64))
        
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
        title_label = QLabel(" Linux Bing Wallpaper")
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
        self.desktop_combo.addItems(["自動検出", "GNOME", "KDE", "XFCE", "COSMIC", "その他 (feh)"])
        
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
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        
        # 新着タブ
        new_tab = QWidget()
        new_layout = QVBoxLayout()
        
        scroll_area_new = QScrollArea()
        scroll_area_new.setWidgetResizable(True)
        scroll_area_new.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.gallery_widget = QWidget()
        self.gallery_layout = QGridLayout()
        self.gallery_layout.setSpacing(10)
        self.gallery_widget.setLayout(self.gallery_layout)
        
        scroll_area_new.setWidget(self.gallery_widget)
        new_layout.addWidget(scroll_area_new)
        new_tab.setLayout(new_layout)
        
        # スポットライトタブ
        spotlight_tab = QWidget()
        spotlight_layout = QVBoxLayout()
        
        scroll_area_spotlight = QScrollArea()
        scroll_area_spotlight.setWidgetResizable(True)
        scroll_area_spotlight.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.spotlight_gallery_widget = QWidget()
        self.spotlight_gallery_layout = QGridLayout()
        self.spotlight_gallery_layout.setSpacing(10)
        self.spotlight_gallery_widget.setLayout(self.spotlight_gallery_layout)
        
        scroll_area_spotlight.setWidget(self.spotlight_gallery_widget)
        spotlight_layout.addWidget(scroll_area_spotlight)
        spotlight_tab.setLayout(spotlight_layout)
        
        # タブに追加
        self.tab_widget.addTab(new_tab, "新着")
        self.tab_widget.addTab(spotlight_tab, "オススメ")
        
        # タブ切り替え時のイベント
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        layout.addWidget(gallery_title)
        layout.addWidget(self.tab_widget)
        
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
            
            QTabWidget::pane {
                border: 2px solid #404040;
                border-radius: 8px;
                background-color: #1e1e1e;
                top: -1px;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #404040;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 20px;
                margin-right: 2px;
                min-width: 120px;
            }
            
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: #ffffff;
                border-color: #2196F3;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #404040;
            }
        """)
        
    def setup_system_tray(self):
        """システムトレイの設定"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setToolTip("Bing Wallpaper")
            
            # アイコンを設定
            tray_icon = get_app_icon(32)  # トレイ用は小さめのアイコン
            self.tray_icon.setIcon(tray_icon)
            
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
        
        # 現在のタブに応じて取得する壁紙タイプを決定
        current_tab = self.tab_widget.currentIndex()
        wallpaper_type = "spotlight" if current_tab == 1 else "new"
        
        if wallpaper_type == "spotlight":
            self.status_label.setText("スポットライト壁紙を取得中...")
            self.clear_spotlight_gallery()
        else:
            self.status_label.setText("壁紙を取得中...")
            self.clear_gallery()
        
        # ワーカースレッドで取得
        self.fetcher = WallpaperFetcher(self.wallpaper_dir, wallpaper_type)
        self.fetcher.finished.connect(self.on_wallpapers_fetched)
        self.fetcher.error.connect(self.on_fetch_error)
        self.fetcher.progress.connect(self.on_fetch_progress)
        self.fetcher.start()
        
    def on_wallpapers_fetched(self, result):
        """壁紙取得完了時の処理"""
        # 現在のタブに応じて保存先を決定
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 1:  # スポットライトタブ
            self.spotlight_wallpapers = result['wallpapers']
            self.populate_spotlight_gallery()
            self.status_label.setText(f"✅ {len(self.spotlight_wallpapers)}枚のスポットライト壁紙を取得しました")
        else:  # 新着タブ
            self.wallpapers = result['wallpapers']
            self.populate_gallery()
            self.status_label.setText(f"✅ {len(self.wallpapers)}枚の壁紙を取得しました")
        
        self.fetch_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
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
    
    def clear_spotlight_gallery(self):
        """スポットライトギャラリーをクリア"""
        while self.spotlight_gallery_layout.count():
            child = self.spotlight_gallery_layout.takeAt(0)
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
    
    def populate_spotlight_gallery(self):
        """スポットライトギャラリーに壁紙を表示（8枚を4x2配置）"""
        row, col = 0, 0
        max_cols = 4  # 4列で8枚を2行に配置
        
        for wallpaper in self.spotlight_wallpapers:
            widget = WallpaperWidget(wallpaper)
            widget.clicked.connect(self.on_wallpaper_selected)
            
            self.spotlight_gallery_layout.addWidget(widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
    def on_wallpaper_selected(self, wallpaper_path):
        """壁紙選択時の処理"""
        self.current_wallpaper = wallpaper_path
        
        # 選択された壁紙の情報を取得（新着とスポットライト両方から探す）
        selected_info = None
        for wallpaper in self.wallpapers + self.spotlight_wallpapers:
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
    
    def on_tab_changed(self, index):
        """タブ切り替え時の処理"""
        if index == 0:
            self.status_label.setText("新着壁紙タブ")
        elif index == 1:
            self.status_label.setText("スポットライト壁紙タブ")
            # スポットライトタブに切り替えた際、まだ壁紙がなければ取得
            if not self.spotlight_wallpapers:
                QTimer.singleShot(500, self.fetch_wallpapers)
            
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
            elif desktop_env == "cosmic":
                # COSMIC環境用：設定ファイルを直接編集
                try:
                    cosmic_config_dir = Path.home() / ".config" / "cosmic" / "com.system76.CosmicBackground" / "v1"
                    config_file = cosmic_config_dir / "all"
                    
                    if config_file.exists():
                        # 既存の設定ファイルを読み込んで壁紙パスのみ更新
                        with open(config_file, 'r') as f:
                            content = f.read()
                        
                        # source: Path("...") の部分を置換
                        import re
                        new_content = re.sub(
                            r'source:\s*Path\(".*?"\)',
                            f'source: Path("{self.current_wallpaper}")',
                            content
                        )
                        
                        # 設定ファイルを書き込み
                        with open(config_file, 'w') as f:
                            f.write(new_content)
                        
                        # cosmic-bgプロセスを再起動して設定を反映
                        subprocess.run(["killall", "-HUP", "cosmic-bg"], 
                                     capture_output=True, timeout=5)
                        
                        self.status_label.setText("✅ 壁紙を設定しました（COSMIC）")
                        
                        if hasattr(self, 'tray_icon'):
                            self.tray_icon.showMessage(
                                "壁紙設定完了",
                                "Bing壁紙を設定しました",
                                QSystemTrayIcon.MessageIcon.Information,
                                3000
                            )
                        return
                    else:
                        raise Exception(f"COSMIC設定ファイルが見つかりません: {config_file}")
                        
                except Exception as cosmic_error:
                    # COSMICの設定に失敗した場合、フォールバックを試す
                    print(f"COSMIC設定エラー: {cosmic_error}")
                    fallback_commands = [
                        ["feh", "--bg-scale", self.current_wallpaper],
                    ]
                    
                    cmd = None
                    for test_cmd in fallback_commands:
                        try:
                            subprocess.run(["which", test_cmd[0]], check=True, 
                                         capture_output=True, timeout=5)
                            cmd = test_cmd
                            break
                        except subprocess.CalledProcessError:
                            continue
                            
                    if not cmd:
                        raise Exception(f"COSMIC壁紙設定に失敗しました: {cosmic_error}\n"
                                      "fehをインストールするか、手動で設定してください。")
                    
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
                import time
                
                wallpaper_path = os.path.abspath(self.current_wallpaper)
                
                # 壁紙ファイルが存在することを確認
                if not os.path.exists(wallpaper_path):
                    raise Exception(f"壁紙ファイルが見つかりません: {wallpaper_path}")
                
                # XFCE環境：複数の方法を順番に試す
                success = False
                
                # 方法1: xfconf-queryで既存プロパティを確認・設定
                try:
                    # 最初に、デスクトップの全プロパティを一覧取得
                    list_cmd = ["xfconf-query", "-c", "xfce4-desktop", "-l"]
                    list_result = subprocess.run(list_cmd, capture_output=True, text=True, timeout=10)
                    
                    if list_result.returncode == 0:
                        properties = list_result.stdout.strip().split('\n')
                        # 実在するlast-imageプロパティを探す
                        image_props = [p for p in properties if 'last-image' in p and p.strip()]
                        
                        if image_props:
                            # すべてのワークスペース/モニタに壁紙を設定
                            for prop in image_props:
                                cmd = ["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", wallpaper_path]
                                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                                if result.returncode == 0:
                                    success = True
                        else:
                            # プロパティが見つからない場合、作成を試みる
                            cmd = ["xfconf-query", "-c", "xfce4-desktop",
                                 "-p", "/backdrop/screen0/monitor0/workspace0/last-image",
                                 "-t", "string", "-s", wallpaper_path, "--create"]
                            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                            if result.returncode == 0:
                                success = True
                except Exception:
                    pass
                
                if success:
                    # 設定が実際に保存されたか確認
                    time.sleep(0.5)
                    
                    # xfdesktopを再起動
                    # 1. xfdesktopを複数の方法で終了
                    subprocess.run(["killall", "-9", "xfdesktop"], capture_output=True, timeout=5)
                    time.sleep(1)
                    
                    # 2. xfdesktopをENVを設定して再起動
                    env = os.environ.copy()
                    env['DISPLAY'] = os.environ.get('DISPLAY', ':0')
                    
                    # xfdesktopを複数プロセス立ち上げ対策
                    subprocess.run(["pkill", "-f", "xfdesktop"], capture_output=True, timeout=5)
                    time.sleep(0.5)
                    
                    # 新しいxfdesktopプロセスを起動
                    subprocess.Popen(
                        ["xfdesktop", "--sm-client-disable"],
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    
                    time.sleep(4)  # 十分に待機
                    
                    self.status_label.setText("✅ 壁紙を設定しました")
                    
                    if hasattr(self, 'tray_icon'):
                        self.tray_icon.showMessage(
                            "壁紙設定完了",
                            "Bing壁紙を設定しました",
                            QSystemTrayIcon.MessageIcon.Information,
                            3000
                        )
                    return
                
                # 方法2: feh/nitrogenをフォールバックで試す
                fallback_commands = [
                    ["feh", "--bg-scale", wallpaper_path],
                    ["nitrogen", "--set-scaled", wallpaper_path],
                ]
                
                for fb_cmd in fallback_commands:
                    try:
                        # コマンドが存在するか確認
                        which_result = subprocess.run(["which", fb_cmd[0]], capture_output=True, timeout=5)
                        if which_result.returncode == 0:
                            result = subprocess.run(fb_cmd, capture_output=True, text=True, timeout=10)
                            if result.returncode == 0:
                                self.status_label.setText("✅ 壁紙を設定しました")
                                
                                if hasattr(self, 'tray_icon'):
                                    self.tray_icon.showMessage(
                                        "壁紙設定完了",
                                        "Bing壁紙を設定しました",
                                        QSystemTrayIcon.MessageIcon.Information,
                                        3000
                                    )
                                return
                    except subprocess.CalledProcessError:
                        continue
                    except Exception:
                        continue
                
                # すべて失敗した場合
                raise Exception("XFCE壁紙設定に失敗しました。\n"
                              "feh、nitrogen、またはxfconf-queryをインストールしてください。")
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
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
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
        
        if 'cosmic' in desktop_session or 'cosmic' in xdg_desktop:
            return 'cosmic'
        elif 'gnome' in desktop_session or 'gnome' in xdg_desktop:
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
    app_icon = get_app_icon(64)
    app.setWindowIcon(app_icon)
    
    # メインウィンドウ作成
    window = BingWallpaperApp()
    window.show()
    
    # システムトレイアイコン表示
    if hasattr(window, 'tray_icon'):
        window.tray_icon.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
