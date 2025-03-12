# Billboard Hot 100 to Spotify Playlist Converter

This tool allows you to select a historical date and automatically create a Spotify playlist containing the Billboard Hot 100 chart songs from that date. It's perfect for users who want to relive past music memories or explore popular music from different eras.

## Features

- Scrapes songs from the Billboard Hot 100 chart for a specified date
- Automatically searches for these songs on Spotify
- Creates a private Spotify playlist and adds the found songs
- Provides detailed logging to track progress and any issues

## Installation

### Prerequisites

- Python 3.6+
- Spotify account
- Spotify developer application (for API access)

### Steps

1. Clone this repository:

```bash
git clone https://github.com/yourusername/billboard-to-spotify.git
cd billboard-to-spotify
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your Spotify developer account:
   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Create a new application
   - Set up a redirect URI (e.g., `http://localhost:8888/callback`)
   - Note down the Client ID and Client Secret

4. Set environment variables:

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

Alternatively, you can create a `.env` file and load it using `python-dotenv`:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=your_redirect_uri
SPOTIFY_USERNAME=your_spotify_username
```

## Usage

### Command Line Arguments

```bash
python main.py --date YYYY-MM-DD
```

### Interactive

If you don't provide a date parameter, the program will prompt you to enter one:

```bash
python main.py
```

Then follow the prompts to enter a date (in YYYY-MM-DD format).

## Example

```bash
python main.py --date 1985-07-13
```

This will create a Spotify playlist containing songs from the Billboard Hot 100 chart from July 13, 1985.

## Error Handling

The program includes multiple layers of error handling:

- Date format validation
- HTTP request error handling
- Web content parsing error handling
- Spotify API connection and authorization error handling
- Song search error handling
- Playlist creation error handling

All errors and progress information are displayed through the logging system, which is both user-friendly for tracking program execution and helpful for developers during troubleshooting.

## Frequently Asked Questions

**Q: I see many songs weren't found, what can I do?**  
A: Some older songs may not be available on Spotify, or there might be issues with song name matching. You can try using a more recent date or manually add the songs that couldn't be found.

**Q: I'm being redirected to a browser on first run?**  
A: This is part of the Spotify OAuth authorization process. Please log in to your Spotify account and authorize your application.

**Q: Will changes to the Billboard website affect the program?**  
A: Yes, if Billboard changes its HTML structure, the scraping might fail. Please report any issues so the code can be updated.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

MIT

## Acknowledgments

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Billboard Charts](https://www.billboard.com/charts/hot-100/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- [Spotipy](https://spotipy.readthedocs.io/)
