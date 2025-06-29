# 🎵 YouTube Playlist Creator

Create YouTube playlists automatically from CSV files containing song titles and artists.

## ✨ Features

- **CSV Import**: Upload CSV files with song titles and artists
- **Automatic Search**: Find matching YouTube videos for each song
- **Playlist Creation**: Create playlists with customizable privacy settings
- **Duplicate Detection**: Automatically skip duplicate videos
- **CLI Interface**: Command-line tools for power users
- **REST API**: Web API for integration with other applications
- **Preview Mode**: Preview CSV contents before processing
- **Comprehensive Logging**: Detailed logs for troubleshooting

## 🚀 Quick Start

### Prerequisites

- Python 3.9+ (tested with Python 3.13.2)
- YouTube Data API v3 key
- macOS (optimized for macOS development)

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd youtube-playlist-creator
   make setup
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Configure API key:**
   Edit `.env` file and add your YouTube API key:
   ```
   YOUTUBE_API_KEY=your_actual_api_key_here
   ```

4. **Test installation:**
   ```bash
   make test-services
   ```

## 📁 Project Structure

```
youtube-playlist-creator/
├── venv/                    # Virtual environment
├── csv_files/              # CSV files for processing
│   ├── .gitkeep           
│   └── sample.csv         # Sample CSV for testing
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── cli.py             # CLI interface
│   ├── services/
│   │   ├── csv_parser.py  # CSV parsing logic
│   │   ├── youtube_api.py # YouTube API integration
│   │   └── playlist_creator.py # Main orchestration
│   ├── models/
│   │   └── schemas.py     # Data models
│   └── utils/
├── tests/                  # Test files
├── logs/                   # Application logs
├── scripts/
│   └── dev.sh             # Development helper script
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── Makefile              # Development commands
├── .env                  # Environment variables
└── README.md
```

## 🖥️ Usage

### CLI Interface

**List available CSV files:**
```bash
python -m app.cli create --list-files
```

**Create playlist from CSV:**
```bash
python -m app.cli create --file sample.csv --playlist-name "My Awesome Playlist"
```

**Preview CSV file:**
```bash
python -m app.cli preview --file sample.csv --rows 10
```

**Test all services:**
```bash
python -m app.cli test
```

### REST API

**Start the API server:**
```bash
make run-api
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API Documentation:**
Visit `http://localhost:3000/docs` for interactive API documentation.

**Key endpoints:**
- `GET /` - API information
- `GET /list-csv-files` - List available CSV files
- `GET /preview-csv` - Preview CSV contents
- `POST /upload-csv` - Upload and process CSV file
- `POST /create-from-csv-folder` - Process CSV from csv_files folder
- `GET /health` - Health check

### Development Helper Script

```bash
# Start API server
./scripts/dev.sh api

# List CSV files
./scripts/dev.sh list

# Create playlist
./scripts/dev.sh create sample.csv

# Test services
./scripts/dev.sh test
```

## 📄 CSV Format

Your CSV file must have these columns:
- `Title`: Song title
- `Artist`: Artist name

Example:
```csv
Title,Artist
Shape of You,Ed Sheeran
Blinding Lights,The Weeknd
Bohemian Rhapsody,Queen
```

## ⚙️ Configuration

Edit `.env` file to configure:

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
LOG_LEVEL=INFO
MAX_SEARCH_RESULTS=5
DEFAULT_PLAYLIST_PRIVACY=private
```

## 🔧 Development

**Available make commands:**
```bash
make setup        # Initial setup
make install      # Install dependencies
make run-api      # Start API server
make run-cli      # Show CLI help
make test-cli     # Test with sample CSV
make test         # Run tests
make clean        # Clean cache files
make help         # Show all commands
```

**Development workflow:**
1. Activate virtual environment: `source venv/bin/activate`
2. Make changes to code
3. Test with: `./scripts/dev.sh test`
4. Run API: `./scripts/dev.sh api`
5. Test CLI: `./scripts/dev.sh create sample.csv`

## 🔑 Getting YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add the key to your `.env` file

## 🔐 OAuth2 Authentication Setup

**This project now supports OAuth2 authentication for creating playlists!**

### Why OAuth2?
- **API Key**: Only allows searching YouTube (read-only)
- **OAuth2**: Required for creating playlists, adding videos (write access)

### Quick Setup

1. **Run the setup script:**
   ```bash
   python setup_oauth.py
   ```

2. **Follow the guided setup:**
   - Check credential files
   - Run OAuth tests
   - Verify integration

### Manual Setup

1. **Create OAuth2 credentials in Google Cloud Console:**
   - Desktop application for CLI usage
   - Web application for API endpoints

2. **Download credential files:**
   - `client_secrets.json` (Desktop OAuth)
   - `web_client_secrets.json` (Web OAuth)

3. **Test your setup:**
   ```bash
   python test_desktop_oauth.py    # Test CLI OAuth
   python test_web_oauth.py        # Test API OAuth
   python test_full_integration.py # Test everything
   ```

### Detailed Instructions

**👉 See `OAUTH_SETUP_GUIDE.md` for complete step-by-step instructions.**

**Required files after setup:**
```
youtube-playlist-creator/
├── client_secrets.json          # Desktop OAuth (for CLI)
├── web_client_secrets.json      # Web OAuth (for API)
├── test_desktop_oauth.py        # Test scripts
├── test_web_oauth.py
├── test_full_integration.py
└── OAUTH_SETUP_GUIDE.md         # Complete setup guide
```

## 🎯 Example Usage

**1. Prepare your CSV file:**
```csv
Title,Artist
Imagine,John Lennon
Hotel California,Eagles
Bohemian Rhapsody,Queen
```

**2. Place it in csv_files folder:**
```bash
cp my_songs.csv csv_files/
```

**3. Create playlist:**
```bash
python -m app.cli create --file my_songs.csv --playlist-name "Classic Rock Hits"
```

**4. Results:**
```
🎉 PLAYLIST CREATION COMPLETE!
==================================================
📋 Playlist: Classic Rock Hits
🔗 URL: https://www.youtube.com/playlist?list=PLxxxxxx
📊 Total songs processed: 3
✅ Successfully added: 3
❌ Not found: 0
🔄 Duplicates skipped: 0
```

## 🐛 Troubleshooting

**Common issues:**

1. **API Key Error**: Ensure your YouTube API key is valid and has YouTube Data API v3 enabled
2. **CSV Format Error**: Check that your CSV has 'Title' and 'Artist' columns
3. **Song Not Found**: Some songs might not be available on YouTube or have different titles
4. **Quota Exceeded**: YouTube API has daily quotas; wait until reset or upgrade quota

**Debug mode:**
Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

## 📊 Performance

- Average processing time: ~2-5 seconds per song
- Success rate: ~85-95% depending on song popularity
- API quota usage: ~100 units per song search + playlist operations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Create Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- YouTube Data API v3
- FastAPI framework
- Click CLI library
- Pandas for CSV processing

## 📞 Support

- Create an issue for bugs or feature requests
- Check logs in `logs/` folder for debugging
- Use `make test-services` to diagnose issues
