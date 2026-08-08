use reqwest;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::SystemTime;

// 保存する壁紙の最大数。通常・スポットライトの画像を合算して管理する。
const MAX_SAVED_WALLPAPERS: usize = 20;

struct SavedWallpaper {
    path: PathBuf,
    date: Option<String>,
    modified: SystemTime,
}

// ファイル名に含まれる YYYYMMDD を取り出す。日付がない旧形式のファイルは更新日時で扱う。
fn wallpaper_date_from_filename(filename: &str) -> Option<String> {
    let date = filename
        .strip_prefix("bing_wallpaper_")
        .or_else(|| filename.strip_prefix("bing_archive_"))?
        .strip_suffix(".jpg")?;

    if date.len() == 8 && date.bytes().all(|byte| byte.is_ascii_digit()) {
        Some(date.to_string())
    } else {
        None
    }
}

// アプリが保存した画像だけを対象に、撮影日が新しい20枚を残す。
fn cleanup_old_wallpapers(wallpaper_dir: &Path) -> Result<(), String> {
    let mut saved_wallpapers = fs::read_dir(wallpaper_dir)
        .map_err(|e| e.to_string())?
        .filter_map(Result::ok)
        .filter_map(|entry| {
            let path = entry.path();
            let filename = path.file_name()?.to_str()?;
            let is_saved_wallpaper = (filename.starts_with("bing_wallpaper_")
                || filename.starts_with("bing_archive_"))
                && filename.ends_with(".jpg");
            if !is_saved_wallpaper {
                return None;
            }

            let date = wallpaper_date_from_filename(filename);
            let modified = entry
                .metadata()
                .ok()?
                .modified()
                .unwrap_or(SystemTime::UNIX_EPOCH);

            Some(SavedWallpaper {
                path,
                date,
                modified,
            })
        })
        .collect::<Vec<_>>();

    // 日付が新しい順、同日の場合は更新日時が新しい順に並べる。
    saved_wallpapers.sort_by(|left, right| {
        right
            .date
            .cmp(&left.date)
            .then_with(|| right.modified.cmp(&left.modified))
    });

    for wallpaper in saved_wallpapers.into_iter().skip(MAX_SAVED_WALLPAPERS) {
        fs::remove_file(wallpaper.path).map_err(|e| e.to_string())?;
    }

    Ok(())
}

// フロントエンドに返す壁紙データの構造体
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Wallpaper {
    pub path: String,       // ローカルに保存された画像のファイルパス
    pub title: String,      // 画像のタイトル
    pub copyright: String,  // 著作権情報
    pub date: String,       // 画像の日付
    pub url: String,        // リモートの画像URL
}

// Bing APIから返される個々の画像データの構造体
#[derive(Serialize, Deserialize, Debug)]
struct BingImage {
    url: String,
    title: String,
    copyright: String,
    startdate: String,
}

// Bing APIのレスポンス全体の構造体
#[derive(Serialize, Deserialize, Debug)]
struct BingResponse {
    images: Vec<BingImage>,
}

// 最新のBing壁紙を取得するコマンド
#[tauri::command]
async fn fetch_new_wallpapers() -> Result<Vec<Wallpaper>, String> {
    // Bingの公式APIエンドポイント（直近8日分の画像、日本市場向け）
    let api_url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8&mkt=ja-JP";
    let client = reqwest::Client::new();
    let res = client.get(api_url).send().await.map_err(|e| e.to_string())?;
    let data: BingResponse = res.json().await.map_err(|e| e.to_string())?;

    // 保存先ディレクトリの設定 (デフォルトは ~/Pictures/BingWallpapers)
    let wallpaper_dir = dirs::picture_dir()
        .unwrap_or_else(|| dirs::home_dir().unwrap().join("Pictures"))
        .join("BingWallpapers");

    // ディレクトリが存在しない場合は作成する
    fs::create_dir_all(&wallpaper_dir).map_err(|e| e.to_string())?;

    let mut wallpapers = Vec::new();

    for img in data.images {
        // 画像の完全なURLを構築
        let image_url = format!("https://www.bing.com{}", img.url);
        // 保存するファイル名を生成（日付ベース）
        let filename = format!("bing_wallpaper_{}.jpg", img.startdate);
        let file_path = wallpaper_dir.join(&filename);

        // ファイルがまだ存在しない場合のみダウンロードして保存
        if !file_path.exists() {
            let img_bytes = client.get(&image_url).send().await.map_err(|e| e.to_string())?.bytes().await.map_err(|e| e.to_string())?;
            fs::write(&file_path, img_bytes).map_err(|e| e.to_string())?;
        }

        // フロントエンドに返すリストに追加
        wallpapers.push(Wallpaper {
            path: file_path.to_string_lossy().to_string(),
            title: img.title,
            copyright: img.copyright,
            date: img.startdate,
            url: image_url,
        });
    }

    cleanup_old_wallpapers(&wallpaper_dir)?;
    wallpapers.retain(|wallpaper| Path::new(&wallpaper.path).exists());

    Ok(wallpapers)
}

