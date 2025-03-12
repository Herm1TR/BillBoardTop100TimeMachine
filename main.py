import os
import sys
import logging
import argparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('billboard_spotify')

def validate_date(date_str):
    """驗證日期格式並確保它是有效的。"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_billboard_songs(date):
    """從Billboard熱門100榜單抓取指定日期的歌曲。"""
    try:
        url = f"https://www.billboard.com/charts/hot-100/{date}/"
        logger.info(f"正在獲取 {url} 的數據...")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 檢查HTTP錯誤
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 第一首歌與其他歌曲的HTML結構不同
        song_titles = []
        
        # 獲取第一首歌
        first_song = soup.find(
            name="h3", 
            class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 u-max-width-230@tablet-only u-letter-spacing-0028@tablet",
            id="title-of-a-story"
        )
        
        if first_song:
            song_titles.append(first_song.text.strip())
        
        # 獲取排名2-100的歌曲
        other_songs = soup.find_all(
            name="h3", 
            id="title-of-a-story",
            class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only"
        )
        
        song_titles.extend([song.text.strip() for song in other_songs])
        
        if not song_titles:
            logger.error("無法找到歌曲。Billboard網站可能已更改其HTML結構。")
            return []
            
        logger.info(f"成功擷取到 {len(song_titles)} 首歌曲")
        return song_titles
        
    except requests.exceptions.RequestException as e:
        logger.error(f"獲取Billboard數據時發生錯誤: {e}")
        return []

def setup_spotify_client():
    """設置並返回Spotify客戶端。"""
    required_env_vars = ["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", 
                         "SPOTIFY_REDIRECT_URI", "SPOTIFY_USERNAME"]
    
    # 檢查所有必需的環境變量
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"缺少必要的環境變量: {', '.join(missing_vars)}")
        logger.info("請設置以下環境變量: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, "
                   "SPOTIFY_REDIRECT_URI, SPOTIFY_USERNAME")
        return None
    
    try:
        sp_auth = SpotifyOAuth(
            client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
            client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI"),
            username=os.environ.get("SPOTIFY_USERNAME"),
            scope="playlist-modify-private"
        )
        
        sp = spotipy.Spotify(oauth_manager=sp_auth)
        # 測試連接
        sp.current_user()
        logger.info("成功連接到Spotify API")
        return sp
    
    except Exception as e:
        logger.error(f"連接Spotify時發生錯誤: {e}")
        return None

def find_spotify_tracks(sp, song_titles, date):
    """在Spotify中查找歌曲並返回URI列表。"""
    if not sp or not song_titles:
        return []
    
    track_uris = []
    year = date.split('-')[0]  # 從日期提取年份以優化搜尋
    
    logger.info(f"開始在Spotify中搜索 {len(song_titles)} 首歌曲...")
    
    for index, title in enumerate(song_titles, 1):
        try:
            # 將年份納入查詢以提高匹配精確度
            search_query = f"track:{title} year:{year}"
            result = sp.search(q=search_query, type="track", limit=1)
            
            if result["tracks"]["items"]:
                track_uri = result["tracks"]["items"][0]["uri"]
                track_name = result["tracks"]["items"][0]["name"]
                artist = result["tracks"]["items"][0]["artists"][0]["name"]
                track_uris.append(track_uri)
                logger.info(f"找到 ({index}/{len(song_titles)}): {track_name} by {artist}")
            else:
                # 如果添加年份沒有結果，嘗試僅使用標題
                result = sp.search(q=f"track:{title}", type="track", limit=1)
                if result["tracks"]["items"]:
                    track_uri = result["tracks"]["items"][0]["uri"]
                    track_name = result["tracks"]["items"][0]["name"]
                    artist = result["tracks"]["items"][0]["artists"][0]["name"]
                    track_uris.append(track_uri)
                    logger.info(f"找到 ({index}/{len(song_titles)}): {track_name} by {artist}")
                else:
                    logger.warning(f"未找到歌曲 ({index}/{len(song_titles)}): {title}")
        
        except Exception as e:
            logger.error(f"搜索歌曲 '{title}' 時發生錯誤: {e}")
    
    logger.info(f"在Spotify中共找到 {len(track_uris)}/{len(song_titles)} 首歌曲")
    return track_uris

def create_spotify_playlist(sp, track_uris, date):
    """創建Spotify播放列表並添加歌曲。"""
    if not sp or not track_uris:
        return None
    
    try:
        username = os.environ.get("SPOTIFY_USERNAME")
        playlist_name = f"Billboard Hot 100 - {date}"
        playlist_description = f"Billboard Hot 100 songs from {date}, created automatically."
        
        logger.info(f"正在創建播放列表 '{playlist_name}'...")
        
        playlist = sp.user_playlist_create(
            user=username,
            name=playlist_name,
            public=False,
            description=playlist_description
        )
        
        # 每次最多添加100首歌曲
        sp.playlist_add_items(playlist_id=playlist["id"], items=track_uris)
        
        logger.info(f"成功創建播放列表 '{playlist_name}' 並添加了 {len(track_uris)} 首歌曲")
        return playlist["external_urls"]["spotify"]
    
    except Exception as e:
        logger.error(f"創建播放列表時發生錯誤: {e}")
        return None

def main():
    """主程序入口點。"""
    parser = argparse.ArgumentParser(description='創建基於歷史Billboard Hot 100的Spotify播放列表')
    parser.add_argument('--date', type=str, help='日期格式為YYYY-MM-DD')
    args = parser.parse_args()
    
    # 獲取日期輸入
    date = args.date
    if not date:
        date = input("請輸入您想回溯的日期 (格式: YYYY-MM-DD): ")
    
    # 驗證日期格式
    if not validate_date(date):
        logger.error("無效的日期格式。請使用YYYY-MM-DD格式。")
        return 1
    
    # 從Billboard獲取歌曲
    song_titles = get_billboard_songs(date)
    if not song_titles:
        return 1
    
    # 設置Spotify客戶端
    sp = setup_spotify_client()
    if not sp:
        return 1
    
    # 在Spotify中查找歌曲
    track_uris = find_spotify_tracks(sp, song_titles, date)
    if not track_uris:
        logger.error("無法找到任何歌曲在Spotify中，無法創建播放列表。")
        return 1
    
    # 創建播放列表
    playlist_url = create_spotify_playlist(sp, track_uris, date)
    if not playlist_url:
        return 1
    
    # 顯示成功消息
    logger.info("-" * 60)
    logger.info(f"您的播放列表已成功創建!")
    logger.info(f"播放列表鏈接: {playlist_url}")
    logger.info("-" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
