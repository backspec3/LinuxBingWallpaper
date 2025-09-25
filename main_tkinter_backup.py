#!/usr/bin/env python3
"""
Linux Bing Wallpaper MVP
軽量なBing壁紙自動設定アプリ
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import json
import os
import subprocess
import threading
from urllib.parse import urljoin
from PIL import Image, ImageTk
import tempfile
from pathlib import Path

class BingWallpaperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux Bing Wallpaper")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # 壁紙保存ディレクトリ
        self.wallpaper_dir = Path.home() / "Pictures" / "BingWallpapers"
        self.wallpaper_dir.mkdir(parents=True, exist_ok=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """UIの設定"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # タイトル
        title_label = ttk.Label(main_frame, text="🖼️ Linux Bing Wallpaper", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 現在の壁紙情報
        ttk.Label(main_frame, text="現在の壁紙:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.current_wallpaper_label = ttk.Label(main_frame, text="取得中...")
        self.current_wallpaper_label.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # プレビュー用キャンバス
        self.preview_frame = ttk.LabelFrame(main_frame, text="プレビュー", padding="5")
        self.preview_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.canvas = tk.Canvas(self.preview_frame, width=400, height=200, bg="lightgray")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # ボタン
        self.fetch_btn = ttk.Button(button_frame, text="🔄 最新壁紙を取得", 
                                   command=self.fetch_wallpaper_async, width=20)
        self.fetch_btn.pack(side=tk.LEFT, padx=5)
        
        self.set_btn = ttk.Button(button_frame, text="🖥️ 壁紙を設定", 
                                 command=self.set_wallpaper, width=20, state="disabled")
        self.set_btn.pack(side=tk.LEFT, padx=5)
        
        self.folder_btn = ttk.Button(button_frame, text="📁 フォルダを開く", 
                                    command=self.open_folder, width=20)
        self.folder_btn.pack(side=tk.LEFT, padx=5)
        
        # ステータスバー
        self.status_var = tk.StringVar(value="準備完了")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # グリッド重み設定
        main_frame.rowconfigure(2, weight=1)
        
        # 現在の壁紙を取得
        self.current_image_path = None
        self.fetch_wallpaper_async()
        
    def fetch_wallpaper_async(self):
        """非同期で壁紙を取得"""
        def run():
            self.fetch_btn.config(state="disabled")
            self.status_var.set("壁紙情報を取得中...")
            self.root.update()
            
            try:
                self.fetch_wallpaper()
            except Exception as e:
                messagebox.showerror("エラー", f"壁紙の取得に失敗しました:\n{str(e)}")
            finally:
                self.fetch_btn.config(state="normal")
                
        threading.Thread(target=run, daemon=True).start()
        
    def fetch_wallpaper(self):
        """Bing APIから壁紙情報を取得"""
        try:
            # Bing公式API
            api_url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=ja-JP"
            
            self.status_var.set("Bing APIに接続中...")
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('images'):
                raise Exception("壁紙データが見つかりません")
                
            image_data = data['images'][0]
            image_url = "https://www.bing.com" + image_data['url']
            title = image_data.get('title', '不明')
            copyright_info = image_data.get('copyright', '')
            
            self.status_var.set("壁紙をダウンロード中...")
            
            # 画像をダウンロード
            img_response = requests.get(image_url, timeout=30)
            img_response.raise_for_status()
            
            # ファイル名を生成
            filename = f"bing_wallpaper_{image_data.get('startdate', 'unknown')}.jpg"
            self.current_image_path = self.wallpaper_dir / filename
            
            # 画像を保存
            with open(self.current_image_path, 'wb') as f:
                f.write(img_response.content)
                
            # プレビューを更新
            self.update_preview()
            
            # UI更新
            self.current_wallpaper_label.config(text=f"{title[:50]}...")
            self.set_btn.config(state="normal")
            self.status_var.set(f"✅ 壁紙を取得しました: {filename}")
            
        except requests.RequestException as e:
            self.status_var.set("❌ ネットワークエラー")
            raise Exception(f"ネットワークエラー: {str(e)}")
        except Exception as e:
            self.status_var.set("❌ 取得失敗")
            raise
            
    def update_preview(self):
        """プレビュー画像を更新"""
        if not self.current_image_path or not self.current_image_path.exists():
            return
            
        try:
            # 画像を読み込んでリサイズ
            with Image.open(self.current_image_path) as img:
                # キャンバスサイズに合わせてリサイズ
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                if canvas_width <= 1:  # まだ描画されていない場合
                    canvas_width, canvas_height = 400, 200
                    
                img_ratio = img.width / img.height
                canvas_ratio = canvas_width / canvas_height
                
                if img_ratio > canvas_ratio:
                    new_width = canvas_width
                    new_height = int(canvas_width / img_ratio)
                else:
                    new_height = canvas_height
                    new_width = int(canvas_height * img_ratio)
                    
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(resized_img)
                
                # キャンバスをクリアして画像を表示
                self.canvas.delete("all")
                x = (canvas_width - new_width) // 2
                y = (canvas_height - new_height) // 2
                self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
                
        except Exception as e:
            print(f"プレビュー更新エラー: {e}")
            
    def set_wallpaper(self):
        """デスクトップ壁紙を設定"""
        if not self.current_image_path or not self.current_image_path.exists():
            messagebox.showwarning("警告", "設定する壁紙がありません")
            return
            
        try:
            self.status_var.set("壁紙を設定中...")
            
            # デスクトップ環境を検出して適切なコマンドを実行
            desktop_env = self.detect_desktop_environment()
            
            if desktop_env == "gnome":
                cmd = ["gsettings", "set", "org.gnome.desktop.background", 
                      "picture-uri", f"file://{self.current_image_path}"]
            elif desktop_env == "kde":
                # KDE Plasma用のコマンド
                cmd = ["qdbus", "org.kde.plasmashell", "/PlasmaShell", 
                      "setWallpaper", str(self.current_image_path)]
            elif desktop_env == "xfce":
                cmd = ["xfconf-query", "-c", "xfce4-desktop", 
                      "-p", "/backdrop/screen0/monitor0/workspace0/last-image", 
                      "-s", str(self.current_image_path)]
            else:
                # フォールバック: feh
                cmd = ["feh", "--bg-scale", str(self.current_image_path)]
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.status_var.set("✅ 壁紙を設定しました")
                messagebox.showinfo("成功", "壁紙を設定しました！")
            else:
                raise Exception(f"コマンド実行エラー: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.status_var.set("❌ タイムアウト")
            messagebox.showerror("エラー", "壁紙設定がタイムアウトしました")
        except FileNotFoundError:
            self.status_var.set("❌ コマンドが見つかりません")
            messagebox.showerror("エラー", f"必要なコマンドが見つかりません\n"
                               f"デスクトップ環境: {desktop_env}")
        except Exception as e:
            self.status_var.set("❌ 設定失敗")
            messagebox.showerror("エラー", f"壁紙の設定に失敗しました:\n{str(e)}")
            
    def detect_desktop_environment(self):
        """デスクトップ環境を検出"""
        # 環境変数から検出
        desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
        xdg_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        
        if 'gnome' in desktop_session or 'gnome' in xdg_desktop:
            return 'gnome'
        elif 'kde' in desktop_session or 'kde' in xdg_desktop:
            return 'kde'
        elif 'xfce' in desktop_session or 'xfce' in xdg_desktop:
            return 'xfce'
        else:
            return 'unknown'
            
    def open_folder(self):
        """壁紙フォルダを開く"""
        try:
            subprocess.run(['xdg-open', str(self.wallpaper_dir)], check=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("エラー", "フォルダを開けませんでした")


def main():
    """メイン関数"""
    root = tk.Tk()
    
    # アイコン設定（オプション）
    try:
        # システムアイコンがあれば使用
        root.iconbitmap('/usr/share/pixmaps/applications-graphics.png')
    except:
        pass
        
    app = BingWallpaperApp(root)
    
    # ウィンドウを画面中央に配置
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()