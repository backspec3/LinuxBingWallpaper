// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    // Linux (Wayland) 環境で画面が真っ白になる問題を回避するため、
    // WebKitGTKのDMABUFレンダラーを無効化する環境変数をプログラム内部で自動設定します。
    #[cfg(target_os = "linux")]
    std::env::set_var("WEBKIT_DISABLE_DMABUF_RENDERER", "1");

    tauri_app_lib::run()
}
