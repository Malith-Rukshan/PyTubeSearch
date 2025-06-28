<p style="text-align:center;" align="center">
  <img align="center" src="https://raw.githubusercontent.com/Malith-Rukshan/PyTubeSearch/refs/heads/main/logo.png" alt="PyTubeSearch" width="300px" height="300px"/>
</p>
<h1 align="center">🔍 PyTubeSearch</h1>
<div align='center'>

[![PyPI Package](https://img.shields.io/badge/PyPI-pytubesearch-4B8BBE?logo=pypi&style=flat)](https://pypi.org/project/pytubesearch/)
[![TestCode](https://img.shields.io/badge/Test%20Code-Ready-009688?logo=verizon&style=flat)](https://github.com/Malith-Rukshan/PyTubeSearch?tab=readme-ov-file#testing)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
</div>

<h4 align="center">🔥 A powerful Python package for searching YouTube content by keywords. 🔍</h4>

<div align="center">
  - Unlock the power of YouTube search with lightning-fast Python integration -
  <br/>
  <sup><sub>🚀 Built for developers, optimized for performance ツ</sub></sup>
</div>

## ✨ Features

- 🎯 **Keyword Search**: Search YouTube videos, channels, playlists by keywords
- 📹 **Video Details**: Get comprehensive video information including metadata
- 📋 **Playlist Support**: Extract playlist contents and metadata
- 📺 **Channel Information**: Retrieve channel details and content
- 🩳 **YouTube Shorts**: Access YouTube Shorts content
- 📄 **Pagination**: Handle large result sets with next page functionality
- 🚀 **Fast & Reliable**: Built with httpx for high performance
- 🔧 **Type Safe**: Full Pydantic model support with type hints
- 🎛️ **Flexible Options**: Filter by content type (video, channel, playlist, movie)

## 📦 Installation

```bash
pip install pytubesearch
```

### Development Installation

```bash
git clone https://github.com/Malith-Rukshan/PyTubeSearch.git
cd PyTubeSearch
pip install -e .
```

## 🚀 Quick Start

### Basic Search

```python
from pytubesearch import PyTubeSearch

# Initialize the client
client = PyTubeSearch()

# Search for videos
results = client.search("python programming")

# Display results
for item in results.items:
    print(f"Title: {item.title}")
    print(f"Channel: {item.channel_title}")
    print(f"Video ID: {item.id}")
    print("-" * 50)

# Close the client
client.close()
```

### Using Context Manager

```python
from pytubesearch import PyTubeSearch

with PyTubeSearch() as client:
    results = client.search("machine learning", limit=10)
    
    for video in results.items:
        if video.type == "video":
            print(f"📹 {video.title} by {video.channel_title}")
```

### Advanced Search with Filters

```python
from pytubesearch import PyTubeSearch, SearchOptions

with PyTubeSearch() as client:
    # Search only for videos
    video_options = [SearchOptions(type="video")]
    results = client.search("python tutorial", options=video_options, limit=5)
    
    # Search only for channels
    channel_options = [SearchOptions(type="channel")]
    channels = client.search("tech channels", options=channel_options, limit=3)
    
    # Search with playlists included
    playlist_results = client.search("programming courses", with_playlist=True)
```

### Get Video Details

```python
from pytubesearch import PyTubeSearch

with PyTubeSearch() as client:
    # Get detailed video information
    video_details = client.get_video_details("dQw4w9WgXcQ")
    
    print(f"Title: {video_details.title}")
    print(f"Channel: {video_details.channel}")
    print(f"Description: {video_details.description}")
    print(f"Keywords: {video_details.keywords}")
    print(f"Is Live: {video_details.is_live}")
    
    # Get suggested videos
    for suggestion in video_details.suggestion:
        print(f"Suggested: {suggestion.title}")
```

### Pagination

```python
from pytubesearch import PyTubeSearch

with PyTubeSearch() as client:
    # Get first page
    results = client.search("data science")
    
    # Process first page
    for item in results.items:
        print(f"Page 1: {item.title}")
    
    # Get next page
    if results.next_page.next_page_token:
        next_results = client.next_page(results.next_page)
        
        for item in next_results.items:
            print(f"Page 2: {item.title}")
```

### Playlist Operations

```python
from pytubesearch import PyTubeSearch

with PyTubeSearch() as client:
    # Get playlist contents
    playlist = client.get_playlist_data("PLrAXtmRdnEQy9j4XPpPNJkr0bO8E4BcJj")
    
    print(f"Playlist has {len(playlist.items)} videos")
    
    for video in playlist.items:
        print(f"🎥 {video.title}")
        print(f"   Channel: {video.channel_title}")
```

### Channel Information

```python
from pytubesearch import PyTubeSearch

with PyTubeSearch() as client:
    # Get channel information
    channel_data = client.get_channel_by_id("UC8butISFwT-Wl7EV0hUK0BQ")
    
    for tab in channel_data:
        print(f"Tab: {tab.title}")
```

### YouTube Shorts

```python
from pytubesearch import PyTubeSearch

with PyTubeSearch() as client:
    # Get YouTube Shorts
    shorts = client.get_short_videos()
    
    for short in shorts:
        print(f"🩳 {short.title}")
        print(f"   ID: {short.id}")
```

### Homepage Suggestions

```python
from pytubesearch import PyTubeSearch

with PyTubeSearch() as client:
    # Get homepage suggestions
    suggestions = client.get_suggestions(limit=10)
    
    for video in suggestions:
        print(f"💡 {video.title}")
        print(f"   Channel: {video.channel_title}")
```

> 💡 **More Examples**: Check out the [examples/](./examples/) directory for additional usage patterns and advanced implementations.

## 📚 API Reference

### PyTubeSearch Class

#### Methods

- `search(keyword, with_playlist=False, limit=0, options=None)`: Search YouTube content
- `next_page(next_page_data, with_playlist=False, limit=0)`: Get next page of results
- `get_video_details(video_id)`: Get detailed video information
- `get_playlist_data(playlist_id, limit=0)`: Get playlist contents
- `get_channel_by_id(channel_id)`: Get channel information
- `get_suggestions(limit=0)`: Get homepage suggestions
- `get_short_videos()`: Get YouTube Shorts

### Models

- `SearchResult`: Contains search results and pagination data
- `SearchItem`: Individual search result item
- `VideoDetails`: Detailed video information
- `PlaylistResult`: Playlist contents and metadata
- `ChannelResult`: Channel information
- `ShortVideo`: YouTube Shorts data
- `SearchOptions`: Search filtering options

## 🛠️ Development Guide

### Setting Up Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Malith-Rukshan/PyTubeSearch.git
   cd PyTubeSearch
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   # Option 1: Using Makefile (recommended)
   make install-dev
   
   # Option 2: Manual installation
   pip install -e .
   pip install -r requirements/dev.txt
   pre-commit install
   ```

### Development Commands

The project includes a Makefile with common development tasks:

```bash
# Install for development
make install-dev

# Run tests
make test

# Run all tests including integration tests
make test-all

# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Security checks
make security

# Run all checks
make check

# Clean build artifacts
make clean

# Build package
make build

# Upload to Test PyPI
make upload-test
```

### Testing

The project uses pytest for testing with multiple test categories:

1. **Unit Tests**: Fast tests that don't require network access
   ```bash
   pytest tests/ -m "not integration"
   ```

2. **Integration Tests**: Tests that interact with real YouTube data
   ```bash
   pytest tests/ -m "integration"
   ```

3. **All Tests with Coverage**:
   ```bash
   pytest tests/ --cov=pytubesearch --cov-report=html
   ```

### Code Quality Standards

- **Code Formatting**: [Black](https://black.readthedocs.io/) with 100 character line length
- **Import Sorting**: [isort](https://pycqa.github.io/isort/) with Black profile
- **Linting**: [Flake8](https://flake8.pycqa.org/) with custom configuration
- **Type Checking**: [mypy](https://mypy.readthedocs.io/) for static type analysis
- **Security**: [Bandit](https://bandit.readthedocs.io/) and [Safety](https://pyup.io/safety/) for security checks

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Project Structure

```
PyTubeSearch/
├── pytubesearch/           # Main package
│   ├── __init__.py        # Package initialization
│   ├── client.py          # Main client implementation
│   └── models.py          # Pydantic models
├── tests/                 # Test suite
│   ├── conftest.py        # Test configuration
│   ├── test_client.py     # Client tests
│   ├── test_models.py     # Model tests
│   └── test_integration.py # Integration tests
├── examples/              # Usage examples
├── requirements/          # Dependency management
│   ├── base.txt          # Core dependencies
│   ├── dev.txt           # Development dependencies
│   └── test.txt          # Testing dependencies
├── .github/workflows/     # CI/CD workflows
├── docs/                  # Documentation
└── ...                   # Configuration files
```

### Contributing Guidelines

1. **Fork the repository** and create your feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes** following the code quality standards

3. **Add tests** for your changes:
   - Unit tests for new functionality
   - Integration tests if applicable
   - Ensure all tests pass

4. **Update documentation** if needed:
   - Update README.md for new features
   - Add docstrings to new functions/classes
   - Update examples if applicable

5. **Run quality checks**:
   ```bash
   make check  # Runs linting, type checking, and tests
   ```

6. **Commit your changes**:
   ```bash
   git commit -m "Add amazing feature"
   ```

7. **Push to your fork** and create a Pull Request

### Release Process

1. **Update version** in `pyproject.toml` and `__init__.py`
2. **Update CHANGELOG.md** with new features and fixes
3. **Create a git tag**:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```
4. **GitHub Actions** will automatically build and publish to PyPI

### Testing with Test PyPI

Before releasing to PyPI, test the package on Test PyPI:

```bash
# Build and upload to Test PyPI
make build
make upload-test

# Install from Test PyPI to test
pip install --index-url https://test.pypi.org/simple/ pytubesearch
```

### Debugging

For debugging integration tests or development:

```bash
# Enable debug logging
export PYTUBESEARCH_DEBUG=1

# Run specific test with verbose output
pytest tests/test_integration.py::TestSearchIntegration::test_basic_search_integration -v -s
```

### Dependencies Management

The project uses a multi-file requirements approach:

- `requirements/base.txt`: Core runtime dependencies
- `requirements/dev.txt`: Development tools and utilities  
- `requirements/test.txt`: Testing framework and tools

To update dependencies:

1. Edit the appropriate requirements file
2. Test the changes locally
3. Update version constraints if needed

## 🔧 Configuration

### Timeout Settings

```python
from pytubesearch import PyTubeSearch

# Set custom timeout (default: 30 seconds)
client = PyTubeSearch(timeout=60.0)
```

### Error Handling

```python
from pytubesearch import PyTubeSearch, PyTubeSearchError

try:
    with PyTubeSearch() as client:
        results = client.search("programming")
except PyTubeSearchError as e:
    print(f"Search failed: {e}")
```

## 📋 Requirements

- Python 3.8+
- httpx >= 0.24.0
- pydantic >= 2.0.0

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/Malith-Rukshan/PyTubeSearch.git
cd PyTubeSearch
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black pytubesearch/
isort pytubesearch/
```

### Type Checking

```bash
mypy pytubesearch/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This package is for educational purposes only. Please respect YouTube's Terms of Service and robots.txt when using this package. The package author is not responsible for any misuse of this tool.

## 🙏 Acknowledgments

- YouTube for providing the platform
- The Python community for amazing tools and libraries

## 🌟 Support and Community

If you found this project helpful, please give it a ⭐ on GitHub. This helps more developers discover the project! 🫶

## 📬 Contact

If you have any questions, feedback, or just want to say hi, you can reach out to me:

- Email: [hello@malith.dev](mailto:hello@malith.dev)
- GitHub: [@Malith-Rukshan](https://github.com/Malith-Rukshan)

🧑‍💻 Built with 💖 by [Malith Rukshan](https://malith.dev)