// スポットライトのアーカイブ壁紙を取得するコマンド
#[tauri::command]
async fn fetch_spotlight_wallpapers() -> Result<Vec<Wallpaper>, String> {
    // サードパーティのBing壁紙アーカイブAPIエンドポイント
    let archive_url = "https://bing.npanuhin.me/JP/ja.json";
    let client = reqwest::Client::new();
    let res = client.get(archive_url).send().await.map_err(|e| e.to_string())?;

    // JSONの配列をパース
    let data: Vec<serde_json::Value> = res.json().await.map_err(|e| e.to_string())?;

    // 保存先ディレクトリの設定
    let wallpaper_dir = dirs::picture_dir()
        .unwrap_or_else(|| dirs::home_dir().unwrap().join("Pictures"))
        .join("BingWallpapers");

    fs::create_dir_all(&wallpaper_dir).map_err(|e| e.to_string())?;

    let mut wallpapers = Vec::new();
    
    // 取得した画像リストからランダムに8枚を選択
    let mut selected_images = data;
    {
        use rand::seq::SliceRandom;
        let mut rng = rand::rng();
        selected_images.shuffle(&mut rng);
    }
    let selected_images = selected_images.into_iter().take(8);

    for img in selected_images {
        // URLが取得できない場合はスキップ
        let image_url = match img.get("url").and_then(|u| u.as_str()) {
            Some(u) => u.to_string(),
            None => continue,
        };
        
        // メタデータの取得（存在しない場合のフォールバックも設定）
        let title = img.get("title").and_then(|t| t.as_str()).unwrap_or("不明").to_string();
        let copyright = img.get("copyright").and_then(|c| c.as_str()).unwrap_or("").to_string();
        let date = img.get("date").and_then(|d| d.as_str()).unwrap_or("unknown").to_string();
        
        // ファイル名の生成
        let filename = format!("bing_archive_{}.jpg", date.replace("-", ""));
        let file_path = wallpaper_dir.join(&filename);

        // まだ存在しない場合のみダウンロードを試みる
        if !file_path.exists() {
            if let Ok(res) = client.get(&image_url).send().await {
                if let Ok(bytes) = res.bytes().await {
                    let _ = fs::write(&file_path, bytes);
                }
            }
        }

        // ファイルが正常に存在する場合のみリストに追加
        if file_path.exists() {
            wallpapers.push(Wallpaper {
                path: file_path.to_string_lossy().to_string(),
                title,
                copyright,
                date,
                url: image_url,
            });
        }
    }

    cleanup_old_wallpapers(&wallpaper_dir)?;
    wallpapers.retain(|wallpaper| Path::new(&wallpaper.path).exists());

    Ok(wallpapers)
}

