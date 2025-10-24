# LinuxBingWallpaper - Bing壁紙自動設定アプリ

美しく現代的なLinux用Bing壁紙自動設定アプリケーション

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 概要

LinuxBingWallpaperは、Microsoftの美しいBing日替わり壁紙を自動的に取得し、Linux環境でデスクトップ壁紙として設定するPyQt6アプリケーションです。

### 主な機能

- 📸 **最新のBing壁紙を8枚取得** - Bing公式APIから高画質壁紙を自動ダウンロード
- 🖼️ **プレビュー機能** - 壁紙をグリッド形式で確認してから設定
- 🎨 **複数DE対応** - GNOME、KDE、XFCE、LXQt、その他のデスクトップ環境に対応
- ⏰ **自動更新機能** - 24時間ごとに新しい壁紙を自動取得
- 🔄 **システムトレイ** - バックグラウンド動作とトレイアイコン
- 📁 **壁紙管理** - ローカルフォルダでの壁紙ファイル管理
- 🌐 **日本語対応** - 完全日本語インターフェース


## 必要条件

### システム要件
- Python 3.8以上
- Linux OS（Ubuntu、Fedora、openSUSE、Arch Linux等）
- インターネット接続
- デスクトップ環境（GNOME、KDE、XFCE、LXQt等）

### 必要なパッケージ
```bash
# Ubuntu/Debian
sudo apt install python3-pip python3-pyqt6 python3-pil

# Fedora
sudo dnf install python3-pip python3-PyQt6 python3-pillow

# Arch Linux
sudo pacman -S python-pip python-pyqt6 python-pillow

# openSUSE
sudo zypper install python3-pip python3-qt6 python3-Pillow
```

## インストール

### 1. リポジトリのクローン
```bash
git clone https://github.com/backspec3/LinuxWallpaper.git
cd LinuxBingWallpaper
```

### 2. 依存関係のインストール
```bash
pip3 install -r requirements.txt
```

または手動でインストール：
```bash
pip3 install PyQt6 Pillow requests
```

### 3. 実行権限の付与
```bash
chmod +x main.py
```

## 使用方法

### 基本的な使い方

1. **アプリケーションの起動**
   ```bash
   python3 main.py
   ```

2. **壁紙の取得**
   - 「壁紙を取得」ボタンをクリック
   - Bingから最新の8枚の壁紙を自動ダウンロード

3. **壁紙の設定**
   - プレビューグリッドから気に入った壁紙をクリック
   - 壁紙に設定ボタンでデスクトップ壁紙として設定

4. **自動更新の有効化**
   - 「自動更新」チェックボックスを有効化
   - 24時間ごとに新しい壁紙を自動取得

### 詳細機能

- **フォルダを開く**: ダウンロードした壁紙ファイルを確認
- **システムトレイ**: ウィンドウを閉じてもバックグラウンドで動作
- **設定の自動保存**: 次回起動時に設定を復元

## 対応デスクトップ環境

KDE環境でのみテストしています、他のデスクトップ環境での動作はテスト出来ていません
| デスクトップ環境 | 対応状況 | 設定方法 |
|---|---|---|
| GNOME | ✅ 対応 | gsettings |
| KDE Plasma | ✅ 完全対応 | qdbus |
| XFCE | ✅ 対応 | xfconf-query |
| LXQt | ✅ 対応 | pcmanfm-qt |
| Cinnamon | ✅ 対応 | gsettings |
| MATE | ✅ 対応 | gsettings |
| その他 | 🔶 部分対応 | feh使用 |

## ファイル構成

```
LinuxBingWallpaper/
├── main.py              # メインアプリケーション
├── README.md            # このファイル
├── requirements.txt     # Python依存関係
└── wallpapers/         # 壁紙保存フォルダ（自動作成）
    ├── bing_wallpaper_20250101.jpg
    ├── bing_wallpaper_20250102.jpg
    └── ...
```

## 設定ファイル

設定は以下に自動保存されます：
- `~/.config/LinuxBingWallpaper/settings.ini`

## トラブルシューティング

### よくある問題と解決方法

1. **PyQt6がインストールできない**
   ```bash
   # システムパッケージマネージャーを使用
   sudo apt install python3-pyqt6  # Ubuntu
   sudo dnf install python3-PyQt6  # Fedora
   ```

2. **壁紙が設定されない**
   - デスクトップ環境を確認
   - 必要なツール（gsettings、qdbus等）がインストールされているか確認

3. **インターネット接続エラー**
   - ファイアウォール設定を確認
   - プロキシ環境の場合は環境変数を設定

4. **権限エラー**
   ```bash
   chmod +x main.py
   chmod -R 755 ~/.config/LinuxBingWallpaper/
   ```

### ログとデバッグ

アプリケーションは標準出力にログを出力します：
```bash
python3 main.py 2>&1 | tee wallpaper.log
```

## 開発者向け情報

### アーキテクチャ

- **WallpaperFetcher**: Bing APIからの壁紙取得を担当するワーカースレッド
- **WallpaperWidget**: 個別壁紙のプレビューウィジェット
- **BingWallpaperApp**: メインアプリケーションウィンドウ

### APIエンドポイント

```python
# Bing壁紙API（8枚取得）
api_url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8&mkt=ja-JP"
```

### 拡張とカスタマイズ

新しいデスクトップ環境のサポートを追加する場合：

```python
def detect_desktop_environment(self):
    """デスクトップ環境の検出"""
    # 新しい環境の検出ロジックを追加
    
def set_wallpaper_your_de(self, image_path):
    """新しいDE用の壁紙設定"""
    # 壁紙設定コマンドを実装
```

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照してください。


## 作者

- **backspec3** - [GitHub](https://github.com/backspec3)

## 謝辞

- Microsoft Bingチーム - 美しい壁紙の提供
- PyQt6コミュニティ - 優秀なGUIフレームワーク
- Linuxコミュニティ - オープンソースエコシステム

## 更新履歴

### v2.0 (2025-9-28)
- PyQt6への移行
- 8枚壁紙同時表示機能
- システムトレイサポート
- 自動更新機能

### v1.0 (2025-9-20)
- 初回リリース
- 基本的な壁紙取得・設定機能

---

⭐ このプロジェクトが気に入ったら、ぜひスターを付けてください！