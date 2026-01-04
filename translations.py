#!/usr/bin/env python3
"""
翻訳管理モジュール
UI文字列の日本語/英語を管理
"""

TRANSLATIONS = {
    "ja": {
        # ウィンドウとタイトル
        "window_title": "Linux Bing Wallpaper",
        "app_name": "Bing Wallpaper",
        "app_version": "2.0",
        "organization": "LinuxWallpaper",
        
        # コントロールパネル
        "current_wallpaper": "現在の壁紙",
        "select_wallpaper": "壁紙を選択してください",
        "title_label": "タイトル: 未選択",
        "operations": "操作",
        "fetch_btn": "🔄 壁紙を更新",
        "set_btn": "🖥️ 壁紙を設定",
        "folder_btn": "📁 フォルダを開く",
        "auto_update": "自動更新 (毎日)",
        "desktop_env": "デスクトップ環境",
        "desktop_env_label": "デスクトップ環境:",
        "auto_detect": "自動検出",
        "gnome": "GNOME",
        "kde": "KDE",
        "xfce": "XFCE",
        "cosmic": "COSMIC",
        "other": "その他 (feh)",
        "ready": "準備完了",
        
        # ギャラリー
        "gallery_title": "壁紙ギャラリー",
        "new_tab": "新着",
        "spotlight_tab": "オススメ",
        "preview_loading_failed": "プレビュー\n読み込み失敗",
        "preview_error": "プレビュー\nエラー",
        
        # 処理メッセージ
        "fetching_api": "Bing APIに接続中...",
        "fetching_archive": "アーカイブAPIからメタデータを取得中...",
        "fetching_archive_found": "アーカイブから{count}枚の壁紙を発見...",
        "downloading_spotlight": "スポットライト壁紙 {current}/{total} をダウンロード中...",
        "fetching_spotlight": "スポットライト壁紙を取得中...",
        "fetching_wallpapers": "壁紙を取得中...",
        "downloading": "壁紙 {current}/{total} をダウンロード中...",
        "wallpaper_not_found": "壁紙データが見つかりません",
        "fetched_success_spotlight": "✅ {count}枚のスポットライト壁紙を取得しました",
        "fetched_success": "✅ {count}枚の壁紙を取得しました",
        "error_prefix": "❌ エラー: ",
        "setting_wallpaper": "壁紙を設定中...",
        "wallpaper_set_success": "✅ 壁紙を設定しました",
        "wallpaper_set_success_cosmic": "✅ 壁紙を設定しました（COSMIC）",
        "selected_wallpaper": "壁紙を選択: {title}...",
        "new_tab_msg": "新着壁紙タブ",
        "spotlight_tab_msg": "スポットライト壁紙タブ",
        "folder_opened": "📁 フォルダを開きました",
        "auto_update_on": "⏰ 自動更新を有効にしました",
        "auto_update_off": "自動更新を無効にしました",
        "timeout": "❌ タイムアウト",
        "command_not_found": "❌ コマンドが見つかりません",
        "setting_failed": "❌ 設定失敗",
        
        # ダイアログ
        "warning": "警告",
        "select_wallpaper_dialog": "設定する壁紙を選択してください",
        "error": "エラー",
        "no_wallpaper_selected": "�定する壁紙を選択してください",
        "timeout_msg": "壁紙設定がタイムアウトしました",
        "command_not_found_msg": "必要なコマンドが見つかりません\nデスクトップ環境: {env}",
        "set_wallpaper_failed": "壁紙の設定に失敗しました:\n{error}",
        "folder_open_failed": "フォルダを開けませんでした",
        "archive_not_found": "アーカイブデータが不足しています",
        
        # トレイメニュー
        "show": "表示",
        "quit": "終了",
        "tray_tooltip": "Bing Wallpaper",
        "notification_title": "壁紙設定完了",
        "notification_msg": "Bing壁紙を設定しました",
        
        # 言語メニュー
        "language": "言語",
        "japanese": "日本語",
        "english": "English",
    },
    
    "en": {
        # ウィンドウとタイトル
        "window_title": "Linux Bing Wallpaper",
        "app_name": "Bing Wallpaper",
        "app_version": "2.0",
        "organization": "LinuxWallpaper",
        
        # コントロールパネル
        "current_wallpaper": "Current Wallpaper",
        "select_wallpaper": "Select a wallpaper",
        "title_label": "Title: Not selected",
        "operations": "Operations",
        "fetch_btn": "🔄 Fetch Wallpapers",
        "set_btn": "🖥️ Set Wallpaper",
        "folder_btn": "📁 Open Folder",
        "auto_update": "Auto-update (Daily)",
        "desktop_env": "Desktop Environment",
        "desktop_env_label": "Desktop Environment:",
        "auto_detect": "Auto-detect",
        "gnome": "GNOME",
        "kde": "KDE",
        "xfce": "XFCE",
        "cosmic": "COSMIC",
        "other": "Other (feh)",
        "ready": "Ready",
        
        # ギャラリー
        "gallery_title": "Wallpaper Gallery",
        "new_tab": "Latest",
        "spotlight_tab": "Recommended",
        "preview_loading_failed": "Preview\nFailed to load",
        "preview_error": "Preview\nError",
        
        # 処理メッセージ
        "fetching_api": "Connecting to Bing API...",
        "fetching_archive": "Fetching metadata from archive...",
        "fetching_archive_found": "Found {count} wallpapers in archive...",
        "downloading_spotlight": "Downloading spotlight wallpaper {current}/{total}...",
        "fetching_spotlight": "Fetching spotlight wallpapers...",
        "fetching_wallpapers": "Fetching wallpapers...",
        "downloading": "Downloading wallpaper {current}/{total}...",
        "wallpaper_not_found": "No wallpaper data found",
        "fetched_success_spotlight": "✅ Successfully fetched {count} spotlight wallpapers",
        "fetched_success": "✅ Successfully fetched {count} wallpapers",
        "error_prefix": "❌ Error: ",
        "setting_wallpaper": "Setting wallpaper...",
        "wallpaper_set_success": "✅ Wallpaper set successfully",
        "wallpaper_set_success_cosmic": "✅ Wallpaper set successfully (COSMIC)",
        "selected_wallpaper": "Selected wallpaper: {title}...",
        "new_tab_msg": "Latest wallpapers tab",
        "spotlight_tab_msg": "Recommended wallpapers tab",
        "folder_opened": "📁 Folder opened",
        "auto_update_on": "⏰ Auto-update enabled",
        "auto_update_off": "Auto-update disabled",
        "timeout": "❌ Timeout",
        "command_not_found": "❌ Command not found",
        "setting_failed": "❌ Setting failed",
        
        # ダイアログ
        "warning": "Warning",
        "select_wallpaper_dialog": "Select a wallpaper to set",
        "error": "Error",
        "no_wallpaper_selected": "Select a wallpaper to set",
        "timeout_msg": "Wallpaper setting timed out",
        "command_not_found_msg": "Required command not found\nDesktop environment: {env}",
        "set_wallpaper_failed": "Failed to set wallpaper:\n{error}",
        "folder_open_failed": "Failed to open folder",
        "archive_not_found": "Insufficient archive data",
        
        # トレイメニュー
        "show": "Show",
        "quit": "Quit",
        "tray_tooltip": "Bing Wallpaper",
        "notification_title": "Wallpaper Setup Complete",
        "notification_msg": "Bing wallpaper has been set",
        
        # 言語メニュー
        "language": "Language",
        "japanese": "日本語",
        "english": "English",
    }
}

class TranslationManager:
    """翻訳管理クラス"""
    
    def __init__(self, language="ja"):
        self.current_language = language
        
    def set_language(self, language):
        """言語を設定"""
        if language in TRANSLATIONS:
            self.current_language = language
            
    def get(self, key, **kwargs):
        """翻訳を取得"""
        translation = TRANSLATIONS.get(self.current_language, {}).get(key, key)
        
        # フォーマット引数がある場合は置換
        if kwargs:
            try:
                return translation.format(**kwargs)
            except KeyError:
                return translation
        return translation
    
    def __(self, key, **kwargs):
        """短い別名"""
        return self.get(key, **kwargs)


# グローバルインスタンス
_translation_manager = None

def get_translation_manager():
    """グローバル翻訳マネージャーを取得"""
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager("ja")
    return _translation_manager

def __(key, **kwargs):
    """翻訳ショートカット"""
    return get_translation_manager().get(key, **kwargs)

def set_language(language):
    """言語を設定"""
    get_translation_manager().set_language(language)

def get_language():
    """現在の言語を取得"""
    return get_translation_manager().current_language
