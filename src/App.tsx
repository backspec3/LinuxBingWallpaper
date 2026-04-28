import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { RefreshCw, Monitor, Settings2, Folder, Languages } from "lucide-react";
import { useTranslation } from "react-i18next";
import "./App.css";

type Wallpaper = {
  path: string;
  title: string;
  copyright: string;
  date: string;
  url: string;
};

type DesktopEnv = "auto_detect" | "gnome" | "kde" | "xfce" | "cosmic" | "other";

function App() {
  const { t, i18n } = useTranslation();
  const [wallpapers, setWallpapers] = useState<Wallpaper[]>([]);
  const [spotlightWallpapers, setSpotlightWallpapers] = useState<Wallpaper[]>([]);
  const [currentTab, setCurrentTab] = useState<"new" | "spotlight">("new");
  const [selectedWallpaper, setSelectedWallpaper] = useState<Wallpaper | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [desktopEnv, setDesktopEnv] = useState<DesktopEnv>("auto_detect");
  const [statusMsg, setStatusMsg] = useState(t("ready"));

  useEffect(() => {
    fetchWallpapers("new");
    fetchWallpapers("spotlight");
  }, []);

  async function fetchWallpapers(type: "new" | "spotlight") {
    try {
      setIsLoading(true);
      const translatedType = t(`tabs.${type}`);
      setStatusMsg(t("fetching_wallpapers", { type: translatedType }));
      const res: Wallpaper[] = await invoke(
        type === "new" ? "fetch_new_wallpapers" : "fetch_spotlight_wallpapers"
      );
      if (type === "new") setWallpapers(res);
      else setSpotlightWallpapers(res);
      setStatusMsg(t("successfully_fetched", { type: translatedType }));
    } catch (error) {
      setStatusMsg(t("error", { error }));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSetWallpaper() {
    if (!selectedWallpaper) return;
    try {
      setIsLoading(true);
      setStatusMsg(t("setting_wallpaper"));
      await invoke("set_wallpaper", { path: selectedWallpaper.path, env: desktopEnv });
      setStatusMsg(t("wallpaper_set_success"));
    } catch (error) {
      setStatusMsg(t("failed_to_set", { error }));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleOpenFolder() {
    try {
      await invoke("open_wallpaper_dir");
    } catch (error) {
      setStatusMsg(t("failed_to_open", { error }));
    }
  }

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  const activeWallpapers = currentTab === "new" ? wallpapers : spotlightWallpapers;

  return (
    <div className="flex h-screen w-full bg-[#1e1e1e] text-white overflow-hidden font-sans">
      {/* Sidebar / Controls */}
      <div className="w-80 bg-[#2d2d2d] border-r border-[#404040] flex flex-col p-6 shadow-xl z-10">
        <h1 className="text-2xl font-bold text-center mb-8 bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">
          {t("title")}
        </h1>

        <div className="bg-[#1e1e1e] rounded-xl p-4 border border-[#404040] mb-6 flex flex-col items-center">
          <h2 className="text-sm font-semibold text-blue-400 mb-3 w-full text-left">{t("current_selection")}</h2>
          <div className="w-full aspect-video bg-[#2d2d2d] rounded-lg border-2 border-[#404040] overflow-hidden mb-3 flex items-center justify-center">
            {selectedWallpaper ? (
              <img src={selectedWallpaper.url} alt={selectedWallpaper.title} className="w-full h-full object-cover" />
            ) : (
              <span className="text-gray-400 text-sm">{t("select_wallpaper")}</span>
            )}
          </div>
          <p className="text-xs text-center text-gray-300 line-clamp-2 h-8">
            {selectedWallpaper ? selectedWallpaper.title : t("title_not_selected")}
          </p>
        </div>

        <div className="flex flex-col gap-3 mb-6">
          <button
            onClick={() => fetchWallpapers(currentTab)}
            disabled={isLoading}
            className="flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 text-white py-2.5 px-4 rounded-lg font-medium transition-colors"
          >
            <RefreshCw size={18} className={isLoading ? "animate-spin" : ""} />
            {t("fetch_wallpapers")}
          </button>
          <button
            onClick={handleSetWallpaper}
            disabled={isLoading || !selectedWallpaper}
            className="flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white py-2.5 px-4 rounded-lg font-medium transition-colors"
          >
            <Monitor size={18} />
            {t("set_wallpaper")}
          </button>
          <button
            onClick={handleOpenFolder}
            className="flex items-center justify-center gap-2 bg-[#404040] hover:bg-[#505050] text-white py-2.5 px-4 rounded-lg font-medium transition-colors"
          >
            <Folder size={18} />
            {t("open_folder")}
          </button>
        </div>

        <div className="mt-auto flex flex-col gap-4">
          <label className="flex flex-col gap-2 text-sm text-gray-300">
            <span className="flex items-center gap-2 font-semibold"><Languages size={16} /> {t("language")}</span>
            <select
              value={i18n.language}
              onChange={(e) => changeLanguage(e.target.value)}
              className="appearance-none bg-[#1e1e1e] border border-[#404040] rounded-lg p-2 text-white outline-none focus:border-blue-500 cursor-pointer"
            >
              <option value="en" className="bg-[#1e1e1e] text-white">English</option>
              <option value="ja" className="bg-[#1e1e1e] text-white">日本語</option>
            </select>
          </label>

          <label className="flex flex-col gap-2 text-sm text-gray-300">
            <span className="flex items-center gap-2 font-semibold"><Settings2 size={16} /> {t("desktop_environment")}</span>
            <select
              value={desktopEnv}
              onChange={(e) => setDesktopEnv(e.target.value as DesktopEnv)}
              className="appearance-none bg-[#1e1e1e] border border-[#404040] rounded-lg p-2 text-white outline-none focus:border-blue-500 cursor-pointer"
            >
              <option value="auto_detect" className="bg-[#1e1e1e] text-white">{t("de.auto_detect")}</option>
              <option value="gnome" className="bg-[#1e1e1e] text-white">{t("de.gnome")}</option>
              <option value="kde" className="bg-[#1e1e1e] text-white">{t("de.kde")}</option>
              <option value="xfce" className="bg-[#1e1e1e] text-white">{t("de.xfce")}</option>
              <option value="cosmic" className="bg-[#1e1e1e] text-white">{t("de.cosmic")}</option>
              <option value="other" className="bg-[#1e1e1e] text-white">{t("de.other")}</option>
            </select>
          </label>

          <div className="bg-[#1e1e1e] rounded-lg p-3 border border-[#404040] text-xs text-blue-400 break-words">
            {statusMsg}
          </div>
        </div>
      </div>

      {/* Main Content / Gallery */}
      <div className="flex-1 flex flex-col bg-[#1e1e1e]">
        <div className="flex px-8 pt-8 pb-4 border-b border-[#404040] gap-8">
          <button
            className={`text-lg font-bold pb-2 border-b-2 transition-colors ${currentTab === "new" ? "border-blue-500 text-blue-400" : "border-transparent text-gray-400 hover:text-white"
              }`}
            onClick={() => setCurrentTab("new")}
          >
            {t("latest_wallpapers")}
          </button>
          <button
            className={`text-lg font-bold pb-2 border-b-2 transition-colors ${currentTab === "spotlight" ? "border-blue-500 text-blue-400" : "border-transparent text-gray-400 hover:text-white"
              }`}
            onClick={() => setCurrentTab("spotlight")}
          >
            {t("spotlight_archive")}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-8">
          {isLoading && activeWallpapers.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-400">{t("loading_wallpapers")}</div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {activeWallpapers.map((wp, i) => (
                <div
                  key={i}
                  onClick={() => setSelectedWallpaper(wp)}
                  className={`group relative bg-[#2d2d2d] rounded-xl overflow-hidden cursor-pointer border-2 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg hover:shadow-blue-500/20 ${selectedWallpaper?.path === wp.path ? "border-blue-500" : "border-transparent"
                    }`}
                >
                  <div className="aspect-video overflow-hidden">
                    <img
                      src={wp.url}
                      alt={wp.title}
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                      loading="lazy"
                    />
                  </div>
                  <div className="p-3">
                    <h3 className="text-sm font-semibold truncate" title={wp.title}>{wp.title}</h3>
                    <p className="text-xs text-gray-400 mt-1">{wp.date}</p>
                  </div>
                  {selectedWallpaper?.path === wp.path && (
                    <div className="absolute inset-0 border-4 border-blue-500 rounded-xl pointer-events-none"></div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
