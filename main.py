import os
import sys
import logging
import argparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('billboard_spotify')

def validate_date(date_str):
    """Validate date format and ensure it is valid."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def get_billboard_songs(date):
    """Scrape songs from the Billboard Hot 100 chart for the specified date."""
    try:
        url = f"https://www.billboard.com/charts/hot-100/{date}/"
        logger.info(f"Getting data from {url}...")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check for HTTP errors
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # The first song has a different HTML structure than the others
        song_titles = []
        
        # Get the first song
        first_song = soup.find(
            name="h3", 
            class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 u-max-width-230@tablet-only u-letter-spacing-0028@tablet",
            id="title-of-a-story"
        )
        
        if first_song:
            song_titles.append(first_song.text.strip())
        
        # Get songs ranked 2-100
        other_songs = soup.find_all(
            name="h3", 
            id="title-of-a-story",
            class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only"
        )
        
        song_titles.extend([song.text.strip() for song in other_songs])
        
        if not song_titles:
            logger.error("Could not find any songs. The Billboard website may have changed its HTML structure.")
            return []
            
        logger.info(f"Successfully extracted {len(song_titles)} songs")
        return song_titles
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred while getting Billboard data: {e}")
        return []

def setup_spotify_client():
    """Set up and return a Spotify client."""
    required_env_vars = ["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", 
                         "SPOTIFY_REDIRECT_URI", "SPOTIFY_USERNAME"]
    
    # Check all required environment variables
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please set the following environment variables: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, "
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
        # Test connection
        sp.current_user()
        logger.info("Successfully connected to Spotify API")
        return sp
    
    except Exception as e:
        logger.error(f"Error occurred while connecting to Spotify: {e}")
        return None

def find_spotify_tracks(sp, song_titles, date):
    """Search for songs on Spotify and return a list of URIs."""
    if not sp or not song_titles:
        return []
    
    track_uris = []
    year = date.split('-')[0]  # Extract year from date to optimize search
    
    logger.info(f"Starting to search for {len(song_titles)} songs on Spotify...")
    
    for index, title in enumerate(song_titles, 1):
        try:
            # Include year in query to improve match accuracy
            search_query = f"track:{title} year:{year}"
            result = sp.search(q=search_query, type="track", limit=1)
            
            if result["tracks"]["items"]:
                track_uri = result["tracks"]["items"][0]["uri"]
                track_name = result["tracks"]["items"][0]["name"]
                artist = result["tracks"]["items"][0]["artists"][0]["name"]
                track_uris.append(track_uri)
                logger.info(f"Found ({index}/{len(song_titles)}): {track_name} by {artist}")
            else:
                # If no results with year, try using just the title
                result = sp.search(q=f"track:{title}", type="track", limit=1)
                if result["tracks"]["items"]:
                    track_uri = result["tracks"]["items"][0]["uri"]
                    track_name = result["tracks"]["items"][0]["name"]
                    artist = result["tracks"]["items"][0]["artists"][0]["name"]
                    track_uris.append(track_uri)
                    logger.info(f"Found ({index}/{len(song_titles)}): {track_name} by {artist}")
                else:
                    logger.warning(f"Could not find song ({index}/{len(song_titles)}): {title}")
        
        except Exception as e:
            logger.error(f"Error occurred while searching for song '{title}': {e}")
    
    logger.info(f"Found a total of {len(track_uris)}/{len(song_titles)} songs on Spotify")
    return track_uris

def create_spotify_playlist(sp, track_uris, date):
    """Create a Spotify playlist and add songs."""
    if not sp or not track_uris:
        return None
    
    try:
        username = os.environ.get("SPOTIFY_USERNAME")
        playlist_name = f"Billboard Hot 100 - {date}"
        playlist_description = f"Billboard Hot 100 songs from {date}, created automatically."
        
        logger.info(f"Creating playlist '{playlist_name}'...")
        
        playlist = sp.user_playlist_create(
            user=username,
            name=playlist_name,
            public=False,
            description=playlist_description
        )
        
        # Add up to 100 songs at once
        sp.playlist_add_items(playlist_id=playlist["id"], items=track_uris)
        
        logger.info(f"Successfully created playlist '{playlist_name}' and added {len(track_uris)} songs")
        return playlist["external_urls"]["spotify"]
    
    except Exception as e:
        logger.error(f"Error occurred while creating playlist: {e}")
        return None

def main():
    """Main program entry point."""
    parser = argparse.ArgumentParser(description='Create Spotify playlists based on historical Billboard Hot 100 charts')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format')
    args = parser.parse_args()
    
    # Get date input
    date = args.date
    if not date:
        date = input("Please enter the date you want to look back to (format: YYYY-MM-DD): ")
    
    # Validate date format
    if not validate_date(date):
        logger.error("Invalid date format. Please use YYYY-MM-DD format.")
        return 1
    
    # Get songs from Billboard
    song_titles = get_billboard_songs(date)
    if not song_titles:
        return 1
    
    # Set up Spotify client
    sp = setup_spotify_client()
    if not sp:
        return 1
    
    # Search for songs on Spotify
    track_uris = find_spotify_tracks(sp, song_titles, date)
    if not track_uris:
        logger.error("Could not find any songs on Spotify, cannot create playlist.")
        return 1
    
    # Create playlist
    playlist_url = create_spotify_playlist(sp, track_uris, date)
    if not playlist_url:
        return 1
    
    # Display success message
    logger.info("-" * 60)
    logger.info(f"Your playlist has been successfully created!")
    logger.info(f"Playlist link: {playlist_url}")
    logger.info("-" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
