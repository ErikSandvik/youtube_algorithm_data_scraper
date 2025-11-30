# YouTube Recommendation Tracker

A Python application that automatically gathers YouTube video recommendations, tracks them in a database, and analyzes recommendation patterns.

## Features

- **Automated Recommendation Collection**: Uses Playwright to browse YouTube and collect video recommendations
- **Data Storage**: Stores videos, channels, categories, and recommendation events in a PostgreSQL database
- **YouTube API Integration**: Fetches detailed video metadata from the YouTube Data API
- **Database Migrations**: Uses Alembic for database schema management

## Prerequisites

- Python 3.12+
- PostgreSQL database (or use the included Docker setup)
- YouTube Data API key

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
YOUTUBE_API_KEY=your_youtube_api_key_here
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=dbname
```

### 3. Start Database (Optional - Docker)

If you don't have PostgreSQL installed locally:

```bash
docker-compose up -d
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Run the Application

```bash
python -m app.main
```

## Project Structure

```
app/
├── models/          # SQLAlchemy database models
├── crud/            # Database operations
├── services/        # Business logic (YouTube API, video processing, etc.)
└── main.py          # Main application entry point

alembic/             # Database migrations
tests/               # Test files
```

## How It Works

1. The application launches a browser using Playwright
2. Navigates YouTube and clicks on recommended videos
3. Collects video URLs and recommendation data
4. Fetches detailed video metadata from YouTube API
5. Stores videos, channels, and recommendation events in the database
6. Repeats the process in a continuous loop

## Running Tests

```bash
pytest
```

## Database Schema

- **videos**: YouTube video metadata
- **channels**: YouTube channel information
- **categories**: YouTube video categories
- **recommendation_events**: Tracks which videos were recommended and their positions

## Notes

- The application respects YouTube API quotas and will pause if quota is exceeded
- Runs in headless mode by default for automated data collection, this can be changed in the main script

