use reqwest;
use serde::{Deserialize, Serialize};
use std::fs;
use std::process::Command;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Wallpaper {
    pub path: String,
    pub title: String,
    pub copyright: String,
    pub date: String,
    pub url: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct BingImage {
    url: String,
    title: String,
    copyright: String,
    startdate: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct BingResponse {
    images: Vec<BingImage>,
}

#[tauri::command]
async fn fetch_new_wallpapers() -> Result<Vec<Wallpaper>, String> {
    let api_url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8&mkt=ja-JP";
    let client = reqwest::Client::new();
    let res = client.get(api_url).send().await.map_err(|e| e.to_string())?;
    let data: BingResponse = res.json().await.map_err(|e| e.to_string())?;

    let wallpaper_dir = dirs::picture_dir()
        .unwrap_or_else(|| dirs::home_dir().unwrap().join("Pictures"))
        .join("BingWallpapers");

    fs::create_dir_all(&wallpaper_dir).map_err(|e| e.to_string())?;

    let mut wallpapers = Vec::new();

    for img in data.images {
        let image_url = format!("https://www.bing.com{}", img.url);
        let filename = format!("bing_wallpaper_{}.jpg", img.startdate);
        let file_path = wallpaper_dir.join(&filename);

        if !file_path.exists() {
            let img_bytes = client.get(&image_url).send().await.map_err(|e| e.to_string())?.bytes().await.map_err(|e| e.to_string())?;
            fs::write(&file_path, img_bytes).map_err(|e| e.to_string())?;
        }

        wallpapers.push(Wallpaper {
            path: file_path.to_string_lossy().to_string(),
            title: img.title,
            copyright: img.copyright,
            date: img.startdate,
            url: image_url,
        });
    }

    Ok(wallpapers)
}

#[tauri::command]
async fn fetch_spotlight_wallpapers() -> Result<Vec<Wallpaper>, String> {
    let archive_url = "https://bing.npanuhin.me/JP/ja.json";
    let client = reqwest::Client::new();
    let res = client.get(archive_url).send().await.map_err(|e| e.to_string())?;
    
    // Parse array of JSON objects
    let data: Vec<serde_json::Value> = res.json().await.map_err(|e| e.to_string())?;

    let wallpaper_dir = dirs::picture_dir()
        .unwrap_or_else(|| dirs::home_dir().unwrap().join("Pictures"))
        .join("BingWallpapers");

    fs::create_dir_all(&wallpaper_dir).map_err(|e| e.to_string())?;

    let mut wallpapers = Vec::new();
    
    let mut selected_images = data;
    {
        use rand::seq::SliceRandom;
        let mut rng = rand::rng();
        selected_images.shuffle(&mut rng);
    }
    let selected_images = selected_images.into_iter().take(8);

    for img in selected_images {
        let image_url = match img.get("url").and_then(|u| u.as_str()) {
            Some(u) => u.to_string(),
            None => continue,
        };
        
        let title = img.get("title").and_then(|t| t.as_str()).unwrap_or("不明").to_string();
        let copyright = img.get("copyright").and_then(|c| c.as_str()).unwrap_or("").to_string();
        let date = img.get("date").and_then(|d| d.as_str()).unwrap_or("unknown").to_string();
        
        let filename = format!("bing_archive_{}.jpg", date.replace("-", ""));
        let file_path = wallpaper_dir.join(&filename);

        if !file_path.exists() {
            if let Ok(res) = client.get(&image_url).send().await {
                if let Ok(bytes) = res.bytes().await {
                    let _ = fs::write(&file_path, bytes);
                }
            }
        }

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

    Ok(wallpapers)
}

#[tauri::command]
fn set_wallpaper(path: String, mut env: String) -> Result<(), String> {
    if env == "auto_detect" {
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

    match env.as_str() {
        "gnome" => {
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
            Command::new("plasma-apply-wallpaperimage")
                .arg(&path)
                .output()
                .map_err(|e| e.to_string())?;
        },
        "xfce" => {
            let output = Command::new("xfconf-query")
                .args(&["-c", "xfce4-desktop", "-l"])
                .output()
                .map_err(|e| e.to_string())?;
            
            let output_str = String::from_utf8_lossy(&output.stdout);
            let mut found = false;
            
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
            let config_dir = dirs::home_dir().unwrap().join(".config").join("cosmic").join("com.system76.CosmicBackground").join("v1");
            let config_file = config_dir.join("all");
            
            if config_file.exists() {
                if let Ok(content) = fs::read_to_string(&config_file) {
                    let re = regex::Regex::new(r#"source:\s*Path\(".*?"\)"#).unwrap();
                    let new_content = re.replace(&content, format!("source: Path(\"{}\")", path).as_str());
                    let _ = fs::write(&config_file, new_content.as_bytes());
                    let _ = Command::new("killall").args(&["-HUP", "cosmic-bg"]).output();
                }
            } else {
                 return Err("COSMIC config not found".to_string());
            }
        },
        _ => { // "other" (using feh as fallback)
            let _ = Command::new("feh")
                .args(&["--bg-scale", &path])
                .output()
                .map_err(|e| format!("Feh fallback failed: {}", e))?;
        }
    }
    
    Ok(())
}

#[tauri::command]
async fn open_wallpaper_dir() -> Result<(), String> {
    let wallpaper_dir = dirs::picture_dir()
        .unwrap_or_else(|| dirs::home_dir().unwrap().join("Pictures"))
        .join("BingWallpapers");
    
    if !wallpaper_dir.exists() {
        fs::create_dir_all(&wallpaper_dir).map_err(|e| e.to_string())?;
    }

    #[cfg(target_os = "linux")]
    {
        Command::new("xdg-open")
            .arg(&wallpaper_dir)
            .spawn()
            .map_err(|e| e.to_string())?;
    }
    
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            fetch_new_wallpapers,
            fetch_spotlight_wallpapers,
            set_wallpaper,
            open_wallpaper_dir
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
