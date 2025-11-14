# Trae.ai Changelog Scraper

![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen?logo=github)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Updates](https://img.shields.io/badge/Updates-Every%2015min-blue)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)

Automated service that scrapes the [Trae.ai changelog](https://www.trae.ai/changelog), downloads images, and converts it to markdown format. Updates automatically every 15 minutes (96 times per day).

## Features

- Scrapes Trae.ai changelog page
- Downloads and stores all images locally
- Converts HTML to clean markdown format
- Runs automatically every 15 minutes via Docker cron or GitHub Actions
- Publishes to GitHub Pages for easy viewing
- Docker containerized for easy deployment

## Quick Start

### Testing Locally First (Recommended)

Before deploying to GitHub, test the scraper locally:

1. **Clone this repository**
   ```bash
   git clone https://github.com/amacsmith/trae-changelog-scraper.git
   cd trae-changelog-scraper
   ```

2. **Test the scraper without Docker**
   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Create output directory
   mkdir -p output/images

   # Run the scraper once
   python scraper.py
   ```

3. **Check the output**
   - Open `output/changelog.md` to see the markdown
   - Check `output/images/` for downloaded images

4. **Test with Docker (without git push)**
   ```bash
   # Build the image
   docker-compose build

   # Run once without restart
   docker run --rm -v ${PWD}/output:/app/output trae-changelog-scraper python /app/scraper.py

   # Check the logs
   docker-compose logs -f
   ```

Once you verify it works, proceed to the full deployment below.

### Full Deployment Setup

This project uses a **dual-repository** approach:
1. **Main repo** (this one): Contains the scraper code, Dockerfile, and configuration
2. **Output repo**: Contains the scraped changelog and images (auto-updated by Docker)

#### Step 1: Create Two GitHub Repositories

1. **Create the main repository** (for the scraper code)
   ```bash
   gh repo create trae-changelog-scraper --public --source=. --remote=origin --push
   ```

2. **Create the output repository** (for the scraped content)
   ```bash
   gh repo create trae-changelog-output --public
   ```

#### Step 2: Set Up the Output Directory

Run the setup script to initialize the output directory as a git repository:

```bash
chmod +x setup-git.sh
./setup-git.sh
```

This will:
- Initialize git in the `output/` directory
- Prompt you for the output repository URL
- Create initial files

#### Step 3: Configure GitHub Pages

1. **For the output repository:**
   - Go to Settings > Pages
   - Source: Deploy from a branch
   - Branch: `main` / `root`
   - Click Save

2. **Your changelog will be available at:**
   `https://amacsmith.github.io/trae-changelog-output/`

#### Step 4: Start the Docker Service

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f

# Verify it's running
docker ps
```

The Docker service will:
- Scrape the changelog every 15 minutes
- Download images
- Commit changes to the output repository
- Push to GitHub automatically

### Option 1: GitHub Pages (Recommended for sharing)

After setting up as described above:

1. **Enable GitHub Actions** (if using the deployment workflow)
   - Go to repository Settings > Actions > General
   - Enable "Read and write permissions" for workflows

3. **Enable GitHub Pages**
   - Go to repository Settings > Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` / `root`
   - Click Save

4. **Trigger the workflow**
   - Go to Actions tab
   - Click "Scrape Trae Changelog" workflow
   - Click "Run workflow"

5. **View your changelog**
   - After the workflow completes, visit: `https://yourusername.github.io/trae-changelog-scraper/`

The changelog will update automatically every 15 minutes!

### Option 2: Docker (For local deployment)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd trae-changelog-scraper
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

4. **Check the output**
   - Markdown file: `./output/changelog.md`
   - Images: `./output/images/`

5. **Stop the service**
   ```bash
   docker-compose down
   ```

### Option 3: Manual Run (For testing)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the scraper**
   ```bash
   python scraper.py
   ```

3. **Check the output**
   - The script will create `output/` directory with markdown and images

## Project Structure

```
trae-changelog-scraper/
├── .github/
│   └── workflows/
│       └── scrape-and-publish.yml  # GitHub Actions workflow
├── scraper.py                       # Main scraping script
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker container definition
├── docker-compose.yml              # Docker Compose configuration
├── output/                         # Output directory (Docker)
│   ├── changelog.md               # Generated markdown
│   └── images/                    # Downloaded images
└── docs/                           # GitHub Pages output
    ├── index.html                 # Web viewer
    ├── changelog.md              # Generated markdown
    └── images/                    # Downloaded images
```

## Configuration

### Update Frequency

The scraper runs every 15 minutes by default (96 times per day).

**To change the schedule:**

1. **For Docker**: Edit `Dockerfile` line 27
   ```dockerfile
   # Current: every 15 minutes
   RUN echo "*/15 * * * * ..."

   # Every 5 minutes:
   RUN echo "*/5 * * * * ..."

   # Every 30 minutes:
   RUN echo "*/30 * * * * ..."

   # Every hour:
   RUN echo "0 * * * * ..."
   ```

2. **For GitHub Actions**: Edit `.github/workflows/scrape-and-publish.yml` line 5
   ```yaml
   # Current: every 15 minutes
   - cron: '*/15 * * * *'

   # Every 5 minutes:
   - cron: '*/5 * * * *'

   # Every 30 minutes:
   - cron: '*/30 * * * *'

   # Every hour:
   - cron: '0 * * * *'
   ```

### Source URL

To scrape a different page, edit `scraper.py` line 22:
```python
CHANGELOG_URL = "https://www.trae.ai/changelog"
```

## Dependencies

- Python 3.11+
- requests - HTTP library for fetching pages
- beautifulsoup4 - HTML parsing
- html2text - HTML to markdown conversion
- lxml - XML/HTML parser

## Sharing Your Changelog

Once deployed to GitHub Pages, you can share:

- **Direct link**: `https://yourusername.github.io/trae-changelog-scraper/`
- **Repository**: Share the GitHub repo for others to fork
- **Raw markdown**: Link to `https://yourusername.github.io/trae-changelog-scraper/changelog.md`

## Troubleshooting

### GitHub Actions not running

1. Check if Actions are enabled in repository settings
2. Ensure workflow has write permissions
3. Manually trigger from Actions tab to test

### Images not loading on GitHub Pages

1. Check that images are being committed to the `docs/images/` directory
2. Verify image paths in the markdown are relative (`images/filename.jpg`)
3. Check browser console for CORS or path errors

### Docker container not updating

1. Check container logs: `docker-compose logs -f`
2. Verify cron is running: `docker exec trae-changelog-scraper crontab -l`
3. Check output directory has write permissions

## Manual Trigger

### GitHub Actions
- Go to Actions tab > "Scrape Trae Changelog" > "Run workflow"

### Docker
```bash
docker exec trae-changelog-scraper python /app/scraper.py
```

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Pull requests welcome! Feel free to:
- Add new features
- Improve markdown conversion
- Enhance error handling
- Optimize image handling

## Credits

Scrapes content from [Trae.ai](https://www.trae.ai/changelog)
