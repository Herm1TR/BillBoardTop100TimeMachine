# Billboard Hot 100 到 Spotify 播放清單轉換器

這個工具讓您可以選擇一個歷史日期，並自動創建一個包含當時 Billboard Hot 100 榜單歌曲的 Spotify 播放清單。非常適合想要重溫過去音樂記憶或探索不同時代流行音樂的用戶。

## 功能

- 從指定日期的 Billboard Hot 100 榜單抓取歌曲
- 自動在 Spotify 中搜索這些歌曲
- 創建一個私人 Spotify 播放清單並添加找到的歌曲
- 提供詳細的日誌以跟蹤進度和任何問題

## 安裝

### 前提條件

- Python 3.6+
- Spotify 帳戶
- Spotify 開發者應用程式（用於 API 訪問）

### 步驟

1. 克隆此倉庫:

```bash
git clone https://github.com/yourusername/billboard-to-spotify.git
cd billboard-to-spotify
```

2. 安裝依賴:

```bash
pip install -r requirements.txt
```

3. 設置您的 Spotify 開發者帳戶:
   - 前往 [Spotify 開發者儀表板](https://developer.spotify.com/dashboard/)
   - 創建一個新的應用程式
   - 設置重定向 URI（例如: `http://localhost:8888/callback`）
   - 記下 Client ID 和 Client Secret

4. 設置環境變量:

```bash
# Linux/Mac
export SPOTIFY_CLIENT_ID='your_client_id'
export SPOTIFY_CLIENT_SECRET='your_client_secret'
export SPOTIFY_REDIRECT_URI='your_redirect_uri'
export SPOTIFY_USERNAME='your_spotify_username'

# Windows (CMD)
set SPOTIFY_CLIENT_ID=your_client_id
set SPOTIFY_CLIENT_SECRET=your_client_secret
set SPOTIFY_REDIRECT_URI=your_redirect_uri
set SPOTIFY_USERNAME=your_spotify_username

# Windows (PowerShell)
$env:SPOTIFY_CLIENT_ID='your_client_id'
$env:SPOTIFY_CLIENT_SECRET='your_client_secret'
$env:SPOTIFY_REDIRECT_URI='your_redirect_uri'
$env:SPOTIFY_USERNAME='your_spotify_username'
```

或者，您可以創建一個 `.env` 文件並使用 `python-dotenv` 加載:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=your_redirect_uri
SPOTIFY_USERNAME=your_spotify_username
```

## 使用方法

### 命令列參數

```bash
python main.py --date YYYY-MM-DD
```

### 互動式

如果您不提供日期參數，程式將提示您輸入:

```bash
python main.py
```

然後按照提示輸入日期（格式為 YYYY-MM-DD）。

## 範例

```bash
python main.py --date 1985-07-13
```

這將創建一個包含 1985 年 7 月 13 日 Billboard Hot 100 榜單歌曲的 Spotify 播放清單。

## 錯誤處理

該程式包含多層錯誤處理機制:

- 日期格式驗證
- HTTP 請求錯誤處理
- 網頁內容解析錯誤處理
- Spotify API 連接和授權錯誤處理
- 歌曲搜索錯誤處理
- 播放清單創建錯誤處理

所有錯誤和進度信息都會通過日誌系統顯示，既方便用戶了解程序執行情況，也方便開發者故障排除。

## 常見問題解答

**Q: 我看到很多歌曲沒有找到，怎麼辦?**  
A: 可能有些老歌在 Spotify 上不可用，或者歌曲名稱匹配有問題。您可以嘗試使用更近期的日期，或手動添加找不到的歌曲。

**Q: 首次運行時被重定向到瀏覽器?**  
A: 這是 Spotify OAuth 授權過程的一部分。請登錄您的 Spotify 帳戶並授權您的應用程式。

**Q: Billboard 網站的更改會影響程式嗎?**  
A: 是的，如果 Billboard 更改了其 HTML 結構，抓取可能會失敗。請報告任何問題，以便更新代碼。

## 貢獻

歡迎貢獻! 請隨時提交問題或拉取請求。

## 許可證

MIT

## 鳴謝

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Billboard Charts](https://www.billboard.com/charts/hot-100/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- [Spotipy](https://spotipy.readthedocs.io/)
