# Linux Bing Wallpaper - プロジェクトドキュメント

## プロジェクト概要

**Linux Bing Wallpaper** は、Microsoft Bing の日替わり壁紙やスポットライトのアーカイブ画像を取得し、Linux デスクトップ環境の背景（壁紙）として設定するためのアプリケーションです。
Rust ベースの **Tauri** フレームワークを用いた構成となっており、高いパフォーマンス、スリムなバイナリサイズ、そして洗練されたユーザーインターフェースを実現しています。

---

## アーキテクチャと技術スタック

本プロジェクトは、フロントエンド層とバックエンド層（コアロジック層）の2層に分かれた Tauri アーキテクチャを採用しています。

### フロントエンド (UI 層)
- **フレームワーク**: React 19 (TypeScript)
- **ビルドツール**: Vite
- **スタイリング**: Tailwind CSS (v4), Lucide React (アイコン)
- **国際化 (i18n)**: i18next, react-i18next (現在英語と日本語をサポート)
- **役割**: ユーザーへの視覚的なフィードバック、壁紙のプレビュー表示（グリッドビュー）、デスクトップ環境の選択、バックエンドへのアクション（壁紙取得、設定、フォルダを開くなど）のトリガー。

### バックエンド (コアロジック層)
- **フレームワーク**: Tauri v2
- **言語**: Rust
- **主要クレート**: `reqwest` (HTTPリクエスト), `serde`, `serde_json` (JSONパース), `dirs` (ディレクトリパス取得), `regex` (正規表現)
- **役割**: Bing API へのアクセス、画像ファイルのローカル環境 (`~/Pictures/BingWallpapers/`) へのダウンロードと保存、各 Linux デスクトップ環境に対応した壁紙設定コマンドの実行、ローカルファイルシステムへのアクセス。

---

## 主要機能と内部実装

### 1. 壁紙の取得機能

フロントエンドからの呼び出しに応じて、Rust 側で定義された Tauri コマンドが実行されます。壁紙データは以下の構造体としてフロントエンドに返されます。

```rust
pub struct Wallpaper {
    pub path: String,       // ローカルのファイルパス
    pub title: String,      // 画像のタイトル
    pub copyright: String,  // 著作権情報
    pub date: String,       // 日付
    pub url: String,        // リモートの画像URL
}
```

#### 最新の壁紙取得 (`fetch_new_wallpapers`)
- **API エンドポイント**: `https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8&mkt=ja-JP`
- **処理内容**: Bing の公式 API から直近8日分の壁紙情報を取得します。画像を `~/Pictures/BingWallpapers/` にダウンロードし、メタデータをフロントエンドに返します。

#### スポットライトアーカイブ取得 (`fetch_spotlight_wallpapers`)
- **API エンドポイント**: `https://bing.npanuhin.me/JP/ja.json`
- **処理内容**: サードパーティのアーカイブ API からデータを取得し、ランダムに8枚の画像を抽出してダウンロード・表示します。

### 2. 壁紙の設定機能 (`set_wallpaper`)

様々な Linux デスクトップ環境 (DE) に対応するため、バックエンド側で環境を自動検出またはフロントエンドからの指定を受け取り、適切なコマンドを発行します。

- **自動検出 (`auto_detect`)**: 環境変数 `XDG_CURRENT_DESKTOP` および `DESKTOP_SESSION` を読み取り、実行中のデスクトップ環境を推測します。
- **GNOME**: `gsettings` コマンドを使用し、`picture-uri` と `picture-uri-dark` の両方に壁紙パスを設定します。
- **KDE Plasma**: `plasma-apply-wallpaperimage` コマンドを使用します。
- **XFCE**: `xfconf-query` コマンドを使用し、現在のプロパティリストから `last-image` を含むキーを検索してパスを上書きします。
- **COSMIC**: `~/.config/cosmic/com.system76.CosmicBackground/v1/all` の設定ファイルを直接パース・書き換えし、`killall -HUP cosmic-bg` でリロードさせます。
- **Other (その他)**: `feh` コマンドの `--bg-scale` オプションを使用してフォールバック対応します。

### 3. 多言語対応 (i18n)

フロントエンドは `i18next` を利用して多言語化されており、現在以下の言語が組み込まれています（言語ファイルは通常 `public/locales/` 等に配置、またはソースコード内に定義）。
- **English (en)**
- **日本語 (ja)**

UI 上のセレクトボックスからリアルタイムで言語を切り替えることが可能です。

### 4. Linux 固有のワークアラウンド

Wayland 環境での WebKitGTK レンダリング問題（画面が真っ白になる現象）を回避するため、Rust の `main.rs` にてプログラムの起動時に環境変数をセットしています。

```rust
#[cfg(target_os = "linux")]
std::env::set_var("WEBKIT_DISABLE_DMABUF_RENDERER", "1");
```

---

## ディレクトリ構造

```text
LinuxBingWallpaper/
├── src-tauri/               # Tauri バックエンド (Rust)
│   ├── Cargo.toml           # Rust 依存関係
│   ├── tauri.conf.json      # Tauri アプリケーション設定
│   └── src/
│       ├── main.rs          # エントリーポイント
│       └── lib.rs           # Tauri コマンド (ロジック本体) 実装
├── src/                     # フロントエンド (React/TypeScript)
│   ├── App.tsx              # メイン UI コンポーネント・ロジック
│   ├── App.css              # グローバルスタイル・Tailwind インポート
│   ├── main.tsx             # React エントリーポイント
│   └── i18n.ts              # (存在する場合) 多言語設定
├── package.json             # Node.js 依存関係・ビルドスクリプト
├── vite.config.ts           # Vite ビルド設定
└── README.md                # 簡易ドキュメント
```

---

## 開発とビルドのフロー

1. **開発サーバーの起動**:
   ```bash
   WEBKIT_DISABLE_DMABUF_RENDERER=1 GDK_BACKEND=x11 npm run tauri dev
   ```
   フロントエンドの Vite 開発サーバーと Tauri ウィンドウが同時に立ち上がり、ホットリロードが有効な状態で開発が行えます。

2. **本番用ビルド**:
   ```bash
   NO_STRIP=1 npm run tauri build
   ```
   Tauri がフロントエンドをビルドした後、Rust バイナリをコンパイルし、Linux 向けの配布パッケージ (AppImage, .deb, .rpm 等) を生成します。生成物は `src-tauri/target/release/bundle/` ディレクトリに出力されます。
