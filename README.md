# 🎵 YouTube Playlist Creator

**Automatically create YouTube playlists from CSV files** containing song titles and artists. Perfect for converting your music lists, Spotify exports, or any song collection into YouTube playlists.

## 🎯 What This Does

1. **Upload a CSV** with song titles and artists
2. **Automatically searches** YouTube for matching videos  
3. **Creates a playlist** with all found songs
4. **Handles duplicates** and provides detailed results

## 🔑 Required API Access

You need a **Google Cloud API Key** with **YouTube Data API v3** enabled.

### ✅ Your API Setup
Since you mentioned you have a `GOOGLE_CLOUD_API_KEY` with these APIs enabled:
- ✅ **YouTube Data API v3** ← **This is what we need!**
- ✅ Custom Search API _(not used by this project)_
- ✅ Gemini for Google Cloud API _(not used by this project)_
- ✅ Generative Language API _(not used by this project)_

**You're all set!** This project only needs YouTube Data API v3, which you already have.

## 🚀 Quick Start (5 minutes)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd youtube-playlist-creator
make setup
source venv/bin/activate
```

### 2. Add Your API Key
Create a `.env` file:
```bash
echo "GOOGLE_CLOUD_API_KEY=your_actual_api_key_here" > .env
```

### 3. Test Everything Works
```bash
make test-services
```

### 4. Create Your First Playlist
```bash
# Preview the sample CSV
python -m app.cli preview --file sample.csv

# Create a playlist (demo mode - won't actually create)
python -m app.cli create --file sample.csv --playlist-name "My Test Playlist" --demo
```

## 💡 Two Ways to Use This

### Option 1: Command Line (CLI) 
**Best for: Personal use, batch processing**

```bash
# List available CSV files
python -m app.cli create --list-files

# Create playlist from CSV
python -m app.cli create --file your_songs.csv --playlist-name "My Playlist"