// 選択した壁紙をデスクトップの背景として設定するコマンド
#[tauri::command]
fn set_wallpaper(path: String, mut env: String) -> Result<(), String> {
    // デスクトップ環境が「自動検出」の場合の処理
    if env == "auto_detect" {
        // 環境変数から現在のデスクトップ環境を推測
        let xdg = std::env::var("XDG_CURRENT_DESKTOP").unwrap_or_default().to_lowercase();
        let desktop_session = std::env::var("DESKTOP_SESSION").unwrap_or_default().to_lowercase();
        
        if xdg.contains("gnome") || desktop_session.contains("gnome") {
            env = "gnome".to_string();
        } else if xdg.contains("kde") || xdg.contains("plasma") || desktop_session.contains("plasma") {
            env = "kde".to_string();
        } else if xdg.contains("xfce") || desktop_session.contains("xfce") {
            env = "xfce".to_string();
        } else if xdg.contains("cosmic") || desktop_session.contains("cosmic") {
            env = "cosmic".to_string();
        } else {
            env = "other".to_string();
        }
    }

    // 各デスクトップ環境に応じた壁紙設定コマンドを実行
    match env.as_str() {
        "gnome" => {
            // GNOME環境：ライトモード用とダークモード用の両方に壁紙を設定
            Command::new("gsettings")
                .args(&["set", "org.gnome.desktop.background", "picture-uri", &format!("file://{}", path)])
                .output()
                .map_err(|e| e.to_string())?;
            Command::new("gsettings")
                .args(&["set", "org.gnome.desktop.background", "picture-uri-dark", &format!("file://{}", path)])
                .output()
                .map_err(|e| e.to_string())?;
        },
        "kde" => {
            // KDE Plasma環境
            Command::new("plasma-apply-wallpaperimage")
                .arg(&path)
                .output()
                .map_err(|e| e.to_string())?;
        },
        "xfce" => {
            // XFCE環境：xfconf-queryを使用して設定を書き換える
            let output = Command::new("xfconf-query")
                .args(&["-c", "xfce4-desktop", "-l"])
                .output()
                .map_err(|e| e.to_string())?;

            let output_str = String::from_utf8_lossy(&output.stdout);
            let mut found = false;
            
            // プロパティリストから "last-image" を探して更新
            for line in output_str.lines() {
                if line.contains("last-image") {
                    let _ = Command::new("xfconf-query")
                        .args(&["-c", "xfce4-desktop", "-p", line, "-s", &path])
                        .output();
                    found = true;
                }
            }
            
            if !found {
                return Err("XFCE wallpaper properties not found. Fallback needed.".to_string());
            }
        },
        "cosmic" => {
            // COSMIC環境：設定ファイルを直接パース・書き換えしてリロードさせる
            let config_dir = dirs::home_dir().unwrap().join(".config").join("cosmic").join("com.system76.CosmicBackground").join("v1");
            let config_file = config_dir.join("all");
            
            if config_file.exists() {
                if let Ok(content) = fs::read_to_string(&config_file) {
                    let re = regex::Regex::new(r#"source:\s*Path\(".*?"\)"#).unwrap();
                    let new_content = re.replace(&content, format!("source: Path(\"{}\")", path).as_str());
                    let _ = fs::write(&config_file, new_content.as_bytes());
                    // 変更を適用するために cosmic-bg をリロード
                    let _ = Command::new("killall").args(&["-HUP", "cosmic-bg"]).output();
                }
            } else {
                 return Err("COSMIC config not found".to_string());
            }
        },
        _ => { 
            // その他の環境（フォールバック）：汎用的な画像ビューア「feh」を使用して背景を設定
            let _ = Command::new("feh")
                .args(&["--bg-scale", &path])
                .output()
                .map_err(|e| format!("Feh fallback failed: {}", e))?;
        }
    }
    
    Ok(())
}

// 壁紙が保存されているフォルダを開くコマンド
#[tauri::command]
async fn open_wallpaper_dir() -> Result<(), String> {
    let wallpaper_dir = dirs::picture_dir()
        .unwrap_or_else(|| dirs::home_dir().unwrap().join("Pictures"))
        .join("BingWallpapers");
    
    // フォルダが存在しない場合は作成
    if !wallpaper_dir.exists() {
        fs::create_dir_all(&wallpaper_dir).map_err(|e| e.to_string())?;
    }

    #[cfg(target_os = "linux")]
    {
        // Linuxの標準コマンド xdg-open を使ってフォルダを開く
        Command::new("xdg-open")
            .arg(&wallpaper_dir)
            .spawn()
            .map_err(|e| e.to_string())?;
    }

    Ok(())
}

// アプリケーションのエントリーポイント
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        // ブラウザなどの外部リンクを開くためのプラグインを初期化
        .plugin(tauri_plugin_opener::init())
        // フロントエンドから呼び出せるコマンドを登録
        .invoke_handler(tauri::generate_handler![
            fetch_new_wallpapers,
            fetch_spotlight_wallpapers,
            set_wallpaper,
            open_wallpaper_dir
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[cfg(test)]
mod tests {
    use super::wallpaper_date_from_filename;

    #[test]
    fn extracts_dates_from_managed_wallpaper_filenames() {
        assert_eq!(
            wallpaper_date_from_filename("bing_wallpaper_20260809.jpg").as_deref(),
            Some("20260809")
        );
        assert_eq!(
            wallpaper_date_from_filename("bing_archive_20200102.jpg").as_deref(),
            Some("20200102")
        );
        assert_eq!(
            wallpaper_date_from_filename("bing_archive_unknown.jpg"),
            None
        );
    }
}
