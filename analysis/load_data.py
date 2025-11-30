import pandas as pd
import logging
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

from app.models.rec_event import RecEvent
from app.models.video import Video
from app.models.channel import Channel
from app.models.category import Category

load_dotenv()

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)


def get_database_url() -> str:
    db_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    if not db_url:
        raise ValueError("DATABASE_URL or DB_URL environment variable not set")
    return db_url


def load_rec_events(
    engine=None,
    run_id: Optional[str] = None,
    iteration: Optional[int] = None
) -> pd.DataFrame:
    if engine is None:
        engine = create_engine(get_database_url())

    query = select(RecEvent)

    if run_id:
        query = query.where(RecEvent.run_id == run_id)
    if iteration is not None:
        query = query.where(RecEvent.iteration == iteration)

    with Session(engine) as session:
        result = session.execute(query)
        events = result.scalars().all()

    data = [{
        'id': e.id,
        'run_id': str(e.run_id),
        'iteration': e.iteration,
        'source_video_id': e.source_video_id,
        'video_id': e.video_id,
        'position': e.position,
        'collected_at': e.collected_at
    } for e in events]

    return pd.DataFrame(data)


def load_videos(engine=None) -> pd.DataFrame:
    if engine is None:
        engine = create_engine(get_database_url())

    with Session(engine) as session:
        result = session.execute(select(Video))
        videos = result.scalars().all()

    data = [{
        'video_id': v.video_id,
        'title': v.title,
        'description': v.description,
        'iteration': v.iteration,
        'channel_id': v.channel_id,
        'channel_title': v.channel_title,
        'tags': v.tags,
        'topic_categories': v.topic_categories,
        'category_id': v.category_id,
        'published_at': v.published_at,
        'language': v.language,
        'duration_iso': v.duration_iso,
        'view_count': v.view_count,
        'like_count': v.like_count,
        'comment_count': v.comment_count
    } for v in videos]

    return pd.DataFrame(data)


def load_channels(engine=None) -> pd.DataFrame:
    if engine is None:
        engine = create_engine(get_database_url())

    with Session(engine) as session:
        result = session.execute(select(Channel))
        channels = result.scalars().all()

    data = [{
        'channel_id': c.channel_id,
        'title': c.title,
        'description': c.description,
        'topic_categories': c.topic_categories,
        'country': c.country
    } for c in channels]

    return pd.DataFrame(data)


def load_categories(engine=None) -> pd.DataFrame:
    if engine is None:
        engine = create_engine(get_database_url())

    with Session(engine) as session:
        result = session.execute(select(Category))
        categories = result.scalars().all()

    data = [{
        'id': c.id,
        'name': c.name
    } for c in categories]

    return pd.DataFrame(data)


def load_full_dataset(engine=None) -> pd.DataFrame:
    if engine is None:
        engine = create_engine(get_database_url())

    logger.info("Loading recommendation events...")
    rec_events = load_rec_events(engine)

    logger.info("Loading videos...")
    videos = load_videos(engine)

    logger.info("Loading channels...")
    channels = load_channels(engine)

    logger.info("Loading categories...")
    categories = load_categories(engine)

    logger.info("Merging data...")
    df = rec_events.merge(
        videos,
        on='video_id',
        how='left',
        suffixes=('_rec', '_video')
    )

    df = df.merge(
        channels,
        on='channel_id',
        how='left',
        suffixes=('', '_channel')
    )

    df = df.merge(
        categories,
        left_on='category_id',
        right_on='id',
        how='left',
        suffixes=('', '_cat')
    )

    if 'name' in df.columns:
        df.rename(columns={'name': 'category_name'}, inplace=True)

    logger.info(f"Loaded {len(df)} recommendation events")
    logger.info(f"Unique videos: {df['video_id'].nunique()}")
    logger.info(f"Unique channels: {df['channel_id'].nunique()}")
    logger.info(f"Run IDs: {df['run_id'].nunique()}")

    return df


def save_labeled_dataset(df: pd.DataFrame, min_signals: int = 2):
    cache_file = CACHE_DIR / f"labeled_dataset_min{min_signals}.parquet"
    df.to_parquet(cache_file, index=False)
    logger.info(f"✓ Cached labeled dataset to: {cache_file}")
    return cache_file


def load_labeled_dataset(min_signals: int = 2, max_age_hours: int = 24) -> Optional[pd.DataFrame]:
    cache_file = CACHE_DIR / f"labeled_dataset_min{min_signals}.parquet"

    if not cache_file.exists():
        return None

    import time
    cache_age_seconds = time.time() - cache_file.stat().st_mtime
    cache_age_hours = cache_age_seconds / 3600

    if cache_age_hours > max_age_hours:
        logger.warning(f"Cache is {cache_age_hours:.1f} hours old (max: {max_age_hours}h), reloading from database...")
        return None

    logger.info(f"✓ Loading labeled dataset from cache ({cache_age_hours:.1f}h old)...")
    df = pd.read_parquet(cache_file)
    logger.info(f"  Loaded {len(df):,} recommendation events")
    logger.info(f"  Political: {df['is_political'].sum():,} ({df['is_political'].mean()*100:.1f}%)")
    return df


def clear_cache():
    import shutil
    if CACHE_DIR.exists():
        shutil.rmtree(CACHE_DIR)
        CACHE_DIR.mkdir(exist_ok=True)
        logger.info("✓ Cache cleared")


def get_labeled_dataset(min_signals: int = 2, max_age_hours: int = 24) -> pd.DataFrame:
    """
    Get labeled dataset - loads from cache if available, otherwise loads from DB and labels.s
    """
    df = load_labeled_dataset(min_signals=min_signals, max_age_hours=max_age_hours)

    if df is not None:
        return df

    logger.info("Loading from database and applying political labeling...")
    from analysis.political_labeling import label_political_content

    df = load_full_dataset()
    df = label_political_content(df, min_signals=min_signals)

    save_labeled_dataset(df, min_signals=min_signals)

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    df = load_full_dataset()
    logger.info(f"\nDataFrame shape: {df.shape}")
    logger.info(f"\nColumns: {df.columns.tolist()}")
    logger.info("\nFirst few rows:")
    logger.info(f"\n{df.head()}")