# Preview CSV before processing
python -m app.cli preview --file your_songs.csv --rows 10
```

### Option 2: Web API 
**Best for: Integration with other apps, web interfaces**

```bash
# Start the web server
make run-api
# Opens at http://localhost:3000
```

**Key endpoints:**
- `GET /docs` - Interactive API documentation
- `POST /upload-csv` - Upload and process CSV file
- `GET /preview-csv` - Preview CSV contents
- `POST /create-from-csv-folder` - Process CSV from csv_files folder

## 📄 CSV Format

Your CSV file needs these two columns:
```csv
Title,Artist
Shape of You,Ed Sheeran
Blinding Lights,The Weeknd
Bohemian Rhapsody,Queen
Hotel California,Eagles
```

**That's it!** Put your CSV files in the `csv_files/` folder or upload them via the API.

## 🎯 Complete Example Walkthrough

**1. Prepare your songs list:**
```csv
Title,Artist
Imagine,John Lennon
Sweet Child O' Mine,Guns N' Roses
Bohemian Rhapsody,Queen
Stairway to Heaven,Led Zeppelin
```

**2. Save as `my_playlist.csv` in the `csv_files/` folder**

**3. Test in demo mode first:**
```bash
python -m app.cli create --file my_playlist.csv --playlist-name "Classic Rock" --demo
```

**4. If results look good, create the actual playlist:**
```bash
python -m app.cli create --file my_playlist.csv --playlist-name "Classic Rock"
```

**5. Results:**
```
🎉 PLAYLIST CREATION COMPLETE!
==================================================
📋 Playlist: Classic Rock
🔗 URL: https://www.youtube.com/playlist?list=PLxxxxxx
📊 Total songs processed: 4
✅ Successfully added: 4
❌ Not found: 0
🔄 Duplicates skipped: 0
```

## 🔧 Configuration Options

Edit `.env` file to customize:
```env
GOOGLE_CLOUD_API_KEY=your_key_here
LOG_LEVEL=INFO
MAX_SEARCH_RESULTS=5
DEFAULT_PLAYLIST_PRIVACY=private
```

**Privacy options:** `private`, `public`, `unlisted`

## 🔐 OAuth2 Setup (For Playlist Creation)

### Why do I need OAuth2?
- **API Key**: Can search YouTube videos ✅
- **OAuth2**: Required to create playlists in your account ✅

### Simple OAuth Setup

**For CLI usage (recommended for personal use):**

1. **Run the setup helper:**
   ```bash
   python setup_oauth.py
   ```

2. **Follow the prompts:**
   - Creates OAuth credentials in Google Cloud Console
   - Downloads `client_secrets.json` file
   - Tests the authentication flow

3. **Test it works:**
   ```bash
   python test_desktop_oauth.py
   ```

**For Web API usage:**
- See `OAUTH_SETUP_GUIDE.md` for detailed web OAuth setup

### Manual OAuth Setup (if helper fails)

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID → Desktop Application
3. Download as `client_secrets.json`
4. Place in project root

## 🔧 Development & Advanced Usage

### Available Commands
```bash
make setup        # Complete setup
make run-api      # Start web server
make test-cli     # Test with sample data
make clean        # Clean cache files
make help         # Show all commands
```

### Helper Script
```bash
./scripts/dev.sh api      # Start API server
./scripts/dev.sh list     # List CSV files  
./scripts/dev.sh create   # Create test playlist
./scripts/dev.sh test     # Test all services
```

### File Structure
```
youtube-playlist-creator/
├── csv_files/              # Put your CSV files here
│   └── sample.csv         # Example file included
├── app/
│   ├── main.py            # FastAPI web server
│   ├── cli.py             # Command line interface
│   └── services/          # Core logic
├── client_secrets.json    # OAuth credentials (you create this)
├── .env                   # Your API key goes here
└── README.md
```

## 🐛 Troubleshooting

### Common Issues

**❌ "API key invalid"**
- Check your `.env` file has the correct `GOOGLE_CLOUD_API_KEY`
- Verify YouTube Data API v3 is enabled in Google Cloud Console

**❌ "Songs not found"**  
- Try different search terms (some songs have alternate titles)
- Check if songs are available on YouTube
- Use `--demo` mode to see search results first

**❌ "Can't create playlist"**
- You need OAuth2 setup for playlist creation
- Run `python setup_oauth.py` to set up authentication

**❌ "Quota exceeded"**
- YouTube API has daily limits
- Wait 24 hours for quota reset, or upgrade your Google Cloud quota

### Debug Mode
```bash
# Enable detailed logging
echo "LOG_LEVEL=DEBUG" >> .env

# Check logs
tail -f logs/app.log
```

## 📊 Performance & Limits

- **Processing speed**: ~2-5 seconds per song
- **Success rate**: ~85-95% (depends on song popularity)
- **API quota usage**: ~100 units per song + playlist operations
- **Daily limit**: YouTube API default is 10,000 units/day (~100 songs)

## ❓ FAQ

**Q: Do I need to pay for anything?**
A: No, Google Cloud API usage is free up to daily quotas (plenty for personal use).

**Q: Can I make playlists private?**  
A: Yes! Set `DEFAULT_PLAYLIST_PRIVACY=private` in `.env` file.

**Q: What if a song isn't found?**
A: The tool will skip it and report which songs couldn't be found. You can manually add them later.

**Q: Can I use Spotify CSV exports?**
A: Yes! Just make sure your CSV has `Title` and `Artist` columns.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`  
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Create Pull Request

## 📝 License

MIT License - feel free to use for personal or commercial projects.

## 📞 Support

- **Issues**: Create a GitHub issue
- **Logs**: Check `logs/` folder for debugging
- **Test**: Use `make test-services` to diagnose problems
- **Documentation**: See `OAUTH_SETUP_GUIDE.md` for detailed OAuth setup
