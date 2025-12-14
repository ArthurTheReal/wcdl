# WCDL - Weeb Central Manga Downloader

A powerful command-line interface for searching and downloading manga from [WeebCentral](https://weebcentral.com/). Built with Python, it provides fast multi-threaded downloads, intelligent chapter selection, and CBZ file creation.

## ✨ Features

- **🔍 Advanced Search** - Search for manga by title with detailed result filtering
- **📥 Fast Downloads** - Multi-threaded concurrent downloads (configurable up to 8+ connections)
- **📖 Smart Chapter Selection** - Download specific chapters using flexible range syntax
  - Single chapters: `wcdl download "Manga" --range 5`
  - Ranges: `wcdl download "Manga" --range 1-10`
  - Multiple chapters: `wcdl download "Manga" --range 1,3,5-7`
- **📦 CBZ Creation** - Automatically create Comic Book Archive files from downloaded chapters
- **✅ Duplicate Detection** - Skips already downloaded chapters automatically
- **🎨 Beautiful Terminal UI** - Rich formatted tables and progress bars
- **🔄 Retry Logic** - Automatic retry with exponential backoff for failed requests
- **⚡ Resume Support** - Continue interrupted downloads without re-downloading existing files

## 🚀 Installation

### From PyPI (Once Published)

pip install wcdl

### From Source

# Clone the repository
git clone https://github.com/yourusername/wcdl.git
cd wcdl

# Install with Poetry
poetry install

# Or install in development mode
poetry install --with dev

### Requirements

- Python 3.8+
- Dependencies automatically installed via Poetry:
  - `click` - Command-line interface creation
  - `rich` - Beautiful terminal output
  - `requests` - HTTP requests with retry logic
  - `beautifulsoup4` - HTML parsing
  - `pillow` - Image processing (optional, for advanced features)

## 📖 Usage

### Quick Start

# Search for manga
wcdl search "Jujutsu Kaisen"

# Download specific chapters
wcdl download "Jujutsu Kaisen" --range 1-5

# Download with CBZ files
wcdl download "Jujutsu Kaisen" --range 1-50 --cbz

### Commands

#### `wcdl search <QUERY>`

Search for manga and display detailed information.

wcdl search "Attack on Titan"

**What it does:**
1. Searches WeebCentral for matching manga
2. Displays a formatted table of results
3. Lets you select a manga by ID
4. Shows detailed information:
   - Title, authors, and tags
   - Publication status and year
   - Total chapters available
   - Latest chapter release date
   - Number of chapters already downloaded (if any)

#### `wcdl download <QUERY> [OPTIONS]`

Search for manga and download specific chapters.

wcdl download "One Piece" --range 1-100 --cbz --connections 16

**Options:**

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--range` | `-r` | TEXT | None | Chapters to download (e.g., `1-5`, `1,3,5`, `2`) |
| `--cbz` | | FLAG | False | Create CBZ files from chapters |
| `--keep-files` | | FLAG | False | Keep image files after CBZ creation |
| `--connections` | `-c` | INT | 8 | Number of simultaneous downloads |

**Range Syntax:**
- `5` - Download chapter 5 only
- `1-10` - Download chapters 1 through 10 (inclusive)
- `1,3,5` - Download chapters 1, 3, and 5
- `1-5,10-15` - Download chapters 1-5 and 10-15
- `1,2-5,8` - Mix single and range selections

**Examples:**

# Download first 20 chapters as individual image folders
wcdl download "Solo Leveling" -r 1-20

# Download chapters and create CBZ files with 4 parallel connections
wcdl download "Jujutsu Kaisen" -r 1-50 --cbz -c 4

# Download and create CBZ files, keep original images
wcdl download "Bleach" -r 1-366 --cbz --keep-files

# Interactive mode (no range specified - choose during execution)
wcdl download "Death Note"

## 📁 Directory Structure

After downloading, manga is organized as follows:

Manga_Title/
├── Chapter_1/
│   ├── image_1.jpg
│   ├── image_2.jpg
│   └── ...
├── Chapter_2/
│   ├── image_1.jpg
│   ├── image_2.jpg
│   └── ...
├── Chapter_1.cbz (if --cbz flag used)
├── Chapter_2.cbz (if --cbz flag used)
└── ...

**With `--cbz --keep-files`**: Both image directories and CBZ files are preserved
**With `--cbz` (without `--keep-files`)**: Only CBZ files remain, image directories are deleted

## 🛠️ Project Structure

wcdl/
├── __init__.py           # Package initialization
├── cli.py               # Command-line interface (Click commands)
├── fetch.py             # Web scraping and manga information retrieval
├── download.py          # Multi-threaded chapter downloading
├── tools.py             # Utility functions and terminal formatting
├── settings.py          # Configuration URLs and constants
└── pyproject.toml       # Poetry configuration

### Module Overview

**`fetch.py`** - Web scraping module
- `search(query)` - Search for manga by title
- `get_chapters(manga_id)` - Fetch chapter list for a manga
- `get_chapter_images(chapter_id)` - Get image URLs for a chapter

**`download.py`** - Download management
- `download(url, out_dir)` - Download single image file
- `download_chapter(manga_name, chapter_name, urls, ...)` - Download entire chapter with threading

**`tools.py`** - Helper utilities
- `random_headers(url)` - Generate random HTTP headers for requests
- `safe_request(url, ...)` - HTTP requests with automatic retry logic
- Terminal formatting functions: `success()`, `error()`, `warn()`, `notic()`

**`cli.py`** - Command-line interface
- Interactive search and selection
- Range parsing and validation
- Download coordination

## ⚙️ Configuration

Edit `wcdl/settings.py` to change target website URLs:

SITE = "https://weebcentral.com/"
SEARCH_URL = SITE + "search/data"
CHAPTER_LIST_URL = "https://weebcentral.com/series/{}/full-chapter-list"
CHAPTER_IMAGES_URL = "https://weebcentral.com/chapters/{}/images"

## 🔄 Download Behavior

### Smart Download Management

- **Duplicate Detection**: If a chapter is already downloaded, it's automatically skipped
- **File Persistence**: Image files are checked before downloading; existing files are preserved
- **Progress Tracking**: Real-time progress bar shows download status
- **Error Handling**: Failed downloads don't stop the entire operation

### Thread Configuration

The `--connections` parameter controls download speed:
- **Fewer connections** (2-4): Lower resource usage, good for stable connections
- **Default** (8): Balanced for most networks
- **More connections** (16+): Faster downloads, requires stable internet

**Warning**: Very high thread counts may be throttled by the server.

## 🐛 Troubleshooting

### "No results found"
- Try different search terms or variations of the manga title
- Verify the manga exists on WeebCentral

### "HTTP 403 Forbidden"
- The scraper's headers may need updating if the website changed
- Check `tools.py` and update user-agent strings if necessary

### Slow downloads
- Increase `--connections` value for faster parallel downloads
- Check your internet connection speed
- Try during off-peak hours

### "Connection timeout"
- The website may be temporarily unavailable
- The tool automatically retries up to 5 times with exponential backoff
- Check your internet connectivity

### Incomplete chapters
- Verify the chapter exists on WeebCentral
- Try re-running the download command (it will skip existing files)
- Check available disk space

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Support for additional manga websites
- GUI version
- Advanced filtering and search options
- Batch downloading from lists
- Metadata and cover image support

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [Requests](https://requests.readthedocs.io/) for HTTP functionality

## 📞 Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Review existing GitHub issues
3. Create a new GitHub issue with detailed information

---

**Happy reading! 📚**