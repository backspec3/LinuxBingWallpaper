# LinuxWallpaper - Bing壁紙自動設定アプリ

美しく現代的なLinux用Bing壁紙自動設定アプリケーション

## 目次

- [概要](#概要)
- [スクリーンショット](#スクリーンショット)
- [主な機能](#主な機能)
- [必要条件](#必要条件)
- [インストール](#インストール)
- [使用方法](#使用方法)
- [対応デスクトップ環境](#対応デスクトップ環境)
- [ファイル構成](#ファイル構成)
- [トラブルシューティング](#トラブルシューティング)
- [開発者向け情報](#開発者向け情報)
- [アンインストール](#アンインストール)
- [ライセンス](#ライセンス)
- [貢献](#貢献)
- [関連プロジェクト](#関連プロジェクト)
- [更新履歴](#更新履歴)

---

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux-orange.svg)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

## 概要

LinuxWallpaperは、Microsoftの美しいBing日替わり壁紙を自動的に取得し、Linux環境でデスクトップ壁紙として設定するPyQt6アプリケーションです。

## スクリーンショット

![メインウィンドウ](assets/screenshot-main.png)
*メインウィンドウ - 8枚の壁紙をグリッド表示*

> **注意**: スクリーンショット画像は `assets` フォルダに追加してください。

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
- **Python**: 3.8以上
- **OS**: Linux（Ubuntu、Fedora、openSUSE、Arch Linux等）
- **メモリ**: 最低256MB RAM（推奨512MB以上）
- **ディスク容量**: 約50MB（アプリ本体 + 壁紙保存用）
- **インターネット接続**: 壁紙ダウンロード時に必要
- **デスクトップ環境**: GNOME、KDE、XFCE、LXQt等

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

### クイックスタート

最速でアプリを起動したい場合：

```bash
# リポジトリをクローン
git clone https://github.com/backspec3/LinuxWallpaper.git
cd LinuxWallpaper

# 依存関係をインストール
pip3 install -r requirements.txt

# アプリケーションを起動
python3 main.py
```

### 詳細なインストール手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/backspec3/LinuxWallpaper.git
cd LinuxWallpaper
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

### 4. インストールの確認
```bash
# Python バージョンの確認
python3 --version  # 3.8以上が必要

# 依存関係のチェック
python3 -c "import PyQt6; import PIL; import requests; print('すべての依存関係が正常にインストールされています')"
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

### パフォーマンスとヒント

- 💡 **初回起動時**: 8枚の壁紙のダウンロードには数秒かかります
- 💡 **ディスク容量**: 各壁紙は約1-2MBです
- 💡 **メモリ使用量**: アプリは約50-100MBのメモリを使用します
- 💡 **バックグラウンド動作**: システムトレイで最小化すると、リソース使用量が削減されます
- 💡 **自動更新**: 自動更新機能を使用すると、毎日新しい壁紙が自動的に取得されます

## 対応デスクトップ環境

| デスクトップ環境 | 対応状況 | 設定方法 |
|---|---|---|
| GNOME | ✅ 完全対応 | gsettings |
| KDE Plasma | ✅ 完全対応 | qdbus |
| XFCE | ✅ 完全対応 | xfconf-query |
| LXQt | ✅ 完全対応 | pcmanfm-qt |
| Cinnamon | ✅ 対応 | gsettings |
| MATE | ✅ 対応 | gsettings |
| その他 | 🔶 部分対応 | feh使用 |

## ファイル構成

```
LinuxWallpaper/
├── main.py                    # メインアプリケーション
├── README.md                  # このファイル
├── requirements.txt           # Python依存関係
├── LICENSE                    # MITライセンス
├── assets/                    # アプリケーションリソース
│   ├── bingwall-icon.png     # アプリアイコン（基本）
│   ├── app_icon_16x16.png    # アイコン（16x16）
│   ├── app_icon_32x32.png    # アイコン（32x32）
│   ├── app_icon_64x64.png    # アイコン（64x64）
│   └── ...                    # その他のアイコンサイズ
└── ~/Pictures/BingWallpapers/ # 壁紙保存フォルダ（自動作成）
    ├── bing_wallpaper_20250101.jpg
    ├── bing_wallpaper_20250102.jpg
    └── ...
```

### 設定とキャッシュ

```
~/.config/LinuxWallpaper/
└── settings.ini               # アプリケーション設定（自動作成）
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. PyQt6がインストールできない

**問題**: pip installでPyQt6がインストールできない

**解決方法**:
```bash
# システムパッケージマネージャーを使用
sudo apt install python3-pyqt6  # Ubuntu/Debian
sudo dnf install python3-PyQt6  # Fedora
sudo pacman -S python-pyqt6     # Arch Linux
sudo zypper install python3-qt6 # openSUSE
```

#### 2. 壁紙が設定されない

**問題**: 「壁紙を設定」ボタンを押しても壁紙が変わらない

**解決方法**:
- デスクトップ環境を確認
  ```bash
  echo $DESKTOP_SESSION
  echo $XDG_CURRENT_DESKTOP
  ```
- 必要なツールがインストールされているか確認
  ```bash
  # GNOME の場合
  which gsettings
  
  # KDE の場合
  which plasma-apply-wallpaperimage
  which qdbus
  
  # XFCE の場合
  which xfconf-query
  
  # その他の環境
  which feh
  ```
- 手動でコマンドラインからテスト
  ```bash
  # GNOME
  gsettings set org.gnome.desktop.background picture-uri file:///path/to/wallpaper.jpg
  
  # KDE
  plasma-apply-wallpaperimage /path/to/wallpaper.jpg
  
  # その他
  feh --bg-scale /path/to/wallpaper.jpg
  ```

#### 3. インターネット接続エラー

**問題**: 「壁紙を取得」時にネットワークエラーが発生する

**解決方法**:
- インターネット接続を確認
  ```bash
  ping -c 3 www.bing.com
  ```
- ファイアウォール設定を確認
  ```bash
  sudo ufw status  # UFW使用時
  ```
- プロキシ環境の場合は環境変数を設定
  ```bash
  export http_proxy="http://proxy.example.com:8080"
  export https_proxy="https://proxy.example.com:8080"
  ```

#### 4. 権限エラー

**問題**: ファイルの読み書きで権限エラーが発生する

**解決方法**:
```bash
# 実行権限を付与
chmod +x main.py

# 設定ディレクトリの権限を修正
chmod -R 755 ~/.config/LinuxWallpaper/

# 壁紙保存先の権限を確認
ls -ld ~/Pictures/BingWallpapers/
```

#### 5. アプリケーションが起動しない

**問題**: `python3 main.py` を実行してもアプリが起動しない

**解決方法**:
```bash
# 詳細なエラーメッセージを確認
python3 main.py 2>&1 | tee error.log

# 必要なライブラリを再インストール
pip3 install --upgrade --force-reinstall PyQt6 Pillow requests
```

### ログとデバッグ

アプリケーションは標準出力にログを出力します：
```bash
python3 main.py 2>&1 | tee wallpaper.log
```

### よくある質問（FAQ）

**Q: 壁紙は自動的に保存されますか？**  
A: はい、ダウンロードした壁紙は `~/Pictures/BingWallpapers/` に自動的に保存されます。

**Q: 何枚まで壁紙を保存できますか？**  
A: 制限はありません。古い壁紙を削除したい場合は、フォルダを手動でクリーンアップしてください。

**Q: オフラインでも動作しますか？**  
A: 既にダウンロード済みの壁紙は設定できますが、新しい壁紙の取得にはインターネット接続が必要です。

**Q: カスタム壁紙を追加できますか？**  
A: 現在のバージョンではBing壁紙のみに対応しています。将来のバージョンで機能追加を予定しています。

**Q: 複数モニターに対応していますか？**  
A: デスクトップ環境の設定に依存します。ほとんどの環境では全モニターに同じ壁紙が設定されます。

## 開発者向け情報

### アーキテクチャ

LinuxWallpaperは以下のコンポーネントで構成されています：

- **WallpaperFetcher**: Bing APIからの壁紙取得を担当するワーカースレッド
  - 非同期でBing APIにアクセス
  - 8枚の壁紙を並列ダウンロード
  - エラーハンドリングと進捗報告

- **WallpaperWidget**: 個別壁紙のプレビューウィジェット
  - サムネイル表示とクリック検出
  - ホバーエフェクト
  - 壁紙メタデータ表示

- **BingWallpaperApp**: メインアプリケーションウィンドウ
  - UIレイアウト管理
  - デスクトップ環境検出
  - 壁紙設定ロジック
  - システムトレイ統合

### 技術スタック

| 技術 | 用途 |
|------|------|
| PyQt6 | GUI フレームワーク |
| Pillow | 画像処理・リサイズ |
| requests | HTTP通信 |
| subprocess | システムコマンド実行 |
| QSettings | 設定の永続化 |

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

### ローカル開発環境のセットアップ

```bash
# 開発用の仮想環境を作成
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows (WSL使用時)

# 開発依存関係をインストール
pip install -r requirements.txt

# アプリケーションを実行
python3 main.py
```

## アンインストール

アプリケーションを完全に削除する場合：

```bash
# 1. アプリケーションディレクトリを削除
cd /path/to/LinuxWallpaper/parent
rm -rf LinuxWallpaper

# 2. 設定ファイルを削除
rm -rf ~/.config/LinuxWallpaper

# 3. ダウンロードした壁紙を削除（オプション）
rm -rf ~/Pictures/BingWallpapers

# 4. Python依存関係を削除（他のアプリで使用していない場合）
pip3 uninstall PyQt6 Pillow requests
```

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 貢献

プロジェクトへの貢献を歓迎します！

### 貢献方法

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

### 貢献ガイドライン

- コードはPEP 8スタイルガイドに従ってください
- 新機能には適切なコメントを追加してください
- バグ報告には再現手順を含めてください
- プルリクエストには変更内容の説明を含めてください

### バグ報告

バグを発見した場合は、以下の情報を含めてIssueを作成してください：
- 使用しているLinuxディストリビューション
- Pythonバージョン
- デスクトップ環境
- エラーメッセージ（あれば）
- 再現手順

## 作者

- **backspec3** - [GitHub](https://github.com/backspec3)

## 謝辞

- **Microsoft Bingチーム** - 美しい壁紙の提供
- **PyQt6コミュニティ** - 優秀なGUIフレームワーク
- **Linuxコミュニティ** - オープンソースエコシステム

## 関連プロジェクト

LinuxWallpaperが気に入った場合、これらのプロジェクトもチェックしてみてください：

- [variety](https://github.com/varietywalls/variety) - 多機能な壁紙管理ツール
- [nitrogen](https://github.com/l3ib/nitrogen) - 軽量な壁紙設定ツール
- [wallpaper-reddit](https://github.com/markubiak/wallpaper-reddit) - Reddit壁紙ダウンローダー

## セキュリティ

セキュリティの脆弱性を発見した場合は、公開のIssueではなく、リポジトリ所有者に直接連絡してください。

## 更新履歴

### v2.0 (2025-9-28)
- PyQt6への移行
- 8枚壁紙同時表示機能
- 改善されたUI/UX
- システムトレイサポート
- 自動更新機能

### v1.0 (2025-9-20)
- 初回リリース
- 基本的な壁紙取得・設定機能

---

⭐ このプロジェクトが気に入ったら、ぜひスターを付けてください！