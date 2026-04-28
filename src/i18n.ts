import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  en: {
    translation: {
      "title": "Linux Bing Wallpaper",
      "current_selection": "Current Selection",
      "select_wallpaper": "Select a wallpaper",
      "title_not_selected": "Title: Not selected",
      "fetch_wallpapers": "Fetch Wallpapers",
      "set_wallpaper": "Set Wallpaper",
      "open_folder": "Open Folder",
      "desktop_environment": "Desktop Environment",
      "latest_wallpapers": "Latest Wallpapers",
      "spotlight_archive": "Spotlight Archive",
      "loading_wallpapers": "Loading wallpapers...",
      "ready": "Ready",
      "fetching_wallpapers": "Fetching {{type}} wallpapers...",
      "successfully_fetched": "Successfully fetched {{type}} wallpapers.",
      "error": "Error: {{error}}",
      "setting_wallpaper": "Setting wallpaper...",
      "wallpaper_set_success": "✅ Wallpaper set successfully!",
      "failed_to_set": "❌ Failed to set wallpaper: {{error}}",
      "failed_to_open": "❌ Failed to open folder: {{error}}",
      "tabs": {
        "new": "latest",
        "spotlight": "spotlight"
      },
      "de": {
        "auto_detect": "Auto-detect",
        "gnome": "GNOME",
        "kde": "KDE Plasma",
        "xfce": "XFCE",
        "cosmic": "COSMIC",
        "other": "Other (feh)"
      },
      "language": "Language"
    }
  },
  ja: {
    translation: {
      "title": "Linux Bing 壁紙",
      "current_selection": "現在の選択",
      "select_wallpaper": "壁紙を選択してください",
      "title_not_selected": "タイトル: 未選択",
      "fetch_wallpapers": "壁紙を取得",
      "set_wallpaper": "壁紙に設定",
      "open_folder": "フォルダを開く",
      "desktop_environment": "デスクトップ環境",
      "latest_wallpapers": "最新の壁紙",
      "spotlight_archive": "スポットライト アーカイブ",
      "loading_wallpapers": "壁紙を読み込み中...",
      "ready": "準備完了",
      "fetching_wallpapers": "{{type}} 壁紙を取得中...",
      "successfully_fetched": "{{type}} 壁紙の取得に成功しました。",
      "error": "エラー: {{error}}",
      "setting_wallpaper": "壁紙を設定中...",
      "wallpaper_set_success": "✅ 壁紙の設定が完了しました！",
      "failed_to_set": "❌ 壁紙の設定に失敗しました: {{error}}",
      "failed_to_open": "❌ フォルダを開けませんでした: {{error}}",
      "tabs": {
        "new": "最新",
        "spotlight": "スポットライト"
      },
      "de": {
        "auto_detect": "自動検出",
        "gnome": "GNOME",
        "kde": "KDE Plasma",
        "xfce": "XFCE",
        "cosmic": "COSMIC",
        "other": "その他 (feh)"
      },
      "language": "言語"
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
